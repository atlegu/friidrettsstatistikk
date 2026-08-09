# Prismodell og lønnsomhet

**Versjon:** 1.0 — 09.08.2026
**Status:** Beslutningsgrunnlag. Prisen er ikke låst.

Kravspekk §21 krever at tilbudet spesifiserer **både etablerings-/implementeringskostnad
og årlig driftskostnad for en periode på tre til fem år**.

---

## 1. Kostnadsgrunnlaget vårt

### 1.1 Utviklingskostnad

Fra `03_GAP_OG_ESTIMAT.md`: kjerneleveransen frem til 01.01.2027 er 1 080–1 490 timer.
Med utvikler nummer to til en kostnad på 700–900 kr/t (innleie eller ansettelse med
sosiale kostnader) dekket for om lag halvparten av timene, og resten som egen innsats:

| Post | Lav | Høy |
|---|---:|---:|
| Innleid/ansatt utvikler, ca. 600 timer | 420 000 | 540 000 |
| Egen innsats, ca. 700 timer (internpris 600 kr/t) | 420 000 | 480 000 |
| **Utviklingskostnad frem til driftsstart** | **840 000** | **1 020 000** |

### 1.2 Årlige driftskostnader

| Post | Årlig |
|---|---:|
| Database (Supabase, Team-nivå for SLA og backup) | 30 000–70 000 |
| Applikasjonsdrift (Vercel Pro/Enterprise) | 10 000–25 000 |
| Overvåking, logging, feilsporing, backup utenfor plattform | 8 000–15 000 |
| Domene, sertifikater, escrow-avtale, forsikring | 15 000–25 000 |
| **Sum infrastruktur** | **63 000–135 000** |
| Løpende forvaltning: importdrift, support, feilretting, oppdatering (ca. 250 t) | 150 000–200 000 |
| Inkludert videreutvikling (150–200 t) | 100 000–150 000 |
| **Sum årlige kostnader** | **313 000–485 000** |

Merk at infrastrukturkostnaden vokser med datamengde og trafikk. Trafikken er
sesongsterkt topplastet — NM-helger, Bislett Games, Holmenkollstafetten — og det er
nettopp da systemet ikke får lov til å falle. Dimensjonering må hensynta dette.

---

## 2. Anbefalt prisstruktur

### Modell: moderat etablering, robust årlig avtale

| Post | Pris |
|---|---:|
| **Etablering og implementering** (fase 1 og 2, drift fra 01.01.2027) | **950 000** |
| **Årlig drift og forvaltning**, inkl. infrastruktur, support, oppdatering og 175 timer videreutvikling | **480 000 / år** |
| Femårsverdi | **3 350 000** |

Etableringshonoraret faktureres mot milepæler, ikke som forskudd:

| Milepæl | Andel |
|---|---:|
| Kontrakt og oppstart | 20 % |
| Migrering verifisert og godkjent av NFIF | 20 % |
| Kvalitetsnivåer, flagging og API i test | 25 % |
| Produksjonssetting 01.01.2027 | 25 % |
| Godkjent overtakelse etter 90 dagers drift | 10 % |

### Opsjoner, prises separat

| Opsjon | Pris |
|---|---:|
| Integrasjon per eksternt system (iSonen, OpenTrack, FriRes/LiveRes, EQ Timing, Ultimate Sport Service) | 90 000–150 000 per system, avhengig av dokumentert grensesnitt |
| Utenbaneløp, full leveranse | 450 000–600 000 |
| Fase 3, aktivitetsmodul og dashboards | 250 000–320 000 |
| Fase 4, historisk utvidelse 2001–2012 | 200 000–300 000 |
| Utvidet analyse- og medieavtale (alle mesterskap, pressestøtte, krets- og klubbrapporter) | 180 000–250 000 / år |
| Utviklingstimer utover inkludert pott | 950 kr/t |
| Analyse og utredning på bestilling | 1 100 kr/t |

**Merk:** grunnavtalen på 480 000 skal inkludere to mesterskapspakker og én årsrapport
(se `08_ANALYSE_OG_MEDIETJENESTE.md`). Det er et bevisst grep: NFIF opplever verdien
før de vurderer å kjøpe mer, og grunnavtalen blir vanskeligere å prissammenligne med
et rent plattformtilbud.

**Prinsipp for integrasjonene:** ingen fastpris før grensesnittet er dokumentert. Vi
tilbyr en forpliktende timepris og et tak per integrasjon, med forbehold om at
motparten stiller med API. Det er ærlig, og det er godt håndverk.

---

## 3. Lønnsomhet

| År | Inntekt | Kostnad | Resultat |
|---|---:|---:|---:|
| 2026–27 (etablering) | 950 000 | 840 000–1 020 000 | −70 000 til +110 000 |
| 2027 og senere, per år | 480 000 | 313 000–485 000 | −5 000 til +167 000 |

Nøkternt lest: **etableringsåret går omtrent i null, og driftsavtalen gir i beste fall
en beskjeden margin.** Det er ikke en feil i modellen — det er den reelle økonomien i å
levere en nasjonal plattform som eneste kunde.

**Analysetjenesten er det som løfter dette fra nullsum til reell drift.** En utvidet
analyseavtale på 180 000–250 000 i året har lav marginalkostnad, fordi datagrunnlaget,
metodikken og produksjonsmalene allerede finnes, og fordi den betales av et annet
budsjett (kommunikasjon og marked) enn plattformdriften. Med analyseavtalen på plass
går årsresultatet fra ca. null til 150 000–350 000. Se
`08_ANALYSE_OG_MEDIETJENESTE.md` punkt 5.

Tre ting gjør dette likevel forsvarlig:

1. **Egen innsats er priset inn som kostnad.** Selskapet betaler altså for arbeidet
   ditt underveis; marginen kommer i tillegg til det.
2. **Plattformen er et aktivum.** Kontrakten finansierer videreutvikling av et produkt
   selskapet eier og kan selge videre til andre særforbund og nordiske forbund.
   Det er der pengene ligger, ikke i NFIF-kontrakten isolert.
3. **Referansen har verdi utover kroner.** Et nasjonalt særforbund som kunde endrer
   hva Athlete Mindset AS kan selge, også utenfor statistikk.

### Nedside å være våken for

Hvis vi bommer på integrasjonene (R3 i risikoregisteret) eller på utenbaneløp (R6),
spises hele marginen. Derfor: opsjonsprising og forbehold, ikke fastpris på det vi
ikke har sett grensesnittet til.

---

## 4. Konkurrentprising — hva NFIF sannsynligvis får inn ellers

| Tilbyder | Antatt femårsverdi | Kommentar |
|---|---:|---|
| Norsk konsulenthus | 4 000 000–6 000 000 | 2 000–3 000 timer til 1 400–1 800 kr/t, pluss drift. Ingen domenekunnskap, må migrere fra bunnen. |
| OpenTrack/Tilastopaja | 1 500 000–3 000 000 | Lisensmodell på ferdig plattform. Billig, men uten norsk historikk, uten utenbaneløp og uten dataeierskap på våre vilkår. |
| Athlete Mindset AS | 3 350 000 | Mer enn en lisensmodell, vesentlig mindre enn et konsulenthus — og eneste tilbyder som allerede har dataene. |

Vi bør **ikke** underby en lisensbasert internasjonal aktør. Vi vinner ikke på pris mot
dem, og en for lav pris undergraver argumentet om at vi er en seriøs, bemannet
leverandør. Vi vinner på at vi allerede har norsk historikk, dekker utenbaneløp,
leverer aktivitetsanalyse og gir NFIF fullt eierskap.

---

## 5. Det vi må vite før prisen låses

1. **Hva er NFIFs budsjettramme?** Spør Magnus Trosdahl direkte. Hvis rammen er
   250 000 i året, er hele modellen over feil, og vi må enten redusere omfang eller
   la være å by.
2. **Tre eller fem års binding?** Fem år gir oss rom til å ta etableringen tynnere.
3. **Er utenbaneløp med i den prisen de sammenligner på?** Avgjørende for om vi
   fremstår dyre eller billige.
4. **Kommer infrastrukturkostnaden på oss eller på NFIF?** Alternativ: NFIF eier
   skykontoene og vi drifter dem. Det styrker dessuten §4-argumentet om dataeierskap
   betydelig, og bør vurderes uansett.
