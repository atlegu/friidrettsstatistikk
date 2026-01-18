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
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-[13px] text-muted-foreground">Ingen rekorder</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="px-3 py-1.5 text-left text-xs font-semibold text-[var(--text-secondary)]">Øvelse</th>
                <th className="px-3 py-1.5 text-left text-xs font-semibold text-[var(--text-secondary)]">Resultat</th>
                {showWind && (
                  <th className="hidden px-3 py-1.5 text-left text-xs font-semibold text-[var(--text-secondary)] sm:table-cell">Vind</th>
                )}
                <th className="px-3 py-1.5 text-left text-xs font-semibold text-[var(--text-secondary)]">Dato</th>
                <th className="hidden px-3 py-1.5 text-left text-xs font-semibold text-[var(--text-secondary)] md:table-cell">Sted</th>
              </tr>
            </thead>
            <tbody>
              {pbs.map((pb) => (
                <tr key={pb.result_id} className="border-b last:border-0 hover:bg-[var(--table-row-hover)]">
                  <td className="px-3 py-1.5 text-[13px]">{pb.event_name}</td>
                  <td className="px-3 py-1.5 text-[13px]">
                    <span className="perf-value">{pb.performance}</span>
                    {pb.is_national_record && (
                      <Badge variant="nr" className="ml-1.5">
                        NR
                      </Badge>
                    )}
                  </td>
                  {showWind && (
                    <td className="hidden px-3 py-1.5 text-[12px] tabular-nums text-[var(--text-muted)] sm:table-cell">
                      {formatWind(pb.wind) || "–"}
                    </td>
                  )}
                  <td className="px-3 py-1.5 text-[12px] text-[var(--text-muted)]">
                    {formatDate(pb.date)}
                  </td>
                  <td className="hidden px-3 py-1.5 text-[13px] md:table-cell">
                    <Link
                      href={`/stevner/${pb.meet_id}`}
                      className="no-underline hover:underline"
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
    <div className="grid gap-4 lg:grid-cols-2">
      <PersonalBestTable pbs={outdoorPBs} title="Utendørs" showWind={hasWindEvents} />
      <PersonalBestTable pbs={indoorPBs} title="Innendørs" showWind={false} />
    </div>
  )
}
