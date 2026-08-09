# Mechanics: figures, tables, formatting, front and back matter

Everything below the sentence level. Measured or observed directly from the 14-paper
corpus, with the two published figures and one table page examined page by page.

## Contents

1. Figure design
2. Table design
3. Figure and table captions, by panel count
4. Cross-reference style
5. Numbers, units and ranges
6. Spelling
7. Paragraph length
8. Citation density and reference count
9. Body length
10. Scenario and case naming
11. Appendices and supplementary material
12. Nomenclature and abbreviation lists
13. Keywords
14. Declarations and back matter
15. What the journal's own guide adds

---

## 1. Figure design

**Width.** Single-column for most charts; both columns only for maps, wide multi-panel
composites and anything with a geographic axis. A chart that would be legible in one
column is put in one column.

**Panel labelling has three accepted forms.** Examining nine papers page by page turned up
all three, so do not treat any one of them as the house rule:

| Form | Seen in |
|---|---|
| `(a)`, `(b)` centred **below** each panel | AE12 Fig. 6 |
| A descriptive **title above** each panel, e.g. *Electrolyzer*, *vRES*, *Hydrogen storage* | AE6 Fig. 7 |
| A bare letter in the panel's **top corner** | AE14 Fig. 5 |

What is not attested is leaving panels unlabelled. Where letters are used the caption
repeats the figure number with them, as `Fig. 6(a)` and `Fig. 6(b)`.

**Value labels on the marks.** Every bar in a stacked bar chart carries its value printed
on or above the segment, to two decimal places. The reader is not asked to read a value
off the axis. This is one of the clearest differences from a typical working-paper figure,
which relies on gridlines.

**Legends sit inside the plot area**, boxed, usually top-right, entries stacked
vertically. They are not placed below the figure or outside the axes.

**Axis labels carry units with a slash and no space before a bracket**:
`LCOHS($/kg)`, `Scale of hydrogen storage/kg`, `Grid carbon intensity (gCO2/kWh)`.

**Overlaid summary series.** A stacked bar chart that has a meaningful total draws that
total as a line with markers over the bars, and names it `Total` in the legend.

**Composite encodings are accepted.** Pie charts overlaid on a choropleth map, with
percentages annotated on the pies, appear without apology.

**Maps carry their full furniture.** AE3's Switzerland maps have a muted relief basemap, a
north arrow, a scale bar in kilometres, plant markers, and a boxed legend inside the frame.
AE14's Portuguese coastal maps put latitude and longitude on the axes, label the cities, and
give the excluded zones their own grey overlay with a legend entry. A bare choropleth with
no scale, no orientation and no place names is off-register.

**Colourbars belong to their panel and carry their unit.** A single map takes a vertical
colourbar at its right. Where two panels show the same quantity over different cases, each
still gets its own bar (AE14). Where a row of panels shares one scale, a single horizontal
bar runs beneath the row with the quantity named under it, e.g. *Factor*, 0.5 to 1.0 (AE6).

**Schematics are coloured, zoned and labelled.** AE2 and AE7 both enclose groups of boxes in
dashed regions with a heading over each region (*Flexible operation: 5%–150% load*,
*Full-load operation*, *Underground Reservoir*), fill the boxes in pastels, and colour each
arrow by what flows along it. Black-and-white box-and-arrow drawings do not appear. If a
process diagram is reading as texty, the fix is usually zones and colour rather than fewer
words.

**Colour.** Muted, low-saturation palettes: pale yellow, pale blue, mid blue, pale pink.
Saturated primaries read as a slide rather than a paper.

**Adapted figures are credited in the caption**: `(modified after [6])`.

**Exclusions are stated in the caption**: *Fractions lower than 1% are not shown in the
percentage distribution.*

## 2. Table design

The single most useful convention here, because it is what keeps captions short.

**Caption above the table**, in two lines: `Table 2` on its own line, then the caption
text beneath it.

**Units go in the column header**, never repeated in the cells: `Installed CAPEX in
2030 AUD`.

**Provenance moves into footnotes below the table**, keyed by superscripts on the cells they
explain. Letters and numbers are both attested, lettered in AE2 and numbered in AE7, so pick
one and hold it across the paper:

> ᵃ Refer to Table 1.
> ᵇ This value is based on the authors' calculation, utilising assumptions (1085
> AUD/tNH3 and 274 AUD/tNH3 in 2030 costs respectively for HB plant and ASU) from [30]
> and a 0.35%/yr reduction rate for mature technologies based on [121].
> ᶜ With this SF, the unit cost of LNH3 storage reported in [133] is by 20% less than
> ours.

**This is the fix for a bloated table caption.** A caption that has grown to 100 words is
usually carrying method, provenance and caveats that belong in lettered footnotes. Move
them down, and the caption returns to a naming line.

**Citations appear inside table cells**: *SF is based on [74]*.

**Cross-references to other tables appear inside cells**: *Refer to Table 2*.

**An en-dash marks not-applicable**, not `N/A` or a blank.

**Two narrow tables sit side by side**, one per column, when they are parallel.

## 3. Figure and table captions, by panel count

Caption length scales with panel count, which the aggregate median hides.

| Kind | Typical length | Example |
|---|---|---|
| Single-panel chart | **8 to 12 words** | *Fig. 8. Trend of LCOHS with storage scale in DGR.* |
| Table | **10 to 15 words** | *Table 2. Estimated CAPEX of main components involved in the ammonia pathway, SF, LR and OMEX.* |
| Multi-panel figure | **45 to 60 words** | *Fig. 6. Global LCOE figures for CapEx representative for present day in Fig. 6(a) and near future in Fig. 6(b). Under present-day cost assumptions, wave power is not included in the mix. … Pie charts show the distribution of energy sources. Fractions lower than 1% are not shown.* |

A series of parallel figures takes near-identical captions rather than varied wording:

> Fig. 8. Trend of LCOHS with storage scale in DGR.
> Fig. 9. Trend of LCOHS with storage scale in SC.
> Fig. 10. Trend of LCOHS with storage scale in LRC.

Resisting the urge to vary the phrasing is correct here. Parallel figures should read as
parallel.

## 4. Cross-reference style

Unambiguous in the corpus, and the asymmetry is easy to get wrong.

| Form | Uses | Rule |
|---|---|---|
| `Fig. 5` | 406 | **Always abbreviated**, even mid-sentence |
| `Figure 5` | 1 | Effectively never |
| `Figs. 6 and 7` | 7 | Plural takes `Figs.` |
| `Table 3` | 197 | **Never abbreviated** |
| `Tab. 3` | 0 | Never |
| `Eq. (7)` | 44 | **Always abbreviated, number in parentheses** |
| `Equation 7` | 0 | Never |
| `Section 3.1` | 80 | Spelled out |
| `Appendix B` | 20 | Spelled out, lettered |

So: `Fig.` abbreviates, `Table` does not, `Eq.` abbreviates and takes brackets.

## 5. Numbers, units and ranges

| Convention | Corpus | Rule |
|---|---|---|
| `25%` no space | 578 | **Dominant form** |
| `25 %` with space | 211 | Minority |
| `1,000` thousands comma | 403 | Use it |
| `5–10` en-dash range | 811 | **Dominant form** |
| `5-10` hyphen range | 197 | Minority |
| `45 °C` | 94 | Space before the degree sign |

Two further habits worth copying:

**The same quantity restated in a second unit**, so the reader never converts:
`15,000 m3/day (approximately 56 kg/hour or 1.3 tons/day)`.

**Percentages carrying their base**:
`95.7 % (15.5 % for drilling, 65.8 % for mining, and 14.4 % for lining)`.

## 6. Spelling

The corpus is mixed and leans American on the forms where the two differ:

| American | Uses | British | Uses |
|---|---|---|---|
| optimiz- | 178 | optimis- | 23 |
| levelized | 157 | levelised | 13 |
| utiliz- | 152 | utilis- | 36 |
| modeling | 79 | modelling | 32 |
| behavior | 33 | behaviour | 4 |

Counts for *analys-* and *characteris-* are not diagnostic, because *analysis* and
*characteristics* are spelled identically in both variants.

Elsevier accepts either provided it is consistent, so a British-spelling manuscript is
fine. Worth knowing only so that a British form is a deliberate choice rather than an
accident: *levelised* is the minority spelling in this journal by twelve to one.

## 7. Paragraph length

Measured over 191 body paragraphs: **median 3 sentences and 62 words**, with a p90 of 9
sentences and 259 words.

Applied Energy paragraphs are short. A draft whose paragraphs routinely run 8 to 12
sentences is carrying an essay's paragraph structure, where a paragraph develops an
argument, into a journal that uses a paragraph to deliver one point.

## 8. Citation density and reference count

| | Range | Median |
|---|---|---|
| Bracket citations per 1,000 body words | 3.7 to 22.4 | ~11.6 |
| Total references | 49 to 157 | ~81 |

The spread is wide because review-heavy introductions push density up. A density below
about 5 per 1,000 words reads as under-referenced for this journal.

## 9. Body length

Body text, introduction through conclusion, runs **8,000 to 12,200 words**, median about
10,000. That is longer than a strict reading of an 8,000-word guideline suggests, because
in practice tables, captions and references sit outside the count.

Worth knowing if a manuscript has been cut hard to hit a self-imposed cap: the published
corpus is not short.

## 10. Scenario and case naming

Two conventions, both common:

- **Coded**: `S1` through `S6`, defined once in a table. 253 uses.
- **Named, CamelCase**: `NoH2WasteHeat`, `OffshoreH2`, `Unconstrained`. 241 uses.

`Scenario 1` spelled out appears 8 times. `base case` (17) and `reference case` (3) are
the standard names for the central run.

## 11. Appendices and supplementary material

Appendices lettered `Appendix A`, `Appendix B` appear in 20 places and are **inside the
article**, carrying figures and tables the body points at. Separate supplementary material
is referenced 25 times. Both are used; the appendix is the more common home for a figure
the reader may want while reading.

Pointer style: *Further details on the implementation of the CSI support tool and the
corresponding exclusion layers are provided in [9] and Appendix C.*

## 12. Nomenclature and abbreviation lists

**Six of the fourteen carry one**, so it is optional and roughly a coin flip. Papers with
heavy symbolic notation include it; papers that are mostly acronyms often do not, relying
on define-on-first-use instead.

## 13. Keywords

Five per paper is typical, set as a stacked list rather than a semicolon-separated line,
each entry capitalised on the first word only:

> Green hydrogen
> Power-to-gas
> Sector coupling
> Renewable energy
> GIS

Acronyms appear as keywords in their own right (`GIS`), and the topic, method and
application each get one.

## 14. Declarations and back matter

The printed order at the end of an article: **CRediT authorship contribution statement →
Declaration of competing interest → Data availability → Acknowledgements → References**.

**CRediT** lists each author with their roles, roles separated by commas, the statement
run inline rather than as a list:

> Mostafa Rezaei: Writing – original draft, Visualization, Software, Methodology,
> Investigation, Conceptualization. Alexandr Akimov: Writing – review & editing,
> Conceptualization. Evan MacA. Gray: Writing – review & editing, Project administration,
> Conceptualization.

Note the en-dash in *Writing – original draft* and *Writing – review & editing*, and the
ampersand.

**Competing interest**, the standard wording, used verbatim:

> The authors declare that they have no known competing financial interests or personal
> relationships that could have appeared to influence the work reported in this paper.

**Data availability**, the shortest standard form:

> Data will be made available on request.

## 15. What the journal's own guide adds

The Applied Energy guide for authors could not be opened from this machine; the search
result carried these points, which should be confirmed at source before relying on them:

- Highlights are capped at **85 characters** each.
- **CRediT is submitted as a separate statement**, not only embedded in the manuscript,
  although published articles do print it.
- A competing-interest statement is required **even when there is nothing to declare**.
- Initial submission follows Elsevier's *Your Paper Your Way* policy: any reasonable
  layout a referee can read is accepted for the first round, with journal formatting
  requested only at the revision stage. This one is corroborated across several
  independent sources and is safe to rely on. Single column with double spacing is the
  conventional submission choice because it is what referees expect.

No explicit body word limit was found in the search. Given the corpus runs to a median of
about 10,000 words, treat any stricter self-imposed cap as a choice rather than a
requirement.

**The consequence for effort allocation.** Layout work before first submission is largely
wasted, because Elsevier's production team typesets the accepted manuscript into the
two-column article and authors never do it themselves. What production does **not** touch
is figure artwork, caption wording, or table content and footnotes, all of which reach
print exactly as supplied. So a table caption carrying 130 words of provenance, or an axis
label that becomes 5 pt at column width, is permanent. See `visual_review.md` §1 for the
full split.
