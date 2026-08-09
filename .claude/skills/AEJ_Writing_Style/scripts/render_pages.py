#!/usr/bin/env python3
"""Render a PDF to page images so the layout can be looked at rather than inferred.

Every other script here reads the source. This one produces something to look at, because
a caption that is too long, a figure floating at 70 per cent width, an axis label under
6 pt and an orphaned float are all invisible in the source and obvious on the page.

Two modes, both usually wanted:

  structure  low resolution, whole pages, for the flick-through. Shape, density, where the
             figures fall, which pages are half empty.
  detail     high resolution, named pages, for reading the smallest text in a figure.

Run:
  python render_pages.py main.pdf                      # structure, all pages
  python render_pages.py main.pdf --pages 20-24        # structure, a range
  python render_pages.py main.pdf --detail 22          # one page, readable
  python render_pages.py main.pdf --detail 22,25,31    # several

Needs pdftoppm from poppler, which is present wherever pdftotext is.

After it runs, open the images. The point is to use your eye. references/visual_review.md
carries the checklist and what the published corpus looks like.
"""
from __future__ import annotations
import argparse
import os
import shutil
import subprocess
import sys

STRUCTURE_DPI = 55   # a whole page fits in one view
DETAIL_DPI = 150     # axis labels are readable


def pages_of(pdf: str) -> int:
    try:
        out = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True,
                             check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return 0
    for line in out.splitlines():
        if line.startswith("Pages:"):
            return int(line.split()[1])
    return 0


def parse_range(spec: str, last: int):
    """'20-24' or '22,25,31' or '7' -> list of (first, last) runs."""
    runs = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            runs.append((int(a), int(b)))
        else:
            runs.append((int(part), int(part)))
    return [(max(1, a), min(last, b)) for a, b in runs if a <= last]


def render(pdf: str, outdir: str, stem: str, first: int, last: int, dpi: int):
    os.makedirs(outdir, exist_ok=True)
    prefix = os.path.join(outdir, stem)
    subprocess.run(["pdftoppm", "-png", "-r", str(dpi),
                    "-f", str(first), "-l", str(last), pdf, prefix], check=True)
    return sorted(f for f in os.listdir(outdir)
                  if f.startswith(stem + "-") and f.endswith(".png"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--out", default="render_review",
                    help="output directory (default render_review/)")
    ap.add_argument("--pages", help="structure pass over this range, e.g. 20-24")
    ap.add_argument("--detail", help="detail pass on these pages, e.g. 22 or 22,25")
    ap.add_argument("--dpi", type=int, help="override the resolution")
    a = ap.parse_args()

    if not shutil.which("pdftoppm"):
        sys.exit("pdftoppm not found. Install poppler-utils.")
    if not os.path.exists(a.pdf):
        sys.exit(f"no such file: {a.pdf}")

    n = pages_of(a.pdf)
    if not n:
        sys.exit("could not read the page count; is this a PDF?")
    print(f"{a.pdf}: {n} pages")

    wrote = []
    if a.detail:
        for first, last in parse_range(a.detail, n):
            wrote += render(a.pdf, a.out, "detail", first, last,
                            a.dpi or DETAIL_DPI)
    else:
        spec = a.pages or f"1-{n}"
        for first, last in parse_range(spec, n):
            wrote += render(a.pdf, a.out, "page", first, last,
                            a.dpi or STRUCTURE_DPI)

    if not wrote:
        sys.exit("nothing rendered; check the page range")

    print(f"\n{len(wrote)} images in {a.out}/")
    for f in wrote[:40]:
        print("   ", os.path.join(a.out, f))
    if len(wrote) > 40:
        print(f"    ... and {len(wrote) - 40} more")

    print("""
Now look at them. In order:

  1. Flick through the low-resolution pages. Where does the eye stop? Which pages are
     half empty? Are the figures spread through the results or clumped?
  2. On each figure page: does the figure fill its measure, is the legend boxed and
     inside the axes, does every bar carry its value, how many lines is the caption?
  3. On each table page: three horizontal rules and no verticals, units in the header,
     provenance in lettered footnotes rather than the caption.

If this is an elsarticle [review] build, remember it is single column and double spaced,
so it is 60 to 70 per cent white where the published article is nearly full. Read nothing
into that: balance, density and float placement are production's, and the review format
makes them misleading anyway. Judge content, not proportion.

Legibility at column width is the one thing this cannot show. Compute it rather than
rebuilding anything: width=f\\textwidth scales by width alone, so a p-point label prints
at p * f * 3.4 / (figure's native width in inches). Hold a 6 pt floor.

references/visual_review.md has the full checklist.""")


if __name__ == "__main__":
    main()
