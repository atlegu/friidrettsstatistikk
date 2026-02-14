"use client"

import { useState, useEffect, useRef, useMemo } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Search, Loader2, X, Trophy } from "lucide-react"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts"
import { createClient } from "@/lib/supabase/client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"
import { formatPerformance, formatPerformanceValue } from "@/lib/format-performance"

interface Athlete {
  id: string
  first_name: string
  last_name: string
  full_name: string | null
  birth_year: number | null
  gender: string | null
}

interface SeasonBestRow {
  event_id: string
  event_name: string
  event_code: string
  result_type: string
  performance: string
  performance_value: number
  season_name: string
}

interface ProcessedSeasonBest {
  season_year: number
  event_id: string
  event_name: string
  event_code: string
  result_type: string
  performance: string
  performance_value: number
}

interface ResultRow {
  id: string
  meet_id: string
  event_id: string
  event_name: string
  event_code: string
  result_type: string
  meet_name: string
  date: string
  place: number | null
  performance: string
  performance_value: number | null
  round: string | null
  status: string
}

interface HeadToHeadMeeting {
  meet_id: string
  event_id: string
  event_name: string
  event_code: string
  result_type: string
  meet_name: string
  date: string
  round: string | null
  athlete1: { place: number | null; performance: string; performance_value: number | null }
  athlete2: { place: number | null; performance: string; performance_value: number | null }
  winner: 1 | 2 | 0 // 0 = tie/unknown
}

function AthleteSearch({
  label,
  selectedAthlete,
  onSelect,
  onClear,
  excludeId,
  isLoading,
}: {
  label: string
  selectedAthlete: Athlete | null
  onSelect: (athlete: Athlete) => void
  onClear: () => void
  excludeId?: string
  isLoading?: boolean
}) {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<Athlete[]>([])
  const [loading, setLoading] = useState(false)
  const [showResults, setShowResults] = useState(false)
  const supabase = createClient()

  useEffect(() => {
    if (query.length < 2) {
      setResults([])
      return
    }

    const timer = setTimeout(async () => {
      setLoading(true)
      const { data } = await supabase
        .from("athletes")
        .select("id, first_name, last_name, full_name, birth_year, gender")
        .or(`first_name.ilike.%${query}%,last_name.ilike.%${query}%,full_name.ilike.%${query}%`)
        .limit(10)

      const filtered = excludeId ? data?.filter(a => a.id !== excludeId) : data
      setResults(filtered ?? [])
      setLoading(false)
    }, 300)

    return () => clearTimeout(timer)
  }, [query, excludeId])

  if (isLoading) {
    return (
      <div className="space-y-2">
        <label className="text-sm font-medium">{label}</label>
        <div className="flex items-center gap-2 rounded-md border bg-muted/50 p-3">
          <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
          <span className="text-sm text-muted-foreground">Laster utøver...</span>
        </div>
      </div>
    )
  }

  if (selectedAthlete) {
    return (
      <div className="space-y-2">
        <label className="text-sm font-medium">{label}</label>
        <div className="flex items-center gap-2 rounded-md border bg-muted/50 p-3">
          <div className="flex-1">
            <p className="font-medium">
              {selectedAthlete.full_name || `${selectedAthlete.first_name} ${selectedAthlete.last_name}`}
            </p>
            <p className="text-sm text-muted-foreground">
              {selectedAthlete.birth_year ? `f. ${selectedAthlete.birth_year}` : ""}
            </p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClear}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium">{label}</label>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Søk etter utøver..."
          value={query}
          onChange={(e) => {
            setQuery(e.target.value)
            setShowResults(true)
          }}
          onFocus={() => setShowResults(true)}
          className="pl-9"
        />
        {showResults && (query.length >= 2 || results.length > 0) && (
          <div className="absolute z-10 mt-1 w-full rounded-md border bg-background shadow-lg">
            {loading ? (
              <div className="p-3 text-center text-sm text-muted-foreground">Søker...</div>
            ) : results.length > 0 ? (
              <ul className="max-h-60 overflow-auto py-1">
                {results.map((athlete) => (
                  <li key={athlete.id}>
                    <button
                      className="w-full px-3 py-2 text-left hover:bg-muted"
                      onClick={() => {
                        onSelect(athlete)
                        setQuery("")
                        setShowResults(false)
                      }}
                    >
                      <p className="font-medium">
                        {athlete.full_name || `${athlete.first_name} ${athlete.last_name}`}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {athlete.birth_year ? `f. ${athlete.birth_year}` : ""}
                      </p>
                    </button>
                  </li>
                ))}
              </ul>
            ) : query.length >= 2 ? (
              <div className="p-3 text-center text-sm text-muted-foreground">Ingen treff</div>
            ) : null}
          </div>
        )}
      </div>
    </div>
  )
}

function getAthleteName(a: Athlete): string {
  return a.full_name || `${a.first_name} ${a.last_name}`
}

function determineWinner(
  meeting: Omit<HeadToHeadMeeting, "winner">,
): 1 | 2 | 0 {
  const a1 = meeting.athlete1
  const a2 = meeting.athlete2

  // Compare by place first
  if (a1.place != null && a2.place != null) {
    if (a1.place < a2.place) return 1
    if (a2.place < a1.place) return 2
    return 0
  }

  // Fallback to performance_value
  if (a1.performance_value != null && a2.performance_value != null) {
    const isTimeEvent = meeting.result_type === "time"
    if (isTimeEvent) {
      if (a1.performance_value < a2.performance_value) return 1
      if (a2.performance_value < a1.performance_value) return 2
    } else {
      if (a1.performance_value > a2.performance_value) return 1
      if (a2.performance_value > a1.performance_value) return 2
    }
  }

  return 0
}

function formatRound(round: string | null): string {
  if (!round) return ""
  const map: Record<string, string> = {
    final: "Finale",
    semi: "Semifinale",
    heat: "Forsøk",
    qual: "Kvalifisering",
  }
  return map[round] || round
}

interface CompareContentProps {
  initialId1: string | null
  initialId2: string | null
  initialEvent: string | null
  initialTab: string | null
}

export default function CompareContent({ initialId1, initialId2, initialEvent, initialTab }: CompareContentProps) {
  const router = useRouter()
  const supabase = createClient()

  const [athlete1, setAthlete1] = useState<Athlete | null>(null)
  const [athlete2, setAthlete2] = useState<Athlete | null>(null)
  const [seasonBests1, setSeasonBests1] = useState<ProcessedSeasonBest[]>([])
  const [seasonBests2, setSeasonBests2] = useState<ProcessedSeasonBest[]>([])
  const [loadingData, setLoadingData] = useState(false)
  const [selectedEventId, setSelectedEventId] = useState<string>(initialEvent ?? "")

  // Head-to-head state
  const [activeTab, setActiveTab] = useState<"progresjon" | "h2h">(
    initialTab === "h2h" ? "h2h" : "progresjon"
  )
  const [h2hResults1, setH2hResults1] = useState<ResultRow[]>([])
  const [h2hResults2, setH2hResults2] = useState<ResultRow[]>([])
  const [loadingH2h, setLoadingH2h] = useState(false)
  const [h2hEventId, setH2hEventId] = useState<string>("all")
  const [loadingAthlete1, setLoadingAthlete1] = useState(!!initialId1)
  const [loadingAthlete2, setLoadingAthlete2] = useState(!!initialId2)
  const initialLoadStarted = useRef(false)
  const initialLoadComplete = useRef(!initialId1 && !initialId2)

  // Load athletes from URL params on mount
  useEffect(() => {
    if (initialLoadStarted.current) return
    initialLoadStarted.current = true

    if (!initialId1 && !initialId2) return

    async function loadAthletes() {
      try {
        if (initialId1) {
          const { data } = await supabase
            .from("athletes")
            .select("id, first_name, last_name, full_name, birth_year, gender")
            .eq("id", initialId1)
            .single()
          if (data) setAthlete1(data)
        }
        if (initialId2) {
          const { data } = await supabase
            .from("athletes")
            .select("id, first_name, last_name, full_name, birth_year, gender")
            .eq("id", initialId2)
            .single()
          if (data) setAthlete2(data)
        }
      } catch (err) {
        console.error('Error loading athletes:', err)
      } finally {
        setLoadingAthlete1(false)
        setLoadingAthlete2(false)
        initialLoadComplete.current = true
      }
    }
    loadAthletes()
  }, [initialId1, initialId2])

  // Update URL when athletes/event/tab change (skip until initial load is complete)
  useEffect(() => {
    if (!initialLoadComplete.current) return
    const p = new URLSearchParams()
    if (athlete1) p.set("id1", athlete1.id)
    if (athlete2) p.set("id2", athlete2.id)
    if (selectedEventId) p.set("event", selectedEventId)
    if (activeTab === "h2h") p.set("tab", "h2h")
    const newUrl = p.toString() ? `/sammenlign?${p.toString()}` : "/sammenlign"
    router.replace(newUrl, { scroll: false })
  }, [athlete1, athlete2, selectedEventId, activeTab, router])

  // Fetch season bests when both athletes are selected
  useEffect(() => {
    if (!athlete1 || !athlete2) {
      setSeasonBests1([])
      setSeasonBests2([])
      return
    }

    async function fetchSeasonBests() {
      setLoadingData(true)

      const [res1, res2] = await Promise.all([
        supabase
          .from("season_bests")
          .select("event_id, event_name, event_code, result_type, performance, performance_value, season_name")
          .eq("athlete_id", athlete1!.id),
        supabase
          .from("season_bests")
          .select("event_id, event_name, event_code, result_type, performance, performance_value, season_name")
          .eq("athlete_id", athlete2!.id),
      ])

      const process = (rows: SeasonBestRow[] | null): ProcessedSeasonBest[] =>
        (rows ?? []).map((sb) => ({
          season_year: parseInt(sb.season_name?.split(" ")[0] || "0"),
          event_id: sb.event_id || "",
          event_name: sb.event_name || "",
          event_code: sb.event_code || "",
          result_type: sb.result_type || "time",
          performance: sb.performance || "",
          performance_value: sb.performance_value || 0,
        }))

      setSeasonBests1(process(res1.data as SeasonBestRow[] | null))
      setSeasonBests2(process(res2.data as SeasonBestRow[] | null))
      setLoadingData(false)
    }

    fetchSeasonBests()
  }, [athlete1, athlete2])

  // Fetch head-to-head results when both athletes selected
  useEffect(() => {
    if (!athlete1 || !athlete2) {
      setH2hResults1([])
      setH2hResults2([])
      return
    }

    async function fetchAllResults(athleteId: string): Promise<ResultRow[]> {
      const allRows: ResultRow[] = []
      const pageSize = 1000
      let from = 0
      while (true) {
        const { data } = await supabase
          .from("results_full")
          .select("id, meet_id, event_id, event_name, event_code, result_type, meet_name, date, place, performance, performance_value, round, status")
          .eq("athlete_id", athleteId)
          .eq("status", "OK")
          .range(from, from + pageSize - 1)
        if (!data || data.length === 0) break
        allRows.push(...(data as ResultRow[]))
        if (data.length < pageSize) break
        from += pageSize
      }
      return allRows
    }

    async function fetchH2hResults() {
      setLoadingH2h(true)

      const [rows1, rows2] = await Promise.all([
        fetchAllResults(athlete1!.id),
        fetchAllResults(athlete2!.id),
      ])

      setH2hResults1(rows1)
      setH2hResults2(rows2)
      setLoadingH2h(false)
    }

    fetchH2hResults()
  }, [athlete1, athlete2])

  // Build head-to-head meetings
  const h2hMeetings = useMemo((): HeadToHeadMeeting[] => {
    if (h2hResults1.length === 0 || h2hResults2.length === 0) return []

    // Build maps for athlete 2: by meet+event+round and by meet+event
    const map2ByRound = new Map<string, ResultRow>()
    const map2ByEvent = new Map<string, ResultRow[]>()
    h2hResults2.forEach((r) => {
      const roundKey = `${r.meet_id}|${r.event_id}|${r.round ?? ""}`
      map2ByRound.set(roundKey, r)

      const eventKey = `${r.meet_id}|${r.event_id}`
      const existing = map2ByEvent.get(eventKey)
      if (existing) existing.push(r)
      else map2ByEvent.set(eventKey, [r])
    })

    const meetings: HeadToHeadMeeting[] = []
    const used2 = new Set<string>() // track used athlete2 result IDs

    h2hResults1.forEach((r1) => {
      // Try exact match on round first
      const roundKey = `${r1.meet_id}|${r1.event_id}|${r1.round ?? ""}`
      let r2 = map2ByRound.get(roundKey)

      // Fallback: match on meet+event only (pick first unused)
      if (!r2) {
        const eventKey = `${r1.meet_id}|${r1.event_id}`
        const candidates = map2ByEvent.get(eventKey)
        if (candidates) {
          r2 = candidates.find(c => !used2.has(c.id))
        }
      }

      if (!r2 || used2.has(r2.id)) return
      used2.add(r2.id)

      const base = {
        meet_id: r1.meet_id,
        event_id: r1.event_id,
        event_name: r1.event_name,
        event_code: r1.event_code,
        result_type: r1.result_type,
        meet_name: r1.meet_name,
        date: r1.date,
        round: r1.round || r2.round,
        athlete1: { place: r1.place, performance: r1.performance, performance_value: r1.performance_value },
        athlete2: { place: r2.place, performance: r2.performance, performance_value: r2.performance_value },
      }

      meetings.push({ ...base, winner: determineWinner(base) })
    })

    // Sort newest first
    meetings.sort((a, b) => b.date.localeCompare(a.date))
    return meetings
  }, [h2hResults1, h2hResults2])

  // H2H event options (events where they've met)
  const h2hEvents = useMemo(() => {
    const eventMap = new Map<string, { name: string; count: number }>()
    h2hMeetings.forEach((m) => {
      const existing = eventMap.get(m.event_id)
      if (existing) {
        existing.count++
      } else {
        eventMap.set(m.event_id, { name: m.event_name, count: 1 })
      }
    })
    return Array.from(eventMap.entries())
      .map(([id, { name, count }]) => ({ id, name, count }))
      .sort((a, b) => b.count - a.count)
  }, [h2hMeetings])

  // Filtered H2H meetings
  const filteredH2hMeetings = useMemo(() => {
    if (h2hEventId === "all") return h2hMeetings
    return h2hMeetings.filter((m) => m.event_id === h2hEventId)
  }, [h2hMeetings, h2hEventId])

  // H2H score
  const h2hScore = useMemo(() => {
    let wins1 = 0
    let wins2 = 0
    filteredH2hMeetings.forEach((m) => {
      if (m.winner === 1) wins1++
      else if (m.winner === 2) wins2++
    })
    return { wins1, wins2 }
  }, [filteredH2hMeetings])

  // Common events (for progression tab)
  const commonEvents = useMemo(() => {
    const events1 = new Map<string, { name: string; result_type: string }>()
    seasonBests1.forEach((sb) => {
      if (!events1.has(sb.event_id)) {
        events1.set(sb.event_id, { name: sb.event_name, result_type: sb.result_type })
      }
    })

    const common: { id: string; name: string; result_type: string }[] = []
    const seen = new Set<string>()
    seasonBests2.forEach((sb) => {
      if (events1.has(sb.event_id) && !seen.has(sb.event_id)) {
        seen.add(sb.event_id)
        common.push({
          id: sb.event_id,
          name: sb.event_name,
          result_type: events1.get(sb.event_id)!.result_type,
        })
      }
    })

    return common.sort((a, b) => a.name.localeCompare(b.name, "no"))
  }, [seasonBests1, seasonBests2])

  // Auto-select first common event if none selected
  useEffect(() => {
    if (commonEvents.length > 0 && (!selectedEventId || !commonEvents.find(e => e.id === selectedEventId))) {
      setSelectedEventId(commonEvents[0].id)
    }
  }, [commonEvents])

  const selectedEvent = commonEvents.find((e) => e.id === selectedEventId)
  const resultType = selectedEvent?.result_type || "time"

  // Build chart data: merge both athletes by age
  const chartData = useMemo(() => {
    if (!athlete1 || !athlete2 || !selectedEventId) return []
    if (!athlete1.birth_year || !athlete2.birth_year) return []

    const lowerIsBetter = resultType === "time"

    // Get best per calendar year for each athlete
    function bestByYear(bests: ProcessedSeasonBest[], birthYear: number) {
      const byAge = new Map<number, ProcessedSeasonBest>()
      bests
        .filter((sb) => sb.event_id === selectedEventId)
        .forEach((sb) => {
          const age = sb.season_year - birthYear
          const existing = byAge.get(age)
          if (!existing) {
            byAge.set(age, sb)
          } else {
            const isBetter = lowerIsBetter
              ? sb.performance_value < existing.performance_value
              : sb.performance_value > existing.performance_value
            if (isBetter) byAge.set(age, sb)
          }
        })
      return byAge
    }

    const map1 = bestByYear(seasonBests1, athlete1.birth_year)
    const map2 = bestByYear(seasonBests2, athlete2.birth_year)

    const allAges = new Set([...map1.keys(), ...map2.keys()])
    const data = Array.from(allAges)
      .sort((a, b) => a - b)
      .map((age) => {
        const sb1 = map1.get(age)
        const sb2 = map2.get(age)
        return {
          age,
          value1: sb1?.performance_value ?? null,
          value2: sb2?.performance_value ?? null,
          perf1: sb1?.performance ?? null,
          perf2: sb2?.performance ?? null,
        }
      })

    return data
  }, [seasonBests1, seasonBests2, athlete1, athlete2, selectedEventId, resultType])

  // Y-axis domain
  const yDomain = useMemo(() => {
    const values = chartData.flatMap((d) =>
      [d.value1, d.value2].filter((v): v is number => v !== null)
    )
    if (values.length === 0) return [0, 100]
    const min = Math.min(...values)
    const max = Math.max(...values)
    const padding = (max - min) * 0.1 || max * 0.1
    return [Math.max(0, min - padding), max + padding]
  }, [chartData])

  const name1 = athlete1 ? getAthleteName(athlete1) : ""
  const name2 = athlete2 ? getAthleteName(athlete2) : ""

  const bothSelected = athlete1 && athlete2
  const isLoading = activeTab === "progresjon" ? loadingData : loadingH2h

  return (
    <div className="container py-6">
      <Breadcrumbs items={[{ label: "Sammenlign utøvere" }]} />

      <h1 className="mt-4 mb-6">Sammenlign utøvere</h1>

      <div className="space-y-6">
        {/* Athlete selection */}
        <Card>
          <CardHeader>
            <CardTitle>Velg utøvere</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <AthleteSearch
                label="Utøver 1"
                selectedAthlete={athlete1}
                onSelect={setAthlete1}
                onClear={() => {
                  setAthlete1(null)
                  setSelectedEventId("")
                }}
                excludeId={athlete2?.id}
                isLoading={loadingAthlete1}
              />
              <AthleteSearch
                label="Utøver 2"
                selectedAthlete={athlete2}
                onSelect={setAthlete2}
                onClear={() => {
                  setAthlete2(null)
                  setSelectedEventId("")
                }}
                excludeId={athlete1?.id}
                isLoading={loadingAthlete2}
              />
            </div>

            {athlete1 && athlete2 && (
              <div className="flex items-center justify-between border-t pt-4">
                <div className="flex gap-2">
                  <Link
                    href={`/utover/${athlete1.id}`}
                    className="text-sm text-primary hover:underline"
                  >
                    Se {athlete1.first_name}
                  </Link>
                  <span className="text-muted-foreground">·</span>
                  <Link
                    href={`/utover/${athlete2.id}`}
                    className="text-sm text-primary hover:underline"
                  >
                    Se {athlete2.first_name}
                  </Link>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Tab selector */}
        {bothSelected && (
          <div className="flex gap-1 rounded-lg bg-muted p-1">
            <button
              onClick={() => setActiveTab("progresjon")}
              className={`flex-1 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                activeTab === "progresjon"
                  ? "bg-background shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Progresjon
            </button>
            <button
              onClick={() => setActiveTab("h2h")}
              className={`flex-1 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                activeTab === "h2h"
                  ? "bg-background shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Head to head
            </button>
          </div>
        )}

        {/* Loading state */}
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        )}

        {/* PROGRESSION TAB */}
        {bothSelected && !isLoading && activeTab === "progresjon" && (
          <>
            {commonEvents.length === 0 ? (
              <Card>
                <CardContent className="py-8 text-center text-sm text-muted-foreground">
                  Ingen felles øvelser funnet for disse utøverne.
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardHeader>
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <CardTitle>Progresjon etter alder</CardTitle>
                    <select
                      value={selectedEventId}
                      onChange={(e) => setSelectedEventId(e.target.value)}
                      className="h-8 w-full rounded border bg-transparent px-2 text-sm sm:w-[200px]"
                    >
                      {commonEvents.map((event) => (
                        <option key={event.id} value={event.id}>
                          {event.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </CardHeader>
                <CardContent>
                  {(!athlete1.birth_year || !athlete2.birth_year) ? (
                    <p className="text-sm text-muted-foreground py-4">
                      Mangler fødselsår for {!athlete1.birth_year ? name1 : ""}{!athlete1.birth_year && !athlete2.birth_year ? " og " : ""}{!athlete2.birth_year ? name2 : ""}. Kan ikke beregne alder.
                    </p>
                  ) : chartData.length === 0 ? (
                    <p className="text-sm text-muted-foreground py-4">
                      Ingen data for valgt øvelse.
                    </p>
                  ) : (
                    <>
                      <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart
                            data={chartData}
                            margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
                          >
                            <CartesianGrid strokeDasharray="3 3" stroke="var(--border-default, #e5e7eb)" />
                            <XAxis
                              dataKey="age"
                              label={{ value: "Alder", position: "insideBottom", offset: -3, style: { fontSize: 12, fill: "var(--text-muted, #6b7280)" } }}
                              tick={{ fill: "var(--text-muted, #6b7280)", fontSize: 11 }}
                              axisLine={{ stroke: "var(--border-default, #e5e7eb)" }}
                            />
                            <YAxis
                              reversed={resultType === "time"}
                              domain={yDomain}
                              tickFormatter={(value) => formatPerformanceValue(value, resultType)}
                              tick={{ fill: "var(--text-muted, #6b7280)", fontSize: 11 }}
                              axisLine={{ stroke: "var(--border-default, #e5e7eb)" }}
                              width={55}
                            />
                            <Tooltip
                              content={({ active, payload }) => {
                                if (active && payload && payload.length) {
                                  const data = payload[0].payload
                                  return (
                                    <div className="rounded border bg-background px-3 py-2 shadow-sm text-sm">
                                      <div className="font-semibold mb-1">{data.age} år</div>
                                      {data.value1 !== null && (
                                        <div className="flex items-center gap-2">
                                          <span className="inline-block h-2 w-2 rounded-full" style={{ backgroundColor: "#2563eb" }} />
                                          <span>{name1}: </span>
                                          <span className="font-mono">{formatPerformance(data.perf1, resultType)}</span>
                                        </div>
                                      )}
                                      {data.value2 !== null && (
                                        <div className="flex items-center gap-2">
                                          <span className="inline-block h-2 w-2 rounded-full" style={{ backgroundColor: "#dc2626" }} />
                                          <span>{name2}: </span>
                                          <span className="font-mono">{formatPerformance(data.perf2, resultType)}</span>
                                        </div>
                                      )}
                                    </div>
                                  )
                                }
                                return null
                              }}
                            />
                            <Legend
                              formatter={(value) => {
                                if (value === "value1") return name1
                                if (value === "value2") return name2
                                return value
                              }}
                            />
                            <Line
                              type="monotone"
                              dataKey="value1"
                              name="value1"
                              stroke="#2563eb"
                              strokeWidth={2}
                              dot={{ fill: "#2563eb", strokeWidth: 2, r: 3 }}
                              connectNulls={false}
                            />
                            <Line
                              type="monotone"
                              dataKey="value2"
                              name="value2"
                              stroke="#dc2626"
                              strokeWidth={2}
                              dot={{ fill: "#dc2626", strokeWidth: 2, r: 3 }}
                              connectNulls={false}
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>

                      {/* Data table */}
                      <div className="mt-6 overflow-x-auto border-t pt-4">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b text-left">
                              <th className="pb-2 pr-4 font-medium text-muted-foreground">Alder</th>
                              <th className="pb-2 pr-4 font-medium" style={{ color: "#2563eb" }}>{name1}</th>
                              <th className="pb-2 font-medium" style={{ color: "#dc2626" }}>{name2}</th>
                            </tr>
                          </thead>
                          <tbody>
                            {chartData.map((row) => (
                              <tr key={row.age} className="border-b last:border-0">
                                <td className="py-1.5 pr-4 tabular-nums text-muted-foreground">{row.age}</td>
                                <td className="py-1.5 pr-4 font-mono tabular-nums">
                                  {row.perf1 ? formatPerformance(row.perf1, resultType) : "–"}
                                </td>
                                <td className="py-1.5 font-mono tabular-nums">
                                  {row.perf2 ? formatPerformance(row.perf2, resultType) : "–"}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </>
                  )}
                </CardContent>
              </Card>
            )}
          </>
        )}

        {/* HEAD TO HEAD TAB */}
        {bothSelected && !isLoading && activeTab === "h2h" && (
          <>
            {h2hMeetings.length === 0 ? (
              <Card>
                <CardContent className="py-8 text-center text-sm text-muted-foreground">
                  Ingen direkte møter funnet mellom disse utøverne.
                </CardContent>
              </Card>
            ) : (
              <>
                {/* Event filter */}
                <div className="flex items-center gap-3">
                  <select
                    value={h2hEventId}
                    onChange={(e) => setH2hEventId(e.target.value)}
                    className="h-8 rounded border bg-transparent px-2 text-sm"
                  >
                    <option value="all">Alle øvelser ({h2hMeetings.length})</option>
                    {h2hEvents.map((ev) => (
                      <option key={ev.id} value={ev.id}>
                        {ev.name} ({ev.count})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Scoreboard */}
                <Card>
                  <CardContent className="py-6">
                    <div className="flex items-center justify-center gap-6 sm:gap-12">
                      {/* Athlete 1 */}
                      <div className="flex flex-col items-center gap-1 min-w-0 flex-1">
                        <span className="text-sm font-medium truncate max-w-full">{name1}</span>
                        <span
                          className={`text-4xl font-bold tabular-nums sm:text-5xl ${
                            h2hScore.wins1 > h2hScore.wins2 ? "text-[#2563eb]" : "text-foreground"
                          }`}
                        >
                          {h2hScore.wins1}
                        </span>
                        {h2hScore.wins1 > h2hScore.wins2 && (
                          <Trophy className="h-4 w-4 text-[#2563eb]" />
                        )}
                      </div>

                      {/* Divider */}
                      <div className="flex flex-col items-center gap-1">
                        <span className="text-xs text-muted-foreground uppercase tracking-wider">Seire</span>
                        <span className="text-2xl font-light text-muted-foreground">–</span>
                        <span className="text-xs text-muted-foreground">
                          {filteredH2hMeetings.length} møter
                        </span>
                      </div>

                      {/* Athlete 2 */}
                      <div className="flex flex-col items-center gap-1 min-w-0 flex-1">
                        <span className="text-sm font-medium truncate max-w-full">{name2}</span>
                        <span
                          className={`text-4xl font-bold tabular-nums sm:text-5xl ${
                            h2hScore.wins2 > h2hScore.wins1 ? "text-[#dc2626]" : "text-foreground"
                          }`}
                        >
                          {h2hScore.wins2}
                        </span>
                        {h2hScore.wins2 > h2hScore.wins1 && (
                          <Trophy className="h-4 w-4 text-[#dc2626]" />
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Meeting list */}
                <Card>
                  <CardHeader>
                    <CardTitle>Konkurranser</CardTitle>
                  </CardHeader>
                  <CardContent className="p-0">
                    <div className="divide-y">
                      {filteredH2hMeetings.map((meeting, i) => (
                        <div key={`${meeting.meet_id}-${meeting.event_id}-${meeting.round}-${i}`} className="px-4 py-3 sm:px-6">
                          {/* Meet info */}
                          <div className="mb-2 flex flex-wrap items-baseline gap-x-2 text-xs text-muted-foreground">
                            <span className="font-medium text-foreground text-sm">{meeting.meet_name}</span>
                            <span>{meeting.date}</span>
                            {meeting.event_name && h2hEventId === "all" && (
                              <span className="rounded bg-muted px-1.5 py-0.5">{meeting.event_name}</span>
                            )}
                            {meeting.round && (
                              <span>{formatRound(meeting.round)}</span>
                            )}
                          </div>

                          {/* Results row */}
                          <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-2 text-sm">
                            {/* Athlete 1 result */}
                            <div
                              className={`flex items-center gap-2 rounded px-2 py-1 ${
                                meeting.winner === 1 ? "bg-[#2563eb]/10 font-semibold" : ""
                              }`}
                            >
                              {meeting.athlete1.place && (
                                <span className="text-muted-foreground text-xs w-4 text-right">{meeting.athlete1.place}.</span>
                              )}
                              <span className="font-mono tabular-nums">
                                {formatPerformance(meeting.athlete1.performance, meeting.result_type)}
                              </span>
                            </div>

                            {/* VS */}
                            <span className="text-xs text-muted-foreground">vs</span>

                            {/* Athlete 2 result */}
                            <div
                              className={`flex items-center justify-end gap-2 rounded px-2 py-1 ${
                                meeting.winner === 2 ? "bg-[#dc2626]/10 font-semibold" : ""
                              }`}
                            >
                              <span className="font-mono tabular-nums">
                                {formatPerformance(meeting.athlete2.performance, meeting.result_type)}
                              </span>
                              {meeting.athlete2.place && (
                                <span className="text-muted-foreground text-xs w-4">{meeting.athlete2.place}.</span>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </>
        )}
      </div>
    </div>
  )
}
