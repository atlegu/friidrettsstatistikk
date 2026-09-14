import Link from "next/link"
import { createClient } from "@/lib/supabase/server"
import { ArrowRight } from "lucide-react"
import { ForsideSok } from "@/components/ForsideSok"
import { formatPerformance } from "@/lib/format-performance"
import {
  INDOOR_CHAMPIONSHIP_EVENTS,
  OUTDOOR_CHAMPIONSHIP_EVENTS,
  TIME_EVENT_CODES,
  getEventDisplayName,
} from "@/lib/event-config"

export const revalidate = 900

// Tellerne leses fra en materialisert visning, ikke med count: "exact".
// En exact count over results (1,95 mill. rader) tar 0,3 s alene, men 2,8 s
// når siden fyrer av knapt 40 spørringer samtidig — og feilet i produksjon,
// der resultattelleren sto tom. Visningen oppdateres av importen.
async function getStats() {
  const supabase = await createClient()

  const { data } = await supabase
    .from("plattform_statistikk")
    .select("antall_utovere,antall_klubber,antall_resultater,antall_stevner")
    .single()

  // Uten tall vises en strek. Et 0 ville sett ut som et gyldig svar.
  return {
    athletes: data?.antall_utovere ?? null,
    clubs: data?.antall_klubber ?? null,
    results: data?.antall_resultater ?? null,
    meets: data?.antall_stevner ?? null,
  }
}

function formatAntall(n: number | null) {
  return n === null ? "–" : n.toLocaleString("no-NO")
}

async function getSeasonLeaders() {
  const supabase = await createClient()
  const month = new Date().getMonth() + 1
  const isIndoor = month >= 12 || month <= 3
  const currentYear = new Date().getFullYear()

  const championshipEvents = isIndoor ? INDOOR_CHAMPIONSHIP_EVENTS : OUTDOOR_CHAMPIONSHIP_EVENTS

  async function getLeadersForGender(gender: "M" | "F") {
    const eventCodes = championshipEvents[gender]

    const selectCols =
      "athlete_id, athlete_name, event_code, event_name, event_id, performance, performance_value, result_type, wind"

    // Query each event individually to guarantee we get the best result per event
    // (a combined query with .limit() misses long-distance events because their
    // performance_value is much higher than sprint events)
    const results = await Promise.all(
      eventCodes.map(async (code) => {
        const isTime = TIME_EVENT_CODES.has(code)
        const { data } = await supabase
          .from("results_full")
          .select(selectCols)
          .eq("event_code", code)
          .eq("season_year", currentYear)
          .eq("meet_indoor", isIndoor)
          .eq("gender", gender)
          .eq("status", "OK")
          .gt("performance_value", 0)
          .order("performance_value", { ascending: isTime })
          .limit(1)
        return data?.[0] ?? null
      })
    )

    return results.filter((r): r is NonNullable<typeof r> => r != null)
  }

  const [men, women] = await Promise.all([
    getLeadersForGender("M"),
    getLeadersForGender("F"),
  ])

  return { men, women, isIndoor, year: currentYear }
}

type Leder = Awaited<ReturnType<typeof getSeasonLeaders>>["men"][number]

/** Ett inngangskort i «Finn fram»-rutenettet. */
function Inngang({ href, tittel, beskrivelse }: {
  href: string; tittel: string; beskrivelse: string
}) {
  return (
    <Link
      href={href}
      className="group flex items-start justify-between gap-3 rounded-xl border
                 border-[var(--border-default)] bg-[var(--bg-surface)] p-4
                 transition-colors hover:border-[var(--nfif-navy-lys)]"
    >
      <div>
        <div className="font-semibold text-[var(--text-primary)]">{tittel}</div>
        <p className="mt-0.5 text-[13px] text-[var(--text-secondary)]">{beskrivelse}</p>
      </div>
      <ArrowRight className="mt-1 h-4 w-4 flex-shrink-0 text-[var(--text-muted)] transition-transform group-hover:translate-x-0.5" />
    </Link>
  )
}

/** Årsbestetabell for ett kjønn. Mann og kvinne var før to like blokker. */
function Aarsbeste({ tittel, ledere, venueParam }: {
  tittel: string; ledere: Leder[]; venueParam: string
}) {
  return (
    <div className="overflow-hidden rounded-xl border border-[var(--border-default)] bg-[var(--bg-surface)]">
      <h3 className="border-b border-[var(--border-default)] bg-[var(--bg-muted)] px-4 py-2.5 text-[13px] font-bold uppercase tracking-wide text-[var(--nfif-navy)]">
        {tittel}
      </h3>
      {ledere.length === 0 ? (
        <p className="p-4 text-center text-sm text-[var(--text-muted)]">Ingen resultater ennå</p>
      ) : (
        <table className="w-full">
          <tbody>
            {ledere.map((r) => (
              <tr
                key={r.event_code}
                className="border-b border-[var(--border-default)] last:border-0 hover:bg-[var(--bg-muted)]"
              >
                <td className="px-4 py-2 text-[13px]">
                  <Link
                    href={`/statistikk?event=${r.event_id}&gender=${tittel === "Menn" ? "M" : "F"}&venue=${venueParam}`}
                    className="text-[var(--text-secondary)] hover:text-[var(--accent-primary)]"
                  >
                    {getEventDisplayName(r.event_code!)}
                  </Link>
                </td>
                <td className="whitespace-nowrap px-4 py-2 text-right">
                  <span className="perf-value text-[13px] font-bold tabular-nums">
                    {formatPerformance(r.performance, r.result_type)}
                  </span>
                  {r.wind !== null && r.wind !== undefined && (
                    <span className="ml-1 text-[11px] text-[var(--text-muted)]">
                      ({r.wind > 0 ? "+" : ""}{r.wind})
                    </span>
                  )}
                </td>
                <td className="px-4 py-2 text-[13px]">
                  <Link
                    href={`/utover/${r.athlete_id}`}
                    className="font-medium text-[var(--accent-primary)] hover:underline"
                  >
                    {r.athlete_name}
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export default async function Home() {
  const [stats, seasonLeaders] = await Promise.all([getStats(), getSeasonLeaders()])

  const venueLabel = seasonLeaders.isIndoor ? "Innendørs" : "Utendørs"
  const venueParam = seasonLeaders.isIndoor ? "indoor" : "outdoor"
  const aar = seasonLeaders.year

  const noekkeltall = [
    { merkelapp: "Resultater", verdi: stats.results },
    { merkelapp: "Utøvere", verdi: stats.athletes },
    { merkelapp: "Stevner", verdi: stats.meets },
    { merkelapp: "Klubber", verdi: stats.clubs },
  ]

  return (
    <>
      {/* Topp med søk. Det vanligste er å slå opp en person, så søket
          står åpent i stedet for bak et ikon i menyen. */}
      <section className="relative overflow-hidden bg-[var(--nfif-navy)]">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 bg-gradient-to-br from-[var(--nfif-navy-dyp)] via-[var(--nfif-navy)] to-[var(--nfif-navy-lys)]"
        />
        <div
          aria-hidden
          className="pointer-events-none absolute -right-32 -top-48 hidden h-[520px] w-[520px] rounded-full border-[64px] border-white/[0.04] lg:block"
        />
        <div className="container relative py-10 md:py-14">
          <div className="mx-auto max-w-2xl text-center">
            <h1 className="text-3xl font-bold tracking-tight text-white md:text-[2.5rem]">
              Norsk friidrettsstatistikk
            </h1>
            <p className="mx-auto mt-2 max-w-lg text-[15px] text-[var(--nfif-navy-blekk)]">
              Resultater, rekorder og utøverprofiler — fra rekrutt til veteran.
            </p>
            <div className="mt-6">
              <ForsideSok />
            </div>
          </div>

          <dl className="mx-auto mt-9 grid max-w-3xl grid-cols-2 gap-x-6 gap-y-5 sm:grid-cols-4">
            {noekkeltall.map((n) => (
              <div key={n.merkelapp} className="text-center">
                <dd className="text-2xl font-bold tabular-nums text-white md:text-[1.75rem]">
                  {formatAntall(n.verdi)}
                </dd>
                <dt className="mt-0.5 text-[11px] font-bold uppercase tracking-[0.07em] text-[var(--nfif-navy-blekk-svak)]">
                  {n.merkelapp}
                </dt>
              </div>
            ))}
          </dl>
        </div>
      </section>

      <div className="container py-8 md:py-10">
        {/* Inngangene. Seks veier videre, ikke tre. */}
        <section className="mb-10">
          <h2 className="mb-4 text-xl font-semibold">Finn fram</h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <Inngang href={`/statistikk/${aar}`} tittel={`Årslister ${aar}`}
                     beskrivelse="Årets beste, per øvelse og aldersklasse" />
            <Inngang href="/statistikk/all-time" tittel="Alle tiders"
                     beskrivelse="De beste noteringene gjennom historien" />
            <Inngang href="/statistikk/rekorder" tittel="Norske rekorder"
                     beskrivelse="Offisielle rekorder i alle øvelser" />
            <Inngang href="/mesterskap" tittel="Mesterskap"
                     beskrivelse="Hvem er kvalifisert til NM" />
            <Inngang href="/stevner" tittel="Stevner"
                     beskrivelse="Stevnekalender og resultatlister" />
            <Inngang href="/klubber" tittel="Klubber"
                     beskrivelse="Klubbstatistikk, rekorder og utøvere" />
          </div>
        </section>

        {/* Årsbeste */}
        <section>
          <div className="mb-4 flex flex-wrap items-baseline justify-between gap-2">
            <h2 className="text-xl font-semibold">
              Årsbeste {aar}
              <span className="ml-2 text-[13px] font-normal text-[var(--text-muted)]">
                {venueLabel.toLowerCase()}
              </span>
            </h2>
            <Link
              href={`/statistikk?venue=${venueParam}`}
              className="inline-flex items-center gap-1 text-[13px] font-medium text-[var(--accent-primary)] hover:underline"
            >
              Se alle årslister <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <Aarsbeste tittel="Menn" ledere={seasonLeaders.men} venueParam={venueParam} />
            <Aarsbeste tittel="Kvinner" ledere={seasonLeaders.women} venueParam={venueParam} />
          </div>
        </section>
      </div>
    </>
  )
}
