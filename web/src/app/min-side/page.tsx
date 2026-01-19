"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Crown, Settings, CreditCard } from "lucide-react"
import { useAuth } from "@/components/auth/AuthProvider"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"

export default function MinSidePage() {
  const { user, profile, loading, isPremium } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) {
      router.push("/logg-inn?redirect=/min-side")
    }
  }, [user, loading, router])

  if (loading) {
    return (
      <div className="container py-6">
        <div className="flex min-h-[50vh] items-center justify-center">
          <p className="text-muted-foreground">Laster...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  const displayName = profile?.full_name || user.email?.split("@")[0] || "Bruker"

  return (
    <div className="container py-6">
      <Breadcrumbs items={[{ label: "Min side" }]} />

      <h1 className="mt-4 mb-6">Min side</h1>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Profile Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Profil
              {isPremium && (
                <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                  <Crown className="mr-1 h-3 w-3" />
                  Premium
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div>
                <p className="text-sm text-muted-foreground">Navn</p>
                <p className="font-medium">{displayName}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">E-post</p>
                <p className="font-medium">{user.email}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Medlem siden</p>
                <p className="font-medium">
                  {new Date(user.created_at).toLocaleDateString("no-NO", {
                    day: "numeric",
                    month: "long",
                    year: "numeric",
                  })}
                </p>
              </div>
            </div>
            <Button variant="outline" size="sm" className="mt-4" asChild>
              <Link href="/min-side/innstillinger">
                <Settings className="mr-2 h-4 w-4" />
                Rediger profil
              </Link>
            </Button>
          </CardContent>
        </Card>

        {/* Subscription Card */}
        <Card>
          <CardHeader>
            <CardTitle>Abonnement</CardTitle>
            <CardDescription>
              {isPremium
                ? "Du har tilgang til alle premium-funksjoner"
                : "Oppgrader for å låse opp alle funksjoner"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isPremium ? (
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-green-600">
                  <Crown className="h-5 w-5" />
                  <span className="font-medium">Premium aktiv</span>
                </div>
                {profile?.subscription_expires_at && (
                  <p className="text-sm text-muted-foreground">
                    Fornyes{" "}
                    {new Date(profile.subscription_expires_at).toLocaleDateString("no-NO", {
                      day: "numeric",
                      month: "long",
                      year: "numeric",
                    })}
                  </p>
                )}
                <Button variant="outline" size="sm" asChild>
                  <Link href="/min-side/abonnement">
                    <CreditCard className="mr-2 h-4 w-4" />
                    Administrer abonnement
                  </Link>
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="rounded-lg bg-muted p-4">
                  <h3 className="font-semibold">Premium-funksjoner:</h3>
                  <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
                    <li>- AI-analyse av utøvere</li>
                    <li>- Avanserte sammenligninger</li>
                    <li>- Eksport til PDF/Excel</li>
                    <li>- Varsler og overvåking</li>
                  </ul>
                </div>
                <Button asChild>
                  <Link href="/abonnement">
                    <Crown className="mr-2 h-4 w-4" />
                    Oppgrader til Premium - 99 kr/mnd
                  </Link>
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions Card */}
        <Card>
          <CardHeader>
            <CardTitle>Snarveier</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Button variant="outline" className="w-full justify-start" asChild>
                <Link href="/statistikk/2025">
                  Årslister 2025
                </Link>
              </Button>
              <Button variant="outline" className="w-full justify-start" asChild>
                <Link href="/statistikk/rekorder">
                  Norgesrekorder
                </Link>
              </Button>
              <Button variant="outline" className="w-full justify-start" asChild>
                <Link href="/utover">
                  Søk utøvere
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
