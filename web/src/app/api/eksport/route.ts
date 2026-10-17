import { NextRequest, NextResponse } from "next/server"
import type { SupabaseClient } from "@supabase/supabase-js"
import { createClient } from "@/lib/supabase/server"
import { getTopResults } from "@/lib/arsliste"
import { getAllTimeResults } from "@/lib/alltime"
import { hentAlle } from "@/lib/hent-alle"
import { formatPerformance } from "@/lib/format-performance"

/* Eksport av lister til CSV (kravspekken §18).
 *
 * Bare for innloggede administratorer: listene inneholder navn og fødselsår,
 * og masseuttrekk av personopplysninger skal ikke være åpent for alle. Hver
 * nedlasting logges i eksport_logg (hvem, hva, når, antall rader). Barn til og
 * med 11 år er aldri med, samme regel som på nettsiden.
 *
 *   /api/eksport?type=arsliste&aar=2026&event=…&gender=M&age=Senior&venue=outdoor
 *   /api/eksport?type=alltime&event=…&gender=F&age=Senior&venue=outdoor&timing=electronic&wind=legal
 *   /api/eksport?type=klubb&klubb=…&aar=2026
 *   /api/eksport?type=stevne&stevne=…
 *
 * CSV med semikolon og BOM, slik at Excel med norsk oppsett åpner fila riktig. */

type Rad = Record<string, string | number | null | undefined>

function csv(kolonner: string[], rader: Rad[]): string {
  const felt = (v: unknown) => {
    const t = v === null || v === undefined ? "" : String(v)
    return /[;"\n]/.test(t) ? `"${t.replace(/"/g, '""')}"` : t
  }
  return "﻿" + [kolonner.join(";"), ...rader.map((r) => kolonner.map((k) => felt(r[k])).join(";"))].join("\r\n")
}

const fodt = (d: string | null | undefined, aar?: number | null) => (d ? Number(d.slice(0, 4)) : aar ?? null)
const vind = (w: number | null | undefined) => (w === null || w === undefined ? null : `${w > 0 ? "+" : ""}${w}`)
const utl = (n: string | null | undefined) => (n && n !== "NOR" ? n : null)

export async function GET(req: NextRequest) {
  const supabase = (await createClient()) as unknown as SupabaseClient
  const {
    data: { user },
  } = await supabase.auth.getUser()
  if (!user) return NextResponse.json({ feil: "Krever innlogging" }, { status: 401 })
  const { data: admin } = await supabase.rpc("check_is_admin", { check_user_id: user.id })
  if (admin !== true) return NextResponse.json({ feil: "Krever administratortilgang" }, { status: 403 })

  const p = req.nextUrl.searchParams
  const type = p.get("type") ?? ""
  let kolonner: string[] = []
  let rader: Rad[] = []
  let filnavn = "eksport"

  if (type === "arsliste" || type === "alltime") {
    const { data: ev } = await supabase.from("events").select("id,code,name,result_type,category").eq("id", p.get("event") ?? "").maybeSingle()
    if (!ev) return NextResponse.json({ feil: "Ukjent øvelse" }, { status: 400 })
    const gender = p.get("gender") === "F" ? "F" : "M"
    const age = p.get("age") ?? "Senior"
    const venue = p.get("venue") ?? "outdoor"
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let liste: any[]
    if (type === "arsliste") {
      const aar = Number(p.get("aar"))
      liste = await getTopResults(aar, ev.id, ev.code ?? "", gender, age, ev.result_type ?? "time", ev.category ?? "", venue, "lovlig", 100)
      filnavn = `arsliste_${aar}_${ev.code}_${gender}_${age}_${venue}`
    } else {
      const timing = p.get("timing") ?? "electronic"
      const wind = p.get("wind") ?? "all"
      liste = (await getAllTimeResults(ev.id, gender, age, ev.result_type ?? "time", venue, timing, wind, 500, 0)).results
      filnavn = `alletiders_${ev.code}_${gender}_${age}_${venue}`
    }
    kolonner = ["Plass", "Resultat", "Vind", "Utøver", "Født", "Utenlandsk", "Klubb", "Stevne", "Dato"]
    rader = liste.map((r, i) => ({
      Plass: i + 1,
      Resultat: formatPerformance(r.performance, r.result_type),
      Vind: vind(r.wind),
      Utøver: r.athlete_name,
      Født: fodt(r.birth_date, r.birth_year),
      Utenlandsk: utl(r.athlete_nationality),
      Klubb: r.club_name,
      Stevne: r.meet_name,
      Dato: r.date,
    }))
  } else if (type === "klubb" || type === "stevne") {
    const felt = "event_name,place,round,performance,result_type,wind,athlete_name,birth_date,club_name,meet_name,date,status,age_group,performance_value"
    const id = p.get(type === "klubb" ? "klubb" : "stevne") ?? ""
    const aar = Number(p.get("aar"))
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const alle = await hentAlle<any>(
      (fra, til) => {
        let q = supabase.from("results_full").select(felt).or("age_group.is.null,age_group.neq.Yngre")
        q = type === "klubb" ? q.eq("club_id", id).eq("season_year", aar).eq("status", "OK") : q.eq("meet_id", id)
        return q.order("event_name").order("performance_value").range(fra, til)
      },
      "Eksport"
    )
    kolonner = ["Øvelse", "Plass", "Runde", "Resultat", "Vind", "Utøver", "Født", "Klubb", "Stevne", "Dato", "Status"]
    rader = alle.map((r) => ({
      Øvelse: r.event_name,
      Plass: r.place,
      Runde: r.round,
      Resultat: formatPerformance(r.performance, r.result_type),
      Vind: vind(r.wind),
      Utøver: r.athlete_name,
      Født: fodt(r.birth_date),
      Klubb: r.club_name,
      Stevne: r.meet_name,
      Dato: r.date,
      Status: r.status === "OK" ? "" : r.status === "IKKE_GODKJENT" ? "Ikke godkjent" : r.status,
    }))
    filnavn = type === "klubb" ? `klubb_${aar}` : "stevne"
  } else {
    return NextResponse.json({ feil: "Ukjent type" }, { status: 400 })
  }

  await supabase.from("eksport_logg").insert({
    user_id: user.id,
    epost: user.email,
    type,
    parametre: Object.fromEntries(p.entries()),
    rader: rader.length,
  })

  return new NextResponse(csv(kolonner, rader), {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": `attachment; filename="${filnavn.replace(/[^\w.-]+/g, "_")}.csv"`,
      "Cache-Control": "no-store",
    },
  })
}
