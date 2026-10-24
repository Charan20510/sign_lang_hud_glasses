#!/bin/sh
# Build docs/hardware_bringup.pdf from docs/guide/bringup.html with headless Chrome.
# Needs: Google Chrome + Space Mono font installed (~/Library/Fonts).
cd "$(git rev-parse --show-toplevel)" || exit 1
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --no-pdf-header-footer --print-to-pdf="$PWD/docs/hardware_bringup.pdf" \
  "file://$PWD/docs/guide/bringup.html" && echo "built docs/hardware_bringup.pdf"
