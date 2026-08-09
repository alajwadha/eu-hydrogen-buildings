# Designing a numbers gate that actually holds

Read this before extending `scripts/integrity_gate.py`. Every failure mode below was
found by a referee after the gate had reported a clean pass, which is the specific
embarrassment this file exists to prevent.

## The architectural mistake

The natural first design is: keep a list of values known to be wrong, grep for them, pass
when none are found.

That design cannot work, and it fails in a way that is worse than having no gate. It is a
blacklist. It detects the recurrence of an error someone has already found, and nothing
else. A brand-new wrong value in a checked slot passes silently, and now it passes with a
green tick beside it, so the next reader trusts it more than they would have without the
gate at all.

The fix has two halves, and both are needed.

**Match the slot, not the string.** Write the pattern to match the shape of the claim and
exclude only the correct answer. `31 to 69` and `31 to 64` and every future variant then
fail alike:

```python
slot("31 to ", "63", guard="kW-yr|hydrogen")
```

**Assert presence.** Require the correct value to appear somewhere. This catches the case
the slot pattern cannot see: a number that quietly disappears, or a sentence rewritten
around a claim until the claim is gone.

## Normalisation: three holes, found one at a time

Each of these was discovered separately, after a patch for the previous one had shipped.
They are listed in the order they bit.

**Line wrapping.** LaTeX and Markdown source wraps around column 80. A phrase written
naturally as `from 8.6 to about 51` sits in the file as `from 8.6 to about\n51`. The
pattern misses it. Every whitespace run must collapse to a single space before matching.

**Math delimiters.** Prose puts numbers in math mode. `$280$~GW` reads to a human as
`280~GW` and to a regex as a different string. Strip `$` before matching.

**Ties.** `~` is a non-breaking space in LaTeX. `32~per cent` and `32~per~cent` are the
same sentence and different strings, and a document will contain both. Python does not
consider `~` whitespace, so it survives a naive whitespace collapse. Normalise it too.

Because normalisation destroys offsets, keep a map from each normalised position back to
its source line, or the gate will report hits a human cannot locate. `normalise()` returns
that map for exactly this reason.

## Scope your patterns or drown in false positives

A bare numeric shape collides with unrelated text. `31 to ` matched `1.31 to 1.33` in a
price table, because the boundary between `.` and `3` is a word boundary.

Two defences, both in `slot()`. Refuse a match that starts mid-number with `(?<![\d.])`.
And require a nearby context word with `guard`, so a payment check only fires near
`kW-yr` or `hydrogen`.

A false positive is not harmless. It trains whoever runs the gate to skim its output, and
a skimmed gate is a decoration.

## What to include in the corpus

Every document that could carry the number. In practice this means more than people
expect:

- the paper body and its section files
- the supplementary information
- the abstract and front matter, including any duplicate copy kept for a Word twin
- the cover letter
- the reproduction guide or README
- any companion or longer version of the paper
- data-directory READMEs, which routinely quote headline results

A cover letter omitted from the corpus carried a wrong headline through two review rounds.
It is the document an editor reads first.

## Cross-reference drift

Inserting a table or figure renumbers everything after it, and hard-coded pointers in
prose or a reproduction guide silently begin naming the wrong object. This is worse than a
stale value, because the pointer still resolves and sends the reader somewhere plausible.

Check pointers against the build's own `.aux` file rather than against your memory of the
ordering. LaTeX resolves the labels; read what it resolved.

## Choosing what to check

Not everything. A gate over every number is unmaintainable and will be disabled. Add a
check when a number is:

- in the abstract, the conclusions, or a highlight
- repeated across more than one document
- load-bearing for a decision the paper recommends
- newly corrected, because a number that has gone stale once tends to do it again

When you add a check, add the pattern for the error you just fixed as well as the slot
pattern. The specific historical error is cheap to encode and confirms the check works.

## Prove the gate catches what you think

After adding a check, verify it. Break the value deliberately, confirm the gate fails,
restore. This takes a minute and is the only way to know a pattern matches the text as
typeset rather than the text as you imagined it.

Two of the three normalisation holes above would have been caught immediately by this
habit. Neither was, because the patterns looked obviously correct.
