"""
Version 3: Fix ALL middle/long distance times.
Uses total-seconds matching to handle all broken formats:
- "601.00" (total seconds) for 3000m/5000m/10000m/1000m/2000m
- "1.47" (packed M.SS) for 600m
- "271.00" (total seconds) for some 1500m
- "4.51" (packed M.SS) for 1 mile
- "2:07.35" (correct format, just needs hundredths fix)
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
PROGRESS_FILE = "fix_times_v3_progress.json"

DRY_RUN = False

# SSL context
ssl_context = ssl.create_default_context()


def parse_source_time(time_str):
    """Parse source time, preserving original precision."""
    if not time_str:
        return None, None

    time_str = time_str.strip()

    # Strip trailing non-digit suffixes like "mx", "+", "h", etc.
    time_str = re.sub(r'[^0-9,]+$', '', time_str)

    # Format: M,SS,CC (with hundredths)
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

    # Format: M,SS (no hundredths - manual time)
    match = re.match(r'^(\d+),(\d{1,2})$', time_str)
    if match:
        mins = int(match.group(1))
        secs = int(match.group(2))
        perf = f"{mins}:{secs:02d}"
        value = (mins * 60 + secs) * 100
        return perf, value

    return None, None


def perf_to_total_seconds(perf):
    """Convert any DB performance format to total integer seconds.

    Handles:
    - "M:SS.CC" or "M:SS" → standard format
    - "SSS.00" → total seconds (1000m+ events)
    - "M.SS" → packed format (600m, short events)
    """
    if not perf:
        return None

    perf = perf.strip()

    # Standard format "M:SS" or "M:SS.CC"
    m = re.match(r'^(\d+):(\d{2})(?:\.(\d{1,2}))?$', perf)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2))

    # Numeric format "NNN.NN" - could be total seconds or packed M.SS
    m = re.match(r'^(\d+)\.(\d{1,2})$', perf)
    if m:
        int_part = int(m.group(1))
        dec_part = int(m.group(2))

        if int_part >= 60:
            # Total seconds (e.g., "601.00" for 10:01, "175.00" for 2:55)
            return int_part
        elif dec_part < 60:
            # Packed M.SS format (e.g., "1.47" for 1:47, "4.51" for 4:51)
            return int_part * 60 + dec_part
        else:
            return int_part

    # Plain integer "NNN"
    m = re.match(r'^(\d+)$', perf)
    if m:
        return int(m.group(1))

    return None


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
                    # Handle multiple results on same date (heats/finals)
                    while key in results:
                        key = f"{key}_dup"
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

    print(f"Fixing times for: {[e['name'] for e in events.data]}")

    # Load progress
    progress = load_progress()
    processed_set = set(progress['processed'])
    fixed_count = progress['fixed']

    print(f"Resuming from: {len(processed_set)} already processed, {fixed_count} already fixed")

    # Get all athletes with results in these events
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
                else:
                    print(f"  ERROR getting athlete {athlete_id}: {e}")

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
                else:
                    print(f"  ERROR fetching source for {external_id}: {e}")

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
                        'id, performance, performance_value, date'
                    ).eq('event_id', event['id']).eq('athlete_id', athlete_id).execute()
                    break
                except Exception as e:
                    if db_attempt < 2:
                        time_module.sleep(3)

            if not db_results:
                continue

            event_prefix = event['name'].split()[0]

            for r in db_results.data:
                db_perf = r['performance']
                db_date = r['date']
                db_date_short = parse_db_date(db_date)

                if not db_date_short:
                    continue

                db_seconds = perf_to_total_seconds(db_perf)
                if db_seconds is None:
                    continue

                new_perf = None
                new_value = None

                # Primary match: date + total seconds
                for key, src in source_results.items():
                    if event_prefix not in key:
                        continue

                    if src['date'] == db_date_short:
                        parsed_perf, parsed_value = parse_source_time(src['performance'])
                        if parsed_perf:
                            src_seconds = parsed_value // 100
                            if src_seconds == db_seconds and parsed_perf != db_perf:
                                new_perf = parsed_perf
                                new_value = parsed_value
                                break

                # Fallback: total seconds match when source has invalid date
                if not new_perf:
                    for key, src in source_results.items():
                        if event_prefix not in key:
                            continue
                        if '00.00' not in src['date']:
                            continue
                        parsed_perf, parsed_value = parse_source_time(src['performance'])
                        if parsed_perf:
                            src_seconds = parsed_value // 100
                            if src_seconds == db_seconds and parsed_perf != db_perf:
                                new_perf = parsed_perf
                                new_value = parsed_value
                                break

                if new_perf and new_value:
                    # Also fix performance_value if it's NULL or wrong
                    needs_update = (new_perf != db_perf) or (r.get('performance_value') != new_value)

                    if needs_update and not DRY_RUN:
                        # DB trigger recalculates performance_value from performance.
                        # It handles M:SS.CC and M:SS.C fine, but sets NULL for M:SS (no decimals).
                        # For M:SS format, do a two-step update.
                        no_decimals = '.' not in new_perf

                        for upd_attempt in range(3):
                            try:
                                supabase.table('results').update({
                                    'performance': new_perf,
                                    'performance_value': new_value
                                }).eq('id', r['id']).execute()

                                # Second step for M:SS format to fix trigger's NULL
                                if no_decimals:
                                    supabase.table('results').update({
                                        'performance_value': new_value
                                    }).eq('id', r['id']).execute()

                                break
                            except Exception as e:
                                if upd_attempt < 2:
                                    time_module.sleep(2)

                    if needs_update:
                        fixed_count += 1

        processed_set.add(athlete_id)
        processed_this_run += 1

        # Save progress periodically
        if processed_this_run % 100 == 0:
            progress = {'processed': list(processed_set), 'fixed': fixed_count}
            save_progress(progress)
            print(f"  Progress: {len(processed_set)}/{len(all_athlete_ids)} athletes, {fixed_count} fixed")

    # Final save
    progress = {'processed': list(processed_set), 'fixed': fixed_count}
    save_progress(progress)

    return fixed_count


if __name__ == '__main__':
    print("=" * 60)
    print("FIXING ALL TIMES (V3 - TOTAL SECONDS MATCHING)")
    print("=" * 60)

    if DRY_RUN:
        print("*** DRY RUN ***\n")

    fixed = fix_all_times()

    print(f"\n{'='*60}")
    print(f"TOTAL: {fixed} times corrected")
    print("=" * 60)
