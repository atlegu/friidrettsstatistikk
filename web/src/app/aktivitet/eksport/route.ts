import { NextRequest } from "next/server"
import { hentPerAar, lesFiltre } from "@/lib/aktivitet"

/** Samme tall som dashbordet viser, som CSV med semikolon (Excel i Norge). */
export async function GET(req: NextRequest) {
  const sp = Object.fromEntries(req.nextUrl.searchParams.entries())
  const naa = new Date()
  const sisteHeleAar = naa.getMonth() >= 10 ? naa.getFullYear() : naa.getFullYear() - 1
  const f = lesFiltre(sp, sisteHeleAar)
  const rader = await hentPerAar(f)

  const linjer = [
    "aar;stevner;starter;unike_deltakere;unike_13_19;menn;kvinner",
    ...rader.map((r) => [r.aar, r.stevner, r.starter, r.unike, r.unike_ungdom, r.menn, r.kvinner].join(";")),
  ]
  const filnavn = `aktivitet_${f.fra}-${f.til}${f.kjonn ? "_" + f.kjonn : ""}${f.alder ? "_" + f.alder : ""}${f.kategori ? "_" + f.kategori : ""}.csv`

  return new Response("﻿" + linjer.join("\r\n"), {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": `attachment; filename="${filnavn}"`,
    },
  })
}
