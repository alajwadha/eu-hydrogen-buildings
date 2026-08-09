#!/usr/bin/env bash
# Build the v9 Word document: a natively-styled Word document. pandoc renders the LaTeX source onto a Word
# style template authored in make_ref_docx.py (the agreed Oxford look: serif body, justified,
# bold numbered-style headings, centred title, A4, footer page numbers), the citations are
# rendered through citeproc into a real author-year reference list, figures embed as their PNG
# twins, and every table is then set to full text-width. Editable Word equations are preserved.
# Run: cd paper && bash build_docx.sh
set -euo pipefail
cd "$(dirname "$0")"
PANDOC="$(command -v pandoc || true)"; [ -z "$PANDOC" ] && PANDOC="$HOME/AppData/Local/Pandoc/pandoc.exe"
[ -x "$PANDOC" ] || { echo "pandoc not found"; exit 1; }

# 1. style template: pandoc default reference doc, retuned to the Oxford look
"$PANDOC" --print-default-data-file reference.docx > _ref_v8.docx
python make_ref_docx.py

# 2. stage the source; swap figure PDFs for PNG twins (Word cannot show PDF images); fix date
BUILD=_build_v8; rm -rf "$BUILD" && mkdir -p "$BUILD/sections"
cp Paper_v20.tex "$BUILD/main.tex"; cp sections/*.tex "$BUILD/sections/"
sed -i '/includegraphics/ s/\.pdf}/.png}/g' "$BUILD/main.tex" "$BUILD"/sections/*.tex
sed -i 's/\\today/June 2026/g' "$BUILD/main.tex"

# 2-0. neutralise siunitx S[table-format=...] columns in the staged tables. pandoc's LaTeX reader
#      cannot parse an S column spec, so it silently DROPS the caption of any tabularx that uses
#      one (the bottom-up validation table, tab:bottomup), leaving that table un-captioned in Word
#      while the PDF is fine. Rewrite each S[...] column to a plain right-aligned r in the staged
#      copies only; the data cells are plain numbers and render identically. Real source untouched.
sed -i -E 's/S\[table-format=[^]]*\]/r/g' "$BUILD"/sections/*.tex

# 2-1. convert glued chemical/unit subscripts (CO$_2$, H$_2$, MtCO$_2$, EUR$_{2024}$) from math
#       mode to \textsubscript in the staged copies. pandoc renders a standalone "$_2$" subscript
#       as an OMML math object whose base is an empty zero-width space, so in Word the "2" floats
#       detached from the preceding letter (e.g. "CO" then a stray subscript), and inside a caption
#       it also broke the plain-text flow. \textsubscript renders as a normal subscript run in Word
#       and is visually identical in the PDF. Only the isolated "$_2$" / "$_{NNNN}$" spans glued to a
#       letter or digit are rewritten; multi-symbol math like $\eta_{\mathrm{g}}$ is left untouched.
sed -i -E 's/\$_2\$/\\textsubscript{2}/g; s/\$_\{([0-9]+)\}\$/\\textsubscript{\1}/g' "$BUILD/main.tex" "$BUILD"/sections/*.tex

# 2a. demote \paragraph{...} run-in lead-ins to bold inline text for the Word build only.
#     pandoc maps \paragraph to a Heading 4 and --number-sections then stamps it with a deep
#     "X.Y.0.1" number (e.g. "1.0.0.1 Three contributions."), which the PDF never shows because
#     there \paragraph is an unnumbered bold run-in. We rewrite it to \noindent\textbf{...} in the
#     staged copies so the Word output matches the PDF's bold lead-in. The real source is untouched.
#     The lead-in is followed by a non-breaking space (~), not \quad: pandoc drops \quad AND swallows
#     the following inter-word space, so the bold lead-in glued straight onto the body text in Word
#     (e.g. "Method.For each"). A trailing ~ renders as a real space in the Word output; any existing
#     whitespace after the closing brace is consumed first so no double space is produced.
sed -i -E 's/\\paragraph\{([^}]*)\}[[:space:]]*/\\noindent\\textbf{\1}~/g' "$BUILD/main.tex" "$BUILD"/sections/*.tex

# 2b. resolve \ref/\eqref cross-references to their literal numbers from Paper_v20.aux.
#     pandoc renders main.tex without a LaTeX .aux, so \ref{...} otherwise leaks the raw
#     label (e.g. "[sec:rq]") into the Word output. We substitute the authoritative number
#     LaTeX itself assigned (read from the compiled .aux), so the Word cross-references match
#     the PDF exactly. Requires a fresh Paper_v20.aux (run pdflatex before this script).
python resolve_refs_docx.py Paper_v20.aux "$BUILD/main.tex" "$BUILD"/sections/*.tex

# Mark numbered equations so the Word pass can set the number beside them.
python mark_equations.py Paper_v20.aux "$BUILD/main.tex" "$BUILD"/sections/*.tex

# 3. render onto the template
( cd "$BUILD" && "$PANDOC" main.tex -o ../_v8_raw.docx \
    --reference-doc=../_ref_v8.docx --citeproc --bibliography=../References_v1.bib \
    --csl=../ieee.csl --resource-path="../figs" \
    --figure-caption-position=above --table-caption-position=above \
    --number-sections )      # IEEE numbered citations + numbered headings (1, 4, 4.6, 4.6.1) to match the PDF
                             # caption-position=above: pandoc otherwise drops the figure/table caption BELOW
                             # the float in Word (the PDF has it above via \caption before \includegraphics)
rm -rf "$BUILD"

# 4. full-width tables, then clean up the scratch template
python fix_docx_tables.py _v8_raw.docx Paper_v20.docx && rm -f _v8_raw.docx _ref_v8.docx
# 4a. restore the "Figure N: " / "Table N: " label pandoc drops from every caption, using the
#     authoritative numbers from Paper_v20.aux (matched to each caption by its text).
python number_captions.py Paper_v20.aux Paper_v20.docx
python title_page.py Paper_v20.docx

# Live Word numbering: SEQ on captions, REF on cross-references, and numbered
# equations in the borderless-table idiom. Static text renumbers wrongly the
# moment a float is inserted; a field recomputes.
python apply_fields.py Paper_v20.docx            # clean native title page (replaces pandoc's split block)
echo "wrote paper/Paper_v20.docx"
