import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

# Events to fix with their minimum realistic values (in hundredths)
# Format: (code_prefix, min_realistic_hundredths, max_wrong_value)
events_to_fix = [
    # 400m hekk: realistic times 45-90 seconds (4500-9000 hundredths)
    # Wrong values like 100 (1:00) to 159 (1:59) need to become 6000-11900
    ('400mh_76_2cm', 4500),
    ('400mh_84cm', 4500),
    ('400mh_91_4cm', 4500),
    ('400mh_68cm', 4500),

    # 3000m hinder: realistic times 8-15 minutes (48000-90000 hundredths)
    # Wrong values like 800 (8:00) to 1500 (15:00) need to become 48000-90000
    ('3000mhinder_76_2cm', 48000),
    ('3000mhinder_84cm', 48000),
    ('3000mhinder_91_4cm', 48000),
]

total_fixed = 0

for code, min_realistic in events_to_fix:
    event = supabase.table('events').select('id, name').eq('code', code).limit(1).execute()
    if not event.data:
        print(f"{code}: Fant ikke øvelse")
        continue

    event_id = event.data[0]['id']
    event_name = event.data[0]['name']
    fixed_count = 0

    print(f"\n{'='*60}")
    print(f"{event_name} ({code}):")
    print(f"{'='*60}")

    # Check all M.SS format values (from 1:00 to 19:59)
    for mins in range(1, 20):
        for secs in range(0, 60):
            wrong_val = mins * 100 + secs  # e.g., 100 for 1:00, 913 for 9:13
            correct_val = (mins * 60 + secs) * 100  # e.g., 6000 for 1:00, 55300 for 9:13

            # Only fix if wrong value is below realistic and correct is realistic
            if wrong_val < min_realistic and correct_val >= min_realistic:
                result = supabase.table('results').update({
                    'performance_value': correct_val
                }).eq('event_id', event_id).eq('performance_value', wrong_val).execute()

                if result.data and len(result.data) > 0:
                    count = len(result.data)
                    fixed_count += count
                    total_fixed += count
                    print(f"  {wrong_val} -> {correct_val} ({mins}:{secs:02d}): {count} resultater")

    if fixed_count == 0:
        print("  Ingen resultater å fikse")
    else:
        print(f"  Fikset: {fixed_count} resultater")

print(f"\n{'='*60}")
print(f"TOTALT FIKSET: {total_fixed} resultater")
print(f"{'='*60}")
