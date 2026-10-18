#!/usr/bin/env python3
"""Legg inn en resultatliste på friidrettens standardmal (Excel) som er sendt
inn på e-post til resultater@friidrett.no.

    python importer_resultatliste.py liste.xls              # tørrkjøring (standard)
    python importer_resultatliste.py liste.xls --apply

Malen: topptekst med «Stevne:», «Stevnested:», «Stevnedato:», «Arrangør»,
«Utendørs:» (Y/J/N), så blokker med klasse og øvelse på én rad («MV70 |
Kule 4,0kg») og resultatrader under (plass | navn | år | klubb | resultat |
vind). Kastfemkamp har delresultatene på en egen rad i parentes.

Reglene er de samme som når stevnet kommer fra minfriidrettsstatistikk.info,
slik at importen der senere kjenner igjen radene og ikke legger dem inn på
nytt (avstemmingen i update_results.py matcher på utøver, øvelse, resultat og
plass):
  * resultat i meter med to desimaler («21.20»), femkamp som heltall poeng
  * plass per klasse slik den står i lista
  * «nm», «dns», «dnf» legges ikke inn (som i kildeimporten)
  * stevnet får tomt sted (city = '') - da finner kildeimporten posten igjen
    på navn + dato og fyller inn sted og kilde-id selv. Har kilden et annet
    navn på stevnet, kjenner finn_tvilling() i update_results.py det igjen
    på de felles radene.

Utøvere kobles bare når det er entydig: samme fødselsår, samme kjønn (fra
klassen), og navnene er like eller det ene er det andre med mellomnavn
(«Helge Lorentzen» = «Helge Andreas Lorentzen»). Finnes ingen eller flere,
stopper skriptet uten å legge inn noe; nye utøvere opprettes ikke herfra.

Radene merkes med en import_batch (source_type 'excel'), så de kan følges og
om nødvendig fjernes samlet:
    delete from results where import_batch_id = '<id>';
"""

import argparse
import json
import logging
import os
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

HER = Path(__file__).resolve().parent
load_dotenv(HER / '.env')
(HER / 'logs').mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(HER / 'logs' / f'importer_resultatliste_{datetime.now():%Y%m%d_%H%M%S}.log'))
logging.getLogger('httpx').setLevel(logging.WARNING)

IKKE_RESULTAT = {'nm', 'dns', 'dnf', 'dq', 'dsq', '-', 'x', 'brutt', 'ikke startet'}
FORKORTELSER = {'fil': 'friidrettslag', 'fik': 'friidrettskrets', 'fk': 'friidrettsklubb'}

# Vekt (kg) -> øvelseskode. Slegge med vaierlengde slik kilden fører den.
SLEGGE = {7.26: 'slegge_726kg/1215cm', 6.0: 'slegge_60kg/1215cm', 5.0: 'slegge_50kg/120cm',
          4.0: 'slegge_40kg/1195cm', 3.0: 'slegge_30kg_1195cm', 2.0: 'slegge_20kg/110cm'}
KULE = {7.26: 'kule_7_26kg', 6.0: 'kule_6kg', 5.0: 'kule_5kg', 4.0: 'kule_4kg', 3.0: 'kule_3kg', 2.0: 'kule_2kg'}
DISKOS = {2.0: 'diskos_2kg', 1.75: 'diskos_1_75kg', 1.5: 'diskos_1_5kg', 1.0: 'diskos_1kg',
          0.75: 'diskos_750g', 0.6: 'diskos_600g'}
SPYD = {0.8: 'spyd_800g', 0.7: 'spyd_700g', 0.6: 'spyd_600g', 0.5: 'spyd_500g', 0.4: 'spyd_400g'}
VEKT = {15.88: 'vektkast_1588kg', 11.34: 'vektkast_1134kg', 9.08: 'vektkast_908kg',
        7.26: 'vektkast_726kg', 5.45: 'vektkast_545kg', 4.0: 'vektkast40kg'}
FEMKAMP = 'kast_5_k_slegge-kule-diskos-spyd-vektkast'


def tall(s) -> float | None:
    try:
        return float(str(s).replace(',', '.').strip())
    except ValueError:
        return None


def vekt_kg(tekst: str) -> float | None:
    """«6,0kg» -> 6.0, «400gr» -> 0.4, «0,75kg» -> 0.75"""
    m = re.search(r'(\d+(?:[.,]\d+)?)\s*(kg|gr|gram|g)\b', tekst.lower())
    if not m:
        return None
    v = tall(m.group(1))
    return round(v / 1000, 3) if m.group(2) in ('gr', 'gram', 'g') else v


def kjonn(klasse: str) -> str | None:
    k = klasse.strip().upper()
    if k[:1] in ('J', 'K'):
        return 'F'
    if k[:1] in ('G', 'M'):
        return 'M'
    return None


def oevelseskode(oevelse: str, klasse: str) -> str | None:
    o = oevelse.lower()
    if 'kamp' in o and 'kast' in o:
        k = klasse.upper().replace('-', '')
        if k.startswith(('KV', 'MV')):
            return FEMKAMP + '_veteran'
        if k[:1] in ('G', 'J'):
            return FEMKAMP + '_ungdom'
        return FEMKAMP
    w = vekt_kg(oevelse)
    for prefiks, tabell in (('slegge', SLEGGE), ('kule', KULE), ('diskos', DISKOS),
                            ('spyd', SPYD), ('vekt', VEKT)):
        if o.startswith(prefiks):
            return tabell.get(w)
    return None


def navnedeler(navn: str) -> list[str]:
    return [d for d in re.split(r'[\s]+', navn.lower().strip()) if d]


def klubbnoekkel(navn: str) -> frozenset:
    deler = re.sub(r'[^a-zæøå0-9\- ]', ' ', (navn or '').lower()).split()
    return frozenset(FORKORTELSER.get(d, d) for d in deler)


def les_liste(fil: Path) -> tuple[dict, list[dict]]:
    """Returnerer (stevneinfo, rader)."""
    if fil.suffix.lower() == '.xls':
        import xlrd
        bok = xlrd.open_workbook(str(fil))
        ark = bok.sheet_by_index(0)
        celler = [[c.value for c in ark.row(r)] for r in range(ark.nrows)]
    else:
        import openpyxl
        ark = openpyxl.load_workbook(str(fil), data_only=True).worksheets[0]
        celler = [[c if c is not None else '' for c in rad] for rad in ark.iter_rows(values_only=True)]

    def dato(v) -> str | None:
        if isinstance(v, (int, float)) and v > 30000:
            return (date(1899, 12, 30) + timedelta(days=int(v))).isoformat()
        if isinstance(v, datetime):
            return v.date().isoformat()
        m = re.match(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', str(v).strip())
        return f'{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}' if m else None

    info: dict = {}
    rader: list[dict] = []
    klasse = oevelse = ''
    for nr, rad in enumerate(celler, start=1):
        rad = list(rad) + [''] * (8 - len(rad))
        c0 = str(rad[0]).strip()
        c1 = str(rad[1]).strip()
        hode = c0.rstrip(':*').strip().lower()
        if hode == 'stevne':
            info['navn'] = c1
            continue
        if hode == 'stevnested':
            info['sted'] = c1
            continue
        if hode == 'stevnedato':
            info['fra'] = dato(rad[1])
            info['til'] = dato(rad[2]) or info['fra']
            continue
        if hode == 'arrangør':
            info['arrangor'] = c1
            continue
        if hode == 'utendørs':
            info['utendors'] = c1.upper() in ('Y', 'J', 'JA', 'YES')
            continue
        if hode in ('kontaktperson', 'erklæring', 'resultatliste'):
            continue
        if not c0 and c1 and not any(str(x).strip() for x in rad[2:]) and not info.get('vaer'):
            info['vaer'] = c1                          # fritekst om forholdene
            continue
        if c0.startswith('('):                         # delresultater i femkamp
            if rader and rader[-1]['oevelse'] == oevelse:
                rader[-1]['delresultater'] = c0.strip('()')
            continue
        plass = tall(c0)
        if c0 and plass is None and c1:                # ny klasse + øvelse
            klasse, oevelse = c0, c1
            continue
        if not c1 or not oevelse:
            continue
        resultat = rad[4]
        rader.append({
            'linje': nr,
            'klasse': klasse,
            'oevelse': oevelse,
            'plass': int(plass) if plass else None,
            'navn': ' '.join(c1.split()),
            'aar': int(tall(rad[2])) if tall(rad[2]) else None,
            'klubb': str(rad[3]).strip(),
            'resultat': resultat,
            'vind': tall(rad[5]) if str(rad[5]).strip() else None,
        })
    return info, rader


def finn_utover(sb, navn: str, aar: int | None, kj: str | None) -> tuple[list[dict], str]:
    deler = navnedeler(navn)
    q = sb.table('athletes').select('id,first_name,last_name,birth_year,gender,current_club_id') \
        .ilike('last_name', f'%{deler[-1]}%')
    if aar:
        q = q.eq('birth_year', aar)
    kand = q.execute().data or []
    treff = []
    for a in kand:
        if kj and a.get('gender') and a['gender'] != kj:
            continue
        ad = navnedeler(f"{a['first_name']} {a['last_name']}")
        if ad == deler:
            treff.append((0, a))
        elif ad[0] == deler[0] and ad[-1] == deler[-1] and (set(ad) <= set(deler) or set(deler) <= set(ad)):
            treff.append((1, a))                       # med/uten mellomnavn
    if not treff:
        return [], 'ingen'
    beste = min(t for t, _ in treff)
    valgt = [a for t, a in treff if t == beste]
    return valgt, 'eksakt' if beste == 0 else 'mellomnavn'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('fil', type=Path)
    ap.add_argument('--apply', action='store_true', help='skriv til basen (standard er tørrkjøring)')
    ap.add_argument('--dry-run', action='store_true', help='tørrkjøring (standard)')
    ap.add_argument('--kilde', default='', help='fritekst om hvor lista kom fra, lagres på importen')
    args = ap.parse_args()
    skriv = args.apply and not args.dry_run

    sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])
    info, rader = les_liste(args.fil)
    logger.info(f"{info.get('navn')} · {info.get('sted')} · {info.get('fra')} · arrangør {info.get('arrangor')} · "
                f"{'utendørs' if info.get('utendors') else 'innendørs'} · {len(rader)} rader")
    if not info.get('navn') or not info.get('fra') or info.get('utendors') is None:
        sys.exit('Mangler stevnenavn, dato eller «Utendørs:» i toppteksten')

    events = {e['code']: e for e in sb.table('events').select('id,code,name,result_type').execute().data}
    klubber = []
    fra = 0
    while True:
        b = sb.table('clubs').select('id,name').order('id').range(fra, fra + 999).execute().data or []
        klubber += b
        if len(b) < 1000:
            break
        fra += 1000
    klubb_navn = {k['id']: k['name'] for k in klubber}
    klubb_noekler: dict = {}
    for k in klubber:
        klubb_noekler.setdefault(klubbnoekkel(k['name']), []).append(k['id'])

    feil, hoppet, klare = [], [], []
    for r in rader:
        res = str(r['resultat']).strip()
        if res.lower() in IKKE_RESULTAT or not res:
            hoppet.append(f"{r['navn']} {r['klasse']} {r['oevelse']}: «{res or 'tomt'}» (legges ikke inn, som i kildeimporten)")
            continue
        kode = oevelseskode(r['oevelse'], r['klasse'])
        if not kode or kode not in events:
            feil.append(f"Linje {r['linje']}: ukjent øvelse «{r['oevelse']}» ({r['klasse']}) -> {kode}")
            continue
        ev = events[kode]
        kj = kjonn(r['klasse'])
        utovere, hvordan = finn_utover(sb, r['navn'], r['aar'], kj)
        if len(utovere) != 1:
            feil.append(f"Linje {r['linje']}: {r['navn']} ({r['aar']}): "
                        f"{'ingen utøver funnet' if not utovere else f'{len(utovere)} mulige utøvere'}")
            continue
        a = utovere[0]
        if kj and not a.get('gender'):
            feil.append(f"Linje {r['linje']}: {r['navn']} mangler kjønn i basen")
            continue
        # Klubb: utøverens klubb når navnet i lista er samme klubb, ellers eksakt navn
        noekkel = klubbnoekkel(r['klubb'])
        club_id = None
        if a.get('current_club_id') and klubbnoekkel(klubb_navn.get(a['current_club_id'], '')) == noekkel:
            club_id = a['current_club_id']
        elif len(klubb_noekler.get(noekkel, [])) == 1:
            club_id = klubb_noekler[noekkel][0]
        elif a.get('current_club_id'):
            club_id = a['current_club_id']
            r['klubbmerknad'] = f"«{r['klubb']}» ikke entydig, bruker {klubb_navn.get(club_id)}"
        v = tall(res)
        if v is None:
            feil.append(f"Linje {r['linje']}: kan ikke lese resultatet «{res}»")
            continue
        perf = str(int(round(v))) if kode.startswith(FEMKAMP) else f'{v:.2f}'
        klare.append({**r, 'kode': kode, 'event_id': ev['id'], 'athlete': a, 'treff': hvordan,
                      'club_id': club_id, 'performance': perf})

    # Stevnet: finnes det fra før (samme navn og dato)?
    meet = (sb.table('meets').select('id,name,city,external_id').ilike('name', info['navn'])
            .eq('start_date', info['fra']).execute().data or [])
    eksisterende = set()
    if meet:
        m = meet[0]
        logger.info(f"Stevnet finnes allerede: {m['id']} ({m['name']}, kilde-id {m.get('external_id')})")
        for x in sb.table('results').select('athlete_id,event_id,performance,place').eq('meet_id', m['id']).execute().data:
            eksisterende.add((x['athlete_id'], x['event_id'], x['performance'], x['place']))
    nye = [k for k in klare if (k['athlete']['id'], k['event_id'], k['performance'], k['plass']) not in eksisterende]

    logger.info('')
    logger.info(f"{'Klasse':<8} {'Øvelse':<26} {'Pl':>2}  {'Navn i lista':<34} {'År':<5} {'Kobles til':<36} {'Resultat':>8}  Klubb")
    for k in klare:
        a = k['athlete']
        merk = '' if k in nye else '  (finnes allerede)'
        logger.info(f"{k['klasse']:<8} {events[k['kode']]['name'][:26]:<26} {k['plass'] or '':>2}  {k['navn']:<34} "
                    f"{k['aar'] or '':<5} {(a['first_name'] + ' ' + a['last_name'])[:30] + (' *' if k['treff'] != 'eksakt' else ''):<36} "
                    f"{k['performance']:>8}  {klubb_navn.get(k['club_id'], '–')}{merk}")
        if k.get('delresultater'):
            logger.info(f"{'':<38}delresultater: {k['delresultater']}")
        if k.get('klubbmerknad'):
            logger.info(f"{'':<38}NB: {k['klubbmerknad']}")
    logger.info('* = koblet med/uten mellomnavn (samme fornavn, etternavn, fødselsår og kjønn)')
    for h in hoppet:
        logger.info(f'Hoppet over: {h}')
    for f in feil:
        logger.error(f)
    logger.info(f"{len(klare)} rader klare, {len(nye)} nye, {len(hoppet)} hoppet over, {len(feil)} feil; "
                f"{len({k['athlete']['id'] for k in klare})} utøvere")

    if feil:
        sys.exit('Stopper: rett feilene over før noe legges inn.')
    if not skriv:
        logger.info('Tørrkjøring - ingenting skrevet. Kjør med --apply for å legge inn.')
        return

    utendors = bool(info['utendors'])
    aar = int(info['fra'][:4]) + (1 if not utendors and int(info['fra'][5:7]) >= 10 else 0)
    sesong = sb.table('seasons').select('id').eq('year', aar).eq('indoor', not utendors).execute().data[0]['id']
    arrangor = ' '.join(FORKORTELSER.get(d.lower(), d).capitalize() if d.lower() in FORKORTELSER else d
                        for d in (info.get('arrangor') or '').split()) or None

    if meet:
        meet_id = meet[0]['id']
    else:
        meet_id = sb.table('meets').insert({
            'name': info['navn'], 'start_date': info['fra'], 'end_date': info['til'],
            'venue': info.get('sted') or None, 'city': '', 'country': 'NOR',
            'indoor': not utendors, 'level': 'local', 'season_id': sesong,
            'organizer_name': arrangor,
            'notes': info.get('vaer'),
        }).execute().data[0]['id']
        logger.info(f'Opprettet stevne {meet_id}')

    batch_id = sb.table('import_batches').insert({
        'name': args.fil.stem, 'source_type': 'excel', 'original_filename': args.fil.name,
        'meet_name': info['navn'], 'meet_date': info['fra'], 'meet_city': info.get('sted'),
        'raw_data': json.loads(json.dumps(rader, default=str)), 'row_count': len(nye), 'status': 'imported',
        'matched_athletes': len({k['athlete']['id'] for k in klare}), 'unmatched_athletes': 0,
        'imported_at': datetime.now().astimezone().isoformat(),
        'admin_notes': f"importer_resultatliste.py. {args.kilde}".strip(),
    }).execute().data[0]['id']

    if nye:
        sb.table('results').insert([{
            'athlete_id': k['athlete']['id'], 'event_id': k['event_id'], 'meet_id': meet_id,
            'season_id': sesong, 'club_id': k['club_id'], 'performance': k['performance'],
            'date': info['fra'], 'place': k['plass'], 'wind': k['vind'], 'status': 'OK',
            'import_batch_id': batch_id,
        } for k in nye]).execute()
    logger.info(f'Lagt inn {len(nye)} resultater i stevne {meet_id}, import {batch_id}')


if __name__ == '__main__':
    main()
