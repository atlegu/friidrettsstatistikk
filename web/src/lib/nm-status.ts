import {
  getChampionship,
  getEventCodes,
  getStandardValue,
  isWindAffected,
  shouldFilterManualTimes,
  formatStandardDisplay,
  type Championship,
  type QualificationStandard,
} from "@/lib/championship-config"

/** Det utøverprofilen trenger av et resultat for å vurdere NM-krav. */
export interface KravResultat {
  id?: string
  date: string
  event_code: string
  performance_value: number | null
  wind: number | null
  meet_indoor: boolean | null
  is_manual_time?: boolean | null
}

export interface KravStatus {
  ovelse: string
  /** Øvelseskodene kravet gjelder, til merking i resultattabellen. */
  koder: string[]
  krav: string
  beste: string | null
  klar: boolean
  /** Avstand til kravet i samme enhet som kravet, negativ = mangler. */
  avstand: string | null
}

function fmtAvstand(diff: number, type: QualificationStandard["resultType"]): string {
  if (type === "time") return `${(diff / 100).toFixed(2).replace(".", ",")} s`
  return `${(diff / 1000).toFixed(2).replace(".", ",")} m`
}

/**
 * Status mot kravene i ett mesterskap, for øvelsene utøveren faktisk har
 * resultater i. Samme regler som NM-kvalifiseringslisten: kvalifiserings-
 * vindu, lovlig vind, ikke håndtid i sprint og hekk, innendørs bare der
 * reglementet tillater det.
 */
export function nmStatus(
  championshipId: string,
  gender: "M" | "F",
  birthYear: number | null,
  resultater: KravResultat[]
): { mesterskap: Championship; rader: KravStatus[]; klareIds: Set<string> } | null {
  const m = getChampionship(championshipId)
  if (!m) return null
  /** Enkeltresultater som selv oppfyller kravet, til merking i tabeller. */
  const klareIds = new Set<string>()

  // Juniorklasse dersom mesterskapet har aldersklasser og utøveren passer
  const klasse = m.ageClasses && birthYear
    ? m.ageClasses.filter((a) => birthYear >= a.minBirthYear).sort((a, b) => b.minBirthYear - a.minBirthYear)[0]?.id
    : undefined

  const rader: KravStatus[] = []
  for (const s of m.standards) {
    const krav = getStandardValue(s, gender, klasse)
    if (krav === undefined) continue
    const koder = new Set(getEventCodes(s, gender, klasse))
    const filtrerManuell = shouldFilterManualTimes([...koder])

    const aktuelle = resultater.filter((r) =>
      koder.has(r.event_code) &&
      r.performance_value !== null && r.performance_value > 0 &&
      r.date >= m.qualificationStart && r.date <= m.qualificationEnd &&
      (s.indoorCounts || !r.meet_indoor) &&
      !(filtrerManuell && r.is_manual_time === true) &&
      !(isWindAffected(r.event_code) && !r.meet_indoor && !(r.wind !== null && r.wind <= 2.0))
    )
    if (aktuelle.length === 0) continue

    const lavereErBedre = s.resultType === "time"
    const beste = aktuelle.reduce((b, r) =>
      (lavereErBedre ? r.performance_value! < b.performance_value! : r.performance_value! > b.performance_value!) ? r : b
    )
    const bv = beste.performance_value!
    const klar = lavereErBedre ? bv <= krav : bv >= krav
    for (const r of aktuelle) {
      const v = r.performance_value!
      if (r.id && (lavereErBedre ? v <= krav : v >= krav)) klareIds.add(r.id)
    }
    const diff = lavereErBedre ? krav - bv : bv - krav   // positiv = innenfor
    rader.push({
      ovelse: s.displayName,
      koder: [...koder],
      krav: formatStandardDisplay(krav, s.resultType),
      beste: formatStandardDisplay(bv, s.resultType),
      klar,
      avstand: klar ? null : `−${fmtAvstand(-diff, s.resultType)}`,
    })
  }
  return { mesterskap: m, rader, klareIds }
}
