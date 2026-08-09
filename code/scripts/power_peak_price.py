"""Endogenous cold-snap (scarcity) electricity price -- supply-side deepening.

The heat merit order (merit_order_heat.py) previously took the winter-peak electricity
price as a per-scenario CONSTANT (210-280 EUR/MWh). That parameter is load-bearing: it
sets the cold-snap heat-pump cost that hydrogen must beat. This module DERIVES it from
the power sector's own merit order instead:

  In a 2050 system the winter-peak / dunkelflaute price is set by the MARGINAL FIRM
  UNIT -- the dispatchable peaker the system actually turns on when VRE is short
  (TYNDP 2024: by 2050 the EU gas+H2 turbine fleet runs ~160 FLH = pure peaking).
  Its short-run marginal cost (SRMC) anchors the price; tight hours add a scarcity
  premium above SRMC (capacity-market / VoLL literature):

    OCGT gas peaker SRMC = gas_wholesale/0.40 + carbon x 0.202/0.40 + VOM
    H2 turbine SRMC      = H2_delivered/0.40 + seasonal storage adder + VOM
    peak price           = min(gas peaker, H2 turbine) + scarcity premium

  Per-country variation enters through the H2 delivered cost (country multipliers),
  salt-cavern access (storage adder), and the scenario's carbon price + H2 trajectory.
  Wholesale (not residential retail) fuel prices apply to power plants.

Outputs results/power_peak_price.csv (peak_elec per country x scenario, with the
scarcity-premium band) and figure F15. merit_order_heat.py consumes the central value,
replacing its former constants (kept there as fallback).

Sources: TYNDP 2024 scenarios (peaker fleet FLH, cost-of-electricity ~EUR 80-245/MWh in
tight hours); EWI 2023 (H2 storage); Caglayan 2020 (caverns); IEA WEO gas wholesale.
Run: cd code && PYTHONPATH=. python -m scripts.power_peak_price
"""
from __future__ import annotations
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
from src.Config import RESULTS_DIR
from src.Economics import get_fuel_price
from src.Policy import get_carbon_price
from scripts._figstyle import set_style, short_scen, legend_below
set_style()

REPO = Path(__file__).resolve().parents[2]
FIG = REPO / "paper" / "figs" / "diagnostics"; FIG.mkdir(parents=True, exist_ok=True)

# Power-sector peaker parameters (TYNDP / DEA technology catalogue).
ETA_OCGT = 0.40            # open-cycle gas turbine, electric efficiency
ETA_H2_TURBINE = 0.40      # H2-ready turbine, electric efficiency
VOM_PEAKER = 4.5           # EUR/MWh-e (TYNDP cost-of-electricity input)
EF_GAS = 0.202             # tCO2/MWh-fuel
GAS_WHOLESALE_2050 = 30.0  # EUR/MWh hub price (IEA WEO / EWI 2050 range 25-35)
# Wholesale H2 for turbines = the residential delivered price MINUS the distribution
# margin (turbines sit on the transmission backbone). Approximate the backbone price
# as the delivered price x 0.85 (EHB: distribution is ~10-20% of delivered).
#
# UNRESOLVED, and it matters. This treats H2_PRICE_TRAJECTORIES as a residential DELIVERED
# price with a distribution margin inside it. Economics.py's own header for the same series
# says the opposite -- "the default H2-boiler LCOH assumes hydrogen is delivered to the home
# at zero distribution-infrastructure cost", which is why h2_distribution_adder is added on
# top there. If Economics is right, this 0.85 discounts a margin the series never carried.
# Measured effect: removing it takes the H2 Push power-arena win count from 15 to 8 on the
# evolving-efficiency series. The equal-efficiency count of 7, the 8.7 per cent
# capacity-weighted recovery and the capacity payments are all invariant, because where
# hydrogen is marginal the clearing price is its own SRMC plus the scarcity premium, so the
# rent does not depend on the fuel level. The 15 is reported in the SI with this
# contingency stated. Resolving which basis the series is on is an author decision.
H2_BACKBONE_FACTOR = 0.85
# Scarcity premium above the marginal unit's SRMC in tight hours (capacity-market /
# VoLL literature; TYNDP tight-hour prices EUR 80-245 are SRMC + this premium).
SCARCITY_PREMIUM = {"low": 30.0, "central": 60.0, "high": 120.0}

# Scenario levers (mirror merit_order_heat.SCEN, minus the now-derived peak_elec).
SCEN_LEVERS = {
    "CURRENT_POLICIES": dict(carbon="LOW", h2="STRANDED"),
    "STATED_POLICIES":  dict(carbon="CENTRAL", h2="CENTRAL"),
    "NET_ZERO":         dict(carbon="HIGH", h2="CENTRAL"),
    "H2_PUSH":          dict(carbon="HIGH", h2="RAPID"),   # carbon = Net Zero (Ali 2026-06)
}


def power_storage_adder(country: str) -> float:
    """Seasonal-storage adder for POWER-sector H2 (EUR/MWh-e). Same cavern physics as
    the heat side (merit_order_heat.storage_adder) but per MWh-electric at turbine eff."""
    from scripts.merit_order_heat import CAVERN, STORE_CAVERN_EUR_KG, STORE_NONCAVERN_EUR_KG, MWH_PER_KG
    eur_kg = STORE_CAVERN_EUR_KG if country in CAVERN else STORE_NONCAVERN_EUR_KG
    return (eur_kg / MWH_PER_KG) / ETA_H2_TURBINE


def peak_price(country: str, scenario: str, bound: str = "central") -> dict:
    lv = SCEN_LEVERS[scenario]
    cp = get_carbon_price(2050, lv["carbon"])
    ocgt = GAS_WHOLESALE_2050 / ETA_OCGT + cp * EF_GAS / ETA_OCGT + VOM_PEAKER
    h2_del = get_fuel_price("hydrogen", country, 2050, lv["h2"]) * H2_BACKBONE_FACTOR
    h2t = h2_del / ETA_H2_TURBINE + power_storage_adder(country) + VOM_PEAKER
    marginal = min(ocgt, h2t)
    return {
        "ocgt_srmc": round(ocgt, 1), "h2_turbine_srmc": round(h2t, 1),
        "marginal_unit": "h2_turbine" if h2t < ocgt else "gas_ocgt",
        "peak_elec_low": round(marginal + SCARCITY_PREMIUM["low"], 1),
        "peak_elec": round(marginal + SCARCITY_PREMIUM["central"], 1),
        "peak_elec_high": round(marginal + SCARCITY_PREMIUM["high"], 1),
    }


def build_table() -> pd.DataFrame:
    from src.Economics import LABOUR_COST_MULTIPLIER
    rows = []
    for c in LABOUR_COST_MULTIPLIER:
        for s in SCEN_LEVERS:
            rows.append({"country": c, "scenario": s, **peak_price(c, s)})
    return pd.DataFrame(rows)


def main():
    df = build_table()
    df.to_csv(RESULTS_DIR / "power_peak_price.csv", index=False)

    old = {"CURRENT_POLICIES": 280, "STATED_POLICIES": 250, "NET_ZERO": 210, "H2_PUSH": 250}
    print("Endogenous winter-peak electricity price (2050, EUR/MWh-e):")
    print(f"{'scenario':<18}{'EU mean':>9}{'min':>7}{'max':>7}{'old const':>11}{'marginal unit (mode)':>24}")
    for s in SCEN_LEVERS:
        d = df[df.scenario == s]
        print(f"{s:<18}{d.peak_elec.mean():>9.0f}{d.peak_elec.min():>7.0f}{d.peak_elec.max():>7.0f}"
              f"{old[s]:>11}{d.marginal_unit.mode()[0]:>24}")

    # figure: peak price by country, central premium, all scenarios
    fig, ax = plt.subplots(figsize=(9.4, 5.2))
    order = df[df.scenario == "STATED_POLICIES"].sort_values("peak_elec").country
    x = np.arange(len(order))
    col = {"CURRENT_POLICIES": "#7f7f7f", "STATED_POLICIES": "#1f77b4",
           "NET_ZERO": "#2ca02c", "H2_PUSH": "#d62728"}
    for s in SCEN_LEVERS:
        d = df[df.scenario == s].set_index("country").loc[order]
        ax.plot(x, d.peak_elec, "o-", ms=3.5, lw=1.4, color=col[s], label=short_scen(s))
    ax.set_xticks(x); ax.set_xticklabels(order, fontsize=7, rotation=0)
    ax.set_ylabel("Winter-peak electricity price (€/MWh)")
    ax.set_title("Endogenous cold-snap electricity price by country and scenario (2050)")
    legend_below(ax, ncol=4)
    fig.savefig(FIG / "F15_peak_power_price.png"); plt.close(fig)
    print("\nWrote results/power_peak_price.csv + F15_peak_power_price.png")


if __name__ == "__main__":
    main()
