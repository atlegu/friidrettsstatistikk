import Link from "next/link"
import { ArrowRightLeft } from "lucide-react"

/** Vises på den mørke utøvertoppen, så fargene er satt for marineblå flate. */
export function CompareLink({ athleteId }: { athleteId: string }) {
  return (
    <Link
      href={`/sammenlign?id1=${athleteId}`}
      className="inline-flex items-center justify-center gap-1.5 whitespace-nowrap rounded-lg
                 border border-white/25 bg-white/10 px-4 py-2 text-[13px] font-medium
                 text-white transition-colors hover:bg-white/20"
    >
      <ArrowRightLeft className="h-3.5 w-3.5" />
      Sammenlign
    </Link>
  )
}
