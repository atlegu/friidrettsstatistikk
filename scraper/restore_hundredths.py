"""
Restore hundredths for 800m and 1500m times by re-fetching from source.

Problem: Times like "2,22,56" (2:22.56) were imported as "2:22" (missing hundredths).
Solution: Re-fetch the correct times from the source and update the database.
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
    """
    Parse time string from source.

    IMPORTANT: Preserve precision from source!
    - "2,03,1" = manual time (tidel) -> "2:03.1" (NOT "2:03.10")
    - "2,03,10" = electronic time (hundredel) -> "2:03.10"
    """
    if not time_str:
        return None, None

    time_str = time_str.strip()

    # Source format: "M,SS,X" or "M,SS,XX" (comma-separated)
    match = re.match(r'^(\d+),(\d{1,2}),(\d{1,2})$', time_str)
    if match:
        mins = int(match.group(1))
        secs = int(match.group(2))
        decimals = match.group(3)  # Keep original precision!

        # Preserve original precision: 1 digit = tenths (manual), 2 digits = hundredths (electronic)
        perf = f"{mins}:{secs:02d}.{decimals}"

        # For performance_value, convert to hundredths
        if len(decimals) == 1:
            value = (mins * 60 + secs) * 100 + int(decimals) * 10
        else:
            value = (mins * 60 + secs) * 100 + int(decimals)

        return perf, value

    # Already correct format "M:SS.X" or "M:SS.XX"
    match = re.match(r'^(\d+):(\d{2})\.(\d{1,2})$', time_str)
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
    """Parse ISO date to dd.mm.yy format for matching."""
    if not date_str:
        return None
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%d.%m.%y')
    except:
        return None


def fetch_athlete_results(external_id, event_names):
    """Fetch ALL results for an athlete from the source using POST."""
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
            # Only process target events
            if not any(en.lower() in current_event.lower() for en in event_names):
                continue

            rows = elem.find_all('tr')
            if not rows:
                continue

            # Check header
            header_row = rows[0]
            headers = [th.get_text(strip=True).upper() for th in header_row.find_all(['th', 'td'])]

            if 'RESULTAT' not in headers:
                continue

            res_idx = headers.index('RESULTAT')
            date_idx = headers.index('DATO') if 'DATO' in headers else -1

            for row in rows[1:]:  # Skip header
                cols = row.find_all('td')
                if len(cols) <= res_idx:
                    continue

                src_perf = cols[res_idx].get_text().strip()
                src_date = cols[date_idx].get_text().strip() if date_idx >= 0 and len(cols) > date_idx else ""

                if src_date:
                    # Store by date and event
                    key = f"{current_event}_{src_date}"
                    results[key] = {
                        'performance': src_perf,
                        'date': src_date,
                        'event': current_event
                    }

    return results


def restore_hundredths():
    """Restore hundredths for all distance events."""

    event_codes = ['600m', '800m', '1000m', '1500m', '1mile', '2000m', '3000m', '5000m', '10000m']
    event_names = ['600 meter', '800 meter', '1000 meter', '1500 meter', '1 mile', '2000 meter', '3000 meter', '5000 meter', '10000 meter']

    events = supabase.table('events').select('id, code, name').in_(
        'code', event_codes
    ).execute()

    event_map = {e['id']: e for e in events.data}

    print(f"Restoring hundredths for: {[e['name'] for e in events.data]}")

    # Find results without hundredths (format "M:SS" without decimal)
    athletes_to_fix = {}

    for event in events.data:
        event_id = event['id']
        event_name = event['name']

        print(f"\nFinding {event_name} results without hundredths...")

        offset = 0
        batch_size = 1000
        count = 0

        while True:
            results = supabase.table('results').select(
                'id, performance, date, athlete_id, event_id'
            ).eq('event_id', event_id).range(offset, offset + batch_size - 1).execute()

            if not results.data:
                break

            for r in results.data:
                perf = r['performance']
                # Check if has colon but no decimal (missing hundredths)
                if perf and ':' in perf and '.' not in perf:
                    athlete_id = r['athlete_id']
                    if athlete_id not in athletes_to_fix:
                        athletes_to_fix[athlete_id] = []
                    athletes_to_fix[athlete_id].append(r)
                    count += 1

            if len(results.data) < batch_size:
                break
            offset += batch_size

        print(f"  Found {count} results without hundredths")

    total_to_fix = sum(len(v) for v in athletes_to_fix.values())
    print(f"\nTotal: {total_to_fix} results to fix across {len(athletes_to_fix)} athletes")

    fixed_count = 0
    skipped_count = 0
    processed = 0

    for athlete_id, bad_results in athletes_to_fix.items():
        processed += 1

        # Get athlete external_id
        athlete = supabase.table('athletes').select(
            'external_id'
        ).eq('id', athlete_id).single().execute()

        if not athlete.data or not athlete.data.get('external_id'):
            skipped_count += len(bad_results)
            continue

        external_id = athlete.data['external_id']

        # Fetch from source
        try:
            source_results = fetch_athlete_results(external_id, event_names)
            time_module.sleep(0.05)  # Rate limit
        except Exception as e:
            skipped_count += len(bad_results)
            continue

        # Match and fix
        for bad_result in bad_results:
            db_perf = bad_result['performance']
            db_date = bad_result['date']
            db_date_short = parse_db_date(db_date)
            event_name = event_map[bad_result['event_id']]['name']

            found = False
            for key, src in source_results.items():
                # Match by date and event
                if src['date'] == db_date_short and event_name.lower() in key.lower():
                    new_perf, new_value = parse_source_time(src['performance'])

                    if new_perf and new_value:
                        # Only update if we're adding hundredths (not changing the time)
                        # DB has "2:22", source has "2:22.56" -> new should be "2:22.xx"
                        if new_perf.startswith(db_perf):
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

        if processed % 500 == 0:
            print(f"  Progress: {processed}/{len(athletes_to_fix)} athletes, {fixed_count} fixed, {skipped_count} skipped")

    return fixed_count, skipped_count


if __name__ == '__main__':
    print("=" * 60)
    print("RESTORING HUNDREDTHS FROM SOURCE")
    print("=" * 60)

    if DRY_RUN:
        print("*** DRY RUN ***\n")

    fixed, skipped = restore_hundredths()

    print(f"\n{'='*60}")
    print(f"TOTAL: {fixed} fixed, {skipped} skipped")
    print("=" * 60)
