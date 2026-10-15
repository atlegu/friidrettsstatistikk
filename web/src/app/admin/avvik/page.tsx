import Link from "next/link"
import type { SupabaseClient } from "@supabase/supabase-js"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent } from "@/components/ui/card"
import { formatPerformance, formatPerformanceValue } from "@/lib/format-performance"
import { behandleAvvik } from "./actions"

export const metadata = {
  title: "Avvik",
}

type AvvikRad = {
  id: number
  type: string
  alvorlighet: number
  dato: string | null
  detaljer: Record<string, unknown>
  oppdaget: string
  status: string
  behandlet_tid: string | null
  kommentar: string | null
  result_id: string | null
  results: {
    performance: string | null
    wind: number | null
    athlete_id: string
    athletes: { full_name: string; birth_year: number | null } | null
  } | null
  athletes: { id: string; full_name: string; birth_year: number | null } | null
  meets: { id: string; name: string; city: string | null } | null
  events: { name: string; result_type: string } | null
}

const TYPER: Record<string, { navn: string; hva: string }> = {
  mulig_rekord: {
    navn: "Mulig rekord eller bestenotering",
    hva: "Resultatet er nå det beste norske i øvelsen. Kontroller før det godkjennes.",
  },
  urimelig_tid: {
    navn: "Urimelig tid",
    hva: "Tiden er raskere enn det som er mulig på distansen. Trolig feil format eller øvelse.",
  },
  stor_forbedring: {
    navn: "Uvanlig stor forbedring",
    hva: "Mye bedre enn utøverens beste de siste 18 månedene. Kan være feil øvelse, redskap eller utøver.",
  },
  mangler_vind: {
    navn: "Mangler vindmåling",
    hva: "Vindavhengig øvelse ute uten vind. Resultatene står i listen for ukjent vind til vinden er kjent.",
  },
  mangler_kjonn: {
    navn: "Utøver uten kjønn",
    hva: "Utøveren kommer ikke med i kjønnsdelte lister.",
  },
  mangler_alder: {
    navn: "Utøver uten fødselsår",
    hva: "Utøveren kommer ikke med i aldersklasselister.",
  },
}

const STATUS: Record<string, string> = {
  aapen: "Åpne",
  godkjent: "Godkjent som riktig",
  rettet: "Rettet",
  underkjent: "Underkjent",
}

const ALVORLIGHET: Record<number, { tekst: string; klasse: string }> = {
  1: { tekst: "Høy", klasse: "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-200" },
  2: { tekst: "Middels", klasse: "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-200" },
  3: { tekst: "Lav", klasse: "bg-muted text-muted-foreground" },
}

function datoTekst(d: string | null) {
  if (!d) return "–"
  const [a, m, dag] = d.slice(0, 10).split("-")
  return `${dag}.${m}.${a}`
}

function beskrivelse(r: AvvikRad): string {
  const d = r.detaljer ?? {}
  const rt = r.events?.result_type
  switch (r.type) {
    case "stor_forbedring":
      return `${d.endring_pst} % bedre enn ${formatPerformanceValue(d.forrige as number, rt)} (${datoTekst(
        d.forrige_dato as string
      )})`
    case "mulig_rekord":
      return d.inne ? "Innendørs" : "Utendørs"
    case "urimelig_tid":
      return `Raskeste mulige er ${formatPerformanceValue(d.minste as number, "time")}`
    case "mangler_vind":
    case "mangler_kjonn":
    case "mangler_alder":
      return `${d.antall} resultater i perioden`
    default:
      return ""
  }
}

async function hent(status: string, type: string | null) {
  const supabase = (await createClient()) as unknown as SupabaseClient

  let q = supabase
    .from("avvik")
    .select(
      `id, type, alvorlighet, dato, detaljer, oppdaget, status, behandlet_tid, kommentar, result_id,
       results(performance, wind, athlete_id, athletes(full_name, birth_year)),
       athletes(id, full_name, birth_year),
       meets(id, name, city),
       events(name, result_type)`
    )
    .eq("status", status)
    .order("alvorlighet")
    .order("dato", { ascending: false })
    .limit(300)
  if (type) q = q.eq("type", type)

  const [{ data, error }, { data: alle }] = await Promise.all([
    q,
    supabase.from("avvik").select("type, status").limit(5000),
  ])
  if (error) throw new Error(error.message)

  const telling: Record<string, Record<string, number>> = {}
  for (const a of (alle ?? []) as { type: string; status: string }[]) {
    telling[a.status] ??= {}
    telling[a.status][a.type] = (telling[a.status][a.type] ?? 0) + 1
  }
  return { rader: (data ?? []) as unknown as AvvikRad[], telling }
}

export default async function AvvikPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>
}) {
  const params = await searchParams
  const status = typeof params.status === "string" && STATUS[params.status] ? params.status : "aapen"
  const type = typeof params.type === "string" && TYPER[params.type] ? params.type : null
  const { rader, telling } = await hent(status, type)

  const iStatus = telling[status] ?? {}
  const sumStatus = (s: string) => Object.values(telling[s] ?? {}).reduce((a, b) => a + b, 0)
  const lenke = (s: string, t: string | null) =>
    `/admin/avvik?status=${s}${t ? `&type=${t}` : ""}`

  return (
    <div className="container py-8">
      <div className="mb-2 flex items-baseline justify-between gap-4">
        <h1 className="text-3xl font-bold">Avvik</h1>
        <p className="text-sm text-muted-foreground">
          Kontrollene kjøres hver natt etter importen
        </p>
      </div>
      <p className="mb-6 max-w-3xl text-sm text-muted-foreground">
        Systemet kontrollerer alle nye resultater og legger det som ikke henger sammen her.
        Hvert avvik behandles én gang: godkjent som riktig, rettet eller underkjent. Et behandlet
        avvik kommer ikke tilbake.
      </p>

      {/* Status */}
      <div className="mb-4 flex flex-wrap gap-2">
        {Object.entries(STATUS).map(([s, navn]) => (
          <Link
            key={s}
            href={lenke(s, null)}
            className={`rounded-md border px-3 py-1.5 text-sm ${
              s === status ? "border-primary bg-primary text-primary-foreground" : "hover:bg-muted"
            }`}
          >
            {navn} <span className="opacity-70">({sumStatus(s)})</span>
          </Link>
        ))}
      </div>

      {/* Typer */}
      <div className="mb-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {Object.entries(TYPER).map(([t, info]) => (
          <Link key={t} href={lenke(status, t === type ? null : t)}>
            <Card
              className={`h-full transition-colors hover:bg-muted/50 ${
                t === type ? "border-primary ring-1 ring-primary" : ""
              }`}
            >
              <CardContent className="p-4">
                <div className="flex items-baseline justify-between gap-2">
                  <span className="font-medium">{info.navn}</span>
                  <span className="text-2xl font-bold tabular-nums">{iStatus[t] ?? 0}</span>
                </div>
                <p className="mt-1 text-xs text-muted-foreground">{info.hva}</p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      <Card>
        <CardContent className="p-0">
          {rader.length === 0 ? (
            <p className="p-6 text-sm text-muted-foreground">Ingen avvik her.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/50 text-left">
                    <th className="px-3 py-2 font-medium">Alvorlighet</th>
                    <th className="px-3 py-2 font-medium">Avvik</th>
                    <th className="px-3 py-2 font-medium">Utøver</th>
                    <th className="px-3 py-2 font-medium">Øvelse</th>
                    <th className="px-3 py-2 font-medium">Resultat</th>
                    <th className="px-3 py-2 font-medium">Stevne</th>
                    <th className="px-3 py-2 font-medium">Dato</th>
                    <th className="px-3 py-2 font-medium">Behandling</th>
                  </tr>
                </thead>
                <tbody>
                  {rader.map((r) => {
                    const utover = r.athletes ?? (r.results?.athletes
                      ? { id: r.results.athlete_id, ...r.results.athletes }
                      : null)
                    const alv = ALVORLIGHET[r.alvorlighet] ?? ALVORLIGHET[2]
                    return (
                      <tr key={r.id} className="border-b align-top last:border-0">
                        <td className="px-3 py-2">
                          <span className={`rounded px-1.5 py-0.5 text-xs font-medium ${alv.klasse}`}>
                            {alv.tekst}
                          </span>
                        </td>
                        <td className="px-3 py-2">
                          <div className="font-medium">{TYPER[r.type]?.navn ?? r.type}</div>
                          <div className="text-xs text-muted-foreground">{beskrivelse(r)}</div>
                        </td>
                        <td className="px-3 py-2">
                          {utover ? (
                            <Link href={`/utover/${utover.id}`} className="hover:underline">
                              {utover.full_name}
                              {utover.birth_year ? (
                                <span className="text-muted-foreground"> ({utover.birth_year})</span>
                              ) : null}
                            </Link>
                          ) : (
                            "–"
                          )}
                        </td>
                        <td className="px-3 py-2">{r.events?.name ?? "–"}</td>
                        <td className="px-3 py-2 tabular-nums">
                          {r.results ? (
                            <Link
                              href={`/admin/results?athlete=${r.results.athlete_id}`}
                              className="font-medium hover:underline"
                              title="Rediger resultatet"
                            >
                              {formatPerformance(r.results.performance, r.events?.result_type)}
                              {r.results.wind != null ? (
                                <span className="font-normal text-muted-foreground"> ({r.results.wind})</span>
                              ) : null}
                            </Link>
                          ) : (
                            "–"
                          )}
                        </td>
                        <td className="px-3 py-2">
                          {r.meets ? (
                            <Link href={`/stevner/${r.meets.id}`} className="hover:underline">
                              {r.meets.name}
                            </Link>
                          ) : (
                            "–"
                          )}
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap tabular-nums">{datoTekst(r.dato)}</td>
                        <td className="px-3 py-2">
                          {status === "aapen" ? (
                            <form action={behandleAvvik} className="flex min-w-[260px] flex-col gap-1.5">
                              <input type="hidden" name="id" value={r.id} />
                              <input
                                name="kommentar"
                                placeholder="Kommentar (valgfritt)"
                                className="h-8 rounded-md border bg-background px-2 text-xs"
                              />
                              <div className="flex flex-wrap gap-1.5">
                                <button
                                  name="status"
                                  value="godkjent"
                                  className="rounded-md border px-2 py-1 text-xs hover:bg-muted"
                                >
                                  Riktig
                                </button>
                                <button
                                  name="status"
                                  value="rettet"
                                  className="rounded-md border px-2 py-1 text-xs hover:bg-muted"
                                >
                                  Rettet
                                </button>
                                <button
                                  name="status"
                                  value="underkjent"
                                  className="rounded-md border px-2 py-1 text-xs hover:bg-muted"
                                >
                                  Underkjent
                                </button>
                              </div>
                            </form>
                          ) : (
                            <form action={behandleAvvik} className="flex flex-col gap-1 text-xs">
                              <input type="hidden" name="id" value={r.id} />
                              <span>
                                {STATUS[r.status]} {datoTekst(r.behandlet_tid)}
                              </span>
                              {r.kommentar ? (
                                <span className="text-muted-foreground">{r.kommentar}</span>
                              ) : null}
                              <button
                                name="status"
                                value="aapen"
                                className="self-start text-muted-foreground underline hover:text-foreground"
                              >
                                Åpne igjen
                              </button>
                            </form>
                          )}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
      {rader.length === 300 ? (
        <p className="mt-2 text-xs text-muted-foreground">Viser de 300 første. Filtrer på type for å se resten.</p>
      ) : null}
    </div>
  )
}
