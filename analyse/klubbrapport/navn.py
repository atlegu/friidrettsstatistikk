"""Navnekobling mellom klubbenes stipendlister og resultatdatabasen.

Stipendlister skrives for mennesker, ikke for maskiner. De samme personene
står med kortformer, mellomnavn som mangler i den ene kilden, ulike endelser
og aksenter. Denne modulen samler de reglene som har vist seg nødvendige, i
tre trinn fra strengest til mildest.
"""

import unicodedata


def folde(s: str) -> str:
    """Fjern aksenter, men behold æ, ø og å — de er egne bokstaver."""
    ut = []
    for tegn in unicodedata.normalize('NFD', s.lower()):
        if tegn in 'æøå' or unicodedata.category(tegn) != 'Mn':
            ut.append(tegn)
    return ''.join(ut)


def naer(a: str, b: str) -> bool:
    """Likt, eller ett tegn fra hverandre (Madelene/Madeleine)."""
    if a == b:
        return True
    if abs(len(a) - len(b)) > 1:
        return False
    kort, lang = sorted((a, b), key=len)
    for i in range(len(lang)):
        if lang[:i] + lang[i + 1:] == kort:
            return True
    return len(a) == len(b) and sum(x != y for x, y in zip(a, b)) == 1


def deler(navn: str):
    """Fornavn, og alle øvrige navneledd oppdelt også på bindestrek."""
    ord_ = [o for o in folde(navn).replace('.', '').split() if o]
    if not ord_:
        return '', set()
    resten = set()
    for o in ord_[1:]:
        resten.add(o)
        resten.update(d for d in o.split('-') if d)
    return ord_[0], resten


def finn(db_navn: str, liste: dict):
    """Slå opp et databasenavn mot en stipendliste. Returnerer (navn, info).

    Trinn 1  Likt fornavn og alle stipendlistens navneledd gjenfunnet.
             «Anthony Johnsen» -> «Anthony Ommundsen Johnsen».
    Trinn 2  Samme, med ett tegns avvik også på navneleddene.
             «Thale Leirfall Bremseth» -> «Thale Leirfall Bremset».
    Trinn 3  Bare fornavn og etternavn, når mellomnavnet mangler i basen.
             «Malin Ingeborg Nyfors» -> «Malin Nyfors». Godtas kun ved
             nøyaktig ett treff, ellers er det ikke trygt å gjette.
    """
    fornavn, ledd = deler(db_navn)

    for navn, info in liste.items():
        b_fornavn, b_ledd = deler(navn)
        if b_ledd and b_ledd <= ledd and naer(fornavn, b_fornavn):
            return navn, info

    for navn, info in liste.items():
        b_fornavn, b_ledd = deler(navn)
        if not b_ledd or not naer(fornavn, b_fornavn):
            continue
        if all(any(naer(bl, l) for l in ledd) for bl in b_ledd):
            return navn, info

    kandidater = []
    for navn, info in liste.items():
        b_ord = folde(navn).split()
        if len(b_ord) < 2 or not naer(fornavn, b_ord[0]):
            continue
        if any(naer(b_ord[-1], l) for l in ledd):
            kandidater.append((navn, info))
    return kandidater[0] if len(kandidater) == 1 else None
