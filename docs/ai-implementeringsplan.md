# AI-analyse Implementeringsplan

## Oversikt

Basert på `ai-analyse-abonnement.md` - en steg-for-steg plan for å implementere AI-analysefunksjonen med "Spør om utøver" som første killer-feature.

---

## Fase 1: Autentisering (1-2 uker)

### 1.1 Supabase Auth Setup
**Mål:** Brukere kan registrere seg og logge inn.

**Oppgaver:**
- [ ] Aktiver e-post/passord auth i Supabase Dashboard
- [ ] Aktiver Google OAuth (valgfritt, men anbefalt)
- [ ] Sett opp Magic Link (passwordless) auth

**Filer å lage:**
```
web/src/app/(auth)/
├── login/page.tsx          # Innloggingsside
├── register/page.tsx       # Registreringsside
├── callback/route.ts       # OAuth callback handler
└── logout/route.ts         # Logg ut handler
```

### 1.2 Brukerprofil med Subscription Tier
**Mål:** Lagre brukerinfo og abonnementsstatus.

**Database-migrering:**
```sql
-- Lag profiles-tabell
CREATE TABLE public.profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT,
  full_name TEXT,
  avatar_url TEXT,
  subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'premium')),
  subscription_expires_at TIMESTAMPTZ,
  stripe_customer_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS policies
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
  ON public.profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON public.profiles FOR UPDATE
  USING (auth.uid() = id);

-- Trigger for å opprette profil ved registrering
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, avatar_url)
  VALUES (
    NEW.id,
    NEW.email,
    NEW.raw_user_meta_data->>'full_name',
    NEW.raw_user_meta_data->>'avatar_url'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

### 1.3 Min Side
**Mål:** Brukere kan se og redigere sin profil.

**Filer å lage:**
```
web/src/app/min-side/
├── page.tsx                # Profiloversikt
├── innstillinger/page.tsx  # Brukerinnstillinger
└── abonnement/page.tsx     # Abonnementsstatus
```

**Komponenter:**
```
web/src/components/auth/
├── login-form.tsx
├── register-form.tsx
├── user-menu.tsx           # Dropdown i header for innlogget bruker
└── auth-provider.tsx       # Context for auth state
```

---

## Fase 2: AI Proof-of-Concept (1-2 uker)

### 2.1 Edge Function for AI Proxy
**Mål:** Sikker kommunikasjon mellom frontend og Claude API.

**Edge Function:**
```
supabase/functions/ai-analyze/
├── index.ts               # Hovedfunksjon
└── prompts.ts             # System prompts
```

**Kode-skisse (index.ts):**
```typescript
import { createClient } from '@supabase/supabase-js'
import Anthropic from '@anthropic-ai/sdk'

const anthropic = new Anthropic({
  apiKey: Deno.env.get('ANTHROPIC_API_KEY'),
})

const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
)

Deno.serve(async (req) => {
  // Verifiser auth token
  const authHeader = req.headers.get('Authorization')
  const { data: { user }, error } = await supabase.auth.getUser(
    authHeader?.replace('Bearer ', '')
  )

  if (!user) {
    return new Response('Unauthorized', { status: 401 })
  }

  // Sjekk subscription_tier
  const { data: profile } = await supabase
    .from('profiles')
    .select('subscription_tier')
    .eq('id', user.id)
    .single()

  if (profile?.subscription_tier !== 'premium') {
    return new Response('Premium required', { status: 403 })
  }

  // Parse request
  const { athlete_id, question } = await req.json()

  // Hent utøverdata fra database
  const { data: athlete } = await supabase
    .from('athletes')
    .select('*')
    .eq('id', athlete_id)
    .single()

  const { data: results } = await supabase
    .from('results_full')
    .select('*')
    .eq('athlete_id', athlete_id)
    .order('date', { ascending: false })
    .limit(100)

  // Lag prompt med data
  const systemPrompt = `Du er en ekspert på norsk friidrett...`
  const userPrompt = `
    Utøver: ${athlete.full_name}
    Født: ${athlete.birth_year}

    Resultater (siste 100):
    ${JSON.stringify(results, null, 2)}

    Spørsmål: ${question}
  `

  // Kall Claude
  const message = await anthropic.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 1024,
    messages: [{ role: 'user', content: userPrompt }],
    system: systemPrompt,
  })

  return new Response(JSON.stringify({
    answer: message.content[0].text
  }), {
    headers: { 'Content-Type': 'application/json' },
  })
})
```

### 2.2 Chat-komponent
**Mål:** Enkel chat på utøversiden.

**Filer å lage:**
```
web/src/components/ai/
├── athlete-chat.tsx        # Chat-komponent
├── chat-message.tsx        # Enkeltmelding
└── chat-input.tsx          # Input-felt
```

**Integrasjon på utøverside:**
```tsx
// web/src/app/utover/[id]/page.tsx
// Legg til under eksisterende innhold:

{user && isPremium && (
  <AthleteChatDialog athleteId={athlete.id} athleteName={athlete.full_name} />
)}
```

### 2.3 System Prompts
**Mål:** Optimaliserte prompts for friidrettsanalyse.

**Prompts å utvikle:**
1. **Generell utøveranalyse** - "Fortell meg om denne utøveren"
2. **Resultatanalyse** - "Hva er PB og utvikling?"
3. **Sammenligning** - "Sammenlign med en annen utøver"
4. **Prediksjon** - "Hva kan utøveren oppnå neste sesong?"

---

## Fase 3: Beta-testing (2-4 uker)

### 3.1 Testbrukere
- Inviter 5-10 friidrettsinteresserte
- Gi dem manuelt "premium" status i database
- Samle feedback via Google Form eller lignende

### 3.2 Logging og Metrics
**Database-tabell for AI-bruk:**
```sql
CREATE TABLE public.ai_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  athlete_id UUID REFERENCES athletes(id),
  question TEXT,
  response TEXT,
  tokens_used INTEGER,
  response_time_ms INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 3.3 Rate Limiting
- Implementer i Edge Function
- 50 spørringer per dag for premium
- 5 spørringer per dag for gratis-brukere (teaser)

### 3.4 Kostnadsoptimalisering
- Cache vanlige spørsmål
- Begrens context-størrelse (maks 50 resultater per request)
- Bruk Claude Haiku for enkle spørsmål

---

## Fase 4: Betalingsintegrasjon (1-2 uker)

### 4.1 Stripe Setup
1. Opprett Stripe-konto (business)
2. Lag produkt "Friidrett.live Premium" - 99 NOK/måned
3. Generer API-nøkler

### 4.2 Checkout Flow
**Edge Function for Stripe:**
```
supabase/functions/create-checkout/
└── index.ts
```

**Webhook for betalingsbekreftelse:**
```
supabase/functions/stripe-webhook/
└── index.ts
```

### 4.3 Abonnementssider
```
web/src/app/abonnement/
├── page.tsx                # Oversikt over planer
├── success/page.tsx        # Etter vellykket betaling
└── cancel/page.tsx         # Ved avbrutt betaling
```

### 4.4 Portal for Stripe
- Implementer Stripe Customer Portal
- Brukere kan selv kansellere/endre abonnement

---

## Fase 5: Lansering

### 5.1 Soft Launch
- Annonsér til eksisterende brukere
- 50% rabatt første måned som launch-tilbud

### 5.2 Markedsføring
- Post på friidrettsforum/grupper
- Kontakt friidrettsklubber
- Demo-video av AI-funksjonen

### 5.3 Overvåking
- Daglig sjekk av API-kostnader
- Ukentlig rapport på nye abonnenter
- A/B-testing av prompts

---

## Tekniske Valg

### Valg 1: Claude-modell
| Modell | Bruksområde | Pris |
|--------|-------------|------|
| Claude Sonnet | Standard analyse | ~$3/M tokens |
| Claude Haiku | Enkle spørsmål | ~$0.25/M tokens |
| Claude Opus | Komplekse prediksjoner | ~$15/M tokens |

**Anbefaling:** Start med Sonnet, bruk Haiku for enkle spørsmål.

### Valg 2: Streaming vs Batch
- **Streaming:** Bedre UX, bruker ser svaret gradvis
- **Batch:** Enklere å implementere

**Anbefaling:** Start med batch, legg til streaming senere.

### Valg 3: Context-håndtering
- **Alt i én prompt:** Enkelt, men dyrere
- **RAG (Retrieval):** Mer komplekst, billigere for mye data

**Anbefaling:** Start enkelt, optimaliser ved behov.

---

## Filstruktur (komplett)

```
web/src/
├── app/
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   ├── callback/route.ts
│   │   └── logout/route.ts
│   ├── min-side/
│   │   ├── page.tsx
│   │   ├── innstillinger/page.tsx
│   │   └── abonnement/page.tsx
│   └── abonnement/
│       ├── page.tsx
│       ├── success/page.tsx
│       └── cancel/page.tsx
├── components/
│   ├── auth/
│   │   ├── login-form.tsx
│   │   ├── register-form.tsx
│   │   ├── user-menu.tsx
│   │   └── auth-provider.tsx
│   └── ai/
│       ├── athlete-chat.tsx
│       ├── chat-message.tsx
│       ├── chat-input.tsx
│       └── premium-badge.tsx
└── lib/
    ├── supabase/
    │   └── client.ts          # Oppdatert med auth
    └── stripe/
        └── client.ts          # Stripe utilities

supabase/functions/
├── ai-analyze/
│   ├── index.ts
│   └── prompts.ts
├── create-checkout/
│   └── index.ts
└── stripe-webhook/
    └── index.ts
```

---

## Prioritert Rekkefølge

### Uke 1-2: Grunnlag
1. ✅ Supabase Auth aktivert
2. ✅ Database-migrering for profiles
3. ✅ Login/register-sider
4. ✅ User menu i header

### Uke 3-4: AI Proof-of-Concept
5. ✅ Edge Function for AI
6. ✅ Chat-komponent
7. ✅ Test med hardkodet premium-bruker
8. ✅ Optimaliserte prompts

### Uke 5-8: Beta + Betaling
9. ✅ Inviter testbrukere
10. ✅ Stripe-integrasjon
11. ✅ Abonnementssider
12. ✅ Webhook for betalinger

### Uke 9+: Lansering
13. ✅ Soft launch
14. ✅ Markedsføring
15. ✅ Iterasjon basert på feedback

---

## Kostnadskontroll

### Daglig budsjett
- Maks $5/dag på Claude API under beta
- Alert ved $10/dag

### Monitorering
```sql
-- Daglig kostnad (estimat)
SELECT
  DATE(created_at) as date,
  COUNT(*) as requests,
  SUM(tokens_used) as total_tokens,
  SUM(tokens_used) * 0.000003 as estimated_cost_usd
FROM ai_requests
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

---

## Risikohåndtering

| Risiko | Tiltak |
|--------|--------|
| Høye API-kostnader | Rate limiting, caching, budsjett-alerts |
| AI gir feil svar | Disclaimer, verifisering mot data |
| Få betalende kunder | Gratis-tier med teaser, god markedsføring |
| Tekniske problemer | Logging, error handling, fallback |

---

## Neste steg

1. **Nå:** Sett opp Supabase Auth i dashboard
2. **Deretter:** Lag profiles-tabell med migrering
3. **Så:** Bygg login/register-sider
4. **Til slutt:** Implementer Edge Function for AI

---

*Sist oppdatert: Januar 2026*
