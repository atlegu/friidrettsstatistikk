#!/bin/bash
# A1 «Stagnasjon før exit» — kjører steg 0-2 (uttrekk, variabler, prereg-trygg deskriptiv).
# 03/04 kjøres IKKE her: de krever OSF_REGISTRERT.txt og --post-registration.
set -euo pipefail
cd "$(dirname "$0")"
PY=/Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/Statistikk/scraper/venv/bin/python

"$PY" 00_uttrekk.py
"$PY" 01_variabler.py
"$PY" 02_deskriptiv.py

echo
echo "Steg 0-2 ferdig. Neste: OSF-registrering (OSF_PREREGISTRATION.md)."
echo "Deretter: $PY 03_modeller.py --post-registration && $PY 04_robusthet.py --post-registration"
