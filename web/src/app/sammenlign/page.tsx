"use client"

import { useState, useEffect, Suspense } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import Link from "next/link"
import { Search, Sparkles, Crown, Loader2, ArrowRight, X } from "lucide-react"
import { useAuth } from "@/components/auth/AuthProvider"
import { createClient } from "@/lib/supabase/client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"

interface Athlete {
  id: string
  first_name: string
  last_name: string
  full_name: string | null
  birth_year: number | null
  gender: string | null
}

function AthleteSearch({
  label,
  selectedAthlete,
  onSelect,
  onClear,
  excludeId,
}: {
  label: string
  selectedAthlete: Athlete | null
  onSelect: (athlete: Athlete) => void
  onClear: () => void
  excludeId?: string
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

function CompareContent() {
  const { user, isPremium, loading: authLoading } = useAuth()
  const searchParams = useSearchParams()
  const router = useRouter()
  const supabase = createClient()

  const [athlete1, setAthlete1] = useState<Athlete | null>(null)
  const [athlete2, setAthlete2] = useState<Athlete | null>(null)
  const [comparison, setComparison] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [requestsRemaining, setRequestsRemaining] = useState<number | null>(null)

  // Load athletes from URL params
  useEffect(() => {
    const id1 = searchParams.get("id1")
    const id2 = searchParams.get("id2")

    async function loadAthletes() {
      if (id1) {
        const { data } = await supabase
          .from("athletes")
          .select("id, first_name, last_name, full_name, birth_year, gender")
          .eq("id", id1)
          .single()
        if (data) setAthlete1(data)
      }
      if (id2) {
        const { data } = await supabase
          .from("athletes")
          .select("id, first_name, last_name, full_name, birth_year, gender")
          .eq("id", id2)
          .single()
        if (data) setAthlete2(data)
      }
    }
    loadAthletes()
  }, [searchParams])

  // Update URL when athletes change
  useEffect(() => {
    const params = new URLSearchParams()
    if (athlete1) params.set("id1", athlete1.id)
    if (athlete2) params.set("id2", athlete2.id)
    const newUrl = params.toString() ? `/sammenlign?${params.toString()}` : "/sammenlign"
    router.replace(newUrl, { scroll: false })
  }, [athlete1, athlete2, router])

  async function handleCompare() {
    if (!athlete1 || !athlete2 || !user) return

    setLoading(true)
    setError(null)
    setComparison(null)

    try {
      const { data: { session } } = await supabase.auth.getSession()

      if (!session) {
        setError("Du må være logget inn")
        return
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_SUPABASE_URL}/functions/v1/compare-athletes`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${session.access_token}`,
          },
          body: JSON.stringify({
            athleteId1: athlete1.id,
            athleteId2: athlete2.id
          }),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        if (data.requiresPremium) {
          setError("Krever Premium-abonnement")
        } else if (data.dailyLimitReached) {
          setError("Du har brukt alle dine 10 daglige AI-analyser")
        } else {
          setError(data.error || "En feil oppstod")
        }
        return
      }

      setComparison(data.comparison)
      setRequestsRemaining(data.requestsRemaining)
    } catch (err) {
      setError("Kunne ikke koble til AI-tjenesten")
    } finally {
      setLoading(false)
    }
  }

  if (authLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="container py-6">
      <Breadcrumbs items={[{ label: "Sammenlign utøvere" }]} />

      <h1 className="mt-4 mb-6">Sammenlign utøvere</h1>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Athlete selection */}
        <div className="lg:col-span-2 space-y-6">
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
                    setComparison(null)
                  }}
                  excludeId={athlete2?.id}
                />
                <AthleteSearch
                  label="Utøver 2"
                  selectedAthlete={athlete2}
                  onSelect={setAthlete2}
                  onClear={() => {
                    setAthlete2(null)
                    setComparison(null)
                  }}
                  excludeId={athlete1?.id}
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

          {/* Comparison result */}
          {comparison && (
            <Card className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-950/30 dark:to-blue-950/30 border-purple-200 dark:border-purple-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-purple-600" />
                  AI-sammenligning
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  <p className="whitespace-pre-wrap">{comparison}</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Action panel */}
        <div className="space-y-4">
          <Card className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-950/30 dark:to-blue-950/30 border-purple-200 dark:border-purple-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Sparkles className="h-4 w-4 text-purple-600" />
                AI-sammenligning
                {!isPremium && <Crown className="ml-auto h-4 w-4 text-yellow-600" />}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {!user ? (
                <>
                  <p className="text-sm text-muted-foreground mb-3">
                    Logg inn og oppgrader til Premium for å få AI-drevne sammenligninger.
                  </p>
                  <Button asChild size="sm" variant="outline">
                    <Link href="/logg-inn?redirect=/sammenlign">Logg inn</Link>
                  </Button>
                </>
              ) : !isPremium ? (
                <>
                  <p className="text-sm text-muted-foreground mb-3">
                    Oppgrader til Premium for AI-drevne sammenligninger av utøvere.
                  </p>
                  <Button asChild size="sm">
                    <Link href="/abonnement">
                      <Crown className="mr-2 h-4 w-4" />
                      Oppgrader til Premium
                    </Link>
                  </Button>
                </>
              ) : (
                <>
                  {error && (
                    <div className="mb-3 rounded bg-red-50 p-2 text-sm text-red-600 dark:bg-red-950 dark:text-red-400">
                      {error}
                    </div>
                  )}
                  <p className="text-sm text-muted-foreground mb-3">
                    {athlete1 && athlete2
                      ? "Klar til å sammenligne utøverne med AI."
                      : "Velg to utøvere for å sammenligne dem."}
                  </p>
                  {requestsRemaining !== null && (
                    <p className="text-xs text-muted-foreground mb-3">
                      {requestsRemaining} analyser igjen i dag
                    </p>
                  )}
                  <Button
                    onClick={handleCompare}
                    disabled={!athlete1 || !athlete2 || loading}
                    size="sm"
                    className="w-full bg-purple-600 hover:bg-purple-700"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Sammenligner...
                      </>
                    ) : (
                      <>
                        <Sparkles className="mr-2 h-4 w-4" />
                        Sammenlign med AI
                      </>
                    )}
                  </Button>
                </>
              )}
            </CardContent>
          </Card>

          {athlete1 && athlete2 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Hurtiglenker</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Link
                  href={`/utover/${athlete1.id}`}
                  className="flex items-center justify-between rounded-md border p-2 text-sm hover:bg-muted"
                >
                  {athlete1.first_name} {athlete1.last_name}
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <Link
                  href={`/utover/${athlete2.id}`}
                  className="flex items-center justify-between rounded-md border p-2 text-sm hover:bg-muted"
                >
                  {athlete2.first_name} {athlete2.last_name}
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}

export default function ComparePage() {
  return (
    <Suspense fallback={
      <div className="container flex min-h-[50vh] items-center justify-center py-6">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    }>
      <CompareContent />
    </Suspense>
  )
}
