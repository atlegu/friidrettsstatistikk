import Link from "next/link"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

export const metadata = {
  title: "Utøvere",
  description: "Søk blant alle registrerte utøvere i norsk friidrett",
}

async function getAthletes(search?: string) {
  const supabase = await createClient()

  let query = supabase
    .from("athletes")
    .select(`
      id,
      first_name,
      last_name,
      full_name,
      birth_year,
      gender,
      current_club_id
    `)
    .order("last_name", { ascending: true })
    .limit(100)

  if (search) {
    query = query.or(`first_name.ilike.%${search}%,last_name.ilike.%${search}%,full_name.ilike.%${search}%`)
  }

  const { data: athletes } = await query

  if (!athletes) return []

  // Get club names for athletes with current_club_id
  const clubIds = [...new Set(athletes.filter(a => a.current_club_id).map(a => a.current_club_id!))]
  let clubsMap: Record<string, string> = {}

  if (clubIds.length > 0) {
    const { data: clubs } = await supabase
      .from("clubs")
      .select("id, name")
      .in("id", clubIds)

    if (clubs) {
      clubsMap = Object.fromEntries(clubs.map(c => [c.id, c.name]))
    }
  }

  return athletes.map(athlete => ({
    ...athlete,
    club_name: athlete.current_club_id ? clubsMap[athlete.current_club_id] : null
  }))
}

export default async function UtoverPage({
  searchParams,
}: {
  searchParams: Promise<{ search?: string }>
}) {
  const { search } = await searchParams
  const athletes = await getAthletes(search)

  return (
    <div className="container py-8">
      <h1 className="mb-6 text-3xl font-bold">Utøvere</h1>

      {/* Search */}
      <form className="mb-8 flex gap-2 max-w-md">
        <Input
          type="search"
          name="search"
          placeholder="Søk etter utøver..."
          defaultValue={search}
        />
        <Button type="submit">Søk</Button>
      </form>

      {/* Athletes list */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="px-4 py-3 text-left text-sm font-medium">Navn</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Fødselsår</th>
                  <th className="hidden px-4 py-3 text-left text-sm font-medium md:table-cell">Klubb</th>
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
                    <td className="hidden px-4 py-3 text-sm md:table-cell">
                      {athlete.club_name ?? "-"}
                    </td>
                  </tr>
                ))}
                {athletes.length === 0 && (
                  <tr>
                    <td colSpan={3} className="px-4 py-8 text-center text-muted-foreground">
                      {search ? `Ingen utøvere funnet for "${search}"` : "Ingen utøvere funnet"}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <p className="mt-4 text-sm text-muted-foreground">
        Viser {athletes.length} utøvere {search && `for søk "${search}"`}
      </p>
    </div>
  )
}
