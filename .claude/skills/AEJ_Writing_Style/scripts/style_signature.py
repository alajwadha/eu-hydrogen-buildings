#!/usr/bin/env python3
"""Compare a manuscript's sentence-level constructions against a journal corpus.

Length metrics tell you a caption is too long. They cannot tell you why a draft reads
as the wrong genre, because genre lives in construction: whether the figure or the
author is the subject, which connectives hinge the paragraphs, whether findings are
announced or argued into. Those are countable, and the count is usually stark: a draft
can use literally none of the connectives a journal runs on.

Defaults are measured from 14 published Applied Energy techno-economic papers
(130,036 words). Pass --corpus to re-derive them from any set of extracted articles.

Run:  python style_signature.py main.tex sections/*.tex
      python style_signature.py main.tex --corpus <dir-of-txt>
"""
from __future__ import annotations
import argparse
import os
import re

GUT = re.compile(r"\s{4,}")

# Per 10,000 words, measured from the shipped Applied Energy corpus.
AE = {
    "Fig./Table as sentence subject": 3.3,
    "As can be seen / as shown": 2.8,
    "This study/paper presents": 1.6,
    "We find/show/propose": 0.5,
    "The results show/indicate": 2.0,
    "Analysis reveals/shows": 0.9,
    "It can be seen/inferred/noted": 0.6,
    "respectively": 8.8,
    "In this study/paper": 6.2,
    "Moreover/Furthermore/In addition": 9.9,
    "However": 8.9,
    "compared to/with": 4.4,
    "ranging from/between": 1.7,
}

PAT = {
    "Fig./Table as sentence subject":
        r"\b(?:Fig\.|Figure|Table)\s*\d*\s*(?:shows|presents|illustrates|depicts"
        r"|summarises|summarizes|compares|reports|displays)",
    "As can be seen / as shown": r"\bas (?:can be seen|shown|illustrated|depicted)\b",
    "This study/paper presents":
        r"\bthis (?:study|paper|work|research) (?:presents|develops|proposes"
        r"|investigates|examines|provides|introduces|assesses|explores|aims)",
    "We find/show/propose":
        r"\bwe (?:find|show|propose|develop|present|investigate|demonstrate"
        r"|observe|conclude|introduce|apply|assess)\b",
    "The results show/indicate":
        r"\b(?:the )?results? (?:show|indicate|reveal|suggest|demonstrate|highlight)\b",
    "Analysis reveals/shows":
        r"\b(?:analysis|assessment|simulation|sensitivity analysis) "
        r"(?:reveals?|shows?|indicates?|demonstrates?)\b",
    "It can be seen/inferred/noted":
        r"\bit (?:can be|should be|is) (?:seen|inferred|noted|observed|concluded)\b",
    "respectively": r"\brespectively\b",
    "In this study/paper": r"\bin this (?:study|paper|work)\b",
    "Moreover/Furthermore/In addition":
        r"\b(?:Moreover|Furthermore|In addition|Additionally)\b",
    "However": r"\bHowever\b",
    "compared to/with": r"\bcompared (?:to|with)\b",
    "ranging from/between": r"\brang(?:ing|es|ed) (?:from|between)\b",
}


def detex(s: str) -> str:
    s = re.sub(r"\\begin\{(figure|table|equation|align|tabular|description)\}"
               r".*?\\end\{\1\}", " ", s, flags=re.S)
    s = re.sub(r"\\(?:label|ref|eqref|cite[tp]?|citep|citet)\s*\{[^}]*\}", " ", s)
    s = re.sub(r"%.*", " ", s)
    s = re.sub(r"\\[a-zA-Z]+\*?\s*", " ", s)
    for ch in "{}$~":
        s = s.replace(ch, " ")
    return " ".join(s.split())


def decolumn(t: str) -> str:
    """Two-column PDF text: keep the longest chunk per line, which is the prose."""
    out = []
    for line in t.split("\n"):
        cs = [c.strip() for c in GUT.split(line.strip()) if c.strip()]
        out.append(max(cs, key=len) if cs else "")
    return " ".join(out)


def rates(text: str) -> tuple[dict, int]:
    n = max(len(text.split()), 1)
    return ({k: 10000 * len(re.findall(p, text, re.I)) / n
             for k, p in PAT.items()}, n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tex", nargs="*")
    ap.add_argument("--corpus", help="directory of extracted .txt articles")
    a = ap.parse_args()

    target = AE
    if a.corpus:
        blob = " ".join(decolumn(open(os.path.join(a.corpus, f), encoding="utf-8",
                                      errors="replace").read())
                        for f in os.listdir(a.corpus) if f.endswith(".txt"))
        target, cn = rates(blob)
        print(f"corpus re-derived from {a.corpus}: {cn:,} words\n")

    if not a.tex:
        print(f"  {'construction':<34} per 10k words")
        for k in PAT:
            print(f"  {k:<34} {target[k]:>8.1f}")
        return

    ours, n = rates(detex("\n".join(open(f, encoding="utf-8", errors="replace").read()
                                    for f in a.tex)))
    print(f"manuscript: {n:,} words\n")
    print(f"  {'construction':<34} {'draft':>7} {'journal':>8}   gap")
    missing = []
    for k in PAT:
        d, j = ours[k], target[k]
        flag = ""
        if j >= 1.5 and d == 0:
            flag = "  ABSENT"
            missing.append(k)
        elif j >= 1.5 and d < j / 3:
            flag = "  thin"
        print(f"  {k:<34} {d:>7.1f} {j:>8.1f}{flag}")

    if missing:
        print(f"\n{len(missing)} construction(s) the journal relies on and the draft "
              f"never uses:")
        for k in missing:
            print(f"  - {k}")
        print("\nThis is what makes a draft read as the wrong genre. Add these where "
              "they\ngenuinely help a transition; do not sprinkle them to hit a rate.")


if __name__ == "__main__":
    main()
