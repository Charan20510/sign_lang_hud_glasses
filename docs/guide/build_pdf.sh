#!/bin/sh
# Build docs/hardware_bringup.pdf from docs/guide/bringup.html with headless Chrome.
# Needs: Google Chrome + Space Mono font installed (~/Library/Fonts).
cd "$(git rev-parse --show-toplevel)" || exit 1
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --no-pdf-header-footer --print-to-pdf="$PWD/docs/hardware_bringup.pdf" \
  "file://$PWD/docs/guide/bringup.html" && echo "built docs/hardware_bringup.pdf"

# Step 12 measurement sheet (fill in by hand before 3D printing).
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --no-pdf-header-footer --print-to-pdf="$PWD/docs/step12_measure.pdf" \
  "file://$PWD/docs/guide/step12_measure.html" && echo "built docs/step12_measure.pdf"

# Project report change log (Space Mono 12px).
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --no-pdf-header-footer --print-to-pdf="$PWD/docs/report/report_changes.pdf" \
  "file://$PWD/docs/report/changes.html" && echo "built docs/report/report_changes.pdf"
