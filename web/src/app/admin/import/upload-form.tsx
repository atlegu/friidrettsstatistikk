"use client"

import { useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { createClient } from "@/lib/supabase/client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Upload, FileSpreadsheet, Loader2, AlertCircle, CheckCircle } from "lucide-react"
import * as XLSX from "xlsx"

// Convert Excel serial date to YYYY-MM-DD string
function excelDateToString(serial: number | string): string | null {
  if (typeof serial === "string") {
    // Already a string, check if it looks like a date
    if (serial.match(/^\d{4}-\d{2}-\d{2}$/)) return serial
    if (serial.match(/^\d{1,2}\.\d{1,2}\.\d{4}$/)) {
      // Norwegian format DD.MM.YYYY
      const [d, m, y] = serial.split(".")
      return `${y}-${m.padStart(2, "0")}-${d.padStart(2, "0")}`
    }
    if (serial.match(/^\d{1,2}\/\d{1,2}\/\d{4}$/)) {
      // US format MM/DD/YYYY
      const [m, d, y] = serial.split("/")
      return `${y}-${m.padStart(2, "0")}-${d.padStart(2, "0")}`
    }
    return null
  }

  if (typeof serial !== "number" || isNaN(serial)) return null

  // Excel serial date: days since 1900-01-01 (with a bug for 1900 leap year)
  const excelEpoch = new Date(1899, 11, 30) // Dec 30, 1899
  const date = new Date(excelEpoch.getTime() + serial * 24 * 60 * 60 * 1000)

  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, "0")
  const day = String(date.getDate()).padStart(2, "0")

  return `${year}-${month}-${day}`
}

type ParsedRow = {
  place?: string
  bib?: string
  name: string
  birth_year?: string
  club?: string
  performance?: string
  wind?: string
  event?: string
  event_class?: string
  round?: string
  indoor?: boolean
}

type ParsedMetadata = {
  meetName?: string
  meetCity?: string
  meetDateFrom?: string
  meetDateTo?: string
  organizer?: string
  outdoor?: boolean
  currentEvent?: string
  currentClass?: string
}

type ValidationResult = {
  rows: ParsedRow[]
  metadata: ParsedMetadata
  errors: string[]
  warnings: string[]
}

export function UploadForm() {
  const router = useRouter()
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // Form fields
  const [file, setFile] = useState<File | null>(null)
  const [meetName, setMeetName] = useState("")
  const [meetCity, setMeetCity] = useState("")
  const [meetDate, setMeetDate] = useState("")
  const [batchName, setBatchName] = useState("")

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      handleFileSelect(droppedFile)
    }
  }, [])

  const handleFileSelect = (selectedFile: File) => {
    setError(null)
    setSuccess(null)

    const validExtensions = [".csv", ".xlsx", ".xls", ".txt"]
    const extension = selectedFile.name.toLowerCase().slice(selectedFile.name.lastIndexOf("."))

    if (!validExtensions.includes(extension)) {
      setError("Ugyldig filtype. Bruk CSV, Excel (.xlsx/.xls) eller tekstfil (.txt)")
      return
    }

    setFile(selectedFile)

    // Auto-fill batch name from filename
    if (!batchName) {
      setBatchName(selectedFile.name.replace(/\.[^/.]+$/, ""))
    }
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      handleFileSelect(selectedFile)
    }
  }

  // Parse Excel file using xlsx library
  const parseExcel = async (file: File): Promise<ValidationResult> => {
    const rows: ParsedRow[] = []
    const errors: string[] = []
    const warnings: string[] = []
    const metadata: ParsedMetadata = {}

    try {
      const arrayBuffer = await file.arrayBuffer()
      const workbook = XLSX.read(arrayBuffer, { type: "array" })
      const sheetName = workbook.SheetNames[0]
      const sheet = workbook.Sheets[sheetName]
      const data = XLSX.utils.sheet_to_json<string[]>(sheet, { header: 1 })

      let currentEvent = ""
      let currentClass = ""
      let currentWind = ""

      for (let i = 0; i < data.length; i++) {
        const row = data[i]
        if (!row || row.length === 0) continue

        const firstCell = String(row[0] || "").trim()
        const secondCell = String(row[1] || "").trim()

        // Parse header metadata (friidrett.no mal format)
        if (firstCell === "Stevne:") {
          metadata.meetName = secondCell
          continue
        }
        if (firstCell === "Stevnested:") {
          metadata.meetCity = secondCell
          continue
        }
        if (firstCell === "Stevnedato:") {
          // Convert Excel serial date if needed
          const dateFrom = row[1]
          const dateTo = row[2]
          metadata.meetDateFrom = excelDateToString(dateFrom) || undefined
          metadata.meetDateTo = excelDateToString(dateTo) || undefined
          continue
        }
        if (firstCell === "Arrangør:") {
          metadata.organizer = secondCell
          continue
        }
        if (firstCell === "Utendørs:") {
          metadata.outdoor = secondCell.toUpperCase() === "J"
          continue
        }

        // Skip other header rows
        if (firstCell.endsWith(":") && !firstCell.match(/^\d/)) {
          continue
        }

        // Detect class and event row (e.g., "Jenter 14", "100m")
        if (firstCell && secondCell && !firstCell.match(/^\d/) &&
            (secondCell.match(/^\d+m$/) || secondCell.match(/^(kule|diskos|slegge|spyd|høyde|stav|lengde|tresteg)/i))) {
          currentClass = firstCell
          currentEvent = secondCell
          continue
        }

        // Detect Heat/Finale with wind
        if (firstCell === "Heat:" || firstCell === "Finale:") {
          currentWind = String(row[3] || "").trim()
          continue
        }

        // Skip template placeholder rows
        if (firstCell.startsWith("<") || secondCell.startsWith("<")) {
          continue
        }

        // Parse result rows - check if first cell is a number (placement)
        const place = parseInt(firstCell)
        if (!isNaN(place) && place > 0 && place < 1000) {
          // Detect column structure:
          // With bib: [place, bib, name, birthYear, club, result, wind]
          // Without bib: [place, name, birthYear, club, result, wind]
          // Check if column 1 looks like a name (not a number) and column 2 looks like a birth year (4-digit number)
          const col1 = String(row[1] || "").trim()
          const col2 = String(row[2] || "").trim()
          const col1IsName = isNaN(parseInt(col1)) || col1.length > 4
          const col2IsBirthYear = !isNaN(parseInt(col2)) && col2.length === 4

          // If col1 is a name and col2 is a birth year, there's no bib column
          const hasBibColumn = !(col1IsName && col2IsBirthYear)
          const offset = hasBibColumn ? 0 : -1

          const name = String(row[2 + offset] || "").trim()
          if (!name || name.startsWith("<")) continue

          const parsedRow: ParsedRow = {
            place: String(place),
            bib: hasBibColumn ? String(row[1] || "").trim() : "",
            name: name,
            birth_year: String(row[3 + offset] || "").trim(),
            club: String(row[4 + offset] || "").trim(),
            performance: String(row[5 + offset] || "").trim(),
            wind: String(row[6 + offset] || "").trim() || currentWind,
            event: currentEvent,
            event_class: currentClass,
          }

          // Validate
          if (!parsedRow.name) {
            warnings.push(`Rad ${i + 1}: Mangler navn`)
            continue
          }

          rows.push(parsedRow)
        }
      }

      if (rows.length === 0) {
        errors.push("Ingen gyldige resultatrader funnet i filen")
      }

      // Set indoor flag on all rows based on metadata
      // outdoor = true means NOT indoor, so indoor = !outdoor
      // Default to indoor if not specified (most imports are from indoor season)
      const isIndoor = metadata.outdoor === undefined ? true : !metadata.outdoor
      rows.forEach(row => {
        row.indoor = isIndoor
      })

    } catch (err) {
      errors.push(`Feil ved lesing av Excel-fil: ${err instanceof Error ? err.message : "Ukjent feil"}`)
    }

    return { rows, metadata, errors, warnings }
  }

  // Parse CSV/text file
  const parseCSV = (content: string): ValidationResult => {
    const lines = content.split("\n").filter(line => line.trim())
    const rows: ParsedRow[] = []
    const errors: string[] = []
    const warnings: string[] = []
    const metadata: ParsedMetadata = {}

    // Try to detect header row
    const firstLine = lines[0]?.toLowerCase() || ""
    const hasHeader = firstLine.includes("navn") || firstLine.includes("name") ||
                      firstLine.includes("plass") || firstLine.includes("place") ||
                      firstLine.includes("resultat") || firstLine.includes("result")

    const dataLines = hasHeader ? lines.slice(1) : lines

    // Detect delimiter
    const delimiter = firstLine.includes(";") ? ";" :
                      firstLine.includes("\t") ? "\t" : ","

    for (let i = 0; i < dataLines.length; i++) {
      const line = dataLines[i]
      if (!line.trim()) continue

      const parts = line.split(delimiter).map(p => p.trim().replace(/^"|"$/g, ""))

      if (parts.length < 2) {
        warnings.push(`Rad ${i + 1}: For få kolonner`)
        continue
      }

      const row: ParsedRow = { name: "" }

      // Try to detect format based on first column
      const firstPartIsNumber = /^\d+\.?$/.test(parts[0])

      if (firstPartIsNumber) {
        // Format: Place, (Bib), Name, BirthYear, Club, Result, Wind
        row.place = parts[0].replace(".", "")

        // Check if second column is bib number or name
        const secondIsNumber = /^\d+$/.test(parts[1])
        if (secondIsNumber && parts.length >= 6) {
          row.bib = parts[1]
          row.name = parts[2]
          row.birth_year = parts[3]
          row.club = parts[4]
          row.performance = parts[5]
          row.wind = parts[6]
        } else {
          row.name = parts[1]
          if (parts.length >= 5) {
            row.birth_year = parts[2]
            row.club = parts[3]
            row.performance = parts[4]
            row.wind = parts[5]
          } else if (parts.length >= 4) {
            row.club = parts[2]
            row.performance = parts[3]
          } else if (parts.length >= 3) {
            row.performance = parts[2]
          }
        }
      } else {
        // Format: Name, Club, Result, Wind
        row.name = parts[0]
        row.club = parts[1]
        row.performance = parts[2]
        row.wind = parts[3]
      }

      if (!row.name) {
        errors.push(`Rad ${i + 1}: Mangler navn`)
        continue
      }

      rows.push(row)
    }

    if (rows.length === 0) {
      errors.push("Ingen gyldige rader funnet i filen")
    }

    return { rows, metadata, errors, warnings }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!file) {
      setError("Velg en fil å laste opp")
      return
    }

    if (!batchName.trim()) {
      setError("Gi import-batchen et navn")
      return
    }

    setIsUploading(true)
    setError(null)
    setSuccess(null)

    try {
      const supabase = createClient()

      // Parse file based on type
      let parseResult: ValidationResult
      const isExcel = file.name.endsWith(".xlsx") || file.name.endsWith(".xls")

      if (isExcel) {
        parseResult = await parseExcel(file)
      } else {
        const content = await file.text()
        parseResult = parseCSV(content)
      }

      const { rows, metadata, errors: parseErrors, warnings } = parseResult

      // Sanitize data for JSON storage
      const sanitizedRows = rows.map(row => {
        const sanitized: ParsedRow = { name: "" }
        for (const [key, value] of Object.entries(row)) {
          if (typeof value === "string") {
            (sanitized as Record<string, unknown>)[key] = value
              .replace(/[\x00-\x1F\x7F]/g, "")
              .trim()
          } else {
            (sanitized as Record<string, unknown>)[key] = value
          }
        }
        return sanitized
      })

      if (parseErrors.length > 0 && sanitizedRows.length === 0) {
        setError(parseErrors.join(", "))
        setIsUploading(false)
        return
      }

      // Auto-fill metadata from file if not provided
      const finalMeetName = meetName.trim() || metadata.meetName || null
      const finalMeetCity = meetCity.trim() || metadata.meetCity || null
      // Ensure date is valid format or null
      let finalMeetDate: string | null = null
      if (meetDate) {
        finalMeetDate = meetDate
      } else if (metadata.meetDateFrom) {
        // Validate it's a proper date format
        if (metadata.meetDateFrom.match(/^\d{4}-\d{2}-\d{2}$/)) {
          finalMeetDate = metadata.meetDateFrom
        }
      }

      // Get current user
      const { data: { user } } = await supabase.auth.getUser()

      // Create import batch
      const { data: batch, error: insertError } = await supabase
        .from("import_batches")
        .insert({
          name: batchName.trim(),
          original_filename: file.name,
          source_type: isExcel ? "excel" : "csv",
          meet_name: finalMeetName,
          meet_city: finalMeetCity,
          meet_date: finalMeetDate,
          status: "pending",
          row_count: sanitizedRows.length,
          raw_data: sanitizedRows,
          validation_errors: parseErrors.length > 0 ? parseErrors : null,
          validation_warnings: warnings.length > 0 ? warnings : null,
          uploaded_at: new Date().toISOString(),
          uploaded_by: user?.id || null,
        })
        .select()
        .single()

      if (insertError) {
        console.error("Insert error details:", insertError)
        throw new Error(insertError.message || insertError.details || insertError.hint || "Kunne ikke lagre til databasen")
      }

      if (!batch) {
        throw new Error("Ingen data returnert fra databasen")
      }

      // Update form fields with extracted metadata
      if (metadata.meetName && !meetName) setMeetName(metadata.meetName)
      if (metadata.meetCity && !meetCity) setMeetCity(metadata.meetCity)

      setSuccess(`Lastet opp ${sanitizedRows.length} rader. Går til gjennomgang...`)

      // Redirect to review page
      setTimeout(() => {
        router.push(`/admin/import/${batch.id}`)
      }, 1000)

    } catch (err: unknown) {
      console.error("Upload error:", err)
      let errorMessage = "Feil ved opplasting"
      if (err instanceof Error) {
        errorMessage = err.message
      } else if (err && typeof err === "object") {
        const supaError = err as { message?: string; error?: string; details?: string; code?: string }
        errorMessage = supaError.message || supaError.error || supaError.details || JSON.stringify(err)
      }
      setError(errorMessage)
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* File Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          relative rounded-lg border-2 border-dashed p-8 text-center transition-colors
          ${isDragging ? "border-primary bg-primary/5" : "border-muted-foreground/25"}
          ${file ? "border-green-500 bg-green-50" : ""}
        `}
      >
        <input
          type="file"
          accept=".csv,.xlsx,.xls,.txt"
          onChange={handleFileInputChange}
          className="absolute inset-0 cursor-pointer opacity-0"
        />

        {file ? (
          <div className="flex flex-col items-center gap-2">
            <FileSpreadsheet className="h-10 w-10 text-green-600" />
            <p className="font-medium">{file.name}</p>
            <p className="text-sm text-muted-foreground">
              {(file.size / 1024).toFixed(1)} KB
            </p>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation()
                setFile(null)
              }}
            >
              Velg en annen fil
            </Button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <Upload className="h-10 w-10 text-muted-foreground" />
            <p className="font-medium">Dra og slipp en fil her</p>
            <p className="text-sm text-muted-foreground">
              eller klikk for å velge fil
            </p>
            <p className="text-xs text-muted-foreground">
              Støtter friidrett.no Excel-mal, CSV og tekstfiler
            </p>
          </div>
        )}
      </div>

      {/* Metadata Fields */}
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <label htmlFor="batchName" className="mb-1 block text-sm font-medium">
            Navn på import *
          </label>
          <Input
            id="batchName"
            value={batchName}
            onChange={(e) => setBatchName(e.target.value)}
            placeholder="F.eks. 'NM Senior 100m menn'"
            required
          />
        </div>

        <div>
          <label htmlFor="meetName" className="mb-1 block text-sm font-medium">
            Stevnenavn
          </label>
          <Input
            id="meetName"
            value={meetName}
            onChange={(e) => setMeetName(e.target.value)}
            placeholder="Hentes fra fil hvis tom"
          />
        </div>

        <div>
          <label htmlFor="meetCity" className="mb-1 block text-sm font-medium">
            By/Sted
          </label>
          <Input
            id="meetCity"
            value={meetCity}
            onChange={(e) => setMeetCity(e.target.value)}
            placeholder="Hentes fra fil hvis tom"
          />
        </div>

        <div>
          <label htmlFor="meetDate" className="mb-1 block text-sm font-medium">
            Dato
          </label>
          <Input
            id="meetDate"
            type="date"
            value={meetDate}
            onChange={(e) => setMeetDate(e.target.value)}
          />
        </div>
      </div>

      {/* Error/Success Messages */}
      {error && (
        <div className="flex items-center gap-2 rounded-lg bg-red-50 p-4 text-red-800">
          <AlertCircle className="h-5 w-5 flex-shrink-0" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      {success && (
        <div className="flex items-center gap-2 rounded-lg bg-green-50 p-4 text-green-800">
          <CheckCircle className="h-5 w-5 flex-shrink-0" />
          <p className="text-sm">{success}</p>
        </div>
      )}

      {/* Submit Button */}
      <div className="flex justify-end">
        <Button type="submit" disabled={!file || isUploading}>
          {isUploading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Laster opp...
            </>
          ) : (
            <>
              <Upload className="mr-2 h-4 w-4" />
              Last opp og fortsett
            </>
          )}
        </Button>
      </div>
    </form>
  )
}
