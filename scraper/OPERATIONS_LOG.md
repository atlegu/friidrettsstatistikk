# Operasjonslogg — Scraper

Logg over alle kjøringer som endrer data. **Oppdater denne filen etter hver operasjon.**

Format: Dato, script, parametre, resultat, eventuelle problemer.

---

## 2026-07-03/04 — Kjønnsopprydding (FULLFØRT)

### Fase 1: Klassebevis fra kilden
- **Script:** `fix_gender_from_source.py --seasons 2013-2026`
- **Formål:** Sette kjønn autoritativt fra klasseoverskrifter på stevnesidene
  (minfriidrettsstatistikk.info). Kun stevner med resultater fra NULL-utøvere
  ble hentet (hjelpetabell `gender_fix_target_meets`, 10 265 stevner).
- **Resultat:** 8 437/10 265 stevner matchet mot kilden (navn+dato), 671 000
  bevisrader høstet. 775 utøvere → M, 305 → F. 2 konflikter, 109 motsigelser
  rapportert. `meets.external_id` populert for 8 437 stevner (ny kolonne +
  RPC `set_meet_external_ids`).
- **Problemer:** (1) Første kjøring krasjet på partial upsert mot meets
  (NOT NULL sjekkes før konfliktløsning) — løst med RPC. (2) Maskinsøvn drepte
  kjøringen ved 4 700 stevner og etterlot trunkert gzip-bevisfil — 367 459 rader
  berget, resume-logikk + `caffeinate` la til. (3) Hovedfunn: kildens stevnesider
  viser IKKE 10-12-årsklassene (barneidrettsbestemmelsene), så ~29k utøvere
  (nesten alle 10-12 år) kan aldri få kjønn fra klassebevis.
- **Bevisfiler:** `new_meets_data/gender_evidence_*.jsonl.gz` (kan gjenbrukes
  til aldersklasse-backfill uten ny scraping!)
- **Loggfiler:** `logs/fix_gender_from_source_*.log`, `logs/fix_gender_report_*.json`

### Fase 2: Fornavnsklassifisering
- **Script:** `fix_gender_by_firstname.py --contradictions-report logs/fix_gender_report_20260704_004330_contradictions.json`
- **Formål:** Klassifisere 10-12-åringene (uten klassebevis) på fornavn, trent
  på 668 436 klassebevisrader + 58 503 utøvere med kjent kjønn.
- **Validering:** Leave-one-out mot kjente utøvere: **99,76 %** treff (55 669/55 805).
- **Terskler:** >= 5 obs og >= 98 % samme kjønn, eller >= 3 obs og 100 %.
- **Resultat:** 14 075 → M, 12 789 → F. 67 motsigelser rettet (enstemmig
  klassebevis >= 5 mot feil DB-kjønn — rest fra batch-korrupsjonen jan 2026).
  2 273 forblir NULL (sjeldne/utenlandske navn) — liste i rapporten.
- **Sluttstatus:** M=47 859, F=37 508, NULL=2 273 (fra 30 217).
  Kvinnelister verifisert rene (100m/5000m).

### Forebygging
- `update_results.py` `match_athlete()` backfiller nå kjønn på eksisterende
  utøvere med gender=NULL når importen har autoritativt klasse-kjønn.

### Restanser
- 2 273 NULL (sjeldne navn) — manuell liste i `logs/fix_gender_by_firstname_report_*.json`
- 1 828 målstevner umatchet mot kilden (navneavvik) — kan diagnostiseres via
  `meets.external_id IS NULL`
- 42 motsigelser med svakt/blandet bevis — samme rapportfil
- Hjelpetabell `gender_fix_target_meets` droppet etter kjøring

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
