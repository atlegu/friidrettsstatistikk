import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

# Get event ID
event = supabase.table('events').select('id').eq('code', '3000mhinder_76_2cm').limit(1).execute()
event_id = event.data[0]['id']

# Get results below realistic (8 minutes = 48000 hundredths)
suspicious = supabase.table('results').select(
    'id, performance_value, date, athlete_id'
).eq('event_id', event_id).lt('performance_value', 48000).gt('performance_value', 0).execute()

print(f"Resultater under 8 minutter:")
for r in suspicious.data:
    val = r['performance_value']
    athlete = supabase.table('athletes').select('full_name').eq('id', r['athlete_id']).limit(1).execute()
    name = athlete.data[0]['full_name'] if athlete.data else 'Ukjent'

    # Possible interpretations:
    # If it's MM:SS format (e.g., 1651 = 16:51)
    if val >= 1000:
        mins = val // 100
        secs = val % 100
        if secs < 60:
            correct = (mins * 60 + secs) * 100
            print(f"  {val} -> {name} ({r['date']}) - Mulig {mins}:{secs:02d} = {correct}")
        else:
            print(f"  {val} -> {name} ({r['date']}) - Ukjent format")
    else:
        print(f"  {val} -> {name} ({r['date']}) - For lav verdi")
