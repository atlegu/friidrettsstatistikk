# friidrettresultater.no - Teknisk oversikt

## Hva er dette systemet?

friidrettresultater.no er en komplett statistikkplattform for norsk friidrett. Systemet samler inn, strukturerer og presenterer resultatdata fra norsk friidrett - fra rekruttnivå til elite, fra 1960-tallet til i dag.

### Noen tall

| | |
|---|---|
| **Resultater** | 1 134 000+ |
| **Utovere** | 46 000+ |
| **Stevner** | 40 000+ |
| **Klubber** | ~2 000 |
| **Ovelser** | 300 |

---

## Oversikt over systemet

Systemet bestar av tre hoveddeler:

```
+------------------+      +------------------+      +------------------+
|                  |      |                  |      |                  |
|    SCRAPER       | ---> |    DATABASE      | ---> |    NETTSIDE      |
|    (Python)      |      |    (Supabase/    |      |    (Next.js)     |
|                  |      |     PostgreSQL)  |      |                  |
|  Henter data     |      |  Lagrer og       |      |  Viser data til  |
|  fra kilder      |      |  strukturerer    |      |  brukerne        |
|                  |      |  all data        |      |                  |
+------------------+      +------------------+      +------------------+
```

**I enkle ord:** Et Python-program henter resultatdata fra nettet, lagrer det i en database, og en nettside presenterer det for brukerne.

---

## Del 1: Datainnsamling (Scraper)

### Hva gjor den?

Scraperen er et Python-program som automatisk henter friidrettsresultater fra nettkilder, i hovedsak minfriidrettsstatistikk.info. Den:

1. Besoker nettsider med resultater
2. Leser og tolker HTML-innholdet
3. Rydder opp og validerer dataene
4. Lagrer alt i databasen

### Teknologi

| Teknologi | Hva det er | Hvorfor vi bruker det |
|-----------|-----------|----------------------|
| **Python 3.13** | Programmeringssprak | Ideelt for databehandling og nettskraping |
| **BeautifulSoup** | HTML-parser | Leser og tolker innholdet pa nettsider |
| **Pandas** | Databibliotek | Behandler store mengder data effektivt |
| **Requests** | HTTP-bibliotek | Henter nettsider |

### Datakvalitet

Scraperen inneholder over 30 spesialiserte scripts for datarensing:

- **Tidsformater**: Konverterer ulike formater (f.eks. "541.00" sekunder til "9:01.85")
- **Duplikathandtering**: Finner og fjerner doble resultater
- **Kjonnsinformasjon**: Utleder kjonn fra navn og resultater
- **Regelverksjekk**: Handterer spesialregler som endring i spydtype for kvinner (1999), vindregler for sprint (etter 1990), og hekkehoyder per aldersklasse

---

## Del 2: Databasen

### Hva er Supabase?

Supabase er en skytjeneste som gir oss en profesjonell PostgreSQL-database med innebygd autentisering, API-lag og sikkerhet - uten at vi trenger a drifte egne servere.

**PostgreSQL** er verdens mest avanserte open-source relasjonsdatabase. Den brukes av store organisasjoner verden over og gir oss:
- Palitelig lagring av over en million resultater
- Raske oppslag og filtrering
- Avanserte sporringer og views
- Innebygd sikkerhet med radniva-tilgangskontroll (RLS)

### Databasestruktur

Databasen er organisert i tabeller som henger sammen:

```
UTOVERE (athletes)              STEVNER (meets)
  - Navn, fodselsdato             - Navn, dato, sted
  - Kjonn, nasjonalitet           - Inne/ute
  - Klubbtilhorighet              - Nivaa
       |                               |
       +---------- RESULTATER ---------+
                   (results)
                - Prestasjon (tid/lengde)
                - Vindmaling
                - Plassering
                - Status (OK/DNS/DNF)
                     |
                   OVELSER (events)
                   - 100m, hoydehopp, kule, osv.
                   - Resultattype (tid/avstand/hoyde)
                   - Spesifikasjoner per aldersklasse
```

### Smarte views (ferdigberegnede visninger)

Databasen har fire views som automatisk beregner sammensatt informasjon:

| View | Hva det gjor |
|------|-------------|
| **results_full** | Kombinerer resultat med utover, stevne, ovelse og klubb i ett oppslag |
| **personal_bests_detailed** | Beregner personlig rekord per ovelse, separat for inne/ute, med vindfilter og spydspesifikasjoner |
| **season_bests** | Beste resultat per sesong per ovelse |
| **personal_bests** | Forenklet PB-visning |

### Spesialregler implementert i databasen

Databasen handterer friidrettens komplekse regelverk:

- **Vindregler**: For sprint/hopp kreves gyldig vindmaling (maks 2.0 m/s) for resultater etter 1990
- **Spydtyper**: Kvinnespyd endret spesifikasjon i 1999 - gamle og nye resultater holdes adskilt
- **Inne/ute**: Personlige rekorder beregnes separat for innendors og utendors
- **Utstyrsklasser**: Forskjellige vekter for kule, diskos, slegge etc. etter kjonn og alder

---

## Del 3: Nettsiden (Frontend)

### Teknologi

| Teknologi | Hva det er | Hvorfor vi bruker det |
|-----------|-----------|----------------------|
| **Next.js 16** | React-rammeverk | Gir oss rask nettside med server-side rendering |
| **React 19** | UI-bibliotek | Bygger interaktive brukergrensesnitt |
| **TypeScript** | Programmeringssprak | JavaScript med typesikkerhet - farre feil |
| **Tailwind CSS 4** | CSS-rammeverk | Effektiv og konsistent styling |
| **shadcn/ui** | Komponentbibliotek | Ferdigbygde, tilgjengelige UI-komponenter |
| **Recharts** | Grafbibliotek | Progresjonskurver og resultatdiagrammer |

### Hvordan Next.js fungerer

Next.js kombinerer det beste fra to verdener:

```
BRUKER BESOKER SIDE
        |
        v
+-------------------+
| SERVER             |    1. Serveren henter data fra Supabase
| (Server Component) |    2. Bygger ferdig HTML
|                    |    3. Sender ferdig side til nettleseren
+-------------------+
        |
        v
+-------------------+
| NETTLESER          |    4. Siden er interaktiv umiddelbart
| (Client Component) |    5. Filtrering/sortering skjer lokalt
|                    |    6. Ingen ny sidelasting nodvendig
+-------------------+
```

**Fordelen:** Forste sidelasting er rask (ferdig HTML fra server), og deretter er alt interaktivt uten ventetid.

### Sidestruktur

**Offentlige sider:**
- `/` - Forside
- `/statistikk/[aar]` - Arslister (f.eks. 2025)
- `/statistikk/all-time` - Alle tiders beste
- `/statistikk/rekorder` - Norgesrekorder
- `/utover/[id]` - Utoverprofil med PB, grafer, alle resultater
- `/klubber/[id]` - Klubbprofil med statistikk
- `/stevner` - Stevnekalender og resultater

**Admin-sider (innlogging pakreves):**
- `/admin` - Dashboard
- `/admin/import` - Import av nye resultater (fra Excel)
- `/admin/athletes` - Redigering av utovere
- `/admin/meets` - Administrering av stevner

### Komponenter i utoverprofilen

Utoverprofilen er et godt eksempel pa hvordan systemet fungerer:

```
UTOVERPROFIL
|
+-- AthleteHeader         Navn, klubb, alder, hovedovelse
|
+-- PersonalBestsSection  PB-tabell: inne og ute separat
|
+-- AthleteChartsSection
|   +-- ProgressionChart      Utviklingskurve over tid (linjediagram)
|   +-- ResultsScatterChart   Alle resultater (punktdiagram)
|
+-- ResultsSection        Alle resultater med filtrering pa ar/ovelse
```

---

## Del 4: Sikkerhet og autentisering

### Brukerroller

| Rolle | Tilgang |
|-------|---------|
| **Besokende** | Se all offentlig statistikk |
| **Bruker** | Innlogget, tilgang til fremtidige premiumfunksjoner |
| **Admin** | Importere resultater, redigere data |
| **Super Admin** | Administrere brukere og roller |

### Sikkerhetstiltak

- **JWT-basert autentisering**: Sikre sesjoner via Supabase Auth
- **Row Level Security (RLS)**: Databasen håndhever tilgangskontroll pa radniva
- **Middleware-beskyttelse**: Admin-sider sjekker rolle for hver forespørsel
- **Bot-blokkering**: Aggressive crawlere (SEO-boter, AI-crawlere) blokkeres
- **Separate API-nokler**: Ulike tilgangsnivåer for nettleser vs. server

---

## Del 5: Hosting og drift

### Infrastruktur

```
+------------------+     +------------------+
|   VERCEL          |     |   SUPABASE       |
|                   |     |                  |
|  Hoster nettsiden |     |  Hoster database |
|  Automatisk       |     |  Autentisering   |
|  deploy fra Git   |     |  API             |
|  CDN/Edge-nettverk|     |  Lagring         |
|                   |     |                  |
|  Gratis/Pro-plan  |     |  Gratis/Pro-plan |
+------------------+     +------------------+
```

**Vercel** hoster nettsiden og sørger for:
- Automatisk deploy nar kode pushes til Git
- Global CDN for rask lasting over hele verden
- Serverless functions for API-kall
- Automatisk HTTPS/SSL

**Supabase** hoster databasen og gir:
- Managed PostgreSQL uten vedlikehold
- Automatisk API fra databaseskjemaet
- Innebygd brukeradministrasjon
- Sanntids-oppdateringer (mulighet)

### Versjonskontroll

All kildekode er versjonskontrollert med **Git** og lagret pa **GitHub**. Dette gir:
- Full historikk over alle endringer
- Mulighet til a rulle tilbake
- Samarbeid mellom utviklere
- Automatisk deploy via Vercel-integrasjon

---

## Del 6: Dataimport-flyten

Slik kommer nye resultater inn i systemet:

```
1. EXCEL-FIL               Admin laster opp stevneresultater (.xlsx)
      |
      v
2. IMPORT-GRENSESNITT      Systemet parser filen og viser forhåndsvisning
      |
      v
3. MATCHING                Utovere kobles mot eksisterende profiler
      |                    Nye utovere opprettes automatisk
      v
4. VALIDERING              Resultater sjekkes for gyldighet
      |                    (rimelige tider, riktig format, etc.)
      v
5. LAGRING                 Godkjente resultater lagres i databasen
      |
      v
6. OPPDATERING             PB-er, arsrekorder og statistikk
                           oppdateres automatisk via views
```

Alternativt kan scraperen kjores for a hente historiske data automatisk fra nettkilder.

---

## Oppsummering av teknologistacken

| Lag | Teknologi | Sprak |
|-----|-----------|-------|
| **Frontend** | Next.js 16, React 19, Tailwind CSS, shadcn/ui | TypeScript |
| **Grafer** | Recharts | TypeScript |
| **Database** | Supabase (PostgreSQL) | SQL |
| **Autentisering** | Supabase Auth (JWT) | - |
| **Hosting** | Vercel (nettside), Supabase (database) | - |
| **Datainnsamling** | BeautifulSoup, Pandas | Python |
| **Versjonskontroll** | Git + GitHub | - |
| **Dataimport** | xlsx-bibliotek, admin-grensesnitt | TypeScript |

### Hvorfor denne stacken?

- **Moderne og vedlikeholdbar**: Alle teknologier er aktivt utviklet og godt dokumentert
- **Skalerbar**: Kan handtere vekst i datamengde og trafikk
- **Kostnadseffektiv**: Bygget pa open-source og skyplattformer med generose gratisnivaer
- **Typesikker**: TypeScript og PostgreSQL gir farre feil og bedre datakvalitet
- **Rask**: Server-side rendering og CDN gir kort lastetid for brukerne
