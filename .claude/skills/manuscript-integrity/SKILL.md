---
name: manuscript-integrity
description: >
  Verify that every load-bearing number in a paper still traces to the artefact that
  produces it, run adversarial referee passes that check claims against model output
  rather than against the prose, and hold the writing to house style. Use this whenever
  someone is preparing, revising, checking, or refereeing a quantitative manuscript,
  thesis, working paper, or journal submission that sits on top of code and data
  (LaTeX, Word, or Markdown; any language). Trigger it for "check my paper's numbers",
  "review my manuscript", "get this ready for submission", "the model changed and I
  need to update the paper", "referee this", "did I propagate that fix everywhere",
  "score this like a reviewer would", and for any request to audit consistency across
  a paper, its supplementary information, and its reproduction guide. Reach for it too
  when a model or analysis has been re-run and the write-up needs to catch up, even if
  the person does not mention checking numbers.
---

# Manuscript integrity

## What this is for

A quantitative paper makes two kinds of claim. Some are arguments, which a careful reader
can evaluate by reading. The rest are assertions about what a model produced, and reading
cannot evaluate those at all. A referee who reads only the PDF will never discover that a
headline figure stopped matching its CSV three commits ago. Neither will a language model
asked to review the prose. The only way to know is to recompute the number and compare.

That gap is where real papers fail. Numbers go stale silently, they survive in the places
nobody re-reads, and they survive in the abstract because the abstract is written first
and revised least. The published tooling for LLM-assisted review almost universally reads
the paper text alone. This skill exists to work the other side: to treat every reported
number as a claim about an artefact, and to check it.

Three convictions run through everything below.

**Recompute, don't read.** A number is verified when it has been derived again from the
data, not when it has been found in the text and looks plausible.

**Assert the right answer, don't just forbid the wrong one.** A checker that greps for
known-bad strings can only catch the recurrence of an error someone already found. It
will certify a brand-new wrong value as correct.

**Fixing is where new errors enter.** Every correction is a chance to propagate
incompletely, or to replace a stale number with a number belonging to something else.
Re-verify after fixing, not just before.

## The workflow

Work in this order. Each phase assumes the one before it.

### Phase 1 — Build the artefact map

Before checking anything, establish what produces what. Find the scripts that write
results, the files they write, and the reproduction guide if one exists.

For each load-bearing number, record: the claim in words, the file and line where it
appears, the artefact it should come from, and how to recompute it. A number is
load-bearing if it appears in the abstract, in a conclusion, in more than one document,
or in a sentence a policy or engineering decision would rest on.

Do not try to check every number in the paper. Chasing a decimal in a footnote while the
abstract carries a wrong headline is the wrong allocation. Prioritise by blast radius.

### Phase 2 — Recompute and compare

Run the scripts. Read the CSVs. Derive each mapped number independently and compare it
with the prose.

Two failure modes deserve specific attention because they look like correct numbers.

**Scope errors.** A range is only as good as the population it is taken over. A capital
range whose maximum comes from a country that builds nothing is wrong even though every
digit traces to a real cell in a real CSV. Before accepting a range, ask what population
it is over and whether that is the population the sentence is about. This is the single
most common way a wrong number passes a naive check.

**Shape claims.** "It plateaus", "it peaks in the late 2030s", "it rises to the horizon"
are claims about a trajectory and need a trajectory to support them. If the only committed
series is monotonic, a plateau claim is not a rounding difference, it is unsupported.
Check any adjective applied to a series against the series.

### Phase 3 — Build or extend the gate

Manual checking does not survive contact with a second revision round. Encode the checks
so they run again.

Use `scripts/integrity_gate.py` as the engine. It handles the parts that are easy to get
wrong; read `references/gate-design.md` before extending it, because the design of this
kind of checker has non-obvious failure modes that have each cost a real round of review.

The short version of that reference:

- **Normalise before matching.** LaTeX wraps lines mid-phrase, writes `$280$~GW` where you
  expect `280~GW`, and uses `~` as a space that Python does not consider whitespace. A
  pattern written as a natural phrase will silently miss all three.
- **Match the slot, not the string.** Write a pattern that matches the shape of the claim
  and excludes only the correct answer, so `31 to 69`, `31 to 64` and every future variant
  fail alike. A literal known-bad string catches only what you have already seen.
- **Assert presence, not just absence.** Require the right value to appear somewhere, so a
  number that silently disappears also fails.
- **Include every document.** Cover letters, reproduction guides, READMEs and companion
  papers all carry headline numbers and are all routinely forgotten.

### Phase 4 — Referee passes

Run independent adversarial reads. `references/referee-passes.md` carries prompts for
three that have proven complementary: a numbers-and-argument referee scoped to the venue,
a structure-and-completeness referee, and a prose referee.

Give each referee the artefacts, not only the paper. A referee that can run the code finds
a different and more serious class of problem than one that cannot.

### Phase 5 — Verify each finding before acting on it

This is not optional and it is not a formality. Referee findings are hypotheses. Some are
wrong, and acting on a wrong finding introduces an error into a correct paper.

For each finding, derive the disputed quantity yourself. Then classify it:

- **Confirmed** — the artefact agrees with the referee. Fix it.
- **Refuted** — the artefact agrees with the paper. Do not fix it, and say so plainly in
  the report. A referee being wrong is information, not an embarrassment to bury.
- **Partly right** — common, and the most dangerous, because the obvious fix addresses the
  wrong half. Establish exactly which part holds before touching anything.

### Phase 6 — Fix, propagate, re-verify

Three disciplines, each learned by getting it wrong.

**Propagate completely.** A number lives in the body, the supplement, the conclusion, the
abstract, the cover letter, the reproduction guide, the README, and sometimes in a code
comment. Search for the value, not the sentence, and search every document.

**Fix to the right value, not merely to a different one.** When two similar quantities
exist, a correction can land on the wrong one and look finished. If a paper has both a
power-sector peaker and a heat-sector peaker with different lifetimes, their capital
ranges differ, and correcting one to the other's value is worse than leaving it stale,
because it now looks checked.

**Re-run the gate after fixing.** Then re-read the sentences you changed, in context. A
number can be right and the sentence around it wrong.

### Phase 7 — Report honestly

State what was checked, what was found, what was fixed, and what was left. Scope every
claim of completeness to what was actually done: "20 of 20 mapped checks pass" is true and
useful; "the manuscript is verified" is neither, and the difference matters when someone
later finds the twenty-first.

Name your own errors in the report, including ones introduced while fixing. A correction
log that hides its own mistakes teaches nobody anything.

## Prose

`references/prose-rules.md` carries the house rules. The defaults there suppress the
register that makes technical writing read as machine-generated: em-dashes, colon splices,
the "not X but Y" tic and its substitutes, stock intensifiers, and code identifiers leaking
into running text.

Adapt them to the author. These are one set of preferences, not a universal standard, and
the point is consistency with a chosen voice rather than compliance with this particular
list. When a project states its own rules, those win.

Two things generalise regardless of house style. Count mechanically rather than by
impression, because a tic you have removed once tends to return in a substituted form
and only counting reveals it. And check that a claimed cleanup actually happened, since
"we removed the colon splices" is itself a claim worth verifying.

## Bundled resources

| Path | Read when |
|---|---|
| `scripts/integrity_gate.py` | Building or extending the checker. Runnable; `--help` explains the check format. |
| `references/gate-design.md` | Before extending the gate. Failure modes of this kind of checker, each of which has cost a review round. |
| `references/referee-passes.md` | Setting up referee agents. Three complementary prompts plus guidance on scoping them to a venue. |
| `references/prose-rules.md` | Running the language pass. House rules with the reasoning behind each. |
| `references/failure-catalogue.md` | When a number is wrong and you want to know how it got that way, or when deciding what to add to the gate. |

## What this skill does not do

It does not judge whether a paper's argument is any good, whether the contribution is
novel, or whether a venue will accept it. Those need a referee with domain knowledge, and
the referee passes here are a supplement to that judgement rather than a replacement.

It also cannot verify a number whose artefact does not exist. When a figure traces to
nothing, the honest options are to compute it and commit the computation, or to remove the
claim. Leaving it in place while describing the paper as checked is the failure this skill
is built to prevent.
