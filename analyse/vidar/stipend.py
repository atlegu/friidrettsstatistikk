"""Utøverstipend 2026 for Sportsklubben Vidar, fra «SKV budsjett 2026 - v1.pdf»,
seksjonen «Utøverbudsjetter». Beløp i hele kroner.
"""

from html import escape

from klubbrapport import navn as _navn

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
        'Jonathan Ødegaard': 118_000, 'Vilde Våge Henriksen': 80_000,
        'Line Kloster': 83_000, 'Anna Marie Sirevåg': 66_000,
        'Lovise Andresen': 80_000, 'Madeleine Holum': 62_000,
        'Kristine Rød': 60_000, 'Ingrid Rismark': 60_000,
        'Susanne Tveit Amundsen': 60_000, 'Anthony Johnsen': 88_000,
        'Kaja Mørch Pettersen': 80_000, 'Kristoffer Randall': 60_000,
        'Sjur Prestsæter': 60_000, 'Sunniva Andersen': 60_000,
        'Ilona Mononen': 50_000,
    },
    'Elite B': {
        'Simen Gimnes': 58_000, 'Frida Konow': 40_000, 'Rachel Ombeni': 48_000,
        'Sander Mathiesen': 50_000, 'Emiliano Røgeberg': 30_000,
        'Lina Svarlien': 30_000, 'Oda Lier': 30_000, 'Ine Bakken': 40_000,
        'Stine Holager': 40_000, 'Malene Kollberg': 40_000,
        'Marte Lien Johnsen': 30_000, 'Mathilde Knutsen': 30_000,
        'Sara Lie': 30_000, 'Emilie Mo': 30_000, 'Bethina Valle': 30_000,
    },
    'Fjelløping': {'Sylvia Nordskar': 50_000, 'Ida Robsam': 50_000},
    'OCR': {'Signy Karoline Kolstø': 50_000, 'Ånung Viken': 30_000},
}

KATEGORIER = ['OL/VM', 'EM', 'Elite A', 'Elite B', 'Fjelløping', 'OCR']

FLAT = {n: {'belop': b, 'kategori': kat}
        for kat, poster in STIPEND.items() for n, b in poster.items()}


def kr(n):
    """Norsk tallformat med hardt mellomrom som tusenskille."""
    return f'{n:,}'.replace(',', ' ')


def finn(db_navn):
    return _navn.finn(db_navn, FLAT)


def merke(info):
    return f' <span class="stipend-belop">(kr {kr(info["belop"])})</span>'


def detalj(info):
    return f'<span class="kat">{escape(info["kategori"])}</span>'


def seksjoner(stip, alle, yngst_forst):
    """Stipendmottakere først, deretter øvrige. Begge yngste først."""
    med = yngst_forst([a for a in alle if a in stip])
    uten = yngst_forst([a for a in alle if a not in stip])
    sum_kr = sum(stip[a]['belop'] for a in med)
    return [
        ('Utøvere med stipend ',
         f'{len(med)} av {len(FLAT)} i budsjettet · kr {kr(sum_kr)}', med),
        ('Øvrige utøvere ', f'{len(uten)} · yngste først', uten),
    ]


def ikke_funnet_linje(navn, info):
    return f'{escape(navn)} — kr {kr(info["belop"])} [{escape(info["kategori"])}]'


def sammendrag(stip):
    return (f'Stipend: {len(stip)} av {len(FLAT)} tildelinger koblet, '
            f'kr {kr(sum(v["belop"] for v in stip.values()))}.')


def csv_kolonner():
    return ['Stipend', 'Stipendkategori']


def csv_verdier(info):
    return [info['belop'], info['kategori']] if info else ['', '']
