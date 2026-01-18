"use client"

import { useRouter, useSearchParams } from "next/navigation"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import type { ReactNode } from "react"

interface AthleteTabsProps {
  defaultTab?: string
  children: {
    overview: ReactNode
    personalBests: ReactNode
    results: ReactNode
    progression: ReactNode
  }
}

export function AthleteTabs({ defaultTab = "overview", children }: AthleteTabsProps) {
  const router = useRouter()
  const searchParams = useSearchParams()

  const currentTab = searchParams.get("tab") || defaultTab

  const handleTabChange = (value: string) => {
    const params = new URLSearchParams(searchParams.toString())
    if (value === defaultTab) {
      params.delete("tab")
    } else {
      params.set("tab", value)
    }
    // Clear other filters when switching tabs
    params.delete("year")
    params.delete("event")
    params.delete("indoor")
    router.push(`?${params.toString()}`, { scroll: false })
  }

  return (
    <Tabs value={currentTab} onValueChange={handleTabChange} className="w-full">
      <TabsList className="mb-4 w-full justify-start overflow-x-auto">
        <TabsTrigger value="overview">Oversikt</TabsTrigger>
        <TabsTrigger value="personal-bests">Personlige rekorder</TabsTrigger>
        <TabsTrigger value="results">Resultater</TabsTrigger>
        <TabsTrigger value="progression">Progresjon</TabsTrigger>
      </TabsList>

      <TabsContent value="overview">{children.overview}</TabsContent>
      <TabsContent value="personal-bests">{children.personalBests}</TabsContent>
      <TabsContent value="results">{children.results}</TabsContent>
      <TabsContent value="progression">{children.progression}</TabsContent>
    </Tabs>
  )
}
