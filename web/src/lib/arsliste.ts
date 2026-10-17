import { createClient } from "@/lib/supabase/server"
import { erVindpaavirket } from "@/lib/vind"

/* Årslisten: beste resultat per utøver i én øvelse, ett år, ett kjønn.
 * Brukes av /statistikk/[year] og av eksporten, så begge gir samme liste. */

// Age group mappings for composite categories
export const AGE_GROUP_MAPPINGS: Record<string, string[]> = {
  "Senior": ["15", "16", "17", "18-19", "20-22", "Senior"],
  "U23": ["15", "16", "17", "18-19", "20-22"],
  "U20": ["15", "16", "17", "18-19"],
}

// Events where manual times should be excluded (sprint and hurdles)
export const MANUAL_TIME_CATEGORIES = ["sprint", "hurdles"]


export async function getTopResults(
  year: number,
  eventId: string,
  eventCode: string,
  gender: string,
  ageGroup: string,
  resultType: string,
  eventCategory: string,
  venue: string,
  vind: "lovlig" | "ukjent" = "lovlig",
  limit = 25
) {
  const supabase = await createClient()

  // For time events, lower is better (ascending)
  // For distance, height, points - higher is better (descending)
  const ascending = resultType === "time"

  let query = supabase
    .from("results_full")
    .select("*")
    .eq("event_id", eventId)
    .eq("season_year", year)
    .eq("gender", gender)
    .eq("status", "OK")
    .not("performance_value", "is", null)
    .gt("performance_value", 0)
          // Barn til og med 11 år vises ikke offentlig (get_age_group gir «Yngre»)
          .or("age_group.is.null,age_group.neq.Yngre")

  // Handle composite age groups (Senior, U23, U20) and individual ages
  if (ageGroup !== "all") {
    const mappedGroups = AGE_GROUP_MAPPINGS[ageGroup]
    if (mappedGroups) {
      query = query.in("age_group", mappedGroups)
    } else {
      query = query.eq("age_group", ageGroup)
    }
  }

  // Filter by indoor/outdoor venue
  if (venue === "indoor") {
    query = query.eq("meet_indoor", true)
  } else if (venue === "outdoor") {
    query = query.eq("meet_indoor", false)
  }
  // venue === "all" means no filter

  // Exclude manual times for sprint and hurdles events
  if (MANUAL_TIME_CATEGORIES.includes(eventCategory)) {
    // IS NOT TRUE, ikke = false: 42 356 resultater har is_manual_time som
    // NULL, og NULL betyr «ikke manuell», altsaa det samme som false. Med
    // «= false» falt de ut av lista. 23 040 av dem er i sprint- og
    // hekkoevelser, der dette filteret brukes. Se CLAUDE.md punkt 8.
    query = query.not("is_manual_time", "is", true)
  }

  // Vind. Gjelder bare sprint til og med 200 m og horisontale hopp med
  // tilløp, se lib/vind.ts. Den vanlige lista krever lovlig vind. Lista for
  // ukjent vind tar resultatene uten vindmåling, utendørs: innendørs finnes
  // det ikke vind, så der er ingenting ukjent.
  if (erVindpaavirket(eventCode)) {
    if (vind === "ukjent") {
      query = query.is("is_wind_legal", null).eq("meet_indoor", false)
    } else {
      query = query.eq("is_wind_legal", true)
    }
  }

  const { data } = await query
    .order("performance_value", { ascending })
    .limit(limit * 20)

  if (!data) return []

  // Filter to best result per athlete
  const bestByAthlete = new Map<string, typeof data[0]>()
  for (const result of data) {
    if (!result.athlete_id) continue
    if (!bestByAthlete.has(result.athlete_id)) {
      bestByAthlete.set(result.athlete_id, result)
    }
  }

  return Array.from(bestByAthlete.values()).slice(0, limit)
}

