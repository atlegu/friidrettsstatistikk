-- Supabase Schema for Norwegian Athletics Statistics
-- Run this in Supabase SQL Editor to create tables

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
-- CLUBS TABLE (normalized)
-- =====================================================
CREATE TABLE IF NOT EXISTS clubs (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- EVENTS TABLE (normalized)
-- =====================================================
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    category TEXT,  -- 'sprint', 'middle_distance', 'long_distance', 'hurdles', 'jumps', 'throws', 'combined', 'walk'
    is_timed BOOLEAN DEFAULT TRUE,  -- TRUE for running events, FALSE for field events
    higher_is_better BOOLEAN DEFAULT FALSE,  -- FALSE for timed events, TRUE for field/combined
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- VENUES TABLE (normalized)
-- =====================================================
CREATE TABLE IF NOT EXISTS venues (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    short_name TEXT,
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
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(name, date)
);

-- =====================================================
-- RESULTS TABLE (main data)
-- =====================================================
CREATE TABLE IF NOT EXISTS results (
    id SERIAL PRIMARY KEY,
    athlete_id INTEGER NOT NULL REFERENCES athletes(id),
    event_id INTEGER NOT NULL REFERENCES events(id),
    club_id INTEGER REFERENCES clubs(id),
    competition_id INTEGER REFERENCES competitions(id),

    -- Result data (stored as raw text to preserve original format)
    result TEXT NOT NULL,
    wind TEXT,  -- Wind reading if applicable (e.g., "+1,4" or "-0,5")

    -- Context
    year INTEGER NOT NULL,
    age INTEGER,  -- Age at time of competition
    date DATE,
    placement TEXT,  -- Can include heat info like "2-h1", "1-fi", "D"

    -- Indoor/Outdoor
    is_outdoor BOOLEAN NOT NULL,

    -- Validity
    is_approved BOOLEAN DEFAULT TRUE,
    rejection_reason TEXT,  -- If not approved

    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Prevent exact duplicates
    UNIQUE(athlete_id, event_id, date, result, placement)
);

-- =====================================================
-- INDEXES
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_results_athlete ON results(athlete_id);
CREATE INDEX IF NOT EXISTS idx_results_event ON results(event_id);
CREATE INDEX IF NOT EXISTS idx_results_date ON results(date);
CREATE INDEX IF NOT EXISTS idx_results_year ON results(year);
CREATE INDEX IF NOT EXISTS idx_results_outdoor ON results(is_outdoor);
CREATE INDEX IF NOT EXISTS idx_results_approved ON results(is_approved);
CREATE INDEX IF NOT EXISTS idx_athletes_name ON athletes(name);
CREATE INDEX IF NOT EXISTS idx_clubs_name ON clubs(name);
CREATE INDEX IF NOT EXISTS idx_events_name ON events(name);

-- =====================================================
-- HELPER FUNCTION: Update timestamps
-- =====================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for athletes
DROP TRIGGER IF EXISTS update_athletes_updated_at ON athletes;
CREATE TRIGGER update_athletes_updated_at
    BEFORE UPDATE ON athletes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- VIEW: Full results with joined data
-- =====================================================
CREATE OR REPLACE VIEW results_full AS
SELECT
    r.id,
    a.id as athlete_id,
    a.name as athlete_name,
    a.birth_date,
    e.name as event_name,
    e.category as event_category,
    c.name as club_name,
    comp.name as competition_name,
    v.name as venue_name,
    r.result,
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
-- EXAMPLE QUERIES
-- =====================================================

-- Get all results for an athlete:
-- SELECT * FROM results_full WHERE athlete_name = 'Simen Guttormsen' ORDER BY date DESC;

-- Get top 10 results for 100m men:
-- SELECT * FROM results_full WHERE event_name = '100 meter' AND is_outdoor = true AND is_approved = true ORDER BY result ASC LIMIT 10;

-- Count results by year:
-- SELECT year, COUNT(*) FROM results GROUP BY year ORDER BY year;
