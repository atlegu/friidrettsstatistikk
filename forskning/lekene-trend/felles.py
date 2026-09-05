"""
felles.py - delt tolkning av resultatstrenger for lekene-analysene.

Kilden lagrer tider i flere formater ("5:41.20", "5.41" = 5:41, "1.45" = 1:45,
"82,3"). performance_value i basen er feil for M.SS-radene (541 for 5:41), så
analysene bruker den tolkede kolonnen `verdi` i stedet.
"""

import re

import numpy as np

# Løp kortere enn 800 m kan være manuelt tidtatt; tideler = manuell (prosjektregel).
SPRINT = {"60m", "200m", "60mh_68cm", "60mh_76_2cm", "80mh_84cm", "200mh_68cm", "200mh_76_2cm"}
# Øvelser der en tid under 60 s er umulig: "M.SS" betyr minutter.sekunder.
MELLOM = {"600m", "1500m", "kappgang_1000_m"}


def parse_verdi(s, code, rtype):
    """Resultat i sekunder (tid) eller meter (hopp/kast); NaN hvis uleselig."""
    s = str(s).strip().replace(",", ".")
    if s in ("", "nan", "None"):
        return np.nan
    try:
        if ":" in s:
            m, sec = s.split(":", 1)
            return 60 * float(m) + float(sec)
        v = float(s)
    except ValueError:
        return np.nan
    if rtype == "time" and code in MELLOM and v < 60:
        m, _, sec = s.partition(".")
        sec = sec.ljust(2, "0")
        return 60 * int(m) + int(sec[:2]) + (float("0." + sec[2:]) if len(sec) > 2 else 0.0)
    return v


def manuell_presisjon(s, code):
    """True når en sprint-/hekketid er oppgitt i tideler (manuell tidtaking)."""
    return code in SPRINT and re.fullmatch(r"\d+[.,]\d", str(s).strip()) is not None
