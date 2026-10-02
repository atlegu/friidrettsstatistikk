import json, sys, unicodedata
nesse = json.load(open(sys.argv[1]))
ours = [l.split('|') for l in open(sys.argv[2]).read().strip().split('\n')]

def key(n):
    p = [w for w in n.lower().replace('-',' ').split() if len(w)>1]
    return (p[0], p[-1]) if len(p)>=2 else (n.lower(), '')

# aldersgrense: 16 år i 2026 -> født 2010 eller tidligere
ours_elig = [o for o in ours if o[1].isdigit() and int(o[1]) <= 2010]
ours_young = [o for o in ours if o[1].isdigit() and int(o[1]) > 2010]

nk = {key(x['navn']): x for x in nesse}
ok = {key(o[0]): o for o in ours_elig}

only_ours  = [ok[k] for k in ok if k not in nk]
only_nesse = [nk[k] for k in nk if k not in ok]
both       = [k for k in ok if k in nk]

print(f"Excel (Jo Nesse):        {len(nesse)} utøvere")
print(f"Vår base, alle:          {len(ours)}")
print(f"Vår base, 16 år eller eldre: {len(ours_elig)}  (utelatt {len(ours_young)} for unge)")
print(f"Match på begge lister:   {len(both)}")
print()
print(f"--- Kun i vår base ({len(only_ours)}) ---")
for o in sorted(only_ours, key=lambda x: x[2]): print(f"   {o[2]}  {o[0]} ({o[1]})")
print()
print(f"--- Kun hos Jo Nesse ({len(only_nesse)}) ---")
for n in only_nesse: print(f"   {n['res']}  {n['navn']} ({n['fodt']})")
