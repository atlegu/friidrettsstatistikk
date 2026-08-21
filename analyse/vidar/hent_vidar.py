"""
Uttrekk: alle utøvere som har representert Sportsklubben Vidar 2024–2026.

For hver utøver, hvert år og hver øvelse: antall starter, beste og nestbeste
resultat. Avgrenset til utøvere som er 15 år eller eldre.

Aldersregel: norsk friidrett bruker kalenderår — alder = konkurranseår minus
fødselsår, uten justering for om bursdagen har vært. Se CLAUDE.md punkt 6.

Klubbtilhørighet hentes fra `results.club_id`, altså klubben utøveren faktisk
representerte i det stevnet — ikke `athletes.current_club_id`.

Skriver `vidar_data.json` som `lag_rapport.py` bygger rapporten fra.
"""

import json
import os
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

load_dotenv(Path(__file__).resolve().parents[2] / 'scraper' / '.env')

CLUB_ID = 'fcfc0ff6-787b-4471-acb6-5705fd7b48d8'   # Sportsklubben Vidar
CLUB_NAME = 'Sportsklubben Vidar'
YEARS = [2024, 2025, 2026]
MIN_AGE = 15
OUT = Path(__file__).parent / 'vidar_data.json'

# 56 utøvere i basen har ugyldige fødselsår (0, 752, 1006, 2097, 9171 …).
# Uten denne sjekken slipper de gjennom aldersfilteret — birth_year = 0 gir
# «2026 år» i 2026. De skilles ut i stedet for å feilklassifiseres.
BY_MIN, BY_MAX = 1890, max(YEARS)


def gyldig_fodselsar(by):
    return by is not None and BY_MIN <= by <= BY_MAX

sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])

rows, start = [], 0
while True:
    res = (sb.table('results')
             .select('performance,performance_value,wind,date,athlete_id,'
                     'athletes(full_name,birth_year,gender),'
                     'events(name,result_type,sort_order,indoor)')
             .eq('club_id', CLUB_ID)
             .gte('date', f'{YEARS[0]}-01-01')
             .lte('date', f'{YEARS[-1]}-12-31')
             .range(start, start + 999).execute())
    rows.extend(res.data)
    if len(res.data) < 1000:
        break
    start += 1000

print(f'Hentet {len(rows)} resultater for {CLUB_NAME}')

# Grupper per utøver / år / øvelse
groups = defaultdict(list)
athletes = {}
skipped_young = 0
usikker_alder = {}          # utøvere med ugyldig/manglende fødselsår

for r in rows:
    a, e = r.get('athletes'), r.get('events')
    if not a or not e or not r.get('date'):
        continue
    year = int(r['date'][:4])
    by = a.get('birth_year')
    if not gyldig_fodselsar(by):
        u = usikker_alder.setdefault(
            r['athlete_id'], {'navn': a['full_name'], 'fodt': by, 'starter': 0})
        u['starter'] += 1
        continue
    if year - by < MIN_AGE:                   # kalenderårsregelen
        skipped_young += 1
        continue
    aid = r['athlete_id']
    athletes[aid] = {'navn': a['full_name'], 'fodt': by, 'kjonn': a.get('gender')}
    groups[(aid, year, e['name'])].append({
        'perf': r['performance'],
        'val': r['performance_value'],
        'wind': r['wind'],
        'dato': r['date'],
        'rt': e['result_type'],
        'so': e.get('sort_order') or 0,
    })

print(f'Utelatt {skipped_young} starter fra utøvere under {MIN_AGE} år')

# Beste og nestbeste. Tid: lavest vinner. Lengde/høyde/poeng: høyest vinner.
def sort_key(x, rt):
    v = x['val']
    if v is None:
        return (1, 0)                      # verdiløse sist
    return (0, v if rt == 'time' else -v)

records = []
for (aid, year, ovelse), lst in groups.items():
    rt = lst[0]['rt']
    lst.sort(key=lambda x: sort_key(x, rt))
    beste, nest = lst[0], (lst[1] if len(lst) > 1 else None)
    records.append({
        'aid': aid, 'ar': year, 'ovelse': ovelse, 'rt': rt, 'so': lst[0]['so'],
        'starter': len(lst),
        'beste': beste['perf'], 'beste_dato': beste['dato'], 'beste_vind': beste['wind'],
        'nest': nest['perf'] if nest else None,
        'nest_dato': nest['dato'] if nest else None,
        'nest_vind': nest['wind'] if nest else None,
    })

OUT.write_text(json.dumps({
    'klubb': CLUB_NAME, 'ar': YEARS, 'min_alder': MIN_AGE,
    'utovere': athletes, 'rader': records,
    'usikker_alder': list(usikker_alder.values()),
}, ensure_ascii=False, indent=1), encoding='utf-8')

print(f'{len(athletes)} utøvere, {sum(r["starter"] for r in records)} starter, '
      f'{len(records)} rader -> {OUT.name}')
if usikker_alder:
    print(f'\n{len(usikker_alder)} utøver(e) holdt utenfor pga. ugyldig fødselsår:')
    for u in usikker_alder.values():
        print(f'   {u["navn"]} (fødselsår {u["fodt"]}) — {u["starter"]} starter')
