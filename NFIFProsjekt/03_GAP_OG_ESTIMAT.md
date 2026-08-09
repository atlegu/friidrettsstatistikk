# Gap-analyse og timeestimat

**Versjon:** 1.0 — 09.08.2026

Formålet med dette dokumentet er internt: å vite hva vi faktisk lover før vi lover det.
Estimatene er grunnlaget for prisen i `05_PRISMODELL.md` og for tidsplanen i tilbudet.

---

## 1. Hva vi har i dag (målt i produksjonsbasen 09.08.2026)

| Element | Status |
|---|---|
| Resultater | 1 411 073 — hvorav 1 190 655 fra 2013 og senere |
| Utøvere | 88 016 |
| Stevner | 47 901, tidligste gyldige 06.08.1922, seneste 01.08.2026 |
| Klubber | 2 636 (2 579 med resultater knyttet til seg) |
| Øvelser | 299, med øvelsesspesifikasjoner per aldersklasse |
| Utøverprofiler | I drift, med PB, SB, resultathistorikk, utviklingskurver |
| Klubbsider | I drift, med årsstatistikk, alle-tiders og rekorder |
| Stevnesider | I drift |
| Nasjonal statistikk | I drift: årsstatistikk, alle-tiders, rekorder |
| Sammenligningsverktøy | I drift |
| Administrasjonsverktøy | Delvis: utøver-, klubb-, stevne-, resultat- og importadministrasjon, samt utøversammenslåing |
| Importrammeverk | `import_batches` med validering, status og manuell gjennomgang |
| Aldersklasser | Implementert etter norsk kalenderårsprinsipp |
| Håndtidtaking | Implementert (presisjonsbasert deteksjon, kun løp under 800 m) |
| Regelverksdetaljer | Spydtype 1999, vindregler, hekkehøyde per klasse |

Dette dekker en betydelig del av kravspekkens §7, §9, §10, §11 og §17.

---

## 2. Gap mot kravspekken, med estimat

Timer er reell utviklingstid inkludert test og dokumentasjon, ikke solgte timer.

### Fase 1 og 2 — må være i drift til 01.01.2027

| # | Leveranse | Kravspekk | Timer | Kommentar |
|---|---|---:|---|---|
| B | Kvalitetsnivå A/B/C med regelmotor og filter | §6, §16, §22 | 120–160 | Ikke bare et felt: kriteriene må utledes automatisk der det er mulig (godkjent stevne, lisens, målt løype, tidtaking, distanse) og kunne overstyres manuelt. |
| C | Flaggingsregime | §7 | 100–140 | TR14.1/TR43.1-baneklassifisering, World Rankings, mixed heats, utenlandske utøvere i norsk klubb, WMA-masters, ikke-ratifisert med årsakskode. Håndtidtaking er ferdig. |
| D | Dokumentert JSON-API | §18, §22 | 120–160 | Kuratert API-lag med OpenAPI-dokumentasjon, nøkkelhåndtering og rate limiting. |
| F | Regions- og kretsstatistikk | §10, §22 | 60–90 | Datamodellen mangler kretsdimensjon. Krever klubb-til-krets-mapping fra NFIF. |
| G | Masters, aldersklasserekorder, rekordgodkjenning | §16, §22 | 80–120 | WMA-regelverk, femårsklasser, godkjenningsstatus og dokumentasjon. |
| I | Datavask og kvalitetsverktøy | §23 | 150–200 | Dubletter, navneendringer, klubboverganger, 2 271 utøvere uten kjønn, 133 ugyldige klubbnavn, ugyldige datoer. |
| J | UX, mobil og WCAG 2.1 AA | §17 | 150–200 | Universell utforming er lovkrav, ikke nevnt i kravspekken. |
| K | Utvidede administrasjonsverktøy | Fase 2 | 120–160 | Rekordgodkjenning, kvalitetsnivå, rollestyring, arbeidsflyt for kretser. |
| M | Personvern, sikkerhet, drifts- og systemdokumentasjon | §19, §21 | 80–120 | DPIA, databehandleravtale, driftsdokumentasjon, escrow-oppsett. |
| E0 | Generisk importrammeverk (JSON/XML/CSV, validering, godkjenningskø) | §13 | 100–140 | Fundamentet alle integrasjoner bygger på. Delvis på plass. |
| **Sum** | | | **1 080–1 490** | |

Med ca. 4,5 måneders effektiv tid fra kontraktsstart til 01.01.2027 tilsvarer dette
**halvannet til to årsverk i perioden.** Konklusjon: leveransen er ikke mulig for én
person. Dette tallet er selve begrunnelsen for å knytte til seg utvikler nummer to,
og det er også prisgulvet vårt.

### Integrasjoner — prises som separate opsjoner

| System | Timer | Usikkerhet |
|---|---:|---|
| iSonen / Buypass | 100–150 | Høy. §14 beskriver en fremtidig arbeidsflyt som ennå ikke finnes. |
| OpenTrack | 60–100 | Middels. Har åpent API, men er samtidig konkurrent. |
| FriRes / LiveRes | 80–120 | Høy. Ukjent grensesnitt. |
| EQ Timing | 80–120 | Høy. |
| Ultimate Sport Service | 60–100 | Høy. |
| **Sum** | **380–590** | |

**Prinsipp:** ingen fastpris på integrasjoner før grensesnittet er dokumentert.
Tilbudet skal si dette rett ut, med forbehold om at motparten stiller med API. Det er
også et troverdighetspoeng — den som fastpriser fem ukjente integrasjoner, har ikke
gjort jobben.

### Fase 3 — aktivitet og analyse

| Leveranse | Kravspekk | Timer |
|---|---|---:|
| Aktivitetsmodul: unike deltakere, starter, fullførte, utvikling over tid, fordelt på klubb, krets, aldersgruppe, kjønn og øvelse | §12 | 150–200 |
| Dashboards for forbund og kretser | §12, §23 | 80–120 |
| **Sum** | | **230–320** |

Analysemetodikken finnes allerede i `analyse/trenerartikkel/`. Dette er
produktifisering av noe som er utviklet og validert, ikke forskning fra bunnen.
Det er en reell kostnadsfordel og bør fremheves.

### Utenbaneløp — fase 2/3, veikart kreves innen 31.12.2026

| Leveranse | Kravspekk | Timer |
|---|---|---:|
| Datamodell for løp, løype, måling, tidtaking, arrangør og deltakerstatistikk | §8 | 120–160 |
| Rankinglister for offisielle rekorddistanser | §8, §16 | 80–120 |
| Registrering av deltakelse på ikke-offisielle distanser | §8, §12 | 60–100 |
| Import fra norske tidtakere | §13 | inngår over |
| Presentasjon, filtrering og løpssider | §8, §17 | 100–140 |
| **Sum** | | **360–520** |

§24 krever kun et **troverdig veikart** innen 31.12.2026 dersom løsningen ikke dekker
utenbaneløp fra start. Det er den viktigste enkeltopplysningen i hele kravspekken for
vår tidsplanlegging: vi kan levere et grundig designnotat i tilbudet og bygge i 2027,
uten å bryte noe krav. Ikke overlov her.

### Fase 4 — historisk utvidelse

| Leveranse | Kravspekk | Timer |
|---|---|---:|
| Delvis historikk 2001–2012 | §15 | 100–160 |
| Eldre data, datavask og kvalitetssikring | §15, §23 | 80–160 |
| **Sum** | | **180–320** |

Prises som opsjon. Vi har allerede data tilbake til 1922, men dekningsgraden
pre-2013 er ujevn og må kartlegges før den kan love noe.

---

## 3. Samlet estimat

| Blokk | Timer (lav–høy) |
|---|---:|
| Fase 1 og 2 — kjerne | 1 080–1 490 |
| Integrasjoner (opsjoner) | 380–590 |
| Fase 3 — aktivitet og analyse | 230–320 |
| Utenbaneløp | 360–520 |
| Fase 4 — historikk (opsjon) | 180–320 |
| **Totalt full leveranse** | **2 230–3 240** |

---

## 4. Kjente datakvalitetsproblemer som må lukkes før demo

Disse er små i omfang, men synlige — og synlig rot i en demo ødelegger nettopp det
argumentet vi er sterkest på.

| Problem | Omfang | Prioritet |
|---|---|---|
| Klubbregisteret inneholder startnumre og statuskoder («01», «04-DNS», «0(558)») | 133 poster med sifferstart, hver med under 15 resultater | **Kritisk før demo** — dette er det brukeren selv reagerte på |
| Utøvere uten kjønn | 2 271 av 88 016 (2,6 %) | Høy — gir feil i kjønnsdelte lister |
| Utøvere uten fødselsår | 30 | Lav |
| Ugyldige stevnedatoer i historisk import | Tidligere observert år 0573 | Middels |
| Umappede øvelsesnavn ved import | Løpende | Middels |

Merk at klubbproblemet er et **presentasjonsproblem mer enn et dataproblem**: de
berørte postene har svært få resultater. Løsningen er dels opprydding, dels et filter
i klubboversikten, dels validering i importrutinen slik at det ikke gjenoppstår.
Fiks roten i importen, ikke bare symptomet — det er allerede lærdommen fra
tids- og duplikathåndteringen i prosjektet.
