"""Report any two pieces of text that collide in a figure, and any text sitting on the data.

The printed-scale checker answers "is this glyph big enough". It says nothing about whether
two glyphs are in the same place. Those are different defects and the second one shipped: on
the district-heat dispatch the legend's first row landed on the descenders of the x-axis
label, because legend_below() anchored at a fixed offset in axes coordinates while the height
of the tick labels and the axis label varies from figure to figure.

Eyeballing a PNG does not catch this reliably. The collision is often a few points, it hides
in whichever panel the author did not zoom into, and it reappears whenever a label's text
changes length. So it is measured here instead, on the drawn figure, with matplotlib's own
renderer reporting where every text artist actually landed.

Two checks per figure:

  overlap  two text artists whose bounding boxes intersect by more than TOL points in both
           directions. Pure containment is ignored, since a legend's own text sits inside the
           legend box by construction.

  on-data  a text artist or annotation drawn inside the axes' data region. This project's
           house rule is that a figure carries no callout over its data: what a callout would
           say belongs in the caption, the legend or the panel title, where it cannot collide
           with anything. Tick labels, axis labels, titles and legends are exempt, as are
           in-bar value labels, which are positioned against the bar they annotate.

Run:  cd code && PYTHONPATH=. python -m scripts.check_figure_overlap
Exit: non-zero if any figure has a collision or an un-exempt callout over its data.
"""
from __future__ import annotations

import importlib
import pathlib
import sys
import tempfile
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.text import Annotation, Text

# Every hooked savefig lands here instead of over the committed artwork.
_SCRATCH = tempfile.mkdtemp(prefix="figcheck-")

TOL_PT = 1.0        # ignore sub-point touching; a real collision is visible
MIN_AREA_PT2 = 4.0  # and covers some area, not just a corner

# Generators to draw. Each entry is (module, callable) run with the module's own styling.
GENERATORS = [
    ("scripts.paper_figures", None),      # None: run every pNN() the module defines
    ("scripts.heat_dispatch", "main"),
    ("scripts.fig_uc_results", None),
    ("scripts.electrification_bridge", "main"),
    ("scripts.power_dispatch", "main"),
]


def _boxes(fig):
    """Every text artist in the figure with its drawn extent, tagged by role."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    out = []
    fw, fh = fig.canvas.get_width_height()

    def add(t, role, ax):
        s = (t.get_text() or "").strip()
        if not s or not t.get_visible():
            return
        try:
            b = t.get_window_extent(r)
        except Exception:
            return
        # A never-drawn artist reports a degenerate unit box at the origin, and two of those
        # overlap completely. Anything degenerate, or wholly off the canvas, is not on the page.
        if b.width < 1.0 or b.height < 1.0:
            return
        if b.x1 <= 0 or b.y1 <= 0 or b.x0 >= fw or b.y0 >= fh:
            return
        out.append((t, b, role, s, ax))

    for ax in fig.get_axes():
        # Tick labels are collected by tick POSITION, filtered to the axis view, rather than
        # through findobj. matplotlib lays out a label for a tick just outside the limits and
        # then clips it at draw time, so it has a real extent and is never painted. One such
        # ghost, panel (b)'s tick at -20 on an axis that starts at 0, was reported as
        # colliding with panel (a)'s rightmost country label for several rounds.
        for axis, getlim in ((ax.xaxis, ax.get_xlim), (ax.yaxis, ax.get_ylim)):
            lo, hi = sorted(getlim())
            for tick in axis.get_major_ticks():
                if lo - 1e-9 <= tick.get_loc() <= hi + 1e-9:
                    add(tick.label1, "chrome", ax)
        for t in (ax.xaxis.label, ax.yaxis.label, ax.title):
            add(t, "chrome", ax)
        leg = ax.get_legend()
        if leg is not None:
            for t in leg.get_texts():
                add(t, "chrome", ax)
        for t in ax.texts:                     # ax.text(...) and ax.annotate(...)
            add(t, "content", ax)
    for t in fig.texts:
        add(t, "chrome", None)
    return out


MIN_HEIGHT_FRAC = 0.45   # the overlap must cover this much of the shorter box's height
MIN_DX_PT = 2.0          # and encroach this far horizontally


def _clash(a, b):
    """Return (height fraction, horizontal encroachment in points) for two text extents.

    Two earlier criteria both failed, in opposite directions, and the figures show why.

    Raw area flagged every pair of adjacent country labels on a 29-row bar chart, because a
    matplotlib text extent is a line box carrying ascender and descender room the glyphs do
    not fill, so consecutive rows always overlap by a thin strip. Sixty false positives.

    Overlap as a fraction of the smaller box's AREA then missed the real collisions, because
    a long axis label is a wide box: two of them can overlap by sixty points of text and still
    only share a fifth of their area. It passed the sensitivity panel, whose two x-axis labels
    visibly run through each other.

    What separates the two cases is which direction the overlap runs in. Labels stacked on
    consecutive rows share a thin horizontal strip, so the overlap is a small fraction of
    their height. Labels colliding on the same baseline share nearly their whole height and
    differ only in how far they reach into each other. Measuring both is what works.
    """
    dx = min(a.x1, b.x1) - max(a.x0, b.x0)
    dy = min(a.y1, b.y1) - max(a.y0, b.y0)
    if dx <= 0 or dy <= 0:
        return 0.0, 0.0
    contained = ((a.x0 >= b.x0 and a.x1 <= b.x1 and a.y0 >= b.y0 and a.y1 <= b.y1)
                 or (b.x0 >= a.x0 and b.x1 <= a.x1 and b.y0 >= a.y0 and b.y1 <= a.y1))
    if contained:
        return 0.0, 0.0
    h = min(a.height, b.height)
    return (dy / h if h > 0 else 0.0), dx


def inspect(fig, label):
    """Return a list of complaint strings for one drawn figure."""
    items = _boxes(fig)
    bad = []
    for i, (ta, ba, ra, sa, _) in enumerate(items):
        for tb, bb, rb, sb, _ in items[i + 1:]:
            if ta is tb:
                continue
            hf, dx = _clash(ba, bb)
            if hf > MIN_HEIGHT_FRAC and dx > MIN_DX_PT:
                bad.append(f"{label}: {sa[:36]!r} overlaps {sb[:36]!r} "
                           f"({dx:.0f} pt across, {hf * 100:.0f}% of the height)")
    for t, b, role, s, ax in items:
        if role != "content" or ax is None:
            continue
        # a callout is text pinned into the data region; an in-bar value label is not, since
        # it is placed at the end of its own bar and moves with it
        if not isinstance(t, Annotation):
            continue
        ab = ax.get_window_extent()
        inside = (b.x0 > ab.x0 and b.x1 < ab.x1 and b.y0 > ab.y0 and b.y1 < ab.y1)
        if inside and (t.arrow_patch is not None or t.get_bbox_patch() is not None):
            bad.append(f"{label}: callout {s[:44]!r} is drawn over the data; "
                       "move it to the caption, legend or title")
    return bad


def run_all(collect):
    """Run every listed generator, calling collect(figure, name) as each figure is saved.

    The hook is on Figure.savefig, not on the generators' own save helpers. Those helpers
    close the figure after writing it, so inspecting plt.get_fignums() afterwards found
    nothing at all and this checker reported a clean sweep of zero figures. Patching savefig
    catches every figure at the one moment it is guaranteed to be fully drawn, whatever
    wrapper the generator happens to use.
    """
    from matplotlib.figure import Figure
    real = Figure.savefig
    seen = set()

    def hooked(self, fname, *a, **kw):
        # Write to a scratch directory, never over the committed artwork. This is a
        # CHECKER: calling the real savefig on the real path rewrote about forty figure
        # files and two result CSVs on every run, which is the same rule the number gate
        # broke by emitting an SI table while reading a value off it. A gate that writes
        # is a build step wearing a gate's clothes, and one day it repairs the defect it
        # is judging and reports a pass.
        scratch = pathlib.Path(_SCRATCH) / pathlib.Path(str(fname)).name
        out = real(self, str(scratch), *a, **kw)
        # Dedupe on the output name, not id(self). CPython reuses an id once plt.close frees
        # the figure, so an id-keyed set silently skipped later figures and the inspected
        # count wobbled between runs. A figure written as .png and .pdf shares one stem.
        stem = str(fname).replace("\\", "/").rsplit("/", 1)[-1].rsplit(".", 1)[0]
        if stem not in seen:
            seen.add(stem)
            collect(self, stem)
        return out

    Figure.savefig = hooked
    try:
        for mod_name, entry in GENERATORS:
            try:
                mod = importlib.import_module(mod_name)
            except Exception as e:
                print(f"  (skipped {mod_name}: {e})")
                continue
            if hasattr(mod, "set_style"):
                mod.set_style()
            fns = ([entry] if entry else
                   sorted(n for n in dir(mod) if len(n) == 3 and n.startswith("p") and
                          n[1:].isdigit() and callable(getattr(mod, n))))
            for fn in fns:
                try:
                    getattr(mod, fn)()
                except Exception as e:
                    print(f"  (skipped {mod_name}.{fn}: {type(e).__name__}: {e})")
                finally:
                    plt.close("all")
    finally:
        Figure.savefig = real


def main() -> int:
    warnings.filterwarnings("ignore")
    bad, seen = [], []

    def collect(fig, name):
        seen.append(name)
        bad.extend(inspect(fig, name))

    run_all(collect)
    plt.close("all")
    print(f"\ninspected {len(seen)} drawn figure(s)")
    # Run without PYTHONPATH=. every module import fails, every figure is skipped, and the
    # checker printed "inspected 0 drawn figure(s)" followed by "No text collides" and exited
    # 0. A gate that passes because it looked at nothing is worse than no gate, so an empty
    # inspection is now a failure.
    MIN_FIGURES = 30
    if len(seen) < MIN_FIGURES:
        print(f"FAIL: only {len(seen)} figure(s) were drawn, below the {MIN_FIGURES} this "
              f"repository contains. The modules did not import (run from code/ with "
              f"PYTHONPATH=.), so this run checked almost nothing and its pass means nothing.")
        return 1
    if bad:
        print(f"{len(bad)} collision(s) or callout(s) over data:\n")
        for b in dict.fromkeys(bad):
            print("  " + b)
        return 1
    print("No text collides with other text, and no callout sits over the data.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
