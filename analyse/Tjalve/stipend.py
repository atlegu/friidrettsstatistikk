"""Idrettsstipend 2026 for IK Tjalve, fra «Stipend-2026.pdf».

Tildelingen er gruppebasert (A til D), ikke beløpsbasert. Dokumentet oppgir
også gren, poengsum for 2025 og eventuelt mesterskap.

Markus Rooth står i en egen tabell nederst: medlemmer som fikk stipend første
år, men har hatt tilbakegang på grunn av graviditet, skade eller sykdom,
beholder normalt samme støtte. Han har derfor ingen poengsum.
"""

from html import escape

from klubbrapport import navn as _navn

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
FLAT = {n: {'gren': g, 'poeng': p, 'mesterskap': m, 'gruppe': gr}
        for n, g, p, m, gr in TILDELINGER}


def finn(db_navn):
    return _navn.finn(db_navn, FLAT)


def merke(info):
    return f' <span class="stipend">{info["gruppe"]}</span>'


def detalj(info):
    biter = [info['gren']]
    if info['poeng']:
        biter.append(f'{info["poeng"]} p')
    if info['mesterskap']:
        biter.append(info['mesterskap'])
    return f'<span class="kat">{escape(" · ".join(biter))}</span>'


def seksjoner(stip, alle, yngst_forst):
    """Gruppe A, B, C og D, med høyest poengsum øverst i hver gruppe slik
    klubbens eget tildelingsdokument er ordnet. Utøvere uten poengsum —
    tildelt etter skade- eller graviditetsbestemmelsen — legges sist.
    Deretter øvrige utøvere med yngste først."""
    ut = []
    for g in GRUPPER:
        gruppe = sorted([a for a in stip if stip[a]['gruppe'] == g],
                        key=lambda a: -(stip[a]['poeng'] or 0))
        ut.append((f'Stipendgruppe {g} ', f'{len(gruppe)} utøvere', gruppe))
    ovrige = yngst_forst([a for a in alle if a not in stip])
    ut.append(('Øvrige utøvere ', f'{len(ovrige)} · yngste først', ovrige))
    return ut


def ikke_funnet_linje(navn, info):
    poeng = f', {info["poeng"]} p' if info['poeng'] else ''
    return f'{escape(navn)} — gruppe {info["gruppe"]}, {escape(info["gren"])}{poeng}'


def sammendrag(stip):
    fordelt = ' · '.join(
        f'{g}: {sum(1 for v in stip.values() if v["gruppe"] == g)}' for g in GRUPPER)
    return f'Stipend: {len(stip)} av {len(FLAT)} tildelinger koblet ({fordelt}).'


def csv_kolonner():
    return ['Stipendgruppe', 'Poeng 2025', 'Gren']


def csv_verdier(info):
    if not info:
        return ['', '', '']
    return [info['gruppe'], info['poeng'] or '', info['gren']]
