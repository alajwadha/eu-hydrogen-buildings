"""
code/src/Visualise.py  —  Paper figures and tables (v2)
=========================================================
Professional-grade figures for the OIES working paper.
All figures follow journal conventions:
  - Consistent 10pt font, DejaVu Sans
  - Source notes on every figure
  - Proper axis labels with units
  - No chartjunk, clean gridlines
  - Colour-blind-safe palettes
  - 300 dpi PDF output

Figures:
  Fig 1: EU useful heat demand by building type (from BuildingStock.py)
  Fig 2: EU technology market shares 2025-2050, STATED_POLICIES scenario
  Fig 3: Technology transition pathways, all 3 scenarios (stacked area)
  Fig 4: EU CO2 emissions trajectory with Monte Carlo uncertainty bands
  Fig 5: LCOH by technology and country — horizontal grouped bar, 3 years
  Fig 6: Country-level tech share heatmap, 2030 vs 2050
  Fig 7: ETS2 carbon cost adder — stacked bar, gas boiler vs HP
  Fig 8: H2 competitiveness gap by country — dot plot, 4 trajectories
  Fig 9: Sensitivity tornado (requires sensitivity run)

Tables:
  Table 1: LCOH summary by tech x country group x year
  Table 2: CO2 reduction vs 2025 baseline by scenario
  Table 3: Country-level tech shares 2030 and 2050
  Table 4: ETS2 carbon cost adder by country and tech
"""
from __future__ import annotations

import sys
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "code"))

from src.Config import RESULTS_DIR, TECHS, EU_COUNTRIES
from src.Economics import (
    compute_lcoh, GAS_PRICE_BY_COUNTRY, ELEC_PRICE_BY_COUNTRY,
    H2_PRICE_TRAJECTORIES,
)
from src.Policy import (
    get_carbon_price, get_grid_carbon_intensity, BOILER_BANS,
    CARBON_PRICE_SCENARIOS,
)

FIGS_DIR = REPO_ROOT / "paper" / "figs"
TABS_DIR = REPO_ROOT / "paper" / "tables"
FIGS_DIR.mkdir(parents=True, exist_ok=True)
TABS_DIR.mkdir(parents=True, exist_ok=True)

# ── Colour palette (colour-blind-safe, Okabe-Ito inspired) ────────────────────
PALETTE = {
    "gas_boiler":        "#D55E00",   # Wong red
    "oil_boiler":        "#E69F00",   # Wong orange
    "biomass_boiler":    "#F0E442",   # Wong yellow
    "resistance_heater": "#888888",   # neutral grey
    "hp_air":            "#0072B2",   # Wong blue
    "hp_ground":         "#56B4E9",   # Wong sky
    "district_heat":     "#009E73",   # Wong green
    "h2_boiler":         "#CC79A7",   # Wong purple
}

# ── General-purpose palettes for paper figures + diagnostic plots ─────────────
# Use these for any chart that is NOT keyed to specific heating technologies.
# Both palettes are imported by 04_diagnostics.py for the LU diagnostic
# PDF, and are intended to be used directly in paper figures so that the
# diagnostic outputs and the published figures share a visual identity.
#
# WONG (Okabe-Ito) — colourblind-safe, used by Nature, Science, IPCC default.
#   Reference: Wong (2011) "Color blindness", Nature Methods 8(6):441.
# IPCC_AR6 — warmer earth-tone palette used in many energy policy papers,
#   close to the Joule house style.
WONG_PALETTE = {
    "blue":   "#0072B2",
    "orange": "#E69F00",
    "green":  "#009E73",
    "red":    "#D55E00",
    "yellow": "#F0E442",
    "purple": "#CC79A7",
    "sky":    "#56B4E9",
    "black":  "#000000",
}
WONG_ORDER = ["blue", "orange", "green", "red", "purple", "sky", "yellow", "black"]

IPCC_AR6_PALETTE = {
    "teal":   "#005F73",
    "ochre":  "#CA6702",
    "olive":  "#94A187",
    "brick":  "#AE2012",
    "sand":   "#E9C46A",
    "navy":   "#0A2540",
    "rust":   "#9B2226",
    "moss":   "#5F7367",
}
IPCC_AR6_ORDER = ["teal", "ochre", "olive", "brick", "sand", "navy", "rust", "moss"]

def get_palette(name: str = "wong") -> dict:
    """Return one of the named general-purpose palettes by lowercased name."""
    name = name.lower().strip()
    if name in ("wong", "okabe-ito", "okabe_ito", "okabe"):
        return WONG_PALETTE
    if name in ("ipcc", "ipcc_ar6", "ar6", "joule"):
        return IPCC_AR6_PALETTE
    raise ValueError(
        f"Unknown palette '{name}'. Use 'wong' (default) or 'ipcc_ar6'."
    )
TECH_LABELS = {
    "gas_boiler":        "Gas boiler",
    "oil_boiler":        "Oil boiler",
    "biomass_boiler":    "Biomass boiler",
    "resistance_heater": "Electric heater",
    "hp_air":            "Heat pump (air-source)",
    "hp_ground":         "Heat pump (ground-source)",
    "district_heat":     "District heating",
    "h2_boiler":         "Hydrogen boiler",
}
TECH_SHORT = {
    "gas_boiler":        "Gas boiler",
    "oil_boiler":        "Oil boiler",
    "biomass_boiler":    "Biomass",
    "resistance_heater": "Electric",
    "hp_air":            "HP (air)",
    "hp_ground":         "HP (ground)",
    "district_heat":     "District heat",
    "h2_boiler":         "H\u2082 boiler",
}
SCENARIO_COLORS = {
    "STATED_POLICIES":          "#0072B2",
    "NET_ZERO":      "#009E73",
    "H2_PUSH":    "#CC79A7",
    "COST_OPT_90":  "#E69F00",
    "COST_OPT_75":  "#E69F00",
    "COST_OPT_100": "#D55E00",
}
SCENARIO_LABELS = {
    "STATED_POLICIES":          "Reference",
    "NET_ZERO":      "High electrification",
    "H2_PUSH":    "Hydrogen hybrid",
    "COST_OPT_90":  "Cost-optimal (−90%)",
    "COST_OPT_75":  "Cost-optimal (−75%)",
    "COST_OPT_100": "Cost-optimal (net-zero)",
}
COUNTRY_GROUPS = {
    "Nordic":   ["SE", "FI", "DK"],
    "Western":  ["DE", "FR", "NL", "BE", "AT", "CH", "LU", "IE"],
    "Southern": ["IT", "ES", "PT", "EL", "CY", "MT"],
    "Eastern":  ["PL", "CZ", "HU", "RO", "BG", "SK", "SI", "HR",
                 "EE", "LV", "LT"],
    "UK":       ["UK"],
}

# ── Global style ──────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":           ["DejaVu Sans"],
    "font.serif":            ["Liberation Serif", "Times New Roman", "DejaVu Serif"],
    "font.size":             10,
    "axes.titlesize":        12,
    "axes.titleweight":      "bold",
    "axes.titlelocation":    "left",
    "axes.titlepad":         8,
    "axes.labelsize":        10,
    "axes.labelpad":         4,
    "axes.labelcolor":       "#333333",
    "axes.edgecolor":        "#333333",
    "axes.linewidth":        0.7,
    "axes.spines.top":       False,
    "axes.spines.right":     False,
    "axes.grid":             True,
    "axes.grid.axis":        "y",
    "grid.color":            "#dddddd",
    "grid.linewidth":        0.4,
    "grid.linestyle":        "-",
    "xtick.color":           "#333333",
    "ytick.color":           "#333333",
    "xtick.labelsize":       9,
    "ytick.labelsize":       9,
    "legend.fontsize":       9,
    "legend.frameon":        False,
    "figure.dpi":            100,
    "savefig.dpi":           300,
    "savefig.bbox":          "tight",
    "savefig.pad_inches":    0.05,
    "pdf.fonttype":          42,
    "ps.fonttype":           42,
})

# Source attribution is carried by the LaTeX figure caption in Paper v3, so
# it is no longer baked into the figure image. _source() is kept as a no-op
# so the existing call sites need not be touched (and the old bottom-of-figure
# note can no longer collide with legends).
SOURCE_NOTE = ""


def _source(fig: plt.Figure, extra: str = "") -> None:  # noqa: ARG001
    """No-op: source notes now live in the LaTeX caption (Paper v3)."""
    return


def _load_mc(scenario: str, file_type: str = "summary") -> pd.DataFrame | None:
    p = RESULTS_DIR / f"mc_{file_type}_{scenario}.csv"
    if not p.exists():
        print(f"  [skip] {p.name} not found")
        return None
    return pd.read_csv(p)


def _tech_shares_from_mc(df: pd.DataFrame, year: int) -> dict[str, float]:
    """Extract median tech shares for a given year from mc_summary."""
    ts = df[(df["variable"] == "tech_share") & (df["year"] == year)]
    result = {}
    for _, row in ts.iterrows():
        if row["tech"] in PALETTE:
            result[row["tech"]] = float(row["q50"])
    # Normalise so shares sum to 1 (avoids floating point drift)
    total = sum(result.values())
    if total > 0:
        result = {k: v / total for k, v in result.items()}
    return result


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 3 — Technology transition pathways (stacked area, 3 scenarios)
# ─────────────────────────────────────────────────────────────────────────────
def fig3_transition_pathways(scenarios: list[str] = None) -> None:
    if scenarios is None:
        scenarios = ["CURRENT_POLICIES","STATED_POLICIES","NET_ZERO","H2_PUSH"]
    # Show the cost-optimal pathway (-90% variant) as a 4th panel when available.
    if "COST_OPT_90" not in scenarios and _load_mc("COST_OPT_90") is not None:
        scenarios = list(scenarios) + ["COST_OPT_90"]

    available = [s for s in scenarios if _load_mc(s) is not None]
    if not available:
        print("  Fig 3 skipped — no MC results found")
        return

    n = len(available)
    fig, axes = plt.subplots(1, n, figsize=(5.5 * n, 4.8), sharey=True)
    if n == 1:
        axes = [axes]

    # Tech order: fossils bottom, clean top
    tech_order = [
        "gas_boiler", "oil_boiler", "biomass_boiler", "resistance_heater",
        "district_heat", "h2_boiler", "hp_ground", "hp_air",
    ]
    years = [2025, 2030, 2040, 2050]

    for ax, scenario in zip(axes, available):
        df = _load_mc(scenario)
        heat_q50 = {y: df[(df["variable"]=="useful_heat_MWh")&(df["year"]==y)]["q50"].sum()/1e6
                    for y in years}
        heat_q10 = {y: df[(df["variable"]=="useful_heat_MWh")&(df["year"]==y)]["q10"].sum()/1e6
                    for y in years}
        heat_q90 = {y: df[(df["variable"]=="useful_heat_MWh")&(df["year"]==y)]["q90"].sum()/1e6
                    for y in years}

        ts = df[df["variable"] == "tech_share"]
        bottoms = np.zeros(len(years))

        for tech in tech_order:
            tdf = ts[ts["tech"] == tech]
            if tdf.empty:
                continue
            vals = np.array([
                tdf[tdf["year"]==y]["q50"].values[0] * heat_q50[y]
                if not tdf[tdf["year"]==y].empty else 0.0
                for y in years
            ])
            ax.fill_between(years, bottoms, bottoms + vals,
                            color=PALETTE.get(tech, "#ccc"), alpha=0.88,
                            linewidth=0)
            ax.plot(years, bottoms + vals,
                    color=PALETTE.get(tech, "#ccc"), linewidth=0.4, alpha=0.6)
            bottoms = bottoms + vals

        # MC uncertainty band on total demand
        q10_arr = np.array([heat_q10[y] for y in years])
        q90_arr = np.array([heat_q90[y] for y in years])
        ax.fill_between(years, q10_arr, q90_arr,
                        alpha=0.18, color="#333333", linewidth=0,
                        label="80% MC interval")
        ax.plot(years, [heat_q50[y] for y in years],
                color="#333333", linewidth=1.2, linestyle="--", alpha=0.6)

        ax.set_title(SCENARIO_LABELS.get(scenario, scenario))
        ax.set_xlabel("Year")
        ax.set_xlim(2024, 2051)
        ax.set_xticks(years)
        ax.set_ylim(bottom=0)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}"))

    axes[0].set_ylabel("Useful heat demand (TWh/yr)")

    # Single shared legend
    handles = [mpatches.Patch(color=PALETTE[t], label=TECH_SHORT[t])
               for t in tech_order if t in PALETTE]
    handles.append(mpatches.Patch(color="#333333", alpha=0.35,
                                  label="80% MC uncertainty"))
    fig.legend(handles=handles, loc="lower center", ncol=5,
               fontsize=8.5, bbox_to_anchor=(0.5, -0.10),
               frameon=True, edgecolor="#cccccc")

    fig.suptitle(
        "EU Building Heating — Technology Transition Pathways, 2025–2050",
        fontsize=11, fontweight="bold", y=1.01)
    _source(fig, "Note: Shaded band shows 10th–90th percentile of 200 Monte Carlo draws.")
    out = FIGS_DIR / "fig3_transition_pathways.pdf"
    fig.savefig(out)
    plt.close(fig)
    print(f"  Saved: {out.name}")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 4 — CO₂ emissions trajectory with uncertainty bands
# ─────────────────────────────────────────────────────────────────────────────
def fig4_co2_trajectory(scenarios: list[str] = None) -> None:
    if scenarios is None:
        scenarios = ["CURRENT_POLICIES","STATED_POLICIES","NET_ZERO","H2_PUSH"]
    if "COST_OPT_90" not in scenarios and _load_mc("COST_OPT_90", "emissions") is not None:
        scenarios = list(scenarios) + ["COST_OPT_90"]

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    years = [2025, 2030, 2040, 2050]
    any_plotted = False

    for scenario in scenarios:
        df = _load_mc(scenario, "emissions")
        if df is None:
            continue
        co2 = df[(df["variable"] == "co2_MtCO2") & df["year"].isin(years)]
        q50 = [co2[co2["year"]==y]["q50"].sum() for y in years]
        q10 = [co2[co2["year"]==y]["q10"].sum() for y in years]
        q90 = [co2[co2["year"]==y]["q90"].sum() for y in years]
        col = SCENARIO_COLORS.get(scenario, "#888888")
        ax.plot(years, q50, color=col, linewidth=2.2, marker="o",
                markersize=6, zorder=3,
                label=SCENARIO_LABELS.get(scenario, scenario))
        ax.fill_between(years, q10, q90,
                        alpha=0.14, color=col, linewidth=0, zorder=2)
        any_plotted = True

    if not any_plotted:
        print("  Fig 4 skipped — no emissions results found")
        plt.close(fig)
        return

    # Reference lines
    ax.axhline(y=0, color="#333333", linewidth=0.6, alpha=0.5, zorder=1)
    ax.axvline(x=2027, color="#e74c3c", linewidth=1.0, linestyle=":",
               alpha=0.7, zorder=1)
    ax.text(2027.3, ax.get_ylim()[1] * 0.96, "ETS2 launch (2027)",
            color="#e74c3c", fontsize=8, va="top")

    ax.set_xlabel("Year")
    ax.set_ylabel("CO\u2082 emissions (MtCO\u2082/yr)")
    ax.set_title(
        "EU Buildings Sector CO\u2082 Emissions — Scenarios, 2025\u20132050")
    ax.set_xlim(2024, 2051)
    ax.set_xticks(years)
    ax.set_ylim(bottom=0)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}"))
    ax.legend(loc="upper right", frameon=True)

    _source(fig, "Note: Shaded band = 10th\u201390th percentile Monte Carlo interval.")
    out = FIGS_DIR / "fig4_co2_trajectory.pdf"
    fig.savefig(out)
    plt.close(fig)
    print(f"  Saved: {out.name}")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 5 — LCOH by technology and country (horizontal grouped bars)
# ─────────────────────────────────────────────────────────────────────────────
def fig5_lcoh_comparison() -> None:
    """
    Fig 5: Three-panel horizontal bar chart (one per year).
    Y = technology. X = LCOH EUR/MWh.
    Bar = median across 12 EU countries. Error bar = min-max range.
    Simple, standard, publication-ready.
    """
    focus_techs = [
        "gas_boiler", "hp_air", "hp_ground",
        "district_heat", "h2_boiler", "biomass_boiler",
    ]
    focus_countries = ["DE","FR","PL","IT","UK","SE","NL","CH",
                       "AT","BE","CZ","DK"]
    years = [2025, 2030, 2050]

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.8), sharey=False)
    fig.subplots_adjust(wspace=0.06, top=0.83, bottom=0.16, left=0.22, right=0.97)

    for ax, year in zip(axes, years):
        medians, lo_errs, hi_errs, labels, colors = [], [], [], [], []
        for tech in focus_techs:
            vals = []
            for c in focus_countries:
                try:
                    vals.append(compute_lcoh(tech, c, year))
                except Exception:
                    pass
            if not vals:
                continue
            med = float(np.median(vals))
            medians.append(med)
            lo_errs.append(med - min(vals))
            hi_errs.append(max(vals) - med)
            labels.append(TECH_SHORT.get(tech, tech))
            colors.append(PALETTE.get(tech, "#888"))

        n = len(medians)
        y = np.arange(n)

        # Bars
        ax.barh(y, medians, height=0.58, color=colors, alpha=0.86,
                linewidth=0, zorder=3)
        # Country-range error bars
        ax.errorbar(medians, y, xerr=[lo_errs, hi_errs],
                    fmt="none", color="#555", linewidth=1.0,
                    capsize=3, capthick=0.8, zorder=4)
        # Median value labels
        for yi, (v, hi) in enumerate(zip(medians, hi_errs)):
            ax.text(v + hi + 3, yi, f"\u20ac{v:.0f}",
                    va="center", ha="left", fontsize=8, color="#333")

        ax.set_xlim(0, max(m + h for m, h in zip(medians, hi_errs)) * 1.2)
        ax.set_yticks(y)
        if ax == axes[0]:
            ax.set_yticklabels(labels, fontsize=10)
        else:
            ax.set_yticklabels([""] * n)
        ax.set_xlabel("\u20ac/MWh useful heat", fontsize=9)
        ax.set_title(str(year), fontsize=12, fontweight="bold")
        ax.set_axisbelow(True)
        ax.grid(axis="x", color="#e8e8e8", linewidth=0.6)
        ax.grid(axis="y", visible=False)
        ax.invert_yaxis()

    fig.suptitle(
        "Levelised Cost of Heat by Technology, 2025 / 2030 / 2050",
        fontsize=11, fontweight="bold", y=0.98)
    fig.text(0.5, 0.92,
             "Bars = median across 12 EU countries \u00b7 "
             "Error bars = country min\u2013max range \u00b7 "
             "CENTRAL carbon scenario (\u20ac122/tCO\u2082 by 2030)",
             ha="center", fontsize=8.5, color="#555555")
    _source(fig)
    out = FIGS_DIR / "fig5_lcoh_comparison.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out.name}")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 6 — Country tech-share heatmap, 2030 vs 2050
# ─────────────────────────────────────────────────────────────────────────────
def fig6_country_heatmap(scenario: str = "STATED_POLICIES") -> None:
    df = _load_mc(scenario, "country")
    if df is None:
        print(f"  Fig 6 skipped")
        return

    ts = df[df["variable"] == "tech_share"]
    plot_techs = [
        "hp_air", "hp_ground", "district_heat", "h2_boiler",
        "gas_boiler", "oil_boiler", "biomass_boiler",
    ]
    plot_countries = [
        c for c in ["DE","FR","IT","UK","PL","ES","NL","SE","BE",
                    "CZ","AT","RO","HU","CH","DK"]
        if c in ts["country"].unique()
    ]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

    for ax, year in zip(axes, [2030, 2050]):
        matrix = np.zeros((len(plot_countries), len(plot_techs)))
        for i, country in enumerate(plot_countries):
            row_total = 0.0
            for j, tech in enumerate(plot_techs):
                r = ts[(ts["country"]==country) &
                       (ts["tech"]==tech) &
                       (ts["year"]==year)]
                v = float(r["q50"].values[0]) if not r.empty else 0.0
                matrix[i, j] = v * 100
                row_total += v
            # If row doesn't sum to 1 (floating point), rescale
            if row_total > 0.01:
                matrix[i, :] = matrix[i, :] / row_total

        im = ax.imshow(matrix, cmap="YlGnBu", aspect="auto",
                       vmin=0, vmax=65, interpolation="nearest")

        ax.set_xticks(range(len(plot_techs)))
        ax.set_xticklabels(
            [TECH_SHORT.get(t, t) for t in plot_techs],
            fontsize=8.5, rotation=35, ha="right")
        ax.set_yticks(range(len(plot_countries)))
        ax.set_yticklabels(plot_countries, fontsize=9)
        ax.set_title(f"{year}")

        # Cell annotations
        for i in range(len(plot_countries)):
            for j in range(len(plot_techs)):
                v = matrix[i, j]
                if v >= 2.0:
                    ax.text(j, i, f"{v:.0f}%", ha="center", va="center",
                            fontsize=7.5,
                            color="white" if v > 38 else "#111111",
                            fontweight="bold" if v > 30 else "normal")

        cb = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
        cb.set_label("Share of useful heat (%)", fontsize=8)
        cb.ax.tick_params(labelsize=8)

    fig.suptitle(
        f"Country-Level Technology Share of Heating — "
        f"{SCENARIO_LABELS.get(scenario, scenario)} Scenario\n"
        "Monte Carlo median (q50), % of useful heat demand",
        fontsize=11, fontweight="bold")
    _source(fig)
    out = FIGS_DIR / "fig6_country_heatmap.pdf"
    fig.savefig(out)
    plt.close(fig)
    print(f"  Saved: {out.name}")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 7 — ETS2 carbon cost adder (stacked bar, clean design)
# ─────────────────────────────────────────────────────────────────────────────
def fig7_ets2_impact() -> None:
    countries = ["DE","FR","PL","IT","NL","SE","UK","CH",
                 "AT","BE","CZ","HU","RO","ES","PT","DK"]
    focus_techs = ["gas_boiler", "hp_air"]
    year = 2030

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
    fig.subplots_adjust(top=0.82, bottom=0.22)
    subtitles = {
        "gas_boiler": "Gas boiler",
        "hp_air":     "Heat pump (air-source)",
    }

    for ax, tech in zip(axes, focus_techs):
        base_vals, adder_vals, labels = [], [], []
        for country in countries:
            try:
                with_c = compute_lcoh(tech, country, year, "CENTRAL")
                no_c   = compute_lcoh(tech, country, year, "LOW")
                base_vals.append(no_c)
                adder_vals.append(max(with_c - no_c, 0))
                labels.append(country)
            except Exception:
                continue

        x = np.arange(len(labels))
        col = PALETTE.get(tech, "#888888")

        ax.bar(x, base_vals, color=col, alpha=0.45, linewidth=0,
               label="LCOH without ETS2 (LOW carbon)")
        ax.bar(x, adder_vals, bottom=base_vals, color=col,
               alpha=0.92, linewidth=0,
               label="ETS2 carbon cost adder (CENTRAL)")

        # Annotate total on top of each bar
        for xi, (base, add) in enumerate(zip(base_vals, adder_vals)):
            total = base + add
            ax.text(xi, total + 2, f"{total:.0f}", ha="center",
                    va="bottom", fontsize=7.5, color="#333333")

        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8.5)
        ax.set_ylabel("LCOH (€/MWh useful heat)")
        ax.set_title(subtitles.get(tech, tech))
        _tops = [b + a for b, a in zip(base_vals, adder_vals)]
        ax.set_ylim(0, (max(_tops) if _tops else 1) * 1.15)
        ax.set_axisbelow(True)

    # Single shared legend below the panels (avoids overlapping the bars).
    _h, _l = axes[0].get_legend_handles_labels()
    fig.legend(_h, _l, loc="lower center", ncol=2, bbox_to_anchor=(0.5, 0.05),
               fontsize=9, frameon=False)

    fig.suptitle(
        "Impact of EU ETS2 Carbon Pricing on Levelised Cost of Heat (2030)\n"
        "CENTRAL scenario: €122/tCO\u2082; LOW scenario: €70/tCO\u2082",
        fontsize=11, fontweight="bold")
    _source(fig, "Note: Carbon adder = difference between CENTRAL and LOW carbon price scenario.")
    out = FIGS_DIR / "fig7_ets2_impact.pdf"
    fig.savefig(out)
    plt.close(fig)
    print(f"  Saved: {out.name}")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 8 — H₂ competitiveness gap (dot plot, all 4 trajectories × 4 years)
# ─────────────────────────────────────────────────────────────────────────────
def fig8_h2_threshold() -> None:
    """
    For each country: how many €/MWh does the H₂ boiler need to fall
    to match the best available HP? Negative = H₂ already cheaper.
    Panel per year, trajectory as colour.
    """
    countries = ["DE","FR","PL","IT","NL","SE","UK","CH",
                 "AT","BE","CZ","HU","RO","ES","DK"]
    years     = [2025, 2030, 2040, 2050]
    traj_cols = {
        "RAPID":    "#2ca02c",
        "CENTRAL":  "#ff7f0e",
        "SLOW":     "#d62728",
        "STRANDED": "#9467bd",
    }

    fig, axes = plt.subplots(2, 2, figsize=(13, 9), sharey=True)
    axes = axes.flat

    def get_h2_price(traj_name: str, year: int) -> float:
        traj = H2_PRICE_TRAJECTORIES[traj_name]
        ys = sorted(traj.keys())
        if year <= ys[0]:   return traj[ys[0]]
        if year >= ys[-1]:  return traj[ys[-1]]
        for i in range(len(ys)-1):
            if ys[i] <= year <= ys[i+1]:
                t = (year - ys[i]) / (ys[i+1] - ys[i])
                return traj[ys[i]] + t * (traj[ys[i+1]] - traj[ys[i]])
        return traj[ys[-1]]

    y_labels = [f"{c}" for c in countries]

    for ax, year in zip(axes, years):
        ax.axvline(0, color="#333333", linewidth=1.0, zorder=2)
        ax.grid(axis="x", color="#e5e5e5", linewidth=0.6, zorder=1)
        ax.grid(axis="y", visible=False)
        ax.set_axisbelow(True)

        # H2 CENTRAL price at this year (used as base for LCOH calculation)
        h2_central_price = get_h2_price("CENTRAL", year)

        for ti, traj_name in enumerate(["RAPID","CENTRAL","SLOW","STRANDED"]):
            h2_fuel_price = get_h2_price(traj_name, year)
            # Price ratio vs CENTRAL — scale the fuel component of H2 LCOH
            price_ratio = h2_fuel_price / max(h2_central_price, 1.0)
            gaps = []
            for country in countries:
                try:
                    hp_best = min(
                        compute_lcoh("hp_air",    country, year),
                        compute_lcoh("hp_ground", country, year),
                    )
                    # H2 LCOH = CENTRAL LCOH adjusted for this trajectory's fuel price
                    # Fuel cost is ~75% of H2 LCOH; scale that component
                    h2_central_lcoh = compute_lcoh("h2_boiler", country, year)
                    # Separate fuel from non-fuel components
                    h2_fuel_frac = 0.75
                    h2_nonfuel   = h2_central_lcoh * (1 - h2_fuel_frac)
                    h2_fuel_adj  = h2_central_lcoh * h2_fuel_frac * price_ratio
                    h2_lcoh_adj  = h2_nonfuel + h2_fuel_adj
                    # Gap: positive = H2 more expensive than HP
                    gap = h2_lcoh_adj - hp_best
                    gaps.append(gap)
                except Exception:
                    gaps.append(np.nan)

            y_pos = np.arange(len(countries)) + ti * 0.18 - 0.27
            ax.scatter(gaps, y_pos, color=traj_cols[traj_name],
                       s=32, zorder=3, alpha=0.85,
                       label=traj_name if year == 2025 else "")

        ax.set_yticks(np.arange(len(countries)) + 0.09)
        ax.set_yticklabels(y_labels, fontsize=8.5)
        ax.set_title(str(year), fontsize=12, fontweight="bold", pad=8)
        ax.set_xlabel("H\u2082 boiler LCOH gap vs best HP (€/MWh)\n"
                      "Positive = H\u2082 more expensive; negative = H\u2082 cheaper",
                      fontsize=8.5)
        ax.invert_yaxis()

        # Shade "H2 competitive" region
        xlim = ax.get_xlim()
        ax.axvspan(xlim[0], 0, alpha=0.05, color="#2ca02c", linewidth=0)

    # Legend on first panel only
    handles = [mpatches.Patch(color=traj_cols[t], label=t)
               for t in ["RAPID","CENTRAL","SLOW","STRANDED"]]
    fig.legend(handles=handles, loc="lower center", ncol=4,
               fontsize=9, bbox_to_anchor=(0.5, -0.04),
               frameon=True, edgecolor="#cccccc",
               title="H\u2082 price trajectory")

    fig.suptitle(
        "H\u2082 Boiler Competitiveness Gap vs Best Heat Pump, 2025\u20132050\n"
        "(CENTRAL carbon scenario; positive values = H\u2082 still more expensive)",
        fontsize=11, fontweight="bold")
    _source(fig)
    out = FIGS_DIR / "fig8_h2_threshold.pdf"
    fig.savefig(out)
    plt.close(fig)
    print(f"  Saved: {out.name}")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 9 — Sensitivity tornado (requires mc_sensitivity_{scenario}.csv)
# ─────────────────────────────────────────────────────────────────────────────
def fig9_sensitivity_tornado(scenario: str = "STATED_POLICIES") -> None:
    df = _load_mc(scenario, "sensitivity")
    if df is None:
        print("  Fig 9 skipped — run --sensitivity first")
        return

    # Metric: 2030 EU buildings CO2 emissions. The 2050 endpoint is a poor
    # tornado metric because STATED_POLICIES emissions are already near-floored (~9.6 Mt)
    # so the sampling noise swamps the axis effect; 2030 retains real signal.
    YEAR = 2030
    BASE = {"carbon_scenario": "CENTRAL", "h2_scenario": "CENTRAL",
            "discount_rate": "base"}
    em = df[(df["variable"] == "co2_MtCO2") & (df["year"] == YEAR)]

    def _median(overrides):
        """One-at-a-time: the other two axes are held at the base case."""
        m = em
        for k, v in {**BASE, **overrides}.items():
            m = m[m[k] == v]
        return m["value"].median()

    base = _median({})
    if pd.isna(base):
        print("  Fig 9 skipped — no base value in sensitivity results")
        return

    axes_cfg = [
        ("Carbon price",      "carbon_scenario", "LOW",    "HIGH"),
        ("H$_2$ price",       "h2_scenario",     "RAPID",  "STRANDED"),
        ("Discount rate",     "discount_rate",   "social", "private"),
    ]
    rows = []
    for label, col, lo_val, hi_val in axes_cfg:
        lo = _median({col: lo_val})
        hi = _median({col: hi_val})
        rows.append((label, lo_val, hi_val,
                     0.0 if pd.isna(lo) else (lo - base),
                     0.0 if pd.isna(hi) else (hi - base)))
    rows.sort(key=lambda r: abs(r[3]) + abs(r[4]), reverse=True)

    c_hi = PALETTE["gas_boiler"]      # higher emissions
    c_lo = PALETTE["district_heat"]   # lower emissions
    span = max(0.6, max(abs(r[3]) + abs(r[4]) for r in rows))

    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    for i, (label, lo_name, hi_name, lo_d, hi_d) in enumerate(rows):
        if abs(lo_d) + abs(hi_d) < 0.05:
            ax.text(0, i, "   immaterial (< 0.1 MtCO$_2$)", va="center",
                    ha="left", fontsize=8, color="#999999", style="italic")
            continue
        for d, name in [(lo_d, lo_name), (hi_d, hi_name)]:
            col = c_hi if d > 0 else c_lo
            ax.barh(i, d, height=0.52, color=col, zorder=3)
            ax.text(d + (span * 0.035 if d > 0 else -span * 0.035), i, name,
                    va="center", ha=("left" if d > 0 else "right"),
                    fontsize=8, color=col)

    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows])
    ax.invert_yaxis()
    ax.axvline(0, color="#333333", linewidth=0.9, zorder=4)
    ax.set_xlim(-span * 1.55, span * 1.55)
    ax.set_xlabel("Change in %d EU buildings CO$_2$ emissions vs base "
                  "(MtCO$_2$ yr$^{-1}$)" % YEAR)
    ax.set_title("Sensitivity of %d buildings CO$_2$ emissions to model parameters"
                 % YEAR)
    ax.grid(axis="x", linewidth=0.4, color="#dddddd")
    ax.set_axisbelow(True)
    legend = [mpatches.Patch(color=c_hi, label="Higher emissions"),
              mpatches.Patch(color=c_lo, label="Lower emissions")]
    ax.legend(handles=legend, loc="lower right")
    fig.subplots_adjust(bottom=0.26, top=0.88)
    fig.text(0.5, 0.035,
             "One-at-a-time variation around the base case (CENTRAL "
             "carbon, CENTRAL H$_2$, 5%% discount; base %d emissions "
             "%.0f MtCO$_2$)." % (YEAR, base),
             ha="center", fontsize=7.2, color="#666666")
    out = FIGS_DIR / "fig9_sensitivity_tornado.pdf"
    fig.savefig(out)
    plt.close(fig)
    print(f"  Saved: {out.name}")

# ─────────────────────────────────────────────────────────────────────────────
# TABLES
# ─────────────────────────────────────────────────────────────────────────────
def table1_lcoh_summary() -> None:
    """Table 1: LCOH by tech × country group × year."""
    rows = []
    for group, ctries in COUNTRY_GROUPS.items():
        for year in [2025, 2030, 2050]:
            for tech in ["gas_boiler","hp_air","hp_ground",
                         "h2_boiler","district_heat","biomass_boiler"]:
                vals = []
                for country in ctries:
                    try:
                        vals.append(compute_lcoh(tech, country, year))
                    except Exception:
                        pass
                if vals:
                    rows.append({
                        "Country group":       group,
                        "Year":                year,
                        "Technology":          TECH_LABELS.get(tech, tech),
                        "Min (€/MWh)":         round(min(vals), 0),
                        "Median (€/MWh)":      round(float(np.median(vals)), 0),
                        "Max (€/MWh)":         round(max(vals), 0),
                        "Carbon scenario":     "CENTRAL",
                    })
    pd.DataFrame(rows).to_csv(TABS_DIR/"table1_lcoh_summary.csv", index=False)
    print(f"  Saved: table1_lcoh_summary.csv ({len(rows)} rows)")


def table2_co2_reduction(scenarios: list[str] = None) -> None:
    """Table 2: CO₂ reduction vs 2025 baseline by scenario."""
    if scenarios is None:
        scenarios = ["CURRENT_POLICIES","STATED_POLICIES","NET_ZERO","H2_PUSH"]
    rows = []
    for scen in scenarios:
        df = _load_mc(scen, "emissions")
        if df is None:
            continue
        co2 = df[df["variable"] == "co2_MtCO2"]
        base = co2[co2["year"]==2025]["q50"].sum()
        for year in [2030, 2040, 2050]:
            val  = co2[co2["year"]==year]["q50"].sum()
            q10  = co2[co2["year"]==year]["q10"].sum()
            q90  = co2[co2["year"]==year]["q90"].sum()
            rows.append({
                "Scenario":                SCENARIO_LABELS.get(scen, scen),
                "Year":                    year,
                "CO\u2082 median (MtCO\u2082)": round(val, 1),
                "CO\u2082 q10 (MtCO\u2082)":    round(q10, 1),
                "CO\u2082 q90 (MtCO\u2082)":    round(q90, 1),
                "Reduction vs 2025 (%)":   round((1 - val/base)*100, 1) if base > 0 else float("nan"),
            })
    if rows:
        pd.DataFrame(rows).to_csv(TABS_DIR/"table2_co2_reduction.csv", index=False)
        print(f"  Saved: table2_co2_reduction.csv")


def table3_country_tech_shares(scenario: str = "STATED_POLICIES") -> None:
    """Table 3: Country-level median tech shares 2030 and 2050."""
    df = _load_mc(scenario, "country")
    if df is None:
        return
    ts = df[df["variable"] == "tech_share"]
    pivot = ts[ts["year"].isin([2030, 2050])].pivot_table(
        index=["country","year"], columns="tech", values="q50", aggfunc="first"
    ).reset_index()
    # Round all tech share columns to 3 decimal places
    tech_cols = [c for c in pivot.columns if c not in ("country","year")]
    pivot[tech_cols] = pivot[tech_cols].round(3)
    pivot.to_csv(TABS_DIR/"table3_country_tech_shares.csv", index=False)
    print(f"  Saved: table3_country_tech_shares.csv")


def table4_ets2_adder() -> None:
    """Table 4: the 2030 LCOH difference (EUR/MWh) between the CENTRAL and LOW
    carbon-price paths, by country and technology.

    NOT the ETS2 adder per 50 EUR/tCO2 that the manuscript quotes; that is computed in
    src/Policy.py and is zero for electricity outside 2030, because electricity carries
    only the increment above its 2025 carbon cost. The file name is legacy. This table is
    a scenario-spread diagnostic and is not used by the Applied Energy submission."""
    countries = ["DE","FR","PL","IT","NL","SE","UK","CH",
                 "AT","BE","CZ","HU","RO","ES","PT","DK"]
    techs     = ["gas_boiler","oil_boiler","hp_air","hp_ground","h2_boiler"]
    year      = 2030
    rows      = []
    for country in countries:
        row = {"Country": country}
        for tech in techs:
            try:
                adder = (compute_lcoh(tech, country, year, "CENTRAL")
                         - compute_lcoh(tech, country, year, "LOW"))
                row[TECH_LABELS.get(tech, tech)] = round(max(adder, 0), 1)
            except Exception:
                row[TECH_LABELS.get(tech, tech)] = float("nan")
        rows.append(row)
    pd.DataFrame(rows).to_csv(TABS_DIR/"table4_ets2_adder.csv", index=False)
    print(f"  Saved: table4_ets2_adder.csv")



# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 10 — Fuel price trajectories 2025-2050 (all carriers)
# ─────────────────────────────────────────────────────────────────────────────
def fig10_fuel_price_trajectories() -> None:
    """
    Line chart: residential end-user fuel prices 2025-2050 for key countries.
    One panel per fuel carrier. Shows how prices diverge across countries.
    """
    import warnings; warnings.filterwarnings("ignore")
    from src.Economics import get_fuel_price

    carriers = ["gas", "electricity", "hydrogen"]
    carrier_labels = {"gas":"Natural gas", "electricity":"Electricity", "hydrogen":"Green hydrogen"}
    countries_fuel = {
        "gas":         ["DE","FR","PL","NL","IT","UK","SE"],
        "electricity": ["DE","FR","PL","SE","IT","HU","UK"],
        "hydrogen":    ["CENTRAL","RAPID","SLOW","STRANDED"],
    }
    years = list(range(2025, 2051))

    cty_colors_gas = {
        "DE":"#1f77b4","FR":"#ff7f0e","PL":"#d62728","NL":"#2ca02c",
        "IT":"#9467bd","UK":"#8c564b","SE":"#17becf",
    }
    traj_colors = {
        "CENTRAL":"#ff7f0e","RAPID":"#2ca02c","SLOW":"#d62728","STRANDED":"#9467bd"
    }

    fig, axes = plt.subplots(1, 3, figsize=(14, 5.0))
    fig.subplots_adjust(wspace=0.32, top=0.82)

    for ax, carrier in zip(axes, carriers):
        ax.set_axisbelow(True)
        ax.set_xlabel("Year", fontsize=9)
        ax.set_ylabel("€/MWh (residential)", fontsize=9)
        ax.set_title(carrier_labels[carrier], fontsize=10, fontweight="bold")
        ax.set_xlim(2025, 2050)

        if carrier == "hydrogen":
            for traj in ["RAPID","CENTRAL","SLOW","STRANDED"]:
                vals = [get_fuel_price("hydrogen", "DE", yr) for yr in years]
                # Override with trajectory-specific H2 prices
                from src.Economics import H2_PRICE_TRAJECTORIES
                traj_data = H2_PRICE_TRAJECTORIES[traj]
                traj_years = sorted(traj_data.keys())
                vals_adj = []
                for yr in years:
                    if yr <= traj_years[0]: vals_adj.append(traj_data[traj_years[0]])
                    elif yr >= traj_years[-1]: vals_adj.append(traj_data[traj_years[-1]])
                    else:
                        for i in range(len(traj_years)-1):
                            if traj_years[i] <= yr <= traj_years[i+1]:
                                t = (yr-traj_years[i])/(traj_years[i+1]-traj_years[i])
                                vals_adj.append(traj_data[traj_years[i]] + t*(traj_data[traj_years[i+1]]-traj_data[traj_years[i]]))
                                break
                ax.plot(years, vals_adj, color=traj_colors[traj],
                        linewidth=2, label=traj)
            ax.legend(title="Trajectory", fontsize=8, title_fontsize=8,
                      loc="upper right")
        else:
            for country in countries_fuel[carrier]:
                vals = [get_fuel_price(carrier, country, yr) for yr in years]
                col  = cty_colors_gas.get(country, "#888")
                ax.plot(years, vals, color=col, linewidth=1.8, label=country)
            ax.legend(title="Country", fontsize=8, title_fontsize=8, ncol=2,
                      loc="upper right")

        # Headroom so the upper-right legend clears the (descending) lines.
        ax.set_ylim(top=ax.get_ylim()[1] * 1.16)
        ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"€{x:.0f}"))

    fig.suptitle(
        "Residential Fuel Price Trajectories, 2025–2050",
        fontsize=11, fontweight="bold", y=0.98)
    fig.text(0.5, 0.92, "Gas & electricity: Eurostat H1 2025 × IEA multipliers · H₂: OIES/IEA scenarios",
             ha="center", fontsize=8.5, color="#555555")
    _source(fig)
    out = FIGS_DIR / "fig10_fuel_prices.pdf"
    fig.savefig(out)
    plt.close(fig)
    print(f"  Saved: {out.name}")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 11 — HP vs gas LCOH crossover year (when HP becomes cheaper)
# ─────────────────────────────────────────────────────────────────────────────
def fig11_hp_crossover() -> None:
    """
    Horizontal bar chart of how far air-source heat-pump LCOH already sits
    below gas-boiler LCOH in 2025, per country. Air-source HP is already the
    cheaper option in every modelled country, so a literal "crossover year"
    chart is uninformative (every country crosses in 2025); the magnitude of
    the cost advantage is the quantity worth showing.
    """
    countries = ["DE", "FR", "PL", "IT", "NL", "SE", "UK", "CH", "AT", "BE",
                 "CZ", "HU", "RO", "ES", "DK", "PT", "EL", "SK", "EE", "LV",
                 "LT", "FI", "BG", "SI"]
    year = 2025
    gaps = {}
    for c in countries:
        try:
            gas = compute_lcoh("gas_boiler", c, year)
            hp = compute_lcoh("hp_air", c, year)
            gaps[c] = gas - hp
        except Exception:
            pass
    order = sorted(gaps, key=lambda c: gaps[c], reverse=True)
    vals = [gaps[c] for c in order]

    fig, ax = plt.subplots(figsize=(7.4, 6.2))
    y = np.arange(len(order))
    colors = [PALETTE["hp_air"] if v >= 0 else PALETTE["gas_boiler"]
              for v in vals]
    ax.barh(y, vals, color=colors, height=0.66, zorder=3)
    span = max((abs(v) for v in vals), default=1.0)
    for i, v in enumerate(vals):
        ax.text(v + (span * 0.02 if v >= 0 else -span * 0.02), i, f"{v:.0f}",
                va="center", ha=("left" if v >= 0 else "right"),
                fontsize=8, color="#333333")
    ax.set_yticks(y)
    ax.set_yticklabels(order)
    ax.invert_yaxis()
    ax.axvline(0, color="#333333", linewidth=0.9, zorder=4)
    ax.set_xlim(0, span * 1.16)
    ax.set_xlabel("Air-source heat-pump cost advantage over a gas boiler, "
                  "2025 (€/MWh useful heat)")
    ax.grid(axis="x", linewidth=0.4, color="#dddddd")
    ax.set_axisbelow(True)
    ax.set_title("Air-source heat pumps are already cheaper than gas boilers "
                 "in every modelled country (2025)",
                 fontsize=11, fontweight="bold")
    fig.text(0.5, -0.03,
             "Bars show the 2025 LCOH gap (gas-boiler LCOH minus air-source "
             "heat-pump LCOH), CENTRAL carbon scenario, labour-cost-adjusted "
             "CAPEX. A positive gap means the heat pump is the cheaper option.",
             ha="center", fontsize=7, color="#666666", wrap=True)
    out = FIGS_DIR / "fig11_hp_crossover.pdf"
    fig.savefig(out)
    plt.close(fig)
    print(f"  Saved: {out.name}")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 12 — Grid CO₂ intensity trajectories by country group
# ─────────────────────────────────────────────────────────────────────────────
def fig12_grid_co2_trajectories() -> None:
    """
    Line chart per country group showing how electricity CO₂ intensity
    falls 2025-2050. This directly determines HP competitiveness.
    """
    from src.Policy import get_grid_carbon_intensity

    group_countries = {
        "Nordic":   ["SE","FI","DK","NO"],
        "Western":  ["DE","FR","NL","AT","BE","CH","IE"],
        "Southern": ["IT","ES","PT","EL"],
        "Eastern":  ["PL","CZ","HU","RO","BG","SK"],
        "UK":       ["UK"],
    }
    group_colors = {
        "Nordic":   "#2ca02c",
        "Western":  "#1f77b4",
        "Southern": "#ff7f0e",
        "Eastern":  "#d62728",
        "UK":       "#9467bd",
    }
    years = list(range(2025, 2051))

    fig, ax = plt.subplots(figsize=(9, 5))

    for group, members in group_countries.items():
        col = group_colors[group]
        members_in_model = [c for c in members if c in EU_COUNTRIES]
        if not members_in_model:
            continue

        # Individual country lines (faint)
        for country in members_in_model:
            vals = [get_grid_carbon_intensity(country, yr) for yr in years]
            ax.plot(years, vals, color=col, linewidth=0.7, alpha=0.35)

        # Group average (bold)
        avg_vals = []
        for yr in years:
            group_vals = [get_grid_carbon_intensity(c, yr) for c in members_in_model]
            avg_vals.append(np.mean(group_vals))
        ax.plot(years, avg_vals, color=col, linewidth=2.5,
                label=f"{group} (avg)", zorder=4)

    # Reference: above this, HP on grid has worse CO₂ than gas boiler
    # Gas boiler: 0.202 tCO2/MWh / 0.92 efficiency = 0.219 tCO2/MWh_useful
    # HP COP 3: grid_intensity / 1000 tCO2/MWh / 3 COP = grid / 3000 tCO2/kWh_useful
    # Crossover: grid / 3000 = 0.219 → grid = 657 gCO2/kWh
    ax.axhline(657, color="#d62728", linewidth=1.2, linestyle=":",
               label="HP breaks even with gas boiler (COP=3, €122/t)")
    ax.axhline(0, color="#333333", linewidth=0.5)

    ax.set_xlabel("Year")
    ax.set_ylabel("Electricity CO₂ intensity (gCO₂/kWh)")
    ax.set_xlim(2025, 2050)
    ax.set_ylim(bottom=0)
    # Legend below the axes -- a 6-entry legend in any corner overlaps either
    # the breakeven line (top) or the descending country lines.
    ax.legend(fontsize=8.5, ncol=3, loc="upper center",
              bbox_to_anchor=(0.5, -0.13))
    ax.set_title(
        "Electricity Grid Carbon Intensity by Country Group, 2025–2050\n"
        "Faint lines = individual countries; bold = group average",
        fontsize=11, fontweight="bold")
    _source(fig, "Source: EMBER 2024 actuals; EEA Fit-for-55 projections. ")
    out = FIGS_DIR / "fig12_grid_co2_trajectories.pdf"
    fig.savefig(out)
    plt.close(fig)
    print(f"  Saved: {out.name}")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 13 — LCOH breakdown waterfall (gas boiler vs HP, Germany 2030)
# ─────────────────────────────────────────────────────────────────────────────
def fig13_lcoh_waterfall() -> None:
    """
    Waterfall / stacked bar showing LCOH cost components for
    gas boiler vs HP air vs H2 boiler, for 3 representative countries.
    Makes the cost structure transparent and citation-ready.
    """
    from src.Emissions import get_emission_factor
    from src.Economics import (
        TECH_PARAMS, capital_recovery_factor, DISCOUNT_RATE_REAL,
        get_annual_hours, get_fuel_price, get_cop, get_capex, get_fom,
    )
    from src.Policy import get_carbon_cost_adder_eur_per_mwh_useful, CARBON_PRICE_SCENARIO

    def get_breakdown(tech, country, year):
        p   = TECH_PARAMS[tech]
        t   = max(0, min(1, (year-2025)/25))
        if "scop_2025" in p:
            eta = get_cop(tech, country, year)
        else:
            e0  = p.get("efficiency_2025", 0.92)
            e1  = p.get("efficiency_2050", e0)
            eta = e0 + t*(e1-e0)
        eta  = max(eta, 0.1)
        # Capital is charged on HEAT OUTPUT: annual_hours is full-load hours of heat
        # and capex is EUR per kW of heat, so there is no efficiency term. This is a
        # third copy of the levelised-cost build, and it carried the same doubled
        # efficiency that was removed from Economics.compute_lcoh. It also has to apply
        # the delivery adders the engine now applies by default, or the stack will not
        # sum to the quoted cost.
        from src.Economics import (DISCOUNT_RATE_BY_COUNTRY,
                                   h2_distribution_adder_eur_mwh,
                                   electricity_distribution_adder_eur_mwh,
                                   h2_seasonal_storage_adder_eur_mwh)
        capex = get_capex(tech, year, country)        # country-adjusted
        r     = DISCOUNT_RATE_BY_COUNTRY.get(country, DISCOUNT_RATE_REAL)
        crf   = capital_recovery_factor(r, p["lifetime_yrs"])
        ah    = get_annual_hours(country)
        aheat = ah / 1000
        fom_c = get_fom(tech, country)                # country-adjusted
        storage = 0.0
        if tech == "h2_boiler":
            infra = h2_distribution_adder_eur_mwh(country, r, mode="blend", bound="central")
            storage = h2_seasonal_storage_adder_eur_mwh(country, eta)
        elif tech in ("hp_air", "hp_ground", "resistance_heater"):
            infra = electricity_distribution_adder_eur_mwh(country, r, bound="central")
        else:
            infra = 0.0
        return {
            "Capital": round(crf*capex/aheat, 1),
            "O&M":     round(fom_c/aheat + p["vom_eur_mwh"], 1),
            "Network": round(infra, 1),
            "Storage": round(storage, 1),
            "Fuel":    round(get_fuel_price(p["fuel"], country, year)/eta, 1),
            "Carbon":  round(get_carbon_cost_adder_eur_per_mwh_useful(
                             p["fuel"], country, year, eta, CARBON_PRICE_SCENARIO), 1),
        }

    countries   = ["DE", "PL", "FR"]
    techs       = ["gas_boiler", "hp_air", "h2_boiler"]
    year        = 2030
    components  = ["Capital", "O&M", "Network", "Storage", "Fuel", "Carbon"]
    comp_colors = {
        "Capital": "#4878cf",
        "O&M":     "#6acc65",
        "Network": "#14b8a6",
        "Storage": "#a855f7",
        "Fuel":    "#d65f5f",
        "Carbon":  "#b47cc7",
    }

    fig, axes = plt.subplots(1, 3, figsize=(13, 5), sharey=False)
    fig.subplots_adjust(wspace=0.35, top=0.80)

    for ax, country in zip(axes, countries):
        x     = np.arange(len(techs))
        width = 0.55
        bottoms = np.zeros(len(techs))

        for comp in components:
            vals = []
            for tech in techs:
                bd = get_breakdown(tech, country, year)
                vals.append(bd.get(comp, 0))
            vals = np.array(vals)
            ax.bar(x, vals, width, bottom=bottoms,
                   color=comp_colors[comp], alpha=0.88, linewidth=0,
                   label=comp)
            # Label component if large enough
            for xi, (v, b) in enumerate(zip(vals, bottoms)):
                if v >= 8:
                    ax.text(xi, b + v/2, f"{v:.0f}", ha="center", va="center",
                            fontsize=7.5, color="white", fontweight="bold")
            bottoms = bottoms + vals

        # Total on top
        for xi, total in enumerate(bottoms):
            ax.text(xi, total + 2, f"€{total:.0f}", ha="center", va="bottom",
                    fontsize=8.5, fontweight="bold", color="#222222")

        ax.set_xticks(x)
        ax.set_xticklabels([TECH_SHORT[t] for t in techs], fontsize=9)
        ax.set_ylabel("LCOH (€/MWh useful heat)" if country == "DE" else "")
        ax.set_title(country, fontsize=11, fontweight="bold")
        ax.set_ylim(0, max(bottoms)*1.18)

    # Single legend
    handles = [mpatches.Patch(color=comp_colors[c], label=c) for c in components]
    fig.legend(handles=handles, loc="lower center", ncol=4,
               fontsize=9, bbox_to_anchor=(0.5, -0.06),
               frameon=True, edgecolor="#cccccc")

    fig.suptitle(
        "LCOH Cost Component Breakdown — Gas Boiler vs Heat Pump vs H₂ Boiler (2030)\n"
        "Central carbon scenario · Country-specific discount rates (3.0-8.0% real)",
        fontsize=11, fontweight="bold", y=1.00)
    _source(fig)
    out = FIGS_DIR / "fig13_lcoh_waterfall.pdf"
    fig.savefig(out)
    plt.close(fig)
    print(f"  Saved: {out.name}")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 14 — Switzerland H2 import price trajectories vs EU HP cost
# ─────────────────────────────────────────────────────────────────────────────
def fig14_switzerland_h2() -> None:
    """
    Switzerland-specific figure for RQ2.
    Plots H2 import price trajectories (LOW/CENTRAL/HIGH from OIES)
    against H2 boiler LCOH and best HP LCOH over time.
    Shows when and under what conditions H2 heating is competitive in Switzerland.
    """
    from src.Policy import SWITZERLAND_POLICY

    years = list(range(2025, 2051))
    h2_import = SWITZERLAND_POLICY.get("h2_import_price_eur_per_mwh", {})
    import_years = sorted(h2_import.keys())

    def interp_import(scenario, year):
        if year <= import_years[0]:  return h2_import[import_years[0]][scenario]
        if year >= import_years[-1]: return h2_import[import_years[-1]][scenario]
        for i in range(len(import_years)-1):
            y0, y1 = import_years[i], import_years[i+1]
            if y0 <= year <= y1:
                t = (year-y0)/(y1-y0)
                return (h2_import[y0][scenario] + t *
                        (h2_import[y1][scenario] - h2_import[y0][scenario]))
        return h2_import[import_years[-1]][scenario]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))
    fig.subplots_adjust(top=0.82, wspace=0.32)

    # Left panel: H2 boiler LCOH (from import price) vs HP LCOH
    # H2 boiler LCOH = fuel cost / 0.90 efficiency + non-fuel fixed costs
    # Non-fuel component = CENTRAL LCOH * 25% (capital + O&M)
    scen_colors = {"LOW":"#2ca02c","CENTRAL":"#ff7f0e","HIGH":"#d62728"}
    h2_central_lcoh = [compute_lcoh("h2_boiler","CH",yr) for yr in years]
    nonfuel_frac = 0.25

    for scen, col in scen_colors.items():
        h2_boiler_lcoh = []
        for i, yr in enumerate(years):
            fuel_price = interp_import(scen, yr)
            fuel_cost  = fuel_price / 0.90          # fuel cost per MWh useful
            nonfuel    = h2_central_lcoh[i] * nonfuel_frac
            h2_boiler_lcoh.append(fuel_cost + nonfuel)
        ax1.plot(years, h2_boiler_lcoh, color=col, linewidth=2.2,
                 label=f"H₂ boiler ({scen} import)")

    # HP LCOH for Switzerland
    hp_air_ch  = [compute_lcoh("hp_air",    "CH", yr) for yr in years]
    hp_gnd_ch  = [compute_lcoh("hp_ground", "CH", yr) for yr in years]
    ax1.plot(years, hp_air_ch,  color="#1f77b4", linewidth=2.2,
             linestyle="--", label="HP air-source LCOH")
    ax1.plot(years, hp_gnd_ch,  color="#17519e", linewidth=2.2,
             linestyle=":",  label="HP ground-source LCOH")
    ax1.fill_between(years, hp_air_ch, hp_gnd_ch, alpha=0.12, color="#1f77b4")

    ax1.set_title("H₂ Boiler LCOH vs Heat Pump LCOH", fontsize=10, fontweight="bold")
    ax1.set_xlabel("Year"); ax1.set_ylabel("LCOH (€/MWh useful heat)")
    ax1.set_xlim(2025, 2050); ax1.set_ylim(0, 420)
    ax1.legend(fontsize=8.5, loc="upper right"); ax1.set_axisbelow(True)

    # Right panel: H2 boiler LCOH gap vs best HP — same calc as left panel
    hp_best = [min(compute_lcoh("hp_air","CH",yr),
                   compute_lcoh("hp_ground","CH",yr)) for yr in years]
    for scen, col in scen_colors.items():
        h2_boiler_lcoh_r = []
        for i, yr in enumerate(years):
            fuel_price = interp_import(scen, yr)
            fuel_cost  = fuel_price / 0.90
            nonfuel    = h2_central_lcoh[i] * nonfuel_frac
            h2_boiler_lcoh_r.append(fuel_cost + nonfuel)
        gap = [h - p for h, p in zip(h2_boiler_lcoh_r, hp_best)]
        ax2.plot(years, gap, color=col, linewidth=2.2, label=f"{scen}")
        ax2.fill_between(years, 0, gap, where=[g > 0 for g in gap],
                         color=col, alpha=0.07)

    ax2.axhline(0, color="#333333", linewidth=1.2, linestyle="-", zorder=3)
    ax2.fill_between(years, -80, 0, alpha=0.05, color="#2ca02c", linewidth=0)
    ax2.text(2049, -5, "H₂ cheaper than HP", ha="right", va="top", fontsize=8,
             color="#2ca02c", style="italic")
    ax2.set_title("H₂ Competitiveness Gap vs Best HP", fontsize=10, fontweight="bold")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("H₂ boiler LCOH − Best HP LCOH (€/MWh)")
    ax2.set_xlim(2025, 2050)
    ax2.set_ylim(-80, 380)
    ax2.legend(fontsize=9, title="Import scenario", title_fontsize=9)
    ax2.set_axisbelow(True)

    fig.suptitle(
        "Switzerland — H₂ Heating vs Heat Pump Competitiveness (RQ2)",
        fontsize=11, fontweight="bold", y=0.98)
    fig.text(0.5, 0.92,
             "H₂ import prices: OIES ET08/ET32 (corrected) · Swiss grid 50 gCO₂/kWh · H₂ boiler η=0.90",
             ha="center", fontsize=8.5, color="#555555")
    _source(fig, "Sources: OIES ET08 (2022), OIES ET32 (2024), IEA Switzerland (2023), "
                 "Swiss Federal Office of Energy EP2050+. ")
    out = FIGS_DIR / "fig14_switzerland_h2.pdf"
    fig.savefig(out)
    plt.close(fig)
    print(f"  Saved: {out.name}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def make_all_figures(scenarios: list[str] = None) -> None:
    if scenarios is None:
        scenarios = ["CURRENT_POLICIES","STATED_POLICIES","NET_ZERO","H2_PUSH"]
    print("\nGenerating paper figures and tables...")

    fig3_transition_pathways(scenarios)
    fig4_co2_trajectory(scenarios)
    fig5_lcoh_comparison()
    fig6_country_heatmap(scenarios[0] if scenarios else "STATED_POLICIES")
    fig7_ets2_impact()
    fig8_h2_threshold()
    fig9_sensitivity_tornado(scenarios[0] if scenarios else "STATED_POLICIES")
    fig10_fuel_price_trajectories()
    fig11_hp_crossover()
    fig12_grid_co2_trajectories()
    fig13_lcoh_waterfall()
    fig14_switzerland_h2()

    table1_lcoh_summary()
    table2_co2_reduction(scenarios)
    table3_country_tech_shares(scenarios[0] if scenarios else "STATED_POLICIES")
    table4_ets2_adder()

    print(f"\nFigures: paper/figs/   Tables: paper/tables/")


if __name__ == "__main__":
    make_all_figures()
