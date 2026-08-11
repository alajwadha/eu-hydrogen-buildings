#!/usr/bin/env python3
"""Build the Applied Energy submission as Word (.docx) and PDF from the gated
LaTeX sections — WITHOUT a system LaTeX install.

  Word : pandoc (via pypandoc_binary), LaTeX -> .docx  (author-year rendered by citeproc)
  PDF  : pandoc + weasyprint engine,   LaTeX -> .pdf
  Refs : numbered, via ../ieee.csl

The canonical *submission* source remains V7.tex (elsarticle) — compile that on
Overleaf for the official Applied Energy PDF. This script produces readable,
shareable Word/PDF twins of the same content.

Deps (already pip-installed in this environment):
  pip install pypandoc_binary weasyprint
Run:
  python3 paper/ae_submission/build.py
"""
import os
import re
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
SECT = os.environ.get("AE_SRCDIR", os.path.join(HERE, "sections"))
OUTDIR = os.environ.get("AE_OUTDIR", HERE)
FIGDIR = os.path.abspath(os.path.join(HERE, "..", "figs", "paper"))
BIB = os.path.abspath(os.path.join(HERE, "..", "References_v1.bib"))
CSL = os.path.abspath(os.path.join(HERE, "..", "ieee.csl"))

SECTION_ORDER = ["intro", "methods", "results", "concl"]

DEFAULT_TITLE = 'Hydrogen in residential heating and the power system: a merit-order and capital-recovery assessment for 29 European markets'


def _read(path):
    return open(path, encoding="utf-8").read() if os.path.exists(path) else ""


def _replace_flag(tex):
    """Replace \\FLAG{...} with visible bold text, matching BALANCED braces so a
    flag reason containing \\euro{}, \\cite{...} etc. is handled correctly."""
    key = r"\FLAG{"
    out, i, n = [], 0, len(tex)
    while i < n:
        j = tex.find(key, i)
        if j < 0:
            out.append(tex[i:])
            break
        out.append(tex[i:j])
        k, depth = j + len(key), 1
        while k < n and depth > 0:
            if tex[k] == "{":
                depth += 1
            elif tex[k] == "}":
                depth -= 1
            k += 1
        inner = tex[j + len(key):k - 1]
        out.append(r"\textbf{[FLAG: " + inner + "]}")
        i = k
    return "".join(out)


def preprocess(tex):
    """Make the gated LaTeX safe for pandoc's LaTeX reader."""
    # 1. eurosym / unit macros FIRST (so any inside a \FLAG{...} lose their braces).
    tex = tex.replace(r"\euro{}", "€").replace(r"\euro", "€")
    for a, b in ((r"\ce{CO2}", "CO₂"), (r"\ce{H2}", "H₂"),
                 (r"\ce{CH4}", "CH₄"), (r"\ce{NOx}", "NOₓ")):
        tex = tex.replace(a, b)
    # 2. Make \FLAG{...} visible (balanced-brace aware).
    tex = _replace_flag(tex)
    # 3. Figures: ensure a .png extension so pandoc/weasyprint can embed the raster twin.
    def fix_img(m):
        opt, name = (m.group(1) or ""), m.group(2)
        if not os.path.splitext(name)[1]:
            name = name + ".png"
        return r"\includegraphics%s{%s}" % (opt, name)
    tex = re.sub(r"\\includegraphics(\[[^\]]*\])?\{([^{}]+)\}", fix_img, tex)
    return tex


def build_body():
    parts = []
    # Optional front matter produced by the front-matter pass (B3): title/abstract/highlights.
    fm = os.path.join(HERE, "frontmatter_body.tex")
    if os.path.exists(fm):
        parts.append(preprocess(_read(fm)))
    for key in SECTION_ORDER:
        body = _read(os.path.join(SECT, key + ".tex"))
        if body:
            parts.append(preprocess(body))
    parts.append(r"\section*{References}")  # citeproc appends the list here
    return "\n\n".join(parts)


def main():
    import pypandoc

    src = os.path.join(OUTDIR, "_reading.tex")
    open(src, "w", encoding="utf-8").write(build_body())

    common = [
        "--from=latex",
        "--citeproc",
        "--bibliography=%s" % BIB,
        "--resource-path=%s" % os.pathsep.join([HERE, FIGDIR]),
        "--metadata", "title=%s" % DEFAULT_TITLE,
        "--metadata", "link-citations=true",
    ]
    if os.path.exists(CSL):
        common += ["--csl=%s" % CSL]

    # These go to a scratch subdirectory, not alongside V7.pdf/V7.docx. They are a
    # different pipeline (pandoc plus WeasyPrint) and a different word count, and shipping
    # them in the submission folder gave anyone uploading from it a coin-flip between two
    # PDFs of the same paper. V7.pdf and V7.docx are the deliverables.
    scratch = os.path.join(OUTDIR, "_reading_copies")
    os.makedirs(scratch, exist_ok=True)
    docx = os.path.join(scratch, "Paper_AE.docx")
    pdf = os.path.join(scratch, "Paper_AE.pdf")

    pypandoc.convert_file(src, "docx", outputfile=docx, extra_args=common)
    print("wrote", docx, os.path.getsize(docx), "bytes")

    pypandoc.convert_file(src, "pdf", outputfile=pdf,
                          extra_args=common + ["--pdf-engine=weasyprint", "--mathml", "--standalone"])
    print("wrote", pdf, os.path.getsize(pdf), "bytes")


if __name__ == "__main__":
    main()
