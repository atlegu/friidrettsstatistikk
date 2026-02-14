"use server"

import { createClient } from "@/lib/supabase/server"

export async function searchAthletes(query: string, excludeId?: string) {
  if (query.length < 2) return []

  const supabase = await createClient()
  const { data } = await supabase
    .from("athletes")
    .select("id, first_name, last_name, full_name, birth_year, gender")
    .or(`first_name.ilike.%${query}%,last_name.ilike.%${query}%,full_name.ilike.%${query}%`)
    .limit(10)

  if (!data) return []
  return excludeId ? data.filter(a => a.id !== excludeId) : data
}

export async function fetchSeasonBests(athleteId: string) {
  const supabase = await createClient()
  const { data } = await supabase
    .from("season_bests")
    .select("event_id, event_name, event_code, result_type, performance, performance_value, season_name")
    .eq("athlete_id", athleteId)

  return data ?? []
}

export async function fetchAthleteResults(athleteId: string) {
  const supabase = await createClient()
  const allRows: Array<{
    id: string
    meet_id: string
    event_id: string
    event_name: string
    event_code: string
    result_type: string
    meet_name: string
    date: string
    place: number | null
    performance: string
    performance_value: number | null
    round: string | null
    status: string
  }> = []
  const pageSize = 1000
  let from = 0

  while (true) {
    const { data } = await supabase
      .from("results_full")
      .select("id, meet_id, event_id, event_name, event_code, result_type, meet_name, date, place, performance, performance_value, round, status")
      .eq("athlete_id", athleteId)
      .eq("status", "OK")
      .range(from, from + pageSize - 1)

    if (!data || data.length === 0) break
    allRows.push(...data)
    if (data.length < pageSize) break
    from += pageSize
  }

  return allRows
}
