#!/usr/bin/env python3
"""Bygg PRESENTASJON.md til lysbilder i 16:9.

    ./lag_lysbilder.py

Hver `---` i markdown blir et nytt lysbilde. Teksten er satt stor nok til å
leses gjennom Teams-komprimering, der skjermdeling ofte skaleres ned.

Samme fontvalg som tilbudet: Helvetica Neue, ikke macOS-systemfonten, som
Chrome bygger inn som Type 3.
"""

import re
import subprocess
import sys
from pathlib import Path

HER = Path(__file__).resolve().parent
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

# 16:9 i millimeter
BREDDE, HOYDE = 338, 190

MAL = """<!doctype html>
<html lang="nb"><head><meta charset="utf-8"><title>{tittel}</title>
<style>
@page {{ size: {b}mm {h}mm; margin: 0; }}
html {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  margin: 0; color: #16191d; font-size: 15pt; line-height: 1.4;
}}

.lysbilde {{
  width: {b}mm; height: {h}mm; box-sizing: border-box;
  padding: 16mm 18mm; break-after: page; position: relative;
  display: flex; flex-direction: column; justify-content: flex-start;
  overflow: hidden;
}}
.lysbilde:last-child {{ break-after: auto; }}

/* Tittelside: første lysbilde */
.lysbilde.tittel {{ justify-content: center; background: #1b3a6b; color: #fff; }}
.lysbilde.tittel h1 {{ font-size: 34pt; color: #fff; border: none; margin: 0 0 6mm; padding: 0; }}
.lysbilde.tittel h2 {{ font-size: 17pt; color: #b9c9e2; font-weight: 400; margin: 0; border: none; }}

h1 {{
  font-size: 25pt; color: #1b3a6b; margin: 0 0 7mm;
  padding-bottom: 3mm; border-bottom: 2pt solid #1b3a6b;
  letter-spacing: -0.3pt;
}}
h2 {{ font-size: 19pt; color: #1b3a6b; margin: 0 0 4mm; border: none; }}
h3 {{ font-size: 15pt; color: #2c3644; margin: 5mm 0 2mm; }}

p {{ margin: 0 0 3.5mm; }}
strong {{ color: #0d1117; }}

table {{ border-collapse: collapse; width: 100%; margin: 3mm 0 4mm; font-size: 13pt; }}
th {{
  background: #eef2f7; text-align: left; font-weight: 600;
  padding: 2mm 3mm; border-bottom: 1pt solid #b9c4d2; color: #1b3a6b;
}}
td {{ padding: 1.8mm 3mm; border-bottom: 0.5pt solid #dde3ea; vertical-align: top; }}

ul, ol {{ margin: 0 0 3mm; padding-left: 7mm; }}
li {{ margin-bottom: 1.6mm; }}

hr {{ display: none; }}
code {{ font-family: Menlo, monospace; font-size: 12pt; background: #eef1f5;
        padding: 0.4mm 1.4mm; border-radius: 1mm; color: #294066; }}

/* Det store tallet på lysbilde 3 */
.lysbilde h2 + p {{ font-size: 15pt; }}
.tall h2 {{ font-size: 54pt; color: #1b3a6b; letter-spacing: -1.5pt; margin: 2mm 0 1mm; }}

/* Sidetall */
.nr {{ position: absolute; bottom: 8mm; right: 18mm; font-size: 10pt; color: #8a95a3; }}
.lysbilde.tittel .nr {{ display: none; }}
</style></head><body>
{innhold}
</body></html>
"""


def main():
    md = HER / 'PRESENTASJON.md'
    frag = subprocess.run(
        ['pandoc', str(md), '-f', 'markdown+pipe_tables', '-t', 'html5'],
        check=True, capture_output=True, text=True).stdout

    # pandoc gjør «---» til <hr />; del der
    deler = [d.strip() for d in re.split(r'<hr\s*/?>', frag) if d.strip()]

    sider = []
    for i, d in enumerate(deler):
        klasser = ['lysbilde']
        if i == 0:
            klasser.append('tittel')
        # Lysbildet med det store tallet kjennes på at en h2 er bare siffer
        if re.search(r'<h2[^>]*>[\d\s ]+</h2>', d):
            klasser.append('tall')
        nr = '' if i == 0 else f'<div class="nr">{i + 1} / {len(deler)}</div>'
        sider.append(f'<section class="{" ".join(klasser)}">{d}{nr}</section>')

    html = HER / 'PRESENTASJON.html'
    html.write_text(MAL.format(tittel='Presentasjon', innhold='\n'.join(sider),
                               b=BREDDE, h=HOYDE), encoding='utf-8')

    pdf = HER / 'PRESENTASJON.pdf'
    subprocess.run([
        CHROME, '--headless', '--disable-gpu', '--no-pdf-header-footer',
        '--run-all-compositor-stages-before-draw', '--virtual-time-budget=20000',
        f'--print-to-pdf={pdf}', f'file://{html.resolve()}',
    ], check=True, capture_output=True)

    info = subprocess.run(['pdfinfo', str(pdf)], capture_output=True, text=True)
    n = next((l.split()[1] for l in info.stdout.splitlines()
              if l.startswith('Pages:')), '?')
    fonter = subprocess.run(['pdffonts', str(pdf)], capture_output=True, text=True)
    advarsel = '  ADVARSEL: Type 3-font!' if 'Type 3' in fonter.stdout else ''
    print(f'{pdf.name} — {n} lysbilder (markdown har {len(deler)}){advarsel}')
    if n != '?' and int(n) != len(deler):
        print('  OBS: sidetall stemmer ikke med antall lysbilder — noe flyter over.')


if __name__ == '__main__':
    main()
