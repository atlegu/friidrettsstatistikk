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
  if (birthDate) {
    return formatDate(birthDate)
  }
  if (birthYear) {
    return `Født ${birthYear}`
  }
  return null
}

export function AthleteHeader({ athlete, club, stats, mainEvent, medalCounts }: AthleteHeaderProps) {
  const fullName = athlete.full_name || `${athlete.first_name} ${athlete.last_name}`
  const age = calculateAge(athlete.birth_date, athlete.birth_year)
  const birthInfo = formatBirthInfo(athlete.birth_date, athlete.birth_year)
  const initials = getInitials(athlete.first_name, athlete.last_name)

  const seasonCount = stats.firstYear && stats.lastYear
    ? stats.lastYear - stats.firstYear + 1
    : null

  return (
    <div className="mb-4">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start">
        {/* Avatar */}
        <div className="flex-shrink-0">
          {athlete.profile_image_url ? (
            <img
              src={athlete.profile_image_url}
              alt={fullName}
              className="h-16 w-16 rounded-full object-cover ring-1 ring-[var(--border-default)] sm:h-20 sm:w-20"
            />
          ) : (
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-[var(--accent-primary)] text-xl font-semibold text-white sm:h-20 sm:w-20 sm:text-2xl">
              {initials}
            </div>
          )}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          {/* Name + Actions */}
          <div className="mb-1 flex items-start justify-between gap-4">
            <h1 className="truncate">{fullName}</h1>
            <CopyLink className="flex-shrink-0" />
          </div>

          {/* Meta info - inline with separators */}
          <div className="mb-2 flex flex-wrap items-center gap-x-2 gap-y-0.5 text-[13px]">
            {birthInfo && (
              <span className="text-[var(--text-secondary)]">
                {birthInfo}
                {age && ` (${age} år)`}
              </span>
            )}
            {club && (
              <>
                <span className="text-[var(--text-muted)]">·</span>
                <Link href={`/klubber/${club.id}`}>
                  {club.name}
                </Link>
              </>
            )}
            {athlete.gender && (
              <>
                <span className="text-[var(--text-muted)]">·</span>
                <span className="text-[var(--text-secondary)]">
                  {athlete.gender === "M" ? "Mann" : "Kvinne"}
                </span>
              </>
            )}
          </div>

          {/* Badges */}
          <div className="flex flex-wrap items-center gap-1.5 mb-2">
            {mainEvent && (
              <span className="chip">{mainEvent}</span>
            )}
            {stats.nationalRecordsCount > 0 && (
              <span className="badge-nr">{stats.nationalRecordsCount} NR</span>
            )}
            {medalCounts && (medalCounts.gold + medalCounts.silver + medalCounts.bronze) > 0 && (
              <span className="badge-medals">
                {medalCounts.gold > 0 && (
                  <span className="inline-flex items-center gap-0.5">
                    <span className="medal-dot medal-gold" />
                    {medalCounts.gold}
                  </span>
                )}
                {medalCounts.silver > 0 && (
                  <span className="inline-flex items-center gap-0.5">
                    <span className="medal-dot medal-silver" />
                    {medalCounts.silver}
                  </span>
                )}
                {medalCounts.bronze > 0 && (
                  <span className="inline-flex items-center gap-0.5">
                    <span className="medal-dot medal-bronze" />
                    {medalCounts.bronze}
                  </span>
                )}
              </span>
            )}
            <CompareLink athleteId={athlete.id} />
          </div>

          {/* Career Stats */}
          <div className="flex flex-wrap gap-x-4 gap-y-0.5 text-[12px] text-[var(--text-muted)]">
            {stats.firstYear && stats.lastYear && (
              <span>
                {stats.firstYear === stats.lastYear
                  ? stats.firstYear
                  : `${stats.firstYear}–${stats.lastYear}`}
                {seasonCount && seasonCount > 1 && ` · ${seasonCount} sesonger`}
              </span>
            )}
            {stats.totalMeets > 0 && (
              <span>{stats.totalMeets} stevner</span>
            )}
            {stats.totalEvents > 0 && (
              <span>{stats.totalEvents} øvelser</span>
            )}
            {stats.totalResults > 0 && (
              <span>{stats.totalResults} resultater</span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
