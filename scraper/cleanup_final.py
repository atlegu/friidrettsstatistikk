"""
Final cleanup pass with proper pagination.
"""
import os
import time
from supabase import create_client
from tqdm import tqdm

# Load env
url = key = None
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('SUPABASE_SERVICE_KEY='):
            key = line.split('=', 1)[1].strip()
        if line.startswith('SUPABASE_URL='):
            url = line.split('=', 1)[1].strip()

supabase = create_client(url, key)

def cleanup_athlete_full(athlete_id):
    """Clean up with proper pagination."""
    all_results = []
    offset = 0
    while True:
        try:
            resp = supabase.table('results').select('id, event_id, meet_id, date, performance').eq('athlete_id', athlete_id).range(offset, offset + 999).execute()
            if not resp.data:
                break
            all_results.extend(resp.data)
            if len(resp.data) < 1000:
                break
            offset += 1000
        except Exception as e:
            print(f"Error fetching results for {athlete_id}: {e}")
            time.sleep(1)
            break

    seen = {}
    to_delete = []
    for r in all_results:
        key = (r['event_id'], r['meet_id'], r['date'], r['performance'])
        if key in seen:
            to_delete.append(r['id'])
        else:
            seen[key] = r['id']

    if to_delete:
        for i in range(0, len(to_delete), 50):
            batch = to_delete[i:i+50]
            try:
                supabase.table('results').delete().in_('id', batch).execute()
                time.sleep(0.1)
            except Exception as e:
                print(f"Error deleting: {e}")
                time.sleep(1)

    return len(to_delete)

# Get all athletes
print("Loading athletes...")
all_athletes = []
offset = 0
while True:
    resp = supabase.table('athletes').select('id').range(offset, offset + 999).execute()
    if not resp.data:
        break
    all_athletes.extend([a['id'] for a in resp.data])
    if len(resp.data) < 1000:
        break
    offset += 1000

print(f"Checking {len(all_athletes)} athletes...")

total_deleted = 0
for athlete_id in tqdm(all_athletes, desc="Cleaning"):
    deleted = cleanup_athlete_full(athlete_id)
    total_deleted += deleted
    time.sleep(0.02)

print(f"\nTotal deleted: {total_deleted}")

resp = supabase.table('results').select('id', count='exact').limit(1).execute()
print(f"Final result count: {resp.count}")
