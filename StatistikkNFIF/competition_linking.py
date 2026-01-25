"""
Competition Linking Utilities

This module provides tools to:
1. Group related competition records into "meets"
2. Identify and merge duplicate competitions
3. Query all results from a specific competition/meet

Usage:
    python competition_linking.py analyze      # Analyze competition patterns
    python competition_linking.py group        # Auto-group competitions
    python competition_linking.py search "NM"  # Find competitions by name
    python competition_linking.py show 123     # Show all results for a meet
"""

import sqlite3
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta

DB_PATH = "athletics_stats.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_competition_groups():
    """Create the competition_groups table for linking related competitions"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        -- A "meet" is a logical grouping of competitions (e.g., "NM 2023" spanning multiple days)
        CREATE TABLE IF NOT EXISTS meets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,              -- Canonical name (e.g., "NM Friidrett 2023")
            short_name TEXT,                 -- Short name (e.g., "NM 2023")
            year INTEGER,
            start_date TEXT,                 -- First day
            end_date TEXT,                   -- Last day
            venue_id INTEGER REFERENCES venues(id),
            is_championship INTEGER DEFAULT 0,  -- NM, UM, KM, etc.
            is_international INTEGER DEFAULT 0,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        -- Link table connecting competitions to meets
        CREATE TABLE IF NOT EXISTS competition_meet_links (
            competition_id INTEGER NOT NULL REFERENCES competitions(id),
            meet_id INTEGER NOT NULL REFERENCES meets(id),
            confidence REAL DEFAULT 1.0,     -- How confident we are in this link (1.0 = manual, <1 = auto)
            created_at TEXT DEFAULT (datetime('now')),
            PRIMARY KEY (competition_id, meet_id)
        );

        CREATE INDEX IF NOT EXISTS idx_meets_year ON meets(year);
        CREATE INDEX IF NOT EXISTS idx_meets_name ON meets(name);
        CREATE INDEX IF NOT EXISTS idx_comp_meet_links_meet ON competition_meet_links(meet_id);
        CREATE INDEX IF NOT EXISTS idx_comp_meet_links_comp ON competition_meet_links(competition_id);

        -- View: All results with meet information
        CREATE VIEW IF NOT EXISTS results_with_meets AS
        SELECT
            r.*,
            a.name as athlete_name,
            a.birth_date,
            e.name as event_name,
            e.category as event_category,
            cl.name as club_name,
            c.name as competition_name,
            v.name as venue_name,
            m.id as meet_id,
            m.name as meet_name,
            m.short_name as meet_short_name,
            m.is_championship
        FROM results r
        JOIN athletes a ON r.athlete_id = a.id
        JOIN events e ON r.event_id = e.id
        LEFT JOIN clubs cl ON r.club_id = cl.id
        LEFT JOIN competitions c ON r.competition_id = c.id
        LEFT JOIN venues v ON c.venue_id = v.id
        LEFT JOIN competition_meet_links cml ON c.id = cml.competition_id
        LEFT JOIN meets m ON cml.meet_id = m.id;
    """)

    conn.commit()
    conn.close()
    print("Competition groups tables created.")


def extract_meet_info(competition_name: str) -> dict:
    """Extract structured info from a competition name"""
    info = {
        'year': None,
        'is_championship': False,
        'championship_type': None,
        'base_name': competition_name
    }

    # Extract year
    year_match = re.search(r'(19|20)\d{2}', competition_name)
    if year_match:
        info['year'] = int(year_match.group())

    # Identify championships
    name_lower = competition_name.lower()

    championship_patterns = [
        (r'\bNM\b', 'NM', True),           # Norgesmesterskap
        (r'\bUM\b', 'UM', True),           # Ungdomsmesterskap
        (r'\bKM\b', 'KM', True),           # Kretsmesterskap
        (r'\bEM\b', 'EM', True),           # Europamesterskap
        (r'\bVM\b', 'VM', True),           # Verdensmesterskap
        (r'\bOL\b', 'OL', True),           # Olympiske Leker
        (r'norgesmesterskap', 'NM', True),
        (r'ungdomsmesterskap', 'UM', True),
        (r'europamesterskap', 'EM', True),
        (r'diamond\s*league', 'Diamond League', True),
        (r'bislett\s*games', 'Bislett Games', True),
    ]

    for pattern, champ_type, is_champ in championship_patterns:
        if re.search(pattern, competition_name, re.IGNORECASE):
            info['is_championship'] = is_champ
            info['championship_type'] = champ_type
            break

    return info


def analyze_competitions():
    """Analyze competition data to find patterns and potential groupings"""
    conn = get_connection()
    cursor = conn.cursor()

    print("\n" + "=" * 70)
    print("COMPETITION ANALYSIS")
    print("=" * 70)

    # Total competitions
    cursor.execute("SELECT COUNT(*) FROM competitions")
    total = cursor.fetchone()[0]
    print(f"\nTotal competition records: {total:,}")

    # Competitions with results
    cursor.execute("""
        SELECT COUNT(DISTINCT competition_id)
        FROM results
        WHERE competition_id IS NOT NULL
    """)
    with_results = cursor.fetchone()[0]
    print(f"Competitions with results: {with_results:,}")

    # Find potential NM/UM championships
    print("\n" + "-" * 70)
    print("DETECTED CHAMPIONSHIPS (sample):")
    print("-" * 70)

    cursor.execute("""
        SELECT c.id, c.name, c.date, c.year, v.name as venue, COUNT(r.id) as result_count
        FROM competitions c
        LEFT JOIN venues v ON c.venue_id = v.id
        LEFT JOIN results r ON r.competition_id = c.id
        WHERE c.name LIKE '%NM%' OR c.name LIKE '%UM%' OR c.name LIKE '%Norgesmesterskap%'
        GROUP BY c.id
        ORDER BY c.year DESC, c.date DESC
        LIMIT 20
    """)

    for row in cursor.fetchall():
        print(f"  [{row['id']:>6}] {row['date']} | {row['name'][:50]:<50} | {row['result_count']:>5} results")

    # Find multi-day competitions (same name, different dates)
    print("\n" + "-" * 70)
    print("MULTI-DAY COMPETITIONS (potential groupings):")
    print("-" * 70)

    cursor.execute("""
        SELECT name, COUNT(DISTINCT date) as days, MIN(date) as start, MAX(date) as end,
               COUNT(DISTINCT c.id) as comp_records, SUM(result_count) as total_results
        FROM competitions c
        LEFT JOIN (
            SELECT competition_id, COUNT(*) as result_count
            FROM results
            GROUP BY competition_id
        ) r ON c.id = r.competition_id
        GROUP BY name
        HAVING days > 1
        ORDER BY total_results DESC
        LIMIT 15
    """)

    for row in cursor.fetchall():
        print(f"  {row['days']} days | {row['start']} to {row['end']} | {row['name'][:45]:<45} | {row['total_results'] or 0:>6} results")

    # Venue name variations
    print("\n" + "-" * 70)
    print("POTENTIAL VENUE DUPLICATES:")
    print("-" * 70)

    cursor.execute("""
        SELECT name, COUNT(*) as result_count
        FROM venues v
        JOIN competitions c ON c.venue_id = v.id
        JOIN results r ON r.competition_id = c.id
        GROUP BY v.id
        ORDER BY result_count DESC
        LIMIT 20
    """)

    venues = cursor.fetchall()
    for v in venues:
        print(f"  {v['result_count']:>8} results | {v['name']}")

    conn.close()
    print("\n" + "=" * 70)


def auto_group_competitions():
    """Automatically group competitions into meets based on name patterns"""
    conn = get_connection()
    cursor = conn.cursor()

    print("\nAuto-grouping competitions into meets...")

    # Get all competitions
    cursor.execute("""
        SELECT c.id, c.name, c.date, c.year, c.venue_id, v.name as venue_name
        FROM competitions c
        LEFT JOIN venues v ON c.venue_id = v.id
        ORDER BY c.name, c.date
    """)

    competitions = cursor.fetchall()

    # Group by normalized name + year
    groups = defaultdict(list)

    for comp in competitions:
        name = comp['name'] or ''
        year = comp['year']

        # Normalize the name
        # Remove location prefix (e.g., "Kristiansand, " or "Oslo/Bi, ")
        normalized = re.sub(r'^[^,]+,\s*', '', name)
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())

        # Create group key
        key = (normalized, year)
        groups[key].append(comp)

    # Create meets for groups with multiple competitions or championships
    meets_created = 0
    links_created = 0

    for (normalized_name, year), comps in groups.items():
        if not normalized_name:
            continue

        info = extract_meet_info(normalized_name)

        # Only create meets for:
        # 1. Multi-day events (multiple competition records)
        # 2. Championships
        # 3. Events with significant results

        total_results = 0
        for c in comps:
            cursor.execute("SELECT COUNT(*) FROM results WHERE competition_id = ?", (c['id'],))
            total_results += cursor.fetchone()[0]

        should_create = (
            len(comps) > 1 or
            info['is_championship'] or
            total_results >= 50
        )

        if should_create:
            # Find date range
            dates = [c['date'] for c in comps if c['date']]
            start_date = min(dates) if dates else None
            end_date = max(dates) if dates else None

            # Use most common venue
            venue_ids = [c['venue_id'] for c in comps if c['venue_id']]
            venue_id = max(set(venue_ids), key=venue_ids.count) if venue_ids else None

            # Create short name
            short_name = None
            if info['championship_type'] and year:
                short_name = f"{info['championship_type']} {year}"

            # Insert meet
            cursor.execute("""
                INSERT INTO meets (name, short_name, year, start_date, end_date, venue_id, is_championship)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                normalized_name,
                short_name,
                year,
                start_date,
                end_date,
                venue_id,
                1 if info['is_championship'] else 0
            ))

            meet_id = cursor.lastrowid
            meets_created += 1

            # Link competitions to meet
            for comp in comps:
                cursor.execute("""
                    INSERT OR IGNORE INTO competition_meet_links (competition_id, meet_id, confidence)
                    VALUES (?, ?, ?)
                """, (comp['id'], meet_id, 0.8))  # 0.8 confidence for auto-grouping
                links_created += 1

    conn.commit()
    conn.close()

    print(f"Created {meets_created} meets")
    print(f"Created {links_created} competition links")


def search_competitions(query: str):
    """Search for competitions/meets by name"""
    conn = get_connection()
    cursor = conn.cursor()

    print(f"\nSearching for: '{query}'")
    print("=" * 70)

    # Search meets first
    cursor.execute("""
        SELECT m.id, m.name, m.short_name, m.year, m.start_date, m.end_date,
               v.name as venue, m.is_championship,
               COUNT(DISTINCT cml.competition_id) as comp_count,
               (SELECT COUNT(*) FROM results r
                JOIN competition_meet_links cml2 ON r.competition_id = cml2.competition_id
                WHERE cml2.meet_id = m.id) as result_count
        FROM meets m
        LEFT JOIN venues v ON m.venue_id = v.id
        LEFT JOIN competition_meet_links cml ON m.id = cml.meet_id
        WHERE m.name LIKE ? OR m.short_name LIKE ?
        GROUP BY m.id
        ORDER BY m.year DESC, m.start_date DESC
        LIMIT 20
    """, (f'%{query}%', f'%{query}%'))

    meets = cursor.fetchall()

    if meets:
        print("\nMEETS FOUND:")
        print("-" * 70)
        for m in meets:
            champ = "[CHAMP]" if m['is_championship'] else ""
            print(f"  Meet #{m['id']}: {m['name']}")
            print(f"    {m['start_date']} to {m['end_date']} | {m['venue'] or 'Unknown venue'}")
            print(f"    {m['comp_count']} competition records | {m['result_count']} results {champ}")
            print()

    # Also search raw competitions
    cursor.execute("""
        SELECT c.id, c.name, c.date, v.name as venue, COUNT(r.id) as result_count
        FROM competitions c
        LEFT JOIN venues v ON c.venue_id = v.id
        LEFT JOIN results r ON r.competition_id = c.id
        WHERE c.name LIKE ?
        GROUP BY c.id
        ORDER BY c.date DESC
        LIMIT 20
    """, (f'%{query}%',))

    comps = cursor.fetchall()

    if comps:
        print("\nRAW COMPETITION RECORDS:")
        print("-" * 70)
        for c in comps:
            print(f"  [{c['id']:>6}] {c['date']} | {c['name'][:50]:<50} | {c['result_count']:>5} results")

    conn.close()


def show_meet_results(meet_id: int):
    """Show all results from a specific meet"""
    conn = get_connection()
    cursor = conn.cursor()

    # Get meet info
    cursor.execute("""
        SELECT m.*, v.name as venue_name
        FROM meets m
        LEFT JOIN venues v ON m.venue_id = v.id
        WHERE m.id = ?
    """, (meet_id,))

    meet = cursor.fetchone()
    if not meet:
        print(f"Meet #{meet_id} not found")
        return

    print("\n" + "=" * 70)
    print(f"MEET: {meet['name']}")
    print(f"Date: {meet['start_date']} to {meet['end_date']}")
    print(f"Venue: {meet['venue_name'] or 'Unknown'}")
    print("=" * 70)

    # Get all results grouped by event
    cursor.execute("""
        SELECT
            e.name as event_name,
            a.name as athlete_name,
            r.result,
            r.result_numeric,
            r.wind,
            r.placement,
            cl.name as club_name,
            r.is_outdoor,
            c.date
        FROM results r
        JOIN competition_meet_links cml ON r.competition_id = cml.competition_id
        JOIN athletes a ON r.athlete_id = a.id
        JOIN events e ON r.event_id = e.id
        LEFT JOIN clubs cl ON r.club_id = cl.id
        LEFT JOIN competitions c ON r.competition_id = c.id
        WHERE cml.meet_id = ?
        ORDER BY e.name, r.result_numeric ASC
    """, (meet_id,))

    results = cursor.fetchall()

    current_event = None
    for r in results:
        if r['event_name'] != current_event:
            current_event = r['event_name']
            indoor_outdoor = "Outdoor" if r['is_outdoor'] else "Indoor"
            print(f"\n{current_event} ({indoor_outdoor}):")
            print("-" * 60)

        wind = f"({r['wind']})" if r['wind'] else ""
        print(f"  {r['placement'] or '-':>6} | {r['result']:>10} {wind:<8} | {r['athlete_name']:<25} | {r['club_name'] or ''}")

    print(f"\nTotal results: {len(results)}")
    conn.close()


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python competition_linking.py init              # Create grouping tables")
        print("  python competition_linking.py analyze           # Analyze competition patterns")
        print("  python competition_linking.py group             # Auto-group competitions")
        print("  python competition_linking.py search <query>    # Search competitions")
        print("  python competition_linking.py show <meet_id>    # Show meet results")
        return

    command = sys.argv[1].lower()

    if command == 'init':
        init_competition_groups()
    elif command == 'analyze':
        analyze_competitions()
    elif command == 'group':
        init_competition_groups()
        auto_group_competitions()
    elif command == 'search' and len(sys.argv) > 2:
        search_competitions(sys.argv[2])
    elif command == 'show' and len(sys.argv) > 2:
        show_meet_results(int(sys.argv[2]))
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
