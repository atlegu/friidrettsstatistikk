import Link from "next/link"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Users, Trophy, Calendar, Building2, Upload, AlertCircle } from "lucide-react"

async function getStats() {
  const supabase = await createClient()

  const [athletesResult, clubsResult, resultsResult, meetsResult, pendingImports] = await Promise.all([
    supabase.from("athletes").select("id", { count: "exact", head: true }),
    supabase.from("clubs").select("id", { count: "exact", head: true }),
    supabase.from("results").select("id", { count: "exact", head: true }),
    supabase.from("meets").select("id", { count: "exact", head: true }),
    supabase.from("import_batches").select("id", { count: "exact", head: true }).eq("status", "pending"),
  ])

  return {
    athletes: athletesResult.count ?? 0,
    clubs: clubsResult.count ?? 0,
    results: resultsResult.count ?? 0,
    meets: meetsResult.count ?? 0,
    pendingImports: pendingImports.count ?? 0,
  }
}

async function getRecentImports() {
  const supabase = await createClient()

  const { data } = await supabase
    .from("import_batches")
    .select("*")
    .order("created_at", { ascending: false })
    .limit(5)

  return data ?? []
}

export default async function AdminDashboardPage() {
  const stats = await getStats()
  const recentImports = await getRecentImports()

  return (
    <div className="container py-8">
      <h1 className="mb-6 text-3xl font-bold">Dashboard</h1>

      {/* Stats */}
      <div className="mb-8 grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Utøvere</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.athletes.toLocaleString("no-NO")}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Klubber</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.clubs.toLocaleString("no-NO")}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Resultater</CardTitle>
            <Trophy className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.results.toLocaleString("no-NO")}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Stevner</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.meets.toLocaleString("no-NO")}</div>
          </CardContent>
        </Card>

        <Card className={stats.pendingImports > 0 ? "border-yellow-500" : ""}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Ventende import</CardTitle>
            {stats.pendingImports > 0 ? (
              <AlertCircle className="h-4 w-4 text-yellow-500" />
            ) : (
              <Upload className="h-4 w-4 text-muted-foreground" />
            )}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.pendingImports}</div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="mb-4 text-xl font-semibold">Administrasjon</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Link href="/admin/athletes">
            <Card className="cursor-pointer transition-colors hover:bg-muted/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Users className="h-5 w-5" />
                  Utøvere
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Søk, rediger og slå sammen utøverprofiler
                </p>
              </CardContent>
            </Card>
          </Link>

          <Link href="/admin/results">
            <Card className="cursor-pointer transition-colors hover:bg-muted/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Trophy className="h-5 w-5" />
                  Resultater
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Rediger og slett feilregistrerte resultater
                </p>
              </CardContent>
            </Card>
          </Link>

          <Link href="/admin/meets">
            <Card className="cursor-pointer transition-colors hover:bg-muted/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Calendar className="h-5 w-5" />
                  Stevner
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Rediger stevneinfo som dato, sted og navn
                </p>
              </CardContent>
            </Card>
          </Link>

          <Link href="/admin/clubs">
            <Card className="cursor-pointer transition-colors hover:bg-muted/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Building2 className="h-5 w-5" />
                  Klubber
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Rediger klubbnavn, by og fylke
                </p>
              </CardContent>
            </Card>
          </Link>

          <Link href="/admin/import">
            <Card className="cursor-pointer transition-colors hover:bg-muted/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Upload className="h-5 w-5" />
                  Importer
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Last opp resultater fra FriRes eller Excel
                </p>
              </CardContent>
            </Card>
          </Link>
        </div>
      </div>

      {/* Recent Imports */}
      <div>
        <h2 className="mb-4 text-xl font-semibold">Nylige importer</h2>
        <Card>
          <CardContent className="p-0">
            {recentImports.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="px-4 py-3 text-left text-sm font-medium">Navn</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Rader</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Dato</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentImports.map((batch) => (
                      <tr key={batch.id} className="border-b last:border-0 hover:bg-muted/30">
                        <td className="px-4 py-3 font-medium">{batch.name}</td>
                        <td className="px-4 py-3">
                          <span
                            className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${
                              batch.status === "imported"
                                ? "bg-green-100 text-green-800"
                                : batch.status === "pending"
                                ? "bg-yellow-100 text-yellow-800"
                                : batch.status === "rejected"
                                ? "bg-red-100 text-red-800"
                                : "bg-gray-100 text-gray-800"
                            }`}
                          >
                            {batch.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm text-muted-foreground">
                          {batch.row_count ?? "-"}
                        </td>
                        <td className="px-4 py-3 text-sm text-muted-foreground">
                          {batch.created_at
                            ? new Date(batch.created_at).toLocaleDateString("no-NO")
                            : "-"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="p-8 text-center text-muted-foreground">
                Ingen importer ennå
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
