import { notFound } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { ImportReview } from "./import-review"

export const metadata = {
  title: "Gjennomgå import | Admin",
}

type Props = {
  params: Promise<{ id: string }>
}

async function getImportBatch(id: string) {
  const supabase = await createClient()

  const { data, error } = await supabase
    .from("import_batches")
    .select("*")
    .eq("id", id)
    .single()

  if (error || !data) {
    return null
  }

  return data
}

async function getAthletes() {
  const supabase = await createClient()

  // Fetch all athletes in batches - Supabase has a 1000 row limit per request
  const allAthletes: any[] = []
  let offset = 0
  const batchSize = 1000

  while (true) {
    const { data, error } = await supabase
      .from("athletes")
      .select("id, full_name, birth_year, gender, current_club_id, clubs:current_club_id(name)")
      .order("full_name")
      .range(offset, offset + batchSize - 1)

    if (error || !data || data.length === 0) break

    allAthletes.push(...data)
    offset += batchSize

    // Safety limit
    if (offset > 100000) break
  }

  console.log("Total athletes fetched:", allAthletes.length)
  return allAthletes
}

async function getEvents() {
  const supabase = await createClient()

  const { data, error } = await supabase
    .from("events")
    .select("id, name, code, category")
    .order("sort_order")

  if (error) {
    console.error("Error fetching events:", error)
  }
  console.log("Events fetched:", data?.length)

  return data ?? []
}

async function getMeets() {
  const supabase = await createClient()

  const { data } = await supabase
    .from("meets")
    .select("id, name, city, start_date")
    .order("start_date", { ascending: false })
    .limit(500)

  return data ?? []
}

async function getSeasons() {
  const supabase = await createClient()

  const { data } = await supabase
    .from("seasons")
    .select("id, year")
    .order("year", { ascending: false })

  return data ?? []
}

export default async function ImportDetailPage({ params }: Props) {
  const { id } = await params
  const [batch, athletes, events, meets, seasons] = await Promise.all([
    getImportBatch(id),
    getAthletes(),
    getEvents(),
    getMeets(),
    getSeasons(),
  ])

  if (!batch) {
    notFound()
  }

  return (
    <div className="container py-8">
      <ImportReview
        batch={batch}
        athletes={athletes}
        events={events}
        meets={meets}
        seasons={seasons}
      />
    </div>
  )
}
