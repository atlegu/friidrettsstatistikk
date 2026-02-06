"""
Fix 800m and 1500m times by re-fetching from source.

Problem: Times like "2,45,47" (2:45.47) were imported incorrectly as "2.51" or similar.
Solution: Re-fetch the correct times from the source and update the database.
"""

import os
import re
import requests
from bs4 import BeautifulSoup
from supabase import create_client
from dotenv import dotenv_values
from datetime import datetime
import time

config = dotenv_values('.env')
supabase = create_client(config['SUPABASE_URL'], config['SUPABASE_SERVICE_KEY'])

BASE_URL = "https://www.minfriidrettsstatistikk.info/php"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) DataVerifier/1.0',
})

DRY_RUN = False  # Set to False to actually update


def parse_source_time(time_str, is_middle_distance=True):
    """
    Parse time string from source.

    Source formats:
    - "2,45,47" -> 2:45.47 (minutes, seconds, hundredths)
    - "4,12,5" -> 4:12.50 (minutes, seconds, tenths)
    - "8:18.25" -> 8:18.25 (already correct format)
    """
    if not time_str:
        return None, None

    # Clean up
    time_str = time_str.strip()

    # Already in correct format with colon and decimal
    if ':' in time_str and '.' in time_str:
        match = re.match(r'^(\d+):(\d{2})\.(\d{1,2})$', time_str)
        if match:
            mins = int(match.group(1))
            secs = int(match.group(2))
            cents = match.group(3).ljust(2, '0')
            perf = f"{mins}:{secs:02d}.{cents}"
            value = (mins * 60 + secs) * 100 + int(cents)
            return perf, value

    # Format with colons but no decimal (like "4:12")
    if ':' in time_str and '.' not in time_str:
        parts = time_str.split(':')
        if len(parts) == 2:
            mins = int(parts[0])
            secs = int(parts[1])
            perf = f"{mins}:{secs:02d}"
            value = (mins * 60 + secs) * 100
            return perf, value

    # Comma-separated format: "2,45,47" or "4,12,5"
    if ',' in time_str:
        parts = time_str.split(',')
        if len(parts) == 3:
            mins = int(parts[0])
            secs = int(parts[1])
            cents = parts[2]
            # If single digit, it's tenths (5 -> 50), if two digits it's hundredths
            if len(cents) == 1:
                cents = cents + '0'
            cents = cents.ljust(2, '0')[:2]
            perf = f"{mins}:{secs:02d}.{cents}"
            value = (mins * 60 + secs) * 100 + int(cents)
            return perf, value
        elif len(parts) == 2:
            # Just minutes and seconds
            mins = int(parts[0])
            secs = int(parts[1])
            perf = f"{mins}:{secs:02d}"
            value = (mins * 60 + secs) * 100
            return perf, value

    return None, None


def fetch_athlete_track_results(external_id):
    """Fetch track results for an athlete from the source."""
    url = f"{BASE_URL}/UtoverStatistikk.php?showathl={external_id}"

    response = session.get(url, timeout=30)
    response.raise_for_status()
    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.text, 'lxml')

    results = {}
    current_event = None

    for elem in soup.find_all(['h3', 'table', 'tr']):
        if elem.name == 'h3':
            text = elem.get_text(strip=True)
            if text and not text.startswith('Født:'):
                current_event = text

        elif elem.name == 'table' and current_event:
            # Only process 800m and 1500m
            if '800' not in current_event and '1500' not in current_event:
                continue

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

                result_data = {'event': current_event}

                for i, header in enumerate(headers):
                    if i >= len(cols):
                        break
                    text = cols[i].get_text(strip=True)

                    if header == 'RESULTAT':
                        # Remove wind info if present
                        text = re.sub(r'\([^)]+\)', '', text).strip()
                        result_data['performance'] = text
                    elif header == 'DATO':
                        result_data['date'] = text

                if result_data.get('performance') and result_data.get('date'):
                    key = f"{current_event}_{result_data['date']}"
                    results[key] = result_data

    return results


def parse_date(date_str):
    """Parse date string to ISO format."""
    if not date_str:
        return None
    for fmt in ['%d.%m.%Y', '%d.%m.%y']:
        try:
            dt = datetime.strptime(date_str, fmt)
            if dt.year < 100:
                dt = dt.replace(year=dt.year + 2000 if dt.year < 50 else dt.year + 1900)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    return None


def is_bad_800m_time(perf):
    """Check if an 800m time is clearly wrong."""
    if not perf:
        return True

    # Already looks good
    if ':' in perf and '.' in perf:
        return False

    # Missing hundredths (like "2:04" instead of "2:04.xx")
    if ':' in perf and '.' not in perf:
        return True

    # Totally wrong format (like "2.51")
    if ':' not in perf:
        return True

    return False


def fix_middle_distance_times():
    """Fix 800m and 1500m times by re-fetching from source."""

    # Get event IDs
    events = supabase.table('events').select('id, code, name').in_(
        'code', ['800m', '1500m']
    ).execute()

    event_map = {e['id']: e for e in events.data}
    event_ids = list(event_map.keys())

    print(f"Checking events: {[e['name'] for e in events.data]}")

    # Find results that need fixing - female athletes only (they have the issue)
    athletes_to_fix = {}

    for event in events.data:
        event_id = event['id']
        event_name = event['name']

        print(f"\nFetching bad {event_name} results...")

        # Get all results for this event
        offset = 0
        batch_size = 1000

        while True:
            results = supabase.table('results').select(
                'id, performance, performance_value, date, athlete_id, event_id'
            ).eq('event_id', event_id).range(offset, offset + batch_size - 1).execute()

            if not results.data:
                break

            for r in results.data:
                if is_bad_800m_time(r['performance']):
                    athlete_id = r['athlete_id']
                    if athlete_id not in athletes_to_fix:
                        athletes_to_fix[athlete_id] = []
                    athletes_to_fix[athlete_id].append(r)

            if len(results.data) < batch_size:
                break
            offset += batch_size

    total_bad = sum(len(v) for v in athletes_to_fix.values())
    print(f"\nFound {total_bad} results to fix across {len(athletes_to_fix)} athletes")

    fixed_count = 0
    skipped_count = 0

    processed = 0
    for athlete_id, bad_results in athletes_to_fix.items():
        processed += 1

        # Get athlete external_id
        athlete = supabase.table('athletes').select(
            'external_id, gender'
        ).eq('id', athlete_id).single().execute()

        if not athlete.data or not athlete.data.get('external_id'):
            skipped_count += len(bad_results)
            continue

        external_id = athlete.data['external_id']

        # Fetch original data
        try:
            source_results = fetch_athlete_track_results(external_id)
            time.sleep(0.1)  # Be nice to the server
        except Exception as e:
            print(f"  Error fetching {external_id}: {e}")
            skipped_count += len(bad_results)
            continue

        # Match and fix each bad result
        for bad_result in bad_results:
            bad_perf = bad_result['performance']
            bad_date = bad_result['date']
            event_name = event_map[bad_result['event_id']]['name']

            # Find matching result in source
            found = False
            for key, src in source_results.items():
                src_date = parse_date(src.get('date'))
                src_perf = src.get('performance', '')

                # Check if dates match
                if src_date == bad_date and event_name.lower() in key.lower():
                    new_perf, new_value = parse_source_time(src_perf)

                    if new_perf and new_value:
                        if not DRY_RUN:
                            supabase.table('results').update({
                                'performance': new_perf,
                                'performance_value': new_value
                            }).eq('id', bad_result['id']).execute()

                        fixed_count += 1
                        found = True
                        break

            if not found:
                skipped_count += 1

        if processed % 100 == 0:
            print(f"  Progress: {processed}/{len(athletes_to_fix)} athletes, {fixed_count} fixed, {skipped_count} skipped")

    return fixed_count, skipped_count


if __name__ == '__main__':
    print("=" * 60)
    print("FIXING 800M/1500M TIMES FROM SOURCE")
    print("=" * 60)

    if DRY_RUN:
        print("*** DRY RUN - ingen endringer vil bli gjort ***")
        print("Sett DRY_RUN = False for a faktisk oppdatere\n")

    fixed, skipped = fix_middle_distance_times()

    print(f"\n{'='*60}")
    print(f"TOTALT: {fixed} fikset, {skipped} hoppet over")
    print("=" * 60)
