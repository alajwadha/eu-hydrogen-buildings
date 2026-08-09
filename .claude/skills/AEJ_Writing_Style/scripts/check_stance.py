#!/usr/bin/env python3
"""Flag stance problems: verdicts, recommendations, hedging and marker balance.

check_manuscript.py measures lengths. This measures position. Every rule here comes from
a count over the 14-paper corpus, and each report line names the corpus figure it is
judged against so a deliberate departure stays possible.

Run:  python check_stance.py <main.tex> [more.tex ...]
      python check_stance.py <main.tex> --section conclusion
"""
from __future__ import annotations
import argparse
import re
import statistics as st
import sys

# --- corpus counts, from paper/style_corpus (14 published AE articles) ----------------

# Verdict vocabulary the corpus does not use in its own voice. The corpus states an
# unfavourable result as a comparison in positive grammar: "is lower than ... but ...".
VERDICTS = [
    (r"\bnot (?:economically )?viable\b",        "0 uses"),
    (r"\bnon-?viable\b",                         "0 uses"),
    (r"\bunviable\b",                            "0 uses"),
    (r"\beconomically unattractive\b",           "0 uses"),
    (r"\bleast promising\b",                     "0 uses"),
    (r"\bfails? to (?:be|compete|deliver|justify|achieve|reach)\b", "1 use, of a demand not met"),
    (r"\bcannot compete\b",                      "0 uses"),
    (r"\brules? out\b",                          "0 uses"),
    (r"\bdoes not capture\b",                    "0 uses"),
    (r"\bthe worst\b",                           "1 use"),
    (r"\bunfortunately\b",                       "0 uses"),
]

# Direct recommendations. The corpus grants a capability instead: "enabling policymakers
# to evaluate ...", "policymakers can identify ...".
RECOMMEND = [
    (r"\bwe recommend\b",                        "0 uses"),
    (r"\bit is recommended\b",                   "2 uses"),
    (r"\bgovernments? should\b",                 "0 uses"),
    (r"\bpolicy ?makers? should\b",              "0 uses"),
    (r"\bpolicymakers? should\b",                "0 uses"),
    (r"\bshould (?:therefore )?(?:prioriti|fund|subsidi|mandate|ban|redirect)", "0 uses"),
    (r"\bwe (?:argue|urge|advocate|call for)\b", "0 uses"),
]

# Epistemic adverbs. Confidence is carried by the modal verb; there is no adverb layer.
ADVERBS = [
    (r"\barguably\b",       "0 uses"),
    (r"\bpresumably\b",     "1 use"),
    (r"\bconceivably\b",    "0 uses"),
    (r"\bappears? to\b",    "0 uses"),
    (r"\bseems? to\b",      "1 use"),
    (r"\bwe believe\b",     "0 uses"),
    (r"\bto some extent\b", "0 uses"),
    (r"\bsomewhat\b",       "rare"),
]

# Intensifier synonyms. The corpus does not avoid intensifiers, it standardises on
# 'significantly' (85) and uses the alternatives rarely. Convert rather than delete.
INTENSIFIERS = [
    (r"\bdramatically\b",  "3 uses"),
    (r"\bmarkedly\b",      "3 uses"),
    (r"\bconsiderably\b",  "3 uses"),
    (r"\bgreatly\b",       "6 uses"),
    (r"\bsubstantially\b", "14 uses"),
    (r"\bvastly\b",        "0 uses"),
    (r"\benormously\b",    "0 uses"),
    (r"\bhugely\b",        "0 uses"),
]

# Disagreement framed by the author rather than by the mechanism.
DISPUTE = [
    (r"\bwe attribute\b",   "0 uses"),
    (r"\bat odds with\b",   "0 uses"),
    (r"\bwe disagree\b",    "0 uses"),
    (r"\bincorrectly\b",    "0 uses"),
    (r"\boverestimates?\b(?!.{0,40}\bour\b)", "used, but always with the mechanism named"),
]

# Discourse markers, corpus counts. Ratios matter more than absolutes.
MARKERS = {
    "However,": 135, "While": 53, "Although": 40, "In contrast,": 28,
    "Conversely,": 18, "Nevertheless,": 15, "Despite": 15, "Nonetheless,": 8,
    "On the other hand": 6, "Yet ": 1,
    "Additionally,": 52, "Furthermore,": 43, "Moreover,": 33, "Finally,": 24,
    "Notably,": 24, "In addition,": 19, "Overall,": 15, "Specifically,": 11,
    "Importantly,": 3,
}

SENT_MEDIAN, SENT_P10, SENT_P90 = 24, 11, 43

# Short sentences the corpus does permit, by job.
SHORT_OK = re.compile(
    r"(organi[sz]ed as follows|is validated|statistically significant|"
    r"as follows|are summari[sz]ed|achieves? lifecycle|is defined as)", re.I)


def strip_tex(s: str) -> str:
    s = re.sub(r"\\begin\{(figure|table|equation|align|tabular|lstlisting)\}"
               r".*?\\end\{\1\}", " ", s, flags=re.S)
    s = re.sub(r"%.*", "", s)
    s = re.sub(r"\\(?:label|ref|eqref|cite[tp]?|nocite)\s*\{[^}]*\}", "", s)
    s = re.sub(r"\\[a-zA-Z]+\*?\s*", " ", s)
    s = s.replace("~", " ").replace("{", "").replace("}", "").replace("$", "")
    return " ".join(s.split())


def hits(text: str, table):
    out = []
    for pat, note in table:
        for m in re.finditer(pat, text, re.I):
            a = max(0, m.start() - 55)
            out.append((m.group(0), note, text[a:m.end() + 55].strip()))
    return out


def report(title, found, advice):
    print(f"\n{title}")
    if not found:
        print("   nothing found")
        return 0
    for word, note, ctx in found:
        print(f"   {word!r}  (corpus: {note})")
        print(f"      ...{ctx}...")
    print(f"   -> {advice}")
    return len(found)


def conclusion_of(text: str) -> str:
    """Text from the conclusion heading to the next \\section, not a fixed window.

    A fixed character window runs past the end of the section and, when several files
    are concatenated, into a different file entirely, which reports another section's
    first person as the conclusion's.
    """
    m = re.search(r"\\section\*?\{[^}]*(?:Conclusion|Concluding)[^}]*\}", text, re.I)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = re.search(r"\\section\*?\{", rest)
    return rest[:nxt.start()] if nxt else rest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tex", nargs="+")
    ap.add_argument("--top", type=int, default=6)
    a = ap.parse_args()

    raw = "\n".join(open(f, encoding="utf-8", errors="replace").read() for f in a.tex)
    concl_raw = conclusion_of(raw)
    text = strip_tex(raw)

    total = 0
    print("Stance check against 14 published Applied Energy articles")

    total += report(
        "1. Verdict vocabulary",
        hits(text, VERDICTS),
        "state the unfavourable result as a comparison in positive grammar, with the "
        "mechanism named. stance.md §1")

    total += report(
        "2. Direct recommendations",
        hits(text, RECOMMEND),
        "convert to an enabling clause: 'the results allow a national programme to "
        "identify ...'. stance.md §2")

    total += report(
        "3. Epistemic adverbs",
        hits(text, ADVERBS),
        "delete the adverb and set confidence with the modal verb alone. stance.md §3")

    total += report(
        "4. Author-framed disagreement",
        hits(text, DISPUTE),
        "make the difference the subject and a named modelling choice the cause. "
        "stance.md §6")

    total += report(
        "4b. Off-register intensifiers",
        hits(text, INTENSIFIERS),
        "the corpus standardises on 'significantly' (85 uses). Convert rather than "
        "delete, and keep the number that justifies it in the same sentence. "
        "wording.md §7")

    # 5. first person in the conclusion
    print("\n5. First person in the conclusion")
    if not concl_raw:
        print("   no conclusion section found")
    else:
        c = strip_tex(concl_raw)
        we = re.findall(r"\b(?:we|our|us)\b", c, re.I)
        print(f"   {len(we)} first-person words in {len(c.split())} words "
              f"(13 of 14 corpus conclusions have none; length 470 to 620 words)")
        if we:
            print("   -> switch the subject to 'this study' / 'the results'. stance.md §4")
            total += len(we)

    # 6. discourse-marker balance
    print("\n6. Discourse markers")
    counts = {k: len(re.findall(re.escape(k), text)) for k in MARKERS}
    used = {k: v for k, v in counts.items() if v}
    total_markers = sum(counts.values())
    words = max(len(text.split()), 1)
    # Corpus: 486 markers over roughly 188,000 body words, so about 2.6 per 1,000.
    rate = 1000 * total_markers / words
    print(f"   {total_markers} markers in {words} words ({rate:.1f} per 1,000; "
          f"corpus 2.6 per 1,000)")
    for k, v in sorted(used.items(), key=lambda x: -x[1])[:12]:
        print(f"   {k:<20} {v:>3}   corpus {MARKERS[k]}")
    if rate < 1.0:
        print("   -> under-signposted. The corpus never leaves a contrast implicit; "
              "where two clauses qualify each other, 'However,' is present. "
              "wording.md §17")
        total += 1
    if counts.get("Moreover,", 0) > counts.get("Additionally,", 0):
        print("   -> corpus prefers 'Additionally,' (52) over 'Moreover,' (33)")
    for rare in ("Importantly,", "Yet ", "On the other hand"):
        if counts.get(rare, 0) > 2:
            print(f"   -> {rare.strip()!r} is near-absent in the corpus "
                  f"({MARKERS[rare]} uses); repeat 'However,' instead")

    # 7. sentence rhythm. Drop the back matter without swallowing anything that
    # follows it in a later file, which a greedy '.*' would do.
    body = re.sub(r"\\section\*?\{[^}]*(?:Reference|Acknowledg|Declaration|CRediT)[^}]*\}"
                  r"(?:(?!\\section).)*", " ", raw, flags=re.S | re.I)
    body = re.sub(r"\\bibliography\{[^}]*\}", " ", body)
    sents = [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(])", strip_tex(body))
             if 3 <= len(s.split()) <= 150]
    if sents:
        L = [len(s.split()) for s in sents]
        print("\n7. Sentence rhythm")
        print(f"   {len(L)} sentences, median {st.median(L):.0f} words "
              f"(corpus median {SENT_MEDIAN}, p10 {SENT_P10}, p90 {SENT_P90})")
        med = st.median(L)
        if med > SENT_P90 * 0.75:
            print(f"   -> median sits well above the corpus median of {SENT_MEDIAN}; "
                  "sentences are carrying more than one claim each")
            total += 1
        rhet = [s for n, s in zip(L, sents)
                if n < SENT_P10 and not SHORT_OK.search(s)]
        pct = 100 * len(rhet) / len(L)
        # The corpus's short sentences are 11% of the total, and nearly all of them do a
        # structural job. The filter above is crude, so 11% is used as a conservative
        # ceiling rather than a target.
        print(f"   {len(rhet)} sentences under {SENT_P10} words with no structural job "
              f"({pct:.0f}%; the corpus is 11% short overall, nearly all structural)")
        for s in rhet[:a.top]:
            print(f"      join to a neighbour: {s}")
        if pct > 11:
            print("   -> the corpus does not alternate long and short for rhythm, so "
                  "short sentences here are doing rhetorical work. wording.md §16")
            total += 1

    print(f"\n{total} stance flags in total")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
