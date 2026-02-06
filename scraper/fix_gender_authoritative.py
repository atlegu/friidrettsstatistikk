"""
Fix gender using authoritative event-based rules.

Height-specific events definitively indicate gender:
- 91.4cm hurdles/steeplechase = Men
- 106.7cm hurdles = Men
- 76.2cm/84cm hurdles/steeplechase = Women (junior women or senior women)
- 100m hurdles = Women
- 110m hurdles = Men
- 7-kamp (Heptathlon) = Women
- 10-kamp (Decathlon) = Men

This overrides any previous incorrect inference.
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))


def get_gender_events():
    """Get event IDs categorized by definitive gender"""
    events = supabase.table('events').select('id, name').execute()

    male_events = []
    female_events = []

    for e in events.data:
        name = e['name'].lower()

        # Men's events (91.4cm is senior men's height, 106.7cm is men's)
        if '91,4cm' in name or '91.4cm' in name:
            male_events.append(e['id'])
        elif '106,7cm' in name or '106.7cm' in name:
            male_events.append(e['id'])
        elif '100,0cm' in name or '100.0cm' in name or '100cm' in name:
            male_events.append(e['id'])  # 100cm is also men's height
        elif name.startswith('110 meter hekk'):
            male_events.append(e['id'])
        elif name == '10-kamp':
            male_events.append(e['id'])

        # Women's events (76.2cm and 84cm are women's heights)
        elif '76,2cm' in name or '76.2cm' in name:
            female_events.append(e['id'])
        elif '84,0cm' in name or '84.0cm' in name or '84cm' in name:
            female_events.append(e['id'])
        elif name.startswith('100 meter hekk') and '91' not in name and '100' not in name and '106' not in name:
            female_events.append(e['id'])
        elif name == '7-kamp':
            female_events.append(e['id'])

    return male_events, female_events


def main():
    print("=" * 60, flush=True)
    print("Fixing gender using authoritative event rules", flush=True)
    print("=" * 60, flush=True)
    print(flush=True)

    male_events, female_events = get_gender_events()
    print(f"Male-definitive events: {len(male_events)}", flush=True)
    print(f"Female-definitive events: {len(female_events)}", flush=True)
    print(flush=True)

    # Load all results for these events
    print("Loading results for gender-specific events...", flush=True)

    # Get athletes who have results in male events
    male_athletes = set()
    for event_id in male_events:
        results = supabase.table('results').select('athlete_id').eq('event_id', event_id).execute()
        for r in results.data:
            male_athletes.add(r['athlete_id'])

    print(f"Athletes with male-specific event results: {len(male_athletes)}", flush=True)

    # Get athletes who have results in female events
    female_athletes = set()
    for event_id in female_events:
        results = supabase.table('results').select('athlete_id').eq('event_id', event_id).execute()
        for r in results.data:
            female_athletes.add(r['athlete_id'])

    print(f"Athletes with female-specific event results: {len(female_athletes)}", flush=True)
    print(flush=True)

    # Check for conflicts (athletes in both - shouldn't happen)
    conflicts = male_athletes & female_athletes
    if conflicts:
        print(f"WARNING: {len(conflicts)} athletes have results in both male and female events!", flush=True)

    # Update athletes to correct gender
    print("Updating athlete genders...", flush=True)

    # Fix males
    male_list = list(male_athletes - conflicts)
    batch_size = 100
    fixed_male = 0
    for i in range(0, len(male_list), batch_size):
        batch = male_list[i:i + batch_size]
        # Only update if currently wrong
        result = supabase.table('athletes').update({'gender': 'M'}).in_('id', batch).neq('gender', 'M').execute()
        fixed_male += len(result.data) if result.data else 0

    print(f"  Fixed to Male: {fixed_male}", flush=True)

    # Fix females
    female_list = list(female_athletes - conflicts)
    fixed_female = 0
    for i in range(0, len(female_list), batch_size):
        batch = female_list[i:i + batch_size]
        result = supabase.table('athletes').update({'gender': 'F'}).in_('id', batch).neq('gender', 'F').execute()
        fixed_female += len(result.data) if result.data else 0

    print(f"  Fixed to Female: {fixed_female}", flush=True)

    print(flush=True)
    print("=" * 60, flush=True)
    print(f"Total fixed: {fixed_male + fixed_female}", flush=True)
    print("=" * 60, flush=True)


if __name__ == '__main__':
    main()
