#!/usr/bin/env bash
#
# Kontrollerer hver sesong mot kilden og henter inn det som mangler.
#
# Terskelen MIN_RESULTS_THRESHOLD = 10 gjorde at delvis importerte stevner
# aldri ble hentet på nytt. Feilen har ligget der hele tiden, så alle sesonger
# må kontrolleres. Se OPERATIONS_LOG.md 2026-08-22.
#
# Nyeste sesong først — de mest brukte dataene blir riktige tidligst.
# Én sesong tar fra minutter til et par timer avhengig av antall stevner.
#
#   ./verify_alle_sesonger.sh            2013 til 2026
#   ./verify_alle_sesonger.sh 2020 2026  bare et utvalg
#
# Kjøringen kan trygt avbrytes og startes igjen: importen hopper over
# resultater som allerede finnes.

set -uo pipefail
cd "$(dirname "$0")"
source venv/bin/activate

FRA=${1:-2013}
TIL=${2:-2026}
SAMLELOGG="logs/verify_alle_$(date +%Y%m%d_%H%M%S).log"

echo "Kontrollerer sesongene $TIL ned til $FRA" | tee -a "$SAMLELOGG"
echo "Samlelogg: $SAMLELOGG" | tee -a "$SAMLELOGG"

for (( AR=TIL; AR>=FRA; AR-- )); do
  for MODUS in outdoor indoor; do
    if [ "$MODUS" = "indoor" ]; then
      # Innendørssesongen starter i november året før
      FRADATO="$((AR-1))-11-01"
      FLAGG="--indoor"
    else
      FRADATO="${AR}-01-01"
      FLAGG="--outdoor"
    fi

    LOGG="logs/verify_${MODUS}_${AR}.log"
    START=$(date +%s)
    echo "" | tee -a "$SAMLELOGG"
    echo "=== $AR $MODUS (fra $FRADATO) ===" | tee -a "$SAMLELOGG"

    python update_results.py $FLAGG --season "$AR" --from-date "$FRADATO" \
        --verify > "$LOGG" 2>&1
    KODE=$?

    MIN=$(( ($(date +%s) - START) / 60 ))
    if [ $KODE -ne 0 ]; then
      echo "  AVBRUTT med kode $KODE etter ${MIN} min — se $LOGG" | tee -a "$SAMLELOGG"
      continue
    fi
    grep -E "Kontrollert|Results imported|Skipped \(no event|Errors:" "$LOGG" \
      | sed 's/.*INFO - //' | sed 's/^/  /' | tee -a "$SAMLELOGG"
    echo "  brukte ${MIN} min" | tee -a "$SAMLELOGG"
  done
done

echo "" | tee -a "$SAMLELOGG"
echo "FERDIG. Umappede øvelser på tvers av alle sesonger:" | tee -a "$SAMLELOGG"
grep -h "Unmapped event" logs/verify_*_[0-9]*.log 2>/dev/null \
  | sed 's/.*Unmapped event: //' | sed 's/ ([0-9]* results)//' \
  | sort | uniq -c | sort -rn | head -30 | tee -a "$SAMLELOGG"
