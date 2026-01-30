"use client"

import { useState } from "react"
import { ProgressionChart } from "./ProgressionChart"
import { ResultsScatterChart } from "./ResultsScatterChart"
import { formatPerformance } from "@/lib/format-performance"

interface SeasonBest {
  season_year: number
  event_id: string
  event_name: string
  event_code: string
  result_type: string
  performance: string
  performance_value: number
  meet_id?: string
}

interface Result {
  id: string
  date: string
  performance: string
  performance_value: number | null
  wind: number | string | null
  place: number | null
  round: string | null
  is_pb: boolean | null
  is_sb: boolean | null
  is_national_record: boolean | null
  event_id: string
  event_name: string
  event_code: string
  result_type: string
  meet_id: string
  meet_name: string
  meet_indoor: boolean | null
  season_year: number | null
}

interface Event {
  id: string
  name: string
  code: string
  result_type: string
}

interface AthleteChartsSectionProps {
  seasonBests: SeasonBest[]
  results: Result[]
  events: Event[]
  pbResultIds: Set<string>
}

export function AthleteChartsSection({
  seasonBests,
  results,
  events,
  pbResultIds,
}: AthleteChartsSectionProps) {
  const [selectedEventId, setSelectedEventId] = useState<string>(
    events.length > 0 ? events[0].id : ""
  )

  const selectedEvent = events.find((e) => e.id === selectedEventId)

  if (events.length === 0) {
    return (
      <div className="card-flat">
        <p className="text-[13px] text-[var(--text-muted)]">Ingen data tilgjengelig</p>
      </div>
    )
  }

  // Filter season bests for selected event
  const eventSeasonBests = seasonBests.filter((sb) => sb.event_id === selectedEventId)

  // Group by year and keep best per year
  const byYear = new Map<number, typeof seasonBests[0]>()
  const resultType = selectedEvent?.result_type || "time"
  const lowerIsBetter = resultType === "time"

  eventSeasonBests.forEach((sb) => {
    const existing = byYear.get(sb.season_year)
    if (!existing) {
      byYear.set(sb.season_year, sb)
    } else {
      const isBetter = lowerIsBetter
        ? sb.performance_value < existing.performance_value
        : sb.performance_value > existing.performance_value
      if (isBetter) {
        byYear.set(sb.season_year, sb)
      }
    }
  })

  const sortedYears = Array.from(byYear.keys()).sort((a, b) => b - a)

  return (
    <div className="space-y-6">
      {/* Shared event selector */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <h2 className="text-lg font-semibold">Statistikk per øvelse</h2>
        <select
          value={selectedEventId}
          onChange={(e) => setSelectedEventId(e.target.value)}
          className="h-9 w-full rounded border bg-transparent px-3 text-sm font-medium sm:w-[200px]"
        >
          {events.map((event) => (
            <option key={event.id} value={event.id}>
              {event.name}
            </option>
          ))}
        </select>
      </div>

      {/* Charts grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Left: Progression Chart */}
        <ProgressionChart
          seasonBests={seasonBests}
          events={events}
          selectedEventId={selectedEventId}
          hideSelector
        />

        {/* Right: Season Bests Summary */}
        <div className="card-flat">
          <h3 className="mb-3">Sesongbeste per år</h3>
          {sortedYears.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="table-compact">
                <thead>
                  <tr>
                    <th>År</th>
                    <th className="col-numeric">Beste</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedYears.slice(0, 10).map((year) => {
                    const sb = byYear.get(year)!
                    return (
                      <tr key={year}>
                        <td className="text-[var(--text-muted)] tabular-nums">{year}</td>
                        <td className="col-numeric">
                          <span className="perf-value">
                            {formatPerformance(sb.performance, sb.result_type)}
                          </span>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
              {sortedYears.length > 10 && (
                <p className="mt-2 text-[12px] text-[var(--text-muted)]">
                  + flere sesonger
                </p>
              )}
            </div>
          ) : (
            <p className="text-[13px] text-[var(--text-muted)]">
              Ingen data for valgt øvelse
            </p>
          )}
        </div>
      </div>

      {/* Scatter plot */}
      <ResultsScatterChart
        results={results}
        events={events}
        pbResultIds={pbResultIds}
        selectedEventId={selectedEventId}
        hideSelector
      />
    </div>
  )
}
