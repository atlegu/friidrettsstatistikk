import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

# Get event ID
event = supabase.table('events').select('id').eq('code', '3000mhinder_76_2cm').limit(1).execute()
event_id = event.data[0]['id']

# Fix values in the 1600-2000 range (16:00-19:59)
suspicious = supabase.table('results').select(
    'id, performance_value'
).eq('event_id', event_id).gte('performance_value', 1600).lte('performance_value', 2000).execute()

print(f"Fant {len(suspicious.data)} resultater å fikse")

for r in suspicious.data:
    val = r['performance_value']
    mins = val // 100
    secs = val % 100
    if secs < 60:
        correct = (mins * 60 + secs) * 100
        supabase.table('results').update({
            'performance_value': correct
        }).eq('id', r['id']).execute()
        print(f"  {val} -> {correct} ({mins}:{secs:02d})")

print("Ferdig!")
