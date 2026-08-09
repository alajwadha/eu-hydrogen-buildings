#!/usr/bin/env python3
"""Prepend the authoritative "Figure N: " / "Table N: " label to every float caption in the Word build.

pandoc's docx writer renders a LaTeX ``\\caption{...}`` as a styled caption paragraph (ImageCaption
or TableCaption in our reference template) but DROPS the float number: the Word caption reads
"The comparative hydrogen-versus-..." where the PDF reads "Figure 1: The comparative ...". The
number is what every in-text "Figure N" / "Table N" reference points at, so without it the Word
cross-references are unresolvable and the float has no title label at all.

This post-processor restores the labels. It reads the authoritative figure/table numbers LaTeX
assigned (from the compiled Paper_v20.aux ``\\newlabel{fig:..}{{N}...{...caption text...}{figure.caption..}``
payload), normalises each caption's text, and matches it against the ImageCaption/TableCaption
paragraphs in the docx by a leading-text fingerprint. It then prepends "Figure N: " / "Table N: "
(bold) to the matched paragraph. Matching by text, not by order, so a float whose caption pandoc
relocates or a sequence gap does not mis-number the rest. Unmatched captions are reported.

Run AFTER pandoc, on the assembled docx: python number_captions.py Paper_v20.aux in.docx [out.docx]
"""
import re
import sys

from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# \newlabel{fig:lit_landscape}{{1}{19}{The comparative ... full caption ...}{figure.caption.4}{}}
#
# This was a regex, and it silently matched under half the floats. Two reasons, both invisible
# in its output because an unmatched float is only a warning:
#
#   * The number group was \d+, but the long paper numbers its appendix floats A.6, B.3, C.1.
#     Every appendix caption therefore failed outright, which is most of them.
#   * The caption group was a non-greedy (.*?)\}, which stops at the FIRST closing brace. Any
#     caption carrying \euro{}, \ce{CO2} or a \ref ends there, so its fingerprint was a
#     truncated fragment that matched nothing in the docx.
#
# Brace counting handles both. The header is matched loosely and the caption is then scanned
# with a depth counter, so nesting is safe and the number is whatever LaTeX actually wrote.
NEWLABEL_HEAD = re.compile(r"newlabel\{(fig|tab):([^}]*)\}\{\{([^{}]*)\}\{[^{}]*\}\{")


def _balanced(text, i):
    """Return (contents, index after the closing brace) for the group opening at text[i-1]=='{'."""
    depth, start = 1, i
    while i < len(text) and depth:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return text[start:i - 1], i


def _norm(text):
    """Lowercase alphanumeric fingerprint of a caption's opening, robust to LaTeX vs Word glyphs.

    Strips LaTeX control sequences and braces/maths, drops every non-alphanumeric character
    (so "CO_2", "CO2" and "CO  2" all collapse to "co2"), and keeps the leading run that
    uniquely identifies the caption.
    """
    t = re.sub(r"\\[a-zA-Z]+\s*\*?", " ", text)   # drop \citep, \eqref, \textwidth, ...
    t = re.sub(r"[^0-9A-Za-z]+", "", t)           # keep only alphanumerics
    return t.lower()


def load_aux(aux_path):
    """Return {'fig': {norm_prefix: 'N'}, 'tab': {...}} from the compiled .aux.

    The number is kept as the string LaTeX wrote, so "A.6" survives alongside "7".
    """
    text = open(aux_path, encoding="utf-8", errors="replace").read()
    out = {"fig": {}, "tab": {}}
    for m in NEWLABEL_HEAD.finditer(text):
        kind, num = m.group(1), m.group(3).strip()
        cap, j = _balanced(text, m.end())
        # confirm this really is a float caption anchor and not some other \newlabel payload
        if not re.match(r"\s*\{(figure|table)\.caption", text[j:j + 24]):
            continue
        key = _norm(cap)[:40]
        if key and num:
            out[kind].setdefault(key, num)
    return out


def _caption_text(p):
    return "".join(t.text or "" for t in p._p.iter(qn("w:t")))


def _style(p):
    pPr = p._p.find(qn("w:pPr"))
    if pPr is None:
        return ""
    ps = pPr.find(qn("w:pStyle"))
    return ps.get(qn("w:val")) if ps is not None else ""


def _prepend_label(p, label):
    """Insert a bold "<label>: " run as the first run of the paragraph."""
    r = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    b = OxmlElement("w:b")
    rPr.append(b)
    r.append(rPr)
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = label + ": "
    r.append(t)
    # place after pPr (if any) but before the first existing run
    pPr = p._p.find(qn("w:pPr"))
    if pPr is not None:
        pPr.addnext(r)
    else:
        p._p.insert(0, r)


def main(argv):
    if len(argv) < 3:
        sys.exit("usage: number_captions.py <aux> <in.docx> [out.docx]")
    aux_path, src = argv[1], argv[2]
    dst = argv[3] if len(argv) > 3 else src
    nums = load_aux(aux_path)
    if not nums["fig"] and not nums["tab"]:
        sys.exit("no figure/table \\newlabel entries in %s; compile the PDF first" % aux_path)

    doc = Document(src)
    style_kind = {"ImageCaption": "fig", "TableCaption": "tab"}
    label_word = {"fig": "Figure", "tab": "Table"}
    done = {"fig": 0, "tab": 0}
    missing = []
    already = 0
    for p in doc.paragraphs:
        kind = style_kind.get(_style(p))
        if not kind:
            continue
        txt = _caption_text(p)
        if re.match(r"\s*(Figure|Table)\s+\d", txt):
            already += 1
            continue
        key = _norm(txt)[:40]
        n = nums[kind].get(key)
        if n is None:
            # fall back to the longest matching known prefix (handles trailing-text truncation)
            cand = [v for k, v in nums[kind].items() if key.startswith(k[:25]) or k.startswith(key[:25])]
            n = cand[0] if len(set(cand)) == 1 else None
        if n is None:
            missing.append((kind, txt[:50]))
            continue
        _prepend_label(p, "%s %s" % (label_word[kind], n))   # %s: appendix floats read "A.6"
        done[kind] += 1

    doc.save(dst)
    print("number_captions: labelled %d figures, %d tables (%d already labelled)"
          % (done["fig"], done["tab"], already))
    if missing:
        for kind, t in missing:
            print("number_captions: WARNING unmatched %s caption: %r" % (kind, t))


if __name__ == "__main__":
    main(sys.argv)
