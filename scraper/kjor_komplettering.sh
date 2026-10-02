#!/usr/bin/env bash
#
# Tetter de to siste hullene etter sesongkontrollen.
#
# 1) MARKØRRADENE. Kilden henger markører på selve resultatverdien
#    («20.37.52mx», «4.43 L», «7.83A», «24.56+»). Databasetriggeren caster
#    performance til numeric, så hver eneste slik rad feilet ved innsetting —
#    1 028 resultater fordelt på 322 stevner. Parseren skiller nå tall fra
#    markør og lagrer markøren ordrett i results.source_marker.
#
#    Stevnene det gjelder er hentet ut av loggene til markorlister/. Vi henter
#    bare dem, i stedet for å telle hele sesonger mot kilden på nytt.
#
# 2) 2018 UTENDØRS. Sesongen ble aldri kontrollert: alle tre forsøkene døde på
#    første kall til Supabase mens DNS var nede, fordi vent_pa_nett() sto
#    ETTER load_events(). Rekkefølgen er rettet; sesongen kjøres nå fullt ut.
#
# Kjøringen kan trygt avbrytes og startes igjen — importen hopper over
# resultater som allerede finnes.

set -uo pipefail
cd "$(dirname "$0")"
source venv/bin/activate

SAMLELOGG="logs/komplettering_$(date +%Y%m%d_%H%M%S).log"
si() { echo "$*" | tee -a "$SAMLELOGG"; }

si "Komplettering startet $(date '+%Y-%m-%d %H:%M')"
si "Samlelogg: $SAMLELOGG"

# ---------- 1) Markørradene ----------
si ""
si "### Markørstevner"

for FIL in markorlister/*.txt; do
  BASE=$(basename "$FIL" .txt)          # f.eks. 2023_outdoor
  AR=${BASE%%_*}
  MODUS=${BASE##*_}

  if [ "$MODUS" = "indoor" ]; then
    FRADATO="$((AR-1))-11-01"; FLAGG="--indoor"
  else
    FRADATO="${AR}-01-01";     FLAGG="--outdoor"
  fi

  LOGG="logs/markor_${MODUS}_${AR}.log"
  START=$(date +%s)
  si ""
  si "=== $AR $MODUS ($(wc -l < "$FIL" | tr -d ' ') stevner) ==="

  for FORSOK in 1 2 3; do
    python update_results.py $FLAGG --season "$AR" --from-date "$FRADATO" \
        --kun-stevner "$FIL" > "$LOGG" 2>&1
    KODE=$?
    [ $KODE -eq 0 ] && break
    si "  forsøk $FORSOK feilet (kode $KODE), venter 5 min"
    sleep 300
  done

  MIN=$(( ($(date +%s) - START) / 60 ))
  if [ $KODE -ne 0 ]; then
    si "  AVBRUTT med kode $KODE etter ${MIN} min — se $LOGG"
    continue
  fi
  grep -E "KUN-STEVNER|Results imported|Errors:" "$LOGG" \
    | sed 's/.*INFO - //' | sed 's/^/  /' | tee -a "$SAMLELOGG"
  si "  brukte ${MIN} min"
done

# ---------- 2) 2018 utendørs ----------
si ""
si "### 2018 utendørs — full kontroll mot kilden"
LOGG="logs/verify_outdoor_2018.log"
START=$(date +%s)

for FORSOK in 1 2 3; do
  python update_results.py --outdoor --season 2018 --from-date 2018-01-01 \
      --verify > "$LOGG" 2>&1
  KODE=$?
  [ $KODE -eq 0 ] && break
  si "  forsøk $FORSOK feilet (kode $KODE), venter 5 min"
  sleep 300
done

MIN=$(( ($(date +%s) - START) / 60 ))
if [ $KODE -ne 0 ]; then
  si "  AVBRUTT med kode $KODE etter ${MIN} min — se $LOGG"
else
  grep -E "Kontrollert|Results imported|Errors:" "$LOGG" \
    | sed 's/.*INFO - //' | sed 's/^/  /' | tee -a "$SAMLELOGG"
  si "  brukte ${MIN} min"
fi

si ""
si "FERDIG $(date '+%Y-%m-%d %H:%M')"
si "Rader som fortsatt feiler på verdiformat:"
grep -h "Rad feilet" logs/markor_*.log logs/verify_outdoor_2018.log 2>/dev/null \
  | wc -l | tee -a "$SAMLELOGG"
