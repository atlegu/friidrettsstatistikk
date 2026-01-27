"""Fiks 2 miles resultater der performance vises som sekunder i stedet for mm:ss.xx format"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

def seconds_to_time_format(seconds_str):
    """Konverter f.eks. '474.10' til '7:54.10'"""
    seconds = float(seconds_str)
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60

    # Behold desimalplasser fra original
    if '.' in seconds_str:
        decimal_part = seconds_str.split('.')[1]
        decimal_places = len(decimal_part)
        return f"{minutes}:{remaining_seconds:0{3+decimal_places}.{decimal_places}f}"
    else:
        return f"{minutes}:{remaining_seconds:05.2f}"

def main():
    # Finn 2 miles event
    event_result = supabase.table('events').select('id').eq('code', '2miles').execute()
    event_id = event_result.data[0]['id']
    print(f"2 miles event_id: {event_id}")
    print()

    # Hent alle 2 miles resultater der performance ikke har kolon
    results = supabase.table('results').select('id, athlete_id, performance, performance_value, date').eq('event_id', event_id).execute()

    updated = 0
    for r in results.data:
        if ':' not in r['performance']:
            old_perf = r['performance']
            new_perf = seconds_to_time_format(old_perf)

            # Hent utøvernavn
            athlete = supabase.table('athletes').select('full_name').eq('id', r['athlete_id']).execute()
            name = athlete.data[0]['full_name'] if athlete.data else 'Ukjent'

            print(f"  {name}: '{old_perf}' -> '{new_perf}'")

            try:
                supabase.table('results').update({
                    'performance': new_perf
                }).eq('id', r['id']).execute()
                updated += 1
            except Exception as e:
                print(f"    Feil: {e}")

    print()
    print(f"Oppdatert {updated} resultater")
    print()
    print("Topp 10 på 2 miles (menn):")

    top_results = supabase.table('results_full').select('athlete_name, performance, performance_value, date').eq('event_code', '2miles').eq('gender', 'M').order('performance_value').limit(10).execute()

    for i, r in enumerate(top_results.data, 1):
        print(f"  {i}. {r['athlete_name']}: {r['performance']} ({r['date']})")

if __name__ == '__main__':
    main()
