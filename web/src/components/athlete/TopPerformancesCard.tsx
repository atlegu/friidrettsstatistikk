"use client"

import { useState } from "react"
import Link from "next/link"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ChevronDown, ChevronRight } from "lucide-react"

interface TopPerformance {
  rank: number
  result_id: string
  event_id: string
  event_name: string
  performance: string
  date: string
  wind: number | null
  meet_id: string
  meet_name: string
  is_national_record: boolean | null
}

interface TopPerformancesCardProps {
  performances: TopPerformance[]
  eventId: string
  eventName: string
  defaultExpanded?: boolean
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

export function TopPerformancesCard({
  performances,
  eventName,
  defaultExpanded = false,
}: TopPerformancesCardProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)

  if (performances.length === 0) {
    return null
  }

  const bestPerformance = performances[0]

  return (
    <Card>
      <CardHeader className="cursor-pointer" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {isExpanded ? (
              <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" />
            ) : (
              <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" />
            )}
            <CardTitle className="text-[14px]">{eventName}</CardTitle>
            <Badge variant="secondary" className="text-[10px]">
              Top {performances.length}
            </Badge>
          </div>
          {!isExpanded && (
            <span className="perf-value text-[13px] text-muted-foreground">
              {bestPerformance.performance}
            </span>
          )}
        </div>
      </CardHeader>

      {isExpanded && (
        <CardContent className="p-0">
          <div className="overflow-x-auto border-t">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="w-10 px-3 py-1.5 text-center text-xs font-semibold text-[var(--text-secondary)]">#</th>
                  <th className="px-3 py-1.5 text-left text-xs font-semibold text-[var(--text-secondary)]">Resultat</th>
                  <th className="hidden px-3 py-1.5 text-left text-xs font-semibold text-[var(--text-secondary)] sm:table-cell">
                    Vind
                  </th>
                  <th className="px-3 py-1.5 text-left text-xs font-semibold text-[var(--text-secondary)]">Dato</th>
                  <th className="hidden px-3 py-1.5 text-left text-xs font-semibold text-[var(--text-secondary)] md:table-cell">
                    Stevne
                  </th>
                </tr>
              </thead>
              <tbody>
                {performances.map((perf) => (
                  <tr
                    key={perf.result_id}
                    className="border-b last:border-0 hover:bg-[var(--table-row-hover)]"
                  >
                    <td className="px-3 py-1.5 text-center text-[12px] text-[var(--text-muted)]">
                      {perf.rank}
                    </td>
                    <td className="px-3 py-1.5 text-[13px]">
                      <span className="perf-value">{perf.performance}</span>
                      {perf.is_national_record && (
                        <Badge variant="nr" className="ml-1.5">
                          NR
                        </Badge>
                      )}
                    </td>
                    <td className="hidden px-3 py-1.5 text-[12px] tabular-nums text-[var(--text-muted)] sm:table-cell">
                      {formatWind(perf.wind) || "–"}
                    </td>
                    <td className="px-3 py-1.5 text-[12px] text-[var(--text-muted)]">
                      {formatDate(perf.date)}
                    </td>
                    <td className="hidden px-3 py-1.5 text-[13px] md:table-cell">
                      <Link
                        href={`/stevner/${perf.meet_id}`}
                        className="no-underline hover:underline"
                      >
                        {perf.meet_name}
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      )}
    </Card>
  )
}

interface TopPerformancesSectionProps {
  performancesByEvent: Record<string, TopPerformance[]>
  eventOrder: { id: string; name: string }[]
}

export function TopPerformancesSection({
  performancesByEvent,
  eventOrder,
}: TopPerformancesSectionProps) {
  const eventsWithPerformances = eventOrder.filter(
    (e) => performancesByEvent[e.id] && performancesByEvent[e.id].length > 0
  )

  if (eventsWithPerformances.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Topp 10 prestasjoner</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-[13px] text-muted-foreground">Ingen data tilgjengelig</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-3">
      <h2 className="text-[16px] font-semibold">Topp 10 prestasjoner</h2>
      <div className="grid gap-3">
        {eventsWithPerformances.map((event, index) => (
          <TopPerformancesCard
            key={event.id}
            eventId={event.id}
            eventName={event.name}
            performances={performancesByEvent[event.id]}
            defaultExpanded={index === 0}
          />
        ))}
      </div>
    </div>
  )
}
