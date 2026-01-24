"use client"

import { useState } from "react"
import Link from "next/link"
import { Sparkles, Crown, Loader2 } from "lucide-react"
import { useAuth } from "@/components/auth/AuthProvider"
import { createClient } from "@/lib/supabase/client"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface AIAnalysisProps {
  athleteId: string
  athleteName: string
}

export function AIAnalysis({ athleteId, athleteName }: AIAnalysisProps) {
  const { user, isPremium, loading: authLoading } = useAuth()
  const [analysis, setAnalysis] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [requestsRemaining, setRequestsRemaining] = useState<number | null>(null)

  async function handleAnalyze() {
    if (!user) return

    setLoading(true)
    setError(null)

    try {
      const supabase = createClient()
      const { data: { session } } = await supabase.auth.getSession()

      if (!session) {
        setError("Du må være logget inn")
        return
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_SUPABASE_URL}/functions/v1/analyze-athlete`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${session.access_token}`,
          },
          body: JSON.stringify({ athleteId }),
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

      setAnalysis(data.analysis)
      setRequestsRemaining(data.requestsRemaining)
    } catch (err) {
      setError("Kunne ikke koble til AI-tjenesten")
    } finally {
      setLoading(false)
    }
  }

  // Loading state - show skeleton to avoid hydration mismatch
  if (authLoading) {
    return (
      <Card className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-950/30 dark:to-blue-950/30 border-purple-200 dark:border-purple-800">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-base">
            <Sparkles className="h-4 w-4 text-purple-600" />
            AI-analyse
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-16 animate-pulse bg-muted rounded" />
        </CardContent>
      </Card>
    )
  }

  // Not logged in - show teaser
  if (!user) {
    return (
      <Card className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-950/30 dark:to-blue-950/30 border-purple-200 dark:border-purple-800">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-base">
            <Sparkles className="h-4 w-4 text-purple-600" />
            AI-analyse
            <span className="ml-auto">
              <Crown className="h-4 w-4 text-yellow-600" />
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-3">
            Få en AI-drevet analyse av {athleteName}s styrker, utvikling og potensial.
          </p>
          <Button asChild size="sm" variant="outline">
            <Link href="/logg-inn">
              Logg inn for AI-analyse
            </Link>
          </Button>
        </CardContent>
      </Card>
    )
  }

  // Logged in but not premium - show upgrade prompt
  if (!isPremium) {
    return (
      <Card className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-950/30 dark:to-blue-950/30 border-purple-200 dark:border-purple-800">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-base">
            <Sparkles className="h-4 w-4 text-purple-600" />
            AI-analyse
            <span className="ml-auto">
              <Crown className="h-4 w-4 text-yellow-600" />
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-3">
            Oppgrader til Premium for å få AI-drevet analyse av utøvere.
          </p>
          <Button asChild size="sm">
            <Link href="/abonnement">
              <Crown className="mr-2 h-4 w-4" />
              Oppgrader til Premium
            </Link>
          </Button>
        </CardContent>
      </Card>
    )
  }

  // Premium user - show analysis or button
  return (
    <Card className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-950/30 dark:to-blue-950/30 border-purple-200 dark:border-purple-800">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-base">
          <Sparkles className="h-4 w-4 text-purple-600" />
          AI-analyse
          {requestsRemaining !== null && (
            <span className="ml-auto text-xs font-normal text-muted-foreground">
              {requestsRemaining} analyser igjen i dag
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="mb-3 rounded bg-red-50 p-2 text-sm text-red-600 dark:bg-red-950 dark:text-red-400">
            {error}
          </div>
        )}

        {analysis ? (
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <p className="whitespace-pre-wrap text-sm">{analysis}</p>
          </div>
        ) : (
          <>
            <p className="text-sm text-muted-foreground mb-3">
              Få en AI-drevet analyse av {athleteName}s styrker, utvikling og potensial basert på resultatene.
            </p>
            <Button
              onClick={handleAnalyze}
              disabled={loading}
              size="sm"
              className="bg-purple-600 hover:bg-purple-700"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyserer...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Generer AI-analyse
                </>
              )}
            </Button>
          </>
        )}
      </CardContent>
    </Card>
  )
}
