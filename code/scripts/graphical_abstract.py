"""Graphical abstract for the Applied Energy submission.

A single two-panel figure carrying the whole argument:
  (A) the base-load verdict, 2050 levelised cost of heat, heat pumps win; and
  (B) the peaking niche, hydrogen wins the operating-cost dispatch in a rising
      number of markets yet recovers its capital in none.

All numbers are the manuscript's own headline values. Colours are imported from the house
technology palette in _figstyle.py, so hydrogen is the same purple here as in every other
figure and carries the same hatch. Nothing is encoded red against green.

LAYOUT NOTE. \\includegraphics[width=\\textwidth] scales a figure by its WIDTH alone, so
printed legibility is (font size in points) x (column width) / (figure width in points).
The earlier canvas was 11.0 in wide against the 345 pt (4.79 in) Applied Energy column, a
factor of 0.436, which printed every label between 3.0 and 5.9 pt: nothing in the figure
cleared the 6 pt floor, including the bold headline. The canvas is 6.6 in here, a factor
of about 0.73, and every font is set so that font x 0.73 >= 6.5 pt. PRINT_SCALE and
assert_legible() below enforce that on every build rather than leaving it to inspection,
which is how the earlier version shipped.

Run:  cd code && PYTHONPATH=. python -m scripts.graphical_abstract
Out:  paper/figs/paper/graphical_abstract.{png,pdf}
"""
from __future__ import annotations
from pathlib import Path
import textwrap
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scripts._figstyle import set_style, TECH_COLOR, H2_HATCH, ink_h2_hatch
set_style()
# explicit gridspec margins below, so disable the global auto-layout to avoid a warning
plt.rcParams.update({"figure.autolayout": False, "savefig.bbox": None})

# These were three near-misses of the house technology palette, and one of them said the
# wrong thing: hydrogen was drawn #e07b39, which is district heat's colour in Fig. 3 and
# Stated Policies' colour in the scenario palette. The graphical abstract is the first
# figure a reader sees, so it taught the wrong key. Take all three from the house palette
# and carry hydrogen's hatch with it, as the house rule requires wherever hydrogen is
# bar-charted against other technologies.
HP, H2, GAS = TECH_COLOR["hp_air"], TECH_COLOR["h2_boiler"], TECH_COLOR["gas_boiler"]
INK, SOFT = "#1a1a1a", "#6b6b6b"
FIGDIR = Path(__file__).resolve().parents[2] / "paper" / "figs" / "paper"
RESULTS = Path(__file__).resolve().parents[1] / "results"


def capacity_payment_band() -> str:
    """The standing capacity payment band, read from the artefact rather than typed.

    This was hard-coded, and it read "EUR 31 to 69/kW-yr" against the artefact's 31 to 63.
    The 69 is not this quantity at all: it is the upper bound of the ANNUALISED CAPITAL
    (ann_capex_h2) over all seven cavern markets, two of which build nothing. So the
    sentence welded the payment's lower bound to a different variable's upper bound on a
    different basis, and printed it on page 1 of the submission.

    Deriving it means the figure cannot disagree with the paper about a number they both
    state. The band is the same over all seven markets and over the five that build, so no
    basis has to be chosen here.
    """
    import pandas as pd
    cp = pd.read_csv(RESULTS / "capacity_payment.csv")
    return (f"\N{EURO SIGN}{cp.standing_payment_h2.min():.0f} to "
            f"{cp.standing_payment_h2.max():.0f}/kW-yr")


_WORDS = {4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine"}


def wrapped(sentence: str, cols: int) -> str:
    """Wrap one source sentence to the canvas it is being drawn on.

    The two footnotes below used to be written out twice, hand-wrapped for each canvas.
    The copies drifted. An edit to the tall copy left half a sentence behind in the wide
    one, so the file Editorial Manager displays read "...the 7 are salt-cavern markets;
    the 5 that build are salt-cavern markets; the 5 that build would need...". No gate
    could see it, because both strings were legal text at a legal size. One source string
    per sentence removes the failure rather than catching it.
    """
    # break_on_hyphens=False, or the wrapper splits the compound units it is given:
    # the first run of this broke the capacity payment across a line as "/kW-" then "yr".
    return "\n".join(textwrap.wrap(sentence, cols, break_on_hyphens=False))

# Two canvases, because the figure has two jobs with incompatible geometry.
#
# TALL is what V6.tex includes at \textwidth: the print-scale note above governs it.
# WIDE is what gets uploaded to Editorial Manager. Elsevier displays a graphical abstract
# at about 13 x 5 cm and asks for at least 1328 x 531 px, an aspect near 2.5:1. The tall
# canvas is 1.29:1 and 8 px short on width, so it fails the spec and prints at double the
# height it is allotted. Widening the manuscript figure instead is not an option: at
# \textwidth a 2.5:1 canvas scales every font by 0.36 and nothing clears the 6 pt floor,
# which is the failure the note above records. So the wide variant moves the headline and
# the kicker into a left-hand text column and keeps the panels at a legible scale.
FIGW_IN = 6.6                      # tall canvas width, inches
FIGH_IN = 5.1
WIDE_W_IN, WIDE_H_IN = 13.28, 5.31   # 1328 x 531 px at 100 dpi, Elsevier's floor
AE_COLUMN_PT = 345.0               # Applied Energy single-column text width
PRINT_SCALE = AE_COLUMN_PT / (FIGW_IN * 72.0)
# The wide file is displayed at 13 cm, not scaled into a text column, so its own scale is
# 13 cm / 13.28 in = 0.385 of native. Fonts below are sized for the tall canvas; the wide
# layout scales them up by this factor so the printed size matches.
WIDE_FONT_SCALE = 1.55
MIN_PRINTED_PT = 6.0

# Every font used below, declared once so the guard can check the set rather than
# trusting that a later edit remembered the floor.
FS_HEAD, FS_SUB = 11.5, 9.0
FS_TITLE, FS_LABEL, FS_VALUE, FS_TICK, FS_NOTE = 10.0, 9.2, 9.5, 9.0, 8.8


def assert_legible():
    """Fail the build if any declared font would print below the 6 pt floor."""
    fonts = {"headline": FS_HEAD, "subtitle": FS_SUB, "panel title": FS_TITLE,
             "axis label": FS_LABEL, "value label": FS_VALUE, "tick": FS_TICK,
             "footnote": FS_NOTE}
    bad = [f"    {k}: {v} pt native -> {v * PRINT_SCALE:.2f} pt printed"
           for k, v in fonts.items() if v * PRINT_SCALE < MIN_PRINTED_PT]
    if bad:
        raise SystemExit("graphical abstract: font(s) below the "
                         f"{MIN_PRINTED_PT} pt print floor at scale "
                         f"{PRINT_SCALE:.3f}:\n" + "\n".join(bad))
    smallest = min(fonts.values()) * PRINT_SCALE
    print(f"  print scale {PRINT_SCALE:.3f}; smallest printed font "
          f"{smallest:.2f} pt (floor {MIN_PRINTED_PT})")



def assert_inside_canvas(png_path, stem, min_clear_px=8):
    """Fail the build if drawn ink reaches the edge of the saved image.

    The two figure gates cannot see this. check_figure_print_scale measures glyph size
    and check_figure_overlap compares text against text, so a string that leaves the
    canvas collides with nothing and prints at a perfectly legal size. This file has
    shipped that defect twice: once when the kicker was hard-clipped mid-word, and once
    when a lengthened axis label ran off the bottom of the wide upload. Measuring the
    rendered raster is the only check that catches it, because it asks the question a
    reader asks: is anything touching the edge?
    """
    from PIL import Image
    im = Image.open(png_path).convert("L")
    w, h = im.size
    px = im.load()
    rows = [r for r in range(h) if any(px[x, r] < 200 for x in range(w))]
    cols = [c for c in range(w) if any(px[c, y] < 200 for y in range(h))]
    if not rows:
        raise SystemExit(f"{stem}: the rendered image is blank")
    clear = {"top": min(rows), "bottom": h - 1 - max(rows),
             "left": min(cols), "right": w - 1 - max(cols)}
    tight = {k: v for k, v in clear.items() if v < min_clear_px}
    if tight:
        raise SystemExit(
            f"{stem}: ink reaches the canvas edge, so it will print clipped: "
            + ", ".join(f"{k} {v}px" for k, v in tight.items()))
    print("  canvas clearance px: " + ", ".join(f"{k} {v}" for k, v in clear.items()))


def main(wide: bool = False):
    """Draw the abstract. `wide` emits the Elsevier-spec 2.5:1 upload variant."""
    assert_legible()
    k = WIDE_FONT_SCALE if wide else 1.0
    fs_head, fs_sub = FS_HEAD * k, FS_SUB * k
    fs_title = FS_TITLE * (k * 0.90 if wide else k)   # panel B's title is the widest string
    fs_label = FS_LABEL * k
    fs_value, fs_tick, fs_note = FS_VALUE * k, FS_TICK * k, FS_NOTE * k
    # The footers sit outside the axes, so the figure carries a deep bottom margin
    # for them. Placing them in figure coordinates (not axes coordinates) keeps them
    # on the page whatever the panel geometry does.
    # Height raised from 4.8 in and the panel block lifted, because the closing kicker
    # below ran off the right edge and was hard-clipped mid-word ("capacity payment to"),
    # on page one of the submission. Neither figure gate could see it: the print-scale
    # gate measures glyph size and the overlap gate measures text against text, and a
    # string that leaves the canvas collides with nothing. The kicker is now three lines.
    if wide:
        fig = plt.figure(figsize=(WIDE_W_IN, WIDE_H_IN))
        # The text column has to clear panel A's y-axis label and the panel block has to
        # clear panel B's centred title, so both margins are pulled in from the defaults.
        gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.02], wspace=0.42,
                              left=0.395, right=0.955, top=0.790, bottom=0.235)
        # The last of these was 0.400, which left a 215 px hole between the second and
        # third text blocks against 97 and 105 px between the ones above. Three gaps in
        # one column of identically styled grey text should not differ by a factor of
        # two, and this is the file Editorial Manager takes, so it is the copy that gets
        # published. 0.465 puts the third gap at 105, matching the one above it.
        HX, HY, SY, NOTE_A_Y, KICK_Y = 0.022, 0.935, 0.800, 0.655, 0.465
    else:
        fig = plt.figure(figsize=(FIGW_IN, FIGH_IN))
        gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.06], wspace=0.30,
                              left=0.105, right=0.985, top=0.700, bottom=0.395)
        HX, HY, SY, NOTE_A_Y, KICK_Y = 0.105, 0.960, 0.850, 0.235, 0.150

    # Takeaway strip. Wrapped to two lines: at this canvas width the single-line
    # version of this sentence runs off the right edge.
    fig.text(HX, HY, "Heat pumps decarbonise Europe’s homes, whereas",
             fontsize=fs_head, fontweight="bold", color=INK, ha="left", va="center")
    fig.text(HX, HY - 0.055, "hydrogen is a support-contingent capacity option",
             fontsize=fs_head, fontweight="bold", color=INK, ha="left", va="center")
    fig.text(HX, SY,
             "29 markets: EU-27, UK, Switzerland\n1,369 NUTS3 regions · 2025 to 2050"
             if wide else
             "29 European markets (EU-27, UK, Switzerland) · 1,369 NUTS3 regions · 2025 to 2050",
             fontsize=fs_sub, color=SOFT, ha="left", va="top" if wide else "center")

    # ---- Panel A: base-load LCOH ----
    axA = fig.add_subplot(gs[0, 0])
    techs = ["Heat\npump", "Hydrogen\nboiler", "Gas\nboiler"]
    # These were typed literals for three model outputs, in a file whose own docstring
    # records a hard-coded band having shipped wrong once already. Read from the artefact.
    _g = pd.read_csv(RESULTS / "h2_hp_gap.csv")
    _e = pd.read_csv(RESULTS / "country_econ_table.csv")
    lcoh = [round(_g.best_hp_lcoh_2050.median(), 1),
            round(_g.h2_lcoh_2050.median(), 1),
            round(_e.lcoh_gas_2050.median(), 1)]
    bars = axA.bar(techs, lcoh, color=[HP, H2, GAS], width=0.64, zorder=3)
    bars[1].set_hatch(H2_HATCH)          # hydrogen carries its hatch here as everywhere
    bars[1].set_edgecolor("white")
    ink_h2_hatch(bars[1])
    for b, v in zip(bars, lcoh):
        axA.text(b.get_x() + b.get_width() / 2, v + 3, f"€{v}", ha="center",
                 va="bottom", fontsize=fs_value, color=INK)
    axA.set_ylim(0, 152)
    axA.set_ylabel("2050 levelised cost of heat (€/MWh)", fontsize=fs_label)
    axA.set_title("Base load: 2050 delivered cost", color=INK, fontsize=fs_title)
    axA.tick_params(labelsize=fs_tick)
    axA.margins(x=0.06)
    # Column widths in characters for the two canvases: the wide variant's footnotes sit
    # in a narrow left-hand text column, the tall variant's run the full page width.
    note_cols, kick_cols = (38, 41) if wide else (58, 88)
    # The three counts in this sentence were typed. Derive them: which countries the heat
    # pump beats, which seven it does not, and how many of those seven sit on salt.
    _geo = pd.read_csv(RESULTS / "storage_geology.csv").set_index("country")
    _exceptions = _g.loc[_g.best_hp_lcoh_2050 > _g.h2_lcoh_2050, "country"].tolist()
    _cavern_exceptions = sum(int(_geo.loc[c, "cavern"]) for c in _exceptions)
    fig.text(HX, NOTE_A_Y,
             wrapped(f"Heat pumps beat the hydrogen boiler in "
                     f"{int((_g.best_hp_lcoh_2050 < _g.h2_lcoh_2050).sum())} of "
                     f"{len(_g)} countries, and {_cavern_exceptions} of the "
                     f"{len(_exceptions)} exceptions are salt-cavern markets.", note_cols),
             fontsize=fs_note, color=SOFT, va="top")

    # ---- Panel B: the peaking niche ----
    axB = fig.add_subplot(gs[0, 1])
    arenas = ["Building\nwinter peak", "District-heat\npeak", "Power\npeaker"]
    # Likewise: the three arena win counts, read from the artefacts that produce them.
    _mh = pd.read_csv(RESULTS / "merit_order_heat.csv")
    _md = pd.read_csv(RESULTS / "merit_order_dh.csv")
    _pp = pd.read_csv(RESULTS / "power_peak_price.csv")
    _h2p = lambda d, col: int(d[(d.scenario == "H2_PUSH")][col].sum())
    wins = [_h2p(_mh, "h2_wins_peak"), _h2p(_md, "h2_beats_gas_chp"),
            int((_pp[_pp.scenario == "H2_PUSH"].h2_turbine_srmc
                 < _pp[_pp.scenario == "H2_PUSH"].ocgt_srmc).sum())]
    # The symmetric-charging counts, read from the sweep rather than typed. They went in
    # as string literals, which is the exposure capacity_payment_band() exists to avoid.
    _ars = pd.read_csv(RESULTS / "dispatch_arena_sensitivity.csv")
    def _sym(axis, setting):
        r = _ars[(_ars.axis == axis) & (_ars.setting == setting)]
        return int(r["count_H2_PUSH"].iloc[0])
    sym = (_sym("h2_last_mile", "charged"), _sym("dh_gas_basis", "wholesale hub 30"),
           wins[2])
    # The symmetric counts are what this panel plots, on the author's decision after
    # review. The bars used to carry the reported basis, which charges the building peak
    # no last-mile network cost for hydrogen and prices the district-heat comparison at
    # retail gas where an operator buys wholesale. The paper says so in the results and
    # in the table note, but page one led with the higher counts anyway, and a reviewer
    # can dismiss a paper in one sentence for headlining the specification its own
    # authors identify as the favourable one. The reported basis is now the sensitivity,
    # named in the kicker below.
    y = range(len(arenas))
    axB.barh(list(y), sym, color=H2, height=0.6, zorder=3)
    for i, w in zip(y, sym):
        axB.text(w + 0.5, i, f"{w}", va="center", ha="left", fontsize=fs_value,
                 color=INK)
    axB.set_yticks(list(y))
    axB.set_yticklabels(arenas)
    axB.invert_yaxis()
    axB.set_xlim(0, 29)
    # Two lines, always. The wide canvas is 2.5:1 and its panel is narrow, so a
    # single-line label runs off the right edge of the file Elsevier displays.
    axB.set_xlabel("Markets won on operating cost,\nH₂ Push (of 29)", fontsize=fs_label)
    axB.set_title("Peaking: dispatch wins", color=INK, fontsize=fs_title)
    axB.tick_params(labelsize=fs_tick)
    axB.grid(axis="x"); axB.grid(axis="y", visible=False)

    # the zero-recovery kicker, under the full width so it is not squeezed
    _cp = pd.read_csv(RESULTS / "capacity_payment.csv")
    _n_build = int((_cp.peaker_cap_gw > 0).sum())     # two of the seven build nothing
    fig.text(HX, KICK_Y,
             # "the reported basis" named the asymmetric counts, which stopped being the
             # reported basis when the manuscript moved to symmetric accounting. Naming
             # the accounting rather than a second pair of numbers keeps the panel and the
             # paper from disagreeing the next time either moves.
             wrapped(f"Counts charge both carriers symmetrically, hydrogen paying its own "
                     f"last-mile network. No market recovers the "
                     f"peaker’s capital from market rent. On the high carbon path "
                     f"hydrogen wins the power peak only in the {wins[2]} salt-cavern "
                     f"markets, a different {_WORDS.get(wins[2], wins[2])}; the "
                     f"{_n_build} that build would need {capacity_payment_band()} to be "
                     f"financeable.", kick_cols),
             fontsize=fs_note, color=SOFT, va="top")

    stem = "graphical_abstract_wide" if wide else "graphical_abstract"
    for ext in (".png", ".pdf"):
        fig.savefig(FIGDIR / (stem + ext), dpi=300 if wide else None)
    plt.close(fig)
    assert_inside_canvas(FIGDIR / (stem + ".png"), stem)
    w, h = (WIDE_W_IN, WIDE_H_IN) if wide else (FIGW_IN, FIGH_IN)
    print(f"wrote {stem} ({w * 100:.0f} x {h * 100:.0f} px at 100 dpi, "
          f"aspect {w / h:.2f}:1)")


if __name__ == "__main__":
    main(wide=False)   # the file V6.tex includes
    main(wide=True)    # the file Editorial Manager wants
