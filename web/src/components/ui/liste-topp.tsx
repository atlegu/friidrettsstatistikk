import type { ReactNode } from "react"
import { SokeFelt } from "@/components/ui/soke-felt"

/**
 * Kompakt mørk topp for listesider, med søkefeltet i seg.
 *
 * Listesidene er bruksverktøy, så de får en lavere topp enn utøver-, klubb-
 * og stevnesidene. Søket ligger i toppen fordi det er det man kommer hit for.
 */
export function ListeTopp({
  tittel,
  beskrivelse,
  sokeNavn = "search",
  sokeVerdi,
  plassholder,
  skjulteFelt,
  ekstra,
}: {
  tittel: string
  beskrivelse?: string
  /** Navnet på søkeparameteren i URL-en. */
  sokeNavn?: string
  sokeVerdi?: string
  plassholder: string
  /** Andre aktive parametre som må overleve et søk. */
  skjulteFelt?: Record<string, string | undefined>
  /** Vises under søket, f.eks. filterknapper. */
  ekstra?: ReactNode
}) {
  return (
    <div className="relative -mx-4 overflow-hidden bg-[var(--nfif-navy)] sm:-mx-6 lg:-mx-8">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-gradient-to-br from-[var(--nfif-navy-dyp)] via-[var(--nfif-navy)] to-[var(--nfif-navy-lys)]"
      />
      <div className="relative px-4 py-5 sm:px-6 lg:px-8">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">{tittel}</h1>
            {beskrivelse && (
              <p className="mt-1 text-[13px] text-[var(--nfif-navy-blekk)]">{beskrivelse}</p>
            )}
          </div>

          <form className="w-full md:max-w-sm">
            {Object.entries(skjulteFelt ?? {}).map(([n, v]) =>
              v ? <input key={n} type="hidden" name={n} value={v} /> : null
            )}
            <label htmlFor="listesok" className="sr-only">
              {plassholder}
            </label>
            <SokeFelt
              id="listesok"
              navn={sokeNavn}
              standardVerdi={sokeVerdi}
              plassholder={plassholder}
              krysselasse="right-2.5 text-white"
              klasse="h-11 w-full rounded-lg border border-white/20 bg-white/10 pl-4 pr-10
                      text-[14px] text-white placeholder:text-[var(--nfif-navy-blekk-svak)]
                      outline-none transition-colors focus:border-white/40 focus:bg-white/15"
            />
          </form>
        </div>

        {ekstra && <div className="mt-4">{ekstra}</div>}
      </div>
    </div>
  )
}
