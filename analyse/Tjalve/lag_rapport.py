"""
Bygger rapport fra tjalve_data.json:

  tjalve_2024_2026.html — søkbar oversikt, én seksjon per utøver
  tjalve_2024_2026.csv  — samme data flatt, semikolon og BOM for norsk Excel

Rekkefølge: stipendmottakere først, gruppe A, B, C og D i den rekkefølgen og
med høyest poengsum øverst i hver gruppe. Deretter øvrige utøvere, yngste først.
"""

import csv
import json
from collections import defaultdict
from datetime import date
from html import escape
from pathlib import Path

from stipend_2026 import FLAT as STIPEND_FLAT, GRUPPER, finn_stipend

DATO = date.today().isoformat()
HERE = Path(__file__).parent
d = json.loads((HERE / 'tjalve_data.json').read_text(encoding='utf-8'))
KLUBB, YEARS, MIN_ALDER = d['klubb'], d['ar'], d['min_alder']
UT, RAD = d['utovere'], d['rader']
USIKKER = d.get('usikker_alder', [])
KLUBB_AR = {k: set(v) for k, v in d.get('tjalve_ar', d.get('vidar_ar', {})).items()}
SLUTTET = d.get('sluttet', {})

# --- Aggregering -----------------------------------------------------------

per_athlete = defaultdict(lambda: defaultdict(dict))   # aid -> ovelse -> ar -> rad
starts = defaultdict(lambda: defaultdict(int))         # aid -> ar -> starter
order = {}                                             # ovelse -> sorteringsnøkkel

for r in RAD:
    per_athlete[r['aid']][r['ovelse']][r['ar']] = r
    starts[r['aid']][r['ar']] += r['starter']
    order[r['ovelse']] = min(order.get(r['ovelse'], 10**9), r['so'] or 10**9)


def fodselsnokkel(u):
    """Sorterbar YYYYMMDD. Uten dato faller utøveren først i sitt årskull."""
    dt = u.get('fodt_dato')
    return f"{dt[:4]}{dt[5:7]}{dt[8:10]}" if dt else f"{u['fodt']}0000"


def yngst_forst(gruppe):
    return sorted(gruppe, key=lambda a: (fodselsnokkel(UT[a]),
                  ''.join(chr(0x10FFFF - ord(c)) for c in UT[a]['navn'])), reverse=True)


# Stipend koblet på navn
STIP = {}
for _aid, _u in UT.items():
    _t = finn_stipend(_u['navn'])
    if _t:
        STIP[_aid] = dict(_t[1], navn=_t[0])

# Gruppe A, B, C, D — innenfor hver gruppe med høyest poengsum øverst, slik
# klubbens eget tildelingsdokument er ordnet. Utøvere uten poengsum (tildelt
# etter skade- eller graviditetsbestemmelsen) legges sist i sin gruppe.
per_gruppe = {g: sorted([a for a in STIP if STIP[a]['gruppe'] == g],
                        key=lambda a: -(STIP[a]['poeng'] or 0))
              for g in GRUPPER}
med_stipend = [a for g in GRUPPER for a in per_gruppe[g]]
uten_stipend = yngst_forst([a for a in UT if a not in STIP])
aids = med_stipend + uten_stipend

IKKE_FUNNET = {n: i for n, i in STIPEND_FLAT.items()
               if n not in {v['navn'] for v in STIP.values()}}

aar_sum = {y: {'utovere': 0, 'starter': 0, 'annen': 0, 'annen_ut': 0} for y in YEARS}
for aid in aids:
    for y in YEARS:
        if not starts[aid][y]:
            continue
        if y in KLUBB_AR.get(aid, set()):
            aar_sum[y]['utovere'] += 1
            aar_sum[y]['starter'] += starts[aid][y]
        else:
            aar_sum[y]['annen_ut'] += 1
            aar_sum[y]['annen'] += starts[aid][y]

# --- CSV -------------------------------------------------------------------

with (HERE / 'tjalve_2024_2026.csv').open('w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f, delimiter=';')
    w.writerow(['Utøver', 'Fødselsår', 'Fødselsdato', 'Kjønn',
                'Stipendgruppe', 'Poeng 2025', 'Gren', 'År', 'Klubb', 'Øvelse', 'Starter',
                'Beste', 'Dato', 'Vind',
                'Nr. 2', 'Dato', 'Vind', 'Nr. 3', 'Dato', 'Vind'])
    for aid in aids:
        u, st = UT[aid], STIP.get(aid, {})
        for ov in sorted(per_athlete[aid], key=lambda o: order[o]):
            for y in YEARS:
                r = per_athlete[aid][ov].get(y)
                if not r:
                    continue
                rad = [u['navn'], u['fodt'], u.get('fodt_dato') or '', u['kjonn'] or '',
                       st.get('gruppe', ''), st.get('poeng', '') or '', st.get('gren', ''),
                       y, r.get('annen_klubb') or KLUBB, ov, r['starter']]
                for i in range(3):
                    res = r['resultater'][i] if i < len(r['resultater']) else None
                    rad += [res['perf'] if res else '', res['dato'] if res else '',
                            res['vind'] if res and res['vind'] is not None else '']
                w.writerow(rad)

# --- HTML ------------------------------------------------------------------


def cell(r):
    if not r:
        return '<td class="tom">–</td>'

    def mark(res):
        v = (f'<span class="v">{res["vind"]:+.1f}</span>'
             if res['vind'] is not None else '')
        return f'{escape(str(res["perf"]))}{v}'

    res = r['resultater']
    beste = f'<div class="best">{mark(res[0])}</div>'
    ovrige = ''.join(f'<div class="nest">{mark(x)}</div>' for x in res[1:])
    # Hold høyden lik selv når det er færre enn tre resultater
    ovrige += '<div class="nest tom">–</div>' * (2 - len(res[1:]))
    kls = ' class="annen"' if r.get('annen_klubb') else ''
    return f'<td{kls}><span class="n">{r["starter"]}</span>{beste}{ovrige}</td>'


def blokk(aid):
    u = UT[aid]
    kj = {'M': 'M', 'F': 'K'}.get(u['kjonn'], '–')
    tot = sum(starts[aid][y] for y in YEARS)
    kaar = KLUBB_AR.get(aid, set())
    badges = ' '.join(
        f'<span class="badge{"" if starts[aid][y] else " null"}'
        f'{" annen" if starts[aid][y] and y not in kaar else ""}">{y}: '
        f'{starts[aid][y] or "–"}</span>' for y in YEARS)
    ny = (f'<span class="nykommer">Kom til {KLUBB} i {min(kaar)}</span>'
          if kaar and min(kaar) > YEARS[0] else '')
    st = STIP.get(aid)
    merke = f' <span class="stipend">{st["gruppe"]}</span>' if st else ''
    detalj = ''
    if st:
        biter = [st['gren']]
        if st['poeng']:
            biter.append(f'{st["poeng"]} p')
        if st['mesterskap']:
            biter.append(st['mesterskap'])
        detalj = f'<span class="kat">{escape(" · ".join(biter))}</span>'

    aarsklubb = {}
    for r in RAD:
        if r['aid'] == aid and r.get('annen_klubb'):
            aarsklubb[r['ar']] = r['annen_klubb']
    aarshoder = ''.join(
        f'<th>{y}{f"<div class=klubb>{escape(aarsklubb[y])}</div>" if y in aarsklubb else ""}</th>'
        for y in YEARS)

    rows = ''.join(
        f'<tr><th>{escape(ov)}</th>'
        + ''.join(cell(per_athlete[aid][ov].get(y)) for y in YEARS) + '</tr>'
        for ov in sorted(per_athlete[aid], key=lambda o: order[o]))

    return f'''
<section class="ath" data-navn="{escape(u['navn'].lower())}" data-starter="{tot}"
         data-alder="{fodselsnokkel(u)}">
  <header>
    <h3>{escape(u['navn'])}{merke}</h3>
    <div class="meta"><span>{u.get('fodt_dato') or u['fodt']}</span><span>{kj}</span>
      <span>{YEARS[-1] - u['fodt']} år i {YEARS[-1]}</span>
      <span>{tot} starter totalt</span>{detalj}{ny}</div>
    <div class="badges">{badges}</div>
  </header>
  <table><thead><tr><th>Øvelse</th>{aarshoder}</tr></thead>
  <tbody>{rows}</tbody></table>
</section>'''


seksjoner = []
for g in GRUPPER:
    if not per_gruppe[g]:
        continue
    seksjoner.append(
        f'<h2 class="gruppe">Stipendgruppe {g} '
        f'<span>{len(per_gruppe[g])} utøvere</span></h2>'
        f'<div class="liste">{"".join(blokk(a) for a in per_gruppe[g])}</div>')
seksjoner.append(
    f'<h2 class="gruppe">Øvrige utøvere <span>{len(uten_stipend)} · yngste først</span></h2>'
    f'<div class="liste">{"".join(blokk(a) for a in uten_stipend)}</div>')

sumrows = ''.join(
    f'<tr><th>{y}</th><td>{aar_sum[y]["utovere"]}</td><td>{aar_sum[y]["starter"]}</td>'
    f'<td class="annen-t">{aar_sum[y]["annen_ut"] or "–"}</td>'
    f'<td class="annen-t">{aar_sum[y]["annen"] or "–"}</td></tr>' for y in YEARS)

gruppesum = ' · '.join(f'{g}: {len(per_gruppe[g])}' for g in GRUPPER if per_gruppe[g])

mangler_html = ''
if IKKE_FUNNET:
    poster = ''.join(
        f'<li>{escape(n)} — gruppe {i["gruppe"]}, {escape(i["gren"])}'
        + (f', {i["poeng"]} p' if i['poeng'] else '') + '</li>'
        for n, i in sorted(IKKE_FUNNET.items(),
                           key=lambda x: (x[1]['gruppe'], -(x[1]['poeng'] or 0))))
    mangler_html = f'''
<div class="panel varsel">
  <strong>Stipendmottakere uten resultater for {KLUBB} 2024–2026 ({len(IKKE_FUNNET)})</strong>
  <ul>{poster}</ul>
</div>'''

sluttet_html = ''
if SLUTTET:
    rader = ''.join(
        f'<tr><th>{escape(v["navn"])}</th>'
        f'<td>{", ".join(str(x) for x in v["tjalve_ar"])}</td>'
        f'<td>{escape(v["ny_klubb"])}</td></tr>'
        for v in sorted(SLUTTET.values(), key=lambda x: x['navn']))
    sluttet_html = f'''
<div class="panel">
  <strong>Tatt ut av listen: konkurrerer for annen klubb i {YEARS[-1]} ({len(SLUTTET)})</strong>
  <table class="sumtab avgang">
    <thead><tr><th>Utøver</th><th>År i {KLUBB}</th><th>Klubb i {YEARS[-1]}</th></tr></thead>
    <tbody>{rader}</tbody>
  </table>
</div>'''

usikker_html = ''
if USIKKER:
    poster = ''.join(
        f'<li>{escape(u["navn"])} — fødselsår registrert som '
        f'<code>{u["fodt"]}</code>, {u["starter"]} '
        f'{"start" if u["starter"] == 1 else "starter"}</li>' for u in USIKKER)
    usikker_html = f'''
<div class="panel varsel">
  <strong>Holdt utenfor: ugyldig fødselsår</strong>
  <ul>{poster}</ul>
</div>'''

html = f'''<!doctype html>
<html lang="no"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{KLUBB} 2024–2026</title>
<style>
:root {{ --bg:#fbfbfa; --fg:#1a1a19; --mut:#6b6b68; --line:#e4e4e1;
        --card:#fff; --acc:#0f5c4a; --nest:#8a8a86; --annen:#a8571c; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:#151514; --fg:#eeeeec; --mut:#9a9a96; --line:#2c2c2a;
          --card:#1d1d1b; --acc:#63c6ab; --nest:#86867f; --annen:#e0925a; }}
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; padding:2rem 1.25rem 4rem; background:var(--bg); color:var(--fg);
  font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }}
.wrap {{ max-width:1080px; margin:0 auto; }}
h1 {{ font-size:1.6rem; margin:0 0 .25rem; letter-spacing:-.02em; }}
.sub {{ color:var(--mut); margin:0 0 1.75rem; }}
.panel {{ background:var(--card); border:1px solid var(--line); border-radius:10px;
  padding:1rem 1.25rem; margin-bottom:1.5rem; }}
.sumtab {{ border-collapse:collapse; }}
.sumtab th,.sumtab td {{ padding:.35rem 1.5rem .35rem 0; text-align:left; }}
.sumtab thead th {{ color:var(--mut); font-weight:500; font-size:.82rem;
  text-transform:uppercase; letter-spacing:.04em; }}
.tools {{ display:flex; gap:.75rem; flex-wrap:wrap; align-items:center; margin-bottom:1.25rem; }}
input,select {{ font:inherit; padding:.5rem .7rem; border:1px solid var(--line);
  border-radius:8px; background:var(--card); color:var(--fg); }}
input {{ flex:1; min-width:220px; }}
.count {{ color:var(--mut); font-size:.88rem; }}
.ath {{ background:var(--card); border:1px solid var(--line); border-radius:10px;
  padding:1rem 1.25rem 1.25rem; margin-bottom:1rem; }}
.ath h3 {{ margin:0; font-size:1.05rem; display:inline; }}
.meta {{ display:flex; gap:.9rem; flex-wrap:wrap; color:var(--mut);
  font-size:.85rem; margin:.2rem 0 .5rem; }}
.badges {{ display:flex; gap:.4rem; flex-wrap:wrap; margin-bottom:.75rem; }}
.badge {{ font-size:.78rem; padding:.15rem .5rem; border-radius:999px;
  background:color-mix(in srgb,var(--acc) 14%,transparent); color:var(--acc); }}
.badge.null {{ background:transparent; color:var(--mut); border:1px dashed var(--line); }}
.ath table {{ width:100%; border-collapse:collapse; }}
.ath thead th {{ font-size:.75rem; text-transform:uppercase; letter-spacing:.04em;
  color:var(--mut); font-weight:500; text-align:left; padding:.3rem .5rem;
  border-bottom:1px solid var(--line); }}
.ath tbody th {{ text-align:left; font-weight:500; padding:.45rem .5rem;
  border-bottom:1px solid var(--line); vertical-align:top; width:32%; }}
.ath td {{ padding:.45rem .5rem; border-bottom:1px solid var(--line);
  vertical-align:top; font-variant-numeric:tabular-nums; }}
.n {{ display:inline-block; font-size:.7rem; color:var(--mut); border:1px solid var(--line);
  border-radius:4px; padding:0 .3rem; margin-bottom:.15rem; }}
.best {{ font-weight:600; }}
.nest {{ color:var(--nest); font-size:.88rem; }}
.tom {{ color:var(--nest); }}
.v {{ font-size:.72rem; color:var(--mut); margin-left:.3rem; }}
.tabellnote {{ color:var(--mut); font-size:.83rem; margin-top:.4rem; }}
.ath td.annen {{ background:color-mix(in srgb,var(--annen) 13%,transparent);
  box-shadow:inset 3px 0 0 var(--annen); }}
.klubb {{ font-size:.72rem; color:var(--annen); margin-top:.2rem; font-weight:500; }}
.badge.annen {{ background:color-mix(in srgb,var(--annen) 16%,transparent); color:var(--annen); }}
.nykommer {{ color:var(--annen); font-weight:500; }}
.annen-t {{ color:var(--annen) !important; }}
.avgang th {{ font-weight:500; padding-right:1.5rem; }}
.legend {{ display:flex; gap:1.25rem; flex-wrap:wrap; align-items:center;
  color:var(--mut); font-size:.83rem; margin:.25rem 0 1.25rem; }}
.swatch {{ display:inline-block; width:.85rem; height:.85rem; border-radius:3px;
  vertical-align:-2px; margin-right:.35rem;
  background:color-mix(in srgb,var(--annen) 30%,transparent);
  box-shadow:inset 2px 0 0 var(--annen); }}
.stipend {{ display:inline-block; background:var(--acc); color:var(--bg);
  font-weight:700; font-size:.78rem; border-radius:4px; padding:0 .38rem;
  vertical-align:2px; margin-left:.15rem; }}
.kat {{ border:1px solid var(--line); border-radius:4px; padding:0 .35rem;
  font-size:.75rem; }}
h2.gruppe {{ font-size:1rem; margin:1.75rem 0 .6rem; letter-spacing:-.01em;
  display:flex; gap:.6rem; align-items:baseline; flex-wrap:wrap; }}
h2.gruppe span {{ font-weight:400; font-size:.83rem; color:var(--mut); }}
.varsel {{ border-left:3px solid #c98a2b; }}
.varsel ul {{ margin:.5rem 0 0; padding-left:1.2rem; }}
.varsel code {{ font-size:.85em; padding:0 .25rem; border-radius:3px;
  background:color-mix(in srgb,var(--fg) 8%,transparent); }}

@media print {{
  @page {{ size:A4 portrait; margin:11mm 10mm; }}
  :root {{ --bg:#fff; --fg:#111; --mut:#555; --line:#ccc; --card:#fff;
          --acc:#0f5c4a; --nest:#666; --annen:#8a4512; }}
  /* macOS-systemfonten kan Chrome bare bygge inn som Type 3-font, som rendres
     med striper i mange PDF-lesere. Helvetica Neue blir ordentlig TrueType. */
  body {{ padding:0; font-size:8.5pt; line-height:1.2;
         font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;
         -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
  .wrap {{ max-width:none; }}
  .tools {{ display:none; }}
  .ath, .panel {{ break-inside:avoid; page-break-inside:avoid; box-shadow:none; }}
  .ath {{ margin-bottom:.3rem; padding:.35rem .55rem .4rem; border-radius:5px; }}
  .ath h3 {{ font-size:.9rem; margin-right:.6rem; }}
  h1 {{ font-size:1.25rem; }}
  h2.gruppe {{ margin:.9rem 0 .35rem; break-after:avoid; page-break-after:avoid; }}
  .ath header {{ display:block; margin-bottom:.15rem; }}
  .meta, .badges {{ display:inline-flex; gap:.55rem; margin:0; vertical-align:middle; }}
  .badge {{ padding:0 .35rem; font-size:.72rem; background:#e6efec; }}
  .badge.annen {{ background:#f6e6d8; }}
  /* Hver rute på én linje: starter · beste / nr. 2 / nr. 3 */
  .ath td .n, .ath td .best, .ath td .nest {{
    display:inline; margin:0; font-size:inherit; }}
  .ath td .n {{ border:0; color:var(--mut); padding:0; }}
  .ath td .n::after {{ content:' · '; }}
  .ath td .nest::before {{ content:' / '; color:var(--nest); }}
  .ath td, .ath tbody th {{ padding:.1rem .4rem; vertical-align:baseline; }}
  .ath thead th {{ padding:.05rem .4rem; font-size:.68rem; }}
  .ath tbody th {{ width:28%; }}
  .v {{ font-size:.9em; }}
  .ath td.annen {{ background:#f6e6d8; box-shadow:inset 2px 0 0 var(--annen); }}
  .swatch {{ background:#f0d8c2; box-shadow:inset 2px 0 0 var(--annen); }}
  .legend {{ margin:.2rem 0 .6rem; font-size:.75rem; }}
}}
@media (max-width:640px) {{ .ath tbody th {{ width:auto; }} body {{ padding:1rem .75rem 3rem; }} }}
</style></head><body><div class="wrap">

<h1>{KLUBB}</h1>
<p class="sub">Utøvere {MIN_ALDER} år og eldre · sesongene {YEARS[0]}–{YEARS[-1]}
 · uttrekk {DATO}</p>

<div class="panel">
  <table class="sumtab">
    <thead><tr><th>År</th><th>Utøvere</th><th>Starter</th>
      <th class="annen-t">Utøvere før<br>{KLUBB}</th>
      <th class="annen-t">Starter før<br>{KLUBB}</th></tr></thead>
    <tbody>{sumrows}</tbody>
  </table>
  <p class="tabellnote">De to siste kolonnene gjelder utøvere som kom til
  {KLUBB} senere enn {YEARS[0]}. Sesongene deres fra før overgangen er tatt med,
  med klubben de da representerte. Alder regnes etter kalenderår.
  Stipend: {len(STIP)} av {len(STIPEND_FLAT)} tildelinger er koblet ({gruppesum}).</p>
</div>
{mangler_html}
{sluttet_html}
{usikker_html}
<p class="legend">
  <span><span class="swatch"></span>Sesong for en annen klubb, før overgang til {KLUBB}</span>
  <span>Tall øverst i ruten = antall starter</span>
  <span>Halvfet = beste, deretter nr. 2 og nr. 3</span>
</p>

<div class="tools">
  <input id="q" type="search" placeholder="Søk etter utøver …" autocomplete="off">
  <select id="sort">
    <option value="std">Stipendgruppe, så alder</option>
    <option value="alder">Yngste først</option>
    <option value="alder-eldst">Eldste først</option>
    <option value="navn">Alfabetisk</option>
    <option value="starter">Flest starter</option>
  </select>
  <span class="count" id="count"></span>
</div>

{''.join(seksjoner)}

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

(HERE / 'tjalve_2024_2026.html').write_text(html, encoding='utf-8')
print(f'{len(aids)} utøvere ({len(STIP)} med stipend) -> tjalve_2024_2026.html og .csv')
for g in GRUPPER:
    if per_gruppe[g]:
        print(f'  Gruppe {g}: {len(per_gruppe[g])}')
print(f'  Øvrige:   {len(uten_stipend)}')
