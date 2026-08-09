#!/usr/bin/env python3
"""Check a manuscript's load-bearing numbers against the artefacts that produce them.

WHY THIS EXISTS

A paper that sits on top of code makes assertions about what that code produced. Those
assertions rot: a model is re-run, most of the prose is updated, and a handful of values
survive in the places nobody re-reads. Reading the paper cannot find them, because a
stale number looks exactly like a fresh one.

This module is the checking engine. You supply the checks (see CHECK FORMAT below); it
supplies the parts that are easy to get wrong and that have each, in practice, let a wrong
number through a review round:

  1. Source normalisation, so a pattern written as a natural phrase matches text that
     LaTeX has wrapped, put in math mode, or spaced with a tie.
  2. Presence assertions, so the gate verifies the right answer is there rather than only
     that a known-wrong answer is absent.
  3. Line-accurate reporting despite that normalisation, so a hit is still something a
     human can open and read.

CHECK FORMAT

A check is a dataclass with five fields:

    Check(
        claim   = "standing capacity payment, EUR/kW-yr",
        value   = "31 to 63",              # what the artefact says, for the report
        stale   = [r"\\b31 to (?!63\\b)\\d+"],  # patterns that must NOT appear
        files   = [Path(...), ...],        # every document that could carry it
        present = r"31 to 63",             # optional: must appear at least once
    )

`stale` patterns are matched against the NORMALISED text, so write them with plain single
spaces and without `$`. `present` is optional but strongly worth setting on anything
load-bearing, because it is what turns the gate from a blacklist into a whitelist.

Run `python integrity_gate.py --demo` to see a worked example, or import `run_checks`.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Check:
    """One claim, the value its artefact produces, and how it can go wrong."""
    claim: str
    value: object
    stale: list = field(default_factory=list)
    files: list = field(default_factory=list)
    present: str | None = None


def normalise(text: str) -> tuple[str, list[int]]:
    """Flatten source so a pattern written as one phrase matches the text as typeset.

    Three transformations, each closing a hole that let a stale number survive a full
    sweep in a real manuscript:

      Line wrapping. LaTeX and Markdown wrap at roughly column 80, so a phrase like
      "from 8.6 to about 51" sits in the file as "from 8.6 to about\\n51". A regex written
      the natural way misses it. Every whitespace run collapses to a single space.

      Math delimiters. Prose writes numbers in math mode, so `$280$~GW` is the same
      sentence to a reader as `280~GW` and a different string to a regex. `$` is dropped.

      Ties. `~` is a non-breaking space in LaTeX but is not whitespace to Python, so
      `32~per cent` and `32~per~cent` differ as strings while reading identically. `~` is
      normalised to a space.

    Returns the flattened text alongside a map from each flattened offset back to its
    source line, so a hit still reports a line a human can open. Without that map the
    normalisation would trade one kind of blindness for another.
    """
    out: list[str] = []
    lines: list[int] = []
    line = 1
    prev_space = False
    for ch in text:
        if ch == "\n":
            line += 1
        if ch == "$":                       # math delimiter, never part of a phrase
            continue
        if ch.isspace() or ch == "~":       # `~` is a LaTeX space, not a character
            if prev_space:
                continue
            out.append(" ")
            lines.append(line)
            prev_space = True
        else:
            out.append(ch)
            lines.append(line)
            prev_space = False
    return "".join(out), lines


def slot(prefix: str, correct: str, suffix: str = r"\d+", guard: str | None = None) -> str:
    """Build a pattern matching the SHAPE of a claim, excluding only the right answer.

    A literal known-bad pattern can only catch the recurrence of an error someone already
    found; it is blind to a new wrong value in the same slot. A slot pattern inverts that:
    it matches the claim's shape and excludes the correct answer, so every wrong variant
    fails alike.

        slot("31 to ", "63")            -> matches "31 to 69", "31 to 64", not "31 to 63"

    `guard` narrows the match to a context, which matters because a bare numeric shape
    will collide with unrelated text. Requiring "kW-yr" or "hydrogen" within the next few
    dozen characters stops "1.31 to 1.33" in a price table from tripping a payment check.

        slot("31 to ", "63", guard="kW-yr|hydrogen")

    The leading (?<![\\d.]) stops a match starting mid-number, which is how "1.31 to 1.33"
    would otherwise register as "31 to 1".
    """
    pat = rf"(?<![\d.]){re.escape(prefix)}(?!{re.escape(correct)}\b){suffix}"
    if guard:
        pat += rf"(?=.{{0,45}}?(?:{guard}))"
    return pat


def run_checks(checks: list[Check], repo_root: Path | None = None) -> int:
    """Run every check and print a report. Returns the number that failed.

    A check fails if any stale pattern matches, or if a `present` pattern is set and
    nothing matches it. Both directions matter: the first catches a wrong value, the
    second catches a right value that has gone missing.
    """
    corpus: dict[Path, tuple[str, list[int]]] = {}
    for c in checks:
        for f in c.files:
            if f not in corpus and Path(f).exists():
                corpus[f] = normalise(Path(f).read_text(encoding="utf-8", errors="replace"))

    def rel(p: Path) -> str:
        try:
            return str(Path(p).relative_to(repo_root)) if repo_root else str(p)
        except ValueError:
            return str(p)

    failed = []
    print("Manuscript numbers against their artefacts\n")
    for c in checks:
        hits, missing = [], None
        for f in c.files:
            text, linemap = corpus.get(f, ("", []))
            for pat in c.stale:
                for m in re.finditer(pat, text):
                    ln = linemap[m.start()] if m.start() < len(linemap) else 0
                    hits.append(f"{rel(f)}:{ln}  {m.group(0)!r}")
        if c.present and not any(
            re.search(c.present, corpus.get(f, ("", []))[0]) for f in c.files
        ):
            missing = c.present

        ok = not hits and not missing
        print(f"  [{'ok ' if ok else 'FAIL'}] {c.claim:44s} artefact = {c.value}")
        for h in hits:
            print(f"           stale:  {h}")
        if missing:
            print(f"           absent: nothing matches {missing!r}; "
                  f"the correct value is asserted nowhere")
        if not ok:
            failed.append(c.claim)

    print()
    if failed:
        print(f"{len(failed)} claim(s) disagree with the artefacts that produce them:")
        for name in failed:
            print(f"  - {name}")
    else:
        print(f"All {len(checks)} checked claims match the artefacts that produce them.")
    return len(failed)


def _demo() -> int:
    """Show the engine catching each of the failure modes it was built for."""
    import tempfile

    sample = (
        "The standing payment is \\euro{}31 to 69/kW-yr across the winning markets.\n"
        "The firm fleet reaches $280$~GW, about 32~per cent of the 889~GW peak, and\n"
        "recovery climbs from 8.6 to about\n51~per~cent once scarcity is priced.\n"
        "Prices in the islands run 1.31 to 1.33 times the hub.\n"
    )
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "results.tex"
        f.write_text(sample)
        checks = [
            Check("standing payment, EUR/kW-yr", "31 to 63",
                  [slot("31 to ", "63", guard="kW-yr|hydrogen")], [f], present=r"31 to 63"),
            Check("firm fleet, GW", 278, [slot("", "278", r"28[01] GW")], [f]),
            Check("fleet share of peak, %", 31, [r"\b32 per cent of the 889"], [f]),
            Check("capacity-weighted recovery, %", 8.7, [r"from 8\.6 to about 51"], [f]),
        ]
        print("DEMO. The sample text carries four errors, each of a kind that has\n"
              "survived a real review round. Note that the price range '1.31 to 1.33'\n"
              "is correctly NOT flagged, and that line numbers survive normalisation.\n")
        n = run_checks(checks, repo_root=Path(d))
        print(f"\nExpected 4 failures, got {n}.")
        return 0 if n == 4 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", action="store_true",
                    help="run a worked example showing each failure mode being caught")
    args = ap.parse_args()
    if args.demo:
        return _demo()
    ap.print_help()
    print("\nImport `Check`, `slot` and `run_checks` and define checks for your project.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
