import os
import re
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

event = supabase.table('events').select('id').eq('code', '400m').limit(1).execute()
event_id = event.data[0]['id']

# Get unique performance values that need fixing
# Values like 101, 102, ..., 159, 200, 201, ... (M.SS interpreted as seconds)
values_to_check = []
for mins in range(1, 6):  # 1-5 minutes
    for secs in range(0, 60):  # 0-59 seconds
        wrong_val = mins * 100 + secs  # Current wrong value
        correct_val = (mins * 60 + secs) * 100  # Correct value
        if wrong_val < 4400 and correct_val >= 4400:
            values_to_check.append((wrong_val, correct_val))

print(f"Checking {len(values_to_check)} value mappings...")

total_fixed = 0
for wrong_val, correct_val in values_to_check:
    # Update all results with this wrong value
    result = supabase.table('results').update({
        'performance_value': correct_val
    }).eq('event_id', event_id).eq('performance_value', wrong_val).execute()

    if result.data:
        count = len(result.data)
        if count > 0:
            total_fixed += count
            print(f"  {wrong_val} -> {correct_val}: {count} resultater")

print(f"\nFerdig! Totalt fikset: {total_fixed}")
