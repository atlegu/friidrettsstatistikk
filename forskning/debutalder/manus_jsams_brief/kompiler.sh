#!/bin/bash
# Kontrollerer Brief Report-versjonen (tall, grenser), skriver tittelsiden og kompilerer de tre
# PDF-ene i full syklus. Deretter: python3 lag_docx.py for Word-filene.
cd "$(dirname "$0")"
PY="${PY:-../../../scraper/venv/bin/python}"
"$PY" kontroll_brief.py || exit 1
for f in main_brief supplement_brief title_page_brief; do
  pdflatex -interaction=nonstopmode -halt-on-error $f.tex >/dev/null || { grep -n "^!" -A3 $f.log | head -20; exit 1; }
  if grep -q "\\\\citation" $f.aux; then bibtex $f >/dev/null || [ $? -eq 1 ]; fi
  pdflatex -interaction=nonstopmode -halt-on-error $f.tex >/dev/null
  pdflatex -interaction=nonstopmode -halt-on-error $f.tex >/dev/null
  echo "$f.pdf: $(pdfinfo $f.pdf | awk '/Pages/{print $2}') sider"
done
echo "udefinerte referanser (skal være 0): $(grep -c 'undefined' main_brief.log)"
echo "manglende nummer (skal være 0): $(pdftotext main_brief.pdf - | grep -c '??')"
