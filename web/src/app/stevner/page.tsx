import Link from "next/link"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"

export const metadata = {
  title: "Stevner",
  description: "Stevnekalender og resultater fra norske friidrettsstevner",
}

async function getMeets(search?: string) {
  const supabase = await createClient()

  let query = supabase
    .from("meets")
    .select("*")
    .order("start_date", { ascending: false })
    .limit(100)

  if (search) {
    query = query.or(`name.ilike.%${search}%,city.ilike.%${search}%,venue.ilike.%${search}%`)
  }

  const { data } = await query

  return data ?? []
}

export default async function StevnerPage({
  searchParams,
}: {
  searchParams: Promise<{ search?: string }>
}) {
  const { search } = await searchParams
  const meets = await getMeets(search)

  return (
    <div className="container py-8">
      <h1 className="mb-6 text-3xl font-bold">Stevner</h1>

      {/* Search */}
      <form className="mb-8">
        <Input
          type="search"
          name="search"
          placeholder="Søk etter stevne..."
          defaultValue={search}
          className="max-w-md"
        />
      </form>

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
                  <th className="hidden px-4 py-3 text-left text-sm font-medium lg:table-cell">Type</th>
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
                        <span className="ml-2 rounded bg-blue-100 px-1.5 py-0.5 text-xs font-medium text-blue-800">
                          Inne
                        </span>
                      )}
                    </td>
                    <td className="hidden px-4 py-3 text-sm md:table-cell">
                      {meet.venue ? `${meet.venue}, ${meet.city}` : meet.city}
                    </td>
                    <td className="hidden px-4 py-3 text-sm capitalize lg:table-cell">
                      {meet.level ?? "-"}
                    </td>
                  </tr>
                ))}
                {meets.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-4 py-8 text-center text-muted-foreground">
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
        Viser {meets.length} stevner {search && `for søk "${search}"`}
      </p>
    </div>
  )
}
