#!/bin/zsh
# Bygger superskoene_fagnytt.md -> Superskoene_Fagnytt.pdf (pandoc + xelatex, magasinmal i to spalter).
set -e
cd "$(dirname "$0")"
pandoc superskoene_fagnytt.md \
  -o Superskoene_Fagnytt.pdf \
  --pdf-engine=xelatex \
  --resource-path=. \
  -V documentclass=article \
  -V classoption=twocolumn \
  -V fontsize=10pt \
  -V papersize=a4 \
  -V geometry:top=22mm \
  -V geometry:bottom=22mm \
  -V geometry:left=18mm \
  -V geometry:right=18mm \
  -V lang=nb \
  -V indent=true \
  -H pdf_preamble.tex \
  --shift-heading-level-by=-1 \
  --lua-filter=magasin.lua
echo "Skrev $(pwd)/Superskoene_Fagnytt.pdf"
