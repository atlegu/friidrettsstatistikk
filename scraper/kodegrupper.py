"""Øvelseskoder som kan bære samme resultat. Brukes av importene for å stoppe kryss-kode-dubletter.

Basen har noen øvelser under to koder. Januarimporten 2026 (complete_scraper.py) laget kodene av
kildens øvelsesnavn («Lengde (Sone 0,5m)» -> lengde_sone_05m, «Kappgang 1000 meter» ->
kappgang_1000_m), mens senere importer oversatte navnene med egne tabeller ('Lengde (Sone 0,5m)'
-> lengde, 'Kappgang 1000 meter' -> 1000mg). Dublettsjekkene så bare innen én kode, så når et
stevne som alt lå inne ble hentet på nytt, kom resultatet inn en gang til under den andre koden:
48 085 sonehopp under brettkoden samme dag og 8 846 i flerdagsstevner, og dessuten sleggekast,
kappgang og 3000 m hinder (OPERATIONS_LOG 2026-10-30, migrations/kryssdubletter.sql).

Regelen importene følger: finnes samme utøver med samme resultat og vind under en beslektet kode
samme dag, er det samme resultat, og raden legges ikke inn på nytt - med mindre kilden selv lister
resultatet under begge kodene.
"""

import re

# Par av koder der samme resultat kan ligge under begge. Sonehopp er egne øvelser i kilden, og
# sonekoden er riktig. For resten er det samme øvelse under to koder, og det er ikke avgjort
# hvilken som skal gjelde.
KODEGRUPPER = [
    ('lengde', 'lengde_sone_05m'),
    ('tresteg', 'tresteg_sone_05m'),
    ('1000mg', 'kappgang_1000_m'),
    ('1500mg', 'kappgang_1500_m'),
    ('2000mg', 'kappgang_2000_m'),
    ('3000mg', 'kappgang_3000_m'),
    ('80mh_84cm', '80_m_h_840cm/85m'),
    ('slegge_2kg', 'slegge_20kg/110cm'),
    ('3000mhinder', '3000mhinder_91_4cm'),
    ('3000mhinder', '3000mhinder_76_2cm'),
    ('1mile', '1_mile'),
    ('300mh_91_4cm', '300_m_h_914cm-8hk'),
    ('30mh_84cm', '30_m_h_840cm'),
]

_MANGEKAMP = re.compile(r'^(\d+)_k(?:_|$)')


def beslektede_koder(koder):
    """{kode: {beslektede koder}} for kodene som finnes i basen.

    I tillegg til KODEGRUPPER: mangekamp med samme antall øvelser («7_k» og
    «7_k_100mh-høyde-...»). get_event_id() i update_results.py faller tilbake til den
    generelle koden når klassen ikke finnes, mens andre importer brukte den fulle.
    """
    koder = set(koder)
    ut = {k: set() for k in koder}
    for a, b in KODEGRUPPER:
        if a in koder and b in koder:
            ut[a].add(b)
            ut[b].add(a)
    mangekamp = {}
    for k in koder:
        m = _MANGEKAMP.match(k)
        if m:
            mangekamp.setdefault(m.group(1), set()).add(k)
    for gruppe in mangekamp.values():
        for k in gruppe:
            ut[k] |= gruppe - {k}
    return {k: v for k, v in ut.items() if v}


def resultatnoekkel(performance):
    """Samme resultat skrevet ulikt («4.1» / «4.10»): sammenlign som tall der det går."""
    try:
        return round(float(str(performance).replace(',', '.')), 3)
    except (TypeError, ValueError):
        return str(performance).strip()


def vindnoekkel(wind):
    """Ingen vind = ingen vind; ellers én desimal."""
    if wind is None or wind == '':
        return None
    try:
        return round(float(wind), 1)
    except (TypeError, ValueError):
        return None
