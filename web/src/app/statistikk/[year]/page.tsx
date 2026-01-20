import Link from "next/link"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { formatPerformance } from "@/lib/format-performance"
import { getBirthYear } from "@/lib/date-utils"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"

const AGE_GROUPS = [
  { value: "Senior", label: "Senior (15+)" },
  { value: "U23", label: "U23" },
  { value: "U20", label: "U20" },
  { value: "U18", label: "U18" },
  { value: "G/J15", label: "G/J15" },
  { value: "G/J14", label: "G/J14" },
  { value: "G/J13", label: "G/J13" },
] as const

// Age groups included in "Senior" filter (15 years and older)
const SENIOR_AGE_GROUPS = ["Senior", "U23", "U20", "U18", "G/J15"]

// Sprint events where manual times (1 decimal) should be excluded
const SPRINT_EVENTS = ["60 meter", "100 meter", "200 meter"]

// Check if a performance is a manual time (only 1 decimal)
function isManualTime(performance: string | null): boolean {
  if (!performance || !performance.includes(".")) return false
  const decimals = performance.split(".")[1]?.length ?? 0
  return decimals === 1
}

async function getEvents() {
  const supabase = await createClient()

  const { data } = await supabase
    .from("events")
    .select("*")
    .order("sort_order", { ascending: true })

  return data ?? []
}

async function getTopResults(
  year: number,
  eventId: string,
  eventName: string,
  gender: string,
  ageGroup: string,
  resultType: string,
  limit = 25
) {
  const supabase = await createClient()

  // For time events, lower is better (ascending)
  // For distance, height, points - higher is better (descending)
  const ascending = resultType === "time"

  // Get only the best result per athlete using RPC or raw query
  // First get all results, then filter to best per athlete in JS
  let query = supabase
    .from("results_full")
    .select("*")
    .eq("event_id", eventId)
    .eq("season_year", year)
    .eq("gender", gender)
    .eq("status", "OK")
    .not("performance_value", "is", null)
    .gt("performance_value", 0)

  if (ageGroup === "Senior") {
    // Senior includes all 15+ age groups
    query = query.in("age_group", SENIOR_AGE_GROUPS)
  } else if (ageGroup !== "all") {
    query = query.eq("age_group", ageGroup)
  }

  // Check if this is a sprint event (manual times should be excluded)
  const isSprintEvent = SPRINT_EVENTS.includes(eventName)

  // For non-sprint events, use a simpler query with limit
  if (!isSprintEvent) {
    const { data } = await query
      .order("performance_value", { ascending })
      .limit(limit * 3) // Get extra to allow for duplicates per athlete

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

  // For sprint events, get more results to filter out manual times
  const { data } = await query
    .order("performance_value", { ascending })
    .limit(limit * 10)

  if (!data) return []

  // Filter to best result per athlete, skipping manual times
  const bestByAthlete = new Map<string, typeof data[0]>()
  for (const result of data) {
    if (!result.athlete_id) continue
    if (isManualTime(result.performance)) continue
    if (!bestByAthlete.has(result.athlete_id)) {
      bestByAthlete.set(result.athlete_id, result)
    }
  }

  return Array.from(bestByAthlete.values()).slice(0, limit)
}

export async function generateMetadata({ params }: { params: Promise<{ year: string }> }) {
  const { year } = await params

  return {
    title: `Årsliste ${year}`,
    description: `Beste norske friidrettsresultater i ${year}`,
  }
}

export default async function YearListPage({
  params,
  searchParams,
}: {
  params: Promise<{ year: string }>
  searchParams: Promise<{ event?: string; gender?: string; age?: string }>
}) {
  const { year } = await params
  const { event: selectedEventId, gender = "M", age = "Senior" } = await searchParams
  const yearNum = parseInt(year)

  const events = await getEvents()
  const selectedEvent = selectedEventId
    ? events.find((e) => e.id === selectedEventId)
    : events[0]

  const results = selectedEvent
    ? await getTopResults(yearNum, selectedEvent.id, selectedEvent.name, gender, age, selectedEvent.result_type ?? "time")
    : []

  const genderLabel = gender === "M" ? "Menn" : "Kvinner"
  const ageLabel = age === "all" ? "Alle aldersgrupper" : AGE_GROUPS.find(a => a.value === age)?.label ?? age

  const buildUrl = (overrides: { event?: string; gender?: string; age?: string }) => {
    const params = new URLSearchParams()
    const eventParam = overrides.event ?? selectedEvent?.id
    const genderParam = overrides.gender ?? gender
    const ageParam = overrides.age ?? age
    if (eventParam) params.set("event", eventParam)
    if (genderParam) params.set("gender", genderParam)
    if (ageParam) params.set("age", ageParam)
    return `/statistikk/${year}?${params.toString()}`
  }

  return (
    <div className="container py-6">
      <Breadcrumbs items={[
        { label: "Statistikk", href: "/statistikk" },
        { label: `Årsliste ${year}` }
      ]} />
      <h1 className="mt-4 mb-4">Årsliste {year}</h1>

      <div className="grid gap-8 lg:grid-cols-5">
        {/* Sidebar - Filters */}
        <div className="lg:col-span-1 space-y-4 lg:max-w-[180px]">
          {/* Gender filter */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Kjønn</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Link
                  href={buildUrl({ gender: "M" })}
                  className={`flex-1 rounded px-3 py-2 text-center text-sm font-medium ${
                    gender === "M"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted hover:bg-muted/80"
                  }`}
                >
                  Menn
                </Link>
                <Link
                  href={buildUrl({ gender: "F" })}
                  className={`flex-1 rounded px-3 py-2 text-center text-sm font-medium ${
                    gender === "F"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted hover:bg-muted/80"
                  }`}
                >
                  Kvinner
                </Link>
              </div>
            </CardContent>
          </Card>

          {/* Age group filter */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Aldersgruppe</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-1">
                <Link
                  href={buildUrl({ age: "all" })}
                  className={`block rounded px-2 py-1 text-sm ${
                    age === "all"
                      ? "bg-primary text-primary-foreground"
                      : "hover:bg-muted"
                  }`}
                >
                  Alle
                </Link>
                {AGE_GROUPS.map((ageGroup) => (
                  <Link
                    key={ageGroup.value}
                    href={buildUrl({ age: ageGroup.value })}
                    className={`block rounded px-2 py-1 text-sm ${
                      age === ageGroup.value
                        ? "bg-primary text-primary-foreground"
                        : "hover:bg-muted"
                    }`}
                  >
                    {ageGroup.label}
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Events filter */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Øvelse</CardTitle>
            </CardHeader>
            <CardContent className="max-h-[50vh] overflow-y-auto">
              <div className="space-y-1">
                {events.map((event) => (
                  <Link
                    key={event.id}
                    href={buildUrl({ event: event.id })}
                    className={`block rounded px-2 py-1 text-sm ${
                      selectedEvent?.id === event.id
                        ? "bg-primary text-primary-foreground"
                        : "hover:bg-muted"
                    }`}
                  >
                    {event.name}
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main content - Results */}
        <div className="lg:col-span-4">
          <Card>
            <CardHeader>
              <CardTitle>
                {selectedEvent?.name ?? "Velg øvelse"}
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                {genderLabel} · {ageLabel}
              </p>
            </CardHeader>
            <CardContent className="p-0">
              {results.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-3 py-2 text-left text-sm font-medium w-10">#</th>
                        <th className="px-3 py-2 text-left text-sm font-medium">Resultat</th>
                        <th className="px-3 py-2 text-left text-sm font-medium">Utøver</th>
                        <th className="px-3 py-2 text-left text-sm font-medium w-14">Født</th>
                        <th className="hidden px-3 py-2 text-left text-sm font-medium md:table-cell">Klubb</th>
                        <th className="hidden px-3 py-2 text-left text-sm font-medium lg:table-cell">Stevne</th>
                        <th className="hidden px-3 py-2 text-left text-sm font-medium lg:table-cell">Dato</th>
                      </tr>
                    </thead>
                    <tbody>
                      {results.map((result, index) => (
                        <tr key={result.id} className="border-b last:border-0 hover:bg-muted/30">
                          <td className="px-3 py-2 text-sm text-muted-foreground">{index + 1}</td>
                          <td className="px-3 py-2">
                            <span className="perf-value">{formatPerformance(result.performance, result.result_type)}</span>
                            {result.wind !== null && (
                              <span className="ml-1 text-xs text-muted-foreground">
                                ({result.wind > 0 ? "+" : ""}{result.wind})
                              </span>
                            )}
                          </td>
                          <td className="px-3 py-2">
                            <Link
                              href={`/utover/${result.athlete_id}`}
                              className="font-medium text-primary hover:underline"
                            >
                              {result.athlete_name}
                            </Link>
                          </td>
                          <td className="px-3 py-2 text-sm text-muted-foreground">
                            {getBirthYear(result.birth_date) ?? "-"}
                          </td>
                          <td className="hidden px-3 py-2 text-sm md:table-cell">
                            {result.club_name ?? "-"}
                          </td>
                          <td className="hidden px-3 py-2 text-sm lg:table-cell">
                            <Link
                              href={`/stevner/${result.meet_id}`}
                              className="hover:text-primary hover:underline"
                            >
                              {result.meet_name}
                            </Link>
                          </td>
                          <td className="hidden px-3 py-2 text-sm text-muted-foreground lg:table-cell">
                            {result.date
                              ? new Date(result.date).toLocaleDateString("no-NO", {
                                  day: "numeric",
                                  month: "short",
                                })
                              : "-"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="p-4 text-center text-muted-foreground">
                  {selectedEvent
                    ? "Ingen resultater funnet for denne øvelsen"
                    : "Velg en øvelse fra listen til venstre"}
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
