"""
Test script to verify we can correctly scrape ALL results for an athlete.
Tests the approach documented in UNIFIED_SCRAPING_GUIDE.md
"""

import requests
from bs4 import BeautifulSoup
import re
import time

BASE_URL = "https://www.minfriidrettsstatistikk.info/php"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) DataVerifier/1.0',
    'Content-Type': 'application/x-www-form-urlencoded'
})


def parse_result_with_wind(result_str):
    """Parse result with optional wind, e.g. '6,82(+1,3)' -> ('6.82', 1.3)"""
    if not result_str:
        return None, None

    result_str = result_str.strip()

    # Extract wind from parentheses
    wind_match = re.search(r'\(([\+\-]?\d+[,\.]\d+)\)', result_str)
    wind = None
    if wind_match:
        wind_str = wind_match.group(1).replace(',', '.')
        try:
            wind = float(wind_str)
        except ValueError:
            pass
        result_str = re.sub(r'\s*\([^\)]+\)', '', result_str).strip()

    result = result_str.replace(',', '.')
    return result, wind


def fetch_athlete_all_results(athlete_id):
    """
    Fetch ALL results for an athlete using type=RES.
    This is the correct method per UNIFIED_SCRAPING_GUIDE.md
    """
    url = f"{BASE_URL}/UtoverStatistikk.php"

    # POST request with type=RES to get ALL results
    data = {
        'athlete': athlete_id,
        'type': 'RES'
    }

    try:
        response = session.post(url, data=data, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        html = response.text
    except requests.RequestException as e:
        print(f"Error fetching athlete {athlete_id}: {e}")
        return None

    soup = BeautifulSoup(html, 'lxml')

    # Get athlete name
    name = None
    name_elem = soup.find('h2')
    if name_elem:
        name = name_elem.get_text(strip=True)

    # Get birth date
    birth_date = None
    for h3 in soup.find_all('h3'):
        text = h3.get_text(strip=True)
        if text.startswith('Født:'):
            match = re.search(r'(\d{2}\.\d{2}\.\d{4})', text)
            if match:
                birth_date = match.group(1)
            break

    results = []
    current_indoor = None
    current_event = None

    # Parse the page structure
    for elem in soup.find_all(['h2', 'h3', 'table']):
        if elem.name == 'h2':
            text = elem.get_text(strip=True).upper()
            if 'INNENDØRS' in text:
                current_indoor = True
            elif 'UTENDØRS' in text:
                current_indoor = False

        elif elem.name == 'h3':
            text = elem.get_text(strip=True)
            if text and not text.startswith('Født:'):
                current_event = text

        elif elem.name == 'table' and current_event:
            rows = elem.find_all('tr')
            if not rows:
                continue

            # Get headers
            header_row = rows[0]
            headers = [th.get_text(strip=True).upper() for th in header_row.find_all(['th', 'td'])]

            # Skip if not a results table
            if 'RESULTAT' not in headers:
                continue

            # Process result rows
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) < 3:
                    continue

                try:
                    # Build result dict based on available columns
                    result_data = {
                        'event': current_event,
                        'indoor': current_indoor
                    }

                    for i, header in enumerate(headers):
                        if i >= len(cols):
                            break

                        cell = cols[i]
                        text = cell.get_text(strip=True)

                        if header == 'RESULTAT':
                            perf, wind = parse_result_with_wind(text)
                            result_data['performance'] = perf
                            result_data['wind'] = wind
                            if wind is not None and wind > 2.0:
                                result_data['wind_assisted'] = True
                        elif header == 'DATO':
                            result_data['date'] = text
                        elif header == 'STED':
                            # Get venue from title attribute if available
                            title = cell.get('title', '')
                            result_data['venue'] = title if title else text
                            result_data['meet_name'] = text
                        elif header == 'KLUBB':
                            result_data['club'] = text
                        elif header == 'PL':
                            result_data['placement'] = text
                        elif header == 'ÅR':
                            # Year column often contains year(age)
                            year_match = re.match(r'(\d{4})', text)
                            if year_match:
                                result_data['year'] = int(year_match.group(1))
                            age_match = re.search(r'\((\d+)\)', text)
                            if age_match:
                                result_data['age'] = int(age_match.group(1))

                    if result_data.get('performance'):
                        results.append(result_data)

                except Exception as e:
                    print(f"Error parsing row: {e}")
                    continue

    return {
        'athlete_id': athlete_id,
        'name': name,
        'birth_date': birth_date,
        'results': results
    }


def test_athlete(athlete_id, expected_name=None):
    """Test scraping for a specific athlete and print summary."""
    print(f"\n{'='*70}")
    print(f"Testing athlete ID: {athlete_id}")
    print('='*70)

    data = fetch_athlete_all_results(athlete_id)

    if not data:
        print("FAILED to fetch athlete!")
        return

    print(f"Name: {data['name']}")
    print(f"Birth date: {data['birth_date']}")
    print(f"Total results: {len(data['results'])}")

    # Count by event
    by_event = {}
    for r in data['results']:
        event = r.get('event', 'Unknown')
        indoor = r.get('indoor')
        key = f"{event} ({'inne' if indoor else 'ute'})"
        if key not in by_event:
            by_event[key] = []
        by_event[key].append(r)

    print(f"\nResults by event:")
    for event, results in sorted(by_event.items()):
        print(f"  {event}: {len(results)} results")
        # Show best result for this event
        best = None
        for r in results:
            if r.get('performance'):
                if best is None or r['performance'] < best['performance']:
                    best = r
        if best:
            wind_str = f" ({best['wind']:+.1f})" if best.get('wind') else ""
            wa_str = " [WIND ASSISTED]" if best.get('wind_assisted') else ""
            print(f"    Best: {best['performance']}{wind_str}{wa_str}")

    # Find wind-assisted results
    wind_assisted = [r for r in data['results'] if r.get('wind_assisted')]
    if wind_assisted:
        print(f"\nWind-assisted results (>2.0 m/s): {len(wind_assisted)}")
        for r in wind_assisted[:5]:  # Show first 5
            print(f"  {r['event']}: {r['performance']} ({r['wind']:+.1f}) - {r.get('date', '?')}")

    return data


if __name__ == '__main__':
    # Test with known athletes

    # 1. Karsten Warholm (should have 45.94 from Tokyo)
    print("\n" + "="*70)
    print("TESTING: Karsten Warholm (ID 1172)")
    print("Expected: Should have 45.94 from Tokyo Olympics")
    print("="*70)
    warholm = test_athlete(1172)

    # Check for 45.94
    if warholm:
        found_45_94 = any(
            r.get('performance') == '45.94'
            for r in warholm['results']
        )
        print(f"\n>>> Found 45.94: {'YES' if found_45_94 else 'NO!!!'}")

    time.sleep(1)

    # 2. Atle Guttormsen (should have 15.19 as best legal result, not 15.36)
    print("\n" + "="*70)
    print("TESTING: Atle Guttormsen (ID 12318)")
    print("Expected: 15.19 (+1.1) as legal PB, 15.36 (+3.6) is wind-assisted")
    print("="*70)
    guttormsen = test_athlete(12318)

    # Check for both results
    if guttormsen:
        found_15_19 = any(
            r.get('performance') == '15.19'
            for r in guttormsen['results']
        )
        found_15_36 = any(
            r.get('performance') == '15.36' and r.get('wind_assisted')
            for r in guttormsen['results']
        )
        print(f"\n>>> Found 15.19: {'YES' if found_15_19 else 'NO!!!'}")
        print(f">>> Found 15.36 as wind-assisted: {'YES' if found_15_36 else 'NO!!!'}")

    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
