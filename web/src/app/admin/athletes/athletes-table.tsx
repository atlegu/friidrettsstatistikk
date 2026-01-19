"use client"

import { useState, useEffect, useCallback } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { createClient } from "@/lib/supabase/client"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Search, ChevronLeft, ChevronRight, Pencil, X, Check, Loader2 } from "lucide-react"
import Link from "next/link"

type Club = {
  id: string
  name: string
}

type Athlete = {
  id: string
  first_name: string
  last_name: string
  full_name: string | null
  gender: string | null
  birth_date: string | null
  birth_year: number | null
  nationality: string | null
  current_club_id: string | null
  external_id: string | null
  isonen_id: string | null
  verified: boolean | null
  clubs: { name: string } | null
}

type AthletesTableProps = {
  clubs: Club[]
  initialSearch: string
  initialClub: string
  initialGender: string
}

const PAGE_SIZE = 50

export function AthletesTable({
  clubs,
  initialSearch,
  initialClub,
  initialGender,
}: AthletesTableProps) {
  const router = useRouter()
  const searchParams = useSearchParams()
  const supabase = createClient()

  const [athletes, setAthletes] = useState<Athlete[]>([])
  const [loading, setLoading] = useState(true)
  const [totalCount, setTotalCount] = useState(0)
  const [page, setPage] = useState(0)

  const [search, setSearch] = useState(initialSearch)
  const [clubFilter, setClubFilter] = useState(initialClub)
  const [genderFilter, setGenderFilter] = useState(initialGender)

  const [editingId, setEditingId] = useState<string | null>(null)
  const [editForm, setEditForm] = useState<Partial<Athlete>>({})
  const [saving, setSaving] = useState(false)

  const fetchAthletes = useCallback(async () => {
    setLoading(true)

    let query = supabase
      .from("athletes")
      .select("*, clubs(name)", { count: "exact" })

    if (search) {
      query = query.or(`full_name.ilike.%${search}%,first_name.ilike.%${search}%,last_name.ilike.%${search}%`)
    }

    if (clubFilter) {
      query = query.eq("current_club_id", clubFilter)
    }

    if (genderFilter) {
      query = query.eq("gender", genderFilter)
    }

    const { data, count, error } = await query
      .order("full_name")
      .range(page * PAGE_SIZE, (page + 1) * PAGE_SIZE - 1)

    if (error) {
      console.error("Error fetching athletes:", error)
    } else {
      setAthletes(data ?? [])
      setTotalCount(count ?? 0)
    }

    setLoading(false)
  }, [supabase, search, clubFilter, genderFilter, page])

  useEffect(() => {
    fetchAthletes()
  }, [fetchAthletes])

  // Update URL params when filters change
  useEffect(() => {
    const params = new URLSearchParams()
    if (search) params.set("search", search)
    if (clubFilter) params.set("club", clubFilter)
    if (genderFilter) params.set("gender", genderFilter)

    const newUrl = params.toString() ? `?${params.toString()}` : "/admin/athletes"
    router.replace(newUrl, { scroll: false })
  }, [search, clubFilter, genderFilter, router])

  const handleSearch = (value: string) => {
    setSearch(value)
    setPage(0)
  }

  const startEditing = (athlete: Athlete) => {
    setEditingId(athlete.id)
    setEditForm({
      first_name: athlete.first_name,
      last_name: athlete.last_name,
      gender: athlete.gender,
      birth_date: athlete.birth_date,
      birth_year: athlete.birth_year,
      nationality: athlete.nationality,
      current_club_id: athlete.current_club_id,
    })
  }

  const cancelEditing = () => {
    setEditingId(null)
    setEditForm({})
  }

  const saveAthlete = async () => {
    if (!editingId) return

    setSaving(true)

    const { error } = await supabase
      .from("athletes")
      .update({
        first_name: editForm.first_name,
        last_name: editForm.last_name,
        full_name: `${editForm.first_name} ${editForm.last_name}`,
        gender: editForm.gender,
        birth_date: editForm.birth_date || null,
        birth_year: editForm.birth_year || null,
        nationality: editForm.nationality || null,
        current_club_id: editForm.current_club_id || null,
        updated_at: new Date().toISOString(),
      })
      .eq("id", editingId)

    if (error) {
      console.error("Error saving athlete:", error)
      alert("Kunne ikke lagre endringer: " + error.message)
    } else {
      setEditingId(null)
      setEditForm({})
      fetchAthletes()
    }

    setSaving(false)
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
                placeholder="Søk etter navn..."
                value={search}
                onChange={(e) => handleSearch(e.target.value)}
                className="pl-9"
              />
            </div>

            <select
              value={clubFilter}
              onChange={(e) => {
                setClubFilter(e.target.value)
                setPage(0)
              }}
              className="h-10 rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="">Alle klubber</option>
              {clubs.map((club) => (
                <option key={club.id} value={club.id}>
                  {club.name}
                </option>
              ))}
            </select>

            <select
              value={genderFilter}
              onChange={(e) => {
                setGenderFilter(e.target.value)
                setPage(0)
              }}
              className="h-10 rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="">Alle kjønn</option>
              <option value="M">Menn</option>
              <option value="K">Kvinner</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Results count */}
      <div className="text-sm text-muted-foreground">
        {totalCount.toLocaleString("no-NO")} utøvere funnet
      </div>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center p-8">
              <Loader2 className="h-6 w-6 animate-spin" />
            </div>
          ) : athletes.length === 0 ? (
            <p className="p-8 text-center text-muted-foreground">
              Ingen utøvere funnet
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="px-4 py-3 text-left text-sm font-medium">Navn</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Kjønn</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Født</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Klubb</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Land</th>
                    <th className="px-4 py-3 text-right text-sm font-medium">Handlinger</th>
                  </tr>
                </thead>
                <tbody>
                  {athletes.map((athlete) => (
                    <tr
                      key={athlete.id}
                      className="border-b last:border-0 hover:bg-muted/30"
                    >
                      {editingId === athlete.id ? (
                        <>
                          <td className="px-4 py-2">
                            <div className="flex gap-2">
                              <Input
                                value={editForm.first_name ?? ""}
                                onChange={(e) =>
                                  setEditForm({ ...editForm, first_name: e.target.value })
                                }
                                placeholder="Fornavn"
                                className="h-8 w-28"
                              />
                              <Input
                                value={editForm.last_name ?? ""}
                                onChange={(e) =>
                                  setEditForm({ ...editForm, last_name: e.target.value })
                                }
                                placeholder="Etternavn"
                                className="h-8 w-28"
                              />
                            </div>
                          </td>
                          <td className="px-4 py-2">
                            <select
                              value={editForm.gender ?? ""}
                              onChange={(e) =>
                                setEditForm({ ...editForm, gender: e.target.value })
                              }
                              className="h-8 rounded-md border border-input bg-background px-2 text-sm"
                            >
                              <option value="">-</option>
                              <option value="M">M</option>
                              <option value="K">K</option>
                            </select>
                          </td>
                          <td className="px-4 py-2">
                            <Input
                              type="number"
                              value={editForm.birth_year ?? ""}
                              onChange={(e) =>
                                setEditForm({
                                  ...editForm,
                                  birth_year: e.target.value ? parseInt(e.target.value) : null,
                                })
                              }
                              placeholder="År"
                              className="h-8 w-20"
                            />
                          </td>
                          <td className="px-4 py-2">
                            <select
                              value={editForm.current_club_id ?? ""}
                              onChange={(e) =>
                                setEditForm({ ...editForm, current_club_id: e.target.value || null })
                              }
                              className="h-8 rounded-md border border-input bg-background px-2 text-sm max-w-[150px]"
                            >
                              <option value="">Ingen klubb</option>
                              {clubs.map((club) => (
                                <option key={club.id} value={club.id}>
                                  {club.name}
                                </option>
                              ))}
                            </select>
                          </td>
                          <td className="px-4 py-2">
                            <Input
                              value={editForm.nationality ?? ""}
                              onChange={(e) =>
                                setEditForm({ ...editForm, nationality: e.target.value })
                              }
                              placeholder="NOR"
                              className="h-8 w-16"
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
                                onClick={saveAthlete}
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
                              href={`/utover/${athlete.id}`}
                              className="font-medium hover:underline"
                            >
                              {athlete.full_name || `${athlete.first_name} ${athlete.last_name}`}
                            </Link>
                          </td>
                          <td className="px-4 py-3 text-sm">
                            {athlete.gender === "M" ? "Mann" : athlete.gender === "K" ? "Kvinne" : "-"}
                          </td>
                          <td className="px-4 py-3 text-sm">
                            {athlete.birth_year ?? "-"}
                          </td>
                          <td className="px-4 py-3 text-sm">
                            {athlete.clubs?.name ?? "-"}
                          </td>
                          <td className="px-4 py-3 text-sm">
                            {athlete.nationality ?? "-"}
                          </td>
                          <td className="px-4 py-3 text-right">
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => startEditing(athlete)}
                            >
                              <Pencil className="h-4 w-4" />
                            </Button>
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
