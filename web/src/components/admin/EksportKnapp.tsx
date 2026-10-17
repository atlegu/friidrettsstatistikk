import type { SupabaseClient } from "@supabase/supabase-js"
import { createClient } from "@/lib/supabase/server"

/**
 * «Last ned CSV» for administratorer. Vises ikke for andre: lister med navn og
 * fødselsår skal ikke kunne lastes ned av hvem som helst. Selve nedlastingen
 * (/api/eksport) sjekker tilgangen på nytt og logger hvem som tok ut hva.
 */
export async function EksportKnapp({ href }: { href: string }) {
  const supabase = (await createClient()) as unknown as SupabaseClient
  const {
    data: { user },
  } = await supabase.auth.getUser()
  if (!user) return null
  const { data: admin } = await supabase.rpc("check_is_admin", { check_user_id: user.id })
  if (admin !== true) return null
  return (
    <a
      href={href}
      className="inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-sm font-medium hover:bg-muted"
      title="Bare for administratorer. Nedlastingen logges."
    >
      Last ned CSV
    </a>
  )
}
