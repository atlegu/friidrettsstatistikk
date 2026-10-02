import Link from "next/link"
import { notFound } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { formatPerformance } from "@/lib/format-performance"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"
import { SideTopp, MetaSkille, ToppKnapp } from "@/components/ui/side-topp"
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

/** Resultat- og utøvertall per klubb, fra den materialiserte visningen. */
async function getClubBruk(clubId: string) {
  const supabase = await createClient()
  const { data } = await supabase
    .from("klubb_bruk")
    .select("resultater,utovere,fra_ar,til_ar")
    .eq("id", clubId)
    .single()
  return data
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

  const [athletes, results, bruk] = await Promise.all([
    getClubAthletes(id),
    getClubResults(id),
    getClubBruk(id),
  ])

  const aktiv =
    bruk?.fra_ar && bruk?.til_ar
      ? bruk.fra_ar === bruk.til_ar
        ? String(bruk.fra_ar)
        : `${bruk.fra_ar}–${bruk.til_ar}`
      : null

  return (
    <div className="container py-6">
      <Breadcrumbs items={[
        { label: "Klubber", href: "/klubber" },
        { label: club.name }
      ]} />

      <SideTopp
        tittel={club.name}
        meta={
          <>
            {club.short_name && club.short_name !== club.name && (
              <span>{club.short_name}</span>
            )}
            {club.city && (
              <>
                {club.short_name && club.short_name !== club.name && <MetaSkille />}
                <span className="font-bold text-white">{club.city}</span>
              </>
            )}
            {club.county && (
              <>
                <MetaSkille />
                <span>{club.county}</span>
              </>
            )}
            {club.website && (
              <>
                <MetaSkille />
                <a
                  href={club.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline-offset-2 hover:underline"
                >
                  Nettsted
                </a>
              </>
            )}
          </>
        }
        noekkeltall={[
          { merkelapp: "Resultater", verdi: bruk?.resultater ?? null },
          { merkelapp: "Utøvere", verdi: bruk?.utovere ?? null },
          { merkelapp: "Aktiv", verdi: aktiv },
        ]}
        handlinger={
          <ToppKnapp href={`/klubber/${id}/statistikk`} fremhevet>
            <BarChart3 className="h-4 w-4" />
            Klubbstatistikk
          </ToppKnapp>
        }
      />

      <div className="mt-6" />

      <div className="grid gap-8 lg:grid-cols-2">
        {/* Athletes */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-baseline justify-between gap-3">
              <span>Utøvere</span>
              {bruk?.utovere && bruk.utovere > athletes.length && (
                <span className="text-[12px] font-normal text-[var(--text-muted)]">
                  viser {athletes.length} av {bruk.utovere.toLocaleString("no-NO")}
                </span>
              )}
            </CardTitle>
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
