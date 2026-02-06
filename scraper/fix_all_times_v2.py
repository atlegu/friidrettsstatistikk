"""
Version 2: Fix ALL middle/long distance times.
Uses HTTP/1.1 to avoid connection issues.
"""

import os
import re
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from supabase import create_client
from dotenv import dotenv_values
from datetime import datetime
import time as time_module
import json
import ssl

config = dotenv_values('.env')
supabase = create_client(config['SUPABASE_URL'], config['SUPABASE_SERVICE_KEY'])

BASE_URL = "https://www.minfriidrettsstatistikk.info/php/UtoverStatistikk.php"
PROGRESS_FILE = "fix_times_progress.json"

DRY_RUN = False

# SSL context
ssl_context = ssl.create_default_context()


def parse_source_time(time_str):
    """Parse source time, preserving original precision."""
    if not time_str:
        return None, None

    time_str = time_str.strip()

    match = re.match(r'^(\d+),(\d{1,2}),(\d{1,2})$', time_str)
    if match:
        mins = int(match.group(1))
        secs = int(match.group(2))
        decimals = match.group(3)

        perf = f"{mins}:{secs:02d}.{decimals}"

        if len(decimals) == 1:
            value = (mins * 60 + secs) * 100 + int(decimals) * 10
        else:
            value = (mins * 60 + secs) * 100 + int(decimals)

        return perf, value

    return None, None


def parse_db_date(date_str):
    """Parse ISO date to dd.mm.yy format."""
    if not date_str:
        return None
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%d.%m.%y')
    except:
        return None


def fetch_athlete_results(external_id, event_names):
    """Fetch ALL results using urllib (HTTP/1.1)."""
    data = urllib.parse.urlencode({'athlete': external_id, 'type': 'RES'}).encode()

    req = urllib.request.Request(
        BASE_URL,
        data=data,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    )

    with urllib.request.urlopen(req, timeout=30, context=ssl_context) as response:
        html = response.read().decode('utf-8')

    soup = BeautifulSoup(html, 'lxml')

    results = {}
    current_event = None

    for elem in soup.find_all(['h3', 'table']):
        if elem.name == 'h3':
            text = elem.get_text(strip=True)
            if text and not text.startswith('Født:'):
                current_event = text

        elif elem.name == 'table' and current_event:
            if not any(en.lower() in current_event.lower() for en in event_names):
                continue

            rows = elem.find_all('tr')
            if not rows:
                continue

            header_row = rows[0]
            headers = [th.get_text(strip=True).upper() for th in header_row.find_all(['th', 'td'])]

            if 'RESULTAT' not in headers:
                continue

            res_idx = headers.index('RESULTAT')
            date_idx = headers.index('DATO') if 'DATO' in headers else -1

            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) <= res_idx:
                    continue

                src_perf = cols[res_idx].get_text().strip()
                src_date = cols[date_idx].get_text().strip() if date_idx >= 0 and len(cols) > date_idx else ""

                if src_date:
                    key = f"{current_event}_{src_date}"
                    results[key] = {
                        'performance': src_perf,
                        'date': src_date,
                        'event': current_event
                    }

    return results


def load_progress():
    """Load progress from file."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {'processed': [], 'fixed': 0}


def save_progress(progress):
    """Save progress to file."""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)


def fix_all_times():
    """Fix all middle/long distance times based on source."""

    event_codes = ['600m', '800m', '1000m', '1500m', '1mile', '2000m', '3000m', '5000m', '10000m']
    event_names = ['600 meter', '800 meter', '1000 meter', '1500 meter', '1 mile',
                   '2000 meter', '3000 meter', '5000 meter', '10000 meter']

    events = supabase.table('events').select('id, code, name').in_(
        'code', event_codes
    ).execute()

    event_map = {e['id']: e for e in events.data}

    print(f"Fixing times for: {[e['name'] for e in events.data]}")

    # Load progress
    progress = load_progress()
    processed_set = set(progress['processed'])
    fixed_count = progress['fixed']

    print(f"Resuming from: {len(processed_set)} already processed, {fixed_count} already fixed")

    # Get all athletes
    all_athlete_ids = set()

    for event in events.data:
        print(f"Collecting athletes for {event['name']}...")
        offset = 0
        batch_size = 1000

        while True:
            results = supabase.table('results').select(
                'athlete_id'
            ).eq('event_id', event['id']).range(offset, offset + batch_size - 1).execute()

            if not results.data:
                break

            for r in results.data:
                all_athlete_ids.add(r['athlete_id'])

            if len(results.data) < batch_size:
                break
            offset += batch_size

    remaining = [aid for aid in all_athlete_ids if aid not in processed_set]

    print(f"\nTotal athletes: {len(all_athlete_ids)}, Remaining: {len(remaining)}")

    processed_this_run = 0

    for i, athlete_id in enumerate(remaining):
        # Rate limiting
        time_module.sleep(0.2)

        # Get athlete external_id with retry
        athlete = None
        for db_attempt in range(3):
            try:
                athlete = supabase.table('athletes').select(
                    'external_id'
                ).eq('id', athlete_id).single().execute()
                break
            except Exception as e:
                if db_attempt < 2:
                    time_module.sleep(3)

        if not athlete or not athlete.data or not athlete.data.get('external_id'):
            processed_set.add(athlete_id)
            continue

        external_id = athlete.data['external_id']

        # Fetch from source with retry
        source_results = None
        for attempt in range(5):
            try:
                source_results = fetch_athlete_results(external_id, event_names)
                break
            except Exception as e:
                if attempt < 4:
                    time_module.sleep(2 * (attempt + 1))

        if not source_results:
            processed_set.add(athlete_id)
            continue

        # Get all DB results and fix them
        for event in events.data:
            # Retry Supabase queries
            db_results = None
            for db_attempt in range(3):
                try:
                    db_results = supabase.table('results').select(
                        'id, performance, date'
                    ).eq('event_id', event['id']).eq('athlete_id', athlete_id).execute()
                    break
                except Exception as e:
                    if db_attempt < 2:
                        time_module.sleep(3)

            if not db_results:
                continue

            for r in db_results.data:
                db_perf = r['performance']
                db_date = r['date']
                db_date_short = parse_db_date(db_date)

                if not db_date_short:
                    continue

                event_prefix = event['name'].split()[0]
                matched = False

                for key, src in source_results.items():
                    if event_prefix not in key:
                        continue

                    # Match by date first
                    if src['date'] == db_date_short:
                        new_perf, new_value = parse_source_time(src['performance'])
                        if new_perf and new_perf != db_perf:
                            db_base = db_perf.split('.')[0] if '.' in db_perf else db_perf
                            new_base = new_perf.split('.')[0]
                            if db_base == new_base:
                                matched = True
                                break

                # Fallback: match by performance base when source has bad date
                if not matched:
                    db_base = db_perf.split('.')[0] if '.' in db_perf else db_perf
                    for key, src in source_results.items():
                        if event_prefix not in key:
                            continue
                        new_perf, new_value = parse_source_time(src['performance'])
                        if new_perf:
                            new_base = new_perf.split('.')[0]
                            if db_base == new_base and new_perf != db_perf:
                                # Only use fallback when source date is invalid
                                if '00.00' in src['date']:
                                    matched = True
                                    break

                if matched and new_perf and new_value:
                    if not DRY_RUN:
                        for upd_attempt in range(3):
                            try:
                                supabase.table('results').update({
                                    'performance': new_perf,
                                    'performance_value': new_value
                                }).eq('id', r['id']).execute()
                                break
                            except Exception as e:
                                if upd_attempt < 2:
                                    time_module.sleep(2)

                    fixed_count += 1

        processed_set.add(athlete_id)
        processed_this_run += 1

        # Save progress
        if processed_this_run % 100 == 0:
            progress = {'processed': list(processed_set), 'fixed': fixed_count}
            save_progress(progress)
            print(f"  Progress: {len(processed_set)}/{len(all_athlete_ids)} athletes, {fixed_count} fixed")

    progress = {'processed': list(processed_set), 'fixed': fixed_count}
    save_progress(progress)

    return fixed_count


if __name__ == '__main__':
    print("=" * 60)
    print("FIXING ALL TIMES (V2 - HTTP/1.1)")
    print("=" * 60)

    if DRY_RUN:
        print("*** DRY RUN ***\n")

    fixed = fix_all_times()

    print(f"\n{'='*60}")
    print(f"TOTAL: {fixed} times corrected")
    print("=" * 60)
