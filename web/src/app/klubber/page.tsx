import Link from "next/link"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"

export const metadata = {
  title: "Klubber",
  description: "Oversikt over alle klubber med registrerte friidrettsresultater",
}

// Klubbtypene slik de vises. Tidligere filtrerte siden på club_type =
// "athletics" og skjulte dermed 737 klubber som faktisk har resultater —
// blant dem NTNUI, Stovnerkameratene og KFUM-Kameratene, som er ekte
// friidrettsklubber feilklassifisert som "other". Nå vises alle klubber med
// resultater, og typen står som etikett i stedet for å avgjøre synlighet.
const TYPER = {
  athletics: null,          // ingen etikett — dette er hovedtilfellet
  school: "Skole",
  company: "Bedriftslag",
  foreign: "Utenlandsk",
  other: "Annet",
} as const

type Klubb = {
  id: string
  name: string
  short_name: string | null
  city: string | null
  club_type: keyof typeof TYPER | null
  antall_resultater: number
  antall_utovere: number
}

async function hentKlubber(search?: string, type?: string): Promise<Klubb[]> {
  const supabase = await createClient()

  let query = supabase
    .from("klubber_med_statistikk")
    .select("id,name,short_name,city,club_type,antall_resultater,antall_utovere")
    // Klubber uten et eneste resultat er importrester eller nedlagte lag.
    // De hører ikke hjemme i en oversikt over hvem som konkurrerer.
    .gt("antall_resultater", 0)
    .order("name", { ascending: true })

  if (type && type in TYPER) {
    query = query.eq("club_type", type as keyof typeof TYPER)
  }
  if (search) {
    query = query.or(
      `name.ilike.%${search}%,short_name.ilike.%${search}%,city.ilike.%${search}%`
    )
  }

  const { data } = await query
  return (data as Klubb[]) ?? []
}

export default async function KlubberPage({
  searchParams,
}: {
  searchParams: Promise<{ search?: string; type?: string }>
}) {
  const { search, type } = await searchParams
  const klubber = await hentKlubber(search, type)

  const filtre = [
    { verdi: "", navn: "Alle" },
    { verdi: "athletics", navn: "Friidrettsklubber" },
    { verdi: "school", navn: "Skoler" },
    { verdi: "company", navn: "Bedriftslag" },
    { verdi: "other", navn: "Annet" },
  ]

  return (
    <div className="container py-6">
      <Breadcrumbs items={[{ label: "Klubber" }]} />
      <h1 className="mt-4 mb-4">Klubber</h1>

      <form className="mb-4">
        <Input
          type="search"
          name="search"
          placeholder="Søk etter klubb, kortnavn eller sted …"
          defaultValue={search}
          className="max-w-md"
        />
        {type && <input type="hidden" name="type" value={type} />}
      </form>

      <nav className="mb-6 flex flex-wrap gap-2" aria-label="Filtrer på klubbtype">
        {filtre.map((f) => {
          const aktiv = (type ?? "") === f.verdi
          const params = new URLSearchParams()
          if (search) params.set("search", search)
          if (f.verdi) params.set("type", f.verdi)
          return (
            <Link
              key={f.verdi || "alle"}
              href={`/klubber${params.toString() ? `?${params}` : ""}`}
              aria-current={aktiv ? "page" : undefined}
              className={`rounded-full border px-3 py-1 text-sm transition-colors ${
                aktiv
                  ? "border-primary bg-primary text-primary-foreground"
                  : "border-border hover:bg-muted"
              }`}
            >
              {f.navn}
            </Link>
          )
        })}
      </nav>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {klubber.map((klubb) => {
          const etikett = klubb.club_type ? TYPER[klubb.club_type] : null
          return (
            <Link key={klubb.id} href={`/klubber/${klubb.id}`}>
              <Card className="h-full cursor-pointer transition-colors hover:bg-muted/50">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between gap-2">
                    <h2 className="font-semibold text-primary">{klubb.name}</h2>
                    {etikett && (
                      <span className="shrink-0 rounded border px-1.5 py-0.5 text-xs text-muted-foreground">
                        {etikett}
                      </span>
                    )}
                  </div>
                  {klubb.short_name && klubb.short_name !== klubb.name && (
                    <p className="text-sm text-muted-foreground">{klubb.short_name}</p>
                  )}
                  {klubb.city && (
                    <p className="mt-1 text-sm text-muted-foreground">{klubb.city}</p>
                  )}
                  <p className="mt-2 text-sm tabular-nums text-muted-foreground">
                    {klubb.antall_utovere.toLocaleString("nb-NO")} utøvere ·{" "}
                    {klubb.antall_resultater.toLocaleString("nb-NO")} resultater
                  </p>
                </CardContent>
              </Card>
            </Link>
          )
        })}
      </div>

      {klubber.length === 0 && (
        <p className="text-center text-muted-foreground">
          {search ? `Ingen klubber funnet for «${search}»` : "Ingen klubber funnet"}
        </p>
      )}

      <p className="mt-6 text-sm text-muted-foreground">
        Viser {klubber.length.toLocaleString("nb-NO")} klubber med registrerte
        resultater{search && ` for søket «${search}»`}.
      </p>
    </div>
  )
}
