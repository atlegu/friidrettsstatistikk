"use client"

import { DensityProvider } from "@/components/ui/density-toggle"
import { AuthProvider } from "@/components/auth/AuthProvider"

interface ProvidersProps {
  children: React.ReactNode
}

export function Providers({ children }: ProvidersProps) {
  return (
    <AuthProvider>
      <DensityProvider>
        {children}
      </DensityProvider>
    </AuthProvider>
  )
}
