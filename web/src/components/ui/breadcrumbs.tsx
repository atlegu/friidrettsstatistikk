"use client"

import Link from "next/link"
import { ChevronRight, Home } from "lucide-react"

interface BreadcrumbItem {
  label: string
  href?: string
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[]
  showHome?: boolean
}

export function Breadcrumbs({ items, showHome = true }: BreadcrumbsProps) {
  const allItems = showHome
    ? [{ label: "Hjem", href: "/" }, ...items]
    : items

  return (
    <nav
      aria-label="Breadcrumb"
      className="flex items-center gap-1 text-[13px] text-[var(--text-muted)]"
    >
      {allItems.map((item, index) => {
        const isLast = index === allItems.length - 1
        const isHome = index === 0 && showHome

        return (
          <span key={index} className="flex items-center gap-1">
            {index > 0 && (
              <ChevronRight className="h-3 w-3 text-[var(--text-muted)]" />
            )}
            {isLast ? (
              <span className="text-[var(--text-primary)] font-medium">
                {item.label}
              </span>
            ) : item.href ? (
              <Link
                href={item.href}
                className="hover:text-[var(--accent-primary)] transition-colors"
              >
                {isHome ? (
                  <Home className="h-3.5 w-3.5" />
                ) : (
                  item.label
                )}
              </Link>
            ) : (
              <span>{item.label}</span>
            )}
          </span>
        )
      })}
    </nav>
  )
}
