"""
Unified update script: scrapes new meets and imports results directly to Supabase.
Combines scrape_new_meets.py + import_new_meets.py into one command with no CSV intermediate.

Usage:
    python update_results.py              # Auto-detect season, update everything
    python update_results.py --indoor     # Force indoor season
    python update_results.py --outdoor    # Force outdoor season
    python update_results.py --from-date 2025-12-01
    python update_results.py --dry-run    # Show what would be imported without importing
"""

import argparse
import os
import re
import time
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================
# Configuration
# ============================================================
BASE_URL = "https://www.minfriidrettsstatistikk.info/php"
REQUEST_DELAY = 0.3  # seconds between requests
MIN_RESULTS_THRESHOLD = 10  # Meets with fewer results are considered incomplete
# Andel av kildens resultater som må mangle før --verify henter stevnet på nytt.
# Små avvik er normalt: basen kan slå sammen to kildestevner til én stevnerad.
VERIFY_MANGEL_ANDEL = 0.05

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def vent_pa_nett(vert: str, forsok: int = 30, pause: int = 60) -> bool:
    """Vent til DNS svarer for `vert`, i stedet for å dø på et nettverksfall.

    En full historisk kjøring tar over et døgn. Da er det påregnelig at nettet
    forsvinner en periode. Uten dette døde hver sesong etter noen sekunder med

        httpx.ConnectError: nodename nor servname provided, or not known

    og elleve sesonger ble hoppet over på under ett minutt til sammen.
    """
    import socket
    for n in range(1, forsok + 1):
        try:
            socket.gethostbyname(vert)
            if n > 1:
                logger.info(f"Nettet er tilbake etter {n - 1} forsøk")
            return True
        except socket.gaierror:
            logger.warning(f"Ingen DNS for {vert} — venter {pause}s (forsøk {n}/{forsok})")
            time.sleep(pause)
    logger.error(f"Ga opp å nå {vert} etter {forsok} forsøk")
    return False


def _slaa_av_http2():
    """Tving HTTP/1.1 mot Supabase.

    Klienten holder én langlevd HTTP/2-forbindelse. Serveren avslutter den
    etter 20 000 strømmer, og klienten reiser seg ikke igjen:

        httpx.RemoteProtocolError: <ConnectionTerminated last_stream_id:19999>

    Det avbrøt kontrollen av sesongen 2023 etter 115 minutter, og forklarer
    trolig også at 2024 utendørs brukte 554 minutter mot 2025s 38 — ytelsen
    faller kraftig når forbindelsen nærmer seg grensen. Under HTTP/1.1 finnes
    ingen slik grense, og httpx gjenoppretter forbindelser selv.
    """
    import httpx
    try:
        gammel = supabase.postgrest.session
        supabase.postgrest.session = httpx.Client(
            base_url=gammel.base_url, headers=gammel.headers,
            timeout=httpx.Timeout(120.0), http2=False,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )
        logger.info("Supabase-forbindelsen satt til HTTP/1.1")
    except Exception as e:
        logger.warning(f"Kunne ikke bytte til HTTP/1.1: {e}")


_slaa_av_http2()

# HTTP session
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) FriidrettLive/1.0'
})

# ============================================================
# EVENT NAME MAPPING (scraped name -> event code in DB)
# ============================================================
EVENT_NAME_TO_CODE = {
    # Kast-femkamp. Kilden bruker full øvelsesbeskrivelse med klassesuffiks,
    # mens basen har kortnavnet "Kast-femkamp Ungdom"/"... Veteran". Uten disse
    # to linjene faller resultatene ut som "Unmapped event" (11 stk 2026-08-21).
    'Kast 5 Kamp (Slegge-Kule-Diskos-Spyd-Vektkast) Veteran':
        'kast_5_k_slegge-kule-diskos-spyd-vektkast_veteran',
    'Kast 5 Kamp (Slegge-Kule-Diskos-Spyd-Vektkast) Ungdom':
        'kast_5_k_slegge-kule-diskos-spyd-vektkast_ungdom',
    'Kast 5 Kamp (Slegge-Kule-Diskos-Spyd-Vektkast)':
        'kast_5_k_slegge-kule-diskos-spyd-vektkast',

    # Sprint
    '60 meter': '60m',
    '100 meter': '100m',
    '150 meter': '150m',
    '200 meter': '200m',
    '300 meter': '300m',
    '400 meter': '400m',
    '600 meter': '600m',
    '800 meter': '800m',
    '1000 meter': '1000m',
    '1500 meter': '1500m',
    '2000 meter': '2000m',
    '3000 meter': '3000m',
    '5000 meter': '5000m',
    '10000 meter': '10000m',
    '1 mile': '1mile',

    # Hurdles
    '60 meter hekk (68,0cm)': '60mh_68cm',
    '60 meter hekk (76,2cm)': '60mh_76_2cm',
    '60 meter hekk (84,0cm)': '60mh_84cm',
    '60 meter hekk (91,4cm)': '60mh_91_4cm',
    '60 meter hekk (100cm)': '60mh_100cm',
    '60 meter hekk (106,7 cm)': '60mh_106_7cm',
    '60 meter hekk (106,7cm)': '60mh_106_7cm',

    # Jumps
    'Høyde': 'hoyde',
    'Stav': 'stav',
    'Lengde': 'lengde',
    'Tresteg': 'tresteg',

    # Standing jumps
    'Lengde uten tilløp': 'lengde_ut',
    'Høyde uten tilløp': 'hoyde_ut',
    'Tresteg uten tilløp': 'tresteg_ut',

    # Throws
    'Kule 7,26kg': 'kule_7_26kg',
    'Kule 6,0kg': 'kule_6kg',
    'Kule 5,0kg': 'kule_5kg',
    'Kule 4,0kg': 'kule_4kg',
    'Kule 3,0kg': 'kule_3kg',
    'Kule 2,0kg': 'kule_2kg',

    # Race walking
    'Kappgang 1000 meter': '1000mg',
    'Kappgang 1500 meter': '1500mg',
    'Kappgang 2000 meter': '2000mg',
    'Kappgang 3000 meter': '3000mg',

    # Zone jumps (map to base event)
    'Lengde (Sone 0,5m)': 'lengde',
    'Tresteg (Sone 0,5m)': 'tresteg',
}

SKIP_EVENTS = {
    # Paraøvelser som ikke har egen øvelse i basen. Tas med når paraidrett
    # får en ordentlig datamodell, jf. kravspekkens §7.
    '60 meter Racerunning',
    '100 meter Racerunning',
    '200 meter Racerunning',
    '400 meter Racerunning',
    '800 meter Racerunning',
    '1500 meter Racerunning',
    '100 meter Rullestol',
    '1500 meter Rullestol',
    '60 meter Rullestol',
    '200 meter Rullestol',
    '400 meter Rullestol',
    '800 meter Rullestol',
    'VektKast 7,26Kg',
    'VektKast 9,08Kg',
    'VektKast 15,88Kg',
}

# COMBINED_EVENT_PATTERNS er fjernet. Den slo til på «N Kamp» og returnerte
# koder («4kamp», «7kamp») som aldri har eksistert i events-tabellen, og
# blokkerte samtidig navneoppslaget som ville truffet. Mangekamp håndteres nå
# i get_event_id() ved å sammenligne komponentene. Se OPERATIONS_LOG 2026-08-25.

# ============================================================
# Caches (loaded once at startup)
# ============================================================
_event_cache = {}      # event_code -> event_id
_event_manual_eligible = set()  # event_id-er der manuell tidtaking er mulig
_club_cache = {}       # club_name -> club_id
_athlete_cache = {}    # (name, birth_year, gender) -> athlete_id
_meet_cache = {}       # (name, date) -> meet_id
_season_cache = {}     # (year, indoor) -> season_id


# ============================================================
# Season detection
# ============================================================

def auto_detect_season() -> Tuple[int, bool]:
    """Determine season year and indoor/outdoor from today's date.
    Dec-Mar: indoor season (next year if Dec)
    Apr-Nov: outdoor season (current year)
    Returns (year, indoor).
    """
    today = datetime.now()
    month = today.month

    if month <= 3 or month == 12:
        # Indoor season
        year = today.year if month <= 3 else today.year + 1
        return year, True
    else:
        # Outdoor season
        return today.year, False


def get_latest_meet_date() -> Optional[datetime]:
    """Get the most recent meet date from the database."""
    try:
        result = supabase.table('meets').select(
            'start_date'
        ).order('start_date', desc=True).limit(1).execute()

        if result.data:
            return datetime.strptime(result.data[0]['start_date'], '%Y-%m-%d')
    except Exception as e:
        logger.warning(f"Could not fetch latest meet date: {e}")
    return None


def determine_min_date(from_date: Optional[str], season_year: int, indoor: bool) -> datetime:
    """Determine the minimum date for scraping.
    Priority: 1) explicit --from-date, 2) latest meet in DB - 7 days, 3) season start.
    """
    if from_date:
        return datetime.strptime(from_date, '%Y-%m-%d')

    latest = get_latest_meet_date()
    if latest:
        min_date = latest - timedelta(days=7)
        logger.info(f"Latest meet in DB: {latest.strftime('%Y-%m-%d')}, using min_date: {min_date.strftime('%Y-%m-%d')}")
        return min_date

    # Fallback: season start
    if indoor:
        return datetime(season_year - 1, 12, 1)
    else:
        return datetime(season_year, 4, 1)


# ============================================================
# Scraping functions (from scrape_new_meets.py)
# ============================================================

def fetch_page(url: str, method: str = 'GET', data: dict = None,
               forsok: int = 4) -> Optional[str]:
    """Hent en side, med retry ved nettverksfeil."""
    for n in range(1, forsok + 1):
        svar = _fetch_page_en_gang(url, method, data)
        if svar is not None:
            return svar
        if n < forsok:
            ventetid = 5 * n
            logger.warning(f"  Henting feilet, prøver igjen om {ventetid}s ({n}/{forsok})")
            time.sleep(ventetid)
    return None


def _fetch_page_en_gang(url: str, method: str = 'GET', data: dict = None) -> Optional[str]:
    time.sleep(REQUEST_DELAY)
    try:
        if method == 'POST':
            response = session.post(url, data=data, timeout=30)
        else:
            response = session.get(url, params=data, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text
    except requests.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        return None


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date from DD.MM.YYYY or DD.MM.YY format."""
    if not date_str:
        return None
    try:
        date_str = date_str.strip()
        parts = date_str.split('.')
        if len(parts) == 3:
            day, month, year = parts
            year = int(year)
            if year < 100:
                year = 2000 + year if year < 50 else 1900 + year
            return datetime(year, int(month), int(day))
    except Exception:
        pass
    return None


def format_date(dt: datetime) -> str:
    """Format date as YYYY-MM-DD."""
    return dt.strftime('%Y-%m-%d')


def fetch_meets_from_source(season: int, outdoor: str, min_date: datetime) -> List[Dict]:
    """Fetch all meets from minfriidrettsstatistikk.info for a season."""
    logger.info(f"Fetching meet list for season {season}, outdoor={outdoor}...")

    url = f"{BASE_URL}/Stevner.php"
    params = {'outdoor': outdoor, 'showseason': season}

    html = fetch_page(url, data=params)
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    meets = []

    for link in soup.find_all('a', href=re.compile(r'posttoresultlist')):
        href = link.get('href', '')
        match = re.search(r'posttoresultlist\((\d+)\)', href)
        if not match:
            continue

        meet_id = int(match.group(1))
        meet_name = link.get_text(strip=True)

        parent_row = link.find_parent('tr')
        if not parent_row:
            continue

        cells = parent_row.find_all('td')
        if len(cells) < 4:
            continue

        date_str = cells[0].get_text(strip=True)
        arena = cells[2].get_text(strip=True) if len(cells) > 2 else ''
        location = cells[3].get_text(strip=True) if len(cells) > 3 else ''

        meet_date = parse_date(date_str)
        if not meet_date:
            continue

        if meet_date < min_date:
            continue

        meets.append({
            'external_id': meet_id,
            'name': meet_name,
            'date': format_date(meet_date),
            'date_obj': meet_date,
            'arena': arena,
            'location': location,
            'outdoor': outdoor == 'Y'
        })

    logger.info(f"Found {len(meets)} meets from {min_date.strftime('%Y-%m-%d')} onwards")
    return meets


def get_existing_meets_from_db(min_date: datetime) -> List[Dict]:
    """Get existing meets from database with result counts."""
    try:
        result = supabase.table('meets').select(
            'id, name, city, start_date'
        ).gte('start_date', min_date.strftime('%Y-%m-%d')).execute()

        meets = []
        for m in result.data:
            count_result = supabase.table('results').select(
                'id', count='exact'
            ).eq('meet_id', m['id']).execute()

            meets.append({
                'id': m['id'],
                'name': m['name'],
                'city': m['city'],
                'date': m['start_date'],
                'result_count': count_result.count or 0
            })

        logger.info(f"Found {len(meets)} existing meets in database")
        return meets
    except Exception as e:
        logger.error(f"Error fetching from database: {e}")
        return []


def normalize_meet_name(name: str) -> str:
    """Normalize meet name for comparison."""
    name = name.lower().strip()
    name = re.sub(r'[^\w\s]', '', name)
    name = ' '.join(name.split())
    return name


def find_missing_meets(source_meets: List[Dict], db_meets: List[Dict]) -> List[Dict]:
    """Find meets that are missing or have too few results in database."""
    db_lookup = {}
    for m in db_meets:
        key = (normalize_meet_name(m['name']), m['date'])
        db_lookup[key] = m.get('result_count', 0)

        if ',' in m['name']:
            short_name = m['name'].split(',', 1)[1].strip()
            db_lookup[(normalize_meet_name(short_name), m['date'])] = m.get('result_count', 0)

    missing = []
    incomplete = []

    for m in source_meets:
        key = (normalize_meet_name(m['name']), m['date'])
        full_key = (normalize_meet_name(f"{m['location']}, {m['name']}"), m['date'])

        result_count = db_lookup.get(key) or db_lookup.get(full_key)

        if result_count is None:
            missing.append(m)
        elif result_count < MIN_RESULTS_THRESHOLD:
            incomplete.append(m)
            logger.info(f"  Incomplete meet: {m['name']} ({m['date']}) - only {result_count} results")

    logger.info(f"Found {len(missing)} missing meets and {len(incomplete)} incomplete meets")
    return missing + incomplete


def finn_ufullstendige_mot_kilden(source_meets, db_meets):
    """Sammenlign antall resultater mot kilden, stevne for stevne.

    `find_missing_meets` regner et stevne som ufullstendig bare hvis det har
    færre enn ti resultater i basen. Det fanger tomme stevner, men ikke de
    delvis importerte: «Hvam, Norgeslekene» 2026 hadde 188 resultater i basen
    mot 539 i kilden, og ble derfor aldri hentet på nytt. Hele øvelser manglet
    — 800 m, 400 m og stav.

    Denne funksjonen henter hvert kildestevne og teller radene. Det koster ett
    kall per stevne, så den kjøres bare med --verify.
    """
    db_lookup = {}
    for m in db_meets:
        db_lookup[(normalize_meet_name(m['name']), m['date'])] = m.get('result_count', 0)
        if ',' in m['name']:
            kort = m['name'].split(',', 1)[1].strip()
            db_lookup[(normalize_meet_name(kort), m['date'])] = m.get('result_count', 0)

    ufullstendige = []
    for i, m in enumerate(source_meets, 1):
        key = (normalize_meet_name(m['name']), m['date'])
        full_key = (normalize_meet_name(f"{m['location']}, {m['name']}"), m['date'])
        i_basen = db_lookup.get(key)
        if i_basen is None:
            i_basen = db_lookup.get(full_key)
        if i_basen is None:
            ufullstendige.append(m)          # helt fraværende
            continue

        html = fetch_page(f"{BASE_URL}/StevneResultater.php", method='POST',
                          data={'competition': m['external_id']})
        if not html:
            continue
        soup = BeautifulSoup(html, 'html.parser')
        i_kilden = sum(1 for t in soup.find_all('table')
                       for tr in t.find_all('tr') if len(tr.find_all('td')) >= 4)

        mangler = i_kilden - i_basen
        if i_kilden and mangler > VERIFY_MANGEL_ANDEL * i_kilden:
            logger.info(f"  Ufullstendig: {m['name']} ({m['date']}) — "
                        f"{i_basen} i basen mot {i_kilden} i kilden, mangler {mangler}")
            ufullstendige.append(m)
        if i % 25 == 0:
            logger.info(f"  ... {i}/{len(source_meets)} stevner kontrollert")

    logger.info(f"Kontrollert {len(source_meets)} stevner mot kilden — "
                f"{len(ufullstendige)} er ufullstendige")
    return ufullstendige


def parse_result_wind(result_str: str) -> Tuple[str, Optional[str], bool]:
    """Parse resultat, vind og manuell-markør.

    Kilden bruker flere varianter:
        '9,17(+0,9)'      -> ('9.17', '+0.9', False)
        '14.9(-0.2) M'    -> ('14.9', '-0.2', True)     ' M' = manuell tidtaking
        '40.0(ok) M'      -> ('40.0', None,   True)     '(ok)' = ingen vindverdi
        '5.01.7 M'        -> ('5.01.7', None, True)

    Tidligere krevde regexen at strengen SLUTTET med ')'. Alt med ' M' etter
    parentesen falt derfor gjennom, og hele strengen ble lagt i `performance`.
    Databasetriggeren `calculate_performance_value` kaller `parse_performance()`
    som caster til numeric, og innsettingen feilet med 22P02. 44 resultater gikk
    tapt i importen 2026-08-21. Se OPERATIONS_LOG.md.
    """
    if not result_str:
        return '', None, False

    result_str = result_str.strip()

    # ' M' til slutt betyr manuell tidtaking. Må fjernes før vindparsingen.
    is_manual = False
    m = re.search(r'\s+M$', result_str)
    if m:
        is_manual = True
        result_str = result_str[:m.start()].strip()

    # Vind i parentes. Innholdet er ikke alltid et tall — '(ok)' betyr at
    # resultatet er godkjent uten registrert vindverdi.
    match = re.match(r'(.+?)\(([^)]*)\)$', result_str)
    if match:
        value, inner = match.group(1).strip(), match.group(2).strip()
        if re.fullmatch(r'[+-]?\d+[,.]?\d*', inner):
            return value, inner.replace(',', '.'), is_manual
        return value, None, is_manual

    return result_str, None, is_manual


def fetch_and_parse_meet_results(meet: Dict) -> List[Dict]:
    """Fetch and parse results for a single meet. Returns list of result dicts."""
    url = f"{BASE_URL}/StevneResultater.php"
    data = {'competition': meet['external_id']}
    html = fetch_page(url, method='POST', data=data)

    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    results = []

    current_event = None
    current_class = None

    for element in soup.find_all(['div', 'table']):
        if element.name == 'div' and element.get('id') == 'header2':
            h2 = element.find('h2')
            if h2:
                current_class = h2.get_text(strip=True)

        elif element.name == 'div' and element.get('id') == 'eventheader':
            h3 = element.find('h3')
            if h3:
                current_event = h3.get_text(strip=True)

        elif element.name == 'table' and current_event:
            rows = element.find_all('tr')

            for row in rows:
                if row.find('th'):
                    continue

                cells = row.find_all('td')
                if len(cells) < 4:
                    continue

                try:
                    place_text = cells[0].get_text(strip=True)
                    result_raw = cells[1].get_text(strip=True)
                    name_text = cells[2].get_text(strip=True)
                    club = cells[3].get_text(strip=True)

                    place = None
                    place_match = re.match(r'^(\d+)', place_text)
                    if place_match:
                        place = int(place_match.group(1))

                    result, wind, is_manual = parse_result_wind(result_raw)

                    name = name_text
                    birth_year = None
                    year_match = re.search(r'\((\d{4})\)$', name_text)
                    if year_match:
                        birth_year = int(year_match.group(1))
                        name = name_text[:year_match.start()].strip()

                    if not name or not result:
                        continue

                    if result.upper() in ['DNS', 'DNF', 'DQ', 'NM', '-']:
                        continue

                    results.append({
                        'meet_external_id': meet['external_id'],
                        'meet_name': meet['name'],
                        'meet_date': meet['date'],
                        'location': meet.get('location', ''),
                        'event': current_event,
                        'event_class': current_class,
                        'place': place,
                        'athlete_name': name,
                        'birth_year': birth_year,
                        'club': club,
                        'result': result.replace(',', '.'),
                        'wind': wind,
                        'is_manual': is_manual,
                        'is_indoor': not meet['outdoor']
                    })
                except Exception as e:
                    logger.debug(f"Error parsing row: {e}")
                    continue

    return results


# ============================================================
# Import functions (from import_new_meets.py)
# ============================================================

def load_events():
    """Load all events from database into cache.

    Bygger også settet over øvelser der manuell tidtaking i det hele tatt er
    mulig. Per regelverket gjelder manuell tidtaking KUN løpsøvelser kortere
    enn 800 m — tekniske øvelser har ingen slik distinksjon, og 800 m og
    lengre har det aldri. Se CLAUDE.md punkt 7.
    """
    global _event_cache, _event_manual_eligible
    response = supabase.table('events').select('id, code, name, result_type').execute()
    for e in response.data:
        _event_cache[e['code']] = e['id']
        _event_cache[e['name']] = e['id']
        _indekser_mangekamp(e['name'], e['id'])
        if e['result_type'] == 'time':
            m = re.match(r'^(\d+)m', e['code'] or '')
            if m and int(m.group(1)) < 800:
                _event_manual_eligible.add(e['id'])
    logger.info(f"Loaded {len(response.data)} events "
                f"({len(_event_manual_eligible)} kan ha manuell tidtaking)")


def load_seasons():
    """Load all seasons from database into cache."""
    global _season_cache
    response = supabase.table('seasons').select('id, year, indoor').execute()
    for s in response.data:
        key = (s['year'], s['indoor'])
        _season_cache[key] = s['id']
    logger.info(f"Loaded {len(response.data)} seasons")


def load_clubs():
    """Load all clubs from database into cache."""
    global _club_cache
    offset = 0
    chunk_size = 1000
    total = 0
    while True:
        response = supabase.table('clubs').select('id, name').range(offset, offset + chunk_size - 1).execute()
        if not response.data:
            break
        for c in response.data:
            _club_cache[c['name']] = c['id']
        total += len(response.data)
        offset += chunk_size
        if len(response.data) < chunk_size:
            break
    logger.info(f"Loaded {total} clubs")


def load_athletes():
    """Load athletes for fast matching (paginated)."""
    global _athlete_cache
    offset = 0
    chunk_size = 1000
    total = 0

    while True:
        response = supabase.table('athletes').select(
            'id, first_name, last_name, birth_year, gender'
        ).range(offset, offset + chunk_size - 1).execute()

        if not response.data:
            break

        for a in response.data:
            full_name = f"{a['first_name']} {a['last_name']}"
            key = (full_name.lower(), a.get('birth_year'), a.get('gender'))
            _athlete_cache[key] = a['id']

        total += len(response.data)
        offset += chunk_size

        if len(response.data) < chunk_size:
            break

        if total % 10000 == 0:
            logger.info(f"  ...loaded {total} athletes so far")

    logger.info(f"Loaded {total} athletes into cache")


def fix_performance_format(result_str):
    """Convert European period-separated time format to colon-separated.
    E.g., '3.34.02' -> '3:34.02', '16.08.70' -> '16:08.70'
    """
    if not result_str:
        return result_str

    match = re.match(r'^(\d{1,2})\.(\d{2})\.(\d{1,2})$', result_str)
    if match:
        minutes, seconds, hundredths = match.groups()
        return f"{minutes}:{seconds}.{hundredths}"

    return result_str


def _mangekamp_deler(navn):
    """Del et mangekampnavn i (antall, komponentsett, klassesuffiks).

    «7 Kamp (100mhekk-Høyde-Kule-200m-Lengde-Spyd-800m) Ungdom»
      -> (7, {'100mhekk','høyde','kule','200m','lengde','spyd','800m'}, 'ungdom')

    Komponentene normaliseres slik at «110m hekk» og «110mhekk» blir like.
    Returnerer None for øvelser som ikke er mangekamp.
    """
    m = re.match(r'^(\d+)\s*Kamp\b(?:\s*\(([^)]*)\))?\s*(.*)$', navn.strip())
    if not m:
        return None
    antall = int(m.group(1))
    deler = frozenset(
        re.sub(r'\s+', '', d).lower()
        for d in (m.group(2) or '').split('-') if d.strip())
    return antall, deler, (m.group(3) or '').strip().lower()


# Mangekamp slås opp på komponentene, ikke på navnestrengen. Kilden og basen
# lister øvelsene i ulik rekkefølge og med ulik mellomromsbruk — «10 Kamp
# (100m-Lengde-...-1500m)» mot «10 Kamp (110m hekk-Diskos-...-1500m)» er samme
# øvelse. Uten dette falt resultatene ut som «Unmapped event».
_mangekamp_indeks = {}       # (antall, komponenter, suffiks) -> event_id
_mangekamp_uten_suffiks = {}  # (antall, komponenter) -> event_id


def _indekser_mangekamp(navn, event_id):
    delt = _mangekamp_deler(navn)
    if not delt:
        return
    antall, deler, suffiks = delt
    if deler:
        _mangekamp_indeks[(antall, deler, suffiks)] = event_id
        _mangekamp_uten_suffiks.setdefault((antall, deler), event_id)


def get_event_id(event_name):
    """Slå opp øvelses-id fra kildens øvelsesnavn.

    Rekkefølgen er fra mest til minst spesifikk. Tidligere ble
    COMBINED_EVENT_PATTERNS sjekket FØRST, og den returnerte `None` når koden
    («4kamp», «7kamp») ikke fantes i basen — uten å falle videre til
    navneoppslaget som ville truffet. Alle mangekampresultater fra de
    mønstrene gikk dermed tapt.
    """
    if event_name in SKIP_EVENTS:
        return None

    # 1. Eksplisitt overstyring
    code = EVENT_NAME_TO_CODE.get(event_name)
    if code and code in _event_cache:
        return _event_cache[code]

    # 2. Eksakt navnetreff
    if event_name in _event_cache:
        return _event_cache[event_name]

    # 3. Mangekamp: samme komponenter, uansett rekkefølge og mellomrom
    delt = _mangekamp_deler(event_name)
    if delt:
        antall, deler, suffiks = delt

        # Samme sammensetning OG samme klasse — det sikreste treffet
        treff = _mangekamp_indeks.get((antall, deler, suffiks))
        if treff:
            return treff

        # Generisk «N Kamp» før vi vurderer en annen klasse. Å legge en
        # seniorsjukamp inn som «Veteran» er verre enn å miste
        # sammensetningen: klassen er en påstand om utøveren.
        for generisk in (f'{antall}_k', f'{antall} Kamp'):
            if generisk in _event_cache:
                return _event_cache[generisk]

        # Siste utvei: samme sammensetning, men bare når kilden ikke selv
        # oppgir en klasse. Da påstår vi ingenting som motsier kilden.
        if not suffiks:
            treff = _mangekamp_uten_suffiks.get((antall, deler))
            if treff:
                return treff

    return None


def get_gender(event_class):
    """Extract gender from event class string."""
    if not event_class:
        return None
    ec = event_class.lower()
    if ec.startswith(('menn', 'gutter', 'ms ', 'g-')):
        return 'M'
    if ec.startswith(('kvinner', 'jenter', 'ks ', 'k-')):
        return 'F'
    return None


def get_season_id(date_str, indoor):
    """Get season ID from date and indoor flag."""
    year = int(date_str[:4])
    if indoor and int(date_str[5:7]) >= 10:
        year += 1
    key = (year, indoor)
    return _season_cache.get(key)


def is_valid_club_name(name):
    """Sperre mot at parsefeil skaper søppelklubber.

    Et klubbnavn må inneholde minst én bokstav og kan ikke være et rent tall
    eller en statuskode. Fanger "01", "61", "04-DNS", "0(558)" — mønsteret som
    oppsto da mangekamp-delresultater ble tolket som klubbnavn i mai 2026.
    Se OPERATIONS_LOG.md 2026-08-09.
    """
    n = (name or '').strip()
    if len(n) < 2:
        return False
    if not re.search(r'[A-Za-zÆØÅæøå]', n):
        return False
    # Kun sifre, skilletegn og statuskoder — f.eks. "04-DNS", "6)-DNS-DNS".
    if re.fullmatch(r'[\d\s\-–,.()]*(?:(?:DNS|DNF|DQ|NM)[\d\s\-–,.()]*)+', n, re.IGNORECASE):
        return False
    return True


def get_or_create_club(name):
    """Get or create a club, return its ID."""
    if not name or name.strip() == '':
        return None

    name = name.strip()
    if not is_valid_club_name(name):
        logger.warning(f"Avviser ugyldig klubbnavn fra parsing: {name!r}")
        return None

    if name in _club_cache:
        return _club_cache[name]

    try:
        response = supabase.table('clubs').insert({'name': name}).execute()
        if response.data:
            _club_cache[name] = response.data[0]['id']
            return _club_cache[name]
    except Exception as e:
        response = supabase.table('clubs').select('id').eq('name', name).execute()
        if response.data:
            _club_cache[name] = response.data[0]['id']
            return _club_cache[name]
        logger.warning(f"Failed to create club '{name}': {e}")

    return None


def get_or_create_meet(name, date, location, indoor):
    """Get or create a meet, return its ID."""
    cache_key = (name, date)
    if cache_key in _meet_cache:
        return _meet_cache[cache_key]

    response = supabase.table('meets').select('id').eq(
        'name', name
    ).eq('start_date', date).execute()

    if response.data:
        _meet_cache[cache_key] = response.data[0]['id']
        return _meet_cache[cache_key]

    if location:
        city_name = f"{location}, {name}"
        response = supabase.table('meets').select('id').eq(
            'name', city_name
        ).eq('start_date', date).execute()
        if response.data:
            _meet_cache[cache_key] = response.data[0]['id']
            return _meet_cache[cache_key]

    year = int(date[:4])
    if indoor and int(date[5:7]) >= 10:
        year += 1
    season_id = _season_cache.get((year, indoor))

    city = location.split('/')[0] if location else ''

    country = 'NOR'
    if location and '/' in location:
        country_code = location.split('/')[-1].strip()
        country_map = {
            'FRA': 'FRA', 'GER': 'GER', 'SUI': 'SUI', 'SWE': 'SWE',
            'DEN': 'DEN', 'FIN': 'FIN', 'USA': 'USA', 'GBR': 'GBR',
            'NOR': 'NOR', 'EST': 'EST', 'NED': 'NED', 'BEL': 'BEL',
            'POL': 'POL', 'CZE': 'CZE', 'AUT': 'AUT', 'ITA': 'ITA',
            'ESP': 'ESP', 'POR': 'POR', 'HUN': 'HUN', 'SVK': 'SVK',
        }
        country = country_map.get(country_code, country_code)

    meet_data = {
        'name': name,
        'start_date': date,
        'city': city,
        'country': country,
        'indoor': indoor,
        'season_id': season_id,
    }

    try:
        response = supabase.table('meets').insert(meet_data).execute()
        if response.data:
            _meet_cache[cache_key] = response.data[0]['id']
            logger.info(f"  Created meet: {name} ({date}) in {city}")
            return _meet_cache[cache_key]
    except Exception as e:
        logger.warning(f"Failed to create meet '{name}': {e}")

    return None


def _bygg_navnaars_indeks():
    """Sekundærindeks (navn, fødselsår) -> [(nøkkel, id), ...].

    Uten den gikk `match_athlete` lineært gjennom hele utøvercachen hver gang
    kjønnet ikke stemte — 87 000 sammenligninger per oppslag. På en full
    historisk kjøring med over en million resultater er det uholdbart.
    """
    global _athlete_navnaar
    _athlete_navnaar = defaultdict(list)
    for k, v in _athlete_cache.items():
        _athlete_navnaar[(k[0], k[1])].append((k, v))


_athlete_navnaar = None


def match_athlete(name, birth_year, gender):
    """Match an athlete by name, birth_year, and gender."""
    if not name:
        return None

    key = (name.lower(), birth_year, gender)
    athlete_id = _athlete_cache.get(key)
    if athlete_id:
        return athlete_id

    # Samme navn og fødselsår, men annet (eller manglende) kjønn
    if _athlete_navnaar is None:
        _bygg_navnaars_indeks()
    for cached_key, cached_id in _athlete_navnaar.get((name.lower(), birth_year), []):
            # Backfill: utøver ligger med gender=NULL men resultatet har
            # autoritativt klasse-kjønn (jf. kjønnsopprydding juli 2026)
            if gender and cached_key[2] is None:
                try:
                    supabase.table('athletes').update({'gender': gender}).eq('id', cached_id).execute()
                    del _athlete_cache[cached_key]
                    ny_nokkel = (cached_key[0], cached_key[1], gender)
                    _athlete_cache[ny_nokkel] = cached_id
                    if _athlete_navnaar is not None:
                        oppf = _athlete_navnaar[(cached_key[0], cached_key[1])]
                        oppf[:] = [(ny_nokkel if k == cached_key else k, i) for k, i in oppf]
                    logger.info(f"Backfilled gender={gender}: {name} ({birth_year})")
                except Exception as e:
                    logger.debug(f"Gender backfill failed for '{name}': {e}")
            return cached_id

    return None


def create_athlete(name, birth_year, gender, club_name):
    """Create a new athlete in the database."""
    name_parts = name.split() if name else []
    first_name = name_parts[0] if name_parts else ''
    last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

    club_id = get_or_create_club(club_name) if club_name else None

    athlete_data = {
        'first_name': first_name,
        'last_name': last_name,
        'gender': gender,
        'birth_year': birth_year,
        'current_club_id': club_id,
    }

    try:
        response = supabase.table('athletes').insert(athlete_data).execute()
        if response.data:
            athlete_id = response.data[0]['id']
            key = (name.lower(), birth_year, gender)
            _athlete_cache[key] = athlete_id
            return athlete_id
    except Exception as e:
        logger.debug(f"Failed to create athlete '{name}': {e}")

    return None


_athlete_club_updated = set()  # Track already-updated athletes this run


def _update_athlete_club(athlete_id, club_id):
    """Update athlete's current_club_id if changed. Only updates once per run."""
    if athlete_id in _athlete_club_updated:
        return
    _athlete_club_updated.add(athlete_id)
    try:
        supabase.table('athletes').update(
            {'current_club_id': club_id}
        ).eq('id', athlete_id).neq('current_club_id', club_id).execute()
    except Exception:
        pass  # Non-critical, don't fail the import


# ============================================================
# Import a single meet's results directly to DB
# ============================================================

def import_meet_results(meet_results: List[Dict], dry_run: bool = False) -> Dict:
    """Import scraped results for one meet directly to the database.
    Returns stats dict for this meet.
    """
    stats = {
        'imported': 0,
        'matched_existing_athlete': 0,
        'created_new_athlete': 0,
        'skipped_no_event': 0,
        'skipped_no_athlete': 0,
        'skipped_no_meet': 0,
        'skipped_duplicate': 0,
        'errors': 0,
        'new_meets': 0,
    }
    unmapped_events = defaultdict(int)

    if not meet_results:
        return stats

    # All results are for the same meet
    first = meet_results[0]
    meet_name = first['meet_name']
    meet_date = first['meet_date']
    location = first.get('location', '')
    is_indoor = first['is_indoor']

    if dry_run:
        logger.info(f"  [DRY RUN] Would import {len(meet_results)} results for {meet_name} ({meet_date})")
        stats['imported'] = len(meet_results)
        return stats

    # Get or create meet
    meet_id = get_or_create_meet(meet_name, meet_date, location, is_indoor)
    if not meet_id:
        stats['skipped_no_meet'] = len(meet_results)
        return stats

    # Check if this meet was newly created (not in cache before this call)
    # We track this via _meet_cache side effects in get_or_create_meet

    season_id = get_season_id(meet_date, is_indoor)

    result_batch = []

    for row in meet_results:
        event_name = row['event']
        event_class = row['event_class']

        event_id = get_event_id(event_name)
        if not event_id:
            if event_name not in SKIP_EVENTS:
                unmapped_events[event_name] += 1
            stats['skipped_no_event'] += 1
            continue

        gender = get_gender(event_class)
        birth_year = row.get('birth_year')

        athlete_name = row['athlete_name']
        athlete_id = match_athlete(athlete_name, birth_year, gender)

        club_id = get_or_create_club(row.get('club'))

        if athlete_id:
            stats['matched_existing_athlete'] += 1
            # Update current_club_id to this meet's club (latest data)
            if club_id:
                _update_athlete_club(athlete_id, club_id)
        else:
            athlete_id = create_athlete(athlete_name, birth_year, gender, row.get('club'))
            if athlete_id:
                stats['created_new_athlete'] += 1
            else:
                stats['skipped_no_athlete'] += 1
                continue

        result_str = fix_performance_format(row['result'])

        place = row.get('place')

        wind = None
        if row.get('wind'):
            try:
                wind = float(row['wind'])
            except ValueError:
                pass

        result_data = {
            'athlete_id': athlete_id,
            'event_id': event_id,
            'meet_id': meet_id,
            'season_id': season_id,
            'performance': result_str,
            'date': meet_date,
            'wind': wind,
            'place': place,
            'club_id': club_id,
            'status': 'OK',
            'verified': True,
        }

        if wind is not None and wind > 2.0:
            result_data['is_wind_legal'] = False

        # Kilden markerer manuell tidtaking med ' M'. Det er en autoritativ
        # opplysning og bedre enn å utlede den fra presisjon. Flagget settes
        # kun der manuell tidtaking faktisk er mulig (løp under 800 m).
        if row.get('is_manual') and event_id in _event_manual_eligible:
            result_data['is_manual_time'] = True

        result_batch.append(result_data)

    # Insert batch.
    # NB: try/except ligger INNE i chunk-lokken. Lå den rundt hele lokken, ville
    # et feilende chunk utlose ny en-og-en-innsetting av HELE result_batch - også
    # de chunkene som allerede var lagt inn. Det ga 813 duplikater 2026-08-07.
    # Unik-constrainten fanger dem ikke opp: den dekker
    # (athlete_id, event_id, meet_id, round, heat_number), og round/heat_number
    # er alltid NULL her - og NULL er aldri lik NULL i Postgres.
    if result_batch:
        inserted = 0
        for i in range(0, len(result_batch), 50):
            chunk = result_batch[i:i + 50]
            try:
                supabase.table('results').insert(chunk).execute()
                stats['imported'] += len(chunk)
                inserted += len(chunk)
            except Exception as e:
                logger.warning(
                    f"  Chunk {i // 50 + 1} failed for {meet_name}, trying one-by-one: {e}")
                for result_data in chunk:
                    try:
                        supabase.table('results').insert(result_data).execute()
                        stats['imported'] += 1
                        inserted += 1
                    except Exception as e2:
                        # Unik-indeksen results_innhold_unik (athlete, event, meet,
                        # performance, place, wind - NULLS NOT DISTINCT) avviser rader
                        # som allerede finnes. Det er forventet ved re-kjoring og er
                        # ikke en feil.
                        if '23505' in str(e2) or 'results_innhold_unik' in str(e2):
                            stats['skipped_duplicate'] += 1
                        else:
                            # Tidligere logget på debug-nivå, som ikke vises ved
                            # normal kjøring. 49 feilende rader gikk derfor
                            # upåaktet hen i august 2026. De tre første per
                            # stevne logges nå; resten telles.
                            stats['errors'] += 1
                            if stats['errors'] <= 3:
                                logger.warning(
                                    f"    Rad feilet: {result_data.get('performance')!r} "
                                    f"i {meet_name} — {e2}")
        if inserted:
            logger.info(f"  Imported {inserted} results for {meet_name} ({meet_date})")

    if unmapped_events:
        for event, count in sorted(unmapped_events.items(), key=lambda x: -x[1]):
            logger.warning(f"  Unmapped event: {event} ({count} results)")

    return stats


# ============================================================
# Main orchestration
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='Update friidrett results: scrape new meets and import to database.'
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--indoor', action='store_true', help='Force indoor season')
    group.add_argument('--outdoor', action='store_true', help='Force outdoor season')

    parser.add_argument('--season', type=int, help='Season year (e.g. 2026)')
    parser.add_argument('--from-date', type=str, help='Start date (YYYY-MM-DD), overrides auto-detection')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be imported without importing')
    parser.add_argument('--verify', action='store_true',
                        help='Tell resultater mot kilden per stevne og hent inn '
                             'de som er delvis importert. Tregere, men fanger '
                             'stevner der bare deler av resultatene kom med.')

    return parser.parse_args()


def main():
    args = parse_args()

    # Determine season
    auto_year, auto_indoor = auto_detect_season()

    if args.indoor:
        indoor = True
    elif args.outdoor:
        indoor = False
    else:
        indoor = auto_indoor

    season_year = args.season or auto_year
    outdoor_flag = 'N' if indoor else 'Y'
    season_label = f"{season_year} {'indoor' if indoor else 'outdoor'}"

    logger.info("=" * 60)
    logger.info(f"UPDATE RESULTS — Season: {season_label}")
    if args.dry_run:
        logger.info("*** DRY RUN — no changes will be made ***")
    logger.info("=" * 60)

    # Determine min date
    min_date = determine_min_date(args.from_date, season_year, indoor)
    logger.info(f"Looking for meets from {min_date.strftime('%Y-%m-%d')} onwards")

    # Load reference data for import
    logger.info("\nLoading reference data...")
    load_events()
    load_seasons()
    load_clubs()
    load_athletes()

    # Step 1: Fetch source meets
    source_meets = fetch_meets_from_source(season_year, outdoor_flag, min_date)

    if not vent_pa_nett(SUPABASE_URL.split('//')[-1].split('/')[0]):
        logger.error("Ingen nettforbindelse — avslutter")
        return

    # Step 2: Get existing meets from DB
    db_meets = get_existing_meets_from_db(min_date)

    # Step 3: Find missing/incomplete meets
    if args.verify:
        logger.info("\nVERIFY — teller resultater mot kilden, stevne for stevne")
        missing_meets = finn_ufullstendige_mot_kilden(source_meets, db_meets)
    else:
        missing_meets = find_missing_meets(source_meets, db_meets)

    if not missing_meets:
        logger.info("\nNo missing meets found — database is up to date!")
        logger.info("=" * 60)
        return

    # Step 4: Scrape + import each meet
    logger.info(f"\nProcessing {len(missing_meets)} missing/incomplete meets...")

    totals = {
        'imported': 0,
        'matched_existing_athlete': 0,
        'created_new_athlete': 0,
        'skipped_no_event': 0,
        'skipped_no_athlete': 0,
        'skipped_no_meet': 0,
        'skipped_duplicate': 0,
        'errors': 0,
        'new_meets': 0,
        'meets_processed': 0,
        'total_scraped': 0,
    }

    for i, meet in enumerate(missing_meets):
        logger.info(f"\n[{i+1}/{len(missing_meets)}] {meet['name']} ({meet['date']})")

        # Scrape results
        results = fetch_and_parse_meet_results(meet)
        totals['total_scraped'] += len(results)

        if not results:
            logger.warning(f"  No results found")
            continue

        logger.info(f"  Scraped {len(results)} results")

        # Import directly
        meet_stats = import_meet_results(results, dry_run=args.dry_run)
        totals['meets_processed'] += 1

        for key in ['imported', 'matched_existing_athlete', 'created_new_athlete',
                     'skipped_no_event', 'skipped_no_athlete', 'skipped_no_meet',
                     'skipped_duplicate', 'errors']:
            totals[key] += meet_stats.get(key, 0)

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("UPDATE COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Season: {season_label}")
    logger.info(f"Source meets found: {len(source_meets)}")
    logger.info(f"Already in database: {len(db_meets)}")
    logger.info(f"Missing/incomplete: {len(missing_meets)}")
    logger.info(f"Meets processed: {totals['meets_processed']}")
    logger.info(f"Results scraped: {totals['total_scraped']}")
    logger.info(f"Results imported: {totals['imported']}")
    logger.info(f"  Matched athletes: {totals['matched_existing_athlete']}")
    logger.info(f"  New athletes created: {totals['created_new_athlete']}")
    logger.info(f"  Skipped (no event mapping): {totals['skipped_no_event']}")
    logger.info(f"  Skipped (no athlete): {totals['skipped_no_athlete']}")
    logger.info(f"  Skipped (already in db): {totals['skipped_duplicate']}")
    logger.info(f"  Errors: {totals['errors']}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
