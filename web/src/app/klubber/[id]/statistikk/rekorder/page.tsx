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

/** Beste resultat per øvelse i én spørring (funksjonen klubbrekorder i
 *  basen). Før gikk det én spørring per øvelse, rundt 300, og siden brukte
 *  12 sekunder. Reglene ligger i funksjonen: håndtid ute i sprint og hekk,
 *  bare lovlig vind der vind teller. */
interface Rekord {
  event_id: string
  performance: string
  performance_value: number
  wind: number | null
  athlete_id: string
  athlete_name: string
  birth_date: string | null
  meet_id: string
  meet_city: string | null
  meet_name: string | null
  date: string
  result_type: string
}

async function getClubRecords(clubId: string, gender: string, age: string, venue: string): Promise<Map<string, Rekord>> {
  const supabase = await createClient()
  // Utelatte filtre sendes ikke med; funksjonen har null som standard.
  const aldersgrupper = age === "all" ? undefined : (AGE_GROUP_MAPPINGS[age] ?? [age])
  const inne = venue === "indoor" ? true : venue === "outdoor" ? false : undefined
  const { data, error } = await supabase.rpc("klubbrekorder", {
    p_klubb: clubId, p_kjonn: gender, p_aldersgrupper: aldersgrupper, p_inne: inne,
  })
  if (error) console.error("klubbrekorder:", error.message)
  return new Map(((data ?? []) as Rekord[]).map((r) => [r.event_id, r]))
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const club = await getClub(id)

  if (!club) {
    return { title: "Klubb ikke funnet" }
  }

  return {
    title: `${club.name} - Klubbrekorder`,
    description: `Beste resultater per øvelse for ${club.name}`,
  }
}

export default async function ClubRecordsPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>
  searchParams: Promise<{ gender?: string; age?: string; venue?: string }>
}) {
  const { id } = await params
  const { gender = "M", age = "Senior", venue = "outdoor" } = await searchParams

  const club = await getClub(id)

  if (!club) {
    notFound()
  }

  const events = await getEvents()

  const genderLabel = gender === "M" ? "Menn" : "Kvinner"
  const ageLabel = age === "all" ? "Alle aldersgrupper" : AGE_GROUPS.find(a => a.value === age)?.label ?? age
  const venueLabel = venue === "indoor" ? "Innendørs" : venue === "outdoor" ? "Utendørs" : "Alle"

  const buildUrl = (overrides: { gender?: string; age?: string; venue?: string }) => {
    const params = new URLSearchParams()
    const genderParam = overrides.gender ?? gender
    const ageParam = overrides.age ?? age
    const venueParam = overrides.venue ?? venue
    if (genderParam) params.set("gender", genderParam)
    if (ageParam) params.set("age", ageParam)
    if (venueParam) params.set("venue", venueParam)
    return `/klubber/${id}/statistikk/rekorder?${params.toString()}`
  }

  const rekorder = await getClubRecords(id, gender, age, venue)
  const validRecords = events
    .map((event) => ({ event, record: rekorder.get(event.id) ?? null }))
    .filter((r) => r.record !== null)

  return (
    <div className="container py-6">
      <Breadcrumbs items={[
        { label: "Klubber", href: "/klubber" },
        { label: club.name, href: `/klubber/${id}` },
        { label: "Statistikk", href: `/klubber/${id}/statistikk` },
        { label: "Klubbrekorder" }
      ]} />
      <h1 className="mt-4 mb-4">{club.name} - Klubbrekorder</h1>

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
        </div>

        {/* Main content */}
        <div className="lg:col-span-4">
          <Card>
            <CardHeader>
              <CardTitle>Beste resultat per øvelse</CardTitle>
              <p className="text-sm text-muted-foreground">
                {genderLabel} · {ageLabel} · {venueLabel}
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
                    {validRecords.map(({ event, record }) => (
                      <tr key={event.id} className="border-b last:border-0 hover:bg-muted/30">
                        <td className="px-3 py-2">
                          <Link
                            href={`/klubber/${id}/statistikk/all-time?event=${event.id}&gender=${gender}&age=${age}&venue=${venue}`}
                            className="font-medium hover:text-primary hover:underline"
                          >
                            {event.name}
                          </Link>
                        </td>
                        <td className="px-3 py-2">
                          <span className="perf-value">{formatPerformance(record!.performance, record!.result_type)}</span>
                          {record!.wind !== null && (
                            <span className="ml-1 text-xs text-muted-foreground">
                              ({record!.wind > 0 ? "+" : ""}{record!.wind})
                            </span>
                          )}
                        </td>
                        <td className="px-3 py-2">
                          <Link
                            href={`/utover/${record!.athlete_id}`}
                            className="text-primary hover:underline"
                          >
                            {record!.athlete_name}
                          </Link>
                        </td>
                        <td className="px-3 py-2 text-sm text-muted-foreground">
                          {getBirthYear(record!.birth_date) ?? "-"}
                        </td>
                        <td className="hidden px-3 py-2 text-sm md:table-cell">
                          <Link
                            href={`/stevner/${record!.meet_id}`}
                            className="hover:text-primary hover:underline"
                          >
                            {record!.meet_city}
                          </Link>
                        </td>
                        <td className="hidden px-3 py-2 text-sm text-muted-foreground lg:table-cell">
                          {record!.date
                            ? new Date(record!.date).toLocaleDateString("no-NO", {
                                day: "numeric",
                                month: "short",
                                year: "numeric",
                              })
                            : "-"}
                        </td>
                      </tr>
                    ))}
                    {validRecords.length === 0 && (
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
        </div>
      </div>
    </div>
  )
}
