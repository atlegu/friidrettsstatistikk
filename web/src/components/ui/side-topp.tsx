import type { ReactNode } from "react"

export interface Noekkeltall {
  merkelapp: string
  verdi: string | number | null
}

interface SideToppProps {
  tittel: string
  /** Kort linje under tittelen: sted, dato, klubbtype og liknende. */
  meta?: ReactNode
  /** Vises som store tall nederst. Poster uten verdi utelates. */
  noekkeltall?: Noekkeltall[]
  /** Knapper eller lenker til høyre. */
  handlinger?: ReactNode
  /** Merkelapper rett under metalinja, f.eks. «Innendørs». */
  merker?: ReactNode
  /** Rundt bilde eller initialer til venstre. */
  bilde?: ReactNode
}

/**
 * Mørk topp i Norsk Friidretts profil, brukt på utøver-, klubb- og
 * stevnesider.
 *
 * Toppen går helt ut til kanten. Sidene ligger i en `.container` med
 * sidepadding på 1/1,5/2 rem, så den trekkes ut igjen med negative marger
 * som matcher nøyaktig.
 */
export function SideTopp({
  tittel,
  meta,
  noekkeltall,
  handlinger,
  merker,
  bilde,
}: SideToppProps) {
  const tall = (noekkeltall ?? []).filter(
    (n) => n.verdi !== null && n.verdi !== undefined && n.verdi !== ""
  )

  return (
    <div className="relative -mx-4 overflow-hidden bg-[var(--nfif-navy)] sm:-mx-6 lg:-mx-8">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-gradient-to-br from-[var(--nfif-navy-dyp)] via-[var(--nfif-navy)] to-[var(--nfif-navy-lys)]"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute -right-24 -top-40 hidden h-[420px] w-[420px] rounded-full border-[56px] border-white/[0.045] lg:block"
      />

      <div className="relative px-4 py-6 sm:px-6 lg:px-8">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:gap-7">
          {bilde && <div className="flex-shrink-0">{bilde}</div>}

          <div className="min-w-0 flex-1">
            <h1 className="text-2xl font-bold tracking-tight text-white sm:text-[2rem]">
              {tittel}
            </h1>

            {meta && (
              <div className="mt-1.5 flex flex-wrap items-center gap-x-2 gap-y-0.5 text-[13px] text-[var(--nfif-navy-blekk)]">
                {meta}
              </div>
            )}

            {merker && (
              <div className="mt-3 flex flex-wrap items-center gap-2">{merker}</div>
            )}

            {tall.length > 0 && (
              <dl className="mt-4 flex flex-wrap gap-x-8 gap-y-3">
                {tall.map((n) => (
                  <div key={n.merkelapp}>
                    <dt className="text-[10.5px] font-bold uppercase tracking-[0.07em] text-[var(--nfif-navy-blekk-svak)]">
                      {n.merkelapp}
                    </dt>
                    <dd className="text-xl font-bold tabular-nums text-white sm:text-2xl">
                      {typeof n.verdi === "number"
                        ? n.verdi.toLocaleString("no-NO")
                        : n.verdi}
                    </dd>
                  </div>
                ))}
              </dl>
            )}
          </div>

          {handlinger && (
            <div className="flex flex-shrink-0 flex-wrap items-center gap-2 sm:flex-col sm:items-stretch">
              {handlinger}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

/** Skillepunkt i metalinja. */
export function MetaSkille() {
  return <span className="text-[var(--nfif-navy-blekk-svak)]">·</span>
}

/** Knapp på mørk flate, til `handlinger`. */
export function ToppKnapp({
  href,
  children,
  fremhevet,
}: {
  href: string
  children: ReactNode
  fremhevet?: boolean
}) {
  return (
    <a
      href={href}
      className={
        "inline-flex items-center justify-center gap-1.5 whitespace-nowrap rounded-lg px-4 py-2 " +
        "text-[13px] font-medium transition-colors " +
        (fremhevet
          ? "bg-[var(--nfif-rod)] font-bold text-white hover:opacity-90"
          : "border border-white/25 bg-white/10 text-white hover:bg-white/20")
      }
    >
      {children}
    </a>
  )
}

/** Merkelapp på mørk flate, til `merker`. */
export function ToppMerke({ children }: { children: ReactNode }) {
  return (
    <span className="rounded-md bg-white/10 px-2 py-0.5 text-[11px] font-bold uppercase tracking-wide text-white ring-1 ring-white/20">
      {children}
    </span>
  )
}
