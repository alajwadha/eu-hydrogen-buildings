"""New explanatory figures for the LMDI / four-scenario results.

These are NOT the old paper figures (archived in paper/figs/old/); they are
designed to communicate the core ideas of the current model:

  fig_three_layer_decomposition  - why -9% demand becomes -98% CO2
                                    (source / efficiency / cleanness)
  fig_grid_attribution           - how much of -98% is switching vs grid cleanness
  fig_rho_sensitivity            - how the EU demand band depends on cross-country
                                    renovation correlation rho
  fig_h2_hp_gap                  - RQ1 quantified: per-country H2-vs-HP LCOH gap
  fig_lmdi_backcast_drivers      - why EU demand is ~flat 2015->2025 (if data present)

Run:  cd code && PYTHONPATH=. python -m scripts.explanatory_figures
Out:  paper/figs/fig_*.pdf  (+ .png)
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
FIGS = ROOT / "paper" / "figs"
FIGS.mkdir(parents=True, exist_ok=True)

set_style()   # autolayout + savefig bbox='tight' (no overlap); presentation sizes below
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 12.5, "axes.titleweight": "bold", "figure.dpi": 120,
})
C = {"demand": "#4c78a8", "efficiency": "#f58518", "emissions": "#54a24b",
     "switch": "#4c78a8", "clean": "#54a24b", "ref": "#1f77b4",
     "high": "#2ca02c", "h2": "#ff7f0e", "bar": "#4c78a8", "accent": "#d62728"}


def _save(fig, name):
    fig.savefig(FIGS / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(FIGS / f"{name}.png", bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"  wrote {name}.pdf/.png")


def fig_three_layer():
    s = pd.read_csv(RES / "mc_summary_STATED_POLICIES.csv")
    u = s[s.variable == "useful_heat_MWh"].groupby("year")["q50"].sum() / 1e6
    f = s[s.variable == "final_energy_MWh"].groupby("year")["q50"].sum() / 1e6
    e = pd.read_csv(RES / "mc_emissions_STATED_POLICIES.csv")
    co2 = e[e.variable == "co2_MtCO2"].groupby("year")["q50"].sum()
    layers = [
        ("Useful heat demand\n(building's physical need)", u[2025], u[2050], "TWh", C["demand"]),
        ("Final / delivered energy\n(efficiency: heat-pump COP)", f[2025], f[2050], "TWh", C["efficiency"]),
        ("CO2 emissions\n(source switch + grid cleanness)", co2[2025], co2[2050], "MtCO2", C["emissions"]),
    ]
    fig, ax = plt.subplots(figsize=(9.2, 4.4))
    ypos = np.arange(len(layers))[::-1]
    for y, (lab, v25, v50, unit, col) in zip(ypos, layers):
        pct = (v50 / v25 - 1) * 100
        fill = v50 / v25 * 100
        ax.barh(y, 100, color="#e8e8e8", height=0.55, zorder=1)
        ax.barh(y, fill, color=col, height=0.55, zorder=2)
        # label to the RIGHT of the grey track, so narrow bars never overlap
        ax.text(101.5, y, f"{pct:+.0f}%   {v25:,.0f}{chr(8594)}{v50:,.0f} {unit}",
                va="center", ha="left", fontweight="bold", color=col, fontsize=9.5)
        ax.text(-2, y, lab, va="center", ha="right", fontsize=10)
    ax.set_xlim(0, 100); ax.set_yticks([]); ax.set_xlabel("2050 level as % of 2025")
    ax.set_title("Demand, efficiency and supply drivers of 2050 emissions (Stated Policies)")
    ax.set_xticks([0, 25, 50, 75, 100])
    fig.text(0.5, -0.02, "EU+CH+UK, Monte Carlo median. Useful heat is the design need; "
             "final energy = useful / system efficiency (1.00->1.57); CO2 from carrier mix x grid intensity.",
             ha="center", fontsize=8, color="#555")
    _save(fig, "fig_three_layer_decomposition")


def fig_grid_attribution():
    g = pd.read_csv(RES / "grid_sensitivity_summary.csv").iloc[0]
    e25 = g.co2_2025_Mt; frozen = g.co2_2050_frozen_grid_Mt; actual = g.co2_2050_actual_Mt
    sw = g.switching_demand_Mt; cl = g.grid_dh_cleanness_Mt
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    # waterfall
    xs = [0, 1, 2, 3]
    ax.bar(0, e25, color="#888", width=0.6)
    ax.text(0, e25 + 8, f"{e25:.0f}", ha="center", fontweight="bold")
    ax.bar(1, sw, bottom=frozen, color=C["switch"], width=0.6)
    ax.text(1, frozen + sw / 2, f"-{sw:.0f}\nswitching\n+ demand\n({g.switching_pct_of_fall:.0f}%)",
            ha="center", va="center", color="white", fontsize=9, fontweight="bold")
    ax.bar(2, frozen, color="#bbb", width=0.6, hatch="//", edgecolor="white")
    ax.text(2, frozen + 8, f"{frozen:.0f}", ha="center", fontweight="bold")
    ax.bar(3, cl, bottom=actual, color=C["clean"], width=0.6)
    ax.text(3, actual + cl / 2, f"-{cl:.0f}\ngrid + DH\ncleanness\n({g.cleanness_pct_of_fall:.0f}%)",
            ha="center", va="center", color="white", fontsize=9, fontweight="bold")
    ax.bar(3.0, actual, color=C["emissions"], width=0.6)
    ax.text(3.0, actual + 8, f"{actual:.0f}", ha="center", fontweight="bold", color=C["emissions"])
    ax.set_xticks(xs)
    ax.set_xticklabels(["2025\nemissions", "fuel\nswitching", "2050 on a\n2025-vintage grid",
                        "2050\nactual"], fontsize=9.5)
    ax.set_ylabel("Buildings CO2 (MtCO2/yr)")
    ax.set_title("Technology switching vs grid cleanness in the 2050 emissions decline")
    ax.axhline(0, color="#333", lw=0.8)
    fig.text(0.5, -0.03, "STATED_POLICIES, EU+CH+UK. 'Frozen grid' holds 2050 electricity and district-heat carbon "
             "intensity at 2025 levels with the same 2050 technology mix. Even then emissions fall 66%.",
             ha="center", fontsize=8, color="#555")
    _save(fig, "fig_grid_attribution")


def fig_rho_sensitivity():
    d = pd.read_csv(RES / "rho_sensitivity.csv")
    scs = ["CURRENT_POLICIES","STATED_POLICIES","NET_ZERO","H2_PUSH"]
    cols = {"CURRENT_POLICIES": "#7f7f7f", "STATED_POLICIES": C["ref"], "NET_ZERO": C["high"], "H2_PUSH": C["h2"]}
    rhos = sorted(d.rho.unique())
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    width = 0.22
    xbase = np.arange(len(rhos))
    for i, sc in enumerate(scs):
        sub = d[d.scenario == sc].set_index("rho")
        x = xbase + (i - 1) * width
        q50 = [sub.loc[r, "q50"] for r in rhos]
        lo = [sub.loc[r, "q50"] - sub.loc[r, "q10"] for r in rhos]
        hi = [sub.loc[r, "q90"] - sub.loc[r, "q50"] for r in rhos]
        ax.errorbar(x, q50, yerr=[lo, hi], fmt="o", color=cols[sc], capsize=5,
                    lw=2, markersize=7, label=sc)
    ax.set_xticks(xbase); ax.set_xticklabels([f"rho = {r:g}" for r in rhos])
    ax.set_ylabel("EU 2050 useful heat demand (TWh)")
    ax.set_title("EU demand uncertainty vs cross-country renovation correlation")
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    ax.annotate("independent\n(diversified away)", (0, d[(d.scenario=='STATED_POLICIES')&(d.rho==0)].q90.iloc[0]),
                xytext=(0, 3700), fontsize=8, ha="center", color="#555")
    fig.text(0.5, -0.08, "Bars: 10th-90th percentile. rho=0 independent draws understate the band; "
             "rho=0.5 (shipped, ~2.2x wider) reflects common EU policy; rho=1 full correlation (~3x).",
             ha="center", fontsize=8, color="#555")
    _save(fig, "fig_rho_sensitivity")


def fig_h2_gap():
    d = pd.read_csv(RES / "h2_hp_gap.csv").sort_values("gap_2050")
    fig, ax = plt.subplots(figsize=(7.2, 8.0))
    y = np.arange(len(d))[::-1]
    norm = plt.Normalize(d.elec_price_2030.min(), d.elec_price_2030.max())
    cmap = plt.cm.viridis_r
    colors = cmap(norm(d.elec_price_2030.values))
    ax.barh(y, d.gap_2050.values, color=colors)
    ax.axvline(0, color=C["accent"], lw=1.4, ls="--")
    ax.text(0.5, len(d) - 0.5, "heat-pump\nparity", color=C["accent"], fontsize=8, va="top")
    ax.set_yticks(y); ax.set_yticklabels(d.country.values, fontsize=8)
    ax.set_xlabel("H2 boiler minus best heat pump, 2050 LCOH (EUR/MWh_useful)")
    ax.set_title("Hydrogen-boiler minus heat-pump cost by country (2050)")
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm); sm.set_array([])
    cb = fig.colorbar(sm, ax=ax, pad=0.02, fraction=0.04)
    cb.set_label("2030 residential electricity price (EUR/MWh)", fontsize=8)
    fig.text(0.5, 0.03, "CENTRAL H2 trajectory. Hydrogen leads in seven markets by 2050, driven by Europe's "
             "highest residential electricity price plus high gas-grid coverage. EU mean gap ~30 EUR/MWh.",
             ha="center", fontsize=8, color="#555")
    _save(fig, "fig_h2_hp_gap")


def fig_lmdi_drivers():
    f = RES / "lmdi_design_drivers.csv"
    fd = RES / "lmdi_design.csv"
    if not (f.exists() and fd.exists()):
        print("  [skip] lmdi driver CSVs not found")
        return
    try:
        drv = pd.read_csv(f).set_index("country")
        des = pd.read_csv(fd)
        des = des[des.country != "EU"].set_index("country")
        m25 = des["model_2025_corrected"].values
        m15 = des["model_2015_corrected"].values
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = np.where((m15 > 0) & (m25 > 0) & (np.abs(m25 - m15) > 1e-9), m15 / m25, np.nan)
            L = np.where(np.isnan(ratio), m25, (m15 - m25) / np.log(ratio))
        cols = ["dlnQ_pop", "dlnQ_occupancy", "dlnQ_size", "dlnQ_intensity"]
        labels = ["Population", "Occupancy\n(Dw/Pop)", "Dwelling\nsize", "Design\nintensity"]
        vals = [-(L * drv.loc[des.index, col].values).sum() for col in cols]
    except Exception as ex:
        print(f"  [skip] lmdi drivers: {ex}")
        return
    net = sum(vals)
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    cum = 0.0
    for i, (lab, v) in enumerate(zip(labels, vals)):
        col = C["emissions"] if v >= 0 else C["accent"]
        ax.bar(i, v, bottom=cum, color=col, width=0.6)
        ax.text(i, cum + v + (4 if v >= 0 else -4), f"{v:+.0f}", ha="center",
                va="bottom" if v >= 0 else "top", fontsize=9, fontweight="bold")
        cum += v
    ax.bar(len(vals), net, color="#555", width=0.6)
    ax.text(len(vals), net + 4, f"net\n{net:+.0f}", ha="center", fontsize=9, fontweight="bold")
    ax.axhline(0, color="#333", lw=0.8)
    ax.set_xticks(range(len(vals) + 1)); ax.set_xticklabels(labels + ["Net\nDelta"])
    ax.set_ylabel("Contribution to EU-27+UK+CH demand change\n2015 -> 2025 (TWh)")
    ax.set_title("Drivers of EU-27+UK+CH heat demand, 2015-2025")
    fig.text(0.5, -0.03, "LMDI additive decomposition (design basis). Stock-side drivers (population, "
             "shrinking households) push demand up; envelope renovation pulls it down by a similar amount.",
             ha="center", fontsize=8, color="#555")
    _save(fig, "fig_lmdi_backcast_drivers")


def main():
    print("Generating explanatory figures into paper/figs/ ...")
    fig_three_layer()
    fig_grid_attribution()
    fig_rho_sensitivity()
    fig_h2_gap()
    fig_lmdi_drivers()
    print("Done.")


if __name__ == "__main__":
    main()
