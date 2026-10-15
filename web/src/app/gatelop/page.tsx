import Link from "next/link"
import type { SupabaseClient } from "@supabase/supabase-js"
import { createClient } from "@/lib/supabase/server"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"
import { SideTopp, MetaSkille, ToppMerke } from "@/components/ui/side-topp"
import { Chip, Filterrad, Flate, Nivaamerke, NivaaForklaring, TD, TH } from "@/components/gatelop/Deler"
import { hentAlle } from "@/lib/hent-alle"
import { datoKort, distanseTekst, lopetid } from "@/lib/gatelop"

export const metadata = {
  title: "Gateløp",
  description: "Løp utenfor bane: årsbeste, løpssider og kvalitetsnivå",
}

const DISTANSER = [
  { m: 3000, navn: "3 km" },
  { m: 5000, navn: "5 km" },
  { m: 10000, navn: "10 km" },
  { m: 21097, navn: "Halvmaraton" },
  { m: 42195, navn: "Maraton" },
]

/** Aldersklasser som i Kondis' statistikk: ungdom og femårsklasser fra 40 år. */
const KLASSER: { id: string; navn: string; fra: number | null; til: number | null }[] = [
  { id: "", navn: "Alle", fra: null, til: null },
  { id: "11", navn: "11 år", fra: 0, til: 11 },
  { id: "12-13", navn: "12–13", fra: 12, til: 13 },
  { id: "14-15", navn: "14–15", fra: 14, til: 15 },
  { id: "16-17", navn: "16–17", fra: 16, til: 17 },
  { id: "18-19", navn: "18–19", fra: 18, til: 19 },
  { id: "20-22", navn: "20–22", fra: 20, til: 22 },
  { id: "40-44", navn: "40–44", fra: 40, til: 44 },
  { id: "45-49", navn: "45–49", fra: 45, til: 49 },
  { id: "50-54", navn: "50–54", fra: 50, til: 54 },
  { id: "55-59", navn: "55–59", fra: 55, til: 59 },
  { id: "60-64", navn: "60–64", fra: 60, til: 64 },
  { id: "65-69", navn: "65–69", fra: 65, til: 69 },
  { id: "70-74", navn: "70–74", fra: 70, til: 74 },
  { id: "75-", navn: "75+", fra: 75, til: null },
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
  nasjon: string | null
}

function maaned(d: string) {
  const s = new Date(d).toLocaleDateString("no-NO", { month: "long", year: "numeric" })
  return s.charAt(0).toUpperCase() + s.slice(1)
}

export default async function GatelopPage({
  searchParams,
}: {
  searchParams: Promise<{ vis?: string; distanse?: string; gender?: string; nivaa?: string; klasse?: string; alle?: string }>
}) {
  const p = await searchParams
  const vis = p.vis === "lop" ? "lop" : "arsbeste"
  const distanse = DISTANSER.find((d) => String(d.m) === p.distanse)?.m ?? 10000
  const gender = p.gender === "F" ? "F" : "M"
  const bareA = p.nivaa === "A"
  const klasse = KLASSER.find((k) => k.id === (p.klasse ?? "")) ?? KLASSER[0]
  const alleNasjoner = p.alle === "1"

  const supabase = (await createClient()) as unknown as SupabaseClient
  const [arr, { count: antallLop }, { data: besteData }] = await Promise.all([
    hentAlle<Arr>(
      (fra, til) =>
        supabase.from("lop_oversikt").select("*").order("dato", { ascending: false }).order("navn").range(fra, til),
      "lop_oversikt"
    ),
    supabase.from("lop_lop").select("id", { count: "exact", head: true }),
    vis === "arsbeste"
      ? supabase.rpc("lop_arsbeste", {
          p_aar: 2026,
          p_distanse: distanse,
          p_kjonn: gender,
          p_nivaa: bareA ? ["A"] : ["A", "B"],
          p_antall: 200,
          p_bare_norske: !alleNasjoner,
          p_alder_fra: klasse.fra,
          p_alder_til: klasse.til,
        })
      : Promise.resolve({ data: null }),
  ])
  const beste = (besteData ?? []) as Beste[]

  const lopere = arr.reduce((s, a) => s + Number(a.lopere), 0)
  const koblet = arr.reduce((s, a) => s + Number(a.koblet), 0)
  const fra = arr.length ? arr[arr.length - 1].dato : null
  const til = arr.length ? arr[0].dato : null

  const url = (o: Record<string, string>) => {
    const q = new URLSearchParams({
      vis,
      distanse: String(distanse),
      gender,
      nivaa: bareA ? "A" : "AB",
      klasse: klasse.id,
      alle: alleNasjoner ? "1" : "",
      ...o,
    })
    for (const [k, v] of [...q.entries()]) if (!v) q.delete(k)
    return `/gatelop?${q}`
  }

  // Alle løp gruppert per måned
  const perMaaned = new Map<string, Arr[]>()
  for (const a of arr) {
    const m = maaned(a.dato)
    perMaaned.set(m, [...(perMaaned.get(m) ?? []), a])
  }

  return (
    <div className="container py-6">
      <Breadcrumbs items={[{ label: "Statistikk", href: "/statistikk" }, { label: "Gateløp" }]} />

      <SideTopp
        tittel="Gateløp"
        meta={
          <>
            <span>Løp utenfor bane under Norges Friidrettsforbund</span>
            {fra && til && (
              <>
                <MetaSkille />
                <span className="font-bold text-white">
                  {datoKort(fra)}–{datoKort(til)}
                </span>
              </>
            )}
            <MetaSkille />
            <span>Kilde: EQ Timing</span>
          </>
        }
        merker={<ToppMerke>Prototype</ToppMerke>}
        noekkeltall={[
          { merkelapp: "Arrangementer", verdi: arr.length },
          { merkelapp: "Løp", verdi: antallLop ?? null },
          { merkelapp: "Resultater", verdi: lopere },
          { merkelapp: "Koblet til utøverregisteret", verdi: koblet },
        ]}
      />

      {/* Filtre */}
      <div className="mt-5 space-y-2">
        <Filterrad navn="Visning">
          <Chip href={url({ vis: "arsbeste" })} aktiv={vis === "arsbeste"}>
            Årsbeste 2026
          </Chip>
          <Chip href={url({ vis: "lop" })} aktiv={vis === "lop"}>
            Alle løp
          </Chip>
        </Filterrad>
        {vis === "arsbeste" && (
          <>
            <Filterrad navn="Distanse">
              {DISTANSER.map((d) => (
                <Chip key={d.m} href={url({ distanse: String(d.m) })} aktiv={d.m === distanse}>
                  {d.navn}
                </Chip>
              ))}
            </Filterrad>
            <Filterrad navn="Kjønn">
              <Chip href={url({ gender: "M" })} aktiv={gender === "M"}>
                Menn
              </Chip>
              <Chip href={url({ gender: "F" })} aktiv={gender === "F"}>
                Kvinner
              </Chip>
            </Filterrad>
            <Filterrad navn="Alder">
              {KLASSER.map((k) => (
                <Chip key={k.id || "alle"} href={url({ klasse: k.id })} aktiv={k.id === klasse.id}>
                  {k.navn}
                </Chip>
              ))}
            </Filterrad>
            <Filterrad navn="Løpere">
              <Chip href={url({ alle: "" })} aktiv={!alleNasjoner}>
                Norske
              </Chip>
              <Chip href={url({ alle: "1" })} aktiv={alleNasjoner}>
                Også utenlandske
              </Chip>
            </Filterrad>
            <Filterrad navn="Nivå">
              <Chip href={url({ nivaa: "AB" })} aktiv={!bareA}>
                A og B
              </Chip>
              <Chip href={url({ nivaa: "A" })} aktiv={bareA}>
                Bare A
              </Chip>
            </Filterrad>
          </>
        )}
        <div className="pt-1 sm:pl-[104px]">
          <NivaaForklaring />
        </div>
      </div>

      <div className="mt-5">
        {vis === "arsbeste" ? (
          <Flate
            tittel={`${distanseTekst(distanse)} · ${gender === "M" ? "Menn" : "Kvinner"}${
              klasse.id ? ` ${klasse.navn}${klasse.navn.includes("år") ? "" : " år"}` : ""
            } · 2026`}
            undertittel={`Beste tid per løper${alleNasjoner ? "; utenlandske løpere er merket med *" : ", norske løpere"}. ${
              bareA ? "Bare rekordgodkjente løyper." : "Rekord- og statistikkgodkjente løyper."
            } Tider rundes opp til hele sekunder, og lik tid gir lik plass. Alder etter kalenderåret.`}
          >
            {beste.length === 0 ? (
              <p className="px-5 py-8 text-center text-[13.5px] text-[var(--text-muted)]">
                Ingen resultater med dette utvalget.
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-[var(--border-default)] bg-[var(--bg-muted)]/60">
                      <th className={`${TH} w-12`}>#</th>
                      <th className={TH}>Tid</th>
                      <th className={TH}>Løper</th>
                      <th className={`${TH} w-16`}>Født</th>
                      <th className={`${TH} hidden md:table-cell`}>Løp</th>
                      <th className={`${TH} hidden lg:table-cell`}>Dato</th>
                      <th className={`${TH} w-14`}>Nivå</th>
                    </tr>
                  </thead>
                  <tbody>
                    {beste.map((b) => (
                      <tr
                        key={b.resultat_id}
                        className="border-b border-[var(--border-default)] last:border-0 hover:bg-[var(--bg-muted)]/50"
                      >
                        <td className={`${TD} tabular-nums text-[var(--text-muted)]`}>{b.plass}</td>
                        <td className={TD}>
                          <span className="perf-value">{lopetid(b.tid_ms)}</span>
                        </td>
                        <td className={TD}>
                          {b.athlete_id ? (
                            <Link href={`/utover/${b.athlete_id}`} className="font-medium text-primary hover:underline">
                              {b.navn}
                            </Link>
                          ) : (
                            <span className="font-medium">{b.navn}</span>
                          )}
                          {b.nasjon && b.nasjon !== "NOR" && (
                            <span className="ml-1 text-[12px] text-[var(--text-muted)]" title={`Nasjon: ${b.nasjon}`}>
                              * {b.nasjon}
                            </span>
                          )}
                          {b.klubb ? <div className="text-[12px] text-[var(--text-muted)]">{b.klubb}</div> : null}
                        </td>
                        <td className={`${TD} tabular-nums text-[var(--text-muted)]`}>{b.fodt ?? "–"}</td>
                        <td className={`${TD} hidden md:table-cell`}>
                          <Link href={`/gatelop/${b.arrangement_id}`} className="text-primary hover:underline">
                            {b.lop_navn}
                          </Link>
                          {b.sted ? <div className="text-[12px] text-[var(--text-muted)]">{b.sted}</div> : null}
                        </td>
                        <td className={`${TD} hidden whitespace-nowrap text-[var(--text-muted)] lg:table-cell`}>
                          {datoKort(b.dato)}
                        </td>
                        <td className={TD}>
                          <Nivaamerke nivaa={b.kvalitetsnivaa} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Flate>
        ) : (
          <div className="space-y-5">
            {[...perMaaned.entries()].map(([m, liste]) => (
              <Flate
                key={m}
                tittel={m}
                undertittel={`${liste.length} arrangementer · ${liste
                  .reduce((s, a) => s + Number(a.lopere), 0)
                  .toLocaleString("no-NO")} resultater`}
              >
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-[var(--border-default)] bg-[var(--bg-muted)]/60">
                        <th className={`${TH} w-28`}>Dato</th>
                        <th className={TH}>Arrangement</th>
                        <th className={`${TH} hidden md:table-cell`}>Type</th>
                        <th className={`${TH} hidden lg:table-cell`}>Distanser</th>
                        <th className={`${TH} text-right`}>Løpere</th>
                        <th className={`${TH} w-14`}>Nivå</th>
                      </tr>
                    </thead>
                    <tbody>
                      {liste.map((a) => (
                        <tr
                          key={a.id}
                          className="border-b border-[var(--border-default)] last:border-0 hover:bg-[var(--bg-muted)]/50"
                        >
                          <td className={`${TD} whitespace-nowrap text-[var(--text-muted)]`}>{datoKort(a.dato)}</td>
                          <td className={TD}>
                            <Link href={`/gatelop/${a.id}`} className="font-medium text-primary hover:underline">
                              {a.navn}
                            </Link>
                            {a.sted ? <div className="text-[12px] text-[var(--text-muted)]">{a.sted}</div> : null}
                          </td>
                          <td className={`${TD} hidden text-[var(--text-secondary)] md:table-cell`}>{a.gren ?? "–"}</td>
                          <td className={`${TD} hidden text-[var(--text-secondary)] lg:table-cell`}>
                            {(a.distanser ?? []).map((d) => distanseTekst(d)).join(", ") || "–"}
                          </td>
                          <td className={`${TD} text-right tabular-nums`}>{Number(a.lopere).toLocaleString("no-NO")}</td>
                          <td className={TD}>
                            <Nivaamerke nivaa={a.beste_nivaa} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Flate>
            ))}
          </div>
        )}
      </div>

      <p className="mt-4 text-[12.5px] text-[var(--text-muted)]">
        Resultatene hentes automatisk fra tidtakeren. Løpere kobles til utøverregisteret når navn, kjønn og fødselsår
        gir ett entydig treff. Kvalitetsnivået settes maskinelt ut fra løypemåling, distanse og type løp.
      </p>
    </div>
  )
}
