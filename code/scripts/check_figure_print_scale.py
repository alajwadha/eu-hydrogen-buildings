"""Report the printed scale of every figure inclusion across the three documents.

\\includegraphics[width=f\\textwidth] scales a figure by its WIDTH alone, so a label set
at 8 pt in the generator prints at 8 x f x column / native_width points. A figure drawn
on a wide canvas and dropped into a narrow column therefore prints far smaller than the
size the author set, and it looks perfectly fine in the PNG they inspected. That is how a
set of figures shipped with 3.5 to 5.6 pt text.

This is the cheap standing check: it does not know each figure's font sizes, so it cannot
prove legibility on its own. What it does is flag every inclusion whose scale is low
enough that ordinary 8 to 10 pt labels would fall under the 6 pt floor, which is the
condition worth looking at before a submission build. Figures whose generator calls
_figstyle.assert_printable() enforce the floor exactly and are marked as such.

Run:  cd code && PYTHONPATH=. python -m scripts.check_figure_print_scale
Exit: non-zero if any inclusion falls below the review threshold.
"""
from __future__ import annotations

FLOOR_PT = 6.0  # the legibility floor this project holds figures to
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FIGDIR = REPO / "paper" / "figs"

# Text-block width of each document, in points (measured with \the\textwidth).
# Each document's text-block width in points, and every file that can carry an
# \includegraphics for it. The root .tex files matter: the graphical abstract is
# included directly in V7.tex and nowhere else, so globbing only sections/ let it
# escape this check entirely.
DOCS = {
    "AE body":  (345.00, [REPO / "paper" / "ae_submission" / "sections"],
                 [REPO / "paper" / "ae_submission" / "V7.tex"]),
    # 469.755 pt: the SI moved from a4paper to letterpaper so the submission is not two
    # page sizes. Measured with \the\textwidth, not assumed.
    "AE SI":    (469.76, [REPO / "paper" / "ae_submission" / "si_body"],
                 [REPO / "paper" / "ae_submission" / "SI.tex"]),
    "long":     (455.24, [REPO / "paper" / "sections"],
                 [REPO / "paper" / "Paper_v20.tex"]),
}

# Below this scale, an 8 pt label prints under 6 pt. Worth a look, not automatically wrong:
# a figure whose smallest font is 12 pt is fine at 0.5.
REVIEW_SCALE = 6.0 / 8.0     # an 8 pt label is the common case; below this it drops under 6 pt

INC = re.compile(r"\\includegraphics\[[^\]]*width=([\d.]*)\\textwidth\]\{([^}]+)\}")


def find_fig(name: str) -> Path | None:
    """Locate the figure PDF an \\includegraphics names, wherever it sits under figs/.

    An earlier version of this file resolved the PDF twice, once by rglob for the MediaBox
    and once as FIGDIR/<stem>.pdf for the font sizes. The second form never matched, since
    every figure lives a directory down in figs/paper/, so the measured-size pass silently
    read nothing and reported every figure clean. One resolver now serves both.
    """
    stem = Path(name).name
    if not stem.endswith(".pdf"):
        stem += ".pdf"
    hits = sorted(FIGDIR.rglob(stem))
    return hits[0] if hits else None


def native_width_pt(pdf: Path) -> float | None:
    """MediaBox width of the figure PDF, in points."""
    raw = pdf.read_bytes()[:400_000]
    m = re.search(rb"/MediaBox\s*\[\s*([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)", raw)
    if m:
        x0, _, x1, _ = (float(v) for v in m.groups())
        return x1 - x0
    return None


def measured_font_sizes(pdf: Path) -> list[float]:
    """Font sizes actually set in a figure PDF's content stream, in native points.

    The scale proxy above cannot prove legibility and says so, and the "guarded" exemption
    turned out to be weaker still: _figstyle.assert_printable() checks the sizes an author
    DECLARES, so it cannot see matplotlib's mathtext shrink (sub/superscripts render at
    0.694x), and it cannot see sizes chosen by matplotlib itself, such as a log-axis
    formatter's minor labels. Five inclusions printed glyphs under 6 pt while every check
    here passed.

    This reads the `<size> Tf` operators out of the decompressed content streams, which is
    what the renderer will actually use. Multiply by the print scale for the printed size.
    """
    import zlib
    raw = pdf.read_bytes()
    sizes: list[float] = []
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", raw, re.S):
        chunk = m.group(1)
        try:
            chunk = zlib.decompress(chunk)
        except zlib.error:
            pass
        for tf in re.finditer(rb"/[A-Za-z0-9+._-]+\s+([\d.]+)\s+Tf", chunk):
            try:
                v = float(tf.group(1))
            except ValueError:
                continue
            if 0.5 < v < 100:
                sizes.append(v)
    return sizes


def guarded_figures() -> set[str]:
    """Figures whose generator enforces the floor with assert_printable()."""
    out = set()
    for py in (REPO / "code" / "scripts").glob("*.py"):
        txt = py.read_text()
        if "assert_printable" not in txt and "assert_legible" not in txt:
            continue
        # labels may carry a parenthetical qualifier, e.g. 'P00_model_flow (AE body)'
        out.update(m.split()[0] for m in re.findall(r'label="([^"]+)"', txt))
        out.update(re.findall(r'"(P\d+[A-Za-z0-9_]*|graphical_abstract)\.(?:png|pdf)"', txt))
    return out


def main() -> int:
    guarded = guarded_figures()
    flagged, missing = [], []
    for doc, (column, dirs, roots) in DOCS.items():
        rows = []
        files = [t for d in dirs for t in sorted(d.glob("*.tex"))]
        files += [r for r in roots if r.exists()]
        for tex in files:
            for frac, name in INC.findall(tex.read_text()):
                f = float(frac) if frac else 1.0
                pdf = find_fig(name)
                nat = native_width_pt(pdf) if pdf else None
                if nat is None:
                    rows.append((name, f, None, None, tex.name, pdf))
                    continue
                rows.append((name, f, nat, f * column / nat, tex.name, pdf))
        print(f"\n=== {doc}  (text block {column:.2f} pt) ===")
        print(f"{'figure':34s}{'frac':>6}{'native pt':>11}{'scale':>8}  note")
        for name, f, nat, s, tex, pdf in sorted(rows, key=lambda r: (r[3] is None, r[3] or 0)):
            stem = Path(name).stem
            if nat is None:
                # A figure this gate cannot find is a failure, not a line of output. It
                # printed "figure PDF not found" and passed, which is the same shape as
                # the unmeasurable image the Word DPI gate used to drop silently: an
                # inclusion nobody measured, reported as though it had been measured.
                print(f"{stem:34s}{f:6.2f}{'?':>11}{'?':>8}  FIGURE PDF NOT FOUND ({tex})")
                missing.append((doc, stem, tex))
                continue
            note = "guarded" if stem in guarded else ""
            # Measured, not inferred: the smallest glyph the renderer will actually set,
            # scaled to the page. This catches what the proxy and the generator-side guard
            # both miss, so a "guarded" figure is no longer exempt from it.
            measured = measured_font_sizes(pdf) if pdf else []
            if measured and min(measured) * s < FLOOR_PT:
                note = ("SUB-%.0fPT: smallest glyph prints at %.2f pt (%d of %d glyph runs "
                        "under the floor)"
                        % (FLOOR_PT, min(measured) * s,
                           sum(1 for v in measured if v * s < FLOOR_PT), len(measured)))
                flagged.append((doc, stem, s, min(measured) * s))
            elif s < REVIEW_SCALE and stem not in guarded and not measured:
                note = "REVIEW: an 8 pt label prints at %.1f pt" % (8.0 * s)
                flagged.append((doc, stem, s, 8.0 * s))
            print(f"{stem:34s}{f:6.2f}{nat:11.1f}{s:8.3f}  {note}")

    if missing:
        print(f"\n{len(missing)} inclusion(s) name a figure this gate could not find:")
        for doc, stem, tex in missing:
            print(f"  {doc:9s} {stem:34s} included by {tex}")
        print("An inclusion nobody can measure has not been checked.")
        return 1

    if flagged:
        print(f"\n{len(flagged)} inclusion(s) set type below the {FLOOR_PT:.0f} pt floor "
              "as printed:")
        for doc, stem, s, worst in sorted(flagged, key=lambda r: r[3]):
            print(f"  {doc:9s} {stem:34s} scale {s:.3f}  smallest {worst:.2f} pt")
        print("Either widen the inclusion, shrink the generator's canvas, or raise the "
              "generator's font sizes.")
        return 1
    print(f"\nEvery inclusion sets its smallest glyph at or above {FLOOR_PT:.0f} pt "
          "as printed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
