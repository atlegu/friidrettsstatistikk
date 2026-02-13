// Championship qualification configuration
// Based on "Reglement for norske mesterskap 2026"

// --- Types ---

export interface QualificationStandard {
  id: string                    // URL slug: "100m", "hoyde"
  displayName: string           // "100 m", "Høyde"
  category: string              // "sprint", "middle", "long", etc.
  eventCodes: {
    M: string[]
    F: string[]
    U20_M?: string[]            // Override for U20 men (different implements/heights)
  }
  resultType: 'time' | 'distance' | 'height'
  standard: {
    M?: number; F?: number
    U23_M?: number; U20_M?: number; U23_F?: number; U20_F?: number
  }
  indoorCounts?: boolean        // Indoor results count (running/walk events)
  notInChampionship?: boolean   // Not in championship program, but qualifies for participation
  qualifiesForEvent?: string    // ID of event this qualifies for
}

export interface AgeClass {
  id: string
  label: string
  minBirthYear: number
}

export interface Championship {
  id: string
  name: string
  shortName: string
  year: number
  type: 'senior' | 'junior'
  indoor?: boolean
  date: string
  venue?: string
  qualificationStart: string
  qualificationEnd: string
  ageClasses?: AgeClass[]
  standards: QualificationStandard[]
}

// --- Category display ---

export const EVENT_CATEGORY_LABELS: Record<string, string> = {
  sprint: 'Sprint',
  middle: 'Mellomdistanse',
  long: 'Langdistanse',
  hurdles: 'Hekk',
  steeplechase: 'Hinder',
  walk: 'Gange',
  jumps: 'Hopp',
  throws: 'Kast',
}

export const EVENT_CATEGORY_ORDER = [
  'sprint', 'middle', 'long', 'hurdles', 'steeplechase', 'walk', 'jumps', 'throws',
]

// --- Helper functions ---

export function getStandardValue(
  standard: QualificationStandard,
  gender: 'M' | 'F',
  ageClassId?: string
): number | undefined {
  if (ageClassId) {
    const key = `${ageClassId}_${gender}` as keyof typeof standard.standard
    if (standard.standard[key] !== undefined) return standard.standard[key]
  }
  return standard.standard[gender]
}

export function getEventCodes(
  standard: QualificationStandard,
  gender: 'M' | 'F',
  ageClassId?: string
): string[] {
  if (ageClassId === 'U20' && gender === 'M' && standard.eventCodes.U20_M) {
    return standard.eventCodes.U20_M
  }
  return standard.eventCodes[gender]
}

export function formatStandardDisplay(
  value: number,
  resultType: 'time' | 'distance' | 'height'
): string {
  if (resultType === 'time') {
    const totalSeconds = value / 100
    // 400m-class events (under ~90s) display in seconds, 800m+ in MM:SS
    if (totalSeconds < 90) {
      return totalSeconds.toFixed(2).replace('.', ',')
    }
    const minutes = Math.floor(totalSeconds / 60)
    const seconds = totalSeconds % 60
    // Drop decimals when they're .00 (e.g. road race standards like 14:45)
    if (seconds === Math.floor(seconds)) {
      return `${minutes}:${seconds.toFixed(0).padStart(2, '0')}`
    }
    const secStr = seconds.toFixed(2).padStart(5, '0').replace('.', ',')
    return `${minutes}:${secStr}`
  }
  // distance or height in mm
  return (value / 1000).toFixed(2).replace('.', ',')
}

export function getDisplayStandard(
  standard: QualificationStandard,
  gender: 'M' | 'F',
  ageClassId?: string
): string | undefined {
  const value = getStandardValue(standard, gender, ageClassId)
  if (value === undefined) return undefined
  return formatStandardDisplay(value, standard.resultType)
}

export function getChampionship(id: string): Championship | undefined {
  return CHAMPIONSHIPS.find(c => c.id === id)
}

export function getActiveChampionships(): Championship[] {
  return CHAMPIONSHIPS
}

// --- Wind and manual time helpers ---

const WIND_AFFECTED_CODES = new Set([
  '100m', '200m', 'lengde', 'tresteg',
])
const WIND_AFFECTED_PREFIXES = ['100mh', '110mh']

export function isWindAffected(eventCode: string): boolean {
  if (WIND_AFFECTED_CODES.has(eventCode)) return true
  return WIND_AFFECTED_PREFIXES.some(p => eventCode.startsWith(p))
}

const MANUAL_TIME_SPRINT = new Set(['60m', '100m', '200m', '400m'])
const MANUAL_TIME_HURDLE_PREFIXES = ['60mh', '100mh', '110mh', '400mh']

export function shouldFilterManualTimes(eventCodes: string[]): boolean {
  return eventCodes.some(code =>
    MANUAL_TIME_SPRINT.has(code) ||
    MANUAL_TIME_HURDLE_PREFIXES.some(p => code.startsWith(p))
  )
}

// --- NM Senior 2026 ---
// Vedlegg A – Hovedmesterskapet
// Date: Torsdag 23.07 – Lørdag 25.07.2026
// Qualification period: 01.01.2025 – påmeldingsfristen
// Rules: Running events indoor+outdoor count. Technical events outdoor only.
//        Running qualifies for running only, technical for technical only.

const NM_SENIOR_2026: Championship = {
  id: 'nm-senior-2026',
  name: 'NM Senior 2026',
  shortName: 'NM Senior',
  year: 2026,
  type: 'senior',
  date: '23.–25. juli 2026',
  qualificationStart: '2025-01-01',
  qualificationEnd: '2026-07-09',
  standards: [
    // Sprint
    {
      id: '100m', displayName: '100 m', category: 'sprint',
      eventCodes: { M: ['100m'], F: ['100m'] },
      resultType: 'time', indoorCounts: true,
      standard: { M: 1130, F: 1280 },
    },
    {
      id: '200m', displayName: '200 m', category: 'sprint',
      eventCodes: { M: ['200m'], F: ['200m'] },
      resultType: 'time', indoorCounts: true,
      standard: { M: 2280, F: 2620 },
    },
    {
      id: '400m', displayName: '400 m', category: 'sprint',
      eventCodes: { M: ['400m'], F: ['400m'] },
      resultType: 'time', indoorCounts: true,
      standard: { M: 4999, F: 5899 },
    },
    // Mellomdistanse
    {
      id: '800m', displayName: '800 m', category: 'middle',
      eventCodes: { M: ['800m'], F: ['800m'] },
      resultType: 'time', indoorCounts: true,
      standard: { M: 11699, F: 13499 },
    },
    {
      id: '1500m', displayName: '1500 m', category: 'middle',
      eventCodes: { M: ['1500m'], F: ['1500m'] },
      resultType: 'time', indoorCounts: true,
      standard: { M: 23999, F: 28499 },
    },
    {
      id: '3000m', displayName: '3000 m', category: 'middle',
      eventCodes: { M: ['3000m'], F: ['3000m'] },
      resultType: 'time', indoorCounts: true,
      standard: { M: 51499, F: 61499 },
      notInChampionship: true,
    },
    // Langdistanse
    {
      id: '5000m', displayName: '5000 m', category: 'long',
      eventCodes: { M: ['5000m'], F: ['5000m'] },
      resultType: 'time', indoorCounts: true,
      standard: { M: 89999, F: 107999 },
    },
    {
      id: '10000m', displayName: '10 000 m', category: 'long',
      eventCodes: { M: ['10000m'], F: ['10000m'] },
      resultType: 'time', indoorCounts: true,
      standard: { M: 191999, F: 224999 },
    },
    {
      id: '5km-gate', displayName: '5 km gate', category: 'long',
      eventCodes: { M: ['5kmvei'], F: ['5kmvei'] },
      resultType: 'time',
      standard: { M: 88500, F: 105000 },
      notInChampionship: true, qualifiesForEvent: '5000m',
    },
    {
      id: '10km-gate', displayName: '10 km gate', category: 'long',
      eventCodes: { M: ['10kmvei'], F: ['10kmvei'] },
      resultType: 'time',
      standard: { M: 188900, F: 221900 },
      notInChampionship: true, qualifiesForEvent: '10000m',
    },
    // Hekk
    {
      id: '110mh', displayName: '110 m hekk', category: 'hurdles',
      eventCodes: { M: ['110mh_106_7cm'], F: [] },
      resultType: 'time', indoorCounts: true,
      standard: { M: 1599 },
    },
    {
      id: '100mh', displayName: '100 m hekk', category: 'hurdles',
      eventCodes: { M: [], F: ['100mh_84cm'] },
      resultType: 'time', indoorCounts: true,
      standard: { F: 1549 },
    },
    {
      id: '400mh', displayName: '400 m hekk', category: 'hurdles',
      eventCodes: { M: ['400mh_91_4cm'], F: ['400mh_76_2cm'] },
      resultType: 'time', indoorCounts: true,
      standard: { M: 5799, F: 6699 },
    },
    // Hinder
    {
      id: '3000mh', displayName: '3000 m hinder', category: 'steeplechase',
      eventCodes: { M: ['3000mhinder_91_4cm'], F: ['3000mhinder_76_2cm'] },
      resultType: 'time', indoorCounts: true,
      standard: { M: 56999, F: 71999 },
    },
    // Gange
    {
      id: '5000mg', displayName: '5000 m kappgang', category: 'walk',
      eventCodes: { M: ['5000mg'], F: ['5000mg'] },
      resultType: 'time', indoorCounts: true,
      standard: { M: 151499, F: 172499 },
    },
    // Hopp
    {
      id: 'hoyde', displayName: 'Høyde', category: 'jumps',
      eventCodes: { M: ['hoyde'], F: ['hoyde'] },
      resultType: 'height',
      standard: { M: 1900, F: 1650 },
    },
    {
      id: 'stav', displayName: 'Stav', category: 'jumps',
      eventCodes: { M: ['stav'], F: ['stav'] },
      resultType: 'height',
      standard: { M: 4200, F: 3200 },
    },
    {
      id: 'lengde', displayName: 'Lengde', category: 'jumps',
      eventCodes: { M: ['lengde'], F: ['lengde'] },
      resultType: 'distance',
      standard: { M: 6600, F: 5350 },
    },
    {
      id: 'tresteg', displayName: 'Tresteg', category: 'jumps',
      eventCodes: { M: ['tresteg'], F: ['tresteg'] },
      resultType: 'distance',
      standard: { M: 13750, F: 11250 },
    },
    // Kast
    {
      id: 'kule', displayName: 'Kule', category: 'throws',
      eventCodes: { M: ['kule_7_26kg'], F: ['kule_4kg'] },
      resultType: 'distance',
      standard: { M: 14000, F: 11250 },
    },
    {
      id: 'diskos', displayName: 'Diskos', category: 'throws',
      eventCodes: { M: ['diskos_2kg'], F: ['diskos_1kg'] },
      resultType: 'distance',
      standard: { M: 44000, F: 36000 },
    },
    {
      id: 'slegge', displayName: 'Slegge', category: 'throws',
      eventCodes: { M: ['slegge_726kg/1215cm'], F: ['slegge_40kg/1195cm'] },
      resultType: 'distance',
      standard: { M: 50000, F: 42000 },
    },
    {
      id: 'spyd', displayName: 'Spyd', category: 'throws',
      eventCodes: { M: ['spyd_800g'], F: ['spyd_600g'] },
      resultType: 'distance',
      standard: { M: 58000, F: 40000 },
    },
  ],
}

// --- NM Junior 2026 ---
// Vedlegg C – Juniormesterskapet
// Qualification period: 01.01.2025 – påmeldingsfristen
// Classes: U20 (born 2007+), U23 (born 2004+)
// Qualified in one event = can participate in all events
// Indoor and outdoor results both count
// U20 men use international implement/hurdle specifications

const NM_JUNIOR_2026: Championship = {
  id: 'nm-junior-2026',
  name: 'NM Junior 2026',
  shortName: 'NM Junior',
  year: 2026,
  type: 'junior',
  date: '2026',
  qualificationStart: '2025-01-01',
  qualificationEnd: '2026-08-01',
  ageClasses: [
    { id: 'U23', label: 'U23 (f. 2004+)', minBirthYear: 2004 },
    { id: 'U20', label: 'U20 (f. 2007+)', minBirthYear: 2007 },
  ],
  standards: [
    // Sprint
    {
      id: '100m', displayName: '100 m', category: 'sprint',
      eventCodes: { M: ['100m'], F: ['100m'] },
      resultType: 'time', indoorCounts: true,
      standard: { U23_M: 1159, U20_M: 1175, U23_F: 1299, U20_F: 1320 },
    },
    {
      id: '200m', displayName: '200 m', category: 'sprint',
      eventCodes: { M: ['200m'], F: ['200m'] },
      resultType: 'time', indoorCounts: true,
      standard: { U23_M: 2330, U20_M: 2375, U23_F: 2680, U20_F: 2710 },
    },
    {
      id: '400m', displayName: '400 m', category: 'sprint',
      eventCodes: { M: ['400m'], F: ['400m'] },
      resultType: 'time', indoorCounts: true,
      standard: { U23_M: 5150, U20_M: 5280, U23_F: 6099, U20_F: 6199 },
    },
    // Mellomdistanse
    {
      id: '800m', displayName: '800 m', category: 'middle',
      eventCodes: { M: ['800m'], F: ['800m'] },
      resultType: 'time', indoorCounts: true,
      standard: { U23_M: 11849, U20_M: 12049, U23_F: 14199, U20_F: 14499 },
    },
    {
      id: '1500m', displayName: '1500 m', category: 'middle',
      eventCodes: { M: ['1500m'], F: ['1500m'] },
      resultType: 'time', indoorCounts: true,
      standard: { U23_M: 24799, U20_M: 25499, U23_F: 30499, U20_F: 30499 },
    },
    {
      id: '3000m', displayName: '3000 m', category: 'middle',
      eventCodes: { M: [], F: ['3000m'] },
      resultType: 'time', indoorCounts: true,
      standard: { U23_F: 65999, U20_F: 66999 },
    },
    // Langdistanse (men only in junior)
    {
      id: '5000m', displayName: '5000 m', category: 'long',
      eventCodes: { M: ['5000m'], F: [] },
      resultType: 'time', indoorCounts: true,
      standard: { U23_M: 96999, U20_M: 98999 },
    },
    // Hekk
    {
      id: '110mh', displayName: '110 m hekk', category: 'hurdles',
      eventCodes: { M: ['110mh_106_7cm'], F: [], U20_M: ['110mh_100cm'] },
      resultType: 'time', indoorCounts: true,
      standard: { U23_M: 1699, U20_M: 1799 },
    },
    {
      id: '100mh', displayName: '100 m hekk', category: 'hurdles',
      eventCodes: { M: [], F: ['100mh_84cm'] },
      resultType: 'time', indoorCounts: true,
      standard: { U23_F: 1649, U20_F: 1649 },
    },
    {
      id: '400mh', displayName: '400 m hekk', category: 'hurdles',
      eventCodes: { M: ['400mh_91_4cm'], F: ['400mh_76_2cm'], U20_M: ['400mh_84cm'] },
      resultType: 'time', indoorCounts: true,
      standard: { U23_M: 5999, U20_M: 6199, U23_F: 6899, U20_F: 6999 },
    },
    // Hinder
    {
      id: '3000mh', displayName: '3000 m hinder', category: 'steeplechase',
      eventCodes: { M: ['3000mhinder_91_4cm'], F: ['3000mhinder_76_2cm'] },
      resultType: 'time', indoorCounts: true,
      standard: { U23_M: 61999 },
    },
    // Gange
    {
      id: '3000mg', displayName: '3000 m kappgang', category: 'walk',
      eventCodes: { M: ['3000mg'], F: ['3000mg'] },
      resultType: 'time', indoorCounts: true,
      standard: { U23_M: 94499, U20_M: 98999, U23_F: 104999, U20_F: 106999 },
    },
    // Hopp
    {
      id: 'hoyde', displayName: 'Høyde', category: 'jumps',
      eventCodes: { M: ['hoyde'], F: ['hoyde'] },
      resultType: 'height', indoorCounts: true,
      standard: { U23_M: 1880, U20_M: 1830, U23_F: 1580, U20_F: 1580 },
    },
    {
      id: 'stav', displayName: 'Stav', category: 'jumps',
      eventCodes: { M: ['stav'], F: ['stav'] },
      resultType: 'height', indoorCounts: true,
      standard: { U23_M: 3500, U20_M: 3500, U23_F: 2700, U20_F: 2700 },
    },
    {
      id: 'lengde', displayName: 'Lengde', category: 'jumps',
      eventCodes: { M: ['lengde'], F: ['lengde'] },
      resultType: 'distance', indoorCounts: true,
      standard: { U23_M: 6400, U20_M: 6150, U23_F: 5150, U20_F: 5100 },
    },
    {
      id: 'tresteg', displayName: 'Tresteg', category: 'jumps',
      eventCodes: { M: ['tresteg'], F: ['tresteg'] },
      resultType: 'distance', indoorCounts: true,
      standard: { U23_M: 13000, U20_M: 12700, U23_F: 10500, U20_F: 10400 },
    },
    // Kast — U20 men use lighter implements
    {
      id: 'kule', displayName: 'Kule', category: 'throws',
      eventCodes: { M: ['kule_7_26kg'], F: ['kule_4kg'], U20_M: ['kule_6kg'] },
      resultType: 'distance', indoorCounts: true,
      standard: { U23_M: 11750, U20_M: 12000, U23_F: 10000, U20_F: 9500 },
    },
    {
      id: 'diskos', displayName: 'Diskos', category: 'throws',
      eventCodes: { M: ['diskos_2kg'], F: ['diskos_1kg'], U20_M: ['diskos_1_75kg'] },
      resultType: 'distance', indoorCounts: true,
      standard: { U23_M: 37000, U20_M: 35000, U23_F: 30000, U20_F: 29000 },
    },
    {
      id: 'slegge', displayName: 'Slegge', category: 'throws',
      eventCodes: { M: ['slegge_726kg/1215cm'], F: ['slegge_40kg/1195cm'], U20_M: ['slegge_60kg/1215cm'] },
      resultType: 'distance', indoorCounts: true,
      standard: { U23_M: 40000, U20_M: 40000, U23_F: 35000, U20_F: 35000 },
    },
    {
      id: 'spyd', displayName: 'Spyd', category: 'throws',
      eventCodes: { M: ['spyd_800g'], F: ['spyd_600g'] },
      resultType: 'distance', indoorCounts: true,
      standard: { U23_M: 50000, U20_M: 46000, U23_F: 35000, U20_F: 35000 },
    },
  ],
}

// --- All championships ---

export const CHAMPIONSHIPS: Championship[] = [
  NM_SENIOR_2026,
  NM_JUNIOR_2026,
]
