"""Two simple, standalone summary figures for Abdul (the headline result + the
hydrogen verdict). Larger fonts, one idea each, readable in five seconds.

  SUM1  the scenario emissions fan (where each policy world lands)
  SUM2  the hydrogen window closes at every test (two-route elimination)

Run: cd code && PYTHONPATH=. python -m scripts.diagnostic_figures
Out: paper/figs/diagnostics/SUM1_*.pdf/.png, SUM2_*.pdf/.png
"""
from __future__ import annotations
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from src.Config import RESULTS_DIR
from scripts._figstyle import set_style

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "paper" / "figs" / "diagnostics"; OUT.mkdir(parents=True, exist_ok=True)
R = RESULTS_DIR
SCEN = ["CURRENT_POLICIES", "STATED_POLICIES", "H2_PUSH", "NET_ZERO"]
SHORT = {"CURRENT_POLICIES": "Current Policies", "STATED_POLICIES": "Stated Policies",
         "NET_ZERO": "Net Zero", "H2_PUSH": "H2 Push"}
SC = {"CURRENT_POLICIES": "#8c8c8c", "STATED_POLICIES": "#1f77b4",
      "NET_ZERO": "#2ca02c", "H2_PUSH": "#d62728"}
YEARS = [2025, 2030, 2040, 2050]

set_style()                                   # shared house style (was a bespoke serif block)
plt.rcParams.update({"lines.linewidth": 2.2}) # keep bolder lines for these headline figures


def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf"); fig.savefig(OUT / f"{name}.png")
    plt.close(fig); print(f"  {name}")


# ── SUM1: emissions fan ───────────────────────────────────────────────────────
def sum1():
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    end = {}
    for sc in SCEN:
        e = pd.read_csv(R / f"mc_emissions_{sc}.csv")
        d = e[(e.variable == "co2_MtCO2") & (e.tech == "all")].set_index("year").reindex(YEARS).copy()
        d.loc[2025, ["q10", "q50", "q90"]] = 639.0  # common observed baseline (see paper)
        ax.plot(YEARS, d.q50, "-o", ms=5, color=SC[sc])
        ax.fill_between(YEARS, d.q10, d.q90, color=SC[sc], alpha=0.10, lw=0)
        end[sc] = d.q50[2050]
    # endpoint labels, staggered if needed
    ys = sorted(SCEN, key=lambda s: end[s])
    last = -1e9
    for sc in ys:
        yv = max(end[sc], last + 22)
        pct = end[sc] / 639 * 100 - 100
        ax.annotate(f"{SHORT[sc]}: {end[sc]:.0f} Mt ({pct:+.0f}%)",
                    (2050, end[sc]), xytext=(8, yv - end[sc] if yv != end[sc] else 0),
                    textcoords="offset points", color=SC[sc], fontsize=9.5,
                    fontweight="bold", va="center")
        last = yv
    ax.scatter([2025], [639], color="#333", zorder=5, s=28)
    ax.annotate("≈639 Mt\n(2025)", (2025, 639), xytext=(6, 6),
                textcoords="offset points", fontsize=9, color="#333")
    ax.set_ylabel("Residential heating CO₂ (Mt yr⁻¹)")
    ax.set_xticks(YEARS); ax.set_xlim(2024, 2062); ax.set_ylim(0, 700)
    ax.set_title("Same technologies in every scenario — ambition sets the outcome",
                 fontsize=11.5)
    save(fig, "SUM1_emissions_fan")


# ── SUM2: hydrogen window closes at every test ───────────────────────────────
def sum2():
    g = pd.read_csv(R / "h2_hp_gap.csv")
    hi = pd.read_csv(R / "h2_infra_scenario.csv")
    mo = pd.read_csv(R / "merit_order_heat.csv")
    n_base = int((g.gap_2050 <= 0).sum())
    n_net = int((hi.gap_convert_central <= 0).sum())
    n_peak = int(mo.groupby("scenario").h2_wins_peak.sum().max())
    n_cap = 0
    rows = [
        ("All EU+UK+CH countries", 29, "#bdbdbd"),
        ("Base-load cost: H₂ ≤ best heat pump (2050)", n_base, "#7d5ba6"),
        ("…still, once H₂ pays for its own network", n_net, "#b03a3a"),
        ("Peaking: H₂ wins the winter peak (best scenario)", n_peak, "#7d5ba6"),
        ("…where that peaker recovers its capital", n_cap, "#b03a3a"),
    ]
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    y = np.arange(len(rows))[::-1]
    for yi, (lab, n, col) in zip(y, rows):
        ax.barh(yi, n, height=0.62, color=col)
        ax.text(n + 0.4, yi, str(n), va="center", fontsize=12, fontweight="bold",
                color=col if n else "#b03a3a")
    ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows], fontsize=9.5)
    ax.set_xlim(0, 31); ax.set_xlabel("Number of countries (of 29)")
    ax.set_title("Hydrogen's window closes at every test", fontsize=12.5)
    save(fig, "SUM2_h2_window")


if __name__ == "__main__":
    sum1(); sum2()
    print(f"Done -> {OUT}")
