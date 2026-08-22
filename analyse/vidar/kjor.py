#!/usr/bin/env python3
"""Sportsklubben Vidar 2024–2026. Hele kjeden: uttrekk, HTML, CSV og PDF.

    ./kjor.py            alt
    ./kjor.py --rapport  bygg rapporten på nytt fra lagret uttrekk
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import klubbrapport
import stipend

KONFIG = klubbrapport.Konfig(
    klubb_id='fcfc0ff6-787b-4471-acb6-5705fd7b48d8',
    klubb_navn='Sportsklubben Vidar',
    mappe=Path(__file__).resolve().parent,
)

if __name__ == '__main__':
    klubbrapport.kjor(KONFIG, stipend, hent_data='--rapport' not in sys.argv)
