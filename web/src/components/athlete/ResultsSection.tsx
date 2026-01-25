"use client"

import { useMemo, useState } from "react"
import Link from "next/link"
import { useRouter, useSearchParams } from "next/navigation"
import { ChevronUp, ChevronDown } from "lucide-react"
import { SingleFilterChip } from "@/components/ui/filter-chips"
import { formatPerformance } from "@/lib/format-performance"

type SortField = "date" | "event" | "performance"
type SortDirection = "asc" | "desc"

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
  result_type?: string
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

function SearchIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
  )
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
    qualification: "Kval.",
  }
  return roundNames[round] || round
}

export function ResultsSection({ results, seasons, events }: ResultsSectionProps) {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [searchQuery, setSearchQuery] = useState("")
  const [sortField, setSortField] = useState<SortField>("date")
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc")

  // Default to showing all results
  const yearParam = searchParams.get("year") || "all"
  const eventParam = searchParams.get("event") || "all"
  const indoorParam = searchParams.get("indoor")
  const pbOnlyParam = searchParams.get("pb") === "true"
  const finalsOnlyParam = searchParams.get("finals") === "true"

  // Check if a single event is selected (for performance sorting)
  const isSingleEventSelected = eventParam !== "all"

  // Get the result_type for the selected event
  const selectedEventResultType = useMemo(() => {
    if (!isSingleEventSelected) return null
    const selectedEvent = events.find(e => e.id === eventParam)
    // Find a result with this event to get the result_type
    const sampleResult = results.find(r => r.event_id === eventParam)
    return sampleResult?.result_type || "time"
  }, [eventParam, events, results, isSingleEventSelected])

  // Filter results
  const filteredResults = useMemo(() => {
    const filtered = results.filter((r) => {
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
      if (pbOnlyParam && !r.is_pb) {
        return false
      }
      if (finalsOnlyParam && r.round !== "final" && r.round !== "a_final") {
        return false
      }
      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase()
        const matchesMeet = r.meet_name?.toLowerCase().includes(query)
        const matchesEvent = r.event_name?.toLowerCase().includes(query)
        if (!matchesMeet && !matchesEvent) {
          return false
        }
      }
      return true
    })

    // Sort results
    return filtered.sort((a, b) => {
      if (sortField === "date") {
        const dateA = new Date(a.date).getTime()
        const dateB = new Date(b.date).getTime()
        return sortDirection === "desc" ? dateB - dateA : dateA - dateB
      } else if (sortField === "event") {
        const comparison = (a.event_name || "").localeCompare(b.event_name || "", "no")
        return sortDirection === "desc" ? -comparison : comparison
      } else if (sortField === "performance" && isSingleEventSelected) {
        const valA = a.performance_value ?? 0
        const valB = b.performance_value ?? 0
        // For time events, lower is better. For distance/height/points, higher is better.
        const isTimeEvent = selectedEventResultType === "time"
        if (sortDirection === "desc") {
          // Best first
          return isTimeEvent ? valA - valB : valB - valA
        } else {
          // Worst first
          return isTimeEvent ? valB - valA : valA - valB
        }
      }
      return 0
    })
  }, [results, yearParam, eventParam, indoorParam, pbOnlyParam, finalsOnlyParam, searchQuery, sortField, sortDirection, isSingleEventSelected, selectedEventResultType])

  // Toggle sort
  const toggleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "desc" ? "asc" : "desc")
    } else {
      setSortField(field)
      setSortDirection("desc")
    }
  }

  const updateSearchParams = (key: string, value: string) => {
    const params = new URLSearchParams(searchParams.toString())
    if (value === "all" || value === "") {
      params.delete(key)
    } else {
      params.set(key, value)
    }
    router.push(`?${params.toString()}`, { scroll: false })
  }

  // Get recent years for filter chips (last 5 years + "All")
  const recentYears = seasons.slice(0, 5)
  const olderYears = seasons.slice(5)

  return (
    <div className="card-flat p-0">
      {/* Filter bar */}
      <div className="flex flex-wrap items-center gap-3 px-3 py-2 border-b border-[var(--border-default)]">
        {/* Year filters */}
        <div className="flex flex-wrap items-center gap-1.5">
          <SingleFilterChip
            label="Alle år"
            active={yearParam === "all"}
            onClick={() => updateSearchParams("year", "all")}
          />
          {recentYears.map((year) => (
            <SingleFilterChip
              key={year}
              label={year.toString()}
              active={yearParam === year.toString()}
              onClick={() => updateSearchParams("year", year.toString())}
            />
          ))}
          {olderYears.length > 0 && (
            <select
              value={olderYears.includes(parseInt(yearParam)) ? yearParam : ""}
              onChange={(e) => updateSearchParams("year", e.target.value)}
              className="h-7 rounded border bg-transparent px-2 text-[13px]"
            >
              <option value="" disabled>Eldre...</option>
              {olderYears.map((year) => (
                <option key={year} value={year.toString()}>
                  {year}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Separator */}
        <div className="h-4 w-px bg-[var(--border-default)]" />

        {/* Indoor/Outdoor filters */}
        <div className="flex items-center gap-1.5">
          <SingleFilterChip
            label="Alle"
            active={!indoorParam}
            onClick={() => updateSearchParams("indoor", "")}
          />
          <SingleFilterChip
            label="Ute"
            active={indoorParam === "false"}
            onClick={() => updateSearchParams("indoor", "false")}
          />
          <SingleFilterChip
            label="Inne"
            active={indoorParam === "true"}
            onClick={() => updateSearchParams("indoor", "true")}
          />
        </div>

        {/* Separator */}
        <div className="h-4 w-px bg-[var(--border-default)]" />

        {/* PB/Finals filters */}
        <div className="flex items-center gap-1.5">
          <SingleFilterChip
            label="Kun PB"
            active={pbOnlyParam}
            onClick={() => updateSearchParams("pb", pbOnlyParam ? "" : "true")}
          />
          <SingleFilterChip
            label="Kun finaler"
            active={finalsOnlyParam}
            onClick={() => updateSearchParams("finals", finalsOnlyParam ? "" : "true")}
          />
        </div>

        {/* Event filter (if many events) */}
        {events.length > 3 && (
          <>
            <div className="h-4 w-px bg-[var(--border-default)]" />
            <select
              value={eventParam}
              onChange={(e) => updateSearchParams("event", e.target.value)}
              className="h-7 rounded border bg-transparent px-2 text-[13px]"
            >
              <option value="all">Alle øvelser</option>
              {events.map((event) => (
                <option key={event.id} value={event.id}>
                  {event.name}
                </option>
              ))}
            </select>
          </>
        )}

        {/* Search */}
        <div className="ml-auto flex items-center">
          <div className="relative">
            <SearchIcon className="absolute left-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-[var(--text-muted)]" />
            <input
              type="text"
              placeholder="Søk stevne..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-7 w-32 rounded border bg-transparent pl-7 pr-2 text-[13px] placeholder:text-[var(--text-muted)] focus:w-48 focus:outline-none focus:ring-1 focus:ring-[var(--focus-ring)] transition-all"
            />
          </div>
        </div>
      </div>

      {/* Results count */}
      <div className="border-b bg-[var(--bg-muted)] px-3 py-1.5">
        <span className="text-[12px] text-[var(--text-muted)]">
          {filteredResults.length} resultat{filteredResults.length !== 1 && "er"}
        </span>
      </div>

      {/* Results table */}
      {filteredResults.length === 0 ? (
        <p className="p-4 text-[13px] text-[var(--text-muted)]">
          Ingen resultater funnet med gjeldende filtre.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table>
            <thead>
              <tr>
                <th>
                  <button
                    onClick={() => toggleSort("date")}
                    className="flex items-center gap-1 hover:text-[var(--text-default)] transition-colors"
                  >
                    Dato
                    {sortField === "date" && (
                      sortDirection === "desc" ? <ChevronDown className="h-3 w-3" /> : <ChevronUp className="h-3 w-3" />
                    )}
                  </button>
                </th>
                <th>
                  <button
                    onClick={() => toggleSort("event")}
                    className="flex items-center gap-1 hover:text-[var(--text-default)] transition-colors"
                  >
                    Øvelse
                    {sortField === "event" && (
                      sortDirection === "desc" ? <ChevronDown className="h-3 w-3" /> : <ChevronUp className="h-3 w-3" />
                    )}
                  </button>
                </th>
                <th>
                  {isSingleEventSelected ? (
                    <button
                      onClick={() => toggleSort("performance")}
                      className="flex items-center gap-1 hover:text-[var(--text-default)] transition-colors"
                    >
                      Resultat
                      {sortField === "performance" && (
                        sortDirection === "desc" ? <ChevronDown className="h-3 w-3" /> : <ChevronUp className="h-3 w-3" />
                      )}
                    </button>
                  ) : (
                    "Resultat"
                  )}
                </th>
                <th className="col-numeric hidden sm:table-cell">Vind</th>
                <th className="col-numeric hidden md:table-cell">Plass</th>
                <th className="hidden lg:table-cell">Runde</th>
                <th>Stevne</th>
              </tr>
            </thead>
            <tbody>
              {filteredResults.map((result) => (
                <tr key={result.id}>
                  <td className="text-[var(--text-muted)] whitespace-nowrap">
                    {formatDate(result.date)}
                  </td>
                  <td className="whitespace-nowrap">{result.event_name}</td>
                  <td className="whitespace-nowrap">
                    <span className="perf-value">{formatPerformance(result.performance, result.result_type)}</span>
                    {result.is_pb && (
                      <span className="badge-pb ml-1.5">PB</span>
                    )}
                    {result.is_sb && !result.is_pb && (
                      <span className="badge-sb ml-1.5">SB</span>
                    )}
                    {result.is_national_record && (
                      <span className="badge-nr ml-1.5">NR</span>
                    )}
                  </td>
                  <td className="col-numeric hidden text-[var(--text-muted)] sm:table-cell">
                    {formatWind(result.wind) || "–"}
                  </td>
                  <td className="col-numeric hidden text-[var(--text-muted)] md:table-cell">
                    {result.place || "–"}
                  </td>
                  <td className="hidden text-[var(--text-muted)] lg:table-cell">
                    {formatRound(result.round) || "–"}
                  </td>
                  <td>
                    <Link href={`/stevner/${result.meet_id}`}>
                      {result.meet_name}
                    </Link>
                    {result.meet_indoor && (
                      <span className="ml-1 text-[11px] text-[var(--text-muted)]">(i)</span>
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
}
