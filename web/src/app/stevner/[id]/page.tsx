import { notFound } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"
import { SideTopp, MetaSkille, ToppMerke } from "@/components/ui/side-topp"
import { Resultattabell } from "@/components/stevne/Resultattabell"
import { hentAlle } from "@/lib/hent-alle"
import type { Database } from "@/types/database"

/** Stevnenivaaene ligger som engelske enum-verdier i basen. */
const NIVAA: Record<string, string> = {
  local: "Lokalt",
  regional: "Krets",
  national: "Nasjonalt",
  championship: "Mesterskap",
  international: "Internasjonalt",
}

async function getMeet(id: string) {
  const supabase = await createClient()

  const { data } = await supabase
    .from("meets")
    .select("*")
    .eq("id", id)
    .single()

  return data
}

/**
 * Hent alle resultatene fra et stevne.
 *
 * PostgREST leverer aldri mer enn 1 000 rader per spørring. Siden hentet
 * alt i én, og for de 171 stevnene som er større enn det, forsvant resten
 * uten at noe sa fra: Tyrvinglekene 2016 har 3 299 resultater, og siden
 * viste 1 000 av dem og oppga «Resultater 1 000» som om det var tallet.
 * Nøkkeltallene ble regnet ut fra den avkortede lista.
 *
 * Her hentes sidene etter hverandre til stevnet er tomt. Et stevne på
 * 3 299 blir fire spørringer.
 */
type Stevneresultat = Pick<
  Database["public"]["Views"]["results_full"]["Row"],
  | "id"
  | "place"
  | "athlete_id"
  | "athlete_name"
  | "club_name"
  | "performance"
  | "result_type"
  | "wind"
  | "is_pb"
  | "event_name"
>

async function getMeetResults(meetId: string): Promise<Stevneresultat[]> {
  const supabase = await createClient()

  return hentAlle(
    (fra, til) =>
      supabase
        .from("results_full")
        // Bare feltene tabellen under bruker. Med «*» ble hver rad mange
        // ganger stoerre, og sidene her er lange.
        .select("id,place,athlete_id,athlete_name,club_name,performance,result_type,wind,is_pb,event_name")
        .eq("meet_id", meetId)
        .order("event_name", { ascending: true })
        .order("performance_value", { ascending: true })
        .order("id", { ascending: true })
        .range(fra, til),
    "Stevneresultater"
  )
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const meet = await getMeet(id)

  if (!meet) {
    return { title: "Stevne ikke funnet" }
  }

  return {
    title: meet.name,
    description: `Resultater fra ${meet.name}, ${meet.city}`,
  }
}

export default async function MeetPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const meet = await getMeet(id)

  if (!meet) {
    notFound()
  }

  const results = await getMeetResults(id)

  // Group results by event
  const resultsByEvent = results.reduce((acc, result) => {
    const eventName = result.event_name ?? "Ukjent"
    if (!acc[eventName]) {
      acc[eventName] = []
    }
    acc[eventName].push(result)
    return acc
  }, {} as Record<string, typeof results>)

  const eventNames = Object.keys(resultsByEvent).sort()

  return (
    <div className="container py-6">
      <Breadcrumbs items={[
        { label: "Stevner", href: "/stevner" },
        { label: meet.name }
      ]} />

      <SideTopp
        tittel={meet.name}
        meta={
          <>
            <span className="font-bold text-white">
              {new Date(meet.start_date).toLocaleDateString("no-NO", {
                day: "numeric",
                month: "long",
                year: "numeric",
              })}
            </span>
            {(meet.venue || meet.city) && (
              <>
                <MetaSkille />
                <span>{meet.venue ? `${meet.venue}, ${meet.city}` : meet.city}</span>
              </>
            )}
            {meet.organizer_name && (
              <>
                <MetaSkille />
                <span>{meet.organizer_name}</span>
              </>
            )}
            {meet.website && (
              <>
                <MetaSkille />
                <a
                  href={meet.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline-offset-2 hover:underline"
                >
                  Stevnets nettside
                </a>
              </>
            )}
          </>
        }
        merker={
          <>
            <ToppMerke>{meet.indoor ? "Innendørs" : "Utendørs"}</ToppMerke>
            {meet.level && <ToppMerke>{NIVAA[meet.level] ?? meet.level}</ToppMerke>}
          </>
        }
        noekkeltall={[
          { merkelapp: "Resultater", verdi: results.length },
          { merkelapp: "Øvelser", verdi: eventNames.length },
          {
            merkelapp: "Utøvere",
            verdi: new Set(results.map((r) => r.athlete_id)).size,
          },
        ]}
      />

      <div className="mt-6" />

      {/* Results by event */}
      {eventNames.length > 0 ? (
        <div className="space-y-6">
          {eventNames.map((eventName) => (
            <Card key={eventName}>
              <CardHeader>
                <CardTitle>{eventName}</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <Resultattabell rader={resultsByEvent[eventName]} />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground">
            Ingen resultater registrert for dette stevnet
          </CardContent>
        </Card>
      )}
    </div>
  )
}
