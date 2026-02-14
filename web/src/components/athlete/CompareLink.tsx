import Link from "next/link"
import { ArrowRightLeft } from "lucide-react"

export function CompareLink({ athleteId }: { athleteId: string }) {
  return (
    <Link
      href={`/sammenlign?id1=${athleteId}`}
      className="chip inline-flex items-center gap-1"
    >
      <ArrowRightLeft className="h-3 w-3" />
      Sammenlign
    </Link>
  )
}
