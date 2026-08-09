# Corpus signals, measured

Measured from 14 published Applied Energy techno-economic articles supplied
by the co-author, using `scripts/measure_corpus.py` on `pdftotext -layout` output.
Re-derive with that script rather than trusting these numbers if the corpus changes.

## Aggregate

| Signal | n | p10 | median | p90 | max |
|---|---|---|---|---|---|
| Figure caption, words | 154 | 7 | 20 | 64 | 137 |
| Table caption, words | 81 | 5 | 11 | 27 | 42 |
| Sentence, words | 6103 | 8 | 21 | 49 | 80 |
| Figures per paper | 14 | 6 | 10 | 16 | 16 |
| Tables per paper | 14 | 2 | 6 | 11 | 13 |
| we/our/us per 1,000 words | 14 | 0 | 1 | 5 | 5 |
| Abstract, words | 10 | 231 | 271 | 329 | 329 |

## Extraction caveats

Honest limits on the numbers above, so they are not over-read.

- **Abstracts.** 14 papers, but 4 extracted at under 150 words (46, 47, 59, 66), which is a two-column extraction failure rather than a genuinely short abstract. The median above uses only the 10 that extracted cleanly.
- **Captions.** Physical lines in a two-column PDF hold both columns, so the script splits on four-or-more-space gutters and measures each chunk separately. A caption that wraps oddly can still be truncated or extended by a line.
- **Sentences.** Reference lists and tabular fragments are excluded, as is anything more than 20 per cent digits, which removes most table debris but not all.

## Section headings across the corpus

| Heading | Papers using it |
|---|---|
| introduction | 13 |
| conclusions | 6 |
| methodology | 5 |
| results | 5 |
| results and discussion | 4 |
| conclusion | 4 |
| discussion | 4 |
| results and discussions | 2 |
| methods | 2 |
| analysis and results | 2 |
| pathways description | 1 |
| system modeling | 1 |
| model application using national-level data | 1 |
| method | 1 |
| study regions and meteorological data | 1 |
| study area, case study configuration, and datasets | 1 |

## Per paper

| Paper | Abstract | Figs | Median fig caption | Tables | Median tab caption | Median sentence |
|---|---|---|---|---|---|---|
| AE1 | 272 | 6 | 11 | 9 | 9 | 18 |
| AE2 | 270 | 13 | 16 | 6 | 14 | 17 |
| AE3 | 272 | 10 | 47 | 2 | 20 | 18 |
| AE4 | 245 | 14 | 36 | 4 | 17 | 17 |
| AE5 | 47* | 16 | 8 | 5 | 10 | 20 |
| AE6 | 280 | 8 | 34 | 3 | 25 | 24 |
| AE7 | 228 | 6 | 45 | 9 | 7 | 23 |
| AE8 | 231 | 14 | 10 | 6 | 10 | 29 |
| AE9 | 329 | 16 | 16 | 13 | 7 | 25 |
| AE10 | 46* | 14 | 52 | 11 | 8 | 20 |
| AE11 | 66* | 11 | 14 | 3 | 13 | 27 |
| AE12 | 249 | 9 | 26 | 2 | 40 | 19 |
| AE13 | 59* | 8 | 23 | 6 | 16 | 22 |
| AE14 | 307 | 9 | 35 | 2 | 24 | 24 |

`*` extraction failure, excluded from the aggregate.

## The manuscript this was built for

Measured the same way, for scale:

| Signal | This manuscript | Corpus median | Ratio |
|---|---|---|---|
| Figure caption | 65 words | 20 | 3.2x |
| Table caption | 138 words | 11 | 12.5x |
| Sentence | 29 words | 21 | 1.4x |
| Abstract | 250 words | 271 | inside range |

The captions, not the prose, are what made it read as a report.
