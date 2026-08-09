"""SI emissions-fan figure: residential-heating CO2 by policy scenario, 2025-2050,
median with the 10th-90th-percentile Monte Carlo band.

All four pathways start from the same reconstructed 2025 baseline and run to
well-separated 2050 endpoints; each scenario's economic
and technology band is narrow beside the between-scenario spread, so ambition, not
technology availability, sets the 2050 gap. Values are the model outputs tabulated in
SI Table (Buildings-sector CO2 by scenario), i.e. the co2_MtCO2 (all/all) series in
results/mc_emissions_<SCEN>.csv.

Run:  cd code && PYTHONPATH=. python -m scripts.fig_emissions_fan
Out:  paper/figs/paper/emissions_scenario_fan.{png,pdf}
"""
from __future__ import annotations
from pathlib import Path
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scripts._figstyle import set_style, SCEN_COLOR
set_style()
plt.rcParams.update({"figure.autolayout": False, "savefig.bbox": "tight"})

RES = Path(__file__).resolve().parents[1] / "results"
FIGDIR = Path(__file__).resolve().parents[2] / "paper" / "figs" / "paper"

# Ordered by 2050 median (top to bottom of the fan) so the legend reads with the lines.
# Labels match the manuscript scenario names exactly (H2 Push, not "Hydrogen Push").
SCEN = [
    ("CURRENT_POLICIES", "Current Policies", SCEN_COLOR["CURRENT_POLICIES"]),
    ("STATED_POLICIES",  "Stated Policies",  SCEN_COLOR["STATED_POLICIES"]),
    ("H2_PUSH",          "H2 Push",          SCEN_COLOR["H2_PUSH"]),
    ("NET_ZERO",         "Net Zero",         SCEN_COLOR["NET_ZERO"]),
]


def _series(key):
    rows = [r for r in csv.DictReader(open(RES / f"mc_emissions_{key}.csv"))
            if r["variable"] == "co2_MtCO2" and r["tech"] == "all" and r["carrier"] == "all"]
    yr = [int(r["year"]) for r in rows]
    q10 = [float(r["q10"]) for r in rows]
    q50 = [float(r["q50"]) for r in rows]
    q90 = [float(r["q90"]) for r in rows]
    return yr, q10, q50, q90


def emissions_scenario_fan():
    # Plot the model output as it stands. All four scenarios now share the same
    # reconstructed 2025 baseline, because the replacement-ban block gained a
    # `year > BASE_YEAR` guard: without it the Net Zero fossil-ambition draw reached back
    # and deleted observed 2025 boiler stock, dropping that scenario's base-year median to
    # about 586 MtCO2 and making the calibration year scenario-dependent. This comment
    # described that state and outlived it. Nothing is overwritten here; the point is
    # plotted from the artefact, which is why the four now coincide at 2025.
    fig, ax = plt.subplots(figsize=(5.2, 3.5))
    for key, lab, col in SCEN:
        yr, q10, q50, q90 = _series(key)
        ax.fill_between(yr, q10, q90, color=col, alpha=0.15, zorder=2)
        ax.plot(yr, q50, color=col, lw=2.4, marker="o", ms=5, zorder=3, label=lab)
        ax.text(2050.6, q50[-1], f"{q50[-1]:.0f}", color=col, va="center",
                fontsize=10.5, fontweight="bold")
    ax.set_xlim(2024, 2054)
    ax.set_ylim(0, 680)
    ax.set_xticks([2025, 2030, 2040, 2050])
    ax.set_ylabel("Residential heating CO₂ (Mt/yr)")
    ax.set_xlabel("Year")
    ax.grid(axis="y")
    ax.legend(loc="upper right", frameon=False, fontsize=9.5)
    fig.subplots_adjust(left=0.11, right=0.94, top=0.97, bottom=0.10)
    for ext in ("png", "pdf"):
        fig.savefig(FIGDIR / f"emissions_scenario_fan.{ext}")
    plt.close(fig)
    print("wrote emissions_scenario_fan.{png,pdf}")


if __name__ == "__main__":
    emissions_scenario_fan()
