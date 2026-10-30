"""Fjern kopier av sonehopp som ligger under brettkoden (kryss-kode-dubletter).

BAKGRUNN
--------
Brettrader i lengde og tresteg er kopier av et sonehopp i lengde_sone_05m/tresteg_sone_05m:
samme utøver, resultatverdi og vind. Sonerakene kom inn i januar 2026 fra kildens utøversider.
Senere importer la det samme hoppet inn under brettkoden, fordi de oversatte «Lengde (Sone 0,5m)»
til lengde: update_results.py 13.-14.02 og 24.08-06.09.2026, import_youth_stats.py 19.05.2026,
og alle tiders-importen 14.02.2026 (117 rader). Dublettsjekkene, og ryddingen 03.10.2026,
sammenlignet bare innen samme øvelseskode. Kilden viser hoppene bare under sonen. Nesten alle
gjelder 11-13-åringer, i alle år 2011-2025. Funnet i dataauditen av A1/A3/A6 30.10.2026.

Roten er rettet i importene (kodegrupper.py, update_results.py, import_youth_stats.py,
import_historical.py). test_fullstendighet.py --bare kryssdubletter er kontrollen.

REGLER (rydd_kryssdubletter i basen, migrations/kryssdubletter.sql)
------
  Sonen beholdes, brettraden slettes, når sonen har samme utøver, resultatverdi og vind (ingen
  vind = ingen vind) og ble lagt inn før brettraden, og
    samme_dato      sonen har samme dato. Stevneposten teller ikke med: 8 % ligger i en annen
                    post. Dette er regelen i forskning/rens_felles.py.
    flerdagsstevne  brettraden har startdatoen til sin post, og sonen ligger 1-6 dager senere i
                    en søskenpost (samme navn uten sted foran, eller samme sted). Augustimporten
                    ga alle resultater i et flerdagsstevne startdatoen; sonehoppet ligger i
                    dagsposten med riktig dato. Ikke med i forskningsregelen.
  Plass kopieres til sonen der den mangler og radene ligger i samme post. Slettede rader lagres
  i opprydding_kryssdubletter (med beholdt_id, kodepar og regel) og kan legges tilbake.
  Stevneposter som blir tomme lagres i opprydding_kryssposter og slettes; har de kildens
  stevne-id, får posten med sonehoppene et alias i stevne_alias.

  Andre kodepar med samme mønster (1000mg/kappgang_1000_m, slegge_2kg/slegge_20kg/110cm,
  80mh_84cm/80_m_h_840cm/85m m.fl.) er samme øvelse under to koder. Der må det først avgjøres
  hvilken kode som gjelder; de røres ikke her, men tallene står i rapporten med --kartlegg.

KJØRING
-------
    python rydd_kryssdubletter.py                       # tørrkjøring (standard), begge reglene
    python rydd_kryssdubletter.py --kartlegg            # også alle andre kodepar med like resultater
    python rydd_kryssdubletter.py --apply --regel samme_dato   # slett - bare etter Atles ja
Alt logges til logs/, og tallene skrives til opprydding/kryssdubletter_<tid>.csv.
"""

import argparse
import csv
import logging
import os
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

load_dotenv(Path(__file__).parent / '.env')
sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])

TS = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
LOGG = Path(__file__).parent / 'logs'; LOGG.mkdir(exist_ok=True)
UT = Path(__file__).parent / 'opprydding'; UT.mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout),
                              logging.FileHandler(LOGG / f'rydd_kryssdubletter_{TS}.log', encoding='utf-8')])
logging.getLogger('httpx').setLevel(logging.WARNING)
log = logging.getLogger(__name__)

# (kopien, koden som beholdes)
PAR = [('lengde', 'lengde_sone_05m'), ('tresteg', 'tresteg_sone_05m')]
REGLER = ('samme_dato', 'flerdagsstevne')
FELT = ('par', 'samme_post', 'alder_11_13', 'uten_fodselsaar', 'fra_annen_kilde',
        'beholdt_med_flere_kopier', 'slettet', 'plass_kopiert', 'plass_feilet')


def aarspenn(kode):
    """Første og siste år med resultater i øvelsen."""
    eid = sb.table('events').select('id').eq('code', kode).single().execute().data['id']
    q = lambda desc: (sb.table('results').select('date').eq('event_id', eid)
                        .order('date', desc=desc).limit(1).execute().data)
    foerst, sist = q(False), q(True)
    if not foerst:
        return None
    return int(foerst[0]['date'][:4]), int(sist[0]['date'][:4])


def kjoer_periode(kopi, beholdt, regel, fra, til, dry, sum_, poster):
    """Én periode; deles i to om basen bruker for lang tid (gatewayen kutter etter 120 s)."""
    try:
        res = sb.rpc('rydd_kryssdubletter', {'p_kopi': kopi, 'p_beholdt': beholdt, 'p_fra': fra.isoformat(),
                                             'p_til': til.isoformat(), 'p_regel': regel,
                                             'p_dry': dry}).execute().data
    except Exception as e:  # noqa: BLE001
        if til - fra <= timedelta(days=7):
            log.error('  %s %s %s - %s feilet: %s', kopi, regel, fra, til, str(e)[:200])
            sum_['feilede_perioder'] = sum_.get('feilede_perioder', 0) + 1
            return
        mid = fra + (til - fra) / 2
        log.info('  %s %s %s - %s for tungt (%s), deles i to', kopi, regel, fra, til, str(e)[:80])
        kjoer_periode(kopi, beholdt, regel, fra, mid, dry, sum_, poster)
        kjoer_periode(kopi, beholdt, regel, mid + timedelta(days=1), til, dry, sum_, poster)
        return
    for f in FELT:
        sum_[f] = sum_.get(f, 0) + int(res.get(f, 0))
    for post, n, i_alt in res.get('poster', []):
        poster[post][0] += n
        poster[post][1] = i_alt


def tomme_poster_torr(poster):
    """Poster der alle radene er kopier, når alle kodepar og regler er talt sammen."""
    tomme = [p for p, (n, i_alt) in poster.items() if n >= i_alt]
    med_id = 0
    for i in range(0, len(tomme), 100):
        rader = sb.table('meets').select('id,external_id').in_('id', tomme[i:i + 100]).execute().data
        med_id += sum(1 for r in rader if r.get('external_id'))
    return {'tomme': len(tomme), 'med_kilde_id': med_id}


def kartlegg(fra_aar, til_aar):
    """Alle kodepar (samme resultattype) med like resultater, per år. Til rapporten."""
    per_par = defaultdict(lambda: defaultdict(int))
    nyest_a = defaultdict(int)
    for aar in range(fra_aar, til_aar + 1):
        try:
            rader = sb.rpc('kartlegg_kryssdubletter', {'p_fra': f'{aar}-01-01', 'p_til': f'{aar}-12-31'}).execute().data
        except Exception as e:  # noqa: BLE001
            log.error('  kartlegging %d feilet: %s', aar, str(e)[:200])
            continue
        for r in rader:
            per_par[(r['kode_a'], r['kode_b'])][aar] += r['antall']
            nyest_a[(r['kode_a'], r['kode_b'])] += r['a_nyest']
    fil = UT / f'kryssdubletter_kart_{TS}.csv'
    with open(fil, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['kode_a', 'kode_b', 'aar', 'antall'])
        for (a, b), aarene in sorted(per_par.items()):
            for aar, n in sorted(aarene.items()):
                w.writerow([a, b, aar, n])
    log.info('ALLE KODEPAR MED LIKE RESULTATER (minst 10 rader; samme utøver, dato, verdi og vind):')
    log.info('  %-44s %-44s %7s  %s', 'kode a', 'kode b', 'rader', 'nyest under a')
    for (a, b), aarene in sorted(per_par.items(), key=lambda x: -sum(x[1].values())):
        n = sum(aarene.values())
        if n >= 10:
            log.info('  %-44s %-44s %7d  %d', a, b, n, nyest_a[(a, b)])
    log.info('  (par med få rader er som regel tilfeldig like verdier, f.eks. diskos 1 kg og spyd 500 g)')
    log.info('Kartleggingen er skrevet til %s', fil)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--apply', action='store_true', help='slett (bare etter Atles ja)')
    ap.add_argument('--dry-run', action='store_true', help='bare tall (standard)')
    ap.add_argument('--regel', nargs='+', choices=REGLER, default=list(REGLER),
                    help='hvilke regler (standard: begge)')
    ap.add_argument('--kartlegg', action='store_true', help='kartlegg også alle andre kodepar med like resultater')
    args = ap.parse_args()
    if args.apply and args.dry_run:
        ap.error('--apply og --dry-run samtidig')
    dry = not args.apply
    log.info('Sonehopp under brettkoden - %s - regler: %s', 'TØRRKJØRING' if dry else 'SLETTER',
             ', '.join(args.regel))

    tabell = []
    totalt = defaultdict(dict)
    poster = defaultdict(lambda: [0, 0])     # post -> [kopier, rader i alt]
    # samme_dato først: flerdagsregelen tar bare brettrader uten sonetvilling samme dag
    for regel in [r for r in REGLER if r in args.regel]:
        for kopi, beholdt in PAR:
            spenn = aarspenn(beholdt)
            if not spenn:
                continue
            sum_par = {}
            for aar in range(spenn[0] - 1, spenn[1] + 1):
                sum_ = {}
                kjoer_periode(kopi, beholdt, regel, date(aar, 1, 1), date(aar, 12, 31), dry, sum_, poster)
                if sum_.get('par') or sum_.get('feilede_perioder'):
                    tabell.append({'regel': regel, 'kodepar': f'{kopi} > {beholdt}', 'aar': aar, **sum_})
                    log.info('  %-15s %-28s %d  %s', regel, f'{kopi} > {beholdt}', aar,
                             {k: v for k, v in sum_.items() if v})
                for k, v in sum_.items():
                    sum_par[k] = sum_par.get(k, 0) + v
            log.info('%s, %s > %s: %s', regel, kopi, beholdt, sum_par)
            for k, v in sum_par.items():
                totalt[regel][k] = totalt[regel].get(k, 0) + v

    fil = UT / f'kryssdubletter_{TS}.csv'
    with open(fil, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['regel', 'kodepar', 'aar', *FELT, 'feilede_perioder'], restval=0)
        w.writeheader()
        w.writerows(tabell)
    log.info('Tallene per regel, kodepar og år er skrevet til %s', fil)
    for regel, t in totalt.items():
        log.info('TOTALT %s: %s', regel, t)

    if dry:
        log.info('Stevneposter som blir tomme: %s', tomme_poster_torr(poster))
    else:
        log.info('Stevneposter som ble tomme: %s', sb.rpc('rydd_tomme_kryssposter', {'p_dry': False}).execute().data)

    if args.kartlegg:
        # fast startår: basen har stevnedatoer fra år 573 (kjent feil), så min(date) duger ikke
        kartlegg(1950, date.today().year)

    if dry:
        log.info('Tørrkjøring. Ingenting er endret. Kjør med --apply for å slette (etter Atles ja).')
        return

    log.info('Oppdaterer forsidetallene …')
    try:
        sb.rpc('refresh_plattform_statistikk').execute()
    except Exception as e:  # noqa: BLE001
        log.warning('  refresh_plattform_statistikk: %s', e)


if __name__ == '__main__':
    main()
