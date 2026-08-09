#!/usr/bin/env python3
"""Measure the house style of a corpus of published papers, so the advice is evidence.

Style guidance written from impression is worth little. Everyone "knows" journal
captions are terse, and nobody knows by how much, so nobody can tell whether a given
draft is inside or outside the norm. This reads the extracted text of published
articles and reports distributions for the signals that actually separate a journal
manuscript from a working paper.

Two-column PDFs need care. pdftotext -layout preserves the physical line, so one line
can hold the left column's caption and the right column's table body. Lines are split
on runs of four or more spaces and each chunk measured separately, which keeps a
caption from swallowing its neighbour.

Run:  python measure_corpus.py <dir-of-txt-files>
Out:  a table per signal, plus corpus_measurements.json beside the directory.
"""
from __future__ import annotations
import json
import os
import re
import statistics as st
import sys
from collections import Counter

GUTTER = re.compile(r"\s{4,}")
FIGCAP = re.compile(r"^(?:Fig\.|Figure)\s*(\d+)\s*[.:]\s+([A-Z(‘\"].{10,})$")
TABTAG = re.compile(r"^Table\s+(\d+)\.?$")
TABCAP = re.compile(r"^Table\s+(\d+)\s*[.:]\s+([A-Z(].{10,})$")
HEADING = re.compile(r"^(\d+)\.\s+([A-Z][A-Za-z][A-Za-z \-,/&]{2,55})$")
SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z(])")


def chunks(line: str):
    """The physical line, split at column gutters."""
    return [c.strip() for c in GUTTER.split(line) if c.strip()]


def measure(text: str) -> dict:
    lines = text.split("\n")
    figs, tabs, heads = [], [], []

    for i, raw in enumerate(lines):
        for c in chunks(raw):
            m = FIGCAP.match(c)
            if m:
                # A caption may wrap; keep taking the same column until it stops.
                body = [m.group(2)]
                for nxt in lines[i + 1:i + 8]:
                    nc = chunks(nxt)
                    if not nc or FIGCAP.match(nc[0]) or TABTAG.match(nc[0]):
                        break
                    if len(nc[0]) < 12 or nc[0][0].isupper() and body[-1].endswith("."):
                        break
                    body.append(nc[0])
                n = len(" ".join(body).split())
                if 3 <= n <= 200:
                    figs.append(n)
                continue

            m = TABCAP.match(c) or TABTAG.match(c)
            if m:
                # "Table N" alone: the caption is the line below, in the same column.
                body = [] if m.re is TABTAG else [m.group(2)]
                for nxt in lines[i + 1:i + 6]:
                    nc = chunks(nxt)
                    if not nc:
                        break
                    cand = nc[0]
                    # A tabular body line is wide-spaced or mostly digits; stop there.
                    if len(GUTTER.split(nxt.strip())) > 2:
                        break
                    if sum(ch.isdigit() for ch in cand) / max(len(cand), 1) > 0.2:
                        break
                    body.append(cand)
                    if cand.endswith("."):
                        break
                n = len(" ".join(body).split())
                if 3 <= n <= 200:
                    tabs.append(n)
                continue

            m = HEADING.match(c)
            if m and int(m.group(1)) <= 12:
                heads.append((int(m.group(1)), m.group(2).strip()))

    m = re.search(r"\n\s*1\.\s+Introduction\b", text)
    body = text[m.end():] if m else text
    body = re.split(r"\n\s*(?:References|Data availability)\s*\n", body)[0]
    sents = []
    for s in SENT.split(body):
        s = " ".join(s.split())
        n = len(s.split())
        if 4 <= n <= 80 and sum(ch.isdigit() for ch in s) / max(len(s), 1) < 0.2:
            sents.append(n)

    a = re.search(r"\bA\s?B\s?S\s?T\s?R\s?A\s?C\s?T\b(.{200,4000}?)"
                  r"(?:\n\s*\n|\bKeywords\b)", text, re.S | re.I)
    fp = len(re.findall(r"\b(we|our|us)\b", body, re.I))
    return {
        "abstract_words": len(a.group(1).split()) if a else None,
        "figure_captions": figs,
        "table_captions": tabs,
        "sentences": sents,
        "headings": heads,
        "first_person_per_1000": round(1000 * fp / max(len(body.split()), 1), 2),
    }


def line(name, vals, unit=""):
    if not vals:
        return f"  {name:<26} no data"
    v = sorted(vals)
    q = lambda p: v[min(int(p * len(v)), len(v) - 1)]
    return (f"  {name:<26} n={len(v):<5} median {st.median(v):>5.0f}{unit}   "
            f"p10 {q(.10):>4.0f}   p90 {q(.90):>4.0f}")


def main():
    d = sys.argv[1]
    files = sorted(f for f in os.listdir(d) if f.endswith(".txt"))
    per, agg = {}, {k: [] for k in
                    ("abstract", "fig", "tab", "sent", "fp", "nfig", "ntab")}
    heads = Counter()
    for fn in files:
        r = measure(open(os.path.join(d, fn), encoding="utf-8",
                         errors="replace").read())
        per[fn] = r
        if r["abstract_words"]:
            agg["abstract"].append(r["abstract_words"])
        agg["fig"] += r["figure_captions"]
        agg["tab"] += r["table_captions"]
        agg["sent"] += r["sentences"]
        agg["fp"].append(r["first_person_per_1000"])
        agg["nfig"].append(len(r["figure_captions"]))
        agg["ntab"].append(len(r["table_captions"]))
        for _, h in r["headings"]:
            heads[h.lower().rstrip(".")] += 1

    print(f"corpus: {len(files)} papers\n")
    print(line("abstract, words", agg["abstract"]))
    print(line("figure caption, words", agg["fig"]))
    print(line("table caption, words", agg["tab"]))
    print(line("sentence, words", agg["sent"]))
    print(line("figures per paper", agg["nfig"]))
    print(line("tables per paper", agg["ntab"]))
    print(line("we/our/us per 1000w", agg["fp"]))
    print("\nsection headings, by frequency:")
    for h, n in heads.most_common(20):
        print(f"  {n:>3}  {h}")

    out = os.path.join(os.path.dirname(os.path.abspath(d)), "corpus_measurements.json")
    json.dump({"n_papers": len(files), "aggregate": agg,
               "headings": heads.most_common(30), "per_paper": per},
              open(out, "w"), indent=1)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
