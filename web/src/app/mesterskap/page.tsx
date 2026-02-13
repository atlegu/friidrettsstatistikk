import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"
import { getActiveChampionships, Championship } from "@/lib/championship-config"

export const metadata = {
  title: "Mesterskap",
  description: "Kvalifiserte utøvere til norske mesterskap i friidrett",
}

function ChampionshipCard({ championship, compact }: { championship: Championship; compact?: boolean }) {
  return (
    <Link href={`/mesterskap/${championship.id}`}>
      <Card className={`h-full transition-colors hover:border-primary ${compact ? "bg-muted/30" : ""}`}>
        <CardHeader className={compact ? "pb-2" : undefined}>
          <CardTitle className={compact ? "text-base" : undefined}>{championship.name}</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className={`space-y-2 ${compact ? "text-xs" : "text-sm"}`}>
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
            {!compact && (
              <div>
                <dt className="text-muted-foreground">Kvalifiseringsperiode</dt>
                <dd className="font-medium">
                  {new Date(championship.qualificationStart + 'T12:00:00').toLocaleDateString("no-NO", { day: "numeric", month: "short", year: "numeric" })}
                  {" – "}
                  påmeldingsfristen
                </dd>
              </div>
            )}
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
  )
}

export default function MesterskapPage() {
  const championships = getActiveChampionships()
  const outdoor = championships.filter(c => !c.indoor)
  const indoor = championships.filter(c => c.indoor)

  return (
    <div className="container py-6">
      <Breadcrumbs items={[{ label: "Mesterskap" }]} />
      <h1 className="mt-4 mb-6">Mesterskap</h1>
      <p className="mb-8 text-muted-foreground">
        Oversikt over kvalifiserte utøvere til norske mesterskap i friidrett.
      </p>

      {/* Outdoor — prominent */}
      {outdoor.length > 0 && (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {outdoor.map((c) => (
            <ChampionshipCard key={c.id} championship={c} />
          ))}
        </div>
      )}

      {/* Indoor — compact */}
      {indoor.length > 0 && (
        <>
          <div className="my-6 flex items-center gap-3">
            <div className="h-px flex-1 bg-border" />
            <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Innendørs</span>
            <div className="h-px flex-1 bg-border" />
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {indoor.map((c) => (
              <ChampionshipCard key={c.id} championship={c} compact />
            ))}
          </div>
        </>
      )}
    </div>
  )
}
