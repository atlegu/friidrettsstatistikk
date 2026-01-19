"use client"

import { useState, useEffect, Suspense } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import Link from "next/link"
import { createClient } from "@/lib/supabase/client"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"

function LoginForm() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [mode, setMode] = useState<"login" | "magic_link">("login")
  const [magicLinkSent, setMagicLinkSent] = useState(false)
  const router = useRouter()
  const searchParams = useSearchParams()
  const supabase = createClient()

  const redirectTo = searchParams.get("redirect") || "/"

  // Check for errors in URL
  useEffect(() => {
    const errorParam = searchParams.get("error")
    if (errorParam === "auth_error") {
      setError("Autentisering feilet. Prøv igjen.")
    }

    // Check for hash fragment errors
    if (typeof window !== "undefined") {
      const hash = window.location.hash
      if (hash.includes("error=")) {
        const params = new URLSearchParams(hash.substring(1))
        const errorCode = params.get("error_code")
        const errorDesc = params.get("error_description")

        if (errorCode === "otp_expired") {
          setError("Innloggingslenken har utløpt. Be om en ny lenke.")
        } else if (errorDesc) {
          setError(decodeURIComponent(errorDesc.replace(/\+/g, " ")))
        } else {
          setError("Autentisering feilet. Prøv igjen.")
        }
        window.history.replaceState(null, "", window.location.pathname)
      }
    }
  }, [searchParams])

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      if (mode === "magic_link") {
        const { error } = await supabase.auth.signInWithOtp({
          email,
          options: {
            emailRedirectTo: `${window.location.origin}/auth/callback?next=${encodeURIComponent(redirectTo)}`,
          },
        })
        if (error) throw error
        setMagicLinkSent(true)
      } else {
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
        })
        if (error) throw error
        router.push(redirectTo)
        router.refresh()
      }
    } catch (err) {
      if (err instanceof Error) {
        if (err.message.includes("Invalid login credentials")) {
          setError("Feil e-post eller passord")
        } else {
          setError(err.message)
        }
      } else {
        setError("En feil oppstod")
      }
    } finally {
      setLoading(false)
    }
  }

  async function handleGoogleLogin() {
    setError(null)
    setLoading(true)

    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: `${window.location.origin}/auth/callback?next=${encodeURIComponent(redirectTo)}`,
        },
      })
      if (error) throw error
    } catch (err) {
      setError(err instanceof Error ? err.message : "En feil oppstod")
      setLoading(false)
    }
  }

  if (magicLinkSent) {
    return (
      <div className="container flex min-h-[70vh] items-center justify-center py-8">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-center">Sjekk e-posten din</CardTitle>
          </CardHeader>
          <CardContent className="text-center">
            <p className="text-muted-foreground">
              Vi har sendt en innloggingslenke til <strong>{email}</strong>.
            </p>
            <p className="mt-2 text-sm text-muted-foreground">
              Klikk på lenken i e-posten for å logge inn.
            </p>
            <Button
              variant="ghost"
              className="mt-4"
              onClick={() => {
                setMagicLinkSent(false)
                setEmail("")
              }}
            >
              Prøv igjen
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container flex min-h-[70vh] items-center justify-center py-8">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-center">Logg inn</CardTitle>
          <CardDescription className="text-center">
            Logg inn for å få tilgang til alle funksjoner
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Google login */}
          <Button
            variant="outline"
            className="w-full"
            onClick={handleGoogleLogin}
            disabled={loading}
          >
            <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="currentColor"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="currentColor"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="currentColor"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            Fortsett med Google
          </Button>

          <div className="relative my-6">
            <Separator />
            <span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-card px-2 text-xs text-muted-foreground">
              eller
            </span>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label htmlFor="email" className="mb-1 block text-sm font-medium">
                E-post
              </label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="din@epost.no"
                required
              />
            </div>

            {mode === "login" && (
              <div>
                <label htmlFor="password" className="mb-1 block text-sm font-medium">
                  Passord
                </label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Ditt passord"
                  required
                />
              </div>
            )}

            {error && (
              <div className="rounded bg-red-50 p-3 text-sm text-red-600 dark:bg-red-950 dark:text-red-400">
                {error}
              </div>
            )}

            <Button type="submit" className="w-full" disabled={loading}>
              {loading
                ? "Logger inn..."
                : mode === "magic_link"
                  ? "Send innloggingslenke"
                  : "Logg inn"}
            </Button>

            <div className="text-center">
              <button
                type="button"
                className="text-sm text-muted-foreground hover:text-primary"
                onClick={() => setMode(mode === "login" ? "magic_link" : "login")}
              >
                {mode === "login"
                  ? "Logg inn med e-postlenke"
                  : "Logg inn med passord"}
              </button>
            </div>
          </form>

          <div className="mt-6 text-center text-sm">
            <span className="text-muted-foreground">Har du ikke konto? </span>
            <Link href="/registrer" className="text-primary hover:underline">
              Registrer deg
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="container flex min-h-[70vh] items-center justify-center py-8">
        <p className="text-muted-foreground">Laster...</p>
      </div>
    }>
      <LoginForm />
    </Suspense>
  )
}
