"""PDF fra HTML med headless Chrome."""

import shutil
import subprocess
from pathlib import Path

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'


def lag_pdf(html_sti: Path, pdf_sti: Path):
    if not Path(CHROME).exists():
        raise SystemExit(f'Fant ikke Chrome på {CHROME}')
    subprocess.run([
        CHROME, '--headless', '--disable-gpu', '--no-pdf-header-footer',
        '--run-all-compositor-stages-before-draw', '--virtual-time-budget=10000',
        f'--print-to-pdf={pdf_sti}', f'file://{html_sti.resolve()}',
    ], check=True, capture_output=True)
    sider = ''
    if shutil.which('pdfinfo'):
        ut = subprocess.run(['pdfinfo', str(pdf_sti)], capture_output=True, text=True)
        for linje in ut.stdout.splitlines():
            if linje.startswith('Pages:'):
                sider = f' — {linje.split()[1]} sider'
    print(f'{pdf_sti.name}{sider}')
