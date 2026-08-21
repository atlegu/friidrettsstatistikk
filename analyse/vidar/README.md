# Sportsklubben Vidar 2024–2026

Uttrekk av alle utøvere 15 år og eldre som har representert Sportsklubben Vidar,
med antall starter og beste/nestbeste resultat per øvelse per år.

## Kjøring

```bash
../../scraper/venv/bin/python hent_vidar.py     # henter data -> vidar_data.json
../../scraper/venv/bin/python lag_rapport.py    # bygger html + csv
./lag_pdf.sh                                    # alt tre stegene + pdf
```

## Filer

| Fil | Innhold |
|---|---|
| `vidar_2024_2026.html` | Søkbar oversikt, én seksjon per utøver |
| `vidar_2024_2026.csv` | Flat tabell, semikolon og BOM for norsk Excel |
| `vidar_2024_2026.pdf` | Utskriftsvennlig versjon, A4 |
| `vidar_data.json` | Mellomlagret datagrunnlag |

## Regler om klubbskifte

1. **Nye i Vidar.** Er utøverens første Vidar-sesong senere enn 2024, tas
   sesongene fra før overgangen med, med klubben de da representerte. Disse er
   fargekodet i HTML-rapporten og har egen klubbkolonne i CSV-en.
2. **Sluttet i Vidar.** Utøvere med Vidar-resultater i 2024 eller 2025 som i
   2026 konkurrerer for en annen klubb og ikke for Vidar, er tatt ut av listen.
   De er listet i egen tabell øverst i rapporten.

## Definisjoner

- **Klubbtilhørighet** hentes fra `results.club_id` — klubben utøveren faktisk
  representerte i det enkelte stevnet, ikke `athletes.current_club_id`.
- **Alder** regnes etter kalenderår: konkurranseår minus fødselsår, uten
  justering for bursdag. Se CLAUDE.md punkt 6.
- **Beste resultat**: laveste `performance_value` for tidsøvelser, høyeste for
  lengde, høyde og poeng.
- **Starter** er antall registrerte resultater. Alle har status OK i perioden.

## Merknad om datakvalitet

Én utøver (Kasper Ellingsen, 1 start) er holdt utenfor fordi fødselsåret er
registrert som `0`. Basen har 56 utøvere med ugyldig fødselsår totalt
(0, 752, 1006, 1070, 1777, 2097, 2995, 9171, 9194 m.fl.), som berører 92
resultater. Uten validering slipper de gjennom aldersfiltre — fødselsår 0 gir
«2026 år» i 2026.
