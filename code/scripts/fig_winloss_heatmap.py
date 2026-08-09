"""Win/loss heatmap: 29 countries x 3 arenas, under H2 Push.

The paper's first contribution is the heterogeneity of where hydrogen can win the
cold-snap peak. This figure makes that heterogeneity visible at a glance: rows are the
29 modelled countries, columns are the three linked arenas the paper tests on one
operating-cost basis -- the building winter peak, the district-heating stack, and the
power-sector peaker -- and each cell is coloured by whether hydrogen WINS or LOSES on
operating cost in the most carbon-ambitious scenario (H2 Push).

A win is further split into DECISIVE (a salt-cavern market, where seasonal storage is
cheap and the win carries the firm-capacity tip) and MARGINAL (a non-cavern win that
the missing-money result subordinates). This is the honest bimodal refinement behind the
16 / 20 / 15 win counts: the counts are real, but only the ~7 cavern markets are decisive.

Win flags are read from the per-country results CSVs that drive Table 5 (tab:arenas):
  building winter peak : results/merit_order_heat.csv     (h2_wins_peak)
  district-heat stack  : results/merit_order_dh.csv       (h2_beats_gas_chp)
  power peaker         : results/power_peaker_economics.csv (h2_var < gas_var, 2050)

Outputs (paper figure family + Abdul summary):
  paper/figs/paper/P35_winloss.png / .pdf
  paper/figs/diagnostics/F35_winloss.png / .pdf

Run: cd code && PYTHONUTF8=1 PYTHONPATH=. python -m scripts.fig_winloss_heatmap
"""
from __future__ import annotations
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
from pathlib import Path
from src.Config import RESULTS_DIR
from scripts._figstyle import set_style, assert_printable
from scripts.merit_order_heat import CAVERN
set_style()

REPO = Path(__file__).resolve().parents[2]
FIG = REPO / "paper" / "figs" / "diagnostics"; FIG.mkdir(parents=True, exist_ok=True)
FIGP = REPO / "paper" / "figs" / "paper"; FIGP.mkdir(parents=True, exist_ok=True)

SCEN = "H2_PUSH"
ARENAS = ["Building\nwinter peak", "District-heat\nstack", "Power\npeaker"]

# Cell states: 0 = loss, 1 = marginal win (non-cavern), 2 = decisive win (cavern market).
LOSS, MARGINAL, DECISIVE = 0, 1, 2
COL_LOSS = "#e6ecf2"      # pale grey-blue: hydrogen loses
COL_MARGINAL = "#f3b07a"  # warm amber: a marginal (non-cavern) win
COL_DECISIVE = "#b5202a"  # deep red: a decisive cavern-market win
CMAP = ListedColormap([COL_LOSS, COL_MARGINAL, COL_DECISIVE])
NORM = BoundaryNorm([-0.5, 0.5, 1.5, 2.5], CMAP.N)

# Readable country names (ISO -> display); ordered with cavern markets grouped at the top.
NAME = {"DE": "Germany", "NL": "Netherlands", "FR": "France", "DK": "Denmark", "UK": "United Kingdom",
        "PL": "Poland", "RO": "Romania", "AT": "Austria", "BE": "Belgium", "BG": "Bulgaria",
        "CH": "Switzerland", "CY": "Cyprus", "CZ": "Czechia", "EE": "Estonia", "EL": "Greece",
        "ES": "Spain", "FI": "Finland", "HR": "Croatia", "HU": "Hungary", "IE": "Ireland",
        "IT": "Italy", "LT": "Lithuania", "LU": "Luxembourg", "LV": "Latvia", "MT": "Malta",
        "PT": "Portugal", "SE": "Sweden", "SI": "Slovenia", "SK": "Slovakia"}


def _win_flags():
    """Per-country boolean win in each of the three arenas under H2 Push."""
    h = pd.read_csv(RESULTS_DIR / "merit_order_heat.csv")
    h = h[h.scenario == SCEN].set_index("country")
    bld = h["h2_wins_peak"].astype(bool)

    dh = pd.read_csv(RESULTS_DIR / "merit_order_dh.csv")
    dh = dh[dh.scenario == SCEN].set_index("country")
    dhw = dh["h2_beats_gas_chp"].astype(bool)

    pe = pd.read_csv(RESULTS_DIR / "power_peaker_economics.csv")
    pe = pe[(pe.scenario == SCEN) & (pe.year == 2050)].set_index("country")
    pkw = (pe["h2_var_eur_mwh"] < pe["gas_var_eur_mwh"])

    countries = sorted(set(bld.index) | set(dhw.index) | set(pkw.index))
    return countries, bld, dhw, pkw


def main():
    countries, bld, dhw, pkw = _win_flags()
    # order: cavern markets first (decisive cluster), then the rest, each alphabetical by name
    cav = sorted([c for c in countries if c in CAVERN], key=lambda c: NAME.get(c, c))
    rest = sorted([c for c in countries if c not in CAVERN], key=lambda c: NAME.get(c, c))
    order = cav + rest

    def state(c, won):
        if not bool(won.get(c, False)):
            return LOSS
        return DECISIVE if c in CAVERN else MARGINAL

    M = np.array([[state(c, bld), state(c, dhw), state(c, pkw)] for c in order])

    n = len(order)
    FIGW_IN = 7.2
    assert_printable(FIGW_IN, {"country label": 8.5, "legend": 8.5, "arena header": 9.5,
                               "annotation": 9.0}, column="long", width_frac=0.86,
                     label="P35_winloss")
    fig, ax = plt.subplots(figsize=(FIGW_IN, 0.34 * n + 1.9))
    fig.patch.set_facecolor("white"); ax.set_facecolor("white")
    ax.imshow(M, cmap=CMAP, norm=NORM, aspect="auto")

    # gridlines between cells
    ax.set_xticks(np.arange(-0.5, 3, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.6)
    ax.tick_params(which="minor", length=0)
    ax.grid(which="major", visible=False)

    ax.set_xticks(range(3)); ax.set_xticklabels(ARENAS, fontsize=9.5)
    ax.set_yticks(range(n))
    ylab = [NAME.get(c, c) + ("  (cavern)" if c in CAVERN else "") for c in order]
    ax.set_yticklabels(ylab, fontsize=8.5)
    ax.tick_params(length=0)
    ax.xaxis.set_ticks_position("top")
    for spine in ax.spines.values():
        spine.set_visible(False)

    # separator line under the cavern cluster
    ax.axhline(len(cav) - 0.5, color="#333333", lw=1.1)

    # per-column win counts in a footnote row of text under the axis
    counts = [int((M[:, j] > 0).sum()) for j in range(3)]
    for j, cnt in enumerate(counts):
        ax.text(j, n - 0.35, f"{cnt}/29", ha="center", va="top", transform=ax.transData,
                fontsize=9, fontweight="bold", color="#333333", clip_on=False)

    legend = [Patch(facecolor=COL_DECISIVE, label="Decisive win (salt-cavern market)"),
              Patch(facecolor=COL_MARGINAL, label="Marginal win (no cavern)"),
              Patch(facecolor=COL_LOSS, edgecolor="#cccccc", label="Hydrogen loses")]
    ax.legend(handles=legend, loc="upper center", bbox_to_anchor=(0.5, -0.05),
              ncol=3, frameon=False, fontsize=8.5)
    ax.set_ylim(n - 0.5 + 0.6, -0.5)  # leave room for the count row at the bottom

    for d, n_ in [(FIG, "F35_winloss"), (FIGP, "P35_winloss")]:
        fig.savefig(d / f"{n_}.png"); fig.savefig(d / f"{n_}.pdf")
    plt.close(fig)
    dec = {j: int((M[:, j] == DECISIVE).sum()) for j in range(3)}
    print(f"Win/loss heatmap: building {counts[0]}/29 (decisive {dec[0]}), "
          f"district-heat {counts[1]}/29 (decisive {dec[1]}), "
          f"power peaker {counts[2]}/29 (decisive {dec[2]}); cavern cluster = {sorted(CAVERN)}")
    print(f"Wrote P35_winloss -> {FIGP}")


if __name__ == "__main__":
    main()
