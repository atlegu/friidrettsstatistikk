import Link from "next/link"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"

export const metadata = {
  title: "Klubber",
  description: "Oversikt over alle friidrettsklubber i Norge",
}

async function getClubs(search?: string) {
  const supabase = await createClient()

  let query = supabase
    .from("clubs")
    .select("*")
    .eq("active", true)
    .eq("club_type", "athletics")  // Kun friidrettsklubber
    .order("name", { ascending: true })

  if (search) {
    query = query.or(`name.ilike.%${search}%,short_name.ilike.%${search}%,city.ilike.%${search}%`)
  }

  const { data } = await query

  return data ?? []
}

export default async function KlubberPage({
  searchParams,
}: {
  searchParams: Promise<{ search?: string }>
}) {
  const { search } = await searchParams
  const clubs = await getClubs(search)

  return (
    <div className="container py-6">
      <Breadcrumbs items={[{ label: "Klubber" }]} />
      <h1 className="mt-4 mb-4">Klubber</h1>

      {/* Search */}
      <form className="mb-8">
        <Input
          type="search"
          name="search"
          placeholder="Søk etter klubb..."
          defaultValue={search}
          className="max-w-md"
        />
      </form>

      {/* Clubs grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {clubs.map((club) => (
          <Link key={club.id} href={`/klubber/${club.id}`}>
            <Card className="h-full cursor-pointer transition-colors hover:bg-muted/50">
              <CardContent className="p-4">
                <h2 className="font-semibold text-primary">{club.name}</h2>
                {club.short_name && club.short_name !== club.name && (
                  <p className="text-sm text-muted-foreground">{club.short_name}</p>
                )}
                {club.city && (
                  <p className="mt-1 text-sm text-muted-foreground">{club.city}</p>
                )}
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      {clubs.length === 0 && (
        <p className="text-center text-muted-foreground">
          {search ? `Ingen klubber funnet for "${search}"` : "Ingen klubber funnet"}
        </p>
      )}

      <p className="mt-4 text-sm text-muted-foreground">
        Viser {clubs.length} klubber {search && `for søk "${search}"`}
      </p>
    </div>
  )
}
