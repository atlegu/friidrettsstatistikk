#!/usr/bin/env bash
# Bygger PDF fra HTML-rapporten med headless Chrome.
# Utskriftsstilene ligger i @media print i lag_rapport.py — søkefelt og
# sortering skjules, og utøverkort brytes aldri over et sideskift.
set -euo pipefail
cd "$(dirname "$0")"

../../scraper/venv/bin/python hent_tjalve.py
../../scraper/venv/bin/python lag_rapport.py

"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-pdf-header-footer \
  --run-all-compositor-stages-before-draw --virtual-time-budget=10000 \
  --print-to-pdf="tjalve_2024_2026.pdf" \
  "file://$PWD/tjalve_2024_2026.html"

echo "tjalve_2024_2026.pdf — $(pdfinfo tjalve_2024_2026.pdf | awk '/^Pages/{print $2}') sider"
