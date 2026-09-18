"use client"

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, LabelList } from "recharts"

interface Rad {
  band: string
  fra: number
  til: number
}

function fmt(n: number) {
  return n.toLocaleString("nb-NO")
}

/** Unike deltakere per aldersband, første år mot siste år i utvalget. */
export function AlderStolper({ data, fraAar, tilAar }: { data: Rad[]; fraAar: number; tilAar: number }) {
  return (
    <div className="h-[220px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 22, right: 8, left: 4, bottom: 4 }} barCategoryGap="28%" barGap={4}>
          <CartesianGrid stroke="var(--border-default)" vertical={false} />
          <XAxis dataKey="band" tick={{ fill: "var(--text-secondary)", fontSize: 12.5 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: "var(--text-muted)", fontSize: 11.5 }} axisLine={false} tickLine={false} width={52} tickFormatter={(v) => fmt(v)} />
          <Tooltip
            cursor={{ fill: "var(--bg-muted)" }}
            content={({ active, payload, label }) => {
              if (!active || !payload?.length) return null
              const p = payload[0].payload as Rad
              return (
                <div className="rounded border bg-[var(--bg-surface)] px-2.5 py-2 text-[12.5px] shadow-sm">
                  <div className="font-semibold">{label}</div>
                  <div>{fraAar}: <b className="tabular-nums">{fmt(p.fra)}</b></div>
                  <div>{tilAar}: <b className="tabular-nums">{fmt(p.til)}</b></div>
                </div>
              )
            }}
          />
          <Bar dataKey="fra" name={String(fraAar)} fill="var(--serie-1)" radius={[4, 4, 0, 0]} isAnimationActive={false}>
            <LabelList dataKey="fra" position="top" formatter={(v: unknown) => fmt(Number(v))} style={{ fill: "var(--text-primary)", fontSize: 12, fontWeight: 700 }} />
          </Bar>
          <Bar dataKey="til" name={String(tilAar)} fill="var(--serie-2)" radius={[4, 4, 0, 0]} isAnimationActive={false}>
            <LabelList dataKey="til" position="top" formatter={(v: unknown) => fmt(Number(v))} style={{ fill: "var(--text-primary)", fontSize: 12, fontWeight: 700 }} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
