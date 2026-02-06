"""
Fix ALL middle/long distance times by comparing with source.

Fixes two issues:
1. Times missing decimals: "2:03" -> "2:03.7" or "2:03.70"
2. Wrong precision: "1:50.10" -> "1:50.1" (manual times with false trailing zero)

Preserves source precision:
- Source "2,03,7" (1 decimal) -> "2:03.7" (manual time)
- Source "2,03,70" (2 decimals) -> "2:03.70" (electronic time)
"""

import os
import re
import requests
from bs4 import BeautifulSoup
from supabase import create_client
from dotenv import dotenv_values
from datetime import datetime
import time as time_module

config = dotenv_values('.env')
supabase = create_client(config['SUPABASE_URL'], config['SUPABASE_SERVICE_KEY'])

BASE_URL = "https://www.minfriidrettsstatistikk.info/php"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) DataVerifier/1.0',
})

DRY_RUN = False


def parse_source_time(time_str):
    """Parse source time, preserving original precision."""
    if not time_str:
        return None, None

    time_str = time_str.strip()

    # Source format: "M,SS,X" or "M,SS,XX"
    match = re.match(r'^(\d+),(\d{1,2}),(\d{1,2})$', time_str)
    if match:
        mins = int(match.group(1))
        secs = int(match.group(2))
        decimals = match.group(3)  # Keep original precision!

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
    """Fetch ALL results for an athlete from the source."""
    url = f"{BASE_URL}/UtoverStatistikk.php"
    data = {'athlete': external_id, 'type': 'RES'}

    try:
        response = session.post(url, data=data, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
    except Exception as e:
        return {}

    soup = BeautifulSoup(response.text, 'lxml')

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


def needs_fix(db_perf, source_perf):
    """Check if DB performance needs correction based on source."""
    if not db_perf or not source_perf:
        return False

    new_perf, _ = parse_source_time(source_perf)
    if not new_perf:
        return False

    # Check if they match when we strip the trailing zero issue
    # DB might have "1:50.10" but should be "1:50.1"
    return db_perf != new_perf


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

    # Get all athletes with results in these events
    all_athlete_ids = set()

    for event in events.data:
        print(f"\nCollecting athletes for {event['name']}...")
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

    print(f"\nTotal athletes to check: {len(all_athlete_ids)}")

    fixed_count = 0
    skipped_count = 0
    processed = 0

    for athlete_id in all_athlete_ids:
        processed += 1

        # Get athlete external_id
        athlete = supabase.table('athletes').select(
            'external_id'
        ).eq('id', athlete_id).single().execute()

        if not athlete.data or not athlete.data.get('external_id'):
            continue

        external_id = athlete.data['external_id']

        # Fetch from source with retry logic
        source_results = None
        for attempt in range(3):
            try:
                source_results = fetch_athlete_results(external_id, event_names)
                time_module.sleep(0.1)  # Rate limit
                break
            except Exception as e:
                if attempt < 2:
                    time_module.sleep(2)  # Wait before retry
                continue

        if not source_results:
            continue

        if not source_results:
            continue

        # Get all DB results for this athlete
        for event in events.data:
            db_results = supabase.table('results').select(
                'id, performance, date'
            ).eq('event_id', event['id']).eq('athlete_id', athlete_id).execute()

            for r in db_results.data:
                db_perf = r['performance']
                db_date = r['date']
                db_date_short = parse_db_date(db_date)

                if not db_date_short:
                    continue

                # Find matching source result
                for key, src in source_results.items():
                    if src['date'] == db_date_short and event['name'].split()[0] in key:
                        new_perf, new_value = parse_source_time(src['performance'])

                        if new_perf and new_perf != db_perf:
                            # Verify the times represent the same result
                            # (same minutes and seconds, just different decimal precision)
                            db_base = db_perf.split('.')[0] if '.' in db_perf else db_perf
                            new_base = new_perf.split('.')[0]

                            if db_base == new_base:
                                if not DRY_RUN:
                                    supabase.table('results').update({
                                        'performance': new_perf,
                                        'performance_value': new_value
                                    }).eq('id', r['id']).execute()

                                fixed_count += 1
                        break

        if processed % 500 == 0:
            print(f"  Progress: {processed}/{len(all_athlete_ids)} athletes, {fixed_count} fixed")

    return fixed_count


if __name__ == '__main__':
    print("=" * 60)
    print("FIXING ALL MIDDLE/LONG DISTANCE TIMES")
    print("=" * 60)

    if DRY_RUN:
        print("*** DRY RUN ***\n")

    fixed = fix_all_times()

    print(f"\n{'='*60}")
    print(f"TOTAL: {fixed} times corrected")
    print("=" * 60)
