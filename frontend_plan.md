# Frontend-plan: Friidrett.live

> **Versjon:** 1.0
> **Dato:** 2025-01-16
> **Prinsipp:** "Ikke bygg sider – bygg visninger av samme data"

---

## Design-prinsipper

### 1. Klikkbart i alle retninger
Hver datapunkt er en lenke. Brukeren skal kunne navigere fritt:

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│    Resultat ←→ Utøver ←→ Klubb                                      │
│       ↕           ↕         ↕                                        │
│    Stevne  ←→  Øvelse  ←→ Årsliste                                  │
│       ↕           ↕         ↕                                        │
│   Sesong   ←→  All-time ←→ Rekorder                                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2. Informasjonstetthet med klarhet
- **Tilastopaja-inspirert:** Mye data, men organisert i klare seksjoner
- **Moderne twist:** Bedre typografi, whitespace, hover-states
- **Progressive disclosure:** Vis det viktigste først, detaljer ved klikk

### 3. Mobil-først
- Touch-vennlige tap-targets (min 44px)
- Horisontal scroll for tabeller på mobil
- Sticky headers for lange lister

### 4. Konsekvent navigasjon
- Breadcrumbs på alle sider
- Global søk alltid tilgjengelig
- Kontekstuell sidebar med relatert innhold

---

## Fargeskjema og visuell identitet

```
Primær:      #1E3A5F (Mørk blå - profesjonell, tillit)
Sekundær:    #E63946 (Rød - energi, friidrett)
Aksent:      #2ECC71 (Grønn - pers, forbedring)
Bakgrunn:    #F8F9FA (Lys grå)
Tekst:       #1A1A2E (Nesten svart)

Spesielle:
- Pers (PB):     #2ECC71 (grønn bakgrunn)
- Sesongbeste:   #3498DB (blå)
- Rekord:        #FFD700 (gull)
- Indoor:        Subtle pattern/ikon
- Outdoor:      Standard
```

---

## Sidestruktur og URL-design

### URL-konvensjoner
```
/                                    # Forside
/sok?q={query}                       # Søkeresultater

# Utøvere
/utover                              # Søk/liste
/utover/{id}                         # Profil
/utover/{id}/resultater              # Alle resultater
/utover/{id}/{øvelse}                # Resultater i én øvelse

# Statistikk
/statistikk/{år}                     # Årsoversikt
/statistikk/{år}/{øvelse}            # Årsliste for øvelse
/statistikk/all-time/{øvelse}        # All-time liste
/statistikk/rekorder                 # Norske rekorder

# Stevner
/stevner                             # Kalender
/stevner/{id}                        # Stevne
/stevner/{id}/{øvelse}               # Øvelse fra stevne

# Klubber
/klubber                             # Liste
/klubber/{id}                        # Klubbside
/klubber/{id}/utovere                # Klubbens utøvere

# Øvelser
/ovelser                             # Alle øvelser
/ovelser/{kode}                      # Øvelsesinfo + statistikk

# Admin (beskyttet)
/admin                               # Dashboard
/admin/import                        # Import av resultater
/admin/utovere                       # Utøver-admin
/admin/stevner                       # Stevne-admin
```

---

## Sider og komponenter

### 1. Forside (`/`)

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Logo]  FRIIDRETT.LIVE            [Søk...]           [Logg inn]    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    SISTE RESULTATER                          │    │
│  │  ────────────────────────────────────────────────────────── │    │
│  │  🏃 Sondre Guttormsen    Stav     5.92   NR   Albuquerque   │    │
│  │  🏃 Jakob Ingebrigtsen   1500m    3:27.14      Monaco       │    │
│  │  🏃 Karsten Warholm      400mH    46.89        Paris        │    │
│  │  [Se alle →]                                                 │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌──────────────────────┐  ┌──────────────────────────────────┐    │
│  │  KOMMENDE STEVNER    │  │  NORSKE REKORDER                 │    │
│  │  ──────────────────  │  │  ────────────────────────────── │    │
│  │  17 jan  Trondheim   │  │  100m M   9.87   Ezinne         │    │
│  │  24 jan  Oslo        │  │  Stav M   5.92   Guttormsen     │    │
│  │  [Kalender →]        │  │  [Alle rekorder →]              │    │
│  └──────────────────────┘  └──────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │               HURTIGLENKER                                   │    │
│  │  [Årslister 2025]  [All-time]  [Klubber]  [Stevnekalender]  │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Komponenter:**
- `<RecentResults />` - Siste X resultater med live-oppdatering
- `<UpcomingMeets />` - Neste stevner fra kalender
- `<RecordHighlights />` - Siste rekorder/pers
- `<QuickLinks />` - Snarvei-grid

---

### 2. Utøverprofil (`/utover/{id}`)

**Inspirert av Tilastopaja, men modernisert:**

```
┌─────────────────────────────────────────────────────────────────────┐
│  ← Tilbake                                    [Del] [Følg]          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────┐                                                        │
│  │  FOTO   │  SONDRE GUTTORMSEN                                     │
│  │         │  Lillehammer IF                                        │
│  │         │  ──────────────────────────────────────────────────    │
│  └─────────┘  Født: 12. juni 2001 (23 år)                          │
│               Høyde: 185 cm                                         │
│               Nasjonalitet: NOR                                     │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  MERITTER                                                    │    │
│  │  • Europamester innendørs 2023, 2025                        │    │
│  │  • OL-finalist 2024                                          │    │
│  │  • Norsk rekord: 5.92 (innendørs)                           │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│  [Pers]  [Resultater]  [Utvikling]  [Statistikk]     ← Tabs        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  PERSONLIGE REKORDER                                                │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                      │
│  Øvelse          Inne           Ute            Sted/Dato            │
│  ──────────────────────────────────────────────────────────────────│
│  Stav            5.92 NR        5.81           Albuquerque 10.3.23 │
│                  ↑ klikk                        Austin TX 29.4.23   │
│  ──────────────────────────────────────────────────────────────────│
│  60m hekk        8.23           -              Pocatello 16.2.23   │
│  110m hekk       -              14.32          Sandnes 2.9.16      │
│                                                                      │
│  SESONGUTVIKLING 2025                                               │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                      │
│   5.95 ┤                                          ●                 │
│        │                                     ●                      │
│   5.85 ┤                               ●                            │
│        │                         ●                                  │
│   5.75 ┤                   ●                                        │
│        │             ●                                              │
│   5.65 ┤       ●                                                    │
│        └────┬────┬────┬────┬────┬────┬────┬────                    │
│            Jan  Feb  Mar  Apr  Mai  Jun  Jul                        │
│                                                                      │
│  SISTE RESULTATER                                                   │
│  ─────────────────────────────────────────────────────────────────  │
│  10 mar 2023   Stav   5.92 NR  1   Albuquerque NM                  │
│  24 feb 2023   Stav   5.87     1   Clermont-Ferrand               │
│  [Se alle resultater →]                                             │
│                                                                      │
│  PLASSERING PÅ ÅRSLISTER                                           │
│  ─────────────────────────────────────────────────────────────────  │
│  2025 Stav inne: #1 Norge, #3 Europa, #5 Verden                    │
│  2024 Stav inne: #1 Norge, #2 Europa, #4 Verden                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Tabs:**
1. **Pers** - Personlige rekorder per øvelse (inne/ute)
2. **Resultater** - Komplett resultathistorikk med filter
3. **Utvikling** - Graf over prestasjonsutvikling
4. **Statistikk** - Avansert: 10 beste, snitt, posisjon på lister

**Klikk-lenker:**
- Øvelse → `/ovelser/stav`
- Resultat → `/stevner/{id}/stav`
- Stevnested → `/stevner/{id}`
- Klubb → `/klubber/lillehammer-if`
- Årsliste-posisjon → `/statistikk/2025/stav-menn`

---

### 3. Årsliste (`/statistikk/{år}/{øvelse}`)

```
┌─────────────────────────────────────────────────────────────────────┐
│  Statistikk > 2025 > 100m menn                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  100 METER MENN - 2025                                              │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Filter:                                                     │    │
│  │  [Inne ▼] [Senior ▼] [Alle fylker ▼] [Maks 1 per utøver ☑] │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  #   Resultat  Vind   Navn              Klubb       Stevne     Dato │
│  ─────────────────────────────────────────────────────────────────  │
│  1   10.12    +1.2   Salum Kashafali   Norna-Salhus  NM       14.6 │
│  2   10.23    +0.5   Henrik Larsson    IK Tjalve     Trondheim 22.5│
│  3   10.34    -0.3   Thomas Olsen      Sturla IF     Bislett   13.6│
│  ...                                                                 │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                      │
│  [← Forrige side]  Side 1 av 5  [Neste side →]                      │
│                                                                      │
│  [Eksporter CSV]  [Eksporter PDF]                                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Filter-alternativer:**
- Sesong: Inne / Ute
- Klasse: Senior, U23, U20, U18, U17, ..., Veteran 35-39, ...
- Region/fylke
- Maks 1 resultat per utøver (toggle)

**Klikk-lenker:**
- Navn → Utøverprofil
- Klubb → Klubbside
- Stevne → Stevneside
- Resultat → Detaljert resultatvisning

---

### 4. Stevneside (`/stevner/{id}`)

```
┌─────────────────────────────────────────────────────────────────────┐
│  Stevner > NM Innendørs 2025                                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  NM INNENDØRS 2025                                                  │
│  ─────────────────────────────────────────────────────────────────  │
│  📅 1-2. mars 2025                                                  │
│  📍 Ullevaal Stadion, Oslo                                          │
│  🏢 Arrangør: Norges Friidrettsforbund                              │
│                                                                      │
│  ØVELSER                                                            │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                      │
│  ┌─────────────────────┐  ┌─────────────────────┐                   │
│  │  LØP                │  │  HOPP               │                   │
│  │  • 60m              │  │  • Høyde            │                   │
│  │  • 200m             │  │  • Stav             │                   │
│  │  • 400m             │  │  • Lengde           │                   │
│  │  • 800m             │  │  • Tresteg          │                   │
│  │  • 1500m            │  └─────────────────────┘                   │
│  │  • 3000m            │                                            │
│  │  • 60m hekk         │  ┌─────────────────────┐                   │
│  └─────────────────────┘  │  KAST               │                   │
│                           │  • Kule             │                   │
│  ┌─────────────────────┐  └─────────────────────┘                   │
│  │  MANGEKAMP          │                                            │
│  │  • Femkamp          │                                            │
│  └─────────────────────┘                                            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 5. Øvelse fra stevne (`/stevner/{id}/{øvelse}`)

```
┌─────────────────────────────────────────────────────────────────────┐
│  NM Innendørs 2025 > Stav menn finale                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  STAV MENN - FINALE                                                 │
│  1. mars 2025                                                       │
│                                                                      │
│  #  Navn                Klubb          Resultat   Forsøk            │
│  ─────────────────────────────────────────────────────────────────  │
│  1  Sondre Guttormsen   Lillehammer IF   5.81    [Se forsøk]       │
│     └→ NM-rekord                                                    │
│  2  Pål Haugen Lillefosse GTI Friidrett  5.50                      │
│  3  Eirik Dolve          Kristiansand IF 5.30                      │
│  4  Martin Pedersen      SK Vidar        5.15                      │
│  -  Ole Hansen           IK Tjalve       NM                        │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  FORSØKSOVERSIKT - Sondre Guttormsen                        │    │
│  │  ──────────────────────────────────────────────────────────│    │
│  │  5.00: -     │  5.50: o     │  5.65: o                      │    │
│  │  5.30: -     │  5.55: xxo   │  5.81: xo  ← NM-rekord       │    │
│  │  5.40: o     │  5.60: o     │  5.87: xxx                    │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 6. Klubbside (`/klubber/{id}`)

```
┌─────────────────────────────────────────────────────────────────────┐
│  Klubber > IK Tjalve                                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  [LOGO]  IK TJALVE                                                  │
│          Oslo                                                       │
│          Stiftet: 1901                                              │
│          🌐 tjalve.no                                               │
│                                                                      │
│  [Utøvere]  [Resultater]  [Rekorder]  [Statistikk]    ← Tabs       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  AKTIVE UTØVERE (47)                                                │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  Filter: [Alle øvelser ▼] [Alle klasser ▼]                 │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
│  Navn                  Øvelser              Pers (hovedøvelse)      │
│  ─────────────────────────────────────────────────────────────────  │
│  Henrik Larsson        100m, 200m           10.23                   │
│  Marie Hansen          Høyde                1.85                    │
│  Per Olsen             Diskos, Kule         58.34                   │
│  ...                                                                 │
│                                                                      │
│  KLUBBREKORDER                                                      │
│  ─────────────────────────────────────────────────────────────────  │
│  100m M:  10.12  Salum Kashafali  2023                             │
│  100m K:  11.34  Lene Hansen      2019                              │
│  ...                                                                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Globale komponenter

### Header
```
┌─────────────────────────────────────────────────────────────────────┐
│  [≡]  FRIIDRETT.LIVE    [🔍 Søk...]              [👤 Logg inn]     │
└─────────────────────────────────────────────────────────────────────┘

Meny (≡):
├── Statistikk
│   ├── Årslister
│   ├── All-time
│   └── Rekorder
├── Stevner
│   ├── Kalender
│   └── Resultater
├── Utøvere
│   └── Søk
├── Klubber
└── Om oss
```

### Søk
- **Instant search** med debounce
- Kategoriserte resultater: Utøvere | Klubber | Stevner | Øvelser
- Nylige søk lagret lokalt
- Tastaturnavigasjon (↑↓ Enter)

### Breadcrumbs
```
Hjem > Statistikk > 2025 > 100m menn
```

### Footer
```
┌─────────────────────────────────────────────────────────────────────┐
│  FRIIDRETT.LIVE                                                     │
│                                                                      │
│  Statistikk    Stevner       Om oss        Kontakt                  │
│  • Årslister   • Kalender    • Om systemet • post@friidrettsresultater.no   │
│  • All-time    • Resultater  • API         • Facebook              │
│  • Rekorder                  • Personvern  • Instagram             │
│                                                                      │
│  © 2025 Friidrett.live. Data fra Norges Friidrettsforbund.         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Admin-panel

### Dashboard (`/admin`)
```
┌─────────────────────────────────────────────────────────────────────┐
│  ADMIN DASHBOARD                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │  VENTENDE   │  │  GODKJENT   │  │  PROBLEMER  │  │  TOTALT    │ │
│  │      3      │  │     145     │  │      7      │  │  121,695   │ │
│  │  importer   │  │  i dag      │  │  flagget    │  │  resultater│ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │
│                                                                      │
│  VENTENDE IMPORTER                                                  │
│  ─────────────────────────────────────────────────────────────────  │
│  □ Trondheim Games (Excel)     145 res.   ⚠ 3 advarsler  [Review] │
│  □ Tjalve-stevnet (FriRes)      89 res.   ✓ OK           [Review] │
│  □ Manuell registrering          3 res.   ✓ OK           [Review] │
│                                                                      │
│  FLAGGEDE PROBLEMER                                                 │
│  ─────────────────────────────────────────────────────────────────  │
│  ⚠ Mulig duplikat: "Ola Hansen" (3 treff)               [Løs]     │
│  ⚠ Usannsynlig: 100m 9.45 - Henrik Olsen               [Sjekk]    │
│  ⚠ Ukjent klubb: "Sportsklubben Sprint"                [Match]    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Import-review (`/admin/import/{id}`)
```
┌─────────────────────────────────────────────────────────────────────┐
│  ← Tilbake til dashboard                                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  TRONDHEIM GAMES 2025                                               │
│  Lastet opp: 16. jan 2025 kl 10:32                                  │
│  Kilde: Excel (trondheim_games_2025.xlsx)                           │
│                                                                      │
│  Status: ⚠ 3 advarsler - krever gjennomgang                        │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  ADVARSLER                                                   │    │
│  │  ──────────────────────────────────────────────────────────│    │
│  │  Rad 23: "Jon Hansen" - Ny utøver (ikke i systemet)        │    │
│  │          [Opprett ny] [Match eksisterende ▼]               │    │
│  │                                                              │    │
│  │  Rad 45: 100m 9.87 +2.1 - Uvanlig bra resultat             │    │
│  │          [Godkjenn] [Korriger] [Forkast]                   │    │
│  │                                                              │    │
│  │  Rad 67: Klubb "Sprint-Jeløy" ikke funnet                  │    │
│  │          [Opprett ny] [Match: "Jeløy IL" ▼]                │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  FORHÅNDSVISNING (145 resultater)                                   │
│  ─────────────────────────────────────────────────────────────────  │
│  Navn           Øvelse  Resultat  Vind  Klubb      Status          │
│  Jon Hansen     100m    11.23     +1.2  ?          ⚠ Ny utøver    │
│  Marie Olsen    Høyde   1.72      -     Tjalve     ✓ Matchet      │
│  ...                                                                 │
│                                                                      │
│  [Avvis alle]                              [Godkjenn og importer]   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Teknisk arkitektur

### Stack
```
Frontend:
├── Next.js 14+ (App Router)
├── TypeScript
├── Tailwind CSS
├── Shadcn/ui (komponenter)
├── React Query (data fetching)
├── Zustand (client state)
└── Recharts (grafer)

Backend:
├── Supabase
│   ├── PostgreSQL (database)
│   ├── Auth (autentisering)
│   ├── Realtime (live updates)
│   ├── Storage (filer)
│   └── Edge Functions (API)
└── Vercel (hosting)
```

### Mappestruktur
```
app/
├── (public)/                    # Offentlige sider
│   ├── page.tsx                 # Forside
│   ├── sok/page.tsx
│   ├── utover/
│   │   ├── page.tsx             # Søk/liste
│   │   └── [id]/page.tsx        # Profil
│   ├── statistikk/
│   │   ├── [år]/
│   │   │   ├── page.tsx         # Årsoversikt
│   │   │   └── [øvelse]/page.tsx
│   │   ├── all-time/[øvelse]/page.tsx
│   │   └── rekorder/page.tsx
│   ├── stevner/
│   │   ├── page.tsx             # Kalender
│   │   └── [id]/
│   │       ├── page.tsx         # Stevne
│   │       └── [øvelse]/page.tsx
│   ├── klubber/
│   │   ├── page.tsx
│   │   └── [id]/page.tsx
│   └── ovelser/
│       └── [kode]/page.tsx
│
├── (admin)/                     # Admin-sider (beskyttet)
│   └── admin/
│       ├── page.tsx             # Dashboard
│       ├── import/
│       │   ├── page.tsx         # Import-liste
│       │   └── [id]/page.tsx    # Review
│       ├── utovere/page.tsx
│       ├── stevner/page.tsx
│       └── klubber/page.tsx
│
├── components/
│   ├── ui/                      # Shadcn komponenter
│   ├── layout/
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   ├── Sidebar.tsx
│   │   └── Breadcrumbs.tsx
│   ├── athlete/
│   │   ├── AthleteCard.tsx
│   │   ├── AthleteProfile.tsx
│   │   ├── PersonalBests.tsx
│   │   └── ProgressionChart.tsx
│   ├── results/
│   │   ├── ResultsTable.tsx
│   │   ├── ResultRow.tsx
│   │   └── TopList.tsx
│   ├── meet/
│   │   ├── MeetCard.tsx
│   │   └── EventResults.tsx
│   └── admin/
│       ├── ImportReview.tsx
│       └── DataEditor.tsx
│
├── lib/
│   ├── supabase/
│   │   ├── client.ts
│   │   ├── server.ts
│   │   └── types.ts
│   ├── utils/
│   │   ├── performance.ts       # Formater tider/lengder
│   │   ├── age-class.ts         # Beregn aldersklasse
│   │   └── wind.ts              # Vindvalidering
│   └── hooks/
│       ├── useAthlete.ts
│       ├── useResults.ts
│       └── useSearch.ts
│
└── types/
    └── database.ts              # Generert fra Supabase
```

---

## Responsivt design

### Breakpoints
```css
sm:  640px   /* Mobil landscape */
md:  768px   /* Tablet */
lg:  1024px  /* Desktop */
xl:  1280px  /* Large desktop */
```

### Mobil-tilpasninger
- Tabeller: Horisontal scroll eller card-layout
- Filtre: Bottom sheet / modal
- Navigasjon: Hamburger-meny
- Grafer: Forenklet visning

---

## Neste steg

### Fase 1: Oppsett og grunnstruktur
1. [ ] Opprette Next.js prosjekt
2. [ ] Konfigurere Tailwind + Shadcn
3. [ ] Sette opp Supabase-klient
4. [ ] Generere TypeScript-typer fra database
5. [ ] Implementere layout (Header, Footer, Nav)

### Fase 2: Offentlige sider (MVP)
1. [ ] Forside
2. [ ] Utøverprofil
3. [ ] Årsliste
4. [ ] Søk

### Fase 3: Admin-panel
1. [ ] Autentisering
2. [ ] Dashboard
3. [ ] Import/review
4. [ ] CRUD-operasjoner

### Fase 4: Polish
1. [ ] Grafer og visualisering
2. [ ] Eksport (CSV, PDF)
3. [ ] SEO-optimalisering
4. [ ] Ytelsesoptimalisering

---

## Referanser

- **Tilastopaja:** Informasjonstetthet, progression-visning, world list positions
- **Friidrottsstatistik.se:** Filter-basert navigasjon, årslister
- **World Athletics:** Moderne design, GraphQL-arkitektur
- **Athletic.net:** Engagement, tracking over tid
