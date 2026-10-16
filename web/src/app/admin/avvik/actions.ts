"use server"

import { revalidatePath } from "next/cache"
import { redirect } from "next/navigation"
import type { SupabaseClient } from "@supabase/supabase-js"
import { createClient } from "@/lib/supabase/server"

const GYLDIGE = ["aapen", "godkjent", "rettet", "underkjent"] as const

/**
 * Behandle ett avvik: sett status, hvem som gjorde det, når, og en kommentar.
 * Tilgangen kontrolleres to steder: her (innlogget administrator) og i basen
 * (radnivåsikkerhet på avvik krever is_admin()).
 *
 * Statusen bindes til knappen (behandleAvvik.bind(null, "godkjent")) i stedet
 * for å leses fra knappens name/value, som ikke alltid følger med skjemaet.
 * Feil kastes ikke, men vises som melding øverst på siden.
 */
export async function behandleAvvik(status: string, formData: FormData) {
  const feil = await lagre(status, formData)
  if (feil) redirect(`/admin/avvik?feil=${encodeURIComponent(feil)}`)
  revalidatePath("/admin/avvik")
  revalidatePath("/admin")
}

async function lagre(status: string, formData: FormData): Promise<string | null> {
  const id = Number(formData.get("id"))
  const kommentar = String(formData.get("kommentar") ?? "").trim() || null

  if (!Number.isFinite(id) || id <= 0 || !GYLDIGE.includes(status as (typeof GYLDIGE)[number])) {
    return "Ugyldig avvik eller status"
  }

  try {
    const supabase = (await createClient()) as unknown as SupabaseClient
    const {
      data: { user },
    } = await supabase.auth.getUser()
    if (!user) return "Du er ikke innlogget. Logg inn på nytt."

    const aapnes = status === "aapen"
    const { data, error } = await supabase
      .from("avvik")
      .update({
        status,
        kommentar,
        behandlet_av: aapnes ? null : user.id,
        behandlet_tid: aapnes ? null : new Date().toISOString(),
      })
      .eq("id", id)
      .select("id")

    if (error) return `Kunne ikke lagre: ${error.message}`
    if (!data?.length) return "Avviket ble ikke lagret. Mangler du administratortilgang?"
    return null
  } catch (e) {
    return `Kunne ikke lagre: ${e instanceof Error ? e.message : String(e)}`
  }
}
