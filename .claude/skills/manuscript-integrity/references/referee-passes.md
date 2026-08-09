# Referee passes

Three independent reads, run in parallel. They are complementary rather than redundant:
each has found things the others missed, and combining them into one referee reliably
produces a shallower review of all three dimensions.

## What makes these different from a normal LLM review

Give every referee access to the code and the model outputs, not only the paper. A referee
that can run the analysis finds a different class of problem from one that reads a PDF,
and it is the more serious class. The single most valuable instruction in all three
prompts below is the one telling the referee to spot-check numbers against artefacts.

Two framing rules matter as much as the prompts.

**Ask for file:line.** A finding without a location cannot be verified and will cost more
time to chase than it saves.

**Require unconfirmed findings to be labelled.** A referee that cannot check something
should say so rather than assert it. Reviews that mix confirmed and speculative findings
without marking which is which force the whole review to be re-verified from scratch.

## Pass 1 — Numbers and argument

Scope to the venue. A journal referee and a working-paper referee reach different verdicts
on the same document, and conflating them produces advice that fits neither.

```
You are an experienced referee for [VENUE]. Score out of 10 on that venue's standards.
Be a hard marker: state what each band means so the score is interpretable.

The manuscript: [paths to body, supplement, figures]
The model: [path to code]  The outputs: [path to results]
The reproduction guide: [path], which maps each headline claim to the script producing it.

Your task, in priority order:

1. NUMBER AUDIT. Spot-check at least fifteen load-bearing numbers against the committed
   outputs. Do not take the prose at its word. Report every mismatch as
   file:line | prose says X | artefact says Y | source. A number that traces to no
   artefact at all is the most serious finding you can make; flag it as such.
2. Internal consistency. The same quantity must carry the same value everywhere,
   including figure captions, table cells and appendices. [State any set identities or
   near-identical quantities that have been confused before.]
3. Argument and evidence. Does each conclusion follow from what was computed? Flag
   overclaiming, and any limitation acknowledged in an appendix but not where the claim
   is made.
4. What is missing, weak, or would not survive a determined reader.

Deliver: a score with a one-paragraph justification and a recommendation; MAJOR findings
numbered M1..; MINOR findings numbered m1..; each with file:line and a concrete fix; and a
consolidated table of every number mismatch.

Verify before asserting. Label anything you could not confirm as unconfirmed rather than
stating it as a finding. Do not edit files.
```

## Pass 2 — Structure and completeness

Most useful on long documents, and on the second and later versions of anything, where the
characteristic failure is a correction that landed in one place and not the three others.

```
Audit [document] for structure and completeness. Another referee is checking the numbers;
concentrate on what is missing, misplaced, or internally contradictory.

Look for:
- A claim corrected in one location and left stale in another. Search for the VALUE, not
  the sentence. Check the abstract, conclusions, supplement, cover letter and any
  companion document.
- Explanations that restate an assumption as though it were a result. If a passage
  explains an outcome by appealing to a parameter the model fixes by hand, the
  explanation is circular until that parameter is varied. Name any you find.
- Robustness tests that exist as artefacts in the repository but are absent from the
  document, or present in one version and not another.
- Claims about the SHAPE of a series (plateaus, peaks, converges) with no series behind
  them.
- Sections promising material that is not delivered, and cross-references pointing at the
  wrong object.

Report each with file:line and a concrete fix. Say explicitly which claims you verified
and which you could not.
```

## Pass 3 — Prose

Keep this separate. A referee asked to judge both substance and style does neither well,
and prose findings are cheap to verify mechanically, so precision is achievable here in a
way it is not elsewhere.

```
Audit the prose of [documents]. Ignore whether the numbers are right; another pass covers
that.

Apply the house rules in [prose-rules.md or the project's own]. For every mechanical rule,
give an exact count and every file:line, using grep rather than impression, because a tic
removed once tends to return in a substituted form that only counting reveals.

Also report, as ordinary prose problems: sentences long enough to lose the thread;
paragraphs over roughly 200 words; the same point made more than once across sections,
with locations and counts; hedging stacked on hedging; mechanical parallelism and
enumerative preambles used as a tic; inconsistent terminology for one concept; and
headings that misdescribe what follows.

Deliver: a table of mechanical violations with counts and locations; judgement-based
findings ordered by how much they hurt the reading, each with a quoted offender and a
concrete rewrite; an overall score with justification; and the ten worst passages, quoted,
with rewrites.
```

## Re-running after fixes

On the second round, tell each referee what changed and ask it to verify the claimed fixes
rather than assume them. Referees are good at catching a fix that was announced but not
made, and that specific failure has recurred often enough to be worth prompting for
directly:

```
You previously raised [N] findings. The authors claim to have addressed them:
[list each claim]
VERIFY each against the files; do not take it on trust. State which hold and which do not,
with file:line. Then look for anything new, including errors introduced while fixing.
```

That last clause earns its place. A fix round reliably introduces at least one new error,
most often by correcting a value to one belonging to a similar but distinct quantity.

## Handling what comes back

Treat every finding as a hypothesis until you have derived the quantity yourself. In
practice a minority of findings do not survive checking, and acting on those damages a
correct paper. Classify each as confirmed, refuted, or partly right, and report the
refuted ones rather than quietly dropping them.
