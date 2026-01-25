"""
Fetch all athletes from the search page using POST requests
No browser automation needed - it's a simple form!
"""

import requests
import os
import time

OUTPUT_DIR = "athlete_search_html"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Norwegian alphabet (excluding X which has no athletes)
LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWYZÆØÅ")

def fetch_athletes_by_letter(letter: str) -> str:
    """Fetch all athletes whose last name starts with the given letter"""
    url = "https://www.minfriidrettsstatistikk.info/php/UtoverSok.php"

    data = {
        "cmd": "SearchAthlete",
        "showchar": letter
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    response = requests.post(url, data=data, headers=headers)
    response.encoding = 'utf-8'

    return response.text


def main():
    print("=" * 60)
    print("Fetching all athletes by last name letter")
    print("=" * 60)

    total_athletes = 0
    all_athlete_ids = []

    for letter in LETTERS:
        print(f"Fetching letter: {letter}...", end=" ", flush=True)

        try:
            html = fetch_athletes_by_letter(letter)

            # Save to file
            filename = f"search_{letter}.html"
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)

            # Count athletes found
            athlete_count = html.count("showathl=")
            total_athletes += athlete_count

            # Extract athlete IDs
            import re
            ids = re.findall(r'showathl=(\d+)', html)
            all_athlete_ids.extend(ids)

            print(f"✓ Found {athlete_count} athletes ({len(html):,} bytes)")

            # Be nice to the server
            time.sleep(0.3)

        except Exception as e:
            print(f"✗ Error: {e}")

    print("\n" + "=" * 60)
    print(f"TOTAL: {total_athletes} athlete entries")
    print(f"Unique athlete IDs: {len(set(all_athlete_ids))}")
    print("=" * 60)

    # Save all athlete IDs to a file
    unique_ids = sorted(set(all_athlete_ids), key=int)
    ids_file = os.path.join(OUTPUT_DIR, "_all_athlete_ids.txt")
    with open(ids_file, 'w') as f:
        for aid in unique_ids:
            f.write(f"{aid}\n")
    print(f"\nAll athlete IDs saved to: {ids_file}")

    # Also save as JSON for easier processing
    import json
    json_file = os.path.join(OUTPUT_DIR, "_all_athlete_ids.json")
    with open(json_file, 'w') as f:
        json.dump(unique_ids, f)
    print(f"All athlete IDs saved to: {json_file}")

    print(f"\nHTML files saved to: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
