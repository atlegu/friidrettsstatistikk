#!/usr/bin/env python3
"""Trekker ut Trenerseminaret 2026 (sidene 5-8 i bladet) som egen PDF til Trenerforeningen."""
from pathlib import Path
from pypdf import PdfReader, PdfWriter
here = Path(__file__).resolve().parent
r = PdfReader(str(here / 'Fagnytt_pilot.pdf'))
w = PdfWriter()
for i in range(4, 8):
    w.add_page(r.pages[i])
w.add_metadata({'/Title': 'Trenerseminaret 2026 – program', '/Author': 'Friidrettens Trenerforening'})
ut = here / 'Trenerseminaret_2026_program.pdf'
with open(ut, 'wb') as f:
    w.write(f)
print('Skrev', ut)
