import Link from "next/link"
import type { SupabaseClient } from "@supabase/supabase-js"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { hentAlle } from "@/lib/hent-alle"
import { NIVAA, datoKort, distanseTekst, lopetid } from "@/lib/gatelop"

export const metadata = {
  title: "Gateløp",
  description: "Løp utenfor bane: resultater, årsbeste og kvalitetsnivå (prototype)",
}

const DISTANSER = [
  { m: 5000, navn: "5 km" },
  { m: 10000, navn: "10 km" },
  { m: 21097, navn: "Halvmaraton" },
  { m: 42195, navn: "Maraton" },
]

type Arr = {
  id: string
  navn: string
  dato: string
  sted: string | null
  gren: string | null
  nivaa: string | null
  lopere: number
  koblet: number
  beste_nivaa: string
  distanser: number[] | null
}

type Beste = {
  plass: number
  resultat_id: string
  navn: string
  fodt: number | null
  klubb: string | null
  tid_ms: number
  athlete_id: string | null
  lop_navn: string
  arrangement_id: string
  dato: string
  sted: string | null
  kvalitetsnivaa: string
}

function Merke({ nivaa }: { nivaa: string }) {
  const n = NIVAA[nivaa] ?? NIVAA.C
  return (
    <span title={n.forklaring} className={`rounded px-1.5 py-0.5 text-xs font-semibold ${n.klasse}`}>
      {n.tekst}
    </span>
  )
}

export default async function GatelopPage({
  searchParams,
}: {
  searchParams: Promise<{ vis?: string; distanse?: string; gender?: string; nivaa?: string }>
}) {
  const p = await searchParams
  const vis = p.vis === "lop" ? "lop" : "arsbeste"
  const distanse = DISTANSER.find((d) => String(d.m) === p.distanse)?.m ?? 10000
  const gender = p.gender === "F" ? "F" : "M"
  const bareA = p.nivaa === "A"

  const supabase = (await createClient()) as unknown as SupabaseClient
  const arr = await hentAlle<Arr>(
    (fra, til) =>
      supabase.from("lop_oversikt").select("*").order("dato", { ascending: false }).order("navn").range(fra, til),
    "lop_oversikt"
  )
  const { data: besteData } =
    vis === "arsbeste"
      ? await supabase.rpc("lop_arsbeste", {
          p_aar: 2026,
          p_distanse: distanse,
          p_kjonn: gender,
          p_nivaa: bareA ? ["A"] : ["A", "B"],
          p_antall: 100,
        })
      : { data: null }
  const beste = (besteData ?? []) as Beste[]

  const sum = arr.reduce(
    (s, a) => ({ lopere: s.lopere + Number(a.lopere), koblet: s.koblet + Number(a.koblet) }),
    { lopere: 0, koblet: 0 }
  )
  const fra = arr.length ? arr[arr.length - 1].dato : null
  const til = arr.length ? arr[0].dato : null

  const url = (o: Record<string, string>) => {
    const q = new URLSearchParams({ vis, distanse: String(distanse), gender, nivaa: bareA ? "A" : "AB", ...o })
    return `/gatelop?${q}`
  }
  const knapp = (aktiv: boolean) =>
    `rounded px-3 py-1.5 text-sm font-medium ${
      aktiv ? "bg-primary text-primary-foreground" : "bg-muted hover:bg-muted/80"
    }`

  return (
    <div className="container py-6">
      <div className="mb-1 flex flex-wrap items-baseline gap-3">
        <h1>Gateløp</h1>
        <span className="rounded bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-900 dark:bg-amber-950 dark:text-amber-200">
          Prototype
        </span>
      </div>
      <p className="mb-6 max-w-3xl text-sm text-muted-foreground">
        Resultater hentet automatisk fra EQ Timing for løp under Norges Friidrettsforbund
        {fra && til ? `, ${datoKort(fra)}–${datoKort(til)}` : ""}: {arr.length.toLocaleString("no-NO")}{" "}
        arrangementer og {sum.lopere.toLocaleString("no-NO")} resultater.{" "}
        {sum.koblet.toLocaleString("no-NO")} løpere er koblet til utøverregisteret på navn, kjønn og
        fødselsår. Kvalitetsnivået settes maskinelt ut fra løypemåling og distanse.
      </p>

      <div className="mb-6 flex gap-2">
        <Link href={url({ vis: "arsbeste" })} className={knapp(vis === "arsbeste")}>
          Årsbeste 2026
        </Link>
        <Link href={url({ vis: "lop" })} className={knapp(vis === "lop")}>
          Alle løp
        </Link>
      </div>

      {vis === "arsbeste" ? (
        <div className="grid gap-6 lg:grid-cols-5">
          <div className="space-y-4 lg:col-span-1 lg:max-w-[200px]">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Distanse</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-1">
                {DISTANSER.map((d) => (
                  <Link key={d.m} href={url({ distanse: String(d.m) })} className={knapp(d.m === distanse)}>
                    {d.navn}
                  </Link>
                ))}
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Kjønn</CardTitle>
              </CardHeader>
              <CardContent className="flex gap-2">
                <Link href={url({ gender: "M" })} className={`flex-1 text-center ${knapp(gender === "M")}`}>
                  Menn
                </Link>
                <Link href={url({ gender: "F" })} className={`flex-1 text-center ${knapp(gender === "F")}`}>
                  Kvinner
                </Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Kvalitetsnivå</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-1">
                <Link href={url({ nivaa: "AB" })} className={knapp(!bareA)}>
                  A og B
                </Link>
                <Link href={url({ nivaa: "A" })} className={knapp(bareA)}>
                  Bare A
                </Link>
              </CardContent>
            </Card>
          </div>

          <div className="lg:col-span-4">
            <Card>
              <CardHeader>
                <CardTitle>
                  {distanseTekst(distanse)} · {gender === "M" ? "Menn" : "Kvinner"} · 2026
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                  Beste resultat per løper. {bareA ? "Bare rekordgodkjente løyper." : "Rekord- og statistikkgodkjente løyper."}
                </p>
              </CardHeader>
              <CardContent className="p-0">
                {beste.length === 0 ? (
                  <p className="p-6 text-sm text-muted-foreground">Ingen resultater med dette utvalget.</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b bg-muted/50 text-left">
                          <th className="w-10 px-3 py-2 font-medium">#</th>
                          <th className="px-3 py-2 font-medium">Tid</th>
                          <th className="px-3 py-2 font-medium">Løper</th>
                          <th className="w-14 px-3 py-2 font-medium">Født</th>
                          <th className="hidden px-3 py-2 font-medium md:table-cell">Løp</th>
                          <th className="hidden px-3 py-2 font-medium lg:table-cell">Dato</th>
                          <th className="px-3 py-2 font-medium">Nivå</th>
                        </tr>
                      </thead>
                      <tbody>
                        {beste.map((b) => (
                          <tr key={b.resultat_id} className="border-b last:border-0 hover:bg-muted/30">
                            <td className="px-3 py-2 tabular-nums text-muted-foreground">{b.plass}</td>
                            <td className="px-3 py-2 font-medium tabular-nums">{lopetid(b.tid_ms)}</td>
                            <td className="px-3 py-2">
                              {b.athlete_id ? (
                                <Link href={`/utover/${b.athlete_id}`} className="text-primary hover:underline">
                                  {b.navn}
                                </Link>
                              ) : (
                                b.navn
                              )}
                              {b.klubb ? <div className="text-xs text-muted-foreground">{b.klubb}</div> : null}
                            </td>
                            <td className="px-3 py-2 text-muted-foreground">{b.fodt ?? "–"}</td>
                            <td className="hidden px-3 py-2 md:table-cell">
                              <Link href={`/gatelop/${b.arrangement_id}`} className="hover:text-primary hover:underline">
                                {b.lop_navn}
                              </Link>
                            </td>
                            <td className="hidden px-3 py-2 text-muted-foreground lg:table-cell">{datoKort(b.dato)}</td>
                            <td className="px-3 py-2">
                              <Merke nivaa={b.kvalitetsnivaa} />
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      ) : (
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/50 text-left">
                    <th className="px-3 py-2 font-medium">Dato</th>
                    <th className="px-3 py-2 font-medium">Arrangement</th>
                    <th className="hidden px-3 py-2 font-medium md:table-cell">Type</th>
                    <th className="hidden px-3 py-2 font-medium lg:table-cell">Distanser</th>
                    <th className="px-3 py-2 text-right font-medium">Løpere</th>
                    <th className="hidden px-3 py-2 text-right font-medium sm:table-cell">Koblet</th>
                    <th className="px-3 py-2 font-medium">Nivå</th>
                  </tr>
                </thead>
                <tbody>
                  {arr.map((a) => (
                    <tr key={a.id} className="border-b last:border-0 hover:bg-muted/30">
                      <td className="whitespace-nowrap px-3 py-2 text-muted-foreground">{datoKort(a.dato)}</td>
                      <td className="px-3 py-2">
                        <Link href={`/gatelop/${a.id}`} className="font-medium hover:text-primary hover:underline">
                          {a.navn}
                        </Link>
                        {a.sted ? <div className="text-xs text-muted-foreground">{a.sted}</div> : null}
                      </td>
                      <td className="hidden px-3 py-2 md:table-cell">{a.gren ?? "–"}</td>
                      <td className="hidden px-3 py-2 lg:table-cell">
                        {(a.distanser ?? []).map((d) => distanseTekst(d)).join(", ") || "–"}
                      </td>
                      <td className="px-3 py-2 text-right tabular-nums">{Number(a.lopere).toLocaleString("no-NO")}</td>
                      <td className="hidden px-3 py-2 text-right tabular-nums text-muted-foreground sm:table-cell">
                        {Number(a.koblet).toLocaleString("no-NO")}
                      </td>
                      <td className="px-3 py-2">
                        <Merke nivaa={a.beste_nivaa} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      <Card className="mt-6">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Kvalitetsnivå</CardTitle>
        </CardHeader>
        <CardContent className="space-y-1.5 text-sm">
          {Object.entries(NIVAA).map(([k, n]) => (
            <div key={k} className="flex items-start gap-2">
              <Merke nivaa={k} />
              <span className="text-muted-foreground">{n.forklaring}</span>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
