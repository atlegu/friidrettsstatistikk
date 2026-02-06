"""
Fix invalid results in the database.

Issues identified:
1. "857.00" - Error code/placeholder (246 results across many events)
2. "0.00" - DNS/failed attempts (8 results)
3. Suspicious 800m times: "0.01", "0.02", "1.00" (performance_value < 1000)
4. Suspicious shot put: values over 50m for actual shot put (not combined events)

This script will DELETE these invalid results.
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

DRY_RUN = False  # Set to False to actually delete

def delete_results(description, query_func):
    """Helper to delete results with logging."""
    results = query_func()
    count = len(results.data) if results.data else 0

    if count == 0:
        print(f"  {description}: Ingen resultater funnet")
        return 0

    if DRY_RUN:
        print(f"  {description}: {count} resultater vil bli slettet (DRY RUN)")
        for r in results.data[:5]:  # Show first 5
            print(f"    - ID: {r['id']}")
        if count > 5:
            print(f"    ... og {count - 5} til")
    else:
        # Actually delete
        ids = [r['id'] for r in results.data]
        for i in range(0, len(ids), 100):  # Delete in batches of 100
            batch = ids[i:i+100]
            supabase.table('results').delete().in_('id', batch).execute()
        print(f"  {description}: {count} resultater slettet")

    return count

print("=" * 60)
print("FIXING INVALID RESULTS")
print("=" * 60)
if DRY_RUN:
    print("*** DRY RUN - ingen endringer vil bli gjort ***")
    print("Sett DRY_RUN = False for å faktisk slette")
print()

total_deleted = 0

# 1. Delete all "857.00" results (error code)
print("1. Sletter '857.00' feilkoder...")
total_deleted += delete_results(
    "857.00 feilkoder",
    lambda: supabase.table('results').select('id').eq('performance', '857.00').execute()
)

# 2. Delete all "0.00" results (DNS/failed)
print("\n2. Sletter '0.00' ugyldige resultater...")
total_deleted += delete_results(
    "0.00 resultater",
    lambda: supabase.table('results').select('id').eq('performance', '0.00').execute()
)

# 3. Delete suspicious 800m results with very low values
print("\n3. Sletter suspekte 800m-tider (under 50 sekunder)...")
# Get 800m event ID
event_800m = supabase.table('events').select('id').eq('name', '800 meter').limit(1).execute()
if event_800m.data:
    event_id_800m = event_800m.data[0]['id']
    total_deleted += delete_results(
        "800m tider under 50 sek",
        lambda: supabase.table('results').select('id').eq('event_id', event_id_800m).lt('performance_value', 5000).execute()
    )

# 4. Delete suspicious shot put results over 50m (for actual shot put events, not combined)
print("\n4. Sletter suspekte kuleresultater over 50m...")
# Get shot put event IDs (actual shot put, not combined events)
shot_put_events = supabase.table('events').select('id, name').like('name', 'Kule %kg').execute()
if shot_put_events.data:
    for event in shot_put_events.data:
        results = supabase.table('results').select('id').eq('event_id', event['id']).gt('performance_value', 50000).execute()
        if results.data:
            total_deleted += delete_results(
                f"{event['name']} over 50m",
                lambda e=event: supabase.table('results').select('id').eq('event_id', e['id']).gt('performance_value', 50000).execute()
            )

# 5. Check for "0.01" and "0.02" specifically
print("\n5. Sletter '0.01' og '0.02' feilkoder...")
total_deleted += delete_results(
    "0.01 resultater",
    lambda: supabase.table('results').select('id').eq('performance', '0.01').execute()
)
total_deleted += delete_results(
    "0.02 resultater",
    lambda: supabase.table('results').select('id').eq('performance', '0.02').execute()
)

print("\n" + "=" * 60)
print(f"TOTALT: {total_deleted} resultater {'vil bli slettet' if DRY_RUN else 'slettet'}")
print("=" * 60)

if DRY_RUN:
    print("\nFor å faktisk slette, endre DRY_RUN = False i scriptet")
