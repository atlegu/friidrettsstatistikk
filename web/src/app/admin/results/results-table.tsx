"use client"

import { useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"
import { createClient } from "@/lib/supabase/client"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Search, ChevronLeft, ChevronRight, Pencil, X, Check, Loader2, Trash2, Hash } from "lucide-react"
import Link from "next/link"
import { formatPerformance } from "@/lib/format-performance"

type Event = {
  id: string
  name: string
  code: string
}

type Athlete = {
  id: string
  full_name: string | null
}

type Result = {
  id: string
  athlete_id: string
  event_id: string
  meet_id: string
  performance: string
  performance_value: number | null
  date: string
  wind: number | null
  place: number | null
  status: string | null
  is_national_record: boolean | null
  athletes: { full_name: string | null } | null
  events: { name: string; code: string; result_type: string } | null
  meets: { name: string } | null
}

type ResultsTableProps = {
  events: Event[]
  athletes: Athlete[]
  initialSearch: string
  initialEvent: string
  initialAthleteId: string
}

const PAGE_SIZE = 50

export function ResultsTable({
  events,
  athletes,
  initialSearch,
  initialEvent,
  initialAthleteId,
}: ResultsTableProps) {
  const router = useRouter()
  const supabase = createClient()

  const [results, setResults] = useState<Result[]>([])
  const [loading, setLoading] = useState(true)
  const [totalCount, setTotalCount] = useState(0)
  const [page, setPage] = useState(0)

  const [search, setSearch] = useState(initialSearch)
  const [eventFilter, setEventFilter] = useState(initialEvent)
  const [athleteFilter, setAthleteFilter] = useState(initialAthleteId)
  const [dateFrom, setDateFrom] = useState("")
  const [dateTo, setDateTo] = useState("")
  const [resultIdSearch, setResultIdSearch] = useState("")

  const [editingId, setEditingId] = useState<string | null>(null)
  const [editForm, setEditForm] = useState<Partial<Result & { meet_id: string; event_id: string; date: string }>>({})
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState<string | null>(null)

  // Meet search for editing
  const [meetSearch, setMeetSearch] = useState("")
  const [meetResults, setMeetResults] = useState<{ id: string; name: string; city: string; start_date: string }[]>([])
  const [searchingMeets, setSearchingMeets] = useState(false)
  const [selectedMeetName, setSelectedMeetName] = useState<string | null>(null)

  // Athlete search for editing
  const [athleteSearch, setAthleteSearch] = useState("")
  const [athleteResults, setAthleteResults] = useState<Athlete[]>([])
  const [selectedAthleteName, setSelectedAthleteName] = useState<string | null>(null)

  const fetchResults = useCallback(async () => {
    setLoading(true)

    // If searching by result ID, fetch that specific result
    if (resultIdSearch.trim()) {
      const { data, error } = await supabase
        .from("results")
        .select(`
          id, athlete_id, event_id, meet_id, performance, performance_value,
          date, wind, place, status, is_national_record,
          athletes(full_name),
          events(name, code, result_type),
          meets(name)
        `)
        .eq("id", resultIdSearch.trim())

      if (!error && data) {
        setResults(data as unknown as Result[])
        setTotalCount(data.length)
      } else {
        setResults([])
        setTotalCount(0)
      }
      setLoading(false)
      return
    }

    let query = supabase
      .from("results")
      .select(`
        id, athlete_id, event_id, meet_id, performance, performance_value,
        date, wind, place, status, is_national_record,
        athletes(full_name),
        events(name, code, result_type),
        meets(name)
      `, { count: "exact" })

    if (eventFilter) {
      query = query.eq("event_id", eventFilter)
    }

    if (athleteFilter) {
      query = query.eq("athlete_id", athleteFilter)
    }

    if (dateFrom) {
      query = query.gte("date", dateFrom)
    }

    if (dateTo) {
      query = query.lte("date", dateTo)
    }

    const { data, count, error } = await query
      .order("date", { ascending: false })
      .range(page * PAGE_SIZE, (page + 1) * PAGE_SIZE - 1)

    if (error) {
      console.error("Error fetching results:", error)
    } else {
      // Cast to expected type (Supabase types don't infer joins correctly)
      const typedData = (data ?? []) as unknown as Result[]
      // Filter by search term on athlete name or meet name
      let filteredData = typedData
      if (search) {
        const searchLower = search.toLowerCase()
        filteredData = filteredData.filter(r =>
          r.athletes?.full_name?.toLowerCase().includes(searchLower) ||
          r.meets?.name?.toLowerCase().includes(searchLower)
        )
      }
      setResults(filteredData)
      setTotalCount(search ? filteredData.length : (count ?? 0))
    }

    setLoading(false)
  }, [supabase, search, eventFilter, athleteFilter, dateFrom, dateTo, resultIdSearch, page])

  useEffect(() => {
    fetchResults()
  }, [fetchResults])

  // Update URL params when filters change
  useEffect(() => {
    const params = new URLSearchParams()
    if (search) params.set("search", search)
    if (eventFilter) params.set("event", eventFilter)
    if (athleteFilter) params.set("athlete", athleteFilter)

    const newUrl = params.toString() ? `?${params.toString()}` : "/admin/results"
    router.replace(newUrl, { scroll: false })
  }, [search, eventFilter, athleteFilter, router])

  const handleSearch = (value: string) => {
    setSearch(value)
    setPage(0)
  }

  const searchMeets = async (query: string) => {
    if (query.length < 2) {
      setMeetResults([])
      return
    }
    setSearchingMeets(true)
    const { data } = await supabase
      .from("meets")
      .select("id, name, city, start_date")
      .or(`name.ilike.%${query}%,city.ilike.%${query}%`)
      .order("start_date", { ascending: false })
      .limit(10)
    setMeetResults(data ?? [])
    setSearchingMeets(false)
  }

  const searchAthletes = async (query: string) => {
    if (query.length < 2) {
      setAthleteResults([])
      return
    }
    const { data } = await supabase
      .from("athletes")
      .select("id, full_name")
      .or(`full_name.ilike.%${query}%,first_name.ilike.%${query}%,last_name.ilike.%${query}%`)
      .order("full_name")
      .limit(10)
    setAthleteResults(data ?? [])
  }

  const startEditing = (result: Result) => {
    setEditingId(result.id)
    setEditForm({
      performance: result.performance,
      wind: result.wind,
      place: result.place,
      athlete_id: result.athlete_id,
      meet_id: result.meet_id,
      event_id: result.event_id,
      date: result.date,
      is_national_record: result.is_national_record,
    })
    setSelectedMeetName(result.meets?.name ?? null)
    setSelectedAthleteName(result.athletes?.full_name ?? null)
    setMeetSearch("")
    setMeetResults([])
    setAthleteSearch("")
    setAthleteResults([])
  }

  const cancelEditing = () => {
    setEditingId(null)
    setEditForm({})
    setMeetSearch("")
    setMeetResults([])
    setSelectedMeetName(null)
    setAthleteSearch("")
    setAthleteResults([])
    setSelectedAthleteName(null)
  }

  const saveResult = async () => {
    if (!editingId) return

    setSaving(true)

    // Calculate performance_value if performance changed
    let performanceValue = null
    if (editForm.performance) {
      const perf = editForm.performance.replace(",", ".")
      // Check if it's a time format (contains : or multiple .)
      if (perf.includes(":")) {
        // Format like 1:42.58
        const [mins, secs] = perf.split(":")
        performanceValue = Math.round((parseFloat(mins) * 60 + parseFloat(secs)) * 1000)
      } else if (perf.split(".").length === 3) {
        // Format like 1.42.58 (min.sec.hundredths)
        const [mins, secs, hundredths] = perf.split(".").map(Number)
        performanceValue = Math.round((mins * 60 + secs + hundredths / 100) * 1000)
      } else {
        // Simple number like 10.45 or 8.23
        performanceValue = Math.round(parseFloat(perf) * 1000)
      }
    }

    const { error } = await supabase
      .from("results")
      .update({
        performance: editForm.performance,
        performance_value: performanceValue,
        wind: editForm.wind,
        place: editForm.place,
        athlete_id: editForm.athlete_id,
        meet_id: editForm.meet_id,
        event_id: editForm.event_id,
        date: editForm.date,
        is_national_record: editForm.is_national_record,
        updated_at: new Date().toISOString(),
      })
      .eq("id", editingId)

    if (error) {
      console.error("Error saving result:", error)
      alert("Kunne ikke lagre endringer: " + error.message)
    } else {
      setEditingId(null)
      setEditForm({})
      setMeetSearch("")
      setMeetResults([])
      setSelectedMeetName(null)
      setAthleteSearch("")
      setAthleteResults([])
      setSelectedAthleteName(null)
      fetchResults()
    }

    setSaving(false)
  }

  const deleteResult = async (id: string) => {
    if (!confirm("Er du sikker på at du vil slette dette resultatet?")) return

    setDeleting(id)

    const { error } = await supabase
      .from("results")
      .delete()
      .eq("id", id)

    if (error) {
      console.error("Error deleting result:", error)
      alert("Kunne ikke slette: " + error.message)
    } else {
      fetchResults()
    }

    setDeleting(null)
  }

  const totalPages = Math.ceil(totalCount / PAGE_SIZE)

  return (
    <div className="space-y-4">
      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="space-y-4">
            {/* Result ID Search */}
            <div className="flex gap-4">
              <div className="relative flex-1 max-w-[400px]">
                <Hash className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Søk på resultat-ID (UUID)..."
                  value={resultIdSearch}
                  onChange={(e) => {
                    setResultIdSearch(e.target.value)
                    setPage(0)
                  }}
                  className="pl-9 font-mono text-sm"
                />
              </div>
              {resultIdSearch && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setResultIdSearch("")}
                >
                  <X className="h-4 w-4 mr-1" />
                  Nullstill
                </Button>
              )}
            </div>

            {/* Main filters */}
            <div className="flex flex-wrap gap-4">
              <div className="relative flex-1 min-w-[200px]">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Søk etter utøver eller stevne..."
                  value={search}
                  onChange={(e) => handleSearch(e.target.value)}
                  className="pl-9"
                  disabled={!!resultIdSearch}
                />
              </div>

              <select
                value={eventFilter}
                onChange={(e) => {
                  setEventFilter(e.target.value)
                  setPage(0)
                }}
                className="h-10 rounded-md border border-input bg-background px-3 text-sm"
                disabled={!!resultIdSearch}
              >
                <option value="">Alle øvelser</option>
                {events.map((event) => (
                  <option key={event.id} value={event.id}>
                    {event.name}
                  </option>
                ))}
              </select>

              <select
                value={athleteFilter}
                onChange={(e) => {
                  setAthleteFilter(e.target.value)
                  setPage(0)
                }}
                className="h-10 rounded-md border border-input bg-background px-3 text-sm max-w-[200px]"
                disabled={!!resultIdSearch}
              >
                <option value="">Alle utøvere</option>
                {athletes.map((athlete) => (
                  <option key={athlete.id} value={athlete.id}>
                    {athlete.full_name}
                  </option>
                ))}
              </select>
            </div>

            {/* Date filters */}
            <div className="flex flex-wrap gap-4 items-center">
              <span className="text-sm text-muted-foreground">Datofilter:</span>
              <div className="flex items-center gap-2">
                <Input
                  type="date"
                  value={dateFrom}
                  onChange={(e) => {
                    setDateFrom(e.target.value)
                    setPage(0)
                  }}
                  className="h-10 w-40"
                  disabled={!!resultIdSearch}
                />
                <span className="text-muted-foreground">til</span>
                <Input
                  type="date"
                  value={dateTo}
                  onChange={(e) => {
                    setDateTo(e.target.value)
                    setPage(0)
                  }}
                  className="h-10 w-40"
                  disabled={!!resultIdSearch}
                />
              </div>
              {(dateFrom || dateTo) && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setDateFrom("")
                    setDateTo("")
                  }}
                >
                  <X className="h-4 w-4 mr-1" />
                  Nullstill datoer
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results count */}
      <div className="text-sm text-muted-foreground">
        {totalCount.toLocaleString("no-NO")} resultater funnet
      </div>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center p-8">
              <Loader2 className="h-6 w-6 animate-spin" />
            </div>
          ) : results.length === 0 ? (
            <p className="p-8 text-center text-muted-foreground">
              Ingen resultater funnet. Velg en øvelse eller utøver for å se resultater.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="px-4 py-3 text-left text-sm font-medium">ID</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Utøver</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Øvelse</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Resultat</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Vind</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Plass</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Stevne</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Dato</th>
                    <th className="px-4 py-3 text-right text-sm font-medium">Handlinger</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((result) => (
                    <tr
                      key={result.id}
                      className="border-b last:border-0 hover:bg-muted/30"
                    >
                      {editingId === result.id ? (
                        <>
                          <td className="px-4 py-2">
                            <code className="text-xs text-muted-foreground" title={result.id}>
                              {result.id.slice(0, 8)}...
                            </code>
                          </td>
                          <td className="px-4 py-2">
                            <div className="relative">
                              <Input
                                value={athleteSearch}
                                onChange={(e) => {
                                  setAthleteSearch(e.target.value)
                                  searchAthletes(e.target.value)
                                }}
                                placeholder={selectedAthleteName ?? "Søk utøver..."}
                                className="h-8 w-40 text-sm"
                              />
                              {athleteResults.length > 0 && (
                                <div className="absolute z-10 mt-1 w-64 bg-background border rounded-md shadow-lg max-h-48 overflow-y-auto">
                                  {athleteResults.map((athlete) => (
                                    <button
                                      key={athlete.id}
                                      onClick={() => {
                                        setEditForm({ ...editForm, athlete_id: athlete.id })
                                        setSelectedAthleteName(athlete.full_name)
                                        setAthleteSearch("")
                                        setAthleteResults([])
                                      }}
                                      className="w-full px-3 py-2 text-left text-sm hover:bg-muted/50"
                                    >
                                      {athlete.full_name}
                                    </button>
                                  ))}
                                </div>
                              )}
                            </div>
                          </td>
                          <td className="px-4 py-2">
                            <select
                              value={editForm.event_id ?? ""}
                              onChange={(e) =>
                                setEditForm({ ...editForm, event_id: e.target.value })
                              }
                              className="h-8 w-full rounded-md border border-input bg-background px-2 text-sm"
                            >
                              {events.map((event) => (
                                <option key={event.id} value={event.id}>
                                  {event.name}
                                </option>
                              ))}
                            </select>
                          </td>
                          <td className="px-4 py-2">
                            <Input
                              value={editForm.performance ?? ""}
                              onChange={(e) =>
                                setEditForm({ ...editForm, performance: e.target.value })
                              }
                              placeholder="Resultat"
                              className="h-8 w-24"
                            />
                          </td>
                          <td className="px-4 py-2">
                            <Input
                              type="number"
                              step="0.1"
                              value={editForm.wind ?? ""}
                              onChange={(e) =>
                                setEditForm({
                                  ...editForm,
                                  wind: e.target.value ? parseFloat(e.target.value) : null,
                                })
                              }
                              placeholder="Vind"
                              className="h-8 w-16"
                            />
                          </td>
                          <td className="px-4 py-2">
                            <Input
                              type="number"
                              value={editForm.place ?? ""}
                              onChange={(e) =>
                                setEditForm({
                                  ...editForm,
                                  place: e.target.value ? parseInt(e.target.value) : null,
                                })
                              }
                              placeholder="#"
                              className="h-8 w-14"
                            />
                          </td>
                          <td className="px-4 py-2">
                            <div className="relative">
                              <Input
                                value={meetSearch}
                                onChange={(e) => {
                                  setMeetSearch(e.target.value)
                                  searchMeets(e.target.value)
                                }}
                                placeholder={selectedMeetName ?? "Søk stevne..."}
                                className="h-8 w-40 text-sm"
                              />
                              {meetResults.length > 0 && (
                                <div className="absolute z-10 mt-1 w-64 bg-background border rounded-md shadow-lg max-h-48 overflow-y-auto">
                                  {meetResults.map((meet) => (
                                    <button
                                      key={meet.id}
                                      onClick={() => {
                                        setEditForm({ ...editForm, meet_id: meet.id })
                                        setSelectedMeetName(`${meet.name} (${meet.city})`)
                                        setMeetSearch("")
                                        setMeetResults([])
                                      }}
                                      className="w-full px-3 py-2 text-left text-sm hover:bg-muted/50"
                                    >
                                      <div className="font-medium">{meet.name}</div>
                                      <div className="text-xs text-muted-foreground">{meet.city} - {meet.start_date}</div>
                                    </button>
                                  ))}
                                </div>
                              )}
                            </div>
                          </td>
                          <td className="px-4 py-2">
                            <Input
                              type="date"
                              value={editForm.date ?? ""}
                              onChange={(e) =>
                                setEditForm({ ...editForm, date: e.target.value })
                              }
                              className="h-8 w-36"
                            />
                          </td>
                          <td className="px-4 py-2 text-right">
                            <div className="flex justify-end gap-1">
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={cancelEditing}
                                disabled={saving}
                              >
                                <X className="h-4 w-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={saveResult}
                                disabled={saving}
                                className="text-green-600 hover:text-green-700 hover:bg-green-50"
                              >
                                {saving ? (
                                  <Loader2 className="h-4 w-4 animate-spin" />
                                ) : (
                                  <Check className="h-4 w-4" />
                                )}
                              </Button>
                            </div>
                          </td>
                        </>
                      ) : (
                        <>
                          <td className="px-4 py-3">
                            <button
                              onClick={() => {
                                navigator.clipboard.writeText(result.id)
                              }}
                              className="cursor-pointer hover:bg-muted rounded px-1"
                              title={`Klikk for å kopiere: ${result.id}`}
                            >
                              <code className="text-xs text-muted-foreground">
                                {result.id.slice(0, 8)}...
                              </code>
                            </button>
                          </td>
                          <td className="px-4 py-3">
                            <Link
                              href={`/utover/${result.athlete_id}`}
                              className="font-medium hover:underline"
                            >
                              {result.athletes?.full_name ?? "-"}
                            </Link>
                          </td>
                          <td className="px-4 py-3 text-sm">
                            {result.events?.name ?? "-"}
                          </td>
                          <td className="px-4 py-3 text-sm font-mono">
                            {formatPerformance(result.performance, result.events?.result_type)}
                            {result.is_national_record && (
                              <span className="ml-1 text-xs text-red-600 font-bold">NR</span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-sm text-muted-foreground">
                            {result.wind != null ? `${result.wind > 0 ? "+" : ""}${result.wind}` : "-"}
                          </td>
                          <td className="px-4 py-3 text-sm">
                            {result.place ?? "-"}
                          </td>
                          <td className="px-4 py-3 text-sm">
                            <Link
                              href={`/stevner/${result.meet_id}`}
                              className="hover:underline"
                            >
                              {result.meets?.name ?? "-"}
                            </Link>
                          </td>
                          <td className="px-4 py-3 text-sm text-muted-foreground">
                            {result.date}
                          </td>
                          <td className="px-4 py-3 text-right">
                            <div className="flex justify-end gap-1">
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => startEditing(result)}
                              >
                                <Pencil className="h-4 w-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => deleteResult(result.id)}
                                disabled={deleting === result.id}
                                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                              >
                                {deleting === result.id ? (
                                  <Loader2 className="h-4 w-4 animate-spin" />
                                ) : (
                                  <Trash2 className="h-4 w-4" />
                                )}
                              </Button>
                            </div>
                          </td>
                        </>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            Side {page + 1} av {totalPages}
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(page - 1)}
              disabled={page === 0}
            >
              <ChevronLeft className="h-4 w-4" />
              Forrige
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(page + 1)}
              disabled={page >= totalPages - 1}
            >
              Neste
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
