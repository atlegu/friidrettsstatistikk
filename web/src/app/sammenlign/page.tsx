import { Suspense } from "react"
import { Loader2 } from "lucide-react"
import CompareContent from "./compare-content"

export default async function ComparePage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>
}) {
  const params = await searchParams

  const id1 = typeof params.id1 === "string" ? params.id1 : null
  const id2 = typeof params.id2 === "string" ? params.id2 : null
  const event = typeof params.event === "string" ? params.event : null
  const tab = typeof params.tab === "string" ? params.tab : null

  return (
    <Suspense
      fallback={
        <div className="container flex min-h-[50vh] items-center justify-center py-6">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      }
    >
      <CompareContent
        initialId1={id1}
        initialId2={id2}
        initialEvent={event}
        initialTab={tab}
      />
    </Suspense>
  )
}
