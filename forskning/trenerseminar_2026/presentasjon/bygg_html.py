#!/usr/bin/env python3
"""Bygger én selvstendig HTML-fil av presentasjonen (deck.json + slides/*.html).

Figurene bakes inn som data-URI-er, så filen virker uten nett. Piltaster/mellomrom
blar, F gir fullskjerm, N viser talemanus, Esc lukker. Åpne i Safari/Chrome.

    python3 bygg_html.py
"""
import base64, json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
UT = HERE / "Foredrag_bredde_topp.html"

# opplastede figurer -> lokale filer
BLOB = {
    "2b7ee10172863262166a1d0b2928a94c": "analyse/trenerartikkel/output/figM1_ungdomsbredde.png",
    "ee0dbb66eae2ec6038f9cddc64500f29": "analyse/trenerartikkel/output/fig5b_frafall_fra_10.png",
    "bfee6c1ae0a978abfab41e6d5ca70b14": "analyse/trenerartikkel/output/figM4_debut.png",
    "bac233d7301da3562b090c4412fa76c2": "analyse/trenerartikkel/output/fig6_dybde.png",
    "b402f880a62c8773dbb98030ef1df806": "forskning/fagnytt/figurer/fig6_frafall.png",
    "9631e8784e5e05940be31260786e0bbd": "forskning/fagnytt/figurer/fig3_rae.png",
    "ddd2583741a2b2b01bf078a08d45c856": "forskning/fagnytt/figurer/fig4_volum.png",
    "69dd49a0306283d3cb14fe648ef38ded": "forskning/fagnytt/figurer/fig1_utvikling.png",
    "5bda4f826fe63379a73db246a7946992": "forskning/fagnytt/figurer/fig2_kjonn.png",
    "193eb5265a745e55f3901b038fe701c7": "forskning/fagnytt/figurer/fig7_kule.png",
    "b3d295c8e58eff92801fb88b7d047cc6": "forskning/fagnytt/figurer/fig8_arvtakere.png",
    "c5c79940817f892d471162bb9c75417b": "forskning/fagnytt/figurer/lek_fig2_kast.png",
    "98213fa2375c8825d1800b93c13f59b3": "forskning/fagnytt/figurer/lek_fig3_forbedring.png",
    "7a74126aa47ed4a9ebfe39ab5efa5ca7": "forskning/fagnytt/figurer/sko_fig1_trend.png",
    "c45ab8d87eb25480bc047b46441ec592": "forskning/fagnytt/blad/bilder/forside_jaeger.jpg",
}


def data_uri(rel):
    b = (ROOT / rel).read_bytes()
    mime = "image/jpeg" if rel.endswith((".jpg", ".jpeg")) else "image/png"
    return f"data:{mime};base64," + base64.b64encode(b).decode()


def main():
    deck = json.loads((HERE / "deck.json").read_text())
    slides, notes = [], []
    for sid in deck["order"]:
        html = (HERE / "slides" / f"{sid}.html").read_text()
        m = re.search(r"<aside>(.*?)</aside>", html, re.S)
        notes.append(m.group(1).strip() if m else "")
        html = re.sub(r"<aside>.*?</aside>", "", html, flags=re.S)
        html = re.sub(r'src="/_blob/([0-9a-f]+)"', lambda m: f'src="{data_uri(BLOB[m.group(1)])}"', html)
        slides.append(html.strip())
    n = len(slides)
    css = """
html,body{margin:0;height:100%;background:#0f2740;overflow:hidden;font-family:'Avenir Next','Rubik',Arial,sans-serif}
#stage{position:absolute;left:50%;top:50%;width:1920px;height:1080px;transform-origin:0 0}
section{position:absolute;left:0;top:0;width:1920px;height:1080px;box-sizing:border-box}
section:not(.aktiv){display:none !important}

section *{box-sizing:border-box}
h1,h2,h3,p,ul,ol{margin:0}
h1{font-size:96px;font-weight:600;line-height:1.1}h2{font-size:64px;font-weight:600;line-height:1.15}h3{font-size:44px;font-weight:600;line-height:1.2}p{font-size:32px;line-height:1.4}
ul{padding-left:1.1em}li{margin:0}
hr{border:none;height:0;margin:0}
img{display:block}
table{border-collapse:collapse}
th,td{padding:0.35em 0.6em;border-bottom:1px solid #D9DEE6;text-align:left;font-weight:400}
th{font-weight:600}
tr{background:transparent}
#teller{position:fixed;right:18px;bottom:12px;color:#8aa3bd;font:14px/1 'Avenir Next',Arial,sans-serif;opacity:.8}
#notat{position:fixed;left:0;right:0;bottom:0;max-height:38%;overflow:auto;background:#FBF3EE;color:#2B2B2B;border-top:6px solid #D9480F;padding:18px 28px;font:18px/1.5 'Charter','Source Serif 4',Georgia,serif;display:none}
#notat.vis{display:block}
#hjelp{position:fixed;left:18px;bottom:12px;color:#8aa3bd;font:14px/1 'Avenir Next',Arial,sans-serif;opacity:.8}
"""
    js = f"""
const N={n};const NOTAT={json.dumps(notes, ensure_ascii=False)};
let i=Math.max(0,Math.min(N-1,(parseInt(location.hash.slice(1))||1)-1));
const secs=document.querySelectorAll('#stage > section');
function vis(){{secs.forEach((s,k)=>s.classList.toggle('aktiv',k===i));location.hash=i+1;document.getElementById('teller').textContent=(i+1)+' / '+N;document.getElementById('notat').textContent=NOTAT[i]||'(ingen notater)';}}
function skaler(){{const s=Math.min(innerWidth/1920,innerHeight/1080);const st=document.getElementById('stage');st.style.transform=`translate(-50%,-50%) scale(${{s}})`;st.style.transformOrigin='center';}}
function neste(){{if(i<N-1){{i++;vis();}}}}function forrige(){{if(i>0){{i--;vis();}}}}
addEventListener('keydown',e=>{{if(['ArrowRight','ArrowDown',' ','PageDown','Enter'].includes(e.key)){{e.preventDefault();neste();}}
else if(['ArrowLeft','ArrowUp','PageUp','Backspace'].includes(e.key)){{e.preventDefault();forrige();}}
else if(e.key==='Home'){{i=0;vis();}}else if(e.key==='End'){{i=N-1;vis();}}
else if(e.key.toLowerCase()==='f'){{document.documentElement.requestFullscreen?.();}}
else if(e.key.toLowerCase()==='n'){{document.getElementById('notat').classList.toggle('vis');}}
else if(e.key==='Escape'){{document.getElementById('notat').classList.remove('vis');}}}});
addEventListener('click',e=>{{if(e.target.closest('#notat'))return;(e.clientX>innerWidth/3)?neste():forrige();}});
addEventListener('resize',skaler);addEventListener('hashchange',()=>{{const k=(parseInt(location.hash.slice(1))||1)-1;if(k!==i&&k>=0&&k<N){{i=k;vis();}}}});
skaler();vis();
"""
    out = f"""<!DOCTYPE html>
<html lang="nb"><head><meta charset="utf-8"><title>{deck["title"]} · Trenerseminaret 2026</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;600;700;800&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&display=swap">
<style>{css}</style></head>
<body>
<div id="stage">
{chr(10).join(slides)}
</div>
<div id="notat"></div>
<div id="hjelp">Piler/mellomrom: bla · F: fullskjerm · N: talemanus</div>
<div id="teller"></div>
<script>{js}</script>
</body></html>
"""
    # Fagnytt-fontene finnes lokalt på Mac; bruk dem først, Google-fontene som reserve
    out = out.replace("font-family:'Rubik', Arial, sans-serif", "font-family:'Avenir Next','Rubik',Arial,sans-serif")
    out = out.replace("font-family:'Source Serif 4', Georgia, serif", "font-family:'Charter','Source Serif 4',Georgia,serif")
    UT.write_text(out, encoding="utf-8")
    print(f"Skrev {UT} ({UT.stat().st_size/1e6:.1f} MB, {n} slides)")


if __name__ == "__main__":
    main()
