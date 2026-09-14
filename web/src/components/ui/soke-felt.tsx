"use client"

import { useRef, useState } from "react"
import { X } from "lucide-react"

/**
 * Søkefelt med et vanlig kryss til å tømme teksten.
 *
 * Nettleserne tegner sitt eget tømmeikon inne i input[type=search], men vi
 * bestemmer ikke hvordan det ser ut: i Safari blir det en fylt sirkel med
 * kors som leses som en emoji, og på de mørke feltene er det nesten
 * usynlig. Det er slått av i globals.css, og krysset her tegnes i stedet.
 *
 * Er feltet knyttet til et søk som allerede er utført, sender krysset
 * skjemaet på nytt med tom tekst, slik at man kommer tilbake til hele
 * lista. Ellers tømmer det bare feltet.
 */
export function SokeFelt({
  id,
  navn = "search",
  standardVerdi = "",
  plassholder,
  klasse,
  krysselasse,
  autoFokus,
  onEndret,
}: {
  id: string
  navn?: string
  standardVerdi?: string
  plassholder: string
  /** Klasser på selve inputen. Husk plass til krysset til høyre. */
  klasse: string
  /** Plassering av krysset, f.eks. «right-16» når det står en knapp der. */
  krysselasse?: string
  autoFokus?: boolean
  /** Kalles ved hver endring, for felt uten skjema rundt seg. */
  onEndret?: (verdi: string) => void
}) {
  const [verdi, setVerdi] = useState(standardVerdi)
  const feltet = useRef<HTMLInputElement>(null)

  function skriv(ny: string) {
    setVerdi(ny)
    onEndret?.(ny)
  }

  function tom() {
    skriv("")
    const felt = feltet.current
    felt?.focus()
    // Et utført søk må også fjernes fra lista, ikke bare fra feltet.
    if (felt && standardVerdi) {
      felt.value = ""
      felt.form?.requestSubmit()
    }
  }

  return (
    <div className="relative">
      <input
        ref={feltet}
        id={id}
        type="search"
        name={navn}
        value={verdi}
        onChange={(e) => skriv(e.target.value)}
        placeholder={plassholder}
        autoFocus={autoFokus}
        className={klasse}
      />
      {verdi && (
        <button
          type="button"
          onClick={tom}
          aria-label="Tøm søket"
          className={
            "absolute top-1/2 flex h-6 w-6 -translate-y-1/2 items-center " +
            "justify-center rounded-full opacity-60 transition-opacity " +
            "hover:opacity-100 " +
            (krysselasse ?? "right-2.5")
          }
        >
          <X className="h-4 w-4" strokeWidth={2.5} aria-hidden />
        </button>
      )}
    </div>
  )
}
