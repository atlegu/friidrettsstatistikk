"""Adapter for klubber som vil ha en bestemt gruppe utøvere øverst.

Rekkefølgen i navnelisten beholdes nøyaktig slik den er gitt — den er som
regel meningsbærende (prioritet, treningsgruppe, satsingsnivå), og skal ikke
sorteres om. Utøvere som ikke står på listen kommer etter, yngste først.

    import klubbrapport
    PRIORITERT = klubbrapport.Prioritert(['Navn Navnesen', ...],
                                         tittel='Satsingsgruppe')
    klubbrapport.kjor(KONFIG, PRIORITERT)
"""

from html import escape

from . import navn as _navn


class Prioritert:
    def __init__(self, navneliste, tittel='Prioriterte utøvere',
                 merke_tekst=None):
        self.navneliste = list(navneliste)
        self.tittel = tittel
        self.merke_tekst = merke_tekst
        # Rekkefølgen lagres slik at seksjonen kan bygges i riktig orden
        self._plass = {n: i for i, n in enumerate(self.navneliste)}
        self.FLAT = {n: {'plass': i} for i, n in enumerate(self.navneliste)}

    def finn(self, db_navn):
        return _navn.finn(db_navn, self.FLAT)

    def merke(self, info):
        return (f' <span class="stipend">{escape(self.merke_tekst)}</span>'
                if self.merke_tekst else '')

    def detalj(self, info):
        return ''

    def seksjoner(self, stip, alle, yngst_forst):
        prioritert = sorted(stip, key=lambda a: stip[a]['plass'])
        ovrige = yngst_forst([a for a in alle if a not in stip])
        return [
            (f'{self.tittel} ', f'{len(prioritert)} · oppgitt rekkefølge', prioritert),
            ('Øvrige utøvere ', f'{len(ovrige)} · yngste først', ovrige),
        ]

    def ikke_funnet_linje(self, navn, info):
        return escape(navn)

    def sammendrag(self, stip):
        if len(stip) == len(self.FLAT):
            return f'Alle {len(self.FLAT)} navn på prioritetslisten er funnet.'
        return (f'{len(stip)} av {len(self.FLAT)} navn på prioritetslisten '
                f'er funnet blant utøverne.')

    def csv_kolonner(self):
        return ['Prioritet']

    def csv_verdier(self, info):
        return [info['plass'] + 1] if info else ['']
