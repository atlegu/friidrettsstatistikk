#!/usr/bin/env bash
# Sesongene som fortsatt mangler etter nettverksfallene 25.-27.08.2026.
set -uo pipefail
cd "$(dirname "$0")"
source venv/bin/activate

SAMLE="logs/verify_rest_$(date +%Y%m%d_%H%M%S).log"

kjor() {   # $1=år  $2=modus  $3=fradato
  local LOGG="logs/verify_$2_$1.log"
  echo "" | tee -a "$SAMLE"; echo "=== $1 $2 ===" | tee -a "$SAMLE"
  local START=$(date +%s)
  for F in 1 2 3; do
    python update_results.py --$2 --season "$1" --from-date "$3" --verify > "$LOGG" 2>&1 && break
    echo "  forsøk $F feilet, venter 5 min" | tee -a "$SAMLE"; sleep 300
  done
  grep -E "Kontrollert|Results imported|Errors:" "$LOGG" | sed 's/.*INFO - /  /' | tee -a "$SAMLE"
  echo "  brukte $(( ($(date +%s)-START)/60 )) min" | tee -a "$SAMLE"
}

kjor 2018 outdoor 2018-01-01
for AR in 2016 2015 2014 2013; do
  kjor $AR outdoor "${AR}-01-01"
  kjor $AR indoor  "$((AR-1))-11-01"
done
echo "" | tee -a "$SAMLE"; echo "FERDIG" | tee -a "$SAMLE"
