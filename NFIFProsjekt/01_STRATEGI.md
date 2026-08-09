# Strategi — hvordan vi vinner NFIF-anskaffelsen

**Versjon:** 1.0 — 09.08.2026
**Tilbyder:** Athlete Mindset AS

---

## 1. Hva NFIF egentlig kjøper

Kravspekken lister 24 kapitler med funksjonalitet, men bak den ligger tre spørsmål
som avgjør hvem som får jobben:

1. **Kan dere levere baneresultater i drift innen 01.01.2027?**
   Fristen er brutal. Fra kontraktsinngåelse i september er det knapt fire måneder.
   En leverandør som skal bygge fra bunnen og migrere 1,2 millioner resultater rekker
   det ikke. Vi er ferdige med den delen allerede.

2. **Finnes dere fortsatt i 2031?**
   §1 sier rett ut at dagens løsning «is no longer sustainable to maintain and develop
   with the volunteer resources currently available». NFIF er brent på nettopp
   personavhengighet. Dette er vår største taperisiko, ikke teknikken.

3. **Hva koster det, og har vi råd?**
   NFIF har drevet dette på dugnad i tretten år. Betalingsviljen er reell, men
   begrenset. Et konsulenthus som priser dette riktig lander på 4–6 MNOK over fem år.
   Vi kan levere mer for mindre — og det er et argument vi skal bruke eksplisitt.

Tilbudet skal svare på disse tre i den rekkefølgen, ikke følge kravspekkens
kapittelnummerering. Kravsporingsmatrisen (`04_KRAVSPORING.md`) tar seg av
punkt-for-punkt-dekningen som vedlegg.

---

## 2. Konkurransebildet

> **Oppdatert 09.08.2026:** Vurderingen er at **Tilastopaja er den mest sannsynlige
> hovedkonkurrenten**, ikke OpenTrack. De leverer allerede til Sverige
> (friidrottsstatistik.se). Full gjennomgang og motposisjonering:
> `07_KONKURRENT_TILASTOPAJA.md`. Avsnittet under står fordi OpenTrack fortsatt er en
> reell tilbyder, og fordi de to opptrer sammen.

### 2.1 OpenTrack + Tilastopaja

OpenTrack (britisk) og Tilastopaja (finsk) samarbeider allerede om nasjonale
rankinglister og utøverbiografier, utviklet i samarbeid med European Athletics, og
betjener over et dusin nasjonale forbund. Tilastopaja er European Athletics'
statistikkleverandør.

Verre: **OpenTrack står oppført i kravspekkens §13 som integrasjonsmål.** De er altså
allerede inne i norsk friidrett gjennom arrangørene. Deres naturlige bud er «dere
bruker oss allerede til konkurranseavvikling — skru på statistikkmodulen vår».

At kravspekken er skrevet på engelsk er et signal om at NFIF forventer, eller allerede
har snakket med, internasjonale tilbydere.

**Deres styrker:** referanser fra et dusin forbund, EA-forankring, ferdig
integrasjonsflate mot egen konkurranseprogramvare, organisatorisk soliditet.

**Deres svakheter — og vårt angrepspunkt:**

| Svakhet | Vårt motsvar |
|---|---|
| Norsk historikk | Vi har 1,4 mill. resultater og 47 901 stevner tilbake til 1922 allerede strukturert. Tilastopaja har toppnivå, ikke bredden. |
| Utenbaneløp | §8 og §12 er tungt vektet. OpenTrack er en baneplattform. Norsk mosjonsløping (EQ Timing, Ultimate Sport Service, terreng- og motbakkeløp) er ukjent terreng for dem. |
| Norsk regelverk | Aldersklasser etter kalenderår, kretsstruktur, NM-systemet, spydtype 1999, hekkehøyder per klasse, TR14.1/TR43.1-baner i Norge. Vi har allerede implementert flere av disse. |
| Aktivitetsanalyse (§12) | Deres produkt er resultatpresentasjon. §12 er samfunnsanalyse — der har vi allerede levert (se 3.3). |
| Dataeierskap (§4) | Vi kan tilby full eksport, kildekode-escrow og exit-klausul uten forbehold. En internasjonal plattformleverandør vil normalt ikke gi fra seg plattformen. |
| Nærhet | Norsk språk, norsk tidssone, kan sitte i møter på Ullevaal. Support under NM-helger. |

### 2.2 Øvrige mulige tilbydere

- **Tidtakerselskaper** (EQ Timing, Ultimate Sport Service) — sterke på løp, svake på
  banestatistikk og historikk. Mulige *partnere* snarere enn motstandere.
- **Norske konsulenthus** — vil kunne levere, men til 4–6 MNOK og med null
  domenekunnskap. Taper på pris og på fristen 01.01.2027.
- **Dagens frivillige miljø** rundt minfriidrettsstatistikk.info — NFIF har allerede
  konkludert med at dette ikke er bærekraftig. Lite sannsynlig som konkurrent, men
  **høyst relevant som interessent**: de sitter på domenekunnskap og godvilje, og
  bør omtales med respekt, ikke som noe vi erstatter. Vurder å tilby dem en rolle
  i et fagråd. Dette er også ren risikohåndtering — motstand fra dette miljøet kan
  koste oss kontrakten.

### 2.3 Er dette en offentlig anskaffelse?

Særforbund under NIF regnes normalt ikke som offentligrettslige organer, og
anskaffelsen er etter alt å dømme privatrettslig. Praktisk konsekvens: **relasjon,
demonstrasjon og tillit veier tyngre enn formell tilbudsformalia.** Det taler for
å oppsøke NFIF aktivt før fristen fremfor å sende inn en PDF og vente.
Antagelsen bør bekreftes (se `06_SPORSMAL_TIL_NFIF.md`).

---

## 3. Våre fire vinnertemaer

Alt vi skriver skal kunne spores tilbake til ett av disse.

### 3.1 «Plattformen finnes allerede — med deres data i»

Dette er tilbudets kjerne. Vi sender ikke inn en plan, vi sender inn en URL.

- 1 190 655 resultater fra 2013 og senere er allerede importert, normalisert og
  søkbare — nøyaktig det §15 setter som førsteprioritet.
- Utøverprofiler, klubbsider, stevnesider, årsstatistikk, alle-tiders-lister,
  rekordoversikter og sammenligningsverktøy er i drift.
- Migrering av historiske data er normalt den dyreste og mest risikofylte posten i
  en slik anskaffelse. Hos oss er den et faktum, ikke et estimat.

**Tiltak:** NFIF-tilpasset demoinstans med egen URL, klar minst en uke før fristen,
pluss en tre minutters videogjennomgang for de i styringsgruppen som aldri logger inn.

### 3.2 «Vi treffer 01.01.2027 fordi vi begynte i 2024»

Konkurrentene må love fristen. Vi kan demonstrere at vi allerede har passert
milepælen som gjør fristen mulig. Tidsplanen i tilbudet skal derfor vise hva som
gjenstår, ikke hva som skal bygges — det er en helt annen samtale.

### 3.3 «Vi har allerede besvart §12»

§12 (aktivitets- og deltakerdata) er ifølge NFIF selv «particularly important for
Norwegian Athletics' strategic work related to recruitment and membership development».

Vi har allerede produsert:

- **«Norsk friidrett 2013–2025»** (`analyse/trenerartikkel/`) — analyse av samtlige
  1,1 millioner resultater fra ca. 85 000 utøvere. Dokumenterer at aktive utøvere i
  alderen 10–19 falt fra 8 745 (2019) til 6 418 (2025), en nedgang på 27 prosent
  konsentrert i de yngste årsklassene, mens seniorgruppen er stabil.
- **Forskningsarbeid om relativ alderseffekt** (`forskning/RAE/`) på samme database,
  under arbeid mot fagfellevurdert publisering.

Dette er et argument ingen konkurrent kan matche: databasen holder ikke bare
presentasjonskvalitet, den holder **forskningskvalitet**. Og vi har allerede gitt NFIF
strategisk innsikt de ikke hadde.

**Tiltak:** Legg ved en kort lederrettet oppsummering av rekrutteringsanalysen som
selvstendig vedlegg til tilbudet. Det er den emosjonelle avslutningen — vi viser dem
noe om deres egen idrett de ikke visste.

> **Merk:** Analysen bør avklares mot eventuelle publiseringsplaner før den deles
> med NFIF. Se `06_SPORSMAL_TIL_NFIF.md`.

### 3.4 «Et selskap, ikke en ildsjel»

Se punkt 4 — dette er like mye risikohåndtering som salgsargument.

### 3.5 «Vi selger ikke tilgang til data — vi er analysemiljøet deres»

Det femte og sterkeste temaet, lagt til 09.08.2026. Konkurrentene tilbyr en database,
i praksis med abonnement. Vi tilbyr plattformen **pluss en kunnskapsfunksjon**:
mesterskapsanalyser før hvert NM, EM, VM og OL, pressemateriell, årsrapport om
aktivitet og rekruttering, samt krets- og klubbrapporter.

Vi har allerede levert alle tre typene: mesterskapsanalysen «56 til Birmingham» om den
norske EM-troppen, breddeanalysen «Norsk friidrett 2013–2025», og fagfellevurdert
forskning på det samme datagrunnlaget.

Dette er den delen av tilbudet som ikke kan kopieres, og som ikke kan
prissammenlignes. Full utforming i `08_ANALYSE_OG_MEDIETJENESTE.md`. Den skal ha eget
hovedkapittel i tilbudet, ikke stå som vedlegg.

---

## 4. Vår største svakhet, og hvordan vi nøytraliserer den

Athlete Mindset AS er nystartet. En innkjøper som skal binde seg for tre til fem år
vil se på soliditet, bemanning og hva som skjer hvis selskapet forsvinner. Vi må ta
dette opp selv, tidlig og uoppfordret — hvis NFIF må stille spørsmålet, har vi
allerede tapt poenget.

| Innvending | Motsvar i tilbudet |
|---|---|
| «Nystartet selskap uten historikk» | Selskapet er nytt, plattformen er det ikke. To års utvikling og 1,4 millioner produksjonsdata er referansen. |
| «Bare én person» | Navngitt utvikler nummer to fra kontraktsstart, finansiert av etableringshonoraret. **Uten dette punktet er tilbudet vesentlig svakere.** |
| «Hva om dere går konkurs?» | Kildekode- og databaseescrow hos tredjepart. Exit-klausul: NFIF får kildekode, data og driftsdokumentasjon vederlagsfritt ved opphør, uansett årsak. |
| «Innelåsing» | Standard, ikke-eksotisk teknologi (PostgreSQL, Next.js, åpne formater). Løsningen kan overtas av enhver kompetent leverandør. Dette er en reell forskjell fra en proprietær internasjonal plattform. |
| «Er dette bare et sideprosjekt?» | Selskapet har flere ben å stå på (laserprodukter for Athlete Mindset Inc., konsulentvirksomhet). Det betyr at vi ikke er økonomisk avhengige av én kontrakt — samtidig som statistikkplattformen er definert som strategisk kjerneprodukt, ikke et oppdrag. |
| «Ingen referansekunder» | Vi har brukere, akademisk bruk av databasen og et publisert analysearbeid. Vurder å be om en referanseuttalelse fra en klubb, krets eller trener som bruker friidrett.live i dag. |

**Konkret anbefaling:** Ikke selg inn Athlete Mindset AS som et konsulentselskap som
tar et oppdrag. Selg det inn som et **produktselskap innen idrettsdata**, der NFIF blir
ankerkunde i et produkt som skal leve videre. Det forklarer både hvorfor prisen er lav
og hvorfor vi vil bli værende.

---

## 5. Den langsiktige forretningslogikken

NFIF-kontrakten alene gir moderat margin (se `05_PRISMODELL.md`). Den strategiske
verdien ligger et annet sted, og det bør styre hvor aggressivt vi priser:

1. **Referansekunden.** Et nasjonalt særforbund som kunde gjør plattformen salgbar.
2. **Gjenbruk mot andre norske særforbund.** Skøyter, svømming, sykkel, ski og
   orientering har det samme problemet: resultatdata spredt, dugnadsdrevet
   statistikk, ingen aktivitetsanalyse. Datamodellen er i stor grad den samme.
3. **Nordisk eksport.** Samme argument mot Sverige, Danmark og Finland — der
   Tilastopaja riktignok står sterkt.
4. **Analyse som eget produkt.** Aktivitets- og frafallsanalyse er noe idretts-Norge
   og forskningsmiljøene etterspør, og som passer selskapets øvrige profil.

Konsekvens for tilbudet: vi kan prise NFIF-kontrakten til å dekke kostnader og gi
en fornuftig, men ikke fet, margin — fordi den virkelige gevinsten er produktet og
referansen. Det må vi *ikke* si til NFIF, men det skal styre beslutningen vår.

---

## 6. Risikoregister for anskaffelsen

| # | Risiko | Konsekvens | Tiltak |
|---|---|---|---|
| R1 | Bus factor / bemanning oppfattes som utilstrekkelig | Taper kontrakten | Navngitt utvikler nr. 2 før tilbudsfrist. Høyest prioritet. |
| R2 | OpenTrack byr med EA-forankring og et dusin referanser | Taper på troverdighet | Fokuser på historikk, utenbaneløp, §12 og dataeierskap. |
| R3 | Vi underestimerer integrasjonene (§13) | Taper penger, sprekker på tid | Pris integrasjoner som separate opsjoner med timepott, ikke fastpris. Forbehold om at motparten leverer API. |
| R4 | Datakvalitet avsløres i demo (søppelklubber, manglende kjønn) | Taper troverdighet der vi er sterkest | Datavask før demo. Se `02_ARBEIDSPLAN.md` dag 3–8. |
| R5 | NFIFs budsjett er lavere enn vår kostnadsdekning | Vi vinner en kontrakt vi taper på | Avklar budsjettramme direkte med Magnus Trosdahl før prisen låses. |
| R6 | Utenbaneløp krever mer enn vi tror | Sprekk på fase 2 | §24 krever bare et troverdig veikart innen 31.12.2026. Utnytt det: lever et godt designnotat nå, bygg i 2027. |
| R7 | Motstand fra dagens frivillige miljø | Politisk motvind internt i NFIF | Tilby fagrådsrolle og eksplisitt anerkjennelse av arbeidet siden 2013. |
| R8 | Personvern, særlig data om mindreårige | Kan velte hele løsningen | Eget personvernvedlegg, ikke et avsnitt. Se punkt 7. |
| R9 | Vi rekker ikke fristen 31.08 med god nok kvalitet | Ute av konkurransen | Arbeidsplanen har buffer fra dag 28. Demoen prioriteres foran dokumentteksten. |

---

## 7. To ting kravspekken ikke nevner — som vi skal nevne

Å ta opp krav kunden har glemt er billig troverdighet, og det viser at vi kan
domenet bedre enn dem som bare leser bestillingen.

**Universell utforming.** Publikumsrettede norske nettsteder er underlagt kravene til
universell utforming av IKT (WCAG 2.1 AA). Kravspekkens §17 nevner bare mobil, nettbrett
og desktop. Vi tar inn WCAG-samsvar som eksplisitt leveranse — og noterer at det er et
lovkrav, ikke en ekstravaganse.

**Personvern for mindreårige.** Basen inneholder navn, fødselsdato, klubb og
resultathistorikk for barn helt ned i tiårsalderen, publisert åpent. Det er
GDPR-relevant på et helt annet nivå enn seniorstatistikk, og NIFs egne
personvernbestemmelser kommer i tillegg. Vi foreslår konkret:

- behandlingsgrunnlag og databehandleravtale på plass fra dag én
- lagring innenfor EU/EØS
- differensiert eksponering for de yngste årsklassene (f.eks. fødselsår i stedet for
  full fødselsdato offentlig, full dato kun internt)
- dokumentert rutine for innsyn, retting og sletting
- vurdering av personvernkonsekvenser (DPIA) som del av leveransen

Dette er potensielt et vinnerargument i seg selv: den tilbyderen som viser at de har
tenkt på at halve databasen består av barn, fremstår som den voksne i rommet.

---

## 8. Anbefalt beslutning

1. **Bemanning avklares først.** Alt annet i tilbudet er svakere uten navn nummer to.
2. **Be om avklaringsmøte med Thor Gjesdal denne uken.** Vis demoen. Et tilbud som
   kommer etter et møte, leses annerledes enn et som kommer kaldt.
3. **Avklar budsjettrammen med Magnus Trosdahl** før prisen låses.
4. **Prioriter demoen over dokumentet** hvis tiden blir knapp. Dokumentet må være
   godt nok; demoen må være uimotståelig.
