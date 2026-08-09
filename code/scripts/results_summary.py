"""Presentation-quality figures of the MAIN modelling results, for Abdul.
Reads the current result CSVs + Economics, writes 6 clean PNGs to
paper/figs/diagnostics/. Run: cd code && PYTHONPATH=. python -m scripts.results_summary
"""
from __future__ import annotations
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from src.Config import RESULTS_DIR
from src.Economics import compute_lcoh, LABOUR_COST_MULTIPLIER
from scripts._figstyle import set_style, short_scen

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT = REPO_ROOT / "paper" / "figs" / "diagnostics"; OUT.mkdir(parents=True, exist_ok=True)
set_style()
plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": 0.25})  # presentation: grid on
SC = {"CURRENT_POLICIES": "#7f7f7f", "STATED_POLICIES": "#1f77b4", "NET_ZERO": "#2ca02c", "H2_PUSH": "#d62728"}
YR = [2025, 2030, 2040, 2050]


def _sm(sc):
    s = pd.read_csv(RESULTS_DIR / f"mc_summary_{sc}.csv")
    e = pd.read_csv(RESULTS_DIR / f"mc_emissions_{sc}.csv")
    dem = {int(r.year): r.q50 / 1e6 for _, r in s[s.variable == "useful_heat_MWh"].iterrows()}
    et = e[(e.variable == "co2_MtCO2") & (e.tech == "all")]
    co2 = {int(r.year): (r.q50, r.q10, r.q90) for _, r in et.iterrows()}
    sh = {r.tech: r.q50 for _, r in s[(s.year == 2050) & (s.variable == "tech_share")].iterrows()}
    return dem, co2, sh


def f1_demand():
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    for sc in SC:
        dem, _, _ = _sm(sc)
        ys = [dem[y] for y in YR]
        ax.plot(YR, ys, "o-", color=SC[sc], lw=2.4, ms=6, label=f"{short_scen(sc)}  ({(ys[-1]/ys[0]-1)*100:+.0f}%)")
        ax.annotate(f"{ys[-1]:,.0f}", (2050, ys[-1]), textcoords="offset points",
                    xytext=(8, 0), color=SC[sc], fontweight="bold", fontsize=10)
    ax.set_ylabel("Useful heat demand (TWh/yr)"); ax.set_xlabel("Year")
    ax.set_title("EU-27 + UK + CH residential heat demand, 2025–2050", fontweight="bold")
    ax.legend(title="Scenario (2050 change)", frameon=False); ax.set_xticks(YR)
    fig.savefig(OUT / "F1_demand_trajectory.png"); plt.close(fig)


def f2_co2():
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    for sc in SC:
        _, co2, _ = _sm(sc)
        med = [co2[y][0] for y in YR]; lo = [co2[y][1] for y in YR]; hi = [co2[y][2] for y in YR]
        ax.plot(YR, med, "o-", color=SC[sc], lw=2.4, ms=6, label=short_scen(sc))
        ax.fill_between(YR, lo, hi, color=SC[sc], alpha=0.12)
    # data-driven endpoint labels (never goes stale): annotate each scenario's 2050 value
    for sc in SC:
        _, co2, _ = _sm(sc)
        ax.annotate(f"{co2[2050][0]:.0f}", (2050, co2[2050][0]), textcoords="offset points",
                    xytext=(8, 0), color=SC[sc], fontweight="bold", fontsize=9, va="center")
    ax.set_ylabel("Buildings CO₂ (MtCO₂/yr)"); ax.set_xlabel("Year")
    ax.set_title("Residential heating CO₂ emissions (with 10–90% bands)", fontweight="bold")
    ax.legend(frameon=False); ax.set_xticks(YR)
    fig.savefig(OUT / "F2_co2_trajectory.png"); plt.close(fig)


def f3_lcoh():
    C = list(LABOUR_COST_MULTIPLIER)
    def med(t, y): return float(np.median([compute_lcoh(t, c, y) for c in C]))
    techs = [("gas_boiler", "Gas boiler"), ("h2_boiler", "Hydrogen boiler"),
             ("hp_air", "Heat pump (air)"), ("hp_ground", "Heat pump (ground)")]
    v25 = [med(t, 2025) for t, _ in techs]; v50 = [med(t, 2050) for t, _ in techs]
    x = np.arange(len(techs)); w = 0.38
    fig, ax = plt.subplots(figsize=(7.8, 4.6))
    ax.bar(x - w/2, v25, w, label="2025", color="#9ecae1")
    b = ax.bar(x + w/2, v50, w, label="2050", color="#08519c")
    for xi, val in zip(x + w/2, v50):
        ax.text(xi, val + 3, f"{val:.0f}", ha="center", fontweight="bold", fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels([n for _, n in techs])
    ax.set_ylabel("Levelised cost of heat (€/MWh useful)")
    ax.set_title("Levelised cost of heat by technology, EU median")
    ax.legend(frameon=False)
    fig.savefig(OUT / "F3_lcoh_by_tech.png"); plt.close(fig)


def f4_gap():
    g = pd.read_csv(RESULTS_DIR / "h2_supply_scenario.csv").sort_values("gap_central")
    cols = ["#2ca02c" if v <= 0 else ("#d62728" if v > 60 else "#ff7f0e") for v in g.gap_central]
    fig, ax = plt.subplots(figsize=(7.6, 8.2))
    y = np.arange(len(g))
    ax.barh(y, g.gap_central, color=cols, height=0.74)
    ax.set_yticks(y); ax.set_yticklabels(g.country, fontsize=8)
    ax.axvline(0, color="#333", lw=1)
    for yi, v in zip(y, g.gap_central):
        ax.text(v + (1 if v >= 0 else -1), yi, f"{v:+.0f}", va="center",
                ha="left" if v >= 0 else "right", fontsize=7.5)
    ax.set_xlabel("Hydrogen-boiler minus best heat-pump LCOH, 2050 (€/MWh)")
    ax.set_title("Hydrogen-boiler minus heat-pump cost by country (2050)")
    fig.savefig(OUT / "F4_h2_vs_hp_gap.png"); plt.close(fig)


def f5_costopt():
    co = pd.read_csv(RESULTS_DIR / "mc_summary_COST_OPT_90.csv")
    sh = {r.tech: r.q50 for _, r in co[(co.year == 2050) & (co.variable == "tech_share")].iterrows()}
    seg = [("Heat pump", sh.get("hp_air", 0) + sh.get("hp_ground", 0), "#08519c"),
           ("District heat", sh.get("district_heat", 0), "#e6550d"),
           ("Hydrogen", sh.get("h2_boiler", 0), "#6a51a3"),
           ("Fossil / biomass", sh.get("gas_boiler", 0) + sh.get("oil_boiler", 0) + sh.get("biomass_boiler", 0), "#969696")]
    fig, ax = plt.subplots(figsize=(9.2, 2.4)); left = 0
    for lbl, val, col in seg:
        ax.barh(0, val * 100, left=left * 100, color=col, edgecolor="white")
        if val > 0.03:
            ax.text((left + val / 2) * 100, 0, f"{lbl}\n{val*100:.0f}%", ha="center",
                    va="center", color="white", fontweight="bold", fontsize=10)
        left += val
    # annotate the ~0% techs below the bar
    ax.text(100, -0.62, "Hydrogen ≈ 0%   ·   fossil/biomass ≈ 0%", ha="right", va="top",
            fontsize=9, color="#444")
    ax.set_xlim(0, 100); ax.set_ylim(-0.7, 0.5); ax.axis("off")
    ax.set_title("Cost-optimal 2050 heating mix (−90% scope-1 cap)")
    fig.savefig(OUT / "F5_costopt_mix.png"); plt.close(fig)


def f6_infra():
    inf = pd.read_csv(RESULTS_DIR / "h2_infra_scenario.csv")
    means = [("Free gas-grid\nreuse", inf.gap_baseline.mean(), "#9ecae1"),
             ("+ retrofit\nthe grid", inf.gap_convert_central.mean(), "#fdae6b"),
             ("+ build a\nnew grid", inf.gap_newbuild_central.mean(), "#de2d26")]
    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    xs = np.arange(len(means))
    ax.bar(xs, [m[1] for m in means], color=[m[2] for m in means], width=0.6)
    for xi, m in zip(xs, means):
        ax.text(xi, m[1] + 0.7, f"€{m[1]:.0f}", ha="center", fontweight="bold")
    ax.set_xticks(xs); ax.set_xticklabels([m[0] for m in means])
    ax.set_ylabel("EU-mean H₂ − heat-pump gap, 2050 (€/MWh)")
    ax.set_title("Hydrogen-boiler cost gap by delivery scenario (2050)")
    fig.savefig(OUT / "F6_h2_infra_ladder.png"); plt.close(fig)


def f7_hotmaps():
    b = pd.read_csv(RESULTS_DIR / "benchmark_multi.csv").sort_values("gap_vs_hotmaps_pct")
    g = b.gap_vs_hotmaps_pct
    cols = ["#2ca02c" if abs(v) <= 15 else ("#ff7f0e" if abs(v) <= 25 else "#d62728") for v in g]
    fig, ax = plt.subplots(figsize=(7.6, 8.4)); y = np.arange(len(b))
    ax.axvspan(-15, 15, color="#2ca02c", alpha=0.08); ax.axvspan(-25, -15, color="#ff7f0e", alpha=0.07)
    ax.axvspan(15, 25, color="#ff7f0e", alpha=0.07)
    ax.barh(y, g, color=cols, height=0.74); ax.axvline(0, color="#333", lw=1)
    ax.set_yticks(y); ax.set_yticklabels(b.country, fontsize=8)
    for yi, v in zip(y, g):
        ax.text(v + (1 if v >= 0 else -1), yi, f"{v:+.0f}%", va="center",
                ha="left" if v >= 0 else "right", fontsize=7)
    ax.set_xlabel("Bottom-up model minus Hotmaps benchmark (% of Hotmaps)")
    ax.set_title("Heat-demand validation: model vs Hotmaps, by country")
    fig.savefig(OUT / "F7_model_vs_hotmaps.png"); plt.close(fig)


def f8_scenarios_by_country():
    order4 = ["CURRENT_POLICIES", "STATED_POLICIES", "NET_ZERO", "H2_PUSH"]  # all four (was 3)
    dem = {}
    for sc in order4:
        d = pd.read_csv(RESULTS_DIR / f"mc_country_{sc}.csv")
        d = d[(d.variable == "useful_heat_TWh") & (d.year == 2050)]
        dem[sc] = dict(zip(d.country, d.q50))
    countries = sorted(dem["STATED_POLICIES"], key=lambda c: dem["STATED_POLICIES"][c], reverse=True)
    y = np.arange(len(countries)); h = 0.2
    fig, ax = plt.subplots(figsize=(8.2, 10.5))
    for i, sc in enumerate(order4):
        ax.barh(y + (1.5 - i) * h, [dem[sc][c] for c in countries], h,
                color=SC[sc], label=short_scen(sc))
    ax.set_yticks(y); ax.set_yticklabels(countries, fontsize=8); ax.invert_yaxis()
    ax.set_xlabel("2050 useful heat demand (TWh)\n(15 largest countries · 91% of EU-27+UK+CH heat demand)")
    ax.set_title("Heat demand by country and scenario, 2050")
    ax.legend(frameon=False, loc="lower right", ncol=2)
    ax.grid(axis="x", color="#ececec", lw=0.8); ax.set_axisbelow(True)
    fig.savefig(OUT / "F8_scenarios_by_country.png"); fig.savefig(OUT / "F8_scenarios_by_country.pdf")
    plt.close(fig)


def f9_lcoh_by_country():
    e = pd.read_csv(RESULTS_DIR / "country_econ_table.csv").dropna(subset=["lcoh_bestHP_2050"])
    e = e.sort_values("lcoh_bestHP_2050")
    y = np.arange(len(e)); h = 0.26
    fig, ax = plt.subplots(figsize=(8.2, 10.5))
    ax.barh(y + h, e.lcoh_H2_2050, h, color="#6a51a3", label="Hydrogen boiler")
    ax.barh(y, e.lcoh_gas_2050, h, color="#969696", label="Gas boiler")
    ax.barh(y - h, e.lcoh_bestHP_2050, h, color="#08519c", label="Best heat pump")
    ax.set_yticks(y); ax.set_yticklabels(e.country, fontsize=8); ax.invert_yaxis()
    ax.set_xlabel("LCOH, 2050 (€/MWh useful heat)")
    ax.set_title("Levelised cost of heat by country, 2050")
    ax.legend(frameon=False, loc="lower right")
    fig.savefig(OUT / "F9_lcoh_by_country.png"); plt.close(fig)


if __name__ == "__main__":
    for f in (f1_demand, f2_co2, f3_lcoh, f4_gap, f5_costopt, f6_infra,
              f7_hotmaps, f8_scenarios_by_country, f9_lcoh_by_country):
        f(); print(f"  wrote {f.__name__}")
    print(f"All figures in {OUT}")
