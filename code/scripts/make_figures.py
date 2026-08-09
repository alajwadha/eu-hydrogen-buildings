"""
code/figures/make_figures.py
=============================
Generates all publication-quality figures for the paper from model outputs.
Reads from: code/data/  (symlinked or copied from eu-buildings-heat-model/results/)
Writes to:  ../paper/figs/

Usage:
    cd code/figures
    python make_figures.py --scenario STATED_POLICIES
    python make_figures.py --all          # all three scenarios

Figures produced:
    fig1_heat_demand.pdf       — EU+CH+UK useful heat demand (all scenarios)
    fig2_tech_shares.pdf       — Technology share trajectories (all scenarios)
    fig3_h2_conditions.pdf     — Conditions for H2 deployment [TODO: post-optimisation]
    fig4_switzerland.pdf       — Switzerland RQ2 results       [TODO: post-RQ2 layer]
    fig5_carriers.pdf          — Final energy by carrier
    figS1_mc_convergence.pdf   — Monte Carlo convergence (Appendix)
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import numpy as np

# ─── Paths ───────────────────────────────────────────────────────────────────
# Repo layout:
#   eu-hydrogen-buildings/
#     model/results/     ← Monte Carlo outputs (read from here directly)
#     paper/figs/        ← publication figures (written here)
#     paper/code/figures/make_figures.py  ← this file

REPO_ROOT = Path(__file__).resolve().parents[2]   # eu-hydrogen-buildings/
DATA_DIR  = REPO_ROOT / "code" / "results"         # code/results/
FIGS_DIR  = REPO_ROOT / "paper" / "figs"           # paper/figs/
FIGS_DIR.mkdir(parents=True, exist_ok=True)

# ─── Plot style ──────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":      "serif",
    "font.size":        11,
    "axes.titlesize":   12,
    "axes.labelsize":   11,
    "legend.fontsize":  9,
    "figure.dpi":       150,
    "savefig.dpi":      300,
    "savefig.bbox":     "tight",
    "axes.spines.top":  False,
    "axes.spines.right": False,
})

SCENARIO_LABELS = {
    "CURRENT_POLICIES": "Current Policies",
    "STATED_POLICIES":  "Stated Policies",
    "NET_ZERO":         "Net Zero",
    "H2_PUSH":          "H2 Push",
}

SCENARIO_COLORS = {
    "CURRENT_POLICIES": "#7f7f7f",
    "STATED_POLICIES":  "#2166ac",
    "NET_ZERO":         "#4dac26",
    "H2_PUSH":          "#d6604d",
}

TECH_COLORS = {
    "gas_boiler":       "#d73027",
    "oil_boiler":       "#fc8d59",
    "biomass_boiler":   "#91cf60",
    "resistance_heater": "#fee090",
    "hp_air":           "#4575b4",
    "hp_ground":        "#313695",
    "district_heat":    "#a6d96a",
    "h2_boiler":        "#762a83",
}

TECH_LABELS = {
    "gas_boiler":       "Gas boiler",
    "oil_boiler":       "Oil boiler",
    "biomass_boiler":   "Biomass boiler",
    "resistance_heater": "Resistance heater",
    "hp_air":           "HP (air-source)",
    "hp_ground":        "HP (ground-source)",
    "district_heat":    "District heat",
    "h2_boiler":        "H\u2082 boiler",
}


def load_summary(scenario: str) -> pd.DataFrame:
    path = DATA_DIR / f"mc_summary_{scenario}.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Summary file not found: {path}\n"
            f"Run eu-buildings-heat-model for scenario '{scenario}' first."
        )
    return pd.read_csv(path)


def fig1_heat_demand(scenarios: list) -> None:
    """Figure 1 — EU+CH+UK useful heat demand across scenarios."""
    fig, ax = plt.subplots(figsize=(7, 4.5))

    for scen in scenarios:
        df = load_summary(scen)
        sub = df[df["variable"] == "useful_heat_MWh"]
        color = SCENARIO_COLORS[scen]
        ax.fill_between(
            sub["year"], sub["q10"] / 1e6, sub["q90"] / 1e6,
            alpha=0.15, color=color
        )
        ax.plot(
            sub["year"], sub["q50"] / 1e6,
            marker="o", color=color, linewidth=1.8,
            label=SCENARIO_LABELS[scen]
        )

    ax.set_xlabel("Year")
    ax.set_ylabel("Useful heat demand [TWh/year]")
    ax.set_title("EU+CH+UK residential useful heat demand")
    ax.legend(frameon=False)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))

    out = FIGS_DIR / "fig1_heat_demand.pdf"
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved {out}")


def fig2_tech_shares(scenarios: list) -> None:
    """Figure 2 — Technology share trajectories (one panel per scenario)."""
    n = len(scenarios)
    fig, axes = plt.subplots(1, n, figsize=(5.5 * n, 4.5), sharey=True)
    if n == 1:
        axes = [axes]

    for ax, scen in zip(axes, scenarios):
        df = load_summary(scen)
        sub = df[df["variable"] == "tech_share"]
        for tech in sorted(sub["tech"].unique()):
            ts = sub[sub["tech"] == tech]
            color = TECH_COLORS.get(tech, "grey")
            ax.plot(
                ts["year"], ts["q50"],
                marker="o", linewidth=1.6,
                color=color,
                label=TECH_LABELS.get(tech, tech)
            )
        ax.set_title(SCENARIO_LABELS[scen])
        ax.set_xlabel("Year")
        if ax == axes[0]:
            ax.set_ylabel("Share of useful heat demand")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center",
               ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.08))
    fig.suptitle("EU+CH+UK heating technology shares", y=1.02)

    out = FIGS_DIR / "fig2_tech_shares.pdf"
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved {out}")


def figS1_mc_convergence(scenario: str = "STATED_POLICIES") -> None:
    """Figure S1 — Monte Carlo convergence check (Appendix)."""
    # TODO: implement once full sample outputs are available
    print("[skip] figS1_mc_convergence — requires mc_samples parquet output")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate paper figures.")
    parser.add_argument("--scenario", default="STATED_POLICIES",
                        help="Single scenario to plot (default: STATED_POLICIES)")
    parser.add_argument("--all", action="store_true",
                        help="Plot all three scenarios together")
    args = parser.parse_args()

    scenarios = ["CURRENT_POLICIES","STATED_POLICIES","NET_ZERO","H2_PUSH"] if args.all else [args.scenario]

    # Only plot scenarios for which data exists
    available = []
    for s in scenarios:
        p = DATA_DIR / f"mc_summary_{s}.csv"
        if p.exists():
            available.append(s)
        else:
            print(f"[skip] {s} — mc_summary_{s}.csv not found in code/data/")

    if not available:
        print("No scenario data found. Copy mc_summary_*.csv files to code/data/")
        return

    print(f"Generating figures for scenarios: {available}")
    fig1_heat_demand(available)
    fig2_tech_shares(available)
    figS1_mc_convergence()
    print(f"\nAll figures saved to {FIGS_DIR}")


if __name__ == "__main__":
    main()
