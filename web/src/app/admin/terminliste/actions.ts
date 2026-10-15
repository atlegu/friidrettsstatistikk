"use server"

import { revalidatePath } from "next/cache"
import type { SupabaseClient } from "@supabase/supabase-js"
import { createClient } from "@/lib/supabase/server"

/**
 * Oppfølging av ett arrangement i terminlisten: purret, avlyst, ingen
 * resultater forventet, eller nullstilt. Tilgangen sjekkes her og i basen
 * (radnivåsikkerhet krever is_admin()).
 */
export async function folgOpp(formData: FormData) {
  const id = String(formData.get("id") ?? "")
  const handling = String(formData.get("handling") ?? "")
  const kommentar = String(formData.get("kommentar") ?? "").trim() || null
  if (!id || !["purret", "avlyst", "ingen_resultater", "nullstill"].includes(handling)) {
    throw new Error("Ugyldig handling")
  }

  const supabase = (await createClient()) as unknown as SupabaseClient
  const {
    data: { user },
  } = await supabase.auth.getUser()
  if (!user) throw new Error("Ikke innlogget")

  if (handling === "nullstill") {
    const { error } = await supabase.from("terminliste_oppfolging").delete().eq("isonen_id", id)
    if (error) throw new Error(error.message)
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
    if (error) throw new Error(error.message)
  }
  revalidatePath("/admin/terminliste")
}
