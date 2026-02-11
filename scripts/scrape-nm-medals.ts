/**
 * Scraper for NM-medaljer (Norwegian Championship medals)
 *
 * Scrapes medal data from NIF's official pages and stores in Supabase.
 * Run locally with: npx tsx scripts/scrape-nm-medals.ts
 *
 * Requires env vars:
 *   SUPABASE_URL (or NEXT_PUBLIC_SUPABASE_URL)
 *   SUPABASE_SERVICE_ROLE_KEY
 */

import { createClient } from "@supabase/supabase-js"
import { JSDOM } from "jsdom"

// ── Config ──────────────────────────────────────────────────────────────

const SUPABASE_URL = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL!
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY!

if (!SUPABASE_URL || !SUPABASE_KEY) {
  console.error("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
  process.exit(1)
}

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)

const BASE = "https://epi-new.nif.no/globalassets/aktivitet/statistikk/norske-mesterskap"
const BASE_ALT = "https://epi-new.nif.no/globalassets/aktivitet/statistikk/norskemesterskap"

interface EventDef {
  file: string
  event_name: string
  gender: "M" | "F"
  championship_type: "NM_outdoor" | "NM_indoor"
  base?: string // override base URL for pages with different path
}

// Event name mapping from filename to display name
const EVENTS: EventDef[] = [
  // ── Outdoor Men ──
  { file: "m100.htm", event_name: "100m", gender: "M", championship_type: "NM_outdoor" },
  { file: "m200.htm", event_name: "200m", gender: "M", championship_type: "NM_outdoor" },
  { file: "m400.htm", event_name: "400m", gender: "M", championship_type: "NM_outdoor" },
  { file: "m800.htm", event_name: "800m", gender: "M", championship_type: "NM_outdoor" },
  { file: "m1500.htm", event_name: "1500m", gender: "M", championship_type: "NM_outdoor" },
  { file: "m5000.htm", event_name: "5000m", gender: "M", championship_type: "NM_outdoor" },
  { file: "m10000.htm", event_name: "10 000m", gender: "M", championship_type: "NM_outdoor" },
  { file: "mhalvmar.htm", event_name: "Halvmaraton", gender: "M", championship_type: "NM_outdoor", base: BASE_ALT },
  { file: "mmar.htm", event_name: "Maraton", gender: "M", championship_type: "NM_outdoor" },
  { file: "m110h.htm", event_name: "110m hekk", gender: "M", championship_type: "NM_outdoor" },
  { file: "m400h.htm", event_name: "400m hekk", gender: "M", championship_type: "NM_outdoor" },
  { file: "m3000h.htm", event_name: "3000m hinder", gender: "M", championship_type: "NM_outdoor" },
  { file: "mhj.htm", event_name: "Høyde", gender: "M", championship_type: "NM_outdoor" },
  { file: "mhjut.htm", event_name: "Høyde (utd.)", gender: "M", championship_type: "NM_outdoor" },
  { file: "mpv.htm", event_name: "Stav", gender: "M", championship_type: "NM_outdoor" },
  { file: "mlj.htm", event_name: "Lengde", gender: "M", championship_type: "NM_outdoor" },
  { file: "mljut.htm", event_name: "Lengde (utd.)", gender: "M", championship_type: "NM_outdoor" },
  { file: "mtj.htm", event_name: "Tresteg", gender: "M", championship_type: "NM_outdoor" },
  { file: "msp.htm", event_name: "Kule", gender: "M", championship_type: "NM_outdoor" },
  { file: "mdt.htm", event_name: "Diskos", gender: "M", championship_type: "NM_outdoor" },
  { file: "mht.htm", event_name: "Slegge", gender: "M", championship_type: "NM_outdoor" },
  { file: "mjt.htm", event_name: "Spyd", gender: "M", championship_type: "NM_outdoor" },
  { file: "m3kmt.htm", event_name: "3 km kappgang", gender: "M", championship_type: "NM_outdoor" },
  { file: "m10km.htm", event_name: "10 km kappgang", gender: "M", championship_type: "NM_outdoor" },
  { file: "mdec.htm", event_name: "Tikamp", gender: "M", championship_type: "NM_outdoor" },

  // ── Outdoor Women ──
  { file: "k100.htm", event_name: "100m", gender: "F", championship_type: "NM_outdoor" },
  { file: "k200.htm", event_name: "200m", gender: "F", championship_type: "NM_outdoor" },
  { file: "k400.htm", event_name: "400m", gender: "F", championship_type: "NM_outdoor" },
  { file: "k800.htm", event_name: "800m", gender: "F", championship_type: "NM_outdoor" },
  { file: "k1500.htm", event_name: "1500m", gender: "F", championship_type: "NM_outdoor" },
  { file: "k5000.htm", event_name: "5000m", gender: "F", championship_type: "NM_outdoor" },
  { file: "k10000.htm", event_name: "10 000m", gender: "F", championship_type: "NM_outdoor" },
  { file: "khalvmar.htm", event_name: "Halvmaraton", gender: "F", championship_type: "NM_outdoor", base: BASE_ALT },
  { file: "kmar.htm", event_name: "Maraton", gender: "F", championship_type: "NM_outdoor" },
  { file: "k100h.htm", event_name: "100m hekk", gender: "F", championship_type: "NM_outdoor" },
  { file: "k400h.htm", event_name: "400m hekk", gender: "F", championship_type: "NM_outdoor" },
  { file: "k3000h.htm", event_name: "3000m hinder", gender: "F", championship_type: "NM_outdoor" },
  { file: "khj.htm", event_name: "Høyde", gender: "F", championship_type: "NM_outdoor" },
  { file: "khjut.htm", event_name: "Høyde (utd.)", gender: "F", championship_type: "NM_outdoor" },
  { file: "kpv.htm", event_name: "Stav", gender: "F", championship_type: "NM_outdoor" },
  { file: "klj.htm", event_name: "Lengde", gender: "F", championship_type: "NM_outdoor" },
  { file: "kljut.htm", event_name: "Lengde (utd.)", gender: "F", championship_type: "NM_outdoor" },
  { file: "ktj.htm", event_name: "Tresteg", gender: "F", championship_type: "NM_outdoor" },
  { file: "ksp.htm", event_name: "Kule", gender: "F", championship_type: "NM_outdoor" },
  { file: "kdt.htm", event_name: "Diskos", gender: "F", championship_type: "NM_outdoor" },
  { file: "kht.htm", event_name: "Slegge", gender: "F", championship_type: "NM_outdoor" },
  { file: "kjt.htm", event_name: "Spyd", gender: "F", championship_type: "NM_outdoor" },
  { file: "k2km.htm", event_name: "2 km kappgang", gender: "F", championship_type: "NM_outdoor" },
  { file: "k6km.htm", event_name: "6 km kappgang", gender: "F", championship_type: "NM_outdoor" },
  { file: "khep.htm", event_name: "Sjukamp", gender: "F", championship_type: "NM_outdoor" },

  // ── Indoor Men ──
  { file: "m60i.htm", event_name: "60m", gender: "M", championship_type: "NM_indoor" },
  { file: "m200i.htm", event_name: "200m", gender: "M", championship_type: "NM_indoor" },
  { file: "m400i.htm", event_name: "400m", gender: "M", championship_type: "NM_indoor" },
  { file: "m800i.htm", event_name: "800m", gender: "M", championship_type: "NM_indoor" },
  { file: "m1500i.htm", event_name: "1500m", gender: "M", championship_type: "NM_indoor" },
  { file: "m3000i.htm", event_name: "3000m", gender: "M", championship_type: "NM_indoor" },
  { file: "m60hi.htm", event_name: "60m hekk", gender: "M", championship_type: "NM_indoor" },
  { file: "mhji.htm", event_name: "Høyde", gender: "M", championship_type: "NM_indoor" },
  { file: "mpvi.htm", event_name: "Stav", gender: "M", championship_type: "NM_indoor" },
  { file: "mlji.htm", event_name: "Lengde", gender: "M", championship_type: "NM_indoor" },
  { file: "mtji.htm", event_name: "Tresteg", gender: "M", championship_type: "NM_indoor" },
  { file: "mspi.htm", event_name: "Kule", gender: "M", championship_type: "NM_indoor" },

  // ── Indoor Women ──
  { file: "k60i.htm", event_name: "60m", gender: "F", championship_type: "NM_indoor" },
  { file: "k200i.htm", event_name: "200m", gender: "F", championship_type: "NM_indoor" },
  { file: "k400i.htm", event_name: "400m", gender: "F", championship_type: "NM_indoor" },
  { file: "k800i.htm", event_name: "800m", gender: "F", championship_type: "NM_indoor" },
  { file: "k1500i.htm", event_name: "1500m", gender: "F", championship_type: "NM_indoor" },
  { file: "k3000i.htm", event_name: "3000m", gender: "F", championship_type: "NM_indoor" },
  { file: "k60hi.htm", event_name: "60m hekk", gender: "F", championship_type: "NM_indoor" },
  { file: "khji.htm", event_name: "Høyde", gender: "F", championship_type: "NM_indoor" },
  { file: "kpvi.htm", event_name: "Stav", gender: "F", championship_type: "NM_indoor" },
  { file: "klji.htm", event_name: "Lengde", gender: "F", championship_type: "NM_indoor" },
  { file: "ktji.htm", event_name: "Tresteg", gender: "F", championship_type: "NM_indoor" },
  { file: "kspi.htm", event_name: "Kule", gender: "F", championship_type: "NM_indoor" },
]

interface MedalRecord {
  athlete_name: string
  club_name: string | null
  year: number
  event_name: string
  championship_type: "NM_outdoor" | "NM_indoor"
  gender: "M" | "F"
  medal: "gold" | "silver" | "bronze"
  performance: string | null
  source_url: string
}

// ── Parsing ─────────────────────────────────────────────────────────────

/** Texts that mean "no medal awarded" */
const SKIP_PATTERNS = [
  /intet\s+mesterskap/i,
  /avlyst/i,
  /ikke\s+arrangert/i,
  /kun\s+\d+\s+deltok/i,
  /utgikk/i,
  /ingen\s+deltakere/i,
  /^-+$/,
  /^\s*$/,
]

function shouldSkip(text: string): boolean {
  return SKIP_PATTERNS.some((p) => p.test(text.trim()))
}

/**
 * Parse "Name, Club" from a cell. Handles common formats:
 * - "Sondre Guttormsen, Vidar"
 * - "Sondre Guttormsen, Ski IL"
 * - "Sondre Guttormsen"  (no club)
 */
function parseNameClub(text: string): { name: string; club: string | null } {
  const trimmed = text.trim()
  if (!trimmed || shouldSkip(trimmed)) return { name: "", club: null }

  // Find the last comma which separates name from club
  const lastComma = trimmed.lastIndexOf(",")
  if (lastComma === -1) {
    return { name: trimmed, club: null }
  }

  const name = trimmed.substring(0, lastComma).trim()
  const club = trimmed.substring(lastComma + 1).trim()
  return { name, club: club || null }
}

async function fetchPage(url: string): Promise<string> {
  const res = await fetch(url)
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`)
  const buffer = await res.arrayBuffer()
  // Pages are windows-1252 encoded
  const decoder = new TextDecoder("windows-1252")
  return decoder.decode(buffer)
}

function parseMedalsFromHtml(
  html: string,
  eventDef: EventDef,
  sourceUrl: string
): MedalRecord[] {
  const dom = new JSDOM(html)
  const doc = dom.window.document
  // Only parse the first table (some pages like khep.htm have many sub-event tables)
  const firstTable = doc.querySelector("table")
  if (!firstTable) return []
  const rows = firstTable.querySelectorAll("tr")
  const medals: MedalRecord[] = []

  let currentYear = 0

  for (const row of rows) {
    const cells = row.querySelectorAll("td")
    if (cells.length < 3) continue

    // Extract text content from all cells
    const cellTexts: string[] = []
    for (const cell of cells) {
      cellTexts.push((cell.textContent || "").replace(/\s+/g, " ").trim())
    }

    // Determine structure: 7 columns (year, gold name, gold perf, silver name, silver perf, bronze name, bronze perf)
    // or sometimes fewer columns (header row, continuation rows)

    // Check if first cell looks like a year
    const yearMatch = cellTexts[0]?.match(/^(\d{4})$/)
    if (yearMatch) {
      currentYear = parseInt(yearMatch[1])
    } else if (!cellTexts[0]?.trim() && currentYear > 0) {
      // Continuation row (e.g. multiple bronze medalists) - keep currentYear
    } else {
      // Header or unrecognized row, skip
      continue
    }

    if (currentYear === 0) continue

    // Parse medal columns depending on available cells
    // Standard layout: [year, goldName, goldPerf, silverName, silverPerf, bronzeName, bronzePerf]
    // Sometimes: [year, goldName, goldPerf, silverName, silverPerf, -, -] (no bronze)
    // Continuation: ["", "", "", "", "", bronzeName, bronzePerf]

    const medalSlots: { medal: "gold" | "silver" | "bronze"; nameIdx: number; perfIdx: number }[] = []

    if (cellTexts.length >= 7) {
      medalSlots.push({ medal: "gold", nameIdx: 1, perfIdx: 2 })
      medalSlots.push({ medal: "silver", nameIdx: 3, perfIdx: 4 })
      medalSlots.push({ medal: "bronze", nameIdx: 5, perfIdx: 6 })
    } else if (cellTexts.length >= 5) {
      medalSlots.push({ medal: "gold", nameIdx: 1, perfIdx: 2 })
      medalSlots.push({ medal: "silver", nameIdx: 3, perfIdx: 4 })
    } else if (cellTexts.length >= 3) {
      medalSlots.push({ medal: "gold", nameIdx: 1, perfIdx: 2 })
    }

    for (const slot of medalSlots) {
      const nameText = cellTexts[slot.nameIdx] || ""
      const perfText = cellTexts[slot.perfIdx] || ""

      if (!nameText.trim() || shouldSkip(nameText)) continue

      // Handle multiple athletes in one cell (tied results)
      // e.g. "Odd Eiken, Ranheim Fredrik Weiseth, Ranheim" with "4.40 4.40"
      // This is tricky. Try to detect by checking if there are multiple performances
      const performances = perfText.trim().split(/\s+/)

      // Simple case: single athlete
      const { name, club } = parseNameClub(nameText)
      if (!name) continue

      medals.push({
        athlete_name: name,
        club_name: club,
        year: currentYear,
        event_name: eventDef.event_name,
        championship_type: eventDef.championship_type,
        gender: eventDef.gender,
        medal: slot.medal,
        performance: perfText.trim() || null,
        source_url: sourceUrl,
      })
    }
  }

  return medals
}

// ── Name matching ───────────────────────────────────────────────────────

function normalizeName(name: string): string {
  return name
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "") // remove diacritics
    .replace(/[.\-]/g, " ")
    .replace(/\s+/g, " ")
    .trim()
}

interface AthleteRow {
  id: string
  full_name: string | null
  first_name: string
  last_name: string
  gender: string | null
}

async function loadAthletes(): Promise<AthleteRow[]> {
  const allAthletes: AthleteRow[] = []
  let offset = 0
  const pageSize = 1000

  while (true) {
    const { data, error } = await supabase
      .from("athletes")
      .select("id, full_name, first_name, last_name, gender")
      .range(offset, offset + pageSize - 1)

    if (error) throw error
    if (!data || data.length === 0) break

    allAthletes.push(...data)
    offset += pageSize
    if (data.length < pageSize) break
  }

  return allAthletes
}

function matchAthletes(
  medals: MedalRecord[],
  athletes: AthleteRow[]
): { matched: (MedalRecord & { athlete_id: string })[]; unmatched: MedalRecord[] } {
  // Build lookup maps
  const exactMap = new Map<string, AthleteRow[]>()
  const normalizedMap = new Map<string, AthleteRow[]>()

  for (const a of athletes) {
    const fullName = a.full_name || `${a.first_name} ${a.last_name}`
    const key = `${fullName.toLowerCase()}|${a.gender || ""}`
    if (!exactMap.has(key)) exactMap.set(key, [])
    exactMap.get(key)!.push(a)

    const normKey = `${normalizeName(fullName)}|${a.gender || ""}`
    if (!normalizedMap.has(normKey)) normalizedMap.set(normKey, [])
    normalizedMap.get(normKey)!.push(a)
  }

  const matched: (MedalRecord & { athlete_id: string })[] = []
  const unmatched: MedalRecord[] = []

  for (const medal of medals) {
    const exactKey = `${medal.athlete_name.toLowerCase()}|${medal.gender}`
    const exactMatch = exactMap.get(exactKey)

    if (exactMatch && exactMatch.length === 1) {
      matched.push({ ...medal, athlete_id: exactMatch[0].id })
      continue
    }

    // Try normalized match
    const normKey = `${normalizeName(medal.athlete_name)}|${medal.gender}`
    const normMatch = normalizedMap.get(normKey)

    if (normMatch && normMatch.length === 1) {
      matched.push({ ...medal, athlete_id: normMatch[0].id })
      continue
    }

    unmatched.push(medal)
  }

  return { matched, unmatched }
}

// ── Main ────────────────────────────────────────────────────────────────

async function main() {
  console.log("=== NM Medal Scraper ===\n")

  // 1. Scrape all pages
  const allMedals: MedalRecord[] = []
  let errorCount = 0

  for (const eventDef of EVENTS) {
    const base = eventDef.base || BASE
    const url = `${base}/${eventDef.file}`
    process.stdout.write(`Scraping ${eventDef.file} (${eventDef.event_name} ${eventDef.gender})... `)

    try {
      const html = await fetchPage(url)
      const medals = parseMedalsFromHtml(html, eventDef, url)
      allMedals.push(...medals)
      console.log(`${medals.length} medals`)
    } catch (err) {
      errorCount++
      console.log(`ERROR: ${err}`)
    }

    // Small delay to be nice to the server
    await new Promise((r) => setTimeout(r, 200))
  }

  console.log(`\nScraped ${allMedals.length} medals from ${EVENTS.length} pages (${errorCount} errors)\n`)

  // 2. Load athletes and match
  console.log("Loading athletes from database...")
  const athletes = await loadAthletes()
  console.log(`Loaded ${athletes.length} athletes`)

  console.log("Matching names...")
  const { matched, unmatched } = matchAthletes(allMedals, athletes)
  console.log(`Matched: ${matched.length} / ${allMedals.length} (${((matched.length / allMedals.length) * 100).toFixed(1)}%)`)
  console.log(`Unmatched: ${unmatched.length}\n`)

  // 3. Insert into database
  console.log("Clearing existing data...")
  const { error: deleteError } = await supabase.from("championship_medals").delete().neq("id", "00000000-0000-0000-0000-000000000000")
  if (deleteError) {
    console.error("Delete error:", deleteError)
    process.exit(1)
  }

  console.log("Inserting matched medals...")
  const matchedRows = matched.map((m) => ({
    athlete_id: m.athlete_id,
    athlete_name: m.athlete_name,
    club_name: m.club_name,
    year: m.year,
    event_name: m.event_name,
    championship_type: m.championship_type,
    gender: m.gender,
    medal: m.medal,
    performance: m.performance,
    source_url: m.source_url,
  }))

  const unmatchedRows = unmatched.map((m) => ({
    athlete_id: null,
    athlete_name: m.athlete_name,
    club_name: m.club_name,
    year: m.year,
    event_name: m.event_name,
    championship_type: m.championship_type,
    gender: m.gender,
    medal: m.medal,
    performance: m.performance,
    source_url: m.source_url,
  }))

  const allRows = [...matchedRows, ...unmatchedRows]

  // Insert in batches of 500
  const batchSize = 500
  for (let i = 0; i < allRows.length; i += batchSize) {
    const batch = allRows.slice(i, i + batchSize)
    const { error } = await supabase.from("championship_medals").insert(batch)
    if (error) {
      console.error(`Insert error at batch ${i / batchSize}:`, error)
      process.exit(1)
    }
    process.stdout.write(`  Inserted ${Math.min(i + batchSize, allRows.length)} / ${allRows.length}\r`)
  }
  console.log(`\nInserted ${allRows.length} medals total.`)

  // 4. Print sample unmatched for review
  if (unmatched.length > 0) {
    console.log("\n--- Sample unmatched medals (last 20 years) ---")
    const recentUnmatched = unmatched
      .filter((m) => m.year >= 2005)
      .slice(0, 30)
    for (const m of recentUnmatched) {
      console.log(`  ${m.year} ${m.championship_type} ${m.event_name}: ${m.athlete_name} (${m.club_name}) - ${m.medal}`)
    }
  }

  console.log("\nDone!")
}

main().catch(console.error)
