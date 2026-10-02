#!/usr/bin/env bash
# Kjører hele lekene-trend-pipelinen: uttrekk -> figurer -> trender -> vedleggstabell.
# Bruk:  bash forskning/lekene-trend/kjor_alt.sh            (med nytt uttrekk fra Supabase)
#        bash forskning/lekene-trend/kjor_alt.sh --uten-uttrekk   (bare figurer/tabeller)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="$HERE/../../scraper/venv/bin/python"
cd "$HERE"
if [[ "${1:-}" != "--uten-uttrekk" ]]; then
  "$PY" 01_uttrekk.py 2>&1 | grep -v "HTTP Request" | grep -v "side [0-9]"
fi
"$PY" 02_deskriptiv.py
"$PY" 03_trender.py
"$PY" 04_vedleggstabell.py
echo "Ferdig. Se over figures/ og tables/, og oppdater tallene i 03_vurdering.md."
