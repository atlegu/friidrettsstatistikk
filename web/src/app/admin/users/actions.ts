"use server"

import { revalidatePath } from "next/cache"
import { redirect } from "next/navigation"
import type { SupabaseClient } from "@supabase/supabase-js"
import { createClient } from "@/lib/supabase/server"

const ROLLER = ["user", "admin", "super_admin"]

/**
 * Endre en brukers rolle. Bare superadministratorer har lov (radnivåsikkerhet
 * på user_profiles krever is_super_admin()). Egen rolle kan ikke endres her,
 * så ingen kan låse seg selv ute.
 */
export async function endreRolle(formData: FormData) {
  const id = String(formData.get("id") ?? "")
  const rolle = String(formData.get("rolle") ?? "")
  let melding = ""
  if (!id || !ROLLER.includes(rolle)) {
    melding = "feil=Ugyldig bruker eller rolle"
  } else {
    const supabase = (await createClient()) as unknown as SupabaseClient
    const {
      data: { user },
    } = await supabase.auth.getUser()
    if (!user) {
      melding = "feil=Du er ikke innlogget"
    } else {
      const { data: rad } = await supabase.from("user_profiles").select("user_id,email").eq("id", id).maybeSingle()
      if (rad?.user_id === user.id) {
        melding = "feil=Du kan ikke endre din egen rolle"
      } else {
        const { data, error } = await supabase.from("user_profiles").update({ role: rolle }).eq("id", id).select("id")
        melding = error
          ? `feil=${encodeURIComponent(`Kunne ikke lagre: ${error.message}`)}`
          : !data?.length
            ? "feil=Bare superadministratorer kan endre roller"
            : `lagret=${encodeURIComponent(`${rad?.email ?? "Brukeren"} har nå rollen ${rolle}`)}`
      }
    }
  }
  revalidatePath("/admin/users")
  redirect(`/admin/users?${melding}`)
}
