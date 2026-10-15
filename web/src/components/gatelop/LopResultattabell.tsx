"use client"

import { lopetid } from "@/lib/gatelop"

export interface Loprad {
  id: string
  plass: number | null
  navn: string
  fodt: number | null
  klubb: string | null
  klasse: string | null
  tid_ms: number | null
  status: string
  athlete_id: string | null
  nasjon?: string | null
}

const TH = "px-4 py-2.5 text-left text-[11.5px] font-semibold uppercase tracking-wide text-[var(--text-muted)]"

/**
 * Resultatene i ett løp. Klientkomponent av samme grunn som stevnesidenes
 * resultattabell: store løp har flere tusen løpere, og da er det billigere å
 * sende radene som data og tegne dem i nettleseren.
 */
export function LopResultattabell({ rader }: { rader: Loprad[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-[var(--border-default)] bg-[var(--bg-muted)]/60">
            <th className={`${TH} w-12`}>#</th>
            <th className={TH}>Løper</th>
            <th className={`${TH} w-16`}>Født</th>
            <th className={`${TH} hidden md:table-cell`}>Klubb</th>
            <th className={`${TH} hidden sm:table-cell`}>Klasse</th>
            <th className={`${TH} text-right`}>Tid</th>
          </tr>
        </thead>
        <tbody>
          {rader.map((r) => (
            <tr key={r.id} className="border-b border-[var(--border-default)] last:border-0 hover:bg-[var(--bg-muted)]/50">
              <td className="px-4 py-2 text-[13px] tabular-nums text-[var(--text-muted)]">{r.plass ?? ""}</td>
              <td className="px-4 py-2 text-[13.5px]">
                {r.athlete_id ? (
                  <a href={`/utover/${r.athlete_id}`} className="font-medium text-primary hover:underline">
                    {r.navn}
                  </a>
                ) : (
                  <span className="font-medium">{r.navn}</span>
                )}
                {r.nasjon && r.nasjon !== "NOR" && (
                  <span className="ml-1 text-[12px] text-[var(--text-muted)]">{r.nasjon}</span>
                )}
              </td>
              <td className="px-4 py-2 text-[13px] tabular-nums text-[var(--text-muted)]">{r.fodt ?? "–"}</td>
              <td className="hidden px-4 py-2 text-[13px] md:table-cell">{r.klubb ?? ""}</td>
              <td className="hidden px-4 py-2 text-[13px] text-[var(--text-muted)] sm:table-cell">{r.klasse ?? ""}</td>
              <td className="px-4 py-2 text-right">
                <span className="perf-value">{r.status === "OK" ? lopetid(r.tid_ms) : r.status}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
