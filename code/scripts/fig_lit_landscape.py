"""Literature positioning map (P_LIT) for the literature review.

An orienting schematic for the thematic review's central gap statement
(Section on hydrogen in buildings, and the closing research-gap section). It
places the major comparative hydrogen-versus-heat-pump studies on the two axes
the prose argues are the live gaps:

  x: spatial resolution at which the comparison is resolved, from a single
     building, through a single country and an EU aggregate or coarse zonal
     model, to the sub-national NUTS3 grain;
  y: how hydrogen's heating share is determined, from an imposed or exogenous
     scenario target, through a system optimisation that does not isolate
     hydrogen's position in the heating merit order, to a share derived
     endogenously from where hydrogen wins the heating peak.

The point is visual: every prior comparative study sits in the lower and middle
bands and to the left of NUTS3, leaving the upper-right cell, a merit-order
derived share at sub-national resolution, empty. That empty cell is the gap this
paper fills, marked here by the star. Nothing in this figure is a model result;
it is a map of the cited literature, so no value is read from results.

Run: cd code && PYTHONUTF8=1 PYTHONPATH=. python -m scripts.fig_lit_landscape
Out: paper/figs/paper/P_LIT_landscape.pdf (+ .png)
"""
from __future__ import annotations
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D
from pathlib import Path
from scripts._figstyle import set_style, PALETTE, assert_printable
set_style()

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "paper" / "figs" / "paper"; OUT.mkdir(parents=True, exist_ok=True)

# ── Axes ───────────────────────────────────────────────────────────────────
# x: spatial resolution. Ordinal bands 0..3 (the studies sit on or between them).
#   0 single building | 1 single country | 2 EU aggregate or coarse zonal | 3 NUTS3
# y: how hydrogen's heating share is set. Ordinal bands 0..2.
#   0 imposed or exogenous target | 1 system optimisation, not heating merit order
#   2 merit-order derived at the heating peak
XT = ["Single\nbuilding", "Single\ncountry", "EU aggregate or\ncoarse zonal", "Sub-national\n(NUTS3)"]
YT = ["Imposed or\nexogenous target",
      "System optimisation,\nnot heating merit order",
      "Merit-order derived\nat the heating peak"]

# Each study: (label, x, y). Positions are slightly jittered within a band so
# co-located studies stay legible; the band, not the decimal, carries the claim.
STUDIES = [
    ("Maestre 2021, 2022",  0.30, 0.18),   # Spain, single building / stock, imposed mix
    ("Huckebrink 2022",     1.00, 0.30),   # Germany, techno-economic, imposed shares
    ("Dickel 2024",         1.00, 0.05),   # Germany, wholesale conversion assessed
    ("Badakhsh 2023",       1.18, 0.92),   # UK buildings, efficiency-led, exogenous
    ("Slorach 2021",        0.84, 1.05),   # UK net zero, system options
    ("Billerbeck 2023",     1.55, 1.18),   # model-based race, optimisation, EU/DE
    ("Berger 2020",         2.05, 1.10),   # European power-to-gas LP, coarse zonal
    ("ICCT 2023",           2.18, 0.30),   # EU households 2050, climate-zone archetypes
    ("Rosenow 2022",        2.18, 0.78),   # EU/global evidence review
]

THIS = ("This paper", 3.0, 2.0)

GAP_BLUE   = PALETTE[0]   # this paper / the open cell
STUDY_GREY = "#7f7f7f"
STUDY_FACE = "#f4f4f4"


def main():
    FIGW_IN = 8.8
    assert_printable(FIGW_IN, {"cell/axis label": 8.6, "tick + legend": 8.6,
                               "column header": 9.2}, column="long",
                     label="P_LIT_landscape")
    fig, ax = plt.subplots(figsize=(FIGW_IN, 6.3))

    # Plot frame slightly beyond the band range so labels and the gap cell breathe.
    ax.set_xlim(-0.45, 3.55)
    ax.set_ylim(-0.40, 2.45)

    # ── Shade the open quadrant the paper fills (NUTS3 x merit-order derived) ──
    ax.add_patch(FancyBboxPatch(
        (2.5 - 0.0, 1.5 - 0.0), 1.02, 0.93,
        boxstyle="round,pad=0.0,rounding_size=0.04",
        fc="#e8f0f8", ec=GAP_BLUE, lw=1.3, ls=(0, (5, 3)), zorder=1))
    ax.text(3.01, 1.97 + 0.30, "Open cell filled\nby this paper",
            ha="center", va="center", fontsize=8.6, color=GAP_BLUE,
            fontstyle="italic", zorder=5)

    # ── Soft gridlines on the band boundaries (behind everything) ─────────────
    for gx in (0.5, 1.5, 2.5):
        ax.axvline(gx, color="#e3e3e3", lw=0.9, zorder=0)
    for gy in (0.5, 1.5):
        ax.axhline(gy, color="#e3e3e3", lw=0.9, zorder=0)

    # ── The cited studies ─────────────────────────────────────────────────────
    for label, x, y in STUDIES:
        ax.scatter(x, y, s=46, marker="o", facecolor=STUDY_FACE,
                   edgecolor=STUDY_GREY, lw=1.2, zorder=4)
        ax.annotate(label, (x, y), xytext=(0, 9), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8.6, color="#2b2b2b",
                    zorder=6)

    # ── This paper ────────────────────────────────────────────────────────────
    lbl, x, y = THIS
    ax.scatter(x, y, s=240, marker="*", facecolor=GAP_BLUE,
               edgecolor="white", lw=1.1, zorder=7)
    ax.annotate(lbl, (x, y), xytext=(0, -16), textcoords="offset points",
                ha="center", va="top", fontsize=9.2, fontweight="bold",
                color=GAP_BLUE, zorder=7)

    # ── Band tick labels ──────────────────────────────────────────────────────
    ax.set_xticks([0, 1, 2, 3]); ax.set_xticklabels(XT, fontsize=8.6)
    ax.set_yticks([0, 1, 2]);    ax.set_yticklabels(YT, fontsize=8.6)
    ax.set_xlabel("Spatial resolution of the comparison")
    ax.set_ylabel("How hydrogen's heating share is determined")

    # No data grid (the band lines above stand in); keep the frame minimal.
    ax.grid(False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)

    legend = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=STUDY_FACE,
               markeredgecolor=STUDY_GREY, markersize=8, label="Prior comparative study"),
        Line2D([0], [0], marker="*", color="none", markerfacecolor=GAP_BLUE,
               markeredgecolor="white", markersize=15, label="This paper"),
    ]
    ax.legend(handles=legend, loc="upper left", bbox_to_anchor=(0.005, 0.998),
              frameon=False, fontsize=8.6, handletextpad=0.4, borderaxespad=0.2)

    fig.savefig(OUT / "P_LIT_landscape.pdf", bbox_inches="tight")
    fig.savefig(OUT / "P_LIT_landscape.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("wrote P_LIT_landscape.pdf/.png (9 studies + this paper; open NUTS3 x merit-order cell)")


if __name__ == "__main__":
    main()
