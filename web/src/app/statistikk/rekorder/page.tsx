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

// Official Norwegian OUTDOOR record events - Senior
// Based on https://www.friidrett.no/siteassets/aktivitet/statistikk/rekorder/
const NORGESREKORDER_OUTDOOR: Record<string, EventCategory[]> = {
  M: [
    { name: "Løp - sprint", events: ["100m", "200m", "400m"] },
    { name: "Løp - mellomdistanse", events: ["800m", "1000m", "1500m", "1mile"] },
    { name: "Løp - langdistanse", events: ["3000m", "5000m", "10000m", "20000m", "1time"] },
    { name: "Hekk", events: ["110mh_106_7cm", "200mh_76_2cm", "400mh_91_4cm"] },
    { name: "Hinder", events: ["3000mhinder_91_4cm"] },
    { name: "Kappgang", events: ["5000mg", "20kmg", "30kmg", "50kmg"] },
    { name: "Stafett", events: ["4x100m", "4x200m", "4x400m", "4x800m", "4x1500m", "1000mstafett"] },
    { name: "Hopp", events: ["hoyde", "stav", "lengde", "tresteg"] },
    { name: "Kast", events: ["kule_7_26kg", "diskos_2kg", "slegge_726kg/1215cm", "spyd_800g"] },
    { name: "Mangekamp", events: ["5kamp", "10kamp"] },
    // Vei tas inn igjen med det historiske veimaterialet (fase 3). Basen har
    // ikke rekordene fra før 2013, og en «rekord» fra 2014 ville vært feil.
  ],
  F: [
    { name: "Løp - sprint", events: ["100m", "200m", "400m"] },
    { name: "Løp - mellomdistanse", events: ["800m", "1000m", "1500m", "1mile"] },
    { name: "Løp - langdistanse", events: ["3000m", "5000m", "10000m"] },
    { name: "Hekk", events: ["100mh_84cm", "200mh_76_2cm", "400mh_76_2cm"] },
    { name: "Hinder", events: ["3000mhinder_76_2cm"] },
    { name: "Kappgang", events: ["3000mg", "5000mg", "10000mg", "20kmg"] },
    { name: "Stafett", events: ["4x100m", "4x200m", "4x400m", "4x800m", "1000mstafett"] },
    { name: "Hopp", events: ["hoyde", "stav", "lengde", "tresteg"] },
    { name: "Kast", events: ["kule_4kg", "diskos_1kg", "slegge_40kg/1195cm", "spyd_600g"] },
    { name: "Mangekamp", events: ["5kamp", "7kamp"] },
    // Vei tas inn igjen med det historiske veimaterialet (fase 3). Basen har
    // ikke rekordene fra før 2013, og en «rekord» fra 2014 ville vært feil.
  ],
}

// Official Norwegian INDOOR record events - Senior
// Based on https://www.friidrett.no/siteassets/aktivitet/statistikk/rekorder/norske-rekorder-menn-senior-innendors.htm
const NORGESREKORDER_INDOOR: Record<string, EventCategory[]> = {
  M: [
    { name: "Løp", events: ["60m", "200m", "400m", "800m", "1000m", "1500m", "1mile", "3000m", "5000m"] },
    { name: "Hekk", events: ["60mh_106_7cm"] },
    { name: "Hopp", events: ["hoyde", "hoyde_ut", "stav", "lengde", "lengde_ut", "tresteg"] },
    { name: "Kast", events: ["kule_7_26kg"] },
    { name: "Kappgang", events: ["5000mg"] },
    { name: "Mangekamp", events: ["7kamp"] },
    { name: "Stafett", events: ["4x200m", "4x400m", "4x800m"] },
  ],
  F: [
    { name: "Løp", events: ["60m", "200m", "400m", "800m", "1000m", "1500m", "1mile", "3000m", "5000m"] },
    { name: "Hekk", events: ["60mh_84cm"] },
    { name: "Hopp", events: ["hoyde", "hoyde_ut", "stav", "lengde", "lengde_ut", "tresteg"] },
    { name: "Kast", events: ["kule_4kg"] },
    { name: "Kappgang", events: ["3000mg"] },
    { name: "Mangekamp", events: ["5kamp"] },
    { name: "Stafett", events: ["4x200m", "4x400m", "4x800m"] },
  ],
}

// Best performances (bestenoteringer) - events without official records - OUTDOOR
const BESTENOTERINGER_OUTDOOR: Record<string, EventCategory[]> = {
  M: [
    { name: "Løp - bane", events: ["300m", "600m", "2000m", "2miles", "25000m"] },
    { name: "Hekk / hinder", events: ["300mh_91_4cm", "2000mhinder_91_4cm"] },
    { name: "Vei", events: ["15kmvei", "20kmvei", "24timer"] },
  ],
  F: [
    { name: "Løp - bane", events: ["300m", "600m", "2000m"] },
    { name: "Hekk / hinder", events: ["300mh_76_2cm", "2000mhinder_76_2cm"] },
    { name: "Kappgang", events: ["50kmg"] },
    { name: "Vei", events: ["15kmvei", "24timer"] },
  ],
}

// Best performances (bestenoteringer) - INDOOR
const BESTENOTERINGER_INDOOR: Record<string, EventCategory[]> = {
  M: [
    { name: "Løp", events: ["100m", "300m", "600m"] },
    { name: "Hekk", events: ["110mh_106_7cm"] },
  ],
  F: [
    { name: "Løp", events: ["100m", "300m", "600m"] },
    { name: "Hekk", events: ["100mh_84cm", "300mh_76_2cm"] },
    { name: "Kast", events: ["vektkast_908kg", "spyd_600g"] },
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



// Events with minimum date requirements (new implement specifications)
// Women's javelin: new specification introduced 1999-04-01
const EVENT_MIN_DATE: Record<string, Record<string, string>> = {
  F: { "spyd_600g": "1999-04-01" },
}

const AGE_CATEGORIES = [
  { value: "Senior", label: "Senior" },
  { value: "Junior", label: "Junior (U20)" },
] as const

const VENUE_OPTIONS = [
  { value: "outdoor", label: "Utendørs" },
  { value: "indoor", label: "Innendørs" },
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

/** Beste resultat per øvelse i ett kall (funksjonen norgesrekorder i basen).
 *  Før gikk det én spørring per øvelse, 60–100 stykker, og en øvelse som
 *  feilet forsvant stille fra listen. Reglene ligger i funksjonen: håndtid
 *  ute i sprint og hekk, lovlig vind der vind teller, aldersgruppe og bane. */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function getBestResults(events: { id: string; code: string }[], gender: string, ageCategory: string, venue: string, minDates: Record<string, string>): Promise<Map<string, any>> {
  if (events.length === 0) return new Map()
  const supabase = await createClient()
  const aldersgrupper = ageCategory === "Senior" ? SENIOR_AGE_GROUPS : ageCategory === "Junior" ? JUNIOR_AGE_GROUPS : undefined
  const { data, error } = await supabase.rpc("norgesrekorder", {
    p_event_ids: events.map((e) => e.id),
    p_kjonn: gender,
    p_aldersgrupper: aldersgrupper,
    p_inne: venue === "indoor",
    p_min_dato: Object.keys(minDates).length ? minDates : undefined,
  })
  if (error) console.error("norgesrekorder:", error.message)
  return new Map((data ?? []).map((r) => [r.event_id, r]))
}

interface RecordRowProps {
  event: { id: string; name: string; code: string }
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  record: any
  gender: string
  age: string
  venue: string
}

function RecordRow({ event, record, gender, age, venue }: RecordRowProps) {
  if (!record) return null

  return (
    <tr className="border-b last:border-0 hover:bg-muted/30">
      <td className="px-3 py-2">
        <Link
          href={`/statistikk/all-time?event=${event.id}&gender=${gender}&age=${age}&venue=${venue}`}
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
  searchParams: Promise<{ gender?: string; age?: string; venue?: string }>
}) {
  const { gender = "M", age = "Senior", venue = "outdoor" } = await searchParams

  const genderLabel = gender === "M" ? "Menn" : "Kvinner"
  const ageLabel = AGE_CATEGORIES.find(a => a.value === age)?.label ?? age
  const venueLabel = venue === "indoor" ? "Innendørs" : "Utendørs"

  const buildUrl = (overrides: { gender?: string; age?: string; venue?: string }) => {
    const params = new URLSearchParams()
    const genderParam = overrides.gender ?? gender
    const ageParam = overrides.age ?? age
    const venueParam = overrides.venue ?? venue
    if (genderParam) params.set("gender", genderParam)
    if (ageParam) params.set("age", ageParam)
    if (venueParam) params.set("venue", venueParam)
    return `/statistikk/rekorder?${params.toString()}`
  }

  // Get events for the selected gender and venue
  const genderKey = gender as "M" | "F"
  const recordCategories = venue === "indoor"
    ? (NORGESREKORDER_INDOOR[genderKey] ?? NORGESREKORDER_INDOOR.M)
    : (NORGESREKORDER_OUTDOOR[genderKey] ?? NORGESREKORDER_OUTDOOR.M)
  const bestCategories = venue === "indoor"
    ? (BESTENOTERINGER_INDOOR[genderKey] ?? BESTENOTERINGER_INDOOR.M)
    : (BESTENOTERINGER_OUTDOOR[genderKey] ?? BESTENOTERINGER_OUTDOOR.M)

  const recordEventCodes = flattenCategories(recordCategories)
  const bestEventCodes = flattenCategories(bestCategories)

  const [recordEvents, bestEvents] = await Promise.all([
    getEventsByIds(recordEventCodes),
    getEventsByIds(bestEventCodes),
  ])

  // Beste resultat per øvelse, ett kall per liste
  const minDatesForGender = EVENT_MIN_DATE[gender] ?? {}
  const [recordMap, bestMap] = await Promise.all([
    getBestResults(recordEvents, gender, age, venue, minDatesForGender),
    getBestResults(bestEvents, gender, age, venue, minDatesForGender),
  ])
  const records = recordEvents.map((event) => ({ event, record: recordMap.get(event.id) ?? null }))
  const bests = bestEvents.map((event) => ({ event, record: bestMap.get(event.id) ?? null }))

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
              <CardTitle>Norgesrekorder - {venueLabel}</CardTitle>
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
                            venue={venue}
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
                <CardTitle>Bestenoteringer - {venueLabel}</CardTitle>
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
                              venue={venue}
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
