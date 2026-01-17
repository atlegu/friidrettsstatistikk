import Link from "next/link"
import { notFound } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

async function getMeet(id: string) {
  const supabase = await createClient()

  const { data } = await supabase
    .from("meets")
    .select("*")
    .eq("id", id)
    .single()

  return data
}

async function getMeetResults(meetId: string) {
  const supabase = await createClient()

  const { data } = await supabase
    .from("results_full")
    .select("*")
    .eq("meet_id", meetId)
    .order("event_name", { ascending: true })
    .order("performance_value", { ascending: true })

  return data ?? []
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const meet = await getMeet(id)

  if (!meet) {
    return { title: "Stevne ikke funnet" }
  }

  return {
    title: meet.name,
    description: `Resultater fra ${meet.name}, ${meet.city}`,
  }
}

export default async function MeetPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const meet = await getMeet(id)

  if (!meet) {
    notFound()
  }

  const results = await getMeetResults(id)

  // Group results by event
  const resultsByEvent = results.reduce((acc, result) => {
    const eventName = result.event_name ?? "Ukjent"
    if (!acc[eventName]) {
      acc[eventName] = []
    }
    acc[eventName].push(result)
    return acc
  }, {} as Record<string, typeof results>)

  const eventNames = Object.keys(resultsByEvent).sort()

  return (
    <div className="container py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="mb-2 text-3xl font-bold">{meet.name}</h1>
        <div className="flex flex-wrap gap-4 text-muted-foreground">
          <span>
            {new Date(meet.start_date).toLocaleDateString("no-NO", {
              day: "numeric",
              month: "long",
              year: "numeric",
            })}
          </span>
          <span>{meet.venue ? `${meet.venue}, ${meet.city}` : meet.city}</span>
          {meet.indoor && (
            <span className="rounded bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800">
              Innendørs
            </span>
          )}
          {meet.level && (
            <span className="capitalize">{meet.level}</span>
          )}
        </div>
        {meet.website && (
          <a
            href={meet.website}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-2 inline-block text-sm text-primary hover:underline"
          >
            Stevnets nettside
          </a>
        )}
      </div>

      {/* Results by event */}
      {eventNames.length > 0 ? (
        <div className="space-y-6">
          {eventNames.map((eventName) => (
            <Card key={eventName}>
              <CardHeader>
                <CardTitle>{eventName}</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-4 py-2 text-left text-sm font-medium w-12">#</th>
                        <th className="px-4 py-2 text-left text-sm font-medium">Utøver</th>
                        <th className="hidden px-4 py-2 text-left text-sm font-medium md:table-cell">Klubb</th>
                        <th className="px-4 py-2 text-left text-sm font-medium">Resultat</th>
                      </tr>
                    </thead>
                    <tbody>
                      {resultsByEvent[eventName].map((result, index) => (
                        <tr key={result.id} className="border-b last:border-0 hover:bg-muted/30">
                          <td className="px-4 py-2 text-sm text-muted-foreground">
                            {result.place ?? index + 1}
                          </td>
                          <td className="px-4 py-2">
                            <Link
                              href={`/utover/${result.athlete_id}`}
                              className="font-medium text-primary hover:underline"
                            >
                              {result.athlete_name}
                            </Link>
                          </td>
                          <td className="hidden px-4 py-2 text-sm md:table-cell">
                            {result.club_name ?? "-"}
                          </td>
                          <td className="px-4 py-2">
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
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground">
            Ingen resultater registrert for dette stevnet
          </CardContent>
        </Card>
      )}
    </div>
  )
}
