#!/usr/bin/env python3
"""Remove duplicate results from the database."""

import sys
sys.stdout.reconfigure(line_buffering=True)

from supabase import create_client
from dotenv import load_dotenv
import os
from collections import defaultdict

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print('Finding all duplicates (same athlete, event, date, performance)...')

batch_size = 1000
offset = 0
duplicates = defaultdict(list)  # key -> list of result IDs

while True:
    results = supabase.table('results').select('id, athlete_id, event_id, date, performance').range(offset, offset + batch_size - 1).execute()

    if not results.data:
        break

    for r in results.data:
        key = (r['athlete_id'], r['event_id'], r['date'], r['performance'])
        duplicates[key].append(r['id'])

    offset += batch_size
    if offset % 200000 == 0:
        print(f'  Scanned {offset} results...')

# Collect IDs to delete (keep first, delete rest)
ids_to_delete = []
for key, ids in duplicates.items():
    if len(ids) > 1:
        ids_to_delete.extend(ids[1:])

print(f'\nFound {len(ids_to_delete)} duplicate results to delete')

# Delete in batches
print('\nDeleting duplicates...')
batch_size = 200
deleted = 0

for i in range(0, len(ids_to_delete), batch_size):
    batch = ids_to_delete[i:i+batch_size]
    try:
        supabase.table('results').delete().in_('id', batch).execute()
        deleted += len(batch)
    except Exception as e:
        print(f'  Error deleting batch: {e}')
        # Try individual deletes
        for result_id in batch:
            try:
                supabase.table('results').delete().eq('id', result_id).execute()
                deleted += 1
            except:
                pass

    if (i + batch_size) % 50000 == 0:
        print(f'  Deleted {min(i + batch_size, len(ids_to_delete))} / {len(ids_to_delete)}...')

print(f'\nDeleted {deleted} duplicate results')

# Verify
total = supabase.table('results').select('id', count='exact').execute()
print(f'Total results after cleanup: {total.count}')

print('\nDone!')
