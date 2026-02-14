"use client"

import { useState, useEffect, useRef } from "react"
import { useRouter } from "next/navigation"
import { Search, X } from "lucide-react"
import { createClient } from "@/lib/supabase/client"
import { Input } from "@/components/ui/input"

interface Club {
  id: string
  name: string
  short_name: string | null
}

export function ClubFilter({
  championshipId,
  currentParams,
  selectedClubName,
}: {
  championshipId: string
  currentParams: Record<string, string>
  selectedClubName: string | null
}) {
  const router = useRouter()
  const supabase = createClient()
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<Club[]>([])
  const [loading, setLoading] = useState(false)
  const [showResults, setShowResults] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (query.length < 2) {
      setResults([])
      return
    }

    const timer = setTimeout(async () => {
      setLoading(true)
      const { data } = await supabase
        .from("clubs")
        .select("id, name, short_name")
        .or(`name.ilike.%${query}%,short_name.ilike.%${query}%`)
        .order("name")
        .limit(10)
      setResults(data ?? [])
      setLoading(false)
    }, 250)

    return () => clearTimeout(timer)
  }, [query])

  // Close dropdown on click outside
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setShowResults(false)
      }
    }
    document.addEventListener("mousedown", handleClick)
    return () => document.removeEventListener("mousedown", handleClick)
  }, [])

  function navigate(clubId?: string) {
    const p = new URLSearchParams()
    for (const [key, val] of Object.entries(currentParams)) {
      if (key !== "club" && val) p.set(key, val)
    }
    if (clubId) p.set("club", clubId)
    router.push(`/mesterskap/${championshipId}?${p.toString()}`)
  }

  if (selectedClubName) {
    return (
      <div className="flex items-center gap-2 rounded-md border bg-muted/50 px-2 py-1.5 text-sm">
        <span className="flex-1 truncate">{selectedClubName}</span>
        <button
          onClick={() => navigate()}
          className="shrink-0 rounded p-0.5 hover:bg-muted"
        >
          <X className="h-3.5 w-3.5 text-muted-foreground" />
        </button>
      </div>
    )
  }

  return (
    <div ref={containerRef} className="relative">
      <Search className="absolute left-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
      <Input
        placeholder="Søk klubb..."
        value={query}
        onChange={(e) => {
          setQuery(e.target.value)
          setShowResults(true)
        }}
        onFocus={() => setShowResults(true)}
        className="h-8 pl-7 text-sm"
      />
      {showResults && query.length >= 2 && (
        <div className="absolute z-10 mt-1 w-full rounded-md border bg-background shadow-lg">
          {loading ? (
            <div className="p-2 text-center text-xs text-muted-foreground">Søker...</div>
          ) : results.length > 0 ? (
            <ul className="max-h-48 overflow-auto py-1">
              {results.map((club) => (
                <li key={club.id}>
                  <button
                    className="w-full px-2 py-1.5 text-left text-sm hover:bg-muted"
                    onClick={() => {
                      navigate(club.id)
                      setQuery("")
                      setShowResults(false)
                    }}
                  >
                    {club.name}
                    {club.short_name && club.short_name !== club.name && (
                      <span className="ml-1 text-xs text-muted-foreground">({club.short_name})</span>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <div className="p-2 text-center text-xs text-muted-foreground">Ingen treff</div>
          )}
        </div>
      )}
    </div>
  )
}
