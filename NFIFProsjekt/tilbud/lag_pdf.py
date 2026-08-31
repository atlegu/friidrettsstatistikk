#!/usr/bin/env python3
"""Bygg PDF av tilbudsdokumentene.

    ./lag_pdf.py              alle
    ./lag_pdf.py TILBUD.md    én fil

Markdown -> HTML-fragment med pandoc -> egen mal -> PDF med headless Chrome.

To ting som er lært den harde veien:

**Ikke bruk pandoc --standalone.** Malen har egen CSS med `max-width: 36em`,
som vinner over vår og presser teksten inn i en smal kolonne midt på siden.
Vi lager derfor HTML-rammen selv.

**Fonten må ikke være macOS-systemfonten.** Chrome bygger den inn som Type 3,
som rendres med striper i mange lesere og ikke lar seg søke i. Helvetica Neue
gir CID TrueType. Kontroller med `pdffonts`.
"""

import subprocess
import sys
from pathlib import Path

HER = Path(__file__).resolve().parent
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

MAL = """<!doctype html>
<html lang="nb"><head><meta charset="utf-8"><title>{tittel}</title>
<style>
@page {{
  size: A4;
  margin: 20mm 18mm 18mm 18mm;
  @bottom-center {{ content: counter(page); }}
}}

html {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}

body {{
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 10pt;
  line-height: 1.48;
  color: #16191d;
  margin: 0;
  max-width: none;
  hyphens: none;
}}

/* Kapitteloverskrifter — ny side, unntatt den aller første */
h1 {{
  font-size: 14.5pt;
  margin: 0 0 10pt;
  padding-bottom: 5pt;
  border-bottom: 1.6pt solid #1b3a6b;
  color: #1b3a6b;
  letter-spacing: -0.2pt;
  break-before: page;
  break-after: avoid;
}}
h1:first-of-type {{ break-before: auto; }}

h2 {{ font-size: 11.4pt; margin: 16pt 0 6pt; color: #1b3a6b; break-after: avoid; }}
h3 {{ font-size: 10.2pt; margin: 12pt 0 4pt; color: #2c3644; break-after: avoid; }}

p {{ margin: 0 0 7.5pt; orphans: 2; widows: 2; }}
strong {{ color: #0d1117; }}
em {{ color: #3a4452; }}

/* Lange tabeller får brekke over sider — ellers skyves en 30-raders
   kravsporingstabell i sin helhet til neste side og etterlater et tomt ark.
   Enkeltrader brekkes ikke, og overskriftsraden gjentas. */
table {{
  border-collapse: collapse; width: 100%;
  margin: 9pt 0 12pt; font-size: 9pt;
}}
thead {{ display: table-header-group; }}
tr {{ break-inside: avoid; }}
th {{
  background: #eef2f7; text-align: left; font-weight: 600;
  padding: 5pt 7pt; border-bottom: 1pt solid #b9c4d2; color: #1b3a6b;
}}
td {{ padding: 4.5pt 7pt; border-bottom: 0.5pt solid #dde3ea; vertical-align: top; }}
tr:last-child td {{ border-bottom: 0.8pt solid #b9c4d2; }}

ul, ol {{ margin: 0 0 8pt; padding-left: 16pt; }}
li {{ margin-bottom: 3pt; }}

blockquote {{
  margin: 10pt 0; padding: 8pt 12pt;
  border-left: 2.5pt solid #1b3a6b; background: #f5f8fc;
  font-size: 10.2pt; break-inside: avoid;
}}
blockquote p:last-child {{ margin-bottom: 0; }}

code {{
  font-family: "SF Mono", Menlo, monospace; font-size: 8.6pt;
  background: #eef1f5; padding: 0.7pt 3pt; border-radius: 2pt; color: #294066;
}}

hr {{ border: none; border-top: 0.5pt solid #e3e8ee; margin: 13pt 0; }}
a {{ color: #1b3a6b; text-decoration: none; }}

/* Tittelblokk */
.tittelside h1 {{ font-size: 21pt; border: none; padding: 0; margin-bottom: 3pt; }}
.tittelside h2 {{ font-size: 12.5pt; color: #5a6472; margin: 0 0 20pt; font-weight: 500; }}
.tittelside p {{ font-size: 10pt; color: #2c3644; }}
</style></head><body>
{innhold}
</body></html>
"""


def bygg(md: Path):
    html_sti = md.with_suffix('.html')
    pdf_sti = md.with_suffix('.pdf')

    frag = subprocess.run(
        ['pandoc', str(md), '-f', 'markdown+pipe_tables', '-t', 'html5'],
        check=True, capture_output=True, text=True).stdout

    # Alt før første <hr /> er tittelblokken
    if '<hr />' in frag:
        topp, resten = frag.split('<hr />', 1)
        frag = f'<div class="tittelside">{topp}</div><hr />{resten}'

    html_sti.write_text(MAL.format(tittel=md.stem, innhold=frag), encoding='utf-8')

    subprocess.run([
        CHROME, '--headless', '--disable-gpu', '--no-pdf-header-footer',
        '--run-all-compositor-stages-before-draw', '--virtual-time-budget=20000',
        f'--print-to-pdf={pdf_sti}', f'file://{html_sti.resolve()}',
    ], check=True, capture_output=True)

    info = subprocess.run(['pdfinfo', str(pdf_sti)], capture_output=True, text=True)
    sider = next((l.split()[1] for l in info.stdout.splitlines()
                  if l.startswith('Pages:')), '?')
    fonter = subprocess.run(['pdffonts', str(pdf_sti)], capture_output=True, text=True)
    advarsel = '  ADVARSEL: Type 3-font!' if 'Type 3' in fonter.stdout else ''
    print(f'{pdf_sti.name} — {sider} sider{advarsel}')


def main():
    filer = [Path(a) for a in sys.argv[1:]] or [
        HER / 'TILBUD.md', HER / 'VEDLEGG_E_SPORSMAL.md']
    for f in filer:
        bygg(f if f.is_absolute() else HER / f)


if __name__ == '__main__':
    main()
