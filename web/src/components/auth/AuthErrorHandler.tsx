"use client"

import { useEffect, useState } from "react"
import { useRouter, usePathname } from "next/navigation"

export function AuthErrorHandler() {
  const router = useRouter()
  const pathname = usePathname()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted) return

    // Only check on non-login pages
    if (pathname === "/admin/login") return

    const hash = window.location.hash
    if (hash.includes("error=")) {
      // Redirect to login page with the error hash
      router.replace(`/admin/login${hash}`)
    }
  }, [mounted, pathname, router])

  return null
}
