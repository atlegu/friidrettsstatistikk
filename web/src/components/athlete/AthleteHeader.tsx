import Link from "next/link"
import { Badge } from "@/components/ui/badge"

interface AthleteStats {
  totalResults: number
  totalMeets: number
  totalEvents: number
  firstYear: number | null
  lastYear: number | null
  nationalRecordsCount: number
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
}

function getInitials(firstName: string, lastName: string): string {
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
}

function calculateAge(birthDate: string | null, birthYear: number | null): number | null {
  if (birthDate) {
    const today = new Date()
    const birth = new Date(birthDate)
    let age = today.getFullYear() - birth.getFullYear()
    const monthDiff = today.getMonth() - birth.getMonth()
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--
    }
    return age
  }
  if (birthYear) {
    return new Date().getFullYear() - birthYear
  }
  return null
}

function formatBirthDate(birthDate: string | null, birthYear: number | null): string | null {
  if (birthDate) {
    const date = new Date(birthDate)
    return date.toLocaleDateString("no-NO", {
      day: "numeric",
      month: "short",
      year: "numeric",
    })
  }
  if (birthYear) {
    return `Født ${birthYear}`
  }
  return null
}

export function AthleteHeader({ athlete, club, stats, mainEvent }: AthleteHeaderProps) {
  const fullName = athlete.full_name || `${athlete.first_name} ${athlete.last_name}`
  const age = calculateAge(athlete.birth_date, athlete.birth_year)
  const birthInfo = formatBirthDate(athlete.birth_date, athlete.birth_year)
  const initials = getInitials(athlete.first_name, athlete.last_name)

  const seasonCount = stats.firstYear && stats.lastYear
    ? stats.lastYear - stats.firstYear + 1
    : null

  return (
    <div className="mb-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start">
        {/* Avatar - smaller size */}
        <div className="flex-shrink-0">
          {athlete.profile_image_url ? (
            <img
              src={athlete.profile_image_url}
              alt={fullName}
              className="h-16 w-16 rounded-full object-cover ring-1 ring-border sm:h-20 sm:w-20"
            />
          ) : (
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary text-xl font-semibold text-primary-foreground sm:h-20 sm:w-20 sm:text-2xl">
              {initials}
            </div>
          )}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          {/* Name - using h1 from base styles (21px) */}
          <h1 className="mb-1 truncate">{fullName}</h1>

          {/* Meta info */}
          <div className="mb-3 flex flex-wrap items-center gap-x-3 gap-y-0.5 text-[13px] text-[var(--text-secondary)]">
            {birthInfo && (
              <span>
                {birthInfo}
                {age && ` (${age} år)`}
              </span>
            )}
            {club && (
              <Link
                href={`/klubber/${club.id}`}
                className="no-underline hover:underline"
              >
                {club.name}
              </Link>
            )}
            {athlete.gender && (
              <span>{athlete.gender === "M" ? "Mann" : "Kvinne"}</span>
            )}
          </div>

          {/* Badges */}
          <div className="flex flex-wrap gap-1.5">
            {mainEvent && (
              <Badge variant="secondary">
                {mainEvent}
              </Badge>
            )}
            {stats.nationalRecordsCount > 0 && (
              <Badge variant="nr">
                {stats.nationalRecordsCount} NR
              </Badge>
            )}
          </div>

          {/* Career Stats - compact */}
          <div className="mt-3 flex flex-wrap gap-x-4 gap-y-0.5 text-[12px] text-[var(--text-muted)]">
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
