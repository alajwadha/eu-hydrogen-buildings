#!/usr/bin/env python3
"""Measure a LaTeX manuscript against the Applied Energy corpus norms.

The point is not to score the writing. It is to say, for each signal where a working
paper habitually differs from a journal article, whether this draft sits inside the
published range and by how much it misses if not. A caption that runs 90 words is not
wrong in the abstract; it is wrong because no paper in the corpus does it.

Run:  python check_manuscript.py <main.tex> [more.tex ...] [--norms corpus.json]
"""
from __future__ import annotations
import argparse
import json
import os
import re
import statistics as st

# Norms measured from the shipped corpus. Override with --norms to re-derive.
NORMS = {
    "caption_words":  {"median": 20, "p90": 64, "hard": 80,
                       "note": "figure captions, 154 measured"},
    "table_caption":  {"median": 11, "p90": 27, "hard": 40,
                       "note": "table captions, 81 measured"},
    "abstract_words": {"median": 271, "p10": 228, "p90": 329,
                       "note": "10 cleanly extracted abstracts"},
    "sentence_words": {"median": 21, "p90": 49, "hard": 60,
                       "note": "6,103 sentences"},
}


def strip_tex(s: str) -> str:
    s = re.sub(r"\\(?:label|ref|eqref|cite[tp]?|citep|citet)\s*\{[^}]*\}", "", s)
    s = re.sub(r"\\[a-zA-Z]+\*?\s*", " ", s)
    s = s.replace("~", " ").replace("{", "").replace("}", "").replace("$", "")
    return " ".join(s.split())


def balanced(s: str, start: int) -> str:
    """The argument of a command whose opening brace is at `start`."""
    depth, i = 0, start
    while i < len(s):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return s[start + 1:i]
        i += 1
    return ""


def captions(tex: str):
    out = []
    for m in re.finditer(r"\\caption\s*\{", tex):
        body = balanced(tex, m.end() - 1)
        # Which float is it in? Look back for the nearest \begin.
        pre = tex[:m.start()]
        b = max(pre.rfind(r"\begin{figure}"), pre.rfind(r"\begin{table}"))
        kind = "Table" if pre.rfind(r"\begin{table}") > pre.rfind(r"\begin{figure}") \
            else "Figure"
        out.append((kind, len(strip_tex(body).split()), strip_tex(body)[:70]))
    return out


def sentences(tex: str):
    body = re.sub(r"\\begin\{(figure|table|equation|align|tabular|description)\}"
                  r".*?\\end\{\1\}", " ", tex, flags=re.S)
    body = strip_tex(body)
    out = []
    for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(])", body):
        n = len(s.split())
        if 4 <= n <= 120:
            out.append((n, s[:80]))
    return out


def verdict(name, value, norm):
    hard = norm.get("hard")
    p90 = norm.get("p90")
    if hard and value > hard:
        return "OVER", f"beyond anything in the corpus (p90 {p90})"
    if p90 and value > p90:
        return "high", f"above the corpus p90 of {p90}"
    return "ok", ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tex", nargs="+")
    ap.add_argument("--norms")
    ap.add_argument("--top", type=int, default=8)
    a = ap.parse_args()

    norms = NORMS
    if a.norms:
        raw = json.load(open(a.norms))["aggregate"]
        q = lambda v, p: sorted(v)[min(int(p * len(v)), len(v) - 1)]
        norms = dict(NORMS)
        norms["caption_words"] = {"median": st.median(raw["fig"]),
                                  "p90": q(raw["fig"], .9), "hard": q(raw["fig"], .99)}
        norms["table_caption"] = {"median": st.median(raw["tab"]),
                                  "p90": q(raw["tab"], .9), "hard": q(raw["tab"], .99)}
        norms["sentence_words"] = {"median": st.median(raw["sent"]),
                                   "p90": q(raw["sent"], .9), "hard": 60}

    tex = "\n".join(open(f, encoding="utf-8", errors="replace").read()
                    for f in a.tex)

    caps = captions(tex)
    figs = [c for c in caps if c[0] == "Figure"]
    tabs = [c for c in caps if c[0] == "Table"]
    sents = sentences(tex)

    print("Applied Energy house style, measured\n")
    for label, items, key in (("figure captions", figs, "caption_words"),
                              ("table captions", tabs, "table_caption")):
        if not items:
            continue
        vals = [n for _, n, _ in items]
        n = norms[key]
        over = [(w, t) for _, w, t in items if w > n.get("hard", 1e9)]
        high = [(w, t) for _, w, t in items if n["p90"] < w <= n.get("hard", 1e9)]
        print(f"{label}: {len(vals)} of them, median {st.median(vals):.0f} words "
              f"against a corpus median of {n['median']:.0f} and p90 of {n['p90']:.0f}")
        for w, t in sorted(over, reverse=True)[:a.top]:
            print(f"   CUT   {w:>3}w  {t}...")
        for w, t in sorted(high, reverse=True)[:a.top]:
            print(f"   trim  {w:>3}w  {t}...")
        if not over and not high:
            print("   all inside the published range")
        print()

    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.S)
    if m:
        w = len(strip_tex(m.group(1)).split())
        n = norms["abstract_words"]
        flag = "ok" if n["p10"] <= w <= n["p90"] else "outside"
        print(f"abstract: {w} words, corpus {n['p10']}-{n['p90']} ({flag})\n")

    vals = [n for n, _ in sents]
    nn = norms["sentence_words"]
    longest = sorted(sents, reverse=True)[:a.top]
    print(f"sentences: {len(vals)} measured, median {st.median(vals):.0f} words "
          f"against a corpus median of {nn['median']:.0f}")
    for w, t in longest:
        if w > nn.get("hard", 60):
            print(f"   split {w:>3}w  {t}...")


if __name__ == "__main__":
    main()
