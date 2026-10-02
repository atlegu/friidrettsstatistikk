"""Standardadapter for klubber uten stipendliste.

Gir én enkelt seksjon med alle utøvere, yngste først. Ingen merker, ingen
ekstra kolonner i CSV-en. Bruk denne til `klubbrapport.kjor(KONFIG,
klubbrapport.uten_stipend)`.
"""

FLAT = {}


def finn(db_navn):
    return None


def merke(info):
    return ''


def detalj(info):
    return ''


def seksjoner(stip, alle, yngst_forst):
    ut = yngst_forst(alle)
    return [('Utøvere ', f'{len(ut)} · yngste først', ut)]


def ikke_funnet_linje(navn, info):
    return navn


def sammendrag(stip):
    return ''


def csv_kolonner():
    return []


def csv_verdier(info):
    return []
