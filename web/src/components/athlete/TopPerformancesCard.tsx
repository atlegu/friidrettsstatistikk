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
      <CardHeader className="cursor-pointer pb-3" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {isExpanded ? (
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
            )}
            <CardTitle className="text-base">{eventName}</CardTitle>
            <Badge variant="secondary" className="text-xs">
              Top {performances.length}
            </Badge>
          </div>
          {!isExpanded && (
            <span className="font-mono text-sm font-medium">
              {bestPerformance.performance}
            </span>
          )}
        </div>
      </CardHeader>

      {isExpanded && (
        <CardContent className="p-0 pt-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-y bg-muted/50">
                  <th className="w-12 px-4 py-2 text-center font-medium">#</th>
                  <th className="px-4 py-2 text-left font-medium">Resultat</th>
                  <th className="hidden px-4 py-2 text-left font-medium sm:table-cell">
                    Vind
                  </th>
                  <th className="px-4 py-2 text-left font-medium">Dato</th>
                  <th className="hidden px-4 py-2 text-left font-medium md:table-cell">
                    Stevne
                  </th>
                </tr>
              </thead>
              <tbody>
                {performances.map((perf) => (
                  <tr
                    key={perf.result_id}
                    className="border-b last:border-0 hover:bg-muted/30"
                  >
                    <td className="px-4 py-2 text-center text-muted-foreground">
                      {perf.rank}
                    </td>
                    <td className="px-4 py-2">
                      <span className="font-mono font-medium">{perf.performance}</span>
                      {perf.is_national_record && (
                        <Badge className="ml-2 bg-amber-500 text-white hover:bg-amber-600">
                          NR
                        </Badge>
                      )}
                    </td>
                    <td className="hidden px-4 py-2 font-mono text-muted-foreground sm:table-cell">
                      {formatWind(perf.wind) || "–"}
                    </td>
                    <td className="px-4 py-2 text-muted-foreground">
                      {formatDate(perf.date)}
                    </td>
                    <td className="hidden px-4 py-2 md:table-cell">
                      <Link
                        href={`/stevner/${perf.meet_id}`}
                        className="hover:text-primary hover:underline"
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
          <p className="text-sm text-muted-foreground">Ingen data tilgjengelig</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Topp 10 prestasjoner</h2>
      <div className="grid gap-4">
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
