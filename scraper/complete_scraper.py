#!/usr/bin/env python3
"""
Complete scraper for minfriidrettsstatistikk.info
Scrapes ALL athletes and ALL their results.
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import requests
from bs4 import BeautifulSoup
import re
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from supabase import create_client
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()

# Configuration
BASE_URL = "https://www.minfriidrettsstatistikk.info/php"
REQUEST_DELAY = 1.5  # seconds between requests
MAX_WORKERS = 1  # single thread to minimize server load
BATCH_SIZE = 100  # results to insert at once
MAX_RETRIES = 5  # retry failed requests
RETRY_DELAY = 10  # base delay for retries (exponential backoff)

# Supabase client
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

# Session for requests
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) NorwegianAthleticsStats/1.0',
    'Content-Type': 'application/x-www-form-urlencoded'
})

# Norwegian letters for athlete search
LETTERS = list('ABCDEFGHIJKLMNOPQRSTUVWXYZÆØÅ')


def parse_date(date_str):
    """Convert DD.MM.YY to YYYY-MM-DD."""
    if not date_str or not date_str.strip():
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


def parse_birth_date(date_str):
    """Convert DD.MM.YYYY to YYYY-MM-DD."""
    if not date_str or not date_str.strip():
        return None
    try:
        parts = date_str.strip().split('.')
        if len(parts) == 3:
            day, month, year = parts
            return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
    except Exception:
        pass
    return None


def parse_result_with_wind(result_str):
    """Parse result with optional wind, e.g. '10,54(+2,7)' -> ('10.54', 2.7)"""
    if not result_str:
        return None, None

    result_str = result_str.strip()

    # Extract wind from parentheses
    wind_match = re.search(r'\(([\+\-]?\d+[,\.]\d+)\)', result_str)
    wind = None
    if wind_match:
        wind_str = wind_match.group(1).replace(',', '.')
        try:
            wind = float(wind_str)
        except ValueError:
            pass
        result_str = re.sub(r'\s*\([^\)]+\)', '', result_str).strip()

    # Normalize decimal separator
    result = result_str.replace(',', '.')
    return result, wind


def is_manual_time(performance):
    """Check if performance is a manual time (1 decimal for times)."""
    if not performance or '.' not in str(performance):
        return False
    # Only applies to time-based results (contains seconds)
    if ':' in str(performance):
        # Format like 2:45.8 - check decimals after last dot
        parts = str(performance).split('.')
        if len(parts) == 2:
            return len(parts[1]) == 1
    else:
        # Format like 10.5 or 10.54
        parts = str(performance).split('.')
        if len(parts) == 2:
            return len(parts[1]) == 1
    return False


def performance_to_value(performance, event_name):
    """Convert performance string to numeric value for sorting."""
    if not performance:
        return None

    try:
        perf = str(performance).strip()

        # Time format: MM:SS.xx or H:MM:SS.xx
        if ':' in perf:
            parts = perf.split(':')
            if len(parts) == 2:
                minutes, seconds = parts
                return int(float(minutes) * 60000 + float(seconds) * 1000)
            elif len(parts) == 3:
                hours, minutes, seconds = parts
                return int(float(hours) * 3600000 + float(minutes) * 60000 + float(seconds) * 1000)

        # Points (mangekamp) - just the number
        if event_name and ('kamp' in event_name.lower()):
            return int(float(perf))

        # Distance/height: convert to mm (e.g., 6.82 -> 6820)
        if '.' in perf:
            return int(float(perf) * 1000)

        # Integer value
        return int(perf) * 1000

    except (ValueError, TypeError):
        return None


def fetch_with_retry(url, data, description="request"):
    """Fetch with exponential backoff retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            time.sleep(REQUEST_DELAY)
            response = session.post(url, data=data, timeout=60)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response
        except requests.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAY * (2 ** attempt)  # Exponential backoff: 5, 10, 20 seconds
                print(f"  Retry {attempt + 1}/{MAX_RETRIES} for {description} after {delay}s delay...")
                time.sleep(delay)
            else:
                print(f"  Failed {description} after {MAX_RETRIES} attempts: {e}")
                return None
    return None


def fetch_athletes_for_letter(letter):
    """Fetch all athletes starting with a letter."""
    url = f"{BASE_URL}/UtoverSok.php"
    data = {
        'cmd': 'SearchAthlete',
        'showchar': letter
    }

    response = fetch_with_retry(url, data, f"athletes for {letter}")
    if not response:
        return []

    soup = BeautifulSoup(response.text, 'lxml')
    athletes = []

    # Find all athlete links with href containing showathl=XXXXX
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        match = re.search(r'showathl=(\d+)', href)
        if match:
            external_id = int(match.group(1))
            name = link.get_text(strip=True)
            athletes.append({
                'external_id': external_id,
                'name': name
            })

    return athletes


def fetch_athlete_results(external_id):
    """Fetch ALL results for an athlete using type=RES."""
    url = f"{BASE_URL}/UtoverStatistikk.php"
    data = {
        'athlete': external_id,
        'type': 'RES'
    }

    response = fetch_with_retry(url, data, f"athlete {external_id}")
    if not response:
        return None

    soup = BeautifulSoup(response.text, 'lxml')

    # Get athlete info
    name = None
    name_elem = soup.find('h2')
    if name_elem:
        name = name_elem.get_text(strip=True)

    birth_date = None
    gender = None
    for h3 in soup.find_all('h3'):
        text = h3.get_text(strip=True)
        if text.startswith('Født:'):
            match = re.search(r'(\d{2}\.\d{2}\.\d{4})', text)
            if match:
                birth_date = parse_birth_date(match.group(1))
        # Gender might be inferred from class names later

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

            # Get headers
            header_row = rows[0]
            headers = [th.get_text(strip=True).upper() for th in header_row.find_all(['th', 'td'])]

            if 'RESULTAT' not in headers:
                continue

            # Process result rows
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) < 3:
                    continue

                try:
                    result_data = {
                        'event_name': current_event,
                        'indoor': current_indoor,
                        'status': 'OK'
                    }

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
                            result_data['date'] = parse_date(text)
                        elif header == 'STED':
                            # Venue from title, meet name from text
                            title = cell.get('title', '')
                            result_data['venue'] = title if title else text
                            result_data['meet_name'] = text
                        elif header == 'KLUBB':
                            result_data['club_name'] = text
                        elif header == 'PL' or header == 'PLASSERING':
                            try:
                                result_data['place'] = int(text) if text.isdigit() else None
                            except:
                                result_data['place'] = None
                        elif header == 'ÅR':
                            year_match = re.match(r'(\d{4})', text)
                            if year_match:
                                result_data['year'] = int(year_match.group(1))
                            age_match = re.search(r'\((\d+)\)', text)
                            if age_match:
                                result_data['age'] = int(age_match.group(1))
                        elif header == 'ÅRSAK':
                            if text:
                                result_data['status'] = text
                                # Mark wind-assisted specifically
                                if 'vind' in text.lower():
                                    result_data['wind_rejected'] = True

                    if result_data.get('performance'):
                        results.append(result_data)

                except Exception as e:
                    continue

    return {
        'external_id': external_id,
        'name': name,
        'birth_date': birth_date,
        'results': results
    }


# Cache for lookups
event_cache = {}
club_cache = {}
season_cache = {}
athlete_cache = {}
meet_cache = {}  # key: (date, venue/meet_name) -> meet_id


def generate_event_code(event_name):
    """Generate a short code from event name."""
    name = event_name.lower()

    # Replace common patterns
    code = name
    code = re.sub(r'meter', 'm', code)
    code = re.sub(r'hekk', 'h', code)
    code = re.sub(r'stafett', 'staf', code)
    code = re.sub(r'kamp', 'k', code)
    code = re.sub(r'\s+', '_', code)
    code = re.sub(r'[(),]', '', code)

    # Truncate to 50 chars
    return code[:50]


def determine_event_category(event_name):
    """Determine the category for an event based on its name."""
    name_lower = event_name.lower()

    # Sprints (up to 400m)
    if any(x in name_lower for x in ['60 m', '100 m', '200 m', '400 m']) and 'hekk' not in name_lower and 'hinder' not in name_lower:
        if '400' in name_lower:
            return 'sprint'  # or could be short_distance
        return 'sprint'

    # Middle distance (800m - 1500m)
    if any(x in name_lower for x in ['800', '1500', 'mil']):
        return 'middle_distance'

    # Long distance (3000m+)
    if any(x in name_lower for x in ['3000', '5000', '10000', '10 km', 'halvmaraton', 'maraton']):
        return 'long_distance'

    # Hurdles
    if 'hekk' in name_lower:
        return 'hurdles'

    # Steeplechase
    if 'hinder' in name_lower:
        return 'steeplechase'

    # Jumps
    if any(x in name_lower for x in ['høyde', 'stav', 'lengde', 'tresteg']):
        return 'jumps'

    # Throws
    if any(x in name_lower for x in ['kule', 'diskos', 'spyd', 'slegge', 'vekt']):
        return 'throws'

    # Combined events
    if 'kamp' in name_lower:
        return 'combined'

    # Relays
    if 'stafett' in name_lower:
        return 'relays'

    # Walking
    if 'kapp' in name_lower and 'gang' in name_lower:
        return 'walking'

    # Default to other
    return 'other'


def get_or_create_event(event_name):
    """Get event ID, create if needed."""
    if event_name in event_cache:
        return event_cache[event_name]

    # Try to find existing
    result = supabase.table('events').select('id').eq('name', event_name).execute()
    if result.data:
        event_cache[event_name] = result.data[0]['id']
        return event_cache[event_name]

    # Create new event
    event_id = str(uuid.uuid4())

    # Determine result type and other attributes
    result_type = 'time'  # default
    name_lower = event_name.lower()
    wind_measured = False

    if any(x in name_lower for x in ['kule', 'diskos', 'spyd', 'slegge', 'vekt']):
        result_type = 'distance'
    elif any(x in name_lower for x in ['høyde', 'stav']):
        result_type = 'distance'
    elif any(x in name_lower for x in ['lengde', 'tresteg']):
        result_type = 'distance'
        wind_measured = True
    elif 'kamp' in name_lower:
        result_type = 'points'
    elif any(x in name_lower for x in ['60', '100', '200']) and 'hekk' not in name_lower:
        wind_measured = True
    elif 'hekk' in name_lower and any(x in name_lower for x in ['60', '100', '110']):
        wind_measured = True

    code = generate_event_code(event_name)
    category = determine_event_category(event_name)

    new_event = {
        'id': event_id,
        'code': code,
        'name': event_name,
        'category': category,
        'result_type': result_type,
        'wind_measured': wind_measured,
        'indoor': False,
    }

    try:
        supabase.table('events').insert(new_event).execute()
        event_cache[event_name] = event_id
        return event_id
    except Exception as e:
        # Might have been created by another thread, or duplicate code
        result = supabase.table('events').select('id').eq('name', event_name).execute()
        if result.data:
            event_cache[event_name] = result.data[0]['id']
            return event_cache[event_name]

        # If name not found, might be duplicate code - try finding by code
        result = supabase.table('events').select('id').eq('code', code).execute()
        if result.data:
            # Use existing event with same code (similar event type)
            event_cache[event_name] = result.data[0]['id']
            return event_cache[event_name]
        raise


def get_or_create_club(club_name):
    """Get club ID, create if needed."""
    if not club_name:
        return None

    if club_name in club_cache:
        return club_cache[club_name]

    result = supabase.table('clubs').select('id').eq('name', club_name).execute()
    if result.data:
        club_cache[club_name] = result.data[0]['id']
        return club_cache[club_name]

    club_id = str(uuid.uuid4())
    new_club = {
        'id': club_id,
        'name': club_name,
        'country': 'NOR'
    }

    try:
        supabase.table('clubs').insert(new_club).execute()
        club_cache[club_name] = club_id
        return club_id
    except Exception:
        result = supabase.table('clubs').select('id').eq('name', club_name).execute()
        if result.data:
            club_cache[club_name] = result.data[0]['id']
            return club_cache[club_name]
        return None


def get_or_create_meet(date, venue, meet_name, indoor, season_id):
    """Get or create a meet for the given date/venue."""
    if not date:
        date = '1900-01-01'  # Fallback date

    # Create a key based on date and venue/name
    key = (date, venue or meet_name or 'Unknown')

    if key in meet_cache:
        return meet_cache[key]

    # Try to find existing meet by date and name/venue
    try:
        query = supabase.table('meets').select('id').eq('start_date', date)
        if venue:
            query = query.or_(f"city.ilike.%{venue}%,name.ilike.%{venue}%")
        elif meet_name:
            query = query.ilike('name', f'%{meet_name}%')

        existing = query.limit(1).execute()
        if existing.data:
            meet_cache[key] = existing.data[0]['id']
            return meet_cache[key]
    except:
        pass

    # Create new meet
    meet_id = str(uuid.uuid4())
    display_name = meet_name or venue or 'Ukjent stevne'

    new_meet = {
        'id': meet_id,
        'name': display_name[:200],  # Truncate if too long
        'city': (venue or '')[:100],
        'country': 'NOR',
        'start_date': date,
        'indoor': indoor or False,
        'season_id': season_id,
        'level': 'local',
    }

    try:
        supabase.table('meets').insert(new_meet).execute()
        meet_cache[key] = meet_id
        return meet_id
    except Exception as e:
        # Try to find again (might have been created by another thread)
        try:
            existing = supabase.table('meets').select('id').eq('start_date', date).limit(1).execute()
            if existing.data:
                meet_cache[key] = existing.data[0]['id']
                return meet_cache[key]
        except:
            pass

        # Last resort - create with unique name
        new_meet['name'] = f"{display_name[:150]} ({date})"
        try:
            supabase.table('meets').insert(new_meet).execute()
            meet_cache[key] = meet_id
            return meet_id
        except:
            pass

    return None


def get_or_create_season(year, indoor):
    """Get season ID, create if needed."""
    if not year:
        return None

    key = (year, indoor)
    if key in season_cache:
        return season_cache[key]

    result = supabase.table('seasons').select('id').eq('year', year).eq('indoor', indoor or False).execute()
    if result.data:
        season_cache[key] = result.data[0]['id']
        return season_cache[key]

    season_id = str(uuid.uuid4())
    new_season = {
        'id': season_id,
        'year': year,
        'indoor': indoor or False,
        'name': f"{'Inne' if indoor else 'Ute'} {year}"
    }

    try:
        supabase.table('seasons').insert(new_season).execute()
        season_cache[key] = season_id
        return season_id
    except Exception:
        result = supabase.table('seasons').select('id').eq('year', year).eq('indoor', indoor or False).execute()
        if result.data:
            season_cache[key] = result.data[0]['id']
            return season_cache[key]
        return None


def get_or_create_athlete(external_id, name, birth_date, gender=None):
    """Get athlete ID, create if needed. Update birth_date if we have better info."""
    if external_id in athlete_cache:
        return athlete_cache[external_id]

    result = supabase.table('athletes').select('id, birth_date').eq('external_id', external_id).execute()
    if result.data:
        athlete_id = result.data[0]['id']
        athlete_cache[external_id] = athlete_id

        # Update birth_date if we have it and it's missing in DB
        if birth_date and not result.data[0].get('birth_date'):
            try:
                supabase.table('athletes').update({'birth_date': birth_date}).eq('id', athlete_id).execute()
            except:
                pass

        return athlete_id

    # Parse name into first/last
    name_parts = name.split() if name else ['Unknown']
    first_name = name_parts[0] if name_parts else 'Unknown'
    last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

    athlete_id = str(uuid.uuid4())
    new_athlete = {
        'id': athlete_id,
        'external_id': external_id,
        'first_name': first_name,
        'last_name': last_name,
        'birth_date': birth_date,
        'gender': gender,
        'country': 'NOR'
    }

    try:
        supabase.table('athletes').insert(new_athlete).execute()
        athlete_cache[external_id] = athlete_id
        return athlete_id
    except Exception:
        result = supabase.table('athletes').select('id').eq('external_id', external_id).execute()
        if result.data:
            athlete_cache[external_id] = result.data[0]['id']
            return athlete_cache[external_id]
        raise


def process_athlete(athlete_info):
    """Process a single athlete: fetch and store all results."""
    external_id = athlete_info['external_id']

    data = fetch_athlete_results(external_id)
    if not data:
        return {'external_id': external_id, 'results': 0, 'error': 'fetch_failed', 'no_results': False}

    if not data['results']:
        # Athlete exists but has no results - not an error
        return {'external_id': external_id, 'results': 0, 'error': None, 'no_results': True}

    try:
        athlete_id = get_or_create_athlete(
            external_id,
            data['name'],
            data['birth_date']
        )

        results_to_insert = []

        for r in data['results']:
            event_id = get_or_create_event(r['event_name'])
            club_id = get_or_create_club(r.get('club_name'))

            year = r.get('year')
            if not year and r.get('date'):
                try:
                    year = int(r['date'].split('-')[0])
                except:
                    year = None

            season_id = get_or_create_season(year, r.get('indoor'))

            # Get or create meet for this result
            meet_id = get_or_create_meet(
                r.get('date'),
                r.get('venue'),
                r.get('meet_name'),
                r.get('indoor'),
                season_id
            )

            if not meet_id:
                continue  # Skip if we can't create a meet

            perf_value = performance_to_value(r['performance'], r['event_name'])

            # Status handling - map to valid enum values: OK, DNS, DNF, DQ, NM
            status = 'OK'
            if r.get('status') and r.get('status') != 'OK':
                reason = r.get('status', '').lower()
                if 'dns' in reason or 'ikke møtt' in reason:
                    status = 'DNS'
                elif 'dnf' in reason or 'ikke fullført' in reason:
                    status = 'DNF'
                elif 'dq' in reason or 'diskvalifisert' in reason:
                    status = 'DQ'
                elif 'nm' in reason or 'ingen høyde' in reason:
                    status = 'NM'
                # Wind-assisted results are still valid performances, just use OK
                # The wind field will indicate if it's wind-assisted (>2.0 m/s)

            result = {
                'id': str(uuid.uuid4()),
                'athlete_id': athlete_id,
                'event_id': event_id,
                'club_id': club_id,
                'season_id': season_id,
                'meet_id': meet_id,
                'performance': r['performance'],
                'performance_value': perf_value,
                'wind': r.get('wind'),
                'date': r.get('date'),
                'place': r.get('place'),
                'status': status,
                'verified': True,
            }

            results_to_insert.append(result)

        # Insert in batches
        for i in range(0, len(results_to_insert), BATCH_SIZE):
            batch = results_to_insert[i:i+BATCH_SIZE]
            try:
                supabase.table('results').insert(batch).execute()
            except Exception as e:
                # Try one by one on error
                for res in batch:
                    try:
                        supabase.table('results').insert(res).execute()
                    except:
                        pass

        return {'external_id': external_id, 'results': len(results_to_insert), 'error': None, 'no_results': False}

    except Exception as e:
        return {'external_id': external_id, 'results': 0, 'error': str(e), 'no_results': False}


def scrape_letter(letter):
    """Scrape all athletes for a given letter."""
    print(f"\n{'='*60}")
    print(f"Processing letter: {letter}")
    print('='*60)

    athletes = fetch_athletes_for_letter(letter)
    print(f"Found {len(athletes)} athletes for letter {letter}")

    if not athletes:
        return {'athletes': 0, 'results': 0, 'errors': 0, 'no_results': 0}

    total_results = 0
    errors = 0
    no_results = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_athlete, a): a for a in athletes}

        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            total_results += result['results']
            if result['error']:
                errors += 1
            if result.get('no_results'):
                no_results += 1

            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(athletes)} athletes, {total_results} results so far")

    print(f"Letter {letter}: {len(athletes)} athletes, {total_results} results, {no_results} without results, {errors} errors")
    return {'athletes': len(athletes), 'results': total_results, 'errors': errors, 'no_results': no_results}


def delete_batch(ids):
    """Delete a batch of results by IDs."""
    try:
        supabase.table('results').delete().in_('id', ids).execute()
        return len(ids)
    except Exception:
        # Fall back to individual deletes
        deleted = 0
        for id in ids:
            try:
                supabase.table('results').delete().eq('id', id).execute()
                deleted += 1
            except:
                pass
        return deleted


def clear_results():
    """Clear all results from the database using parallel deletion."""
    print("Clearing all results...")

    # Count first
    count = supabase.table('results').select('id', count='exact').execute()
    total = count.count
    print(f"Found {total} results to delete")

    if total == 0:
        print("No results to delete")
        return

    deleted = 0
    fetch_batch = 1000  # Fetch this many at a time
    delete_batch_size = 50  # Delete in batches of 50 (safe for URL length)

    while deleted < total:
        # Fetch a chunk of IDs
        results = supabase.table('results').select('id').limit(fetch_batch).execute()
        if not results.data:
            break

        ids = [r['id'] for r in results.data]

        # Split into smaller batches and delete in parallel
        batches = [ids[i:i+delete_batch_size] for i in range(0, len(ids), delete_batch_size)]

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(delete_batch, batch) for batch in batches]
            for future in as_completed(futures):
                deleted += future.result()

        if deleted % 10000 == 0 or deleted >= total:
            print(f"  Deleted {deleted} / {total} results...")

    print(f"Deleted {deleted} results total")


def recover_athletes():
    """Re-scrape athletes that exist but have no results."""
    print("Finding athletes without results...")

    # Get athletes with results
    athletes_with_results = set()
    offset = 0
    while True:
        resp = supabase.table('results').select('athlete_id').range(offset, offset + 999).execute()
        if not resp.data:
            break
        for r in resp.data:
            athletes_with_results.add(r['athlete_id'])
        offset += 1000
        if offset % 10000 == 0:
            print(f"  Checked {offset} results...")

    print(f"Found {len(athletes_with_results)} athletes with results")

    # Get all athletes
    all_athletes = []
    offset = 0
    while True:
        resp = supabase.table('athletes').select('id, external_id, first_name, last_name').range(offset, offset + 999).execute()
        if not resp.data:
            break
        all_athletes.extend(resp.data)
        offset += 1000

    print(f"Found {len(all_athletes)} total athletes")

    # Find athletes without results
    athletes_to_scrape = []
    for a in all_athletes:
        if a['id'] not in athletes_with_results and a.get('external_id'):
            athletes_to_scrape.append({
                'external_id': a['external_id'],
                'name': f"{a['first_name']} {a['last_name']}"
            })

    print(f"Found {len(athletes_to_scrape)} athletes without results to re-scrape")

    if not athletes_to_scrape:
        print("Nothing to recover!")
        return

    # Process sequentially in batches (to avoid overwhelming the server)
    total_results = 0
    errors = 0
    no_results = 0
    batch_size = 100  # Process and report every 100 athletes

    print(f"Processing {len(athletes_to_scrape)} athletes sequentially...")

    for i, athlete in enumerate(athletes_to_scrape):
        try:
            result = process_athlete(athlete)
            total_results += result['results']
            if result['error']:
                errors += 1
            if result.get('no_results'):
                no_results += 1
        except Exception as e:
            print(f"  Exception processing athlete {athlete['external_id']}: {e}")
            errors += 1

        if (i + 1) % batch_size == 0:
            print(f"Progress: {i + 1}/{len(athletes_to_scrape)} athletes, {total_results} results, {errors} errors, {no_results} without results")
            sys.stdout.flush()

    print(f"\nRecovery complete!")
    print(f"Athletes processed: {len(athletes_to_scrape)}")
    print(f"Results imported: {total_results}")
    print(f"Athletes without results: {no_results}")
    print(f"Errors: {errors}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Complete scraper for Norwegian athletics')
    parser.add_argument('command', choices=['scrape', 'clear', 'test', 'status', 'recover'],
                        help='Command to run')
    parser.add_argument('letters', nargs='*', default=LETTERS,
                        help='Letters to scrape (default: all)')

    args = parser.parse_args()

    if args.command == 'clear':
        clear_results()

    elif args.command == 'recover':
        recover_athletes()

    elif args.command == 'status':
        results = supabase.table('results').select('id', count='exact').execute()
        athletes = supabase.table('athletes').select('id', count='exact').execute()
        events = supabase.table('events').select('id', count='exact').execute()
        print(f"Results: {results.count}")
        print(f"Athletes: {athletes.count}")
        print(f"Events: {events.count}")

    elif args.command == 'test':
        # Test with letter Å (smallest)
        print("Testing with letter Å...")
        scrape_letter('Å')

    elif args.command == 'scrape':
        letters = args.letters if args.letters != LETTERS else LETTERS
        print(f"Scraping letters: {letters}")

        start_time = time.time()

        total_athletes = 0
        total_results = 0
        total_errors = 0
        total_no_results = 0

        for letter in letters:
            stats = scrape_letter(letter)
            if stats:
                total_athletes += stats['athletes']
                total_results += stats['results']
                total_errors += stats['errors']
                total_no_results += stats['no_results']

        elapsed = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"SCRAPING COMPLETE")
        print(f"{'='*60}")
        print(f"Total time: {elapsed/60:.1f} minutes")
        print(f"Athletes processed: {total_athletes}")
        print(f"Results imported: {total_results}")
        print(f"Athletes without results: {total_no_results}")
        print(f"Errors: {total_errors}")

        # Final status
        results = supabase.table('results').select('id', count='exact').execute()
        print(f"\nTotal results in database: {results.count}")


if __name__ == '__main__':
    main()
