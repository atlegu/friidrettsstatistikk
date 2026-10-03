#!/bin/zsh
# Bygger Fagnytt-bladet (mal i blad/): artikler/*.md -> .tex via pandoc, deretter xelatex to ganger (sidetall i innholdslisten).
set -e
cd "$(dirname "$0")/blad"
for f in artikler/*.md; do
  pandoc "$f" -t latex -o "${f%.md}.tex" --resource-path=..:. --shift-heading-level-by=-1 --lua-filter=../magasin.lua --wrap=preserve
done
xelatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null || { tail -40 main.log; exit 1; }
xelatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null
N=$(pdfinfo main.pdf | awk '/Pages/{print $2}')
[ "$N" -le 28 ] || { echo "FEIL: $N sider, maks 28 (siste side er annonse)"; exit 1; }
cp main.pdf ../Fagnytt_pilot.pdf
echo "Skrev $(cd .. && pwd)/Fagnytt_pilot.pdf ($(pdfinfo main.pdf | grep Pages))"
