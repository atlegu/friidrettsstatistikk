# Unified Norwegian Athletics Statistics Scraping Guide

## Overview

This guide describes the process of scraping the complete historical database from [minfriidrettsstatistikk.info](https://www.minfriidrettsstatistikk.info) - the official statistics system for Norges Friidrettsforbund (Norwegian Athletic Federation).

**Goal:** Build a complete, accurate, and properly linked database of all Norwegian athletics competition results.

**Challenge:** The source system has two different data access patterns:
- **2011 onwards:** Competitions have unique IDs and can be scraped directly
- **Pre-2011:** No competition IDs exist; data must be extracted from individual athlete profiles

**Solution:** A unified 3-phase scraping approach that combines both methods.

---

## Source System Analysis

### Available Endpoints

| Endpoint | Purpose | Data Available |
|----------|---------|----------------|
| `LandsStatistikk.php` | National rankings by event/class/year | Links to competition IDs (2011+ only) |
| `StevneResultater.php` | Full competition results | All results for a competition with metadata |
| `UtoverStatistikk.php` | Individual athlete profiles | All results for an athlete (all years) |
| `UtoverSok.php` | Athlete search by letter | List of all athlete IDs |

### Key Discovery: Competition Links Only Exist From 2011

```
Year    Competition Links Available
─────   ───────────────────────────
1990    ✗ No
2000    ✗ No
2010    ✗ No
2011    ✓ Yes (658 links found)
2012    ✓ Yes (862 links found)
...     ✓ Yes
2025    ✓ Yes
```

This means we need a **hybrid approach**:
- 2011+: Scrape via competitions (best quality)
- Pre-2011: Scrape via athletes (only option)

---

## Database Schema

### Entity Relationship

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  athletes   │     │   results   │     │competitions │
├─────────────┤     ├─────────────┤     ├─────────────┤
│ id          │◄────│ athlete_id  │     │ id          │
│ source_id   │     │ competition_│────►│ source_id   │
│ name        │     │ event_id    │     │ name        │
│ birth_date  │     │ club_id     │     │ venue       │
│ birth_year  │     │ result      │     │ organizer   │
└─────────────┘     │ wind        │     │ start_date  │
                    │ placement   │     │ end_date    │
┌─────────────┐     │ date        │     │ is_derived  │
│   events    │     │ year        │     └─────────────┘
├─────────────┤     │ age         │
│ id          │◄────│ is_outdoor  │     ┌─────────────┐
│ name        │     │ is_approved │     │   clubs     │
│ category    │     │ source      │     ├─────────────┤
│ is_timed    │     └─────────────┘     │ id          │
└─────────────┘                         │ name        │
                                        └─────────────┘
```

### Key Design Decisions

1. **Competitions Table**
   - `source_id`: Real competition ID from source system (2011+ only, NULL for derived)
   - `is_derived`: Flag indicating if created from athlete scrape (pre-2011 data)
   - `derived_hash`: Unique hash of `date|venue|name` for derived competitions

2. **Athletes Table**
   - `source_id`: Athlete ID from source system
   - `birth_date`: Full date (YYYY-MM-DD) from athlete scrape
   - `birth_year`: Just year, used for matching across sources

3. **Results Table**
   - `source`: Tracks whether result came from 'competition_scrape' or 'athlete_scrape'
   - Unique constraint prevents duplicates: `(athlete_id, event_id, date, result, placement, is_outdoor)`

---

## Phase 1: Competition Scraping (2011+)

### Purpose
Scrape all competitions that have proper IDs in the source system, getting the highest quality data with full metadata.

### Process

```
Step 1: Discover Competition IDs
────────────────────────────────
For each combination of:
  • Event (100m, 200m, high jump, etc.) - ~20 events
  • Class (Men Senior, Women U20, etc.) - ~50 classes
  • Year (2011-2025) - ~14 years
  • Indoor/Outdoor - 2 options

Request: GET LandsStatistikk.php?showclass=X&showevent=Y&showseason=Z&outdoor=Y/N

Extract: All competition IDs from onclick="posttoresultlist(XXXXXX)"

Total requests: ~28,000
Unique competitions found: ~5,000-10,000
```

```
Step 2: Scrape Each Competition
───────────────────────────────
For each discovered competition ID:

Request: POST StevneResultater.php
         Body: competition=XXXXXX

Extract:
  • Competition metadata:
    - Name (e.g., "NM Friidrett 2023")
    - Venue (e.g., "Bislett Stadion")
    - Organizer (e.g., "Norges Friidrettsforbund")
    - Date range (e.g., "24.08.2023 til 27.08.2023")

  • All results grouped by:
    - Age class (e.g., "Menn Senior")
    - Event (e.g., "100 meter")
    - Individual results with:
      - Placement
      - Result + wind
      - Athlete name + birth year
      - Club

Total requests: ~5,000-10,000
Time estimate: 1-2 hours
```

### Data Quality
- **Competition IDs**: Real, unique identifiers from source system
- **Metadata**: Complete (venue, organizer, date range)
- **Results**: Properly grouped and linked
- **Athletes**: Identified by name + birth year (no source ID yet)

---

## Phase 2: Athlete Scraping (All Years)

### Purpose
1. Get all historical results (especially pre-2011 data not available via competitions)
2. Get athlete source IDs and full birth dates
3. Fill gaps in competition-scraped data

### Process

```
Step 1: Load Athlete List
─────────────────────────
Pre-downloaded HTML files from UtoverSok.php for each letter A-Å
Contains: ~100,000 athletes with source IDs

Distribution:
  A: 5,348    H: 10,915   O: 2,379    V: 2,868
  B: 8,538    I: 861      P: 1,798    W: 2,142
  C: 784      J: 3,316    Q: 52       X: (in W)
  D: 2,342    K: 5,826    R: 4,736    Y: 206
  E: 3,740    L: 5,991    S: 13,426   Z: 219
  F: 4,205    M: 5,513    T: 3,990    Æ: 4
  G: 4,179    N: 4,084    U: 773      Ø: 1,384
                                      Å: 319
```

```
Step 2: Scrape Each Athlete
───────────────────────────
For each athlete:

Request: POST UtoverStatistikk.php
         Body: athlete=XXXXXX&type=RES

Extract:
  • Athlete info:
    - Name
    - Birth date (full: DD.MM.YYYY)

  • All results (outdoor + indoor):
    - Event name
    - Year (age)
    - Result + wind
    - Placement
    - Club
    - Date
    - Venue (from title attribute)
    - Competition name
    - Approved/rejected status
    - Rejection reason if applicable

Total requests: ~100,000
Time estimate: 7-8 hours (single thread)
```

### Competition Handling

For each result found:

```
If year >= 2011:
  └── Try to match to existing competition from Phase 1
      └── Match by: year + venue + competition name pattern
      └── If found: Link to existing competition_id
      └── If not found: Create derived competition

If year < 2011:
  └── Create derived competition
      └── Generate hash from: date + venue + competition_name
      └── Use hash as unique identifier
      └── Set is_derived = 1
```

### Data Quality
- **Athletes**: Full source IDs and birth dates
- **Results**: Complete historical data back to 1960s
- **Competitions**: Derived from text (less accurate metadata)
- **Linking**: Results properly linked to athletes by source_id

---

## Phase 3: Linking & Cleanup

### Purpose
Merge data from both sources for maximum completeness and accuracy.

### Process

```
Step 1: Link Athletes
─────────────────────
Match athletes from competition scrape to athlete scrape:
  • Match by: name + birth_year
  • Update competition-scraped athletes with source_id
  • Propagate birth_date to all matching records

Step 2: Enrich Data
───────────────────
  • Fill in missing birth dates where we have them
  • Categorize events (sprint, throws, jumps, etc.)
  • Set is_timed and higher_is_better flags

Step 3: Verify Integrity
────────────────────────
  • Check for orphaned results
  • Verify all foreign keys
  • Report data quality metrics
```

### Time Estimate
~1 minute (local database operations only)

---

## Running the Scraper

### Prerequisites

```bash
# Required Python packages
pip install requests beautifulsoup4

# Required files
athlete_search_html/search_A.html
athlete_search_html/search_B.html
...
athlete_search_html/search_Å.html
```

### Commands

```bash
# Initialize database
python unified_scraper.py init

# Run Phase 1: Competition scraping (2011+)
python unified_scraper.py phase1

# Run Phase 2: Athlete scraping (all years)
python unified_scraper.py phase2

# Run Phase 2 for specific letters only
python unified_scraper.py phase2 A B C

# Run Phase 3: Linking & cleanup
python unified_scraper.py phase3

# Check progress at any time
python unified_scraper.py status

# Export to CSV for Supabase
python unified_scraper.py export

# Run everything
python unified_scraper.py all
```

### Parallel Execution

To speed up Phase 2, run multiple terminals:

```bash
# Terminal 1
python unified_scraper.py phase2 A B C D E F G

# Terminal 2
python unified_scraper.py phase2 H I J K L M N

# Terminal 3
python unified_scraper.py phase2 O P Q R S T

# Terminal 4
python unified_scraper.py phase2 U V W X Y Z Æ Ø Å
```

**Note:** Phase 1 cannot be parallelized (single discovery + scrape process).

---

## Time Estimates

| Phase | Requests | Single Thread | 4 Parallel |
|-------|----------|---------------|------------|
| Phase 1: Discovery | ~28,000 | ~2 hours | - |
| Phase 1: Scraping | ~5,000-10,000 | ~1-2 hours | - |
| Phase 2: Athletes | ~100,000 | ~7-8 hours | ~2 hours |
| Phase 3: Linking | Local only | ~1 minute | - |
| **Total** | | **~10-12 hours** | **~4-5 hours** |

---

## Output Database

### Final Statistics (Expected)

```
Athletes:      ~100,000
Competitions:  ~15,000-20,000
  - Real:      ~5,000-10,000 (2011+)
  - Derived:   ~10,000+ (pre-2011)
Results:       ~2,000,000+
Events:        ~200
Clubs:         ~1,000+
```

### Data Quality Metrics

| Metric | Expected |
|--------|----------|
| Athletes with source_id | ~100% |
| Athletes with birth_date | ~80-90% |
| Results with competition_id | ~100% |
| Competitions with real source_id | ~30-40% (2011+ only) |
| Results approved | ~95% |

---

## Export to Supabase

```bash
# Generate CSV files
python unified_scraper.py export

# Files created in export/ directory:
#   athletes.csv
#   clubs.csv
#   events.csv
#   age_classes.csv
#   competitions.csv
#   results.csv
```

### Import Order (Supabase)

1. `clubs.csv` (no dependencies)
2. `events.csv` (no dependencies)
3. `age_classes.csv` (no dependencies)
4. `athletes.csv` (no dependencies)
5. `competitions.csv` (no dependencies)
6. `results.csv` (depends on all above)

---

## Troubleshooting

### Scraper Stops Mid-Process
Just run the same command again. Progress is tracked:
- Phase 1: `competition_discovery` table tracks scraped IDs
- Phase 2: `athlete_scrape_progress` table tracks completed letters/indices

### Rate Limiting
If you get blocked:
1. Increase `DELAY_BETWEEN_REQUESTS` in the script (default: 0.25s)
2. Wait an hour before resuming
3. Consider running during off-peak hours (night in Norway)

### Memory Issues
The scraper processes one athlete/competition at a time and commits frequently. Should not have memory issues.

### Duplicate Results
The UNIQUE constraint prevents exact duplicates. If you see fewer results than expected, some were already in the database from the other phase.

---

## Files Reference

| File | Purpose |
|------|---------|
| `unified_scraper.py` | Main scraper script |
| `athletics_unified.db` | SQLite database |
| `unified_scrape.log` | Scraping log |
| `athlete_search_html/` | Pre-downloaded athlete lists |
| `export/` | CSV export directory |

---

## Querying the Data

### Example Queries

```sql
-- Get all results for an athlete
SELECT * FROM results_full
WHERE athlete_name = 'Jakob Ingebrigtsen'
ORDER BY date DESC;

-- Get top 10 all-time 100m results
SELECT athlete_name, result, date, competition_name, venue
FROM results_full
WHERE event_name = '100 meter'
  AND is_outdoor = 1
  AND is_approved = 1
ORDER BY result_numeric ASC
LIMIT 10;

-- Get all results from a specific competition
SELECT athlete_name, event_name, result, placement
FROM results_full
WHERE competition_source_id = 10007768
ORDER BY event_name, placement;

-- Count results by decade
SELECT (year/10)*10 as decade, COUNT(*) as count
FROM results
GROUP BY decade
ORDER BY decade;

-- Find all NM competitions
SELECT * FROM competitions
WHERE name LIKE '%NM%'
ORDER BY year DESC;
```

---

## Contact & Support

For issues with this scraper, check:
1. The log file: `unified_scrape.log`
2. Database status: `python unified_scraper.py status`
3. Source website availability: https://www.minfriidrettsstatistikk.info
