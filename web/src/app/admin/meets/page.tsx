import { createClient } from "@/lib/supabase/server"
import { MeetsTable } from "./meets-table"

export const metadata = {
  title: "Administrer stevner",
}

export default async function AdminMeetsPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>
}) {
  const params = await searchParams

  return (
    <div className="container py-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold">Stevner</h1>
      </div>

      <MeetsTable
        initialSearch={typeof params.search === "string" ? params.search : ""}
        initialYear={typeof params.year === "string" ? params.year : ""}
        initialIndoor={typeof params.indoor === "string" ? params.indoor : ""}
      />
    </div>
  )
}
