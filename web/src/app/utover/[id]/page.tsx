import { Suspense } from "react"
import { notFound } from "next/navigation"
import Link from "next/link"
import { createClient } from "@/lib/supabase/server"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"
import { AthleteHeader } from "@/components/athlete/AthleteHeader"
import { PersonalBestsSection } from "@/components/athlete/PersonalBestsSection"
import { ResultsSection } from "@/components/athlete/ResultsSection"
import { AthleteChartsSection } from "@/components/athlete/AthleteChartsSection"

// Type definitions
interface AthleteStats {
  totalResults: number
  totalMeets: number
  totalEvents: number
  firstYear: number | null
  lastYear: number | null
  nationalRecordsCount: number
}

// Data fetching functions
async function getAthlete(id: string) {
  const supabase = await createClient()

  const { data: athlete } = await supabase
    .from("athletes")
    .select("*")
    .eq("id", id)
    .single()

  if (!athlete) return null

  let club = null
  if (athlete.current_club_id) {
    const { data: clubData } = await supabase
      .from("clubs")
      .select("id, name")
      .eq("id", athlete.current_club_id)
      .single()
    club = clubData
  }

  return { ...athlete, club }
}

async function getAthleteStats(athleteId: string): Promise<AthleteStats> {
  const supabase = await createClient()

  const { data: statsData } = await supabase
    .from("results_full")
    .select("id, meet_id, event_id, season_year, is_national_record")
    .eq("athlete_id", athleteId)

  if (!statsData || statsData.length === 0) {
    return {
      totalResults: 0,
      totalMeets: 0,
      totalEvents: 0,
      firstYear: null,
      lastYear: null,
      nationalRecordsCount: 0,
    }
  }

  const uniqueMeets = new Set(statsData.map((r) => r.meet_id))
  const uniqueEvents = new Set(statsData.map((r) => r.event_id))
  const years = statsData.map((r) => r.season_year).filter((y): y is number => y !== null)
  const nationalRecords = statsData.filter((r) => r.is_national_record).length

  return {
    totalResults: statsData.length,
    totalMeets: uniqueMeets.size,
    totalEvents: uniqueEvents.size,
    firstYear: years.length > 0 ? Math.min(...years) : null,
    lastYear: years.length > 0 ? Math.max(...years) : null,
    nationalRecordsCount: nationalRecords,
  }
}

async function getMainEvent(athleteId: string): Promise<string | null> {
  const supabase = await createClient()

  const { data } = await supabase
    .from("results_full")
    .select("event_name")
    .eq("athlete_id", athleteId)

  if (!data || data.length === 0) return null

  const eventCounts: Record<string, number> = {}
  data.forEach((r) => {
    if (r.event_name) {
      eventCounts[r.event_name] = (eventCounts[r.event_name] || 0) + 1
    }
  })

  const sortedEvents = Object.entries(eventCounts).sort((a, b) => b[1] - a[1])
  return sortedEvents.length > 0 ? sortedEvents[0][0] : null
}

async function getPersonalBestsDetailed(athleteId: string) {
  const supabase = await createClient()

  const { data } = await supabase
    .from("personal_bests_detailed")
    .select("*")
    .eq("athlete_id", athleteId)

  return data ?? []
}

async function getAthleteResults(athleteId: string) {
  const supabase = await createClient()

  const { data } = await supabase
    .from("results_full")
    .select("*")
    .eq("athlete_id", athleteId)
    .eq("status", "OK")
    .order("date", { ascending: false })

  return data ?? []
}

async function getAthleteSeasons(athleteId: string): Promise<number[]> {
  const supabase = await createClient()

  const { data } = await supabase
    .from("results_full")
    .select("season_year")
    .eq("athlete_id", athleteId)

  if (!data) return []

  const years = [...new Set(data.map((r) => r.season_year).filter((y): y is number => y !== null))]
  return years.sort((a, b) => b - a)
}

async function getAthleteEvents(athleteId: string) {
  const supabase = await createClient()

  const { data } = await supabase
    .from("results_full")
    .select("event_id, event_name, event_code, result_type")
    .eq("athlete_id", athleteId)

  if (!data) return []

  const uniqueEvents = new Map<string, { id: string; name: string; code: string; result_type: string }>()
  data.forEach((r) => {
    if (r.event_id && r.event_name && !uniqueEvents.has(r.event_id)) {
      uniqueEvents.set(r.event_id, {
        id: r.event_id,
        name: r.event_name,
        code: r.event_code || "",
        result_type: r.result_type || "time",
      })
    }
  })

  return Array.from(uniqueEvents.values()).sort((a, b) =>
    a.name.localeCompare(b.name, "no")
  )
}

async function getSeasonBests(athleteId: string) {
  const supabase = await createClient()

  const { data } = await supabase
    .from("season_bests")
    .select("*")
    .eq("athlete_id", athleteId)

  if (!data) return []

  return data.map((sb) => ({
    season_year: parseInt(sb.season_name?.split(" ")[0] || "0"),
    event_id: sb.event_id || "",
    event_name: sb.event_name || "",
    event_code: sb.event_code || "",
    result_type: sb.result_type || "time",
    performance: sb.performance || "",
    performance_value: sb.performance_value || 0,
    meet_id: sb.meet_id || "",
  }))
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const athlete = await getAthlete(id)

  if (!athlete) {
    return { title: "Utøver ikke funnet" }
  }

  return {
    title: athlete.full_name || `${athlete.first_name} ${athlete.last_name}`,
    description: `Resultater og statistikk for ${athlete.full_name || `${athlete.first_name} ${athlete.last_name}`}`,
  }
}

export default async function AthletePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const athlete = await getAthlete(id)

  if (!athlete) {
    notFound()
  }

  // Fetch all data in parallel
  const [stats, mainEvent, personalBests, results, seasons, events, seasonBests] =
    await Promise.all([
      getAthleteStats(id),
      getMainEvent(id),
      getPersonalBestsDetailed(id),
      getAthleteResults(id),
      getAthleteSeasons(id),
      getAthleteEvents(id),
      getSeasonBests(id),
    ])

  const club = athlete.club as { id: string; name: string } | null
  const fullName = athlete.full_name || `${athlete.first_name} ${athlete.last_name}`

  // Map results for ResultsSection
  const mappedResults = results.map((r) => ({
    id: r.id || "",
    date: r.date || "",
    performance: r.performance || "",
    performance_value: r.performance_value,
    wind: r.wind,
    place: r.place,
    round: r.round,
    is_pb: r.is_pb,
    is_sb: r.is_sb,
    is_national_record: r.is_national_record,
    event_id: r.event_id || "",
    event_name: r.event_name || "",
    event_code: r.event_code || "",
    result_type: r.result_type || "time",
    meet_id: r.meet_id || "",
    meet_name: r.meet_name || "",
    meet_indoor: r.meet_indoor,
    season_year: r.season_year,
  }))

  // Map personal bests for PersonalBestsSection
  const mappedPBs = personalBests.map((pb) => ({
    result_id: pb.result_id || "",
    event_id: pb.event_id || "",
    event_name: pb.event_name || "",
    event_code: pb.event_code || "",
    result_type: pb.result_type || "time",
    performance: pb.performance || "",
    performance_value: pb.performance_value,
    date: pb.date || "",
    wind: pb.wind,
    is_national_record: pb.is_national_record,
    meet_id: pb.meet_id || "",
    meet_name: pb.meet_name || "",
    meet_city: pb.meet_city || "",
    is_indoor: pb.is_indoor || false,
    event_sort_order: pb.event_sort_order,
  }))

  // Create Set of PB result IDs for marking in charts/tables
  const pbResultIds = new Set(
    personalBests
      .map((pb) => pb.result_id)
      .filter((id): id is string => id !== null && id !== undefined)
  )

  return (
    <div className="container py-6">
      {/* Breadcrumbs */}
      <Breadcrumbs
        items={[
          { label: "Utøvere", href: "/utover" },
          { label: fullName },
        ]}
      />

      {/* Header */}
      <div className="mt-4">
        <AthleteHeader
          athlete={{
            id: athlete.id,
            full_name: athlete.full_name,
            first_name: athlete.first_name,
            last_name: athlete.last_name,
            birth_date: athlete.birth_date,
            birth_year: athlete.birth_year,
            gender: athlete.gender,
            profile_image_url: athlete.profile_image_url,
          }}
          club={club}
          stats={stats}
          mainEvent={mainEvent}
        />
      </div>

      {/* Main content - "At a glance" layout */}
      <div className="mt-6 space-y-6">
        {/* Section 1: Personal Bests (full width, most important) */}
        <section>
          <h2 className="mb-3">Personlige rekorder</h2>
          <PersonalBestsSection personalBests={mappedPBs} />
        </section>

        {/* Section 2: Charts with shared event selector */}
        <section>
          <Suspense fallback={<div className="h-[400px] bg-muted animate-pulse rounded" />}>
            <AthleteChartsSection
              seasonBests={seasonBests}
              results={mappedResults}
              events={events}
              pbResultIds={pbResultIds}
            />
          </Suspense>
        </section>

        {/* Section 4: All Results (filterable) */}
        <section>
          <h2 className="mb-3">Alle resultater</h2>
          <Suspense fallback={<div className="h-[300px] bg-muted animate-pulse rounded" />}>
            <ResultsSection
              results={mappedResults}
              seasons={seasons}
              events={events.map((e) => ({ id: e.id, name: e.name, code: e.code }))}
              pbResultIds={pbResultIds}
            />
          </Suspense>
        </section>
      </div>
    </div>
  )
}

