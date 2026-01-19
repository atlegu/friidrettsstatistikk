"use client"

import { DensityProvider } from "@/components/ui/density-toggle"

interface ProvidersProps {
  children: React.ReactNode
}

export function Providers({ children }: ProvidersProps) {
  return (
    <DensityProvider>
      {children}
    </DensityProvider>
  )
}
