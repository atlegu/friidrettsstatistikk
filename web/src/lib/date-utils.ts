/**
 * Parse a date string (YYYY-MM-DD) without timezone conversion.
 * This prevents dates from being shifted due to UTC interpretation.
 */
export function parseDateString(dateStr: string): Date {
  const [year, month, day] = dateStr.split('-').map(Number)
  return new Date(year, month - 1, day)
}

/**
 * Get birth year from a date string without timezone issues.
 */
export function getBirthYear(birthDate: string | null): number | null {
  if (!birthDate) return null
  const [year] = birthDate.split('-').map(Number)
  return year
}

/**
 * Format a date string (YYYY-MM-DD) to Norwegian locale.
 */
export function formatDate(
  dateStr: string,
  options: Intl.DateTimeFormatOptions = { day: "numeric", month: "short", year: "numeric" }
): string {
  const date = parseDateString(dateStr)
  return date.toLocaleDateString("no-NO", options)
}

/**
 * Calculate age from birth date or birth year.
 */
export function calculateAge(birthDate: string | null, birthYear: number | null): number | null {
  if (birthDate) {
    const today = new Date()
    const birth = parseDateString(birthDate)
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
