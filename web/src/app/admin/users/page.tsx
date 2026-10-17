import type { SupabaseClient } from "@supabase/supabase-js"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent } from "@/components/ui/card"
import { endreRolle } from "./actions"

export const metadata = { title: "Brukere" }

const ROLLENAVN: Record<string, string> = {
  user: "Bruker",
  admin: "Administrator",
  super_admin: "Superadministrator",
}

type Profil = { id: string; user_id: string; email: string | null; display_name: string | null; role: string; created_at: string }
type Eksport = { id: number; epost: string | null; type: string; parametre: Record<string, string>; rader: number; tid: string }

const dato = (d: string) =>
  new Date(d).toLocaleString("nb-NO", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" })

export default async function BrukerePage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>
}) {
  const sp = await searchParams
  const supabase = (await createClient()) as unknown as SupabaseClient
  const {
    data: { user },
  } = await supabase.auth.getUser()

  const [{ data: profiler }, { data: eksporter }] = await Promise.all([
    supabase.from("user_profiles").select("id,user_id,email,display_name,role,created_at").order("created_at"),
    supabase.from("eksport_logg").select("id,epost,type,parametre,rader,tid").order("tid", { ascending: false }).limit(50),
  ])
  const rader = (profiler ?? []) as Profil[]
  const meg = rader.find((p) => p.user_id === user?.id)
  const erSuper = meg?.role === "super_admin"
  const feil = typeof sp.feil === "string" ? sp.feil.slice(0, 300) : null
  const lagret = typeof sp.lagret === "string" ? sp.lagret.slice(0, 300) : null

  return (
    <div className="container py-8">
      <h1 className="mb-2 text-3xl font-bold">Brukere</h1>
      <p className="mb-6 max-w-3xl text-sm text-muted-foreground">
        Administratorer behandler avvik, terminliste, import og redigering, og kan laste ned lister.
        Superadministratorer kan i tillegg endre roller.
      </p>

      {feil && (
        <p className="mb-4 rounded-md border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-200">{feil}</p>
      )}
      {lagret && !feil && (
        <p className="mb-4 rounded-md border border-green-300 bg-green-50 px-4 py-3 text-sm text-green-800 dark:border-green-900 dark:bg-green-950 dark:text-green-200">Lagret. {lagret}</p>
      )}

      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/50 text-left">
                  <th className="px-3 py-2 font-medium">E-post</th>
                  <th className="px-3 py-2 font-medium">Navn</th>
                  <th className="px-3 py-2 font-medium">Rolle</th>
                  <th className="px-3 py-2 font-medium">Opprettet</th>
                </tr>
              </thead>
              <tbody>
                {rader.map((p) => (
                  <tr key={p.id} className="border-b last:border-0">
                    <td className="px-3 py-2">{p.email ?? "–"}</td>
                    <td className="px-3 py-2">{p.display_name ?? "–"}</td>
                    <td className="px-3 py-2">
                      {erSuper && p.user_id !== user?.id ? (
                        <form action={endreRolle} className="flex items-center gap-2">
                          <input type="hidden" name="id" value={p.id} />
                          <select name="rolle" defaultValue={p.role} className="h-8 rounded-md border bg-background px-2 text-xs">
                            {Object.entries(ROLLENAVN).map(([v, n]) => (
                              <option key={v} value={v}>{n}</option>
                            ))}
                          </select>
                          <button className="rounded-md border px-2 py-1 text-xs hover:bg-muted">Lagre</button>
                        </form>
                      ) : (
                        <span>{ROLLENAVN[p.role] ?? p.role}{p.user_id === user?.id ? " (deg)" : ""}</span>
                      )}
                    </td>
                    <td className="px-3 py-2 tabular-nums text-muted-foreground">{dato(p.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <h2 className="mb-2 mt-10 text-xl font-bold">Siste nedlastinger</h2>
      <p className="mb-4 max-w-3xl text-sm text-muted-foreground">
        Lister med navn og fødselsår er personopplysninger. Hver nedlasting logges med hvem, hva og når.
      </p>
      <Card>
        <CardContent className="p-0">
          {(eksporter ?? []).length === 0 ? (
            <p className="p-6 text-sm text-muted-foreground">Ingen nedlastinger ennå.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/50 text-left">
                    <th className="px-3 py-2 font-medium">Tidspunkt</th>
                    <th className="px-3 py-2 font-medium">Bruker</th>
                    <th className="px-3 py-2 font-medium">Liste</th>
                    <th className="px-3 py-2 text-right font-medium">Rader</th>
                  </tr>
                </thead>
                <tbody>
                  {((eksporter ?? []) as Eksport[]).map((e) => (
                    <tr key={e.id} className="border-b last:border-0">
                      <td className="px-3 py-2 tabular-nums">{dato(e.tid)}</td>
                      <td className="px-3 py-2">{e.epost ?? "–"}</td>
                      <td className="px-3 py-2">
                        {e.type}
                        <span className="ml-2 text-xs text-muted-foreground">
                          {Object.entries(e.parametre ?? {}).filter(([k]) => k !== "type").map(([k, v]) => `${k}=${v}`).join(" · ")}
                        </span>
                      </td>
                      <td className="px-3 py-2 text-right tabular-nums">{e.rader}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
