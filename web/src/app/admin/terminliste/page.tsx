import Link from "next/link"
import type { SupabaseClient } from "@supabase/supabase-js"
import { createClient } from "@/lib/supabase/server"
import { Chip, Filterrad, Flate, TD, TH } from "@/components/gatelop/Deler"
import { hentAlle } from "@/lib/hent-alle"
import { folgOpp } from "./actions"

export const metadata = { title: "Terminliste" }

/** Dager etter siste stevnedag før et arrangement uten resultater regnes som manglende. */
const VENTETID = 3
/** Dager før et manglende arrangement kommer på purrelisten. */
const PURREGRENSE = 7

type Rad = {
  isonen_id: string
  tittel: string
  krets: string | null
  type: string | null
  kategori: "bane" | "gate"
  arrangor: string | null
  sted: string | null
  start_dato: string
  slutt_dato: string
  url: string | null
  meet_id: string | null
  lop_arrangement_id: string | null
  antall_resultater: number
  liveres_id: number | null
  oppdatert: string
  terminliste_oppfolging: {
    status: string
    purret_dato: string | null
    purringer: number
    kommentar: string | null
  } | null
}

type Status = "kommer" | "pagar" | "inne" | "venter" | "mangler" | "purret" | "avlyst" | "ingen_resultater"

const STATUS: Record<Status, { tekst: string; klasse: string }> = {
  kommer: { tekst: "Kommer", klasse: "bg-[var(--bg-muted)] text-[var(--text-muted)]" },
  pagar: { tekst: "Pågår", klasse: "bg-[var(--bg-muted)] text-[var(--text-muted)]" },
  inne: { tekst: "Resultater inne", klasse: "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200" },
  venter: { tekst: "Venter", klasse: "bg-[var(--nfif-navy)]/10 text-[var(--nfif-navy)] dark:bg-white/10 dark:text-[var(--nfif-navy-blekk)]" },
  mangler: { tekst: "Mangler", klasse: "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-200" },
  purret: { tekst: "Purret", klasse: "bg-amber-100 text-amber-900 dark:bg-amber-950 dark:text-amber-200" },
  avlyst: { tekst: "Avlyst", klasse: "bg-[var(--bg-muted)] text-[var(--text-muted)] line-through" },
  ingen_resultater: { tekst: "Ingen resultater", klasse: "bg-[var(--bg-muted)] text-[var(--text-muted)]" },
}

function dagerSiden(d: string, idag: Date) {
  return Math.floor((idag.getTime() - new Date(d + "T12:00:00").getTime()) / 86_400_000)
}

function statusFor(r: Rad, idag: Date): Status {
  const iso = idag.toISOString().slice(0, 10)
  if (r.start_dato > iso) return "kommer"
  if (r.slutt_dato >= iso) return "pagar"
  if (r.antall_resultater > 0) return "inne"
  const o = r.terminliste_oppfolging?.status
  if (o === "avlyst" || o === "ingen_resultater") return o
  if (o === "purret") return "purret"
  return dagerSiden(r.slutt_dato, idag) <= VENTETID ? "venter" : "mangler"
}

function dato(d: string) {
  return new Date(d + "T12:00:00").toLocaleDateString("no-NO", { day: "numeric", month: "short" })
}

function Flis({ navn, verdi, under }: { navn: string; verdi: string; under?: string }) {
  return (
    <div className="rounded-xl border border-[var(--border-default)] bg-[var(--bg-surface)] px-[18px] py-4">
      <div className="text-[12px] font-bold uppercase tracking-[0.06em] text-[var(--text-muted)]">{navn}</div>
      <div className="my-0.5 text-[28px] font-black tracking-tight tabular-nums">{verdi}</div>
      {under && <div className="text-[12.5px] text-[var(--text-muted)]">{under}</div>}
    </div>
  )
}

function purretekst(arrangor: string, liste: Rad[]) {
  const linjer = liste.map((r) => `- ${r.tittel} (${dato(r.slutt_dato)})`).join("\n")
  const emne = `Resultater fra ${liste.length === 1 ? liste[0].tittel : `${liste.length} arrangementer`}`
  const tekst =
    `Hei,\n\nVi finner ikke resultater fra følgende arrangement${liste.length > 1 ? "er" : ""} ` +
    `i den nasjonale statistikken:\n\n${linjer}\n\n` +
    `Kan dere sende resultatlisten, eller gi beskjed dersom arrangementet ble avlyst?\n\n` +
    `Vennlig hilsen\n`
  return `mailto:?subject=${encodeURIComponent(emne)}&body=${encodeURIComponent(tekst)}`
}

export default async function TerminlistePage({
  searchParams,
}: {
  searchParams: Promise<{ kategori?: string; vis?: string; feil?: string }>
}) {
  const sp = await searchParams
  const kategori = sp.kategori === "gate" ? "gate" : "bane"
  const vis = ["mangler", "purret", "alle", "kommende"].includes(sp.vis ?? "") ? sp.vis! : "mangler"
  const feil = sp.feil ? sp.feil.slice(0, 300) : null
  const idag = new Date()

  const supabase = (await createClient()) as unknown as SupabaseClient
  const rader = await hentAlle<Rad>(
    (fra, til) =>
      supabase
        .from("terminliste")
        .select("*, terminliste_oppfolging(status, purret_dato, purringer, kommentar)")
        .eq("kategori", kategori)
        .order("slutt_dato", { ascending: false })
        .order("isonen_id")
        .range(fra, til),
    "terminliste"
  )
  const medStatus = rader.map((r) => ({ ...r, status: statusFor(r, idag) }))
  const avholdt = medStatus.filter((r) => !["kommer", "pagar"].includes(r.status))
  const inne = avholdt.filter((r) => r.status === "inne").length
  const manglende = avholdt.filter((r) => ["mangler", "purret", "venter"].includes(r.status))
  const purret = avholdt.filter((r) => r.status === "purret")
  const avklart = avholdt.filter((r) => ["avlyst", "ingen_resultater"].includes(r.status)).length
  const sistOppdatert = rader.reduce((m, r) => (r.oppdatert > m ? r.oppdatert : m), "")

  const vises =
    vis === "mangler"
      ? manglende
      : vis === "purret"
        ? purret
        : vis === "kommende"
          ? medStatus.filter((r) => ["kommer", "pagar"].includes(r.status)).reverse()
          : avholdt

  // Purreliste: manglende i mer enn en uke, ikke purret de siste to ukene
  const tilPurring = new Map<string, Rad[]>()
  for (const r of avholdt) {
    const o = r.terminliste_oppfolging
    const nyligPurret = o?.purret_dato && dagerSiden(o.purret_dato, idag) < 14
    if ((r.status === "mangler" || r.status === "purret") && dagerSiden(r.slutt_dato, idag) > PURREGRENSE && !nyligPurret) {
      const n = r.arrangor ?? "Ukjent arrangør"
      tilPurring.set(n, [...(tilPurring.get(n) ?? []), r])
    }
  }

  const url = (o: Record<string, string>) => `/admin/terminliste?${new URLSearchParams({ kategori, vis, ...o })}`
  const andel = avholdt.length ? Math.round((100 * inne) / (avholdt.length - avklart || 1)) : 0

  return (
    <div className="container py-8">
      <div className="mb-1 flex flex-wrap items-baseline justify-between gap-3">
        <h1 className="text-3xl font-bold">Terminliste</h1>
        {sistOppdatert && (
          <p className="text-sm text-muted-foreground">
            Oppdatert{" "}
            {new Date(sistOppdatert).toLocaleString("no-NO", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" })}
          </p>
        )}
      </div>
      {feil ? (
        <p className="mb-4 rounded-md border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-200">
          {feil}
        </p>
      ) : null}
      <p className="mb-5 max-w-3xl text-sm text-muted-foreground">
        Arrangementene i terminlisten fra iSonen, hentet fra friidrett.no hver natt og koblet mot resultatene i basen.
        Et arrangement uten resultater {VENTETID} dager etter siste stevnedag regnes som manglende, og etter{" "}
        {PURREGRENSE} dager kommer arrangøren på purrelisten.
      </p>

      <div className="space-y-2">
        <Filterrad navn="Type">
          <Chip href={url({ kategori: "bane" })} aktiv={kategori === "bane"}>
            Banestevner
          </Chip>
          <Chip href={url({ kategori: "gate" })} aktiv={kategori === "gate"}>
            Gateløp
          </Chip>
        </Filterrad>
        <Filterrad navn="Vis">
          <Chip href={url({ vis: "mangler" })} aktiv={vis === "mangler"}>
            Mangler resultater ({manglende.length})
          </Chip>
          <Chip href={url({ vis: "purret" })} aktiv={vis === "purret"}>
            Purret ({purret.length})
          </Chip>
          <Chip href={url({ vis: "alle" })} aktiv={vis === "alle"}>
            Alle avholdte ({avholdt.length})
          </Chip>
          <Chip href={url({ vis: "kommende" })} aktiv={vis === "kommende"}>
            Kommende
          </Chip>
        </Filterrad>
      </div>

      <div className="mt-5 grid gap-3.5 sm:grid-cols-2 lg:grid-cols-4">
        <Flis navn="Avholdt" verdi={avholdt.length.toLocaleString("no-NO")} under="i terminlisten" />
        <Flis navn="Resultater inne" verdi={inne.toLocaleString("no-NO")} under={`${andel} % av arrangementene`} />
        <Flis navn="Mangler" verdi={manglende.length.toLocaleString("no-NO")} under={`${purret.length} purret`} />
        <Flis navn="Til purring" verdi={tilPurring.size.toLocaleString("no-NO")} under="arrangører" />
      </div>

      {kategori === "gate" && (
        <p className="mt-3 text-[12.5px] text-[var(--text-muted)]">
          Gateløp faller ut av terminlisten på friidrett.no når de er avholdt. Historikken bygges derfor opp fra
          15. oktober 2026, da hentingen startet.
        </p>
      )}

      <div className="mt-5">
        <Flate
          tittel={
            vis === "mangler"
              ? "Mangler resultater"
              : vis === "purret"
                ? "Purret"
                : vis === "kommende"
                  ? "Kommende"
                  : "Alle avholdte"
          }
          undertittel={`${vises.length.toLocaleString("no-NO")} arrangementer`}
        >
          {vises.length === 0 ? (
            <p className="px-5 py-8 text-center text-[13.5px] text-[var(--text-muted)]">Ingen arrangementer her.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[var(--border-default)] bg-[var(--bg-muted)]/60">
                    <th className={`${TH} w-24`}>Dato</th>
                    <th className={TH}>Arrangement</th>
                    <th className={`${TH} hidden lg:table-cell`}>Type</th>
                    <th className={TH}>Status</th>
                    <th className={`${TH} min-w-[230px]`}>Oppfølging</th>
                  </tr>
                </thead>
                <tbody>
                  {vises.slice(0, 400).map((r) => {
                    const s = STATUS[r.status]
                    const o = r.terminliste_oppfolging
                    const dager = dagerSiden(r.slutt_dato, idag)
                    return (
                      <tr key={r.isonen_id} className="border-b border-[var(--border-default)] align-top last:border-0">
                        <td className={`${TD} whitespace-nowrap text-[var(--text-muted)]`}>
                          {dato(r.start_dato)}
                          {r.slutt_dato !== r.start_dato && <div className="text-[12px]">–{dato(r.slutt_dato)}</div>}
                        </td>
                        <td className={TD}>
                          {r.url ? (
                            <a href={r.url} target="_blank" rel="noopener noreferrer" className="font-medium text-primary hover:underline">
                              {r.tittel}
                            </a>
                          ) : (
                            <span className="font-medium">{r.tittel}</span>
                          )}
                          <div className="text-[12px] text-[var(--text-muted)]">
                            {[r.arrangor?.replace(/ - Friidrett$/, ""), r.sted, r.krets].filter(Boolean).join(" · ")}
                          </div>
                        </td>
                        <td className={`${TD} hidden text-[var(--text-secondary)] lg:table-cell`}>{r.type ?? "–"}</td>
                        <td className={TD}>
                          <span className={`inline-flex rounded-md px-1.5 py-0.5 text-[11px] font-bold uppercase tracking-wide ${s.klasse}`}>
                            {s.tekst}
                          </span>
                          <div className="mt-1 text-[12px] text-[var(--text-muted)]">
                            {r.status === "inne" && (
                              <Link
                                href={r.meet_id ? `/stevner/${r.meet_id}` : `/gatelop/${r.lop_arrangement_id}`}
                                className="hover:underline"
                              >
                                {r.antall_resultater.toLocaleString("no-NO")} resultater
                              </Link>
                            )}
                            {["mangler", "venter", "purret"].includes(r.status) && <span>{dager} dager siden</span>}
                            {r.status === "purret" && o?.purret_dato && (
                              <span>
                                {" "}
                                · purret {dato(o.purret_dato)}
                                {o.purringer > 1 ? ` (${o.purringer}. gang)` : ""}
                              </span>
                            )}
                            {r.liveres_id && r.status !== "inne" && (
                              <div className="font-medium text-[var(--nfif-navy)] dark:text-[var(--nfif-navy-blekk)]">Finnes i LiveRes</div>
                            )}
                            {o?.kommentar && <div className="italic">{o.kommentar}</div>}
                          </div>
                        </td>
                        <td className={TD}>
                          {!["kommer", "pagar", "inne"].includes(r.status) && (
                            <form className="flex flex-col gap-1.5">
                              <input type="hidden" name="id" value={r.isonen_id} />
                              <input
                                name="kommentar"
                                placeholder="Kommentar"
                                className="h-8 rounded-md border bg-background px-2 text-xs"
                              />
                              <div className="flex flex-wrap gap-1.5">
                                <button formAction={folgOpp.bind(null, "purret")} className="rounded-md border px-2 py-1 text-xs hover:bg-muted">
                                  Purret
                                </button>
                                <button formAction={folgOpp.bind(null, "avlyst")} className="rounded-md border px-2 py-1 text-xs hover:bg-muted">
                                  Avlyst
                                </button>
                                <button
                                  formAction={folgOpp.bind(null, "ingen_resultater")}
                                  className="rounded-md border px-2 py-1 text-xs hover:bg-muted"
                                  title="For eksempel barneidrett eller skolestevne uten statistikk"
                                >
                                  Ingen resultater
                                </button>
                                {o && (
                                  <button formAction={folgOpp.bind(null, "nullstill")} className="px-1 text-xs text-muted-foreground underline">
                                    Nullstill
                                  </button>
                                )}
                              </div>
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
        </Flate>
        {vises.length > 400 && (
          <p className="mt-2 text-xs text-muted-foreground">Viser de 400 siste av {vises.length}.</p>
        )}
      </div>

      {tilPurring.size > 0 && (
        <div className="mt-6">
          <Flate
            tittel="Purreliste"
            undertittel={`Arrangører med arrangementer uten resultater i mer enn ${PURREGRENSE} dager, som ikke er purret de siste to ukene. «Skriv e-post» åpner et ferdig utkast; legg inn mottaker og trykk Purret når den er sendt.`}
          >
            <ul className="divide-y divide-[var(--border-default)]">
              {[...tilPurring.entries()]
                .sort((a, b) => b[1].length - a[1].length)
                .map(([arrangor, liste]) => (
                  <li key={arrangor} className="flex flex-wrap items-start justify-between gap-3 px-5 py-3">
                    <div className="min-w-0">
                      <div className="text-[13.5px] font-medium">{arrangor.replace(/ - Friidrett$/, "")}</div>
                      <div className="text-[12px] text-[var(--text-muted)]">
                        {liste.map((r) => `${r.tittel} (${dato(r.slutt_dato)})`).join(" · ")}
                      </div>
                    </div>
                    <a
                      href={purretekst(arrangor, liste)}
                      className="shrink-0 rounded-lg border border-[var(--border-default)] px-3 py-1.5 text-[13px] hover:border-[var(--nfif-navy-lys)]"
                    >
                      Skriv e-post
                    </a>
                  </li>
                ))}
            </ul>
          </Flate>
        </div>
      )}
    </div>
  )
}
