/**
 * Format a performance value for display.
 *
 * Times are stored as seconds (e.g., "279.48" for 4:39.48).
 * This function converts them to proper MM:SS.ss or H:MM:SS.ss format.
 *
 * @param performance - The raw performance string from the database
 * @param resultType - "time", "distance", "height", or "points"
 * @returns Formatted performance string
 */
export function formatPerformance(
  performance: string | null | undefined,
  resultType?: string | null
): string {
  if (!performance) return "–"

  // Check if it's already formatted (contains ":")
  if (performance.includes(":")) {
    return performance
  }

  // If explicitly NOT a time, return as-is
  if (resultType === "distance" || resultType === "height" || resultType === "points") {
    return performance
  }

  // Try to parse as a number (seconds)
  const seconds = parseFloat(performance)
  if (isNaN(seconds)) {
    return performance
  }

  // If under 60 seconds, keep as-is (sprint times like 10.45)
  if (seconds < 60) {
    return performance
  }

  // If over 60 seconds and looks like a time, format it
  // This handles 1500m (around 200-300s), 5000m (700-900s), etc.
  return formatSecondsToTime(seconds)
}

/**
 * Convert seconds to time format (MM:SS.ss or H:MM:SS.ss)
 */
export function formatSecondsToTime(totalSeconds: number): string {
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60

  if (hours > 0) {
    // H:MM:SS.ss format
    const secs = seconds.toFixed(2).padStart(5, "0")
    return `${hours}:${minutes.toString().padStart(2, "0")}:${secs}`
  }

  // MM:SS.ss format (but don't pad minutes if < 10)
  const secs = seconds.toFixed(2).padStart(5, "0")
  return `${minutes}:${secs}`
}

/**
 * Format performance value (in hundredths of seconds) to time
 */
export function formatPerformanceValue(
  value: number | null | undefined,
  resultType?: string | null
): string {
  if (value === null || value === undefined) return "–"

  if (resultType === "time") {
    // performance_value is in hundredths of seconds
    const totalSeconds = value / 100

    if (totalSeconds < 60) {
      return totalSeconds.toFixed(2)
    }

    return formatSecondsToTime(totalSeconds)
  }

  if (resultType === "distance" || resultType === "height") {
    // Value is in centimeters, display in meters
    return (value / 100).toFixed(2)
  }

  // Points or other
  return value.toString()
}
