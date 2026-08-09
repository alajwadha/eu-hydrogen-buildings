#!/usr/bin/env python3
"""Append EQ-MARK-n after each numbered equation in the staged LaTeX.

LaTeX numbers a displayed equation and pandoc has nowhere to put that number, so it
vanishes and every "Eq. (7)" in the text points at nothing visible. This leaves a marker
the Word pass converts into a right-aligned number beside the equation. The number comes
from the compiled .aux, so it is the same one the PDF prints.

Run: python mark_equations.py Paper_v20.aux staged/main.tex staged/sections/*.tex
"""
import re
import sys

NEWLABEL = re.compile(r"\\newlabel\{([^}]+)\}\{\{([^}]*)\}")
ENVS = ("equation", "align", "gather")


def labels(aux):
    out = {}
    for line in open(aux, encoding="utf-8", errors="replace"):
        m = NEWLABEL.search(line)
        if m and m.group(1) not in out:
            out[m.group(1)] = m.group(2)
    return out


def main():
    aux, files = sys.argv[1], sys.argv[2:]
    lab = labels(aux)
    total = 0
    for path in files:
        text = open(path, encoding="utf-8").read()
        for env in ENVS:
            def sub(m):
                num = lab.get(m.group(1))
                return m.group(0) if not num else m.group(0) + "\n\nEQ-MARK-" + num + "\n"
            text, n = re.subn(
                r"\\begin\{%s\}.*?\\label\{([^}]+)\}.*?\\end\{%s\}" % (env, env),
                sub, text, flags=re.S)
            total += n
        open(path, "w", encoding="utf-8").write(text)
    print("mark_equations: marked %d numbered equations" % total)


if __name__ == "__main__":
    main()
