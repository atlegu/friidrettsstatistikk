import Link from "next/link"
import { formatPerformance } from "@/lib/format-performance"
import { getBirthYear } from "@/lib/date-utils"

export interface AarslisteRad {
  id: string | null
  performance: string | null
  result_type: string | null
  wind: number | null
  athlete_id: string | null
  athlete_name: string | null
  birth_date: string | null
  club_name: string | null
  meet_id: string | null
  meet_name: string | null
  date: string | null
}

/**
 * Tabellen i årslistene. Brukes to ganger på samme side: én for den vanlige
 * lista, og én for resultatene med ukjent vind under den.
 */
export function AarslisteTabell({ rader }: { rader: AarslisteRad[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b bg-muted/50">
            <th className="w-10 px-3 py-2 text-left text-sm font-medium">#</th>
            <th className="px-3 py-2 text-left text-sm font-medium">Resultat</th>
            <th className="px-3 py-2 text-left text-sm font-medium">Utøver</th>
            <th className="w-14 px-3 py-2 text-left text-sm font-medium">Født</th>
            <th className="hidden px-3 py-2 text-left text-sm font-medium md:table-cell">Klubb</th>
            <th className="hidden px-3 py-2 text-left text-sm font-medium lg:table-cell">Stevne</th>
            <th className="hidden px-3 py-2 text-left text-sm font-medium lg:table-cell">Dato</th>
          </tr>
        </thead>
        <tbody>
          {rader.map((r, i) => (
            <tr key={r.id ?? i} className="border-b last:border-0 hover:bg-muted/30">
              <td className="px-3 py-2 text-sm text-muted-foreground">{i + 1}</td>
              <td className="px-3 py-2">
                <span className="perf-value">{formatPerformance(r.performance, r.result_type)}</span>
                {r.wind !== null && (
                  <span className="ml-1 text-xs text-muted-foreground">
                    ({r.wind > 0 ? "+" : ""}
                    {r.wind})
                  </span>
                )}
              </td>
              <td className="px-3 py-2">
                <Link href={`/utover/${r.athlete_id}`} className="font-medium text-primary hover:underline">
                  {r.athlete_name}
                </Link>
              </td>
              <td className="px-3 py-2 text-sm text-muted-foreground">
                {getBirthYear(r.birth_date) ?? "-"}
              </td>
              <td className="hidden px-3 py-2 text-sm md:table-cell">{r.club_name ?? "-"}</td>
              <td className="hidden px-3 py-2 text-sm lg:table-cell">
                <Link href={`/stevner/${r.meet_id}`} className="hover:text-primary hover:underline">
                  {r.meet_name}
                </Link>
              </td>
              <td className="hidden px-3 py-2 text-sm text-muted-foreground lg:table-cell">
                {r.date
                  ? new Date(r.date).toLocaleDateString("no-NO", { day: "numeric", month: "short" })
                  : "-"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
