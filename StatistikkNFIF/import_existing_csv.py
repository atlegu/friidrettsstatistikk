"""
Import existing scraped CSV data into the new SQLite database.

This script imports data from your existing scraped_data/*.csv files
into the new normalized database structure.

Usage:
    python import_existing_csv.py
"""

import sqlite3
import csv
import os
import sys
from datetime import datetime

DB_PATH = "athletics_stats.db"
SCRAPED_DATA_DIR = "scraped_data"


def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


class ImportCache:
    """Cache for normalized table lookups during import"""

    def __init__(self, conn):
        self.conn = conn
        self.clubs = {}
        self.events = {}
        self.venues = {}
        self.competitions = {}
        self._load_existing()

    def _load_existing(self):
        cursor = self.conn.cursor()
        for row in cursor.execute("SELECT id, name FROM clubs"):
            self.clubs[row['name']] = row['id']
        for row in cursor.execute("SELECT id, name FROM events"):
            self.events[row['name']] = row['id']
        for row in cursor.execute("SELECT id, name FROM venues"):
            self.venues[row['name']] = row['id']
        for row in cursor.execute("SELECT id, name, date, venue_id FROM competitions"):
            key = (row['name'], row['date'], row['venue_id'])
            self.competitions[key] = row['id']

    def get_or_create_club(self, name):
        if not name or name.strip() == '':
            return None
        name = name.strip()
        if name in self.clubs:
            return self.clubs[name]
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO clubs (name) VALUES (?)", (name,))
        cursor.execute("SELECT id FROM clubs WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            self.clubs[name] = row['id']
            return row['id']
        return None

    def get_or_create_event(self, name):
        if not name or name.strip() == '':
            return None
        name = name.strip()
        if name in self.events:
            return self.events[name]
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO events (name) VALUES (?)", (name,))
        cursor.execute("SELECT id FROM events WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            self.events[name] = row['id']
            return row['id']
        return None

    def get_or_create_venue(self, name):
        if not name or name.strip() == '':
            return None
        name = name.strip()
        if name in self.venues:
            return self.venues[name]
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO venues (name) VALUES (?)", (name,))
        cursor.execute("SELECT id FROM venues WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            self.venues[name] = row['id']
            return row['id']
        return None

    def get_or_create_competition(self, name, date, venue_id):
        if not name or name.strip() == '':
            return None
        name = name.strip()
        key = (name, date, venue_id)
        if key in self.competitions:
            return self.competitions[key]

        year = None
        if date:
            try:
                year = int(date.split('-')[0])
            except:
                pass

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO competitions (name, date, venue_id, year)
            VALUES (?, ?, ?, ?)
        """, (name, date, venue_id, year))
        cursor.execute("""
            SELECT id FROM competitions
            WHERE name = ? AND (date = ? OR (date IS NULL AND ? IS NULL))
            AND (venue_id = ? OR (venue_id IS NULL AND ? IS NULL))
        """, (name, date, date, venue_id, venue_id))
        row = cursor.fetchone()
        if row:
            self.competitions[key] = row['id']
            return row['id']
        return None


def import_athletes_csv(conn, filepath):
    """Import athletes from CSV"""
    if not os.path.exists(filepath):
        return 0

    count = 0
    cursor = conn.cursor()

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO athletes (id, name, birth_date)
                    VALUES (?, ?, ?)
                """, (
                    int(row['id']),
                    row['name'],
                    row.get('birth_date') or None
                ))
                count += 1
            except Exception as e:
                print(f"Error importing athlete: {e}")

    conn.commit()
    return count


def import_results_csv(conn, cache, filepath):
    """Import results from CSV"""
    if not os.path.exists(filepath):
        return 0

    count = 0
    cursor = conn.cursor()

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                athlete_id = int(row['athlete_id'])
                event_id = cache.get_or_create_event(row.get('event'))
                club_id = cache.get_or_create_club(row.get('club'))
                venue_id = cache.get_or_create_venue(row.get('venue'))
                competition_id = cache.get_or_create_competition(
                    row.get('competition'),
                    row.get('date'),
                    venue_id
                )

                # Parse boolean values
                is_outdoor = row.get('is_outdoor', 'True').lower() == 'true'
                is_approved = row.get('is_approved', 'True').lower() == 'true'

                # Parse numeric values
                year = int(row['year']) if row.get('year') else None
                age = int(row['age']) if row.get('age') else None

                cursor.execute("""
                    INSERT OR IGNORE INTO results (
                        athlete_id, event_id, club_id, competition_id,
                        result, wind, year, age, date, placement,
                        is_outdoor, is_approved, rejection_reason,
                        source_athlete_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    athlete_id, event_id, club_id, competition_id,
                    row.get('result'), row.get('wind'),
                    year, age, row.get('date'), row.get('placement'),
                    1 if is_outdoor else 0,
                    1 if is_approved else 0,
                    row.get('rejection_reason') or None,
                    athlete_id
                ))
                count += 1

            except Exception as e:
                print(f"Error importing result: {e} - Row: {row}")

    conn.commit()
    return count


def main():
    if not os.path.exists(DB_PATH):
        print(f"Database not found: {DB_PATH}")
        print("Run 'python comprehensive_scraper.py init' first")
        return

    if not os.path.exists(SCRAPED_DATA_DIR):
        print(f"Scraped data directory not found: {SCRAPED_DATA_DIR}")
        return

    # Find all CSV files
    athlete_files = sorted([f for f in os.listdir(SCRAPED_DATA_DIR) if f.startswith('athletes_') and f.endswith('.csv')])
    result_files = sorted([f for f in os.listdir(SCRAPED_DATA_DIR) if f.startswith('results_') and f.endswith('.csv')])

    if not athlete_files and not result_files:
        print("No CSV files found to import")
        return

    print(f"\nFound {len(athlete_files)} athlete files and {len(result_files)} result files")
    print("=" * 60)

    conn = get_connection()
    cache = ImportCache(conn)

    # Import athletes first
    total_athletes = 0
    for filename in athlete_files:
        filepath = os.path.join(SCRAPED_DATA_DIR, filename)
        count = import_athletes_csv(conn, filepath)
        print(f"  Imported {count} athletes from {filename}")
        total_athletes += count

    # Import results
    total_results = 0
    for filename in result_files:
        filepath = os.path.join(SCRAPED_DATA_DIR, filename)
        count = import_results_csv(conn, cache, filepath)
        print(f"  Imported {count} results from {filename}")
        total_results += count

    conn.close()

    print("=" * 60)
    print(f"\nImport complete!")
    print(f"  Total athletes: {total_athletes}")
    print(f"  Total results: {total_results}")
    print(f"\nRun 'python comprehensive_scraper.py status' to see full statistics")


if __name__ == "__main__":
    main()
