#!/bin/zsh
# Bygger 01_hovedartikkel.md -> Hovedartikkel_Fagnytt.pdf (pandoc + xelatex).
set -e
cd "$(dirname "$0")"
pandoc 01_hovedartikkel.md \
  -o Hovedartikkel_Fagnytt.pdf \
  --pdf-engine=xelatex \
  --resource-path=. \
  -V mainfont="Charter" \
  -V sansfont="Helvetica Neue" \
  -V fontsize=11pt \
  -V geometry:margin=2.4cm \
  -V linestretch=1.3 \
  -V lang=nb \
  -H pdf_preamble.tex \
  --lua-filter=faktaboks.lua
echo "Skrev $(pwd)/Hovedartikkel_Fagnytt.pdf"
