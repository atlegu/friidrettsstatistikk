"use client"

import { useState } from "react"
import { cn } from "@/lib/utils"

interface CopyLinkProps {
  className?: string
}

export function CopyLink({ className }: CopyLinkProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error("Failed to copy:", err)
    }
  }

  return (
    <button
      onClick={handleCopy}
      className={cn(
        // Brukes på den mørke utøvertoppen
        "inline-flex items-center justify-center gap-1.5 whitespace-nowrap px-4 py-2",
        "text-[13px] font-medium rounded-lg border border-white/25 bg-white/10",
        "text-white hover:bg-white/20 transition-colors",
        className
      )}
    >
      {copied ? (
        <>
          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
          Kopiert!
        </>
      ) : (
        <>
          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
          Del lenke
        </>
      )}
    </button>
  )
}
