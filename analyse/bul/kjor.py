#!/usr/bin/env python3
"""IL i BUL 2024–2026. Hele kjeden: uttrekk, HTML, CSV og PDF.

    ./kjor.py            alt
    ./kjor.py --rapport  bygg rapporten på nytt fra lagret uttrekk

Klubben har ingen stipendliste, så utøverne listes samlet med yngste først.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import klubbrapport

KONFIG = klubbrapport.Konfig(
    klubb_id='814e5ce8-b9f2-4d10-949c-d4e7bb3169a6',
    klubb_navn='IL i BUL',
    mappe=Path(__file__).resolve().parent,
)

if __name__ == '__main__':
    klubbrapport.kjor(KONFIG, klubbrapport.uten_stipend,
                      hent_data='--rapport' not in sys.argv)
