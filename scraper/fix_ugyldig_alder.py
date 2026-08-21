"""
Rett resultater der utøverens alder på konkurransetidspunktet er umulig.

BAKGRUNN
--------
333 resultater gir en alder under 5 eller over 100 år når man regner
konkurranseår minus fødselsår. Diagnosen 2026-08-21 viste to ulike årsaker:

  1. FEIL ÅRHUNDRE I STEVNEDATO. Fire stevner i januar 2026 er lagret med
     årstall 1926. Alle utøverne på disse stevnene har resultater på nøyaktig
     samme dato i 2026, så det er ingen tvil.

  2. UGYLDIGE FØDSELSÅR. Verdier som 0, 752, 1006, 1070, 2097, 2995, 9171 og
     9194 — tall fra en annen kolonne som har havnet i birth_year.

MERK: utøvere født på 1860–1880-tallet er ekte. En fast nedre grense på
årstall flagger dem feilaktig. Derfor testes fødselsåret mot utøverens EGNE
resultater — er alderen mellom 5 og 100 år, godtas den.

BRUK
----
    python fix_ugyldig_alder.py                # dry-run (standard)
    python fix_ugyldig_alder.py --apply
    python fix_ugyldig_alder.py --apply --yes
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SCRIPT_NAME = Path(__file__).stem
TIMESTAMP = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
LOG_DIR = Path(__file__).parent / 'logs'
BACKUP_DIR = Path(__file__).parent / 'backups'
LOG_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout),
              logging.FileHandler(LOG_DIR / f'{SCRIPT_NAME}_{TIMESTAMP}.log',
                                  encoding='utf-8')])
logger = logging.getLogger(__name__)

# Stevner med feil århundre. Bekreftet: samtlige utøvere har resultater på
# samme dag i 2026, og det finnes ingen 2026-utgave å kollidere med.
MEET_FIX = {
    '2f6040b4-8bfe-4ca7-a62f-e8f773333011': ('Distriktskampen', '1926-01-10', '2026-01-10'),
    '35f5c810-ed6a-4b41-9673-d48b0e497aa3': ('Kengurukarusellen 1', '1926-01-08', '2026-01-08'),
    '1f2a792c-4f6a-48b5-9d9b-7913e399adf3': ('Nyttårsstevnet', '1926-01-11', '2026-01-11'),
    'b3b2687f-80e7-4ba4-a57b-9ab1bf53b6ac': ('Sprintstevne', '1926-01-06', '2026-01-06'),
}
SEASON_2026_INNE = '5e4a5ba5-f36a-49f4-880b-cf9a49b6b883'

# Kjent enkeltrettelse oppgitt av bruker.
KASPER_JUNK = '347f75f1-ca15-4aa2-a8e0-e1a2df382bcf'   # birth_year 0, 1 resultat
KASPER_EKTE = 'f2bb6f54-1046-48ba-8410-68345fa63ddc'   # birth_year 2003, 9 resultater
KASPER_DATE = '2003-01-20'

ALDER_MIN, ALDER_MAX = 5, 100

# Nedre grense for et ekte fødselsår. Utøvere født på 1860-tallet konkurrerte
# rundt århundreskiftet og finnes i basen — grensen må ikke settes høyere.
AAR_MIN, AAR_MAX = 1860, 2026


def er_odelagt(by) -> bool:
    """Er fødselsåret utvetydig ødelagt, eller bare i strid med resultatene?"""
    return by is not None and (by == 0 or by < AAR_MIN or by > AAR_MAX)


def likner_aar(odelagt: int, ekte: int) -> bool:
    """Er den ødelagte verdien en forvansket utgave av det ekte årstallet?

    Fanger 1070/1970, 1006/2006, 9194/1994 (ett tegn feil eller ombyttet) og
    752/1952 (sifre falt bort). Skal IKKE godta to ulike, plausible årstall.
    """
    a, b = str(odelagt), str(ekte)
    if len(a) < 4:                      # avkortet, f.eks. 752 av 1952
        return a in b or a[-2:] == b[-2:]
    if len(a) != len(b):
        return False
    ulike = sum(1 for x, y in zip(a, b) if x != y)
    if ulike <= 1:                      # ett siffer feil
        return True
    return sorted(a) == sorted(b)       # sifre ombyttet, f.eks. 9194/1994


def fetch_all(sb: Client, table: str, columns: str, chunk: int = 1000, retries: int = 4):
    """Hent alle rader med NØKKELBASERT paginering.

    Offset-paginering (`.range()`) uten sortering gir ikke stabil rekkefølge i
    PostgREST. Over 1,4 millioner resultatrader betyr det at rader både kan
    hoppes over og komme dobbelt. Det er ikke teoretisk: første versjon av dette
    skriptet mistet nettopp raden vi lette etter. Vi sorterer derfor på `id` og
    blar med `id > forrige`, som er både korrekt og raskt.

    `columns` må inkludere `id`.
    """
    rows, siste = [], '00000000-0000-0000-0000-000000000000'
    while True:
        for forsok in range(retries):
            try:
                res = (sb.table(table).select(columns)
                         .gt('id', siste).order('id').limit(chunk).execute())
                break
            except Exception as e:
                if forsok == retries - 1:
                    raise
                logger.warning('  nettverksfeil (%s), forsøker igjen …', type(e).__name__)
                time.sleep(2 * (forsok + 1))
        if not res.data:
            return rows
        rows.extend(res.data)
        siste = res.data[-1]['id']
        if len(rows) % 200000 < chunk:
            logger.info('  ... %d rader hentet fra %s', len(rows), table)
        if len(res.data) < chunk:
            return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--yes', action='store_true')
    args = ap.parse_args()

    sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])
    logger.info('=' * 72)
    logger.info('Rett umulig alder — modus: %s', 'APPLY' if args.apply else 'DRY-RUN')
    logger.info('=' * 72)

    # ---- Steg 1: stevner med feil århundre ----------------------------------
    logger.info('')
    logger.info('STEG 1 — stevner med feil århundre')
    meet_rows = {}
    for mid, (navn, gammel, ny) in MEET_FIX.items():
        res = sb.table('results').select('id,date').eq('meet_id', mid).execute().data
        meet_rows[mid] = res
        logger.info('  %-22s %s -> %s  (%d resultater)', navn, gammel, ny, len(res))

    # ---- Steg 2: fødselsår som ikke kan stemme ------------------------------
    logger.info('')
    logger.info('STEG 2 — fødselsår som ikke stemmer med egne resultater')

    athletes = {a['id']: a for a in fetch_all(sb, 'athletes', 'id,full_name,birth_year,birth_date')}

    # Årsspenn per utøver. Resultater på stevnene som rettes i steg 1 telles med
    # sitt KORRIGERTE årstall — ellers ville utøverne der bli flagget som om
    # fødselsåret var feil, når det i virkeligheten var stevnedatoen.
    aar = {}
    for r in fetch_all(sb, 'results', 'id,athlete_id,date,meet_id'):
        if not r['date']:
            continue
        y = 2026 if r['meet_id'] in MEET_FIX else int(r['date'][:4])
        lo, hi = aar.get(r['athlete_id'], (y, y))
        aar[r['athlete_id']] = (min(lo, y), max(hi, y))

    daarlige = []
    for aid, a in athletes.items():
        by = a['birth_year']
        if by is None or aid not in aar:
            continue
        lo, hi = aar[aid]
        if (lo - by) < ALDER_MIN or (hi - by) > ALDER_MAX:
            daarlige.append((aid, a, lo, hi))

    # Navnetvillinger med gyldig fødselsår
    by_name = {}
    for aid, a in athletes.items():
        by_name.setdefault((a['full_name'] or '').strip().lower(), []).append(aid)

    def gyldig(aid):
        a, by = athletes[aid], athletes[aid]['birth_year']
        if by is None or aid not in aar:
            return False
        lo, hi = aar[aid]
        return ALDER_MIN <= (lo - by) and (hi - by) <= ALDER_MAX

    plan_merge, plan_null, plan_fra_dato, til_gjennomgang = [], [], [], []
    for aid, a, lo, hi in daarlige:
        by = a['birth_year']

        # a) fødselsår kan utledes fra birth_date — alltid trygt
        if a['birth_date'] and str(a['birth_date'])[:4].isdigit():
            by2 = int(str(a['birth_date'])[:4])
            if ALDER_MIN <= (lo - by2) and (hi - by2) <= ALDER_MAX:
                plan_fra_dato.append((aid, a, by2))
                continue

        # Bare utvetydig ødelagte verdier røres automatisk. Et fødselsår som
        # SER plausibelt ut men strider mot resultatene, kan like gjerne bety at
        # et resultat er feil eller at to personer er slått sammen — det er en
        # vurdering, ikke en regel. De havner på gjennomgangslisten.
        if not er_odelagt(by):
            til_gjennomgang.append((aid, a, lo, hi))
            continue

        # b) navnetvilling med gyldig fødselsår som ligner på den ødelagte
        #    verdien -> samme person, to poster
        tvilling = [x for x in by_name.get((a['full_name'] or '').strip().lower(), [])
                    if x != aid and gyldig(x)
                    and (by == 0 or likner_aar(by, athletes[x]['birth_year']))]
        if len(tvilling) == 1:
            plan_merge.append((aid, a, tvilling[0]))
            continue

        # c) ellers: sett fødselsår til NULL. Ukjent er ærlig, 0 er en løgn.
        plan_null.append((aid, a, lo, hi))

    logger.info('  Fødselsår utledet fra birth_date: %d', len(plan_fra_dato))
    for aid, a, by2 in plan_fra_dato:
        logger.info('     %-28s %s -> %s', a['full_name'], a['birth_year'], by2)
    logger.info('  Dublett med gyldig tvilling (slås sammen): %d', len(plan_merge))
    for aid, a, t in plan_merge[:10]:
        logger.info('     %-28s (%s) -> %s', a['full_name'], a['birth_year'],
                    athletes[t]['birth_year'])
    logger.info('  Fødselsår settes til NULL (ukjent): %d', len(plan_null))
    logger.info('  Til manuell gjennomgang (røres ikke): %d', len(til_gjennomgang))

    # Gjennomgangslisten skrives som CSV — disse krever menneskelig vurdering.
    gj = BACKUP_DIR / f'{SCRIPT_NAME}_{TIMESTAMP}_til_gjennomgang.csv'
    with gj.open('w', encoding='utf-8-sig', newline='') as f:
        import csv as _csv
        w = _csv.writer(f, delimiter=';')
        w.writerow(['athlete_id', 'Navn', 'Fødselsår', 'Første resultatår',
                    'Siste resultatår', 'Alder ved første', 'Alder ved siste'])
        for aid, a, lo, hi in sorted(til_gjennomgang, key=lambda x: x[1]['full_name'] or ''):
            w.writerow([aid, a['full_name'], a['birth_year'], lo, hi,
                        lo - a['birth_year'], hi - a['birth_year']])
    logger.info('  Gjennomgangsliste: %s', gj.name)

    backup = BACKUP_DIR / f'{SCRIPT_NAME}_{TIMESTAMP}.json'
    backup.write_text(json.dumps({
        'generated_at': TIMESTAMP,
        'meet_fix': {k: v for k, v in MEET_FIX.items()},
        'meet_results': {k: [r['id'] for r in v] for k, v in meet_rows.items()},
        'fra_dato': [{'id': a, 'navn': x['full_name'], 'fra': x['birth_year'], 'til': b}
                     for a, x, b in plan_fra_dato],
        'merge': [{'junk': a, 'navn': x['full_name'], 'junk_by': x['birth_year'],
                   'target': t} for a, x, t in plan_merge],
        'null': [{'id': a, 'navn': x['full_name'], 'by': x['birth_year'],
                  'res_ar': [lo, hi]} for a, x, lo, hi in plan_null],
        'kasper': {'junk': KASPER_JUNK, 'target': KASPER_EKTE, 'birth_date': KASPER_DATE},
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    logger.info('')
    logger.info('Sikkerhetskopi: %s', backup)

    if not args.apply:
        logger.info('DRY-RUN — ingenting endret. Kjør med --apply.')
        return
    if not args.yes:
        print('\nDette endrer 4 stevnedatoer og retter fødselsår på '
              f'{len(plan_fra_dato) + len(plan_merge) + len(plan_null)} utøvere.')
        if input('Skriv "JA" for å fortsette: ').strip() != 'JA':
            logger.info('Avbrutt av bruker.')
            return

    # ---- Utfør steg 1 -------------------------------------------------------
    endret_res = 0
    for mid, (navn, gammel, ny) in MEET_FIX.items():
        sb.table('meets').update({'start_date': ny, 'end_date': ny}).eq('id', mid).execute()
        for r in meet_rows[mid]:
            nydato = ny if r['date'] == gammel else '2026' + str(r['date'])[4:]
            sb.table('results').update(
                {'date': nydato, 'season_id': SEASON_2026_INNE}).eq('id', r['id']).execute()
            endret_res += 1
    logger.info('Stevnedatoer rettet: %d, resultatdatoer rettet: %d',
                len(MEET_FIX), endret_res)

    # ---- Utfør steg 2 -------------------------------------------------------
    for aid, a, by2 in plan_fra_dato:
        sb.table('athletes').update({'birth_year': by2}).eq('id', aid).execute()

    for aid, a, target in plan_merge:
        sb.table('results').update({'athlete_id': target}).eq('athlete_id', aid).execute()
        sb.table('athletes').delete().eq('id', aid).execute()

    for aid, a, lo, hi in plan_null:
        sb.table('athletes').update({'birth_year': None}).eq('id', aid).execute()

    logger.info('Fødselsår fra birth_date: %d', len(plan_fra_dato))
    logger.info('Dubletter slått sammen:   %d', len(plan_merge))
    logger.info('Fødselsår satt til NULL:  %d', len(plan_null))

    # ---- Kasper Ellingsen ---------------------------------------------------
    if any(x[0] == KASPER_JUNK for x in plan_merge):
        sb.table('athletes').update(
            {'birth_date': KASPER_DATE, 'birth_year': 2003}).eq('id', KASPER_EKTE).execute()
        logger.info('Kasper Ellingsen: fødselsdato satt til %s på den beholdte posten',
                    KASPER_DATE)

    logger.info('Ferdig. Logg: %s', LOG_DIR / f'{SCRIPT_NAME}_{TIMESTAMP}.log')


if __name__ == '__main__':
    main()
