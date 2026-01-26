# Utviklingslogg - FRIIDRETT.LIVE

## Siste oppdatering: 2026-01-26

### Prosjektoversikt
- **Frontend**: Next.js 16.1.3 med Turbopack, TypeScript, Tailwind CSS
- **Backend**: Supabase (PostgreSQL med RLS)
- **Hosting**: Vercel

---

## Import-system for resultatlister (Januar 2026)

### Hva ble bygget
Et komplett system for å importere resultatlister fra Excel-filer (friidrett.no-format).

### Hovedfiler
- `/web/src/app/admin/import/page.tsx` - Hovedside for import
- `/web/src/app/admin/import/upload-form.tsx` - Excel-parsing og opplasting
- `/web/src/app/admin/import/[id]/page.tsx` - Server-side data-henting for gjennomgang
- `/web/src/app/admin/import/[id]/import-review.tsx` - Gjennomgang og godkjenning av import

### Funksjoner implementert

#### Excel-parsing (upload-form.tsx)
- Auto-deteksjon av kolonnestruktur (med/uten startnummer-kolonne)
- Parsing av metadata fra fil (stevnenavn, sted, dato, øvelse)
- Støtte for innendørs/utendørs-flagg
- Håndtering av friidrett.no Excel-format

#### Utøver-matching (import-review.tsx)
- Fuzzy-matching av navn mot 46000+ utøvere i databasen
- Scoring basert på eksakt navnematch (+10) og fødselsår-match (+5)
- Auto-valg av beste match når flere kandidater finnes
- Manuell søk og matching for uklare tilfeller
- Mulighet for å opprette nye utøvere

#### Øvelse-matching
- Automatisk matching av øvelsesnavn (f.eks. "3000m" → "3000 meter")
- Støtte for ulike formater og koder

#### Stevne-håndtering
- Auto-matching av stevne fra fil mot eksisterende stevner
- Opprettelse av nye stevner ved behov
- Sjekk for duplikater før opprettelse

#### Resultat-import
- Konvertering av tidsformat (MM.SS.hh → sekunder)
- Batch-innsetting (10 resultater om gangen) for å unngå timeout
- Validering av alle ID-er før innsetting
- Detaljert feilhåndtering med radnummer

### Løste problemer

| Problem | Løsning |
|---------|---------|
| Navn ble vist som fødselsår | Auto-deteksjon av kolonnestruktur |
| Kun 1000 utøvere ble hentet | Batch-henting med `.range()` |
| Øvelser ble ikke funnet | Fikset query til å bruke `category` i stedet for `event_type` |
| Tidsformat-feil (7.54.96) | Konvertering til sekunder (474.96) |
| Duplikat stevne-feil | Sjekk for eksisterende stevne før opprettelse |
| AbortError ved import | Batch-innsetting i stedet for bulk |

### Database-tabeller involvert
- `import_batches` - Lagrer opplastede filer og status
- `results` - Resultatdata
- `athletes` - Utøvere
- `events` - Øvelser
- `meets` - Stevner
- `seasons` - Sesonger

---

## Dataopprydding (26. januar 2026)

### Problemet
Import fra 2026-01-26 hadde parsing-feil som korruperte tidsformater:
- `14.9` → `14.09` (X.Y → X.0Y) - 2,617 tilfeller
- `112.7` → `112.007` (X.Y → X.00Y) - 2,873 tilfeller

### Opprydding utført

| Handling | Antall |
|----------|--------|
| Slettet X.0Y korrupte duplikater | 2,091 |
| Korrigert X.0Y → X.Y | 526 |
| Slettet X.00Y korrupte duplikater | 322 |
| Korrigert X.00Y → X.Y | ~2,551 |
| Slettet eksakte duplikater | 14,124 |
| **Totalt resultater etter opprydding** | 1,133,571 |

### Nytt felt: is_manual_time

Lagt til felt `is_manual_time` (BOOLEAN) i results-tabellen for å markere manuelle tider.

**Regler for manuelle tider (sprint/hekk under 400m):**
- Har kun én desimal (f.eks. 14.9 ikke 14.90)
- Skal IKKE telle som rekorder
- Skal IKKE være med på alle-tiders lister
- Kan vises separat med "manuell tid" markering

**Statistikk:**
- Elektroniske tider: 1,114,642
- Manuelle tider markert: 18,929

### SQL for å sjekke manuelle tider
```sql
SELECT * FROM results
WHERE is_manual_time = TRUE
  AND event_id IN (SELECT id FROM events WHERE category IN ('sprint', 'hurdles'))
ORDER BY performance_value;
```

---

## Andre nylige endringer

### Personlige rekorder (PB-markering)
- Commit: 17b17ca - Bruker `personal_bests`-data konsistent for PB-markering

### Øvelse-sortering
- Commit: 90c2263 - Lagt til øvelse-sortering i ResultsSection

### Grafer
- Commit: d1dba33 - Grafer er nå klikkbare for å navigere til stevner

---

## Kjente begrensninger
- Import støtter kun friidrett.no Excel-format
- Maks 500 stevner vises i dropdown (nyeste først)
- Utøver-søk ved matching er begrenset til topp 10 treff

---

## Neste steg / TODO
- [ ] Støtte for flere filformater
- [ ] Bulk-import av flere filer
- [ ] Bedre feilhåndtering ved nettverksproblemer
- [ ] Progress-indikator under import
