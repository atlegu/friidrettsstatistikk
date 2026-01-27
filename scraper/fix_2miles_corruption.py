"""Fiks korrupte 2 miles resultater der tider er lagret som sekunder i stedet for hundredeler"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

def main():
    # Finn 2 miles event
    event_result = supabase.table('events').select('id, name, code').eq('code', '2miles').execute()
    if not event_result.data:
        print("Fant ikke 2 miles øvelse!")
        return

    event_id = event_result.data[0]['id']
    print(f"2 miles event_id: {event_id}")
    print()

    # Finn alle 2 miles resultater med suspekt lav performance_value
    # En 2 miles tid på f.eks. 8:44 = 524.40 sek = 52440 hundredeler
    # Resultater under 30000 (5 min) er helt feil for 2 miles
    results = supabase.table('results').select('id, athlete_id, performance, performance_value, date').eq('event_id', event_id).lt('performance_value', 30000).execute()

    print(f"Fant {len(results.data)} korrupte 2 miles resultater:")
    print()

    for r in results.data:
        # Hent utøvernavn
        athlete = supabase.table('athletes').select('full_name').eq('id', r['athlete_id']).execute()
        athlete_name = athlete.data[0]['full_name'] if athlete.data else 'Ukjent'

        old_value = r['performance_value']
        performance = r['performance']

        # Analyser hva som er galt
        # Hvis performance er f.eks. "8:44.12", da burde value være 52412
        # Men hvis value er 844, har noen lagret sekunder*100 i stedet for totale hundredeler

        print(f"  {athlete_name}: performance='{performance}', value={old_value}, date={r['date']}")

        # Parse performance for å finne riktig verdi
        if ':' in performance:
            # Standard format: "8:44.12"
            parts = performance.split(':')
            if len(parts) == 2:
                minutes = int(parts[0])
                seconds_part = parts[1]
                if '.' in seconds_part:
                    seconds = float(seconds_part)
                else:
                    seconds = float(seconds_part)
                correct_value = int(minutes * 6000 + seconds * 100)
                correct_perf = f"{minutes}:{seconds_part}"
        else:
            # Format uten kolon: "8.44" betyr 8 minutter og 44 sekunder
            # Disse må konverteres til riktig format
            parts = performance.split('.')
            if len(parts) == 2:
                minutes = int(parts[0])
                seconds = int(parts[1])
                # Håndter case der sekunder kan være 2 eller 3 siffer
                if seconds < 60:
                    # f.eks. "8.44" = 8:44.00
                    correct_value = int(minutes * 6000 + seconds * 100)
                    correct_perf = f"{minutes}:{seconds:02d}.00"
                else:
                    # f.eks. "8.441" = 8:44.1 (sjeldent)
                    correct_value = int(minutes * 6000 + (seconds / 10) * 100)
                    correct_perf = f"{minutes}:{int(seconds/10):02d}.{seconds % 10}0"
            else:
                print(f"    -> Ukjent format, hopper over")
                continue

        print(f"    -> Riktig verdi: {correct_value}, riktig format: '{correct_perf}'")

        # Oppdater både performance og performance_value
        try:
            supabase.table('results').update({
                'performance': correct_perf,
                'performance_value': correct_value
            }).eq('id', r['id']).execute()
            print(f"    ✓ Oppdatert!")
        except Exception as e:
            print(f"    ✗ Feil ved oppdatering: {e}")

    print()
    print("Ferdig! Sjekker nå topp 10 på 2 miles:")
    print()

    # Verifiser med å hente topp 10
    top_results = supabase.table('results_full').select('athlete_name, performance, performance_value, date').eq('event_code', '2miles').eq('gender', 'M').order('performance_value').limit(10).execute()

    for i, r in enumerate(top_results.data, 1):
        print(f"  {i}. {r['athlete_name']}: {r['performance']} ({r['date']})")

if __name__ == '__main__':
    main()
