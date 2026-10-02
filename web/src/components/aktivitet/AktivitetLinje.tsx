"use client"

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

interface Punkt {
  aar: number
  alle: number
  ungdom: number | null
}

const SERIE_1 = "var(--serie-1)"
const SERIE_2 = "var(--serie-2)"

function fmt(n: number) {
  return n.toLocaleString("nb-NO")
}

/**
 * Unike deltakere per år: én linje for alle, én for 13–19 år. Direkte
 * etiketter bare på første og siste punkt, ikke på hvert punkt.
 */
export function AktivitetLinje({ data, visUngdom }: { data: Punkt[]; visUngdom: boolean }) {
  const siste = data.length - 1

  const etikett = (farge: string, plassering: "over" | "under") =>
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (p: any) => {
      const i = p.index as number
      if (i !== 0 && i !== siste) return null
      const dy = plassering === "over" ? -10 : 18
      return (
        <text
          x={p.x}
          y={(p.y as number) + dy}
          textAnchor={i === 0 ? "start" : "end"}
          fill={farge}
          fontSize={12.5}
          fontWeight={700}
        >
          {fmt(p.value)}
        </text>
      )
    }

  return (
    <div className="h-[260px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 18, right: 14, left: 4, bottom: 4 }}>
          <CartesianGrid stroke="var(--border-default)" vertical={false} />
          <XAxis
            dataKey="aar"
            tick={{ fill: "var(--text-muted)", fontSize: 11.5 }}
            axisLine={{ stroke: "var(--border-default)" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "var(--text-muted)", fontSize: 11.5 }}
            axisLine={false}
            tickLine={false}
            width={52}
            tickFormatter={(v) => fmt(v)}
            domain={[0, "auto"]}
          />
          <Tooltip
            content={({ active, payload, label }) => {
              if (!active || !payload?.length) return null
              const p = payload[0].payload as Punkt
              return (
                <div className="rounded border bg-[var(--bg-surface)] px-2.5 py-2 text-[12.5px] shadow-sm">
                  <div className="font-semibold">{label}</div>
                  <div>Alle aldre: <b className="tabular-nums">{fmt(p.alle)}</b></div>
                  {visUngdom && p.ungdom !== null && (
                    <div>13–19 år: <b className="tabular-nums">{fmt(p.ungdom)}</b></div>
                  )}
                </div>
              )
            }}
          />
          <Line
            type="monotone"
            dataKey="alle"
            stroke={SERIE_1}
            strokeWidth={2}
            dot={{ r: 4, fill: SERIE_1, strokeWidth: 0 }}
            activeDot={{ r: 6 }}
            label={etikett(SERIE_1, "over")}
            isAnimationActive={false}
          />
          {visUngdom && (
            <Line
              type="monotone"
              dataKey="ungdom"
              stroke={SERIE_2}
              strokeWidth={2}
              dot={{ r: 4, fill: SERIE_2, strokeWidth: 0 }}
              activeDot={{ r: 6 }}
              label={etikett(SERIE_2, "under")}
              isAnimationActive={false}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
