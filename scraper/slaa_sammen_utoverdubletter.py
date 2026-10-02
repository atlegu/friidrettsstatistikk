"""Slaa sammen utoeverposter som er samme person.

BAKGRUNN
--------
match_athlete() noekler paa (navn, foedselsaar, kjoenn). Der den lagrede
utoeveren manglet foedselsaar eller kjoenn, traff ikke noekkelen, og importen
opprettet en NY utoever for samme person. Resultatet: samme resultat paa
samme stevne under to utoever-id-er med samme navn. 414 slike par fantes
15.09.2026, alle opprettet i 2026. Avstemmingen kjenner naa igjen raden paa
navn innenfor stevnet, saa nye par oppstaar ikke. Dette skriptet rydder.

REGEL
-----
  Trygge par: samme navn, samme foedselsaar, samme kjoenn (eller ett av
  dem tomt), og minst ett felles resultat (samme stevne/oevelse/resultat/
  plass). Den ELDSTE posten beholdes. Alle resultater flyttes dit;
  resultater som da blir like paa alt (dublett av det felles resultatet)
  slettes. current_club_id og manglende foedselsaar/kjoenn fylles fra den
  som slettes.

  Par med ulikt foedselsaar eller ulikt kjoenn roeres ikke. De listes i
  planen og maa vurderes for haand.

KJOERING
--------
    python slaa_sammen_utoverdubletter.py --kartlegg # bygg parlista paa nytt
    python slaa_sammen_utoverdubletter.py            # toerrkjoering
    python slaa_sammen_utoverdubletter.py --apply
Leser opprydding/utoveravdrift_par.json. --kartlegg bygger den fra
test_utoveravdrift(event_id) for alle oevelser (den gamle fila faar
tidsstempel). Trengs etter stevneoppryddingen 18.09.2026: rader som laa i
to stevneposter under hver sin utoever-id havnet i samme post.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

load_dotenv(Path(__file__).parent / '.env')
sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])

TS = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
LOGG = Path(__file__).parent / 'logs'; LOGG.mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout),
                              logging.FileHandler(LOGG / f'slaa_sammen_utoverdubletter_{TS}.log', encoding='utf-8')])
logging.getLogger('httpx').setLevel(logging.WARNING)
log = logging.getLogger(__name__)


def hent_utover(i):
    r = sb.table('athletes').select('id,full_name,birth_year,birth_date,gender,current_club_id,created_at') \
          .eq('id', i).execute().data
    return r[0] if r else None


def hent_resultater(i):
    ut, fra = [], 0
    while True:
        r = sb.table('results').select('id,meet_id,event_id,performance,place,wind').eq('athlete_id', i) \
              .order('id').range(fra, fra + 999).execute().data
        ut.extend(r)
        if len(r) < 1000:
            return ut
        fra += 1000


def kartlegg(fil: Path):
    """Par av utoever-id-er med felles resultater, klassifisert."""
    felles = {}
    for e in sb.table('events').select('id').execute().data:
        for g in sb.rpc('test_utoveravdrift', {'p_event_id': e['id']}).execute().data:
            ids = sorted(g['athlete_ids'])
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    felles[(ids[i], ids[j])] = felles.get((ids[i], ids[j]), 0) + 1
    par = []
    for (a, b), n in sorted(felles.items(), key=lambda x: -x[1]):
        A, B = hent_utover(a), hent_utover(b)
        if not A or not B:
            continue
        aa, ab = A.get('birth_year'), B.get('birth_year')
        ka, kb = A.get('gender'), B.get('gender')
        if ka and kb and ka != kb:
            t = 'ulikt kjoenn'
        elif aa and ab and aa != ab:
            t = 'ulikt foedselsaar'
        elif not aa or not ab:
            t = 'en mangler foedselsaar'
        else:
            t = 'samme aar og kjoenn (trygg)'
        par.append({'a': a, 'b': b, 'felles_resultater': n, 'type': t, 'navn': A['full_name'], 'aar': [aa, ab]})
    if fil.exists():
        fil.rename(fil.with_name(f'utoveravdrift_par_{TS}.json'))
    json.dump(par, open(fil, 'w'), ensure_ascii=False, indent=1)
    log.info(f"Kartlagt {len(par)} par -> {fil}")
    for t in sorted({p['type'] for p in par}):
        log.info(f"   {t}: {sum(1 for p in par if p['type'] == t)}")
    return par


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--kartlegg', action='store_true', help='bygg parlista paa nytt foer kjoering')
    ap.add_argument('--fil', default=Path(__file__).parent / 'opprydding' / 'utoveravdrift_par.json')
    args = ap.parse_args()

    if args.kartlegg:
        kartlegg(Path(args.fil))
    par = json.load(open(args.fil, encoding='utf-8'))
    trygge = [p for p in par if p['type'] in ('samme aar og kjoenn (trygg)', 'en mangler foedselsaar')]
    for_haand = [p for p in par if p not in trygge]
    log.info(f"{len(par)} par: {len(trygge)} trygge, {len(for_haand)} for haand")

    # Samme utoever kan staa i flere par; slaa sammen ett par om gangen og
    # hopp over par der en av dem alt er borte.
    plan = []
    for p in trygge:
        A, B = hent_utover(p['a']), hent_utover(p['b'])
        if not A or not B:
            continue
        behold, slett = (A, B) if A['created_at'] <= B['created_at'] else (B, A)
        plan.append((behold, slett, p['felles_resultater']))

    ut = Path(__file__).parent / 'opprydding' / f'utoverdubletter_plan_{TS}.json'
    json.dump({'slaa_sammen': [{'behold': b['id'], 'slett': s['id'], 'navn': b['full_name'], 'felles': n}
                               for b, s, n in plan],
               'for_haand': for_haand}, open(ut, 'w'), ensure_ascii=False, indent=1)
    log.info(f"Plan: {len(plan)} sammenslaainger. Lagret {ut}")
    for b, s, n in plan[:10]:
        log.info(f"   {b['full_name']} ({b['birth_year']}): behold {b['id'][:8]}, slett {s['id'][:8]}, {n} felles")

    if not args.apply:
        log.info("DRY-RUN. Kjoer med --apply.")
        return

    flyttet = slettet_res = slettet_utov = hoppet = 0
    for b, s, n in plan:
        # Samme utoever kan staa i flere par (A-B, B-C). Er en av dem alt
        # slaatt sammen og borte, hopp over; neste kartlegging finner A-C.
        if not hent_utover(b['id']) or not hent_utover(s['id']):
            hoppet += 1
            continue
        behold_res = {(r['meet_id'], r['event_id'], r['performance'], r['place']): r for r in hent_resultater(b['id'])}
        for r in hent_resultater(s['id']):
            key = (r['meet_id'], r['event_id'], r['performance'], r['place'])
            if key in behold_res:
                sb.table('results').delete().eq('id', r['id']).execute(); slettet_res += 1
            else:
                sb.table('results').update({'athlete_id': b['id']}).eq('id', r['id']).execute(); flyttet += 1
        felt = {}
        if not b['birth_year'] and s['birth_year']: felt['birth_year'] = s['birth_year']
        if not b['birth_date'] and s['birth_date']: felt['birth_date'] = s['birth_date']
        if not b['gender'] and s['gender']: felt['gender'] = s['gender']
        if not b['current_club_id'] and s['current_club_id']: felt['current_club_id'] = s['current_club_id']
        if felt:
            sb.table('athletes').update(felt).eq('id', b['id']).execute()
        sb.table('athletes').delete().eq('id', s['id']).execute(); slettet_utov += 1
        log.info(f"   {b['full_name']} ({b['birth_year']}): slaatt sammen")
    log.info(f"Ferdig: {slettet_utov} utoevere slaatt sammen, {flyttet} resultater flyttet, "
             f"{slettet_res} dublettresultater slettet, {hoppet} par hoppet over (alt borte).")
    log.info("Husk: refresh_plattform_statistikk() og utled_gjeldende_klubb.")


if __name__ == '__main__':
    main()
