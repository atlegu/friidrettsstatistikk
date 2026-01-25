import Link from "next/link"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowRight } from "lucide-react"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"
import { formatPerformance } from "@/lib/format-performance"
import { getBirthYear } from "@/lib/date-utils"

export const metadata = {
  title: "Statistikk",
  description: "Norsk friidrettsstatistikk - årslister, all-time lister og rekorder",
}

const currentYear = new Date().getFullYear()
const years = Array.from({ length: 10 }, (_, i) => currentYear - i)

const AGE_GROUPS = [
  { value: "Senior", label: "Senior (15+)" },
  { value: "U23", label: "U23" },
  { value: "U20", label: "U20" },
  { value: "U18", label: "U18" },
  { value: "G/J15", label: "G/J15" },
  { value: "G/J14", label: "G/J14" },
  { value: "G/J13", label: "G/J13" },
] as const

const SENIOR_AGE_GROUPS = ["Senior", "U23", "U20", "U18", "G/J15"]
const SPRINT_EVENTS = ["60 meter", "100 meter", "200 meter"]

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

  if (ageGroup === "Senior") {
    query = query.in("age_group", SENIOR_AGE_GROUPS)
  } else if (ageGroup !== "all") {
    query = query.eq("age_group", ageGroup)
  }

  const isSprintEvent = SPRINT_EVENTS.includes(eventName)

  if (!isSprintEvent) {
    const { data } = await query
      .order("performance_value", { ascending })
      .limit(limit * 20)

    if (!data) return []

    const bestByAthlete = new Map<string, typeof data[0]>()
    for (const result of data) {
      if (!result.athlete_id) continue
      if (!bestByAthlete.has(result.athlete_id)) {
        bestByAthlete.set(result.athlete_id, result)
      }
    }
    return Array.from(bestByAthlete.values()).slice(0, limit)
  }

  const { data } = await query
    .order("performance_value", { ascending })
    .limit(limit * 50)

  if (!data) return []

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

export default async function StatistikkPage({
  searchParams,
}: {
  searchParams: Promise<{ event?: string; gender?: string; age?: string }>
}) {
  const { event: selectedEventId, gender = "M", age = "Senior" } = await searchParams

  const events = await getEvents()
  const selectedEvent = selectedEventId
    ? events.find((e) => e.id === selectedEventId)
    : events[0]

  const results = selectedEvent
    ? await getTopResults(currentYear, selectedEvent.id, selectedEvent.name, gender, age, selectedEvent.result_type ?? "time")
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
    return `/statistikk?${params.toString()}`
  }

  return (
    <div className="container py-6">
      <Breadcrumbs items={[{ label: "Statistikk" }]} />
      <h1 className="mt-4 mb-4">Statistikk</h1>

      {/* Navigation cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-8">
        {/* Annual lists */}
        <Card>
          <CardHeader>
            <CardTitle>Årslister</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4 text-sm text-muted-foreground">
              Beste resultater per år, fordelt på øvelser og aldersklasser
            </p>
            <div className="flex flex-wrap gap-2">
              {years.map((year) => (
                <Link
                  key={year}
                  href={`/statistikk/${year}`}
                  className="rounded bg-muted px-3 py-1 text-sm font-medium hover:bg-primary hover:text-primary-foreground"
                >
                  {year}
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* All-time */}
        <Link href="/statistikk/all-time">
          <Card className="h-full cursor-pointer transition-colors hover:bg-muted/50">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                All-time lister
                <ArrowRight className="h-4 w-4" />
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Historiske toppresultater gjennom alle tider i norsk friidrett
              </p>
            </CardContent>
          </Card>
        </Link>

        {/* Records */}
        <Link href="/statistikk/rekorder">
          <Card className="h-full cursor-pointer transition-colors hover:bg-muted/50">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Norske rekorder
                <ArrowRight className="h-4 w-4" />
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Offisielle norske rekorder i alle øvelser og aldersklasser
              </p>
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* Divider */}
      <hr className="mb-8 border-border" />

      {/* Current year list */}
      <h2 className="text-2xl font-bold mb-4">Årsliste {currentYear}</h2>

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
