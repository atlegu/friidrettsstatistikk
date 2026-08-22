# Fana IL 2024–2026

Uttrekk av alle utøvere 15 år og eldre som har representert Fana IL, med
antall starter og de tre beste resultatene per øvelse per år.

**Merk aldersgrensen.** Fana har 139 utøvere med resultater i perioden, men
1 133 av startene kommer fra utøvere under 15 år. Etter aldersfilteret står
53 utøvere igjen. Klubben er altså tung på de yngste årsklassene — senk
`min_alder` i `kjor.py` hvis hele bredden skal med.

## Kjøring

```bash
./kjor.py            # uttrekk, html, csv og pdf
./kjor.py --rapport  # bygg rapporten på nytt fra lagret uttrekk
```

## Rekkefølge

Prioritetslisten fra klubben står øverst, i nøyaktig den rekkefølgen den ble
oppgitt — den er meningsbærende og sorteres ikke om. Alle 16 navnene er funnet
i basen. Fem av dem står med lengre navn der enn på listen, blant andre
«Benjamin Christensen Moen» → «Benjamin Moen» og
«Andreas Gjesdal» → «Andreas F. T. Gjesdal».

Etter prioritetslisten kommer øvrige utøvere med yngste først.

## Felles kode

Maskineriet ligger i `../klubbrapport/`. Denne mappen har bare
konfigurasjonen og prioritetslisten i `kjor.py`.
