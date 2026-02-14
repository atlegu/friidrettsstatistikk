# Operasjonslogg — Scraper

Logg over alle kjøringer som endrer data. **Oppdater denne filen etter hver operasjon.**

Format: Dato, script, parametre, resultat, eventuelle problemer.

---

## 2026-02-13

### Backfill fødselsår
- **Script:** `backfill_birth_years.py`
- **Status:** Kjører (startet av bruker)
- **Formål:** Hente fødselsår for utøvere som mangler birth_year
- **Resultat:** _Oppdater når ferdig_

---

## 2026-02-12

### Oppdatering av nye stevner
- **Script:** `update_results.py` (antatt basert på new_results CSV)
- **Output:** `new_meets_data/new_results_20260212_134837.csv`
- **Resultat:** Nye resultater importert

---

## Rekonstruert historikk (fra git-log og loggfiler)

### 2026-02-09 — Historisk import og all-time disclaimer
- **Commit:** ed713d9
- **Script:** `import_historical.py`
- **Formål:** Import av historiske all-time statistikk fra friidrett.no
- **Detaljer:** 3-nivå dedup (normalisert navn+dato, fuzzy, cross-meet)

### 2026-02-07 — Footer, championship layout, klubboppdateringer
- **Commit:** 69f5bfc
- **Endringer:** Oppdatert footer, mesterskap-layout, utøver-klubb-oppdateringer

### 2026-02-06 — Fix sammenlign-side lasting
- **Commit:** f2bbbf8
- **Problem:** Utøvernavn lastet ikke på sammenligningssiden
- **Løsning:** Fix i sammenlign/page.tsx

### 2026-02-02 — Manglende øvelser + unified update script
- **Commit:** 7f3ba82
- **Endringer:** Fix manglende øvelser på forsiden, opprettet `update_results.py`

### 2026-01-31 — Mesterskap-medaljer (NM)
- **Commit:** 501d0f9
- **Endringer:** Lagt til NM-medaljer på utøversider

### 2026-01-26 — Import og duplikat-opprydding
- **Logget i README.md**
- **Resultater:** 885 resultater importert, 19 duplikat-resultater slettet, 57 duplikat-stevner merget
- **Scripts brukt:** `import_scraped_results.py`, `merge_duplicate_meets.py`
- **Loggfiler:** `import_log.txt`

### 2026-01-25 — Massiv duplikat-opprydding
- **Scripts kjørt (i rekkefølge):**
  1. `cleanup_duplicates.py` → `cleanup_log.txt` (815 KB)
  2. `cleanup_duplicates_v2.py` → `cleanup_v2_log.txt` (1.4 MB)
  3. `cleanup_duplicates_v3.py` → `cleanup_v3_log.txt` (37 MB!)
  4. `cleanup_final.py` → `cleanup_final_log.txt` (3.5 MB)
  5. `cleanup_crossmeet.py` → `cleanup_crossmeet_log.txt` (3.5 MB)
- **Lærdom:** Trengte 5 iterasjoner. Burde vært gjort riktig i import-steget.

### 2026-01-25 — Cleanup final
- **Loggfil:** `cleanup_final.log` (6 KB)

### 2026-01-27 — Kjønnsfiks (MISLYKKET)
- **Dokumentert i:** `FIX_GENDER_README.md`
- **Problem:** `fix_missing_gender_batch.py` ødela kjønnsdata
- **Status:** UFIKSET. Mange utøvere har fortsatt feil kjønn.
- **VIKTIG:** Ikke kjør batch-kjønnsinferens igjen.

### 2026-01-22/24 — Data recovery
- **Loggfiler:** `recover_output.log` til `recover_output5.log`
- **Formål:** Ukjent — sannsynligvis recovery etter feilaktig sletting/oppdatering

### 2026-01-19 — Scraping
- **Loggfil:** `scrape_output.log` (158 KB)
- **Formål:** Stor scraping-kjøring

### Ca. jan 2026 — Diverse fikser
- Flere iterasjoner av tidsformat-fiks (fix_all_times v1/v2/v3/robust)
- Hekke-fiks (fix_hurdle_events/times/fast)
- Vekt-øvelse-fiks (fix_weight_events/fast)
- Kjønnsinferens (fix_missing_gender/batch/authoritative/complete)

---

## Mal for nye innføringer

```
### [Kort beskrivelse]
- **Script:** `script_name.py [--flagg]`
- **Formål:** Hva og hvorfor
- **Resultat:** Antall endringer, status
- **Problemer:** Eventuelle feil eller uventede ting
- **Loggfil:** `logs/script_name_YYYYMMDD.log` (hvis relevant)
```
