"use client"

import { useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"
import { createClient } from "@/lib/supabase/client"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Search, ChevronLeft, ChevronRight, Pencil, X, Check, Loader2, Trash2 } from "lucide-react"
import Link from "next/link"

type Club = {
  id: string
  name: string
  short_name: string | null
  city: string | null
  county: string | null
  website: string | null
  active: boolean | null
}

type ClubsTableProps = {
  initialSearch: string
}

const PAGE_SIZE = 50

export function ClubsTable({ initialSearch }: ClubsTableProps) {
  const router = useRouter()
  const supabase = createClient()

  const [clubs, setClubs] = useState<Club[]>([])
  const [loading, setLoading] = useState(true)
  const [totalCount, setTotalCount] = useState(0)
  const [page, setPage] = useState(0)

  const [search, setSearch] = useState(initialSearch)

  const [editingId, setEditingId] = useState<string | null>(null)
  const [editForm, setEditForm] = useState<Partial<Club>>({})
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState<string | null>(null)

  const fetchClubs = useCallback(async () => {
    setLoading(true)

    let query = supabase
      .from("clubs")
      .select("id, name, short_name, city, county, website, active", { count: "exact" })

    if (search) {
      query = query.or(`name.ilike.%${search}%,short_name.ilike.%${search}%,city.ilike.%${search}%`)
    }

    const { data, count, error } = await query
      .order("name")
      .range(page * PAGE_SIZE, (page + 1) * PAGE_SIZE - 1)

    if (error) {
      console.error("Error fetching clubs:", error)
    } else {
      setClubs(data ?? [])
      setTotalCount(count ?? 0)
    }

    setLoading(false)
  }, [supabase, search, page])

  useEffect(() => {
    fetchClubs()
  }, [fetchClubs])

  // Update URL params when filters change
  useEffect(() => {
    const params = new URLSearchParams()
    if (search) params.set("search", search)

    const newUrl = params.toString() ? `?${params.toString()}` : "/admin/clubs"
    router.replace(newUrl, { scroll: false })
  }, [search, router])

  const handleSearch = (value: string) => {
    setSearch(value)
    setPage(0)
  }

  const startEditing = (club: Club) => {
    setEditingId(club.id)
    setEditForm({
      name: club.name,
      short_name: club.short_name,
      city: club.city,
      county: club.county,
      website: club.website,
      active: club.active,
    })
  }

  const cancelEditing = () => {
    setEditingId(null)
    setEditForm({})
  }

  const saveClub = async () => {
    if (!editingId) return

    setSaving(true)

    const { error } = await supabase
      .from("clubs")
      .update({
        name: editForm.name,
        short_name: editForm.short_name || null,
        city: editForm.city || null,
        county: editForm.county || null,
        website: editForm.website || null,
        active: editForm.active,
        updated_at: new Date().toISOString(),
      })
      .eq("id", editingId)

    if (error) {
      console.error("Error saving club:", error)
      alert("Kunne ikke lagre endringer: " + error.message)
    } else {
      setEditingId(null)
      setEditForm({})
      fetchClubs()
    }

    setSaving(false)
  }

  const deleteClub = async (id: string) => {
    if (!confirm("Er du sikker på at du vil slette denne klubben? Utøvere knyttet til klubben vil miste klubbtilhørighet.")) return

    setDeleting(id)

    const { error } = await supabase
      .from("clubs")
      .delete()
      .eq("id", id)

    if (error) {
      console.error("Error deleting club:", error)
      alert("Kunne ikke slette: " + error.message)
    } else {
      fetchClubs()
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
                placeholder="Søk etter navn eller by..."
                value={search}
                onChange={(e) => handleSearch(e.target.value)}
                className="pl-9"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results count */}
      <div className="text-sm text-muted-foreground">
        {totalCount.toLocaleString("no-NO")} klubber funnet
      </div>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center p-8">
              <Loader2 className="h-6 w-6 animate-spin" />
            </div>
          ) : clubs.length === 0 ? (
            <p className="p-8 text-center text-muted-foreground">
              Ingen klubber funnet
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="px-4 py-3 text-left text-sm font-medium">Navn</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Kortnavn</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">By</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Fylke</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                    <th className="px-4 py-3 text-right text-sm font-medium">Handlinger</th>
                  </tr>
                </thead>
                <tbody>
                  {clubs.map((club) => (
                    <tr
                      key={club.id}
                      className="border-b last:border-0 hover:bg-muted/30"
                    >
                      {editingId === club.id ? (
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
                              value={editForm.short_name ?? ""}
                              onChange={(e) =>
                                setEditForm({ ...editForm, short_name: e.target.value })
                              }
                              placeholder="Kortnavn"
                              className="h-8 w-24"
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
                              value={editForm.county ?? ""}
                              onChange={(e) =>
                                setEditForm({ ...editForm, county: e.target.value })
                              }
                              placeholder="Fylke"
                              className="h-8 w-28"
                            />
                          </td>
                          <td className="px-4 py-2">
                            <select
                              value={editForm.active ? "true" : "false"}
                              onChange={(e) =>
                                setEditForm({ ...editForm, active: e.target.value === "true" })
                              }
                              className="h-8 rounded-md border border-input bg-background px-2 text-sm"
                            >
                              <option value="true">Aktiv</option>
                              <option value="false">Inaktiv</option>
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
                                onClick={saveClub}
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
                              href={`/klubber/${club.id}`}
                              className="font-medium hover:underline"
                            >
                              {club.name}
                            </Link>
                          </td>
                          <td className="px-4 py-3 text-sm text-muted-foreground">
                            {club.short_name ?? "-"}
                          </td>
                          <td className="px-4 py-3 text-sm">
                            {club.city ?? "-"}
                          </td>
                          <td className="px-4 py-3 text-sm text-muted-foreground">
                            {club.county ?? "-"}
                          </td>
                          <td className="px-4 py-3 text-sm">
                            <span className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${
                              club.active !== false
                                ? "bg-green-100 text-green-800"
                                : "bg-gray-100 text-gray-800"
                            }`}>
                              {club.active !== false ? "Aktiv" : "Inaktiv"}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-right">
                            <div className="flex justify-end gap-1">
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => startEditing(club)}
                              >
                                <Pencil className="h-4 w-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => deleteClub(club.id)}
                                disabled={deleting === club.id}
                                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                              >
                                {deleting === club.id ? (
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
