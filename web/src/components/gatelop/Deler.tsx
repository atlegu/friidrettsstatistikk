import Link from "next/link"
import type { ReactNode } from "react"
import { NIVAA } from "@/lib/gatelop"

/** Valgknapp i filterradene, samme utforming som på aktivitetssiden. */
export function Chip({ href, aktiv, children }: { href: string; aktiv?: boolean; children: ReactNode }) {
  const klasse =
    "inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-[13px] no-underline transition-colors hover:no-underline " +
    (aktiv
      ? "border-[var(--nfif-navy)] bg-[var(--nfif-navy)] font-semibold text-white"
      : "border-[var(--border-default)] bg-[var(--bg-surface)] text-[var(--text-primary)] hover:border-[var(--nfif-navy-lys)]")
  return (
    <Link href={href} className={klasse}>
      {children}
    </Link>
  )
}

export function Filterrad({ navn, children }: { navn: string; children: ReactNode }) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="w-24 text-[12px] font-bold uppercase tracking-wide text-[var(--text-muted)]">{navn}</span>
      {children}
    </div>
  )
}

/** Hvit flate med avrundede hjørner, som kortene på aktivitetssiden. */
export function Flate({
  tittel,
  undertittel,
  hoyre,
  children,
}: {
  tittel?: ReactNode
  undertittel?: ReactNode
  hoyre?: ReactNode
  children: ReactNode
}) {
  return (
    <section className="overflow-hidden rounded-xl border border-[var(--border-default)] bg-[var(--bg-surface)]">
      {(tittel || hoyre) && (
        <header className="flex flex-wrap items-start justify-between gap-3 border-b border-[var(--border-default)] px-5 py-4">
          <div className="min-w-0">
            {tittel && <h2 className="text-[16px] font-bold tracking-tight">{tittel}</h2>}
            {undertittel && <p className="mt-0.5 text-[13px] text-[var(--text-muted)]">{undertittel}</p>}
          </div>
          {hoyre}
        </header>
      )}
      {children}
    </section>
  )
}

export function Nivaamerke({ nivaa, lang }: { nivaa: string; lang?: boolean }) {
  const n = NIVAA[nivaa] ?? NIVAA.C
  return (
    <span
      title={n.forklaring}
      className={`inline-flex items-center rounded-md px-1.5 py-0.5 text-[11px] font-bold uppercase tracking-wide ${n.klasse}`}
    >
      {lang ? `Nivå ${n.tekst}` : n.tekst}
    </span>
  )
}

/** Forklaring av nivåene, kompakt. */
export function NivaaForklaring() {
  return (
    <div className="flex flex-wrap gap-x-5 gap-y-1.5 text-[12.5px] text-[var(--text-muted)]">
      {Object.entries(NIVAA).map(([k, n]) => (
        <span key={k} className="inline-flex items-center gap-1.5">
          <Nivaamerke nivaa={k} />
          {n.kort}
        </span>
      ))}
    </div>
  )
}

export const TH = "px-4 py-2.5 text-left text-[11.5px] font-semibold uppercase tracking-wide text-[var(--text-muted)]"
export const TD = "px-4 py-2 text-[13.5px]"
