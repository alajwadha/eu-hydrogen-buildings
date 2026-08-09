"""Shared figure style for the whole repo: academic, never-overlapping defaults.

Three house rules, applied everywhere:
  1. Text never overlaps -> figure.autolayout (auto tight_layout on every draw) +
     savefig.bbox='tight' (nothing placed outside the axes, e.g. legends or long
     tick labels, is ever clipped) + restrained default font sizes.
  2. Titles are academic and short -> we don't enforce the string here, but the
     small titlesize/titlepad keep a short noun-phrase title from crowding the plot.
  3. Every PNG gets a VECTOR PDF twin -> set_style() wraps Figure.savefig so that
     saving 'name.png' also writes 'name.pdf' alongside it. The paper includes the
     PDF (crisp at any zoom -- raster PNGs at print width look soft); the PNG remains
     for READMEs, dashboards and quick browsing. Scripts need no changes.

Usage at the top of any figure script (after importing matplotlib):
    from scripts._figstyle import set_style
    set_style()

Also provides two helpers used by the figure scripts:
    legend_below(ax, ncol)   -> legend placed under the axes (never over the data)
    short_scen(name)         -> 'H2_PUSH' -> 'H2 Push' for readable titles
"""
from __future__ import annotations
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_orig_savefig = matplotlib.figure.Figure.savefig

# A PDF carries a CreationDate, so rebuilding an unchanged figure produced a new file
# every time and forty-odd figures showed as modified in git with identical content.
# matplotlib honours SOURCE_DATE_EPOCH for that field, so pinning it makes the output
# byte-reproducible and leaves the working tree clean unless a figure genuinely changed.
os.environ.setdefault("SOURCE_DATE_EPOCH", "1704067200")   # 2024-01-01T00:00:00Z


def _dual_savefig(self, fname, *args, **kwargs):
    """Figure.savefig wrapper: a .png save also emits a vector .pdf twin."""
    out = _orig_savefig(self, fname, *args, **kwargs)
    p = os.fspath(fname) if not hasattr(fname, "write") else None
    if p and p.lower().endswith(".png"):
        kw = {k: v for k, v in kwargs.items() if k != "dpi"}
        _orig_savefig(self, p[:-4] + ".pdf", *args, **kw)
    return out

_SCEN_DISPLAY = {
    "CURRENT_POLICIES": "Current Policies",
    "STATED_POLICIES":  "Stated Policies",
    "NET_ZERO":         "Net Zero",
    "H2_PUSH":          "H2 Push",
    "COST_OPT":         "Cost-Optimised",
}


# Refined, restrained categorical palette (muted journal tones, not matplotlib tab10).
PALETTE = ["#2c6fb3", "#e07b39", "#4f9d69", "#c0504d",
           "#7d6fb0", "#3fa7b5", "#d4ac3a", "#7f7f7f"]


def set_style() -> None:
    plt.rcParams.update({
        "figure.autolayout":   True,    # auto tight_layout -> no title/label overlap
        "savefig.bbox":        "tight", # never clip outside-axes artists (legends, labels)
        "savefig.pad_inches":  0.08,
        # 400, not 200. The Word twin embeds these PNGs and scales them to a fixed
        # physical width, so the raster DPI of the file IS the DPI Elsevier receives:
        # at 200 the submitted .docx carried every figure at 199 to 213 dpi against a
        # 300 dpi floor for combination artwork. The LaTeX path is unaffected, since it
        # includes the vector PDFs beside these.
        "savefig.dpi":         400,
        "savefig.facecolor":   "white", # never transparent (transparent renders badly on dark UIs)
        "figure.dpi":          120,
        "figure.facecolor":    "white",
        "axes.facecolor":      "white",
        # clean sans stack; falls back gracefully if a face is absent
        "font.family":         "sans-serif",
        "font.sans-serif":     ["Segoe UI", "Calibri", "Helvetica Neue", "Arial", "DejaVu Sans"],
        "font.size":           10,
        "axes.titlesize":      12.5,
        "axes.titleweight":    "bold",
        "axes.titlelocation":  "left",  # modern, uncluttered (title flush with the y-axis)
        "axes.titlepad":       10,
        "axes.labelsize":      10,
        "axes.labelcolor":     "#1a1a1a",
        "axes.edgecolor":      "#bdbdbd", # soft spines, not hard black
        "axes.linewidth":      0.8,
        "text.color":          "#1a1a1a",
        "xtick.color":         "#4d4d4d",
        "ytick.color":         "#4d4d4d",
        "xtick.labelsize":     9,
        "ytick.labelsize":     9,
        "legend.fontsize":     9,
        "legend.frameon":      False,
        "axes.grid":           True,    # subtle reference grid, always behind the data
        "axes.grid.axis":      "y",
        "grid.color":          "#ececec",
        "grid.linewidth":      0.8,
        "axes.axisbelow":      True,
        "figure.titlesize":    13.5,
        "figure.titleweight":  "bold",
        "axes.spines.top":     False,
        "axes.spines.right":   False,
        "axes.prop_cycle":     plt.cycler(color=PALETTE),
    })


def short_scen(name: str) -> str:
    """Readable scenario label for titles (e.g. 'H2_PUSH' -> 'H2 Push')."""
    return _SCEN_DISPLAY.get(name, name.replace("_", " ").title())


def legend_below(ax, ncol: int = 4, pad: float = 0.055, fontsize: float = 8,
                 y: float | None = None):
    """Place the legend below everything the x axis draws, so nothing collides.

    This used to anchor at a fixed y=-0.12 in axes coordinates. That is inside the space the
    tick labels and the axis label occupy, and how far inside depends on how tall they are,
    so on the district-heat dispatch the legend's first row landed on the descenders of
    "Hour of cold-snap day (from 06:00)". A fixed offset cannot be right for every figure.

    The bottom of the x axis is measured instead: the figure is drawn, the tick labels and
    the axis label are asked for their extents, and the legend is anchored `pad` below the
    lowest of them. Pass an explicit `y` only to override the measurement.
    """
    fig = ax.figure
    if y is None:
        fig.canvas.draw()
        r = fig.canvas.get_renderer()
        boxes = [t.get_window_extent(r) for t in ax.get_xticklabels() if t.get_text()]
        if ax.xaxis.label.get_text():
            boxes.append(ax.xaxis.label.get_window_extent(r))
        inv = ax.transAxes.inverted()
        y = (min(inv.transform((0, b.y0))[1] for b in boxes) - pad) if boxes else -0.12
    return ax.legend(loc="upper center", bbox_to_anchor=(0.5, y),
                     ncol=ncol, frameon=False, fontsize=fontsize)


# ── printed-legibility guard ────────────────────────────────────────────────--
# \includegraphics[width=f\textwidth] scales a figure by its WIDTH alone, so what
# decides whether a label is readable on the page is
#     printed_pt = native_pt * (f * column_pt) / (figure_width_in * 72).
# A figure drawn on a wide canvas and placed in a narrow column therefore prints
# its labels far smaller than the size set in the script, and it looks perfectly
# fine in the PNG the author inspects. That is how a set of long-paper figures
# shipped with 3.5 to 5.6 pt text. assert_printable() makes the arithmetic part of
# the build so the failure is loud instead of invisible.
COLUMN_PT = {"ae_body": 345.0, "ae_si": 452.97, "long": 455.24}
MIN_PRINTED_PT = 6.0


def print_scale(fig_width_in: float, column: str = "long", width_frac: float = 1.0) -> float:
    """Factor by which a figure's native point sizes shrink on the printed page."""
    return width_frac * COLUMN_PT[column] / (fig_width_in * 72.0)


def assert_printable(fig_width_in: float, fonts: dict, column: str = "long",
                     width_frac: float = 1.0, label: str = "figure",
                     floor: float = MIN_PRINTED_PT) -> float:
    """Fail the build if any named font would print below `floor` points.

    `fonts` maps a human name to the native size in points, so the error says which
    label is illegible rather than only that something is.
    """
    s = print_scale(fig_width_in, column, width_frac)
    bad = [f"    {k}: {v} pt native -> {v * s:.2f} pt printed"
           for k, v in fonts.items() if v * s < floor]
    if bad:
        raise SystemExit(
            f"{label}: font(s) below the {floor} pt print floor at scale {s:.3f} "
            f"({fig_width_in} in canvas into a {COLUMN_PT[column]:.0f} pt column at "
            f"{width_frac:g}x):\n" + "\n".join(bad))
    print(f"  {label}: print scale {s:.3f}, smallest printed font "
          f"{min(fonts.values()) * s:.2f} pt (floor {floor})")
    return s


# ── the blind spot in the guard above ───────────────────────────────────────--
# assert_printable() checks the font sizes the author declares. matplotlib does not
# render a mathtext sub- or superscript at the declared size: it shrinks it, measured
# here at 0.694x. So "H$_2$ Push" set at 9.8 pt prints its 2 at 6.8 pt native, and at a
# 0.639 column scale that is 4.35 pt, under the floor, in a figure the declared-size
# check passes. Three figures instrumented in the last legibility pass shipped exactly
# this way.
#
# assert_no_shrunk_mathtext() closes it by measuring the drawn figure rather than
# trusting the declaration. The cheaper fix, and the one used in the generators here,
# is to write H₂ and CO₂ and /MWh as Unicode, which renders at full size; the guard
# then catches any that get written back as mathtext.
MATHTEXT_SHRINK = 0.694


def assert_no_shrunk_mathtext(fig, scale: float, label: str = "figure",
                              floor: float = MIN_PRINTED_PT) -> None:
    """Fail the build if a drawn label's mathtext sub/superscript prints below `floor`.

    Call after the figure is fully populated. `scale` is the value assert_printable()
    returned, i.e. the factor the column applies to this figure's native point sizes.
    """
    import re as _re
    fig.canvas.draw()
    bad, seen = [], set()

    def check(t):
        s = t.get_text()
        if not s or "$" not in s or not _re.search(r"[_^]", s):
            return
        printed = t.get_fontsize() * MATHTEXT_SHRINK * scale
        key = (s, round(printed, 2))
        if printed < floor and key not in seen:
            seen.add(key)
            bad.append(f"    {s!r}: {t.get_fontsize()} pt base -> sub/superscript "
                       f"prints at {printed:.2f} pt")

    for ax in fig.get_axes():
        items = (list(ax.texts) + list(ax.get_xticklabels()) + list(ax.get_yticklabels())
                 + [ax.xaxis.label, ax.yaxis.label, ax.title])
        leg = ax.get_legend()
        if leg is not None:
            items += list(leg.get_texts())
        for t in items:
            check(t)
    for t in fig.texts:
        check(t)

    if bad:
        raise SystemExit(
            f"{label}: mathtext sub/superscript below the {floor} pt print floor. "
            f"matplotlib renders these at {MATHTEXT_SHRINK:g}x the base size, so the "
            f"declared-size check does not see them. Write H₂ / CO₂ / "
            f"/MWh as Unicode instead, or raise the base size:\n" + "\n".join(bad))
    print(f"  {label}: no mathtext sub/superscript under {floor} pt")


# ── one scenario palette, chosen for lightness separation ───────────────────--
# Three scripts declared their own scenario colours and they disagreed: H2 Push was
# orange in the emissions fan and red everywhere else, and the red sat against Net
# Zero's green, which is the classic deuteranopia failure pair (simulated separation
# 38.8 of 441). The set below is ordered by relative luminance so it decodes by
# lightness alone, whatever the viewer's colour vision:
# Import it rather than redeclaring, so the four scenarios look the same everywhere.
# The measured relative luminances are 0.384, 0.303, 0.146 and 0.113, not the 0.42/0.30/
# 0.16/0.06 an earlier version of this note claimed. That matters: the adjacent pairs sit
# at 1.23:1 and 1.20:1, so the set does NOT decode by lightness alone and this palette
# should not be relied on as the only channel. Where two scenarios must be told apart in
# one figure, carry a second channel as well (marker, hatch, or a direct label).
SCEN_COLOR = {
    "CURRENT_POLICIES": "#c9a227",   # ochre, lightest
    "STATED_POLICIES":  "#e07b39",   # orange
    "H2_PUSH":          "#7d5ba6",   # purple, hydrogen's own colour in the tech palette
    "NET_ZERO":         "#1f5fa8",   # deep blue, darkest
}

# Hydrogen is this paper's subject and its colour sits close to the heat-pump blue under
# deuteranopia (simulated separation 27.1 of 441, the closest pair in the technology
# palette). Anywhere hydrogen is stacked or bar-charted against other technologies, give
# it this hatch as well as its colour so the segment is identifiable without colour.
H2_HATCH = "///"

# The hatch ink. It was white, which is fine on its own and was not fine in the 2050 mix
# figure, where the segment labels are also white: the stripes crossed the digits, and the
# workaround was a solid patch of the segment's own fill behind each number. That patch
# chopped the stripes into stubs around every hydrogen label and read as a rendering
# fault. Drawn in a dark shade of hydrogen's own purple the stripes cannot collide with a
# white label and no patch is needed. Measured against the #7d5ba6 fill it is 2.11:1,
# visible as texture without muddying a thin band, and a white digit crossing a stripe is
# 11.3:1 rather than invisible.
#
# Applied through Patch.set_hatchcolor rather than through edgecolor. Several of these
# figures use a white edgecolor as the separator between stacked segments or as the bar
# outline, so setting the ink that way would have changed those too. set_hatchcolor is
# matplotlib 3.11, which is why requirements.txt asks for it.
H2_HATCH_INK = "#45325b"
H2_HATCH_LW = 1.6


def ink_h2_hatch(patches) -> None:
    """Draw hydrogen's hatch in H2_HATCH_INK at H2_HATCH_LW, on one patch or many.

    Through set_hatchcolor rather than through edgecolor, deliberately. Four of the seven
    places hydrogen is hatched use a white edgecolor for something else: the separator
    between stacked segments in the dispatch and merit-order figures, and the bar outline
    in the Switzerland figure. Setting the ink through edgecolor would have changed those
    too. At 1.0 the dark stripes read thinner than the white ones did, because white on
    this purple is 5.36:1 and the dark ink is 2.11:1, so the weight goes up to match.
    """
    for p in (patches if hasattr(patches, "__iter__") else [patches]):
        p.set_hatchcolor(H2_HATCH_INK)
        p.set_hatch_linewidth(H2_HATCH_LW)

# ── one technology palette, for the same reason as the scenario palette above ──
# This dict was declared separately in six scripts and they had drifted: the graphical
# abstract, which is page one of the submission, painted hydrogen #e07b39, the colour
# that means district heat in the 2050 mix figure and Stated Policies in the scenario
# palette. Import it rather than redeclaring, so a technology keeps one colour from the
# first figure a reader sees to the last.
TECH_COLOR = {"hp_air": "#1f5fa8", "hp_ground": "#5b9bd5", "district_heat": "#e07b39",
              "biomass_boiler": "#4daf6a", "h2_boiler": "#7d5ba6", "gas_boiler": "#9e9e9e",
              "oil_boiler": "#616161", "resistance_heater": "#e8b54d"}
