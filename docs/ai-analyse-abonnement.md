# AI-analysefunksjon med abonnement - Friidrett.live

## Oversikt

Dette dokumentet beskriver muligheten for å tilby en premium AI-analysefunksjon for betalende abonnenter på Friidrett.live. Funksjonen vil gi brukere mulighet til å utføre avanserte analyser, generere grafer, identifisere trender og stille spørsmål om friidrettsdata.

---

## Mulige funksjoner

### 1. Utøveranalyse
- **"Spør om utøver"** - Naturlig språk-spørringer om en spesifikk utøver
- **Karriereoversikt** - Automatisk generert sammendrag av utøverens karriere
- **Styrker og svakheter** - Analyse av hvilke øvelser utøveren presterer best i
- **Sesonganalyse** - Detaljert gjennomgang av en sesong med høydepunkter

### 2. Sammenligning
- **Utøver vs utøver** - Sammenlign to eller flere utøvere i samme øvelse
- **Generasjonssammenligning** - Sammenlign utøvere på samme alder (f.eks. "Warholm vs Karsten på 20 år")
- **Klubbsammenligning** - Hvilken klubb produserer best resultater i en øvelse
- **Nasjonal vs internasjonal** - Hvordan ligger norske utøvere an internasjonalt

### 3. Trendanalyse
- **Utvikling over tid** - Hvordan har nivået i en øvelse utviklet seg
- **Juniortalenter** - Identifiser utøvere med sterk progresjon
- **Klubbtrender** - Hvilke klubber er på vei opp/ned
- **Sesongmønstre** - Når på året presteres det best i ulike øvelser

### 4. Prediksjoner
- **Forventet utvikling** - Basert på historisk progresjon, hva kan utøver forvente
- **Mesterskapsanalyse** - Hvem er favoritter basert på sesongform
- **Rekordsjanse** - Sannsynlighet for at en rekord blir slått

### 5. Visualisering
- **Interaktive grafer** - Progresjonsgrafer, sammenligningsgrafer
- **Heatmaps** - Når presterer utøvere best (måned, sted, etc.)
- **Rangering over tid** - Animert visning av rangering gjennom årene

### 6. Rapporter
- **Utøverrapport** - Komplett PDF-rapport for en utøver
- **Klubbrapport** - Oversikt over klubbens utøvere og resultater
- **Sesongrapport** - Oppsummering av en hel sesong
- **Eksport til Excel** - Last ned data for egen analyse

### 7. Avanserte spørringer
- **Naturlig språk til SQL** - "Vis alle som har løpt under 11 sekunder på 100m"
- **Komplekse filter** - Kombiner flere kriterier
- **Historiske fakta** - "Hvem hadde norgesrekorden på 1500m i 1990?"

### 8. Varsler og overvåking
- **Utøvervarsler** - Få beskjed når favorittutøver oppnår ny PB
- **Rekordvarsler** - Varsling når rekorder slås
- **Talentovervåking** - Følg med på unge utøvere med potensial

---

## Teknisk arkitektur

### Autentisering
```
Supabase Auth
├── E-post/passord
├── Google OAuth
├── Magisk lenke (e-post)
└── Brukerprofile med subscription_tier
```

### Abonnementsmodell
```
Gratis (alle)
├── Se resultater
├── Se utøverprofiler
├── Enkle statistikker
└── Begrenset søk

Premium (abonnement)
├── Alt i gratis
├── AI-analyse (ubegrenset)
├── Avanserte grafer
├── Eksport til PDF/Excel
├── Varsler og overvåking
└── Prioritert support
```

### AI-backend

#### Alternativ 1: Claude API (Anbefalt)
- Beste resonnering og analyse
- God på norsk
- Kan håndtere komplekse spørsmål
- Kostnad: ~$3-15 per million tokens

#### Alternativ 2: OpenAI GPT-4
- God på kode/grafer
- Raskere respons
- Kostnad: ~$5-30 per million tokens

#### Alternativ 3: Lokal modell (Llama 3)
- Ingen API-kostnader
- Krever egen server
- Dårligere kvalitet

### Dataflyt
```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│   Bruker    │────▶│  Edge Function   │────▶│  Claude API │
│  (Frontend) │     │  (Supabase)      │     │             │
└─────────────┘     └──────────────────┘     └─────────────┘
                            │
                            ▼
                    ┌──────────────────┐
                    │    Database      │
                    │   (Read-only)    │
                    └──────────────────┘
```

### Sikkerhet
- AI har kun lesetilgang til databasen
- Rate limiting per bruker (f.eks. 100 spørringer/dag)
- Logging av alle AI-spørringer
- Ingen persondata eksponeres til AI
- Abuse detection for misbruk

---

## Betalingsløsninger

### Stripe (Anbefalt)
- Fungerer godt i Norge
- Enkel integrasjon
- Støtter abonnement
- 2.9% + 2.50 NOK per transaksjon

### Vipps Recurring
- Kjent for norske brukere
- Høyere terskel for integrasjon
- Krever bedriftsavtale

### Implementasjonsflyt
```
1. Bruker klikker "Oppgrader"
2. Sendes til Stripe Checkout
3. Betaling gjennomføres
4. Webhook mottas av Edge Function
5. Brukerens subscription_tier oppdateres
6. Bruker får tilgang til premium-funksjoner
```

---

## Kostnadsestimat

### Faste kostnader
| Komponent | Månedlig kostnad |
|-----------|------------------|
| Supabase Pro | $25 (~275 NOK) |
| Domene | ~10 NOK |
| **Total fast** | **~285 NOK** |

### Variable kostnader (per 100 aktive brukere)
| Komponent | Estimat |
|-----------|---------|
| Claude API (50 spørringer/bruker) | ~500-1500 NOK |
| Stripe-gebyrer | ~3% av omsetning |

### Inntektspotensial
| Abonnenter | Pris/mnd | Brutto inntekt | Netto (etter kostnader) |
|------------|----------|----------------|-------------------------|
| 10 | 99 NOK | 990 NOK | ~500 NOK |
| 50 | 99 NOK | 4 950 NOK | ~3 500 NOK |
| 100 | 99 NOK | 9 900 NOK | ~7 000 NOK |
| 500 | 99 NOK | 49 500 NOK | ~40 000 NOK |

---

## Implementasjonsplan

### Fase 1: Grunnlag (1-2 uker)
- [ ] Sett opp Supabase Auth
- [ ] Lag innloggings- og registreringssider
- [ ] Legg til `subscription_tier` på brukerprofil
- [ ] Lag enkel "Min side"

### Fase 2: AI Proof-of-Concept (1-2 uker)
- [ ] Sett opp Edge Function for AI-proxy
- [ ] Integrer Claude API
- [ ] Bygg enkel chat-komponent
- [ ] Test med hardkodet "premium"-bruker

### Fase 3: Beta-testing (2-4 uker)
- [ ] Inviter 5-10 testbrukere
- [ ] Samle feedback
- [ ] Finjuster AI-prompts
- [ ] Optimaliser ytelse og kostnader

### Fase 4: Betaling (1-2 uker)
- [ ] Sett opp Stripe-konto
- [ ] Integrer Stripe Checkout
- [ ] Implementer webhooks
- [ ] Test betalingsflyt

### Fase 5: Lansering
- [ ] Soft launch til eksisterende brukere
- [ ] Markedsføring på sosiale medier
- [ ] Kontakt friidrettsmiljøet
- [ ] Overvåk og optimaliser

---

## Mulige utvidelser

### Fremtidige funksjoner
- **API-tilgang** - La utviklere bygge på dataene
- **Trenerverktøy** - Spesialfunksjoner for trenere
- **Klubbabonnement** - Rabatt for hele klubber
- **Medieabonnement** - Tilgang for journalister
- **Integrasjon med treningsapper** - Koble til Strava, Garmin, etc.

### Partnerskap
- Norges Friidrettsforbund
- Friidrettsklubber
- Sportsjournalister
- Treningssentre

---

## Risikovurdering

### Tekniske risikoer
| Risiko | Sannsynlighet | Konsekvens | Tiltak |
|--------|---------------|------------|--------|
| AI gir feil svar | Middels | Lav | Disclaimer, verifisering |
| Høye API-kostnader | Middels | Middels | Kostnadskontroll, caching |
| Nedetid | Lav | Høy | Redundans, overvåking |

### Forretningsmessige risikoer
| Risiko | Sannsynlighet | Konsekvens | Tiltak |
|--------|---------------|------------|--------|
| Få betalende kunder | Middels | Høy | Freemium-modell, markedsføring |
| Konkurranse | Lav | Middels | Fokus på norsk marked |
| Datakvalitetsproblemer | Middels | Middels | Kontinuerlig datavask |

---

## Konklusjon

En AI-analysefunksjon med abonnement er **teknisk gjennomførbart** og har et **realistisk inntektspotensial** i det norske friidrettsmiljøet.

Nøkkelen til suksess er:
1. Start enkelt med én killer-funksjon
2. Test grundig med ekte brukere
3. Hold kostnadene lave i starten
4. Bygg ut basert på feedback

Anbefalt første funksjon: **"Spør om utøver"** - en enkel chat hvor man kan stille spørsmål om en utøvers resultater og utvikling.

---

*Sist oppdatert: Januar 2026*
