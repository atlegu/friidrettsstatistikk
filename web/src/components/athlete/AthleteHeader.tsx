import Link from "next/link"
import { CopyLink } from "@/components/ui/copy-link"
import { CompareLink } from "@/components/athlete/CompareLink"
import { calculateAge, formatDate } from "@/lib/date-utils"

interface AthleteStats {
  totalResults: number
  totalMeets: number
  totalEvents: number
  firstYear: number | null
  lastYear: number | null
  nationalRecordsCount: number
}

interface MedalCounts {
  gold: number
  silver: number
  bronze: number
}

interface AthleteHeaderProps {
  athlete: {
    id: string
    full_name: string | null
    first_name: string
    last_name: string
    birth_date: string | null
    birth_year: number | null
    gender: string | null
    profile_image_url: string | null
  }
  club: { id: string; name: string } | null
  stats: AthleteStats
  mainEvent: string | null
  medalCounts?: MedalCounts | null
}

function getInitials(firstName: string, lastName: string): string {
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
}

function formatBirthInfo(birthDate: string | null, birthYear: number | null): string | null {
  if (birthDate) return formatDate(birthDate)
  if (birthYear) return `Født ${birthYear}`
  return null
}

/** Ett nøkkeltall i toppen. Vises bare når det finnes. */
function Noekkeltall({ merkelapp, verdi }: { merkelapp: string; verdi: string | number }) {
  return (
    <div>
      <div className="text-[10.5px] font-bold uppercase tracking-[0.07em] text-[var(--nfif-navy-blekk-svak)]">
        {merkelapp}
      </div>
      <div className="text-xl font-bold tabular-nums text-white sm:text-2xl">{verdi}</div>
    </div>
  )
}

export function AthleteHeader({ athlete, club, stats, mainEvent, medalCounts }: AthleteHeaderProps) {
  const fullName = athlete.full_name || `${athlete.first_name} ${athlete.last_name}`
  const age = calculateAge(athlete.birth_date, athlete.birth_year)
  const birthInfo = formatBirthInfo(athlete.birth_date, athlete.birth_year)
  const initials = getInitials(athlete.first_name, athlete.last_name)

  const seasonCount =
    stats.firstYear && stats.lastYear ? stats.lastYear - stats.firstYear + 1 : null

  const medaljer = medalCounts
    ? medalCounts.gold + medalCounts.silver + medalCounts.bronze
    : 0

  return (
    // Toppen går helt ut til kanten. Siden ligger i en .container med
    // sidepadding, så den trekkes ut igjen med negative marger.
    <div className="relative -mx-4 overflow-hidden bg-[var(--nfif-navy)] sm:-mx-6 lg:-mx-8">
      {/* Antydning av en baneoval. Rent dekorativt, skjules for skjermlesere. */}
      <div
        aria-hidden
        className="pointer-events-none absolute -right-24 -top-40 hidden h-[420px] w-[420px] rounded-full border-[56px] border-white/[0.045] lg:block"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-gradient-to-br from-[var(--nfif-navy-dyp)] via-[var(--nfif-navy)] to-[var(--nfif-navy-lys)]"
      />

      <div className="relative px-4 py-6 sm:px-6 lg:px-8">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:gap-7">
          {/* Portrett */}
          <div className="flex-shrink-0">
            {athlete.profile_image_url ? (
              <img
                src={athlete.profile_image_url}
                alt={fullName}
                className="h-20 w-20 rounded-full object-cover ring-4 ring-white/80 sm:h-28 sm:w-28"
              />
            ) : (
              <div className="flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-[#E9EDF5] to-[#C6D0E2] text-2xl font-bold tracking-tight text-[var(--nfif-navy)] ring-4 ring-white/80 sm:h-28 sm:w-28 sm:text-3xl">
                {initials}
              </div>
            )}
          </div>

          {/* Navn og opplysninger */}
          <div className="min-w-0 flex-1">
            <h1 className="text-2xl font-bold tracking-tight text-white sm:text-[2rem]">
              {fullName}
            </h1>

            <div className="mt-1.5 flex flex-wrap items-center gap-x-2 gap-y-0.5 text-[13px] text-[var(--nfif-navy-blekk)]">
              {birthInfo && (
                <span>
                  {birthInfo}
                  {age && <span className="font-bold text-white"> ({age} år)</span>}
                </span>
              )}
              {club && (
                <>
                  <span className="text-[var(--nfif-navy-blekk-svak)]">·</span>
                  <Link
                    href={`/klubber/${club.id}`}
                    className="font-bold text-white underline-offset-2 hover:underline"
                  >
                    {club.name}
                  </Link>
                </>
              )}
              {athlete.gender && (
                <>
                  <span className="text-[var(--nfif-navy-blekk-svak)]">·</span>
                  <span>{athlete.gender === "M" ? "Mann" : "Kvinne"}</span>
                </>
              )}
              {mainEvent && (
                <>
                  <span className="text-[var(--nfif-navy-blekk-svak)]">·</span>
                  <span>{mainEvent}</span>
                </>
              )}
            </div>

            {/* Utmerkelser */}
            {(stats.nationalRecordsCount > 0 || medaljer > 0) && (
              <div className="mt-3 flex flex-wrap items-center gap-2">
                {stats.nationalRecordsCount > 0 && (
                  <span className="rounded-md bg-[var(--nfif-rod)] px-2 py-0.5 text-[11px] font-bold uppercase tracking-wide text-white">
                    {stats.nationalRecordsCount} norsk rekord
                    {stats.nationalRecordsCount > 1 ? "er" : ""}
                  </span>
                )}
                {medalCounts && medaljer > 0 && (
                  <span className="inline-flex items-center gap-2 rounded-md bg-white/10 px-2 py-0.5 text-[11px] font-bold text-white ring-1 ring-white/20">
                    {medalCounts.gold > 0 && (
                      <span className="inline-flex items-center gap-1">
                        <span className="medal-dot medal-gold" />
                        {medalCounts.gold}
                      </span>
                    )}
                    {medalCounts.silver > 0 && (
                      <span className="inline-flex items-center gap-1">
                        <span className="medal-dot medal-silver" />
                        {medalCounts.silver}
                      </span>
                    )}
                    {medalCounts.bronze > 0 && (
                      <span className="inline-flex items-center gap-1">
                        <span className="medal-dot medal-bronze" />
                        {medalCounts.bronze}
                      </span>
                    )}
                  </span>
                )}
              </div>
            )}

            {/* Nøkkeltall for karrieren */}
            <div className="mt-4 flex flex-wrap gap-x-8 gap-y-3">
              {seasonCount && seasonCount > 0 && (
                <Noekkeltall
                  merkelapp={seasonCount > 1 ? "Sesonger" : "Sesong"}
                  verdi={seasonCount}
                />
              )}
              {stats.totalMeets > 0 && (
                <Noekkeltall merkelapp="Stevner" verdi={stats.totalMeets} />
              )}
              {stats.totalResults > 0 && (
                <Noekkeltall merkelapp="Resultater" verdi={stats.totalResults} />
              )}
              {stats.totalEvents > 0 && (
                <Noekkeltall merkelapp="Øvelser" verdi={stats.totalEvents} />
              )}
              {stats.firstYear && stats.lastYear && (
                <Noekkeltall
                  merkelapp="Aktiv"
                  verdi={
                    stats.firstYear === stats.lastYear
                      ? stats.firstYear
                      : `${stats.firstYear}–${stats.lastYear}`
                  }
                />
              )}
            </div>
          </div>

          {/* Handlinger */}
          <div className="flex flex-shrink-0 flex-wrap items-center gap-2 sm:flex-col sm:items-stretch">
            <CompareLink athleteId={athlete.id} />
            <CopyLink />
          </div>
        </div>
      </div>
    </div>
  )
}
