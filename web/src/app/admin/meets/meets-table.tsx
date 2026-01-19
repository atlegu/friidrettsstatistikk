"use client"

import { useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"
import { createClient } from "@/lib/supabase/client"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Search, ChevronLeft, ChevronRight, Pencil, X, Check, Loader2, Trash2 } from "lucide-react"
import Link from "next/link"

type Meet = {
  id: string
  name: string
  start_date: string
  end_date: string | null
  city: string
  venue: string | null
  country: string | null
  indoor: boolean
  level: string | null
}

type MeetsTableProps = {
  initialSearch: string
  initialYear: string
  initialIndoor: string
}

const PAGE_SIZE = 50

export function MeetsTable({
  initialSearch,
  initialYear,
  initialIndoor,
}: MeetsTableProps) {
  const router = useRouter()
  const supabase = createClient()

  const [meets, setMeets] = useState<Meet[]>([])
  const [loading, setLoading] = useState(true)
  const [totalCount, setTotalCount] = useState(0)
  const [page, setPage] = useState(0)

  const [search, setSearch] = useState(initialSearch)
  const [yearFilter, setYearFilter] = useState(initialYear)
  const [indoorFilter, setIndoorFilter] = useState(initialIndoor)

  const [editingId, setEditingId] = useState<string | null>(null)
  const [editForm, setEditForm] = useState<Partial<Meet>>({})
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState<string | null>(null)

  const currentYear = new Date().getFullYear()
  const years = Array.from({ length: 30 }, (_, i) => currentYear - i)

  const fetchMeets = useCallback(async () => {
    setLoading(true)

    let query = supabase
      .from("meets")
      .select("id, name, start_date, end_date, city, venue, country, indoor, level", { count: "exact" })

    if (search) {
      query = query.or(`name.ilike.%${search}%,city.ilike.%${search}%,venue.ilike.%${search}%`)
    }

    if (yearFilter) {
      query = query
        .gte("start_date", `${yearFilter}-01-01`)
        .lte("start_date", `${yearFilter}-12-31`)
    }

    if (indoorFilter === "true") {
      query = query.eq("indoor", true)
    } else if (indoorFilter === "false") {
      query = query.eq("indoor", false)
    }

    const { data, count, error } = await query
      .order("start_date", { ascending: false })
      .range(page * PAGE_SIZE, (page + 1) * PAGE_SIZE - 1)

    if (error) {
      console.error("Error fetching meets:", error)
    } else {
      setMeets(data ?? [])
      setTotalCount(count ?? 0)
    }

    setLoading(false)
  }, [supabase, search, yearFilter, indoorFilter, page])

  useEffect(() => {
    fetchMeets()
  }, [fetchMeets])

  // Update URL params when filters change
  useEffect(() => {
    const params = new URLSearchParams()
    if (search) params.set("search", search)
    if (yearFilter) params.set("year", yearFilter)
    if (indoorFilter) params.set("indoor", indoorFilter)

    const newUrl = params.toString() ? `?${params.toString()}` : "/admin/meets"
    router.replace(newUrl, { scroll: false })
  }, [search, yearFilter, indoorFilter, router])

  const handleSearch = (value: string) => {
    setSearch(value)
    setPage(0)
  }

  const startEditing = (meet: Meet) => {
    setEditingId(meet.id)
    setEditForm({
      name: meet.name,
      start_date: meet.start_date,
      end_date: meet.end_date,
      city: meet.city,
      venue: meet.venue,
      country: meet.country,
      indoor: meet.indoor,
    })
  }

  const cancelEditing = () => {
    setEditingId(null)
    setEditForm({})
  }

  const saveMeet = async () => {
    if (!editingId) return

    setSaving(true)

    const { error } = await supabase
      .from("meets")
      .update({
        name: editForm.name,
        start_date: editForm.start_date,
        end_date: editForm.end_date || null,
        city: editForm.city,
        venue: editForm.venue || null,
        country: editForm.country || null,
        indoor: editForm.indoor,
        updated_at: new Date().toISOString(),
      })
      .eq("id", editingId)

    if (error) {
      console.error("Error saving meet:", error)
      alert("Kunne ikke lagre endringer: " + error.message)
    } else {
      setEditingId(null)
      setEditForm({})
      fetchMeets()
    }

    setSaving(false)
  }

  const deleteMeet = async (id: string) => {
    if (!confirm("Er du sikker på at du vil slette dette stevnet? Alle tilhørende resultater vil også bli slettet!")) return

    setDeleting(id)

    const { error } = await supabase
      .from("meets")
      .delete()
      .eq("id", id)

    if (error) {
      console.error("Error deleting meet:", error)
      alert("Kunne ikke slette: " + error.message)
    } else {
      fetchMeets()
    }

    setDeleting(null)
  }

  const totalPages = Math.ceil(totalCount / PAGE_SIZE)

  return (
    <div className="space-y-4">
      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-4">
            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Søk etter navn, by eller arena..."
                value={search}
                onChange={(e) => handleSearch(e.target.value)}
                className="pl-9"
              />
            </div>

            <select
              value={yearFilter}
              onChange={(e) => {
                setYearFilter(e.target.value)
                setPage(0)
              }}
              className="h-10 rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="">Alle år</option>
              {years.map((year) => (
                <option key={year} value={year}>
                  {year}
                </option>
              ))}
            </select>

            <select
              value={indoorFilter}
              onChange={(e) => {
                setIndoorFilter(e.target.value)
                setPage(0)
              }}
              className="h-10 rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="">Inne/Ute</option>
              <option value="true">Innendørs</option>
              <option value="false">Utendørs</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Results count */}
      <div className="text-sm text-muted-foreground">
        {totalCount.toLocaleString("no-NO")} stevner funnet
      </div>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center p-8">
              <Loader2 className="h-6 w-6 animate-spin" />
            </div>
          ) : meets.length === 0 ? (
            <p className="p-8 text-center text-muted-foreground">
              Ingen stevner funnet
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="px-4 py-3 text-left text-sm font-medium">Navn</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Dato</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">By</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Arena</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Type</th>
                    <th className="px-4 py-3 text-right text-sm font-medium">Handlinger</th>
                  </tr>
                </thead>
                <tbody>
                  {meets.map((meet) => (
                    <tr
                      key={meet.id}
                      className="border-b last:border-0 hover:bg-muted/30"
                    >
                      {editingId === meet.id ? (
                        <>
                          <td className="px-4 py-2">
                            <Input
                              value={editForm.name ?? ""}
                              onChange={(e) =>
                                setEditForm({ ...editForm, name: e.target.value })
                              }
                              placeholder="Navn"
                              className="h-8"
                            />
                          </td>
                          <td className="px-4 py-2">
                            <Input
                              type="date"
                              value={editForm.start_date ?? ""}
                              onChange={(e) =>
                                setEditForm({ ...editForm, start_date: e.target.value })
                              }
                              className="h-8 w-36"
                            />
                          </td>
                          <td className="px-4 py-2">
                            <Input
                              value={editForm.city ?? ""}
                              onChange={(e) =>
                                setEditForm({ ...editForm, city: e.target.value })
                              }
                              placeholder="By"
                              className="h-8 w-28"
                            />
                          </td>
                          <td className="px-4 py-2">
                            <Input
                              value={editForm.venue ?? ""}
                              onChange={(e) =>
                                setEditForm({ ...editForm, venue: e.target.value })
                              }
                              placeholder="Arena"
                              className="h-8 w-32"
                            />
                          </td>
                          <td className="px-4 py-2">
                            <select
                              value={editForm.indoor ? "true" : "false"}
                              onChange={(e) =>
                                setEditForm({ ...editForm, indoor: e.target.value === "true" })
                              }
                              className="h-8 rounded-md border border-input bg-background px-2 text-sm"
                            >
                              <option value="false">Ute</option>
                              <option value="true">Inne</option>
                            </select>
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
                                onClick={saveMeet}
                                disabled={saving}
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
                            <Link
                              href={`/stevner/${meet.id}`}
                              className="font-medium hover:underline"
                            >
                              {meet.name}
                            </Link>
                          </td>
                          <td className="px-4 py-3 text-sm">
                            {meet.start_date}
                            {meet.end_date && meet.end_date !== meet.start_date && (
                              <span className="text-muted-foreground"> – {meet.end_date}</span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-sm">
                            {meet.city}
                          </td>
                          <td className="px-4 py-3 text-sm text-muted-foreground">
                            {meet.venue ?? "-"}
                          </td>
                          <td className="px-4 py-3 text-sm">
                            <span className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${
                              meet.indoor
                                ? "bg-blue-100 text-blue-800"
                                : "bg-green-100 text-green-800"
                            }`}>
                              {meet.indoor ? "Inne" : "Ute"}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-right">
                            <div className="flex justify-end gap-1">
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => startEditing(meet)}
                              >
                                <Pencil className="h-4 w-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => deleteMeet(meet.id)}
                                disabled={deleting === meet.id}
                                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                              >
                                {deleting === meet.id ? (
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
