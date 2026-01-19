"use client"

import { cn } from "@/lib/utils"

interface FilterChip {
  label: string
  value: string
  active?: boolean
}

interface FilterChipsProps {
  chips: FilterChip[]
  onSelect: (value: string) => void
  className?: string
}

export function FilterChips({ chips, onSelect, className }: FilterChipsProps) {
  return (
    <div className={cn("flex flex-wrap gap-1.5", className)}>
      {chips.map((chip) => (
        <button
          key={chip.value}
          onClick={() => onSelect(chip.value)}
          className={cn(
            "chip",
            chip.active && "chip-active"
          )}
        >
          {chip.label}
        </button>
      ))}
    </div>
  )
}

interface FilterChipGroupProps {
  label?: string
  children: React.ReactNode
  className?: string
}

export function FilterChipGroup({ label, children, className }: FilterChipGroupProps) {
  return (
    <div className={cn("flex items-center gap-2", className)}>
      {label && (
        <span className="text-[12px] font-medium text-[var(--text-muted)]">
          {label}:
        </span>
      )}
      <div className="flex flex-wrap gap-1.5">
        {children}
      </div>
    </div>
  )
}

interface SingleFilterChipProps {
  label: string
  active?: boolean
  onClick: () => void
  className?: string
}

export function SingleFilterChip({ label, active, onClick, className }: SingleFilterChipProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "chip",
        active && "chip-active",
        className
      )}
    >
      {label}
    </button>
  )
}
