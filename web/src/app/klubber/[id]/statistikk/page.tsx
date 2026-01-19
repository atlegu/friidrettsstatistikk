import Link from "next/link"
import { notFound } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowRight } from "lucide-react"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"

async function getClub(id: string) {
  const supabase = await createClient()

  const { data } = await supabase
    .from("clubs")
    .select("*")
    .eq("id", id)
    .single()

  return data
}

async function getClubStats(clubId: string) {
  const supabase = await createClient()

  // Get total results count
  const { count: totalResults } = await supabase
    .from("results_full")
    .select("*", { count: "exact", head: true })
    .eq("club_id", clubId)

  // Get unique athletes count
  const { data: athletesData } = await supabase
    .from("results_full")
    .select("athlete_id")
    .eq("club_id", clubId)

  const uniqueAthletes = new Set(athletesData?.map(r => r.athlete_id) ?? []).size

  // Get first and last year with results
  const { data: yearsData } = await supabase
    .from("results_full")
    .select("season_year")
    .eq("club_id", clubId)
    .order("season_year", { ascending: true })

  const years = yearsData?.map(r => r.season_year).filter(y => y !== null) ?? []
  const firstYear = years[0] ?? null
  const lastYear = years[years.length - 1] ?? null
  const activeSeasons = new Set(years).size

  return {
    totalResults: totalResults ?? 0,
    uniqueAthletes,
    firstYear,
    lastYear,
    activeSeasons,
  }
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const club = await getClub(id)

  if (!club) {
    return { title: "Klubb ikke funnet" }
  }

  return {
    title: `${club.name} - Statistikk`,
    description: `Statistikk for ${club.name} - årslister, all-time lister og klubbrekorder`,
  }
}

const currentYear = new Date().getFullYear()
const years = Array.from({ length: 10 }, (_, i) => currentYear - i)

export default async function ClubStatisticsPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const club = await getClub(id)

  if (!club) {
    notFound()
  }

  const stats = await getClubStats(id)

  return (
    <div className="container py-6">
      <Breadcrumbs items={[
        { label: "Klubber", href: "/klubber" },
        { label: club.name, href: `/klubber/${id}` },
        { label: "Statistikk" }
      ]} />

      <h1 className="mt-4 mb-4">{club.name} - Statistikk</h1>

      {/* Quick stats */}
      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="pt-4">
            <p className="text-2xl font-bold">{stats.totalResults.toLocaleString("no-NO")}</p>
            <p className="text-sm text-muted-foreground">Resultater totalt</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <p className="text-2xl font-bold">{stats.uniqueAthletes.toLocaleString("no-NO")}</p>
            <p className="text-sm text-muted-foreground">Utøvere med resultater</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <p className="text-2xl font-bold">{stats.activeSeasons}</p>
            <p className="text-sm text-muted-foreground">Sesonger med aktivitet</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <p className="text-2xl font-bold">
              {stats.firstYear && stats.lastYear
                ? `${stats.firstYear}-${stats.lastYear}`
                : "-"}
            </p>
            <p className="text-sm text-muted-foreground">Resultatperiode</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Annual lists */}
        <Card>
          <CardHeader>
            <CardTitle>Årslister</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4 text-sm text-muted-foreground">
              Beste resultater per år for {club.name}
            </p>
            <div className="flex flex-wrap gap-2">
              {years.map((year) => (
                <Link
                  key={year}
                  href={`/klubber/${id}/statistikk/${year}`}
                  className="rounded bg-muted px-3 py-1 text-sm font-medium hover:bg-primary hover:text-primary-foreground"
                >
                  {year}
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* All-time */}
        <Link href={`/klubber/${id}/statistikk/all-time`}>
          <Card className="h-full cursor-pointer transition-colors hover:bg-muted/50">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                All-time lister
                <ArrowRight className="h-4 w-4" />
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Historiske toppresultater for {club.name} gjennom alle tider
              </p>
            </CardContent>
          </Card>
        </Link>

        {/* Records */}
        <Link href={`/klubber/${id}/statistikk/rekorder`}>
          <Card className="h-full cursor-pointer transition-colors hover:bg-muted/50">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Klubbrekorder
                <ArrowRight className="h-4 w-4" />
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Beste resultat per øvelse for {club.name}
              </p>
            </CardContent>
          </Card>
        </Link>
      </div>
    </div>
  )
}
