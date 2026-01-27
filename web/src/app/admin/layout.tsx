import Link from "next/link"
import { createClient } from "@/lib/supabase/server"
import { redirect } from "next/navigation"
import { LogoutButton } from "@/components/admin/logout-button"

export const metadata = {
  title: {
    template: "%s | Admin - friidrettresultater.no",
    default: "Admin - friidrettresultater.no",
  },
}

async function getAdminUser() {
  const supabase = await createClient()

  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return null

  const { data: profile } = await supabase
    .from("user_profiles")
    .select("*")
    .eq("user_id", user.id)
    .single()

  if (!profile || !["admin", "super_admin"].includes(profile.role)) {
    return null
  }

  return { user, profile }
}

export default async function AdminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const adminData = await getAdminUser()

  // If on login page, don't show admin chrome
  // The middleware handles redirects, but we still need to render login without layout
  if (!adminData) {
    return <>{children}</>
  }

  const { profile } = adminData

  return (
    <div className="min-h-screen bg-muted/30">
      {/* Admin Header */}
      <header className="sticky top-0 z-50 border-b bg-background">
        <div className="container flex h-14 items-center justify-between">
          <div className="flex items-center gap-6">
            <Link href="/admin" className="font-semibold">
              friidrettresultater.no Admin
            </Link>
            <nav className="flex items-center gap-4 text-sm">
              <Link href="/admin" className="text-muted-foreground hover:text-foreground">
                Dashboard
              </Link>
              <Link href="/admin/import" className="text-muted-foreground hover:text-foreground">
                Import
              </Link>
              <Link href="/admin/athletes" className="text-muted-foreground hover:text-foreground">
                Utøvere
              </Link>
              <Link href="/admin/meets" className="text-muted-foreground hover:text-foreground">
                Stevner
              </Link>
              {profile.role === "super_admin" && (
                <Link href="/admin/users" className="text-muted-foreground hover:text-foreground">
                  Brukere
                </Link>
              )}
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">
              {profile.display_name || profile.email}
            </span>
            <Link href="/" className="text-sm text-muted-foreground hover:text-foreground">
              Tilbake til nettstedet
            </Link>
            <LogoutButton />
          </div>
        </div>
      </header>

      {/* Admin Content */}
      <main>{children}</main>
    </div>
  )
}
