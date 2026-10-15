import Link from "next/link"
import { notFound } from "next/navigation"
import type { SupabaseClient } from "@supabase/supabase-js"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"
import { hentAlle } from "@/lib/hent-alle"
import { NIVAA, datoKort, distanseTekst, lopetid } from "@/lib/gatelop"

type Lop = {
  id: string
  navn: string | null
  distanse_m: number | null
  loypegrad: string | null
  ranking: boolean
  kvalitetsnivaa: string
  merknad: string | null
}

type Res = {
  id: string
  lop_id: string
  plass: number | null
  navn: string
  kjonn: string | null
  fodt: number | null
  klubb: string | null
  klasse: string | null
  tid_ms: number | null
  status: string
  athlete_id: string | null
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  if (!/^[0-9a-f-]{36}$/i.test(id)) return { title: "Gateløp" }
  const supabase = (await createClient()) as unknown as SupabaseClient
  const { data } = await supabase.from("lop_arrangement").select("navn").eq("id", id).maybeSingle()
  return { title: data?.navn ?? "Gateløp" }
}

export default async function ArrangementPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  if (!/^[0-9a-f-]{36}$/i.test(id)) notFound()
  const supabase = (await createClient()) as unknown as SupabaseClient

  const [{ data: arr }, { data: lopData }] = await Promise.all([
    supabase.from("lop_arrangement").select("*").eq("id", id).maybeSingle(),
    supabase.from("lop_lop").select("*").eq("arrangement_id", id).order("distanse_m", { ascending: false }),
  ])
  if (!arr) notFound()
  const lop = (lopData ?? []) as Lop[]
  const res = lop.length
    ? await hentAlle<Res>(
        (fra, til) =>
          supabase
            .from("lop_resultat")
            .select("id, lop_id, plass, navn, kjonn, fodt, klubb, klasse, tid_ms, status, athlete_id")
            .in("lop_id", lop.map((l) => l.id))
            .order("lop_id")
            .order("plass", { nullsFirst: false })
            .range(fra, til),
        "lop_resultat"
      )
    : []

  return (
    <div className="container py-6">
      <Breadcrumbs items={[{ label: "Gateløp", href: "/gatelop?vis=lop" }, { label: arr.navn }]} />
      <h1 className="mt-4 mb-1">{arr.navn}</h1>
      <p className="mb-6 text-sm text-muted-foreground">
        {datoKort(arr.dato)}
        {arr.sted ? ` · ${arr.sted}` : ""}
        {arr.arrangor ? ` · ${arr.arrangor}` : ""}
        {arr.gren ? ` · ${arr.gren}` : ""}
        {arr.nivaa && arr.nivaa !== "Ingen" ? ` · ${arr.nivaa}` : ""} · Kilde: EQ Timing
      </p>

      <div className="space-y-6">
        {lop.map((l) => {
          const rader = res.filter((r) => r.lop_id === l.id)
          const n = NIVAA[l.kvalitetsnivaa] ?? NIVAA.C
          return (
            <Card key={l.id}>
              <CardHeader>
                <CardTitle className="flex flex-wrap items-center gap-2">
                  {distanseTekst(l.distanse_m)}
                  <span className={`rounded px-1.5 py-0.5 text-xs font-semibold ${n.klasse}`} title={n.forklaring}>
                    Nivå {n.tekst}
                  </span>
                  {l.loypegrad ? (
                    <span className="text-xs font-normal text-muted-foreground">
                      Sertifisert målt løype, {l.loypegrad}-måling
                    </span>
                  ) : null}
                  {l.ranking ? (
                    <span className="text-xs font-normal text-muted-foreground">· World Ranking-løp</span>
                  ) : null}
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                  {rader.length.toLocaleString("no-NO")} løpere · {rader.filter((r) => r.athlete_id).length} koblet til
                  utøverregisteret
                </p>
                {l.merknad ? (
                  <p className="rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-900 dark:bg-amber-950 dark:text-amber-200">
                    {l.merknad}
                  </p>
                ) : null}
              </CardHeader>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50 text-left">
                        <th className="w-10 px-3 py-2 font-medium">#</th>
                        <th className="px-3 py-2 font-medium">Løper</th>
                        <th className="w-14 px-3 py-2 font-medium">Født</th>
                        <th className="hidden px-3 py-2 font-medium md:table-cell">Klubb</th>
                        <th className="hidden px-3 py-2 font-medium sm:table-cell">Klasse</th>
                        <th className="px-3 py-2 text-right font-medium">Tid</th>
                      </tr>
                    </thead>
                    <tbody>
                      {rader.map((r) => (
                        <tr key={r.id} className="border-b last:border-0 hover:bg-muted/30">
                          <td className="px-3 py-1.5 tabular-nums text-muted-foreground">{r.plass ?? ""}</td>
                          <td className="px-3 py-1.5">
                            {r.athlete_id ? (
                              <Link href={`/utover/${r.athlete_id}`} className="text-primary hover:underline">
                                {r.navn}
                              </Link>
                            ) : (
                              r.navn
                            )}
                          </td>
                          <td className="px-3 py-1.5 text-muted-foreground">{r.fodt ?? "–"}</td>
                          <td className="hidden px-3 py-1.5 md:table-cell">{r.klubb ?? ""}</td>
                          <td className="hidden px-3 py-1.5 text-muted-foreground sm:table-cell">{r.klasse ?? ""}</td>
                          <td className="px-3 py-1.5 text-right font-medium tabular-nums">
                            {r.status === "OK" ? lopetid(r.tid_ms) : r.status}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
