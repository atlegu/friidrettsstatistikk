"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Search } from "lucide-react"
import { SokeFelt } from "@/components/ui/soke-felt"

/**
 * Søkefeltet på forsiden.
 *
 * Det vanligste en besøkende vil, er å slå opp en person. I toppmenyen ligger
 * søket bak et ikon som må klikkes fram; her står det åpent og er det første
 * man ser.
 */
export function ForsideSok() {
  const [sok, setSok] = useState("")
  const router = useRouter()

  function send(e: React.FormEvent) {
    e.preventDefault()
    const q = sok.trim()
    if (q) router.push(`/utover?search=${encodeURIComponent(q)}`)
  }

  return (
    <form onSubmit={send} className="mx-auto w-full max-w-xl">
      <label htmlFor="forsidesok" className="sr-only">
        Søk etter utøver
      </label>
      <div className="relative">
        <Search
          aria-hidden
          className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-[var(--nfif-navy-blekk-svak)]"
        />
        <SokeFelt
          id="forsidesok"
          navn="sok"
          plassholder="Søk etter utøver …"
          onEndret={setSok}
          krysselasse="right-24 text-white"
          klasse="h-14 w-full rounded-xl border border-white/20 bg-white/10 pl-12 pr-32
                  text-[15px] text-white placeholder:text-[var(--nfif-navy-blekk-svak)]
                  outline-none backdrop-blur-sm transition-colors
                  focus:border-white/40 focus:bg-white/15"
        />
        <button
          type="submit"
          className="absolute right-2 top-1/2 h-10 -translate-y-1/2 rounded-lg
                     bg-[var(--nfif-rod)] px-5 text-[14px] font-bold text-white
                     transition-opacity hover:opacity-90"
        >
          Søk
        </button>
      </div>
    </form>
  )
}
