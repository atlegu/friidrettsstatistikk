import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

def format_time(hundredths, is_long=False):
    """Format hundredths to readable time"""
    if not hundredths:
        return "N/A"
    seconds = hundredths / 100
    if is_long:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}:{mins:02d}:{secs:02d}"
    else:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}:{secs:05.2f}"

events_to_check = [
    ('400mh', '400m hekk', False),
    ('3000mhinder', '3000m hinder', False),
    ('halvmaraton', 'Halvmaraton', True),
    ('maraton', 'Maraton', True),
]

for code, name, is_long in events_to_check:
    event = supabase.table('events').select('id').eq('code', code).limit(1).execute()
    if not event.data:
        print(f"\n{name}: Fant ikke øvelse")
        continue

    event_id = event.data[0]['id']

    # Get top 10 results
    results = supabase.table('results').select(
        'performance_value, date, athlete_id'
    ).eq('event_id', event_id).eq('status', 'OK').gt('performance_value', 0).order(
        'performance_value', desc=False
    ).limit(10).execute()

    print(f"\n{'='*60}")
    print(f"{name} - Topp 10:")
    print(f"{'='*60}")

    for i, r in enumerate(results.data, 1):
        val = r['performance_value']
        time_str = format_time(val, is_long)

        # Get athlete name
        athlete = supabase.table('athletes').select('full_name, gender').eq('id', r['athlete_id']).limit(1).execute()
        name_str = athlete.data[0]['full_name'] if athlete.data else 'Ukjent'
        gender = athlete.data[0].get('gender', '?') if athlete.data else '?'

        print(f"{i:2}. {time_str:>12}  ({val:>10})  {gender}  {name_str[:30]:<30}  {r['date']}")
