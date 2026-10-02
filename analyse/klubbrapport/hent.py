"""Uttrekk av klubbdata fra resultatdatabasen.

Felles for alle klubbrapporter. Klubbspesifikke valg — klubb, år, aldersgrense
og hvor mange resultater som skal tas med — settes i `Konfig`.

TO REGLER OM KLUBBSKIFTE
------------------------
1. Er utøverens første sesong i klubben etter det første året i perioden,
   hentes sesongene FØR overgangen også, med klubben de da representerte.
2. Utøvere med klubbresultater tidlig i perioden, som i siste året
   konkurrerer for en annen klubb og ikke for klubben, er sluttet og tas ut.

Aldersregel: norsk friidrett bruker kalenderår — alder = konkurranseår minus
fødselsår, uten justering for bursdag. Se CLAUDE.md punkt 6.

Klubbtilhørighet hentes fra `results.club_id`, altså klubben utøveren faktisk
representerte i det enkelte stevnet — ikke `athletes.current_club_id`.
"""

import json
import os
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

SELECT = ('id,performance,performance_value,wind,date,athlete_id,club_id,'
          'athletes(full_name,birth_year,birth_date,gender),'
          'events(name,result_type,sort_order)')

# Basen har hatt utøvere med ugyldige fødselsår (0, 752, 9171 …). De er ryddet
# 2026-08-21 og sperret med en databasesjekk, men uttrekket validerer likevel —
# et aldersfilter skal aldri stole blindt på feltet.
BY_MIN = 1860


@dataclass
class Konfig:
    klubb_id: str
    klubb_navn: str
    mappe: Path
    ar: list = field(default_factory=lambda: [2024, 2025, 2026])
    min_alder: int = 15
    antall_resultater: int = 3

    @property
    def datafil(self):
        return self.mappe / 'data.json'

    @property
    def stamme(self):
        return f"{self.mappe.name.lower()}_{self.ar[0]}_{self.ar[-1]}"


def _klient():
    load_dotenv(Path(__file__).resolve().parents[2] / 'scraper' / '.env')
    return create_client(os.environ['SUPABASE_URL'],
                         os.environ['SUPABASE_SERVICE_KEY'])


def _hent(sb, ar, **filtre):
    """Nøkkelbasert paginering. `.range()` uten sortering mister rader —
    PostgREST garanterer ikke stabil rekkefølge uten `order by`."""
    ut, siste = [], '00000000-0000-0000-0000-000000000000'
    while True:
        q = (sb.table('results').select(SELECT)
               .gte('date', f'{ar[0]}-01-01').lte('date', f'{ar[-1]}-12-31')
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


def _sorteringsnokkel(x, rt):
    """Tid: lavest vinner. Lengde, høyde og poeng: høyest vinner."""
    v = x['val']
    return (1, 0) if v is None else (0, v if rt == 'time' else -v)


def hent(k: Konfig, stille=False):
    def si(*a):
        if not stille:
            print(*a)

    sb = _klient()
    by_maks = max(k.ar)

    klubbrader = _hent(sb, k.ar, club_id=k.klubb_id)
    si(f'{k.klubb_navn}-resultater {k.ar[0]}–{k.ar[-1]}: {len(klubbrader)}')

    klubb_ar = defaultdict(set)
    utovere, usikker_alder = {}, {}
    for r in klubbrader:
        a = r.get('athletes')
        if not a or not r.get('date'):
            continue
        by = a.get('birth_year')
        if by is None or not (BY_MIN <= by <= by_maks):
            u = usikker_alder.setdefault(
                r['athlete_id'], {'navn': a['full_name'], 'fodt': by, 'starter': 0})
            u['starter'] += 1
            continue
        klubb_ar[r['athlete_id']].add(int(r['date'][:4]))
        utovere[r['athlete_id']] = {'navn': a['full_name'], 'fodt': by,
                                    'fodt_dato': a.get('birth_date'),
                                    'kjonn': a.get('gender')}

    aids = list(utovere)
    alle = []
    for i in range(0, len(aids), 100):
        alle.extend(_hent(sb, k.ar, athlete_id=aids[i:i + 100]))
    si(f'Alle resultater for de samme utøverne: {len(alle)}')

    klubber = {c['id']: c['name'] for c in
               sb.table('clubs').select('id,name').execute().data}

    # Regel 2: sluttet i klubben
    siste_ar = k.ar[-1]
    har_annen, har_egen = defaultdict(set), set()
    for r in alle:
        if not r.get('date') or int(r['date'][:4]) != siste_ar:
            continue
        if r['club_id'] == k.klubb_id:
            har_egen.add(r['athlete_id'])
        elif r['club_id']:
            har_annen[r['athlete_id']].add(r['club_id'])

    sluttet = {}
    for aid in list(utovere):
        tidligere = klubb_ar[aid] & set(k.ar[:-1])
        if tidligere and aid not in har_egen and har_annen.get(aid):
            sluttet[aid] = {
                'navn': utovere[aid]['navn'],
                'ny_klubb': ', '.join(sorted(klubber.get(c, '?')
                                             for c in har_annen[aid])),
                'klubb_ar': sorted(tidligere),
            }
            del utovere[aid]
    si(f'Tatt ut — konkurrerer for annen klubb i {siste_ar}: {len(sluttet)}')

    # Bygg radene
    grupper, for_unge = defaultdict(list), 0
    for r in alle:
        aid = r['athlete_id']
        if aid not in utovere or not r.get('date'):
            continue
        e = r.get('events')
        if not e:
            continue
        ar = int(r['date'][:4])
        if ar - utovere[aid]['fodt'] < k.min_alder:
            for_unge += 1
            continue
        egen = r['club_id'] == k.klubb_id
        # Regel 1: annen klubb bare for sesongene FØR overgangen. Ellers ville
        # vi dratt inn parallelle klubbytter og år etter at de sluttet.
        if not egen and ar >= min(klubb_ar[aid]):
            continue
        grupper[(aid, ar, e['name'])].append({
            'perf': r['performance'], 'val': r['performance_value'],
            'wind': r['wind'], 'dato': r['date'],
            'rt': e['result_type'], 'so': e.get('sort_order') or 0,
            'klubb': None if egen else klubber.get(r['club_id'], 'Ukjent klubb'),
        })
    si(f'Utelatt {for_unge} starter fra utøvere under {k.min_alder} år')

    rader = []
    for (aid, ar, ovelse), lst in grupper.items():
        rt = lst[0]['rt']
        lst.sort(key=lambda x: _sorteringsnokkel(x, rt))
        andre = sorted({x['klubb'] for x in lst if x['klubb']})
        rader.append({
            'aid': aid, 'ar': ar, 'ovelse': ovelse, 'rt': rt, 'so': lst[0]['so'],
            'starter': len(lst),
            'annen_klubb': ', '.join(andre) if andre else None,
            'resultater': [{'perf': x['perf'], 'dato': x['dato'], 'vind': x['wind']}
                           for x in lst[:k.antall_resultater]],
        })

    # Utøvere som er for unge i alle årene har ingen rader igjen
    med_rader = {r['aid'] for r in rader}
    utovere = {a: v for a, v in utovere.items() if a in med_rader}

    k.datafil.write_text(json.dumps({
        'klubb': k.klubb_navn, 'ar': k.ar, 'min_alder': k.min_alder,
        'antall_resultater': k.antall_resultater,
        'utovere': utovere, 'rader': rader,
        'klubb_ar': {a: sorted(v) for a, v in klubb_ar.items() if a in utovere},
        'sluttet': sluttet,
        'usikker_alder': list(usikker_alder.values()),
    }, ensure_ascii=False, indent=1), encoding='utf-8')

    fra_annen = sum(r['starter'] for r in rader if r['annen_klubb'])
    si(f'\n{len(utovere)} utøvere, {sum(r["starter"] for r in rader)} starter '
       f'({fra_annen} fra andre klubber), {len(rader)} rader -> {k.datafil.name}')
    if usikker_alder:
        si(f'{len(usikker_alder)} utøver(e) holdt utenfor pga. ugyldig fødselsår')
