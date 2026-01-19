import Link from "next/link"
import { createClient } from "@/lib/supabase/server"
import { AthletesTable } from "./athletes-table"
import { Button } from "@/components/ui/button"
import { GitMerge } from "lucide-react"

export const metadata = {
  title: "Administrer utøvere",
}

async function getClubs() {
  const supabase = await createClient()
  const { data } = await supabase
    .from("clubs")
    .select("id, name")
    .order("name")
  return data ?? []
}

export default async function AdminAthletesPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>
}) {
  const params = await searchParams
  const clubs = await getClubs()

  return (
    <div className="container py-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold">Utøvere</h1>
        <Link href="/admin/athletes/merge">
          <Button variant="outline">
            <GitMerge className="h-4 w-4 mr-2" />
            Slå sammen utøvere
          </Button>
        </Link>
      </div>

      <AthletesTable
        clubs={clubs}
        initialSearch={typeof params.search === "string" ? params.search : ""}
        initialClub={typeof params.club === "string" ? params.club : ""}
        initialGender={typeof params.gender === "string" ? params.gender : ""}
      />
    </div>
  )
}
