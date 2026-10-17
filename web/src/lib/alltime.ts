import { createClient } from "@/lib/supabase/server"

/* Alle tiders-listen (get_all_time_best). Brukes av /statistikk/all-time og
 * av eksporten, så begge gir samme liste. */

export const AGE_GROUP_MAPPINGS: Record<string, string[]> = {
  "Senior": ["15", "16", "17", "18-19", "20-22", "Senior"],
  "U23": ["15", "16", "17", "18-19", "20-22"],
  "U20": ["15", "16", "17", "18-19"],
}

export async function getAllTimeResults(
  eventId: string,
  gender: string,
  ageGroup: string,
  resultType: string,
  venue: string,
  timing: string,
  wind: string,
  limit: number,
  offset: number
) {
  const supabase = await createClient()

  const ascending = resultType === "time"

  // Resolve age groups
  let ageGroups: string[] | null = null
  if (ageGroup !== "all") {
    const mapped = AGE_GROUP_MAPPINGS[ageGroup]
    ageGroups = mapped ?? [ageGroup]
  }

  // Resolve venue
  const indoor = venue === "indoor" ? true : venue === "outdoor" ? false : null

  // Timing filter only applies to running events (result_type "time")
  // Field events (distance/height) have no concept of electronic/manual timing
  const isTimingRelevant = resultType === "time"
  const excludeManual = isTimingRelevant && timing === "electronic"
  const onlyManual = isTimingRelevant && timing === "manual"
  const excludeWindIllegal = wind === "legal"

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const { data, error } = await (supabase.rpc as any)("get_all_time_best", {
    p_event_id: eventId,
    p_gender: gender,
    p_age_groups: ageGroups,
    p_indoor: indoor,
    p_ascending: ascending,
    p_exclude_manual: excludeManual,
    p_exclude_wind_illegal: excludeWindIllegal,
    p_only_manual: onlyManual,
    p_limit: limit,
    p_offset: offset,
  })

  if (error) {
    console.error("RPC error:", error)
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return { results: [] as any[], totalCount: 0 }
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const results = (data ?? []) as any[]
  const totalCount = results.length > 0 ? Number(results[0].total_count) : 0

  return { results, totalCount }
}
