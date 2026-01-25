-- Improved Schema for Norwegian Athletics Statistics
-- Designed for SQLite first, then export to Supabase

-- =====================================================
-- ATHLETES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS athletes (
    id INTEGER PRIMARY KEY,  -- Original system ID from source
    name TEXT NOT NULL,
    birth_date TEXT,  -- YYYY-MM-DD format
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- =====================================================
-- CLUBS TABLE (normalized)
-- =====================================================
CREATE TABLE IF NOT EXISTS clubs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

-- =====================================================
-- EVENTS TABLE (normalized)
-- =====================================================
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    category TEXT,  -- 'sprint', 'middle_distance', 'long_distance', 'hurdles', 'jumps', 'throws', 'combined', 'walk', 'relay'
    is_timed INTEGER DEFAULT 1,  -- 1 for running events, 0 for field events
    higher_is_better INTEGER DEFAULT 0,  -- 0 for timed events, 1 for field/combined
    created_at TEXT DEFAULT (datetime('now'))
);

-- =====================================================
-- VENUES TABLE (normalized)
-- =====================================================
CREATE TABLE IF NOT EXISTS venues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,  -- Full venue name (from title attribute)
    created_at TEXT DEFAULT (datetime('now'))
);

-- =====================================================
-- COMPETITIONS TABLE
-- Now properly unique by name + date + venue
-- =====================================================
CREATE TABLE IF NOT EXISTS competitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    venue_id INTEGER REFERENCES venues(id),
    date TEXT,  -- YYYY-MM-DD format
    year INTEGER,  -- For easy filtering
    created_at TEXT DEFAULT (datetime('now')),
    -- A competition is unique by its name, date, AND venue
    UNIQUE(name, date, venue_id)
);

-- =====================================================
-- RESULTS TABLE (main data)
-- =====================================================
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    athlete_id INTEGER NOT NULL REFERENCES athletes(id),
    event_id INTEGER NOT NULL REFERENCES events(id),
    club_id INTEGER REFERENCES clubs(id),
    competition_id INTEGER REFERENCES competitions(id),

    -- Result data
    result TEXT NOT NULL,  -- Raw result string (e.g., "9,17" or "1,45,04")
    result_numeric REAL,   -- Normalized numeric value for sorting/comparison
    wind TEXT,  -- Wind reading if applicable (e.g., "+1,4")

    -- Context
    year INTEGER NOT NULL,
    age INTEGER,  -- Age at time of competition
    date TEXT,  -- YYYY-MM-DD format
    placement TEXT,  -- Can include heat info like "2-h1", "1-fi", "D", "M"

    -- Indoor/Outdoor
    is_outdoor INTEGER NOT NULL,  -- 1 for outdoor, 0 for indoor

    -- Validity
    is_approved INTEGER DEFAULT 1,  -- 1 for approved, 0 for not approved
    rejection_reason TEXT,  -- If not approved

    -- Source tracking
    source_athlete_id INTEGER,  -- Original athlete ID from scraping

    created_at TEXT DEFAULT (datetime('now')),

    -- Prevent exact duplicates
    UNIQUE(athlete_id, event_id, date, result, placement, is_outdoor)
);

-- =====================================================
-- SCRAPE PROGRESS TABLE (for resumable scraping)
-- =====================================================
CREATE TABLE IF NOT EXISTS scrape_progress (
    letter TEXT PRIMARY KEY,
    total_athletes INTEGER,
    processed_count INTEGER DEFAULT 0,
    last_athlete_index INTEGER DEFAULT 0,
    last_athlete_id INTEGER,
    started_at TEXT,
    updated_at TEXT DEFAULT (datetime('now')),
    completed_at TEXT
);

-- =====================================================
-- SCRAPE LOG TABLE (for debugging)
-- =====================================================
CREATE TABLE IF NOT EXISTS scrape_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    athlete_id INTEGER,
    status TEXT,  -- 'success', 'error', 'empty', 'skipped'
    message TEXT,
    results_count INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
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
CREATE INDEX IF NOT EXISTS idx_clubs_name ON clubs(name);
CREATE INDEX IF NOT EXISTS idx_events_name ON events(name);
CREATE INDEX IF NOT EXISTS idx_competitions_date ON competitions(date);
CREATE INDEX IF NOT EXISTS idx_competitions_year ON competitions(year);
CREATE INDEX IF NOT EXISTS idx_venues_name ON venues(name);

-- =====================================================
-- VIEW: Full results with all joined data
-- =====================================================
CREATE VIEW IF NOT EXISTS results_full AS
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
-- VIEW: Competition summary
-- =====================================================
CREATE VIEW IF NOT EXISTS competition_summary AS
SELECT
    comp.id,
    comp.name,
    v.name as venue_name,
    comp.date,
    comp.year,
    COUNT(DISTINCT r.athlete_id) as athlete_count,
    COUNT(r.id) as result_count,
    COUNT(DISTINCT r.event_id) as event_count
FROM competitions comp
LEFT JOIN venues v ON comp.venue_id = v.id
LEFT JOIN results r ON r.competition_id = comp.id
GROUP BY comp.id;

-- =====================================================
-- VIEW: Athlete summary
-- =====================================================
CREATE VIEW IF NOT EXISTS athlete_summary AS
SELECT
    a.id,
    a.name,
    a.birth_date,
    COUNT(r.id) as total_results,
    COUNT(DISTINCT r.event_id) as events_competed,
    MIN(r.year) as first_year,
    MAX(r.year) as last_year,
    COUNT(DISTINCT r.competition_id) as competitions_entered
FROM athletes a
LEFT JOIN results r ON r.athlete_id = a.id
GROUP BY a.id;
