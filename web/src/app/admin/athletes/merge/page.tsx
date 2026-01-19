"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { createClient } from "@/lib/supabase/client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Search, ArrowRight, Loader2, AlertTriangle, Check } from "lucide-react"
import Link from "next/link"

type Athlete = {
  id: string
  full_name: string | null
  first_name: string
  last_name: string
  birth_year: number | null
  gender: string | null
  clubs: { name: string } | null
}

type AthleteWithStats = Athlete & {
  resultsCount: number
}

export default function MergeAthletesPage() {
  const router = useRouter()
  const supabase = createClient()

  const [sourceSearch, setSourceSearch] = useState("")
  const [targetSearch, setTargetSearch] = useState("")
  const [sourceResults, setSourceResults] = useState<Athlete[]>([])
  const [targetResults, setTargetResults] = useState<Athlete[]>([])
  const [sourceAthlete, setSourceAthlete] = useState<AthleteWithStats | null>(null)
  const [targetAthlete, setTargetAthlete] = useState<AthleteWithStats | null>(null)
  const [searching, setSearching] = useState<"source" | "target" | null>(null)
  const [merging, setMerging] = useState(false)
  const [merged, setMerged] = useState(false)

  const searchAthletes = async (query: string, type: "source" | "target") => {
    if (query.length < 2) {
      if (type === "source") setSourceResults([])
      else setTargetResults([])
      return
    }

    setSearching(type)

    const { data } = await supabase
      .from("athletes")
      .select("id, full_name, first_name, last_name, birth_year, gender, clubs(name)")
      .or(`full_name.ilike.%${query}%,first_name.ilike.%${query}%,last_name.ilike.%${query}%`)
      .order("full_name")
      .limit(10)

    if (type === "source") setSourceResults(data ?? [])
    else setTargetResults(data ?? [])

    setSearching(null)
  }

  const selectAthlete = async (athlete: Athlete, type: "source" | "target") => {
    // Get result count for this athlete
    const { count } = await supabase
      .from("results")
      .select("id", { count: "exact", head: true })
      .eq("athlete_id", athlete.id)

    const athleteWithStats: AthleteWithStats = {
      ...athlete,
      resultsCount: count ?? 0,
    }

    if (type === "source") {
      setSourceAthlete(athleteWithStats)
      setSourceSearch("")
      setSourceResults([])
    } else {
      setTargetAthlete(athleteWithStats)
      setTargetSearch("")
      setTargetResults([])
    }
  }

  const performMerge = async () => {
    if (!sourceAthlete || !targetAthlete) return
    if (sourceAthlete.id === targetAthlete.id) {
      alert("Kan ikke slå sammen en utøver med seg selv!")
      return
    }

    if (!confirm(
      `Er du sikker på at du vil slå sammen disse utøverne?\n\n` +
      `"${sourceAthlete.full_name}" (${sourceAthlete.resultsCount} resultater) vil bli SLETTET.\n` +
      `Alle resultater vil bli overført til "${targetAthlete.full_name}".\n\n` +
      `Denne handlingen kan ikke angres!`
    )) return

    setMerging(true)

    try {
      // 1. Transfer all results from source to target
      const { error: transferError } = await supabase
        .from("results")
        .update({
          athlete_id: targetAthlete.id,
          updated_at: new Date().toISOString()
        })
        .eq("athlete_id", sourceAthlete.id)

      if (transferError) throw transferError

      // 2. Delete the source athlete
      const { error: deleteError } = await supabase
        .from("athletes")
        .delete()
        .eq("id", sourceAthlete.id)

      if (deleteError) throw deleteError

      setMerged(true)
    } catch (error) {
      console.error("Error merging athletes:", error)
      alert("Kunne ikke slå sammen utøvere: " + (error instanceof Error ? error.message : "Ukjent feil"))
    }

    setMerging(false)
  }

  if (merged) {
    return (
      <div className="container py-8">
        <Card className="max-w-2xl mx-auto">
          <CardContent className="p-8 text-center">
            <div className="mb-4 flex justify-center">
              <div className="rounded-full bg-green-100 p-3">
                <Check className="h-8 w-8 text-green-600" />
              </div>
            </div>
            <h2 className="text-xl font-semibold mb-2">Utøvere slått sammen!</h2>
            <p className="text-muted-foreground mb-6">
              {sourceAthlete?.resultsCount} resultater ble overført til {targetAthlete?.full_name}.
            </p>
            <div className="flex gap-4 justify-center">
              <Button variant="outline" onClick={() => router.push("/admin/athletes")}>
                Tilbake til utøvere
              </Button>
              <Button onClick={() => {
                setSourceAthlete(null)
                setTargetAthlete(null)
                setMerged(false)
              }}>
                Slå sammen flere
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Slå sammen utøvere</h1>
        <p className="text-muted-foreground mt-2">
          Overfør alle resultater fra én utøver til en annen, og slett den første.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr,auto,1fr]">
        {/* Source Athlete */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg text-red-600">Utøver som skal slettes</CardTitle>
          </CardHeader>
          <CardContent>
            {sourceAthlete ? (
              <div className="space-y-4">
                <div className="p-4 rounded-lg bg-red-50 border border-red-200">
                  <p className="font-semibold">{sourceAthlete.full_name}</p>
                  <p className="text-sm text-muted-foreground">
                    {sourceAthlete.birth_year && `Født ${sourceAthlete.birth_year}`}
                    {sourceAthlete.clubs?.name && ` · ${sourceAthlete.clubs.name}`}
                  </p>
                  <p className="text-sm mt-2">
                    <span className="font-medium">{sourceAthlete.resultsCount}</span> resultater
                  </p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSourceAthlete(null)}
                  className="w-full"
                >
                  Velg en annen
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    placeholder="Søk etter utøver..."
                    value={sourceSearch}
                    onChange={(e) => {
                      setSourceSearch(e.target.value)
                      searchAthletes(e.target.value, "source")
                    }}
                    className="pl-9"
                  />
                </div>
                {searching === "source" && (
                  <div className="flex justify-center py-4">
                    <Loader2 className="h-5 w-5 animate-spin" />
                  </div>
                )}
                {sourceResults.length > 0 && (
                  <div className="border rounded-md divide-y max-h-64 overflow-y-auto">
                    {sourceResults.map((athlete) => (
                      <button
                        key={athlete.id}
                        onClick={() => selectAthlete(athlete, "source")}
                        className="w-full px-4 py-3 text-left hover:bg-muted/50 transition-colors"
                      >
                        <p className="font-medium">{athlete.full_name}</p>
                        <p className="text-sm text-muted-foreground">
                          {athlete.birth_year && `Født ${athlete.birth_year}`}
                          {athlete.clubs?.name && ` · ${athlete.clubs.name}`}
                        </p>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Arrow */}
        <div className="flex items-center justify-center">
          <ArrowRight className="h-8 w-8 text-muted-foreground" />
        </div>

        {/* Target Athlete */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg text-green-600">Utøver som skal beholdes</CardTitle>
          </CardHeader>
          <CardContent>
            {targetAthlete ? (
              <div className="space-y-4">
                <div className="p-4 rounded-lg bg-green-50 border border-green-200">
                  <p className="font-semibold">{targetAthlete.full_name}</p>
                  <p className="text-sm text-muted-foreground">
                    {targetAthlete.birth_year && `Født ${targetAthlete.birth_year}`}
                    {targetAthlete.clubs?.name && ` · ${targetAthlete.clubs.name}`}
                  </p>
                  <p className="text-sm mt-2">
                    <span className="font-medium">{targetAthlete.resultsCount}</span> resultater
                  </p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setTargetAthlete(null)}
                  className="w-full"
                >
                  Velg en annen
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    placeholder="Søk etter utøver..."
                    value={targetSearch}
                    onChange={(e) => {
                      setTargetSearch(e.target.value)
                      searchAthletes(e.target.value, "target")
                    }}
                    className="pl-9"
                  />
                </div>
                {searching === "target" && (
                  <div className="flex justify-center py-4">
                    <Loader2 className="h-5 w-5 animate-spin" />
                  </div>
                )}
                {targetResults.length > 0 && (
                  <div className="border rounded-md divide-y max-h-64 overflow-y-auto">
                    {targetResults.map((athlete) => (
                      <button
                        key={athlete.id}
                        onClick={() => selectAthlete(athlete, "target")}
                        className="w-full px-4 py-3 text-left hover:bg-muted/50 transition-colors"
                      >
                        <p className="font-medium">{athlete.full_name}</p>
                        <p className="text-sm text-muted-foreground">
                          {athlete.birth_year && `Født ${athlete.birth_year}`}
                          {athlete.clubs?.name && ` · ${athlete.clubs.name}`}
                        </p>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Merge Button */}
      {sourceAthlete && targetAthlete && (
        <div className="mt-8">
          <Card className="border-yellow-300 bg-yellow-50">
            <CardContent className="p-6">
              <div className="flex items-start gap-4">
                <AlertTriangle className="h-6 w-6 text-yellow-600 flex-shrink-0" />
                <div className="flex-1">
                  <h3 className="font-semibold text-yellow-800">Bekreft sammenslåing</h3>
                  <p className="text-sm text-yellow-700 mt-1">
                    <strong>{sourceAthlete.resultsCount}</strong> resultater vil bli overført fra{" "}
                    <strong>{sourceAthlete.full_name}</strong> til{" "}
                    <strong>{targetAthlete.full_name}</strong>.
                    <br />
                    Etter sammenslåing vil {targetAthlete.full_name} ha totalt{" "}
                    <strong>{sourceAthlete.resultsCount + targetAthlete.resultsCount}</strong> resultater.
                  </p>
                  <Button
                    onClick={performMerge}
                    disabled={merging}
                    className="mt-4 bg-yellow-600 hover:bg-yellow-700"
                  >
                    {merging ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                        Slår sammen...
                      </>
                    ) : (
                      "Slå sammen utøvere"
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
