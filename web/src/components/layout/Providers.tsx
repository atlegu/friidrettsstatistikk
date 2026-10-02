"use client"

import { AuthProvider } from "@/components/auth/AuthProvider"

interface ProvidersProps {
  children: React.ReactNode
}

export function Providers({ children }: ProvidersProps) {
  return (
    <AuthProvider>
        {children}
    </AuthProvider>
  )
}
