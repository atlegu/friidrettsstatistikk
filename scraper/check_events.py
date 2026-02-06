import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

# Find events with "hekk" or "hinder" in name
print("Events med 'hekk' eller 'hinder' i navnet:")
print("="*80)

events = supabase.table('events').select('id, code, name, result_type').execute()

for e in events.data:
    name_lower = e['name'].lower()
    code_lower = e['code'].lower()
    if 'hekk' in name_lower or 'hinder' in name_lower or 'hurdle' in name_lower or 'steeple' in name_lower:
        # Count results
        count = supabase.table('results').select('id', count='exact').eq('event_id', e['id']).execute()
        print(f"{e['code']:<20} {e['name']:<30} {e['result_type']:<10} {count.count:>5} resultater")

print("\n\nEvents med '400' i koden:")
print("="*80)
for e in events.data:
    if '400' in e['code']:
        count = supabase.table('results').select('id', count='exact').eq('event_id', e['id']).execute()
        print(f"{e['code']:<20} {e['name']:<30} {e['result_type']:<10} {count.count:>5} resultater")

print("\n\nEvents med '3000' i koden:")
print("="*80)
for e in events.data:
    if '3000' in e['code']:
        count = supabase.table('results').select('id', count='exact').eq('event_id', e['id']).execute()
        print(f"{e['code']:<20} {e['name']:<30} {e['result_type']:<10} {count.count:>5} resultater")
