"""Second batch of explanatory figures (15) for the LMDI / four-scenario model.

Distinct from the first five (decomposition, grid attribution, rho-sensitivity,
H2-HP gap, backcast drivers). All read the shipped result CSVs / engines.

Run:  cd code && PYTHONPATH=. python -m scripts.explanatory_figures_2
Out:  paper/figs/fig_*.pdf (+ .png)
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scripts._figstyle import set_style, short_scen

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "code" / "results"
CFG = ROOT / "code" / "data" / "country_config"
PROC = ROOT / "code" / "data" / "processed"
FIGS = ROOT / "paper" / "figs"
FIGS.mkdir(parents=True, exist_ok=True)

set_style()   # autolayout + savefig bbox='tight' (no overlap); presentation sizes below
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10.5,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 12.5, "axes.titleweight": "bold", "figure.dpi": 120,
})

SC = ["CURRENT_POLICIES","STATED_POLICIES","NET_ZERO","H2_PUSH"]
SC_COL = {"CURRENT_POLICIES": "#7f7f7f", "STATED_POLICIES": "#1f77b4", "NET_ZERO": "#2ca02c", "H2_PUSH": "#ff7f0e",
          "COST_OPT": "#d62728"}
YEARS = [2025, 2030, 2040, 2050]
TECH_COL = {
    "hp_air": "#4c78a8", "hp_ground": "#2a5783", "district_heat": "#9467bd",
    "biomass_boiler": "#8c6d31", "h2_boiler": "#ff7f0e", "gas_boiler": "#7f7f7f",
    "oil_boiler": "#4d4d4d", "resistance_heater": "#72b7b2",
}
TECH_LAB = {"hp_air": "HP air", "hp_ground": "HP ground", "district_heat": "District heat",
            "biomass_boiler": "Biomass", "h2_boiler": "Hydrogen", "gas_boiler": "Gas",
            "oil_boiler": "Oil", "resistance_heater": "Resistance"}
CARR_COL = {"gas": "#7f7f7f", "oil": "#4d4d4d", "biomass": "#8c6d31",
            "electricity": "#4c78a8", "district_heat": "#9467bd", "hydrogen": "#ff7f0e"}


def _save(fig, name):
    fig.savefig(FIGS / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(FIGS / f"{name}.png", bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"  wrote {name}")


def _eu_demand(sc):
    d = pd.read_csv(RES / f"mc_summary_{sc}.csv")
    return d[d.variable == "useful_heat_MWh"].groupby("year")[["q10", "q50", "q90"]].sum() / 1e6


def _eu_co2(sc):
    d = pd.read_csv(RES / f"mc_emissions_{sc}.csv")
    return d[d.variable == "co2_MtCO2"].groupby("year")[["q10", "q50", "q90"]].sum()


# 1 -----------------------------------------------------------------
def f01_scenario_fan():
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    for sc in SC:
        g = _eu_demand(sc)
        ax.fill_between(g.index, g.q10, g.q90, color=SC_COL[sc], alpha=0.15)
        ax.plot(g.index, g.q50, "-o", color=SC_COL[sc], lw=2, ms=5, label=sc)
    try:
        co = pd.read_csv(RES / "cost_opt_pathway.csv")
        s = co[co.variant == "COST_OPT_90"].groupby("year")["useful_heat_MWh"].sum() / 1e6
        ax.plot(s.index, s.values, "--s", color=SC_COL["COST_OPT"], lw=2, ms=5, label="COST_OPT (-90%)")
    except Exception:
        pass
    ax.set_ylabel("EU+CH+UK useful heat demand (TWh/yr)"); ax.set_xlabel("Year")
    ax.set_title("Scenario heat-demand trajectories, 2025-2050")
    ax.set_ylim(0, None); ax.legend(frameon=False, ncol=2)
    _save(fig, "fig_scenario_demand_fan")


# 2 -----------------------------------------------------------------
def f02_co2_traj():
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    for sc in SC:
        g = _eu_co2(sc)
        ax.fill_between(g.index, g.q10, g.q90, color=SC_COL[sc], alpha=0.15)
        ax.plot(g.index, g.q50, "-o", color=SC_COL[sc], lw=2, ms=5, label=sc)
    ax.set_ylabel("Buildings CO2 (MtCO2/yr)"); ax.set_xlabel("Year")
    ax.set_title("Buildings CO2 trajectories by scenario, 2025-2050")
    ax.set_ylim(0, None); ax.legend(frameon=False)
    _save(fig, "fig_co2_trajectory_scenarios")


# 3 -----------------------------------------------------------------
def f03_tech_evolution_ref():
    d = pd.read_csv(RES / "mc_summary_STATED_POLICIES.csv")
    ts = d[d.variable == "tech_share"]
    piv = ts.pivot_table(index="year", columns="tech", values="q50", aggfunc="mean").reindex(YEARS)
    techs = [t for t in TECH_COL if t in piv.columns]
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    ax.stackplot(piv.index, *[piv[t] * 100 for t in techs],
                 labels=[TECH_LAB[t] for t in techs], colors=[TECH_COL[t] for t in techs])
    ax.set_ylabel("Share of useful heat (%)"); ax.set_xlabel("Year"); ax.set_ylim(0, 100)
    ax.set_title("Technology mix evolution (Stated Policies), 2025-2050")
    ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.1), fontsize=8.5)
    _save(fig, "fig_tech_mix_evolution_ref")


# 4 -----------------------------------------------------------------
def f04_mix_2050_scenarios():
    rows = {}
    for sc in SC:
        d = pd.read_csv(RES / f"mc_summary_{sc}.csv")
        ts = d[(d.variable == "tech_share") & (d.year == 2050)].groupby("tech")["q50"].mean()
        rows[sc] = ts * 100
    try:
        co = pd.read_csv(RES / "cost_opt_pathway.csv")
        s = co[(co.variant == "COST_OPT_90") & (co.year == 2050)]
        tot = s["useful_heat_MWh"].sum()
        rows["COST_OPT"] = s.groupby("tech")["useful_heat_MWh"].sum() / tot * 100
    except Exception:
        pass
    order = list(rows.keys())
    techs = [t for t in TECH_COL]
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    bottom = np.zeros(len(order))
    for t in techs:
        vals = np.array([rows[s].get(t, 0.0) for s in order])
        ax.bar(order, vals, bottom=bottom, color=TECH_COL[t], label=TECH_LAB[t])
        bottom += vals
    ax.set_ylabel("Share of useful heat in 2050 (%)"); ax.set_ylim(0, 100)
    ax.set_title("2050 technology mix by scenario")
    ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.08), fontsize=8.5)
    _save(fig, "fig_tech_mix_2050_scenarios")


# 5 -----------------------------------------------------------------
def f05_carrier_flip():
    d = pd.read_csv(RES / "mc_summary_STATED_POLICIES.csv")
    fe = d[d.variable == "final_energy_MWh"]
    carr = [c for c in CARR_COL]
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    for i, y in enumerate([2025, 2050]):
        sub = fe[fe.year == y].groupby("carrier")["q50"].sum()
        tot = sub.sum()
        bottom = 0.0
        for c in carr:
            v = sub.get(c, 0.0) / tot * 100
            ax.bar(i, v, bottom=bottom, color=CARR_COL[c], width=0.6,
                   label=c if i == 0 else None)
            if v > 4:
                ax.text(i, bottom + v / 2, f"{v:.0f}", ha="center", va="center",
                        color="white", fontsize=9, fontweight="bold")
            bottom += v
    ax.set_xticks([0, 1]); ax.set_xticklabels(["2025", "2050"])
    ax.set_ylabel("Share of final energy (%)"); ax.set_ylim(0, 100)
    ax.set_title("Final-energy carrier mix (Stated Policies), 2025-2050")
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.08), fontsize=8.5)
    _save(fig, "fig_final_energy_carrier_flip")


# 6 -----------------------------------------------------------------
def f06_system_efficiency():
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    for sc in SC:
        d = pd.read_csv(RES / f"mc_summary_{sc}.csv")
        u = d[d.variable == "useful_heat_MWh"].groupby("year")["q50"].sum()
        f = d[d.variable == "final_energy_MWh"].groupby("year")["q50"].sum()
        eff = (u / f).reindex(YEARS)
        ax.plot(eff.index, eff.values, "-o", color=SC_COL[sc], lw=2, label=sc)
    ax.set_ylabel("System efficiency (useful / final energy)"); ax.set_xlabel("Year")
    ax.set_title("System efficiency of heat supply by scenario")
    ax.axhline(1.0, color="#999", ls=":", lw=1)
    ax.legend(frameon=False)
    _save(fig, "fig_system_efficiency")


# 7 -----------------------------------------------------------------
def f07_country_demand_2050():
    d = pd.read_csv(RES / "mc_country_STATED_POLICIES.csv")
    s = d[(d.variable == "useful_heat_TWh") & (d.tech == "all") & (d.year == 2050)]
    s = s.groupby("country")["q50"].first().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(7.0, 8.0))
    ax.barh(s.index, s.values, color="#4c78a8")
    for i, (c, v) in enumerate(s.items()):
        ax.text(v + max(s) * 0.01, i, f"{v:.0f}", va="center", fontsize=7.5)
    ax.set_xlabel("2050 useful heat demand (TWh, STATED_POLICIES median)")
    ax.set_title("Per-country 2050 heat demand (Stated Policies)")
    _save(fig, "fig_country_demand_2050_ref")


# 8 -----------------------------------------------------------------
def f08_country_demand_change():
    d = pd.read_csv(RES / "mc_country_STATED_POLICIES.csv")
    s = d[(d.variable == "useful_heat_TWh") & (d.tech == "all")]
    piv = s.pivot_table(index="country", columns="year", values="q50")
    chg = ((piv[2050] / piv[2025] - 1) * 100).sort_values()
    fig, ax = plt.subplots(figsize=(7.0, 8.0))
    cols = ["#2ca02c" if v < 0 else "#d62728" for v in chg.values]
    ax.barh(chg.index, chg.values, color=cols)
    ax.axvline(0, color="#333", lw=0.8)
    ax.set_xlabel("Demand change 2025->2050 (%, STATED_POLICIES)")
    ax.set_title("National heat-demand change, 2025-2050")
    fig.text(0.5, 0.02, "Green: demand falls (retrofit beats stock growth). Red: demand rises "
             "(population/household growth dominates).", ha="center", fontsize=8, color="#555")
    _save(fig, "fig_country_demand_change_ref")


# 9 -----------------------------------------------------------------
def f09_envelope_rate():
    d = pd.read_csv(CFG / "scenario_intensity_rates.csv")
    ref = d[d.scenario == "STATED_POLICIES"].set_index("country")["central_pct_yr"].sort_values()
    fig, ax = plt.subplots(figsize=(7.0, 8.0))
    ax.barh(ref.index, ref.values, color="#2a5783")
    ax.set_xlabel("STATED_POLICIES envelope-design intensity decline rate (%/yr)")
    ax.set_title("Per-country renovation pace (Stated Policies)")
    fig.text(0.5, 0.02, "NET_ZERO scales each value x2.73, H2_PUSH x1.64 (proportional, not "
             "convergence). FI lowest, CH highest.", ha="center", fontsize=8, color="#555")
    _save(fig, "fig_envelope_rate_by_country")


# 10 ----------------------------------------------------------------
def f10_population():
    d = pd.read_csv(CFG / "pop_projection.csv")
    keys = [c for c in ["IE", "FR", "UK", "ES", "DE", "PL", "IT"] if c in d.country.unique()]
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    for c in keys:
        sub = d[d.country == c].set_index("year")["population"]
        idx = sub / sub.loc[2025] * 100
        ax.plot(idx.index, idx.values, lw=2, label=c)
        ax.text(2050.3, idx.loc[2050], c, fontsize=8, va="center")
    ax.axhline(100, color="#999", ls=":", lw=1)
    ax.set_ylabel("Population index (2025 = 100)"); ax.set_xlabel("Year")
    ax.set_title("National population trajectories, 2025-2050")
    ax.legend(frameon=False, ncol=4, fontsize=8, loc="lower left")
    _save(fig, "fig_population_trajectories")


# 11 ----------------------------------------------------------------
def f11_backcast_validation():
    d = pd.read_csv(RES / "lmdi_design.csv")
    d = d[d.country != "EU"].copy().sort_values("gap_2015_vs_hotmaps_pct")
    fig, ax = plt.subplots(figsize=(7.0, 8.0))
    cols = ["#2ca02c" if abs(v) <= 15 else "#d62728" for v in d.gap_2015_vs_hotmaps_pct]
    ax.barh(d.country, d.gap_2015_vs_hotmaps_pct, color=cols)
    ax.axvspan(-15, 15, color="#2ca02c", alpha=0.08)
    ax.axvline(0, color="#333", lw=0.8)
    ax.set_xlabel("Model 2015 vs Hotmaps 2015 gap (%)")
    ax.set_title("Vintage-matched demand validation by country")
    fig.text(0.5, 0.02, "Shaded band: +/-15% acceptance. EU-aggregate gap is -1.2% (no "
             "Hotmaps-targeted calibration).", ha="center", fontsize=8, color="#555")
    _save(fig, "fig_backcast_validation")


# 12 ----------------------------------------------------------------
def f12_grid_dumbbell():
    from src.Policy import GRID_CARBON_INTENSITY as G
    items = sorted(((c, v.get(2025), v.get(2050)) for c, v in G.items() if 2025 in v and 2050 in v),
                   key=lambda x: x[1])
    cc = [i[0] for i in items]; g25 = [i[1] for i in items]; g50 = [i[2] for i in items]
    y = np.arange(len(cc))
    fig, ax = plt.subplots(figsize=(7.0, 8.0))
    for i in y:
        ax.plot([g50[i], g25[i]], [i, i], color="#ccc", lw=2, zorder=1)
    ax.scatter(g25, y, color="#d62728", s=28, zorder=2, label="2025")
    ax.scatter(g50, y, color="#2ca02c", s=28, zorder=2, label="2050")
    ax.set_yticks(y); ax.set_yticklabels(cc, fontsize=8)
    ax.set_xlabel("Electricity grid carbon intensity (gCO2/kWh)")
    ax.set_title("Grid decarbonisation 2025 -> 2050 (exogenous)")
    ax.legend(frameon=False, loc="lower right")
    _save(fig, "fig_grid_intensity_dumbbell")


# 13 ----------------------------------------------------------------
def f13_shadow_prices():
    d = pd.read_csv(RES / "cost_opt_shadow_prices.csv")
    s = d[(d.variant == "COST_OPT_90") & (d.year == 2050) & (~d.degenerate_low_baseline)]
    s = s.groupby("country")["shadow_eur_tco2"].first().sort_values()
    s = s[s > 0.01]
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    if s.empty:
        # No country's scope-1 cap binds: the least-cost mix already meets the
        # target with the ETS2 price embedded, so the implied carbon price is zero.
        ax.text(0.5, 0.5, "No binding emissions cap:\nimplied carbon price = 0 in all "
                "countries\n(cost-minimisation meets the target with ETS2 alone)",
                ha="center", va="center", transform=ax.transAxes, fontsize=11)
        ax.set_xticks([])
    else:
        ax.bar(s.index, s.values, color="#d62728", width=0.5)
        for c, v in s.items():
            ax.text(c, v + 1, f"{v:.0f}", ha="center", fontweight="bold")
    ax.set_ylabel("Implied carbon price (EUR/tCO2)")
    ax.set_title("Cost-optimal implied carbon price by country (-90% cap)")
    fig.text(0.5, -0.04, "Every country reaches the -90% scope-1 cap at zero implied carbon price: "
             "cost-minimisation meets the target with the ETS2 price alone.", ha="center", fontsize=8, color="#555")
    _save(fig, "fig_costopt_shadow_prices")


# 14 ----------------------------------------------------------------
def f14_costopt_mix_by_cap():
    co = pd.read_csv(RES / "cost_opt_pathway.csv")
    variants = ["COST_OPT_75", "COST_OPT_90", "COST_OPT_100"]
    labels = ["-75%", "-90%", "-100%"]
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    bottom = np.zeros(len(variants))
    rows = {}
    for v in variants:
        s = co[(co.variant == v) & (co.year == 2050)]
        tot = s["useful_heat_MWh"].sum()
        rows[v] = s.groupby("tech")["useful_heat_MWh"].sum() / tot * 100
    for t in TECH_COL:
        vals = np.array([rows[v].get(t, 0.0) for v in variants])
        ax.bar(labels, vals, bottom=bottom, color=TECH_COL[t], label=TECH_LAB[t])
        bottom += vals
    ax.set_ylabel("Share of useful heat in 2050 (%)"); ax.set_ylim(0, 100)
    ax.set_xlabel("Emissions cap")
    ax.set_title("Cost-optimal 2050 mix by emissions cap")
    ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.1), fontsize=8.5)
    _save(fig, "fig_costopt_mix_by_cap")


# 15 ----------------------------------------------------------------
def f15_lcoh_by_tech():
    from src.Economics import compute_lcoh
    countries = pd.read_csv(CFG / "scenario_intensity_rates.csv").country.unique()
    techs = ["hp_ground", "hp_air", "district_heat", "biomass_boiler", "gas_boiler", "h2_boiler"]
    res = {y: {} for y in [2025, 2050]}
    for y in [2025, 2050]:
        for t in techs:
            vals = []
            for c in countries:
                try:
                    vals.append(compute_lcoh(t, c, y))
                except Exception:
                    pass
            res[y][t] = float(np.median(vals)) if vals else np.nan
    x = np.arange(len(techs)); w = 0.38
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    ax.bar(x - w/2, [res[2025][t] for t in techs], w, color="#7f7f7f", label="2025")
    ax.bar(x + w/2, [res[2050][t] for t in techs], w, color="#4c78a8", label="2050")
    ax.set_xticks(x); ax.set_xticklabels([TECH_LAB[t] for t in techs], rotation=20, ha="right")
    ax.set_ylabel("LCOH (EUR/MWh useful), EU median")
    ax.set_title("Levelised cost of heat by technology")
    ax.legend(frameon=False)
    _save(fig, "fig_lcoh_by_tech")


def main():
    print("Generating 15 more explanatory figures into paper/figs/ ...")
    for fn in [f01_scenario_fan, f02_co2_traj, f03_tech_evolution_ref, f04_mix_2050_scenarios,
               f05_carrier_flip, f06_system_efficiency, f07_country_demand_2050,
               f08_country_demand_change, f09_envelope_rate, f10_population,
               f11_backcast_validation, f12_grid_dumbbell, f13_shadow_prices,
               f14_costopt_mix_by_cap, f15_lcoh_by_tech]:
        try:
            fn()
        except Exception as ex:
            print(f"  [skip] {fn.__name__}: {ex}")
    print("Done.")


if __name__ == "__main__":
    main()
