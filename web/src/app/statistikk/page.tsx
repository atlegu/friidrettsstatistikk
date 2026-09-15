import Link from "next/link"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowRight } from "lucide-react"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"
import { erVindpaavirket } from "@/lib/vind"
import { AarslisteTabell } from "@/components/statistikk/AarslisteTabell"

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

// Age group mappings for composite categories
const AGE_GROUP_MAPPINGS: Record<string, string[]> = {
  "Senior": ["15", "16", "17", "18-19", "20-22", "Senior"],
  "U23": ["15", "16", "17", "18-19", "20-22"],
  "U20": ["15", "16", "17", "18-19"],
  "U18": ["15", "16", "17"],
  "G/J15": ["15"],
  "G/J14": ["14"],
  "G/J13": ["13"],
}

// Events where manual times should be excluded (sprint and hurdles)
const MANUAL_TIME_CATEGORIES = ["sprint", "hurdles"]


// Determine default venue based on current date
// Indoor: December 1 - March 31, Outdoor: April 1 - November 30
function getDefaultVenue(): "indoor" | "outdoor" {
  const month = new Date().getMonth() + 1 // 1-12
  return (month >= 4 && month <= 11) ? "outdoor" : "indoor"
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

  // Handle composite age groups
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

export default async function StatistikkPage({
  searchParams,
}: {
  searchParams: Promise<{ event?: string; gender?: string; age?: string; venue?: string }>
}) {
  const params = await searchParams
  const { event: selectedEventId, gender = "M", age = "Senior" } = params
  const venue = params.venue ?? getDefaultVenue()

  const events = await getEvents()
  const selectedEvent = selectedEventId
    ? events.find((e) => e.id === selectedEventId)
    : events[0]

  const results = selectedEvent
    ? await getTopResults(
        currentYear,
        selectedEvent.id,
        selectedEvent.code ?? "",
        gender,
        age,
        selectedEvent.result_type ?? "time",
        selectedEvent.category ?? "",
        venue
      )
    : []

  // Resultater uten vindmåling, i egen liste under den vanlige. Bare for
  // vindpåvirkede øvelser, og ikke når lista er innendørs.
  const ukjentVind =
    selectedEvent && erVindpaavirket(selectedEvent.code) && venue !== "indoor"
      ? await getTopResults(
          currentYear, selectedEvent.id, selectedEvent.code ?? "", gender, age,
          selectedEvent.result_type ?? "time", selectedEvent.category ?? "", venue, "ukjent"
        )
      : []

  const genderLabel = gender === "M" ? "Menn" : "Kvinner"
  const ageLabel = age === "all" ? "Alle aldersgrupper" : AGE_GROUPS.find(a => a.value === age)?.label ?? age
  const venueLabel = venue === "indoor" ? "Innendørs" : "Utendørs"

  const buildUrl = (overrides: { event?: string; gender?: string; age?: string; venue?: string }) => {
    const params = new URLSearchParams()
    const eventParam = overrides.event ?? selectedEvent?.id
    const genderParam = overrides.gender ?? gender
    const ageParam = overrides.age ?? age
    const venueParam = overrides.venue ?? venue
    if (eventParam) params.set("event", eventParam)
    if (genderParam) params.set("gender", genderParam)
    if (ageParam) params.set("age", ageParam)
    if (venueParam) params.set("venue", venueParam)
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
                {selectedEvent?.name ?? "Velg øvelse"}
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                {genderLabel} · {ageLabel} · {venueLabel}
              </p>
            </CardHeader>
            <CardContent className="p-0">
              {results.length > 0 ? (
                <AarslisteTabell rader={results} />
              ) : (
                <p className="p-4 text-center text-muted-foreground">
                  {selectedEvent
                    ? "Ingen resultater funnet for denne øvelsen"
                    : "Velg en øvelse fra listen til venstre"}
                </p>
              )}
            </CardContent>
          </Card>

          {ukjentVind.length > 0 && (
            <Card className="mt-6">
              <CardHeader>
                <CardTitle className="text-base">Ukjent vind</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Resultater fra stevner uten vindmåling. De kan ikke godkjennes
                  til lista over, men er reelle resultater. Beste per utøver.
                </p>
              </CardHeader>
              <CardContent className="p-0">
                <AarslisteTabell rader={ukjentVind} />
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
