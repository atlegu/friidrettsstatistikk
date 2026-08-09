# Operasjonslogg — Scraper

Logg over alle kjøringer som endrer data. **Oppdater denne filen etter hver operasjon.**

Format: Dato, script, parametre, resultat, eventuelle problemer.

---

## 2026-08-09 — Reparasjon av mangekamp-korrupsjon (FULLFØRT)

- **Script:** `fix_mangekamp_korrupsjon.py --apply --yes` (dry-run kjørt først)
- **Symptom:** Klubbregisteret inneholdt 133 «klubber» med navn som «01», «61»,
  «55-DNF». Synlig som søppel i klubboversikten på nettsiden.
- **Årsak:** Importparseren for mangekampstevner splittet ikke kolonnene. Hele
  strengen `"Navn, Klubb<delresultater>"` havnet i `athletes.full_name`, og halen
  av strengen ble opprettet som egen klubb. Eksempel:
  `"Maiken Rose Bjerknesli, IL i BUL14,23-7,40-16,56-14,43-4"` med klubb `"61"`.
  Hver slik rad skapte en falsk utøverpost med nøyaktig ett resultat.
- **Omfang:** 660 falske utøverposter, 133 falske klubber, 660 berørte resultater.
- **Metode:** Ekte navn og klubb ble trukket ut av den korrupte strengen,
  ekte utøver slått opp på navn + fødselsår, resultatet flyttet dit.
  Nasjonalitetskoder som `(DEN)`, `(GER)`, `(SWE)` ble strippet før oppslag.
- **Resultat:**
  - 318 resultater flyttet til riktig utøver og klubb
  - 275 duplikatresultater slettet (fantes allerede korrekt importert)
  - 656 falske utøverposter slettet — utøvere 88 016 → 87 360
  - 131 av 133 falske klubber slettet — klubber 2 636 → 2 505
  - Resultater 1 411 073 → 1 410 798. Ingen foreldreløse resultater.
- **Står igjen, krever manuell vurdering (4 poster, 2 klubber):**
  - «Siv Sundt (12)» — strengen mangler komma å dele på
  - «Alfred Lund Stende» (2 rader) — 4 navnelike utøvere i basen
  - «Linnea Elise Westre» — 3 navnelike utøvere i basen
- **Første kjøring stoppet** etter 63 rader på unik-constrainten
  `results_innhold_unik`. Det avdekket at 275 av postene var rene duplikater.
  Skriptet ble endret til å la databasen avgjøre: ved 23505 slettes duplikatet
  i stedet for å flyttes. Ingen data gikk tapt.
- **Sikkerhetskopi:** `backups/fix_mangekamp_korrupsjon_20260809_18*.json`
  (alle berørte utøvere, resultater og klubber før endring).
### ROT-ÅRSAK FUNNET OG FIKSET

- **Skyldig:** `import_youth_stats.py` linje 462 (kjørt mai 2026 — 659 av de 660
  korrupte radene ble opprettet da). *Ikke* `update_results.py`; dagens kilde på
  `StevneResultater.php` leverer navn og klubb i separate kolonner og er ren.
- **Feilen:** `name_club_text.rsplit(',', 1)`. Cellen har formen `"Navn, Klubb"`,
  men for mangekamp limes delresultatene på i samme celle med komma som
  desimaltegn. `rsplit` tok da *siste* komma:

      "Maiken Rose Bjerknesli, IL i BUL14,23-7,40-16,56-14,43-4,61"
        -> navn  = "Maiken Rose Bjerknesli, IL i BUL14,23-7,40-16,56-14,43-4"
        -> klubb = "61"

- **Fikset:**
  1. `split(',', 1)` — splitter på *første* komma. Strengt tryggere enn `rsplit`
     også for klubbnavn som inneholder komma.
  2. Ny `strip_combined_event_results()` kutter påhengte delresultater fra
     klubbnavnet. Kutter på desimaltall (`14,23`) og statuskoder (`DNF-`), men
     ikke på rene sifre — ekte klubber som «3T» overlever.
  3. Ny `is_valid_club_name()` i **både** `import_youth_stats.py` og
     `update_results.py` som siste forsvarslinje: et klubbnavn må inneholde
     minst én bokstav og kan ikke bestå kun av sifre, skilletegn og statuskoder.
     Ugyldige navn gir `None` og en advarsel i loggen i stedet for en ny klubb.
- **Verifisert mot sikkerhetskopien:** klubbnavnet gjenvinnes korrekt fra alle
  659 korrupte strenger, alle 133 kjente søppelklubber avvises av begge
  skriptene, og ingen av de testede ekte klubbnavnene avvises.

---

## 2026-08-07 — Sesongoppdatering mai–august (FULLFØRT)

### Import
- **Script:** `update_results.py --outdoor --season 2026`
- **Formål:** Basen sto på 17. mai; hele sommersesongen manglet.
- **Omfang:** 411 stevner i kilden, 28 i basen → 396 manglende/ufullstendige.
  392 stevner behandlet, 17 358 resultater skrapet.
- **Resultat:** 16 411 nye resultater etter 17. mai, 350 nye stevner,
  16 834 utøvere matchet, 376 nye utøvere opprettet. Siste dato nå 2026-08-01.
  Sesong 2026 totalt: 36 110 resultater. Base totalt: 1 412 964.
- **Forarbeid:** Slettet 31 resultater for 9 stevner som lå ufullstendige i basen
  og skulle re-importeres i sin helhet (ren re-import framfor duplikater).
  NB: «Hopp til Musikk» (11.05, 7 res.) hadde også <10 resultater, men sto IKKE
  på kildens liste — den ble bevisst *ikke* slettet.

### BUG FUNNET OG FIKSET: duplikater fra batch-retry
- **Symptom:** Skriptet rapporterte 17 653 importert av 17 358 skrapet — flere enn
  det fantes. 839 duplikatgrupper i basen etterpå.
- **Årsak:** `import_meet_results()` hadde `try/except` rundt HELE chunk-løkken.
  Feilet chunk 3 av 5, kjørte feilhåndteringen `result_batch` på nytt én og én —
  altså ble chunk 1–2 satt inn en gang til.
- **Hvorfor constrainten ikke fanget det:** `results` har
  `UNIQUE (athlete_id, event_id, meet_id, round, heat_number)`, men importen setter
  aldri `round`/`heat_number`. 19 241 av 19 301 2026-rader har begge NULL, og
  NULL er aldri lik NULL i Postgres. **Constrainten er i praksis inert for denne
  importveien.**
- **Opprydding:** Slettet 813 duplikater (nøkkel: athlete+event+meet+performance
  +place+wind, beholdt eldste `created_at`). 26 par som avvek på plass/vind ble
  BEVART — det er ekte heat+finale med samme tid, verifisert ved at de har
  identisk `created_at`, altså samme batch fra kilden.
- **Fiks:** `try/except` flyttet inn i chunk-løkken, slik at kun det feilende
  chunket retries. Kommentar lagt inn i koden.
- **Gjenstående duplikater etter opprydding:** 0 (verifisert).

### Kjente svakheter (ikke fikset)
- **357 importfeil** på ferdigparsede verdier: `9.5(+0.0) M`, `9.14()`,
  `18.16.1 M`. Håndtidsmarkør «M» og tomme/doble vindparenteser strippes ikke av
  `parse_result_wind()`/`fix_performance_format()`. Disse resultatene mangler.
- **148 resultater hoppet over** pga. manglende øvelsesmapping: kappgang
  (1000/1500/2000 m), 7-kamp/10-kamp-varianter, 400 m Racerunning,
  Kast 5-kamp veteran.
- **Løst samme dag — se neste bolk.**

### Duplikatsperre i databasen (FULLFØRT 2026-08-07)
- **Problem:** Den gamle constrainten
  `UNIQUE (athlete_id, event_id, meet_id, round, heat_number)` var inert:
  36 050 av 36 110 2026-rader har NULL i både `round` og `heat_number`, og
  `NULL = NULL` gir NULL (ikke true) i Postgres. Sperren låste aldri.
- **Hvorfor ikke bare `NULLS NOT DISTINCT` på den gamle?** Den ville da slått ut
  ekte heat+finale-par. Kilden (`StevneResultater.php`) har bare fire kolonner
  — plass, resultat, navn, klubb — og gir *ingen* rundeinfo, så `round` kan ikke
  fylles ut herfra. Heat og finale skilles kun ved ulik plass/vind.
- **Løsning:** Ny indeks på innholdet i stedet for runden:
  ```sql
  CREATE UNIQUE INDEX CONCURRENTLY results_innhold_unik
  ON results (athlete_id, event_id, meet_id, performance, place, wind)
  NULLS NOT DISTINCT;
  ```
  Blokkerer eksakte duplikater, men slipper gjennom heat+finale som avviker på
  plass eller vind.
- **Forarbeid:** Måtte rydde 1 891 eksisterende duplikatrader (1 736 grupper) i
  hele basen, ellers ville indeksen ikke la seg bygge. Fordeling: 345 grupper var
  NULL-runde mot utfylt runde (beholdt den utfylte — mest informasjon), 1 389 var
  identiske uten runde (beholdt eldste). **Ingen gruppe hadde ulik `status`**, så
  ingen risiko for å beholde et godkjent og slette et diskvalifisert resultat.
  1 170 av gruppene lå i 2026 (innendørs/vår), altså samme bug fra tidligere kjøringer.
- **Verifisert:** Forsøk på å sette inn kopi av en ekte rad avvises med
  `23505 duplicate key value violates unique constraint "results_innhold_unik"`.
- **Importskript:** `update_results.py` teller nå avviste duplikater som
  `skipped_duplicate` i stedet for `errors`. Importen er dermed trygt
  re-kjørbar — en ny kjøring over samme periode legger ikke inn noe på nytt.
- **Loggfiler:** `logs/update_20260807.log`, `logs/dryrun_20260807.log`

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
