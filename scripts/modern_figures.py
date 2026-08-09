"""Ten modern, editorial-style figures for the EU hydrogen-buildings model.

Each uses a distinct, contemporary chart idiom (slopegraph, bubble plot,
lollipop, streamgraph, dumbbell, diverging bars, heatmap, radial bars,
small-multiple fans, connected-scatter) under one design system: a restrained
palette, direct labelling instead of legend boxes, de-emphasised context, and a
left-aligned title + subtitle + source treatment.

Run:  cd code && PYTHONPATH=. python -m scripts.modern_figures
Out:  paper/figs/fig_m*.pdf (+ .png)
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch
from scripts._figstyle import short_scen

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "code" / "results"
CFG = ROOT / "code" / "data" / "country_config"
FIGS = ROOT / "paper" / "figs"
FIGS.mkdir(parents=True, exist_ok=True)

# ── design system ────────────────────────────────────────────────────────────
INK, SUB, FAINT, GRID = "#1b2330", "#6b7480", "#aab2bd", "#edeff2"
PAL = ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51",
       "#6d597a", "#3a7ca5", "#8ab17d"]
ACCENT, TEAL, NAVY, MUTE = "#e76f51", "#2a9d8f", "#264653", "#c4cad2"
TECH_COL = {"hp_air": "#3a7ca5", "hp_ground": "#264653", "district_heat": "#6d597a",
            "biomass_boiler": "#8ab17d", "h2_boiler": "#e76f51", "gas_boiler": "#b8c0c9",
            "oil_boiler": "#7d868f", "resistance_heater": "#83b9c9"}
TECH_LAB = {"hp_air": "HP air", "hp_ground": "HP ground", "district_heat": "District heat",
            "biomass_boiler": "Biomass", "h2_boiler": "Hydrogen", "gas_boiler": "Gas",
            "oil_boiler": "Oil", "resistance_heater": "Resistance"}
SC = ["CURRENT_POLICIES","STATED_POLICIES","NET_ZERO","H2_PUSH"]
SC_COL = {"CURRENT_POLICIES": "#8d99ae", "STATED_POLICIES": "#3a7ca5", "NET_ZERO": "#2a9d8f", "H2_PUSH": "#e76f51"}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10.5, "text.color": INK,
    "axes.edgecolor": FAINT, "axes.linewidth": 0.8, "axes.labelcolor": SUB,
    "xtick.color": SUB, "ytick.color": SUB, "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5, "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 120, "savefig.facecolor": "white", "figure.facecolor": "white",
})


def dress(fig, title, subtitle, source=None, tx=0.025, ty=0.975):
    fig.text(tx, ty, title, fontsize=15.5, fontweight="bold", color=INK, va="top")
    fig.text(tx, ty - 0.052, subtitle, fontsize=10.3, color=SUB, va="top")
    if source:
        fig.text(tx, 0.012, source, fontsize=8, color=FAINT, va="bottom")


def grid_y(ax):
    ax.grid(axis="y", color=GRID, lw=0.9, zorder=0)
    ax.set_axisbelow(True)


def grid_x(ax):
    ax.grid(axis="x", color=GRID, lw=0.9, zorder=0)
    ax.set_axisbelow(True)


def save(fig, name):
    fig.savefig(FIGS / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(FIGS / f"{name}.png", bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"  wrote {name}")


# ── M1  slopegraph: H2-HP gap 2030 -> 2050 ───────────────────────────────────
def m1_slope():
    d = pd.read_csv(RES / "h2_hp_gap.csv")
    hi = {"DE", "NL", "BE", "DK", "PL"}
    fig, ax = plt.subplots(figsize=(7.6, 8.2))
    for _, r in d.iterrows():
        c = r.country
        col = ACCENT if c == "DE" else (NAVY if c in hi else MUTE)
        lw = 2.4 if c in hi else 1.0
        z = 3 if c in hi else 1
        ax.plot([0, 1], [r.gap_2030, r.gap_2050], "-", color=col, lw=lw, zorder=z,
                alpha=1 if c in hi else 0.6)
        ax.scatter([0, 1], [r.gap_2030, r.gap_2050], s=18 if c in hi else 9,
                   color=col, zorder=z + 1)
        if c in hi or r.gap_2050 > 60 or r.gap_2030 < 20:
            ax.text(1.02, r.gap_2050, f"{c} {r.gap_2050:.0f}", color=col, fontsize=8.5,
                    va="center", fontweight="bold" if c in hi else "normal")
            ax.text(-0.02, r.gap_2030, c, color=col, fontsize=8.5, va="center", ha="right")
    ax.axhline(0, color=INK, lw=1, ls=(0, (4, 3)))
    ax.text(0.5, 2, "heat-pump parity", color=INK, fontsize=8.5, ha="center")
    ax.set_xlim(-0.18, 1.2); ax.set_xticks([0, 1]); ax.set_xticklabels(["2030", "2050"], fontsize=11)
    ax.set_ylabel("H₂ boiler − best heat pump  (€/MWh useful)")
    for s in ["top", "right", "bottom"]:
        ax.spines[s].set_visible(False)
    dress(fig, "Hydrogen's cost gap to heat pumps narrows — but closes in seven markets (BE, DE, DK, IE, NL, PL, UK)",
          "Per-country LCOH gap, CENTRAL hydrogen trajectory. Highlighted: the narrow-gap cluster.",
          "Model output. Gap = H₂ boiler LCOH minus the cheaper of air-/ground-source heat pump.")
    save(fig, "fig_m01_slope_h2gap")


# ── M2  bubble: RQ1 drivers ──────────────────────────────────────────────────
def m2_bubble():
    d = pd.read_csv(RES / "h2_hp_gap.csv")
    fig, ax = plt.subplots(figsize=(9.0, 6.2))
    grid_y(ax)
    sizes = 60 + d.gas_grid_coverage * 900
    sc = ax.scatter(d.elec_price_2030, d.gap_2050, s=sizes, c=d.gap_2050,
                    cmap="RdYlGn_r", edgecolor="white", lw=1.1, zorder=3, alpha=0.92)
    for _, r in d.iterrows():
        ax.text(r.elec_price_2030, r.gap_2050 + 2.2, r.country, fontsize=8, ha="center",
                color=INK, zorder=4)
    ax.axhline(0, color=INK, lw=1, ls=(0, (4, 3)))
    ax.text(d.elec_price_2030.max(), 1.5, "heat-pump parity", color=INK, fontsize=8.5, ha="right")
    ax.set_xlabel("2030 residential electricity price  (€/MWh)")
    ax.set_ylabel("H₂ − best heat pump, 2050  (€/MWh)")
    # legend for bubble size
    for cov, lab in [(0.2, "20%"), (0.6, "60%"), (0.9, "90%")]:
        ax.scatter([], [], s=60 + cov * 900, c="#cfd6dd", edgecolor="white",
                   label=f"gas grid {lab}")
    ax.legend(frameon=False, loc="upper right", labelspacing=1.4, borderpad=1,
              fontsize=8.5, title="bubble = gas-grid coverage", title_fontsize=8.5)
    dress(fig, "Where hydrogen competes: high power prices and dense gas grids",
          "Each bubble a country; lower is closer to heat-pump parity. Colour repeats the gap.",
          "Model output, CENTRAL hydrogen. Bubble area ∝ household gas-grid coverage (ACER).")
    save(fig, "fig_m02_bubble_rq1")


# ── M3  lollipop: envelope renovation rate ───────────────────────────────────
def m3_lollipop():
    d = pd.read_csv(CFG / "scenario_intensity_rates.csv")
    s = d[d.scenario == "STATED_POLICIES"].set_index("country")["central_pct_yr"].sort_values()
    fig, ax = plt.subplots(figsize=(7.2, 8.2))
    grid_x(ax)
    y = np.arange(len(s))
    norm = plt.Normalize(s.min(), s.max())
    cols = plt.cm.viridis(norm(s.values))
    ax.hlines(y, 0, s.values, color="#dfe3e8", lw=2.2, zorder=1)
    ax.scatter(s.values, y, color=cols, s=70, zorder=2, edgecolor="white", lw=1)
    for i, (c, v) in enumerate(s.items()):
        ax.text(v + 0.03, i, f"{v:.2f}", va="center", fontsize=8, color=SUB)
    ax.set_yticks(y); ax.set_yticklabels(s.index, fontsize=8.5)
    ax.set_xlabel("STATED_POLICIES envelope-design intensity decline  (%/yr)")
    ax.margins(x=0.12)
    dress(fig, "The scenario lever: how fast each country's stock improves",
          "STATED_POLICIES renovation pace per country. NET_ZERO scales every value ×2.73, H2_PUSH ×1.64.",
          "Derived from JRC depth bands; see scenario_intensity_rates.csv. FI slowest, CH fastest.")
    save(fig, "fig_m03_lollipop_envelope")


# ── M4  streamgraph: EU tech mix evolution (STATED_POLICIES) ─────────────────────────────
def m4_stream():
    d = pd.read_csv(RES / "mc_summary_STATED_POLICIES.csv")
    ts = d[d.variable == "tech_share"].pivot_table(index="year", columns="tech",
                                                    values="q50", aggfunc="mean")
    yrs = np.array([2025, 2030, 2040, 2050]); ts = ts.reindex(yrs)
    techs = [t for t in TECH_COL if t in ts.columns]
    # smooth via interpolation for a stream look
    xs = np.linspace(2025, 2050, 200)
    smooth = {t: np.interp(xs, yrs, ts[t].values * 100) for t in techs}
    fig, ax = plt.subplots(figsize=(9.0, 5.6))
    ax.stackplot(xs, *[smooth[t] for t in techs], colors=[TECH_COL[t] for t in techs],
                 baseline="zero")
    # direct labels at 2050
    cum = 0
    for t in techs:
        v = ts[t].iloc[-1] * 100
        if v > 3:
            ax.text(2050.4, cum + v / 2, f"{TECH_LAB[t]}", va="center", fontsize=8.8,
                    color=TECH_COL[t], fontweight="bold")
        cum += v
    ax.set_xlim(2025, 2056); ax.set_ylim(0, 100)
    ax.set_ylabel("Share of useful heat  (%)"); ax.set_xticks(yrs)
    for sname in ["left"]:
        ax.spines[sname].set_visible(False)
    dress(fig, "Reference pathway: heat pumps and district heat take the stock",
          "EU+CH+UK technology mix, STATED_POLICIES scenario, Monte Carlo median.",
          "Model output. Gas falls to zero by 2050 under EPBD boiler bans; hydrogen stays a minor share.")
    save(fig, "fig_m04_stream_techmix")


# ── M5  dumbbell: LCOH by technology 2025 -> 2050 ────────────────────────────
def m5_dumbbell():
    from src.Economics import compute_lcoh
    countries = pd.read_csv(CFG / "scenario_intensity_rates.csv").country.unique()
    techs = ["h2_boiler", "biomass_boiler", "gas_boiler", "district_heat", "hp_air", "hp_ground"]
    med = {y: {} for y in (2025, 2050)}
    for y in (2025, 2050):
        for t in techs:
            v = [compute_lcoh(t, c, y) for c in countries]
            med[y][t] = float(np.median(v))
    order = sorted(techs, key=lambda t: med[2050][t])
    fig, ax = plt.subplots(figsize=(8.6, 5.2))
    grid_x(ax)
    yv = np.arange(len(order))
    for i, t in enumerate(order):
        a, b = med[2025][t], med[2050][t]
        ax.plot([b, a], [i, i], color="#dfe3e8", lw=3, zorder=1, solid_capstyle="round")
        ax.scatter(a, i, color=MUTE, s=70, zorder=2, edgecolor="white", lw=1)
        ax.scatter(b, i, color=TEAL, s=80, zorder=3, edgecolor="white", lw=1)
        ax.text(b - 4, i, f"{b:.0f}", va="center", ha="right", fontsize=8.5, color=NAVY, fontweight="bold")
        ax.text(a + 4, i, f"{a:.0f}", va="center", ha="left", fontsize=8.5, color=SUB)
    ax.set_yticks(yv); ax.set_yticklabels([TECH_LAB[t] for t in order], fontsize=10)
    ax.set_xlabel("Levelised cost of heat  (€/MWh useful, EU median)")
    ax.scatter([], [], color=MUTE, s=70, label="2025"); ax.scatter([], [], color=TEAL, s=80, label="2050")
    ax.legend(frameon=False, loc="lower right", fontsize=9)
    ax.margins(x=0.1)
    dress(fig, "Heat pumps are the cheapest heat in 2025 — and pull further ahead",
          "EU-median LCOH by technology; dots show the move from 2025 to 2050.",
          "Model output, CENTRAL carbon + hydrogen. Hydrogen falls most but stays well above heat pumps.")
    save(fig, "fig_m05_dumbbell_lcoh")


# ── M6  diverging lollipop: country demand change ────────────────────────────
def m6_diverging():
    d = pd.read_csv(RES / "mc_country_STATED_POLICIES.csv")
    s = d[(d.variable == "useful_heat_TWh") & (d.tech == "all")]
    piv = s.pivot_table(index="country", columns="year", values="q50")
    chg = ((piv[2050] / piv[2025] - 1) * 100).sort_values()
    fig, ax = plt.subplots(figsize=(7.2, 8.2))
    grid_x(ax)
    y = np.arange(len(chg))
    cols = [TEAL if v < 0 else ACCENT for v in chg.values]
    ax.hlines(y, 0, chg.values, color="#e3e7eb", lw=2, zorder=1)
    ax.scatter(chg.values, y, color=cols, s=60, zorder=2, edgecolor="white", lw=1)
    for i, (c, v) in enumerate(chg.items()):
        ax.text(v + (0.6 if v >= 0 else -0.6), i, f"{v:+.0f}", va="center",
                ha="left" if v >= 0 else "right", fontsize=7.6, color=SUB)
    ax.axvline(0, color=INK, lw=1)
    ax.set_yticks(y); ax.set_yticklabels(chg.index, fontsize=8.3)
    ax.set_xlabel("Useful heat demand change 2025 → 2050  (%, STATED_POLICIES)")
    ax.margins(x=0.12)
    dress(fig, "One EU number hides 29 national stories",
          "Demand falls where retrofit outpaces stock growth (teal); rises where population/households grow (coral).",
          "Model output, STATED_POLICIES scenario. Net EU change −9%, but Ireland +, Italy/Germany −.")
    save(fig, "fig_m06_diverging_demand")


# ── M7  heatmap: country x tech 2050 share (STATED_POLICIES) ─────────────────────────────
def m7_heatmap():
    d = pd.read_csv(RES / "mc_country_STATED_POLICIES.csv")
    ts = d[(d.variable == "tech_share") & (d.year == 2050)]
    piv = ts.pivot_table(index="country", columns="tech", values="q50", aggfunc="mean") * 100
    techs = [t for t in TECH_COL if t in piv.columns]
    piv = piv[techs]
    piv = piv.loc[(piv.get("hp_air", 0) + piv.get("hp_ground", 0)).sort_values(ascending=False).index]
    fig, ax = plt.subplots(figsize=(8.6, 8.6))
    im = ax.imshow(piv.values, cmap="BuPu", aspect="auto", vmin=0, vmax=max(40, piv.values.max()))
    ax.set_xticks(range(len(techs))); ax.set_xticklabels([TECH_LAB[t] for t in techs],
                                                          rotation=35, ha="right", fontsize=9)
    ax.set_yticks(range(len(piv))); ax.set_yticklabels(piv.index, fontsize=8)
    for i in range(len(piv)):
        for j in range(len(techs)):
            v = piv.values[i, j]
            if v >= 4:
                ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=7,
                        color="white" if v > 25 else INK)
    cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    cb.set_label("share of useful heat (%)", fontsize=8.5); cb.ax.tick_params(labelsize=8)
    for s in ["top", "right", "left", "bottom"]:
        ax.spines[s].set_visible(False)
    dress(fig, "The 2050 heating map is not uniform across Europe",
          "Reference-scenario technology shares by country, sorted by heat-pump penetration.",
          "Model output. District heat clusters in the Nordics/east; biomass in forested and rural states.")
    save(fig, "fig_m07_heatmap_techmix")


# ── M8  radial bars: per-country 2050 demand ─────────────────────────────────
def m8_radial():
    d = pd.read_csv(RES / "mc_country_STATED_POLICIES.csv")
    s = d[(d.variable == "useful_heat_TWh") & (d.tech == "all") & (d.year == 2050)]
    s = s.groupby("country")["q50"].first().sort_values(ascending=False)
    n = len(s); ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
    fig = plt.figure(figsize=(8.4, 8.4)); ax = fig.add_subplot(111, polar=True)
    norm = plt.Normalize(s.min(), s.max())
    cols = plt.cm.viridis(norm(s.values))
    ax.bar(ang, s.values, width=2 * np.pi / n * 0.9, color=cols, edgecolor="white", lw=0.6)
    ax.set_theta_offset(np.pi / 2); ax.set_theta_direction(-1)
    ax.set_xticks(ang); ax.set_xticklabels([])
    ax.set_yticklabels([]); ax.spines["polar"].set_visible(False)
    ax.set_rlabel_position(0); ax.grid(color=GRID, lw=0.8)
    for a, (c, v) in zip(ang, s.items()):
        rot = np.degrees(-a) + 90 if np.pi/2 < a < 3*np.pi/2 else np.degrees(-a) - 90
        ha = "left"
        lab_a = a
        deg = np.degrees(a)
        rotation = 90 - deg if deg <= 180 else 270 - deg
        ax.text(a, v + s.max() * 0.06, c, rotation=rotation, rotation_mode="anchor",
                ha="center", va="center", fontsize=7.3, color=INK)
    dress(fig, "Demand is concentrated: a few large countries dominate the EU total",
          "2050 useful heat demand by country (TWh), STATED_POLICIES — radial bars, longest = largest.",
          "Model output. Germany, France, Italy, the UK and Poland account for the bulk of EU demand.",
          ty=0.985)
    save(fig, "fig_m08_radial_demand")


# ── M9  small-multiple fans: demand bands by scenario ────────────────────────
def m9_smallmult():
    fig, axes = plt.subplots(1, len(SC), figsize=(3.85 * len(SC), 4.4), sharey=True)
    for ax, sc in zip(axes, SC):
        d = pd.read_csv(RES / f"mc_summary_{sc}.csv")
        g = d[d.variable == "useful_heat_MWh"].groupby("year")[["q10", "q50", "q90"]].sum() / 1e6
        ax.fill_between(g.index, g.q10, g.q90, color=SC_COL[sc], alpha=0.18)
        ax.plot(g.index, g.q50, "-o", color=SC_COL[sc], lw=2.4, ms=4)
        ax.text(2050, g.q50.iloc[-1], f"  {g.q50.iloc[-1]:.0f}", color=SC_COL[sc],
                fontsize=10, fontweight="bold", va="center")
        ax.set_title(short_scen(sc), loc="left", fontsize=11.5, color=SC_COL[sc], fontweight="bold")
        ax.set_ylim(0, 4100); ax.set_xticks([2025, 2040, 2050]); grid_y(ax)
        for s in ["left"]:
            ax.spines[s].set_visible(False)
    axes[0].set_ylabel("EU useful heat demand (TWh/yr)")
    dress(fig, "Three policy worlds for 2050 demand",
          "Median trajectory with the 10th–90th-percentile Monte Carlo band (ρ = 0.5 correlated sampling).",
          "Model output, EU+CH+UK. Only NET_ZERO approaches the IEA Net-Zero demand-reduction range.",
          ty=0.96)
    fig.subplots_adjust(top=0.78, bottom=0.12, wspace=0.08)
    save(fig, "fig_m09_smallmult_fans")


# ── M10  connected scatter: demand-emissions decoupling ──────────────────────
def m10_decoupling():
    fig, ax = plt.subplots(figsize=(8.6, 6.2))
    grid_y(ax); grid_x(ax)
    yrs = [2025, 2030, 2040, 2050]
    for sc in SC:
        dem = pd.read_csv(RES / f"mc_summary_{sc}.csv")
        u = dem[dem.variable == "useful_heat_MWh"].groupby("year")["q50"].sum() / 1e6
        co = pd.read_csv(RES / f"mc_emissions_{sc}.csv")
        c = co[co.variable == "co2_MtCO2"].groupby("year")["q50"].sum()
        x = [u[y] for y in yrs]; yv = [c[y] for y in yrs]
        ax.plot(x, yv, "-", color=SC_COL[sc], lw=2, zorder=2, alpha=0.9)
        ax.scatter(x, yv, color=SC_COL[sc], s=30, zorder=3)
        ax.text(x[-1], yv[-1] - 12, sc, color=SC_COL[sc], fontsize=9.5, fontweight="bold",
                ha="center")
        for y, xi, yi in zip(yrs, x, yv):
            if sc == "STATED_POLICIES":
                ax.text(xi + 25, yi, str(y), fontsize=7.5, color=SUB, va="center")
    ax.scatter([3819], [585], color=INK, s=55, zorder=4)
    ax.text(3819, 600, "2025 start", fontsize=9, color=INK, ha="center", fontweight="bold")
    ax.set_xlabel("Useful heat demand  (TWh/yr)")
    ax.set_ylabel("Buildings CO₂  (MtCO₂/yr)")
    ax.set_ylim(0, 640)
    dress(fig, "Decoupling: demand barely moves while emissions fall off a cliff",
          "Each path traces a scenario through 2025–30–40–50 in demand–emissions space.",
          "Model output. Near-vertical descent = decarbonisation via supply (efficiency, fuel switch, clean grid).")
    save(fig, "fig_m10_decoupling_scatter")


def main():
    print("Generating 10 modern figures into paper/figs/ ...")
    for fn in [m1_slope, m2_bubble, m3_lollipop, m4_stream, m5_dumbbell, m6_diverging,
               m7_heatmap, m8_radial, m9_smallmult, m10_decoupling]:
        try:
            fn()
        except Exception as ex:
            import traceback
            print(f"  [skip] {fn.__name__}: {ex}")
            traceback.print_exc()
    print("Done.")


if __name__ == "__main__":
    main()
