/** Felles for gateløpssidene (prototype). */

/** Millisekunder til «17:28» eller «1:07:12». Tider i løp utenfor bane
 *  rundes opp til hele sekunder. */
export function lopetid(ms: number | null | undefined): string {
  if (ms == null || ms <= 0) return "–"
  const totalt = Math.ceil(ms / 1000)
  const t = Math.floor(totalt / 3600)
  const m = Math.floor((totalt % 3600) / 60)
  const ss = String(totalt % 60).padStart(2, "0")
  return t > 0 ? `${t}:${String(m).padStart(2, "0")}:${ss}` : `${m}:${ss}`
}

export function distanseTekst(m: number | null | undefined): string {
  if (!m) return "Ukjent distanse"
  if (m === 21097) return "Halvmaraton"
  if (m === 42195) return "Maraton"
  if (m < 1000) return `${m} m`
  return `${(m / 1000).toLocaleString("no-NO", { maximumFractionDigits: 1 })} km`
}

export const NIVAA: Record<string, { tekst: string; kort: string; forklaring: string; klasse: string }> = {
  A: {
    tekst: "A",
    kort: "Rekordgodkjent",
    forklaring: "Rekordgodkjent: sertifisert målt løype (A- eller B-måling) og offisiell distanse",
    klasse: "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200",
  },
  B: {
    tekst: "B",
    kort: "Statistikkgodkjent",
    forklaring: "Statistikkgodkjent: offisiell distanse eller sertifisert målt løype (C-måling)",
    klasse: "bg-[var(--nfif-navy)]/10 text-[var(--nfif-navy)] dark:bg-white/10 dark:text-[var(--nfif-navy-blekk)]",
  },
  C: {
    tekst: "C",
    kort: "Registrert aktivitet",
    forklaring:
      "Registrert aktivitet: terreng-, motbakke- og fjelløp, ikke målt løype, distanse som ikke er standard, eller distanse som må kontrolleres",
    klasse: "bg-[var(--bg-muted)] text-[var(--text-muted)] ring-1 ring-[var(--border-default)]",
  },
}

export function datoKort(d: string): string {
  return new Date(d).toLocaleDateString("no-NO", { day: "numeric", month: "short", year: "numeric" })
}
