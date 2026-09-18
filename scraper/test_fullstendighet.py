"""Sjekk at sidene viser ALT, ikke bare de første tusen radene.

HVORFOR DENNE FINNES
--------------------
PostgREST i Supabase leverer aldri mer enn 1 000 rader per spørring. Ber du
om 5 000, får du 1 000 - med HTTP 200, uten feil og uten advarsel. En
avkortet henting er ikke til å skille fra en som fikk alt.

Det gjorde at flere sider talte opp nøkkeltall fra det de fikk og viste
tallet som et faktum. Stevnesiden sto med «Resultater 1 000» for
Tyrvinglekene, som har 3 299. NM-lista viste 64 kvalifiserte av 138.

Feilen ble funnet fire ganger, én side om gangen. Denne testen leter etter
den systematisk: den regner ut fasiten selv, henter den ferdige sida, og
sammenlikner. Den velger alltid de STØRSTE tilfellene, for det er bare der
taket slår inn.

FASITEN ER UAVHENGIG AV APPEN
-----------------------------
Totaler hentes med PostgREST sin egen `count=exact`, som teller i databasen
og ikke kan avkortes - det er nettopp det som avslørte feilen. Antall unike
øvelser og utøvere regnes ut ved at testen selv blar gjennom alle radene og
teller i Python. Ingenting av dette går gjennom koden som testes.

KJØRING
-------
    python test_fullstendighet.py                     # mot localhost:3000
    python test_fullstendighet.py --url https://www.friidrettsresultater.no
    python test_fullstendighet.py --antall 5          # flere tilfeller per type

Avslutter med kode 1 hvis noe avviker, så den kan brukes i CI.
"""

import argparse
from datetime import datetime, timedelta
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import requests
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv(Path(__file__).parent / '.env')

URL = os.environ['SUPABASE_URL']
NOKKEL = os.environ['SUPABASE_SERVICE_KEY']
HODER = {'apikey': NOKKEL, 'Authorization': f'Bearer {NOKKEL}'}

sb: Client = create_client(URL, NOKKEL)

# Tallene på sidene har hardt mellomrom som tusenskille.
MELLOMROM = re.compile(r'[\s  ]')


def tall(s: str | None) -> int | None:
    if s is None:
        return None
    reint = MELLOMROM.sub('', s)
    return int(reint) if reint.isdigit() else None


# ------------------------------------------------------------------ fasit

def antall_i_basen(tabell: str, filter_: str) -> int:
    """Eksakt antall rader, talt i databasen.

    `count=exact` med `head=true` returnerer totalen i Content-Range uten å
    sende en eneste rad, så tusenradstaket gjelder ikke. Dette er den samme
    mekanismen som avslørte avkortingen: «content-range: 0-999/2430».
    """
    r = requests.get(f'{URL}/rest/v1/{tabell}?select=id&{filter_}',
                     headers={**HODER, 'Prefer': 'count=exact'},
                     timeout=180)
    r.raise_for_status()
    return int(r.headers['content-range'].split('/')[1])


def alle_rader(tabell: str, kolonner: str, filter_: str) -> list[dict]:
    """Bla gjennom alle radene. Testen gjør sin egen sideinndeling."""
    ut, side = [], 0
    while True:
        r = requests.get(
            f'{URL}/rest/v1/{tabell}?select={kolonner}&{filter_}&order=id.asc',
            headers={**HODER, 'Range-Unit': 'items',
                     'Range': f'{side * 1000}-{side * 1000 + 999}'},
            timeout=180)
        r.raise_for_status()
        rader = r.json()
        ut.extend(rader)
        if len(rader) < 1000:
            return ut
        side += 1
        if side > 50:
            raise RuntimeError(f'{tabell}: over 50 000 rader, noe er galt')


# ------------------------------------------------------- lesing av sidene

def noekkeltall_sidetopp(html: str) -> dict[str, str]:
    """Nøkkeltall på stevne- og klubbsider (SideTopp bruker dt/dd)."""
    return dict(re.findall(r'<dt[^>]*>(.*?)</dt><dd[^>]*>(.*?)</dd>', html))


def noekkeltall_utover(html: str) -> dict[str, str]:
    """Nøkkeltall på utøverprofilen (egen oppbygning)."""
    return dict(re.findall(
        r'uppercase tracking-\[0\.07em\][^>]*>([^<]+)</div>'
        r'<div class="text-xl[^>]*>([^<]+)</div>', html))


def antall_rader(html: str) -> int:
    """Rader i resultattabellene, uten overskriftsradene."""
    return len(re.findall(r'<tr\b', html)) - len(re.findall(r'<thead\b', html))


def ren_tekst(html: str) -> str:
    """Bare den synlige teksten.

    React deler opp tekst i egne noder og skiller dem med tomme HTML-
    kommentarer, så «Viser 120 av 2 430 klubber» står som
    «Viser <!-- -->120<!-- --> av<!-- --> <!-- -->2 430<!-- --> klubber».
    Uten denne ville regexene måtte ta høyde for det.
    """
    s = re.sub(r'<script\b.*?</script>', ' ', html, flags=re.S)
    s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'[\s  ]+', ' ', s)


def hent(url: str) -> str:
    """Hent en side fra nettstedet.

    Produksjonen svarer 429 til klienter uten vanlig nettleser-UA, og til
    for tette kall. Derfor en nettleser-UA, en kort pause, og ett nytt
    forsøk etter en lengre pause dersom det likevel skjer.
    """
    hoder = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                            'AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/128.0 Safari/537.36 test_fullstendighet')}
    for forsok in (1, 2):
        time.sleep(0.5)
        r = requests.get(url, headers=hoder, timeout=300)
        if r.status_code == 429 and forsok == 1:
            time.sleep(15)
            continue
        r.raise_for_status()
        return r.text
    raise RuntimeError('uoppnåelig')


# ----------------------------------------------------------------- rammen

@dataclass
class Avvik:
    side: str
    felt: str
    vist: object
    fasit: object
    merknad: str = ''


@dataclass
class Resultat:
    sjekket: int = 0
    avvik: list[Avvik] = field(default_factory=list)

    def lik(self, side, felt, vist, fasit, merknad=''):
        if vist != fasit:
            self.avvik.append(Avvik(side, felt, vist, fasit, merknad))


# ---------------------------------------------------------------- sjekkene

def sjekk_stevner(base: str, n: int, res: Resultat):
    """De største stevnene. Taket slo inn for 171 av dem."""
    for k in sb.rpc('test_storste_stevner', {'p_antall': n}).execute().data:
        navn = f"stevne «{k['name'][:44]}»"
        filt = f"meet_id=eq.{k['id']}"

        fasit_res = antall_i_basen('results', filt)
        rader = alle_rader('results_full', 'id,event_id,athlete_id', filt)
        fasit_ovelser = len({r['event_id'] for r in rader})
        fasit_utovere = len({r['athlete_id'] for r in rader})

        html = hent(f"{base}/stevner/{k['id']}")
        vist = noekkeltall_sidetopp(html)
        res.sjekket += 1

        res.lik(navn, 'Resultater', tall(vist.get('Resultater')), fasit_res)
        res.lik(navn, 'Øvelser', tall(vist.get('Øvelser')), fasit_ovelser)
        res.lik(navn, 'Utøvere', tall(vist.get('Utøvere')), fasit_utovere)
        res.lik(navn, 'rader i tabellen', antall_rader(html), fasit_res,
                'nøkkeltallet kan stemme selv om tabellen er avkortet')


def sjekk_utovere(base: str, n: int, res: Resultat):
    """Utøverne med flest resultater. 37 har over tusen."""
    for k in sb.rpc('test_storste_utovere', {'p_antall': n}).execute().data:
        navn = f"utøver «{k['full_name']}»"
        filt = f"athlete_id=eq.{k['id']}"

        fasit_res = antall_i_basen('results', filt)
        rader = alle_rader('results_full', 'id,meet_id,event_id', filt)
        fasit_stevner = len({r['meet_id'] for r in rader})
        fasit_ovelser = len({r['event_id'] for r in rader})

        html = hent(f"{base}/utover/{k['id']}")
        vist = noekkeltall_utover(html)
        res.sjekket += 1

        res.lik(navn, 'Resultater', tall(vist.get('Resultater')), fasit_res)
        res.lik(navn, 'Stevner', tall(vist.get('Stevner')), fasit_stevner)
        res.lik(navn, 'Øvelser', tall(vist.get('Øvelser')), fasit_ovelser)


def sjekk_klubber(base: str, n: int, res: Resultat):
    """De største klubbene. Tallene leses fra klubb_bruk, som er en
    materialisert visning - testen sjekker at den ikke er utdatert."""
    storste = (sb.table('klubb_bruk')
                 .select('id,name')
                 .gt('resultater', 0)
                 .order('resultater', desc=True)
                 .limit(n).execute().data)

    for k in storste:
        navn = f"klubb «{k['name']}»"

        # De største klubbene har 68 000 resultater. Å bla gjennom dem over
        # REST tar for lang tid, så her telles det i basen i stedet.
        fasit = sb.rpc('test_klubb_fasit', {'p_klubb': k['id']}).execute().data[0]
        fasit_res = fasit['resultater']
        fasit_utovere = fasit['utovere']

        html = hent(f"{base}/klubber/{k['id']}")
        vist = noekkeltall_sidetopp(html)
        res.sjekket += 1

        res.lik(navn, 'Resultater', tall(vist.get('Resultater')), fasit_res,
                'klubb_bruk kan være utdatert; kjør refresh_plattform_statistikk()')
        res.lik(navn, 'Utøvere', tall(vist.get('Utøvere')), fasit_utovere,
                'klubb_bruk kan være utdatert; kjør refresh_plattform_statistikk()')


def sjekk_lister(base: str, res: Resultat):
    """Listesidene skal si «viser N av M», og M skal stemme."""
    fasit = antall_i_basen('klubb_bruk', 'resultater=gt.0')
    tekst = ren_tekst(hent(f"{base}/klubber"))
    res.sjekket += 1
    m = re.search(r'av ([0-9 ]+?) klubber', tekst)
    res.lik('/klubber', 'totalt', tall(m.group(1)) if m else None, fasit)

    fasit = antall_i_basen('meets', 'id=not.is.null')
    tekst = ren_tekst(hent(f"{base}/stevner"))
    res.sjekket += 1
    m = re.search(r'av ([0-9 ]+?) stevner', tekst)
    res.lik('/stevner', 'totalt', tall(m.group(1)) if m else None, fasit)


def sjekk_forsiden(base: str, res: Resultat):
    """Forsidetallene kommer fra en materialisert visning, ikke fra en
    opptelling. Testen sjekker at visningen er i takt med basen."""
    mv = sb.table('plattform_statistikk').select('*').single().execute().data
    res.sjekket += 1
    utdatert = f"visningen ble sist oppdatert {mv['oppdatert']}"
    res.lik('forsiden', 'utøvere', mv['antall_utovere'],
            antall_i_basen('athletes', 'id=not.is.null'), utdatert)
    res.lik('forsiden', 'stevner', mv['antall_stevner'],
            antall_i_basen('meets', 'id=not.is.null'), utdatert)
    res.lik('forsiden', 'klubber', mv['antall_klubber'],
            antall_i_basen('clubs', 'id=not.is.null'), utdatert)


def sjekk_nm(base: str, res: Resultat):
    """NM-lista. Her lå den verste feilen: 64 viste av 138 kvalifiserte.

    Kravene speiler championship-config.ts. Blir kravene endret der, må de
    endres her - det er med vilje: to uavhengige kilder, ellers tester vi
    koden mot seg selv.
    """
    krav = [
        # mesterskap, kjønn, øvelse, krav (hundredeler), fra, til, ekstra filtre
        ('nm-senior-2026', 'M', '100m', 1130, '2025-01-01', '2026-07-09',
         'is_manual_time=not.is.true&is_wind_legal=is.true'),
        ('nm-senior-2026', 'F', '100m', 1280, '2025-01-01', '2026-07-09',
         'is_manual_time=not.is.true&is_wind_legal=is.true'),
        ('nm-senior-2026', 'M', '200m', 2280, '2025-01-01', '2026-07-09',
         'is_manual_time=not.is.true&is_wind_legal=is.true'),
        ('nm-senior-2026', 'M', '400m', 4999, '2025-01-01', '2026-07-09',
         'is_manual_time=not.is.true'),
        ('nm-senior-2026', 'F', '400m', 5899, '2025-01-01', '2026-07-09',
         'is_manual_time=not.is.true'),
    ]

    for mesterskap, kjonn, ovelse, grense, fra, til, ekstra in krav:
        filt = (f'event_code=eq.{ovelse}&gender=eq.{kjonn}&status=eq.OK'
                f'&performance_value=gt.0&performance_value=lte.{grense}'
                f'&date=gte.{fra}&date=lte.{til}&{ekstra}')
        rader = alle_rader('results_full', 'id,athlete_id', filt)
        fasit = len({r['athlete_id'] for r in rader})

        html = hent(f"{base}/mesterskap/{mesterskap}?gender={kjonn}&event={ovelse}")
        res.sjekket += 1
        m = re.search(r'([0-9 ]+) kvalifiserte', ren_tekst(html))
        navn = f"NM {ovelse} {kjonn}"
        res.lik(navn, 'kvalifiserte', tall(m.group(1)) if m else None, fasit)
        res.lik(navn, 'rader i tabellen', antall_rader(html), fasit)


def sjekk_klubb_alltime(base: str, res: Resultat):
    """Klubbenes all-time-lister. Sto med «.limit(50000)», fikk 1 000, og
    plukket deretter ett resultat per utøver: Tyrving 60 m kvinner viste 43
    utøvere av 668.

    Verste tilfelle er den største klubben, 60 m (løpes innendørs, mange
    starter), alle aldre, alle baner. Sida deler lista opp i sider à 100, og
    totalen leses av den siste sideknappen («601-668»).
    """
    klubb = (sb.table('klubb_bruk').select('id,name').gt('resultater', 0)
               .order('resultater', desc=True).limit(1).execute().data[0])
    ovelse = sb.table('events').select('id').eq('name', '60 meter') \
               .limit(1).execute().data[0]['id']

    for kjonn in ('F', 'M'):
        filt = (f"club_id=eq.{klubb['id']}&event_id=eq.{ovelse}&gender=eq.{kjonn}"
                f"&status=eq.OK&performance_value=gt.0"
                f"&is_manual_time=not.is.true&is_wind_legal=is.true")
        rader = alle_rader('results_full', 'id,athlete_id', filt)
        fasit = len({r['athlete_id'] for r in rader})

        url = (f"{base}/klubber/{klubb['id']}/statistikk/all-time"
               f"?event={ovelse}&gender={kjonn}&age=all&venue=all")
        res.sjekket += 1
        navn = f"all-time «{klubb['name']}» 60 m {kjonn}"

        # Siste sideknapp er «601-668»; står det bare én side, ingen knapper.
        # Dev-serveren kan svare med et tomt skall midt i en omkompilering,
        # så en side helt uten rader hentes én gang til før den telles.
        for _ in (1, 2):
            html = hent(url)
            knapper = re.findall(r'>(\d+)-(\d+)<', html)
            vist = max((int(b) for _, b in knapper), default=antall_rader(html))
            if vist > 0 or fasit == 0:
                break
            time.sleep(5)
        res.lik(navn, 'utøvere', vist, fasit)


def sjekk_vindflagg(base: str, res: Resultat):
    """is_wind_legal skal foelge regelen i vindflagg.sql, rad for rad.

    Flagget hadde standardverdi true og ble bare satt til false ved vind
    over 2,0. Dermed sto 2 842 medvindsloep som lovlige, og 44 169 loep med
    maalt, lovlig vind sto som NULL. En trigger setter det naa; denne
    sjekken fanger opp om en ny importvei omgaar den.
    """
    res.sjekket += 1
    avvik = sb.rpc('test_vindflagg_avvik').execute().data[0]
    for felt, n in avvik.items():
        res.lik('is_wind_legal', felt, n, 0,
                'kjoer rett_vindflagg(event_id) for hver oevelse')


def sjekk_dubletter(base: str, res: Resultat):
    """Ingen rader skal vaere like paa alt unntatt vind.

    Den unike indeksen omfatter wind, saa da kilden rettet en vindverdi og
    stevnet ble hentet paa nytt, slapp den nye raden inn ved siden av den
    gamle. 187 slike par fantes 15.09.2026. Importen avstemmer naa mot
    kilden foer den legger inn; denne sjekken fanger opp om det glipper.
    Sjekkes per oevelse - hele tabellen paa én gang roek paa gatewayen.
    """
    res.sjekket += 1
    n = 0
    for e in sb.table('events').select('id').execute().data:
        # Bare grupper der én rad mangler vind: det er mekanismen vi kjenner.
        # To rader med hver sin maalte vind kan vaere forsoek og finale med
        # samme tid, og kan ikke avgjoeres maskinelt.
        n += sum(1 for g in sb.rpc('test_innholdsdubletter', {'p_event_id': e['id']}).execute().data
                 if any(w is None for w in g['winds']) and any(w is not None for w in g['winds']))
    res.lik('results', 'dublettpar (likt unntatt vind, en uten maaling)', n, 0,
            'kjoer rydd_innholdsdubletter.py')


def sjekk_utoveravdrift(base: str, res: Resultat):
    """Samme resultat skal ikke ligge under to utoever-id-er med samme navn.

    Da matchingen ikke traff (lagret utoever uten foedselsaar/kjoenn) opprettet
    importen en ny utoever og la resultatet inn en gang til - 56 rader og 16
    utoevere paa én kjoering 15.09.2026. Avstemmingen kjenner naa igjen raden
    paa navn innenfor stevnet. Denne sjekken fanger opp om det glipper.
    """
    res.sjekket += 1
    n = 0
    for e in sb.table('events').select('id').execute().data:
        n += len(sb.rpc('test_utoveravdrift', {'p_event_id': e['id']}).execute().data)
    res.lik('results', 'samme resultat under to utoever-id-er med samme navn', n, 0,
            'utoeverdubletter; se opprydding')


def sjekk_stevnedubletter(base: str, res: Resultat):
    """Samme resultat skal ikke ligge i to stevneposter.

    Importkjoeringene i januar 2026 la samme stevne inn baade som «Bærum,
    Tyrvinglekene» og «Tyrvinglekene», og slo stevner med samme navn samme
    dag sammen til ett. 4 925 stevnepar med felles resultater 18.09.2026.
    get_or_create_meet() finner naa stevnet paa kildens stevne-id og sted.
    Ryddes med rydd_stevnedubletter.py. Sjekkes for siste 400 dager.
    """
    res.sjekket += 1
    fra = (datetime.now() - timedelta(days=400)).strftime('%Y-%m-%d')
    d = sb.rpc('test_stevnedubletter', {'p_fra': fra}).execute().data[0]
    res.lik('results', f'stevnepar med felles resultater siden {fra}', d['par'], 0,
            'kjoer rydd_stevnedubletter.py')


# ------------------------------------------------------------------- main

SJEKKER = {
    'stevnedubletter': lambda base, n, res: sjekk_stevnedubletter(base, res),
    'vindflagg': lambda base, n, res: sjekk_vindflagg(base, res),
    'dubletter': lambda base, n, res: sjekk_dubletter(base, res),
    'avdrift': lambda base, n, res: sjekk_utoveravdrift(base, res),
    'stevner': lambda base, n, res: sjekk_stevner(base, n, res),
    'utovere': lambda base, n, res: sjekk_utovere(base, n, res),
    'klubber': lambda base, n, res: sjekk_klubber(base, n, res),
    'lister': lambda base, n, res: sjekk_lister(base, res),
    'forsiden': lambda base, n, res: sjekk_forsiden(base, res),
    'nm': lambda base, n, res: sjekk_nm(base, res),
    'alltime': lambda base, n, res: sjekk_klubb_alltime(base, res),
}


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--url', default='http://localhost:3000')
    ap.add_argument('--antall', type=int, default=3,
                    help='Hvor mange av de største som sjekkes per type')
    ap.add_argument('--bare', nargs='+', choices=list(SJEKKER),
                    help='Kjør bare disse sjekkene')
    args = ap.parse_args()
    base = args.url.rstrip('/')

    res = Resultat()
    print(f"Sjekker {base}")
    print(f"Fasit hentes fra {URL}\n")

    for navn in (args.bare or list(SJEKKER)):
        print(f"  {navn:10}", end=' ', flush=True)
        foer = len(res.avvik)
        try:
            SJEKKER[navn](base, args.antall, res)
            nye = len(res.avvik) - foer
            print('ok' if nye == 0 else f'{nye} AVVIK')
        except Exception as e:
            print(f'FEIL: {e}')
            res.avvik.append(Avvik(navn, 'kjøring', 'unntak', str(e)))

    print(f"\n{res.sjekket} sider sjekket.")
    if not res.avvik:
        print("Ingen avvik. Alle tall på sidene stemmer med basen.")
        return 0

    print(f"\n{len(res.avvik)} AVVIK\n")
    for a in res.avvik:
        print(f"  {a.side}")
        print(f"    {a.felt}: siden viser {a.vist}, basen sier {a.fasit}")
        if a.merknad:
            print(f"    ({a.merknad})")
    return 1


if __name__ == '__main__':
    sys.exit(main())
