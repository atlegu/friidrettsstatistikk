"""
Import a single athlete from minfriidrettsstatistikk.info to Supabase.
Usage: python import_single_athlete.py <athlete_id>
"""

import os
import re
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BASE_URL = "https://www.minfriidrettsstatistikk.info/php"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) DataVerifier/1.0',
    'Content-Type': 'application/x-www-form-urlencoded'
})

# Event name mapping (scraped name -> database code)
EVENT_NAME_TO_CODE = {
    # Sprint
    '30 meter': '30m', '40 meter': '40m', '50 meter': '50m',
    '60 meter': '60m', '80 meter': '80m', '100 meter': '100m',
    '150 meter': '150m', '200 meter': '200m', '300 meter': '300m',
    '400 meter': '400m', '600 meter': '600m',
    # Middle/Long distance
    '800 meter': '800m', '1000 meter': '1000m', '1500 meter': '1500m',
    '2000 meter': '2000m', '3000 meter': '3000m', '5000 meter': '5000m',
    '10000 meter': '10000m', '1 engelsk mil': '1mile',
    # Jumps
    'Høyde': 'hoyde', 'Stav': 'stav', 'Lengde': 'lengde', 'Tresteg': 'tresteg',
    'Lengde uten tilløp': 'lengde_ut', 'Høyde uten tilløp': 'hoyde_ut',
    'Tresteg uten tilløp': 'tresteg_ut',
    # Throws
    'Kule 7,26kg': 'kule_7_26kg', 'Kule 6,0kg': 'kule_6kg', 'Kule 5,0kg': 'kule_5kg',
    'Kule 4,0kg': 'kule_4kg', 'Kule 3,0kg': 'kule_3kg', 'Kule 2,0kg': 'kule_2kg',
    'Diskos 2,0kg': 'diskos_2kg', 'Diskos 1,75kg': 'diskos_1_75kg',
    'Diskos 1,5kg': 'diskos_1_5kg', 'Diskos 1,0kg': 'diskos_1kg',
    'Spyd 800gram': 'spyd_800g', 'Spyd 700gram': 'spyd_700g',
    'Spyd 600gram': 'spyd_600g', 'Spyd 500gram': 'spyd_500g',
    'Slegge 7,26kg/121,5cm': 'slegge_7_26kg', 'Slegge 6,0kg/121,5cm': 'slegge_6kg',
    'Slegge 5,0kg/120cm': 'slegge_5kg', 'Slegge 4,0kg/120cm': 'slegge_4kg',
    # Combined events
    'Femkamp': '5kamp', 'Sjukamp': '7kamp', 'Tikamp': '10kamp',
}

# Add hurdle mappings dynamically
for dist in ['30', '40', '50', '60', '80', '100', '110', '200', '300', '400']:
    EVENT_NAME_TO_CODE[f'{dist} meter hekk'] = f'{dist}mh'
    for height in ['60cm', '68cm', '68,0cm', '76,2cm', '84cm', '84,0cm', '91,4cm', '100cm', '106,7cm']:
        h_code = height.replace(',', '_').replace('cm', 'cm').replace('.', '_')
        EVENT_NAME_TO_CODE[f'{dist} meter hekk ({height})'] = f'{dist}mh_{h_code}'

# Steeplechase
for dist in ['1500', '2000', '3000']:
    EVENT_NAME_TO_CODE[f'{dist} meter hinder'] = f'{dist}mhinder'
    for height in ['76,2cm', '84cm', '84,0cm', '91,4cm']:
        h_code = height.replace(',', '_').replace('cm', 'cm')
        EVENT_NAME_TO_CODE[f'{dist} meter hinder ({height})'] = f'{dist}mhinder_{h_code}'


def convert_time_format(time_str):
    """Convert old time format like '4.05.36' (4:05.36) to '4:05.36' format.

    Handles formats like:
    - '4.05.36' -> '4:05.36' (minutes.seconds.centiseconds)
    - '8.31.75' -> '8:31.75'
    - '15.08.80' -> '15:08.80'
    - '1.32.4' -> '1:32.40'
    - '2.03.5' -> '2:03.50'
    - '31.15.4' -> '31:15.40'
    """
    if not time_str:
        return time_str

    # Check if it matches the old format: digits.digits.digits
    # This pattern matches times like 4.05.36, 15.08.80, 1.32.4
    match = re.match(r'^(\d{1,2})\.(\d{2})\.(\d{1,2})$', time_str)
    if match:
        minutes = match.group(1)
        seconds = match.group(2)
        centiseconds = match.group(3)
        # Pad centiseconds to 2 digits if needed
        if len(centiseconds) == 1:
            centiseconds = centiseconds + '0'
        return f"{minutes}:{seconds}.{centiseconds}"

    # Also handle hour format like 2.03.5 which could be 2:03:50 for marathon
    # But more likely it's 2:03.50 for 800m etc
    match2 = re.match(r'^(\d{1,2})\.(\d{2})\.(\d)$', time_str)
    if match2:
        part1 = match2.group(1)
        part2 = match2.group(2)
        part3 = match2.group(3)
        return f"{part1}:{part2}.{part3}0"

    return time_str


def parse_result_with_wind(result_str):
    """Parse result with optional wind, e.g. '6,82(+1,3)' -> ('6.82', 1.3)"""
    if not result_str:
        return None, None
    result_str = result_str.strip()

    # Remove any trailing markers like (ok)
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

    # Replace comma with period
    result = result_str.replace(',', '.')

    # Convert old time format (4.05.36) to standard format (4:05.36)
    result = convert_time_format(result)

    return result, wind


def parse_date(date_str):
    """Parse date string to ISO format."""
    if not date_str:
        return None
    # Try common formats
    for fmt in ['%d.%m.%Y', '%d.%m.%y', '%Y-%m-%d']:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    return None


def fetch_athlete_data(athlete_id):
    """Fetch all results for an athlete."""
    url = f"{BASE_URL}/UtoverStatistikk.php"
    data = {'athlete': athlete_id, 'type': 'RES'}

    response = session.post(url, data=data, timeout=30)
    response.raise_for_status()
    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.text, 'lxml')

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
                birth_date = match.group(1)
            break

    # Get club (usually in an h3 after the name)
    club = None
    for h3 in soup.find_all('h3'):
        text = h3.get_text(strip=True)
        if not text.startswith('Født:') and not text.startswith('INNENDØRS') and not text.startswith('UTENDØRS'):
            # This might be the club or event name - check if it looks like a club
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
                    result_data = {
                        'event': current_event,
                        'indoor': current_indoor
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

                except Exception as e:
                    print(f"  Error parsing row: {e}")
                    continue

    return {
        'external_id': str(athlete_id),
        'name': name,
        'birth_date': birth_date,
        'club': club,
        'results': results
    }


def get_event_id(event_name):
    """Get event ID from database."""
    # Try direct mapping
    code = EVENT_NAME_TO_CODE.get(event_name)
    if code:
        result = supabase.table('events').select('id').eq('code', code).limit(1).execute()
        if result.data:
            return result.data[0]['id']

    # Try by name
    result = supabase.table('events').select('id').eq('name', event_name).limit(1).execute()
    if result.data:
        return result.data[0]['id']

    return None


def get_or_create_club(name):
    """Get or create a club."""
    if not name:
        return None
    result = supabase.table('clubs').select('id').eq('name', name).limit(1).execute()
    if result.data:
        return result.data[0]['id']
    # Create new
    result = supabase.table('clubs').insert({'name': name}).execute()
    if result.data:
        return result.data[0]['id']
    return None


def get_or_create_meet(name, date, city, indoor):
    """Get or create a meet."""
    if not name or not date:
        return None

    # Check existing
    result = supabase.table('meets').select('id').eq('name', name).eq('start_date', date).limit(1).execute()
    if result.data:
        return result.data[0]['id']

    # Create new
    meet_data = {
        'name': name,
        'start_date': date,
        'city': city or name,
        'indoor': indoor or False,
        'country': 'NOR'
    }
    result = supabase.table('meets').insert(meet_data).execute()
    if result.data:
        return result.data[0]['id']
    return None


def get_season_id(year, indoor):
    """Get season ID."""
    result = supabase.table('seasons').select('id').eq('year', year).eq('indoor', indoor or False).limit(1).execute()
    if result.data:
        return result.data[0]['id']
    return None


def import_athlete(athlete_id, gender='M'):
    """Import a single athlete with all their results."""
    print(f"\n{'='*60}")
    print(f"Importing athlete ID: {athlete_id}")
    print('='*60)

    # Fetch data from source
    data = fetch_athlete_data(athlete_id)
    if not data:
        print("Failed to fetch athlete data!")
        return

    print(f"Name: {data['name']}")
    print(f"Birth date: {data['birth_date']}")
    print(f"Club: {data['club']}")
    print(f"Total results: {len(data['results'])}")

    # Parse name
    name_parts = data['name'].split() if data['name'] else []
    first_name = name_parts[0] if name_parts else ''
    last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

    # Parse birth date
    birth_date_iso = None
    birth_year = None
    if data['birth_date']:
        birth_date_iso = parse_date(data['birth_date'])
        if birth_date_iso:
            birth_year = int(birth_date_iso[:4])

    # Get/create club
    club_id = get_or_create_club(data['club'])

    # Check if athlete exists
    existing = supabase.table('athletes').select('id').eq('external_id', data['external_id']).limit(1).execute()
    if existing.data:
        athlete_db_id = existing.data[0]['id']
        print(f"Athlete already exists with ID: {athlete_db_id}")
    else:
        # Create athlete
        athlete_data = {
            'first_name': first_name,
            'last_name': last_name,
            'gender': gender,
            'birth_date': birth_date_iso,
            'birth_year': birth_year,
            'current_club_id': club_id,
            'external_id': data['external_id'],
            'nationality': 'NOR'
        }
        result = supabase.table('athletes').insert(athlete_data).execute()
        if not result.data:
            print("Failed to create athlete!")
            return
        athlete_db_id = result.data[0]['id']
        print(f"Created athlete with ID: {athlete_db_id}")

    # Import results
    imported = 0
    skipped_event = 0
    skipped_dup = 0
    unmapped_events = set()

    for r in data['results']:
        event_id = get_event_id(r['event'])
        if not event_id:
            unmapped_events.add(r['event'])
            skipped_event += 1
            continue

        date_iso = parse_date(r.get('date'))
        if not date_iso:
            continue

        year = r.get('year') or (int(date_iso[:4]) if date_iso else None)
        indoor = r.get('indoor', False)

        # Check for duplicate
        dup_check = supabase.table('results').select('id').eq('athlete_id', athlete_db_id).eq('event_id', event_id).eq('date', date_iso).eq('performance', r['performance']).limit(1).execute()
        if dup_check.data:
            skipped_dup += 1
            continue

        # Get/create meet
        meet_id = get_or_create_meet(
            name=r.get('meet_name') or r.get('venue', ''),
            date=date_iso,
            city=r.get('venue', ''),
            indoor=indoor
        )

        # Get season
        season_id = get_season_id(year, indoor) if year else None

        # Get club for this result
        result_club_id = get_or_create_club(r.get('club')) or club_id

        # Create result
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
            supabase.table('results').insert(result_data).execute()
            imported += 1
        except Exception as e:
            print(f"  Error inserting result: {e}")

    print(f"\nImport summary:")
    print(f"  Imported: {imported}")
    print(f"  Skipped (no event mapping): {skipped_event}")
    print(f"  Skipped (duplicate): {skipped_dup}")

    if unmapped_events:
        print(f"\nUnmapped events:")
        for e in sorted(unmapped_events):
            print(f"  - {e}")

    return athlete_db_id


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python import_single_athlete.py <athlete_id> [gender]")
        print("Example: python import_single_athlete.py 90 M")
        sys.exit(1)

    athlete_id = int(sys.argv[1])
    gender = sys.argv[2] if len(sys.argv) > 2 else 'M'

    import_athlete(athlete_id, gender)
