# CLAUDE.md — Prosjekthukommelse for friidrett.live

## Hva er dette?
Norsk friidrettsstatistikk-plattform. Supabase (Postgres) backend, Next.js 16 frontend, Python-scraper mot minfriidrettsstatistikk.info og friidrett.no.

## Arkitektur

### Web (`web/`)
- **Next.js 16 App Router** med TypeScript
- Server-komponenter som standard. Klient-komponenter (`"use client"`) kun der det trengs.
- **Mønster for searchParams:** Server-komponent awaiter searchParams, sender som props til klient-komponent. Se `sammenlign/page.tsx` + `sammenlign/compare-content.tsx` som referanse.
- Supabase client: `@/lib/supabase/client` (browser), `@/lib/supabase/server` (server)
- UI: shadcn/ui, Tailwind, Recharts

### Scraper (`scraper/`)
- Python 3, virtualenv i `scraper/venv/`
- Kobler til Supabase via `.env` (SUPABASE_URL, SUPABASE_SERVICE_KEY)
- Kildedata fra minfriidrettsstatistikk.info (primær) og friidrett.no (historisk)

### Database (Supabase)
- Prosjekt-ID: `lwkykthpnthfcldifixg`
- Hovedtabeller: athletes, results, meets, events, seasons, clubs, season_bests, age_classes
- View: results_full (join av results + athletes + meets + events + clubs)
- **Performance-format:** `performance` = tid i sekunder som string ("214.32"), `performance_value` = millisekunder (214320). For felt: meter / centimeter.
- **Aldersgruppe:** `get_age_group(birth_date, competition_date)` — beregner fra kalenderår, brukes i results_full view
- **RPC:** `get_all_time_best` — henter alle-tiders-beste per utøver med filtre (kjønn, alder, bane, tidtaking, vind)
- **is_manual_time:** NULL = ikke manuell (samme som false). Kun `true` betyr manuell. Bruk `IS NOT TRUE` i filtre.

---

## Aktive scripts (bruk disse)

| Script | Formål | Når |
|--------|--------|-----|
| `update_results.py` | Scrape + importer nye stevner | Regelmessig oppdatering |
| `import_historical.py` | Import historiske all-time data fra friidrett.no | Ved behov, sjelden |
| `backfill_birth_years.py` | Hent fødselsår fra kilden for utøvere som mangler | Ved behov |
| `merge_duplicate_meets.py` | Slå sammen duplikate stevner | Vedlikehold |

## Utdaterte/farlige scripts (IKKE KJØR)

| Script | Hvorfor |
|--------|---------|
| `fix_missing_gender_batch.py` | SKAPTE kjønnsproblem. Infererte kjønn fra medkonkurrenter — fungerer ikke pga mixed heats. |
| `fix_missing_gender.py` | Første versjon, også problematisk |
| `fix_all_times.py` / `v2` / `v3` | Gamle tidsfiks-scripts, erstattet av `fix_all_times_robust.py` |
| `cleanup_duplicates.py` / `v2` / `v3` | Gamle duplikat-scripts, erstattet av `cleanup_final.py` |
| `scraper.py` / `scraper_v2.py` | Gamle scrapere, erstattet av `update_results.py` |

---

## Kjente problemer og lærdom

### 1. Kjønn (gender) — DELVIS ØDELAGT
**Status:** Mange utøvere har feil kjønn pga batch-inferens fra heats.
**Symptom:** Kvinnelister viser mannsnavn.
**Årsak:** `fix_missing_gender_batch.py` antok alle i samme heat = samme kjønn. Feil.
**Regel:** Kjønn kan KUN settes pålitelig via:
- Autoritative øvelser (hekkhøyder, 7-kamp vs 10-kamp)
- Norske fornavn-mønstre
- Manuell gjennomgang
**ALDRI** infer kjønn fra medkonkurrenter.
Se `scraper/FIX_GENDER_README.md` for full plan.

### 2. Tidsformat — Gjentakende problem
**Problem:** Tider fra kilden kommer i ulike formater (M.SS.CC, M:SS.CC, bare sekunder).
**Regel:** All konvertering skjer i `fix_performance_format()` i `update_results.py`. Ikke lag nye fix-scripts — fiks heller roten i import-logikken.
**Lærdom:** 5+ iterasjoner av fix-scripts (fix_all_times v1-v3, robust) fordi feilen ble fikset i etterkant i stedet for i import.

### 3. Duplikater — Gjentakende problem
**Problem:** Duplikate stevner/resultater oppstår ved re-import.
**Regel:** `update_results.py` har innebygd duplikatsjekk med `normalize_meet_name()`. Bruk dette. Ikke kjør gamle import-scripts manuelt.
**Lærdom:** 5+ iterasjoner av cleanup-scripts fordi duplikater ble opprettet på nytt.

### 4. Fødselsår mangler
**Problem:** Mange utøvere mangler birth_year.
**Løsning:** `backfill_birth_years.py` henter fra kilden via external_id-matching.
**OBS:** Scriptet oppdaterer KUN der birth_year IS NULL — trygt å kjøre flere ganger.

### 5. Event-mapping
**Problem:** Nye øvelsenavn fra kilden som ikke er mappet.
**Symptom:** "Unmapped event" warnings i update_results.py.
**Løsning:** Legg til mapping i `EVENT_NAME_TO_CODE` i update_results.py, og opprett evt. ny event i DB.

### 6. Aldersklasser — Kalenderår (VIKTIG)
**Regel:** Norsk friidrett bruker **kalenderår** for aldersklasser: alder = konkurranseår − fødselsår.
**IKKE** juster for om bursdag har vært. En utøver født i 1999 er G14 i HELE 2013.
**DB-funksjon:** `get_age_group(birth_date, competition_date)` bruker `EXTRACT(YEAR FROM ...)` uten bursdagsjustering.
**Lærdom:** Opprinnelig versjon justerte for eksakt bursdag → feil aldersklasse for utøvere med bursdag sent på året.

### 7. Manuell vs elektronisk tidtaking
**Regler:**
- Manuell tidtaking gjelder **KUN løpsøvelser kortere enn 800m** (100m, 200m, 400m, 600m)
- Tekniske øvelser (hopp/kast) har ALDRI manuell/elektronisk-distinksjon
- 800m og lengre har ALDRI manuell tidtaking
- **Deteksjon:** Bruk presisjon, IKKE desimaltegn (komma/punktum):
  - Tideler (11.7, 12.0, 12.3) → manuell
  - Hundredeler (11.68, 12.31) → elektronisk
- **Frontend:** Tidtaking-filter vises KUN for løpsøvelser (`result_type === "time"`). Tekniske øvelser viser alle resultater ufiltrert.
**Lærdom:** Komma som desimaltegn er IKKE en pålitelig indikator — friidrett.no bruker komma som norsk tallformat for alle tider i ungdomslistene.

### 8. NULL-håndtering i SQL boolean-filtre
**Regel:** Bruk `IS NOT TRUE` / `IS NOT FALSE` i stedet for `= false` / `= true` når kolonnen kan være NULL.
- `WHERE is_manual_time = false` ekskluderer NULL-rader (feil!)
- `WHERE is_manual_time IS NOT TRUE` inkluderer både false OG NULL (riktig!)
**Lærdom:** 20 690 resultater ble usynlige fordi `is_manual_time = NULL` ikke matchet `= false` i RPC-funksjonen.

---

## Regler for nye scripts

1. **Bruk Python `logging`-modulen**, aldri bare `print()`. Standard oppsett:
   ```python
   import logging
   logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
   logger = logging.getLogger(__name__)
   ```

2. **Logg til fil i tillegg til konsoll** for operasjoner som endrer data:
   ```python
   file_handler = logging.FileHandler(f'scraper/logs/{script_name}_{timestamp}.log')
   logger.addHandler(file_handler)
   ```

3. **Alltid --dry-run flagg** for scripts som endrer data.

4. **Dokumenter i OPERATIONS_LOG.md** hva som ble kjørt, når, og resultatet.

5. **Ikke lag nye fix-scripts** for problemer som allerede er fikset. Sjekk OPERATIONS_LOG.md først.

6. **Fiks i import-logikken** heller enn å lage etterpå-scripts. Forebygg > reparer.

---

## Bygge og kjøre

```bash
# Frontend
cd web && npm run dev        # Utvikling
cd web && npx next build     # Verifiser build

# Scraper
cd scraper && source venv/bin/activate
python update_results.py     # Oppdater resultater
python update_results.py --dry-run  # Test først
```

## Mappestruktur (viktige filer)

```
web/
  src/app/             # Next.js routes
  src/components/      # React-komponenter
  src/lib/             # Utilities, Supabase-klienter
scraper/
  update_results.py    # Hovedscript for oppdatering
  import_historical.py # Historisk import
  backfill_birth_years.py # Fødselsår-backfill
  new_meets_data/      # Scraped data (midlertidig)
  migrations/          # SQL-migrasjoner
  logs/                # Loggfiler (opprett ved behov)
  OPERATIONS_LOG.md    # Operasjonslogg
  FIX_GENDER_README.md # Kjønnsproblem-dokumentasjon
```
