#!/usr/bin/env python3
"""Sett kjønn autoritativt fra klasseoverskrifter på minfriidrettsstatistikk.info.

Strategi (se FIX_GENDER_README.md / OPERATIONS_LOG.md):
- Stevnesidene (StevneResultater.php) har klasseoverskrift per øvelse
  ("Gutter 15", "Kvinner Senior", ...). Klassen gir kjønn.
- Vi henter kun stevner som inneholder resultater fra utøvere med gender=NULL
  (hjelpetabell gender_fix_target_meets, opprettet 2026-07-03).
- Bevis aggregeres per (navn, fødselsår) på tvers av alle stevner. Kjønn settes
  KUN der bevisene er konsistente. Konflikter flagges til manuell gjennomgang.
- Utøvere som allerede har kjønn oppdateres ALDRI automatisk — motstridende
  bevis rapporteres kun.
- Rå bevis lagres som gzip-JSONL slik at aldersklasse-backfill kan gjøres
  senere uten ny scraping.

Bruk:
    python fix_gender_from_source.py --seasons 2025 --dry-run
    python fix_gender_from_source.py --seasons 2013-2026
    python fix_gender_from_source.py --seasons 2025 --limit 50 --dry-run
"""

import argparse
import gzip
import json
import logging
import os
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import Client, create_client

SCRIPT_DIR = Path(__file__).resolve().parent
load_dotenv(SCRIPT_DIR / '.env')

BASE_URL = "https://www.minfriidrettsstatistikk.info/php"
REQUEST_DELAY = 0.6

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (friidrett.live datakvalitet)'})

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_DIR = SCRIPT_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(LOG_DIR / f'fix_gender_from_source_{timestamp}.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)


# ------------------------------------------------------------
# Kilde-hjelpere
# ------------------------------------------------------------

def fetch_page(url, method='GET', data=None, retries=3):
    for attempt in range(retries):
        time.sleep(REQUEST_DELAY)
        try:
            if method == 'POST':
                r = session.post(url, data=data, timeout=30)
            else:
                r = session.get(url, params=data, timeout=30)
            r.raise_for_status()
            r.encoding = 'utf-8'
            return r.text
        except requests.RequestException as e:
            logger.warning(f"Fetch attempt {attempt + 1}/{retries} failed for {url}: {e}")
            time.sleep(2 * (attempt + 1))
    return None


def normalize_meet_name(name):
    name = name.lower().strip()
    name = re.sub(r'[^\w\s]', '', name)
    return ' '.join(name.split())


def normalize_athlete_name(name):
    return ' '.join(name.split()).lower()


def parse_date(date_str):
    try:
        parts = date_str.strip().split('.')
        if len(parts) == 3:
            day, month, year = parts
            year = int(year)
            if year < 100:
                year = 2000 + year if year < 50 else 1900 + year
            return datetime(year, int(month), int(day))
    except Exception:
        pass
    return None


def get_gender_from_class(class_str):
    if not class_str:
        return None
    c = class_str.lower().strip()
    if c.startswith(('menn', 'gutter', 'ms', 'g-', 'mikset')):
        return None if c.startswith('mikset') else 'M'
    if c.startswith(('kvinner', 'jenter', 'ks', 'k-')):
        return 'F'
    return None


def fetch_meets_from_source(season, outdoor):
    """Hent stevneliste for en sesong. Returnerer liste av dicts."""
    html = fetch_page(f"{BASE_URL}/Stevner.php", data={'outdoor': outdoor, 'showseason': season})
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    meets = []
    for link in soup.find_all('a', href=re.compile(r'posttoresultlist')):
        m = re.search(r'posttoresultlist\((\d+)\)', link.get('href', ''))
        if not m:
            continue
        row = link.find_parent('tr')
        if not row:
            continue
        cells = row.find_all('td')
        if len(cells) < 4:
            continue
        meet_date = parse_date(cells[0].get_text(strip=True))
        if not meet_date:
            continue
        meets.append({
            'external_id': m.group(1),
            'name': link.get_text(strip=True),
            'date': meet_date.strftime('%Y-%m-%d'),
            'location': cells[3].get_text(strip=True) if len(cells) > 3 else '',
        })
    return meets


BIRTH_YEAR_RE = re.compile(r'\((\d{4})\)\s*$')


def parse_meet_results(html):
    """Parse stevneside. Returnerer liste av (event, class, name, birth_year)."""
    soup = BeautifulSoup(html, 'html.parser')
    rows_out = []
    current_class = None
    current_event = None
    for element in soup.find_all(['div', 'table']):
        if element.name == 'div' and element.get('id') == 'header2':
            h2 = element.find('h2')
            if h2:
                current_class = h2.get_text(strip=True)
        elif element.name == 'div' and element.get('id') == 'eventheader':
            h3 = element.find('h3')
            if h3:
                current_event = h3.get_text(strip=True)
        elif element.name == 'table' and current_class:
            for row in element.find_all('tr'):
                if row.find('th'):
                    continue
                cells = row.find_all('td')
                if len(cells) < 4:
                    continue
                name_text = cells[2].get_text(strip=True)
                if not name_text:
                    continue
                birth_year = None
                m = BIRTH_YEAR_RE.search(name_text)
                if m:
                    birth_year = int(m.group(1))
                    name_text = name_text[:m.start()].strip()
                # fjern lands-suffiks som "(NED)"
                name_text = re.sub(r'\([A-Z]{3}\)\s*$', '', name_text).strip()
                if not name_text:
                    continue
                rows_out.append((current_event, current_class, name_text, birth_year))
    return rows_out


# ------------------------------------------------------------
# Database-hjelpere
# ------------------------------------------------------------

def load_paginated(table, columns, page_size=1000):
    rows = []
    offset = 0
    while True:
        resp = supabase.table(table).select(columns).range(offset, offset + page_size - 1).execute()
        rows.extend(resp.data)
        if len(resp.data) < page_size:
            break
        offset += page_size
    return rows


def load_athletes():
    logger.info("Laster alle utøvere fra databasen ...")
    athletes = load_paginated('athletes', 'id, full_name, birth_year, gender')
    logger.info(f"Lastet {len(athletes)} utøvere")
    index = defaultdict(list)
    for a in athletes:
        if a['full_name']:
            index[(normalize_athlete_name(a['full_name']), a['birth_year'])].append(a)
    return athletes, index


def load_target_meets():
    logger.info("Laster målstevner (gender_fix_target_meets) ...")
    meets = load_paginated('gender_fix_target_meets', 'meet_id, name, start_date, indoor')
    logger.info(f"Lastet {len(meets)} målstevner")
    return meets


# ------------------------------------------------------------
# Hovedlogikk
# ------------------------------------------------------------

def build_meet_lookup(target_meets):
    """(normalisert navn, dato) -> meet. Indekserer også navn etter komma."""
    lookup = {}
    for m in target_meets:
        keys = {(normalize_meet_name(m['name']), m['start_date'])}
        if ',' in m['name']:
            short = m['name'].split(',', 1)[1].strip()
            keys.add((normalize_meet_name(short), m['start_date']))
        for k in keys:
            lookup.setdefault(k, m)
    return lookup


def match_source_meet(lookup, source_meet):
    """Match kildestevne mot målstevner: eksakt dato, så ±1 dag."""
    names = [source_meet['name']]
    if source_meet['location']:
        names.append(f"{source_meet['location']}, {source_meet['name']}")
    base_date = datetime.strptime(source_meet['date'], '%Y-%m-%d')
    for delta in (0, 1, -1):
        d = (base_date + timedelta(days=delta)).strftime('%Y-%m-%d')
        for n in names:
            hit = lookup.get((normalize_meet_name(n), d))
            if hit:
                return hit
    return None


def decide_gender(counts):
    """Bestem kjønn fra bevis-Counter. Returnerer (gender|None, grunn)."""
    m, f = counts.get('M', 0), counts.get('F', 0)
    total = m + f
    if total == 0:
        return None, 'ingen bevis'
    if f == 0:
        return 'M', f'entydig ({m} M)'
    if m == 0:
        return 'F', f'entydig ({f} F)'
    majority, maj_n = ('M', m) if m > f else ('F', f)
    if total >= 5 and maj_n / total >= 0.9:
        return majority, f'flertall {maj_n}/{total}'
    return None, f'konflikt (M={m}, F={f})'


def update_gender_batch(athlete_ids, gender, dry_run):
    if dry_run or not athlete_ids:
        return
    for i in range(0, len(athlete_ids), 200):
        batch = athlete_ids[i:i + 200]
        supabase.table('athletes').update({'gender': gender}).in_('id', batch).execute()


def update_meet_external_ids(pairs, dry_run):
    """pairs: liste av (meet_id, external_id). Bruker RPC set_meet_external_ids
    (partial upsert er umulig pga NOT NULL-sjekk før konfliktløsning)."""
    if dry_run or not pairs:
        return
    rows = [{'id': mid, 'external_id': ext} for mid, ext in pairs]
    for i in range(0, len(rows), 2000):
        supabase.rpc('set_meet_external_ids', {'pairs': rows[i:i + 2000]}).execute()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seasons', required=True, help='F.eks. "2025" eller "2013-2026"')
    parser.add_argument('--dry-run', action='store_true', help='Ingen databaseendringer')
    parser.add_argument('--limit', type=int, help='Maks antall stevnesider å hente (pilot)')
    parser.add_argument('--evidence-file', help='Gjenbruk bevis fra tidligere kjøring (jsonl.gz) i stedet for å scrape')
    args = parser.parse_args()

    if '-' in args.seasons:
        lo, hi = args.seasons.split('-')
        seasons = list(range(int(lo), int(hi) + 1))
    else:
        seasons = [int(args.seasons)]

    if args.dry_run:
        logger.info("=== DRY RUN — ingen databaseendringer ===")

    athletes, athlete_index = load_athletes()
    null_athletes = [a for a in athletes if a['gender'] is None]
    logger.info(f"{len(null_athletes)} utøvere mangler kjønn")

    evidence = defaultdict(Counter)   # (norm_name, birth_year) -> Counter{M,F}
    class_inventory = Counter()
    unknown_classes = Counter()

    if args.evidence_file:
        logger.info(f"Leser bevis fra {args.evidence_file} (ingen scraping)")
        with gzip.open(args.evidence_file, 'rt', encoding='utf-8') as fh:
            for line in fh:
                rec = json.loads(line)
                g = get_gender_from_class(rec['class'])
                if g:
                    evidence[(normalize_athlete_name(rec['name']), rec['birth_year'])][g] += 1
    else:
        target_meets = load_target_meets()
        lookup = build_meet_lookup(target_meets)

        evidence_path = SCRIPT_DIR / 'new_meets_data' / f'gender_evidence_{timestamp}.jsonl.gz'
        done_path = SCRIPT_DIR / 'new_meets_data' / 'gender_evidence_done_meets.txt'
        done_ids = set()
        if done_path.exists():
            done_ids = set(done_path.read_text().split())
            logger.info(f"Resume: {len(done_ids)} stevner allerede hentet i tidligere kjøringer")

        # Les inn bevis fra tidligere (avbrutte/pilot-)kjøringer slik at
        # stevner i done-fila fortsatt teller med i beslutningene.
        for old_file in sorted((SCRIPT_DIR / 'new_meets_data').glob('gender_evidence_*.jsonl.gz')):
            if old_file == evidence_path:
                continue
            n_old = 0
            try:
                with gzip.open(old_file, 'rt', encoding='utf-8') as fh:
                    for line in fh:
                        try:
                            rec = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        g = get_gender_from_class(rec['class'])
                        if g:
                            evidence[(normalize_athlete_name(rec['name']), rec['birth_year'])][g] += 1
                            n_old += 1
            except (EOFError, gzip.BadGzipFile) as e:
                logger.warning(f"Trunkert bevisfil {old_file.name} (avbrutt kjøring): "
                               f"leste {n_old} rader før feilen ({e})")
            logger.info(f"Leste {n_old} bevisrader fra tidligere kjøring: {old_file.name}")

        matched = {}       # external_id -> db meet
        ext_id_pairs = []  # (meet_id, external_id)
        for season in seasons:
            for outdoor in ('Y', 'N'):
                source_meets = fetch_meets_from_source(season, outdoor)
                logger.info(f"Sesong {season} {'ute' if outdoor == 'Y' else 'inne'}: {len(source_meets)} stevner fra kilden")
                for sm in source_meets:
                    hit = match_source_meet(lookup, sm)
                    if hit and sm['external_id'] not in matched:
                        matched[sm['external_id']] = hit
                        ext_id_pairs.append((hit['meet_id'], sm['external_id']))

        logger.info(f"Matchet {len(matched)} av {len(lookup and target_meets)} målstevner mot kilden")
        update_meet_external_ids(ext_id_pairs, args.dry_run)
        if not args.dry_run:
            logger.info(f"Lagret external_id på {len(ext_id_pairs)} stevner")

        to_fetch = [(ext, m) for ext, m in matched.items() if ext not in done_ids]
        if args.limit:
            to_fetch = to_fetch[:args.limit]
        logger.info(f"Henter {len(to_fetch)} stevnesider ...")

        n_rows = 0
        with gzip.open(evidence_path, 'at', encoding='utf-8') as ev_fh, open(done_path, 'a') as done_fh:
            for i, (ext_id, dbm) in enumerate(to_fetch, 1):
                html = fetch_page(f"{BASE_URL}/StevneResultater.php", method='POST',
                                  data={'competition': ext_id})
                if not html:
                    logger.warning(f"Kunne ikke hente stevne {ext_id} ({dbm['name']})")
                    continue
                rows = parse_meet_results(html)
                for event, klass, name, birth_year in rows:
                    class_inventory[klass] += 1
                    g = get_gender_from_class(klass)
                    if g is None:
                        unknown_classes[klass] += 1
                        continue
                    evidence[(normalize_athlete_name(name), birth_year)][g] += 1
                    ev_fh.write(json.dumps({
                        'meet_external_id': ext_id, 'meet_id': dbm['meet_id'],
                        'date': dbm['start_date'], 'event': event, 'class': klass,
                        'name': name, 'birth_year': birth_year,
                    }, ensure_ascii=False) + '\n')
                    n_rows += 1
                done_fh.write(ext_id + '\n')
                done_fh.flush()
                if i % 100 == 0:
                    logger.info(f"  {i}/{len(to_fetch)} stevner, {n_rows} bevisrader, "
                                f"{len(evidence)} unike (navn, år)")

        logger.info(f"Ferdig scrapet: {n_rows} bevisrader, bevis lagret i {evidence_path}")
        if unknown_classes:
            logger.warning(f"Klasser uten kjønnsmapping (hoppet over): {dict(unknown_classes.most_common(20))}")

    # ------------------------------------------------------------
    # Beslutninger
    # ------------------------------------------------------------
    set_m, set_f = [], []
    conflicts, no_evidence = [], []
    contradictions = []

    for a in null_athletes:
        key = (normalize_athlete_name(a['full_name'] or ''), a['birth_year'])
        counts = evidence.get(key)
        if not counts:
            no_evidence.append(a)
            continue
        gender, reason = decide_gender(counts)
        if gender == 'M':
            set_m.append(a['id'])
        elif gender == 'F':
            set_f.append(a['id'])
        else:
            conflicts.append({'id': a['id'], 'name': a['full_name'],
                              'birth_year': a['birth_year'], 'reason': reason})

    # Kryssjekk av utøvere som allerede har kjønn (rapporteres kun)
    for a in athletes:
        if a['gender'] not in ('M', 'F'):
            continue
        key = (normalize_athlete_name(a['full_name'] or ''), a['birth_year'])
        counts = evidence.get(key)
        if not counts:
            continue
        derived, _ = decide_gender(counts)
        if derived and derived != a['gender'] and sum(counts.values()) >= 3:
            contradictions.append({'id': a['id'], 'name': a['full_name'],
                                   'birth_year': a['birth_year'], 'db_gender': a['gender'],
                                   'evidence_M': counts.get('M', 0), 'evidence_F': counts.get('F', 0)})

    logger.info("=" * 60)
    logger.info(f"Setter M: {len(set_m)}  |  Setter F: {len(set_f)}")
    logger.info(f"Konflikter (manuell gjennomgang): {len(conflicts)}")
    logger.info(f"Uten bevis i denne kjøringen: {len(no_evidence)}")
    logger.info(f"Motstridende eksisterende kjønn (KUN rapportert): {len(contradictions)}")

    report_base = LOG_DIR / f'fix_gender_report_{timestamp}'
    for suffix, data in (('conflicts', conflicts), ('contradictions', contradictions)):
        if data:
            path = f"{report_base}_{suffix}.json"
            Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=1))
            logger.info(f"Rapport skrevet: {path}")

    update_gender_batch(set_m, 'M', args.dry_run)
    update_gender_batch(set_f, 'F', args.dry_run)
    if not args.dry_run:
        logger.info("Databaseoppdatering fullført")
    else:
        logger.info("DRY RUN fullført — ingenting endret")


if __name__ == '__main__':
    main()
