# Plan: Neste generasjons norsk friidrettsstatistikksystem

## Visjon
**Friidrett.live** - Et system som ikke bare matcher, men overgår alle eksisterende løsninger ved å kombinere det beste fra etablerte systemer med moderne teknologi, AI og en utøver-sentrert opplevelse.

---

## Del 1: Research på eksisterende systemer

### 1.1 Internasjonale systemer - styrker og svakheter

#### TFRRS (USA)
| Styrker | Svakheter |
|---------|-----------|
| Sterk relasjonell kjerne | Lite fleksibel visning |
| Konsekvent URL-struktur (`/athletes/{id}`) | Begrenset historikk før college |
| Atomiske resultater (én prestasjon = én rad) | Ingen sanntidsoppdatering |
| Rekrutteringsverktøy for college | Kun college-fokus |

**Lærdom:** Sterk relasjonsmodell + konsekvent navigasjon er fundamentet.

#### Tilastopaja (Finland)
| Styrker | Svakheter |
|---------|-----------|
| Hele karrierer dokumentert | Lukket system |
| "Sesongkort" per utøver | Treg navigasjon |
| Normalisering: vind, inne/ute, aldersklasse | Begrenset API |
| 30+ alderskategorier (masters) | Gammel teknologi |
| Offisiell leverandør til European Athletics | |

**Lærdom:** Sesong- og øvelsesfokusert navigasjon + komplett historikk er kritisk.

#### Friidrottsstatistik.se (Sverige)
| Styrker | Svakheter |
|---------|-----------|
| Én datamodell, mange visninger | Utdatert UX |
| 35.000+ utøvere, 400.000+ resultater | Ingen sanntid |
| Premium-abonnement for dypere data | Lite mobilvennlig |
| Klubb-abonnementer | |
| Integrasjon med EasyRecord, WebAthletics, Roster | |

**Lærdom:** Én sann datamodell med mange innganger fungerer i praksis.

#### World Athletics
| Styrker | Svakheter |
|---------|-----------|
| GraphQL API (4 mill. requests/dag) | Ikke nasjonalt detaljnivå |
| Absolutt autoritet for ranking/rekorder | Begrenset klubbinfo |
| Skalerbart (AWS) | Kun elite-fokus |
| Global Calendar-integrasjon | |

**Lærdom:** GraphQL + skalerbar arkitektur er fremtiden.

#### Athletic.net (USA)
| Styrker | Svakheter |
|---------|-----------|
| **AthleticLIVE** - sanntidsresultater | Datakvalitet varierer |
| Mobilapp med sosiale funksjoner | Duplikatproblemer |
| Varsler (SMS, e-post, tweet) | USA-fokus |
| Video, GPS-tracking, virtuelle stevner | |
| 4.500+ stevner med live field results (2024-25) | |

**Lærdom:** Sanntid + sosiale funksjoner + mobilapp = brukerengasjement.

#### OpenTrack
| Styrker | Svakheter |
|---------|-----------|
| W3C Open Athletics Data Model | Komplekst å implementere |
| Åpen kildekode/standarder | Krever teknisk kompetanse |
| Integrasjoner: FinishLynx, Alge, Seiko, Swiss Timing | |
| Støttet av European Athletics | |

**Lærdom:** Åpne standarder sikrer fremtidig interoperabilitet.

---

### 1.2 Norsk status i dag - kritisk analyse

#### Dagens fragmenterte landskap:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────────────┐
│   iSonen    │     │  EQ Timing  │     │ minfriidrettsstatistikk │
│ (påmelding) │     │ (tidtaking) │     │     (statistikk)        │
└──────┬──────┘     └──────┬──────┘     └───────────┬─────────────┘
       │                   │                        │
       └───────────────────┴────────────────────────┘
                           │
                    ❌ Ingen integrasjon
                    ❌ Manuell dataflyt
                    ❌ Duplikater/feil
```

#### Konkrete problemer:

1. **Datakvalitet**: "Statistikken er basert på resultater publisert på www.friidrett.no. Feil i resultatlistene vil derfor fremkomme som feil i statistikken."

2. **Manuell prosess**: Resultater fra utlandet må sendes via e-post til resultater@friidrett.no

3. **Fragmentert**: Terminliste på iSonen, live-resultater på EQ Timing, statistikk på minfriidrettsstatistikk.info

4. **Under utvikling**: "Norske rekorder og andre innholdssider er under utvikling" (friidrett.no)

5. **Ingen API**: Ingen programmatisk tilgang til data

6. **Ingen mobil**: Ingen dedikert mobilapp for utøvere

---

## Del 2: Hva som gjør et system til en "vinner"

### 2.1 Kritiske suksessfaktorer

Basert på research identifiserer jeg 7 faktorer som skiller vinnere fra tapere:

| # | Faktor | Hvorfor kritisk |
|---|--------|-----------------|
| 1 | **Sanntid** | Utøvere vil se resultater umiddelbart, ikke dagen etter |
| 2 | **Én sannhet** | All data fra samme kilde eliminerer konflikter |
| 3 | **Mobil-først** | 80%+ av brukere er på mobil |
| 4 | **Sosial** | Deling, sammenligning, konkurranse driver engasjement |
| 5 | **Komplett historikk** | Fra mini til masters, hele karrieren |
| 6 | **Åpent** | API-er for tredjeparter, media, forskning |
| 7 | **Smart** | AI for innsikt, prediksjon, personalisering |

### 2.2 Differensierende funksjoner (ingen andre har dette)

#### A) AI-drevet innsikt
- **Prestasjonsanalyse**: Automatisk identifisering av trender og utviklingspotensial
- **Prediksjon**: "Med nåværende utvikling kan du nå X.XX på 100m innen Y måneder"
- **Sammenlignbar karrierebane**: "Din utvikling ligner på [Warholm/Ingebrigtsen] på samme alder"
- **Skaderisiko**: Varsling ved uvanlige prestasjonsmønstre

#### B) Gamification
- **Badges**: "Første NM-deltakelse", "Pers 5 ganger på rad", "Klubbrekord"
- **Sesongobjektiver**: Sett mål, spor fremgang, feir oppnåelser
- **Klubb-leaderboards**: Mest fremgang, flest stevner, beste poengsum
- **Nasjonale utfordringer**: "Beat the Legend" - sammenlign med historiske prestasjoner

#### C) Sosial plattform
- **Følg utøvere**: Varsler når noen du følger konkurrerer
- **Kommentarer**: På resultater, stevner, rekorder
- **Deling**: Ett-klikks deling til sosiale medier med automatisk grafikk
- **Lag**: Trenere kan følge hele grupper

#### D) Integrert treningsdagbok
- **Sync med Strava/Garmin**: Automatisk import av treningsdata
- **Korrelasjon**: Se sammenheng mellom trening og resultater
- **Belastningsovervåking**: Varsling ved over/undertrening

---

## Del 3: Teknisk arkitektur

### 3.1 Overordnet arkitektur

```
┌─────────────────────────────────────────────────────────────────┐
│                        BRUKERGRENSESNITT                        │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Web App       │   iOS App       │   Android App               │
│   (Next.js)     │   (Swift)       │   (Kotlin)                  │
└────────┬────────┴────────┬────────┴─────────────┬───────────────┘
         │                 │                      │
         ▼                 ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API GATEWAY                              │
│              (GraphQL + REST + WebSocket)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Result Service │ │ Athlete Service │ │  Stats Service  │
│                 │ │                 │ │                 │
│ - Import        │ │ - Profiler      │ │ - Ranking       │
│ - Validering    │ │ - Historikk     │ │ - Rekorder      │
│ - Deduplisering │ │ - Klubbytter    │ │ - Aggregering   │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SUPABASE / POSTGRESQL                       │
│                                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ athletes │ │ results  │ │  meets   │ │  events  │   ...      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘            │
│                                                                  │
│  + Row Level Security    + Realtime Subscriptions               │
│  + Edge Functions        + Storage (bilder, dokumenter)         │
└─────────────────────────────────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   AI/ML Layer   │ │  Import Pipeline │ │  External APIs  │
│                 │ │                  │ │                 │
│ - Prediksjon    │ │ - iSonen        │ │ - World Athletics│
│ - Anomali       │ │ - EQ Timing     │ │ - Strava        │
│ - Anbefaling    │ │ - Excel/CSV     │ │ - Garmin        │
└─────────────────┘ └──────────────────┘ └─────────────────┘
```

### 3.2 Utvidet datamodell

```sql
-- Kjerne-entiteter (utvidet fra ER-diagrammet)

-- ATHLETE med utvidet funksjonalitet
CREATE TABLE athletes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Basis
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    gender TEXT CHECK (gender IN ('M', 'F')),
    birth_date DATE,
    nationality TEXT DEFAULT 'NOR',

    -- Aktiv klubb (historikk i egen tabell)
    current_club_id UUID REFERENCES clubs(id),

    -- Profil
    bio TEXT,
    profile_image_url TEXT,

    -- Sosiale lenker
    instagram_handle TEXT,
    strava_athlete_id TEXT,

    -- Gamification
    total_competitions INTEGER DEFAULT 0,
    total_pbs INTEGER DEFAULT 0,
    badges JSONB DEFAULT '[]',

    -- System
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    verified BOOLEAN DEFAULT FALSE
);

-- RESULT med alle metadata
CREATE TABLE results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relasjoner
    athlete_id UUID REFERENCES athletes(id) NOT NULL,
    event_id UUID REFERENCES events(id) NOT NULL,
    meet_id UUID REFERENCES meets(id) NOT NULL,
    season_id UUID REFERENCES seasons(id) NOT NULL,

    -- Prestasjon
    performance TEXT NOT NULL,  -- "10.45" eller "2.10" eller "8521"
    performance_value INTEGER,  -- Normalisert verdi for sortering (centisekunder/cm/poeng)

    -- Kontekst
    date DATE NOT NULL,
    wind DECIMAL(3,1),  -- +2.0, -1.5
    altitude INTEGER,   -- Høyde over havet (relevant for sprint)

    -- Plassering
    place INTEGER,
    round TEXT CHECK (round IN ('heat', 'quarter', 'semi', 'final', 'qualification')),
    lane INTEGER,

    -- Status
    status TEXT DEFAULT 'OK' CHECK (status IN ('OK', 'DNS', 'DNF', 'DQ', 'NM')),

    -- Rekord-flagg
    is_pb BOOLEAN DEFAULT FALSE,
    is_sb BOOLEAN DEFAULT FALSE,
    is_national_record BOOLEAN DEFAULT FALSE,
    is_championship_record BOOLEAN DEFAULT FALSE,

    -- AI-generert
    predicted_equivalent DECIMAL(10,2),  -- Vind-korrigert tid
    performance_score INTEGER,           -- Normalisert poengsum (0-1000)

    -- Sporbarhet
    source_id UUID REFERENCES sources(id),
    verified BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- CLUB med historikk
CREATE TABLE club_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    athlete_id UUID REFERENCES athletes(id) NOT NULL,
    club_id UUID REFERENCES clubs(id) NOT NULL,
    from_date DATE NOT NULL,
    to_date DATE,  -- NULL = nåværende
    membership_type TEXT DEFAULT 'active'
);

-- FØLGER (sosial funksjon)
CREATE TABLE follows (
    follower_id UUID REFERENCES athletes(id),
    following_id UUID REFERENCES athletes(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (follower_id, following_id)
);

-- BADGES (gamification)
CREATE TABLE badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    icon_url TEXT,
    criteria JSONB NOT NULL,  -- {"type": "pb_count", "threshold": 5}
    rarity TEXT CHECK (rarity IN ('common', 'rare', 'epic', 'legendary'))
);

CREATE TABLE athlete_badges (
    athlete_id UUID REFERENCES athletes(id),
    badge_id UUID REFERENCES badges(id),
    earned_at TIMESTAMPTZ DEFAULT NOW(),
    result_id UUID REFERENCES results(id),  -- Hvilket resultat trigget badgen
    PRIMARY KEY (athlete_id, badge_id)
);

-- VARSLER
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    type TEXT NOT NULL,  -- 'new_result', 'pb', 'followed_athlete', etc.
    title TEXT NOT NULL,
    body TEXT,
    data JSONB,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- INDEKSER for ytelse
CREATE INDEX idx_results_athlete ON results(athlete_id);
CREATE INDEX idx_results_event ON results(event_id);
CREATE INDEX idx_results_meet ON results(meet_id);
CREATE INDEX idx_results_date ON results(date DESC);
CREATE INDEX idx_results_performance ON results(event_id, performance_value);
CREATE INDEX idx_athletes_name ON athletes(last_name, first_name);
CREATE INDEX idx_athletes_club ON athletes(current_club_id);
```

### 3.3 API-design (GraphQL)

```graphql
type Query {
  # Utøver
  athlete(id: ID!): Athlete
  athletes(filter: AthleteFilter, pagination: Pagination): AthleteConnection
  searchAthletes(query: String!): [Athlete!]!

  # Resultater
  result(id: ID!): Result
  results(filter: ResultFilter, pagination: Pagination): ResultConnection

  # Statistikk
  toplist(event: ID!, season: ID, gender: Gender, ageGroup: AgeGroup, limit: Int): [ToplistEntry!]!
  alltimeList(event: ID!, gender: Gender, limit: Int): [ToplistEntry!]!
  records(type: RecordType, gender: Gender): [Record!]!

  # Stevner
  meet(id: ID!): Meet
  meets(filter: MeetFilter): [Meet!]!
  upcomingMeets(limit: Int): [Meet!]!

  # AI
  performancePrediction(athleteId: ID!, eventId: ID!): Prediction
  similarAthletes(athleteId: ID!): [Athlete!]!
}

type Mutation {
  # Resultat-import
  importResults(meetId: ID!, results: [ResultInput!]!): ImportResult!

  # Sosiale funksjoner
  followAthlete(athleteId: ID!): Boolean!
  unfollowAthlete(athleteId: ID!): Boolean!

  # Gamification
  setSeasonGoal(eventId: ID!, target: String!): SeasonGoal!
}

type Subscription {
  # Sanntid
  liveResults(meetId: ID!): Result!
  athleteNewResult(athleteId: ID!): Result!
  followedAthletesActivity: Activity!
}

type Athlete {
  id: ID!
  firstName: String!
  lastName: String!
  fullName: String!
  gender: Gender!
  birthDate: Date
  age: Int
  ageGroup: AgeGroup!

  currentClub: Club
  clubHistory: [ClubMembership!]!

  # Statistikk
  personalBests: [PersonalBest!]!
  seasonBests(season: ID): [SeasonBest!]!
  results(filter: ResultFilter, pagination: Pagination): ResultConnection!

  # Gamification
  badges: [EarnedBadge!]!
  totalCompetitions: Int!
  totalPBs: Int!

  # Sosial
  followers: [Athlete!]!
  following: [Athlete!]!
  isFollowedByMe: Boolean!

  # AI
  predictedPerformances: [Prediction!]!
  careerSimilarity: [SimilarAthlete!]!
}
```

### 3.4 Sanntidsarkitektur

```
┌─────────────────┐
│   Tidtaking     │ (EQ Timing / FinishLynx)
│   (på banen)    │
└────────┬────────┘
         │ Webhook / Polling
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    IMPORT GATEWAY                                │
│                                                                  │
│  1. Motta rå data                                               │
│  2. Validere format                                             │
│  3. Normalisere (tid, vind, etc.)                               │
│  4. Matche utøver (fuzzy matching)                              │
│  5. Deduplisere                                                 │
│  6. Lagre i database                                            │
│  7. Trigger events                                              │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SUPABASE REALTIME                             │
│                                                                  │
│  PostgreSQL NOTIFY → Supabase Realtime → WebSocket → Klienter   │
│                                                                  │
│  Kanaler:                                                       │
│  - meet:{meet_id}        (alle resultater fra et stevne)        │
│  - athlete:{athlete_id}  (resultater for én utøver)             │
│  - event:{event_id}      (alle resultater i en øvelse)          │
│  - club:{club_id}        (alle klubbens utøvere)                │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────┬─────────┬─────────┐
│  Web    │  iOS    │ Android │
│  App    │  App    │  App    │
└─────────┴─────────┴─────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PUSH NOTIFICATIONS                            │
│                                                                  │
│  Trigger: Nytt resultat for fulgt utøver                        │
│                                                                  │
│  "🏃 Sondre Guttormsen hoppet 5.92 i stav!                      │
│   Det er ny pers! 🎉"                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Del 4: Funksjonell spesifikasjon

### 4.1 Brukerreiser

#### A) Utøver ser sine egne resultater

```
1. Logger inn med BankID / Min idrett
2. Ser dashboard med:
   - Siste resultater
   - Pers-oversikt per øvelse
   - Sesongmål og progresjon
   - Badges opptjent
3. Klikker på et resultat → ser:
   - Plassering i stevnet
   - Rangering på årsliste
   - Sammenligning med forrige gang
   - AI-analyse: "3% bedre enn forventet basert på trening"
```

#### B) Fan følger NM live

```
1. Åpner app / friidrett.live/nm-2025
2. Ser oversikt over pågående øvelser
3. Velger "Stav menn finale"
4. Ser:
   - Live-oppdatering etter hvert hopp
   - Automatisk sortering
   - Grafikk med høydeutvikling
   - Push-varsel ved rekord/pers
5. Kan dele resultatet med ett klikk
```

#### C) Journalist henter data

```
1. Bruker GraphQL API
2. Query:
   {
     toplist(event: "100m", season: "2025", gender: M, limit: 10) {
       athlete { fullName, club { name } }
       performance
       wind
       meet { name, date }
     }
   }
3. Får strukturert JSON
4. Bygger automatisk grafikk/artikkel
```

#### D) Trener analyserer laget

```
1. Logger inn som trener
2. Ser oversikt over alle utøvere i gruppen
3. Filtrerer på øvelse/periode
4. Ser:
   - Hvem har forbedret seg mest
   - Hvem trenger oppfølging (ingen pers på 6 mnd)
   - Belastningsanalyse fra Strava-data
5. Eksporterer rapport til PDF/Excel
```

### 4.2 Sider og visninger

| Side | URL | Beskrivelse |
|------|-----|-------------|
| Forside | `/` | Live-aktivitet, kommende stevner, nyeste rekorder |
| Utøver | `/utover/{id}` | Profil, pers, historikk, badges |
| Stevne | `/stevne/{id}` | Program, resultater, live |
| Resultatliste | `/stevne/{id}/{event}` | Én øvelse fra et stevne |
| Årsliste | `/statistikk/{år}/{øvelse}` | Topp X i Norge dette året |
| All-time | `/statistikk/all-time/{øvelse}` | Beste gjennom alle tider |
| Rekorder | `/rekorder` | NR, ER, VR med historikk |
| Klubb | `/klubb/{id}` | Klubbens utøvere og resultater |
| Søk | `/sok?q=...` | Universalsøk |
| Live | `/live` | Alle pågående stevner |

---

## Del 5: Implementeringsplan

### Fase 1: Fundament (Måned 1-3)

**Mål:** Kjernedatabase og grunnleggende API

- [ ] Sette opp Supabase-prosjekt
- [ ] Implementere datamodell (alle tabeller)
- [ ] Lage import-pipeline for historiske data
- [ ] Bygge GraphQL API med basisfunksjonalitet
- [ ] Enkel web-frontend for validering

**Leveranse:** API som kan svare på grunnleggende spørringer

### Fase 2: Import og integrasjon (Måned 4-6)

**Mål:** Automatisk dataflyt fra eksisterende systemer

- [ ] Integrasjon med iSonen (terminliste, påmeldinger)
- [ ] Integrasjon med EQ Timing (live-resultater)
- [ ] Import av historiske data fra minfriidrettsstatistikk
- [ ] Dedupliseringslogikk og datakvalitetssikring
- [ ] Admin-grensesnitt for manuell korrigering

**Leveranse:** Automatisk oppdatert database med alle norske resultater

### Fase 3: Brukeropplevelse (Måned 7-9)

**Mål:** Fullverdig web-applikasjon

- [ ] Responsiv web-app (Next.js)
- [ ] Alle statistikksider
- [ ] Søkefunksjonalitet
- [ ] Brukerautentisering (via NIF/Min idrett)
- [ ] Utøverprofiler med verifisering

**Leveranse:** Offentlig tilgjengelig web-app

### Fase 4: Sanntid og sosial (Måned 10-12)

**Mål:** Live-funksjoner og engasjement

- [ ] WebSocket-basert sanntidsoppdatering
- [ ] Push-varsler (iOS/Android)
- [ ] Følg-funksjon
- [ ] Deling til sosiale medier
- [ ] Kommentarfelt

**Leveranse:** Fullt live-oppdatert system med sosiale funksjoner

### Fase 5: Mobilapper (Måned 13-15)

**Mål:** Native mobilopplevelse

- [ ] iOS-app (Swift/SwiftUI)
- [ ] Android-app (Kotlin/Jetpack Compose)
- [ ] Push-notifikasjoner
- [ ] Offline-støtte for favoritter

**Leveranse:** Mobilapper i App Store og Google Play

### Fase 6: AI og gamification (Måned 16-18)

**Mål:** Differensierende funksjoner

- [ ] ML-modeller for prestasjonsanalyse
- [ ] Prediksjonssystem
- [ ] Badge-system
- [ ] Leaderboards
- [ ] Sesongobjektiver

**Leveranse:** Komplett system med AI-drevne innsikter

---

## Del 6: Teknologivalg

| Komponent | Teknologi | Begrunnelse |
|-----------|-----------|-------------|
| Database | **Supabase (PostgreSQL)** | Sanntid innebygd, RLS, Edge Functions, norsk datacenter |
| Backend API | **GraphQL (Supabase + Edge Functions)** | Fleksibelt, typesikkert, caching |
| Web frontend | **Next.js 14+ (App Router)** | SSR, ISR, React Server Components |
| iOS | **SwiftUI** | Moderne, deklarativt |
| Android | **Jetpack Compose** | Moderne, deklarativt |
| AI/ML | **Python + Supabase Edge Functions** | Scikit-learn, TensorFlow Lite |
| Hosting | **Vercel (web) + Supabase** | Edge-nettverk, automatisk skalering |
| CDN | **Vercel Edge / Cloudflare** | Global distribusjon |
| Autentisering | **Supabase Auth + NIF SSO** | Integrert med norsk idrett |

---

## Del 7: Konkurransefordeler vs. eksisterende systemer

| Funksjon | Tilastopaja | Friidrottsstatistik.se | Athletic.net | **Friidrett.live** |
|----------|-------------|------------------------|--------------|---------------------|
| Sanntidsresultater | ❌ | ❌ | ✅ | ✅ |
| Mobilapp | ❌ | ❌ | ✅ | ✅ |
| Åpent API | ❌ | ❌ | Delvis | ✅ GraphQL |
| AI-analyse | ❌ | ❌ | ❌ | ✅ |
| Gamification | ❌ | ❌ | Delvis | ✅ |
| Sosiale funksjoner | ❌ | ❌ | ✅ | ✅ |
| Treningsintegrasjon | ❌ | ❌ | ❌ | ✅ Strava/Garmin |
| Komplett historikk | ✅ | ✅ | Delvis | ✅ |
| Norsk fokus | ❌ | ❌ | ❌ | ✅ |

---

## Del 8: Risiko og mitigering

| Risiko | Sannsynlighet | Konsekvens | Mitigering |
|--------|---------------|------------|------------|
| Datakvalitet fra kilder | Høy | Høy | Robust validering, manuell korrigering, sporbarhet |
| Manglende integrasjon med iSonen/EQ | Medium | Høy | Tidlig dialog med leverandører, fallback til scraping |
| Lav brukeradopsjon | Medium | Høy | Involver brukere tidlig, fokus på UX, gamification |
| Teknisk gjeld | Medium | Medium | Automatiserte tester, code review, dokumentasjon |
| Skalerbarhet ved NM/store stevner | Lav | Høy | Lastesting, CDN-caching, Supabase autoskalering |

---

## Del 9: Suksesskriterier

### Kvantitative mål (12 måneder etter lansering)

- [ ] 50.000+ registrerte brukere
- [ ] 80%+ av alle norske stevneresultater importert automatisk
- [ ] < 5 minutter fra resultat på banen til synlig i app
- [ ] 4.5+ rating i App Store / Google Play
- [ ] API brukt av 10+ tredjeparter (media, klubber, etc.)

### Kvalitative mål

- [ ] "Go-to" kilde for norsk friidrettsstatistikk
- [ ] Brukes aktivt av NRK/TV2 under stevner
- [ ] Utøvere deler aktivt fra plattformen
- [ ] Positiv omtale i friidrettsmiljøet

---

## Referanser og kilder

### Systemer analysert
- [TFRRS](https://www.tfrrs.org/) - Track & Field Results Reporting System
- [Tilastopaja](https://www.tilastopaja.info/) - Finnish Athletics Statistics
- [Friidrottsstatistik.se](https://www.friidrottsstatistik.se/) - Swedish Athletics Database
- [World Athletics Stats Zone](https://worldathletics.org/stats-zone)
- [Athletic.net](https://www.athletic.net/) - US Track & Field Results
- [OpenTrack](https://opentrack.run/) - Competition Management Suite

### Norske systemer
- [friidrett.no](https://www.friidrett.no/resultater-og-statistikk/)
- [minfriidrettsstatistikk.info](https://minfriidrettsstatistikk.info/)
- [iSonen](https://isonen.no/)
- [EQ Timing](https://www.eqtiming.com/)

### Tekniske standarder
- [W3C Open Athletics Data Model](https://w3c.github.io/opentrack-cg/spec/model/)
- [OpenTrack GitHub](https://github.com/openath)

### Forskning og trender
- [AI in Sports Analytics (Nature)](https://www.nature.com/articles/s41598-025-01438-9)
- [Machine Learning for Performance Prediction](https://www.sciencedirect.com/science/article/pii/S2210832717301485)
- [Gamification in Sports](https://blog.brandmovers.com/gamification-in-sports-the-ultimate-marketing-playbook-for-2025)
