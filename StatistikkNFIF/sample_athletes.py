"""
Sample athlete data fetcher
Fetches HTML from diverse athletes to identify edge cases before full scrape
"""

import requests
import time
import os

# Create output directory
OUTPUT_DIR = "sample_html"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Diverse sample of athlete IDs to test
# Mix of old/new, different event types expected
SAMPLE_ATHLETES = [
    # Low IDs (likely older athletes/data)
    1,
    10,
    50,
    100,
    500,

    # Mid-range IDs
    1000,
    5000,
    10000,
    15000,
    20000,

    # Higher IDs (likely newer athletes)
    30000,
    40000,
    50000,
    55000,
    60000,

    # Known athlete (Simen Guttormsen - pole vault)
    346,

    # Random samples across the range
    2500,
    7500,
    12500,
    17500,
    25000,
    35000,
    45000,
]

def fetch_athlete_results(athlete_id: int) -> str:
    """Fetch all results for an athlete using POST request"""
    url = "https://www.minfriidrettsstatistikk.info/php/UtoverStatistikk.php"

    data = {
        "athlete": athlete_id,
        "type": "RES"  # All results
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    response = requests.post(url, data=data, headers=headers)
    response.encoding = 'utf-8'

    return response.text


def extract_basic_info(html: str) -> dict:
    """Quick extraction of basic info to identify what type of athlete this is"""
    info = {
        "has_name": False,
        "name": None,
        "birth_date": None,
        "has_outdoor": False,
        "has_indoor": False,
        "events": [],
        "has_disqualified": False,
        "approximate_results": 0
    }

    # Check for name
    if '<div id="athlete">' in html:
        info["has_name"] = True
        # Simple extraction
        import re
        name_match = re.search(r'<h2>([^<]+)</h2>', html)
        if name_match:
            info["name"] = name_match.group(1)

        birth_match = re.search(r'Født: ([^<]+)</h3>', html)
        if birth_match:
            info["birth_date"] = birth_match.group(1)

    # Check sections
    info["has_outdoor"] = "UTENDØRS" in html
    info["has_indoor"] = "INNENDØRS" in html
    info["has_disqualified"] = "Ikke godkjente resultater" in html

    # Extract event names
    event_matches = re.findall(r'<div id="eventheader"><h3>([^<]+)', html)
    info["events"] = list(set(event_matches))

    # Count approximate results (count table rows)
    info["approximate_results"] = html.count("<tr><td>")

    return info


def main():
    print("=" * 60)
    print("Fetching sample athletes to identify edge cases")
    print("=" * 60)

    results_summary = []

    for athlete_id in SAMPLE_ATHLETES:
        print(f"\nFetching athlete ID: {athlete_id}...", end=" ")

        try:
            html = fetch_athlete_results(athlete_id)

            # Save raw HTML
            filepath = os.path.join(OUTPUT_DIR, f"athlete_{athlete_id}.html")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)

            # Extract basic info
            info = extract_basic_info(html)
            info["id"] = athlete_id
            info["file"] = filepath
            info["html_size"] = len(html)

            results_summary.append(info)

            if info["has_name"]:
                print(f"✓ {info['name']} - {len(info['events'])} events, ~{info['approximate_results']} results")
            else:
                print("✗ Empty/Invalid")

            # Be nice to the server
            time.sleep(0.5)

        except Exception as e:
            print(f"✗ Error: {e}")
            results_summary.append({"id": athlete_id, "error": str(e)})

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    valid_athletes = [r for r in results_summary if r.get("has_name")]
    empty_athletes = [r for r in results_summary if not r.get("has_name") and not r.get("error")]

    print(f"\nValid athletes: {len(valid_athletes)}")
    print(f"Empty/Invalid IDs: {len(empty_athletes)}")

    # Collect all unique events
    all_events = set()
    for r in valid_athletes:
        all_events.update(r.get("events", []))

    print(f"\nUnique events found: {len(all_events)}")
    for event in sorted(all_events):
        print(f"  - {event}")

    # Athletes with disqualified results
    disqualified = [r for r in valid_athletes if r.get("has_disqualified")]
    print(f"\nAthletes with disqualified results: {len(disqualified)}")

    # Indoor vs outdoor
    outdoor_only = [r for r in valid_athletes if r.get("has_outdoor") and not r.get("has_indoor")]
    indoor_only = [r for r in valid_athletes if r.get("has_indoor") and not r.get("has_outdoor")]
    both = [r for r in valid_athletes if r.get("has_indoor") and r.get("has_outdoor")]

    print(f"\nOutdoor only: {len(outdoor_only)}")
    print(f"Indoor only: {len(indoor_only)}")
    print(f"Both indoor & outdoor: {len(both)}")

    # Size distribution
    print(f"\nHTML size range:")
    sizes = [r.get("html_size", 0) for r in valid_athletes]
    if sizes:
        print(f"  Min: {min(sizes):,} bytes")
        print(f"  Max: {max(sizes):,} bytes")
        print(f"  Avg: {sum(sizes)//len(sizes):,} bytes")

    # Save summary to file
    summary_file = os.path.join(OUTPUT_DIR, "_summary.txt")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("ATHLETE SAMPLE SUMMARY\n")
        f.write("=" * 60 + "\n\n")

        for r in results_summary:
            if r.get("has_name"):
                f.write(f"ID {r['id']}: {r['name']}\n")
                f.write(f"  Born: {r.get('birth_date', 'Unknown')}\n")
                f.write(f"  Events: {', '.join(r.get('events', []))}\n")
                f.write(f"  Results: ~{r.get('approximate_results', 0)}\n")
                f.write(f"  Outdoor: {r.get('has_outdoor')}, Indoor: {r.get('has_indoor')}\n")
                f.write(f"  Has disqualified: {r.get('has_disqualified')}\n")
                f.write(f"  HTML size: {r.get('html_size', 0):,} bytes\n")
                f.write("\n")
            else:
                f.write(f"ID {r['id']}: EMPTY/INVALID\n\n")

        f.write("\nALL EVENTS FOUND:\n")
        for event in sorted(all_events):
            f.write(f"  - {event}\n")

    print(f"\nSummary saved to: {summary_file}")
    print(f"HTML files saved to: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
