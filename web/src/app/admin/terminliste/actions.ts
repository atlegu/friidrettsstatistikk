"use server"

import { revalidatePath } from "next/cache"
import { redirect } from "next/navigation"
import type { SupabaseClient } from "@supabase/supabase-js"
import { createClient } from "@/lib/supabase/server"

const HANDLINGER = ["purret", "avlyst", "ingen_resultater", "nullstill"]

/**
 * Oppfølging av ett arrangement i terminlisten: purret, avlyst, ingen
 * resultater forventet, eller nullstilt. Tilgangen sjekkes her og i basen
 * (radnivåsikkerhet krever is_admin()). Handlingen bindes til knappen, og
 * feil vises som melding på siden i stedet for å kastes.
 */
export async function folgOpp(handling: string, formData: FormData) {
  const feil = await lagre(handling, formData)
  if (feil) redirect(`/admin/terminliste?feil=${encodeURIComponent(feil)}`)
  revalidatePath("/admin/terminliste")
}

async function lagre(handling: string, formData: FormData): Promise<string | null> {
  const id = String(formData.get("id") ?? "")
  const kommentar = String(formData.get("kommentar") ?? "").trim() || null
  if (!id || !HANDLINGER.includes(handling)) return "Ugyldig handling"

  try {
    const supabase = (await createClient()) as unknown as SupabaseClient
    const {
      data: { user },
    } = await supabase.auth.getUser()
    if (!user) return "Du er ikke innlogget. Logg inn på nytt."

    if (handling === "nullstill") {
      const { error } = await supabase.from("terminliste_oppfolging").delete().eq("isonen_id", id)
      if (error) return `Kunne ikke lagre: ${error.message}`
    } else {
      const { data: forrige } = await supabase
        .from("terminliste_oppfolging")
        .select("purringer, kommentar")
        .eq("isonen_id", id)
        .maybeSingle()
      const idag = new Date().toISOString().slice(0, 10)
      const { error } = await supabase.from("terminliste_oppfolging").upsert({
        isonen_id: id,
        status: handling,
        purret_dato: handling === "purret" ? idag : null,
        purringer: (forrige?.purringer ?? 0) + (handling === "purret" ? 1 : 0),
        kommentar: kommentar ?? forrige?.kommentar ?? null,
        behandlet_av: user.id,
        behandlet_tid: new Date().toISOString(),
      })
      if (error) return `Kunne ikke lagre: ${error.message}`
    }
    return null
  } catch (e) {
    return `Kunne ikke lagre: ${e instanceof Error ? e.message : String(e)}`
  }
}
