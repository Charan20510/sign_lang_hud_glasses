#!/bin/sh
# Build docs/hardware_bringup.pdf from docs/guide/bringup.html with headless Chrome.
# Needs: Google Chrome + Space Mono font installed (~/Library/Fonts).
cd "$(git rev-parse --show-toplevel)" || exit 1
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --no-pdf-header-footer --print-to-pdf="$PWD/docs/hardware_bringup.pdf" \
  "file://$PWD/docs/guide/bringup.html" && echo "built docs/hardware_bringup.pdf"

# Mirror order sheet for the glass shop: PDF + PNG (to show on a phone).
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --no-pdf-header-footer --print-to-pdf="$PWD/docs/mirror_order.pdf" \
  "file://$PWD/docs/guide/mirror_order.html" && echo "built docs/mirror_order.pdf"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --hide-scrollbars --window-size=794,1123 --force-device-scale-factor=2 \
  --screenshot="$PWD/docs/mirror_order.png" \
  "file://$PWD/docs/guide/mirror_order.html" && echo "built docs/mirror_order.png"

# Step 12 measurement sheet (fill in by hand before 3D printing).
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --no-pdf-header-footer --print-to-pdf="$PWD/docs/step12_measure.pdf" \
  "file://$PWD/docs/guide/step12_measure.html" && echo "built docs/step12_measure.pdf"
