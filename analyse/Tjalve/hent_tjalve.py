"""
Uttrekk: utøvere som representerer IK Tjalve 2024–2026.

For hver utøver, hvert år og hver øvelse: antall starter og de tre beste
resultatene. Avgrenset til utøvere som er 15 år eller eldre.

TO REGLER OM KLUBBSKIFTE
------------------------
1. Er utøverens første Tjalve-sesong etter 2024, hentes resultatene fra
   sesongene FØR de kom til Tjalve også, med klubben de da representerte.
   Disse merkes i rapporten så det synes at det er en annen klubb.

2. Utøvere som har Tjalve-resultater i 2024 eller 2025, men som i 2026
   konkurrerer for en annen klubb og ikke for Tjalve, er sluttet i klubben og
   tas ut av listen.

Aldersregel: norsk friidrett bruker kalenderår — alder = konkurranseår minus
fødselsår. Se CLAUDE.md punkt 6.

Klubbtilhørighet hentes fra `results.club_id`, altså klubben utøveren faktisk
representerte i det enkelte stevnet.

Skriver `tjalve_data.json` som `lag_rapport.py` bygger rapporten fra.
"""

import json
import os
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

load_dotenv(Path(__file__).resolve().parents[2] / 'scraper' / '.env')

CLUB_ID = 'd38f1050-45c0-40a5-af81-4215edb599fe'   # IK Tjalve
CLUB_NAME = 'IK Tjalve'
YEARS = [2024, 2025, 2026]
MIN_AGE = 15
OUT = Path(__file__).parent / 'tjalve_data.json'

# Basen har hatt utøvere med ugyldige fødselsår (0, 752, 9171 …). De er ryddet
# 2026-08-21 og sperret med en databasesjekk, men uttrekket validerer likevel —
# et aldersfilter skal aldri stole blindt på feltet.
BY_MIN, BY_MAX = 1860, max(YEARS)

SELECT = ('id,performance,performance_value,wind,date,athlete_id,club_id,'
          'athletes(full_name,birth_year,birth_date,gender),'
          'events(name,result_type,sort_order)')

sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])


def hent(**filtre):
    """Nøkkelbasert paginering — `.range()` uten sortering mister rader."""
    ut, siste = [], '00000000-0000-0000-0000-000000000000'
    while True:
        q = (sb.table('results').select(SELECT)
               .gte('date', f'{YEARS[0]}-01-01').lte('date', f'{YEARS[-1]}-12-31')
               .gt('id', siste).order('id').limit(1000))
        for k, v in filtre.items():
            q = q.in_(k, v) if isinstance(v, list) else q.eq(k, v)
        res = q.execute()
        if not res.data:
            return ut
        ut.extend(res.data)
        siste = res.data[-1]['id']
        if len(res.data) < 1000:
            return ut


# --- 1. Tjalve-resultatene --------------------------------------------------

tjalve_rows = hent(club_id=CLUB_ID)
print(f'Tjalve-resultater 2024–2026: {len(tjalve_rows)}')

tjalve_ar = defaultdict(set)          # athlete_id -> {år med Tjalve-start}
athletes = {}
usikker_alder = {}

for r in tjalve_rows:
    a = r.get('athletes')
    if not a or not r.get('date'):
        continue
    by = a.get('birth_year')
    if by is None or not (BY_MIN <= by <= BY_MAX):
        u = usikker_alder.setdefault(r['athlete_id'],
                                     {'navn': a['full_name'], 'fodt': by, 'starter': 0})
        u['starter'] += 1
        continue
    tjalve_ar[r['athlete_id']].add(int(r['date'][:4]))
    athletes[r['athlete_id']] = {'navn': a['full_name'], 'fodt': by,
                                 'fodt_dato': a.get('birth_date'),
                                 'kjonn': a.get('gender')}

# --- 2. Alle resultater for disse utøverne, uansett klubb ------------------

aids = list(athletes)
alle = []
for i in range(0, len(aids), 100):
    alle.extend(hent(athlete_id=aids[i:i + 100]))
print(f'Alle resultater for de samme utøverne: {len(alle)}')

klubber = {c['id']: c['name'] for c in
           sb.table('clubs').select('id,name').execute().data}

# --- 3. Regel 2: sluttet i klubben -----------------------------------------

har_2026_annen, har_2026_tjalve = defaultdict(set), set()
for r in alle:
    if not r.get('date') or int(r['date'][:4]) != 2026:
        continue
    if r['club_id'] == CLUB_ID:
        har_2026_tjalve.add(r['athlete_id'])
    elif r['club_id']:
        har_2026_annen[r['athlete_id']].add(r['club_id'])

sluttet = {}
for aid in list(athletes):
    tidligere = tjalve_ar[aid] & {2024, 2025}
    if tidligere and aid not in har_2026_tjalve and har_2026_annen.get(aid):
        sluttet[aid] = {
            'navn': athletes[aid]['navn'],
            'ny_klubb': ', '.join(sorted(klubber.get(c, '?')
                                         for c in har_2026_annen[aid])),
            'tjalve_ar': sorted(tidligere),
        }
        del athletes[aid]

print(f'Tatt ut — konkurrerer for annen klubb i 2026: {len(sluttet)}')

# --- 4. Bygg radene --------------------------------------------------------

groups = defaultdict(list)
skipped_young = 0

for r in alle:
    aid = r['athlete_id']
    if aid not in athletes or not r.get('date'):
        continue
    e = r.get('events')
    if not e:
        continue
    year = int(r['date'][:4])
    if year - athletes[aid]['fodt'] < MIN_AGE:       # kalenderårsregelen
        skipped_young += 1
        continue

    er_tjalve = r['club_id'] == CLUB_ID
    # Regel 1: resultater fra annen klubb tas bare med for sesongene FØR
    # utøveren kom til Tjalve. Ellers ville vi dratt inn parallelle klubbytter
    # og år etter at de sluttet.
    if not er_tjalve and year >= min(tjalve_ar[aid]):
        continue

    groups[(aid, year, e['name'])].append({
        'perf': r['performance'], 'val': r['performance_value'],
        'wind': r['wind'], 'dato': r['date'],
        'rt': e['result_type'], 'so': e.get('sort_order') or 0,
        'klubb': None if er_tjalve else klubber.get(r['club_id'], 'Ukjent klubb'),
    })

print(f'Utelatt {skipped_young} starter fra utøvere under {MIN_AGE} år')


def sort_key(x, rt):
    v = x['val']
    return (1, 0) if v is None else (0, v if rt == 'time' else -v)


ANTALL_RESULTATER = 3

records = []
for (aid, year, ovelse), lst in groups.items():
    rt = lst[0]['rt']
    lst.sort(key=lambda x: sort_key(x, rt))
    andre = sorted({x['klubb'] for x in lst if x['klubb']})
    rad = {
        'aid': aid, 'ar': year, 'ovelse': ovelse, 'rt': rt, 'so': lst[0]['so'],
        'starter': len(lst),
        'annen_klubb': ', '.join(andre) if andre else None,
        'resultater': [
            {'perf': x['perf'], 'dato': x['dato'], 'vind': x['wind']}
            for x in lst[:ANTALL_RESULTATER]
        ],
    }
    records.append(rad)

# Utøvere som er under 15 i alle årene har ingen rader igjen. De skal ut av
# lista, ikke stå som tomme oppføringer.
med_rader = {r['aid'] for r in records}
athletes = {a: v for a, v in athletes.items() if a in med_rader}

OUT.write_text(json.dumps({
    'klubb': CLUB_NAME, 'ar': YEARS, 'min_alder': MIN_AGE,
    'utovere': athletes, 'rader': records,
    'tjalve_ar': {a: sorted(v) for a, v in tjalve_ar.items() if a in athletes},
    'sluttet': sluttet,
    'usikker_alder': list(usikker_alder.values()),
}, ensure_ascii=False, indent=1), encoding='utf-8')

fra_annen = sum(r['starter'] for r in records if r['annen_klubb'])
print(f'\n{len(athletes)} utøvere, {sum(r["starter"] for r in records)} starter '
      f'({fra_annen} fra andre klubber), {len(records)} rader -> {OUT.name}')
if usikker_alder:
    print(f'{len(usikker_alder)} utøver(e) holdt utenfor pga. ugyldig fødselsår')
