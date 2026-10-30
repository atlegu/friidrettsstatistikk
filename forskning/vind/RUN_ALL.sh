#!/usr/bin/env bash
# RUN_ALL.sh — A6 «How much is the wind worth?»: hele kjeden fra frosset uttrekk til PDF og
# alle kontroller (paper-data-audit fase 5). Stopper ved første feil.
#
# Uttrekket (00_uttrekk.py, 00b_uttrekk_hekk.py) kjøres IKKE: data_private/ er frosset og
# hashkontrolleres. 04_figurer_tabeller.py og 06_manusfigurer_tabeller.py er runde 1-skript
# som er erstattet av 08/09 og kjøres ikke (de ville overskrevet figurene).
set -eo pipefail
cd "$(dirname "$0")"
PY=../../scraper/venv/bin/python
export SOURCE_DATE_EPOCH=1793318400 FORCE_SOURCE_DATE=1   # reproduserbare PDF-er

echo "== 0. Frysekontroll (fryst 30.10.2026, se FREEZE.md)"
shasum -a 256 -c --quiet FREEZE_data.sha256
shasum -a 256 -c --quiet FREEZE_code.sha256
shasum -a 256 -c --quiet eliteende_input.sha256   # tfrrs_shared v1.2 og Tilastopaja-uttrekket (tabell S8)
echo "data, kode og eksterne inndata stemmer med FREEZE"

echo "== 1. Analysekjede"
$PY 01_variabler.py
$PY 02_deskriptiv.py
$PY 03_estimering.py
$PY 05_hekk.py
$PY 07_revisjon_r1.py
$PY 07b_revisjon_r2.py
$PY 10_eiv_kalibrering.py
$PY 11_eliteende.py
$PY 08_r1_figurer_tabeller.py
$PY 09_r1_supptex.py

echo "== 2. Manus (full LaTeX-syklus)"
(
  cd manus
  rm -f main.aux main.bbl main.blg
  pdflatex -interaction=nonstopmode -halt-on-error main.tex > /dev/null
  bibtex main > /dev/null || [ $? -eq 1 ]
  pdflatex -interaction=nonstopmode -halt-on-error main.tex > /dev/null
  pdflatex -interaction=nonstopmode -halt-on-error main.tex > /dev/null
  # egen tittelside (JSS er dobbeltanonym; manus har ingen forfatteropplysninger)
  pdflatex -interaction=nonstopmode -halt-on-error title_page.tex > /dev/null
)
if grep -Eq "Reference .* undefined|Citation .* undefined" manus/main.log; then
  echo "FEIL: udefinerte referanser"; exit 1
fi
if pdftotext manus/main.pdf - | grep -q '??'; then
  echo "FEIL: ?? i PDF"; exit 1
fi
# anonymitet: ingen forfatteropplysninger i manus-PDF-en eller metadataene (selvsitering i
# tredje person, «Guttormsen (2026)», er tillatt)
if pdftotext manus/main.pdf - | grep -Eq "Atle|Simen|NMBU|ORCID|nmbu\.no|\bAGG\b|\bSG\b|Ås|author's initiative|from the author"; then
  echo "FEIL: identifiserende tekst i det anonymiserte manuset"; exit 1
fi
if pdfinfo manus/main.pdf | grep -Eq "^Author: +[^ ]"; then
  echo "FEIL: forfatter i PDF-metadataene"; exit 1
fi

echo "== 3. Uavhengig R-implementasjon og tallsporing"
Rscript audit/uavhengig.R > audit/r_out_logg.txt 2>&1
$PY audit/sammenlign.py
$PY audit/kontroll_tall.py

echo "RUN_ALL A6 OK"
