import Link from "next/link"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent } from "@/components/ui/card"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"
import { ListeTopp } from "@/components/ui/liste-topp"

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
  resultater: number
  utovere: number
  totalt: number
}

// Hvor mange kort lista viser. Det finnes 2 430 klubber med resultater, og
// PostgREST leverer uansett aldri mer enn 1 000 rader. Lista hentet dem
// alfabetisk og stoppet stille på tusen, så alt fra «S» og utover fantes ikke.
// Nå vises de største først, og resten finner man med søket.
const ANTALL = 120

// Både lista og søket går gjennom sok_klubber. Den leser fra den
// materialiserte visningen klubb_bruk, ikke fra viewet
// klubber_med_statistikk: det viewet teller opp fra results ved hver
// sidevisning og bruker 107 sekunder over 1,95 millioner rader.
//
// Søket sammenlikner ikke navnene slik de står. Både det du skriver og
// klubbnavnet føres først tilbake til en felles form, der «idrettslag» og
// «IL» er samme ord. Derfor finner «Ås IL» klubben som heter «Ås
// Idrettslag», og «SK Vidar» finner «Sportsklubben Vidar». Ordstillingen
// spiller ingen rolle, for «Idrettslaget Skjalg» heter «Skjalg IL» til
// daglig. Ordlista ligger i tabellen klubb_ordformer.
async function hentKlubber(
  search?: string,
  type?: string
): Promise<{ klubber: Klubb[]; totalt: number | null }> {
  const supabase = await createClient()

  const { data, error } = await supabase.rpc("sok_klubber", {
    p_sok: search || undefined,
    p_type: type && type in TYPER ? type : undefined,
    p_antall: ANTALL,
  })

  if (error) {
    console.error("Klubblista kunne ikke hentes:", error.message)
    return { klubber: [], totalt: null }
  }

  const klubber = (data as Klubb[]) ?? []
  // Alle radene bærer det samme totalet. Uten treff finnes ingen rad å
  // lese det fra, og da er totalen null.
  return { klubber, totalt: klubber[0]?.totalt ?? 0 }
}

export default async function KlubberPage({
  searchParams,
}: {
  searchParams: Promise<{ search?: string; type?: string }>
}) {
  const { search, type } = await searchParams
  const { klubber, totalt } = await hentKlubber(search, type)

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
      <ListeTopp
        tittel="Klubber"
        beskrivelse="Klubber med registrerte resultater"
        sokeVerdi={search}
        skjulteFelt={{ type }}
        plassholder="Søk etter klubb, for eksempel «Ås IL» eller «SK Vidar» …"
        ekstra={
          <nav className="flex flex-wrap gap-2" aria-label="Filtrer på klubbtype">
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
                  className={`rounded-full border px-3 py-1 text-[13px] transition-colors ${
                    aktiv
                      ? "border-white bg-white font-medium text-[var(--nfif-navy)]"
                      : "border-white/25 text-white hover:bg-white/15"
                  }`}
                >
                  {f.navn}
                </Link>
              )
            })}
          </nav>
        }
      />

      <div className="mt-6" />

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
                    {klubb.utovere.toLocaleString("nb-NO")} utøvere ·{" "}
                    {klubb.resultater.toLocaleString("nb-NO")} resultater
                  </p>
                </CardContent>
              </Card>
            </Link>
          )
        })}
      </div>

      {klubber.length === 0 ? (
        <div className="py-8 text-center">
          <p className="text-muted-foreground">
            {search ? `Ingen klubber funnet for «${search}»` : "Ingen klubber funnet"}
          </p>
          {search && (
            <p className="mt-2 text-sm text-muted-foreground">
              Søket forstår forkortelser, så «Ås IL» finner Ås Idrettslag. Prøv
              færre ord, eller bare stedsnavnet.
            </p>
          )}
        </div>
      ) : (
        <p className="mt-6 text-sm text-muted-foreground">
          {totalt !== null && totalt > klubber.length ? (
            <>
              Viser {klubber.length.toLocaleString("nb-NO")} av{" "}
              {totalt.toLocaleString("nb-NO")} klubber
              {search
                ? ` for søket «${search}»`
                : ", de med flest resultater først"}
              .{" "}
              {search
                ? "De mest treffende står først."
                : "Søk etter navnet for å finne de øvrige. Forkortelser virker: «Ås IL» finner Ås Idrettslag."}
            </>
          ) : (
            <>
              Viser {klubber.length.toLocaleString("nb-NO")}{" "}
              {klubber.length === 1 ? "klubb" : "klubber"} med registrerte
              resultater{search && ` for søket «${search}»`}.
            </>
          )}
        </p>
      )}
    </div>
  )
}
