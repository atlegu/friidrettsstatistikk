import Link from "next/link"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent } from "@/components/ui/card"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"
import { ListeTopp } from "@/components/ui/liste-topp"

export const metadata = {
  title: "Stevner",
  description: "Stevnekalender og resultater fra norske friidrettsstevner",
}

/** Antall stevner lista viser. Basen har nær 48 000. */
const ANTALL = 100

async function getMeets(search?: string) {
  const supabase = await createClient()

  let query = supabase
    .from("meets")
    .select("id,name,city,venue,start_date,indoor", { count: "exact" })
    .order("start_date", { ascending: false })

  if (search) {
    query = query.or(`name.ilike.%${search}%,city.ilike.%${search}%,venue.ilike.%${search}%`)
  }

  const { data, error, count } = await query.limit(ANTALL)
  if (error) {
    console.error("Stevnelista kunne ikke hentes:", error.message)
  }

  return { meets: data ?? [], totalt: count }
}

export default async function StevnerPage({
  searchParams,
}: {
  searchParams: Promise<{ search?: string }>
}) {
  const { search } = await searchParams
  const { meets, totalt } = await getMeets(search)

  return (
    <div className="container py-6">
      <Breadcrumbs items={[{ label: "Stevner" }]} />
      <ListeTopp
        tittel="Stevner"
        beskrivelse="Stevnekalender og resultatlister"
        sokeVerdi={search}
        plassholder="Søk etter stevne, sted eller bane …"
      />

      <div className="mt-6" />

      {/* Meets list */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="px-4 py-3 text-left text-sm font-medium">Dato</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Stevne</th>
                  <th className="hidden px-4 py-3 text-left text-sm font-medium md:table-cell">Sted</th>
                </tr>
              </thead>
              <tbody>
                {meets.map((meet) => (
                  <tr key={meet.id} className="border-b last:border-0 hover:bg-muted/30">
                    <td className="px-4 py-3 text-sm text-muted-foreground">
                      {new Date(meet.start_date).toLocaleDateString("no-NO", {
                        day: "numeric",
                        month: "short",
                        year: "numeric",
                      })}
                    </td>
                    <td className="px-4 py-3">
                      <Link
                        href={`/stevner/${meet.id}`}
                        className="font-medium text-primary hover:underline"
                      >
                        {meet.name}
                      </Link>
                      {meet.indoor && (
                        <span className="ml-2 rounded bg-[var(--nfif-navy)]/10 px-1.5 py-0.5 text-xs font-medium text-[var(--nfif-navy)] dark:bg-white/10 dark:text-[var(--nfif-navy-blekk)]">
                          Inne
                        </span>
                      )}
                    </td>
                    <td className="hidden px-4 py-3 text-sm md:table-cell">
                      {meet.venue ? `${meet.venue}, ${meet.city}` : meet.city}
                    </td>
                  </tr>
                ))}
                {meets.length === 0 && (
                  <tr>
                    <td colSpan={3} className="px-4 py-8 text-center text-muted-foreground">
                      {search ? `Ingen stevner funnet for "${search}"` : "Ingen stevner funnet"}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <p className="mt-4 text-sm text-muted-foreground">
        {totalt !== null && totalt > meets.length ? (
          <>
            Viser de {meets.length.toLocaleString("nb-NO")} siste av{" "}
            {totalt.toLocaleString("nb-NO")} stevner
            {search && ` for søket «${search}»`}. Søk etter navn, sted eller bane
            for å finne eldre stevner.
          </>
        ) : (
          <>
            Viser {meets.length.toLocaleString("nb-NO")}{" "}
            {meets.length === 1 ? "stevne" : "stevner"}
            {search && ` for søket «${search}»`}.
          </>
        )}
      </p>
    </div>
  )
}
