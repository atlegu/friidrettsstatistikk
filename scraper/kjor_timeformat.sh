#!/usr/bin/env bash
# Henter inn resultatene som ble kastet på firedelt tidsformat (H.MM.SS.hh).
# Se fix_performance_format() — løp over én time ble sendt uendret til basen.
set -uo pipefail
cd "$(dirname "$0")"
source venv/bin/activate
LOGG="logs/timeformat_$(date +%Y%m%d_%H%M%S).log"
for FIL in timelister/*.txt; do
  BASE=$(basename "$FIL" .txt); AR=${BASE%%_*}; MODUS=${BASE##*_}
  [ "$MODUS" = indoor ] && { FRA="$((AR-1))-11-01"; FLAGG=--indoor; } \
                        || { FRA="${AR}-01-01";     FLAGG=--outdoor; }
  echo "=== $AR $MODUS ===" | tee -a "$LOGG"
  python update_results.py $FLAGG --season "$AR" --from-date "$FRA" \
      --kun-stevner "$FIL" > "logs/tf_${MODUS}_${AR}.log" 2>&1
  grep -E "Results imported|Errors:" "logs/tf_${MODUS}_${AR}.log" \
    | sed 's/.*INFO - //;s/^/  /' | tee -a "$LOGG"
done
echo "FERDIG" | tee -a "$LOGG"
