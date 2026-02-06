"""
Fix 800m and 1500m times that were imported with missing hundredths.

Problem: Times like "1,58,10" (1:58.10) were stored as "118.00" or "119.00"
         losing the hundredths precision.
Solution: Re-fetch the correct times from the source and update the database.
"""

import os
import re
import requests
from bs4 import BeautifulSoup
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

BASE_URL = "https://www.minfriidrettsstatistikk.info/php"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) DataVerifier/1.0',
})

DRY_RUN = True  # Set to False to actually update


def parse_time_to_hundredths(time_str):
    """Parse time string like '1:58.10' to hundredths of seconds."""
    if not time_str:
        return None

    # Normalize separators
    time_str = time_str.replace(',', ':')

    # Try M:SS.cc format (e.g., "1:58.10")
    match = re.match(r'^(\d{1,2}):(\d{2})\.(\d{1,2})$', time_str)
    if match:
        minutes = int(match.group(1))
        seconds = int(match.group(2))
        centiseconds = match.group(3).ljust(2, '0')
        total_hundredths = (minutes * 60 + seconds) * 100 + int(centiseconds)
        return total_hundredths

    # Try M:SS format (e.g., "1:58")
    match = re.match(r'^(\d{1,2}):(\d{2})$', time_str)
    if match:
        minutes = int(match.group(1))
        seconds = int(match.group(2))
        return (minutes * 60 + seconds) * 100

    return None


def format_time_from_source(time_str):
    """Convert source format (1,58,10) to display format (1:58.10)."""
    if not time_str:
        return None
    # Replace commas with colons and periods
    parts = time_str.split(',')
    if len(parts) == 3:
        mins, secs, centis = parts
        return f"{mins}:{secs}.{centis.zfill(2)}"
    elif len(parts) == 2:
        mins, secs = parts
        return f"{mins}:{secs}"
    return time_str


def fetch_athlete_results(external_id, event_filter=None):
    """Fetch results for an athlete from the source."""
    url = f"{BASE_URL}/UtoverStatistikk.php"
    data = {'athlete': external_id, 'type': 'RES'}

    response = session.post(url, data=data, timeout=30)
    response.raise_for_status()
    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.text, 'lxml')

    results = []
    current_event = None
    current_indoor = None

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
            # Filter for specific events if requested
            if event_filter and not any(f in current_event for f in event_filter):
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

                result_data = {'event': current_event, 'indoor': current_indoor}

                for i, header in enumerate(headers):
                    if i >= len(cols):
                        break
                    text = cols[i].get_text(strip=True)

                    if header == 'RESULTAT':
                        result_data['performance'] = text
                    elif header == 'DATO':
                        result_data['date'] = text

                if result_data.get('performance'):
                    results.append(result_data)

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


def fix_middle_distance_times():
    """Find and fix 800m/1500m times with missing hundredths."""

    # Get event IDs
    events = supabase.table('events').select('id, code, name').in_(
        'code', ['800m', '1500m']
    ).execute()

    event_map = {e['id']: e for e in events.data}
    event_ids = list(event_map.keys())
    event_filters = {'800m': ['800 meter'], '1500m': ['1500 meter']}

    print(f"Checking events: {[e['name'] for e in events.data]}")

    # Find results with whole seconds (missing hundredths)
    results = supabase.table('results').select(
        'id, performance, performance_value, date, athlete_id, event_id'
    ).in_('event_id', event_ids).execute()

    # Group by athlete for efficient fetching
    athletes_to_fix = {}

    for r in results.data:
        perf = r['performance']
        # Check if it's a whole second time (like "118.00" or "119.0" or ends with ".00")
        if perf:
            # Match patterns like "118.00", "119.0", "120"
            if re.match(r'^\d+\.0+$', perf) or re.match(r'^\d+\.00$', perf) or re.match(r'^\d+$', perf):
                athlete_id = r['athlete_id']
                if athlete_id not in athletes_to_fix:
                    athletes_to_fix[athlete_id] = []
                athletes_to_fix[athlete_id].append(r)

    total_to_fix = sum(len(v) for v in athletes_to_fix.values())
    print(f"\nFound {total_to_fix} results with whole seconds across {len(athletes_to_fix)} athletes")

    if total_to_fix == 0:
        print("No results to fix!")
        return 0

    fixed_count = 0

    for athlete_id, bad_results in athletes_to_fix.items():
        # Get athlete external_id
        athlete = supabase.table('athletes').select(
            'first_name, last_name, external_id'
        ).eq('id', athlete_id).single().execute()

        if not athlete.data or not athlete.data.get('external_id'):
            continue

        name = f"{athlete.data['first_name']} {athlete.data['last_name']}"
        external_id = athlete.data['external_id']

        # Determine which events we need
        event_codes = set(event_map[r['event_id']]['code'] for r in bad_results)
        filters = []
        for code in event_codes:
            filters.extend(event_filters.get(code, []))

        print(f"\n{name} (external_id: {external_id}):")

        # Fetch original data
        try:
            source_results = fetch_athlete_results(external_id, filters)
        except Exception as e:
            print(f"  Error fetching data: {e}")
            continue

        # Match and fix each bad result
        for bad_result in bad_results:
            bad_perf = bad_result['performance']
            bad_date = bad_result['date']
            event_code = event_map[bad_result['event_id']]['code']
            event_name = event_map[bad_result['event_id']]['name']

            # Convert stored performance to approximate seconds
            try:
                stored_seconds = float(bad_perf.rstrip('0').rstrip('.')) if '.' in bad_perf else float(bad_perf)
            except:
                continue

            # Find matching result in source
            found = False
            for src in source_results:
                src_date = parse_date(src.get('date'))
                src_perf = src.get('performance', '')

                # Check if dates match
                if src_date == bad_date:
                    # Parse source performance
                    formatted = format_time_from_source(src_perf)
                    new_value = parse_time_to_hundredths(formatted)

                    if new_value:
                        # Convert to seconds to compare
                        src_seconds = new_value / 100

                        # Check if it's close to our stored value (within 1 second)
                        if abs(src_seconds - stored_seconds) < 1.0:
                            print(f"  {event_name}: {bad_perf} -> {formatted} (value: {bad_result['performance_value']} -> {new_value})")

                            if not DRY_RUN:
                                supabase.table('results').update({
                                    'performance': formatted,
                                    'performance_value': new_value
                                }).eq('id', bad_result['id']).execute()

                            fixed_count += 1
                            found = True
                            break

            if not found:
                print(f"  {event_name}: {bad_perf} on {bad_date} - NO MATCH FOUND")

    return fixed_count


if __name__ == '__main__':
    print("=" * 60)
    print("FIXING 800M/1500M TIMES (MISSING HUNDREDTHS)")
    print("=" * 60)

    if DRY_RUN:
        print("*** DRY RUN - ingen endringer vil bli gjort ***")
        print("Sett DRY_RUN = False for a faktisk oppdatere\n")

    fixed = fix_middle_distance_times()

    print(f"\n{'='*60}")
    print(f"TOTALT: {fixed} resultater {'vil bli oppdatert' if DRY_RUN else 'oppdatert'}")
    print("=" * 60)

    if DRY_RUN:
        print("\nFor a faktisk oppdatere, endre DRY_RUN = False i scriptet")
