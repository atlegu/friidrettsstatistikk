# Scraper — friidrett.live

Verktøy for å scrape og importere friidrettsresultater til Supabase.

## Aktive scripts

### Daglig oppdatering
```bash
cd scraper && source venv/bin/activate
python update_results.py              # Auto-detect sesong, oppdater alt
python update_results.py --dry-run    # Forhåndsvisning uten endringer
python update_results.py --indoor     # Tving innendørs-sesong
python update_results.py --from-date 2026-01-01  # Fra en spesifikk dato
```

`update_results.py` er det eneste scriptet du trenger for daglig oppdatering. Det:
- Scraper nye stevner fra minfriidrettsstatistikk.info
- Sammenligner med eksisterende stevner i DB
- Importerer resultater direkte (ingen mellom-CSV)
- Matcher/oppretter utøvere, klubber, stevner
- Logger alt med Python `logging`

### Historisk import
```bash
python import_historical.py    # All-time statistikk fra friidrett.no
```
Brukes sjelden. Har 3-nivå duplikatdeteksjon.

### Fødselsår-backfill
```bash
python backfill_birth_years.py --dry-run   # Forhåndsvisning
python backfill_birth_years.py             # Kjør oppdatering
python backfill_birth_years.py --letters A B C  # Kun spesifikke bokstaver
```
Henter fødselsår fra kilden for utøvere som mangler. Trygt å kjøre flere ganger.

### Vedlikehold
```bash
python merge_duplicate_meets.py   # Slå sammen duplikate stevner
```

## Utdaterte scripts

Mappen inneholder ~70 scripts fra utviklingsfasen. De fleste er **engangs-scripts** som fikset spesifikke dataproblemer. Se `CLAUDE.md` i prosjektroten for liste over scripts som **ALDRI** skal kjøres igjen.

Viktigste advarsler:
- **`fix_missing_gender_batch.py`** — Skapte massiv kjønnsfeil. Se `FIX_GENDER_README.md`.
- **`cleanup_duplicates*.py`** — Gamle versjoner. Duplikathåndtering er nå innebygd i `update_results.py`.
- **`fix_all_times*.py`** — Gamle tidsfiks. Tidsformat håndteres nå i import-logikken.

## Filstruktur

```
scraper/
  update_results.py        # Hovedscript
  import_historical.py     # Historisk import
  backfill_birth_years.py  # Fødselsår
  merge_duplicate_meets.py # Duplikat-vedlikehold
  new_meets_data/          # Midlertidige filer fra scraping
  migrations/              # SQL-migrasjoner
  logs/                    # Loggfiler
  OPERATIONS_LOG.md        # Operasjonslogg — hva er kjørt og når
  FIX_GENDER_README.md     # Dokumentasjon om kjønnsproblematikk
```

## Dataformat

| Felt | Tidsøvelser | Feltøvelser |
|------|-------------|-------------|
| `performance` | Sekunder som string ("214.32" = 3:34.32) | Meter som string ("8.95") |
| `performance_value` | Millisekunder (214320) | Centimeter (895) |

## Miljøvariabler

`.env` i scraper-mappen:
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJxxx...
```

## Logging

Alle scripts skal bruke Python `logging`-modulen. For operasjoner som endrer data, logg også til fil:
```python
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
```

**Husk:** Oppdater `OPERATIONS_LOG.md` etter hver kjøring.

## Sist oppdatert

**2026-02-13**
