#!/usr/bin/env python3
"""Bygger Trenerseminaret 2026 som egen PDF (fire sider, egen topptekst, uten sidetall) til Trenerforeningen.

Bruker blad/artikler/seminar.tex (samme innhold som i bladet) og blad/program_main.tex.
    python3 lag_program_pdf.py
"""
import shutil, subprocess
from pathlib import Path
here = Path(__file__).resolve().parent
blad = here / 'blad'
for _ in range(2):
    r = subprocess.run(['xelatex', '-interaction=nonstopmode', '-halt-on-error', 'program_main.tex'],
                       cwd=blad, capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-3000:]); raise SystemExit(1)
shutil.copy(blad / 'program_main.pdf', here / 'Trenerseminaret_2026_program.pdf')
print('Skrev', here / 'Trenerseminaret_2026_program.pdf')
