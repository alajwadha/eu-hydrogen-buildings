"""District-heating SOURCE-SWITCHING merit order (workstream C, Abdul's June 2026 steer).

A district-heating (DH) network is the clearest place to see the merit order, because one
operator dispatches a STACK of heat sources into the same pipes and picks the cheapest
available source each hour. The order, by marginal operating cost, is typically:

    waste/excess heat  ->  large heat pumps / geothermal  ->  biomass CHP  ->  {H2, gas CHP}

H2's position depends on its delivered price and the carbon price. With expensive H2 it sits at
the TOP (dearest) and only catches the residual peak. With cheap derived H2 + high carbon
(Hydrogen Push) H2 is CHEAPER than gas CHP, so it ranks just below gas CHP and GAS CHP becomes
the dearest source that sets the peak price. This script ranks the five DH sources per country x
scenario (2050), reports H2's rank and the marginal source at the peak, and derives the DH heat
share H2 could capture (the peak slice, only where H2 beats gas CHP). It mirrors
merit_order_heat.py (building level) but for the DH supply stack, reusing the same fuel-price,
carbon and seasonal-storage cost basis.

Inputs: heat_load_profile.csv (load-duration -> peak slice), Economics fuel prices + COP,
Policy carbon price. Run: cd code && PYTHONPATH=. python -m scripts.merit_order_dh
Out: code/results/merit_order_dh.csv + figure F13.
"""
from __future__ import annotations
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
from src.Config import RESULTS_DIR
from src.Economics import get_fuel_price
from src.Policy import get_carbon_price
from scripts.merit_order_heat import SCEN, CAVERN, storage_adder, peak_slice_fraction, EF_GAS
from scripts._figstyle import set_style, short_scen, legend_below
set_style()

REPO = Path(__file__).resolve().parents[2]
FIG = REPO / "paper" / "figs" / "diagnostics"; FIG.mkdir(parents=True, exist_ok=True)

# DH supply-stack technology parameters (heat-allocated efficiencies / COPs).
WASTE_HEAT_EUR_MWH = 10.0    # excess industrial / waste-incineration heat: near-zero fuel, opex+distribution
COP_LARGE_HP = 3.0           # large river/sewage/geothermal-source DH heat pumps (warmer source than air)
ETA_BIOMASS_CHP = 0.85       # biomass CHP/boiler, heat basis
ETA_GAS_CHP = 0.90           # gas CHP/boiler, heat basis
ETA_H2_CHP = 0.90            # H2 boiler/CHP, heat basis

STACK_ORDER = ["waste", "large_hp", "biomass", "gas_chp", "h2"]
STACK_LABEL = {"waste": "waste/excess heat", "large_hp": "large heat pump",
               "biomass": "biomass CHP", "gas_chp": "gas CHP", "h2": "H2 CHP/boiler"}


def dh_marginal_costs(country, scen):
    """Marginal operating cost (EUR/MWh-heat) of each DH source, 2050."""
    lv = SCEN[scen]
    cp = get_carbon_price(2050, lv["carbon"])
    elec = get_fuel_price("electricity", country, 2050)            # baseload (non-scarcity) elec
    gas = get_fuel_price("gas", country, 2050)
    bio = get_fuel_price("biomass", country, 2050)
    h2 = get_fuel_price("hydrogen", country, 2050, lv["h2"])
    return {
        "waste":    WASTE_HEAT_EUR_MWH,
        "large_hp": elec / COP_LARGE_HP,
        "biomass":  bio / ETA_BIOMASS_CHP,                          # biomass ~zero scope-1 in EU accounting
        "gas_chp":  gas / ETA_GAS_CHP + cp * EF_GAS / ETA_GAS_CHP,  # fuel + ETS carbon
        "h2":       h2 / ETA_H2_CHP + storage_adder(country),       # fuel + seasonal storage (peaking)
    }


def main():
    lp = pd.read_csv(RESULTS_DIR / "heat_load_profile.csv").set_index("country")
    rows = []
    for c in lp.index:
        pslice = peak_slice_fraction(lp.loc[c])
        for s in SCEN:
            mc = dh_marginal_costs(c, s)
            order = sorted(STACK_ORDER, key=lambda k: mc[k])         # cheapest -> dearest
            h2_rank = order.index("h2") + 1                          # 1 = cheapest, 5 = dearest
            # H2 only fires for the residual peak, and only if it beats the gas peaker there
            h2_beats_gas = mc["h2"] <= mc["gas_chp"]
            h2_dh_share = pslice if h2_beats_gas else 0.0
            rows.append({
                "country": c, "scenario": s, "cavern": c in CAVERN,
                **{f"mc_{k}": round(mc[k], 1) for k in STACK_ORDER},
                "h2_rank_in_stack": h2_rank,
                "marginal_source_at_peak": order[-1],                # who sets the DH peak price
                "h2_beats_gas_chp": h2_beats_gas,
                "peak_slice_frac": round(pslice, 3),
                "h2_dh_share": round(h2_dh_share, 3),
            })
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS_DIR / "merit_order_dh.csv", index=False)

    print("DH source-switching merit order (2050)")
    print("Scenario          | H2 mean rank (1=cheapest,5=dearest) | countries H2<gas CHP | EU-wt H2 DH share")
    for s in SCEN:
        d = df[df.scenario == s]
        win = d[d.h2_beats_gas_chp]
        wt = (d.h2_dh_share * lp.loc[d.country, "annual_TWh"].values).sum() / lp["annual_TWh"].sum()
        print(f"  {s:<16}| {d.h2_rank_in_stack.mean():>4.1f} | {len(win):>2} / 29 "
              f"({', '.join(win.country.head(6))}{'...' if len(win) > 6 else ''}) | {wt*100:.1f}%")

    # figure: DH supply stack (sorted marginal costs) for H2_PUSH, a representative country panel
    d = df[df.scenario == "H2_PUSH"].set_index("country")
    panel = [c for c in ["DE", "DK", "NL", "FR", "PL", "SE", "ES", "IT"] if c in d.index]
    fig, ax = plt.subplots(figsize=(9.0, 5.0))
    x = np.arange(len(panel)); w = 0.16
    colors = {"waste": "#8c8c8c", "large_hp": "#1f77b4", "biomass": "#2ca02c",
              "gas_chp": "#d62728", "h2": "#9467bd"}
    for i, k in enumerate(STACK_ORDER):
        ax.bar(x + (i - 2) * w, [d.loc[c, f"mc_{k}"] for c in panel], w,
               color=colors[k], label=STACK_LABEL[k])
    ax.set_xticks(x); ax.set_xticklabels(panel)
    ax.set_ylabel("Marginal cost (€/MWh-heat)")
    ax.set_title(f"District-heating supply merit order ({short_scen('H2_PUSH')}, 2050)")
    legend_below(ax, ncol=5, y=-0.16)
    fig.savefig(FIG / "F13_dh_merit_order.png"); plt.close(fig)
    print("\nWrote results/merit_order_dh.csv + F13_dh_merit_order.png.")


if __name__ == "__main__":
    main()
