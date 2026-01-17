# Utviklingsplan: Norsk Friidrettsstatistikk

> **Prosjekt:** Friidrettsstatistikk
> **Database:** Supabase (lwkykthpnthfcldifixg)
> **Status:** Database opprettet, klar for utvikling

---

## Oversikt over faser

```
┌─────────────────────────────────────────────────────────────────────────┐
│  FASE 1: Grunndata & Import (Uke 1-3)                                   │
│  - Scrape minfriidrettsstatistikk.info                                  │
│  - Importere klubber, utøvere, historiske resultater                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  FASE 2: Admin-system (Uke 4-6)                                         │
│  - Admin-dashboard                                                       │
│  - Resultat-mottak og godkjenning                                       │
│  - Feilretting og manuell editering                                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  FASE 3: Automatisering (Uke 7-8)                                       │
│  - Automatisk parsing av resultatlister                                  │
│  - Utøver-matching                                                       │
│  - Validering og flagging                                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  FASE 4: Offentlig frontend (Uke 9-12)                                  │
│  - Statistikksider (årslister, all-time, utøverprofiler)                │
│  - Søk                                                                   │
│  - Stevnevisning                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  FASE 5: Utvidelser (Uke 13+)                                           │
│  - API for tredjeparter                                                  │
│  - Sanntidsoppdatering                                                   │
│  - Mobilapp                                                              │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## FASE 1: Grunndata & Import

### 1.1 Scrape minfriidrettsstatistikk.info

**Mål:** Hente all historisk data som utgangspunkt

**Sider å scrape:**
- Landsstatistikk alle år (2000-2024): `/php/LandsStatistikk.php?showclass={klasse}&showevent={øvelse}`
- Utøversøk: `/php/UtoverSok.php`
- Utøverprofiler: `/php/Utoversider.php?LicenseNo={id}`
- Stevneresultater: `/php/Stevneresultat.php`

**Klasser å hente:**
| Kode | Klasse |
|------|--------|
| 11 | Senior menn |
| 12 | Senior kvinner |
| 21 | U23 menn |
| 22 | U23 kvinner |
| 31 | U20 menn |
| 32 | U20 kvinner |
| 41 | U18 menn |
| 42 | U18 kvinner |
| ... | (alle aldersklasser) |

**Øvelser å hente:**
- Alle 32 øvelser definert i `events`-tabellen

**Output:**
1. Liste over alle klubber → `clubs`
2. Liste over alle utøvere → `athletes`
3. Alle resultater med kobling → `results`
4. Stevneinformasjon → `meets`

**Teknisk tilnærming:**
```
1. Python-script med BeautifulSoup/Scrapy
2. Rate-limiting (vær snill mot serveren)
3. Lagre rå HTML som backup
4. Parse til JSON
5. Import til Supabase
```

### 1.2 Datarengjøring

**Utfordringer å håndtere:**
- [ ] Duplikate utøvere (samme person, ulik stavemåte)
- [ ] Klubbnavnvarianter ("IL Tyrving" vs "Tyrving IL" vs "Tyrving")
- [ ] Manglende fødselsdatoer
- [ ] Gamle resultater med kun årstall

**Tiltak:**
1. Lag mapping-tabell for klubbnavn
2. Fuzzy matching på utøvernavn
3. Manuell gjennomgang av usikre matcher

### 1.3 Leveranser Fase 1

- [ ] Scraper-script ferdig
- [ ] Alle klubber importert (~400 klubber)
- [ ] Alle utøvere importert (~20.000+ utøvere)
- [ ] Historiske resultater importert (~500.000+ resultater)
- [ ] Grunndata verifisert mot original kilde

---

## FASE 2: Admin-system

### 2.1 Admin-dashboard

**Funksjonalitet:**

```
┌─────────────────────────────────────────────────────────────────┐
│  ADMIN DASHBOARD                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Ventende    │  │ Flagget     │  │ Siste       │              │
│  │ import: 3   │  │ feil: 12    │  │ import: 45  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ VENTENDE GODKJENNING                                        ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │ □ Trondheim Games 2025 (145 resultater) - Lastet opp 10:32  ││
│  │ □ Tjalvestevnet (89 resultater) - Lastet opp 09:15          ││
│  │ □ Manuell registrering (3 resultater) - Lastet opp 08:45    ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ FLAGGEDE PROBLEMER                                          ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │ ⚠ "Ola Hansen" - Mulig duplikat (3 treff)                  ││
│  │ ⚠ 100m: 9.45 - Usannsynlig tid (verifiser)                 ││
│  │ ⚠ Ukjent klubb: "Sportsklubben Sprint"                     ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Resultat-mottak

**Flyt for nye resultater:**

```
Arrangør laster opp CSV/Excel
            │
            ▼
    ┌───────────────┐
    │ PARSING       │ ← Konverter til standardformat
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │ VALIDERING    │ ← Sjekk format, rimelige verdier
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │ MATCHING      │ ← Koble til eksisterende utøvere
    └───────┬───────┘
            │
    ┌───────┴───────┐
    │               │
    ▼               ▼
┌───────┐      ┌───────────┐
│ AUTO  │      │ MANUELL   │
│ OK    │      │ REVIEW    │
└───┬───┘      └─────┬─────┘
    │                │
    │                ▼
    │         Admin godkjenner
    │                │
    └────────┬───────┘
             │
             ▼
      Publisert i database
```

**Automatisk godkjenning hvis:**
- Alle utøvere matcher eksisterende (>95% sikkerhet)
- Alle resultater er innenfor rimelige grenser
- Stevnet finnes i terminlisten (iSonen)
- Ingen duplikater oppdaget

**Manuell review hvis:**
- Nye utøvere (ukjent i systemet)
- Usannsynlige resultater (for gode/dårlige)
- Ukjent klubb
- Mulige duplikater

### 2.3 Admin-verktøy for editering

**Utøver-editering:**
- Endre navn, fødselsdato, kjønn
- Slå sammen duplikater
- Endre klubbtilhørighet (med historikk)
- Koble til ekstern ID (fremtidig)

**Resultat-editering:**
- Endre prestasjon, vind, plassering
- Endre status (OK → DQ)
- Flytte resultat til annen utøver
- Slette feilregistreringer
- Legge til manuelt

**Stevne-editering:**
- Endre navn, dato, sted
- Legge til/fjerne øvelser
- Slå sammen duplikater

**Klubb-editering:**
- Endre navn
- Slå sammen duplikater
- Sette aktiv/inaktiv

### 2.4 Leveranser Fase 2

- [ ] Admin-autentisering (Supabase Auth)
- [ ] Dashboard med oversikt
- [ ] Filopplasting for resultater
- [ ] Parsing av CSV/Excel
- [ ] Godkjenningsflyt
- [ ] CRUD for alle entiteter
- [ ] Merge-funksjon for duplikater
- [ ] Audit log (hvem endret hva)

---

## FASE 3: Automatisering

### 3.1 Automatisk parsing

**Støttede formater:**
1. **Standardformat** (vårt definerte CSV/JSON)
2. **FriRes-eksport** (hvis dokumentert)
3. **OpenTrack-eksport**
4. **Generic Excel** (intelligent gjenkjenning)

**Intelligent kolonnegjenkjenning:**
```
Inndata:                    Gjenkjent som:
"Navn"                  →   fornavn + etternavn
"Res."                  →   resultat
"Plass"                 →   plassering
"Vind (m/s)"           →   vind
"Født"                  →   fødselsdato
```

### 3.2 Utøver-matching algoritme

```
Input: "Jakob Ingebrigtsen", "Sandnes IL", "2000-09-19"

1. Eksakt match på navn + fødselsdato
   → Match funnet? → Bruk denne

2. Eksakt match på navn + klubb
   → Match funnet? → Sjekk fødselsdato-konflikt
   → Ingen konflikt? → Bruk denne

3. Fuzzy match på navn (Levenshtein < 2)
   → Flere treff? → Flag for manuell review
   → Ett treff? → Sjekk klubb/fødsel

4. Ingen match
   → Opprett ny utøver (flagget for review)
```

**Confidence score:**
- 100%: Eksakt match på alle felter
- 90%: Eksakt navn, matching fødselsdato
- 80%: Eksakt navn, samme klubb
- 70%: Fuzzy navn, samme klubb
- <70%: Flagg for manuell review

### 3.3 Validering og flagging

**Automatiske valideringsregler:**

| Sjekk | Handling |
|-------|----------|
| 100m under 9.50 (menn) | Flag: Usannsynlig |
| 100m over 15.00 | Flag: Mulig feil |
| Høyde over 2.50 (menn) | Flag: Usannsynlig |
| Vind over +4.0 eller under -4.0 | Flag: Mulig feil |
| Resultat identisk med forrige | Flag: Mulig duplikat |
| Utøver under 10 år | Flag: Sjekk alder |
| Utøver over 100 år | Flag: Mulig feil |

**PB/SB-beregning:**
- Automatisk flagging av nye pers
- Sammenligning med eksisterende beste
- Historisk trend-sjekk (plutselig stor forbedring)

### 3.4 Leveranser Fase 3

- [ ] Multi-format parser
- [ ] Kolonnegjenkjenning
- [ ] Utøver-matching med confidence
- [ ] Valideringsregler
- [ ] Automatisk PB/SB-flagging
- [ ] Duplikatdeteksjon
- [ ] Kø-system for automatisk/manuell prosessering

---

## FASE 4: Offentlig frontend

### 4.1 Sidestruktur

```
friidrett.live/
├── /                           # Forside
├── /statistikk/
│   ├── /{år}/                  # Årsstatistikk 2025
│   │   └── /{øvelse}           # 100m menn 2025
│   ├── /all-time/              # All-time lister
│   │   └── /{øvelse}           # All-time 100m menn
│   └── /rekorder/              # Norske rekorder
├── /utover/
│   ├── /                       # Søk/liste
│   └── /{id}                   # Utøverprofil
├── /stevner/
│   ├── /                       # Stevnekalender
│   ├── /kommende/              # Fremtidige stevner
│   └── /{id}                   # Stevneresultater
├── /klubber/
│   ├── /                       # Klubbliste
│   └── /{id}                   # Klubbside
└── /admin/                     # Admin (beskyttet)
```

### 4.2 Nøkkelsider

**Forside:**
- Siste resultater (sanntid når tilgjengelig)
- Kommende stevner
- Nyeste rekorder/pers
- Søkefelt

**Årsstatistikk:**
- Filter: År, øvelse, kjønn, aldersklasse
- Sortert liste med paginering
- Eksport til CSV

**Utøverprofil:**
- Personalia og bilde
- Pers-oversikt alle øvelser
- Resultathistorikk
- Sesong-for-sesong utvikling
- Grafisk fremstilling

**Stevneside:**
- Stevneinfo
- Øvelsesoversikt
- Resultatlister per øvelse

### 4.3 Teknologi

- **Framework:** Next.js 14+ (App Router)
- **Styling:** Tailwind CSS
- **State:** React Query / SWR
- **Hosting:** Vercel

### 4.4 Leveranser Fase 4

- [ ] Forside
- [ ] Årsstatistikk med filter
- [ ] All-time lister
- [ ] Utøversøk
- [ ] Utøverprofiler
- [ ] Stevneoversikt
- [ ] Stevneresultater
- [ ] Klubbsider
- [ ] Rekordoversikt
- [ ] Responsivt design (mobil)

---

## FASE 5: Utvidelser

### 5.1 API for tredjeparter

**GraphQL API:**
```graphql
query {
  toplist(event: "100m", year: 2025, gender: "M", limit: 10) {
    athlete { name, club { name } }
    performance
    wind
    meet { name, date }
  }
}
```

**Bruksområder:**
- Media (NRK, TV2)
- Klubber (egne nettsider)
- Forskere
- Tredjepartsapper

### 5.2 Sanntidsoppdatering

**Når tilgjengelig:**
- Supabase Realtime subscriptions
- Push-varsler ved nye resultater
- Live-oppdatering under stevner

### 5.3 Mobilapp

**Fase 5b - Native apper:**
- iOS (SwiftUI)
- Android (Jetpack Compose)
- Push-varsler
- Favoritt-utøvere
- Offline-støtte

---

## Spørsmål å avklare

### Høy prioritet (må avklares før start)

1. **Tilgang til minfriidrettsstatistikk.info**
   - Er det OK å scrape hele databasen?
   - Finnes det en enklere måte å få dataene (database-dump)?
   - Hvem drifter siden og kan kontaktes?

2. **Admin-brukere**
   - Hvem skal ha admin-tilgang?
   - Ulike roller (superadmin, arrangør, klubb)?
   - Skal klubber kunne registrere egne resultater?

3. **Domene og hosting**
   - Hvilket domene? (friidrett.live, statistikk.friidrett.no, annet?)
   - Hvem eier/betaler?

4. **Forholdet til NFF (Norges Friidrettsforbund)**
   - Er dette et uavhengig prosjekt eller i samarbeid med NFF?
   - Tilgang til offisielle data?
   - Skal dette erstatte minfriidrettsstatistikk.info?

### Medium prioritet (kan avklares underveis)

5. **iSonen-integrasjon**
   - API-tilgang?
   - Hva kan hentes automatisk?

6. **Import fra stevnesystemer**
   - Dokumentasjon for FriRes, OpenTrack, Roster?
   - Direkte integrasjon eller kun eksport?

7. **Historiske data**
   - Hvor langt tilbake skal vi gå?
   - Kvalitet på eldre data (pre-2000)?

### Lav prioritet (fremtidige beslutninger)

8. **Internasjonale resultater**
   - Skal norske utøveres resultater fra utlandet inkluderes?
   - Integrasjon med World Athletics/Tilastopaja?

9. **Betalingsfunksjoner**
   - Premium-abonnement for utvidet tilgang?
   - Klubb-abonnementer?

10. **Sosiale funksjoner**
    - Brukerkontoer for utøvere?
    - Følg-funksjon?
    - Kommentarer?

---

## Teknisk gjeld å håndtere

| Problem | Når | Løsning |
|---------|-----|---------|
| Utøver-duplikater | Fase 1-2 | Merge-funksjon i admin |
| Klubbnavn-varianter | Fase 1 | Alias-tabell |
| Manglende fødselsdatoer | Løpende | Berik fra andre kilder |
| Gamle tider (manuell) | Aldri | Marker som "manuell tid" |

---

## Milepæler og tidslinje

| Uke | Milepæl | Status |
|-----|---------|--------|
| 1 | Database ferdig | ✅ |
| 1-2 | Scraper ferdig, data importert | ⏳ |
| 3 | Grunndata verifisert | |
| 4-5 | Admin-dashboard MVP | |
| 6 | Godkjenningsflyt ferdig | |
| 7-8 | Automatisering ferdig | |
| 9-10 | Frontend MVP (statistikk) | |
| 11-12 | Frontend komplett | |
| 13+ | API, utvidelser | |

---

## Neste steg (umiddelbart)

1. **Avklar spørsmål 1-4** (høy prioritet)
2. **Start scraping** av minfriidrettsstatistikk.info
3. **Sett opp utviklingsmiljø** for frontend
4. **Design admin-grensesnitt** (Figma/skisse)

---

## Vedlegg

### A. Databaseskjema (oppsummering)

```
federations (1)
    └── clubs (0)
            └── athletes (0)
                    └── club_memberships (0)
                    └── results (0)
                            └── events (32)
                            └── meets (0)
                            └── seasons (62)
                            └── sources (0)
```

### B. API-nøkler

```
Supabase URL: https://lwkykthpnthfcldifixg.supabase.co
Anon key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Dashboard: https://supabase.com/dashboard/project/lwkykthpnthfcldifixg
```

### C. Filer opprettet

- `plan_friidrettsstatistikk.md` - Overordnet plan og research
- `import_spesifikasjon_v1.md` - Format for resultatimport
- `utviklingsplan.md` - Denne filen
