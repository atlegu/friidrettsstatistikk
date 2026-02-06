"""Import alle resultater for Sondre Nordstad Moen fra minfriidrettsstatistikk.info"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

# Sondre Nordstad Moen sin ID
athlete_id = '2fd5db7b-5062-4d8f-8578-beecd00fa623'

# performance_value er i hundredeler (sekunder * 100) eller cm for lengde/kast
# For tider: 3:48.65 = 228.65 sek = 22865 hundredeler
results_to_import = [
    # Utendørs
    {'event': '1500 meter', 'code': '1500m', 'performance': '228.65', 'perf_value': 22865, 'date': '2014-07-11', 'meet': 'Norwegian Milers Club', 'city': 'Oslo', 'indoor': False},
    {'event': '2000 meter', 'code': '2000m', 'performance': '327.51', 'perf_value': 32751, 'date': '2017-08-09', 'meet': 'IAAF World Championships', 'city': 'London', 'indoor': False},
    {'event': '3000 meter', 'code': '3000m', 'performance': '472.55', 'perf_value': 47255, 'date': '2017-07-07', 'meet': 'Meeting Internazionale Città di Nembro', 'city': 'Nembro', 'indoor': False},
    {'event': '5000 meter', 'code': '5000m', 'performance': '800.16', 'perf_value': 80016, 'date': '2017-07-22', 'meet': 'NACHT van de Atletiek', 'city': 'Heusden-Zolder', 'indoor': False},
    {'event': '10000 meter', 'code': '10000m', 'performance': '1644.78', 'perf_value': 164478, 'date': '2019-08-31', 'meet': 'Stadionmila', 'city': 'Kristiansand', 'indoor': False},
    {'event': '20000 meter', 'code': '20000m', 'performance': '3411.60', 'perf_value': 341160, 'date': '2020-08-07', 'meet': 'Stadionmila', 'city': 'Kristiansand', 'indoor': False},
    {'event': '25000 meter', 'code': '25000m', 'performance': '4366.49', 'perf_value': 436649, 'date': '2020-06-11', 'meet': 'Impossible Games', 'city': 'Oslo', 'indoor': False},
    {'event': 'Halvmaraton', 'code': 'halvmaraton', 'performance': '3588.00', 'perf_value': 358800, 'date': '2017-10-22', 'meet': 'Medio Maratón Valencia', 'city': 'Valencia', 'indoor': False},
    {'event': 'Maraton', 'code': 'maraton', 'performance': '7548.00', 'perf_value': 754800, 'date': '2017-12-03', 'meet': 'Fukuoka International Open Marathon Championship', 'city': 'Fukuoka', 'indoor': False},
    {'event': '3000 meter hinder (91,4cm)', 'code': '3000mhinder_91_4cm', 'performance': '550.01', 'perf_value': 55001, 'date': '2008-06-14', 'meet': 'Stevne Florø', 'city': 'Florø', 'indoor': False},
    # Innendørs
    {'event': '3000 meter', 'code': '3000m', 'performance': '492.54', 'perf_value': 49254, 'date': '2015-01-24', 'meet': 'Steinkjer innendørs', 'city': 'Steinkjer', 'indoor': True},
]

def get_season_id(year, indoor):
    """Finn season_id basert på år og indoor/outdoor"""
    season_type = 'innendørs' if indoor else 'utendørs'
    result = supabase.table('seasons').select('id').eq('year', year).ilike('name', f'%{season_type}%').execute()
    if result.data:
        return result.data[0]['id']
    return None

def main():
    # Sjekk hvilke resultater vi allerede har
    existing = supabase.table('results_full').select('date, event_name, performance_value').eq('athlete_id', athlete_id).execute()
    existing_set = set()
    for r in existing.data:
        key = f"{r['date']}_{r['event_name']}_{r['performance_value']}"
        existing_set.add(key)

    print(f"Eksisterende resultater for Sondre: {len(existing.data)}")
    print()

    imported = 0
    skipped = 0
    errors = []

    for r in results_to_import:
        key = f"{r['date']}_{r['event']}_{r['perf_value']}"
        if key in existing_set:
            print(f"Finnes allerede: {r['event']} {r['performance']} ({r['date']})")
            skipped += 1
            continue

        # Finn event_id
        event_result = supabase.table('events').select('id').eq('name', r['event']).execute()
        if not event_result.data:
            event_result = supabase.table('events').select('id').eq('code', r['code']).execute()

        if not event_result.data:
            event_result = supabase.table('events').select('id, name').ilike('name', f"%{r['event'].split()[0]}%").ilike('name', f"%{r['event'].split()[-1]}%").execute()
            if event_result.data:
                print(f"  Fant alternativ øvelse: {event_result.data[0]['name']}")

        if not event_result.data:
            errors.append(f"Øvelse ikke funnet: {r['event']} / {r['code']}")
            continue

        event_id = event_result.data[0]['id']

        # Finn season_id
        year = int(r['date'][:4])
        season_id = get_season_id(year, r['indoor'])
        if not season_id:
            errors.append(f"Sesong ikke funnet: {year} {'innendørs' if r['indoor'] else 'utendørs'}")
            continue

        # Finn eller opprett meet
        meet_result = supabase.table('meets').select('id').ilike('name', f"%{r['meet'].split()[0]}%").eq('start_date', r['date']).execute()

        if not meet_result.data:
            new_meet = supabase.table('meets').insert({
                'name': r['meet'],
                'city': r['city'],
                'start_date': r['date'],
                'end_date': r['date'],
                'indoor': r['indoor'],
                'season_id': season_id
            }).execute()
            meet_id = new_meet.data[0]['id']
            print(f"  Opprettet stevne: {r['meet']} ({r['date']})")
        else:
            meet_id = meet_result.data[0]['id']

        # Opprett resultat
        try:
            new_result = supabase.table('results').insert({
                'athlete_id': athlete_id,
                'event_id': event_id,
                'meet_id': meet_id,
                'season_id': season_id,
                'performance': r['performance'],
                'performance_value': r['perf_value'],
                'date': r['date'],
                'status': 'OK'
            }).execute()

            print(f"✓ Importert: {r['event']} {r['performance']} ({r['date']}) - {r['meet']}")
            imported += 1
        except Exception as e:
            errors.append(f"Feil ved import av {r['event']}: {e}")

    print()
    print("=" * 50)
    print(f"Importert: {imported}")
    print(f"Hoppet over (fantes): {skipped}")
    if errors:
        print(f"Feil: {len(errors)}")
        for err in errors:
            print(f"  - {err}")

if __name__ == '__main__':
    main()
