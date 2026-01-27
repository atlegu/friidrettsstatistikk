"use client"

import { useState } from "react"
import Link from "next/link"
import { ChevronDown, ChevronRight } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  EVENT_CATEGORIES,
  getCategoryEvents,
  getEventDisplayName,
} from "@/lib/event-config"

interface Event {
  id: string
  name: string
  code: string
  result_count?: number
}

interface EventSelectorProps {
  events: Event[]
  selectedEventId?: string
  gender: "M" | "F"
  baseUrl: string  // Base URL with current params (without event param)
}

export function EventSelector({ events, selectedEventId, gender, baseUrl }: EventSelectorProps) {
  // Build URL for an event
  const buildEventUrl = (eventId: string) => {
    const url = new URL(baseUrl, "http://localhost")  // Need a base for URL parsing
    url.searchParams.set("event", eventId)
    return `${url.pathname}?${url.searchParams.toString()}`
  }

  const [showAllEvents, setShowAllEvents] = useState(false)
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(() => {
    // Initialize with default expanded categories
    const expanded = new Set<string>()
    EVENT_CATEGORIES.forEach(cat => {
      if (cat.defaultExpanded) expanded.add(cat.id)
    })
    return expanded
  })

  // Create a map of event codes to event objects
  const eventsByCode = new Map<string, Event>()
  events.forEach(e => {
    if (e.code) eventsByCode.set(e.code, e)
  })

  // Toggle category expansion
  const toggleCategory = (categoryId: string) => {
    setExpandedCategories(prev => {
      const next = new Set(prev)
      if (next.has(categoryId)) {
        next.delete(categoryId)
      } else {
        next.add(categoryId)
      }
      return next
    })
  }

  // Get events that don't belong to any category (for "Other" section)
  const categorizedCodes = new Set<string>()
  EVENT_CATEGORIES.forEach(cat => {
    getCategoryEvents(cat, gender).forEach(code => categorizedCodes.add(code))
  })

  // Other events are shown when "show all" is enabled
  const otherEvents = showAllEvents
    ? events.filter(e => e.code && !categorizedCodes.has(e.code))
    : []

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm flex items-center justify-between">
          <span>Øvelse</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-1">
        {/* Main categories */}
        {EVENT_CATEGORIES.map(category => {
          const categoryEventCodes = getCategoryEvents(category, gender)
          const categoryEvents = categoryEventCodes
            .map(code => eventsByCode.get(code))
            .filter((e): e is Event => e !== undefined)

          if (categoryEvents.length === 0) return null

          const isExpanded = expandedCategories.has(category.id)
          const hasSelectedEvent = categoryEvents.some(e => e.id === selectedEventId)

          return (
            <div key={category.id} className="space-y-0.5">
              <button
                onClick={() => toggleCategory(category.id)}
                className={`w-full flex items-center gap-1 rounded px-2 py-1.5 text-sm font-medium hover:bg-muted ${
                  hasSelectedEvent ? "text-primary" : ""
                }`}
              >
                {isExpanded ? (
                  <ChevronDown className="h-3.5 w-3.5" />
                ) : (
                  <ChevronRight className="h-3.5 w-3.5" />
                )}
                {category.name}
              </button>

              {isExpanded && (
                <div className="ml-4 space-y-0.5">
                  {categoryEvents.map(event => (
                    <Link
                      key={event.id}
                      href={buildEventUrl(event.id)}
                      className={`block rounded px-2 py-1 text-sm ${
                        selectedEventId === event.id
                          ? "bg-primary text-primary-foreground"
                          : "hover:bg-muted"
                      }`}
                    >
                      {getEventDisplayName(event.code) || event.name}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          )
        })}

        {/* Other events (uncategorized) */}
        {otherEvents.length > 0 && (
          <div className="space-y-0.5 pt-2 border-t">
            <button
              onClick={() => toggleCategory("other")}
              className="w-full flex items-center gap-1 rounded px-2 py-1.5 text-sm font-medium hover:bg-muted"
            >
              {expandedCategories.has("other") ? (
                <ChevronDown className="h-3.5 w-3.5" />
              ) : (
                <ChevronRight className="h-3.5 w-3.5" />
              )}
              Andre øvelser ({otherEvents.length})
            </button>

            {expandedCategories.has("other") && (
              <div className="ml-4 space-y-0.5 max-h-[200px] overflow-y-auto">
                {otherEvents.map(event => (
                  <Link
                    key={event.id}
                    href={buildEventUrl(event.id)}
                    className={`block rounded px-2 py-1 text-sm ${
                      selectedEventId === event.id
                        ? "bg-primary text-primary-foreground"
                        : "hover:bg-muted"
                    }`}
                  >
                    {getEventDisplayName(event.code) || event.name}
                  </Link>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Show all events toggle */}
        <div className="pt-2 border-t">
          <button
            onClick={() => {
              setShowAllEvents(!showAllEvents)
              if (!showAllEvents) {
                // Auto-expand "other" category when showing all events
                setExpandedCategories(prev => new Set([...prev, "other"]))
              }
            }}
            className="w-full text-xs text-muted-foreground hover:text-foreground py-1"
          >
            {showAllEvents ? "← Vis kun hovedøvelser" : "Vis alle øvelser →"}
          </button>
        </div>
      </CardContent>
    </Card>
  )
}
