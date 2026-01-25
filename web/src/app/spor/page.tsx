"use client"

import { useState } from "react"
import Link from "next/link"
import { Sparkles, Crown, Loader2, Send, Database, Brain, HelpCircle } from "lucide-react"
import { useAuth } from "@/components/auth/AuthProvider"
import { createClient } from "@/lib/supabase/client"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"
import { Badge } from "@/components/ui/badge"

const EXAMPLE_QUESTIONS = [
  "Hvem har den beste 100m-tiden i Norge?",
  "Hvilke utøvere har hoppet over 2 meter i høyde?",
  "Hvor mange resultater finnes fra 2024?",
  "Hvilken klubb har flest utøvere?",
  "Hva er de 10 beste tidene på 1500m for kvinner?",
]

export default function AskPage() {
  const { user, isPremium, loading: authLoading } = useAuth()
  const [question, setQuestion] = useState("")
  const [answer, setAnswer] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [requestsRemaining, setRequestsRemaining] = useState<number | null>(null)
  const [dataSource, setDataSource] = useState<string | null>(null)

  async function handleAsk() {
    if (!question.trim() || !user) return

    setLoading(true)
    setError(null)
    setAnswer(null)
    setDataSource(null)

    try {
      const supabase = createClient()
      const { data: { session } } = await supabase.auth.getSession()

      if (!session) {
        setError("Du må være logget inn")
        return
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_SUPABASE_URL}/functions/v1/ask-database`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${session.access_token}`,
          },
          body: JSON.stringify({ question: question.trim() }),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        if (data.requiresPremium) {
          setError("Krever Premium-abonnement")
        } else if (data.dailyLimitReached) {
          setError("Du har brukt alle dine 10 daglige AI-spørringer")
        } else {
          setError(data.error || "En feil oppstod")
        }
        return
      }

      setAnswer(data.answer)
      setRequestsRemaining(data.requestsRemaining)
      setDataSource(data.dataSource)
    } catch (err) {
      setError("Kunne ikke koble til AI-tjenesten")
    } finally {
      setLoading(false)
    }
  }

  function handleExampleClick(example: string) {
    setQuestion(example)
  }

  if (authLoading) {
    return (
      <div className="container flex min-h-[50vh] items-center justify-center py-6">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="container py-6">
      <Breadcrumbs items={[{ label: "Spør statistikken" }]} />

      <h1 className="mt-4 mb-2">Spør statistikken</h1>
      <p className="text-muted-foreground mb-6">
        Still spørsmål om norsk friidrettsstatistikk og få svar fra AI-en vår.
      </p>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Question input */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <HelpCircle className="h-5 w-5" />
                Ditt spørsmål
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                placeholder="Skriv spørsmålet ditt her... F.eks. 'Hvem har den beste 100m-tiden i Norge?'"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                rows={3}
                className="resize-none"
              />

              {!user ? (
                <Button asChild>
                  <Link href="/logg-inn?redirect=/spor">
                    Logg inn for å stille spørsmål
                  </Link>
                </Button>
              ) : !isPremium ? (
                <Button asChild>
                  <Link href="/abonnement">
                    <Crown className="mr-2 h-4 w-4" />
                    Oppgrader til Premium
                  </Link>
                </Button>
              ) : (
                <Button
                  onClick={handleAsk}
                  disabled={!question.trim() || loading}
                  className="bg-purple-600 hover:bg-purple-700"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Tenker...
                    </>
                  ) : (
                    <>
                      <Send className="mr-2 h-4 w-4" />
                      Spør AI-en
                    </>
                  )}
                </Button>
              )}

              {error && (
                <div className="rounded bg-red-50 p-3 text-sm text-red-600 dark:bg-red-950 dark:text-red-400">
                  {error}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Answer */}
          {answer && (
            <Card className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-950/30 dark:to-blue-950/30 border-purple-200 dark:border-purple-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-purple-600" />
                  Svar
                  {dataSource && (
                    <Badge variant="secondary" className="ml-auto text-xs">
                      {dataSource === "database" ? (
                        <>
                          <Database className="mr-1 h-3 w-3" />
                          Fra databasen
                        </>
                      ) : (
                        <>
                          <Brain className="mr-1 h-3 w-3" />
                          Generell kunnskap
                        </>
                      )}
                    </Badge>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  <p className="whitespace-pre-wrap">{answer}</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Info card */}
          <Card className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-950/30 dark:to-blue-950/30 border-purple-200 dark:border-purple-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Sparkles className="h-4 w-4 text-purple-600" />
                AI-spørringer
                {!isPremium && <Crown className="ml-auto h-4 w-4 text-yellow-600" />}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {!user ? (
                <p className="text-sm text-muted-foreground">
                  Logg inn og oppgrader til Premium for å stille spørsmål til statistikkdatabasen.
                </p>
              ) : !isPremium ? (
                <p className="text-sm text-muted-foreground">
                  Oppgrader til Premium for å få tilgang til AI-spørringer.
                </p>
              ) : (
                <>
                  <p className="text-sm text-muted-foreground mb-2">
                    Du kan stille spørsmål om alt i statistikkdatabasen. AI-en vil analysere dataene og gi deg et svar.
                  </p>
                  {requestsRemaining !== null && (
                    <p className="text-xs text-muted-foreground">
                      {requestsRemaining} spørringer igjen i dag
                    </p>
                  )}
                </>
              )}
            </CardContent>
          </Card>

          {/* Example questions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Eksempler</CardTitle>
              <CardDescription>Klikk for å bruke</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {EXAMPLE_QUESTIONS.map((example, i) => (
                <button
                  key={i}
                  onClick={() => handleExampleClick(example)}
                  className="w-full text-left text-sm p-2 rounded-md border hover:bg-muted transition-colors"
                >
                  {example}
                </button>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
