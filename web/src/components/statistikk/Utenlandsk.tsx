/**
 * Stjerne bak navnet på utenlandske statsborgere i norske lister. De står i
 * norsk statistikk bare når de representerer en norsk klubb, og merkes da
 * med * (samme praksis som Kondis' statistikk).
 */
export function Utenlandsk({ nasjon }: { nasjon: string | null | undefined }) {
  if (!nasjon || nasjon === "NOR") return null
  return (
    <span className="ml-0.5 text-muted-foreground" title={`Utenlandsk statsborger (${nasjon}) i norsk klubb`}>
      *
    </span>
  )
}
