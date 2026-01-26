# Scraper - FRIIDRETT.LIVE

Verktøy for å scrape og importere friidrettsresultater til databasen.

## Inkrementell scraper (NYE STEVNER)

For å holde databasen oppdatert med nye stevner fra minfriidrettsstatistikk.info:

```bash
cd /Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/Statistikk/scraper
source venv/bin/activate

# 1. Scrape nye stevner (sammenligner med DB og finner manglende)
python scrape_new_meets.py

# 2. Importer resultatene til databasen
python import_scraped_results.py new_meets_data/new_results_*.csv
```

### Filer

| Fil | Beskrivelse |
|-----|-------------|
| `scrape_new_meets.py` | Scraper stevner fra minfriidrettsstatistikk.info, sammenligner med DB, og henter resultater for manglende stevner |
| `import_scraped_results.py` | Importerer CSV-resultater til Supabase. Matcher/oppretter utøvere, klubber, stevner og øvelser |

### Output

Scraperen lagrer filer i `new_meets_data/`:
- `source_meets.json` - Alle stevner funnet på kilden
- `missing_meets.json` - Stevner som mangler i databasen
- `new_results_YYYYMMDD_HHMMSS.csv` - Resultater klare for import

### Duplikathåndtering

Import-scriptet har smart duplikatdeteksjon som:
- Normaliserer stevnenavn (fjerner lokasjonsprefiks som "Lubbock/TX/USA, " eller "Bærum, ")
- Matcher eksisterende stevner selv om navnene varierer litt
- Hopper over resultater som allerede finnes i databasen

## Vedlikehold: Merge duplikate stevner

Hvis det har oppstått duplikate stevner i databasen (samme stevne med ulike navn):

```bash
python merge_duplicate_meets.py
```

Dette scriptet:
- Finner stevner på samme dato med like navn
- Flytter resultater til stevnet med flest resultater
- Sletter tomme duplikater

### Konfigurasjon

I `scrape_new_meets.py`:
- `MIN_DATE` - Minimum dato for stevner (standard: 15. desember 2025)
- `REQUEST_DELAY` - Forsinkelse mellom requests (standard: 0.3 sek)

### Dataformat

**Performance-verdier lagres slik:**
- `performance`: Tid i sekunder som string (f.eks. "214.32" for 3:34.32)
- `performance_value`: Tid i millisekunder (f.eks. 214320)
- For feltøvelser: meter som string, centimeter som verdi

## Historisk import

For stor-import av historiske data (brukes sjelden):

```bash
python import_all_historical.py
```

## Miljøvariabler

Krever `.env` fil med:
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJxxx...
```

## Sist oppdatert

**2026-01-26**:
- Importerte 885 resultater totalt (722 + 163 fra incomplete stevner)
- Slettet 19 duplikate resultater og 57 duplikate stevner
- Forbedret duplikatdeteksjon i import-scriptet med normalize_meet_name()
- Opprettet merge_duplicate_meets.py for vedlikehold
