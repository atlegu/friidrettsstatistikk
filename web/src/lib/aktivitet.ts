import { createClient } from "@/lib/supabase/server"

/**
 * Aktivitet og deltakelse (kravspekkens §12).
 *
 * Tallene kommer fra den materialiserte visningen aktivitet_grunnlag: én rad
 * per (år, utøver, stevne, øvelsesgruppe). Den oppdateres av cron-jobben
 * sammen med klubb_bruk etter hver import.
 */

export const KATEGORIER: Record<string, string> = {
  sprint: "Sprint",
  hurdles: "Hekk",
  middle_distance: "Mellomdistanse",
  long_distance: "Langdistanse",
  steeplechase: "Hinder",
  jumps: "Hopp",
  throws: "Kast",
  combined: "Mangekamp",
  walking: "Kappgang",
  relay: "Stafett",
}

export const ALDERSBAND: Record<string, string> = {
  under13: "Under 13",
  "13-19": "13–19 år",
  "20-34": "20–34 år",
  "35+": "35+",
}

export interface AarRad {
  aar: number
  stevner: number
  starter: number
  unike: number
  unike_ungdom: number
  menn: number
  kvinner: number
}

export interface Filtre {
  fra: number
  til: number
  kjonn: "M" | "F" | null
  alder: string | null
  kategori: string | null
}

export function lesFiltre(sp: Record<string, string | undefined>, sisteHeleAar: number): Filtre {
  const fra = parseInt(sp.fra ?? "") || 2019
  const til = parseInt(sp.til ?? "") || sisteHeleAar
  const kjonn = sp.kjonn === "M" || sp.kjonn === "F" ? sp.kjonn : null
  const alder = sp.alder && sp.alder in ALDERSBAND ? sp.alder : null
  const kategori = sp.kategori && sp.kategori in KATEGORIER ? sp.kategori : null
  return { fra: Math.min(fra, til), til: Math.max(fra, til), kjonn, alder, kategori }
}

export async function hentPerAar(f: Filtre): Promise<AarRad[]> {
  const supabase = await createClient()
  const { data, error } = await supabase.rpc("aktivitet_per_aar", {
    p_fra: f.fra,
    p_til: f.til,
    p_kjonn: f.kjonn ?? undefined,
    p_alder: f.alder ?? undefined,
    p_kategori: f.kategori ?? undefined,
  })
  if (error) {
    console.error("aktivitet_per_aar:", error.message)
    return []
  }
  return (data ?? []) as AarRad[]
}

export async function hentPerAlder(aar: number, f: Filtre): Promise<Record<string, number>> {
  const supabase = await createClient()
  const { data, error } = await supabase.rpc("aktivitet_alder", {
    p_aar: aar,
    p_kjonn: f.kjonn ?? undefined,
    p_kategori: f.kategori ?? undefined,
  })
  if (error) {
    console.error("aktivitet_alder:", error.message)
    return {}
  }
  return Object.fromEntries((data ?? []).map((r) => [r.alder, Number(r.unike)]))
}

export async function hentKlubber(fra: number, til: number) {
  const supabase = await createClient()
  const { data, error } = await supabase.rpc("aktivitet_klubber", { p_fra: fra, p_til: til })
  if (error) {
    console.error("aktivitet_klubber:", error.message)
    return []
  }
  return (data ?? []).map((r) => ({ aar: r.aar, alle: Number(r.alle), aktive: Number(r.aktive) }))
}

/** Prosentvis endring, avrundet. null når grunnlaget mangler. */
export function endring(fra: number | undefined, til: number | undefined): number | null {
  if (!fra || til === undefined) return null
  return Math.round(((til - fra) / fra) * 100)
}

export function tall(n: number | null | undefined, desimaler = 0): string {
  if (n === null || n === undefined || Number.isNaN(n)) return "–"
  return n.toLocaleString("nb-NO", { minimumFractionDigits: desimaler, maximumFractionDigits: desimaler })
}
