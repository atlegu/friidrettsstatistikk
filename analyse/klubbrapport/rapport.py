"""Bygger HTML- og CSV-rapport fra uttrekket i `hent.py`.

Klubbspesifikke forskjeller ligger i en stipendadapter som klubben leverer.
Adapteren må ha:

    FLAT                      navn -> opplysninger, hele stipendlisten
    finn(db_navn)             -> (navn, info) eller None
    merke(info)               -> HTML-merke som settes etter utøvernavnet
    detalj(info)              -> HTML-bit i metalinja, kan være tom
    seksjoner(stip, alle, yngst) -> [(tittel, undertittel, [aid, ...]), ...]
                                 `alle` er samtlige utøver-id-er, `yngst`
                                 sorterer en liste med yngste først.
                                 Adapteren lager også «Øvrige»-seksjonen.
    ikke_funnet_linje(n, i)   -> tekst i lista over ukoblede tildelinger
    sammendrag(stip)          -> setning i sammendragspanelet
    csv_kolonner()            -> kolonnenavn for stipendfeltene
    csv_verdier(info)         -> verdier, info er None for utøvere uten stipend

Alt annet — layout, farger, utskriftsstiler, sortering og klubbskiftelogikk —
er felles.
"""

import csv
import json
from collections import defaultdict
from datetime import date
from html import escape

from .stil import STILARK


def _fodselsnokkel(u):
    """Sorterbar YYYYMMDD. Uten dato faller utøveren først i sitt årskull —
    vi vet ikke bedre, og det er ærligere enn å gjette på en dato."""
    d = u.get('fodt_dato')
    return f"{d[:4]}{d[5:7]}{d[8:10]}" if d else f"{u['fodt']}0000"


def bygg(k, stipend, stille=False):
    d = json.loads(k.datafil.read_text(encoding='utf-8'))
    KLUBB, YEARS, MIN_ALDER = d['klubb'], d['ar'], d['min_alder']
    UT, RAD = d['utovere'], d['rader']
    N_RES = d.get('antall_resultater', 2)
    KLUBB_AR = {a: set(v) for a, v in d.get('klubb_ar', {}).items()}
    SLUTTET, USIKKER = d.get('sluttet', {}), d.get('usikker_alder', [])
    DATO = date.today().isoformat()

    per_utover = defaultdict(lambda: defaultdict(dict))
    starter = defaultdict(lambda: defaultdict(int))
    rekkefolge = {}
    for r in RAD:
        per_utover[r['aid']][r['ovelse']][r['ar']] = r
        starter[r['aid']][r['ar']] += r['starter']
        rekkefolge[r['ovelse']] = min(rekkefolge.get(r['ovelse'], 10**9),
                                      r['so'] or 10**9)

    def yngst_forst(gruppe):
        return sorted(gruppe, key=lambda a: (
            _fodselsnokkel(UT[a]),
            ''.join(chr(0x10FFFF - ord(c)) for c in UT[a]['navn'])), reverse=True)

    STIP = {}
    for aid, u in UT.items():
        t = stipend.finn(u['navn'])
        if t:
            STIP[aid] = dict(t[1], navn=t[0])

    seksjoner = stipend.seksjoner(STIP, list(UT), yngst_forst)
    aids = [a for _, _, gruppe in seksjoner for a in gruppe]
    ikke_funnet = {n: i for n, i in stipend.FLAT.items()
                   if n not in {v['navn'] for v in STIP.values()}}

    aar_sum = {y: {'ut': 0, 'st': 0, 'a_ut': 0, 'a_st': 0} for y in YEARS}
    for aid in aids:
        for y in YEARS:
            if not starter[aid][y]:
                continue
            nokler = ('ut', 'st') if y in KLUBB_AR.get(aid, set()) else ('a_ut', 'a_st')
            aar_sum[y][nokler[0]] += 1
            aar_sum[y][nokler[1]] += starter[aid][y]

    # --- CSV ---------------------------------------------------------------
    csv_sti = k.mappe / f'{k.stamme}.csv'
    with csv_sti.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';')
        res_kol = []
        for i in range(N_RES):
            res_kol += [['Beste', 'Nr. 2', 'Nr. 3', 'Nr. 4'][i], 'Dato', 'Vind']
        w.writerow(['Utøver', 'Fødselsår', 'Fødselsdato', 'Kjønn']
                   + stipend.csv_kolonner()
                   + ['År', 'Klubb', 'Øvelse', 'Starter'] + res_kol)
        for aid in aids:
            u = UT[aid]
            for ov in sorted(per_utover[aid], key=lambda o: rekkefolge[o]):
                for y in YEARS:
                    r = per_utover[aid][ov].get(y)
                    if not r:
                        continue
                    rad = ([u['navn'], u['fodt'], u.get('fodt_dato') or '',
                            u['kjonn'] or '']
                           + stipend.csv_verdier(STIP.get(aid))
                           + [y, r.get('annen_klubb') or KLUBB, ov, r['starter']])
                    for i in range(N_RES):
                        res = r['resultater'][i] if i < len(r['resultater']) else None
                        rad += [res['perf'] if res else '',
                                res['dato'] if res else '',
                                res['vind'] if res and res['vind'] is not None else '']
                    w.writerow(rad)

    # --- HTML --------------------------------------------------------------
    def rute(r):
        if not r:
            return '<td class="tom">–</td>'

        def vis(res):
            v = (f'<span class="v">{res["vind"]:+.1f}</span>'
                 if res['vind'] is not None else '')
            return f'{escape(str(res["perf"]))}{v}'

        res = r['resultater']
        ovrige = ''.join(f'<div class="nest">{vis(x)}</div>' for x in res[1:])
        # Hold høyden lik selv når det er færre resultater enn plassene tilsier
        ovrige += '<div class="nest tom">–</div>' * (N_RES - 1 - len(res[1:]))
        kls = ' class="annen"' if r.get('annen_klubb') else ''
        return (f'<td{kls}><span class="n">{r["starter"]}</span>'
                f'<div class="best">{vis(res[0])}</div>{ovrige}</td>')

    def blokk(aid):
        u = UT[aid]
        kj = {'M': 'M', 'F': 'K'}.get(u['kjonn'], '–')
        tot = sum(starter[aid][y] for y in YEARS)
        kaar = KLUBB_AR.get(aid, set())
        merker = ' '.join(
            f'<span class="badge{"" if starter[aid][y] else " null"}'
            f'{" annen" if starter[aid][y] and y not in kaar else ""}">{y}: '
            f'{starter[aid][y] or "–"}</span>' for y in YEARS)
        ny = (f'<span class="nykommer">Kom til {escape(KLUBB)} i {min(kaar)}</span>'
              if kaar and min(kaar) > YEARS[0] else '')
        st = STIP.get(aid)

        aarsklubb = {r['ar']: r['annen_klubb'] for r in RAD
                     if r['aid'] == aid and r.get('annen_klubb')}
        hoder = ''.join(
            f'<th>{y}' + (f'<div class=klubb>{escape(aarsklubb[y])}</div>'
                          if y in aarsklubb else '') + '</th>' for y in YEARS)
        rader = ''.join(
            f'<tr><th>{escape(ov)}</th>'
            + ''.join(rute(per_utover[aid][ov].get(y)) for y in YEARS) + '</tr>'
            for ov in sorted(per_utover[aid], key=lambda o: rekkefolge[o]))

        return f'''
<section class="ath" data-navn="{escape(u['navn'].lower())}" data-starter="{tot}"
         data-alder="{_fodselsnokkel(u)}">
  <header>
    <h3>{escape(u['navn'])}{stipend.merke(st) if st else ''}</h3>
    <div class="meta"><span>{u.get('fodt_dato') or u['fodt']}</span><span>{kj}</span>
      <span>{YEARS[-1] - u['fodt']} år i {YEARS[-1]}</span>
      <span>{tot} starter totalt</span>{stipend.detalj(st) if st else ''}{ny}</div>
    <div class="badges">{merker}</div>
  </header>
  <table><thead><tr><th>Øvelse</th>{hoder}</tr></thead>
  <tbody>{rader}</tbody></table>
</section>'''

    seksjon_html = ''.join(
        f'<h2 class="gruppe">{escape(tittel)}<span>{under}</span></h2>'
        f'<div class="liste">{"".join(blokk(a) for a in gruppe)}</div>'
        for tittel, under, gruppe in seksjoner if gruppe)

    sumrader = ''.join(
        f'<tr><th>{y}</th><td>{aar_sum[y]["ut"]}</td><td>{aar_sum[y]["st"]}</td>'
        f'<td class="annen-t">{aar_sum[y]["a_ut"] or "–"}</td>'
        f'<td class="annen-t">{aar_sum[y]["a_st"] or "–"}</td></tr>' for y in YEARS)

    def panel(tittel, innhold, varsel=False):
        return (f'<div class="panel{" varsel" if varsel else ""}">'
                f'<strong>{tittel}</strong>{innhold}</div>')

    mangler_html = panel(
        f'Stipendmottakere uten resultater for {escape(KLUBB)} '
        f'{YEARS[0]}–{YEARS[-1]} ({len(ikke_funnet)})',
        '<ul>' + ''.join(f'<li>{stipend.ikke_funnet_linje(n, i)}</li>'
                         for n, i in ikke_funnet.items()) + '</ul>',
        varsel=True) if ikke_funnet else ''

    sluttet_html = panel(
        f'Tatt ut av listen: konkurrerer for annen klubb i {YEARS[-1]} ({len(SLUTTET)})',
        '<table class="sumtab avgang"><thead><tr><th>Utøver</th>'
        f'<th>År i {escape(KLUBB)}</th><th>Klubb i {YEARS[-1]}</th></tr></thead><tbody>'
        + ''.join(f'<tr><th>{escape(v["navn"])}</th>'
                  f'<td>{", ".join(str(x) for x in v["klubb_ar"])}</td>'
                  f'<td>{escape(v["ny_klubb"])}</td></tr>'
                  for v in sorted(SLUTTET.values(), key=lambda x: x['navn']))
        + '</tbody></table>') if SLUTTET else ''

    usikker_html = panel(
        'Holdt utenfor: ugyldig fødselsår',
        '<ul>' + ''.join(
            f'<li>{escape(u["navn"])} — fødselsår registrert som '
            f'<code>{u["fodt"]}</code>, {u["starter"]} '
            f'{"start" if u["starter"] == 1 else "starter"}</li>' for u in USIKKER)
        + '</ul><p class="tabellnote">Aldersfilteret kan ikke anvendes på disse. '
          'De er utelatt framfor å bli feilklassifisert.</p>',
        varsel=True) if USIKKER else ''

    resultatforklaring = ('Halvfet = beste, under = nestbeste' if N_RES == 2
                          else f'Halvfet = beste, deretter nr. 2'
                               + (' og nr. 3' if N_RES >= 3 else ''))

    html = f'''<!doctype html>
<html lang="no"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(KLUBB)} {YEARS[0]}–{YEARS[-1]}</title>
<style>{STILARK}</style></head><body><div class="wrap">

<h1>{escape(KLUBB)}</h1>
<p class="sub">Utøvere {MIN_ALDER} år og eldre · sesongene {YEARS[0]}–{YEARS[-1]}
 · uttrekk {DATO}</p>

<div class="panel">
  <table class="sumtab">
    <thead><tr><th>År</th><th>Utøvere</th><th>Starter</th>
      <th class="annen-t">Utøvere før<br>{escape(KLUBB)}</th>
      <th class="annen-t">Starter før<br>{escape(KLUBB)}</th></tr></thead>
    <tbody>{sumrader}</tbody>
  </table>
  <p class="tabellnote">De to siste kolonnene gjelder utøvere som kom til
  {escape(KLUBB)} senere enn {YEARS[0]}. Sesongene deres fra før overgangen er
  tatt med, med klubben de da representerte. Alder regnes etter kalenderår.
  {stipend.sammendrag(STIP)}</p>
</div>
{mangler_html}
{sluttet_html}
{usikker_html}
<p class="legend">
  <span><span class="swatch"></span>Sesong for en annen klubb, før overgang til {escape(KLUBB)}</span>
  <span>Tall øverst i ruten = antall starter</span>
  <span>{resultatforklaring}</span>
</p>

<div class="tools">
  <input id="q" type="search" placeholder="Søk etter utøver …" autocomplete="off">
  <select id="sort">
    <option value="std">Standardrekkefølge</option>
    <option value="alder">Yngste først</option>
    <option value="alder-eldst">Eldste først</option>
    <option value="navn">Alfabetisk</option>
    <option value="starter">Flest starter</option>
  </select>
  <span class="count" id="count"></span>
</div>

{seksjon_html}
</div>
<script>
const lister=[...document.querySelectorAll('.liste')].map(l=>({{el:l,barn:[...l.children]}})),
      q=document.getElementById('q'), s=document.getElementById('sort'),
      c=document.getElementById('count'),
      totalt=lister.reduce((n,l)=>n+l.barn.length,0);
const cmp={{
  starter:(a,b)=>b.dataset.starter-a.dataset.starter,
  navn:(a,b)=>a.dataset.navn.localeCompare(b.dataset.navn,'no'),
  alder:(a,b)=>b.dataset.alder.localeCompare(a.dataset.alder)
               ||a.dataset.navn.localeCompare(b.dataset.navn,'no'),
  'alder-eldst':(a,b)=>a.dataset.alder.localeCompare(b.dataset.alder)
               ||a.dataset.navn.localeCompare(b.dataset.navn,'no'),
}};
function render(){{
  const t=q.value.trim().toLowerCase();
  let n=0;
  for (const l of lister) {{
    const vis=l.barn.filter(e=>!t||e.dataset.navn.includes(t));
    if (s.value!=='std') vis.sort(cmp[s.value]);
    l.el.replaceChildren(...vis);
    l.el.previousElementSibling.style.display = vis.length ? '' : 'none';
    n+=vis.length;
  }}
  c.textContent=n+' av '+totalt+' utøvere';
}}
q.addEventListener('input',render); s.addEventListener('change',render); render();
</script>
</body></html>'''

    html_sti = k.mappe / f'{k.stamme}.html'
    html_sti.write_text(html, encoding='utf-8')
    if not stille:
        print(f'{len(aids)} utøvere ({len(STIP)} med stipend) '
              f'-> {html_sti.name} og {csv_sti.name}')
        for tittel, under, gruppe in seksjoner:
            if gruppe:
                print(f'  {tittel}: {len(gruppe)}')
    return html_sti
