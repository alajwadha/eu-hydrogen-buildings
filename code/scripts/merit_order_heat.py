"""Merit-order (dispatch) reframe of the hydrogen question, per Abdul's June 2026 steer.

Instead of "H2 boiler LCOH vs heat pump", we ask: in the heat-supply MERIT ORDER, where the
cold-snap PEAK slice of demand must be met by a quick-start dispatchable source, does HYDROGEN
beat the fossil (gas) peaker on MARGINAL OPERATING cost? Hydrogen's advantage is carbon-free;
its penalty is that peaking H2 must be stored seasonally (summer->winter), and seasonal salt-
cavern storage adds ~EUR 50/MWh-heat where caverns exist and ~EUR 100/MWh where they don't.

So H2's heating share is DERIVED (the peak slice it captures), not imposed. It depends on each
scenario's levers (carbon price -> fossil-peaker cost; H2-price trajectory -> H2 cost) and on
whether the country has cheap seasonal storage (Caglayan 2020).

Inputs: heat_load_profile.csv (the load-duration curve), Economics fuel prices + carbon,
literature/merit_order_supply_research.md (storage adder, marginal costs).
Run: cd code && PYTHONPATH=. python -m scripts.merit_order_heat
Out: code/results/merit_order_heat.csv + figure F11.
"""
from __future__ import annotations
import numpy as np, pandas as pd
# numpy 2.0 removed np.trapz in favour of np.trapezoid; support both.
_trapz = getattr(np, "trapezoid", None) or np.trapz

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
from src.Config import RESULTS_DIR
from src.Economics import get_fuel_price, get_cop
from src.Policy import get_carbon_price
from scripts._figstyle import set_style, short_scen, legend_below
set_style()

REPO = Path(__file__).resolve().parents[2]
FIG = REPO / "paper" / "figs" / "diagnostics"; FIG.mkdir(parents=True, exist_ok=True)

# 5-scenario lever bundles (the agreed multi-lever design). peak_elec = the cold-snap
# SCARCITY electricity price (EUR/MWh), set by the power system's own marginal peaker in
# dunkelflaute hours. It is now DERIVED per country x scenario by scripts/power_peak_price.py
# (marginal OCGT-vs-H2-turbine SRMC + scarcity premium); the constants below are only the
# FALLBACK when that table has not been built yet.
SCEN = {
    "CURRENT_POLICIES": dict(carbon="LOW",     h2="STRANDED", peak_elec=280),
    "STATED_POLICIES":  dict(carbon="CENTRAL", h2="CENTRAL",  peak_elec=250),
    "NET_ZERO":         dict(carbon="HIGH",    h2="CENTRAL",  peak_elec=210),
    "H2_PUSH":          dict(carbon="HIGH",    h2="RAPID",    peak_elec=250),  # carbon = Net Zero (Ali 2026-06)
}


def _load_peak_elec() -> dict:
    """(country, scenario) -> derived peak price, from power_peak_price.csv if present."""
    f = RESULTS_DIR / "power_peak_price.csv"
    if not f.exists():
        return {}
    d = pd.read_csv(f)
    return {(r.country, r.scenario): float(r.peak_elec) for _, r in d.iterrows()}
# Countries with cheap domestic salt-cavern seasonal H2 storage (Caglayan et al. 2020).
CAVERN = {"DE", "NL", "PL", "DK", "UK", "RO", "FR"}
EF_GAS = 0.202          # tCO2/MWh gas
ETA_GAS, ETA_H2 = 0.92, 0.90
MWH_PER_KG = 1.0 / 30.0   # 1 kg H2 ~ 0.0333 MWh
STORE_CAVERN_EUR_KG, STORE_NONCAVERN_EUR_KG = 1.5, 3.0   # seasonal, ~1 cycle/yr (EWI 2023)
CUM = [100, 500, 1000, 2000, 4000, 8760]


def storage_adder(c):
    """Seasonal-storage cost in EUR/MWh-heat (per MWh of useful H2 heat delivered)."""
    eur_kg = STORE_CAVERN_EUR_KG if c in CAVERN else STORE_NONCAVERN_EUR_KG
    return (eur_kg / MWH_PER_KG) / ETA_H2     # EUR/kg -> EUR/MWh-H2 -> EUR/MWh-heat


def peak_slice_fraction(row):
    """Energy in the cold-snap peak (top 2000 h, above the 2000-h demand level) as a share of
    annual heat -- the slice a dispatchable peaker must serve. Trapezoidal from the LDC points."""
    h = np.array(CUM, float)
    gw = np.array([row[f"GW_at_{x}h"] for x in CUM], float)
    base = np.interp(2000, h, gw)             # demand level exceeded for 2000 h
    hh = np.linspace(0, 2000, 200)
    dd = np.clip(np.interp(hh, h, gw) - base, 0, None)
    peak_energy_gwh = _trapz(dd, hh)        # GW*h = GWh over the year
    annual_gwh = row["annual_TWh"] * 1e3
    return float(peak_energy_gwh / annual_gwh)


def main():
    lp = pd.read_csv(RESULTS_DIR / "heat_load_profile.csv").set_index("country")
    peak_tbl = _load_peak_elec()
    if peak_tbl:
        print("peak_elec: ENDOGENOUS per-country (power_peak_price.csv)")
    else:
        print("peak_elec: fallback constants (run scripts.power_peak_price to derive)")
        print("  WARNING: on the fallback the published win counts change from 0/4/9/16 to")
        print("  0/4/4/10. The basis is recorded in the peak_price_basis column below.")
    rows = []
    for c in lp.index:
        # Air-source COP COLLAPSES on the coldest hours (~-7C): ~0.6 of the seasonal COP,
        # floored ~1.8. This is why HP cannot cheaply serve the cold-snap peak on its own.
        cop_peak = max(get_cop("hp_air", c, 2050) * 0.60, 1.8)
        for s, lv in SCEN.items():
            cp = get_carbon_price(2050, lv["carbon"])
            gas = get_fuel_price("gas", c, 2050)
            gas_peaker = gas / ETA_GAS + cp * EF_GAS / ETA_GAS
            h2 = get_fuel_price("hydrogen", c, 2050, lv["h2"])
            h2_peaker = h2 / ETA_H2 + storage_adder(c)
            peak_elec = peak_tbl.get((c, s), lv["peak_elec"])
            hp_peak = peak_elec / max(cop_peak, 1.0)
            cheapest_peaker = min(gas_peaker, h2_peaker, hp_peak)
            h2_wins = (h2_peaker <= gas_peaker) and (h2_peaker <= hp_peak)
            pslice = peak_slice_fraction(lp.loc[c])
            rows.append({
                "country": c, "scenario": s, "cavern": c in CAVERN,
                "gas_peaker_eur_mwh": round(gas_peaker, 1),
                "h2_peaker_eur_mwh": round(h2_peaker, 1),
                "h2_storage_adder": round(storage_adder(c), 1),
                "peak_elec_eur_mwh": round(peak_elec, 1),
                "hp_peak_eur_mwh": round(hp_peak, 1),
                "peak_slice_frac": round(pslice, 3),
                "h2_wins_peak": h2_wins,
                # Six decimals, not three. A reader who sums this column across the 29
                # countries, which is what the reproduction guide points them at, has to
                # land on the ceiling the paper prints. At three decimals the rounding
                # accumulated 0.02 pp and gave 8.0 against the published 7.9.
                "h2_derived_share": round(pslice if h2_wins else 0.0, 6),
                "_share_exact": pslice if h2_wins else 0.0,
            })
    df = pd.DataFrame(rows)
    # Which peak-price basis produced this file. Without it a fallback run is byte-shaped
    # like an endogenous one, and the fallback moves the Net Zero count from 9 to 4 and the
    # H2 Push count from 16 to 10 -- two of the four published numbers.
    df["peak_price_basis"] = "endogenous" if peak_tbl else "fallback"
    df.drop(columns=["_share_exact"]).to_csv(RESULTS_DIR / "merit_order_heat.csv",
                                             index=False)

    # summary per scenario
    # This weighted share is one of the four ceilings the manuscript prints. It used to be
    # summed from h2_derived_share, which is rounded to three decimals for the file; over
    # 29 countries that rounding accumulated to 0.02 pp and pushed Net Zero from 7.94 to
    # 7.96, so the paper printed 8.0 while the sensitivity sweep, which does the same sum
    # at full precision, wrote 7.9. Two artefacts disagreed about one number because one of
    # them was adding up a display column.
    print("Scenario          | countries where H2 wins peak | EU-wt H2 derived share")
    for s in SCEN:
        d = df[df.scenario == s]
        win = d[d.h2_wins_peak]
        wt = (d._share_exact * lp.loc[d.country, "annual_TWh"].values).sum() / lp["annual_TWh"].sum()
        print(f"  {s:<16}| {len(win):>2} / 29 ({', '.join(win.country.head(8))}{'...' if len(win)>8 else ''}) | {wt*100:.1f}%")

    # figure: marginal cost of the peaking options, H2_PUSH, by country (sorted)
    d = df[df.scenario == "H2_PUSH"].set_index("country")
    order = d.sort_values("h2_peaker_eur_mwh").index
    fig, ax = plt.subplots(figsize=(7.4, 9.2)); y = np.arange(len(order))
    ax.barh(y - 0.2, d.loc[order, "gas_peaker_eur_mwh"], 0.4, color="#969696", label="gas peaker")
    ax.barh(y + 0.2, d.loc[order, "h2_peaker_eur_mwh"], 0.4,
            color=["#2ca02c" if d.loc[c, "h2_wins_peak"] else "#6a51a3" for c in order],
            label="H₂ peaker (green = H₂ wins)")
    ax.set_yticks(y); ax.set_yticklabels([f"{c}{'*' if d.loc[c,'cavern'] else ''}" for c in order])
    ax.invert_yaxis()
    ax.set_xlabel("Marginal cost of peaking heat, 2050 (€/MWh-heat)   |   * = salt-cavern storage")
    ax.set_title(f"Marginal cost of peaking heat by source ({short_scen('H2_PUSH')}, 2050)")
    legend_below(ax, ncol=2)
    fig.savefig(FIG / "F11_merit_order_peak.png"); plt.close(fig)
    print(f"\nWrote results/merit_order_heat.csv + F11_merit_order_peak.png. Storage adder: cavern "
          f"{storage_adder('DE'):.0f} vs non-cavern {storage_adder('ES'):.0f} EUR/MWh.")


if __name__ == "__main__":
    main()
