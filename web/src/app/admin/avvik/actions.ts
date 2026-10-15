"use server"

import { revalidatePath } from "next/cache"
import type { SupabaseClient } from "@supabase/supabase-js"
import { createClient } from "@/lib/supabase/server"

const GYLDIGE = ["aapen", "godkjent", "rettet", "underkjent"] as const

/**
 * Behandle ett avvik: sett status, hvem som gjorde det, når, og en kommentar.
 * Tilgangen kontrolleres to steder: her (innlogget administrator) og i basen
 * (radnivåsikkerhet på avvik krever is_admin()).
 */
export async function behandleAvvik(formData: FormData) {
  const id = Number(formData.get("id"))
  const status = String(formData.get("status") ?? "")
  const kommentar = String(formData.get("kommentar") ?? "").trim() || null

  if (!Number.isFinite(id) || !GYLDIGE.includes(status as (typeof GYLDIGE)[number])) {
    throw new Error("Ugyldig avvik eller status")
  }

  const supabase = (await createClient()) as unknown as SupabaseClient
  const {
    data: { user },
  } = await supabase.auth.getUser()
  if (!user) throw new Error("Ikke innlogget")

  const aapnes = status === "aapen"
  const { error } = await supabase
    .from("avvik")
    .update({
      status,
      kommentar,
      behandlet_av: aapnes ? null : user.id,
      behandlet_tid: aapnes ? null : new Date().toISOString(),
    })
    .eq("id", id)

  if (error) throw new Error(`Kunne ikke lagre: ${error.message}`)
  revalidatePath("/admin/avvik")
  revalidatePath("/admin")
}
