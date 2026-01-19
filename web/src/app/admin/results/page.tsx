import { createClient } from "@/lib/supabase/server"
import { ResultsTable } from "./results-table"

export const metadata = {
  title: "Administrer resultater",
}

async function getEvents() {
  const supabase = await createClient()
  const { data } = await supabase
    .from("events")
    .select("id, name, code")
    .order("name")
  return data ?? []
}

async function getAthletes() {
  const supabase = await createClient()
  const { data } = await supabase
    .from("athletes")
    .select("id, full_name")
    .order("full_name")
    .limit(1000)
  return data ?? []
}

export default async function AdminResultsPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>
}) {
  const params = await searchParams
  const events = await getEvents()
  const athletes = await getAthletes()

  return (
    <div className="container py-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold">Resultater</h1>
      </div>

      <ResultsTable
        events={events}
        athletes={athletes}
        initialSearch={typeof params.search === "string" ? params.search : ""}
        initialEvent={typeof params.event === "string" ? params.event : ""}
        initialAthleteId={typeof params.athlete === "string" ? params.athlete : ""}
      />
    </div>
  )
}
