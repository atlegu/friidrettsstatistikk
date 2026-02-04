// Event configuration for smart display and grouping

// Event categories for collapsible display with gender-specific events
export interface EventCategory {
  id: string
  name: string
  events?: string[]  // Same events for both genders
  genderEvents?: { M: string[]; F: string[] }  // Different events per gender
  indoorGenderEvents?: { M: string[]; F: string[] }  // Indoor-specific events per gender
  defaultExpanded?: boolean
}

export const EVENT_CATEGORIES: EventCategory[] = [
  {
    id: 'sprint',
    name: 'Sprint',
    events: ['60m', '100m', '200m', '400m'],
    defaultExpanded: true,
  },
  {
    id: 'middle',
    name: 'Mellomdistanse',
    events: ['800m', '1500m', '1mile', '3000m'],
    defaultExpanded: true,
  },
  {
    id: 'long',
    name: 'Langdistanse',
    events: ['5000m', '10000m'],
    defaultExpanded: true,
  },
  {
    id: 'hurdles',
    name: 'Hekk',
    genderEvents: {
      M: ['110mh_106_7cm', '400mh_91_4cm'],
      F: ['100mh_84cm', '400mh_76_2cm'],
    },
    indoorGenderEvents: {
      M: ['60mh_106_7cm'],
      F: ['60mh_84cm'],
    },
    defaultExpanded: true,
  },
  {
    id: 'steeplechase',
    name: 'Hinder',
    genderEvents: {
      M: ['3000mhinder_91_4cm'],
      F: ['3000mhinder_76_2cm'],
    },
    defaultExpanded: true,
  },
  {
    id: 'jumps',
    name: 'Hopp',
    events: ['hoyde', 'stav', 'lengde', 'tresteg'],
    defaultExpanded: true,
  },
  {
    id: 'throws',
    name: 'Kast',
    genderEvents: {
      M: ['kule_7_26kg', 'diskos_2kg', 'slegge_726kg/1215cm', 'spyd_800g'],
      F: ['kule_4kg', 'diskos_1kg', 'slegge_40kg/1195cm', 'spyd_600g'],
    },
    defaultExpanded: true,
  },
  {
    id: 'combined',
    name: 'Mangekamp',
    genderEvents: {
      M: ['10_k_100m-lengde-kule-høyde-400m-110mh-diskos-stav'],
      F: ['7_k_100mh-høyde-kule-200m-lengde-spyd-800m'],
    },
    defaultExpanded: false,
  },
  {
    id: 'relay',
    name: 'Stafett',
    events: ['4x100m', '4x400m'],
    defaultExpanded: false,
  },
  {
    id: 'walk',
    name: 'Gange',
    events: ['3000mg', '5000mg', '10000mg', '20kmg'],
    defaultExpanded: false,
  },
]

// Display names for events (cleaner than database names)
export const EVENT_DISPLAY_NAMES: Record<string, string> = {
  // Sprint
  '60m': '60 meter',
  '100m': '100 meter',
  '200m': '200 meter',
  '400m': '400 meter',
  // Middle distance
  '800m': '800 meter',
  '1500m': '1500 meter',
  '1mile': '1 engelsk mil',
  '3000m': '3000 meter',
  // Long distance
  '5000m': '5000 meter',
  '10000m': '10000 meter',
  // Hurdles - show clean names for standard heights
  '110mh_106_7cm': '110 meter hekk',
  '110mh_100cm': '110 meter hekk (J)',
  '110mh_91_4cm': '110 meter hekk (G)',
  '100mh_84cm': '100 meter hekk',
  '100mh_76_2cm': '100 meter hekk (J)',
  '400mh_91_4cm': '400 meter hekk',
  '400mh_76_2cm': '400 meter hekk',
  '400mh_84cm': '400 meter hekk (J)',
  // 60m hurdles (indoor)
  '60mh_106_7cm': '60 meter hekk',
  '60mh_84cm': '60 meter hekk',
  '60mh_91_4cm': '60 meter hekk (G)',
  '60mh_100cm': '60 meter hekk (J)',
  '60mh_76_2cm': '60 meter hekk (J)',
  '60mh_68cm': '60 meter hekk (rekrutt)',
  '60mh_60cm': '60 meter hekk (yngre)',
  // Steeplechase
  '3000mhinder_91_4cm': '3000 meter hinder',
  '3000mhinder_76_2cm': '3000 meter hinder',
  // Jumps
  'hoyde': 'Høyde',
  'stav': 'Stav',
  'lengde': 'Lengde',
  'tresteg': 'Tresteg',
  // Throws - show clean names for standard weights
  'kule_7_26kg': 'Kule',
  'kule_4kg': 'Kule',
  'kule_6kg': 'Kule (6kg)',
  'kule_5kg': 'Kule (5kg)',
  'kule_3kg': 'Kule (3kg)',
  'kule_2kg': 'Kule (2kg)',
  'diskos_2kg': 'Diskos',
  'diskos_1kg': 'Diskos',
  'diskos_1_75kg': 'Diskos (1,75kg)',
  'diskos_1_5kg': 'Diskos (1,5kg)',
  'diskos_750g': 'Diskos (750g)',
  'diskos_600g': 'Diskos (600g)',
  'slegge_726kg/1215cm': 'Slegge',
  'slegge_40kg/1195cm': 'Slegge',
  'slegge_60kg/1215cm': 'Slegge (6kg)',
  'slegge_50kg/120cm': 'Slegge (5kg)',
  'slegge_30kg/110cm': 'Slegge (3kg)',
  'slegge_30kg_1195cm': 'Slegge (3kg)',
  'slegge_20kg/110cm': 'Slegge (2kg)',
  'spyd_800g': 'Spyd',
  'spyd_600g': 'Spyd',
  'spyd_700g': 'Spyd (700g)',
  'spyd_500g': 'Spyd (500g)',
  'spyd_400g': 'Spyd (400g)',
  // Combined
  '10_k_100m-lengde-kule-høyde-400m-110mh-diskos-stav': 'Tikamp',
  '7_k_100mh-høyde-kule-200m-lengde-spyd-800m': 'Sjukamp',
  // Relay
  '4x100m': '4 x 100 meter',
  '4x400m': '4 x 400 meter',
  // Walk
  '3000mg': '3000 meter gange',
  '5000mg': '5000 meter gange',
  '10000mg': '10000 meter gange',
  '20kmg': '20 km gange',
}

// Championship events for season leaders display on the front page
// Indoor: December–March, Outdoor: April–November
export const INDOOR_CHAMPIONSHIP_EVENTS: Record<'M' | 'F', string[]> = {
  M: ['60m', '200m', '400m', '800m', '1500m', '3000m', '60mh_106_7cm', 'hoyde', 'stav', 'lengde', 'tresteg', 'kule_7_26kg'],
  F: ['60m', '200m', '400m', '800m', '1500m', '3000m', '60mh_84cm', 'hoyde', 'stav', 'lengde', 'tresteg', 'kule_4kg'],
}

export const OUTDOOR_CHAMPIONSHIP_EVENTS: Record<'M' | 'F', string[]> = {
  M: ['100m', '200m', '400m', '800m', '1500m', '5000m', '10000m', '110mh_106_7cm', '400mh_91_4cm', '3000mhinder_91_4cm', 'hoyde', 'stav', 'lengde', 'tresteg', 'kule_7_26kg', 'diskos_2kg', 'slegge_726kg/1215cm', 'spyd_800g'],
  F: ['100m', '200m', '400m', '800m', '1500m', '5000m', '10000m', '100mh_84cm', '400mh_76_2cm', '3000mhinder_76_2cm', 'hoyde', 'stav', 'lengde', 'tresteg', 'kule_4kg', 'diskos_1kg', 'slegge_40kg/1195cm', 'spyd_600g'],
}

// Time event codes where lower performance_value is better
export const TIME_EVENT_CODES = new Set([
  '60m', '100m', '200m', '400m', '800m', '1500m', '3000m', '5000m', '10000m',
  '60mh_106_7cm', '60mh_100cm', '60mh_91_4cm', '60mh_84cm', '60mh_76_2cm', '60mh_68cm', '60mh_60cm',
  '110mh_106_7cm', '100mh_84cm',
  '400mh_91_4cm', '400mh_76_2cm', '3000mhinder_91_4cm', '3000mhinder_76_2cm',
])

// Minimum results to show in standard view
export const MIN_RESULTS_STANDARD_VIEW = 50

// Get events for a category based on gender and venue
export function getCategoryEvents(
  category: EventCategory,
  gender: 'M' | 'F',
  indoor?: boolean
): string[] {
  if (indoor && category.indoorGenderEvents) {
    return category.indoorGenderEvents[gender] || []
  }
  if (category.genderEvents) {
    return category.genderEvents[gender] || []
  }
  return category.events || []
}

// Get display name for an event code
export function getEventDisplayName(code: string): string {
  return EVENT_DISPLAY_NAMES[code] || code
}

// Check if an event code is in our "main events" list
export function isMainEvent(code: string, gender: 'M' | 'F'): boolean {
  for (const category of EVENT_CATEGORIES) {
    const events = getCategoryEvents(category, gender)
    if (events.includes(code)) {
      return true
    }
  }
  return false
}
