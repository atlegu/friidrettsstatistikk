"""Felles maskineri for klubbrapportene.

En klubb trenger bare en `Konfig` og en stipendadapter — resten er felles.
Se `Tjalve/kjor.py` eller `vidar/kjor.py` for hvor lite som skal til.
"""

from .hent import Konfig, hent
from .rapport import bygg
from .pdf import lag_pdf
from . import uten_stipend
from .prioritert import Prioritert

__all__ = ['Konfig', 'hent', 'bygg', 'lag_pdf', 'kjor', 'uten_stipend', 'Prioritert']


def kjor(konfig, stipend, hent_data=True, pdf=True):
    """Hele kjeden: uttrekk fra basen, HTML og CSV, og til slutt PDF."""
    if hent_data:
        hent(konfig)
    html = bygg(konfig, stipend)
    if pdf:
        lag_pdf(html, konfig.mappe / f'{konfig.stamme}.pdf')
