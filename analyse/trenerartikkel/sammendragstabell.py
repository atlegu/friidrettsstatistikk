#!/usr/bin/env python3
"""Regenererer sammendragstabellen med alle 19 standardøvelser.

Tabellen sto i artikkelutkastet uten å være generert av `generate.py` —
`EVENTS` der har bare de fem referanseøvelsene som får egne figurer. Den var
altså ikke reproduserbar, og ble utdatert da basen ble komplettert.

Denne kjører samme RPC (`analyse_event_trend`) for alle 19, med seniorredskap
og -høyder, utendørs, beste notering uansett alder.

    ../../scraper/venv/bin/python sammendragstabell.py

Skriver output/sammendrag_19_ovelser.csv og en ferdig markdown-tabell.
"""

import csv
import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

HER = Path(__file__).resolve().parent
load_dotenv(HER.parent.parent / 'scraper' / '.env')
sb = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

FRA, TIL = 2013, 2025

# (visningsnavn, kode M, kode K, min_v, max_v, høyere_er_bedre, enhet)
# Grensene luker bort tastefeil og urimelige verdier, som i generate.py.
OVELSER = [
    ('100 m',          '100m',        '100m',        950,    2500,   False, 's'),
    ('200 m',          '200m',        '200m',        1900,   5000,   False, 's'),
    ('400 m',          '400m',        '400m',        4300,   11000,  False, 's'),
    ('800 m',          '800m',        '800m',        10000,  30000,  False, 'min'),
    ('1500 m',         '1500m',       '1500m',       20000,  60000,  False, 'min'),
    ('3000 m',         '3000m',       '3000m',       44000,  120000, False, 'min'),
    ('5000 m',         '5000m',       '5000m',       76000,  200000, False, 'min'),
    ('10 000 m',       '10000m',      '10000m',      160000, 420000, False, 'min'),
    ('100/110 m hekk', '110mh_106_7cm', '100mh_84cm', 1250,  3000,   False, 's'),
    ('400 m hekk',     '400mh_91_4cm', '400mh_76_2cm', 4600, 12000,  False, 's'),
    ('3000 m hinder',  '3000mhinder_91_4cm', '3000mhinder_76_2cm', 48000, 130000, False, 'min'),
    ('Lengde',         'lengde',      'lengde',      2000,   8500,   True,  'm'),
    ('Høyde',          'hoyde',       'hoyde',       800,    2400,   True,  'm'),
    ('Stav',           'stav',        'stav',        800,    6300,   True,  'm'),
    ('Tresteg',        'tresteg',     'tresteg',     4000,   18000,  True,  'm'),
    ('Kule',           'kule_7_26kg', 'kule_4kg',    3000,   23000,  True,  'm'),
    ('Diskos',         'diskos_2kg',  'diskos_1kg',  8000,   72000,  True,  'm'),
    ('Slegge',         'slegge_726kg/1215cm', 'slegge_40kg/1195cm', 8000, 85000, True, 'm'),
    ('Spyd',           'spyd_800g',   'spyd_600g',   10000,  99000,  True,  'm'),
]


def fmt(v, enhet):
    if v is None:
        return '–'
    v = float(v)
    if enhet == 's':
        return f'{v / 100:.2f}'.replace('.', ',')
    if enhet == 'min':
        tot = v / 100
        m, s = int(tot // 60), tot % 60
        return f'{m}:{s:04.1f}'.replace('.', ',')
    return f'{v / 1000:.2f}'.replace('.', ',')


def hent(kode, min_v, max_v, hoyere, kjonn):
    rader = sb.rpc('analyse_event_trend', {
        'p_event_code': kode, 'p_min_v': min_v, 'p_max_v': max_v,
        'p_higher_better': hoyere, 'p_from_year': FRA, 'p_to_year': TIL,
        'p_age_lo': 0, 'p_age_hi': 200, 'p_outdoor_only': True,
    }).execute().data
    ut = {}
    for r in rader:
        if r.get('gender') == kjonn and r['yr'] in (FRA, TIL):
            ut[r['yr']] = r.get('top10_avg')
    return ut


def main():
    rader, linjer = [], []
    for navn, kode_m, kode_k, lo, hi, hoyere, enhet in OVELSER:
        m = hent(kode_m, lo, hi, hoyere, 'M')
        k = hent(kode_k, lo, hi, hoyere, 'F')
        rader.append({'ovelse': navn, 'menn_2013': m.get(FRA), 'menn_2025': m.get(TIL),
                      'kvinner_2013': k.get(FRA), 'kvinner_2025': k.get(TIL)})
        linjer.append(f'| {navn} | {fmt(m.get(FRA), enhet)} | {fmt(m.get(TIL), enhet)} | '
                      f'{fmt(k.get(FRA), enhet)} | {fmt(k.get(TIL), enhet)} |')
        print(linjer[-1])

    ut = HER / 'output'
    with open(ut / 'sammendrag_19_ovelser.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rader[0]))
        w.writeheader()
        w.writerows(rader)

    tabell = ('| Øvelse | Menn 2013 | Menn 2025 | Kvinner 2013 | Kvinner 2025 |\n'
              '|---|---|---|---|---|\n' + '\n'.join(linjer) + '\n')
    (ut / 'sammendrag_19_ovelser.md').write_text(tabell, encoding='utf-8')
    print(f'\nSkrevet: {ut / "sammendrag_19_ovelser.md"}')


if __name__ == '__main__':
    main()
