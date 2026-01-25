"""
Test the scraper on a few sample athletes
"""

import json
from scrape_all_results import fetch_athlete_results, parse_athlete_page

# Test athletes
TEST_IDS = [
    346,     # Simen Guttormsen - pole vaulter with lots of data
    10,      # Martin Berntzen Engevik - many results
    1000,    # Nina Katrine Brandt
    14975,   # Mathias Hove Johansen
]

def main():
    print("Testing scraper on sample athletes\n")
    print("=" * 60)

    for athlete_id in TEST_IDS:
        print(f"\nFetching athlete {athlete_id}...")

        html = fetch_athlete_results(athlete_id)
        data = parse_athlete_page(html, athlete_id)

        print(f"  Name: {data['name']}")
        print(f"  Birth date: {data['birth_date']}")
        print(f"  Total results: {len(data['results'])}")

        if data['results']:
            # Count by event
            events = {}
            for r in data['results']:
                events[r['event']] = events.get(r['event'], 0) + 1

            print(f"  Events: {len(events)}")
            for event, count in sorted(events.items(), key=lambda x: -x[1])[:5]:
                print(f"    - {event}: {count}")

            # Show sample results
            print(f"\n  Sample results:")
            for r in data['results'][:3]:
                print(f"    {r['event']}: {r['result']} ({r['wind'] or 'no wind'}) - {r['date']} - {r['placement']}")

            # Check for disqualified
            disqualified = [r for r in data['results'] if not r['is_approved']]
            if disqualified:
                print(f"\n  Disqualified results: {len(disqualified)}")
                for r in disqualified[:2]:
                    print(f"    {r['event']}: {r['result']} - {r['rejection_reason']}")

        print("-" * 60)


if __name__ == "__main__":
    main()
