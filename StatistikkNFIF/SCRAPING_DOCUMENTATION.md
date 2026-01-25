# Norwegian Athletics Statistics Scraping Documentation

## Project Overview

Scraping the complete historical database from [minfriidrettsstatistikk.info](https://www.minfriidrettsstatistikk.info) - the official statistics system for Norges Friidrettsforbund (Norwegian Athletic Federation).

**Goal:** Extract ALL competition results for ALL athletes to build a new statistics system using Supabase.

---

## Website Structure

### Base URL
```
https://www.minfriidrettsstatistikk.info/php/
```

### Key Pages

| Page | Purpose |
|------|---------|
| `LandsStatistikk.php` | National statistics/rankings by event and class |
| `UtoverStatistikk.php` | Individual athlete profiles and results |
| `UtoverSok.php` | Athlete search (alphabetical A-Å) |

---

## Athlete Results Endpoint

### How to Get ALL Results for an Athlete

**Method:** POST
**URL:** `https://www.minfriidrettsstatistikk.info/php/UtoverStatistikk.php`
**Content-Type:** `application/x-www-form-urlencoded`

**Form Data:**
```
athlete=[ATHLETE_ID]&type=RES
```

### Available View Types

| type | View |
|------|------|
| `PR` | Personal Records (best per event) |
| `SB` | Season Bests |
| `PRG` | Progression |
| `RES` | **ALL Results** ← This is what we need |

### Athlete ID Discovery

**Method:** POST to `UtoverSok.php` with `cmd=SearchAthlete&showchar=[LETTER]`

This returns all athletes whose last name starts with that letter.

**Results from scanning all letters A-Å:**
- **Total unique athlete IDs: 99,938**
- ID range: 1 to 10,033,254 (sparse, many gaps)
- All IDs saved to: `athlete_search_html/_all_athlete_ids.json`

**Athletes per letter:**
| Letter | Count | Letter | Count |
|--------|-------|--------|-------|
| A | 5,348 | O | 2,379 |
| B | 8,538 | P | 1,798 |
| C | 784 | Q | 52 |
| D | 2,342 | R | 4,736 |
| E | 3,740 | S | 13,426 |
| F | 4,205 | T | 3,990 |
| G | 4,179 | U | 773 |
| H | 10,915 | V | 2,868 |
| I | 861 | W | 2,142 |
| J | 3,316 | Y | 206 |
| K | 5,826 | Z | 219 |
| L | 5,991 | Æ | 4 |
| M | 5,513 | Ø | 1,384 |
| N | 4,084 | Å | 319 |

---

## HTML Response Structure

### Athlete Header
```html
<div id="athlete">
  <h2>Simen Guttormsen</h2>
  <h3>Født: 19.01.2001</h3>
</div>
```

### Section Headers
```html
<div id="header2"><h2>UTENDØRS</h2></div>  <!-- Outdoor -->
<div id="header2"><h2>INNENDØRS</h2></div> <!-- Indoor -->
```

### Event Headers
```html
<div id="eventheader"><h3>60 meter</h3></div>
<div id="eventheader"><h3>Høyde</h3></div>
```

### Results Table Structure
```html
<table>
  <tr>
    <th>ÅR</th>        <!-- Year (age) -->
    <th>RESULTAT</th>  <!-- Result -->
    <th>PLASSERING</th><!-- Placement -->
    <th>KLUBB</th>     <!-- Club -->
    <th>DATO</th>      <!-- Date -->
    <th>STED</th>      <!-- Location -->
  </tr>
  <tr>
    <td>2015 (14)</td>
    <td>9,17(+0,9)</td>
    <td>2</td>
    <td>Ski IL Friidrett</td>
    <td>28.08.15</td>
    <td title="Sportsplassen Bækkelaget">Bækkelaget, Mangekampstevne 2015</td>
  </tr>
</table>
```

### Disqualified Results
Has an additional column:
```html
<div><h4>Ikke godkjente resultater</h4></div>
<table>
  <!-- Same columns + -->
  <th>ÅRSAK</th>  <!-- Reason for disqualification -->
</table>
```

**Rejection reasons found:**
- `For mye vind/Assisting wind` - Excessive tailwind
- `Manglende informasjon om vind` - Missing wind information
- `Ikke godkjent` - Not approved (generic)
- `Feil på tider som følge av feilkoplet startutstyr` - Timing error due to incorrectly connected starting equipment
- `I konkurranse med seniorer` - In competition with seniors (age class note)

### Placement Format Variations

| Format | Meaning |
|--------|---------|
| `1`, `2`, `3` | Simple placement |
| `2-h1`, `4-h2` | Heat placement (heat number) |
| `1-fi `, `4-fi ` | Final (note trailing space) |
| `6-fi-B`, `8-fi-B` | B final |
| `9-fi-C` | C final |
| `6-grpA `, `7-grpB ` | Group placement |
| `8-kvB `, `9-kv ` | Qualifier |
| `D`, `D-h1` | Decathlon |
| `H` | Heptathlon |
| `M` | Mangekamp (combined event) |

---

## Result Format Variations

### Running Events (time-based, lower is better)

| Event Type | Format Examples | Notes |
|------------|-----------------|-------|
| Sprints (60m-400m) | `9,17(+0,9)`, `9,86(-0,4)` | Seconds with wind in parentheses |
| Middle distance | `1,45,04`, `1,01,6` | Minutes,seconds,hundredths (comma separated!) |
| Long distance | `5,00,24`, `6,10,81` | Minutes,seconds,hundredths |
| Very long | `28,06,36` | Likely same format |

**Important:** Time format uses COMMAS as separators: `minutes,seconds,hundredths`
- Sometimes only 1 decimal: `1,01,6` (1:01.6)
- Sometimes 2 decimals: `1,45,04` (1:45.04)

### Field Events - Jumps (distance/height, higher is better)

| Event | Format Examples | Notes |
|-------|-----------------|-------|
| High jump | `1,80`, `2,15` | Meters with comma decimal |
| Pole vault | `5,80`, `5,94` | Meters |
| Long jump | `6,78(+1,4)`, `8,27(+1,4)` | Meters with wind |
| Triple jump | `14,85(+0,8)` | Meters with wind |

**Wind format inconsistency:** Usually comma (`+1,4`) but sometimes period (`+2.5`)!

### Field Events - Throws (distance, higher is better)

| Event | Format Examples |
|-------|-----------------|
| Shot put | `8,65`, `12,45` |
| Discus | `40,56`, `55,32` |
| Javelin | `47,10`, `72,15` |
| Hammer | `48,40`, `65,20` |

### Combined Events (points, higher is better)

| Event | Format Examples |
|-------|-----------------|
| Decathlon | `6826`, `8500` |
| Heptathlon | `4016`, `6200` |
| Other | `4663`, `4760` |

**Note:** Combined event points are integers with no decimals.

### Special Result Values

| Value | Meaning |
|-------|---------|
| `(-)` | No wind reading / Not applicable |

---

## Data Fields to Extract

### Per Athlete
- `id` - Source system athlete ID (from URL)
- `name` - Full name
- `birth_date` - Date of birth

### Per Result
- `athlete_id` - Foreign key to athlete
- `event_name` - Event name (e.g., "60 meter", "Høyde")
- `result` - Raw result string
- `wind` - Wind reading (if applicable)
- `year` - Competition year
- `age` - Athlete's age at competition
- `placement` - Placement (may include heat info like "2-h1")
- `club` - Club name at time of competition
- `date` - Competition date
- `venue` - Venue name (from `title` attribute)
- `competition_name` - Competition name
- `is_outdoor` - Boolean (UTENDØRS vs INNENDØRS)
- `is_approved` - Boolean (valid vs "Ikke godkjente")
- `rejection_reason` - If not approved

---

## Scraping Strategy

### Approach: Iterate Athlete IDs

1. Loop through athlete IDs from 1 to ~65,000
2. For each ID, POST to `UtoverStatistikk.php` with `athlete=[ID]&type=RES`
3. Parse the HTML response
4. Extract athlete info and all results
5. Store in Supabase

### Rate Limiting Considerations

- Be respectful to the server
- Suggested delay: 0.5-1 second between requests
- Consider running during off-peak hours
- Estimated time: ~65,000 requests × 1 sec = ~18 hours

### Handling Edge Cases

- Empty/invalid athlete IDs → Skip (page will be mostly empty)
- Athletes with no results → Store athlete, skip results
- Malformed data → Log and continue

---

## Alternative Scraping Approaches (Not Used)

### Alphabetical Search (A-Å)
URL: `https://www.minfriidrettsstatistikk.info/php/UtoverSok.php`

- Uses JavaScript to load results dynamically
- URL doesn't change when clicking letters
- Would require Selenium/Playwright
- **Rejected:** More complex than ID iteration

### Statistics Pages
URL: `https://www.minfriidrettsstatistikk.info/php/LandsStatistikk.php`

Parameters discovered:
- `showclass` - Age/gender category (1=Gutter 13, 11=Menn Senior, etc.)
- `showevent` - Event ID (2=60m, 4=100m, 68=Høyde, 70=Stav, etc.)
- `showseason` - Year filter
- `outdoor` - Y/N for outdoor/indoor

**Rejected:** Only shows top results per event, not complete history.

---

## Technical Notes

### Character Encoding
- UTF-8 throughout
- Norwegian characters: Æ, Ø, Å (and lowercase æ, ø, å)
- Decimal separator: comma (,) not period (.)

### Date Formats
- Birth date: `DD.MM.YYYY` (e.g., "19.01.2001")
- Competition date: `DD.MM.YY` (e.g., "28.08.15")

### Wind Reading Format
- In parentheses after result: `(+0,9)` or `(-1,5)`
- Positive = tailwind (assistance)
- Negative = headwind

---

## Next Steps

1. [ ] Design final Supabase schema
2. [ ] Build Python scraper with BeautifulSoup
3. [ ] Test on sample of ~100 athletes
4. [ ] Run full scrape with progress tracking
5. [ ] Import data to Supabase
6. [ ] Build data validation/cleanup scripts
