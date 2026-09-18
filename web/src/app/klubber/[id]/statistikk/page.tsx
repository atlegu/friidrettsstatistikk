import Link from "next/link"
import { notFound } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"
import { AktivitetLinje } from "@/components/aktivitet/AktivitetLinje"
import { formatPerformance } from "@/lib/format-performance"

export const revalidate = 3600

/* ------------------------------------------------------------------ data */

async function getClub(id: string) {
  const supabase = await createClient()
  const { data } = await supabase.from("clubs").select("*").eq("id", id).single()
  return data
}

/** Tallene fra klubb_bruk, samme kilde som klubbsiden. En levende
 *  opptelling over results_full tok for lang tid og ga 0. */
async function getClubStats(clubId: string) {
  const supabase = await createClient()
  const { data } = await supabase
    .from("klubb_bruk")
    .select("resultater,utovere,fra_ar,til_ar")
    .eq("id", clubId)
    .maybeSingle()
  return {
    totalResults: data?.resultater ?? 0,
    uniqueAthletes: data?.utovere ?? 0,
    firstYear: data?.fra_ar ?? null,
    lastYear: data?.til_ar ?? null,
  }
}

interface PerAar { aar: number; resultater: number; utovere: number; stevner: number }
interface Topp { id: string; full_name: string; birth_year: number | null; resultater: number; stevner: number }
interface Statistikk { per_aar: PerAar[]; i_aar: { resultater: number; utovere: number; stevner: number } | null; topp: Topp[] }

/** Aktivitet per år, sesongen i år og de mest aktive utøverne, i ett kall. */
async function getStatistikk(clubId: string): Promise<Statistikk> {
  const supabase = await createClient()
  const { data, error } = await supabase.rpc("klubb_statistikk", { p_klubb: clubId })
  if (error) console.error("klubb_statistikk:", error.message)
  const d = (data ?? {}) as Partial<Statistikk>
  return { per_aar: d.per_aar ?? [], i_aar: d.i_aar ?? null, topp: d.topp ?? [] }
}

interface Rekord {
  event_id: string
  performance: string
  wind: number | null
  athlete_id: string
  athlete_name: string
  date: string
  result_type: string
}

/** Klubbrekorder senior utendørs for ett kjønn (funksjonen klubbrekorder). */
async function getRekorder(clubId: string, kjonn: "M" | "F"): Promise<Map<string, Rekord>> {
  const supabase = await createClient()
  const { data, error } = await supabase.rpc("klubbrekorder", {
    p_klubb: clubId, p_kjonn: kjonn,
    p_aldersgrupper: ["15", "16", "17", "18-19", "20-22", "Senior"], p_inne: false,
  })
  if (error) console.error("klubbrekorder:", error.message)
  return new Map(((data ?? []) as Rekord[]).map((r) => [r.event_id, r]))
}

async function getEvents() {
  const supabase = await createClient()
  const { data } = await supabase.from("events").select("id,name,sort_order").order("sort_order", { ascending: true })
  return data ?? []
}

/* ------------------------------------------------------------------ ui */

function tall(n: number) {
  return n.toLocaleString("nb-NO")
}

function Tall({ navn, verdi, under }: { navn: string; verdi: string; under?: string }) {
  return (
    <div className="rounded-xl border border-[var(--border-default)] bg-[var(--bg-surface)] px-[18px] py-4">
      <div className="text-[12px] font-bold uppercase tracking-[0.06em] text-[var(--text-muted)]">{navn}</div>
      <div className="my-0.5 text-[30px] font-black tracking-tight tabular-nums text-[var(--text-primary)]">{verdi}</div>
      {under && <div className="text-[12.5px] text-[var(--text-secondary)]">{under}</div>}
    </div>
  )
}

function Kort({ tittel, lenke, children }: { tittel: string; lenke?: { href: string; tekst: string }; children: React.ReactNode }) {
  return (
    <section className="min-w-0 rounded-xl border border-[var(--border-default)] bg-[var(--bg-surface)] p-5">
      <div className="mb-3 flex items-baseline justify-between gap-3">
        <h2 className="text-[16px] font-bold tracking-tight">{tittel}</h2>
        {lenke && <Link href={lenke.href} className="text-[13px] font-semibold">{lenke.tekst} →</Link>}
      </div>
      {children}
    </section>
  )
}

function RekordCelle({ r }: { r: Rekord | undefined }) {
  if (!r) return <td className="py-2 pr-3 text-[var(--text-muted)]">–</td>
  return (
    <td className="py-2 pr-3">
      <span className="font-black tabular-nums">{formatPerformance(r.performance, r.result_type)}</span>
      {r.wind !== null && <span className="ml-1 text-[11.5px] text-[var(--text-muted)]">({r.wind > 0 ? "+" : ""}{r.wind})</span>}
      <div className="text-[12.5px] text-[var(--text-secondary)]">
        <Link href={`/utover/${r.athlete_id}`} className="text-[var(--text-primary)]">{r.athlete_name}</Link>
        <span className="ml-1 text-[var(--text-muted)]">{r.date?.slice(0, 4)}</span>
      </div>
    </td>
  )
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const club = await getClub(id)
  if (!club) return { title: "Klubb ikke funnet" }
  return {
    title: `${club.name} - Statistikk`,
    description: `Statistikk for ${club.name} - aktivitet, klubbrekorder, årslister og all-time lister`,
  }
}

const iAar = new Date().getFullYear()
const aarsliste = Array.from({ length: 10 }, (_, i) => iAar - i)

export default async function ClubStatistikkPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const club = await getClub(id)
  if (!club) notFound()

  const [stats, statistikk, rekM, rekF, events] = await Promise.all([
    getClubStats(id), getStatistikk(id), getRekorder(id, "M"), getRekorder(id, "F"), getEvents(),
  ])

  const linjedata = statistikk.per_aar.map((p) => ({ aar: p.aar, alle: p.utovere, ungdom: null }))
  const rekordRader = events.filter((e) => rekM.has(e.id) || rekF.has(e.id))
  const sesong = statistikk.i_aar

  return (
    <div className="container py-6">
      <Breadcrumbs items={[
        { label: "Klubber", href: "/klubber" },
        { label: club.name, href: `/klubber/${id}` },
        { label: "Statistikk" },
      ]} />
      <h1 className="mt-4 mb-4">{club.name} – Statistikk</h1>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Tall navn="Resultater totalt" verdi={tall(stats.totalResults)} />
        <Tall navn="Utøvere med resultater" verdi={tall(stats.uniqueAthletes)} />
        <Tall navn="Resultatperiode" verdi={stats.firstYear && stats.lastYear ? `${stats.firstYear}–${stats.lastYear}` : "–"} />
        <Tall navn={`Sesongen ${iAar}`} verdi={sesong ? tall(sesong.resultater) : "0"}
              under={sesong ? `resultater · ${tall(sesong.utovere)} utøvere · ${tall(sesong.stevner)} stevner` : undefined} />
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-[minmax(0,1fr)_340px] lg:items-start">
        <div className="grid min-w-0 grid-cols-1 gap-4">
          <Kort tittel="Aktive utøvere per år">
            {linjedata.length > 1 ? (
              <AktivitetLinje data={linjedata} visUngdom={false} />
            ) : (
              <p className="text-[13px] text-[var(--text-muted)]">For lite grunnlag.</p>
            )}
            <p className="mt-2 text-[12.5px] text-[var(--text-muted)]">
              Utøvere med minst ett godkjent resultat for {club.name} i året. Inneværende sesong er ufullstendig til den er over.
            </p>
          </Kort>

          <Kort tittel="Klubbrekorder senior utendørs" lenke={{ href: `/klubber/${id}/statistikk/rekorder`, tekst: "Alle klubbrekorder" }}>
            {rekordRader.length === 0 ? (
              <p className="text-[13px] text-[var(--text-muted)]">Ingen godkjente resultater.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full whitespace-nowrap text-[14px]">
                  <thead>
                    <tr className="border-b border-[var(--border-default)] text-left text-[11.5px] uppercase tracking-wide text-[var(--text-muted)]">
                      <th className="py-1.5 pr-3 font-bold">Øvelse</th>
                      <th className="py-1.5 pr-3 font-bold">Menn</th>
                      <th className="py-1.5 pr-3 font-bold">Kvinner</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rekordRader.map((e) => (
                      <tr key={e.id} className="border-b border-[var(--border-default)] last:border-0 align-top">
                        <td className="py-2 pr-3">
                          <Link href={`/klubber/${id}/statistikk/all-time?event=${e.id}&gender=M&age=Senior&venue=outdoor`} className="text-[var(--text-primary)]">{e.name}</Link>
                        </td>
                        <RekordCelle r={rekM.get(e.id)} />
                        <RekordCelle r={rekF.get(e.id)} />
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            <p className="mt-2 text-[12.5px] text-[var(--text-muted)]">
              Beste godkjente resultat per øvelse: lovlig vind der vind teller, ikke håndtid i sprint og hekk. Innendørs og aldersklasser under «Alle klubbrekorder».
            </p>
          </Kort>
        </div>

        <div className="grid min-w-0 grid-cols-1 gap-4">
          <Kort tittel={`Mest aktive i ${iAar}`} lenke={{ href: `/klubber/${id}/statistikk/${iAar}`, tekst: "Årsliste" }}>
            {statistikk.topp.length === 0 ? (
              <p className="text-[13px] text-[var(--text-muted)]">Ingen resultater i {iAar} ennå.</p>
            ) : (
              <table className="w-full text-[14px]">
                <tbody>
                  {statistikk.topp.map((u) => (
                    <tr key={u.id} className="border-b border-[var(--border-default)] last:border-0">
                      <td className="py-1.5 pr-2">
                        <Link href={`/utover/${u.id}`} className="text-[var(--text-primary)]">{u.full_name}</Link>
                        {u.birth_year && <span className="ml-1 text-[12px] text-[var(--text-muted)]">{u.birth_year}</span>}
                      </td>
                      <td className="py-1.5 text-right tabular-nums text-[var(--text-secondary)]">
                        <b className="text-[var(--text-primary)]">{u.resultater}</b> res · {u.stevner} stevner
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </Kort>

          <Kort tittel="Årslister">
            <p className="mb-3 text-[13px] text-[var(--text-secondary)]">Beste resultater per år og øvelse for {club.name}.</p>
            <div className="flex flex-wrap gap-2">
              {aarsliste.map((aar) => (
                <Link key={aar} href={`/klubber/${id}/statistikk/${aar}`}
                      className="rounded-md bg-[var(--bg-muted)] px-3 py-1 text-[13px] font-semibold text-[var(--text-primary)] hover:bg-[var(--nfif-navy)] hover:text-white">
                  {aar}
                </Link>
              ))}
            </div>
          </Kort>

          <Kort tittel="All-time lister" lenke={{ href: `/klubber/${id}/statistikk/all-time`, tekst: "Åpne" }}>
            <p className="text-[13px] text-[var(--text-secondary)]">Historiske toppresultater for {club.name} gjennom alle tider, per øvelse, kjønn, aldersklasse og bane.</p>
          </Kort>
        </div>
      </div>
    </div>
  )
}
