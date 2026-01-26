import Link from "next/link"
import { notFound } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { formatPerformance } from "@/lib/format-performance"
import { getBirthYear } from "@/lib/date-utils"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"

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

async function getClub(id: string) {
  const supabase = await createClient()

  const { data } = await supabase
    .from("clubs")
    .select("*")
    .eq("id", id)
    .single()

  return data
}

async function getEvents() {
  const supabase = await createClient()

  const { data } = await supabase
    .from("events")
    .select("*")
    .order("sort_order", { ascending: true })

  return data ?? []
}

async function getClubTopResults(
  clubId: string,
  year: number,
  eventId: string,
  eventName: string,
  gender: string,
  ageGroup: string,
  resultType: string,
  eventCategory: string,
  limit = 25
) {
  const supabase = await createClient()

  const ascending = resultType === "time"

  let query = supabase
    .from("results_full")
    .select("*")
    .eq("club_id", clubId)
    .eq("event_id", eventId)
    .eq("season_year", year)
    .eq("gender", gender)
    .eq("status", "OK")
    .not("performance_value", "is", null)
    .gt("performance_value", 0)

  // Handle composite age groups (Senior, U23, U20) and individual ages
  if (ageGroup !== "all") {
    const mappedGroups = AGE_GROUP_MAPPINGS[ageGroup]
    if (mappedGroups) {
      query = query.in("age_group", mappedGroups)
    } else {
      query = query.eq("age_group", ageGroup)
    }
  }

  // Exclude manual times for sprint and hurdles events
  if (MANUAL_TIME_CATEGORIES.includes(eventCategory)) {
    query = query.eq("is_manual_time", false)
  }

  // Exclude wind-assisted results for affected events
  if (WIND_AFFECTED_EVENTS.includes(eventName) || WIND_AFFECTED_CATEGORIES.includes(eventCategory)) {
    query = query.eq("is_wind_legal", true)
  }

  const { data } = await query.order("performance_value", { ascending })

  if (!data) return []

  // Filter to best result per athlete
  const bestByAthlete = new Map<string, typeof data[0]>()
  for (const result of data) {
    if (!result.athlete_id) continue
    const existing = bestByAthlete.get(result.athlete_id)
    if (!existing) {
      bestByAthlete.set(result.athlete_id, result)
    }
  }

  const results = Array.from(bestByAthlete.values())
  return results.slice(0, limit)
}

export async function generateMetadata({ params }: { params: Promise<{ id: string; year: string }> }) {
  const { id, year } = await params
  const club = await getClub(id)

  if (!club) {
    return { title: "Klubb ikke funnet" }
  }

  return {
    title: `${club.name} - Årsliste ${year}`,
    description: `Beste resultater for ${club.name} i ${year}`,
  }
}

export default async function ClubYearListPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string; year: string }>
  searchParams: Promise<{ event?: string; gender?: string; age?: string }>
}) {
  const { id, year } = await params
  const { event: selectedEventId, gender = "M", age = "Senior" } = await searchParams
  const yearNum = parseInt(year)

  const club = await getClub(id)

  if (!club) {
    notFound()
  }

  const events = await getEvents()
  const selectedEvent = selectedEventId
    ? events.find((e) => e.id === selectedEventId)
    : events[0]

  const results = selectedEvent
    ? await getClubTopResults(id, yearNum, selectedEvent.id, selectedEvent.name, gender, age, selectedEvent.result_type ?? "time", selectedEvent.category ?? "")
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
    return `/klubber/${id}/statistikk/${year}?${params.toString()}`
  }

  return (
    <div className="container py-6">
      <Breadcrumbs items={[
        { label: "Klubber", href: "/klubber" },
        { label: club.name, href: `/klubber/${id}` },
        { label: "Statistikk", href: `/klubber/${id}/statistikk` },
        { label: `Årsliste ${year}` }
      ]} />
      <h1 className="mt-4 mb-4">{club.name} - Årsliste {year}</h1>

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
