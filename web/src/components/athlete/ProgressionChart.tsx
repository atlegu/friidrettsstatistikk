"use client"

import { useMemo, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"

interface SeasonBest {
  season_year: number
  event_id: string
  event_name: string
  event_code: string
  result_type: string
  performance: string
  performance_value: number
}

interface ProgressionChartProps {
  seasonBests: SeasonBest[]
  events: { id: string; name: string; code: string; result_type: string }[]
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

export function ProgressionChart({ seasonBests, events }: ProgressionChartProps) {
  const [selectedEventId, setSelectedEventId] = useState<string>(
    events.length > 0 ? events[0].id : ""
  )

  const selectedEvent = events.find((e) => e.id === selectedEventId)
  const resultType = selectedEvent?.result_type || "time"

  const chartData = useMemo(() => {
    if (!selectedEventId) return []

    const eventBests = seasonBests.filter((sb) => sb.event_id === selectedEventId)

    // Group by year and keep best performance per year
    // (there can be both indoor and outdoor seasons in the same year)
    const bestByYear = new Map<number, SeasonBest>()
    const lowerIsBetter = resultType === "time"

    eventBests.forEach((sb) => {
      const existing = bestByYear.get(sb.season_year)
      if (!existing) {
        bestByYear.set(sb.season_year, sb)
      } else {
        // Keep the better performance
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
      }))
  }, [seasonBests, selectedEventId, resultType])

  if (events.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Progresjon</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Ingen data tilgjengelig</p>
        </CardContent>
      </Card>
    )
  }

  // Calculate Y-axis domain
  const yDomain = useMemo(() => {
    if (chartData.length === 0) return [0, 100]

    const values = chartData.map((d) => d.value)
    const min = Math.min(...values)
    const max = Math.max(...values)
    const padding = (max - min) * 0.1 || max * 0.1

    // For times, we want higher values at the bottom (lower is better)
    // For distances/heights, we want lower values at the bottom (higher is better)
    if (resultType === "time") {
      return [Math.max(0, min - padding), max + padding]
    }
    return [Math.max(0, min - padding), max + padding]
  }, [chartData, resultType])

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <CardTitle>Progresjon</CardTitle>
          <Select value={selectedEventId} onValueChange={setSelectedEventId}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Velg øvelse" />
            </SelectTrigger>
            <SelectContent>
              {events.map((event) => (
                <SelectItem key={event.id} value={event.id}>
                  {event.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      <CardContent>
        {chartData.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            Ingen data for valgt øvelse
          </p>
        ) : chartData.length === 1 ? (
          <div className="text-center py-8">
            <p className="text-muted-foreground">
              Kun ett datapunkt: <span className="font-mono font-medium">{chartData[0].performance}</span> ({chartData[0].year})
            </p>
          </div>
        ) : (
          <>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={chartData}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis
                    dataKey="year"
                    className="text-xs"
                    tick={{ fill: "hsl(var(--muted-foreground))" }}
                  />
                  <YAxis
                    reversed={resultType === "time"}
                    domain={yDomain}
                    tickFormatter={(value) => formatYAxisTick(value, resultType)}
                    className="text-xs"
                    tick={{ fill: "hsl(var(--muted-foreground))" }}
                  />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const data = payload[0].payload
                        return (
                          <div className="rounded-lg border bg-background p-2 shadow-sm">
                            <div className="font-semibold">{data.year}</div>
                            <div className="font-mono">{data.performance}</div>
                          </div>
                        )
                      }
                      return null
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke="hsl(var(--primary))"
                    strokeWidth={2}
                    dot={{ fill: "hsl(var(--primary))", strokeWidth: 2 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Data table below chart */}
            <div className="mt-6 overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="px-4 py-2 text-left font-medium">År</th>
                    <th className="px-4 py-2 text-left font-medium">Resultat</th>
                  </tr>
                </thead>
                <tbody>
                  {chartData.map((row) => (
                    <tr key={row.year} className="border-b last:border-0">
                      <td className="px-4 py-2 text-muted-foreground">{row.year}</td>
                      <td className="px-4 py-2 font-mono">{row.performance}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}
