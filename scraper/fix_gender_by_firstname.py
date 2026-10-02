#!/usr/bin/env python3
"""Sett kjønn via fornavnsklassifisering + fiks enstemmige bevis-motsigelser.

Bakgrunn: Stevnesidene på kilden viser ikke 10-12-årsklassene
(barneidrettsbestemmelsene), så ~29k utøvere (nesten alle 10-12 år) kan ikke
få kjønn fra klassebevis. Fornavn er i stedet den godkjente metoden
(jf. CLAUDE.md og FIX_GENDER_README.md).

Treningsdata for fornavn → kjønn:
1. Bevisradene fra fix_gender_from_source.py (klassebasert, autoritativt)
2. Utøvere i databasen med kjent kjønn

Klassifisering (konservativ):
- >= 5 observasjoner og >= 98 % samme kjønn, ELLER
- >= 3 observasjoner og 100 % samme kjønn
Alt annet forblir NULL og rapporteres.

Validering: leave-one-out mot alle utøvere med kjent kjønn — rapporterer
treffprosent før noe endres.

I tillegg (--contradictions-report): retter utøvere der databasens kjønn
motsier ENSTEMMIG klassebevis med >= 5 observasjoner (rest-korrupsjon fra
batch-scriptet i januar 2026).

Bruk:
    python fix_gender_by_firstname.py --dry-run
    python fix_gender_by_firstname.py --contradictions-report logs/fix_gender_report_20260704_004330_contradictions.json
"""

import argparse
import gzip
import json
import logging
import os
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from supabase import Client, create_client

SCRIPT_DIR = Path(__file__).resolve().parent
load_dotenv(SCRIPT_DIR / '.env')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_DIR = SCRIPT_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('httpx').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(LOG_DIR / f'fix_gender_by_firstname_{timestamp}.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)


def get_gender_from_class(class_str):
    c = (class_str or '').lower().strip()
    if c.startswith('mikset'):
        return None
    if c.startswith(('menn', 'gutter', 'ms', 'g-')):
        return 'M'
    if c.startswith(('kvinner', 'jenter', 'ks', 'k-')):
        return 'F'
    return None


def first_name(full_name):
    tokens = (full_name or '').split()
    if not tokens or len(tokens[0]) < 2:
        return None
    return tokens[0].lower()


def load_paginated(table, columns, filters=None, page_size=1000):
    rows, offset = [], 0
    while True:
        q = supabase.table(table).select(columns)
        if filters:
            q = filters(q)
        resp = q.range(offset, offset + page_size - 1).execute()
        rows.extend(resp.data)
        if len(resp.data) < page_size:
            break
        offset += page_size
    return rows


def classify(counts):
    """Returner (gender|None, grunn) fra en Counter{M,F}."""
    m, f = counts.get('M', 0), counts.get('F', 0)
    total = m + f
    if total == 0:
        return None, 'ukjent navn'
    gender, n = ('M', m) if m >= f else ('F', f)
    ratio = n / total
    if total >= 5 and ratio >= 0.98:
        return gender, f'{n}/{total}'
    if total >= 3 and ratio == 1.0:
        return gender, f'{n}/{total} (lav n)'
    return None, f'usikker (M={m}, F={f})'


def update_gender_batch(ids, gender, dry_run):
    if dry_run or not ids:
        return
    for i in range(0, len(ids), 200):
        supabase.table('athletes').update({'gender': gender}).in_('id', ids[i:i + 200]).execute()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--contradictions-report', help='JSON-rapport fra fix_gender_from_source.py')
    args = parser.parse_args()

    if args.dry_run:
        logger.info("=== DRY RUN — ingen databaseendringer ===")

    # --- Treningsdata 1: klassebevis fra scraping ---
    name_stats = defaultdict(Counter)
    n_ev = 0
    for f in sorted((SCRIPT_DIR / 'new_meets_data').glob('gender_evidence_*.jsonl.gz')):
        try:
            with gzip.open(f, 'rt', encoding='utf-8') as fh:
                for line in fh:
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    g = get_gender_from_class(rec['class'])
                    fn = first_name(rec['name'])
                    if g and fn:
                        name_stats[fn][g] += 1
                        n_ev += 1
        except (EOFError, gzip.BadGzipFile):
            logger.warning(f"Trunkert bevisfil hoppet over resten: {f.name}")
    logger.info(f"Klassebevis: {n_ev} rader, {len(name_stats)} unike fornavn")

    # --- Treningsdata 2 + validering: utøvere med kjent kjønn ---
    logger.info("Laster utøvere ...")
    athletes = load_paginated('athletes', 'id, full_name, birth_year, gender')
    known = [a for a in athletes if a['gender'] in ('M', 'F')]
    nulls = [a for a in athletes if a['gender'] is None]
    logger.info(f"{len(known)} med kjønn, {len(nulls)} uten")

    db_contrib = []
    for a in known:
        fn = first_name(a['full_name'])
        if fn:
            name_stats[fn][a['gender']] += 1
            db_contrib.append((a, fn))

    # --- Leave-one-out-validering mot kjente utøvere ---
    agree = disagree = abstain = 0
    disagreements = []
    for a, fn in db_contrib:
        counts = name_stats[fn].copy()
        counts[a['gender']] -= 1  # fjern egen observasjon
        pred, _ = classify(counts)
        if pred is None:
            abstain += 1
        elif pred == a['gender']:
            agree += 1
        else:
            disagree += 1
            if len(disagreements) < 200:
                disagreements.append({'name': a['full_name'], 'birth_year': a['birth_year'],
                                      'db_gender': a['gender'], 'predicted': pred})
    total_pred = agree + disagree
    logger.info(f"VALIDERING (leave-one-out): {agree}/{total_pred} riktig "
                f"({100 * agree / max(total_pred, 1):.2f} %), {abstain} avstår")

    # --- Klassifiser NULL-utøvere ---
    set_m, set_f = [], []
    unresolved = []
    per_reason = Counter()
    for a in nulls:
        fn = first_name(a['full_name'])
        if not fn:
            unresolved.append({'name': a['full_name'], 'birth_year': a['birth_year'], 'reason': 'mangler fornavn'})
            per_reason['mangler fornavn'] += 1
            continue
        pred, reason = classify(name_stats[fn])
        if pred == 'M':
            set_m.append(a['id'])
        elif pred == 'F':
            set_f.append(a['id'])
        else:
            unresolved.append({'id': a['id'], 'name': a['full_name'], 'birth_year': a['birth_year'],
                               'first_name': fn, 'reason': reason,
                               'M': name_stats[fn].get('M', 0), 'F': name_stats[fn].get('F', 0)})
            per_reason[reason.split(' (')[0].split(',')[0]] += 1

    logger.info("=" * 60)
    logger.info(f"Fornavnsklassifisering: setter M: {len(set_m)}  |  F: {len(set_f)}")
    logger.info(f"Uavklart: {len(unresolved)}")

    # --- Motsigelsesfiks fra klassebevis (rest-korrupsjon) ---
    fix_to_m, fix_to_f = [], []
    if args.contradictions_report:
        contradictions = json.loads(Path(args.contradictions_report).read_text())
        for c in contradictions:
            m, f = c['evidence_M'], c['evidence_F']
            if m + f >= 5 and (m == 0 or f == 0):
                (fix_to_m if m > 0 else fix_to_f).append(c['id'])
        logger.info(f"Motsigelsesfiks (enstemmig klassebevis >=5): {len(fix_to_m)} -> M, {len(fix_to_f)} -> F "
                    f"av {len(contradictions)} rapporterte")

    report = {
        'validation': {'agree': agree, 'disagree': disagree, 'abstain': abstain,
                       'accuracy_pct': round(100 * agree / max(total_pred, 1), 2),
                       'disagreements_sample': disagreements[:100]},
        'set_m': len(set_m), 'set_f': len(set_f),
        'contradiction_fix_m': len(fix_to_m), 'contradiction_fix_f': len(fix_to_f),
        'unresolved': unresolved,
    }
    report_path = LOG_DIR / f'fix_gender_by_firstname_report_{timestamp}.json'
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=1))
    logger.info(f"Rapport: {report_path}")

    update_gender_batch(set_m, 'M', args.dry_run)
    update_gender_batch(set_f, 'F', args.dry_run)
    update_gender_batch(fix_to_m, 'M', args.dry_run)
    update_gender_batch(fix_to_f, 'F', args.dry_run)
    logger.info("DRY RUN fullført — ingenting endret" if args.dry_run else "Databaseoppdatering fullført")


if __name__ == '__main__':
    main()
