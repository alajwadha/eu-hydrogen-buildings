"""Model-architecture figure: what the model takes in, and the three tests it runs.

Main paper Figure 2, Applied Energy submission Figure 1.

WHY THIS IS NOT A PIPELINE INVENTORY. The previous version drew seven numbered stages,
about thirty-five labelled boxes and a header band carrying twelve bullet points, which
is a methods section rendered as a graphic. A reader cannot hold that; the useful thing
a roadmap figure does is show the shape of the argument, and the argument here is three
tests applied in sequence to the same technologies. Everything the old figure listed
about data sources, technology coverage and parameter ranges is named in the methods
prose and in the supplement, so it is dropped here rather than duplicated.

The figure is also deliberately structural. It carries no results, because the graphical
abstract already reports them and a reader meeting both should not see the same counts
twice.

LAYOUT NOTE. \\includegraphics[width=\\textwidth] scales a figure by its WIDTH alone, so
printed legibility is (font size in points) / (figure width in inches) times the column
width. A narrower canvas at the same font size therefore prints LARGER. Cutting the
content let the canvas come down from 7.4 in to 6.6 in, which lifts every printed font
by about 12 per cent against the old figure while the fonts themselves are unchanged.

Near-monochrome by design, so it reproduces cleanly in greyscale and in print.

Run:  cd code && PYTHONPATH=. python -m scripts.fig_model_flow
Out:  paper/figs/paper/P00_model_flow.{png,pdf}
"""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from scripts._figstyle import set_style, assert_printable

set_style()
plt.rcParams.update({"figure.autolayout": False, "savefig.bbox": "tight",
                     "axes.grid": False})

OUT = Path(__file__).resolve().parents[2] / "paper" / "figs" / "paper"
OUT.mkdir(parents=True, exist_ok=True)

INK, LINE, SOFT = "#1a1a1a", "#4d4d4d", "#6b6b6b"
FILL, PANEL, TEST = "#ffffff", "#f7f8f9", "#eceff2"

FIGW = 6.6
PT_PER_UNIT = FIGW * 72.0 / 100.0

FS_BAND, FS_BOX, FS_SUB, FS_TEST, FS_ASK = 11.6, 10.4, 9.6, 11.6, 9.6

_FITS: list = []
MIN_CLEARANCE = 0.30


def rbox(ax, x0, y0, x1, y1, fc=FILL, ec=LINE, lw=0.9, r=0.6, z=2):
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0,
                                boxstyle=f"round,pad=0,rounding_size={r}",
                                facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z))


def ctext(ax, x, y, s, fs=FS_BOX, w="normal", c=INK, z=5, style="normal"):
    return ax.text(x, y, s, ha="center", va="center", fontsize=fs, fontweight=w,
                   color=c, zorder=z, style=style, linespacing=1.40)


def fitted(ax, x, y, s, box, **kw):
    """A centred label that the build checks against the box drawn around it."""
    _FITS.append((ctext(ax, x, y, s, **kw), box))


def arrow(ax, x0, y0, x1, y1, c=LINE, lw=1.0, z=3):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                 mutation_scale=8, color=c, linewidth=lw,
                                 shrinkA=0, shrinkB=0, zorder=z))


def assert_fits(fig, ax, label):
    """Fail loudly if any label has outgrown the box drawn around it.

    Every label is hand-placed in data coordinates, so a reworded box or a changed
    font silently spills text across its own border. The check runs on every build
    rather than on inspection.
    """
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    bad, worst = [], None
    for t, (bx0, by0, bx1, by1) in _FITS:
        bb = t.get_window_extent(renderer=r).transformed(ax.transData.inverted())
        margin = min(bb.x0 - bx0, bx1 - bb.x1, bb.y0 - by0, by1 - bb.y1)
        if worst is None or margin < worst[0]:
            worst = (margin, t.get_text().replace("\n", " / "))
        if margin < MIN_CLEARANCE:
            bad.append(f"    {t.get_text()!r} clears its box by only {margin:+.3f} canvas "
                       f"units, {margin * PT_PER_UNIT:+.2f} pt")
    if bad:
        raise SystemExit(f"{label}: {len(bad)} label(s) below the {MIN_CLEARANCE} "
                         f"canvas-unit clearance floor:\n" + "\n".join(bad))
    print(f"  {label}: {len(_FITS)} labels clear their boxes, tightest "
          f"{worst[0]:+.3f} units on {worst[1]!r}")


# Three inputs, named by what they are rather than by the file they arrive in.
INPUTS = [
    ("Building stock", "footprints, archetypes,\ndwelling counts"),
    ("Costs and performance", "capital, efficiencies,\nlifetimes, cost of capital"),
    ("Power and geology", "2050 capacity, renewables,\nsalt caverns"),
]

# The spine of the paper. Each test is a question, and the order matters: a technology
# that fails an earlier one never reaches the later ones.
TESTS = [
    ("1. Levelised cost",
     "Which carrier gives a MWh\nof useful heat for least,\neach charged its last mile\nand its seasonal store?"),
    ("2. Merit order",
     "Which is cheapest to run\nat the winter peak, across\nbuilding heat, district\nheat and the power peaker?"),
    ("3. Capital recovery",
     "Does scarcity rent cover\nthe annualised cost of\nbuilding the plant, and if\nnot, what payment would?"),
]


def model_flow():
    fonts = {"band": FS_BAND, "box": FS_BOX, "sub": FS_SUB,
             "test": FS_TEST, "ask": FS_ASK}
    assert_printable(FIGW, fonts, column="ae_body", label="P00_model_flow (AE body)")
    assert_printable(FIGW, fonts, column="long", width_frac=0.80,
                     label="P00_model_flow (long paper)")

    H = 89.0
    fig, ax = plt.subplots(figsize=(FIGW, FIGW * H / 100.0))
    ax.set_xlim(0, 100); ax.set_ylim(0, H); ax.axis("off")
    X0, X1 = 0.6, 99.4
    MID = 50.0

    def band(y1, h, title, fc=PANEL, lw=1.0):
        rbox(ax, X0, y1 - h, X1, y1, fc=fc, ec=LINE, lw=lw, r=0.8, z=1)
        ax.text(X0 + 2.0, y1 - 1.0, title, ha="left", va="top", fontsize=FS_BAND,
                fontweight="bold", color=INK, zorder=5)
        return y1 - h

    # ── inputs ────────────────────────────────────────────────────────────────
    y = H - 0.6
    yb = band(y, 18.0, "Inputs")
    bw = (X1 - X0 - 4.0 - 2 * 2.2) / 3.0
    for j, (name, sub) in enumerate(INPUTS):
        bx = X0 + 2.0 + j * (bw + 2.2)
        box = (bx, yb + 1.8, bx + bw, yb + 12.6)
        rbox(ax, *box)
        fitted(ax, bx + bw / 2, yb + 10.2, name, box, w="bold")
        fitted(ax, bx + bw / 2, yb + 5.0, sub, box, fs=FS_SUB, c=SOFT)
    y = yb

    # ── demand reconstruction ─────────────────────────────────────────────────
    arrow(ax, MID, y, MID, y - 2.6)
    y -= 2.6
    yb = band(y, 11.0, "Heat demand")
    fitted(ax, MID, yb + 4.0,
           "Residential useful heat reconstructed bottom-up for 1,369 NUTS3 regions\n"
           "across 29 markets, validated against national statistics",
           (X0, yb + 0.6, X1, yb + 7.8), fs=FS_SUB)
    y = yb

    # ── scenarios ─────────────────────────────────────────────────────────────
    arrow(ax, MID, y, MID, y - 2.6)
    y -= 2.6
    yb = band(y, 11.0, "Scenarios")
    fitted(ax, MID, yb + 4.0,
           "200 Monte Carlo draws over 2025 to 2050, under Current Policies,\n"
           "Stated Policies, Net Zero and H2 Push",
           (X0, yb + 0.6, X1, yb + 7.8), fs=FS_SUB)
    y = yb

    # ── the three tests ───────────────────────────────────────────────────────
    arrow(ax, MID, y, MID, y - 2.6)
    y -= 2.6
    TH = 26.0
    yb = band(y, TH, "Three tests, applied in order")
    tw = (X1 - X0 - 4.0 - 2 * 2.2) / 3.0
    for j, (name, ask) in enumerate(TESTS):
        bx = X0 + 2.0 + j * (tw + 2.2)
        box = (bx, yb + 1.8, bx + tw, yb + 21.0)
        rbox(ax, *box, fc=TEST)
        fitted(ax, bx + tw / 2, yb + 18.4, name, box, fs=FS_TEST, w="bold")
        fitted(ax, bx + tw / 2, yb + 8.8, ask, box, fs=FS_ASK, c=INK)
        if j:
            arrow(ax, bx - 2.2, yb + 11.4, bx, yb + 11.4)
    y = yb

    # ── outputs ───────────────────────────────────────────────────────────────
    arrow(ax, MID, y, MID, y - 2.6)
    y -= 2.6
    yb = band(y, 11.0, "Outputs")
    fitted(ax, MID, yb + 4.0,
           "Cost gaps and technology shares by country, emissions pathways, and the\n"
           "capacity payment a hydrogen peaker would need to be built",
           (X0, yb + 0.6, X1, yb + 7.8), fs=FS_SUB)

    fig.subplots_adjust(left=0.004, right=0.996, top=0.996, bottom=0.004)
    assert_fits(fig, ax, "P00_model_flow")
    for ext in ("png", "pdf"):
        # savefig.bbox="tight" crops this one, so the house 400 dpi lands at about
        # 282 dpi once Word scales it to the column. 460 clears Elsevier's 300.
        fig.savefig(OUT / f"P00_model_flow.{ext}", dpi=460 if ext == "png" else None)
    plt.close(fig)
    print("wrote P00_model_flow.{png,pdf}")


if __name__ == "__main__":
    model_flow()
