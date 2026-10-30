"""Shared paths for the R1 pipeline.

DATA  — the original pipeline folder in the main checkout (scripts 07-16, Tyrving workbook, original
        data files; read-only).
CDATA — the corrected cohort, career and analysis data written by r1_00_corrected_data.py
        (athlete-level, git-ignored). Every R1 analysis reads its data from here.
"""

from pathlib import Path

HERE = Path(__file__).parent
R1 = HERE.parent
DATA = Path("/Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/Statistikk/forskning/ncc-kohort/data")
PRIV = R1 / "data_private"
CDATA = PRIV / "corrected"
ENV = Path("/Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/Statistikk/scraper/.env")

# register state used throughout: rows created on or before the original extraction
CUTOFF = "2026-05-18T00:00:00+00:00"
# follow-up ends with the last complete season
FOLLOW_UP_END = "2025-12-31"
