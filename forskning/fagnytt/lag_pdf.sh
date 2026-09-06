#!/bin/zsh
# Bygger 01_hovedartikkel.md -> Hovedartikkel_Fagnytt.pdf (pandoc + xelatex, magasinmal i to spalter).
set -e
cd "$(dirname "$0")"
pandoc 01_hovedartikkel.md \
  -o Hovedartikkel_Fagnytt.pdf \
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
echo "Skrev $(pwd)/Hovedartikkel_Fagnytt.pdf"
