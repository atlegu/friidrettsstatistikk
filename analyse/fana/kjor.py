#!/usr/bin/env python3
"""Fana IL 2024–2026. Hele kjeden: uttrekk, HTML, CSV og PDF.

    ./kjor.py            alt
    ./kjor.py --rapport  bygg rapporten på nytt fra lagret uttrekk

Klubben har ingen stipendliste, så utøverne listes samlet med yngste først.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import klubbrapport

KONFIG = klubbrapport.Konfig(
    klubb_id='a864b676-bb93-41d4-a9f9-9ebffd5c787e',
    klubb_navn='Fana IL',
    mappe=Path(__file__).resolve().parent,
)

if __name__ == '__main__':
    klubbrapport.kjor(KONFIG, klubbrapport.uten_stipend,
                      hent_data='--rapport' not in sys.argv)
