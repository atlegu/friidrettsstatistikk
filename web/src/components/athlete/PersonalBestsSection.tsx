import Link from "next/link"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface PersonalBest {
  result_id: string
  event_id: string
  event_name: string
  event_code: string
  performance: string
  performance_value: number | null
  date: string
  wind: number | null
  is_national_record: boolean | null
  meet_id: string
  meet_name: string
  meet_city: string
  is_indoor: boolean
  event_sort_order: number | null
}

interface PersonalBestsSectionProps {
  personalBests: PersonalBest[]
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString("no-NO", {
    day: "numeric",
    month: "numeric",
    year: "2-digit",
  })
}

function formatWind(wind: number | null): string | null {
  if (wind === null || wind === undefined) return null
  return wind >= 0 ? `+${wind.toFixed(1)}` : wind.toFixed(1)
}

function PersonalBestTable({
  pbs,
  title,
  showWind = true
}: {
  pbs: PersonalBest[]
  title: string
  showWind?: boolean
}) {
  if (pbs.length === 0) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Ingen rekorder</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="px-4 py-2 text-left font-medium">Øvelse</th>
                <th className="px-4 py-2 text-left font-medium">Resultat</th>
                {showWind && (
                  <th className="hidden px-4 py-2 text-left font-medium sm:table-cell">Vind</th>
                )}
                <th className="px-4 py-2 text-left font-medium">Dato</th>
                <th className="hidden px-4 py-2 text-left font-medium md:table-cell">Sted</th>
              </tr>
            </thead>
            <tbody>
              {pbs.map((pb) => (
                <tr key={pb.result_id} className="border-b last:border-0 hover:bg-muted/30">
                  <td className="px-4 py-2">{pb.event_name}</td>
                  <td className="px-4 py-2">
                    <span className="font-mono font-medium">{pb.performance}</span>
                    {pb.is_national_record && (
                      <Badge className="ml-2 bg-amber-500 text-white hover:bg-amber-600">
                        NR
                      </Badge>
                    )}
                  </td>
                  {showWind && (
                    <td className="hidden px-4 py-2 font-mono text-muted-foreground sm:table-cell">
                      {formatWind(pb.wind) || "–"}
                    </td>
                  )}
                  <td className="px-4 py-2 text-muted-foreground">
                    {formatDate(pb.date)}
                  </td>
                  <td className="hidden px-4 py-2 md:table-cell">
                    <Link
                      href={`/stevner/${pb.meet_id}`}
                      className="hover:text-primary hover:underline"
                    >
                      {pb.meet_city || pb.meet_name}
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}

export function PersonalBestsSection({ personalBests }: PersonalBestsSectionProps) {
  // Sort by event sort order then by event name
  const sortedPBs = [...personalBests].sort((a, b) => {
    const orderA = a.event_sort_order ?? 999
    const orderB = b.event_sort_order ?? 999
    if (orderA !== orderB) return orderA - orderB
    return a.event_name.localeCompare(b.event_name, "no")
  })

  const outdoorPBs = sortedPBs.filter(pb => !pb.is_indoor)
  const indoorPBs = sortedPBs.filter(pb => pb.is_indoor)

  // Determine if we should show wind column (only relevant for outdoor)
  const hasWindEvents = outdoorPBs.some(pb => pb.wind !== null)

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <PersonalBestTable pbs={outdoorPBs} title="Utendørs" showWind={hasWindEvents} />
      <PersonalBestTable pbs={indoorPBs} title="Innendørs" showWind={false} />
    </div>
  )
}
