"use client"

import { useMemo, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"
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
  meet_name?: string
}

interface ProgressionChartProps {
  seasonBests: SeasonBest[]
  events: { id: string; name: string; code: string; result_type: string }[]
  // Controlled mode props - when provided, hides internal selector
  selectedEventId?: string
  hideSelector?: boolean
}

function formatPerformanceForChart(value: number, resultType: string): string {
  if (resultType === "time") {
    // Convert from hundredths of seconds
    const totalSeconds = value / 100
    const minutes = Math.floor(totalSeconds / 60)
    const seconds = totalSeconds % 60

    if (minutes > 0) {
      return `${minutes}:${seconds.toFixed(2).padStart(5, "0")}`
    }
    return seconds.toFixed(2)
  }
  // Distance/height in centimeters, display in meters
  if (resultType === "distance" || resultType === "height") {
    return (value / 100).toFixed(2)
  }
  // Points
  return value.toString()
}

function formatYAxisTick(value: number, resultType: string): string {
  if (resultType === "time") {
    const totalSeconds = value / 100
    const minutes = Math.floor(totalSeconds / 60)
    const seconds = totalSeconds % 60

    if (minutes > 0) {
      return `${minutes}:${seconds.toFixed(0).padStart(2, "0")}`
    }
    return seconds.toFixed(1)
  }
  if (resultType === "distance" || resultType === "height") {
    return (value / 100).toFixed(2)
  }
  return value.toString()
}

export function ProgressionChart({ seasonBests, events, selectedEventId: controlledEventId, hideSelector }: ProgressionChartProps) {
  const router = useRouter()
  const [internalEventId, setInternalEventId] = useState<string>(
    events.length > 0 ? events[0].id : ""
  )

  // Use controlled value if provided, otherwise use internal state
  const selectedEventId = controlledEventId ?? internalEventId
  const setSelectedEventId = setInternalEventId

  const selectedEvent = events.find((e) => e.id === selectedEventId)
  const resultType = selectedEvent?.result_type || "time"

  const chartData = useMemo(() => {
    if (!selectedEventId) return []

    const eventBests = seasonBests.filter((sb) => sb.event_id === selectedEventId)

    // Group by year and keep best performance per year
    const bestByYear = new Map<number, SeasonBest>()
    const lowerIsBetter = resultType === "time"

    eventBests.forEach((sb) => {
      const existing = bestByYear.get(sb.season_year)
      if (!existing) {
        bestByYear.set(sb.season_year, sb)
      } else {
        const isBetter = lowerIsBetter
          ? sb.performance_value < existing.performance_value
          : sb.performance_value > existing.performance_value
        if (isBetter) {
          bestByYear.set(sb.season_year, sb)
        }
      }
    })

    return Array.from(bestByYear.values())
      .sort((a, b) => a.season_year - b.season_year)
      .map((sb) => ({
        year: sb.season_year,
        value: sb.performance_value,
        performance: sb.performance,
        displayValue: formatPerformanceForChart(sb.performance_value, resultType),
        meet_id: sb.meet_id,
      }))
  }, [seasonBests, selectedEventId, resultType])

  if (events.length === 0) {
    return (
      <div className="card-flat">
        <h3 className="mb-3">Progresjon</h3>
        <p className="text-[13px] text-[var(--text-muted)]">Ingen data tilgjengelig</p>
      </div>
    )
  }

  // Calculate Y-axis domain
  const yDomain = useMemo(() => {
    if (chartData.length === 0) return [0, 100]

    const values = chartData.map((d) => d.value)
    const min = Math.min(...values)
    const max = Math.max(...values)
    const padding = (max - min) * 0.1 || max * 0.1

    return [Math.max(0, min - padding), max + padding]
  }, [chartData, resultType])

  return (
    <div className="card-flat">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h3>Progresjon</h3>
        {!hideSelector && (
          <select
            value={selectedEventId}
            onChange={(e) => setSelectedEventId(e.target.value)}
            className="h-8 w-full rounded border bg-transparent px-2 text-[13px] sm:w-[160px]"
          >
            {events.map((event) => (
              <option key={event.id} value={event.id}>
                {event.name}
              </option>
            ))}
          </select>
        )}
      </div>

      {chartData.length === 0 ? (
        <p className="text-[13px] text-[var(--text-muted)]">
          Ingen data for valgt øvelse
        </p>
      ) : chartData.length === 1 ? (
        <div className="py-6 text-center">
          <p className="text-[13px] text-[var(--text-muted)]">
            Kun ett datapunkt: <span className="perf-value font-medium">{formatPerformance(chartData[0].performance, resultType)}</span> ({chartData[0].year})
          </p>
        </div>
      ) : (
        <>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={chartData}
                margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-default)" />
                <XAxis
                  dataKey="year"
                  tick={{ fill: "var(--text-muted)", fontSize: 11 }}
                  axisLine={{ stroke: "var(--border-default)" }}
                />
                <YAxis
                  reversed={resultType === "time"}
                  domain={yDomain}
                  tickFormatter={(value) => formatYAxisTick(value, resultType)}
                  tick={{ fill: "var(--text-muted)", fontSize: 11 }}
                  axisLine={{ stroke: "var(--border-default)" }}
                  width={50}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload
                      return (
                        <div className="rounded border bg-[var(--bg-surface)] px-2 py-1.5 shadow-sm">
                          <div className="text-[12px] font-semibold">{data.year}</div>
                          <div className="perf-value text-[13px]">{formatPerformance(data.performance, resultType)}</div>
                          {data.meet_id && (
                            <div className="mt-1 text-[10px] text-[var(--accent-primary)]">
                              Klikk for å gå til stevnet →
                            </div>
                          )}
                        </div>
                      )
                    }
                    return null
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="var(--accent-primary)"
                  strokeWidth={2}
                  dot={{ fill: "var(--accent-primary)", strokeWidth: 2, r: 4, cursor: "pointer" }}
                  activeDot={{
                    r: 6,
                    fill: "var(--accent-primary)",
                    cursor: "pointer",
                    onClick: (_, payload: unknown) => {
                      const data = (payload as { payload?: { meet_id?: string } })?.payload
                      if (data?.meet_id) {
                        router.push(`/stevner/${data.meet_id}`)
                      }
                    },
                  }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Data table below chart */}
          <div className="mt-4 overflow-x-auto border-t pt-2">
            <table className="table-compact">
              <thead>
                <tr>
                  <th>År</th>
                  <th className="col-numeric">Resultat</th>
                  <th className="hidden sm:table-cell"></th>
                </tr>
              </thead>
              <tbody>
                {chartData.map((row) => (
                  <tr key={row.year}>
                    <td className="text-[var(--text-muted)] tabular-nums">{row.year}</td>
                    <td className="col-numeric">
                      <span className="perf-value">{formatPerformance(row.performance, resultType)}</span>
                    </td>
                    <td className="hidden sm:table-cell">
                      {row.meet_id && (
                        <Link
                          href={`/stevner/${row.meet_id}`}
                          className="text-[var(--accent-primary)] hover:underline text-[12px]"
                        >
                          Se stevne →
                        </Link>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}
