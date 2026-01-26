"""
Import scraped results from CSV into Supabase database.
Handles matching/creating athletes, clubs, meets, and events.
"""

import csv
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Event name mapping (from scraped names to database codes)
EVENT_MAPPING = {
    # Sprint
    '60 meter': '60m',
    '100 meter': '100m',
    '200 meter': '200m',
    '300 meter': '300m',
    '400 meter': '400m',
    '600 meter': '600m',
    '800 meter': '800m',
    '1000 meter': '1000m',
    '1500 meter': '1500m',
    '3000 meter': '3000m',
    '5000 meter': '5000m',
    '10000 meter': '10000m',
    # Hurdles - various heights
    '60 meter hekk': '60mh',
    '60 meter hekk (68cm)': '60mh',
    '60 meter hekk (76cm)': '60mh',
    '60 meter hekk (76,2cm)': '60mh',
    '60 meter hekk (84cm)': '60mh',
    '60 meter hekk (84,0cm)': '60mh',
    '60 meter hekk (91cm)': '60mh',
    '60 meter hekk (91,4cm)': '60mh',
    '60 meter hekk (100cm)': '60mh',
    '60 meter hekk (100,0cm)': '60mh',
    '60 meter hekk (106,7cm)': '60mh',
    '100 meter hekk': '100mh',
    '110 meter hekk': '110mh',
    '400 meter hekk': '400mh',
    '3000 meter hinder': '3000mSt',
    '2000 meter hinder': '2000mSt',
    # Jumps
    'høyde': 'HJ',
    'stav': 'PV',
    'lengde': 'LJ',
    'tresteg': 'TJ',
    'høyde uten tilløp': 'HJut',
    'lengde uten tilløp': 'LJut',
    # Throws - various weights
    'kule': 'SP',
    'kule 2,0kg': 'SP',
    'kule 3,0kg': 'SP',
    'kule 4,0kg': 'SP',
    'kule 5,0kg': 'SP',
    'kule 6,0kg': 'SP',
    'kule 7,26kg': 'SP',
    'diskos': 'DT',
    'diskos 0,75kg': 'DT',
    'diskos 1,0kg': 'DT',
    'diskos 1,5kg': 'DT',
    'diskos 1,75kg': 'DT',
    'diskos 2,0kg': 'DT',
    'slegge': 'HT',
    'spyd': 'JT',
    'spyd 400g': 'JT',
    'spyd 500g': 'JT',
    'spyd 600g': 'JT',
    'spyd 700g': 'JT',
    'spyd 800g': 'JT',
    'vektkast': 'WT',
    # Combined events
    '5-kamp': 'Pent',
    '7-kamp': 'Hept',
    '10-kamp': 'Dec',
    '4 kamp': '4K',
    '5 kamp': '5K',
    '7 kamp': '7K',
}


def get_supabase_client() -> Client:
    """Create Supabase client"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Missing Supabase credentials")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def normalize_name(name: str) -> str:
    """Normalize athlete name for comparison"""
    name = name.lower().strip()
    # Remove extra whitespace
    name = ' '.join(name.split())
    return name


def normalize_meet_name(name: str) -> str:
    """
    Normalize meet name for comparison.
    Removes location prefixes like 'Lubbock/TX/USA, ' or 'Bærum, '
    """
    name = name.strip()
    if ', ' in name:
        parts = name.split(', ', 1)
        # Check if first part looks like a location:
        # - Contains '/' (e.g., 'Lubbock/TX/USA', 'Aarhus/DEN')
        # - Is a short word (likely a city name, < 20 chars)
        if '/' in parts[0] or len(parts[0]) < 20:
            name = parts[1]
    return name.lower().strip()


def parse_performance(perf_str: str, event_code: str) -> Tuple[Optional[str], Optional[int]]:
    """
    Parse performance string and return (performance, performance_value).

    For time events:
    - performance: total seconds as string (e.g., "214.32" for 3:34.32)
    - performance_value: total milliseconds (e.g., 214320)

    For field events:
    - performance: meters as string (e.g., "7.20")
    - performance_value: centimeters (e.g., 720)
    """
    if not perf_str:
        return None, None

    perf_str = perf_str.strip().replace(',', '.')

    # Categorize event types
    time_events = ['60m', '100m', '200m', '300m', '400m', '600m', '800m',
                   '1000m', '1500m', '3000m', '5000m', '10000m',
                   '60mh', '100mh', '110mh', '400mh', '3000mSt', '2000mSt']

    points_events = ['Pent', '5K', '4K', 'Hept', '7K', 'Dec']

    is_time_event = event_code in time_events
    is_points_event = event_code in points_events

    # Handle points events (combined events)
    if is_points_event:
        try:
            points = int(float(perf_str))
            return perf_str, points
        except:
            return perf_str, None

    if is_time_event:
        # Parse time: could be SS.hh, M.SS.hh, MM.SS.hh, H.MM.SS.hh
        parts = perf_str.split('.')

        try:
            if len(parts) == 2:
                # SS.hh format (e.g., "7.11" = 7.11 seconds)
                total_seconds = float(perf_str)
                total_ms = int(round(total_seconds * 1000))
                perf_seconds = f"{total_seconds:.2f}"
                return perf_seconds, total_ms
            elif len(parts) == 3:
                # M.SS.hh format (e.g., "3.34.32" = 3 min 34.32 sec)
                minutes = int(parts[0])
                seconds = int(parts[1])
                hundredths = int(parts[2].ljust(2, '0')[:2])
                total_seconds = minutes * 60 + seconds + hundredths / 100
                total_ms = int(round(total_seconds * 1000))
                perf_seconds = f"{total_seconds:.2f}"
                return perf_seconds, total_ms
            elif len(parts) == 4:
                # H.MM.SS.hh format
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = int(parts[2])
                hundredths = int(parts[3].ljust(2, '0')[:2])
                total_seconds = hours * 3600 + minutes * 60 + seconds + hundredths / 100
                total_ms = int(round(total_seconds * 1000))
                perf_seconds = f"{total_seconds:.2f}"
                return perf_seconds, total_ms
        except:
            pass

        return perf_str, None
    else:
        # Field event - distance/height in meters, convert to centimeters
        try:
            meters = float(perf_str)
            centimeters = int(round(meters * 100))
            return perf_str, centimeters
        except:
            return perf_str, None


class ResultImporter:
    def __init__(self):
        self.supabase = get_supabase_client()
        self.athletes_cache: Dict[str, str] = {}  # name+year -> id
        self.clubs_cache: Dict[str, str] = {}  # name -> id
        self.events_cache: Dict[str, str] = {}  # code -> id
        self.meets_cache: Dict[str, str] = {}  # name+date -> id
        self.seasons_cache: Dict[int, str] = {}  # year -> id

    def load_caches(self):
        """Load existing data into caches"""
        logger.info("Loading existing data...")

        # Load athletes
        offset = 0
        while True:
            result = self.supabase.table('athletes').select(
                'id, full_name, birth_year'
            ).range(offset, offset + 999).execute()

            if not result.data:
                break

            for a in result.data:
                if a['full_name']:
                    key = f"{normalize_name(a['full_name'])}|{a.get('birth_year', '')}"
                    self.athletes_cache[key] = a['id']

            offset += 1000
            if len(result.data) < 1000:
                break

        logger.info(f"  Loaded {len(self.athletes_cache)} athletes")

        # Load clubs
        result = self.supabase.table('clubs').select('id, name').execute()
        for c in result.data:
            self.clubs_cache[c['name'].lower()] = c['id']
        logger.info(f"  Loaded {len(self.clubs_cache)} clubs")

        # Load events
        result = self.supabase.table('events').select('id, code, name').execute()
        for e in result.data:
            if e['code']:
                self.events_cache[e['code'].lower()] = e['id']
            if e['name']:
                self.events_cache[e['name'].lower()] = e['id']
        logger.info(f"  Loaded {len(self.events_cache)} events")

        # Load recent meets (with normalized name variants for better matching)
        result = self.supabase.table('meets').select(
            'id, name, start_date'
        ).gte('start_date', '2025-01-01').execute()
        for m in result.data:
            key = f"{m['name'].lower()}|{m['start_date']}"
            self.meets_cache[key] = m['id']

            # Also index by normalized name for better duplicate detection
            normalized = normalize_meet_name(m['name'])
            norm_key = f"{normalized}|{m['start_date']}"
            if norm_key not in self.meets_cache:
                self.meets_cache[norm_key] = m['id']
        logger.info(f"  Loaded {len(result.data)} meets (with normalized variants)")

        # Load seasons
        result = self.supabase.table('seasons').select('id, year').execute()
        for s in result.data:
            self.seasons_cache[s['year']] = s['id']
        logger.info(f"  Loaded {len(self.seasons_cache)} seasons")

    def find_or_create_athlete(self, name: str, birth_year: Optional[int],
                                club_id: Optional[str], gender: Optional[str]) -> Optional[str]:
        """Find existing athlete or create new one"""
        key = f"{normalize_name(name)}|{birth_year or ''}"

        if key in self.athletes_cache:
            return self.athletes_cache[key]

        # Try to find by name only if birth year doesn't match
        name_key = f"{normalize_name(name)}|"
        for cached_key, athlete_id in self.athletes_cache.items():
            if cached_key.startswith(name_key):
                return athlete_id

        # Create new athlete
        name_parts = name.strip().split()
        first_name = name_parts[0] if name_parts else ''
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

        try:
            result = self.supabase.table('athletes').insert({
                'first_name': first_name,
                'last_name': last_name,
                'birth_year': birth_year,
                'gender': gender,
                'current_club_id': club_id,
            }).execute()

            if result.data:
                athlete_id = result.data[0]['id']
                self.athletes_cache[key] = athlete_id
                logger.debug(f"Created athlete: {name}")
                return athlete_id
        except Exception as e:
            logger.warning(f"Error creating athlete {name}: {e}")

        return None

    def find_or_create_club(self, club_name: str) -> Optional[str]:
        """Find existing club or create new one"""
        if not club_name:
            return None

        key = club_name.lower()
        if key in self.clubs_cache:
            return self.clubs_cache[key]

        try:
            result = self.supabase.table('clubs').insert({
                'name': club_name,
            }).execute()

            if result.data:
                club_id = result.data[0]['id']
                self.clubs_cache[key] = club_id
                logger.info(f"Created club: {club_name}")
                return club_id
        except Exception as e:
            logger.warning(f"Error creating club {club_name}: {e}")

        return None

    def find_or_create_meet(self, name: str, date: str, city: str,
                            arena: str, is_indoor: bool) -> Optional[str]:
        """Find existing meet or create new one, with smart duplicate detection"""
        key = f"{name.lower()}|{date}"

        # Check cache with exact key
        if key in self.meets_cache:
            return self.meets_cache[key]

        # Try alternative key with city prefix
        alt_key = f"{city.lower()}, {name.lower()}|{date}"
        if alt_key in self.meets_cache:
            return self.meets_cache[alt_key]

        # Normalize the incoming meet name to find duplicates
        normalized = normalize_meet_name(name)

        # Search cache for meets on the same date with similar normalized names
        for cached_key, meet_id in self.meets_cache.items():
            if not cached_key.endswith(f"|{date}"):
                continue

            cached_name = cached_key.rsplit('|', 1)[0]
            cached_normalized = normalize_meet_name(cached_name)

            # Check if normalized names match
            if normalized == cached_normalized:
                logger.debug(f"Found existing meet for '{name}': '{cached_name}'")
                # Also cache this variant for future lookups
                self.meets_cache[key] = meet_id
                return meet_id

            # Check if one contains the other
            if normalized in cached_normalized or cached_normalized in normalized:
                logger.debug(f"Found similar meet for '{name}': '{cached_name}'")
                self.meets_cache[key] = meet_id
                return meet_id

        # Query database directly for meets on this date with similar names
        # This catches meets that weren't in the initial cache
        try:
            db_meets = self.supabase.table('meets').select(
                'id, name'
            ).eq('start_date', date).execute()

            for m in db_meets.data:
                db_normalized = normalize_meet_name(m['name'])
                if normalized == db_normalized or normalized in db_normalized or db_normalized in normalized:
                    logger.info(f"Found existing DB meet for '{name}': '{m['name']}'")
                    self.meets_cache[key] = m['id']
                    return m['id']
        except Exception as e:
            logger.warning(f"Error querying meets: {e}")

        # No existing meet found, create new one
        try:
            # Use city prefix if the name doesn't already start with the city
            full_name = name
            if city and not name.lower().startswith(city.lower()):
                full_name = f"{city}, {name}"

            result = self.supabase.table('meets').insert({
                'name': full_name,
                'city': arena or city,
                'start_date': date,
                'indoor': is_indoor,
            }).execute()

            if result.data:
                meet_id = result.data[0]['id']
                self.meets_cache[key] = meet_id
                self.meets_cache[f"{full_name.lower()}|{date}"] = meet_id
                logger.info(f"Created meet: {full_name} ({date})")
                return meet_id
        except Exception as e:
            logger.warning(f"Error creating meet {name}: {e}")

        return None

    def find_event(self, event_name: str) -> Optional[str]:
        """Find event by name"""
        event_lower = event_name.lower().strip()

        # First try direct mapping
        if event_lower in EVENT_MAPPING:
            code = EVENT_MAPPING[event_lower].lower()
            if code in self.events_cache:
                return self.events_cache[code]

        # Try the name directly
        if event_lower in self.events_cache:
            return self.events_cache[event_lower]

        # Handle truncated event names (due to CSV comma parsing)
        # e.g., "60 meter hekk (106" -> match "60 meter hekk"
        if '(' in event_lower:
            base_name = event_lower.split('(')[0].strip()
            if base_name in EVENT_MAPPING:
                code = EVENT_MAPPING[base_name].lower()
                if code in self.events_cache:
                    return self.events_cache[code]
            if base_name in self.events_cache:
                return self.events_cache[base_name]

        # Try prefix matching for hurdles with height specs
        hurdle_patterns = [
            ('60 meter hekk', '60mh'),
            ('100 meter hekk', '100mh'),
            ('110 meter hekk', '110mh'),
        ]
        for pattern, code in hurdle_patterns:
            if event_lower.startswith(pattern):
                if code.lower() in self.events_cache:
                    return self.events_cache[code.lower()]

        # Try prefix matching for throws with weight specs
        throw_patterns = [
            ('kule', 'SP'),
            ('diskos', 'DT'),
            ('slegge', 'HT'),
            ('spyd', 'JT'),
        ]
        for pattern, code in throw_patterns:
            if event_lower.startswith(pattern):
                if code.lower() in self.events_cache:
                    return self.events_cache[code.lower()]

        # Try prefix matching for jumps with specifications
        if event_lower.startswith('lengde'):
            if 'uten' in event_lower:
                if 'ljut' in self.events_cache:
                    return self.events_cache['ljut']
            else:
                if 'lj' in self.events_cache:
                    return self.events_cache['lj']

        # Try partial match
        for cached_name, event_id in self.events_cache.items():
            if event_lower in cached_name or cached_name in event_lower:
                return event_id

        # Handle combined events with varying names
        combined_keywords = ['kamp', 'mangekamp', 'pentathlon', 'heptathlon', 'decathlon']
        if any(kw in event_lower for kw in combined_keywords):
            # Try to find a combined event in cache
            for code in ['5k', 'pent', '7k', 'hept', 'dec', '4k']:
                if code in self.events_cache:
                    return self.events_cache[code]

        logger.warning(f"Could not find event: {event_name}")
        return None

    def get_gender_from_class(self, event_class: str) -> Optional[str]:
        """Determine gender from event class"""
        if not event_class:
            return None

        event_class_lower = event_class.lower()
        if any(w in event_class_lower for w in ['menn', 'gutter', 'herr']):
            return 'M'
        if any(w in event_class_lower for w in ['kvinn', 'jent', 'dam']):
            return 'F'
        return None

    def get_season_id(self, date_str: str) -> Optional[str]:
        """Get season ID for a date"""
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            year = date.year
            return self.seasons_cache.get(year)
        except:
            return None

    def import_results(self, csv_path: str, dry_run: bool = False) -> Dict:
        """Import results from CSV file"""
        stats = {
            'total_rows': 0,
            'imported': 0,
            'skipped': 0,
            'errors': 0,
            'new_athletes': 0,
            'new_clubs': 0,
            'new_meets': 0,
        }

        # Load existing data
        self.load_caches()
        initial_athletes = len(self.athletes_cache)
        initial_clubs = len(self.clubs_cache)
        initial_meets = len(self.meets_cache)

        # Read CSV
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        stats['total_rows'] = len(rows)
        logger.info(f"Processing {len(rows)} rows...")

        # Group by meet for efficiency
        by_meet: Dict[str, List[dict]] = {}
        for row in rows:
            key = f"{row['meet_name']}|{row['meet_date']}"
            if key not in by_meet:
                by_meet[key] = []
            by_meet[key].append(row)

        results_to_insert = []

        for meet_key, meet_rows in by_meet.items():
            first_row = meet_rows[0]

            # Get or create meet
            meet_id = self.find_or_create_meet(
                name=first_row['meet_name'],
                date=first_row['meet_date'],
                city=first_row.get('location', ''),
                arena=first_row.get('arena', ''),
                is_indoor=first_row['is_indoor'].lower() == 'true'
            )

            if not meet_id:
                stats['errors'] += len(meet_rows)
                continue

            season_id = self.get_season_id(first_row['meet_date'])

            for row in meet_rows:
                try:
                    # Get or create club
                    club_id = self.find_or_create_club(row['club']) if row['club'] else None

                    # Determine gender
                    gender = self.get_gender_from_class(row.get('event_class', ''))

                    # Get or create athlete
                    birth_year = int(row['birth_year']) if row.get('birth_year') else None
                    athlete_id = self.find_or_create_athlete(
                        name=row['athlete_name'],
                        birth_year=birth_year,
                        club_id=club_id,
                        gender=gender
                    )

                    if not athlete_id:
                        stats['skipped'] += 1
                        continue

                    # Find event
                    event_id = self.find_event(row['event'])
                    if not event_id:
                        stats['skipped'] += 1
                        continue

                    # Parse performance
                    event_code = EVENT_MAPPING.get(row['event'].lower(), '')
                    performance, performance_value = parse_performance(row['result'], event_code)

                    # Parse wind
                    wind = None
                    if row.get('wind'):
                        try:
                            wind = float(row['wind'].replace(',', '.'))
                        except:
                            pass

                    # Parse place
                    place = None
                    if row.get('place'):
                        try:
                            place = int(row['place'])
                        except:
                            pass

                    results_to_insert.append({
                        'athlete_id': athlete_id,
                        'event_id': event_id,
                        'meet_id': meet_id,
                        'season_id': season_id,
                        'club_id': club_id,
                        'performance': performance,
                        'performance_value': performance_value,
                        'date': first_row['meet_date'],
                        'place': place,
                        'wind': wind,
                        'status': 'OK',
                    })

                except Exception as e:
                    logger.warning(f"Error processing row: {e}")
                    stats['errors'] += 1

        # Filter out duplicates before inserting
        if results_to_insert:
            logger.info("Checking for existing results...")
            unique_results = []
            for r in results_to_insert:
                # Check if this result already exists
                existing = self.supabase.table('results').select('id').eq(
                    'athlete_id', r['athlete_id']
                ).eq('event_id', r['event_id']).eq(
                    'meet_id', r['meet_id']
                ).eq('date', r['date']).limit(1).execute()

                if not existing.data:
                    unique_results.append(r)
                else:
                    stats['skipped'] += 1

            logger.info(f"Found {len(unique_results)} new results, {stats['skipped']} already exist")
            results_to_insert = unique_results

        # Insert results in batches
        if not dry_run and results_to_insert:
            batch_size = 50
            for i in range(0, len(results_to_insert), batch_size):
                batch = results_to_insert[i:i + batch_size]
                try:
                    result = self.supabase.table('results').insert(batch).execute()
                    stats['imported'] += len(batch)
                except Exception as e:
                    logger.error(f"Error inserting batch: {e}")
                    stats['errors'] += len(batch)

                if (i + batch_size) % 200 == 0:
                    logger.info(f"  Inserted {i + batch_size}/{len(results_to_insert)} results")

        # Calculate new items
        stats['new_athletes'] = len(self.athletes_cache) - initial_athletes
        stats['new_clubs'] = len(self.clubs_cache) - initial_clubs
        stats['new_meets'] = len(self.meets_cache) - initial_meets

        return stats


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Import scraped results to database')
    parser.add_argument('csv_file', help='CSV file to import')
    parser.add_argument('--dry-run', action='store_true', help='Preview without importing')
    args = parser.parse_args()

    if not os.path.exists(args.csv_file):
        logger.error(f"File not found: {args.csv_file}")
        return

    logger.info("=" * 60)
    logger.info("Starting result import")
    logger.info(f"File: {args.csv_file}")
    logger.info(f"Dry run: {args.dry_run}")
    logger.info("=" * 60)

    importer = ResultImporter()
    stats = importer.import_results(args.csv_file, dry_run=args.dry_run)

    logger.info("\n" + "=" * 60)
    logger.info("IMPORT COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total rows: {stats['total_rows']}")
    logger.info(f"Imported: {stats['imported']}")
    logger.info(f"Skipped: {stats['skipped']}")
    logger.info(f"Errors: {stats['errors']}")
    logger.info(f"New athletes created: {stats['new_athletes']}")
    logger.info(f"New clubs created: {stats['new_clubs']}")
    logger.info(f"New meets created: {stats['new_meets']}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
