import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

def format_time(hundredths):
    """Format hundredths to readable time"""
    if not hundredths:
        return "N/A"
    seconds = hundredths / 100
    mins = int(seconds // 60)
    secs = seconds % 60
    return f"{mins}:{secs:05.2f}"

# Check 400m hekk variants
print("400m hekk varianter - Topp 5 per variant:")
print("="*80)

hurdle_400_codes = ['400mh_76_2cm', '400mh_84cm', '400mh_91_4cm', '400mh_68cm']
for code in hurdle_400_codes:
    event = supabase.table('events').select('id, name').eq('code', code).limit(1).execute()
    if not event.data:
        continue

    event_id = event.data[0]['id']
    event_name = event.data[0]['name']

    results = supabase.table('results').select(
        'performance_value, date, athlete_id'
    ).eq('event_id', event_id).eq('status', 'OK').gt('performance_value', 0).order(
        'performance_value', desc=False
    ).limit(5).execute()

    if results.data:
        print(f"\n{event_name} ({code}):")
        for r in results.data:
            val = r['performance_value']
            time_str = format_time(val)
            athlete = supabase.table('athletes').select('full_name, gender').eq('id', r['athlete_id']).limit(1).execute()
            name_str = athlete.data[0]['full_name'] if athlete.data else 'Ukjent'
            gender = athlete.data[0].get('gender', '?') if athlete.data else '?'
            print(f"  {time_str:>12}  ({val:>8})  {gender}  {name_str[:30]}")

# Check 3000m hinder variants
print("\n\n3000m hinder varianter - Topp 5 per variant:")
print("="*80)

hurdle_3000_codes = ['3000mhinder_76_2cm', '3000mhinder_84cm', '3000mhinder_91_4cm']
for code in hurdle_3000_codes:
    event = supabase.table('events').select('id, name').eq('code', code).limit(1).execute()
    if not event.data:
        continue

    event_id = event.data[0]['id']
    event_name = event.data[0]['name']

    results = supabase.table('results').select(
        'performance_value, date, athlete_id'
    ).eq('event_id', event_id).eq('status', 'OK').gt('performance_value', 0).order(
        'performance_value', desc=False
    ).limit(5).execute()

    if results.data:
        print(f"\n{event_name} ({code}):")
        for r in results.data:
            val = r['performance_value']
            time_str = format_time(val)
            athlete = supabase.table('athletes').select('full_name, gender').eq('id', r['athlete_id']).limit(1).execute()
            name_str = athlete.data[0]['full_name'] if athlete.data else 'Ukjent'
            gender = athlete.data[0].get('gender', '?') if athlete.data else '?'
            print(f"  {time_str:>12}  ({val:>8})  {gender}  {name_str[:30]}")
