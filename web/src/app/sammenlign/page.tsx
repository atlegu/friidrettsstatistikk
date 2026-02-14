import { Suspense } from "react"
import { Loader2 } from "lucide-react"
import { createClient } from "@/lib/supabase/server"
import CompareContent from "./compare-content"

export default async function ComparePage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>
}) {
  const params = await searchParams

  const id1 = typeof params.id1 === "string" ? params.id1 : null
  const id2 = typeof params.id2 === "string" ? params.id2 : null
  const event = typeof params.event === "string" ? params.event : null
  const tab = typeof params.tab === "string" ? params.tab : null

  // Fetch athletes on the server to avoid client-side Supabase auth issues
  const supabase = await createClient()
  let athlete1 = null
  let athlete2 = null

  if (id1) {
    const { data } = await supabase
      .from("athletes")
      .select("id, first_name, last_name, full_name, birth_year, gender")
      .eq("id", id1)
      .single()
    athlete1 = data
  }

  if (id2) {
    const { data } = await supabase
      .from("athletes")
      .select("id, first_name, last_name, full_name, birth_year, gender")
      .eq("id", id2)
      .single()
    athlete2 = data
  }

  return (
    <Suspense
      fallback={
        <div className="container flex min-h-[50vh] items-center justify-center py-6">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      }
    >
      <CompareContent
        initialAthlete1={athlete1}
        initialAthlete2={athlete2}
        initialEvent={event}
        initialTab={tab}
      />
    </Suspense>
  )
}
