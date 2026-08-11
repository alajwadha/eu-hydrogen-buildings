"""Fail when the Word twin embeds a figure below Elsevier's raster floor.

Measured on the shipped .docx, not on the sources, because that is where the defect was.
Every generator saved a perfectly good PNG and every vector PDF sat beside it; the Word
path scaled those PNGs to a fixed physical width, so the file an editor receives carried
its artwork at 199 to 213 dpi against a 300 dpi floor for combination artwork. Nothing in
the repository could see it: the print-scale gate measures glyph size in points, which is
resolution-independent, and the freshness gate compares timestamps.

The rule is the same one the upload-set gate follows. Check the rendering a reader is
handed, not the source it was made from.

Run:  cd code && PYTHONPATH=. python -m scripts.check_word_figure_dpi
Exit: non-zero if any embedded image prints below MIN_DPI.
"""
from __future__ import annotations

import io
import re
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOCX = REPO / "paper" / "ae_submission" / "V7.docx"
MIN_DPI = 300.0          # Elsevier: 300 for combination artwork, 500+ for line art
EMU_PER_INCH = 914400.0


def embedded() -> list[tuple[str, int, float]]:
    """(relationship target, pixel width, display width in inches) per drawing."""
    from PIL import Image
    out = []
    with zipfile.ZipFile(DOCX) as z:
        doc = z.read("word/document.xml").decode("utf-8", "replace")
        rels = dict(re.findall(r'Id="([^"]+)"[^>]*?Target="([^"]+)"',
                               z.read("word/_rels/document.xml.rels").decode("utf-8", "replace")))
        # Each drawing pairs an extent (EMU) with a blip embed id, in document order.
        for m in re.finditer(r"<wp:extent\s+cx=\"(\d+)\"[^>]*/>.*?r:embed=\"([^\"]+)\"",
                             doc, re.S):
            cx, rid = int(m.group(1)), m.group(2)
            target = rels.get(rid)
            if not target:
                continue
            name = "word/" + target.lstrip("/").replace("../", "")
            try:
                px = Image.open(io.BytesIO(z.read(name))).size[0]
            except Exception:
                # An image that cannot be measured is a failure, not an omission. Dropping
                # it silently made the gate report "All 7 embedded figures at or above
                # 300 dpi" while the eighth had been replaced by non-image bytes.
                out.append((Path(target).name, 0, cx / EMU_PER_INCH))
                continue
            out.append((Path(target).name, px, cx / EMU_PER_INCH))
    return out


def main() -> int:
    if not DOCX.exists():
        print(f"{DOCX.relative_to(REPO)} not built; run build_docx_elsevier.py first.")
        return 1
    imgs = embedded()
    if not imgs:
        print("no embedded images found in the Word twin; the extractor needs updating.")
        return 1
    unreadable = [n for n, px, _ in imgs if px == 0]
    bad = [(n, px, w, px / w) for n, px, w in imgs if w > 0 and px / w < MIN_DPI]
    if unreadable:
        print(f"{len(unreadable)} embedded object(s) could not be measured: "
              + ", ".join(unreadable))
        return 1
    for n, px, w, d in sorted(((n, px, w, px / w) for n, px, w in imgs if w > 0),
                              key=lambda r: r[3]):
        print(f"  {n:22s} {px:5d} px over {w:5.2f} in = {d:6.1f} dpi")
    if bad:
        print(f"\n{len(bad)} embedded figure(s) below the {MIN_DPI:.0f} dpi floor. Raise the "
              "generator's savefig dpi; the vector PDFs already sit beside the PNGs.")
        return 1
    print(f"\nAll {len(imgs)} embedded figures at or above {MIN_DPI:.0f} dpi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
