"""
Batch import of all missing athletes from minfriidrettsstatistikk.info.
Iterates through ID ranges 1-75000, skips IDs already in the database,
and imports all results for missing athletes.

Usage: python3 import_missing_athletes.py [--start N] [--end N] [--workers N]
"""

import os
import re
import sys
import json
import time
import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from threading import Lock
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
BASE_URL = "https://www.minfriidrettsstatistikk.info/php"

# Progress file for resume support
PROGRESS_FILE = 'import_missing_progress.json'

# --- Event mapping (same as import_single_athlete.py) ---
EVENT_NAME_TO_CODE = {
    '30 meter': '30m', '40 meter': '40m', '50 meter': '50m',
    '60 meter': '60m', '80 meter': '80m', '100 meter': '100m',
    '150 meter': '150m', '200 meter': '200m', '300 meter': '300m',
    '400 meter': '400m', '600 meter': '600m',
    '800 meter': '800m', '1000 meter': '1000m', '1500 meter': '1500m',
    '2000 meter': '2000m', '3000 meter': '3000m', '5000 meter': '5000m',
    '10000 meter': '10000m', '1 engelsk mil': '1mile',
    'Høyde': 'hoyde', 'Stav': 'stav', 'Lengde': 'lengde', 'Tresteg': 'tresteg',
    'Lengde uten tilløp': 'lengde_ut', 'Høyde uten tilløp': 'hoyde_ut',
    'Tresteg uten tilløp': 'tresteg_ut',
    'Kule 7,26kg': 'kule_7_26kg', 'Kule 6,0kg': 'kule_6kg', 'Kule 5,0kg': 'kule_5kg',
    'Kule 4,0kg': 'kule_4kg', 'Kule 3,0kg': 'kule_3kg', 'Kule 2,0kg': 'kule_2kg',
    'Diskos 2,0kg': 'diskos_2kg', 'Diskos 1,75kg': 'diskos_1_75kg',
    'Diskos 1,5kg': 'diskos_1_5kg', 'Diskos 1,0kg': 'diskos_1kg',
    'Diskos 750gram': 'diskos_750g', 'Diskos 600gram': 'diskos_600g',
    'Spyd 800gram': 'spyd_800g', 'Spyd 700gram': 'spyd_700g',
    'Spyd 600gram': 'spyd_600g', 'Spyd 500gram': 'spyd_500g',
    'Spyd 400gram': 'spyd_400g',
    'Slegge 7,26kg/121,5cm': 'slegge_726kg/1215cm', 'Slegge 6,0kg/121,5cm': 'slegge_60kg/1215cm',
    'Slegge 5,0kg/120cm': 'slegge_50kg/120cm', 'Slegge 4,0kg/119,5cm': 'slegge_40kg/1195cm',
    'Slegge 4,0kg/120cm': 'slegge_40kg/1195cm',
    'Slegge 3,0kg/119,5cm': 'slegge_30kg_1195cm', 'Slegge 3,0kg/110cm': 'slegge_30kg/110cm',
    'Slegge 2,0kg/110cm': 'slegge_20kg/110cm',
    'Femkamp': '5kamp', 'Sjukamp': '7kamp', 'Tikamp': '10kamp',
    # Road events
    '5 km': '5km', '10 km': '10km', '15 km': '15km',
    'Halvmaraton': 'halvmaraton', 'Maraton': 'maraton',
    # Walk events
    '3000 meter gange': '3000mg', '5000 meter gange': '5000mg',
    '10000 meter gange': '10000mg', '20 km gange': '20kmg',
    # Relay
    '4 x 100 meter': '4x100m', '4 x 400 meter': '4x400m',
}

for dist in ['30', '40', '50', '60', '80', '100', '110', '200', '300', '400']:
    EVENT_NAME_TO_CODE[f'{dist} meter hekk'] = f'{dist}mh'
    for height in ['60cm', '68cm', '68,0cm', '76,2cm', '84cm', '84,0cm', '91,4cm', '100cm', '106,7cm']:
        h_code = height.replace(',', '_').replace('cm', 'cm').replace('.', '_')
        EVENT_NAME_TO_CODE[f'{dist} meter hekk ({height})'] = f'{dist}mh_{h_code}'

for dist in ['1500', '2000', '3000']:
    EVENT_NAME_TO_CODE[f'{dist} meter hinder'] = f'{dist}mhinder'
    for height in ['76,2cm', '84cm', '84,0cm', '91,4cm']:
        h_code = height.replace(',', '_').replace('cm', 'cm')
        EVENT_NAME_TO_CODE[f'{dist} meter hinder ({height})'] = f'{dist}mhinder_{h_code}'


def convert_time_format(time_str):
    if not time_str:
        return time_str
    match = re.match(r'^(\d{1,2})\.(\d{2})\.(\d{1,2})$', time_str)
    if match:
        minutes = match.group(1)
        seconds = match.group(2)
        centiseconds = match.group(3)
        if len(centiseconds) == 1:
            centiseconds = centiseconds + '0'
        return f"{minutes}:{seconds}.{centiseconds}"
    return time_str


def parse_result_with_wind(result_str):
    if not result_str:
        return None, None
    result_str = result_str.strip()
    result_str = re.sub(r'\(ok\)', '', result_str, flags=re.IGNORECASE).strip()
    wind_match = re.search(r'\(([\+\-]?\d+[,\.]\d+)\)', result_str)
    wind = None
    if wind_match:
        wind_str = wind_match.group(1).replace(',', '.')
        try:
            wind = float(wind_str)
        except ValueError:
            pass
        result_str = re.sub(r'\s*\([^\)]+\)', '', result_str).strip()
    result = result_str.replace(',', '.')
    result = convert_time_format(result)
    return result, wind


def parse_date(date_str):
    if not date_str:
        return None
    for fmt in ['%d.%m.%Y', '%d.%m.%y', '%Y-%m-%d']:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    return None


def fetch_athlete_data(athlete_id, session, max_retries=3):
    """Fetch all results for an athlete from source website."""
    url = f"{BASE_URL}/UtoverStatistikk.php"
    data = {'athlete': athlete_id, 'type': 'RES'}

    for attempt in range(max_retries):
        try:
            response = session.post(url, data=data, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            break
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            return None

    soup = BeautifulSoup(response.text, 'lxml')

    name = None
    name_elem = soup.find('h2')
    if name_elem:
        name = name_elem.get_text(strip=True)

    if not name or name == '' or 'ikke funnet' in (name or '').lower():
        return None

    birth_date = None
    for h3 in soup.find_all('h3'):
        text = h3.get_text(strip=True)
        if text.startswith('Født:'):
            match = re.search(r'(\d{2}\.\d{2}\.\d{4})', text)
            if match:
                birth_date = match.group(1)
            break

    club = None
    for h3 in soup.find_all('h3'):
        text = h3.get_text(strip=True)
        if not text.startswith('Født:') and not text.startswith('INNENDØRS') and not text.startswith('UTENDØRS'):
            if 'IL' in text or 'SK' in text or 'IF' in text or 'BIL' in text or 'FK' in text:
                club = text
                break

    results = []
    current_indoor = None
    current_event = None

    for elem in soup.find_all(['h2', 'h3', 'table']):
        if elem.name == 'h2':
            text = elem.get_text(strip=True).upper()
            if 'INNENDØRS' in text:
                current_indoor = True
            elif 'UTENDØRS' in text:
                current_indoor = False
        elif elem.name == 'h3':
            text = elem.get_text(strip=True)
            if text and not text.startswith('Født:'):
                current_event = text
        elif elem.name == 'table' and current_event:
            rows = elem.find_all('tr')
            if not rows:
                continue
            header_row = rows[0]
            headers = [th.get_text(strip=True).upper() for th in header_row.find_all(['th', 'td'])]
            if 'RESULTAT' not in headers:
                continue
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) < 3:
                    continue
                try:
                    result_data = {'event': current_event, 'indoor': current_indoor}
                    for i, header in enumerate(headers):
                        if i >= len(cols):
                            break
                        cell = cols[i]
                        text = cell.get_text(strip=True)
                        if header == 'RESULTAT':
                            perf, wind = parse_result_with_wind(text)
                            result_data['performance'] = perf
                            result_data['wind'] = wind
                        elif header == 'DATO':
                            result_data['date'] = text
                        elif header == 'STED':
                            title = cell.get('title', '')
                            result_data['venue'] = title if title else text
                            result_data['meet_name'] = text
                        elif header == 'KLUBB':
                            result_data['club'] = text
                        elif header == 'PL':
                            try:
                                result_data['place'] = int(text) if text.isdigit() else None
                            except:
                                pass
                        elif header == 'ÅR':
                            year_match = re.match(r'(\d{4})', text)
                            if year_match:
                                result_data['year'] = int(year_match.group(1))
                    if result_data.get('performance'):
                        results.append(result_data)
                except Exception:
                    continue

    return {
        'external_id': str(athlete_id),
        'name': name,
        'birth_date': birth_date,
        'club': club,
        'results': results
    }


class AthleteImporter:
    """Handles database operations with caching."""

    def __init__(self):
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.event_cache = {}
        self.club_cache = {}
        self.meet_cache = {}
        self.season_cache = {}
        self.lock = Lock()
        self._load_caches()

    def _load_caches(self):
        """Pre-load events and seasons to avoid repeated queries."""
        print("Loading caches...")
        events = self.supabase.table('events').select('id, code, name').execute()
        for e in events.data:
            self.event_cache[e['code']] = e['id']
            self.event_cache[e['name']] = e['id']

        seasons = self.supabase.table('seasons').select('id, year, indoor').execute()
        for s in seasons.data:
            self.season_cache[(s['year'], s['indoor'])] = s['id']

        print(f"  {len(self.event_cache)} events, {len(self.season_cache)} seasons cached")

    def get_event_id(self, event_name):
        code = EVENT_NAME_TO_CODE.get(event_name)
        if code and code in self.event_cache:
            return self.event_cache[code]
        if event_name in self.event_cache:
            return self.event_cache[event_name]
        return None

    def get_or_create_club(self, name):
        if not name:
            return None
        with self.lock:
            if name in self.club_cache:
                return self.club_cache[name]
        result = self.supabase.table('clubs').select('id').eq('name', name).limit(1).execute()
        if result.data:
            club_id = result.data[0]['id']
        else:
            try:
                result = self.supabase.table('clubs').insert({'name': name}).execute()
                club_id = result.data[0]['id'] if result.data else None
            except:
                result = self.supabase.table('clubs').select('id').eq('name', name).limit(1).execute()
                club_id = result.data[0]['id'] if result.data else None
        with self.lock:
            self.club_cache[name] = club_id
        return club_id

    def get_or_create_meet(self, name, date, city, indoor):
        if not name or not date:
            return None
        key = f"{name}|{date}"
        with self.lock:
            if key in self.meet_cache:
                return self.meet_cache[key]
        result = self.supabase.table('meets').select('id').eq('name', name).eq('start_date', date).limit(1).execute()
        if result.data:
            meet_id = result.data[0]['id']
        else:
            try:
                meet_data = {
                    'name': name, 'start_date': date,
                    'city': city or name, 'indoor': indoor or False, 'country': 'NOR'
                }
                result = self.supabase.table('meets').insert(meet_data).execute()
                meet_id = result.data[0]['id'] if result.data else None
            except:
                result = self.supabase.table('meets').select('id').eq('name', name).eq('start_date', date).limit(1).execute()
                meet_id = result.data[0]['id'] if result.data else None
        with self.lock:
            self.meet_cache[key] = meet_id
        return meet_id

    def get_season_id(self, year, indoor):
        key = (year, indoor or False)
        return self.season_cache.get(key)

    def import_athlete(self, athlete_data):
        """Import one athlete and all results. Returns (imported, skipped, athlete_name)."""
        if not athlete_data or not athlete_data.get('name'):
            return 0, 0, None

        name = athlete_data['name']
        name_parts = name.split()
        first_name = name_parts[0] if name_parts else ''
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

        birth_date_iso = None
        birth_year = None
        if athlete_data.get('birth_date'):
            birth_date_iso = parse_date(athlete_data['birth_date'])
            if birth_date_iso:
                birth_year = int(birth_date_iso[:4])

        club_id = self.get_or_create_club(athlete_data.get('club'))
        ext_id = athlete_data['external_id']

        # Check if athlete exists
        existing = self.supabase.table('athletes').select('id').eq('external_id', ext_id).limit(1).execute()
        if existing.data:
            athlete_db_id = existing.data[0]['id']
        else:
            # Determine gender from source (default M, but check name patterns)
            athlete_row = {
                'first_name': first_name,
                'last_name': last_name,
                'gender': None,  # Will be set by scraper or left null
                'birth_date': birth_date_iso,
                'birth_year': birth_year,
                'current_club_id': club_id,
                'external_id': ext_id,
                'nationality': 'NOR'
            }
            try:
                result = self.supabase.table('athletes').insert(athlete_row).execute()
                if not result.data:
                    return 0, 0, name
                athlete_db_id = result.data[0]['id']
            except Exception as e:
                # Might already exist due to race condition
                existing = self.supabase.table('athletes').select('id').eq('external_id', ext_id).limit(1).execute()
                if existing.data:
                    athlete_db_id = existing.data[0]['id']
                else:
                    return 0, 0, name

        imported = 0
        skipped = 0

        for r in athlete_data.get('results', []):
            event_id = self.get_event_id(r['event'])
            if not event_id:
                skipped += 1
                continue

            date_iso = parse_date(r.get('date'))
            if not date_iso:
                skipped += 1
                continue

            year = r.get('year') or (int(date_iso[:4]) if date_iso else None)
            indoor = r.get('indoor', False)

            # Duplicate check
            dup = self.supabase.table('results').select('id').eq(
                'athlete_id', athlete_db_id
            ).eq('event_id', event_id).eq('date', date_iso).eq(
                'performance', r['performance']
            ).limit(1).execute()
            if dup.data:
                skipped += 1
                continue

            meet_id = self.get_or_create_meet(
                name=r.get('meet_name') or r.get('venue', ''),
                date=date_iso, city=r.get('venue', ''), indoor=indoor
            )
            season_id = self.get_season_id(year, indoor) if year else None
            result_club_id = self.get_or_create_club(r.get('club')) or club_id

            result_data = {
                'athlete_id': athlete_db_id,
                'event_id': event_id,
                'meet_id': meet_id,
                'season_id': season_id,
                'club_id': result_club_id,
                'performance': r['performance'],
                'date': date_iso,
                'wind': r.get('wind'),
                'place': r.get('place'),
                'status': 'OK',
                'verified': True
            }

            try:
                self.supabase.table('results').insert(result_data).execute()
                imported += 1
            except Exception:
                skipped += 1

        return imported, skipped, name


def load_progress():
    """Load set of already-processed IDs."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            data = json.load(f)
            return set(data.get('processed_ids', []))
    return set()


def save_progress(processed_ids):
    """Save progress to disk."""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump({'processed_ids': sorted(processed_ids), 'updated': datetime.now().isoformat()}, f)


def get_existing_external_ids(supabase):
    """Get all external_ids already in database."""
    print("Fetching existing external IDs from database...")
    all_ids = set()
    page_size = 1000
    offset = 0
    while True:
        result = supabase.table('athletes').select('external_id').not_.is_('external_id', 'null').range(offset, offset + page_size - 1).execute()
        if not result.data:
            break
        for row in result.data:
            if row['external_id']:
                all_ids.add(row['external_id'])
        if len(result.data) < page_size:
            break
        offset += page_size
    print(f"  Found {len(all_ids)} existing athletes in database")
    return all_ids


def main():
    parser = argparse.ArgumentParser(description='Import all missing athletes')
    parser.add_argument('--start', type=int, default=1, help='Start ID')
    parser.add_argument('--end', type=int, default=75000, help='End ID')
    parser.add_argument('--delay', type=float, default=0.5, help='Delay between requests in seconds')
    args = parser.parse_args()

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    existing_ids = get_existing_external_ids(supabase)
    processed_ids = load_progress()

    # Build list of IDs to check
    ids_to_check = []
    for i in range(args.start, args.end + 1):
        ext_id = str(i)
        if ext_id not in existing_ids and ext_id not in processed_ids:
            ids_to_check.append(i)

    print(f"\nIDs to check: {len(ids_to_check)} (range {args.start}-{args.end})")
    print(f"Already in DB: {len(existing_ids)}")
    print(f"Already processed (no data): {len(processed_ids)}")
    print(f"Delay: {args.delay}s between requests")
    print(f"Starting import at {datetime.now().strftime('%H:%M:%S')}\n")

    importer = AthleteImporter()

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) DataImporter/1.0',
        'Content-Type': 'application/x-www-form-urlencoded'
    })

    total_imported = 0
    total_new_athletes = 0
    total_empty = 0
    total_errors = 0
    batch_size = 50

    start_time = time.time()

    for i, athlete_id in enumerate(ids_to_check):
        try:
            data = fetch_athlete_data(athlete_id, session)

            if not data:
                total_empty += 1
                processed_ids.add(str(athlete_id))
            else:
                imported, skipped, name = importer.import_athlete(data)
                processed_ids.add(str(athlete_id))

                if name:
                    total_new_athletes += 1
                    total_imported += imported
                    elapsed = time.time() - start_time
                    checked = total_new_athletes + total_empty + total_errors
                    rate = checked / elapsed * 3600 if elapsed > 0 else 0
                    remaining = len(ids_to_check) - i - 1
                    eta_h = remaining / (checked / elapsed) / 3600 if checked > 0 and elapsed > 0 else 0
                    print(f"  [{i+1}/{len(ids_to_check)}] "
                          f"ID {athlete_id}: {name} — {imported} new results "
                          f"({rate:.0f}/h, ETA {eta_h:.1f}h)")

        except Exception as e:
            total_errors += 1
            print(f"  [{i+1}/{len(ids_to_check)}] ID {athlete_id}: ERROR {e}")

        # Save progress periodically
        if (i + 1) % batch_size == 0:
            save_progress(processed_ids)
            elapsed = time.time() - start_time
            print(f"\n  === Progress: {total_new_athletes} new athletes, "
                  f"{total_imported} results, {total_empty} empty, "
                  f"{total_errors} errors, {elapsed:.0f}s elapsed ===\n")

        # Rate limit
        time.sleep(args.delay)

    save_progress(processed_ids)

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"DONE in {elapsed/3600:.1f}h ({elapsed:.0f}s)")
    print(f"  New athletes: {total_new_athletes}")
    print(f"  Results imported: {total_imported}")
    print(f"  Empty/not found: {total_empty}")
    print(f"  Errors: {total_errors}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
