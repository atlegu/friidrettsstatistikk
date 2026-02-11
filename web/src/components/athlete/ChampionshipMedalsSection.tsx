"use client"

interface ChampionshipMedal {
  id: string
  year: number
  event_name: string
  championship_type: string
  medal: string
  performance: string | null
}

interface ChampionshipMedalsSectionProps {
  medals: ChampionshipMedal[]
}

function MedalDot({ medal }: { medal: string }) {
  const colors: Record<string, string> = {
    gold: "#D4A017",
    silver: "#9CA3AF",
    bronze: "#B87333",
  }
  return (
    <span
      className="inline-block h-3 w-3 rounded-full flex-shrink-0"
      style={{ backgroundColor: colors[medal] || "#666" }}
      title={medal === "gold" ? "Gull" : medal === "silver" ? "Sølv" : "Bronse"}
    />
  )
}

function championshipLabel(type: string): string {
  return type === "NM_indoor" ? "NM innendørs" : "NM utendørs"
}

export function ChampionshipMedalsSection({ medals }: ChampionshipMedalsSectionProps) {
  if (!medals || medals.length === 0) return null

  const goldCount = medals.filter((m) => m.medal === "gold").length
  const silverCount = medals.filter((m) => m.medal === "silver").length
  const bronzeCount = medals.filter((m) => m.medal === "bronze").length

  return (
    <section>
      <h2 className="mb-3">NM-medaljer</h2>

      {/* Summary */}
      <p className="text-[13px] text-[var(--text-secondary)] mb-3">
        {medals.length} medalje{medals.length !== 1 ? "r" : ""}
        <span className="ml-2">
          {goldCount > 0 && (
            <span className="inline-flex items-center gap-0.5 mr-2">
              <MedalDot medal="gold" />
              <span className="ml-0.5">{goldCount}</span>
            </span>
          )}
          {silverCount > 0 && (
            <span className="inline-flex items-center gap-0.5 mr-2">
              <MedalDot medal="silver" />
              <span className="ml-0.5">{silverCount}</span>
            </span>
          )}
          {bronzeCount > 0 && (
            <span className="inline-flex items-center gap-0.5">
              <MedalDot medal="bronze" />
              <span className="ml-0.5">{bronzeCount}</span>
            </span>
          )}
        </span>
      </p>

      {/* Table */}
      <div className="card-flat rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="data-table w-full">
            <thead>
              <tr>
                <th className="text-left">År</th>
                <th className="text-left">Mesterskap</th>
                <th className="text-left">Øvelse</th>
                <th className="text-center">Medalje</th>
                <th className="text-right">Resultat</th>
              </tr>
            </thead>
            <tbody>
              {medals.map((m) => (
                <tr key={m.id}>
                  <td>{m.year}</td>
                  <td>{championshipLabel(m.championship_type)}</td>
                  <td>{m.event_name}</td>
                  <td className="text-center">
                    <MedalDot medal={m.medal} />
                  </td>
                  <td className="text-right tabular-nums">{m.performance || "–"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  )
}
