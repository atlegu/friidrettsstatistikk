#!/usr/bin/env bash
# Kontrollerer sesongene 2012 og 2011 mot kilden.
# Kilden har ingenting før 2011 — sondert 06.09.2026:
#   2013: 1106 stevner · 2012: 911 · 2011: 618 · 2010 og eldre: 0
# Det som ligger i basen fra før 2011 er alle-tiders-materiale fra
# friidrett.no, ikke sesongdata, og kan ikke kontrolleres på denne måten.
set -uo pipefail
cd "$(dirname "$0")"
source venv/bin/activate
SAMLELOGG="logs/eldre_$(date +%Y%m%d_%H%M%S).log"
for AR in 2012 2011; do
  for MODUS in outdoor indoor; do
    if [ "$MODUS" = indoor ]; then FRA="$((AR-1))-11-01"; FLAGG=--indoor
    else FRA="${AR}-01-01"; FLAGG=--outdoor; fi
    LOGG="logs/verify_${MODUS}_${AR}.log"; START=$(date +%s)
    echo "" | tee -a "$SAMLELOGG"; echo "=== $AR $MODUS ===" | tee -a "$SAMLELOGG"
    for FORSOK in 1 2 3; do
      python update_results.py $FLAGG --season "$AR" --from-date "$FRA" \
          --verify > "$LOGG" 2>&1
      KODE=$?; [ $KODE -eq 0 ] && break
      echo "  forsøk $FORSOK feilet (kode $KODE), venter 5 min" | tee -a "$SAMLELOGG"
      sleep 300
    done
    grep -E "Kontrollert|Results imported|Errors:" "$LOGG" \
      | sed 's/.*INFO - //;s/^/  /' | tee -a "$SAMLELOGG"
    echo "  brukte $(( ($(date +%s) - START) / 60 )) min" | tee -a "$SAMLELOGG"
  done
done
echo "" | tee -a "$SAMLELOGG"; echo "FERDIG $(date '+%F %H:%M')" | tee -a "$SAMLELOGG"
