#!/bin/bash
# Build.sh — builds the long working paper from LaTeX source.
# Usage: ./Build.sh [Paper_v20|<other stem in paper/>]
# Defaults to Paper_v20, the current long version. The Applied Energy
# submission is NOT built here; build it from paper/ae_submission/.

MAIN=${1:-Paper_v20}
cd "$(dirname "$0")/paper" || exit 1

echo "Building $MAIN.pdf ..."
pdflatex -interaction=nonstopmode "$MAIN"
bibtex "$MAIN"
pdflatex -interaction=nonstopmode "$MAIN"
pdflatex -interaction=nonstopmode "$MAIN"

if [ -f "$MAIN.pdf" ]; then
    echo "✓ Built: paper/$MAIN.pdf ($(du -h "$MAIN.pdf" | cut -f1))"
else
    echo "✗ Build failed — check paper/$MAIN.log"
    exit 1
fi
