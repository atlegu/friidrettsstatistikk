"""Insert missing results for Atle Guttormsen."""
from supabase import create_client
from dotenv import load_dotenv
import os
import uuid

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

ATHLETE_ID = '66bc86ac-86ca-4809-8721-342d4b0d4113'  # Atle Guttormsen
CLUB_NAME = 'Ski IL Friidrett'

# Get club ID
club = supabase.table('clubs').select('id').ilike('name', f'%{CLUB_NAME}%').execute()
club_id = club.data[0]['id'] if club.data else None
print(f"Club ID: {club_id}")


def get_or_create_meet(date, venue, name=None, indoor=False):
    """Get existing meet or create new one."""
    meet_name = name or f"Stevne i {venue}"
    # Try to find existing meet by start_date and venue/name
    existing = supabase.table('meets').select('id').eq('start_date', date).ilike('name', f'%{venue}%').limit(1).execute()
    if existing.data:
        return existing.data[0]['id']
    # Try by name and date
    existing = supabase.table('meets').select('id').eq('start_date', date).ilike('name', f'%{name}%').limit(1).execute()
    if existing.data:
        return existing.data[0]['id']

    # Get season for the meet
    year = int(date.split('-')[0])
    season = supabase.table('seasons').select('id').eq('year', year).eq('indoor', indoor).execute()
    season_id = season.data[0]['id'] if season.data else None

    # Create new meet
    new_meet = {
        'id': str(uuid.uuid4()),
        'name': f"{meet_name}, {venue}",
        'city': venue,
        'country': 'NOR',
        'start_date': date,
        'indoor': indoor,
        'season_id': season_id,
        'level': 'local',
    }
    supabase.table('meets').insert(new_meet).execute()
    print(f"  Created meet: {new_meet['name']} ({date})")
    return new_meet['id']


def get_season(year, indoor=False):
    """Get season ID for year."""
    season = supabase.table('seasons').select('id').eq('year', year).eq('indoor', indoor).execute()
    return season.data[0]['id'] if season.data else None


def get_event(name):
    """Get event ID by name."""
    event = supabase.table('events').select('id').eq('name', name).execute()
    return event.data[0]['id'] if event.data else None


# Missing results from source that are not in DB
missing_results = [
    {
        'event_name': '110 meter hekk (106,7cm)',
        'performance': '15.19',
        'wind': 1.1,
        'date': '1995-08-18',
        'venue': 'Lillehammer',
        'meet_name': 'NM Friidrett',
        'place': 6,
        'indoor': False,
    },
    {
        'event_name': '200 meter hekk (76,2cm)',
        'performance': '33.28',
        'wind': -2.0,
        'date': '2013-09-16',
        'venue': 'Ås',
        'meet_name': 'Kretsstevne',
        'place': 1,
        'indoor': False,
    },
    {
        'event_name': 'Kule 7,26kg',
        'performance': '8.73',
        'wind': None,
        'date': '2013-09-18',
        'venue': 'Ski',
        'meet_name': 'Kretsstevne',
        'place': 1,
        'indoor': False,
    },
    {
        'event_name': 'Stav',
        'performance': '3.70',
        'wind': None,
        'date': '1992-02-23',
        'venue': 'Drammen',
        'meet_name': 'Hallstevne',
        'place': None,  # 'M' in source (manual ranking)
        'indoor': True,
    },
]

for r in missing_results:
    year = int(r['date'].split('-')[0])
    event_id = get_event(r['event_name'])
    if not event_id:
        print(f"ERROR: Event not found: {r['event_name']}")
        continue

    season_id = get_season(year, r['indoor'])
    if not season_id:
        print(f"ERROR: Season not found: {year} {'indoor' if r['indoor'] else 'outdoor'}")
        continue

    meet_id = get_or_create_meet(r['date'], r['venue'], r['meet_name'], r['indoor'])

    # Convert performance to value (milliseconds for times, mm for distances)
    perf_str = r['performance']
    if ':' in perf_str:
        # Time format like 2:45.80
        parts = perf_str.split(':')
        perf_value = int(float(parts[0]) * 60000 + float(parts[1]) * 1000)
    elif '.' in perf_str:
        perf_value = int(float(perf_str) * 1000)
    else:
        perf_value = int(perf_str) * 1000

    result = {
        'id': str(uuid.uuid4()),
        'athlete_id': ATHLETE_ID,
        'event_id': event_id,
        'meet_id': meet_id,
        'season_id': season_id,
        'club_id': club_id,
        'performance': r['performance'],
        'performance_value': perf_value,
        'wind': r['wind'],
        'date': r['date'],
        'place': r['place'],
        'status': 'OK',
        'verified': True,
    }

    try:
        supabase.table('results').insert(result).execute()
        wind_str = f" ({r['wind']:+.1f})" if r['wind'] else ""
        indoor_str = " (inne)" if r['indoor'] else ""
        print(f"Inserted: {r['event_name']}{indoor_str} - {r['performance']}{wind_str} - {r['date']}")
    except Exception as e:
        print(f"Error inserting {r['event_name']}: {e}")

print("\nDone inserting missing results!")
