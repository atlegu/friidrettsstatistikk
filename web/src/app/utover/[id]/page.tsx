import { Suspense } from "react"
import { notFound } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { AthleteHeader } from "@/components/athlete/AthleteHeader"
import { AthleteTabs } from "@/components/athlete/AthleteTabs"
import { PersonalBestsSection } from "@/components/athlete/PersonalBestsSection"
import { ResultsSection } from "@/components/athlete/ResultsSection"
import { ProgressionChart } from "@/components/athlete/ProgressionChart"
import { TopPerformancesSection } from "@/components/athlete/TopPerformancesCard"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

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

  // Get counts and date range
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

  // Find the event with most results
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
  }))
}

async function getTopPerformances(athleteId: string) {
  const supabase = await createClient()

  // Get all results for ranking
  const { data } = await supabase
    .from("results_full")
    .select("id, event_id, event_name, performance, performance_value, date, wind, meet_id, meet_name, is_national_record, result_type")
    .eq("athlete_id", athleteId)
    .eq("status", "OK")
    .not("performance_value", "is", null)

  if (!data) return {}

  // Group by event and rank
  const byEvent: Record<string, typeof data> = {}
  data.forEach((r) => {
    if (r.event_id) {
      if (!byEvent[r.event_id]) {
        byEvent[r.event_id] = []
      }
      byEvent[r.event_id].push(r)
    }
  })

  // Sort and take top 10 for each event
  const result: Record<string, Array<{
    rank: number
    result_id: string
    event_id: string
    event_name: string
    performance: string
    date: string
    wind: number | null
    meet_id: string
    meet_name: string
    is_national_record: boolean | null
  }>> = {}

  Object.entries(byEvent).forEach(([eventId, results]) => {
    // Determine if lower is better (times) or higher is better (distances, heights, points)
    const resultType = results[0]?.result_type || "time"
    const lowerIsBetter = resultType === "time"

    const sorted = [...results].sort((a, b) => {
      const valA = a.performance_value ?? 0
      const valB = b.performance_value ?? 0
      return lowerIsBetter ? valA - valB : valB - valA
    })

    result[eventId] = sorted.slice(0, 10).map((r, index) => ({
      rank: index + 1,
      result_id: r.id || "",
      event_id: r.event_id || "",
      event_name: r.event_name || "",
      performance: r.performance || "",
      date: r.date || "",
      wind: r.wind,
      meet_id: r.meet_id || "",
      meet_name: r.meet_name || "",
      is_national_record: r.is_national_record,
    }))
  })

  return result
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
  const [stats, mainEvent, personalBests, results, seasons, events, seasonBests, topPerformances] =
    await Promise.all([
      getAthleteStats(id),
      getMainEvent(id),
      getPersonalBestsDetailed(id),
      getAthleteResults(id),
      getAthleteSeasons(id),
      getAthleteEvents(id),
      getSeasonBests(id),
      getTopPerformances(id),
    ])

  const club = athlete.club as { id: string; name: string } | null

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

  // Create event order for top performances
  const eventOrder = events.map((e) => ({ id: e.id, name: e.name }))

  return (
    <div className="container py-8">
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

      <Suspense fallback={<div>Laster...</div>}>
        <AthleteTabs
          children={{
            overview: (
              <div className="space-y-8">
                {/* Summary section with key stats */}
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium text-muted-foreground">
                        Resultater
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{stats.totalResults}</div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium text-muted-foreground">
                        Stevner
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{stats.totalMeets}</div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium text-muted-foreground">
                        Øvelser
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{stats.totalEvents}</div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium text-muted-foreground">
                        Norske rekorder
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{stats.nationalRecordsCount}</div>
                    </CardContent>
                  </Card>
                </div>

                {/* Personal bests preview */}
                <div>
                  <h2 className="mb-4 text-xl font-semibold">Personlige rekorder</h2>
                  <PersonalBestsSection personalBests={mappedPBs} />
                </div>

                {/* Recent results preview */}
                <Card>
                  <CardHeader>
                    <CardTitle>Siste resultater</CardTitle>
                  </CardHeader>
                  <CardContent className="p-0">
                    {mappedResults.length > 0 ? (
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b bg-muted/50">
                              <th className="px-4 py-2 text-left font-medium">Dato</th>
                              <th className="px-4 py-2 text-left font-medium">Øvelse</th>
                              <th className="px-4 py-2 text-left font-medium">Resultat</th>
                              <th className="hidden px-4 py-2 text-left font-medium md:table-cell">
                                Stevne
                              </th>
                            </tr>
                          </thead>
                          <tbody>
                            {mappedResults.slice(0, 10).map((result) => (
                              <tr
                                key={result.id}
                                className="border-b last:border-0 hover:bg-muted/30"
                              >
                                <td className="px-4 py-2 text-muted-foreground">
                                  {new Date(result.date).toLocaleDateString("no-NO", {
                                    day: "numeric",
                                    month: "short",
                                  })}
                                </td>
                                <td className="px-4 py-2">{result.event_name}</td>
                                <td className="px-4 py-2">
                                  <span className="font-mono font-medium">
                                    {result.performance}
                                  </span>
                                  {result.is_pb && (
                                    <span className="ml-2 rounded bg-green-100 px-1.5 py-0.5 text-xs font-medium text-green-800">
                                      PB
                                    </span>
                                  )}
                                </td>
                                <td className="hidden px-4 py-2 md:table-cell">
                                  {result.meet_name}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <p className="p-4 text-sm text-muted-foreground">
                        Ingen resultater registrert
                      </p>
                    )}
                  </CardContent>
                </Card>
              </div>
            ),
            personalBests: <PersonalBestsSection personalBests={mappedPBs} />,
            results: (
              <ResultsSection
                results={mappedResults}
                seasons={seasons}
                events={events.map((e) => ({ id: e.id, name: e.name, code: e.code }))}
              />
            ),
            progression: (
              <div className="space-y-8">
                <ProgressionChart seasonBests={seasonBests} events={events} />
                <TopPerformancesSection
                  performancesByEvent={topPerformances}
                  eventOrder={eventOrder}
                />
              </div>
            ),
          }}
        />
      </Suspense>
    </div>
  )
}
