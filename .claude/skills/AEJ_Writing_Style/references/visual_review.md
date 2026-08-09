# Looking at the pages

Everything else in this skill was derived by reading extracted text. Text extraction is
blind to the thing an editor notices in two seconds: what the page looks like. A caption
of 55 words is a number until you see it sitting five lines deep under a figure that
occupies a third of the page, and then it is obviously wrong.

This section is the procedure for looking, and what fourteen published pages look like
when you do.

## Contents

1. Why the submission PDF cannot be judged by eye
2. Rendering pages for review
3. What the corpus's pages look like
4. The checklist
5. What only the render catches

---

## 1. Why the submission PDF cannot be judged by eye

**First, the thing not to do.** Do not try to make the submission look like the published
article. Under Elsevier's *Your Paper Your Way* policy the initial submission may be in any
reasonable layout a referee can read, and single column with double spacing is the
conventional choice because it is what referees expect. Journal formatting is requested
only at the revision stage, and the two-column article is produced by Elsevier's own
production team from the accepted manuscript. Authors never typeset it.

So an elsarticle `[review]` build, single column, double spaced, 12 pt, wide margins, is
**correct as a submission** and should stay that way. Reformatting it to two columns before
first submission is wasted effort, and it makes the manuscript harder to referee.

**Now the thing that does transfer.** Production re-typesets the text. It does not redraw
your figures, rewrite your captions, or shorten your table captions. Artwork is placed at
the width the layout gives it and scaled to fit. So:

| Under your control, permanently | Handled by production |
|---|---|
| What the figure contains, its fonts, its palette, its legend | Where the figure lands on the page |
| Caption wording and length | Column widths, margins, line spacing |
| Table content, structure, footnotes | Table typesetting and rule weights |
| Whether an axis label is legible at 3.5 inches | Page breaks and float placement |

That is the whole reason for the visual pass. A five-line caption stays five lines. A table
caption carrying 130 words of provenance stays that way. An axis label set at 5 pt in a
figure scaled to column width is 5 pt in print, and nobody at Elsevier will notice or fix it.

**Consequence.** Render the **submission PDF** and judge everything in the left-hand column
of that table from it: caption length, table structure, what each figure contains, whether it
earns its place.

That leaves one question the submission PDF cannot answer, because it is single column and
the article is not: **will the smallest text in this figure still be readable at a two-column
width?** Do not rebuild the manuscript to find out. Two cheaper answers, in order of
preference.

**Compute it.** `\includegraphics[width=f\textwidth]` scales a figure by its width alone, so
a label set at *p* points in the generator prints at

    p × f × (column width in inches) / (figure's native width in inches)

Applied Energy's column is about 3.4 inches. A figure drawn on a 10 inch canvas with 9 pt
labels, included at full column width, prints those labels at 3.1 pt. This is arithmetic,
not judgement, and it is how a set of figures ships with 3.5 pt text while looking perfectly
fine in the PNG the author inspected. Hold a **6 pt floor**. Better still, assert the floor
inside the figure generator, so a figure cannot be built that violates it.

**Or look at the one figure, not the document.** Render or export the single figure at 3.4
inches wide and open it. That answers the same question in one command and does not touch the
manuscript.

A two-column rebuild answers this too, but it is the most expensive way to get there and it
introduces a second document to keep in sync. Skip it.

**One trap in the review format itself.** A review page is roughly 60 to 70 per cent white
where a published page is nearly full. Do not read anything into that. Balance, density,
where floats landed and whether a page is half empty are all production's, and the review
format makes them misleading anyway. Judge content, not proportion.

## 2. Rendering pages for review

`pdftoppm` ships with poppler and is already present wherever `pdftotext` is.

**Whole-structure pass**, low resolution, so a page fits in one view and you are looking at
shape rather than words:

    pdftoppm -png -r 55 -f 1 -l 12 main.pdf out/page

**Detail pass** on one figure or table, high enough to read the axis labels:

    pdftoppm -png -r 150 -f 22 -l 22 main.pdf out/fig4

**Legibility at column width**, which is the one thing the submission PDF cannot show. Do
the arithmetic in §1, or render the single figure at 3.4 inches and open it. Do not rebuild
the manuscript in two columns for this.

`scripts/render_pages.py` wraps the first two and prints what it wrote.

Then **read the images**. Not the caption text, the image. The whole point is to use the
eye rather than the word count.

## 3. What the corpus's pages look like

Observed by rendering and examining roughly forty pages from AE1, AE2, AE3, AE5, AE6, AE7,
AE12, AE13 and AE14.

**Pages are full.** Text runs to the bottom of both columns. There is no decorative white
space anywhere, and a half-empty page does not occur except at the end of the article.

**But the density is not relentless.** AE13 page 10 is roughly 85 per cent prose with one
small table at the foot of a column. A results section does not need a figure on every page,
and a paper that manufactures one is padding.

**Figures fill their measure.** A single-column figure runs the full column width, edge to
edge. A full-width figure runs the full text width. Nothing is centred at 70 per cent with
margins either side. If a chart does not deserve the full width, it is made single-column,
not shrunk.

**Figures cluster and text wraps around them.** AE5 page 11 carries four figures: one
full-width at the top, two side by side beneath it, a short text block, then a fourth in
the right column. The text is wedged into what is left. This is the opposite of the LaTeX
default habit of pushing every float to the top or bottom of its own page, and it is worth
forcing, because it is what makes the results section feel evidence-dense.

**Full-width figures sit at the top or the bottom of a page**, never floated into the
middle of a two-column spread. AE12's world map sits at the page foot with its caption
beneath it and two columns of text above.

**Captions are visually short.** Under a full-width map, one line. Under a single-column
bar chart, one line. A caption that wraps past two lines is a caption doing work that
belongs in the table footnotes or the body. The exception earns it: AE6's five-line caption
has to explain a three-panel layout and a continuous colour mapping, and there is no shorter
way to do that.

**Panels are always identified, in one of three ways.** Letters below (AE12), a descriptive
title above (AE6), or a bare letter in the panel's top corner (AE14). All three are in
register. Unlabelled panels are not.

**Colourbars belong to their panel.** Two maps of the same quantity still get a bar each
(AE14). A row of panels sharing one scale gets a single horizontal bar beneath the row with
the quantity named under it (AE6).

**Maps carry their furniture.** AE3's Switzerland maps have a relief basemap, north arrow,
scale bar in kilometres, plant markers and a boxed legend inside the frame. AE14's put
latitude and longitude on the axes, name the cities, and give the exclusion zones a legend
entry of their own.

**Wide tables span both columns at the page top**, and the table font is visibly smaller
than the body font. Applied Energy shrinks tables to fit rather than splitting or rotating
them.

**Narrow tables sit side by side**, one per column, when they are parallel. AE2 page 9 puts
Table 2 and Table 3 next to each other, both with footnotes underneath, and the body text
resumes below both. Footnote markers are lettered in AE2 and numbered in AE7; either is
fine, held consistently.

**Tables have horizontal rules only**, three of them: above the header, below the header,
and at the foot. No vertical rules anywhere, and no grid.

**Schematics use pastel fills, coloured arrows and labelled zones.** AE2 and AE7 both enclose
groups of boxes in dashed regions with a heading over each region (*Flexible operation:
5%–150% load*, *Full-load operation*, *Underground Reservoir*), and colour each arrow by what
flows along it. They are not black-and-white box-and-arrow drawings. When a process diagram
is criticised as too texty, the fix in this journal is zones and colour, not fewer words.

**Equations are in-column**, numbered at the right edge of their own column, and long
expressions are broken to fit the column rather than spanning the page.

**The first page is a fixed piece of furniture**: journal banner, title full width, authors
with superscript affiliation markers, affiliations in small italic, a ruled HIGHLIGHTS box
of four or five one-line bullets, then a two-part band with keywords stacked in a narrow
left column and the abstract as one justified block on the right, then the body begins in
two columns. Everything else in the article is arranged around that.

## 4. The checklist

Run through this with the rendered pages open, not the source.

**Every figure**

- Does it fill its column or the full text width? If it is floating with margins either
  side, either widen it or make it single-column.
- Read the smallest text in the image at 100 per cent. If it is not comfortably readable,
  it will be under 6 pt in print.
- Is the legend inside the plot area and boxed? Outside or below is off-register.
- Does every bar or point carry its value? The corpus does not make the reader read values
  off an axis.
- Does a stacked chart with a meaningful total draw the total as a line over the bars?
- Is the axis unit written the corpus way, `(€/MWh)` or `LCOH/kWh`, rather than with a
  superscript minus one?
- Is the palette muted? Saturated primaries read as a slide, not a paper.
- Are the panels identified, by letters below, titles above, or letters in the corner?
- If it is a map: relief or context basemap, north arrow, scale bar, place names, boxed
  legend, and a legend entry for any excluded or masked area?
- If it has a colourbar: does each panel have its own, or does a shared row have one bar
  beneath it with the quantity named?
- If it is a schematic: are the boxes filled with pastels, the streams coloured by content,
  and the functional groups enclosed in labelled zones?

**Every caption**

- Count the rendered lines, not the words. One line for a single-panel figure, two at the
  outside. Anything longer is method or provenance that belongs elsewhere.
- Under a multi-panel figure, longer is correct, up to about four lines.

**Every table**

- Horizontal rules only, three of them.
- Units in the header, not repeated in cells.
- Provenance in lettered footnotes below, not in the caption.
- Does it fit the column, or does it need to span both? Decide deliberately rather than
  letting it overflow.

**The document as a whole**

- Scroll the low-resolution renders quickly, as a flick-through. Where does the eye stop?
  A page that is all text with no figure for four pages running is where a reader
  disengages, and it is visible instantly at this zoom.
- Are figures spread through the results, or clumped at the end because the floats drifted?
- Do the section headings fall at sensible intervals, or is one section four pages of
  unbroken prose?

Do not add "is any page half empty" to this list. Float placement and page density belong
to production, and the review format's whiteness tells you nothing about the printed
article.

## 5. What only the render catches

These are the defects that survive every text-level check in this skill and are obvious the
moment a page is looked at.

| Defect | Why text extraction misses it |
|---|---|
| A figure floating at 70 per cent width with white margins | The `\includegraphics` width is a number that looks fine in source |
| Axis text below 6 pt at print size | Depends on the figure's native size and its scale factor together |
| A five-line caption under a small figure | Word count alone does not give the ratio |
| A legend colliding with the tallest bar | Nothing in the source says where the legend landed |
| An orphaned figure on a page of its own | Float placement is decided at typeset time |
| A table that overflows the column | The source compiles; the box just sticks out |
| Two figures on one page whose fonts differ | Each figure is individually fine |
| Inconsistent palettes between figures | Each script sets its own colours |
| A caption on the wrong side of a table | The source has `\caption` in the right place; the class puts it elsewhere |
| Panel labels in the corner rather than centred below | The corpus convention is invisible in any word count |

**The rule this section exists to enforce.** Before declaring a manuscript finished, render
it and look at it. Every other check in this skill reads the source. A referee and an editor
look at pages, and the first impression is formed before a single sentence is read.
