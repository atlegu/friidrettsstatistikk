import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowRight } from "lucide-react"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"

export const metadata = {
  title: "Statistikk",
  description: "Norsk friidrettsstatistikk - årslister, all-time lister og rekorder",
}

const currentYear = new Date().getFullYear()
const years = Array.from({ length: 10 }, (_, i) => currentYear - i)

export default function StatistikkPage() {
  return (
    <div className="container py-6">
      <Breadcrumbs items={[{ label: "Statistikk" }]} />
      <h1 className="mt-4 mb-4">Statistikk</h1>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Annual lists */}
        <Card>
          <CardHeader>
            <CardTitle>Årslister</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4 text-sm text-muted-foreground">
              Beste resultater per år, fordelt på øvelser og aldersklasser
            </p>
            <div className="flex flex-wrap gap-2">
              {years.map((year) => (
                <Link
                  key={year}
                  href={`/statistikk/${year}`}
                  className="rounded bg-muted px-3 py-1 text-sm font-medium hover:bg-primary hover:text-primary-foreground"
                >
                  {year}
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* All-time */}
        <Link href="/statistikk/all-time">
          <Card className="h-full cursor-pointer transition-colors hover:bg-muted/50">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                All-time lister
                <ArrowRight className="h-4 w-4" />
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Historiske toppresultater gjennom alle tider i norsk friidrett
              </p>
            </CardContent>
          </Card>
        </Link>

        {/* Records */}
        <Link href="/statistikk/rekorder">
          <Card className="h-full cursor-pointer transition-colors hover:bg-muted/50">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Norske rekorder
                <ArrowRight className="h-4 w-4" />
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Offisielle norske rekorder i alle øvelser og aldersklasser
              </p>
            </CardContent>
          </Card>
        </Link>
      </div>
    </div>
  )
}
