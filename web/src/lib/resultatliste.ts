/* Resultatlister på friidrettens standardmal (Excel), slik arrangørene sender
 * dem til resultater@friidrett.no. Brukes av admin-importen.
 *
 * Reglene er de samme som i scraper/importer_resultatliste.py og som når
 * stevnet senere kommer fra minfriidrettsstatistikk.info, slik at
 * kildeimporten kjenner igjen radene (utøver, øvelse, resultat, plass) og
 * ikke legger dem inn på nytt:
 *   - resultat i meter med to desimaler («21.20»), mangekamp som heltall poeng
 *   - «nm», «dns», «dnf» legges ikke inn
 *   - stevnested er anlegget (venue), ikke byen
 *
 * Malen: «Stevne:», «Stevnested:», «Stevnedato:», «Arrangør», «Utendørs:»
 * (Y/J/N), så blokker med klasse og øvelse på én rad («MV70 | Kule 4,0kg»)
 * og resultatrader under (plass | [startnr] | navn | år | klubb | resultat |
 * vind). Kastfemkamp har delresultatene på en egen rad i parentes. */

export type ListeRad = {
  place?: string
  bib?: string
  name: string
  birth_year?: string
  club?: string
  performance?: string
  wind?: string
  event?: string
  event_class?: string
  round?: string
  indoor?: boolean
  delresultater?: string
  organizer?: string
}

export type ListeInfo = {
  meetName?: string
  meetVenue?: string
  meetDateFrom?: string
  meetDateTo?: string
  organizer?: string
  outdoor?: boolean
  conditions?: string
}

export const IKKE_RESULTAT = new Set(["nm", "dns", "dnf", "dq", "dsq", "-", "x", "brutt", "ikke startet"])

const FORKORTELSER: Record<string, string> = { fil: "friidrettslag", fik: "friidrettskrets", fk: "friidrettsklubb" }

const SLEGGE: Record<string, string> = {
  "7.26": "slegge_726kg/1215cm", "6": "slegge_60kg/1215cm", "5": "slegge_50kg/120cm",
  "4": "slegge_40kg/1195cm", "3": "slegge_30kg_1195cm", "2": "slegge_20kg/110cm",
}
const KULE: Record<string, string> = {
  "7.26": "kule_7_26kg", "6": "kule_6kg", "5": "kule_5kg", "4": "kule_4kg", "3": "kule_3kg", "2": "kule_2kg",
}
const DISKOS: Record<string, string> = {
  "2": "diskos_2kg", "1.75": "diskos_1_75kg", "1.5": "diskos_1_5kg", "1": "diskos_1kg",
  "0.75": "diskos_750g", "0.6": "diskos_600g",
}
const SPYD: Record<string, string> = {
  "0.8": "spyd_800g", "0.7": "spyd_700g", "0.6": "spyd_600g", "0.5": "spyd_500g", "0.4": "spyd_400g",
}
const VEKT: Record<string, string> = {
  "15.88": "vektkast_1588kg", "11.34": "vektkast_1134kg", "9.08": "vektkast_908kg",
  "7.26": "vektkast_726kg", "5.45": "vektkast_545kg", "4": "vektkast40kg",
}
const FEMKAMP = "kast_5_k_slegge-kule-diskos-spyd-vektkast"

export function tall(v: unknown): number | null {
  if (v === null || v === undefined || v === "") return null
  const n = Number(String(v).replace(",", ".").trim())
  return Number.isFinite(n) ? n : null
}

/** «6,0kg» -> 6, «400gr» -> 0.4, «0,75kg» -> 0.75 */
function vektKg(tekst: string): number | null {
  const m = tekst.toLowerCase().match(/(\d+(?:[.,]\d+)?)\s*(kg|gr|gram|g)\b/)
  if (!m) return null
  const v = tall(m[1])
  if (v === null) return null
  return m[2] === "kg" ? v : Math.round(v) / 1000
}

export function kjonnFraKlasse(klasse: string | undefined): "M" | "F" | null {
  const k = (klasse ?? "").trim().toUpperCase()
  if (/^(J|K)/.test(k)) return "F"
  if (/^(G|M)/.test(k)) return "M"
  return null
}

/** Øvelseskode for kastøvelser med vekt (og kastfemkamp per klasse). Andre
 *  øvelser gir null og matches på navn som før. */
export function kastkode(oevelse: string, klasse: string | undefined): string | null {
  const o = oevelse.toLowerCase()
  if (o.includes("kast") && o.includes("kamp")) {
    const k = (klasse ?? "").toUpperCase().replace(/-/g, "")
    if (k.startsWith("KV") || k.startsWith("MV")) return `${FEMKAMP}_veteran`
    if (k.startsWith("G") || k.startsWith("J")) return `${FEMKAMP}_ungdom`
    return FEMKAMP
  }
  const w = vektKg(oevelse)
  if (w === null) return null
  const n = String(Number(w.toFixed(3)))
  const tabeller: [string, Record<string, string>][] = [
    ["slegge", SLEGGE], ["kule", KULE], ["diskos", DISKOS], ["spyd", SPYD], ["vekt", VEKT],
  ]
  for (const [prefiks, tabell] of tabeller) if (o.startsWith(prefiks)) return tabell[n] ?? null
  return null
}

/** Mangekamp på koden: «7_k_…», «kast_5_k_…», «5kamp». Resultattypen hjelper
 *  ikke - de fleste mangekampene står med «distance» i events. */
export function erMangekamp(code: string | null | undefined): boolean {
  return !!code && /(^|_)\d+_k_|kamp/.test(code)
}

const deler = (navn: string) => navn.toLowerCase().normalize("NFC").split(/\s+/).filter(Boolean)

/** Er «Helge Lorentzen» og «Helge Andreas Lorentzen» samme navn? Eksakt, eller
 *  samme fornavn og etternavn der det ene har mellomnavn det andre mangler. */
export function navnTreff(fraFil: string, iBasen: string): "eksakt" | "mellomnavn" | null {
  const a = deler(fraFil)
  const b = deler(iBasen)
  if (!a.length || !b.length) return null
  if (a.join(" ") === b.join(" ")) return "eksakt"
  if (a[0] !== b[0] || a[a.length - 1] !== b[b.length - 1]) return null
  const sa = new Set(a)
  const sb = new Set(b)
  const iA = b.every((d) => sa.has(d))
  const iB = a.every((d) => sb.has(d))
  return iA || iB ? "mellomnavn" : null
}

/** Klubbnavn uten rekkefølge og med vanlige forkortelser skrevet ut:
 *  «IL Norna-Salhus» = «Norna-Salhus IL», «Gloppen FIL» = «Gloppen Friidrettslag». */
export function klubbNoekkel(navn: string | null | undefined): string {
  return (navn ?? "")
    .toLowerCase()
    .replace(/[^a-zæøåäöü0-9\- ]/g, " ")
    .split(/\s+/)
    .filter(Boolean)
    .map((d) => FORKORTELSER[d] ?? d)
    .sort()
    .join(" ")
}

/** Arrangør med forkortelser skrevet ut: «Hordaland FIK» -> «Hordaland Friidrettskrets». */
export function arrangorNavn(navn: string | undefined): string | null {
  if (!navn?.trim()) return null
  return navn
    .trim()
    .split(/\s+/)
    .map((d) => {
      const full = FORKORTELSER[d.toLowerCase()]
      return full ? full.charAt(0).toUpperCase() + full.slice(1) : d
    })
    .join(" ")
}

/** Resultatet slik kildeimporten fører det (fix_performance_format i
 *  update_results.py): tider over ett minutt som «7:54.96» (fra «7,54,96» /
 *  «7.54.96»), kortere tider og lengder som «12.34», mangekamp som poeng.
 *  Triggeren i basen regner performance_value ut fra dette. */
export function formaterResultat(raw: string, code: string | null | undefined, resultType: string | null | undefined): string {
  const t = raw.trim().replace(/,/g, ".")
  if (erMangekamp(code)) {
    const n = tall(t)
    return n === null ? t : String(Math.round(n))
  }
  if (resultType === "time") {
    let m = t.match(/^(\d{1,2})\.(\d{2})\.(\d{2})\.(\d{1,2})$/)
    if (m) return `${m[1]}:${m[2]}:${m[3]}.${m[4]}`
    m = t.match(/^(\d{1,2})\.(\d{2})\.(\d{1,2})$/)
    if (m) return `${m[1]}:${m[2]}.${m[3]}`
    // Ikke fyll på desimaler: «11.7» er manuell tid, «11.70» elektronisk
    return t
  }
  const n = tall(t)
  return n === null ? t : n.toFixed(2)
}

function excelDato(v: unknown): string | undefined {
  if (typeof v === "number" && v > 30000) {
    const d = new Date(Date.UTC(1899, 11, 30) + Math.round(v) * 86400000)
    return d.toISOString().slice(0, 10)
  }
  const s = String(v ?? "").trim()
  let m = s.match(/^(\d{1,2})\.(\d{1,2})\.(\d{4})$/)
  if (m) return `${m[3]}-${m[2].padStart(2, "0")}-${m[1].padStart(2, "0")}`
  m = s.match(/^(\d{4})-(\d{2})-(\d{2})/)
  return m ? m[0] : undefined
}

const celle = (v: unknown) => (v === null || v === undefined ? "" : String(v).trim())

/** Les arket. `data` er rådataene (XLSX.utils.sheet_to_json(ark, {header: 1})),
 *  `vist` det samme med teksten slik Excel viser den ({header: 1, raw: false}).
 *  Resultatene leses fra den viste teksten: en tallcelle med 11,70 er 11.7 i
 *  rådataene, og da ser en elektronisk tid ut som en manuell. */
export function lesResultatliste(data: unknown[][], vist?: unknown[][]): { info: ListeInfo; rows: ListeRad[]; warnings: string[] } {
  const info: ListeInfo = {}
  const rows: ListeRad[] = []
  const warnings: string[] = []
  let klasse = ""
  let oevelse = ""
  let vind = ""

  data.forEach((rad, i) => {
    if (!rad || rad.length === 0) return
    const c = Array.from({ length: Math.max(8, rad.length) }, (_, k) => celle(rad[k]))
    const hode = c[0].replace(/[:*\s]+$/, "").toLowerCase()

    if (hode === "stevne") { info.meetName = c[1]; return }
    if (hode === "stevnested") { info.meetVenue = c[1]; return }
    if (hode === "stevnedato") {
      info.meetDateFrom = excelDato(rad[1])
      info.meetDateTo = excelDato(rad[2]) ?? info.meetDateFrom
      return
    }
    if (hode === "arrangør") { info.organizer = c[1]; return }
    if (hode === "utendørs") { info.outdoor = ["Y", "J", "JA", "YES"].includes(c[1].toUpperCase()); return }
    if (hode === "heat" || hode === "finale") { vind = c[3]; return }
    if (["kontaktperson", "erklæring", "resultatliste"].includes(hode)) return
    if (c[0].endsWith(":") && !/^\d/.test(c[0])) return
    if (c[0].startsWith("<") || c[1].startsWith("<")) return       // malens plassholdere

    // Fritekst om forholdene (vær, vind) rett under toppteksten
    if (!c[0] && c[1] && c.slice(2).every((x) => !x) && !info.conditions && !oevelse) {
      info.conditions = c[1]
      return
    }
    // Delresultater i kastfemkamp: «(26,88-7,86-24,08-21,98-9,23)»
    if (c[0].startsWith("(")) {
      const forrige = rows[rows.length - 1]
      if (forrige && forrige.event === oevelse) forrige.delresultater = c[0].replace(/[()]/g, "")
      return
    }
    // Ny klasse og øvelse: tekst i første celle, øvelse i andre, resten tomt
    if (c[0] && tall(c[0]) === null && c[1] && c.slice(2).every((x) => !x)) {
      klasse = c[0]
      oevelse = c[1]
      vind = ""
      return
    }

    const plass = tall(c[0])
    if (!oevelse || (c[0] && plass === null)) return
    // Med startnummer: [plass, nr, navn, år, klubb, res, vind]; uten: [plass, navn, år, klubb, res, vind]
    const utenNr = tall(c[1]) === null && /^\d{4}$/.test(c[2].replace(/\.0$/, ""))
    const o = utenNr ? -1 : 0
    const navn = c[2 + o].replace(/\s+/g, " ")
    if (!navn) return
    const visteRad = vist?.[i]
    const resultat = (visteRad ? celle(visteRad[5 + o]) : "") || c[5 + o]
    if (!resultat || IKKE_RESULTAT.has(resultat.toLowerCase())) {
      warnings.push(`Linje ${i + 1}: ${navn}, ${klasse} ${oevelse}: «${resultat || "tomt"}» legges ikke inn`)
      return
    }
    rows.push({
      place: plass ? String(Math.round(plass)) : undefined,
      bib: utenNr ? undefined : c[1],
      name: navn,
      birth_year: c[3 + o].replace(/\.0$/, ""),
      club: c[4 + o],
      performance: resultat,
      wind: c[6 + o] || vind || undefined,
      event: oevelse,
      event_class: klasse,
    })
  })

  return { info, rows, warnings }
}
