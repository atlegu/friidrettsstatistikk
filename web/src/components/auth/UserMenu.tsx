"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { User, LogOut, Settings, Crown } from "lucide-react"
import { useAuth } from "./AuthProvider"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export function UserMenu() {
  const { user, profile, loading, isPremium, signOut } = useAuth()
  const router = useRouter()

  if (loading) {
    return (
      <Button variant="ghost" size="sm" disabled className="ml-2">
        <span className="h-4 w-4 animate-pulse rounded-full bg-muted" />
      </Button>
    )
  }

  if (!user) {
    return (
      <Button variant="ghost" size="sm" className="ml-2" asChild>
        <Link href="/logg-inn">Logg inn</Link>
      </Button>
    )
  }

  const displayName = profile?.full_name || user.email?.split("@")[0] || "Bruker"
  const initials = displayName
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2)

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="sm" className="ml-2 gap-2">
          {profile?.avatar_url ? (
            <img
              src={profile.avatar_url}
              alt={displayName}
              className="h-6 w-6 rounded-full"
            />
          ) : (
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-xs text-primary-foreground">
              {initials}
            </div>
          )}
          <span className="hidden md:inline">{displayName}</span>
          {isPremium && <Crown className="h-3 w-3 text-yellow-500" />}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel>
          <div className="flex flex-col">
            <span>{displayName}</span>
            <span className="text-xs font-normal text-muted-foreground">
              {user.email}
            </span>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />

        {isPremium ? (
          <DropdownMenuItem className="text-yellow-600" disabled>
            <Crown className="mr-2 h-4 w-4" />
            Premium-medlem
          </DropdownMenuItem>
        ) : (
          <DropdownMenuItem asChild>
            <Link href="/abonnement" className="cursor-pointer">
              <Crown className="mr-2 h-4 w-4" />
              Oppgrader til Premium
            </Link>
          </DropdownMenuItem>
        )}

        <DropdownMenuSeparator />

        <DropdownMenuItem asChild>
          <Link href="/min-side" className="cursor-pointer">
            <User className="mr-2 h-4 w-4" />
            Min side
          </Link>
        </DropdownMenuItem>

        <DropdownMenuItem asChild>
          <Link href="/min-side/innstillinger" className="cursor-pointer">
            <Settings className="mr-2 h-4 w-4" />
            Innstillinger
          </Link>
        </DropdownMenuItem>

        <DropdownMenuSeparator />

        <DropdownMenuItem
          onClick={async () => {
            await signOut()
            router.push("/")
            router.refresh()
          }}
          className="cursor-pointer text-red-600 focus:text-red-600"
        >
          <LogOut className="mr-2 h-4 w-4" />
          Logg ut
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
