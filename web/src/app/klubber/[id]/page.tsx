import Link from "next/link"
import { notFound } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { formatPerformance } from "@/lib/format-performance"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"
import { BarChart3 } from "lucide-react"

async function getClub(id: string) {
  const supabase = await createClient()

  const { data } = await supabase
    .from("clubs")
    .select("*")
    .eq("id", id)
    .single()

  return data
}

async function getClubAthletes(clubId: string) {
  const supabase = await createClient()

  const { data } = await supabase
    .from("athletes")
    .select("id, first_name, last_name, full_name, birth_year, gender")
    .eq("current_club_id", clubId)
    .order("last_name", { ascending: true })
    .limit(50)

  return data ?? []
}

async function getClubResults(clubId: string) {
  const supabase = await createClient()

  const { data } = await supabase
    .from("results_full")
    .select("*")
    .eq("club_id", clubId)
    .order("date", { ascending: false })
    .limit(20)

  return data ?? []
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const club = await getClub(id)

  if (!club) {
    return { title: "Klubb ikke funnet" }
  }

  return {
    title: club.name,
    description: `Utøvere og resultater for ${club.name}`,
  }
}

export default async function ClubPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const club = await getClub(id)

  if (!club) {
    notFound()
  }

  const [athletes, results] = await Promise.all([
    getClubAthletes(id),
    getClubResults(id),
  ])

  return (
    <div className="container py-6">
      <Breadcrumbs items={[
        { label: "Klubber", href: "/klubber" },
        { label: club.name }
      ]} />

      {/* Header */}
      <div className="mt-4 mb-6">
        <h1 className="mb-2">{club.name}</h1>
        <div className="flex flex-wrap gap-4 text-muted-foreground">
          {club.short_name && club.short_name !== club.name && (
            <span>{club.short_name}</span>
          )}
          {club.city && <span>{club.city}</span>}
          {club.county && <span>{club.county}</span>}
        </div>
        {club.website && (
          <a
            href={club.website}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-2 inline-block text-sm text-primary hover:underline"
          >
            {club.website}
          </a>
        )}
        <Link
          href={`/klubber/${id}/statistikk`}
          className="mt-4 inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
        >
          <BarChart3 className="h-4 w-4" />
          Se klubbstatistikk
        </Link>
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        {/* Athletes */}
        <Card>
          <CardHeader>
            <CardTitle>Utøvere ({athletes.length})</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {athletes.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="px-4 py-3 text-left text-sm font-medium">Navn</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Fødselsår</th>
                    </tr>
                  </thead>
                  <tbody>
                    {athletes.map((athlete) => (
                      <tr key={athlete.id} className="border-b last:border-0 hover:bg-muted/30">
                        <td className="px-4 py-3">
                          <Link
                            href={`/utover/${athlete.id}`}
                            className="font-medium text-primary hover:underline"
                          >
                            {athlete.full_name || `${athlete.first_name} ${athlete.last_name}`}
                          </Link>
                        </td>
                        <td className="px-4 py-3 text-sm text-muted-foreground">
                          {athlete.birth_year ?? "-"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="p-4 text-sm text-muted-foreground">Ingen utøvere registrert</p>
            )}
          </CardContent>
        </Card>

        {/* Recent Results */}
        <Card>
          <CardHeader>
            <CardTitle>Siste resultater</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {results.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="px-4 py-3 text-left text-sm font-medium">Utøver</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Øvelse</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Resultat</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((result) => (
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
                        <td className="px-4 py-3"><span className="perf-value">{formatPerformance(result.performance, result.result_type)}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="p-4 text-sm text-muted-foreground">Ingen resultater registrert</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
