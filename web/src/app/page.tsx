import Link from "next/link"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Users, Trophy, Calendar, Building2, ArrowRight } from "lucide-react"

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

async function getRecentResults() {
  const supabase = await createClient()

  const { data } = await supabase
    .from("results_full")
    .select("*")
    .order("date", { ascending: false })
    .limit(10)

  return data ?? []
}

export default async function Home() {
  const stats = await getStats()
  const recentResults = await getRecentResults()

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

      {/* Recent Results */}
      {recentResults.length > 0 && (
        <section>
          <div className="mb-6 flex items-center justify-between">
            <h2 className="text-2xl font-semibold">Siste resultater</h2>
            <Button variant="ghost" asChild>
              <Link href="/statistikk/2025">
                Se alle <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>

          <Card>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="px-4 py-3 text-left text-sm font-medium">Utøver</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Øvelse</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Resultat</th>
                      <th className="hidden px-4 py-3 text-left text-sm font-medium md:table-cell">
                        Stevne
                      </th>
                      <th className="hidden px-4 py-3 text-left text-sm font-medium lg:table-cell">
                        Dato
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentResults.map((result) => (
                      <tr key={result.id} className="border-b last:border-0 hover:bg-muted/30">
                        <td className="px-4 py-3">
                          <Link
                            href={`/utover/${result.athlete_id}`}
                            className="font-medium text-primary hover:underline"
                          >
                            {result.athlete_name}
                          </Link>
                        </td>
                        <td className="px-4 py-3 text-sm">{result.event_name}</td>
                        <td className="px-4 py-3">
                          <span className="font-mono font-medium">{result.performance}</span>
                          {result.wind !== null && (
                            <span className="ml-1 text-xs text-muted-foreground">
                              ({result.wind > 0 ? "+" : ""}{result.wind})
                            </span>
                          )}
                          {result.is_pb && (
                            <span className="ml-2 rounded bg-green-100 px-1.5 py-0.5 text-xs font-medium text-green-800">
                              PB
                            </span>
                          )}
                          {result.is_sb && !result.is_pb && (
                            <span className="ml-2 rounded bg-blue-100 px-1.5 py-0.5 text-xs font-medium text-blue-800">
                              SB
                            </span>
                          )}
                        </td>
                        <td className="hidden px-4 py-3 text-sm md:table-cell">
                          <Link
                            href={`/stevner/${result.meet_id}`}
                            className="hover:text-primary hover:underline"
                          >
                            {result.meet_name}
                          </Link>
                        </td>
                        <td className="hidden px-4 py-3 text-sm text-muted-foreground lg:table-cell">
                          {result.date
                            ? new Date(result.date).toLocaleDateString("no-NO", {
                                day: "numeric",
                                month: "short",
                                year: "numeric",
                              })
                            : "-"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </section>
      )}
    </div>
  )
}
