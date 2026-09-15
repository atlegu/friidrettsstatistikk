/**
 * Hvilke øvelser vinden gjelder for.
 *
 * Regelen (WA 17.9 / NFIF): sprint til og med 200 m, hekk til og med 200 m,
 * og horisontale hopp med tilløp. Ikke vertikale hopp, ikke hopp uten
 * tilløp, ikke lengre løp, ikke mangekamp.
 *
 * Samme regel ligger i basen som `er_vindpaavirket(code)`, og en trigger
 * setter `is_wind_legal` fra den for hver rad. Endres regelen her, må den
 * endres der - se scraper/migrations/vindflagg.sql.
 *
 * Tidligere sto det `WIND_AFFECTED_CATEGORIES = ["jumps"]` i tre sider, og
 * kategorien «jumps» omfatter også høyde, stav og hoppene uten tilløp. De
 * fikk dermed samme vindkrav som lengde, og 5 204 høyderesultater og 1 550
 * stavresultater uten vindverdi ble stille utelatt fra årslistene. Hekk
 * manglet, og fikk ikke vindkrav i det hele tatt.
 *
 * Ukjent vind: en vindpåvirket øvelse utendørs uten målt vind. Innendørs er
 * vinden ikke ukjent, den finnes ikke, så innendørsresultater regnes som
 * vanlige.
 */
const SPRINT_MED_VIND = new Set(["60m", "80m", "100m", "150m", "200m"])
const HEKK_MED_VIND = /^(30|40|55|60|80|100|110|200)(mh|_m_h)/

export function erVindpaavirket(eventCode: string | null | undefined): boolean {
  if (!eventCode) return false
  if (SPRINT_MED_VIND.has(eventCode)) return true
  if (HEKK_MED_VIND.test(eventCode)) return true
  // lengde, tresteg, lengde_sone_05m, tresteg_sone_05m ... men ikke *_ut
  return (
    (eventCode.startsWith("lengde") || eventCode.startsWith("tresteg")) &&
    !eventCode.endsWith("_ut")
  )
}

export function harUkjentVind(r: {
  event_code?: string | null
  wind: number | null
  meet_indoor: boolean | null
}): boolean {
  return erVindpaavirket(r.event_code) && r.wind === null && !r.meet_indoor
}
