# Forskningsprosjekter — friidrett.live

Denne mappen inneholder forskningsprosjekter som bruker data fra friidrett.live-databasen.

## Tilgjengelige data

Databasen (Supabase/Postgres) inneholder norsk friidrettsstatistikk med følgende omfang:

| Tabell | Rader | Beskrivelse |
|--------|-------|-------------|
| `athletes` | ~78 800 | Utøvere med navn, kjønn, fødselsår, klubb, nasjonalitet |
| `results` | ~1 250 000 | Enkeltresultater med prestasjon, vind, plassering, runde, tidtakingstype |
| `meets` | ~47 000 | Stevner med dato, sted, nivå (lokal→internasjonal), innendørs/utendørs |
| `events` | 299 | Øvelser med kategori (sprint, hopp, kast, ...) og resultattype (tid/avstand/høyde/poeng) |
| `clubs` | ~2 400 | Klubber med by, fylke, type (friidrett, BIL, skole, utenlandsk) |
| `age_classes` | 56 | Aldersklasser (G/J 10–19, senior, veteran) |
| `championship_medals` | ~13 600 | NM-medaljer (innendørs/utendørs) med år, øvelse, utøver |
| `seasons` | 182 | Sesonger (år + innendørs/utendørs) |
| `event_specifications` | 74 | Redskaps-/hekkvekter per aldersklasse |

### Nøkkelviews
- **`results_full`** — Hovedview som joiner results + athletes + meets + events + clubs + seasons. Inkluderer beregnet aldersgruppe.
- **`personal_bests`** / **`personal_bests_detailed`** — Personlige rekorder per utøver per øvelse.
- **`season_bests`** — Sesongbeste per utøver.

### Viktige datafelter i `results`
- `performance` — Tid i sekunder som tekst ("10.45") eller avstand ("8.95")
- `performance_value` — Normalisert heltall for sortering (hundredeler for tid, centimeter for avstand)
- `wind` — Vindmåling i m/s (NULL hvis ikke målt)
- `is_manual_time` — Manuell tidtaking (kun sprint <800m)
- `is_wind_legal` — Om vind er innenfor lovlig grense (≤2.0 m/s)
- `reaction_time` — Reaksjonstid
- `attempts` — Forsøksserier for tekniske øvelser (JSON)
- `splits` — Mellomtider for løp (JSON)
- `round` — Runde (heat, semi, finale, etc.)

## Datakvalitet — kjente begrensninger

1. **Kjønn**: ~30 000 utøvere mangler kjønn (NULL). Noen har feil kjønn pga. batch-inferens. Filtrering på kjønn gir ufullstendige datasett.
2. **Tidsperiode**: Hovedsakelig data fra 2012+. Historisk data (pre-2012) er kun over visse prestasjonsterskler.
3. **Fødselsår**: Nesten komplett (kun ~30 mangler), men noen kan ha feil.
4. **Manuell tidtaking**: `is_manual_time = NULL` betyr elektronisk (ikke ukjent). Bruk `IS NOT TRUE` i SQL.

## Mappestruktur

```
forskning/
  README.md              ← Denne filen
  maler/
    prosjektmal.md       ← Mal for nye forskningsprosjekter
    datauttrekk.py       ← Python-mal for datauthenning fra Supabase
  <prosjektnavn>/        ← Ett undermappe per forskningsprosjekt
    README.md
    data/
    analyse/
    resultater/
```

## Kom i gang

1. Kopier `maler/prosjektmal.md` til en ny mappe under `forskning/`
2. Tilpass `maler/datauttrekk.py` for ditt datauttrekk
3. Dokumenter metode, funn og begrensninger i prosjektets README

## Tilgang til databasen

Forskere trenger Supabase-credentials (URL + service key) som settes i `.env`:
```
SUPABASE_URL=https://lwkykthpnthfcldifixg.supabase.co
SUPABASE_SERVICE_KEY=<service-key>
```

Se `maler/datauttrekk.py` for eksempel på oppkobling.

## Forskningsetikk

- Dataene er offentlige konkurranseresultater, men vær oppmerksom på personvern ved publisering
- Utøvere under 16 bør behandles med ekstra varsomhet
- Ikke publiser individuelle utøveridentiteter i negative kontekster (frafall, skadeindikasjon, etc.)
- Følg institusjonens retningslinjer for forskningsetikk
