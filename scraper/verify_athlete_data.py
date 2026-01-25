"""
Verify athlete data by comparing source (minfriidrettsstatistikk.info) with database.
Identifies missing results and data quality issues.
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

BASE_URL = "https://www.minfriidrettsstatistikk.info/php"
REQUEST_DELAY = 0.5

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) DataVerifier/1.0'
})

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))


def parse_date(date_str):
    """Convert date from DD.MM.YY to YYYY-MM-DD."""
    if not date_str or date_str.strip() == '':
        return None
    try:
        date_str = date_str.strip()
        parts = date_str.split('.')
        if len(parts) == 3:
            day, month, year = parts
            year = int(year)
            if year < 100:
                year = 2000 + year if year < 50 else 1900 + year
            return f"{year:04d}-{int(month):02d}-{int(day):02d}"
    except Exception:
        pass
    return None


def parse_result_with_wind(result_str):
    """Parse result with optional wind, e.g. '6,82(+1,3)' -> ('6.82', 1.3)"""
    if not result_str:
        return None, None

    result_str = result_str.strip()

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
    return result, wind


def fetch_athlete_from_source(external_id):
    """Fetch athlete's best results from source website."""
    url = f"{BASE_URL}/UtoverStatistikk.php"
    params = {
        'showathl': external_id,
        'showevent': 0,
        'showseason': 0,
        'outdoor': 'A',  # Both indoor and outdoor
        'listtype': 'All'
    }

    time.sleep(REQUEST_DELAY)
    try:
        response = session.get(url, params=params, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        html = response.text
    except requests.RequestException as e:
        print(f"Error fetching athlete {external_id}: {e}")
        return None

    soup = BeautifulSoup(html, 'lxml')

    # Get athlete name
    name = None
    name_elem = soup.find('h2')
    if name_elem:
        name = name_elem.get_text(strip=True)

    # Get birth date
    birth_date = None
    for h3 in soup.find_all('h3'):
        text = h3.get_text(strip=True)
        if text.startswith('Født:'):
            match = re.search(r'(\d{2}\.\d{2}\.\d{4})', text)
            if match:
                birth_date = parse_date(match.group(1))
            break

    results = []
    current_indoor = False
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

            # Find header row
            header_row = rows[0]
            headers = [th.get_text(strip=True).upper() for th in header_row.find_all(['th', 'td'])]

            if 'RESULTAT' not in headers:
                continue

            # This is a "best results" table - usually only 1-2 rows
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) < 4:
                    continue

                try:
                    # Find result column
                    result_idx = headers.index('RESULTAT') if 'RESULTAT' in headers else 0
                    result_str = cols[result_idx].get_text(strip=True) if result_idx < len(cols) else ''
                    performance, wind = parse_result_with_wind(result_str)

                    if not performance:
                        continue

                    # Find date column
                    date_idx = headers.index('DATO') if 'DATO' in headers else None
                    date = None
                    if date_idx is not None and date_idx < len(cols):
                        date = parse_date(cols[date_idx].get_text(strip=True))

                    # Find meet/location column
                    location_idx = headers.index('STED') if 'STED' in headers else None
                    meet_name = None
                    if location_idx is not None and location_idx < len(cols):
                        meet_name = cols[location_idx].get_text(strip=True)

                    results.append({
                        'event': current_event,
                        'performance': performance,
                        'wind': wind,
                        'date': date,
                        'meet': meet_name,
                        'indoor': current_indoor,
                        'wind_assisted': wind is not None and wind > 2.0
                    })

                except Exception as e:
                    continue

    return {
        'external_id': external_id,
        'name': name,
        'birth_date': birth_date,
        'results': results
    }


def get_athlete_from_db(athlete_id):
    """Get athlete's results from database."""
    results = supabase.table('results_full').select(
        'event_name, performance, wind, date, meet_name'
    ).eq('athlete_id', athlete_id).execute()

    return results.data


def find_athlete_in_db(name=None, external_id=None):
    """Find athlete in database by name or external ID."""
    if external_id:
        # Check if we have external_id mapping
        athletes = supabase.table('athletes').select('id, first_name, last_name, external_id').eq('external_id', external_id).execute()
        if athletes.data:
            return athletes.data[0]

    if name:
        # Search by name in results_full
        results = supabase.table('results_full').select('athlete_id, athlete_name').ilike('athlete_name', f'%{name}%').limit(1).execute()
        if results.data:
            return {'id': results.data[0]['athlete_id'], 'name': results.data[0]['athlete_name']}

    return None


def normalize_event_name(event_name):
    """Normalize event name for comparison."""
    if not event_name:
        return ''

    name = event_name.lower().strip()

    # Common replacements
    name = name.replace('meter', 'm')
    name = name.replace(' m ', 'm ')
    name = re.sub(r'\s+', ' ', name)

    return name


def compare_results(source_results, db_results):
    """Compare source results with database results."""
    missing = []
    wind_issues = []

    # Create lookup of DB results by normalized event name
    db_by_event = {}
    for r in db_results:
        event = normalize_event_name(r.get('event_name', ''))
        if event not in db_by_event:
            db_by_event[event] = []
        db_by_event[event].append(r)

    for src in source_results:
        src_event = normalize_event_name(src['event'])
        src_perf = src['performance']

        # Find matching event in DB
        matched = False
        for db_event, db_results_for_event in db_by_event.items():
            # Fuzzy match event names
            if src_event in db_event or db_event in src_event:
                for db_r in db_results_for_event:
                    if db_r['performance'] == src_perf:
                        matched = True

                        # Check wind
                        if src.get('wind_assisted') and db_r.get('wind') is not None and db_r['wind'] > 2.0:
                            wind_issues.append({
                                'event': src['event'],
                                'performance': src_perf,
                                'wind': src['wind'],
                                'issue': 'Wind-assisted result should not be PB/record eligible'
                            })
                        break
                if matched:
                    break

        if not matched:
            missing.append({
                'event': src['event'],
                'performance': src_perf,
                'wind': src.get('wind'),
                'date': src.get('date'),
                'meet': src.get('meet')
            })

    return missing, wind_issues


def verify_athlete(external_id=None, name=None):
    """Verify a single athlete's data."""
    print(f"\n{'='*60}")
    print(f"Verifying athlete: {name or external_id}")
    print('='*60)

    # Fetch from source
    if external_id:
        source_data = fetch_athlete_from_source(external_id)
    else:
        print("Need external_id to fetch from source")
        return

    if not source_data:
        print("Could not fetch athlete from source")
        return

    print(f"Source: {source_data['name']}")
    print(f"Birth date: {source_data['birth_date']}")
    print(f"Results in source: {len(source_data['results'])}")

    # Find in database
    db_athlete = find_athlete_in_db(name=source_data['name'])

    if not db_athlete:
        print("ATHLETE NOT FOUND IN DATABASE!")
        return

    print(f"DB athlete ID: {db_athlete.get('id')}")

    # Get DB results
    db_results = get_athlete_from_db(db_athlete['id'])
    print(f"Results in database: {len(db_results)}")

    # Compare
    missing, wind_issues = compare_results(source_data['results'], db_results)

    print(f"\n--- MISSING RESULTS ({len(missing)}) ---")
    for m in missing:
        wind_str = f" ({m['wind']:+.1f})" if m.get('wind') else ""
        print(f"  {m['event']}: {m['performance']}{wind_str} - {m.get('meet', 'Unknown')} ({m.get('date', 'Unknown')})")

    print(f"\n--- WIND ISSUES ({len(wind_issues)}) ---")
    for w in wind_issues:
        print(f"  {w['event']}: {w['performance']} (wind: {w['wind']:+.1f}) - {w['issue']}")

    return {
        'name': source_data['name'],
        'source_count': len(source_data['results']),
        'db_count': len(db_results),
        'missing': missing,
        'wind_issues': wind_issues
    }


def verify_random_athletes(count=10):
    """Verify a random sample of athletes."""
    # Get random athletes from database
    athletes = supabase.table('athletes').select('id, first_name, last_name, external_id').not_.is_('external_id', 'null').limit(count).execute()

    results = []
    for athlete in athletes.data:
        if athlete.get('external_id'):
            result = verify_athlete(external_id=athlete['external_id'])
            if result:
                results.append(result)

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    total_missing = sum(len(r['missing']) for r in results)
    total_wind_issues = sum(len(r['wind_issues']) for r in results)

    print(f"Athletes verified: {len(results)}")
    print(f"Total missing results: {total_missing}")
    print(f"Total wind issues: {total_wind_issues}")

    return results


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        # Verify specific athlete by external ID
        external_id = int(sys.argv[1])
        verify_athlete(external_id=external_id)
    else:
        # Verify Karsten Warholm and Atle Guttormsen as examples
        print("Verifying known athletes with issues...")
        verify_athlete(external_id=1172)  # Karsten Warholm
        verify_athlete(external_id=12318)  # Atle Guttormsen
