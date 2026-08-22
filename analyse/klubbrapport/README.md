# klubbrapport

Felles maskineri for klubbrapportene. En klubb trenger bare to filer:
`kjor.py` med konfigurasjonen, og `stipend.py` med klubbens stipendliste.

## Legge til en ny klubb

```python
# nyklubb/kjor.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import klubbrapport
import stipend

KONFIG = klubbrapport.Konfig(
    klubb_id='<uuid fra clubs-tabellen>',
    klubb_navn='Navn på klubben',
    mappe=Path(__file__).resolve().parent,
    antall_resultater=3,        # standard er 2
    ar=[2024, 2025, 2026],      # standard
    min_alder=15,               # standard
)

if __name__ == '__main__':
    klubbrapport.kjor(KONFIG, stipend, hent_data='--rapport' not in sys.argv)
```

```bash
./kjor.py              # uttrekk fra basen, HTML, CSV og PDF
./kjor.py --rapport    # bygg rapporten på nytt fra lagret uttrekk
```

## Moduler

| Fil | Ansvar |
|---|---|
| `hent.py` | Uttrekk fra databasen, klubbskifteregler, aldersfilter |
| `rapport.py` | HTML og CSV |
| `stil.py` | Stilark for skjerm og utskrift |
| `pdf.py` | PDF via headless Chrome |
| `navn.py` | Navnekobling mellom stipendliste og database |

## Stipendadapteren

Klubbens `stipend.py` må ha:

| Funksjon | Returnerer |
|---|---|
| `FLAT` | `navn -> opplysninger` for hele stipendlisten |
| `finn(db_navn)` | `(navn, info)` eller `None` |
| `merke(info)` | HTML-merke etter utøvernavnet |
| `detalj(info)` | HTML-bit i metalinja |
| `seksjoner(stip, alle, yngst)` | `[(tittel, undertittel, [aid, …]), …]` — også «Øvrige» |
| `ikke_funnet_linje(navn, info)` | tekst i lista over ukoblede tildelinger |
| `sammendrag(stip)` | setning i sammendragspanelet |
| `csv_kolonner()` / `csv_verdier(info)` | stipendfeltene i CSV-en |

Seksjonsinndelingen er adapterens ansvar. Vidar har én stipendseksjon sortert
på alder; Tjalve har én seksjon per gruppe A–D sortert på poengsum. Begge
legger «Øvrige utøvere» til slutt.

## Erfaringer som er bygget inn

**Paginering må være nøkkelbasert.** `.range()` uten `order by` gir ikke stabil
rekkefølge i PostgREST, og over 1,4 millioner resultatrader mistet vi rader.
`hent.py` blar med `order('id')` + `gt('id', forrige)`.

**Fødselsår må valideres.** Basen har hatt verdier som 0, 752 og 9171. De er
ryddet, men uttrekket sjekker likevel — et aldersfilter skal aldri stole blindt
på feltet.

**PDF-fonten må ikke være macOS-systemfonten.** Chrome bygger den inn som
Type 3, som rendres med striper i mange lesere og ikke lar seg søke i.
Utskriftsstilen bruker derfor Helvetica Neue.

**Navn skrives ulikt i de to kildene.** `navn.py` prøver tre trinn fra
strengest til mildest og stopper ved første treff. Siste trinn godtar bare
entydige treff.
