import Link from "next/link"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Upload, FileSpreadsheet, Clock, CheckCircle, XCircle, AlertTriangle } from "lucide-react"
import { UploadForm } from "./upload-form"

export const metadata = {
  title: "Import | Admin",
}

async function getImportBatches() {
  const supabase = await createClient()

  const { data, error } = await supabase
    .from("import_batches")
    .select("*")
    .order("created_at", { ascending: false })
    .limit(50)

  if (error) {
    console.error("Error fetching import batches:", error)
    return []
  }

  return data ?? []
}

async function getStats() {
  const supabase = await createClient()

  const [pending, imported, rejected] = await Promise.all([
    supabase.from("import_batches").select("id", { count: "exact", head: true }).eq("status", "pending"),
    supabase.from("import_batches").select("id", { count: "exact", head: true }).eq("status", "imported"),
    supabase.from("import_batches").select("id", { count: "exact", head: true }).eq("status", "rejected"),
  ])

  return {
    pending: pending.count ?? 0,
    imported: imported.count ?? 0,
    rejected: rejected.count ?? 0,
  }
}

function StatusBadge({ status }: { status: string | null }) {
  const config = {
    pending: { label: "Venter", className: "bg-yellow-100 text-yellow-800", icon: Clock },
    imported: { label: "Importert", className: "bg-green-100 text-green-800", icon: CheckCircle },
    rejected: { label: "Avvist", className: "bg-red-100 text-red-800", icon: XCircle },
    processing: { label: "Behandler", className: "bg-blue-100 text-blue-800", icon: Clock },
  }

  const { label, className, icon: Icon } = config[status as keyof typeof config] ?? {
    label: status ?? "Ukjent",
    className: "bg-gray-100 text-gray-800",
    icon: AlertTriangle,
  }

  return (
    <span className={`inline-flex items-center gap-1 rounded px-2 py-0.5 text-xs font-medium ${className}`}>
      <Icon className="h-3 w-3" />
      {label}
    </span>
  )
}

export default async function ImportPage() {
  const [batches, stats] = await Promise.all([getImportBatches(), getStats()])

  return (
    <div className="container py-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold">Import</h1>
      </div>

      {/* Stats */}
      <div className="mb-8 grid gap-4 md:grid-cols-3">
        <Card className={stats.pending > 0 ? "border-yellow-500" : ""}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Venter på godkjenning</CardTitle>
            <Clock className={`h-4 w-4 ${stats.pending > 0 ? "text-yellow-500" : "text-muted-foreground"}`} />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.pending}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Importert</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.imported}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avvist</CardTitle>
            <XCircle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.rejected}</div>
          </CardContent>
        </Card>
      </div>

      {/* Upload Section */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Last opp resultatliste
          </CardTitle>
        </CardHeader>
        <CardContent>
          <UploadForm />
        </CardContent>
      </Card>

      {/* Import Batches List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileSpreadsheet className="h-5 w-5" />
            Resultatlister
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {batches.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="px-4 py-3 text-left text-sm font-medium">Navn</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Stevne</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Rader</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Utøvere</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Lastet opp</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Handlinger</th>
                  </tr>
                </thead>
                <tbody>
                  {batches.map((batch) => (
                    <tr key={batch.id} className="border-b last:border-0 hover:bg-muted/30">
                      <td className="px-4 py-3">
                        <div className="font-medium">{batch.name}</div>
                        {batch.original_filename && (
                          <div className="text-xs text-muted-foreground">{batch.original_filename}</div>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        {batch.meet_name && (
                          <div>
                            <div className="text-sm">{batch.meet_name}</div>
                            <div className="text-xs text-muted-foreground">
                              {batch.meet_city}{batch.meet_date && ` • ${new Date(batch.meet_date).toLocaleDateString("no-NO")}`}
                            </div>
                          </div>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <StatusBadge status={batch.status} />
                      </td>
                      <td className="px-4 py-3 text-sm">{batch.row_count ?? "-"}</td>
                      <td className="px-4 py-3">
                        {(batch.matched_athletes !== null || batch.unmatched_athletes !== null) && (
                          <div className="text-sm">
                            <span className="text-green-600">{batch.matched_athletes ?? 0}</span>
                            {" / "}
                            <span className={batch.unmatched_athletes ? "text-yellow-600" : ""}>
                              {batch.unmatched_athletes ?? 0}
                            </span>
                          </div>
                        )}
                      </td>
                      <td className="px-4 py-3 text-sm text-muted-foreground">
                        {batch.uploaded_at
                          ? new Date(batch.uploaded_at).toLocaleDateString("no-NO", {
                              day: "numeric",
                              month: "short",
                              hour: "2-digit",
                              minute: "2-digit",
                            })
                          : batch.created_at
                          ? new Date(batch.created_at).toLocaleDateString("no-NO", {
                              day: "numeric",
                              month: "short",
                            })
                          : "-"}
                      </td>
                      <td className="px-4 py-3">
                        <Link href={`/admin/import/${batch.id}`}>
                          <Button variant="outline" size="sm">
                            {batch.status === "pending" ? "Gjennomgå" : "Se detaljer"}
                          </Button>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="p-8 text-center text-muted-foreground">
              Ingen resultatlister lastet opp ennå
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
