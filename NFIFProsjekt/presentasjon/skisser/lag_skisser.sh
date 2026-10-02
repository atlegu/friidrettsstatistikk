#!/usr/bin/env bash
# Gjør skissene om til PNG for lysbildene.
# Vindushøyden er valgt slik at utsnittet fyller et 16:9-lysbilde uten å krympe
# til ulesbarhet — bedre å vise toppen stort enn hele siden smått.
set -euo pipefail
cd "$(dirname "$0")"
C="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
skjermbilde () {
  "$C" --headless --disable-gpu --window-size=1500,"$2" \
       --virtual-time-budget=20000 --screenshot="$1.png" "file://$PWD/$1.html" >/dev/null 2>&1
  echo "$1.png"
}
skjermbilde 1_utoverprofil 760
skjermbilde 2_aktivitet    830
