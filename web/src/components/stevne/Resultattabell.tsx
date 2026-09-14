"use client"

import { formatPerformance } from "@/lib/format-performance"

export interface Stevnerad {
  /** Null i teorien fordi raden kommer fra et view; alltid satt i praksis. */
  id: string | null
  place: number | null
  athlete_id: string | null
  athlete_name: string | null
  club_name: string | null
  performance: string | null
  result_type: string | null
  wind: number | null
  is_pb: boolean | null
}

/**
 * Resultatene i én øvelse.
 *
 * Dette er en klientkomponent, og det er et bevisst valg. Tegnes tabellen
 * på serveren, må hele komponenttreet serialiseres og sendes med sida: for
 * Tyrvinglekene med 3 299 resultater ble sida 12 MB, hvorav 10,5 MB var
 * det serialiserte treet. Sender vi radene som rene data i stedet, og lar
 * nettleseren tegne dem, er det bare tallene som går over linja.
 *
 * Median-stevnet har fire resultater, så dette betyr ingenting for de
 * fleste sidene. Det betyr mye for de 171 som er større enn tusen.
 */
export function Resultattabell({ rader }: { rader: Stevnerad[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b bg-muted/50">
            <th className="w-12 px-4 py-2 text-left text-sm font-medium">#</th>
            <th className="px-4 py-2 text-left text-sm font-medium">Utøver</th>
            <th className="hidden px-4 py-2 text-left text-sm font-medium md:table-cell">
              Klubb
            </th>
            <th className="px-4 py-2 text-left text-sm font-medium">Resultat</th>
          </tr>
        </thead>
        <tbody>
          {rader.map((r, i) => (
            <tr key={r.id} className="border-b last:border-0 hover:bg-muted/30">
              <td className="px-4 py-2 text-sm text-muted-foreground">
                {r.place ?? i + 1}
              </td>
              <td className="px-4 py-2">
                <a
                  href={`/utover/${r.athlete_id}`}
                  className="font-medium text-primary hover:underline"
                >
                  {r.athlete_name}
                </a>
              </td>
              <td className="hidden px-4 py-2 text-sm md:table-cell">
                {r.club_name ?? "-"}
              </td>
              <td className="px-4 py-2">
                <span className="perf-value">
                  {formatPerformance(r.performance, r.result_type)}
                </span>
                {r.wind !== null && (
                  <span className="ml-1 text-xs text-muted-foreground">
                    ({r.wind > 0 ? "+" : ""}
                    {r.wind})
                  </span>
                )}
                {r.is_pb && (
                  <span className="ml-2 rounded bg-green-100 px-1.5 py-0.5 text-xs font-medium text-green-800 dark:bg-green-900 dark:text-green-200">
                    PB
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
