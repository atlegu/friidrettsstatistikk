import Link from "next/link"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { formatPerformance } from "@/lib/format-performance"
import { getBirthYear } from "@/lib/date-utils"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"

export const metadata = {
  title: "All-time lister",
  description: "Historiske toppresultater i norsk friidrett gjennom alle tider",
}

const AGE_GROUPS = [
  { value: "Senior", label: "Senior" },
  { value: "U23", label: "Junior 15-22" },
  { value: "U20", label: "Junior 15-19" },
  { value: "20-22", label: "20-22 år" },
  { value: "18-19", label: "18-19 år" },
  { value: "17", label: "17 år" },
  { value: "16", label: "16 år" },
  { value: "15", label: "15 år" },
  { value: "14", label: "14 år" },
  { value: "13", label: "13 år" },
] as const

// Age group mappings for composite categories
const AGE_GROUP_MAPPINGS: Record<string, string[]> = {
  "Senior": ["15", "16", "17", "18-19", "20-22", "Senior"],
  "U23": ["15", "16", "17", "18-19", "20-22"],
  "U20": ["15", "16", "17", "18-19"],
}

// Events where manual times should be excluded (sprint and hurdles)
const MANUAL_TIME_CATEGORIES = ["sprint", "hurdles"]

// Events where wind affects validity (outdoor sprints ≤200m, long jump, triple jump)
const WIND_AFFECTED_EVENTS = ["60 meter", "80 meter", "100 meter", "150 meter", "200 meter"]
const WIND_AFFECTED_CATEGORIES = ["jumps"] // lengde, tresteg

async function getEvents() {
  const supabase = await createClient()

  const { data } = await supabase
    .from("events")
    .select("*")
    .order("sort_order", { ascending: true })

  return data ?? []
}

async function getAllTimeResults(
  eventId: string,
  eventName: string,
  gender: string,
  ageGroup: string,
  resultType: string,
  eventCategory: string,
  venue: string
) {
  const supabase = await createClient()

  // For time events, lower is better (ascending)
  // For distance, height, points - higher is better (descending)
  const ascending = resultType === "time"

  // Build base query function (we'll call it multiple times for batching)
  const buildQuery = () => {
    let q = supabase
      .from("results_full")
      .select("*", { count: "exact" })
      .eq("event_id", eventId)
      .eq("gender", gender)
      .eq("status", "OK")
      .not("performance_value", "is", null)
      .gt("performance_value", 0)

    // Handle composite age groups (Senior, U23, U20) and individual ages
    if (ageGroup !== "all") {
      const mappedGroups = AGE_GROUP_MAPPINGS[ageGroup]
      if (mappedGroups) {
        q = q.in("age_group", mappedGroups)
      } else {
        q = q.eq("age_group", ageGroup)
      }
    }

    // Filter by indoor/outdoor venue
    if (venue === "indoor") {
      q = q.eq("meet_indoor", true)
    } else if (venue === "outdoor") {
      q = q.eq("meet_indoor", false)
    }

    // Exclude manual times for sprint and hurdles events
    if (MANUAL_TIME_CATEGORIES.includes(eventCategory)) {
      q = q.eq("is_manual_time", false)
    }

    // Exclude wind-assisted results for affected events
    if (WIND_AFFECTED_EVENTS.includes(eventName) || WIND_AFFECTED_CATEGORIES.includes(eventCategory)) {
      q = q.eq("is_wind_legal", true)
    }

    return q
  }

  // Fetch data in batches of 1000 to work around API limits
  const BATCH_SIZE = 1000
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const allData: any[] = []
  let offset = 0
  let hasMore = true

  while (hasMore) {
    const { data, error, count } = await buildQuery()
      .order("performance_value", { ascending })
      .range(offset, offset + BATCH_SIZE - 1)

    if (error) {
      console.error("Supabase query error:", error)
      break
    }

    if (data && data.length > 0) {
      allData.push(...data)
      offset += BATCH_SIZE
      // Stop if we got fewer than BATCH_SIZE (means we're at the end)
      // or if we've fetched enough unique athletes (optimization)
      hasMore = data.length === BATCH_SIZE && allData.length < 50000
    } else {
      hasMore = false
    }
  }

  console.log(`[All-time] Event: ${eventName}, Gender: ${gender}, Raw results: ${allData.length}`)

  // Filter to best result per athlete
  const bestByAthlete = new Map<string, typeof allData[0]>()
  for (const result of allData) {
    if (!result.athlete_id) continue
    if (!bestByAthlete.has(result.athlete_id)) {
      bestByAthlete.set(result.athlete_id, result)
    }
  }

  const uniqueResults = Array.from(bestByAthlete.values())
  console.log(`[All-time] Unique athletes: ${uniqueResults.length}`)

  return uniqueResults
}

const RESULTS_PER_PAGE = 100

export default async function AllTimePage({
  searchParams,
}: {
  searchParams: Promise<{ event?: string; gender?: string; age?: string; venue?: string; page?: string }>
}) {
  const { event: selectedEventId, gender = "M", age = "Senior", venue = "outdoor", page = "1" } = await searchParams
  const currentPage = Math.max(1, parseInt(page) || 1)

  const events = await getEvents()
  const selectedEvent = selectedEventId
    ? events.find((e) => e.id === selectedEventId)
    : events[0]

  const results = selectedEvent
    ? await getAllTimeResults(selectedEvent.id, selectedEvent.name, gender, age, selectedEvent.result_type ?? "time", selectedEvent.category ?? "", venue)
    : []

  const genderLabel = gender === "M" ? "Menn" : "Kvinner"
  const ageLabel = age === "all" ? "Alle aldersgrupper" : AGE_GROUPS.find(a => a.value === age)?.label ?? age
  const venueLabel = venue === "indoor" ? "Innendørs" : venue === "outdoor" ? "Utendørs" : "Alle"

  const buildUrl = (overrides: { event?: string; gender?: string; age?: string; venue?: string; page?: number }) => {
    const params = new URLSearchParams()
    const eventParam = overrides.event ?? selectedEvent?.id
    const genderParam = overrides.gender ?? gender
    const ageParam = overrides.age ?? age
    const venueParam = overrides.venue ?? venue
    const pageParam = overrides.page ?? (overrides.event !== undefined || overrides.gender !== undefined || overrides.age !== undefined || overrides.venue !== undefined ? 1 : currentPage)
    if (eventParam) params.set("event", eventParam)
    if (genderParam) params.set("gender", genderParam)
    if (ageParam) params.set("age", ageParam)
    if (venueParam) params.set("venue", venueParam)
    if (pageParam > 1) params.set("page", pageParam.toString())
    return `/statistikk/all-time?${params.toString()}`
  }

  // Pagination calculations
  const totalResults = results.length
  const totalPages = Math.ceil(totalResults / RESULTS_PER_PAGE)
  const startIndex = (currentPage - 1) * RESULTS_PER_PAGE
  const endIndex = Math.min(startIndex + RESULTS_PER_PAGE, totalResults)
  const paginatedResults = results.slice(startIndex, endIndex)

  // Generate page buttons
  const pageButtons: { label: string; page: number }[] = []
  for (let i = 1; i <= totalPages; i++) {
    const start = (i - 1) * RESULTS_PER_PAGE + 1
    const end = Math.min(i * RESULTS_PER_PAGE, totalResults)
    pageButtons.push({ label: `${start}-${end}`, page: i })
  }

  return (
    <div className="container py-6">
      <Breadcrumbs items={[
        { label: "Statistikk", href: "/statistikk" },
        { label: "All-time" }
      ]} />
      <h1 className="mt-4 mb-4">All-time lister</h1>

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

          {/* Venue filter (indoor/outdoor) */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Bane</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Link
                  href={buildUrl({ venue: "outdoor" })}
                  className={`flex-1 rounded px-3 py-2 text-center text-sm font-medium ${
                    venue === "outdoor"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted hover:bg-muted/80"
                  }`}
                >
                  Ute
                </Link>
                <Link
                  href={buildUrl({ venue: "indoor" })}
                  className={`flex-1 rounded px-3 py-2 text-center text-sm font-medium ${
                    venue === "indoor"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted hover:bg-muted/80"
                  }`}
                >
                  Inne
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
                {selectedEvent?.name ?? "Velg øvelse"} (All-time)
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                {genderLabel} · {ageLabel} · {venueLabel} · {totalResults} utøvere totalt
              </p>
            </CardHeader>
            <CardContent className="p-0">
              {paginatedResults.length > 0 ? (
                <>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b bg-muted/50">
                          <th className="px-2 py-2 text-left text-sm font-medium w-10">#</th>
                          <th className="px-2 py-2 text-left text-sm font-medium">Resultat</th>
                          <th className="px-2 py-2 text-left text-sm font-medium">Utøver</th>
                          <th className="px-2 py-2 text-left text-sm font-medium w-12">Født</th>
                          <th className="hidden px-2 py-2 text-left text-sm font-medium md:table-cell">Klubb</th>
                          <th className="hidden px-2 py-2 text-left text-sm font-medium lg:table-cell">Stevne</th>
                          <th className="hidden px-2 py-2 text-left text-sm font-medium lg:table-cell whitespace-nowrap w-24">Dato</th>
                        </tr>
                      </thead>
                      <tbody>
                        {paginatedResults.map((result, index) => (
                          <tr key={result.id} className="border-b last:border-0 hover:bg-muted/30">
                            <td className="px-2 py-1.5 text-sm text-muted-foreground">{startIndex + index + 1}</td>
                            <td className="px-2 py-1.5">
                              <span className="perf-value">{formatPerformance(result.performance, result.result_type)}</span>
                              {result.wind !== null && (
                                <span className="ml-1 text-xs text-muted-foreground">
                                  ({result.wind > 0 ? "+" : ""}{result.wind})
                                </span>
                              )}
                              {result.is_national_record && (
                                <span className="ml-1 rounded bg-yellow-100 px-1 py-0.5 text-xs font-medium text-yellow-800">
                                  NR
                                </span>
                              )}
                            </td>
                            <td className="px-2 py-1.5">
                              <Link
                                href={`/utover/${result.athlete_id}`}
                                className="font-medium text-primary hover:underline"
                              >
                                {result.athlete_name}
                              </Link>
                            </td>
                            <td className="px-2 py-1.5 text-sm text-muted-foreground">
                              {getBirthYear(result.birth_date) ?? "-"}
                            </td>
                            <td className="hidden px-2 py-1.5 text-sm md:table-cell truncate max-w-[120px]">
                              {result.club_name ?? "-"}
                            </td>
                            <td className="hidden px-2 py-1.5 text-sm lg:table-cell truncate max-w-[180px]">
                              <Link
                                href={`/stevner/${result.meet_id}`}
                                className="hover:text-primary hover:underline"
                              >
                                {result.meet_name}
                              </Link>
                            </td>
                            <td className="hidden px-2 py-1.5 text-sm text-muted-foreground lg:table-cell whitespace-nowrap">
                              {result.date
                                ? new Date(result.date).toLocaleDateString("no-NO", {
                                    day: "2-digit",
                                    month: "2-digit",
                                    year: "numeric",
                                  })
                                : "-"}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {/* Pagination */}
                  {totalPages > 1 && (
                    <div className="flex flex-wrap items-center justify-center gap-2 border-t p-4">
                      <span className="text-sm text-muted-foreground mr-2">
                        Viser {startIndex + 1}-{endIndex} av {totalResults}
                      </span>
                      {pageButtons.map((btn) => (
                        <Link
                          key={btn.page}
                          href={buildUrl({ page: btn.page })}
                          className={`rounded px-3 py-1.5 text-sm font-medium ${
                            currentPage === btn.page
                              ? "bg-primary text-primary-foreground"
                              : "bg-muted hover:bg-muted/80"
                          }`}
                        >
                          {btn.label}
                        </Link>
                      ))}
                    </div>
                  )}
                </>
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
