import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

events_to_check = [
    ('400mh', '400m hekk', 4500, 9000),      # Realistic: 45-90 seconds
    ('3000mhinder', '3000m hinder', 48000, 72000),  # Realistic: 8-12 minutes
]

for code, name, min_realistic, max_realistic in events_to_check:
    event = supabase.table('events').select('id').eq('code', code).limit(1).execute()
    if not event.data:
        print(f"\n{name}: Fant ikke øvelse")
        continue

    event_id = event.data[0]['id']

    # Count total results
    total = supabase.table('results').select('id', count='exact').eq('event_id', event_id).eq('status', 'OK').execute()

    # Count results in realistic range
    realistic = supabase.table('results').select('id', count='exact').eq('event_id', event_id).eq('status', 'OK').gte('performance_value', min_realistic).lte('performance_value', max_realistic).execute()

    # Count results below realistic (likely wrong format)
    below = supabase.table('results').select('id', count='exact').eq('event_id', event_id).eq('status', 'OK').gt('performance_value', 0).lt('performance_value', min_realistic).execute()

    # Count results above realistic (also possibly wrong)
    above = supabase.table('results').select('id', count='exact').eq('event_id', event_id).eq('status', 'OK').gt('performance_value', max_realistic).execute()

    print(f"\n{'='*60}")
    print(f"{name} ({code}):")
    print(f"{'='*60}")
    print(f"  Totalt antall resultater: {total.count}")
    print(f"  Realistisk range ({min_realistic/100:.0f}s - {max_realistic/100:.0f}s): {realistic.count}")
    print(f"  Under realistisk (< {min_realistic/100:.0f}s): {below.count}")
    print(f"  Over realistisk (> {max_realistic/100:.0f}s): {above.count}")

    # Show some suspicious values
    if below.count > 0:
        print(f"\n  Eksempler på verdier under realistisk:")
        suspicious = supabase.table('results').select('performance_value').eq('event_id', event_id).eq('status', 'OK').gt('performance_value', 0).lt('performance_value', min_realistic).order('performance_value', desc=False).limit(20).execute()

        unique_vals = sorted(set(r['performance_value'] for r in suspicious.data))
        for val in unique_vals[:15]:
            # If this looks like M.SS format (e.g., 108 = 1:08)
            if val < 2000:
                mins = val // 100
                secs = val % 100
                if secs < 60:
                    correct = (mins * 60 + secs) * 100
                    print(f"    {val} -> mulig {mins}:{secs:02d} = {correct} ({correct/100:.2f}s)")
