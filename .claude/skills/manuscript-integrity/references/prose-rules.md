# House prose rules

These are one author's preferences, tuned to suppress the register that makes technical
writing read as machine-generated. Adapt them. When a project states its own rules, those
win. What generalises is the method: count mechanically, and verify that a claimed
cleanup happened.

## Mechanical rules

Each is greppable, so each should be reported with an exact count and every location
rather than an impression.

**No em-dashes. No en-dash number ranges.** Write "48 to 343 hours", not "48–343". The
em-dash in particular is the single strongest tell of generated prose in technical writing.

```
grep -c $'—' *.tex      # em-dash
grep -c $'–' *.tex      # en-dash
grep -n -- "---" *.tex       # LaTeX em-dash
```

**No colon splices.** A colon must not join two independent clauses where a full stop
belongs. This is the most persistent violation in practice: it reads as authoritative, so
it survives revision, and it regenerates after being removed. One manuscript went from 35
to 86 between passes.

Legitimate uses remain: introducing a list, or a genuinely subordinate gloss. Judgement is
needed, so report borderline cases separately rather than inflating the count.

**Minimise "not X but Y".** Occasional use is fine. It becomes a tic, and when removed it
tends to return as "rather than" or the comma form "X, not Y". Count all three, or the
cleanup will look more successful than it was.

**Banned register.** Remove on sight: "it is worth noting", "delve", "tapestry",
"underscore", "testament to", "crucial", "pivotal", "leverage" as a verb (as a noun it is
fine), "landscape" and "navigate" as metaphors (literal uses are fine).

**No code or data identifiers in running prose.** File names, function names and enum
constants belong in tables, source attributions and reproduction guides, not in sentences.
Write "H2 Push", not `H2_PUSH`; "the levelised-cost routine", not `compute_lcoh`. Standard
dataset codes are fine anywhere.

**British spelling**, held consistently: -ise, "programme" for a plan, "modelling",
"labour". Watch for the same object named both ways in adjacent sentences, which is the
usual failure rather than outright American spelling.

**No dangling antecedents.** A "this" or "that" opening a sentence needs an unambiguous
referent. Chains of pronouns whose referent shifts mid-passage are the worst version.

## Judgement-based

**Paragraph length.** Over roughly 200 words, an argument becomes unfindable even when it
is correct. Dense is defensible; undivided is not.

**Repetition across sections.** The same explanation appearing in abstract, results,
discussion and conclusion is the commonest structural fault in a revised paper, because
each section was revised separately. State it fully once, where the evidence sits, and
refer back elsewhere. Report with locations and counts.

**Approximators.** "about", "approximately" and "roughly" doing one job between them, at
high density, reads as hedging. State the precision convention once, then drop most of
them.

**Epistemic virtue-signalling.** "and we state that plainly", "documented honestly",
"we do not claim otherwise". Each adds nothing after the plain statement it follows. The
honesty is demonstrated by the sentence, not by the annotation.

**Revision-history narration.** "Earlier drafts reported X. It is not." A reader has no
access to the earlier draft and cannot judge it. State the result. Keep an exception only
where the correction itself instructs, and attribute it to the method rather than to a
draft.

**Enumerative preambles.** "Two qualifications belong with...", repeated across a
document, is mechanical parallelism. Vary it, or start with the first item and let the
second follow.

**Inconsistent terminology.** One concept, one name. Count the variants: "best heat pump"
against "best available heat pump", "cost-optimal" against "least-cost".

## Two things that generalise past this list

**Count, don't impress.** A tic you removed once returns in substituted form. Only exact
counts across all variants reveal it.

**Verify the cleanup.** "We removed the colon splices" is a claim like any other. Check it.
