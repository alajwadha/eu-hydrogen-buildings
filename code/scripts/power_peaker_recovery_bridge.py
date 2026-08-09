"""Investment caveat for the POWER peaker: the two strongest caveat numbers, made visual.

The power merit-order result (scripts/power_merit_order.py) shows hydrogen can take the
dispatchable-backup role on OPERATING cost. The caveat (paper sec:power:caveat) is that
operating-cost competitiveness does not finance the plant: at ~126 running hours a year the
inframarginal rent recovers only a small share of the hydrogen turbine's annualised capital,
and cumulatively to 2050 the build runs a large loss. This figure puts those two numbers,
which the section otherwise carries in prose only, on one self-contained panel.

It is deliberately kept distinct from the HEAT-side missing-money figure (F12, a different
model: scripts/merit_order_profit.py, the building/district-heat peaker). This is the POWER
peaker, read straight from the power dispatch's own outputs so the figure and the dispatch
never disagree.

Two panels, focused on Hydrogen Push (the only scenario in which hydrogen wins the dispatch
widely), EU+UK+CH aggregate:
  (a) Capital recovered from market revenue, 2030 to 2050: the hydrogen turbine (solid) climbs
      to about 15 per cent by 2050 and never approaches break-even; the gas peaker (dashed)
      slips the other way as the grid decarbonises. The other three scenarios are drawn faint
      for context.
  (b) Cumulative peaker profit to 2050: the hydrogen build loses about EUR 358 bn against about
      EUR 143 bn for an equivalent gas peaker, neither recovering its capital.

  Both panels print their own figures at the end of a run; the numbers quoted above are the
  live values and the run is the authority on them.

Reads:  results/power_peaker_recovery_projection.csv (year, scenario, gas/h2 recovery %)
        results/power_peaker_economics.csv         (per country/scenario/year cumulative profit)
Out:    paper/figs/paper/{P32_peaker_recovery_bridge}.png (+ pdf, + diagnostics mirror)
Run:    cd code && PYTHONUTF8=1 PYTHONPATH=. python -m scripts.power_peaker_recovery_bridge
"""
from __future__ import annotations
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
from src.Config import RESULTS_DIR
from scripts._figstyle import set_style, short_scen, assert_printable
set_style()

FS_ANN = 9.0
REPO = Path(__file__).resolve().parents[2]
FIGP = REPO / "paper" / "figs" / "paper"; FIGP.mkdir(parents=True, exist_ok=True)
FIGA = REPO / "paper" / "figs" / "diagnostics"; FIGA.mkdir(parents=True, exist_ok=True)

SCEN, YEAR = "H2_PUSH", 2050
START = 2030          # the build-out window over which recovery climbs toward its 2050 ceiling
H2_RED, GAS_GREY = "#c0392b", "#9a9a9a"
FAINT = "#cfcfcf"     # the three context scenarios in panel (a)
YEARS_MILE = [2025, 2030, 2040, 2050]


def save(fig, name):
    for d in (FIGP, FIGA):
        fig.savefig(d / f"{name}.png"); fig.savefig(d / f"{name}.pdf")
    plt.close(fig)


def _load():
    rec = pd.read_csv(RESULTS_DIR / "power_peaker_recovery_projection.csv")
    econ = pd.read_csv(RESULTS_DIR / "power_peaker_economics.csv")
    # EU+UK+CH aggregate cumulative profit by year, hydrogen vs gas, for the focus scenario.
    cum = (econ[econ.scenario == SCEN]
           .groupby("year")[["cum_gas_profit_meur", "cum_h2_profit_meur"]].sum()
           .reindex(YEARS_MILE) / 1e3)              # EUR bn
    return rec, cum


def panel_recovery(ax, rec):
    """(a) Share of the peaker's annualised capital recovered from market revenue, to 2050."""
    # context: the other three scenarios, faint, hydrogen only
    # These three were drawn with no legend entry at all, so the panel carried five lines
    # and explained two of them.
    for i, sc in enumerate(["CURRENT_POLICIES", "STATED_POLICIES", "NET_ZERO"]):
        d = rec[(rec.scenario == sc) & (rec.year >= START)]
        ax.plot(d.year, d.h2_recovery_pct, "-", color=FAINT, lw=1.2, zorder=2,
                label="H₂ turbine, other three scenarios" if i == 0 else None)
    d = rec[(rec.scenario == SCEN) & (rec.year >= START)].set_index("year")
    ax.plot(d.index, d.h2_recovery_pct, "-", color=H2_RED, lw=2.4, zorder=4,
            label="H₂ turbine (H₂ Push)")
    ax.plot(d.index, d.gas_recovery_pct, "--", color=GAS_GREY, lw=1.8, zorder=3,
            label="Gas peaker (H₂ Push)")
    end = float(d.loc[YEAR, "h2_recovery_pct"])
    ax.scatter([YEAR], [end], color=H2_RED, s=34, zorder=5)
    # "15%" alone reads as a contradiction of the paper's 9 per cent headline. The two are
    # different aggregations of the same run: this is the study-area total, the headline is
    # weighted by the capacity that actually gets built.
    ax.annotate(f"{end:.0f}% by 2050\n(study-area aggregate)", xy=(YEAR, end),
                xytext=(-6, 14), textcoords="offset points", ha="right", va="bottom",
                fontsize=8.6, fontweight="bold", color=H2_RED)
    ax.axhline(100, color="#333333", lw=1.0, zorder=1)
    ax.text(START + 0.3, 100, "break-even (100%)", fontsize=FS_ANN, va="bottom", color="#333333")
    ax.axhline(0, color="#bbbbbb", lw=0.8, zorder=1)
    ax.set_xlim(START, YEAR); ax.set_ylim(-60, 115)
    ax.set_xticks([2030, 2035, 2040, 2045, 2050])
    ax.set_ylabel("Capital recovered from market revenue (%)")
    ax.set_xlabel("Year")
    ax.set_title("(a)", loc="left")
    # Lower right put the legend box on top of the three context lines it had just been
    # written to explain, which is worse than leaving them unlabelled, and upper right ran
    # into the y-axis tick labels. Below the axes is where the other reworked panels put
    # theirs.
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=1, frameon=False,
              fontsize=FS_ANN - 0.6)
    ax.grid(axis="y", color="#ececec", lw=0.8, zorder=0); ax.set_axisbelow(True)
    return end


def panel_cumulative(ax, cum):
    """(b) Cumulative peaker profit to 2050: hydrogen vs an equivalent gas peaker."""
    yrs = cum.index.values
    ax.plot(yrs, cum.cum_gas_profit_meur, "-o", ms=5, color=GAS_GREY, lw=2.0,
            label="Gas peaker", zorder=3)
    ax.plot(yrs, cum.cum_h2_profit_meur, "-s", ms=5, color=H2_RED, lw=2.2,
            label="H₂ turbine", zorder=4)
    ax.fill_between(yrs, cum.cum_h2_profit_meur, cum.cum_gas_profit_meur,
                    color=H2_RED, alpha=0.08, zorder=1,
                    label="hydrogen's excess loss over gas")
    g50 = float(cum.loc[YEAR, "cum_gas_profit_meur"])
    h50 = float(cum.loc[YEAR, "cum_h2_profit_meur"])
    ax.annotate(f"−€{abs(h50):.0f} bn", xy=(YEAR, h50), xytext=(-6, -2),
                textcoords="offset points", ha="right", va="top",
                fontsize=9.5, fontweight="bold", color=H2_RED)
    ax.annotate(f"−€{abs(g50):.0f} bn", xy=(YEAR, g50), xytext=(-6, 10),
                textcoords="offset points", ha="right", va="bottom",
                fontsize=9.5, fontweight="bold", color="#6f6f6f")
    ax.axhline(0, color="#bbbbbb", lw=0.8, zorder=1)
    ax.set_xlim(2025, YEAR); ax.set_xticks(YEARS_MILE)
    ax.set_ylabel("Cumulative peaker profit to year (€ bn)")
    ax.set_xlabel("Year")
    ax.set_title("(b)", loc="left")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=1, frameon=False,
              fontsize=FS_ANN - 0.6)
    ax.grid(axis="y", color="#ececec", lw=0.8, zorder=0); ax.set_axisbelow(True)
    return g50, h50


def main():
    rec, cum = _load()
    # An 11.4 in canvas placed at 0.96\textwidth printed the 8.5 pt annotations at
    # 4.6 pt. Drawn at the column width instead so the fonts print as set.
    FIGW_IN = 7.4
    assert_printable(FIGW_IN, {"annotation/legend": FS_ANN, "axis/tick default": 9.0},
                     column="long", width_frac=0.96, label="P32_peaker_recovery_bridge")
    fig, (axa, axb) = plt.subplots(1, 2, figsize=(FIGW_IN, 3.6))
    end = panel_recovery(axa, rec)
    g50, h50 = panel_cumulative(axb, cum)
    save(fig, "P32_peaker_recovery_bridge")
    print(f"P32 panel (a): H2 recovers {end:.0f}% of annualised capital by 2050 (gas slips below break-even).")
    print(f"P32 panel (b): cumulative to 2050  H2 -EUR{abs(h50):.0f} bn  vs  gas -EUR{abs(g50):.0f} bn.")
    print("Wrote P32_peaker_recovery_bridge (png+pdf) -> paper/figs/paper + diagnostics")


if __name__ == "__main__":
    main()
