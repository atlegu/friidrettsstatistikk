"use client"

import { useState, useMemo, useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { createClient } from "@/lib/supabase/client"
import {
  arrangorNavn,
  formaterResultat,
  kastkode,
  kjonnFraKlasse,
  klubbNoekkel,
  navnTreff,
  type ListeRad,
} from "@/lib/resultatliste"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  ArrowLeft,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Loader2,
  Search,
  UserPlus,
  Check,
  X,
} from "lucide-react"

type ParsedRow = ListeRad

type Athlete = {
  id: string
  full_name: string | null
  birth_year: number | null
  gender: string | null
  current_club_id: string | null
  clubs: { name: string } | null
}

type Event = {
  id: string
  name: string
  code: string | null
  category: string | null
  result_type: string | null
}

type Meet = {
  id: string
  name: string
  city: string | null
  start_date: string | null
}

type Season = {
  id: string
  year: number
}

type ImportBatch = {
  id: string
  name: string
  status: string | null
  raw_data: unknown
  validation_errors: unknown
  validation_warnings: unknown
  meet_name: string | null
  meet_city: string | null
  meet_date: string | null
  row_count: number | null
  matched_athletes: number | null
  unmatched_athletes: number | null
  admin_notes: string | null
  imported_at: string | null
}

type RowMapping = {
  athleteId: string | null
  eventId: string | null
  isNewAthlete: boolean
  newAthleteName?: string
  newAthleteGender?: string
}

type Club = {
  id: string
  name: string
}

type Props = {
  batch: ImportBatch
  athletes: Athlete[]
  events: Event[]
  meets: Meet[]
  seasons: Season[]
  clubs: Club[]
}

function fuzzyMatch(name: string, athletes: Athlete[], birthYear?: string): Athlete[] {
  const normalizedName = name.toLowerCase().trim().normalize("NFC")
  const parts = normalizedName.split(/\s+/).filter(p => p.length > 0)
  const yearNum = birthYear ? parseInt(birthYear) : null

  if (parts.length === 0) return []

  const matches = athletes
    .filter(a => {
      if (!a.full_name) return false
      const athleteName = a.full_name.toLowerCase().normalize("NFC")

      // Exact match
      if (athleteName === normalizedName) return true

      // All parts must be in the name
      return parts.every(part => athleteName.includes(part))
    })
    .map(a => {
      // Calculate match score
      let score = 1
      const athleteName = a.full_name!.toLowerCase().normalize("NFC")

      // Exact match gets highest score
      if (athleteName === normalizedName) score += 10

      // Birth year match
      if (a.birth_year && yearNum && a.birth_year === yearNum) score += 5

      return { ...a, _score: score }
    })
    .sort((a, b) => b._score - a._score)
    .slice(0, 5)

  return matches
}

export function ImportReview({ batch, athletes, events, meets, clubs }: Props) {
  const router = useRouter()
  const rows = (batch.raw_data as ParsedRow[]) || []

  // Debug logging (only on first render)
  // console.log("ImportReview loaded - athletes:", athletes.length, "events:", events.length, "rows:", rows.length)

  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // Row mappings - athleteId and eventId for each row
  // Automatisk kobling bare når den er entydig: samme fødselsår, samme kjønn
  // (fra klassen), og navnet likt eller med/uten mellomnavn («Helge Lorentzen»
  // = «Helge Andreas Lorentzen»). Eksakt navn går foran mellomnavn. Ellers
  // må raden kobles for hånd. Tidligere ble beste treff valgt selv med ulikt
  // fødselsår, og navn med mellomnavn ble ikke funnet (ny utøver = dublett).
  const [mappings, setMappings] = useState<Record<number, RowMapping>>(() => {
    const initial: Record<number, RowMapping> = {}
    const etterAar = new Map<number, Athlete[]>()
    athletes.forEach(a => {
      if (a.birth_year) etterAar.set(a.birth_year, [...(etterAar.get(a.birth_year) ?? []), a])
    })

    rows.forEach((row, idx) => {
      const aar = row.birth_year ? parseInt(row.birth_year) : NaN
      const kj = kjonnFraKlasse(row.event_class)
      const treff = (etterAar.get(aar) ?? [])
        .filter(a => !kj || !a.gender || a.gender === kj)
        .map(a => ({ a, t: navnTreff(row.name, a.full_name ?? "") }))
        .filter(x => x.t)
      const eksakte = treff.filter(x => x.t === "eksakt")
      const kandidater = eksakte.length ? eksakte : treff
      initial[idx] = {
        athleteId: kandidater.length === 1 ? kandidater[0].a.id : null,
        eventId: null,
        isNewAthlete: false,
        newAthleteGender: kj ?? undefined,
      }
    })
    return initial
  })

  // Selected meet for all rows
  const [selectedMeetId, setSelectedMeetId] = useState<string>("")
  const [isIndoor, setIsIndoor] = useState<boolean>(() => {
    // Default based on first row's indoor flag, or true if not set
    return rows[0]?.indoor ?? true
  })
  const [adminNotes, setAdminNotes] = useState(batch.admin_notes || "")

  // Auto-select meet based on file data, or default to "create new"
  useEffect(() => {
    if (!selectedMeetId && batch.meet_name) {
      // Samme navn og samme dato. Delstrengtreff uten dato valgte feil stevne:
      // «Skansemyren kastkarusell 13» inneholder «Skansemyren kastkarusell 1».
      const meetNameFromFile = batch.meet_name.toLowerCase().trim()
      const matchedMeet = meets.find(m =>
        m.name.toLowerCase().trim() === meetNameFromFile && m.start_date === batch.meet_date
      )
      if (matchedMeet) {
        setSelectedMeetId(matchedMeet.id)
      } else {
        // No match found - default to create new
        setSelectedMeetId("__create_new__")
      }
    }
  }, [meets, batch.meet_name, batch.meet_date, selectedMeetId])

  // Search state for athlete matching
  const [searchingRow, setSearchingRow] = useState<number | null>(null)
  const [athleteSearch, setAthleteSearch] = useState("")

  // Calculate stats
  const stats = useMemo(() => {
    const mapped = Object.values(mappings).filter(m => m.athleteId || m.isNewAthlete).length
    const newAthletes = Object.values(mappings).filter(m => m.isNewAthlete).length
    return {
      total: rows.length,
      mapped,
      unmapped: rows.length - mapped,
      newAthletes,
    }
  }, [mappings, rows.length])

  // Filter athletes for search
  const filteredAthletes = useMemo(() => {
    if (!athleteSearch.trim()) return []
    return fuzzyMatch(athleteSearch, athletes).slice(0, 10)
  }, [athleteSearch, athletes])

  const updateMapping = (rowIdx: number, update: Partial<RowMapping>) => {
    setMappings(prev => ({
      ...prev,
      [rowIdx]: { ...prev[rowIdx], ...update },
    }))
  }

  // Helper to match event from file to database
  const matchEventFromFile = (eventName: string, klasse?: string): string | null => {
    if (!eventName) return null
    // Kast med redskapsvekt og kastfemkamp: samme koder som kilden bruker
    const kode = kastkode(eventName, klasse)
    if (kode) return events.find(e => e.code === kode)?.id ?? null
    const normalized = eventName.toLowerCase().trim()
    // Also try without 'm' suffix for cases like "3000m" -> "3000"
    const withoutM = normalized.replace(/m$/, "")

    const matched = events.find(e => {
      const eName = e.name?.toLowerCase() || ""
      const eCode = e.code?.toLowerCase() || ""

      return (
        eName === normalized ||
        eCode === normalized ||
        eName.replace(/\s+/g, "") === normalized.replace(/\s+/g, "") ||
        // Match "3000m" to "3000 meter"
        eName.startsWith(withoutM + " ") ||
        eCode === normalized
      )
    })

    return matched?.id || null
  }

  const handleApprove = async () => {
    if (!selectedMeetId) {
      setError("Velg et stevne eller opprett nytt")
      return
    }

    const unmappedRows = rows.filter((_, idx) =>
      !mappings[idx]?.athleteId && !mappings[idx]?.isNewAthlete
    )
    if (unmappedRows.length > 0) {
      setError(`${unmappedRows.length} utøvere er ikke matchet. Match alle før godkjenning.`)
      return
    }

    // Check that all events can be matched
    const unmatchedEvents = rows
      .filter(r => r.event && !matchEventFromFile(r.event, r.event_class))
      .map(r => `${r.event} (${r.event_class ?? "?"})`)
    if (unmatchedEvents.length > 0) {
      const uniqueUnmatched = Array.from(new Set(unmatchedEvents))
      setError(`Kunne ikke matche øvelser: ${uniqueUnmatched.join(", ")}. Sjekk at øvelsene finnes i databasen.`)
      return
    }

    setIsProcessing(true)
    setError(null)

    try {
      const supabase = createClient()

      let actualMeetId = selectedMeetId
      let meetDate = batch.meet_date
      const utendors = !isIndoor

      // Nytt stevne fra fila. «Stevnested» i malen er anlegget, ikke byen, så
      // det går i venue og city står tom: når stevnet senere kommer fra
      // minfriidrettsstatistikk, finner importen posten igjen (navn + dato, eller
      // på de felles radene) og fyller inn sted og kilde-id selv.
      if (selectedMeetId === "__create_new__") {
        if (!batch.meet_name || !batch.meet_date) {
          throw new Error("Mangler stevnenavn eller dato fra fila")
        }
        const { data: finnes } = await supabase
          .from("meets")
          .select("id, start_date")
          .ilike("name", batch.meet_name)
          .eq("start_date", batch.meet_date)
          .limit(1)

        if (finnes?.length) {
          actualMeetId = finnes[0].id
          meetDate = finnes[0].start_date
        } else {
          const aar = Number(batch.meet_date.slice(0, 4)) + (!utendors && Number(batch.meet_date.slice(5, 7)) >= 10 ? 1 : 0)
          const { data: sesongRad } = await supabase
            .from("seasons").select("id").eq("year", aar).eq("indoor", !utendors).limit(1)
          const { data: newMeet, error: meetError } = await supabase
            .from("meets")
            .insert({
              name: batch.meet_name,
              city: "",
              venue: batch.meet_city || null,
              country: "NOR",
              start_date: batch.meet_date,
              end_date: batch.meet_date,
              indoor: !utendors,
              level: "local",
              season_id: sesongRad?.[0]?.id ?? null,
              organizer_name: arrangorNavn(rows.find(r => r.organizer)?.organizer),
            })
            .select("id, start_date")
            .single()

          if (meetError) throw new Error(`Kunne ikke opprette stevne: ${meetError.message}`)
          actualMeetId = newMeet.id
          meetDate = newMeet.start_date
        }
      } else {
        const selectedMeet = meets.find(m => m.id === selectedMeetId)
        meetDate = selectedMeet?.start_date || batch.meet_date
      }
      if (!meetDate) throw new Error("Stevnet mangler dato")

      // Sesong: utendørs og innendørs er hver sin, og innendørssesongen som
      // starter i oktober hører til året etter (samme regel som kildeimporten).
      const sesongAar = Number(meetDate.slice(0, 4)) + (!utendors && Number(meetDate.slice(5, 7)) >= 10 ? 1 : 0)
      const { data: sesongRader } = await supabase
        .from("seasons").select("id").eq("year", sesongAar).eq("indoor", !utendors).limit(1)
      const season = sesongRader?.[0]
      if (!season) {
        throw new Error(`Ingen ${utendors ? "utendørs" : "innendørs"}sesong funnet for ${sesongAar}`)
      }

      // Klubb: samme klubb når navnet er likt uten hensyn til rekkefølge og
      // vanlige forkortelser («IL Norna-Salhus» = «Norna-Salhus IL», «Gloppen
      // FIL» = «Gloppen Friidrettslag»). Utøverens egen klubb går foran når
      // den er den samme. Tidligere ble første klubb med navnet som delstreng
      // valgt, så «IL Fri» kunne bli en hvilken som helst «IL Friidrett».
      const klubbNavn = new Map(clubs.map(c => [c.id, c.name]))
      const etterNoekkel = new Map<string, string[]>()
      clubs.forEach(c => {
        const n = klubbNoekkel(c.name)
        etterNoekkel.set(n, [...(etterNoekkel.get(n) ?? []), c.id])
      })
      const nyeKlubber = new Map<string, string>()
      const finnKlubb = (radKlubb: string | undefined, athleteId: string | null): string | null => {
        const egen = athleteId ? athletes.find(a => a.id === athleteId)?.current_club_id ?? null : null
        const n = klubbNoekkel(radKlubb)
        if (!n) return egen
        if (egen && klubbNoekkel(klubbNavn.get(egen)) === n) return egen
        const like = etterNoekkel.get(n) ?? []
        if (like.length) return egen && like.includes(egen) ? egen : like[0]
        return nyeKlubber.get(n) ?? null
      }

      // Klubber som ikke finnes, opprettes (en ny klubb, eller et navn basen ikke kjenner)
      for (const row of rows) {
        const n = klubbNoekkel(row.club)
        if (!n || etterNoekkel.has(n) || nyeKlubber.has(n)) continue
        const { data: newClub, error: clubError } = await supabase
          .from("clubs").insert({ name: row.club!.trim() }).select("id").single()
        if (clubError) console.error("Club creation error:", clubError)
        else if (newClub) nyeKlubber.set(n, newClub.id)
      }

      // Nye utøvere
      const newAthleteIds: Record<number, string> = {}
      for (const [i, row] of rows.entries()) {
        const mapping = mappings[i]
        if (!mapping?.isNewAthlete) continue
        const nameParts = (mapping.newAthleteName || row.name).trim().split(/\s+/)
        const { data: newAthlete, error: athleteError } = await supabase
          .from("athletes")
          .insert({
            first_name: nameParts.slice(0, -1).join(" ") || nameParts[0],
            last_name: nameParts[nameParts.length - 1],
            gender: mapping.newAthleteGender || kjonnFraKlasse(row.event_class),
            birth_year: row.birth_year ? parseInt(row.birth_year) : null,
            current_club_id: finnKlubb(row.club, null),
          })
          .select("id")
          .single()
        if (athleteError) throw athleteError
        newAthleteIds[i] = newAthlete.id
      }

      // Rader som alt ligger i stevnet (samme utøver, øvelse, resultat og
      // plass) legges ikke inn på nytt - samme nøkkel som kildeimporten bruker.
      const finnes = new Set<string>()
      for (let fra = 0; ; fra += 1000) {
        const { data } = await supabase
          .from("results").select("athlete_id, event_id, performance, place")
          .eq("meet_id", actualMeetId).order("id").range(fra, fra + 999)
        data?.forEach(r => finnes.add(`${r.athlete_id}|${r.event_id}|${r.performance}|${r.place}`))
        if (!data || data.length < 1000) break
      }

      let hoppetOver = 0
      const results = rows.flatMap((row, idx) => {
        const mapping = mappings[idx]
        const athleteId = mapping.isNewAthlete ? newAthleteIds[idx] : mapping.athleteId
        const eventId = matchEventFromFile(row.event || "", row.event_class)
        if (!athleteId) throw new Error(`Mangler utøver-ID for rad ${idx + 1} (${row.name})`)
        if (!eventId) throw new Error(`Mangler øvelse-ID for rad ${idx + 1} (${row.event})`)
        const ev = events.find(e => e.id === eventId)
        const performance = formaterResultat(row.performance || "", ev?.code, ev?.result_type)
        const place = row.place ? parseInt(row.place) : null
        if (finnes.has(`${athleteId}|${eventId}|${performance}|${place}`)) {
          hoppetOver++
          return []
        }
        finnes.add(`${athleteId}|${eventId}|${performance}|${place}`)
        return [{
          athlete_id: athleteId,
          event_id: eventId,
          meet_id: actualMeetId,
          season_id: season.id,
          club_id: finnKlubb(row.club, athleteId),
          performance, // performance_value regnes ut av triggeren i basen
          date: meetDate!,
          place,
          wind: row.wind ? parseFloat(row.wind.replace(",", ".")) : null,
          status: "OK" as const,
          import_batch_id: batch.id,
        }]
      })

      if (results.length === 0 && hoppetOver === 0) {
        throw new Error("Ingen resultater å importere")
      }

      let insertedCount = 0
      for (let i = 0; i < results.length; i += 50) {
        const del = results.slice(i, i + 50)
        const { error: insertError } = await supabase.from("results").insert(del)
        if (insertError) {
          throw new Error(`Feil ved innsetting av resultat ${i + 1}: ${insertError.message}` +
            (insertedCount ? ` (${insertedCount} rader var alt lagt inn, merket med denne importen)` : ""))
        }
        insertedCount += del.length
      }

      // Utøvere uten klubb får klubben fra lista
      for (const [idx, row] of rows.entries()) {
        const mapping = mappings[idx]
        if (!row.club || !mapping?.athleteId || mapping.isNewAthlete) continue
        const a = athletes.find(x => x.id === mapping.athleteId)
        const klubb = finnKlubb(row.club, null)
        if (a && !a.current_club_id && klubb) {
          await supabase.from("athletes").update({ current_club_id: klubb }).eq("id", a.id)
          a.current_club_id = klubb
        }
      }

      // Update batch status
      const { error: updateError } = await supabase
        .from("import_batches")
        .update({
          status: "imported",
          imported_at: new Date().toISOString(),
          matched_athletes: stats.mapped - stats.newAthletes,
          unmatched_athletes: stats.newAthletes,
          admin_notes: adminNotes || null,
          row_count: insertedCount,
        })
        .eq("id", batch.id)

      if (updateError) {
        console.error("Update error:", updateError)
        throw new Error(`Feil ved oppdatering av import-status: ${updateError.message}`)
      }

      setIsProcessing(false)
      setSuccess(`Importerte ${insertedCount} resultater${hoppetOver ? ` (${hoppetOver} lå inne fra før og ble hoppet over)` : ""}. Omdirigerer …`)
      setTimeout(() => router.push("/admin/import"), 2000)

    } catch (err) {
      console.error("Import error:", err)
      setError(err instanceof Error ? err.message : "Feil ved import")
      setIsProcessing(false)
    }
  }

  const handleReject = async () => {
    if (!confirm("Er du sikker på at du vil avvise denne importen?")) return

    setIsProcessing(true)
    setError(null)

    try {
      const supabase = createClient()

      const { error: updateError } = await supabase
        .from("import_batches")
        .update({
          status: "rejected",
          admin_notes: adminNotes || null,
        })
        .eq("id", batch.id)

      if (updateError) {
        throw new Error(updateError.message)
      }

      router.push("/admin/import")
      router.refresh()

    } catch (err) {
      setError(err instanceof Error ? err.message : "Feil ved avvisning")
      setIsProcessing(false)
    }
  }

  // Already imported
  if (batch.status === "imported") {
    return (
      <div>
        <Link href="/admin/import" className="mb-4 inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" />
          Tilbake til import
        </Link>

        <Card className="border-green-500">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-green-700">
              <CheckCircle className="h-5 w-5" />
              Allerede importert
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">
              Denne batchen ble importert {batch.imported_at
                ? new Date(batch.imported_at).toLocaleDateString("no-NO", {
                    day: "numeric",
                    month: "long",
                    year: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })
                : "tidligere"}.
            </p>
            {batch.admin_notes && (
              <p className="mt-2 text-sm">
                <strong>Notater:</strong> {batch.admin_notes}
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div>
      <Link href="/admin/import" className="mb-4 inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft className="h-4 w-4" />
        Tilbake til import
      </Link>

      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{batch.name}</h1>
          {batch.meet_name && (
            <p className="text-muted-foreground">
              {batch.meet_name}
              {batch.meet_city && ` • ${batch.meet_city}`}
              {batch.meet_date && ` • ${new Date(batch.meet_date).toLocaleDateString("no-NO")}`}
            </p>
          )}
        </div>
      </div>

      {/* Stats */}
      <div className="mb-6 grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{stats.total}</div>
            <p className="text-sm text-muted-foreground">Totalt rader</p>
          </CardContent>
        </Card>
        <Card className={stats.mapped === stats.total ? "border-green-500" : ""}>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-green-600">{stats.mapped}</div>
            <p className="text-sm text-muted-foreground">Matchet</p>
          </CardContent>
        </Card>
        <Card className={stats.unmapped > 0 ? "border-yellow-500" : ""}>
          <CardContent className="pt-6">
            <div className={`text-2xl font-bold ${stats.unmapped > 0 ? "text-yellow-600" : ""}`}>
              {stats.unmapped}
            </div>
            <p className="text-sm text-muted-foreground">Umatchet</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-blue-600">{stats.newAthletes}</div>
            <p className="text-sm text-muted-foreground">Nye utøvere</p>
          </CardContent>
        </Card>
      </div>

      {/* Quick actions */}
      {stats.unmapped > 0 && (
        <div className="mb-6 flex gap-2">
          <Button
            variant="outline"
            onClick={() => {
              const newMappings = { ...mappings }
              rows.forEach((row, idx) => {
                if (!newMappings[idx]?.athleteId && !newMappings[idx]?.isNewAthlete) {
                  newMappings[idx] = {
                    ...newMappings[idx],
                    athleteId: null,
                    isNewAthlete: true,
                    newAthleteName: row.name,
                  }
                }
              })
              setMappings(newMappings)
            }}
          >
            <UserPlus className="mr-2 h-4 w-4" />
            Opprett alle {stats.unmapped} som nye utøvere
          </Button>
        </div>
      )}

      {/* Stevne og sesongtype */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Stevne og sesongtype</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="mb-1 block text-sm font-medium">Stevne *</label>
              <div className="space-y-2">
                <select
                  value={selectedMeetId}
                  onChange={(e) => setSelectedMeetId(e.target.value)}
                  className="w-full rounded-md border border-input bg-background px-3 py-2"
                >
                  <option value="">Velg eksisterende stevne...</option>
                  <option value="__create_new__">➕ Opprett nytt fra fil-data</option>
                  {meets.map(meet => (
                    <option key={meet.id} value={meet.id}>
                      {meet.name} ({meet.city}, {meet.start_date ? new Date(meet.start_date).toLocaleDateString("no-NO") : "?"})
                    </option>
                  ))}
                </select>
                {(batch.meet_name || batch.meet_city || batch.meet_date) && (
                  <div className="rounded-md bg-muted p-2 text-sm">
                    <span className="font-medium">Fra fil:</span> {batch.meet_name}{batch.meet_city ? `, ${batch.meet_city}` : ""}{batch.meet_date ? ` (${batch.meet_date})` : ""}
                  </div>
                )}
              </div>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium">Sesongtype</label>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setIsIndoor(true)}
                  className={`flex-1 rounded-md border px-3 py-2 text-sm font-medium transition-colors ${
                    isIndoor
                      ? "border-blue-500 bg-blue-50 text-blue-700"
                      : "border-input bg-background hover:bg-muted"
                  }`}
                >
                  Innendørs
                </button>
                <button
                  type="button"
                  onClick={() => setIsIndoor(false)}
                  className={`flex-1 rounded-md border px-3 py-2 text-sm font-medium transition-colors ${
                    !isIndoor
                      ? "border-green-500 bg-green-50 text-green-700"
                      : "border-input bg-background hover:bg-muted"
                  }`}
                >
                  Utendørs
                </button>
              </div>
              {rows[0]?.indoor !== undefined && (
                <p className="mt-1 text-xs text-muted-foreground">
                  Fra fil: {rows[0].indoor ? "Innendørs" : "Utendørs"}
                </p>
              )}
            </div>
          </div>

          {/* Øvelser fra fil */}
          <div className="mt-4">
            <label className="mb-1 block text-sm font-medium">Øvelser i filen</label>
            <div className="flex flex-wrap gap-2">
              {Array.from(new Set(rows.map(r => r.event).filter(Boolean))).map(event => (
                <span key={event} className="rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-800">
                  {event}
                </span>
              ))}
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              Øvelser matches automatisk mot databasen ved import
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Validation Warnings/Errors */}
      {(Array.isArray(batch.validation_errors) && batch.validation_errors.length > 0) ||
       (Array.isArray(batch.validation_warnings) && batch.validation_warnings.length > 0) ? (
        <Card className="mb-6 border-yellow-500">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-yellow-700">
              <AlertTriangle className="h-5 w-5" />
              Advarsler fra parsing
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-inside list-disc space-y-1 text-sm">
              {Array.isArray(batch.validation_errors) && batch.validation_errors.map((e, i) => (
                <li key={`e-${i}`} className="text-red-600">{String(e)}</li>
              ))}
              {Array.isArray(batch.validation_warnings) && batch.validation_warnings.map((w, i) => (
                <li key={`w-${i}`} className="text-yellow-600">{String(w)}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      ) : null}

      {/* Results Table */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Resultater</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="px-4 py-3 text-left text-sm font-medium">#</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Plass</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Navn (fra fil)</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Matchet utøver</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Klubb</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Resultat</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Vind</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row, idx) => {
                  const mapping = mappings[idx]
                  const matchedAthlete = athletes.find(a => a.id === mapping?.athleteId)
                  const isSearching = searchingRow === idx

                  return (
                    <tr key={idx} className="border-b last:border-0 hover:bg-muted/30">
                      <td className="px-4 py-3 text-sm text-muted-foreground">{idx + 1}</td>
                      <td className="px-4 py-3 text-sm">{row.place || "-"}</td>
                      <td className="px-4 py-3">
                        <div className="font-medium">{row.name}</div>
                        {row.birth_year && (
                          <div className="text-xs text-muted-foreground">f. {row.birth_year}</div>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        {isSearching ? (
                          <div className="space-y-2">
                            <div className="flex gap-2">
                              <Input
                                value={athleteSearch}
                                onChange={(e) => setAthleteSearch(e.target.value)}
                                placeholder="Søk utøver..."
                                className="h-8 text-sm"
                                autoFocus
                              />
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => {
                                  setSearchingRow(null)
                                  setAthleteSearch("")
                                }}
                              >
                                <X className="h-4 w-4" />
                              </Button>
                            </div>
                            {filteredAthletes.length > 0 && (
                              <div className="rounded border bg-background shadow-lg">
                                {filteredAthletes.map(a => (
                                  <button
                                    key={a.id}
                                    className="flex w-full items-center justify-between px-3 py-2 text-left text-sm hover:bg-muted"
                                    onClick={() => {
                                      updateMapping(idx, { athleteId: a.id, isNewAthlete: false })
                                      setSearchingRow(null)
                                      setAthleteSearch("")
                                    }}
                                  >
                                    <div>
                                      <div className="font-medium">{a.full_name}</div>
                                      <div className="text-xs text-muted-foreground">
                                        {a.birth_year && `f. ${a.birth_year}`}
                                        {a.clubs?.name && ` • ${a.clubs.name}`}
                                      </div>
                                    </div>
                                    <Check className="h-4 w-4 text-green-600" />
                                  </button>
                                ))}
                              </div>
                            )}
                            <Button
                              size="sm"
                              variant="outline"
                              className="w-full"
                              onClick={() => {
                                updateMapping(idx, {
                                  isNewAthlete: true,
                                  athleteId: null,
                                  newAthleteName: row.name,
                                })
                                setSearchingRow(null)
                                setAthleteSearch("")
                              }}
                            >
                              <UserPlus className="mr-2 h-4 w-4" />
                              Opprett ny utøver
                            </Button>
                          </div>
                        ) : mapping?.isNewAthlete ? (
                          <div className="flex items-center gap-2">
                            <span className="inline-flex items-center gap-1 rounded bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800">
                              <UserPlus className="h-3 w-3" />
                              Ny: {mapping.newAthleteName || row.name}
                            </span>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => {
                                setSearchingRow(idx)
                                setAthleteSearch(row.name)
                              }}
                            >
                              <Search className="h-4 w-4" />
                            </Button>
                          </div>
                        ) : matchedAthlete ? (
                          <div className="flex items-center gap-2">
                            <div>
                              <div className="flex items-center gap-1 text-sm font-medium text-green-700">
                                <CheckCircle className="h-3 w-3" />
                                {matchedAthlete.full_name}
                              </div>
                              {matchedAthlete.clubs?.name && (
                                <div className="text-xs text-muted-foreground">
                                  {matchedAthlete.clubs.name}
                                </div>
                              )}
                            </div>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => {
                                setSearchingRow(idx)
                                setAthleteSearch(row.name)
                              }}
                            >
                              <Search className="h-4 w-4" />
                            </Button>
                          </div>
                        ) : (
                          <Button
                            size="sm"
                            variant="outline"
                            className="text-yellow-600"
                            onClick={() => {
                              setSearchingRow(idx)
                              setAthleteSearch(row.name)
                            }}
                          >
                            <Search className="mr-2 h-4 w-4" />
                            Søk / Match
                          </Button>
                        )}
                      </td>
                      <td className="px-4 py-3 text-sm">{row.club || "-"}</td>
                      <td className="px-4 py-3 text-sm font-mono">
                        {row.performance || row.performance || "-"}
                      </td>
                      <td className="px-4 py-3 text-sm">{row.wind || "-"}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Admin Notes */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Admin-notater</CardTitle>
        </CardHeader>
        <CardContent>
          <textarea
            value={adminNotes}
            onChange={(e) => setAdminNotes(e.target.value)}
            placeholder="Eventuelle notater om denne importen..."
            className="w-full rounded-md border border-input bg-background px-3 py-2"
            rows={3}
          />
        </CardContent>
      </Card>

      {/* Error/Success Messages */}
      {error && (
        <div className="mb-6 flex items-center gap-2 rounded-lg bg-red-50 p-4 text-red-800">
          <AlertTriangle className="h-5 w-5 flex-shrink-0" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      {success && (
        <div className="mb-6 flex items-center gap-2 rounded-lg bg-green-50 p-4 text-green-800">
          <CheckCircle className="h-5 w-5 flex-shrink-0" />
          <p className="text-sm">{success}</p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex justify-end gap-4">
        <Button
          variant="outline"
          onClick={handleReject}
          disabled={isProcessing}
          className="text-red-600 hover:bg-red-50"
        >
          <XCircle className="mr-2 h-4 w-4" />
          Avvis import
        </Button>
        <Button
          onClick={handleApprove}
          disabled={isProcessing || stats.unmapped > 0 || !selectedMeetId}
        >
          {isProcessing ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Importerer...
            </>
          ) : (
            <>
              <CheckCircle className="mr-2 h-4 w-4" />
              Godkjenn og importer ({stats.mapped}/{stats.total} matchet)
            </>
          )}
        </Button>
      </div>
    </div>
  )
}
