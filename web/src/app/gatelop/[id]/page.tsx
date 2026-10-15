import { notFound } from "next/navigation"
import type { SupabaseClient } from "@supabase/supabase-js"
import { createClient } from "@/lib/supabase/server"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"
import { SideTopp, MetaSkille, ToppMerke } from "@/components/ui/side-topp"
import { Flate, Nivaamerke } from "@/components/gatelop/Deler"
import { LopResultattabell, type Loprad } from "@/components/gatelop/LopResultattabell"
import { hentAlle } from "@/lib/hent-alle"
import { distanseTekst } from "@/lib/gatelop"

type Lop = {
  id: string
  navn: string | null
  distanse_m: number | null
  loypegrad: string | null
  ranking: boolean
  kvalitetsnivaa: string
  merknad: string | null
  dato: string | null
}

const GYLDIG_ID = /^[0-9a-f-]{36}$/i

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  if (!GYLDIG_ID.test(id)) return { title: "Gateløp" }
  const supabase = (await createClient()) as unknown as SupabaseClient
  const { data } = await supabase.from("lop_arrangement").select("navn, sted").eq("id", id).maybeSingle()
  return {
    title: data?.navn ?? "Gateløp",
    description: data ? `Resultater fra ${data.navn}${data.sted ? `, ${data.sted}` : ""}` : undefined,
  }
}

export default async function ArrangementPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  if (!GYLDIG_ID.test(id)) notFound()
  const supabase = (await createClient()) as unknown as SupabaseClient

  const [{ data: arr }, { data: lopData }] = await Promise.all([
    supabase.from("lop_arrangement").select("*").eq("id", id).maybeSingle(),
    supabase.from("lop_lop").select("*").eq("arrangement_id", id).order("distanse_m", { ascending: false }),
  ])
  if (!arr) notFound()
  const lop = (lopData ?? []) as Lop[]
  const res = lop.length
    ? await hentAlle<Loprad & { lop_id: string }>(
        (fra, til) =>
          supabase
            .from("lop_resultat")
            .select("id, lop_id, plass, navn, fodt, klubb, klasse, tid_ms, status, athlete_id, nasjon")
            .in("lop_id", lop.map((l) => l.id))
            .order("lop_id")
            .order("plass", { nullsFirst: false })
            .order("id")
            .range(fra, til),
        "lop_resultat"
      )
    : []

  const synlige = res.filter((r) => !(r.fodt && new Date(arr.dato).getFullYear() - r.fodt <= 11))
  const koblet = synlige.filter((r) => r.athlete_id).length
  const fullforte = synlige.filter((r) => r.status === "OK").length

  return (
    <div className="container py-6">
      <Breadcrumbs
        items={[
          { label: "Gateløp", href: "/gatelop?vis=lop" },
          { label: arr.navn },
        ]}
      />

      <SideTopp
        tittel={arr.navn}
        meta={
          <>
            <span className="font-bold text-white">
              {new Date(arr.dato).toLocaleDateString("no-NO", { day: "numeric", month: "long", year: "numeric" })}
            </span>
            {arr.sted && (
              <>
                <MetaSkille />
                <span>{arr.sted}</span>
              </>
            )}
            {arr.arrangor && (
              <>
                <MetaSkille />
                <span>{arr.arrangor}</span>
              </>
            )}
            <MetaSkille />
            <span>Kilde: {arr.kilde === "ultimate" ? "Ultimate Sport Service" : "EQ Timing"}</span>
          </>
        }
        merker={
          <>
            {arr.gren && <ToppMerke>{arr.gren}</ToppMerke>}
            {arr.nivaa && arr.nivaa !== "Ingen" && <ToppMerke>{arr.nivaa}</ToppMerke>}
          </>
        }
        noekkeltall={[
          { merkelapp: "Løp", verdi: lop.length },
          { merkelapp: "Fullførte", verdi: fullforte },
          { merkelapp: "Koblet til utøverregisteret", verdi: koblet },
        ]}
      />

      <div className="mt-6 space-y-5">
        {lop.map((l) => {
          // Barn til og med 11 år (etter kalenderåret) vises ikke offentlig
          const aar = new Date(l.dato ?? arr.dato).getFullYear()
          const rader = res.filter((r) => r.lop_id === l.id && !(r.fodt && aar - r.fodt <= 11))
          return (
            <Flate
              key={l.id}
              tittel={
                <span className="flex flex-wrap items-center gap-2">
                  {distanseTekst(l.distanse_m)}
                  <Nivaamerke nivaa={l.kvalitetsnivaa} lang />
                </span>
              }
              undertittel={
                <>
                  {l.dato && l.dato !== arr.dato
                    ? `${new Date(l.dato).toLocaleDateString("no-NO", { day: "numeric", month: "long" })} · `
                    : ""}
                  {rader.length.toLocaleString("no-NO")} løpere
                  {l.loypegrad ? ` · Sertifisert målt løype, ${l.loypegrad}-måling` : ""}
                  {l.ranking ? " · World Ranking-løp" : ""}
                </>
              }
            >
              {l.merknad ? (
                <p className="border-b border-[var(--border-default)] bg-amber-50 px-5 py-2.5 text-[13px] text-amber-900 dark:bg-amber-950/40 dark:text-amber-200">
                  {l.merknad}
                </p>
              ) : null}
              <LopResultattabell rader={rader} />
            </Flate>
          )
        })}
      </div>
    </div>
  )
}
