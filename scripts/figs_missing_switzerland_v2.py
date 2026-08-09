"""Switzerland body figure, redrawn from the manuscript's own numbers.

  switzerland_2050 : Swiss levelised cost of heat, 2025 vs 2050, grouped bars.
                     Heat-pump LCOH undercuts the hydrogen boiler and crushes the gas
                     boiler in both years. Every value is read from
                     results/swiss_integration.csv (limit mode, Stated Policies) at draw
                     time. An earlier version transcribed the numbers as literals, which
                     matched the CSV but would not have moved if the model did.
                     No title, no on-chart insight text.

Grey 2025 bars, technology-coloured 2050 bars; every value is labelled so the figure
reads in greyscale and for colour-vision deficiency.

Run:  cd code && PYTHONPATH=. python -m scripts.figs_missing_switzerland_v2
Out:  paper/figs/paper/switzerland_2050.{png,pdf}
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scripts._figstyle import set_style, TECH_COLOR, H2_HATCH, ink_h2_hatch
set_style()
plt.rcParams.update({"figure.autolayout": False, "savefig.bbox": "tight"})

# Hydrogen was "#e07b39" here, which is the DISTRICT-HEAT orange in the house palette
# (paper_figures.TECH_COLOR), while hydrogen there is "#7d5ba6". The same carrier therefore
# had two colours across the submission's own figures, one of them another carrier's. Aligned
# to the house palette, with the hatch this paper uses for hydrogen elsewhere.
HP, H2, GAS = (TECH_COLOR["hp_air"], TECH_COLOR["h2_boiler"],
               TECH_COLOR["gas_boiler"])
INK, SOFT = "#1a1a1a", "#6b6b6b"
FIGDIR = Path(__file__).resolve().parents[2] / "paper" / "figs" / "paper"
RES = Path(__file__).resolve().parents[1] / "results"

# The standalone Swiss case: no domestic caverns, so the storage adder is the
# non-cavern one. "limit" is the standalone treatment the body figure reports; the
# endogenous coupling is discussed in the text and tabulated in the SI.
MODE, SCEN = "limit", "STATED_POLICIES"
COLS = ["hp_ground_lcoh", "hp_air_lcoh", "h2_boiler_lcoh", "gas_lcoh"]


def switzerland_2050():
    """Swiss levelised cost of heat, 2025 vs 2050, grouped bars, read from
    results/swiss_integration.csv (limit mode, Stated Policies)."""
    labels = ["Heat pump\n(ground)", "Heat pump\n(air)", "Hydrogen\nboiler", "Gas\nboiler"]
    d = pd.read_csv(RES / "swiss_integration.csv")
    d = d[(d["mode"] == MODE) & (d["scenario"] == SCEN)].set_index("year")
    v2025 = [round(float(d.loc[2025, c])) for c in COLS]
    v2050 = [round(float(d.loc[2050, c])) for c in COLS]
    # COLS order is ground, air, hydrogen, gas. This list had the two blues the wrong
    # way round against TECH_COLOR, so a reader comparing Fig. 3 and Fig. 7 read
    # air-source as ground-source. Taken from the house palette now.
    cols = [TECH_COLOR["hp_ground"], TECH_COLOR["hp_air"],
            TECH_COLOR["h2_boiler"], TECH_COLOR["gas_boiler"]]
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    x = range(len(labels)); w = 0.38
    # The 2050 series carries four different colours, and matplotlib takes a legend swatch
    # from the first patch only, so a "2050" entry showed as dark blue against three bars
    # that are medium blue, purple and grey. The grey 2050 gas bar was also mistakable for
    # a 2025 bar. Year needs an encoding one swatch can honestly stand for, and it was
    # hatch, which this paper reserves for hydrogen: the 2025 hydrogen bar came out purple
    # and hatched, pixel for pixel the hydrogen encoding of Fig. 3, here meaning "2025".
    # Year is now a pale fill inside a solid outline of its own colour, which no other
    # figure uses for anything, and hatch stays reserved.
    bars25 = ax.bar([i - w / 2 for i in x], v2025, w, color=cols, alpha=0.32,
                    edgecolor=cols, linewidth=1.2, zorder=3)
    b50 = ax.bar([i + w / 2 for i in x], v2050, w, color=cols, zorder=3)
    # Hydrogen's purple sits 7.6 of 441 from the ground-source blue under simulated
    # protanopia, so on this figure colour alone does not separate them. The hatch is
    # what the house rule reserves for exactly this, and it was declared and not used.
    for b in (bars25[2], b50[2]):
        b.set_hatch(H2_HATCH); ink_h2_hatch(b)
    # One size and one ink for all eight labels. They used to differ three ways at once,
    # 9 pt grey for 2025 against 10.5 pt near-black and bold for 2050, so the row read as
    # two kinds of number rather than one series. The year is already carried by the pale
    # and solid fills and named in the legend, so the labels do not have to carry it too.
    for i in x:
        ax.text(i - w / 2, v2025[i] + 4, f"€{v2025[i]}", ha="center", fontsize=9.5,
                color=INK)
        ax.text(i + w / 2, v2050[i] + 4, f"€{v2050[i]}", ha="center", fontsize=9.5,
                color=INK)
    ax.set_xticks(list(x)); ax.set_xticklabels(labels)
    # 300 clipped the 2025 hydrogen bar's own EUR 298 label, which is drawn 4 above the bar.
    ax.set_ylim(0, 330)
    ax.set_ylabel("Levelised cost of heat (€/MWh useful)")
    ax.grid(axis="y"); ax.margins(x=0.06)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(facecolor="#8c8c8c", alpha=0.32, edgecolor="#8c8c8c",
                             linewidth=1.2, label="2025 (pale fill)"),
                       Patch(facecolor="#8c8c8c", label="2050 (solid fill)")],
              loc="upper center", bbox_to_anchor=(0.5, -0.11), ncol=2, frameon=False,
              fontsize=9.5, handlelength=1.5)
    fig.subplots_adjust(left=0.10, right=0.97, top=0.96, bottom=0.22)
    for out in ("switzerland_2050.png", "switzerland_2050.pdf"):
        fig.savefig(FIGDIR / out)
    plt.close(fig)
    print(f"wrote switzerland_2050.{{png,pdf}}  2025={v2025}  2050={v2050}")


if __name__ == "__main__":
    switzerland_2050()
