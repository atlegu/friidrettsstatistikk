import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"
import { getActiveChampionships } from "@/lib/championship-config"

export const metadata = {
  title: "Mesterskap",
  description: "Kvalifiserte utøvere til norske mesterskap i friidrett",
}

export default function MesterskapPage() {
  const championships = getActiveChampionships()

  return (
    <div className="container py-6">
      <Breadcrumbs items={[{ label: "Mesterskap" }]} />
      <h1 className="mt-4 mb-6">Mesterskap</h1>
      <p className="mb-8 text-muted-foreground">
        Oversikt over kvalifiserte utøvere til norske mesterskap i friidrett.
      </p>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {championships.map((championship) => (
          <Link key={championship.id} href={`/mesterskap/${championship.id}`}>
            <Card className="h-full transition-colors hover:border-primary">
              <CardHeader>
                <CardTitle>{championship.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <dl className="space-y-2 text-sm">
                  <div>
                    <dt className="text-muted-foreground">Dato</dt>
                    <dd className="font-medium">{championship.date}</dd>
                  </div>
                  {championship.venue && (
                    <div>
                      <dt className="text-muted-foreground">Sted</dt>
                      <dd className="font-medium">{championship.venue}</dd>
                    </div>
                  )}
                  <div>
                    <dt className="text-muted-foreground">Kvalifiseringsperiode</dt>
                    <dd className="font-medium">
                      {new Date(championship.qualificationStart + 'T12:00:00').toLocaleDateString("no-NO", { day: "numeric", month: "short", year: "numeric" })}
                      {" – "}
                      påmeldingsfristen
                    </dd>
                  </div>
                  {championship.ageClasses && (
                    <div>
                      <dt className="text-muted-foreground">Klasser</dt>
                      <dd className="font-medium">
                        {championship.ageClasses.map(ac => ac.id).join(", ")}
                      </dd>
                    </div>
                  )}
                </dl>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
