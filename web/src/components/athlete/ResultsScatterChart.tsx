"use client"

import { useMemo, useState } from "react"
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"
import { formatPerformance } from "@/lib/format-performance"

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

interface ResultsScatterChartProps {
  results: Result[]
  events: { id: string; name: string; code: string; result_type: string }[]
}

// Detect divisor based on typical value ranges
// Height/distance in meters: ~1-100m => stored as cm (100-10000) or mm (1000-100000)
function detectDivisor(maxValue: number, resultType: string): number {
  if (resultType === "time") return 100 // hundredths of seconds
  if (resultType === "distance" || resultType === "height") {
    // If max value > 1000, likely stored in mm, need /1000
    // If max value < 1000, likely stored in cm, need /100
    // For pole vault: 6m = 600cm or 6000mm
    // For throws: 80m = 8000cm or 80000mm
    if (maxValue > 10000) return 1000 // Definitely mm (throws in mm)
    if (maxValue > 1000) return 1000  // Likely mm (heights in mm)
    return 100 // Likely cm
  }
  return 1 // points
}

function formatPerformanceForChart(value: number, resultType: string, divisor: number): string {
  if (resultType === "time") {
    const totalSeconds = value / 100
    const minutes = Math.floor(totalSeconds / 60)
    const seconds = totalSeconds % 60

    if (minutes > 0) {
      return `${minutes}:${seconds.toFixed(2).padStart(5, "0")}`
    }
    return seconds.toFixed(2)
  }
  if (resultType === "distance" || resultType === "height") {
    return (value / divisor).toFixed(2)
  }
  return value.toString()
}

function formatYAxisTick(value: number, resultType: string, divisor: number): string {
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
    return (value / divisor).toFixed(2)
  }
  return value.toString()
}

function formatDateShort(dateStr: string): string {
  // Parse date string directly to avoid timezone issues
  const parts = dateStr.split("-")
  if (parts.length !== 3) return dateStr
  const day = parseInt(parts[2], 10)
  const month = parseInt(parts[1], 10)
  const year = parseInt(parts[0], 10) % 100
  return `${day}/${month}-${year.toString().padStart(2, "0")}`
}

function dateToTimestamp(dateStr: string): number {
  // Parse as UTC to avoid timezone differences between server/client
  const parts = dateStr.split("-")
  if (parts.length !== 3) return 0
  return Date.UTC(parseInt(parts[0], 10), parseInt(parts[1], 10) - 1, parseInt(parts[2], 10))
}

export function ResultsScatterChart({ results, events }: ResultsScatterChartProps) {
  const [selectedEventId, setSelectedEventId] = useState<string>(
    events.length > 0 ? events[0].id : ""
  )

  const selectedEvent = events.find((e) => e.id === selectedEventId)
  const resultType = selectedEvent?.result_type || "time"

  const chartData = useMemo(() => {
    if (!selectedEventId) return []

    const eventResults = results.filter(
      (r) => r.event_id === selectedEventId && r.performance_value !== null
    )

    return eventResults
      .map((r) => ({
        date: r.date,
        timestamp: dateToTimestamp(r.date),
        value: r.performance_value as number,
        performance: r.performance,
        meet_name: r.meet_name,
        is_pb: r.is_pb,
        is_sb: r.is_sb,
        is_national_record: r.is_national_record,
        wind: r.wind,
        place: r.place,
      }))
      .sort((a, b) => a.timestamp - b.timestamp)
  }, [results, selectedEventId])

  if (events.length === 0) {
    return (
      <div className="card-flat">
        <h3 className="mb-3">Alle resultater</h3>
        <p className="text-[13px] text-[var(--text-muted)]">Ingen data tilgjengelig</p>
      </div>
    )
  }

  // Calculate divisor for formatting based on max value
  const divisor = useMemo(() => {
    if (chartData.length === 0) return 100
    const maxValue = Math.max(...chartData.map((d) => d.value))
    return detectDivisor(maxValue, resultType)
  }, [chartData, resultType])

  // Calculate Y-axis domain
  const yDomain = useMemo(() => {
    if (chartData.length === 0) return [0, 100]

    const values = chartData.map((d) => d.value)
    const min = Math.min(...values)
    const max = Math.max(...values)
    const padding = (max - min) * 0.1 || max * 0.1

    return [Math.max(0, min - padding), max + padding]
  }, [chartData])

  // Calculate X-axis domain (timestamps)
  const xDomain = useMemo(() => {
    if (chartData.length === 0) return [Date.now() - 365 * 24 * 60 * 60 * 1000, Date.now()]

    const timestamps = chartData.map((d) => d.timestamp)
    const min = Math.min(...timestamps)
    const max = Math.max(...timestamps)
    const padding = (max - min) * 0.05 || 30 * 24 * 60 * 60 * 1000

    return [min - padding, max + padding]
  }, [chartData])

  return (
    <div className="card-flat">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h3>Alle resultater (spredningsplott)</h3>
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
      </div>

      {chartData.length === 0 ? (
        <p className="text-[13px] text-[var(--text-muted)]">
          Ingen data for valgt øvelse
        </p>
      ) : chartData.length === 1 ? (
        <div className="py-6 text-center">
          <p className="text-[13px] text-[var(--text-muted)]">
            Kun ett resultat: <span className="perf-value font-medium">{formatPerformance(chartData[0].performance, resultType)}</span> ({formatDateShort(chartData[0].date)})
          </p>
        </div>
      ) : (
        <>
          <div className="mb-2 text-[12px] text-[var(--text-muted)]">
            {chartData.length} resultater
          </div>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-default)" />
                <XAxis
                  dataKey="timestamp"
                  type="number"
                  domain={xDomain}
                  tickFormatter={(ts) => {
                    const date = new Date(ts)
                    return `${date.getUTCFullYear()}`
                  }}
                  tick={{ fill: "var(--text-muted)", fontSize: 11 }}
                  axisLine={{ stroke: "var(--border-default)" }}
                />
                <YAxis
                  dataKey="value"
                  type="number"
                  reversed={resultType === "time"}
                  domain={yDomain}
                  tickFormatter={(value) => formatYAxisTick(value, resultType, divisor)}
                  tick={{ fill: "var(--text-muted)", fontSize: 11 }}
                  axisLine={{ stroke: "var(--border-default)" }}
                  width={50}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload
                      return (
                        <div className="rounded border bg-[var(--bg-surface)] px-3 py-2 shadow-sm">
                          <div className="text-[12px] font-semibold">{formatDateShort(data.date)}</div>
                          <div className="perf-value text-[14px]">
                            {formatPerformance(data.performance, resultType)}
                            {data.wind && <span className="ml-1 text-[11px] text-[var(--text-muted)]">({data.wind})</span>}
                          </div>
                          <div className="mt-1 text-[11px] text-[var(--text-muted)]">{data.meet_name}</div>
                          {data.place && (
                            <div className="text-[11px] text-[var(--text-muted)]">{data.place}. plass</div>
                          )}
                          <div className="mt-1 flex gap-1">
                            {data.is_pb && (
                              <span className="rounded bg-[var(--accent-primary)] px-1 py-0.5 text-[9px] font-semibold text-white">
                                PB
                              </span>
                            )}
                            {data.is_sb && !data.is_pb && (
                              <span className="rounded bg-[var(--accent-secondary)] px-1 py-0.5 text-[9px] font-semibold text-white">
                                SB
                              </span>
                            )}
                            {data.is_national_record && (
                              <span className="rounded bg-amber-500 px-1 py-0.5 text-[9px] font-semibold text-white">
                                NR
                              </span>
                            )}
                          </div>
                        </div>
                      )
                    }
                    return null
                  }}
                />
                <Scatter
                  data={chartData}
                  fill="var(--accent-primary)"
                  shape={(props: unknown) => {
                    const { cx, cy, payload } = props as {
                      cx: number
                      cy: number
                      payload: { is_pb: boolean | null; is_national_record: boolean | null }
                    }
                    const isPB = payload.is_pb
                    const isNR = payload.is_national_record

                    if (isNR) {
                      // Gold star-like marker for national records
                      return (
                        <g>
                          <circle cx={cx} cy={cy} r={10} fill="#f59e0b" stroke="#b45309" strokeWidth={2} />
                          <text x={cx} y={cy + 1} textAnchor="middle" dominantBaseline="middle" fill="#fff" fontSize={8} fontWeight="bold">NR</text>
                        </g>
                      )
                    }
                    if (isPB) {
                      // Green marker for personal bests
                      return (
                        <circle
                          cx={cx}
                          cy={cy}
                          r={7}
                          fill="#22c55e"
                          stroke="#15803d"
                          strokeWidth={2}
                        />
                      )
                    }
                    // Regular results - smaller, semi-transparent blue
                    return (
                      <circle
                        cx={cx}
                        cy={cy}
                        r={4}
                        fill="var(--accent-primary)"
                        fillOpacity={0.5}
                      />
                    )
                  }}
                />
              </ScatterChart>
            </ResponsiveContainer>
          </div>

          {/* Legend */}
          <div className="mt-3 flex flex-wrap gap-4 text-[11px] text-[var(--text-muted)]">
            <div className="flex items-center gap-1.5">
              <span className="inline-flex h-4 w-4 items-center justify-center rounded-full bg-amber-500 text-[7px] font-bold text-white">NR</span>
              <span>Norgesrekord</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="inline-block h-3 w-3 rounded-full border-2 border-green-700" style={{ backgroundColor: "#22c55e" }}></span>
              <span>Pers</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="inline-block h-2 w-2 rounded-full opacity-50" style={{ backgroundColor: "var(--accent-primary)" }}></span>
              <span>Øvrige resultater</span>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
