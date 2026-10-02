import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import type { Database } from '@/types/database'

/**
 * Alle svar fra basen som ikke er OK logges her, med sti og feilmelding.
 * Mange sider leser bare `data` og viser «ingen resultater» når en
 * spørring feiler, og da var feilen usynlig. Nå står den i loggen uansett
 * om siden sjekker `error` eller ikke.
 */
async function loggetFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  const svar = await fetch(input, init)
  if (!svar.ok) {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
    let melding = ''
    try {
      melding = (await svar.clone().text()).slice(0, 300)
    } catch {
      /* uten kropp */
    }
    console.error(`Supabase ${svar.status} ${url.replace(process.env.NEXT_PUBLIC_SUPABASE_URL ?? '', '')}: ${melding}`)
  }
  return svar
}

export async function createClient() {
  const cookieStore = await cookies()

  return createServerClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      global: { fetch: loggetFetch },
      cookies: {
        getAll() {
          return cookieStore.getAll()
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            )
          } catch {
            // The `setAll` method was called from a Server Component.
            // This can be ignored if you have middleware refreshing
            // user sessions.
          }
        },
      },
    }
  )
}
