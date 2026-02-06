"""
Fix steeplechase (hinder) times using the same V3 logic.
Uses full event name matching to avoid confusing 3000m with 3000m hinder.
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
PROGRESS_FILE = "fix_steeplechase_progress.json"

DRY_RUN = False

ssl_context = ssl.create_default_context()


def parse_source_time(time_str):
    if not time_str:
        return None, None
    time_str = time_str.strip()
    time_str = re.sub(r'[^0-9,]+$', '', time_str)

    match = re.match(r'^(\d+),(\d{1,2}),(\d{1,2})$', time_str)
    if match:
        mins, secs, decimals = int(match.group(1)), int(match.group(2)), match.group(3)
        perf = f"{mins}:{secs:02d}.{decimals}"
        if len(decimals) == 1:
            value = (mins * 60 + secs) * 100 + int(decimals) * 10
        else:
            value = (mins * 60 + secs) * 100 + int(decimals)
        return perf, value

    match = re.match(r'^(\d+),(\d{1,2})$', time_str)
    if match:
        mins, secs = int(match.group(1)), int(match.group(2))
        return f"{mins}:{secs:02d}", (mins * 60 + secs) * 100

    return None, None


def perf_to_total_seconds(perf):
    if not perf:
        return None
    perf = perf.strip()

    m = re.match(r'^(\d+):(\d{2})(?:\.(\d{1,2}))?$', perf)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2))

    m = re.match(r'^(\d+)\.(\d{1,2})$', perf)
    if m:
        ip, dp = int(m.group(1)), int(m.group(2))
        if ip >= 60:
            return ip
        elif dp < 60:
            return ip * 60 + dp
        else:
            return ip

    m = re.match(r'^(\d+)$', perf)
    if m:
        return int(m.group(1))

    return None


def parse_db_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d.%m.%y')
    except:
        return None


def fetch_athlete_results(external_id, event_names):
    data = urllib.parse.urlencode({'athlete': external_id, 'type': 'RES'}).encode()
    req = urllib.request.Request(
        BASE_URL, data=data,
        headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
                 'Content-Type': 'application/x-www-form-urlencoded'}
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
            headers = [th.get_text(strip=True).upper() for th in rows[0].find_all(['th', 'td'])]
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
                    while key in results:
                        key = f"{key}_dup"
                    results[key] = {
                        'performance': src_perf,
                        'date': src_date,
                        'event': current_event
                    }

    return results


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {'processed': [], 'fixed': 0}


def save_progress(progress):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)


def fix_steeplechase():
    hinder_codes = [
        '3000mhinder', '2000mhinder', '1500mhinder',
        '1500mhinder_76_2cm', '2000mhinder_76_2cm', '2000mhinder_84cm',
        '2000mhinder_91_4cm', '3000mhinder_76_2cm', '3000mhinder_84cm',
        '3000mhinder_91_4cm', '1500mhinder_91_4cm'
    ]

    # Source uses "hinder" in the event name, so match on that
    event_names = ['hinder']

    events = supabase.table('events').select('id, code, name').in_(
        'code', hinder_codes
    ).execute()

    print(f"Fixing times for: {[e['name'] for e in events.data]}")

    progress = load_progress()
    processed_set = set(progress['processed'])
    fixed_count = progress['fixed']

    print(f"Resuming from: {len(processed_set)} already processed, {fixed_count} already fixed")

    all_athlete_ids = set()
    for event in events.data:
        print(f"Collecting athletes for {event['name']}...")
        offset = 0
        while True:
            results = supabase.table('results').select(
                'athlete_id'
            ).eq('event_id', event['id']).range(offset, offset + 999).execute()
            if not results.data:
                break
            for r in results.data:
                all_athlete_ids.add(r['athlete_id'])
            if len(results.data) < 1000:
                break
            offset += 1000

    remaining = [aid for aid in all_athlete_ids if aid not in processed_set]
    print(f"\nTotal athletes: {len(all_athlete_ids)}, Remaining: {len(remaining)}")

    processed_this_run = 0

    for i, athlete_id in enumerate(remaining):
        time_module.sleep(0.2)

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

        for event in events.data:
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

            # Use full event name for matching (e.g. "3000 meter hinder (76,2cm)")
            # to avoid confusing with regular 3000m results
            db_event_name = event['name']

            for r in db_results.data:
                db_perf = r['performance']
                db_date_short = parse_db_date(r['date'])
                if not db_date_short:
                    continue

                db_seconds = perf_to_total_seconds(db_perf)
                if db_seconds is None:
                    continue

                new_perf = None
                new_value = None

                # Match using full event name in the source key
                for key, src in source_results.items():
                    if db_event_name.lower() not in key.lower():
                        continue
                    if src['date'] == db_date_short:
                        parsed_perf, parsed_value = parse_source_time(src['performance'])
                        if parsed_perf:
                            src_seconds = parsed_value // 100
                            if src_seconds == db_seconds and parsed_perf != db_perf:
                                new_perf = parsed_perf
                                new_value = parsed_value
                                break

                # Fallback for invalid source dates
                if not new_perf:
                    for key, src in source_results.items():
                        if db_event_name.lower() not in key.lower():
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
                    needs_update = (new_perf != db_perf) or (r.get('performance_value') != new_value)

                    if needs_update and not DRY_RUN:
                        no_decimals = '.' not in new_perf
                        for upd_attempt in range(3):
                            try:
                                supabase.table('results').update({
                                    'performance': new_perf,
                                    'performance_value': new_value
                                }).eq('id', r['id']).execute()
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

        if processed_this_run % 50 == 0:
            progress = {'processed': list(processed_set), 'fixed': fixed_count}
            save_progress(progress)
            print(f"  Progress: {len(processed_set)}/{len(all_athlete_ids)} athletes, {fixed_count} fixed")

    progress = {'processed': list(processed_set), 'fixed': fixed_count}
    save_progress(progress)
    return fixed_count


if __name__ == '__main__':
    print("=" * 60)
    print("FIXING STEEPLECHASE TIMES")
    print("=" * 60)

    if DRY_RUN:
        print("*** DRY RUN ***\n")

    fixed = fix_steeplechase()

    print(f"\n{'='*60}")
    print(f"TOTAL: {fixed} times corrected")
    print("=" * 60)
