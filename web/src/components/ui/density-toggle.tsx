"use client"

import { useState, useEffect, createContext, useContext } from "react"
import { cn } from "@/lib/utils"

type Density = "comfortable" | "compact" | "ultra"

interface DensityContextValue {
  density: Density
  setDensity: (density: Density) => void
}

const DensityContext = createContext<DensityContextValue>({
  density: "compact",
  setDensity: () => {},
})

export function useDensity() {
  return useContext(DensityContext)
}

interface DensityProviderProps {
  children: React.ReactNode
}

export function DensityProvider({ children }: DensityProviderProps) {
  const [density, setDensity] = useState<Density>("compact")

  useEffect(() => {
    const saved = localStorage.getItem("density") as Density | null
    if (saved && ["comfortable", "compact", "ultra"].includes(saved)) {
      setDensity(saved)
    }
  }, [])

  useEffect(() => {
    localStorage.setItem("density", density)
    document.documentElement.setAttribute("data-density", density)
  }, [density])

  return (
    <DensityContext.Provider value={{ density, setDensity }}>
      {children}
    </DensityContext.Provider>
  )
}

interface DensityToggleProps {
  className?: string
}

export function DensityToggle({ className }: DensityToggleProps) {
  const { density, setDensity } = useDensity()

  const options: { value: Density; label: string; hideOnMobile?: boolean }[] = [
    { value: "comfortable", label: "Romslig" },
    { value: "compact", label: "Kompakt" },
    { value: "ultra", label: "Ultra", hideOnMobile: true },
  ]

  return (
    <div className={cn("flex items-center gap-1 rounded border bg-[var(--bg-muted)] p-0.5", className)}>
      {options.map((option) => (
        <button
          key={option.value}
          onClick={() => setDensity(option.value)}
          className={cn(
            "px-2 py-1 text-[12px] font-medium rounded transition-colors",
            option.hideOnMobile && "hidden md:block",
            density === option.value
              ? "bg-[var(--bg-surface)] text-[var(--text-primary)] shadow-sm"
              : "text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
          )}
        >
          {option.label}
        </button>
      ))}
    </div>
  )
}
