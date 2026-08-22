"""
Idrettsstipend 2026 for IK Tjalve, hentet fra «Stipend-2026.pdf».

Tildelingen er gruppebasert (A til D), ikke beløpsbasert. Dokumentet oppgir
også gren, poengsum for 2025 og eventuelt mesterskap utøveren deltok i.

Markus Rooth står i en egen tabell nederst: medlemmer som fikk stipend første
år, men har hatt tilbakegang på grunn av graviditet, skade eller sykdom,
beholder normalt samme støtte. Han har derfor ingen poengsum for 2025.
"""

import unicodedata

# (navn, gren, poeng 2025, mesterskap, gruppe)
TILDELINGER = [
    ('Sander Skotheim',            'Mangekamp', 1251, 'VM (2025)', 'A'),
    ('Amalie Hammild Iuel',        'Løp',       1190, 'VM (2025)', 'A'),
    ('Karoline Bjerkeli Grøvdal',  'Løp',       1180, 'OL (2024)', 'A'),
    ('Magnus Tuv Myhre',           'Løp',       1177, None,        'A'),
    ('Tobias Grønstad',            'Løp',       1174, 'VM (2025)', 'A'),
    ('Awet Nftalem Kibrab',        'Løp',       1155, 'VM (2025)', 'A'),
    ('Eivind Prestegård Henriksen','Kast',      1150, 'VM (2025)', 'A'),
    ('Sigrid Borge',               'Kast',      1136, 'VM (2025)', 'A'),
    ('Ingeborg Østgård',           'Løp',       1131, 'VM (2025)', 'A'),
    ('Anne Gine Løvnes',           'Løp',       1122, 'VM (2025)', 'A'),
    ('Marie-Therese Obst',         'Kast',      1071, 'VM (2025)', 'A'),
    ('Markus Rooth',               'Mangekamp', None, 'OL (2024)', 'A'),

    ('Malin Ingeborg Nyfors',      'Løp',       1133, None,        'B'),
    ('Ida Andrea Breigan',         'Hopp',      1130, None,        'B'),
    ('Amanda Frøynes',             'Løp',       1125, None,        'B'),
    ('Astri Ayo Lakeri Ertzgaard', 'Løp',       1124, 'VM (2025)', 'B'),
    ('Andreas Ofstad Kulseng',     'Løp',       1123, None,        'B'),
    ('Ferdinand Kvan Edman',       'Løp',       1113, None,        'B'),
    ('Abraham Vogelsang',          'Mangekamp', 1109, None,        'B'),

    ('Kenny Emi Tijani-Ajayi',     'Løp',       1097, None,        'C'),
    ('Line Al Saiddi',             'Løp',       1085, None,        'C'),
    ('Maren Bakke Amundsen',       'Løp',       1081, None,        'C'),
    ('Laura Van Der Veen',         'Løp',       1069, None,        'C'),
    ('Sigrid Jervell Våg',         'Løp',       1056, None,        'C'),

    ('Mikkel Blikstad Thomassen',  'Løp',       1041, None,        'D'),
    ('Maiken Prøitz',              'Løp',       1029, None,        'D'),
    ('Nora Aune',                  'Løp',       1026, None,        'D'),
    ('Senay Fissehatsion',         'Løp',       1020, None,        'D'),
    ('Sunniva Indahl',             'Mangekamp', 1018, None,        'D'),
    ('Vilde Humstad Aasmo',        'Løp',       1012, None,        'D'),
    ('Kaitesi Ertzgaard',          'Løp',       1011, None,        'D'),
    ('Sara Busic',                 'Løp',       1009, None,        'D'),
    ('Marius Bull Hjeltnes',       'Hopp',      1006, None,        'D'),
    ('Thale Leirfall Bremseth',    'Hopp',      1005, None,        'D'),
]

GRUPPER = ['A', 'B', 'C', 'D']

FLAT = {navn: {'gren': gren, 'poeng': poeng, 'mesterskap': mst, 'gruppe': gr}
        for navn, gren, poeng, mst, gr in TILDELINGER}


def _folde(s: str) -> str:
    """Fjern aksenter, men behold æ, ø og å — de er egne bokstaver."""
    ut = []
    for tegn in unicodedata.normalize('NFD', s.lower()):
        if tegn in 'æøå' or unicodedata.category(tegn) != 'Mn':
            ut.append(tegn)
    return ''.join(ut)


def _naer(a: str, b: str) -> bool:
    """Likt, eller ett tegn fra hverandre."""
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
    ord_ = [o for o in _folde(navn).replace('.', '').split() if o]
    if not ord_:
        return '', set()
    resten = set()
    for o in ord_[1:]:
        resten.add(o)
        resten.update(d for d in o.split('-') if d)
    return ord_[0], resten


def finn_stipend(db_navn: str):
    """Slå opp et navn fra databasen mot stipendlisten.

    Krever likt fornavn (aksenttolerant, ett tegns avvik) og at ALLE
    stipendlistens øvrige navneledd finnes hos utøveren. Etternavn i
    stipendlisten kan være kortformer av sammensatte navn i basen.

    Returnerer (navn, opplysninger) eller None.
    """
    fornavn, ledd = _deler(db_navn)
    for navn, info in FLAT.items():
        b_fornavn, b_ledd = _deler(navn)
        if b_ledd and b_ledd <= ledd and _naer(fornavn, b_fornavn):
            return navn, info
    # Etternavn kan være skrevet med ulik endelse i de to kildene
    # («Bremseth» mot «Bremset»), så prøv en runde til med tegnavvik.
    for navn, info in FLAT.items():
        b_fornavn, b_ledd = _deler(navn)
        if not b_ledd or not _naer(fornavn, b_fornavn):
            continue
        if all(any(_naer(bl, l) for l in ledd) for bl in b_ledd):
            return navn, info

    # Til slutt: mellomnavnet kan mangle i BASEN i stedet for i stipendlisten
    # («Malin Ingeborg Nyfors» mot «Malin Nyfors»). Da holder fornavn og
    # etternavn — men bare hvis det gir nøyaktig ett treff, ellers er det
    # ikke trygt å gjette.
    kandidater = []
    for navn, info in FLAT.items():
        b_ord = _folde(navn).split()
        if len(b_ord) < 2 or not _naer(fornavn, b_ord[0]):
            continue
        if any(_naer(b_ord[-1], l) for l in ledd):
            kandidater.append((navn, info))
    return kandidater[0] if len(kandidater) == 1 else None
