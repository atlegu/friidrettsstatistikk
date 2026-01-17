"""
Test-script for å analysere HTML-strukturen på minfriidrettsstatistikk.info
Kjør dette først for å se hvordan dataene er strukturert.
"""

import requests
from bs4 import BeautifulSoup
from pathlib import Path

BASE_URL = "https://www.minfriidrettsstatistikk.info/php"
OUTPUT_DIR = Path(__file__).parent / "html_samples"
OUTPUT_DIR.mkdir(exist_ok=True)

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) FriidrettsstatistikkScraper/1.0'
})


def save_html(html, filename):
    """Lagre HTML til fil for inspeksjon."""
    filepath = OUTPUT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Lagret: {filepath}")


def test_athlete_search():
    """Test søk etter utøvere på bokstav A."""
    print("\n=== TEST: Utøversøk på bokstav A ===")

    url = f"{BASE_URL}/UtoverSok.php"

    # Test 1: GET med parameter
    response = session.get(url, params={'athlname': 'A'})
    print(f"Status: {response.status_code}")
    save_html(response.text, 'search_A_get.html')

    # Test 2: POST med data
    response = session.post(url, data={'athlname': 'A'})
    print(f"Status: {response.status_code}")
    save_html(response.text, 'search_A_post.html')

    # Analyser innholdet
    soup = BeautifulSoup(response.text, 'html.parser')
    print(f"\nAntall lenker totalt: {len(soup.find_all('a'))}")

    # Finn lenker til utøverprofiler
    profile_links = soup.find_all('a', href=lambda h: h and 'UtoverStatistikk' in h)
    print(f"Antall utøverlenker: {len(profile_links)}")

    if profile_links[:5]:
        print("\nFørste 5 utøverlenker:")
        for link in profile_links[:5]:
            print(f"  - {link.get_text(strip=True)}: {link.get('href')}")


def test_athlete_profile():
    """Test henting av en utøverprofil."""
    print("\n=== TEST: Utøverprofil (Mathias Hove Johansen) ===")

    url = f"{BASE_URL}/UtoverStatistikk.php"
    params = {
        'showathl': 14975,
        'showevent': 0,
        'showseason': 0,
        'outdoor': 'A',
        'listtype': 'All'
    }

    response = session.get(url, params=params)
    print(f"Status: {response.status_code}")
    save_html(response.text, 'profile_14975.html')

    soup = BeautifulSoup(response.text, 'html.parser')

    # Finn navn
    headers = soup.find_all(['h1', 'h2', 'h3'])
    print(f"\nHeaders funnet: {[h.get_text(strip=True)[:50] for h in headers]}")

    # Finn tabeller
    tables = soup.find_all('table')
    print(f"\nAntall tabeller: {len(tables)}")

    for i, table in enumerate(tables[:3]):
        rows = table.find_all('tr')
        print(f"\nTabell {i+1}: {len(rows)} rader")
        if rows:
            # Vis første rad (ofte header)
            first_row = rows[0]
            cells = first_row.find_all(['th', 'td'])
            print(f"  Header: {[c.get_text(strip=True)[:20] for c in cells]}")

            # Vis andre rad (data)
            if len(rows) > 1:
                second_row = rows[1]
                cells = second_row.find_all(['td'])
                print(f"  Data:   {[c.get_text(strip=True)[:20] for c in cells]}")


def test_landsstatistikk():
    """Test henting av landsstatistikk."""
    print("\n=== TEST: Landsstatistikk (100m senior menn 2024) ===")

    url = f"{BASE_URL}/LandsStatistikk.php"

    # Test med ulike parametere
    params_variations = [
        {'showclass': 11, 'showevent': 2},  # Senior menn, 100m
        {'showclass': 11, 'showevent': 2, 'showseason': 2024},
        {'showclass': 11, 'showevent': 2, 'showseason': 2024, 'outdoor': 'Y'},
    ]

    for i, params in enumerate(params_variations):
        response = session.get(url, params=params)
        print(f"\nParams {params}: Status {response.status_code}")
        save_html(response.text, f'landsstat_{i+1}.html')

        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')
        print(f"  Tabeller: {len(tables)}")

        # Sjekk om det er resultater
        # Se etter typiske resultatmønstre (tider som 10.XX)
        import re
        time_pattern = re.compile(r'\d{1,2}[,\.]\d{2}')
        matches = time_pattern.findall(soup.get_text())
        print(f"  Mulige tider funnet: {len(matches)}")
        if matches[:5]:
            print(f"  Eksempler: {matches[:5]}")


def test_stevneresultater():
    """Test henting av stevneresultater."""
    print("\n=== TEST: Stevneresultater ===")

    url = f"{BASE_URL}/StevneResultater.php"

    # Prøv med ulike parametere
    response = session.get(url)
    print(f"GET uten params: Status {response.status_code}")
    save_html(response.text, 'stevne_get.html')

    # Prøv POST
    response = session.post(url, data={'competition': 1})
    print(f"POST competition=1: Status {response.status_code}")
    save_html(response.text, 'stevne_post.html')


if __name__ == '__main__':
    print("Tester scraping av minfriidrettsstatistikk.info")
    print("=" * 60)

    test_athlete_search()
    test_athlete_profile()
    test_landsstatistikk()
    test_stevneresultater()

    print("\n" + "=" * 60)
    print(f"HTML-filer lagret i: {OUTPUT_DIR}")
    print("Åpne disse filene i en nettleser for å se strukturen.")
