# Makefile — hydrogen-eu-buildings-paper
# Builds Paper_v3.pdf from LaTeX source by default.
# Usage:
#   make          — full build (pdflatex + bibtex + pdflatex x2)
#   make v2       — build Paper_v2.pdf
#   make v1       — build Paper_v1.pdf
#   make quick    — single pdflatex pass (fast, for checking layout)
#   make clean    — remove auxiliary files
#   make distclean — remove auxiliary files + PDF

MAIN = Paper_v3
LATEX = pdflatex
BIBTEX = bibtex

.PHONY: all v1 v2 quick clean distclean

all: $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex References_v1.bib sections/*.tex
	$(LATEX) $(MAIN)
	$(BIBTEX) $(MAIN)
	$(LATEX) $(MAIN)
	$(LATEX) $(MAIN)

v2: Paper_v2.pdf

Paper_v2.pdf: Paper_v2.tex References_v1.bib sections/*.tex
	$(LATEX) Paper_v2
	$(BIBTEX) Paper_v2
	$(LATEX) Paper_v2
	$(LATEX) Paper_v2

v1: Paper_v1.pdf

Paper_v1.pdf: Paper_v1.tex References_v1.bib sections/*.tex
	$(LATEX) Paper_v1
	$(BIBTEX) Paper_v1
	$(LATEX) Paper_v1
	$(LATEX) Paper_v1

quick:
	$(LATEX) $(MAIN)

clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.toc *.lof *.lot *.fls *.fdb_latexmk
	rm -f sections/*.aux

distclean: clean
	rm -f $(MAIN).pdf Paper_v1.pdf
