#!/usr/bin/env python3
"""Fana IL 2024–2026. Hele kjeden: uttrekk, HTML, CSV og PDF.

    ./kjor.py            alt
    ./kjor.py --rapport  bygg rapporten på nytt fra lagret uttrekk

Utøverne på prioritetslisten står øverst i den rekkefølgen de er oppgitt.
Resten kommer etter, yngste først.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import klubbrapport

# Oppgitt rekkefølge fra klubben. Blanklinjene i den opprinnelige listen er
# beholdt som grupperinger her, men rekkefølgen er det som styrer visningen.
PRIORITERT = klubbrapport.Prioritert([
    'Pål Haugen Lillefosse',
    'Lene Onsrud Retzius',

    'Kitty Friele Faye',
    'Tobias Heldal',
    'Embla Adele Østreim Øina',

    'Philip Andreas Kubon',
    'Benjamin Christensen Moen',
    'Andreas Gjesdal',

    'Teodor Heldal',
    'Gustav Vincent Holmefjord',
    'Andreas Joseph Dixon',
    'Mathias Myrmel Herdlevær',
    'Odin Østreim Øina',
    'Kjell Augustin Kubon',
    'Martine Vik',
    'Thea Emilie Turøy',
])

KONFIG = klubbrapport.Konfig(
    klubb_id='a864b676-bb93-41d4-a9f9-9ebffd5c787e',
    klubb_navn='Fana IL',
    mappe=Path(__file__).resolve().parent,
)

if __name__ == '__main__':
    klubbrapport.kjor(KONFIG, PRIORITERT, hent_data='--rapport' not in sys.argv)
