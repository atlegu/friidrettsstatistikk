# [Prosjekttittel]

## Forskningsspørsmål

_Beskriv forskningsspørsmålet/hypotesen._

## Bakgrunn

_Kort om motivasjon og relevant litteratur._

## Data

- **Tabeller brukt**: (f.eks. results_full, athletes, meets)
- **Tidsperiode**: (f.eks. 2015–2025)
- **Utvalg**: (f.eks. senior menn, 100m, elektronisk tidtaking)
- **Utvalgsstørrelse**: N = _
- **Eksklusjonskriterier**: (f.eks. manuell tidtaking, ulovlig vind, DNS/DNF)
- **Kjente begrensninger**: (f.eks. kjønnsproblematikk, historisk dekning)

## Metode

_Beskriv analysemetoden (deskriptiv statistikk, regresjon, etc.)._

## Datauttrekk

Script: `data/uttrekk.py`

```sql
-- Eksempel-query for datauttrekk
SELECT ...
FROM results_full
WHERE ...
```

## Resultater

_Oppsummer funn._

## Konklusjon

_Kort konklusjon og implikasjoner._

## Filer

| Fil | Beskrivelse |
|-----|-------------|
| `data/uttrekk.py` | Datauttrekk fra Supabase |
| `data/datasett.csv` | Uttrekket datasett |
| `analyse/analyse.py` | Analysescript |
| `resultater/figurer/` | Genererte figurer |
