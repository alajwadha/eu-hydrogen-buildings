#!/usr/bin/env python3
"""Resolve LaTeX \\ref / \\eqref cross-references to literal numbers for the Word build.

pandoc renders the staged .tex without a LaTeX .aux, so \\ref{label} leaks the raw label
(for example "[sec:rq]") into the Word document instead of the section number. This script
reads the authoritative label-to-number map from the compiled Paper_v20.aux and rewrites
\\ref{label} -> N and \\eqref{label} -> (N) in the staged source files, so the Word
cross-references match the numbers LaTeX assigned in the PDF. It never invents a number:
an unknown label is left untouched and reported, so the build surfaces it rather than
silently emitting a wrong reference.

Usage: python resolve_refs_docx.py Paper_v20.aux staged_main.tex staged_sections/*.tex
"""
import re
import sys

NEWLABEL = re.compile(r"\\newlabel\{([^}]+)\}\{\{([^}]*)\}")


def load_labels(aux_path):
    labels = {}
    with open(aux_path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = NEWLABEL.search(line)
            if not m:
                continue
            label, number = m.group(1), m.group(2)
            # the first field of the \newlabel payload is the printed reference number
            if label not in labels:
                labels[label] = number
    return labels


def rewrite(text, labels, missing):
    def ref_sub(m):
        label = m.group(1)
        if label in labels:
            return labels[label]
        missing.add(label)
        return m.group(0)

    def eqref_sub(m):
        label = m.group(1)
        if label in labels:
            return "(" + labels[label] + ")"
        missing.add(label)
        return m.group(0)

    text = re.sub(r"\\eqref\{([^}]+)\}", eqref_sub, text)
    text = re.sub(r"\\ref\{([^}]+)\}", ref_sub, text)
    return text


def main(argv):
    if len(argv) < 3:
        sys.exit("usage: resolve_refs_docx.py <aux> <texfile> [<texfile> ...]")
    aux_path, tex_files = argv[1], argv[2:]
    labels = load_labels(aux_path)
    if not labels:
        sys.exit("no \\newlabel entries found in %s; compile the PDF first" % aux_path)
    missing = set()
    for path in tex_files:
        with open(path, encoding="utf-8", errors="replace") as fh:
            src = fh.read()
        out = rewrite(src, labels, missing)
        if out != src:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(out)
    print("resolve_refs_docx: %d labels loaded, %d files scanned" % (len(labels), len(tex_files)))
    if missing:
        print("resolve_refs_docx: WARNING unresolved labels left as-is: %s"
              % ", ".join(sorted(missing)))


if __name__ == "__main__":
    main(sys.argv)
