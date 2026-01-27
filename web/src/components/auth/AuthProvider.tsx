"use client"

import { createContext, useContext, useEffect, useState } from "react"
import { createClient } from "@/lib/supabase/client"
import type { User } from "@supabase/supabase-js"

interface Profile {
  id: string
  email: string | null
  full_name: string | null
  avatar_url: string | null
  subscription_tier: "free" | "premium"
  subscription_expires_at: string | null
  is_admin?: boolean
}

interface AuthContextType {
  user: User | null
  profile: Profile | null
  loading: boolean
  isPremium: boolean
  isAdmin: boolean
  signOut: () => Promise<void>
  refreshProfile: () => Promise<void>
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  profile: null,
  loading: true,
  isPremium: false,
  isAdmin: false,
  signOut: async () => {},
  refreshProfile: async () => {},
})

export function useAuth() {
  return useContext(AuthContext)
}

interface AuthProviderProps {
  children: React.ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [profile, setProfile] = useState<Profile | null>(null)
  const [loading, setLoading] = useState(true)
  const supabase = createClient()

  const fetchProfile = async (userId: string) => {
    const { data } = await supabase
      .from("profiles")
      .select("*")
      .eq("id", userId)
      .single()

    if (data) {
      setProfile(data as Profile)
    }
  }

  const refreshProfile = async () => {
    if (user) {
      await fetchProfile(user.id)
    }
  }

  useEffect(() => {
    // Get initial session with error handling for AbortError
    const initSession = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession()
        setUser(session?.user ?? null)
        if (session?.user) {
          await fetchProfile(session.user.id)
        }
      } catch (error) {
        // Ignore AbortError - this happens when the lock times out
        if (error instanceof Error && error.name === 'AbortError') {
          console.warn('Auth session fetch aborted, will retry on next navigation')
        } else {
          console.error('Error fetching session:', error)
        }
      } finally {
        setLoading(false)
      }
    }

    initSession()

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      setUser(session?.user ?? null)

      if (session?.user) {
        try {
          await fetchProfile(session.user.id)
        } catch (error) {
          console.error('Error fetching profile:', error)
        }
      } else {
        setProfile(null)
      }

      setLoading(false)
    })

    return () => subscription.unsubscribe()
  }, [])

  const signOut = async () => {
    await supabase.auth.signOut()
    setUser(null)
    setProfile(null)
  }

  const isAdmin = profile?.is_admin === true

  // Admins have premium access, otherwise check subscription
  const isPremium =
    isAdmin ||
    (profile?.subscription_tier === "premium" &&
      (!profile.subscription_expires_at ||
        new Date(profile.subscription_expires_at) > new Date()))

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        loading,
        isPremium,
        isAdmin,
        signOut,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
