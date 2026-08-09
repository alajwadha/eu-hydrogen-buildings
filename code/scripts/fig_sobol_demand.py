"""SI Fig. S3: variance-based (Sobol) decomposition of 2050 EU useful-heat demand.

Plots the first-order (S1) and total-effect (ST) indices for the four demand drivers,
with their bootstrap confidence intervals, from the Saltelli screen in
scripts/global_sensitivity.py. S1 and ST sit close together for every driver, so the
variance is almost entirely first-order and the drivers barely interact.

This figure previously shipped as a loose binary with no generating script, which left
it as the one SI figure a reader could not regenerate. Values come straight from
results/global_sensitivity.csv.

Run:  cd code && PYTHONPATH=. python -m scripts.fig_sobol_demand
Out:  paper/figs/paper/P40_sobol_demand.{png,pdf}
"""
from __future__ import annotations
from pathlib import Path
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scripts._figstyle import set_style, PALETTE

set_style()

RES = Path(__file__).resolve().parents[1] / "results"
FIGDIR = Path(__file__).resolve().parents[2] / "paper" / "figs" / "paper"

# Readable names for the sampled drivers, in the order the screen reports them.
LABEL = {
    "envelope_rate_mult": "Envelope renovation rate",
    "occupancy_mult": "Household size / occupancy",
    "population_mult": "Population growth",
    "dwelling_size_mult": "Dwelling floor area",
    "hdd_mult": "Heating degree days",
}


def sobol_demand():
    rows = list(csv.DictReader(open(RES / "global_sensitivity.csv")))
    rows.sort(key=lambda r: float(r["ST"]), reverse=True)
    names = [LABEL.get(r["driver"], r["driver"].replace("_", " ")) for r in rows]
    s1 = np.array([float(r["S1"]) for r in rows])
    st = np.array([float(r["ST"]) for r in rows])
    s1c = np.array([float(r["S1_conf"]) for r in rows])
    stc = np.array([float(r["ST_conf"]) for r in rows])

    y = np.arange(len(rows))[::-1]
    h = 0.36
    fig, ax = plt.subplots(figsize=(5.2, 2.8))
    ax.barh(y + h / 2, st, height=h, xerr=stc, color=PALETTE[0], alpha=0.85,
            error_kw=dict(ecolor="0.35", lw=1.0, capsize=3), label="Total effect (S$_T$)")
    ax.barh(y - h / 2, s1, height=h, xerr=s1c, color=PALETTE[1], alpha=0.85,
            error_kw=dict(ecolor="0.35", lw=1.0, capsize=3), label="First order (S$_1$)")
    for yi, v in zip(y, st):
        ax.text(v + 0.022, yi + h / 2, f"{v:.2f}", va="center", fontsize=9)
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.set_xlabel("Share of variance in 2050 EU useful-heat demand")
    ax.set_xlim(0, max(st.max(), s1.max()) * 1.22)
    ax.grid(axis="x")
    ax.legend(loc="lower right", frameon=False, fontsize=9)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(FIGDIR / f"P40_sobol_demand.{ext}")
    plt.close(fig)
    print("wrote P40_sobol_demand.{png,pdf}")
    for n, a, b in zip(names, s1, st):
        print(f"  {n:32s} S1={a:.3f}  ST={b:.3f}")


if __name__ == "__main__":
    sobol_demand()
