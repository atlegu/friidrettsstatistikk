"""
Bygger rapport fra vidar_data.json:

  vidar_2024_2026.html — søkbar oversikt, én seksjon per utøver
  vidar_2024_2026.csv  — samme data flatt, semikolon og BOM for norsk Excel
"""

import csv
import json
from collections import defaultdict
from html import escape
from pathlib import Path

HERE = Path(__file__).parent
d = json.loads((HERE / 'vidar_data.json').read_text(encoding='utf-8'))
KLUBB, YEARS, MIN_ALDER = d['klubb'], d['ar'], d['min_alder']
UT, RAD = d['utovere'], d['rader']
USIKKER = d.get('usikker_alder', [])

# --- Aggregering -----------------------------------------------------------

per_athlete = defaultdict(lambda: defaultdict(dict))   # aid -> ovelse -> ar -> rad
starts = defaultdict(lambda: defaultdict(int))         # aid -> ar -> starter
order = {}                                             # ovelse -> sorteringsnøkkel

for r in RAD:
    per_athlete[r['aid']][r['ovelse']][r['ar']] = r
    starts[r['aid']][r['ar']] += r['starter']
    order[r['ovelse']] = min(order.get(r['ovelse'], 10**9), r['so'] or 10**9)

aids = sorted(UT, key=lambda a: UT[a]['navn'])

aar_sum = {y: {'utovere': 0, 'starter': 0} for y in YEARS}
for aid in aids:
    for y in YEARS:
        if starts[aid][y]:
            aar_sum[y]['utovere'] += 1
            aar_sum[y]['starter'] += starts[aid][y]

# --- CSV -------------------------------------------------------------------

csv_path = HERE / 'vidar_2024_2026.csv'
with csv_path.open('w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f, delimiter=';')
    w.writerow(['Utøver', 'Fødselsår', 'Kjønn', 'År', 'Øvelse', 'Starter',
                'Beste', 'Dato beste', 'Vind beste',
                'Nestbeste', 'Dato nestbeste', 'Vind nestbeste'])
    for aid in aids:
        u = UT[aid]
        for ov in sorted(per_athlete[aid], key=lambda o: order[o]):
            for y in YEARS:
                r = per_athlete[aid][ov].get(y)
                if not r:
                    continue
                w.writerow([u['navn'], u['fodt'], u['kjonn'] or '', y, ov, r['starter'],
                            r['beste'], r['beste_dato'], r['beste_vind'] if r['beste_vind'] is not None else '',
                            r['nest'] or '', r['nest_dato'] or '',
                            r['nest_vind'] if r['nest_vind'] is not None else ''])

# --- HTML ------------------------------------------------------------------

def cell(r):
    if not r:
        return '<td class="tom">–</td>'
    def mark(p, wind):
        w = f'<span class="v">{wind:+.1f}</span>' if wind is not None else ''
        return f'{escape(str(p))}{w}'
    nest = (f'<div class="nest">{mark(r["nest"], r["nest_vind"])}</div>'
            if r['nest'] else '<div class="nest tom">–</div>')
    return (f'<td><span class="n">{r["starter"]}</span>'
            f'<div class="best">{mark(r["beste"], r["beste_vind"])}</div>{nest}</td>')

blocks = []
for aid in aids:
    u = UT[aid]
    kj = {'M': 'M', 'F': 'K'}.get(u['kjonn'], '–')
    tot = sum(starts[aid][y] for y in YEARS)
    badges = ' '.join(
        f'<span class="badge{"" if starts[aid][y] else " null"}">{y}: '
        f'{starts[aid][y] or "–"}</span>' for y in YEARS)
    rows = []
    for ov in sorted(per_athlete[aid], key=lambda o: order[o]):
        cells = ''.join(cell(per_athlete[aid][ov].get(y)) for y in YEARS)
        rows.append(f'<tr><th>{escape(ov)}</th>{cells}</tr>')
    blocks.append(f'''
<section class="ath" data-navn="{escape(u['navn'].lower())}" data-starter="{tot}">
  <header>
    <h3>{escape(u['navn'])}</h3>
    <div class="meta"><span>{u['fodt']}</span><span>{kj}</span>
      <span>{2026 - u['fodt']} år i 2026</span><span>{tot} starter totalt</span></div>
    <div class="badges">{badges}</div>
  </header>
  <table><thead><tr><th>Øvelse</th>{''.join(f'<th>{y}</th>' for y in YEARS)}</tr></thead>
  <tbody>{''.join(rows)}</tbody></table>
</section>''')

sumrows = ''.join(
    f'<tr><th>{y}</th><td>{aar_sum[y]["utovere"]}</td>'
    f'<td>{aar_sum[y]["starter"]}</td></tr>' for y in YEARS)

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
  <p class="tabellnote">Aldersfilteret kan ikke anvendes på disse. De er utelatt
  framfor å bli feilklassifisert — fødselsår 0 ville gitt «2026 år» i 2026.
  Dette er et datafeil i basen, ikke i uttrekket.</p>
</div>'''

html = f'''<!doctype html>
<html lang="no"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{KLUBB} 2024–2026</title>
<style>
:root {{ --bg:#fbfbfa; --fg:#1a1a19; --mut:#6b6b68; --line:#e4e4e1;
        --card:#fff; --acc:#0f5c4a; --nest:#8a8a86; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:#151514; --fg:#eeeeec; --mut:#9a9a96; --line:#2c2c2a;
          --card:#1d1d1b; --acc:#63c6ab; --nest:#86867f; }}
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
.ath h3 {{ margin:0; font-size:1.05rem; }}
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
  border-bottom:1px solid var(--line); vertical-align:top; width:34%; }}
.ath td {{ padding:.45rem .5rem; border-bottom:1px solid var(--line);
  vertical-align:top; font-variant-numeric:tabular-nums; }}
.n {{ display:inline-block; font-size:.7rem; color:var(--mut); border:1px solid var(--line);
  border-radius:4px; padding:0 .3rem; margin-bottom:.15rem; }}
.best {{ font-weight:600; }}
.nest {{ color:var(--nest); font-size:.88rem; }}
.tom {{ color:var(--nest); }}
.v {{ font-size:.72rem; color:var(--mut); margin-left:.3rem; }}
.tabellnote {{ color:var(--mut); font-size:.83rem; margin-top:.4rem; }}
.varsel {{ border-left:3px solid #c98a2b; }}
.varsel ul {{ margin:.5rem 0 0; padding-left:1.2rem; }}
.varsel code {{ font-size:.85em; padding:0 .25rem; border-radius:3px;
  background:color-mix(in srgb,var(--fg) 8%,transparent); }}
@media (max-width:640px) {{ .ath tbody th {{ width:auto; }} body {{ padding:1rem .75rem 3rem; }} }}
</style></head><body><div class="wrap">

<h1>{KLUBB}</h1>
<p class="sub">Utøvere {MIN_ALDER} år og eldre · sesongene {YEARS[0]}–{YEARS[-1]}</p>

<div class="panel">
  <table class="sumtab">
    <thead><tr><th>År</th><th>Utøvere</th><th>Starter</th></tr></thead>
    <tbody>{sumrows}</tbody>
  </table>
  <p class="tabellnote">Alder regnes etter kalenderår, altså konkurranseår minus
  fødselsår. Klubbtilhørighet er hentet fra klubben utøveren representerte i det
  enkelte stevnet.</p>
</div>
{usikker_html}
<div class="tools">
  <input id="q" type="search" placeholder="Søk etter utøver …" autocomplete="off">
  <select id="sort">
    <option value="navn">Sorter alfabetisk</option>
    <option value="starter">Sorter etter antall starter</option>
  </select>
  <span class="count" id="count"></span>
</div>

<div id="list">{''.join(blocks)}</div>

<p class="tabellnote">I hver rute: antall starter øverst, beste resultat i halvfet,
nestbeste under. Vind vises der den er registrert.</p>

<script>
const list=document.getElementById('list'), q=document.getElementById('q'),
      s=document.getElementById('sort'), c=document.getElementById('count'),
      all=[...list.children];
function render(){{
  const t=q.value.trim().toLowerCase();
  const vis=all.filter(e=>!t||e.dataset.navn.includes(t));
  vis.sort(s.value==='starter'
    ? (a,b)=>b.dataset.starter-a.dataset.starter
    : (a,b)=>a.dataset.navn.localeCompare(b.dataset.navn,'no'));
  list.replaceChildren(...vis);
  c.textContent=vis.length+' av {len(aids)} utøvere';
}}
q.addEventListener('input',render); s.addEventListener('change',render); render();
</script>
</div></body></html>'''

(HERE / 'vidar_2024_2026.html').write_text(html, encoding='utf-8')
print(f'{len(aids)} utøvere skrevet til vidar_2024_2026.html og .csv')
for y in YEARS:
    print(f'  {y}: {aar_sum[y]["utovere"]:3d} utøvere, {aar_sum[y]["starter"]:4d} starter')
