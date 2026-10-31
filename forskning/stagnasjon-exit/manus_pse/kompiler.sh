#!/bin/bash
# Kompilerer PSE-versjonen. biber fra TeX Live feiler på denne maskinen (lipo-utpakking);
# bruk en utpakket arm64-biber: lipo /usr/local/texlive/2025/bin/universal-darwin/biber -thin arm64 -output <sti>
BIBER="${BIBER:-/private/tmp/claude-501/-Users-atleguttormsen-Dropbox-Aktuelt1-Florida25-Statistikk/d01f5049-1602-4e0b-9a8f-bbb28ecbbe76/scratchpad/biber_arm64/biber}"
cd "$(dirname "$0")"
python3 bygg_pse.py || exit 1
for f in main_anonymised supplement title_page; do
  pdflatex -interaction=nonstopmode $f.tex >/dev/null || { grep -n "^!" -A3 $f.log | head -20; exit 1; }
  [ -f $f.bcf ] && "$BIBER" $f >/dev/null
  pdflatex -interaction=nonstopmode $f.tex >/dev/null
  pdflatex -interaction=nonstopmode $f.tex >/dev/null
  echo "$f.pdf: $(pdfinfo $f.pdf | awk '/Pages/{print $2}') sider"
done
grep -c "undefined" main_anonymised.log | sed 's/^/udefinerte referanser i hovedfil (skal være 0): /'
