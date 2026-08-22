"""
Utøverstipend 2026, hentet fra «SKV budsjett 2026 - v1.pdf», seksjonen
«Utøverbudsjetter». Beløp i hele kroner.

Navnene er skrevet slik de står i budsjettet. De er ofte kortere enn navnet i
resultatdatabasen («Anthony Johnsen» mot «Anthony Ommundsen Johnsen»), så
koblingen skjer på fornavn + etternavn, ikke på hele strengen.
"""

import unicodedata

STIPEND = {
    'OL/VM': {
        'Sondre Guttormsen': 215_000,
        'Simen Guttormsen': 185_500,
        'Sondre Nordstad Moen': 182_500,
    },
    'EM': {
        'Amalie Sæten': 135_000,
        'Henrik Flåtnes': 165_000,
        'Elea Bock': 126_000,
    },
    'Elite A': {
        'Jonathan Ødegaard': 118_000,
        'Vilde Våge Henriksen': 80_000,
        'Line Kloster': 83_000,
        'Anna Marie Sirevåg': 66_000,
        'Lovise Andresen': 80_000,
        'Madeleine Holum': 62_000,
        'Kristine Rød': 60_000,
        'Ingrid Rismark': 60_000,
        'Susanne Tveit Amundsen': 60_000,
        'Anthony Johnsen': 88_000,
        'Kaja Mørch Pettersen': 80_000,
        'Kristoffer Randall': 60_000,
        'Sjur Prestsæter': 60_000,
        'Sunniva Andersen': 60_000,
        'Ilona Mononen': 50_000,
    },
    'Elite B': {
        'Simen Gimnes': 58_000,
        'Frida Konow': 40_000,
        'Rachel Ombeni': 48_000,
        'Sander Mathiesen': 50_000,
        'Emiliano Røgeberg': 30_000,
        'Lina Svarlien': 30_000,
        'Oda Lier': 30_000,
        'Ine Bakken': 40_000,
        'Stine Holager': 40_000,
        'Malene Kollberg': 40_000,
        'Marte Lien Johnsen': 30_000,
        'Mathilde Knutsen': 30_000,
        'Sara Lie': 30_000,
        'Emilie Mo': 30_000,
        'Bethina Valle': 30_000,
    },
    'Fjelløping': {
        'Sylvia Nordskar': 50_000,
        'Ida Robsam': 50_000,
    },
    'OCR': {
        'Signy Karoline Kolstø': 50_000,
        'Ånung Viken': 30_000,
    },
}

# Rekkefølgen kategoriene skal vises i
KATEGORIER = ['OL/VM', 'EM', 'Elite A', 'Elite B', 'Fjelløping', 'OCR']

# Flat oppslagstabell: navn -> (beløp, kategori)
FLAT = {navn: (belop, kat)
        for kat, poster in STIPEND.items()
        for navn, belop in poster.items()}


def _folde(s: str) -> str:
    """Fjern aksenter, så «Madelène» og «Madeleine» kan sammenlignes.
    Norske æ, ø og å beholdes — de er egne bokstaver, ikke aksenter."""
    ut = []
    for tegn in unicodedata.normalize('NFD', s.lower()):
        if tegn in 'æøå' or unicodedata.category(tegn) != 'Mn':
            ut.append(tegn)
    return ''.join(ut)


def _naer(a: str, b: str) -> bool:
    """Likt, eller ett tegn fra hverandre (Madelene/Madeleine)."""
    if a == b:
        return True
    if abs(len(a) - len(b)) > 1:
        return False
    kort, lang = sorted((a, b), key=len)
    for i in range(len(lang)):
        if lang[:i] + lang[i + 1:] == kort:
            return True
    return len(a) == len(b) and sum(x != y for x, y in zip(a, b)) == 1


def _deler(navn: str):
    """Fornavn og alle øvrige navneledd, oppdelt også på bindestrek."""
    ord_ = [o for o in _folde(navn).replace('.', '').split() if o]
    if not ord_:
        return '', set()
    resten = set()
    for o in ord_[1:]:
        resten.add(o)
        resten.update(d for d in o.split('-') if d)
    return ord_[0], resten


def finn_stipend(db_navn: str):
    """Slå opp et navn fra databasen mot budsjettlisten.

    Budsjettet bruker kortformer: «Jonathan Ødegaard» er «Jonathan
    Hertwig-Ødegaard» i basen, og «Emiliano Røgeberg» er «Emiliano Storm
    Røgeberg-Ortiz». Kravet er derfor likt fornavn, og at budsjettets
    etternavn finnes som et navneledd hos utøveren. Mellomnavn i budsjettet
    må også gjenfinnes, slik at «Anna Marie Sirevåg» ikke treffer en annen Anna.

    Returnerer (budsjettnavn, beløp, kategori) eller None.
    """
    fornavn, ledd = _deler(db_navn)
    for navn, (belop, kat) in FLAT.items():
        b_fornavn, b_ledd = _deler(navn)
        if b_ledd and b_ledd <= ledd and _naer(fornavn, b_fornavn):
            return navn, belop, kat
    return None
