import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

# Get event IDs first
events = {}
codes = ['400mh_76_2cm', '400mh_84cm', '400mh_91_4cm', '3000mhinder_76_2cm', '3000mhinder_91_4cm']

for code in codes:
    event = supabase.table('events').select('id, name').eq('code', code).limit(1).execute()
    if event.data:
        events[code] = {'id': event.data[0]['id'], 'name': event.data[0]['name']}
        print(f"Found {code}: {event.data[0]['name']}")

print("\n" + "="*60)

# Find suspicious low values for 400m hekk (should be 45-90s = 4500-9000)
for code in ['400mh_76_2cm', '400mh_84cm', '400mh_91_4cm']:
    if code not in events:
        continue

    event_id = events[code]['id']
    print(f"\n{events[code]['name']}:")

    # Get results with values that look like M.SS format (100-159 for 1:00-1:59)
    suspicious = supabase.table('results').select('id, performance_value').eq(
        'event_id', event_id
    ).gt('performance_value', 99).lt('performance_value', 200).execute()

    if suspicious.data:
        print(f"  Fant {len(suspicious.data)} resultater med M.SS-format (1:00-1:59)")

        # Fix each one
        fixed = 0
        for r in suspicious.data:
            wrong_val = r['performance_value']
            mins = wrong_val // 100
            secs = wrong_val % 100
            if secs < 60:
                correct_val = (mins * 60 + secs) * 100
                supabase.table('results').update({
                    'performance_value': correct_val
                }).eq('id', r['id']).execute()
                fixed += 1
        print(f"  Fikset: {fixed}")
    else:
        print("  Ingen å fikse")

# Find suspicious low values for 3000m hinder (should be 8-15min = 48000-90000)
for code in ['3000mhinder_76_2cm', '3000mhinder_91_4cm']:
    if code not in events:
        continue

    event_id = events[code]['id']
    print(f"\n{events[code]['name']}:")

    # Get results with values that look like M.SS format (800-1559 for 8:00-15:59)
    suspicious = supabase.table('results').select('id, performance_value').eq(
        'event_id', event_id
    ).gt('performance_value', 799).lt('performance_value', 1600).execute()

    if suspicious.data:
        print(f"  Fant {len(suspicious.data)} resultater med M.SS-format (8:00-15:59)")

        # Fix each one
        fixed = 0
        for r in suspicious.data:
            wrong_val = r['performance_value']
            mins = wrong_val // 100
            secs = wrong_val % 100
            if secs < 60:
                correct_val = (mins * 60 + secs) * 100
                supabase.table('results').update({
                    'performance_value': correct_val
                }).eq('id', r['id']).execute()
                fixed += 1
        print(f"  Fikset: {fixed}")
    else:
        print("  Ingen å fikse")

print("\nFerdig!")
