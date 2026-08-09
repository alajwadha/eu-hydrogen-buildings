"""Model-architecture flowchart (P00) for the methodology section.

Replaces the stale old/fig15_model_architecture.pdf, which wrongly labelled the model as
"3 scenarios" and a "power-law reduction trajectory". The model in fact runs FOUR multi-lever
scenarios (Current Policies, Stated Policies, Net Zero, H2 Push) and an LMDI multi-driver demand
trajectory (Eq.~demand), and the pipeline does not stop at the technology layer: it runs on into a
four-stage peak/dispatch block, namely the winter-peak merit order (Eq.~peakers, peakprice), the
peaking-investment missing-money rent (Eq.~missingmoney), the network capital bill (Eq.~infrabill)
and the explicit 8760-hour power-coupled dispatch (Eq.~dispatch). Green = bottom-up build,
blue = top-down reconciliation benchmark (matching the caption).

Verified against the methodology section: four scenarios (tab:scenarios), N = 200 Monte Carlo
samples per scenario (Uncertainty Quantification), eight heating technologies (tab:techparams).

Run: cd code && PYTHONPATH=. python -m scripts.fig_architecture
Out: paper/figs/paper/P00_model_architecture.pdf (+ .png)
"""
from __future__ import annotations
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from pathlib import Path
from scripts._figstyle import set_style
set_style()

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "paper" / "figs" / "paper"; OUT.mkdir(parents=True, exist_ok=True)


def box(ax, x, y, w, h, text, fc, ec, fs=9, eq=None):
    """Rounded box centred on (x, y); optional small equation tag in the corner."""
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0.02,rounding_size=0.05",
                                fc=fc, ec=ec, lw=1.3, zorder=3))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color="#1a1a1a", zorder=4)
    if eq:
        ax.text(x + w / 2 - 0.12, y - h / 2 + 0.16, eq, ha="right", va="bottom",
                fontsize=7.0, style="italic", color=ec, zorder=4)


def arrow(ax, x1, y1, x2, y2, ec="#555555"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=13,
                                 lw=1.4, color=ec, zorder=2))


def main():
    fig, ax = plt.subplots(figsize=(9.0, 9.6))
    ax.set_xlim(0, 10); ax.set_ylim(0, 16.4); ax.axis("off")
    GREEN, GE = "#e3f0e3", "#4f9d69"
    BLUE, BE = "#e1ecf6", "#2c6fb3"
    GREY, GYE = "#f1f1f1", "#999999"
    PURP, PE = "#efe9f5", "#7d6fb0"
    RED, RE = "#f7e2df", "#c0392b"

    # --- demand: two independent strands reconciled -------------------------------
    box(ax, 2.7, 15.5, 4.2, 1.45, "Bottom-up build  (green)\nEUBUCCO footprints, TABULA heat\n"
        "intensities, NUTS3 useful heat", GREEN, GE, fs=8.5)
    box(ax, 7.3, 15.5, 4.2, 1.45, "Top-down benchmark  (blue)\nHotmaps and census building-type\n"
        "shares, reconciliation check", BLUE, BE, fs=8.5)

    # --- shared engine: demand -> technology -> scenarios -------------------------
    box(ax, 5.0, 13.3, 7.4, 1.2, "Useful-heat demand to 2050\n"
        "LMDI multi-driver trajectory: power growth, household-size decline, "
        "envelope renovation", GREY, GYE, fs=8.7, eq="Eq. demand")
    box(ax, 5.0, 11.3, 7.4, 1.2, "Technology, cost and policy layers\n"
        "eight technologies, levelised cost and LCOH, ETS2 carbon, bans and mandates",
        GREY, GYE, fs=8.7)
    box(ax, 5.0, 9.3, 7.4, 1.2, "Four scenarios, Monte Carlo (N = 200 per scenario)\n"
        "Current Policies / Stated Policies / Net Zero / H2 Push",
        PURP, PE, fs=8.9, eq="tab. scenarios")

    # --- peak / dispatch block (the downstream stages the v7 method adds) ----------
    # Captions are hand-wrapped so every line sits inside the 4.4-wide box at fs 7.8.
    ax.text(5.0, 7.55, "Peak dispatch, peaking investment and network capital",
            ha="center", va="center", fontsize=10.5, fontweight="bold", color="#1a1a1a")
    box(ax, 2.7, 6.0, 4.4, 1.55, "Winter-peak merit order\n"
        "cold-snap slice dispatched among gas,\nhydrogen and heat-pump peakers,\n"
        "at an endogenous scarcity power price", RED, RE, fs=7.8, eq="Eq. peakers")
    box(ax, 7.3, 6.0, 4.4, 1.55, "Peaking-investment test\n"
        "inframarginal rent over the slice hours\nversus annualised peaker capital\n"
        "(the missing-money condition)", RED, RE, fs=7.8, eq="Eq. missingmoney")
    box(ax, 2.7, 3.7, 4.4, 1.55, "Network capital bill\n"
        "grid reinforcement, district-heat\nexpansion and hydrogen network,\n"
        "by pathway", RED, RE, fs=7.8, eq="Eq. infrabill")
    box(ax, 7.3, 3.7, 4.4, 1.55, "Explicit 8760-hour dispatch\n"
        "temperature-derated heat-pump load\nand Dunkelflaute, power coupling;\n"
        "robustness of the peak findings", RED, RE, fs=7.8, eq="Eq. dispatch")

    box(ax, 5.0, 1.55, 7.4, 1.05, "Outputs\n"
        "technology mix and emissions, LCOH, hydrogen peak slice it can win, "
        "missing-money gap and infrastructure bill", BLUE, BE, fs=8.5)

    # --- flow ---------------------------------------------------------------------
    arrow(ax, 2.9, 14.75, 4.3, 13.95)
    arrow(ax, 7.1, 14.75, 5.7, 13.95)
    arrow(ax, 5.0, 12.68, 5.0, 11.93)
    arrow(ax, 5.0, 10.68, 5.0, 9.93)
    # scenarios -> the two top peak boxes
    arrow(ax, 4.3, 8.78, 2.85, 6.83)
    arrow(ax, 5.7, 8.78, 7.15, 6.83)
    # within the peak block: top row -> bottom row
    arrow(ax, 2.7, 5.20, 2.7, 4.50, ec=RE)
    arrow(ax, 7.3, 5.20, 7.3, 4.50, ec=RE)
    # peak block -> outputs
    arrow(ax, 2.85, 2.90, 4.3, 2.10)
    arrow(ax, 7.15, 2.90, 5.7, 2.10)

    fig.savefig(OUT / "P00_model_architecture.pdf", bbox_inches="tight")
    # bbox_inches="tight" crops, so this needs its own dpi to clear Elsevier's 300 dpi
    # floor once the Word twin scales it to the column. At 200 it shipped at 213.
    fig.savefig(OUT / "P00_model_architecture.png", bbox_inches="tight", dpi=460)
    plt.close(fig)
    print("wrote P00_model_architecture.pdf/.png "
          "(four scenarios N=200, LMDI multi-driver, peak/missing-money/infrabill/dispatch stages)")


if __name__ == "__main__":
    main()
