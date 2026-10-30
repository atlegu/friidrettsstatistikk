#!/usr/bin/env bash
# RUN_ALL.sh — A3 «Debutalder»: hele kjeden fra frosset uttrekk til PDF og alle kontroller
# (paper-data-audit fase 5). Stopper ved første feil.
#
# Uttrekket (00_uttrekk.py) kjøres IKKE: data_private/ er frosset og hashkontrolleres.
set -eo pipefail
cd "$(dirname "$0")"
PY=../../scraper/venv/bin/python
export SOURCE_DATE_EPOCH=1793318400 FORCE_SOURCE_DATE=1   # reproduserbare PDF-er

echo "== 0. Frysekontroll (fryst 30.10.2026, se FREEZE.md)"
shasum -a 256 -c --quiet FREEZE_data.sha256
shasum -a 256 -c --quiet FREEZE_code.sha256
echo "data og kode stemmer med FREEZE"

echo "== 1. Analysekjede"
$PY 01_variabler.py
$PY 02_deskriptiv.py
$PY 03_modeller.py
$PY 04_figurer_tabeller.py
$PY 05_revisjon_r1.py
$PY 05b_revisjon_r2.py
$PY 06_manustabeller.py

echo "== 2. Manus (full LaTeX-syklus)"
(
  cd manus
  rm -f main.aux main.bbl main.blg
  pdflatex -interaction=nonstopmode -halt-on-error main.tex > /dev/null
  bibtex main > /dev/null || [ $? -eq 1 ]
  pdflatex -interaction=nonstopmode -halt-on-error main.tex > /dev/null
  pdflatex -interaction=nonstopmode -halt-on-error main.tex > /dev/null
)
if grep -Eq "Reference .* undefined|Citation .* undefined" manus/main.log; then
  echo "FEIL: udefinerte referanser"; exit 1
fi
if pdftotext manus/main.pdf - | grep -q '??'; then
  echo "FEIL: ?? i PDF"; exit 1
fi

echo "== 3. Uavhengig R-implementasjon og tallsporing"
Rscript audit/uavhengig.R > audit/r_out_logg.txt 2>&1
$PY audit/sammenlign.py
$PY audit/kontroll_tall.py

echo "RUN_ALL A3 OK"
