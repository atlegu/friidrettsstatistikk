import os
import re
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

# Events to fix with their minimum realistic values
# Format: (code, min_value_hundredths, is_hours_format)
events_to_fix = [
    ('400mh', 4600, False),      # 46 seconds min, M.SS format
    ('3000mhinder', 48000, False),  # 8 minutes min, M.SS format
    ('halvmaraton', 360000, True),  # 1 hour min, H.MM format
    ('maraton', 720000, True),      # 2 hours min, H.MM format
]

total_fixed = 0

for code, min_val, is_hours in events_to_fix:
    event = supabase.table('events').select('id, name').eq('code', code).limit(1).execute()
    if not event.data:
        print(f"{code}: Fant ikke øvelse")
        continue

    event_id = event.data[0]['id']
    event_name = event.data[0]['name']
    print(f"\n{event_name} ({code}):")

    if is_hours:
        # Hours format: H.MM -> (H*3600 + MM*60) * 100
        # Values like 103 (1.03 = 1h03m), 214 (2.14 = 2h14m)
        for hours in range(1, 10):  # 1-9 hours
            for mins in range(0, 60):
                wrong_val = hours * 100 + mins
                correct_val = (hours * 3600 + mins * 60) * 100

                if wrong_val < min_val / 100 and correct_val >= min_val:
                    result = supabase.table('results').update({
                        'performance_value': correct_val
                    }).eq('event_id', event_id).eq('performance_value', wrong_val).execute()

                    if result.data:
                        count = len(result.data)
                        if count > 0:
                            total_fixed += count
                            print(f"  {wrong_val} -> {correct_val} ({hours}h{mins:02d}m): {count} resultater")
    else:
        # Minutes format: M.SS -> (M*60 + SS) * 100
        for mins in range(1, 20):  # 1-19 minutes
            for secs in range(0, 60):
                wrong_val = mins * 100 + secs
                correct_val = (mins * 60 + secs) * 100

                if wrong_val < min_val and correct_val >= min_val:
                    result = supabase.table('results').update({
                        'performance_value': correct_val
                    }).eq('event_id', event_id).eq('performance_value', wrong_val).execute()

                    if result.data:
                        count = len(result.data)
                        if count > 0:
                            total_fixed += count
                            print(f"  {wrong_val} -> {correct_val} ({mins}:{secs:02d}): {count} resultater")

print(f"\nTotalt fikset: {total_fixed}")
