#!/bin/bash
# Bygger JSAMS-versjonen av A3 fra det fryste manuset og kompilerer alle tre PDF-er
# i full syklus (pdflatex, bibtex, pdflatex ×2). Kjør deretter tallkontroll_jsams.py og lag_docx.py.
cd "$(dirname "$0")"
PY="${PY:-../../../scraper/venv/bin/python}"
"$PY" bygg_jsams.py || exit 1
for f in main_anonymised supplement title_page; do
  pdflatex -interaction=nonstopmode -halt-on-error $f.tex >/dev/null || { grep -n "^!" -A3 $f.log | head -20; exit 1; }
  if grep -q "\\\\citation" $f.aux; then bibtex $f >/dev/null || [ $? -eq 1 ]; fi
  pdflatex -interaction=nonstopmode -halt-on-error $f.tex >/dev/null
  pdflatex -interaction=nonstopmode -halt-on-error $f.tex >/dev/null
  echo "$f.pdf: $(pdfinfo $f.pdf | awk '/Pages/{print $2}') sider"
done
echo "udefinerte referanser i hovedfil (skal være 0): $(grep -c 'undefined' main_anonymised.log)"
echo "manglende tabell-/figurnumre (skal være 0): $(pdftotext main_anonymised.pdf - | grep -c '??')"
