# V5 submission set

**Upload the files in this folder.** They are copies of `V5.pdf`, `V5.docx`, `SI.pdf`
and the wide graphical abstract, which is what the build and the gates produce. The parent
copies are authoritative.

They are no longer refreshed by hand. This folder once held a full revision's stale copy of
the manuscript: a corrected number reached every LaTeX source, both compiled PDFs and both
papers, and these four files kept the old value, because every gate read the LaTeX corpus
and these are renderings. `package_v5.py` refreshes them from the built deliverables and
`check_submission.py` fails if they differ, so the two cannot drift again. Run the build,
then `python3 package_v5.py`, then the gate.

| File | What it is |
|---|---|
| `Hydrogen_residential_heating_V5.pdf` | Main manuscript, elsarticle `[review]`: single column, double spaced |
| `Hydrogen_residential_heating_V5.docx` | The same manuscript, written natively as Word |
| `Hydrogen_residential_heating_SI_V5.pdf` | Supplementary Information |
| `Hydrogen_residential_heating_graphical_abstract_V5.png` | Graphical abstract, 3984 x 1593 px, a separate Editorial Manager upload |

## The Word file is native, and matches the PDF

Not a print-to-Word. Counted in the built file: 143 OMML math objects, 11 `SEQ` counter fields on captions and equation numbers, and 17 `REF` cross-reference fields, so numbering
updates inside Word rather than being frozen text. No margin line numbering.

Both documents compile from one source, and the Word pass is checked against that source
rather than against the PDF's extracted text, which injects page numbers and running heads
into the middle of sentences and reports false gaps. Of the 270 body sentences in the
preprocessed source, 270 reach the Word file, and every cross-reference keeps its closing
bracket, which an earlier build was swallowing. Checked individually as well: the 7 figures
plus the graphical abstract, the two body tables with their lettered footnotes, all five
figure notes, the five highlights word for word, references through [70], the Nomenclature,
and the back matter (CRediT, Funding, Acknowledgements, Declaration of competing interest,
Data availability).

## Regenerate

    pdflatex V5 && bibtex V5 && pdflatex V5 && pdflatex V5
    pdflatex SI && bibtex SI && pdflatex SI && pdflatex SI
    python3 build_docx_elsevier.py
    python3 package_v5.py

Gates: `python3 check_submission.py` (all pass, body at 7,395 words against a 7,400 cap)
and `python3 -m scripts.check_manuscript_numbers` from `code/`.

## Still open, and needing an author decision

- **Generative-AI declaration.** Elsevier requires one either way.
- **The prior working paper**, disclosed in the results text with no bibliography entry.
- **Both ORCIDs.**
