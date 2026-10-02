# IK Tjalve 2024–2026

Uttrekk av alle utøvere 15 år og eldre som har representert IK Tjalve, med
antall starter og **de tre beste** resultatene per øvelse per år.

## Kjøring

```bash
./kjor.py            # uttrekk, html, csv og pdf
./kjor.py --rapport  # bygg rapporten på nytt fra lagret uttrekk
```

## Filer

| Fil | Innhold |
|---|---|
| `tjalve_2024_2026.pdf` | Utskriftsvennlig versjon, A4 |
| `tjalve_2024_2026.html` | Søkbar oversikt, én seksjon per utøver |
| `tjalve_2024_2026.csv` | Flat tabell, semikolon og BOM for norsk Excel |
| `stipend.py` | Idrettsstipend 2026 fra `Stipend-2026.pdf` |
| `data.json` | Mellomlagret datagrunnlag |

## Rekkefølge

Stipendmottakerne først, gruppe A, deretter B, C og D. Innenfor hver gruppe
står den med høyest poengsum for 2025 øverst, slik klubbens eget
tildelingsdokument er ordnet. Utøvere uten poengsum — tildelt etter
bestemmelsen om skade, sykdom eller graviditet — står sist i sin gruppe.

Etter stipendmottakerne kommer øvrige utøvere med yngste først.

## Stipend

`Stipend-2026.pdf` tildeler 34 utøvere til gruppene A–D, med gren, poengsum
for 2025 og eventuelt mesterskap. Alle 34 er koblet mot databasen.

**Navnekobling** skjer i tre trinn, fra strengest til mildest, og stopper ved
første treff:

1. Likt fornavn (aksenttolerant, ett tegns avvik) og alle stipendlistens
   øvrige navneledd gjenfunnet hos utøveren.
2. Samme, men med ett tegns avvik også på navneleddene —
   «Thale Leirfall Bremseth» mot «Thale Leirfall Bremset».
3. Bare fornavn og etternavn, når mellomnavnet mangler i basen —
   «Malin Ingeborg Nyfors» mot «Malin Nyfors». Godtas kun hvis det gir
   nøyaktig ett treff.

## Regler om klubbskifte

1. **Nye i Tjalve.** Er utøverens første Tjalve-sesong senere enn 2024, tas
   sesongene fra før overgangen med, med klubben de da representerte.
   Fargekodet i rapporten.
2. **Sluttet i Tjalve.** Utøvere med Tjalve-resultater i 2024 eller 2025 som i
   2026 konkurrerer for en annen klubb og ikke for Tjalve, er tatt ut.

## Definisjoner

- **Klubbtilhørighet** hentes fra `results.club_id` — klubben utøveren faktisk
  representerte i det enkelte stevnet.
- **Alder** regnes etter kalenderår: konkurranseår minus fødselsår.
  Se CLAUDE.md punkt 6.
- **Beste resultat**: laveste `performance_value` for tidsøvelser, høyeste for
  lengde, høyde og poeng.

## Felles kode

Selve maskineriet ligger i `../klubbrapport/`. Denne mappen har bare
konfigurasjonen (`kjor.py`) og klubbens stipendliste (`stipend.py`).
