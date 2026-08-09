# How numbers go wrong

Every entry is a real failure from a manuscript that was under active, careful revision
with a working checker in place. Read this when a number is wrong and you want to know how
it got that way, or when deciding what a gate should cover.

The pattern across all of them: none was a careless typo. Each survived because it looked
like a correct number.

## Wrong population behind a right digit

A capital-payment range was reported as €31 to 69/kW-yr for eight months across eight
locations. Every digit traced to a real cell in a real CSV. The 69 was one country's
annualised capex, and that country built nothing, so it had no capital to recover and
could not be the top of a payment range. The correct range was €31 to 63.

The check that catches this is not "does the number appear in the data" but "is it taken
over the population this sentence is about". Ask that of every range.

**Gate implication.** Compute range endpoints in the check itself, filtered to the right
population, rather than hard-coding them.

## Adjective without a series

The prose said recovery "plateaus from the late 2030s rather than rising to the horizon"
and "peaks in the late 2030s". The only committed trajectory rose monotonically from 2037
to 2050, peaking at the final year and still climbing.

Shape words are claims. Check every one against the series.

## Explanation that restates an assumption

A flexibility bound was explained by saying the binding event was multi-day, so no
intra-day pre-heating could move load out of it. The event length was hard-coded at six
days. The explanation was a restatement of that constant, presented as a finding.

Sweeping the constant showed the bound was nearly invariant to it: what actually bound the
result was the share of load that could shift. The conclusion survived; the reasoning did
not.

**How to spot it.** When a passage explains an outcome by appealing to a parameter the
model fixes by hand, it is circular until that parameter is varied. Vary it. The sweep is
usually cheap and sometimes overturns the explanation while confirming the result, which
is a better paper than either alone.

## The fix that corrects to the wrong quantity

A heat-side peaker's annualised capital was stale at "51 to 69". It was corrected to
"51 to 66" — the *power* peaker's range, from a different asset with a different lifetime
and fixed-cost fraction. The heat-side figure was 52 to 73.

This is worse than leaving it stale, because it now looks checked.

**How to spot it.** When two similar quantities exist, establish which one the sentence is
about before correcting it. Name the distinguishing parameters in the check's `claim`
string so the next person cannot conflate them.

## Incomplete propagation

The recurring failure, and the one that produces the most rounds. A value lives in the
body, supplement, conclusion, abstract, cover letter, reproduction guide, README, and
sometimes a code comment. A fix reaches most of them.

Two specific variants:

**The suffix miss.** A replacement targeted `31 to 69/kW-yr`; one sentence read "against
31 to 69 for hydrogen" with no suffix, and survived. Search for the value, not the phrase.

**The tenth of a per cent.** A capacity-weighted figure moved 8.6 to 8.7. It reads as a
typo rather than a stale number, so it was corrected in one document and skipped in
another for two full rounds.

## Documents outside the corpus

A cover letter carried a wrong headline through two review rounds because the checker's
file list did not include it. It is the document an editor reads first.

Enumerate every document that could carry a number. Include READMEs and data-directory
indexes; one understated its own artefact, claiming a maximum of 8.9 per cent where the
committed CSV said 10.7.

## Cross-reference drift

Inserting a table renumbered three others, and four hard-coded pointers in a reproduction
guide silently began naming the wrong tables. The pointers still resolved, which is what
makes this worse than a stale value: the reader lands somewhere plausible.

Check pointers against the build's `.aux` file, not against your memory of the ordering.

## A figure with no artefact at all

Four values — a median, a range, and a before/after count — were quantified in the prose
and existed in no script and no CSV. They were model-derivable, so nobody had questioned
them, but no reader could regenerate them and no gate could check them.

When a figure traces to nothing: compute it, commit the computation, and let the prose
follow the script. If the script's output differs from what the prose carried, the script
wins.

## The check that deleted itself

Found while building a gate, not while writing a paper, and it is the subtlest entry here.

A checker worked out which documents were required to carry a headline value by searching
for that value in the documents. The set was derived from the corpus rather than declared.

So deleting the sentence from the cover letter also deleted the check that covered the
cover letter. The number vanished, the requirement vanished with it, and the run went
green. A gate built this way reports most confidently at the moment the claim disappears.

**How to avoid it.** Declare the required document set explicitly. Anything a check
derives from the material it is checking can be erased by editing that material, and a
self-referential check is worse than no check because it produces a green tick over a
hole.

The same reasoning applies to presence assertions generally: they are only meaningful if
the set of files that must contain the value is fixed independently of what those files
currently say.

## The guard that certified the error

The checker itself. It searched only for known-stale strings and used the correct value
solely to print. It was a blacklist: capable of detecting the recurrence of a known error,
blind to a new wrong value in the same slot. It reported "all gates pass" on a manuscript
whose central policy number was wrong in the results section.

See `gate-design.md`. The two-part fix is slot patterns plus presence assertions.

## Overstating what was verified

A completion report said "20 of 20 verified". The 20 checks had all run and all passed.
Four residues remained that no check covered.

The statement was true of the checks and false as a claim about the manuscript. Scope
every completeness claim to what was actually done. When someone later finds the
twenty-first residue, the difference between those two sentences is what determines
whether the earlier report was honest.
