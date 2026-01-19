"use client"

import { useState, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { createClient } from "@/lib/supabase/client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

export default function AdminLoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [mode, setMode] = useState<"login" | "magic_link">("login")
  const [magicLinkSent, setMagicLinkSent] = useState(false)
  const router = useRouter()
  const searchParams = useSearchParams()
  const supabase = createClient()

  // Check for errors in URL (from failed auth redirects)
  useEffect(() => {
    const errorParam = searchParams.get("error")
    if (errorParam === "auth_error") {
      setError("Autentisering feilet. Prøv igjen.")
    } else if (errorParam === "not_admin") {
      setError("Du har ikke admin-tilgang. Logg inn med en admin-konto.")
    }

    // Check for hash fragment errors (Supabase returns errors this way)
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
        // Clear the hash
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
            emailRedirectTo: `${window.location.origin}/auth/callback?next=/admin`,
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
        router.push("/admin")
        router.refresh()
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "En feil oppstod")
    } finally {
      setLoading(false)
    }
  }

  if (magicLinkSent) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-muted/30">
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
    <div className="flex min-h-screen items-center justify-center bg-muted/30">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-center">Admin-innlogging</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-1">
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
                <label htmlFor="password" className="block text-sm font-medium mb-1">
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
              <div className="rounded bg-red-50 p-3 text-sm text-red-600">
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
                  ? "Bruk innloggingslenke i stedet"
                  : "Bruk passord i stedet"}
              </button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
