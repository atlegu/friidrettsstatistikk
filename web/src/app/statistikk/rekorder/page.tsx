import { Fragment } from "react"
import Link from "next/link"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { formatPerformance } from "@/lib/format-performance"
import { getBirthYear } from "@/lib/date-utils"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"

export const metadata = {
  title: "Norgesrekorder",
  description: "Norske rekorder og bestenoteringer i friidrett",
}

// Event categories for better organization
interface EventCategory {
  name: string
  events: string[]
}

// Official Norwegian record events - Senior
// Based on https://www.friidrett.no/siteassets/aktivitet/statistikk/rekorder/
const NORGESREKORDER_CATEGORIES: Record<string, EventCategory[]> = {
  M: [
    { name: "Løp - bane", events: ["100m", "200m", "400m", "800m", "1000m", "1500m", "1mile", "3000m", "5000m", "10000m", "20000m"] },
    { name: "Hekk / hinder", events: ["110mh_106_7cm", "200mh_76_2cm", "400mh_91_4cm", "3000mhinder_91_4cm"] },
    { name: "Hopp", events: ["hoyde", "stav", "lengde", "tresteg", "hoyde_ut", "lengde_ut"] },
    { name: "Kast", events: ["kule_7_26kg", "diskos_2kg", "slegge_7_26kg", "spyd_800g"] },
    { name: "Mangekamp", events: ["5kamp", "10kamp"] },
    { name: "Stafett", events: ["4x100m", "4x400m"] },
    { name: "Kappgang", events: ["5000mg", "20kmg"] },
    { name: "Vei", events: ["3km", "5km", "10km", "halvmaraton", "maraton", "100km"] },
  ],
  F: [
    { name: "Løp - bane", events: ["100m", "200m", "400m", "800m", "1000m", "1500m", "1mile", "3000m", "5000m", "10000m"] },
    { name: "Hekk / hinder", events: ["100mh_84cm", "200mh_76_2cm", "400mh_76_2cm", "3000mhinder_76_2cm"] },
    { name: "Hopp", events: ["hoyde", "stav", "lengde", "tresteg", "hoyde_ut", "lengde_ut"] },
    { name: "Kast", events: ["kule_4kg", "diskos_1kg", "slegge_4kg", "spyd_600g"] },
    { name: "Mangekamp", events: ["5kamp", "7kamp"] },
    { name: "Stafett", events: ["4x100m", "4x400m"] },
    { name: "Kappgang", events: ["3000mg"] },
    { name: "Vei", events: ["3km", "5km", "10km", "halvmaraton", "maraton", "100km"] },
  ],
}

// Best performances (bestenoteringer) - events without official records
const BESTENOTERINGER_CATEGORIES: Record<string, EventCategory[]> = {
  M: [
    { name: "Løp - bane", events: ["60m", "300m", "600m", "2000m", "2miles", "25000m"] },
    { name: "Hekk / hinder", events: ["60mh_106_7cm", "300mh_91_4cm", "2000mhinder_91_4cm"] },
    { name: "Kast", events: ["spyd_800g_old", "vektkast_1588kg", "vektkast_1134kg", "vektkast_726kg"] },
  ],
  F: [
    { name: "Løp - bane", events: ["60m", "300m", "600m", "2000m"] },
    { name: "Hekk / hinder", events: ["60mh_84cm", "300mh_76_2cm", "2000mhinder_76_2cm"] },
    { name: "Kast", events: ["vektkast_908kg", "vektkast_545kg", "vektkast40kg"] },
    { name: "Kappgang", events: ["10000mg", "20kmg"] },
  ],
}

// Helper to flatten categories to event codes
function flattenCategories(categories: EventCategory[]): string[] {
  return categories.flatMap(cat => cat.events)
}

// Age groups included in "Senior" filter (15 years and older)
const SENIOR_AGE_GROUPS = ["15", "16", "17", "18-19", "20-22", "Senior"]

// Junior age groups (15-19)
const JUNIOR_AGE_GROUPS = ["15", "16", "17", "18-19"]

// Events where manual times should be excluded
const SPRINT_EVENT_CODES = ["60m", "80m", "100m", "150m", "200m"]
const HURDLE_EVENT_PREFIXES = ["60mh", "80mh", "100mh", "110mh", "200mh"]

// Events where wind affects validity
const WIND_AFFECTED_EVENT_CODES = ["60m", "80m", "100m", "150m", "200m", "lengde", "tresteg"]
const WIND_AFFECTED_EVENT_PREFIXES = ["60mh", "80mh", "100mh", "110mh", "200mh"]

const AGE_CATEGORIES = [
  { value: "Senior", label: "Senior" },
  { value: "Junior", label: "Junior (U20)" },
] as const

async function getEventsByIds(eventCodes: string[]) {
  const supabase = await createClient()

  const { data } = await supabase
    .from("events")
    .select("*")
    .in("code", eventCodes)
    .order("sort_order", { ascending: true })

  return data ?? []
}

async function getBestResult(eventId: string, eventCode: string, gender: string, ageCategory: string, resultType: string) {
  const supabase = await createClient()

  // For time events, lower is better (ascending)
  // For distance, height, points - higher is better (descending)
  const ascending = resultType === "time"

  let query = supabase
    .from("results_full")
    .select("*")
    .eq("event_id", eventId)
    .eq("gender", gender)
    .eq("status", "OK")
    .not("performance_value", "is", null)
    .gt("performance_value", 0)

  if (ageCategory === "Senior") {
    query = query.in("age_group", SENIOR_AGE_GROUPS)
  } else if (ageCategory === "Junior") {
    query = query.in("age_group", JUNIOR_AGE_GROUPS)
  }

  // Check if manual times should be excluded (sprints and hurdles)
  const isSprintEvent = SPRINT_EVENT_CODES.includes(eventCode)
  const isHurdleEvent = HURDLE_EVENT_PREFIXES.some(prefix => eventCode.startsWith(prefix))
  if (isSprintEvent || isHurdleEvent) {
    query = query.eq("is_manual_time", false)
  }

  // Check if wind-assisted results should be excluded
  const isWindAffected = WIND_AFFECTED_EVENT_CODES.includes(eventCode) ||
    WIND_AFFECTED_EVENT_PREFIXES.some(prefix => eventCode.startsWith(prefix))
  if (isWindAffected) {
    query = query.eq("is_wind_legal", true)
  }

  const { data } = await query
    .order("performance_value", { ascending })
    .limit(1)

  return data?.[0] ?? null
}

interface RecordRowProps {
  event: { id: string; name: string; code: string }
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  record: any
  gender: string
  age: string
}

function RecordRow({ event, record, gender, age }: RecordRowProps) {
  if (!record) return null

  return (
    <tr className="border-b last:border-0 hover:bg-muted/30">
      <td className="px-3 py-2">
        <Link
          href={`/statistikk/all-time?event=${event.id}&gender=${gender}&age=${age}`}
          className="font-medium hover:text-primary hover:underline"
        >
          {event.name}
        </Link>
      </td>
      <td className="px-3 py-2">
        <span className="perf-value">{formatPerformance(record.performance, record.result_type)}</span>
        {record.wind !== null && (
          <span className="ml-1 text-xs text-muted-foreground">
            ({record.wind > 0 ? "+" : ""}{record.wind})
          </span>
        )}
      </td>
      <td className="px-3 py-2">
        <Link
          href={`/utover/${record.athlete_id}`}
          className="text-primary hover:underline"
        >
          {record.athlete_name}
        </Link>
      </td>
      <td className="px-3 py-2 text-sm text-muted-foreground">
        {getBirthYear(record.birth_date) ?? "-"}
      </td>
      <td className="hidden px-3 py-2 text-sm md:table-cell">
        <Link
          href={`/stevner/${record.meet_id}`}
          className="hover:text-primary hover:underline"
        >
          {record.meet_city}
        </Link>
      </td>
      <td className="hidden px-3 py-2 text-sm text-muted-foreground lg:table-cell">
        {record.date
          ? new Date(record.date).toLocaleDateString("no-NO", {
              day: "numeric",
              month: "short",
              year: "numeric",
            })
          : "-"}
      </td>
    </tr>
  )
}

export default async function RekordsPage({
  searchParams,
}: {
  searchParams: Promise<{ gender?: string; age?: string }>
}) {
  const { gender = "M", age = "Senior" } = await searchParams

  const genderLabel = gender === "M" ? "Menn" : "Kvinner"
  const ageLabel = AGE_CATEGORIES.find(a => a.value === age)?.label ?? age

  const buildUrl = (overrides: { gender?: string; age?: string }) => {
    const params = new URLSearchParams()
    const genderParam = overrides.gender ?? gender
    const ageParam = overrides.age ?? age
    if (genderParam) params.set("gender", genderParam)
    if (ageParam) params.set("age", ageParam)
    return `/statistikk/rekorder?${params.toString()}`
  }

  // Get events for the selected gender
  const genderKey = gender as "M" | "F"
  const recordCategories = NORGESREKORDER_CATEGORIES[genderKey] ?? NORGESREKORDER_CATEGORIES.M
  const bestCategories = BESTENOTERINGER_CATEGORIES[genderKey] ?? BESTENOTERINGER_CATEGORIES.M

  const recordEventCodes = flattenCategories(recordCategories)
  const bestEventCodes = flattenCategories(bestCategories)

  const [recordEvents, bestEvents] = await Promise.all([
    getEventsByIds(recordEventCodes),
    getEventsByIds(bestEventCodes),
  ])

  // Get best results for each event
  const recordPromises = recordEvents.map(async (event) => {
    const best = await getBestResult(event.id, event.code, gender, age, event.result_type ?? "time")
    return { event, record: best }
  })

  const bestPromises = bestEvents.map(async (event) => {
    const best = await getBestResult(event.id, event.code, gender, age, event.result_type ?? "time")
    return { event, record: best }
  })

  const [records, bests] = await Promise.all([
    Promise.all(recordPromises),
    Promise.all(bestPromises),
  ])

  // Create lookup for records by event code
  const recordsByCode = new Map(records.map(r => [r.event.code, r]))
  const bestsByCode = new Map(bests.map(r => [r.event.code, r]))

  // Build categorized results
  const categorizedRecords = recordCategories.map(category => ({
    name: category.name,
    results: category.events
      .map(code => recordsByCode.get(code))
      .filter((r): r is { event: typeof recordEvents[0], record: NonNullable<typeof records[0]["record"]> } =>
        r !== undefined && r.record !== null
      )
  })).filter(cat => cat.results.length > 0)

  const categorizedBests = bestCategories.map(category => ({
    name: category.name,
    results: category.events
      .map(code => bestsByCode.get(code))
      .filter((r): r is { event: typeof bestEvents[0], record: NonNullable<typeof bests[0]["record"]> } =>
        r !== undefined && r.record !== null
      )
  })).filter(cat => cat.results.length > 0)

  return (
    <div className="container py-6">
      <Breadcrumbs items={[
        { label: "Statistikk", href: "/statistikk" },
        { label: "Norgesrekorder" }
      ]} />
      <h1 className="mt-4 mb-4">Norgesrekorder</h1>

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

          {/* Age category filter */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Klasse</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-1">
                {AGE_CATEGORIES.map((ageCategory) => (
                  <Link
                    key={ageCategory.value}
                    href={buildUrl({ age: ageCategory.value })}
                    className={`block rounded px-2 py-1 text-sm ${
                      age === ageCategory.value
                        ? "bg-primary text-primary-foreground"
                        : "hover:bg-muted"
                    }`}
                  >
                    {ageCategory.label}
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main content */}
        <div className="lg:col-span-4 space-y-8">
          {/* Norgesrekorder */}
          <Card>
            <CardHeader>
              <CardTitle>Norgesrekorder</CardTitle>
              <p className="text-sm text-muted-foreground">
                {genderLabel} · {ageLabel}
              </p>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="px-3 py-2 text-left text-sm font-medium">Øvelse</th>
                      <th className="px-3 py-2 text-left text-sm font-medium">Resultat</th>
                      <th className="px-3 py-2 text-left text-sm font-medium">Utøver</th>
                      <th className="px-3 py-2 text-left text-sm font-medium w-14">Født</th>
                      <th className="hidden px-3 py-2 text-left text-sm font-medium md:table-cell">Sted</th>
                      <th className="hidden px-3 py-2 text-left text-sm font-medium lg:table-cell">Dato</th>
                    </tr>
                  </thead>
                  <tbody>
                    {categorizedRecords.map((category) => (
                      <Fragment key={category.name}>
                        <tr className="bg-muted/30">
                          <td colSpan={6} className="px-3 py-2 text-sm font-semibold text-muted-foreground">
                            {category.name}
                          </td>
                        </tr>
                        {category.results.map(({ event, record }) => (
                          <RecordRow
                            key={event.id}
                            event={event}
                            record={record}
                            gender={gender}
                            age={age}
                          />
                        ))}
                      </Fragment>
                    ))}
                    {categorizedRecords.length === 0 && (
                      <tr>
                        <td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">
                          Ingen resultater funnet
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Bestenoteringer */}
          {categorizedBests.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Bestenoteringer</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Øvelser uten offisielle norgesrekorder · {genderLabel} · {ageLabel}
                </p>
              </CardHeader>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-3 py-2 text-left text-sm font-medium">Øvelse</th>
                        <th className="px-3 py-2 text-left text-sm font-medium">Resultat</th>
                        <th className="px-3 py-2 text-left text-sm font-medium">Utøver</th>
                        <th className="px-3 py-2 text-left text-sm font-medium w-14">Født</th>
                        <th className="hidden px-3 py-2 text-left text-sm font-medium md:table-cell">Sted</th>
                        <th className="hidden px-3 py-2 text-left text-sm font-medium lg:table-cell">Dato</th>
                      </tr>
                    </thead>
                    <tbody>
                      {categorizedBests.map((category) => (
                        <Fragment key={category.name}>
                          <tr className="bg-muted/30">
                            <td colSpan={6} className="px-3 py-2 text-sm font-semibold text-muted-foreground">
                              {category.name}
                            </td>
                          </tr>
                          {category.results.map(({ event, record }) => (
                            <RecordRow
                              key={event.id}
                              event={event}
                              record={record}
                              gender={gender}
                              age={age}
                            />
                          ))}
                        </Fragment>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
