import Link from "next/link"
import { notFound } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"
import { formatPerformance } from "@/lib/format-performance"
import { getBirthYear } from "@/lib/date-utils"
import {
  getChampionship,
  getStandardValue,
  getEventCodes,
  getDisplayStandard,
  isWindAffected,
  shouldFilterManualTimes,
  EVENT_CATEGORY_LABELS,
  EVENT_CATEGORY_ORDER,
  type QualificationStandard,
  type Championship,
} from "@/lib/championship-config"
import { ClubFilter } from "@/components/championship/ClubFilter"

export const dynamic = 'force-dynamic'

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const championship = getChampionship(id)
  if (!championship) return { title: "Mesterskap ikke funnet" }
  return {
    title: `Kvalifiserte – ${championship.name}`,
    description: `Utøvere kvalifisert for ${championship.name}`,
  }
}

// --- Data fetching ---

async function getQualifiedAthletesForQuery(
  standard: QualificationStandard,
  gender: 'M' | 'F',
  championship: Championship,
  ageClassId?: string,
  clubId?: string
) {
  const threshold = getStandardValue(standard, gender, ageClassId)
  if (!threshold) return []

  const eventCodes = getEventCodes(standard, gender, ageClassId)
  if (!eventCodes.length) return []

  const supabase = await createClient()

  let query = supabase
    .from('results_full')
    .select('athlete_id, athlete_name, birth_date, club_id, club_name, performance, performance_value, result_type, wind, meet_name, meet_id, date, event_code, meet_indoor')
    .in('event_code', eventCodes)
    .gte('date', championship.qualificationStart)
    .lte('date', championship.qualificationEnd)
    .eq('gender', gender)
    .eq('status', 'OK')
    .gt('performance_value', 0)

  if (standard.resultType === 'time') {
    query = query.lte('performance_value', threshold)
  } else {
    query = query.gte('performance_value', threshold)
  }

  // Technical events: outdoor only (unless indoorCounts is true)
  if (!standard.indoorCounts) {
    query = query.eq('meet_indoor', false)
  }

  // Filter manual times for sprint/hurdle events
  if (shouldFilterManualTimes(eventCodes)) {
    query = query.eq('is_manual_time', false)
  }

  // Filter wind-assisted results
  if (eventCodes.some(isWindAffected)) {
    query = query.eq('is_wind_legal', true)
  }

  // Club filter
  if (clubId) {
    query = query.eq('club_id', clubId)
  }

  // Junior age filter
  if (ageClassId && championship.ageClasses) {
    const ac = championship.ageClasses.find(a => a.id === ageClassId)
    if (ac) {
      query = query.gte('birth_date', `${ac.minBirthYear}-01-01`)
    }
  }

  const ascending = standard.resultType === 'time'
  query = query.order('performance_value', { ascending }).limit(500)

  const { data } = await query

  // Deduplicate: best result per athlete
  const bestByAthlete = new Map<string, NonNullable<typeof data>[0]>()
  for (const r of data ?? []) {
    if (r.athlete_id && !bestByAthlete.has(r.athlete_id)) {
      bestByAthlete.set(r.athlete_id, r)
    }
  }
  return Array.from(bestByAthlete.values())
}

async function getQualifiedAthletes(
  standard: QualificationStandard,
  gender: 'M' | 'F',
  championship: Championship,
  ageClassId?: string,
  clubId?: string
) {
  // For junior "Alle" view: merge U23 and U20 results
  if (championship.type === 'junior' && !ageClassId && championship.ageClasses) {
    const allResults = await Promise.all(
      championship.ageClasses.map(ac =>
        getQualifiedAthletesForQuery(standard, gender, championship, ac.id, clubId)
      )
    )

    const ascending = standard.resultType === 'time'
    const bestByAthlete = new Map<string, (typeof allResults)[0][0]>()
    for (const results of allResults) {
      for (const r of results) {
        if (!r.athlete_id) continue
        const existing = bestByAthlete.get(r.athlete_id)
        if (!existing) {
          bestByAthlete.set(r.athlete_id, r)
        } else {
          const better = ascending
            ? (r.performance_value ?? 0) < (existing.performance_value ?? 0)
            : (r.performance_value ?? 0) > (existing.performance_value ?? 0)
          if (better) bestByAthlete.set(r.athlete_id, r)
        }
      }
    }

    const merged = Array.from(bestByAthlete.values())
    merged.sort((a, b) => ascending
      ? (a.performance_value ?? 0) - (b.performance_value ?? 0)
      : (b.performance_value ?? 0) - (a.performance_value ?? 0)
    )
    return merged
  }

  return getQualifiedAthletesForQuery(standard, gender, championship, ageClassId, clubId)
}

async function getQualifiedCount(
  standard: QualificationStandard,
  gender: 'M' | 'F',
  championship: Championship,
  ageClassId?: string,
  clubId?: string
): Promise<number> {
  const results = await getQualifiedAthletes(standard, gender, championship, ageClassId, clubId)
  return results.length
}

// --- Page ---

export default async function ChampionshipDetailPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>
  searchParams: Promise<{ gender?: string; event?: string; age?: string; club?: string }>
}) {
  const { id } = await params
  const championship = getChampionship(id)
  if (!championship) notFound()

  const { gender = 'M', event: eventSlug, age: ageClassId, club: clubId } = await searchParams
  const genderKey = (gender === 'F' ? 'F' : 'M') as 'M' | 'F'
  const validAgeClassId = championship.ageClasses?.find(ac => ac.id === ageClassId)?.id

  // Look up club name if filtered
  let clubName: string | null = null
  if (clubId) {
    const supabaseForClub = await createClient()
    const { data: clubData } = await supabaseForClub
      .from('clubs')
      .select('name')
      .eq('id', clubId)
      .single()
    clubName = clubData?.name ?? null
  }

  // Filter standards to those with a value for the selected gender+age
  const filteredStandards = championship.standards.filter(s =>
    getStandardValue(s, genderKey, validAgeClassId) !== undefined
  )

  // Select event (default to first)
  const selectedStandard = filteredStandards.find(s => s.id === eventSlug) ?? filteredStandards[0]

  // Get qualified athletes for selected event
  const results = selectedStandard
    ? await getQualifiedAthletes(selectedStandard, genderKey, championship, validAgeClassId, clubId)
    : []

  // Get counts for all events in sidebar
  const counts = await Promise.all(
    filteredStandards.map(async (s) => {
      const count = await getQualifiedCount(s, genderKey, championship, validAgeClassId, clubId)
      return { id: s.id, count }
    })
  )
  const countMap = new Map(counts.map(c => [c.id, c.count]))

  // Group events by category for sidebar
  const groupedStandards = EVENT_CATEGORY_ORDER
    .map(catId => ({
      id: catId,
      name: EVENT_CATEGORY_LABELS[catId],
      standards: filteredStandards.filter(s => s.category === catId),
    }))
    .filter(g => g.standards.length > 0)

  const genderLabel = genderKey === 'M' ? 'Menn' : 'Kvinner'
  const ageLabel = validAgeClassId
    ? championship.ageClasses?.find(ac => ac.id === validAgeClassId)?.label ?? validAgeClassId
    : championship.type === 'junior' ? 'Alle klasser' : undefined

  const buildUrl = (overrides: { gender?: string; event?: string; age?: string }) => {
    const p = new URLSearchParams()
    const g = overrides.gender ?? gender
    const e = overrides.event ?? selectedStandard?.id
    const a = overrides.age !== undefined ? overrides.age : (ageClassId ?? '')
    if (g) p.set('gender', g)
    if (e) p.set('event', e)
    if (a) p.set('age', a)
    if (clubId) p.set('club', clubId)
    return `/mesterskap/${id}?${p.toString()}`
  }

  const displayStd = selectedStandard ? getDisplayStandard(selectedStandard, genderKey, validAgeClassId) : undefined

  return (
    <div className="container py-6">
      <Breadcrumbs items={[
        { label: "Mesterskap", href: "/mesterskap" },
        { label: championship.name },
      ]} />
      <h1 className="mt-4 mb-2">{championship.name}</h1>
      <p className="mb-6 text-sm text-muted-foreground">
        {championship.date} · Kvalifiseringsperiode fra {new Date(championship.qualificationStart + 'T12:00:00').toLocaleDateString("no-NO", { day: "numeric", month: "short", year: "numeric" })}
      </p>

      <div className="grid gap-8 lg:grid-cols-5">
        {/* Sidebar */}
        <div className="lg:col-span-1 space-y-4 lg:max-w-[200px]">
          {/* Gender filter */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Kjønn</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Link
                  href={buildUrl({ gender: 'M' })}
                  className={`flex-1 rounded px-3 py-2 text-center text-sm font-medium ${
                    genderKey === 'M'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted hover:bg-muted/80'
                  }`}
                >
                  Menn
                </Link>
                <Link
                  href={buildUrl({ gender: 'F' })}
                  className={`flex-1 rounded px-3 py-2 text-center text-sm font-medium ${
                    genderKey === 'F'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted hover:bg-muted/80'
                  }`}
                >
                  Kvinner
                </Link>
              </div>
            </CardContent>
          </Card>

          {/* Age class filter (junior only) */}
          {championship.ageClasses && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Klasse</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-1">
                  <Link
                    href={buildUrl({ age: '' })}
                    className={`block rounded px-2 py-1 text-sm ${
                      !validAgeClassId
                        ? 'bg-primary text-primary-foreground'
                        : 'hover:bg-muted'
                    }`}
                  >
                    Alle
                  </Link>
                  {championship.ageClasses.map((ac) => (
                    <Link
                      key={ac.id}
                      href={buildUrl({ age: ac.id })}
                      className={`block rounded px-2 py-1 text-sm ${
                        validAgeClassId === ac.id
                          ? 'bg-primary text-primary-foreground'
                          : 'hover:bg-muted'
                      }`}
                    >
                      {ac.label}
                    </Link>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Club filter */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Klubb</CardTitle>
            </CardHeader>
            <CardContent>
              <ClubFilter
                championshipId={id}
                currentParams={{ gender, event: selectedStandard?.id ?? '', age: ageClassId ?? '' }}
                selectedClubName={clubName}
              />
            </CardContent>
          </Card>

          {/* Events by category */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Øvelser</CardTitle>
            </CardHeader>
            <CardContent className="max-h-[60vh] overflow-y-auto">
              {groupedStandards.map((group) => (
                <div key={group.id} className="mb-3">
                  <p className="mb-1 text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                    {group.name}
                  </p>
                  <div className="space-y-0.5">
                    {group.standards.map((s) => {
                      const isSelected = selectedStandard?.id === s.id
                      const display = getDisplayStandard(s, genderKey, validAgeClassId)
                      const count = countMap.get(s.id) ?? 0
                      return (
                        <Link
                          key={s.id}
                          href={buildUrl({ event: s.id })}
                          className={`flex items-center justify-between rounded px-2 py-1 text-sm ${
                            isSelected
                              ? 'bg-primary text-primary-foreground'
                              : 'hover:bg-muted'
                          }`}
                        >
                          <span className={s.notInChampionship ? 'italic' : ''}>
                            {s.displayName}
                          </span>
                          <span className="flex items-center gap-1.5 text-xs tabular-nums">
                            <span className={isSelected ? 'text-primary-foreground/70' : 'text-muted-foreground'}>
                              {display}
                            </span>
                            {count > 0 && (
                              <span className={`rounded-full px-1.5 py-0.5 text-[10px] font-medium ${
                                isSelected
                                  ? 'bg-primary-foreground/20 text-primary-foreground'
                                  : 'bg-muted text-muted-foreground'
                              }`}>
                                {count}
                              </span>
                            )}
                          </span>
                        </Link>
                      )
                    })}
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Main content */}
        <div className="lg:col-span-4">
          <Card>
            <CardHeader>
              <CardTitle>
                {selectedStandard?.displayName ?? "Velg øvelse"}
                {selectedStandard?.notInChampionship && (
                  <span className="ml-2 text-sm font-normal text-muted-foreground">(ikke i NM-programmet)</span>
                )}
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                {genderLabel}
                {ageLabel ? ` · ${ageLabel}` : ''}
                {clubName ? ` · ${clubName}` : ''}
                {displayStd ? ` · Krav: ${displayStd}` : ''}
                {' · '}
                {results.length} kvalifisert{results.length !== 1 ? 'e' : ''}
              </p>
            </CardHeader>
            <CardContent className="p-0">
              {results.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-3 py-2 text-left text-sm font-medium w-10">#</th>
                        <th className="px-3 py-2 text-left text-sm font-medium">Resultat</th>
                        <th className="px-3 py-2 text-left text-sm font-medium">Utøver</th>
                        <th className="px-3 py-2 text-left text-sm font-medium w-14">Født</th>
                        <th className="hidden px-3 py-2 text-left text-sm font-medium md:table-cell">Klubb</th>
                        <th className="hidden px-3 py-2 text-left text-sm font-medium md:table-cell">Stevne</th>
                        <th className="hidden px-3 py-2 text-left text-sm font-medium lg:table-cell">Dato</th>
                      </tr>
                    </thead>
                    <tbody>
                      {results.map((result, index) => (
                        <tr key={`${result.athlete_id}-${index}`} className="border-b last:border-0 hover:bg-muted/30">
                          <td className="px-3 py-2 text-sm text-muted-foreground">{index + 1}</td>
                          <td className="px-3 py-2">
                            <span className="perf-value">
                              {formatPerformance(result.performance, result.result_type)}
                            </span>
                            {result.wind !== null && result.wind !== undefined && (
                              <span className="ml-1 text-xs text-muted-foreground">
                                ({result.wind > 0 ? '+' : ''}{result.wind})
                              </span>
                            )}
                          </td>
                          <td className="px-3 py-2">
                            <Link
                              href={`/utover/${result.athlete_id}`}
                              className="font-medium text-primary hover:underline"
                            >
                              {result.athlete_name}
                            </Link>
                          </td>
                          <td className="px-3 py-2 text-sm text-muted-foreground">
                            {getBirthYear(result.birth_date) ?? '-'}
                          </td>
                          <td className="hidden px-3 py-2 text-sm md:table-cell">
                            {result.club_id ? (
                              <Link
                                href={`/klubber/${result.club_id}`}
                                className="hover:text-primary hover:underline"
                              >
                                {result.club_name}
                              </Link>
                            ) : (
                              result.club_name ?? '-'
                            )}
                          </td>
                          <td className="hidden px-3 py-2 text-sm md:table-cell">
                            <Link
                              href={`/stevner/${result.meet_id}`}
                              className="hover:text-primary hover:underline"
                            >
                              {result.meet_name}
                            </Link>
                          </td>
                          <td className="hidden px-3 py-2 text-sm text-muted-foreground lg:table-cell">
                            {result.date
                              ? new Date(result.date).toLocaleDateString('no-NO', {
                                  day: 'numeric',
                                  month: 'short',
                                })
                              : '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="p-6 text-center text-muted-foreground">
                  {selectedStandard
                    ? 'Ingen kvalifiserte utøvere funnet for denne øvelsen'
                    : 'Velg en øvelse fra listen til venstre'}
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
