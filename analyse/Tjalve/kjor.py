#!/usr/bin/env python3
"""IK Tjalve 2024–2026. Hele kjeden: uttrekk, HTML, CSV og PDF.

    ./kjor.py            alt
    ./kjor.py --rapport  bygg rapporten på nytt fra lagret uttrekk
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import klubbrapport
import stipend

KONFIG = klubbrapport.Konfig(
    klubb_id='d38f1050-45c0-40a5-af81-4215edb599fe',
    klubb_navn='IK Tjalve',
    mappe=Path(__file__).resolve().parent,
    antall_resultater=3,
)

if __name__ == '__main__':
    klubbrapport.kjor(KONFIG, stipend, hent_data='--rapport' not in sys.argv)
