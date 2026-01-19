import { ClubsTable } from "./clubs-table"

export const metadata = {
  title: "Administrer klubber",
}

export default async function AdminClubsPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>
}) {
  const params = await searchParams

  return (
    <div className="container py-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold">Klubber</h1>
      </div>

      <ClubsTable
        initialSearch={typeof params.search === "string" ? params.search : ""}
      />
    </div>
  )
}
