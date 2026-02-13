import Link from "next/link"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Users, Trophy, Calendar, Building2, ArrowRight } from "lucide-react"
import { formatPerformance } from "@/lib/format-performance"
import {
  INDOOR_CHAMPIONSHIP_EVENTS,
  OUTDOOR_CHAMPIONSHIP_EVENTS,
  TIME_EVENT_CODES,
  getEventDisplayName,
} from "@/lib/event-config"

async function getStats() {
  const supabase = await createClient()

  const [athletesResult, clubsResult, resultsResult, meetsResult] = await Promise.all([
    supabase.from("athletes").select("id", { count: "exact", head: true }),
    supabase.from("clubs").select("id", { count: "exact", head: true }),
    supabase.from("results").select("id", { count: "exact", head: true }),
    supabase.from("meets").select("id", { count: "exact", head: true }),
  ])

  return {
    athletes: athletesResult.count ?? 0,
    clubs: clubsResult.count ?? 0,
    results: resultsResult.count ?? 0,
    meets: meetsResult.count ?? 0,
  }
}

async function getSeasonLeaders() {
  const supabase = await createClient()
  const month = new Date().getMonth() + 1
  const isIndoor = month >= 12 || month <= 3
  const currentYear = new Date().getFullYear()

  const championshipEvents = isIndoor ? INDOOR_CHAMPIONSHIP_EVENTS : OUTDOOR_CHAMPIONSHIP_EVENTS

  async function getLeadersForGender(gender: "M" | "F") {
    const eventCodes = championshipEvents[gender]

    const selectCols =
      "athlete_id, athlete_name, event_code, event_name, event_id, performance, performance_value, result_type, wind"

    // Query each event individually to guarantee we get the best result per event
    // (a combined query with .limit() misses long-distance events because their
    // performance_value is much higher than sprint events)
    const results = await Promise.all(
      eventCodes.map(async (code) => {
        const isTime = TIME_EVENT_CODES.has(code)
        const { data } = await supabase
          .from("results_full")
          .select(selectCols)
          .eq("event_code", code)
          .eq("season_year", currentYear)
          .eq("meet_indoor", isIndoor)
          .eq("gender", gender)
          .eq("status", "OK")
          .gt("performance_value", 0)
          .order("performance_value", { ascending: isTime })
          .limit(1)
        return data?.[0] ?? null
      })
    )

    return results.filter((r): r is NonNullable<typeof r> => r != null)
  }

  const [men, women] = await Promise.all([
    getLeadersForGender("M"),
    getLeadersForGender("F"),
  ])

  return { men, women, isIndoor, year: currentYear }
}

export default async function Home() {
  const [stats, seasonLeaders] = await Promise.all([getStats(), getSeasonLeaders()])

  const venueLabel = seasonLeaders.isIndoor ? "Innendørs" : "Utendørs"
  const venueParam = seasonLeaders.isIndoor ? "indoor" : "outdoor"

  return (
    <div className="container py-8 md:py-12">
      {/* Hero Section */}
      <section className="mb-12 text-center">
        <h1 className="mb-4 text-4xl font-bold tracking-tight md:text-5xl">
          Norsk Friidrettsstatistikk
        </h1>
        <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
          Komplett oversikt over norsk friidrett - fra rekrutt til veteran.
          Resultater, rekorder, utøverprofiler og stevnekalender.
        </p>
      </section>

      {/* Stats Cards */}
      <section className="mb-12 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Utøvere</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.athletes.toLocaleString("no-NO")}</div>
            <Link href="/utover" className="text-xs text-muted-foreground hover:text-primary">
              Se alle utøvere
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Klubber</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.clubs.toLocaleString("no-NO")}</div>
            <Link href="/klubber" className="text-xs text-muted-foreground hover:text-primary">
              Se alle klubber
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Resultater</CardTitle>
            <Trophy className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.results.toLocaleString("no-NO")}</div>
            <Link href="/statistikk/2025" className="text-xs text-muted-foreground hover:text-primary">
              Se årslister
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Stevner</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.meets.toLocaleString("no-NO")}</div>
            <Link href="/stevner" className="text-xs text-muted-foreground hover:text-primary">
              Se stevnekalender
            </Link>
          </CardContent>
        </Card>
      </section>

      {/* Quick Links */}
      <section className="mb-12">
        <h2 className="mb-6 text-2xl font-semibold">Utforsk statistikken</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Link href="/statistikk/2025">
            <Card className="cursor-pointer transition-colors hover:bg-muted/50">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Årslister 2025
                  <ArrowRight className="h-4 w-4" />
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Se årets beste resultater fordelt på øvelser og aldersklasser
                </p>
              </CardContent>
            </Card>
          </Link>

          <Link href="/statistikk/all-time">
            <Card className="cursor-pointer transition-colors hover:bg-muted/50">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  All-time lister
                  <ArrowRight className="h-4 w-4" />
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Historiske toppresultater gjennom alle tider
                </p>
              </CardContent>
            </Card>
          </Link>

          <Link href="/statistikk/rekorder">
            <Card className="cursor-pointer transition-colors hover:bg-muted/50">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Norske rekorder
                  <ArrowRight className="h-4 w-4" />
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Offisielle norske rekorder i alle øvelser
                </p>
              </CardContent>
            </Card>
          </Link>
        </div>
      </section>

      {/* Season Leaders */}
      <section>
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-2xl font-semibold">
            Årsbeste {seasonLeaders.year} – {venueLabel}
          </h2>
          <Button variant="ghost" asChild>
            <Link href={`/statistikk?venue=${venueParam}`}>
              Se årslister <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {/* Men */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Menn</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {seasonLeaders.men.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-3 py-2 text-left text-xs font-medium">Øvelse</th>
                        <th className="px-3 py-2 text-left text-xs font-medium">Resultat</th>
                        <th className="px-3 py-2 text-left text-xs font-medium">Utøver</th>
                      </tr>
                    </thead>
                    <tbody>
                      {seasonLeaders.men.map((result) => (
                        <tr key={result.event_code} className="border-b last:border-0 hover:bg-muted/30">
                          <td className="px-3 py-1.5 text-sm">
                            <Link
                              href={`/statistikk?event=${result.event_id}&gender=M&venue=${venueParam}`}
                              className="hover:text-primary hover:underline"
                            >
                              {getEventDisplayName(result.event_code!)}
                            </Link>
                          </td>
                          <td className="px-3 py-1.5">
                            <span className="perf-value text-sm">
                              {formatPerformance(result.performance, result.result_type)}
                            </span>
                            {result.wind !== null && result.wind !== undefined && (
                              <span className="ml-1 text-xs text-muted-foreground">
                                ({result.wind > 0 ? "+" : ""}{result.wind})
                              </span>
                            )}
                          </td>
                          <td className="px-3 py-1.5 text-sm">
                            <Link
                              href={`/utover/${result.athlete_id}`}
                              className="font-medium text-primary hover:underline"
                            >
                              {result.athlete_name}
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="p-4 text-center text-sm text-muted-foreground">
                  Ingen resultater ennå
                </p>
              )}
            </CardContent>
          </Card>

          {/* Women */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Kvinner</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {seasonLeaders.women.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-3 py-2 text-left text-xs font-medium">Øvelse</th>
                        <th className="px-3 py-2 text-left text-xs font-medium">Resultat</th>
                        <th className="px-3 py-2 text-left text-xs font-medium">Utøver</th>
                      </tr>
                    </thead>
                    <tbody>
                      {seasonLeaders.women.map((result) => (
                        <tr key={result.event_code} className="border-b last:border-0 hover:bg-muted/30">
                          <td className="px-3 py-1.5 text-sm">
                            <Link
                              href={`/statistikk?event=${result.event_id}&gender=F&venue=${venueParam}`}
                              className="hover:text-primary hover:underline"
                            >
                              {getEventDisplayName(result.event_code!)}
                            </Link>
                          </td>
                          <td className="px-3 py-1.5">
                            <span className="perf-value text-sm">
                              {formatPerformance(result.performance, result.result_type)}
                            </span>
                            {result.wind !== null && result.wind !== undefined && (
                              <span className="ml-1 text-xs text-muted-foreground">
                                ({result.wind > 0 ? "+" : ""}{result.wind})
                              </span>
                            )}
                          </td>
                          <td className="px-3 py-1.5 text-sm">
                            <Link
                              href={`/utover/${result.athlete_id}`}
                              className="font-medium text-primary hover:underline"
                            >
                              {result.athlete_name}
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="p-4 text-center text-sm text-muted-foreground">
                  Ingen resultater ennå
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  )
}
