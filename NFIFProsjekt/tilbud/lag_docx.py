#!/usr/bin/env python3
"""Bygg redigerbare Word-dokumenter av tilbudet.

    ./lag_docx.py              alle
    ./lag_docx.py TILBUD.md    én fil

Markdown -> docx med pandoc. Overskrifter blir ekte Word-stiler (Overskrift 1,
2, 3), så navigasjonsruten og innholdsfortegnelsen virker, og teksten kan
redigeres med spor endringer.

Malen `mal.docx` styrer font, størrelse og språk. Den bygges av
`pandoc --print-default-data-file reference.docx` med tre endringer:
Calibri i stedet for temafont, 10,5 pt, og `nb-NO` som språk slik at Words
stavekontroll er norsk.

Pandoc skriver «Table of Contents» inn i docx uansett `toc-title`, så
tittelen byttes til «Innhold» etterpå.
"""

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

HER = Path(__file__).resolve().parent
MAL = HER / 'mal.docx'


def sett_toc_tittel(docx: Path, tittel: str = 'Innhold'):
    """Bytt pandocs engelske TOC-overskrift uten å røre resten av arkivet."""
    tmp = docx.with_suffix('.tmp.docx')
    with zipfile.ZipFile(docx) as inn, \
         zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as ut:
        for post in inn.infolist():
            data = inn.read(post.filename)
            if post.filename == 'word/document.xml':
                data = data.replace(b'Table of Contents', tittel.encode('utf-8'))
            ut.writestr(post, data)
    tmp.replace(docx)


def bygg(md: Path):
    docx = md.with_suffix('.docx')
    cmd = ['pandoc', str(md), '-f', 'markdown+pipe_tables', '-t', 'docx',
           '--metadata', 'lang=nb-NO', '-o', str(docx)]
    if MAL.exists():
        cmd[6:6] = ['--reference-doc', str(MAL)]
    if md.stem == 'TILBUD':
        cmd[6:6] = ['--toc', '--toc-depth=2']
    subprocess.run(cmd, check=True)
    sett_toc_tittel(docx)
    print(f'{docx.name} — {docx.stat().st_size // 1024} kB')


def main():
    if not MAL.exists():
        print(f'Advarsel: fant ikke {MAL.name}, bruker pandocs standardmal')
    filer = [Path(a) for a in sys.argv[1:]] or [
        HER / 'TILBUD.md', HER / 'VEDLEGG_E_SPORSMAL.md']
    for f in filer:
        bygg(f if f.is_absolute() else HER / f)


if __name__ == '__main__':
    main()
