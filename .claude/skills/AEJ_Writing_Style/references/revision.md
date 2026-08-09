# The response to reviewers

## Provenance, stated up front

A response letter is not a published artefact, so **nothing in this file comes from the
fourteen-paper corpus in the way the rest of the skill does.** It has two sources, kept
separate below.

**Process conventions** come from search-result summaries of Elsevier and Applied Energy
author guidance. The primary pages were unreachable from this machine:
`sciencedirect.com/journal/applied-energy/publish/guide-for-authors` and
`elsevier.com/researcher/...` both returned HTTP 403. Treat the process section as a
sensible default to confirm against the journal's own page, not as verified requirement.

**Wording** comes from the corpus, and this part is solid. A reply to an Applied Energy
referee should sound like an Applied Energy paper, and the corpus already tells us exactly
how this journal concedes a point, explains a difference and justifies an assumption. Those
constructions are attested and are reused here.

## Process, unverified

Reported conventions, consistent across sources:

- The revision goes back through Editorial Manager with a **point-by-point response**
  uploaded as its own file, alongside the revised manuscript and a marked-up copy.
- **Each reviewer comment is quoted in full**, set in bold or otherwise distinguished, with
  the reply beneath it. Numbering follows the reviewer's own, under a heading per reviewer.
- **Every reply ends with a location**: page and line number of the change, and the figure or
  table number where one was added or redrawn.
- A major revision normally **returns to the original reviewers**, so the reply is read by
  the person who wrote the comment, next to the text that is supposed to answer it.
- If the requested work will not fit the deadline, **ask the editorial office before the
  deadline** rather than after.

One point recurs and is worth taking seriously even though it is unverified: the fastest way
to turn a major revision into a rejection is tone. Applied Energy referees are domain
specialists. A reply that argues rather than answers is read as a refusal to revise.

## Wording, from the corpus

Four moves cover almost every reply. All four already exist in the corpus, doing the same
work inside published articles.

### Move 1. The comment is right, and the change is made

Open with the change, not with agreement. State what was done, where, and what it altered.

Corpus grammar to reuse: the plain past-tense report of a modelling action, which is the
methods section's own voice.

> The heat demand series has been recomputed on the revised degree-day basis and the
> comparison is now reported in Section 3.2 (p. 11, lines 214 to 229) and in the new Fig. 5.
> The regional ordering is unchanged; the central value moves from X to Y.

**Always say whether the conclusion moved.** A referee's first question after any recomputation
is whether the headline survived it. Answering it unprompted is worth more than any amount
of thanks.

### Move 2. The comment is right, and the change cannot be made

This is the concession reversal from `stance.md` §5, used verbatim in its published form. Name
the limitation, name the **direction of the bias**, then state what the choice buys.

The corpus sentence to model on:

> This discrepancy is primarily due to the assumption of horizontal panel orientation without
> tilt-angle optimization, **which is expected to underestimate PV capacity factors relative to
> optimally tilted systems but avoids overestimating performance given the uncertain impact**
> of wave-induced motions on OFPV systems [34].

Adapted:

> A multi-year weather sample is beyond what the present model can carry, and the single year
> used here **will understate inter-annual variation in peak heat demand, which biases the
> comparison against the electrified pathway rather than in its favour.** The assumption is
> now stated in Section 2.3 (p. 7, line 130) and in the limitations (p. 24, lines 501 to 508).

The bias direction is the load-bearing clause. A referee who can see that the simplification
runs against the paper's own conclusion has no reason to press further. If the bias runs
*towards* the conclusion, say that too, and quantify it, because that is the case where a
sensitivity run is the only real answer.

The corpus's closing form for a block of limitations transfers directly:

> **Despite these limitations, the adopted assumptions are necessary to** keep the optimisation
> tractable at NUTS3 resolution.

### Move 3. The comment rests on a misreading

Restate what the paper claims, then say what has been changed so the misreading cannot recur.
Never say the reviewer misread.

The corpus's own clarifying construction, from AE4:

> For this, **it is crucial to understand that** the overall electrolysis efficiency, which
> ultimately determines hydrogen output, **differs from** stack efficiency, also known as DC
> efficiency.

Adapted:

> The reported figure is the delivered cost of heat at the dwelling, which differs from the
> production cost at the plant gate by the distribution and conversion terms in Eq. (4). The
> distinction was implicit and is now stated explicitly at first use (p. 9, line 172), and the
> axis label in Fig. 4 has been changed to *delivered cost of heat*.

The tell of a good reply of this kind is that it ends in a change. A reply that only explains
invites the same comment from the next referee.

### Move 4. The comment is wrong

The corpus's single instance of contradicting a published claim is the model, and its
restraint is the point:

> **Musa et al. report a lower LCOH of USD$1.99/kg, a difference primarily attributable to the
> substantial economies of scale in their larger model.**

Subject is the difference. Cause is a named modelling choice. No adjective on anyone's work.
The same shape answers a referee:

> The value in [12] is lower at X €/MWh. The difference is primarily attributable to the
> assumption of Y per cent network utilisation there, against Z per cent here, which is the
> figure reported by [source] for the regions modelled. Both values and the source of the
> divergence are now given in Section 4.3 (p. 19, lines 388 to 396).

**Show the arithmetic and let it settle the point.** The corpus never adjudicates a
disagreement in words; it explains it with a mechanism and moves on. Where a comment turns on
a number, recompute it and report the recomputation rather than restating the original claim.

And where the referee is simply right and the paper was wrong, say so in one clause and fix
it. `stance.md` §6 notes that `we attribute`, `at odds with` and `disagree` appear zero times
in fourteen papers. That vocabulary does not belong in the reply either.

## Register for the letter

Everything in `stance.md` §3 applies. Confidence is carried by the modal verb. There is no
adverb layer, so no *arguably*, no *we believe*, no *it seems*. `can` for a demonstrated
capability, `could` for a projection, `may` for an untested possibility, and nothing weaker
than that.

Three further constraints, all following from the corpus rather than from etiquette:

- **No verdict adjectives**, on the comment or on the paper. The corpus does not call results
  *excellent* or concerns *valid*. It reports.
- **Numbers, not assurances.** *The ordering is unchanged in 218 of 234 regions* answers a
  robustness comment; *the results are robust* does not.
- **The same number everywhere.** `restatement.md` applies to the letter too. A value quoted in
  the reply must match the revised manuscript digit for digit, with the same qualifying
  condition. A reply that quotes a stale number is the one thing certain to cost a further round.
