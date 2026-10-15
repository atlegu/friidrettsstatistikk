import Link from "next/link"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"
import { formatPerformance } from "@/lib/format-performance"

export const metadata = {
  title: "Masters",
  description: "Beste norske resultater i masters-klassene, fra 35 år, i femårsklasser",
}

const KLASSER = ["V35", "V40", "V45", "V50", "V55", "V60", "V65", "V70", "V75", "V80", "V85", "V90", "V95"]

type Rekord = {
  event_id: string
  event_name: string
  result_type: string
  result_id: string
  performance: string
  wind: number | null
  athlete_id: string
  athlete_name: string
  fodt: number | null
  club_name: string | null
  meet_id: string
  meet_name: string
  meet_city: string | null
  date: string
  antall_utovere: number
}

type Oversikt = { klasse: string; gender: string; resultater: number; utovere: number }

function datoTekst(d: string) {
  return new Date(d).toLocaleDateString("no-NO", { day: "numeric", month: "short", year: "numeric" })
}

export default async function MastersPage({
  searchParams,
}: {
  searchParams: Promise<{ gender?: string; klasse?: string; venue?: string }>
}) {
  const params = await searchParams
  const gender = params.gender === "F" ? "F" : "M"
  const klasse = params.klasse && KLASSER.includes(params.klasse) ? params.klasse : "V35"
  const venue = params.venue === "indoor" ? "indoor" : "outdoor"

  const supabase = await createClient()
  const [{ data: rek, error }, { data: ov }] = await Promise.all([
    supabase.rpc("masters_rekorder" as never, {
      p_kjonn: gender,
      p_klasse: klasse,
      p_inne: venue === "indoor",
    } as never),
    supabase.rpc("masters_oversikt" as never),
  ])
  if (error) console.error("masters_rekorder:", error.message)

  const rekorder = ((rek ?? []) as unknown as Rekord[])
  const oversikt = ((ov ?? []) as unknown as Oversikt[])
  const denne = oversikt.find((o) => o.klasse === klasse && o.gender === gender)
  const totalt = oversikt
    .filter((o) => KLASSER.includes(o.klasse))
    .reduce((s, o) => ({ r: s.r + Number(o.resultater), u: s.u + Number(o.utovere) }), { r: 0, u: 0 })

  const genderLabel = gender === "M" ? "Menn" : "Kvinner"
  const klasseLabel = `${gender === "M" ? "M" : "K"}${klasse.slice(1)}`
  const buildUrl = (o: { gender?: string; klasse?: string; venue?: string }) => {
    const p = new URLSearchParams({
      gender: o.gender ?? gender,
      klasse: o.klasse ?? klasse,
      venue: o.venue ?? venue,
    })
    return `/statistikk/masters?${p}`
  }
  const knapp = (aktiv: boolean) =>
    `rounded px-3 py-2 text-center text-sm font-medium ${
      aktiv ? "bg-primary text-primary-foreground" : "bg-muted hover:bg-muted/80"
    }`

  return (
    <div className="container py-6">
      <Breadcrumbs items={[{ label: "Statistikk", href: "/statistikk" }, { label: "Masters" }]} />
      <h1 className="mt-4 mb-2">Masters</h1>
      <p className="mb-6 max-w-3xl text-sm text-muted-foreground">
        Beste norske resultat i hver øvelse, per femårsklasse fra 35 år. Klassen følger
        kalenderåret: konkurranseår minus fødselsår. Redskap og hekkehøyde står i øvelsesnavnet.
        Samme regler som for norgesrekordene: lovlig vind, ikke håndtid i sprint og hekk.
        {totalt.r > 0 ? (
          <>
            {" "}
            Basen har {totalt.r.toLocaleString("no-NO")} masters-resultater.
          </>
        ) : null}
      </p>

      <div className="grid gap-8 lg:grid-cols-5">
        <div className="space-y-4 lg:col-span-1 lg:max-w-[180px]">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Kjønn</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Link href={buildUrl({ gender: "M" })} className={`flex-1 ${knapp(gender === "M")}`}>
                  Menn
                </Link>
                <Link href={buildUrl({ gender: "F" })} className={`flex-1 ${knapp(gender === "F")}`}>
                  Kvinner
                </Link>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Bane</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Link href={buildUrl({ venue: "outdoor" })} className={`flex-1 ${knapp(venue === "outdoor")}`}>
                  Ute
                </Link>
                <Link href={buildUrl({ venue: "indoor" })} className={`flex-1 ${knapp(venue === "indoor")}`}>
                  Inne
                </Link>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Klasse</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-1 lg:grid-cols-2">
                {KLASSER.map((k) => (
                  <Link key={k} href={buildUrl({ klasse: k })} className={knapp(k === klasse)}>
                    {gender === "M" ? "M" : "K"}
                    {k.slice(1)}
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-4">
          <Card>
            <CardHeader>
              <CardTitle>
                {klasseLabel} · {venue === "indoor" ? "Innendørs" : "Utendørs"}
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                {genderLabel} {klasse.slice(1)}–{Number(klasse.slice(1)) + 4} år
                {denne
                  ? ` · ${Number(denne.utovere).toLocaleString("no-NO")} utøvere og ${Number(
                      denne.resultater
                    ).toLocaleString("no-NO")} resultater i klassen, ute og inne`
                  : ""}
              </p>
            </CardHeader>
            <CardContent className="p-0">
              {rekorder.length === 0 ? (
                <p className="p-6 text-sm text-muted-foreground">Ingen resultater i denne klassen.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-3 py-2 text-left text-sm font-medium">Øvelse</th>
                        <th className="px-3 py-2 text-left text-sm font-medium">Resultat</th>
                        <th className="px-3 py-2 text-left text-sm font-medium">Utøver</th>
                        <th className="w-14 px-3 py-2 text-left text-sm font-medium">Født</th>
                        <th className="hidden px-3 py-2 text-left text-sm font-medium md:table-cell">Stevne</th>
                        <th className="hidden px-3 py-2 text-left text-sm font-medium lg:table-cell">Dato</th>
                        <th className="hidden px-3 py-2 text-right text-sm font-medium sm:table-cell">
                          Utøvere
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {rekorder.map((r) => (
                        <tr key={r.event_id} className="border-b last:border-0 hover:bg-muted/30">
                          <td className="px-3 py-2 font-medium">{r.event_name}</td>
                          <td className="px-3 py-2">
                            <span className="perf-value">{formatPerformance(r.performance, r.result_type)}</span>
                            {r.wind !== null && (
                              <span className="ml-1 text-xs text-muted-foreground">
                                ({Number(r.wind) > 0 ? "+" : ""}
                                {r.wind})
                              </span>
                            )}
                          </td>
                          <td className="px-3 py-2">
                            <Link href={`/utover/${r.athlete_id}`} className="text-primary hover:underline">
                              {r.athlete_name}
                            </Link>
                            {r.club_name ? (
                              <div className="text-xs text-muted-foreground">{r.club_name}</div>
                            ) : null}
                          </td>
                          <td className="px-3 py-2 text-sm text-muted-foreground">{r.fodt ?? "–"}</td>
                          <td className="hidden px-3 py-2 text-sm md:table-cell">
                            <Link href={`/stevner/${r.meet_id}`} className="hover:text-primary hover:underline">
                              {r.meet_name}
                            </Link>
                          </td>
                          <td className="hidden px-3 py-2 text-sm text-muted-foreground lg:table-cell">
                            {datoTekst(r.date)}
                          </td>
                          <td className="hidden px-3 py-2 text-right text-sm tabular-nums text-muted-foreground sm:table-cell">
                            {r.antall_utovere}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
          <p className="mt-3 text-xs text-muted-foreground">
            Resultatene dekker perioden basen har fullstendige data for. Eldre masters-rekorder
            hentes inn sammen med den øvrige historiske statistikken. Listen bygges om hver uke.
          </p>
        </div>
      </div>
    </div>
  )
}
