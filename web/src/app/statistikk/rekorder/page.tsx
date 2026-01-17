import Link from "next/link"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export const metadata = {
  title: "Norske rekorder",
  description: "Beste registrerte resultater i norsk friidrett",
}

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

async function getEvents() {
  const supabase = await createClient()

  const { data } = await supabase
    .from("events")
    .select("*")
    .order("sort_order", { ascending: true })

  return data ?? []
}

async function getBestResult(eventId: string, gender: string, ageGroup: string, resultType: string) {
  const supabase = await createClient()

  // For time events, lower is better (ascending)
  // For distance, height, points - higher is better (descending)
  const ascending = resultType === "time"

  let query = supabase
    .from("results_full")
    .select("*")
    .eq("event_id", eventId)
    .eq("gender", gender)
    .not("performance_value", "is", null)

  if (ageGroup === "Senior") {
    // Senior includes all 15+ age groups
    query = query.in("age_group", SENIOR_AGE_GROUPS)
  } else if (ageGroup !== "all") {
    query = query.eq("age_group", ageGroup)
  }

  const { data } = await query
    .order("performance_value", { ascending })
    .limit(1)

  return data?.[0] ?? null
}

export default async function RekordsPage({
  searchParams,
}: {
  searchParams: Promise<{ gender?: string; age?: string }>
}) {
  const { gender = "M", age = "Senior" } = await searchParams
  const events = await getEvents()

  const genderLabel = gender === "M" ? "Menn" : "Kvinner"
  const ageLabel = age === "all" ? "Alle aldersgrupper" : AGE_GROUPS.find(a => a.value === age)?.label ?? age

  const buildUrl = (overrides: { gender?: string; age?: string }) => {
    const params = new URLSearchParams()
    const genderParam = overrides.gender ?? gender
    const ageParam = overrides.age ?? age
    if (genderParam) params.set("gender", genderParam)
    if (ageParam) params.set("age", ageParam)
    return `/statistikk/rekorder?${params.toString()}`
  }

  // Get best result for each event
  const recordsPromises = events.map(async (event) => {
    const best = await getBestResult(event.id, gender, age, event.result_type ?? "time")
    return {
      event,
      record: best,
    }
  })

  const records = await Promise.all(recordsPromises)
  const validRecords = records.filter((r) => r.record !== null)

  return (
    <div className="container py-8">
      <h1 className="mb-6 text-3xl font-bold">Beste resultater</h1>

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
        </div>

        {/* Main content */}
        <div className="lg:col-span-4">
          <Card>
            <CardHeader>
              <CardTitle>Beste registrerte resultater per øvelse</CardTitle>
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
                    {validRecords.map(({ event, record }) => (
                      <tr key={event.id} className="border-b last:border-0 hover:bg-muted/30">
                        <td className="px-3 py-2">
                          <Link
                            href={`/statistikk/all-time?event=${event.id}&gender=${gender}&age=${age}`}
                            className="font-medium hover:text-primary hover:underline"
                          >
                            {event.name}
                          </Link>
                        </td>
                        <td className="px-3 py-2">
                          <span className="font-mono font-medium">{record!.performance}</span>
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
                          {record!.birth_date ? new Date(record!.birth_date).getFullYear() : "-"}
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
