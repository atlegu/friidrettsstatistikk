#!/bin/zsh
# Bygger artikkel_utkast.md -> Trenerartikkel.pdf (pandoc + xelatex).
# Underlagsfigur-notatene (interne referanser) filtreres bort i PDF-en.
set -e
cd "$(dirname "$0")"

sed '/Underlagsfigur/d' artikkel_utkast.md > /tmp/artikkel_pdf.md

pandoc /tmp/artikkel_pdf.md \
  -o Trenerartikkel.pdf \
  --pdf-engine=xelatex \
  --resource-path=. \
  -V mainfont="Charter" \
  -V sansfont="Helvetica Neue" \
  -V fontsize=11pt \
  -V geometry:margin=2.4cm \
  -V linestretch=1.3 \
  -V lang=nb \
  -H pdf_preamble.tex

echo "Skrev $(pwd)/Trenerartikkel.pdf"
