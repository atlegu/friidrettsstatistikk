"""
Export SQLite database to Supabase-compatible format.

This script exports data from the local SQLite database to:
1. CSV files for bulk import
2. SQL statements for direct execution

Usage:
    python export_to_supabase.py csv       # Export to CSV files
    python export_to_supabase.py sql       # Generate SQL insert statements
    python export_to_supabase.py stats     # Show export statistics
"""

import sqlite3
import csv
import os
import sys
from datetime import datetime

DB_PATH = "athletics_stats.db"
EXPORT_DIR = "supabase_export"


def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def export_to_csv():
    """Export all tables to CSV files for Supabase import"""
    os.makedirs(EXPORT_DIR, exist_ok=True)

    conn = get_connection()
    cursor = conn.cursor()

    # Tables to export in dependency order
    tables = [
        ('athletes', ['id', 'name', 'birth_date', 'created_at', 'updated_at']),
        ('clubs', ['id', 'name', 'created_at']),
        ('events', ['id', 'name', 'category', 'is_timed', 'higher_is_better', 'created_at']),
        ('venues', ['id', 'name', 'created_at']),
        ('competitions', ['id', 'name', 'venue_id', 'date', 'year', 'created_at']),
        ('results', [
            'id', 'athlete_id', 'event_id', 'club_id', 'competition_id',
            'result', 'result_numeric', 'wind', 'year', 'age', 'date',
            'placement', 'is_outdoor', 'is_approved', 'rejection_reason',
            'source_athlete_id', 'created_at'
        ]),
    ]

    print("\nExporting tables to CSV...")
    print("=" * 60)

    for table_name, columns in tables:
        output_file = os.path.join(EXPORT_DIR, f"{table_name}.csv")

        # Get count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]

        # Export data
        cursor.execute(f"SELECT {', '.join(columns)} FROM {table_name}")

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(columns)

            batch_size = 10000
            while True:
                rows = cursor.fetchmany(batch_size)
                if not rows:
                    break
                for row in rows:
                    # Convert Row object to list, handling booleans for Supabase
                    row_data = []
                    for i, col in enumerate(columns):
                        val = row[i]
                        # Convert SQLite integers back to booleans for boolean columns
                        if col in ('is_timed', 'higher_is_better', 'is_outdoor', 'is_approved'):
                            val = 'true' if val else 'false'
                        row_data.append(val)
                    writer.writerow(row_data)

        print(f"  {table_name}: {count:,} rows -> {output_file}")

    conn.close()

    print("=" * 60)
    print(f"\nCSV files exported to: {EXPORT_DIR}/")
    print("\nTo import to Supabase:")
    print("1. Create tables using the Supabase SQL editor (see schema.sql)")
    print("2. Import CSV files in order: athletes, clubs, events, venues, competitions, results")
    print("3. Reset sequences after import")


def generate_supabase_schema():
    """Generate Supabase-compatible PostgreSQL schema"""
    schema = """-- Supabase Schema for Norwegian Athletics Statistics
-- Run this in Supabase SQL Editor to create tables

-- Enable UUID extension if needed
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- ATHLETES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS athletes (
    id INTEGER PRIMARY KEY,  -- Original system ID
    name TEXT NOT NULL,
    birth_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- CLUBS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS clubs (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- EVENTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    category TEXT,
    is_timed BOOLEAN DEFAULT TRUE,
    higher_is_better BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- VENUES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS venues (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- COMPETITIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS competitions (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    venue_id INTEGER REFERENCES venues(id),
    date DATE,
    year INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(name, date, venue_id)
);

-- =====================================================
-- RESULTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS results (
    id SERIAL PRIMARY KEY,
    athlete_id INTEGER NOT NULL REFERENCES athletes(id),
    event_id INTEGER NOT NULL REFERENCES events(id),
    club_id INTEGER REFERENCES clubs(id),
    competition_id INTEGER REFERENCES competitions(id),
    result TEXT NOT NULL,
    result_numeric DOUBLE PRECISION,
    wind TEXT,
    year INTEGER NOT NULL,
    age INTEGER,
    date DATE,
    placement TEXT,
    is_outdoor BOOLEAN NOT NULL,
    is_approved BOOLEAN DEFAULT TRUE,
    rejection_reason TEXT,
    source_athlete_id INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(athlete_id, event_id, date, result, placement, is_outdoor)
);

-- =====================================================
-- INDEXES
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_results_athlete ON results(athlete_id);
CREATE INDEX IF NOT EXISTS idx_results_event ON results(event_id);
CREATE INDEX IF NOT EXISTS idx_results_competition ON results(competition_id);
CREATE INDEX IF NOT EXISTS idx_results_date ON results(date);
CREATE INDEX IF NOT EXISTS idx_results_year ON results(year);
CREATE INDEX IF NOT EXISTS idx_results_outdoor ON results(is_outdoor);
CREATE INDEX IF NOT EXISTS idx_results_approved ON results(is_approved);
CREATE INDEX IF NOT EXISTS idx_results_numeric ON results(result_numeric);
CREATE INDEX IF NOT EXISTS idx_athletes_name ON athletes(name);
CREATE INDEX IF NOT EXISTS idx_competitions_date ON competitions(date);
CREATE INDEX IF NOT EXISTS idx_competitions_year ON competitions(year);

-- =====================================================
-- VIEWS
-- =====================================================
CREATE OR REPLACE VIEW results_full AS
SELECT
    r.id,
    a.id as athlete_id,
    a.name as athlete_name,
    a.birth_date,
    e.id as event_id,
    e.name as event_name,
    e.category as event_category,
    c.id as club_id,
    c.name as club_name,
    comp.id as competition_id,
    comp.name as competition_name,
    v.id as venue_id,
    v.name as venue_name,
    r.result,
    r.result_numeric,
    r.wind,
    r.year,
    r.age,
    r.date,
    r.placement,
    r.is_outdoor,
    r.is_approved,
    r.rejection_reason
FROM results r
JOIN athletes a ON r.athlete_id = a.id
JOIN events e ON r.event_id = e.id
LEFT JOIN clubs c ON r.club_id = c.id
LEFT JOIN competitions comp ON r.competition_id = comp.id
LEFT JOIN venues v ON comp.venue_id = v.id;

-- =====================================================
-- USEFUL QUERIES
-- =====================================================

-- Get athlete personal bests (outdoor, approved only):
-- SELECT athlete_name, event_name, MIN(result) as pb, date
-- FROM results_full
-- WHERE is_outdoor = true AND is_approved = true AND event_category IN ('sprint', 'middle_distance')
-- GROUP BY athlete_id, event_id
-- ORDER BY athlete_name, event_name;

-- Get rankings for a specific event:
-- SELECT athlete_name, result, result_numeric, date, competition_name, venue_name
-- FROM results_full
-- WHERE event_name = '100 meter' AND is_outdoor = true AND is_approved = true
-- ORDER BY result_numeric ASC
-- LIMIT 100;

-- Get all results for a competition:
-- SELECT athlete_name, event_name, result, placement
-- FROM results_full
-- WHERE competition_name LIKE '%NM%' AND year = 2023
-- ORDER BY event_name, placement;
"""

    output_file = os.path.join(EXPORT_DIR, "supabase_schema.sql")
    os.makedirs(EXPORT_DIR, exist_ok=True)

    with open(output_file, 'w') as f:
        f.write(schema)

    print(f"\nSupabase schema written to: {output_file}")


def show_stats():
    """Show statistics about the data to be exported"""
    conn = get_connection()
    cursor = conn.cursor()

    print("\n" + "=" * 60)
    print("EXPORT STATISTICS")
    print("=" * 60)

    tables = ['athletes', 'clubs', 'events', 'venues', 'competitions', 'results']

    print("\nTable sizes:")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count:,} rows")

    # Estimate CSV file sizes
    print("\nEstimated export sizes:")
    cursor.execute("SELECT COUNT(*) FROM results")
    result_count = cursor.fetchone()[0]
    # Rough estimate: 200 bytes per result row
    estimated_results_size = result_count * 200 / (1024 * 1024)
    print(f"  results.csv: ~{estimated_results_size:.1f} MB")

    # Data quality summary
    print("\nData quality:")

    cursor.execute("SELECT COUNT(*) FROM athletes WHERE birth_date IS NOT NULL")
    athletes_with_dob = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM athletes")
    total_athletes = cursor.fetchone()[0]
    print(f"  Athletes with birth date: {athletes_with_dob:,}/{total_athletes:,} ({100*athletes_with_dob/total_athletes:.1f}%)")

    cursor.execute("SELECT COUNT(*) FROM results WHERE competition_id IS NOT NULL")
    results_with_comp = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM results")
    total_results = cursor.fetchone()[0]
    print(f"  Results with competition: {results_with_comp:,}/{total_results:,} ({100*results_with_comp/total_results:.1f}%)")

    cursor.execute("SELECT COUNT(*) FROM results WHERE result_numeric IS NOT NULL")
    results_with_numeric = cursor.fetchone()[0]
    print(f"  Results with numeric value: {results_with_numeric:,}/{total_results:,} ({100*results_with_numeric/total_results:.1f}%)")

    cursor.execute("SELECT COUNT(*) FROM results WHERE is_approved = 1")
    approved = cursor.fetchone()[0]
    print(f"  Approved results: {approved:,}/{total_results:,} ({100*approved/total_results:.1f}%)")

    # Year range
    cursor.execute("SELECT MIN(year), MAX(year) FROM results WHERE year IS NOT NULL")
    row = cursor.fetchone()
    print(f"\n  Year range: {row[0]} - {row[1]}")

    conn.close()
    print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python export_to_supabase.py csv      # Export to CSV files")
        print("  python export_to_supabase.py schema   # Generate Supabase schema")
        print("  python export_to_supabase.py stats    # Show export statistics")
        print("  python export_to_supabase.py all      # Do everything")
        return

    if not os.path.exists(DB_PATH):
        print(f"Database not found: {DB_PATH}")
        print("Run 'python comprehensive_scraper.py init' first")
        return

    command = sys.argv[1].lower()

    if command == 'csv':
        export_to_csv()
    elif command == 'schema':
        generate_supabase_schema()
    elif command == 'stats':
        show_stats()
    elif command == 'all':
        generate_supabase_schema()
        show_stats()
        export_to_csv()
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
