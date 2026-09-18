import Link from "next/link"
import { formatPerformance } from "@/lib/format-performance"
import { harUkjentVind } from "@/lib/vind"
import type { KravStatus } from "@/lib/nm-status"

/** Kort i samme uttrykk som designskissen: hvit flate, tynn ramme, 12 px hjørner. */
export function Kort({ tittel, children, className = "" }: { tittel: string; children: React.ReactNode; className?: string }) {
  return (
    <section className={`min-w-0 rounded-xl border border-[var(--border-default)] bg-[var(--bg-surface)] p-5 ${className}`}>
      <h2 className="mb-3 text-[16px] font-bold tracking-tight">{tittel}</h2>
      {children}
    </section>
  )
}

function Underoverskrift({ children }: { children: React.ReactNode }) {
  return <h3 className="mb-1 mt-4 text-[11.5px] font-bold uppercase tracking-[0.07em] text-[var(--text-muted)] first:mt-0">{children}</h3>
}

/* ---------------------------------------------------------- rekorder */

interface PB {
  event_id: string
  event_name: string
  performance: string
  result_type: string
  date: string
  is_indoor: boolean
  event_sort_order: number | null
}

/**
 * Rekordene i øvelsene utøveren har konkurrert i de siste sesongene vises
 * først. Resten (gamle redskapsvekter, sjeldne øvelser) ligger bak «Vis alle»,
 * slik at en mangekjemper ikke får en liste på seksti linjer.
 */
export function PersonligeRekorder({ pbs, aktiveEventIds }: { pbs: PB[]; aktiveEventIds: Set<string> }) {
  const sorter = (a: PB, b: PB) => (a.event_sort_order ?? 999) - (b.event_sort_order ?? 999)
  const aktive = aktiveEventIds.size > 0 ? pbs.filter((p) => aktiveEventIds.has(p.event_id)) : pbs
  const ovrige = aktiveEventIds.size > 0 ? pbs.filter((p) => !aktiveEventIds.has(p.event_id)) : []
  const ute = aktive.filter((p) => !p.is_indoor).sort(sorter)
  const inne = aktive.filter((p) => p.is_indoor).sort(sorter)
  const ovrigeUte = ovrige.filter((p) => !p.is_indoor).sort(sorter)
  const ovrigeInne = ovrige.filter((p) => p.is_indoor).sort(sorter)
  const Rad = ({ p }: { p: PB }) => (
    <div className="flex items-baseline justify-between border-b border-[var(--border-default)] py-2 last:border-0">
      <span className="text-[14px]">{p.event_name}</span>
      <span className="text-[17px] font-black tabular-nums tracking-tight">
        {formatPerformance(p.performance, p.result_type)}
        <span className="ml-2 text-[12px] font-normal text-[var(--text-muted)]">{p.date?.slice(0, 4)}</span>
      </span>
    </div>
  )
  if (pbs.length === 0) return <Kort tittel="Personlige rekorder"><p className="text-[13px] text-[var(--text-muted)]">Ingen resultater ennå.</p></Kort>
  return (
    <Kort tittel="Personlige rekorder">
      {ute.length > 0 && <><Underoverskrift>Utendørs</Underoverskrift>{ute.map((p) => <Rad key={"u" + p.event_name} p={p} />)}</>}
      {inne.length > 0 && <><Underoverskrift>Innendørs</Underoverskrift>{inne.map((p) => <Rad key={"i" + p.event_name} p={p} />)}</>}
      {ovrige.length > 0 && (
        <details className="mt-3">
          <summary className="cursor-pointer text-[13px] text-[var(--text-secondary)]">Vis alle øvelser ({ovrige.length} til)</summary>
          {ovrigeUte.length > 0 && <><Underoverskrift>Utendørs, tidligere øvelser</Underoverskrift>{ovrigeUte.map((p) => <Rad key={"ou" + p.event_name} p={p} />)}</>}
          {ovrigeInne.length > 0 && <><Underoverskrift>Innendørs, tidligere øvelser</Underoverskrift>{ovrigeInne.map((p) => <Rad key={"oi" + p.event_name} p={p} />)}</>}
        </details>
      )}
    </Kort>
  )
}

/* ---------------------------------------------------------- NM-krav */

export function NmKrav({ navn, aar, rader, lenke }: { navn: string; aar: number; rader: KravStatus[]; lenke: string }) {
  return (
    <Kort tittel={`Kvalifisert til ${navn} ${aar}`}>
      {rader.length === 0 ? (
        <p className="text-[13px] text-[var(--text-muted)]">Ingen resultater i kvalifiseringsperioden i mesterskapets øvelser.</p>
      ) : (
        <table className="w-full text-[14px]">
          <tbody>
            {rader.map((r) => (
              <tr key={r.ovelse} className="border-b border-[var(--border-default)] last:border-0">
                <td className="py-2">{r.ovelse}<span className="ml-2 text-[12px] text-[var(--text-muted)]">krav {r.krav}</span></td>
                <td className="py-2 text-right tabular-nums">
                  {r.klar
                    ? <span className="font-black text-[var(--serie-3)]">Klar</span>
                    : <span className="text-[var(--text-muted)]">{r.avstand}</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <p className="mt-2 text-[12.5px] text-[var(--text-muted)]">
        Oppdateres i det resultatet importeres. <Link href={lenke}>Hele kvalifiseringslisten</Link>
      </p>
    </Kort>
  )
}

/* ---------------------------------------------------------- klubbhistorikk */

export function KlubbHistorikk({ perioder }: { perioder: { id: string | null; navn: string; fra: number; til: number }[] }) {
  if (perioder.length === 0) return null
  return (
    <Kort tittel="Klubbhistorikk">
      <table className="w-full text-[14px]">
        <tbody>
          {perioder.map((p, i) => (
            <tr key={i} className="border-b border-[var(--border-default)] last:border-0">
              <td className="py-2">{p.id ? <Link href={`/klubber/${p.id}`} className="text-[var(--text-primary)]">{p.navn}</Link> : p.navn}</td>
              <td className="py-2 text-right tabular-nums text-[var(--text-secondary)]">{p.fra === p.til ? p.fra : `${p.fra}–${i === 0 ? "" : p.til}`}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Kort>
  )
}

/** Sammenhengende år per klubb, nyeste først. Avbrudd gir ny periode. */
export function klubbPerioder(rader: { club_id: string | null; club_name: string | null; season_year: number | null }[]) {
  const aarPerKlubb = new Map<string, { id: string | null; navn: string; aar: Set<number> }>()
  for (const r of rader) {
    if (!r.season_year || !r.club_name) continue
    const k = aarPerKlubb.get(r.club_name) ?? { id: r.club_id, navn: r.club_name, aar: new Set<number>() }
    k.aar.add(r.season_year); aarPerKlubb.set(r.club_name, k)
  }
  const perioder: { id: string | null; navn: string; fra: number; til: number }[] = []
  for (const k of aarPerKlubb.values()) {
    const aar = [...k.aar].sort((a, b) => a - b)
    let fra = aar[0], til = aar[0]
    for (const a of aar.slice(1)) {
      if (a === til + 1) til = a
      else { perioder.push({ id: k.id, navn: k.navn, fra, til }); fra = til = a }
    }
    perioder.push({ id: k.id, navn: k.navn, fra, til })
  }
  return perioder.sort((a, b) => b.til - a.til || b.fra - a.fra)
}

/* ---------------------------------------------------------- sesongen */

interface Res {
  id: string
  date: string
  event_name: string
  event_code: string
  performance: string
  result_type: string
  wind: number | null
  meet_id: string
  meet_name: string
  meet_indoor: boolean | null
  is_pb: boolean | null
  is_sb: boolean | null
  season_year: number | null
}

function Merkelapp({ farge, children }: { farge: "rod" | "bla" | "gronn" | "graa"; children: React.ReactNode }) {
  const k = {
    rod: "bg-[#fdeaea] text-[#b21f1f]",
    bla: "bg-[#e8eefa] text-[#24487f]",
    gronn: "bg-[#e4f4f0] text-[#0d6b5c]",
    graa: "bg-[#eef0f3] text-[var(--text-secondary)]",
  }[farge]
  return <span className={`inline-block rounded px-1.5 py-0.5 text-[11px] font-bold uppercase tracking-wide ${k}`}>{children}</span>
}

export function SesongTabell({ aar, rader, pbIds }: {
  aar: number; rader: Res[]; pbIds: Set<string>
}) {
  const sesong = rader.filter((r) => r.season_year === aar).sort((a, b) => b.date.localeCompare(a.date))
  const fmtDato = (d: string) => new Date(d).toLocaleDateString("nb-NO", { day: "2-digit", month: "2-digit" })
  return (
    <Kort tittel={`Sesongen ${aar}`}>
      {sesong.length === 0 ? (
        <p className="text-[13px] text-[var(--text-muted)]">Ingen resultater i {aar} ennå.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full whitespace-nowrap text-[14px]">
            <thead>
              <tr className="border-b border-[var(--border-default)] text-left text-[11.5px] uppercase tracking-wide text-[var(--text-muted)]">
                <th className="py-1.5 pr-3 font-bold">Dato</th><th className="py-1.5 pr-3 font-bold">Øvelse</th>
                <th className="py-1.5 pr-3 font-bold">Resultat</th><th className="py-1.5 pr-3 font-bold">Stevne</th>
                <th className="py-1.5 text-right font-bold">Status</th>
              </tr>
            </thead>
            <tbody>
              {sesong.map((r) => {
                const pb = pbIds.has(r.id) || r.is_pb
                const ukjent = harUkjentVind(r)
                const medvind = r.wind !== null && r.wind > 2.0 && !r.meet_indoor
                return (
                  <tr key={r.id} className="border-b border-[var(--border-default)] last:border-0">
                    <td className="py-2 pr-3 tabular-nums text-[var(--text-secondary)]">{fmtDato(r.date)}</td>
                    <td className="max-w-[240px] whitespace-normal py-2 pr-3">{r.event_name}{r.meet_indoor && <span className="ml-1 text-[11px] text-[var(--text-muted)]">(i)</span>}</td>
                    <td className="py-2 pr-3 tabular-nums">
                      <b>{formatPerformance(r.performance, r.result_type)}</b>
                      {r.wind !== null && <span className="ml-1 text-[var(--text-muted)]">({r.wind > 0 ? "+" : ""}{r.wind})</span>}
                    </td>
                    <td className="max-w-[240px] truncate py-2 pr-3"><Link href={`/stevner/${r.meet_id}`} className="text-[var(--text-primary)]" title={r.meet_name}>{r.meet_name}</Link></td>
                    <td className="py-2 text-right">
                      {medvind ? <Merkelapp farge="graa">Medvind</Merkelapp>
                        : ukjent ? <Merkelapp farge="graa">Ukjent vind</Merkelapp>
                          : pb ? <Merkelapp farge="rod">Pers</Merkelapp>
                              : r.is_sb ? <Merkelapp farge="gronn">Sesongbeste</Merkelapp>
                                : null}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </Kort>
  )
}
