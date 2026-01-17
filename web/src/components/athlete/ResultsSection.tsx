"use client"

import { useMemo, useState } from "react"
import Link from "next/link"
import { useRouter, useSearchParams } from "next/navigation"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { ChevronDown, ChevronRight } from "lucide-react"

interface Result {
  id: string
  date: string
  performance: string
  performance_value: number | null
  wind: number | null
  place: number | null
  round: string | null
  is_pb: boolean | null
  is_sb: boolean | null
  is_national_record: boolean | null
  event_id: string
  event_name: string
  event_code: string
  meet_id: string
  meet_name: string
  meet_indoor: boolean | null
  season_year: number | null
}

interface ResultsSectionProps {
  results: Result[]
  seasons: number[]
  events: { id: string; name: string; code: string }[]
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString("no-NO", {
    day: "numeric",
    month: "short",
    year: "numeric",
  })
}

function formatWind(wind: number | null): string | null {
  if (wind === null || wind === undefined) return null
  return wind >= 0 ? `+${wind.toFixed(1)}` : wind.toFixed(1)
}

function formatRound(round: string | null): string | null {
  if (!round) return null
  const roundNames: Record<string, string> = {
    heat: "Forsøk",
    quarter: "Kvartfinale",
    semi: "Semifinale",
    final: "Finale",
    a_final: "A-finale",
    b_final: "B-finale",
    qualification: "Kvalifisering",
  }
  return roundNames[round] || round
}

export function ResultsSection({ results, seasons, events }: ResultsSectionProps) {
  const router = useRouter()
  const searchParams = useSearchParams()

  const currentYear = new Date().getFullYear()
  const defaultYear = seasons.includes(currentYear)
    ? currentYear.toString()
    : seasons.length > 0
      ? seasons[0].toString()
      : "all"

  const yearParam = searchParams.get("year") || defaultYear
  const eventParam = searchParams.get("event") || "all"
  const indoorParam = searchParams.get("indoor")

  const [expandedEvents, setExpandedEvents] = useState<Set<string>>(new Set())

  // Filter results
  const filteredResults = useMemo(() => {
    return results.filter((r) => {
      if (yearParam !== "all" && r.season_year?.toString() !== yearParam) {
        return false
      }
      if (eventParam !== "all" && r.event_id !== eventParam) {
        return false
      }
      if (indoorParam === "true" && !r.meet_indoor) {
        return false
      }
      if (indoorParam === "false" && r.meet_indoor) {
        return false
      }
      return true
    })
  }, [results, yearParam, eventParam, indoorParam])

  // Group results by event
  const groupedResults = useMemo(() => {
    const groups: Record<string, { event: { id: string; name: string }; results: Result[] }> = {}

    filteredResults.forEach((r) => {
      if (!groups[r.event_id]) {
        groups[r.event_id] = {
          event: { id: r.event_id, name: r.event_name },
          results: [],
        }
      }
      groups[r.event_id].results.push(r)
    })

    // Sort results within each group by date descending
    Object.values(groups).forEach((group) => {
      group.results.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    })

    return Object.values(groups).sort((a, b) =>
      a.event.name.localeCompare(b.event.name, "no")
    )
  }, [filteredResults])

  const updateSearchParams = (key: string, value: string) => {
    const params = new URLSearchParams(searchParams.toString())
    if (value === "all" || value === "") {
      params.delete(key)
    } else {
      params.set(key, value)
    }
    router.push(`?${params.toString()}`, { scroll: false })
  }

  const toggleEvent = (eventId: string) => {
    const newExpanded = new Set(expandedEvents)
    if (newExpanded.has(eventId)) {
      newExpanded.delete(eventId)
    } else {
      newExpanded.add(eventId)
    }
    setExpandedEvents(newExpanded)
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <CardTitle>Resultater</CardTitle>
          <div className="flex flex-wrap gap-2">
            <Select value={yearParam} onValueChange={(v) => updateSearchParams("year", v)}>
              <SelectTrigger className="w-[120px]">
                <SelectValue placeholder="År" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Alle år</SelectItem>
                {seasons.map((year) => (
                  <SelectItem key={year} value={year.toString()}>
                    {year}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={eventParam} onValueChange={(v) => updateSearchParams("event", v)}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Øvelse" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Alle øvelser</SelectItem>
                {events.map((event) => (
                  <SelectItem key={event.id} value={event.id}>
                    {event.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select
              value={indoorParam || "all"}
              onValueChange={(v) => updateSearchParams("indoor", v)}
            >
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Bane" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Alle</SelectItem>
                <SelectItem value="false">Utendørs</SelectItem>
                <SelectItem value="true">Innendørs</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        {groupedResults.length === 0 ? (
          <p className="p-6 text-sm text-muted-foreground">
            Ingen resultater funnet med gjeldende filtre.
          </p>
        ) : (
          <div className="divide-y">
            {groupedResults.map((group) => {
              const isExpanded = expandedEvents.has(group.event.id) || eventParam !== "all"
              const bestResult = group.results.reduce((best, curr) => {
                if (!best) return curr
                const currVal = curr.performance_value ?? 0
                const bestVal = best.performance_value ?? 0
                // Assuming lower is better for times (we'll improve this later)
                return currVal < bestVal ? curr : best
              }, group.results[0])

              return (
                <div key={group.event.id}>
                  <button
                    className="flex w-full items-center justify-between px-6 py-4 text-left hover:bg-muted/30"
                    onClick={() => toggleEvent(group.event.id)}
                  >
                    <div className="flex items-center gap-3">
                      {isExpanded ? (
                        <ChevronDown className="h-4 w-4 text-muted-foreground" />
                      ) : (
                        <ChevronRight className="h-4 w-4 text-muted-foreground" />
                      )}
                      <span className="font-medium">{group.event.name}</span>
                      <Badge variant="secondary" className="text-xs">
                        {group.results.length}
                      </Badge>
                    </div>
                    {!isExpanded && (
                      <span className="font-mono text-sm text-muted-foreground">
                        SB: {bestResult.performance}
                      </span>
                    )}
                  </button>

                  {isExpanded && (
                    <div className="overflow-x-auto border-t bg-muted/20">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b bg-muted/50">
                            <th className="px-6 py-2 text-left font-medium">Dato</th>
                            <th className="px-4 py-2 text-left font-medium">Resultat</th>
                            <th className="hidden px-4 py-2 text-left font-medium sm:table-cell">
                              Vind
                            </th>
                            <th className="hidden px-4 py-2 text-left font-medium md:table-cell">
                              Plass
                            </th>
                            <th className="hidden px-4 py-2 text-left font-medium lg:table-cell">
                              Runde
                            </th>
                            <th className="px-4 py-2 text-left font-medium">Stevne</th>
                          </tr>
                        </thead>
                        <tbody>
                          {group.results.map((result) => (
                            <tr
                              key={result.id}
                              className="border-b last:border-0 hover:bg-muted/30"
                            >
                              <td className="px-6 py-2 text-muted-foreground">
                                {formatDate(result.date)}
                              </td>
                              <td className="px-4 py-2">
                                <span className="font-mono font-medium">
                                  {result.performance}
                                </span>
                                {result.is_pb && (
                                  <Badge className="ml-2 bg-green-600 text-white">PB</Badge>
                                )}
                                {result.is_sb && !result.is_pb && (
                                  <Badge variant="secondary" className="ml-2">
                                    SB
                                  </Badge>
                                )}
                                {result.is_national_record && (
                                  <Badge className="ml-2 bg-amber-500 text-white">NR</Badge>
                                )}
                              </td>
                              <td className="hidden px-4 py-2 font-mono text-muted-foreground sm:table-cell">
                                {formatWind(result.wind) || "–"}
                              </td>
                              <td className="hidden px-4 py-2 text-muted-foreground md:table-cell">
                                {result.place || "–"}
                              </td>
                              <td className="hidden px-4 py-2 text-muted-foreground lg:table-cell">
                                {formatRound(result.round) || "–"}
                              </td>
                              <td className="px-4 py-2">
                                <Link
                                  href={`/stevner/${result.meet_id}`}
                                  className="hover:text-primary hover:underline"
                                >
                                  {result.meet_name}
                                </Link>
                                {result.meet_indoor && (
                                  <span className="ml-1 text-xs text-muted-foreground">(i)</span>
                                )}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
