import os
from supabase import create_client
from dotenv import load_dotenv
from difflib import SequenceMatcher
from collections import defaultdict

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("Henter alle utøvere...")

# Get all athletes
all_athletes = []
offset = 0
batch_size = 1000

while True:
    result = supabase.table('athletes').select('id, first_name, last_name, full_name, birth_year, gender').range(offset, offset + batch_size - 1).execute()
    if not result.data:
        break
    all_athletes.extend(result.data)
    offset += batch_size
    print(f"  Hentet {len(all_athletes)} utøvere...")

print(f"\nTotalt: {len(all_athletes)} utøvere")

# Group by last name
by_last_name = defaultdict(list)
for a in all_athletes:
    last = (a.get('last_name') or '').strip().lower()
    if last:
        by_last_name[last].append(a)

def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def normalize_name(name):
    """Normalize common Norwegian name variations"""
    if not name:
        return ""
    n = name.lower().strip()
    n = n.replace('th', 't')
    n = n.replace('tt', 't')
    n = n.replace('nn', 'n')
    n = n.replace('ll', 'l')
    return n

print("\nSøker etter potensielle duplikater (samme etternavn)...")
potential_duplicates = []

# Check within same last name groups only (much faster)
for last_name, athletes in by_last_name.items():
    if len(athletes) < 2:
        continue

    for i, a1 in enumerate(athletes):
        for a2 in athletes[i+1:]:
            first1 = a1.get('first_name') or ''
            first2 = a2.get('first_name') or ''

            if not first1 or not first2:
                continue

            # Skip if names are identical
            if first1.lower() == first2.lower():
                continue

            # Check if first names are similar
            sim = similar(first1, first2)
            norm_sim = similar(normalize_name(first1), normalize_name(first2))

            is_potential = False
            reason = ""

            if norm_sim >= 0.85 and sim < 1.0:
                is_potential = True
                reason = f"Normalisert likhet: {norm_sim:.0%}"
            elif sim >= 0.8 and sim < 1.0:
                is_potential = True
                reason = f"Navnelikhet: {sim:.0%}"
            elif len(first1) > 2 and len(first2) > 2 and abs(len(first1) - len(first2)) <= 1 and sim >= 0.7:
                is_potential = True
                reason = f"Mulig skrivefeil ({sim:.0%})"

            if is_potential:
                same_gender = a1.get('gender') == a2.get('gender')
                by1 = a1.get('birth_year')
                by2 = a2.get('birth_year')

                # Only include if same gender or unknown gender
                if same_gender or (not a1.get('gender') or not a2.get('gender')):
                    potential_duplicates.append({
                        'a1': a1,
                        'a2': a2,
                        'reason': reason,
                        'same_gender': same_gender,
                        'birth_diff': abs(by1 - by2) if by1 and by2 else None
                    })

# Sort: same gender first, then by birth year difference
potential_duplicates.sort(key=lambda x: (not x['same_gender'], x['birth_diff'] or 999))

print(f"\nFant {len(potential_duplicates)} potensielle duplikater:\n")
print("=" * 110)

for i, d in enumerate(potential_duplicates, 1):
    a1 = d['a1']
    a2 = d['a2']
    name1 = f"{a1.get('first_name', '')} {a1.get('last_name', '')}"
    name2 = f"{a2.get('first_name', '')} {a2.get('last_name', '')}"
    by1 = a1.get('birth_year') or '?'
    by2 = a2.get('birth_year') or '?'
    g1 = a1.get('gender') or '?'
    g2 = a2.get('gender') or '?'

    print(f"{i:3}. {name1:<35} (f.{by1}, {g1}) | {a1['id']}")
    print(f"     {name2:<35} (f.{by2}, {g2}) | {a2['id']}")
    print(f"     Grunn: {d['reason']}")
    print()
