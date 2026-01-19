import Link from "next/link"
import { formatPerformance } from "@/lib/format-performance"

interface PersonalBest {
  result_id: string
  event_id: string
  event_name: string
  event_code: string
  result_type?: string
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
      <div className="card-flat">
        <h3 className="mb-3">{title}</h3>
        <p className="text-[13px] text-[var(--text-muted)]">Ingen rekorder</p>
      </div>
    )
  }

  return (
    <div className="card-flat p-0 overflow-hidden">
      <div className="px-3 pt-3 pb-2">
        <h3>{title}</h3>
      </div>
      <div className="overflow-x-auto">
        <table>
          <thead>
            <tr>
              <th>Øvelse</th>
              <th>Resultat</th>
              {showWind && (
                <th className="col-numeric hidden sm:table-cell">Vind</th>
              )}
              <th>Dato</th>
              <th className="hidden md:table-cell">Sted</th>
            </tr>
          </thead>
          <tbody>
            {pbs.map((pb) => (
              <tr key={pb.result_id}>
                <td className="whitespace-nowrap">{pb.event_name}</td>
                <td className="whitespace-nowrap">
                  <span className="perf-value">{formatPerformance(pb.performance, pb.result_type)}</span>
                  {pb.is_national_record && (
                    <span className="badge-nr ml-1.5">NR</span>
                  )}
                </td>
                {showWind && (
                  <td className="col-numeric hidden text-[var(--text-muted)] sm:table-cell">
                    {formatWind(pb.wind) || "–"}
                  </td>
                )}
                <td className="text-[var(--text-muted)] whitespace-nowrap">
                  {formatDate(pb.date)}
                </td>
                <td className="hidden md:table-cell">
                  <Link href={`/stevner/${pb.meet_id}`}>
                    {pb.meet_city || pb.meet_name}
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
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
