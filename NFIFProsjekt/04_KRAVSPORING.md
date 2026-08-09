# Kravsporingsmatrise

**Versjon:** 1.0 — 09.08.2026
**Status verifisert mot kodebase og produksjonsbase 09.08.2026**

Denne matrisen har to formål. Internt: å vite nøyaktig hva vi kan love. Eksternt:
den blir vedlegg til tilbudet, fordi den viser at vi har lest kravspekken punkt for
punkt — noe overraskende mange tilbud ikke gjør.

**Statuskoder**
`I DRIFT` — finnes i produksjon i dag ·
`DELVIS` — deler finnes, må ferdigstilles ·
`MANGLER` — må bygges ·
`AVTALE` — løses kontraktuelt, ikke teknisk

---

## §22 Obligatoriske krav

| # | Krav | Status | Kommentar / leveranse |
|---|---|---|---|
| 1 | NFIF eier alle data | AVTALE | Formaliseres i kontrakt: full eksportrett, escrow, exit-klausul. Vurder at NFIF eier skykontoene. |
| 2 | Offisiell statistikkplattform for NFIF | AVTALE | — |
| 3 | Banestatistikk | I DRIFT | 1,41 mill. resultater, 299 øvelser, inne og ute, alle aldersklasser. |
| 4 | Løpsstatistikk (utenbane) | MANGLER | Største enkeltgap. Veikart leveres med tilbudet, jf. §24. |
| 5 | Utøverprofiler | I DRIFT | PB, SB, resultathistorikk, utviklingskurver, klubbhistorikk. |
| 6 | Nasjonal statistikk | I DRIFT | Årsstatistikk, alle-tiders, rekorder. |
| 7 | Klubbstatistikk | I DRIFT | Klubbside med årsstatistikk, alle-tiders og rekorder. |
| 8 | Regionsstatistikk | MANGLER | Kretsdimensjon mangler i datamodellen. Krever klubb-til-krets-mapping fra NFIF. |
| 9 | Stevnesider | I DRIFT | 47 901 stevner med resultatlister og lenker til utøverprofiler. |
| 10 | Historiske data | I DRIFT / DELVIS | 1 190 655 resultater fra 2013 og senere er importert — kravspekkens førsteprioritet. Data finnes tilbake til 1922, men dekningen pre-2013 er ujevn. |
| 11 | Kvalitetsklassifisering av resultater (A/B/C) | MANGLER | Regelmotor, ikke bare et datafelt. Se `03_GAP_OG_ESTIMAT.md` post B. |
| 12 | API-støtte | MANGLER | Ingen API-ruter i dag. JSON-API v0 bygges før tilbudsfrist. |
| 13 | Eksportfunksjonalitet | DELVIS | `xlsx`-biblioteket brukes i dag kun til import. Eksport til Excel/CSV må eksponeres i grensesnittet. |
| 14 | Mobilvennlig løsning | I DRIFT | Responsivt grensesnitt. Merk: WCAG 2.1 AA må dokumenteres i tillegg — se §17. |

**Oppsummert:** åtte av fjorten obligatoriske krav er i drift i dag. Ingen av de
gjenstående er teknisk risikofylte; de er arbeidsmengde.

---

## §23 Ønskede tilleggsfunksjoner

| Krav | Status | Kommentar |
|---|---|---|
| Fullautomatisk resultatimport | DELVIS | Scraper og `import_batches` med validering og manuell godkjenning finnes. Full automatisering avhenger av integrasjonene i §13. |
| Analysemoduler | DELVIS | Finnes som analysekode og publisert analyse, ikke som produktmodul. |
| Grafiske utviklingskurver | I DRIFT | `ProgressionChart`, `ResultsScatterChart`, sammenligningsverktøy. |
| Avansert aktivitetsanalyse | DELVIS | Metodikken er utviklet og validert i «Norsk friidrett 2013–2025». Skal produktifiseres i fase 3. |
| Datavaskverktøy | DELVIS | Utøversammenslåing og administrasjonsverktøy finnes. Utvides i fase 2. |
| Offentlige dashbord | MANGLER | Fase 3. |
| Utvidet historisk statistikk | DELVIS | Fase 4, prises som opsjon. |
| Åpne API-er for partnere | MANGLER | Bygges sammen med §18. |

---

## Utvalgte kapittelkrav

| § | Krav | Status | Merknad |
|---|---|---|---|
| §6 | Kvalitetsnivå A/B/C med filtrering | MANGLER | Kriteriene i nivå A (godkjent stevne, lisens, målt løype, godkjent tidtaking, offisiell distanse, dokumentasjon) må dels utledes automatisk, dels registreres. Krever avklaring med NFIF om hvem som eier vurderingen. |
| §7 | Baneklassifisering TR14.1 / TR43.1 | MANGLER | Krever baneregister med klassifisering per anlegg. |
| §7 | Flagg: innendørs | I DRIFT | `meets.indoor`, `events.indoor`. |
| §7 | Flagg: World Rankings-stevne | MANGLER | |
| §7 | Flagg: mixed heats | MANGLER | Norsk særregel: tillatt i alle løpsøvelser utenom World Ranking-stevner. |
| §7 | Flagg: utenlandske utøvere i norsk klubb | DELVIS | `athletes.nationality` finnes, men brukes ikke i lister. |
| §7 | Flagg: WMA-masters | MANGLER | |
| §7 | Flagg: ikke-ratifisert, med årsakskode | MANGLER | Kodeverket er «TBD» i kravspekken — må avklares med NFIF. |
| §7 | Flagg: håndtidtaking | I DRIFT | Presisjonsbasert deteksjon, kun løp under 800 m. |
| §8 | Utenbaneløp med full metadata | MANGLER | Se veikart-vedlegg. |
| §9 | Navneendring, klubbovergang, dubletthåndtering | DELVIS | `club_memberships` og utøversammenslåing finnes. Navneendringshistorikk mangler. |
| §11 | Godkjennings- og statusinformasjon på stevnesider | DELVIS | Avhenger av §6. |
| §12 | Aktivitets- og deltakerdata | DELVIS | Metodikk validert, produktmodul gjenstår. |
| §13 | Integrasjoner mot fem navngitte systemer | MANGLER | Prises som opsjoner med forbehold om dokumentert API. |
| §14 | Fremtidig iSonen-arbeidsflyt | MANGLER | Kravspekken beskriver en arbeidsflyt som ennå ikke eksisterer. Vi lover forberedt arkitektur, ikke ferdig integrasjon. |
| §15 | Historisk import 2013+ | I DRIFT | Ferdig. Dokumenteres som eget vedlegg. |
| §15 | Historisk import 2001–2012 | DELVIS | Fase 4, opsjon. |
| §16 | Rekorder, aldersklasserekorder, masters, godkjenningsstatus | DELVIS | Norske rekorder og rekordsider finnes. Masters, godkjenningsarbeidsflyt og dokumentasjon mangler. |
| §17 | Filtrering på 11 dimensjoner | DELVIS | Utøver, klubb, alder, kjønn, øvelse, sesong, dato og stevne finnes. Region, distanse og kvalitetsnivå mangler. |
| §18 | Dokumentert JSON-API | MANGLER | |
| §19 | Personvern og sikkerhet | DELVIS | Radnivå-tilgangskontroll og autentisering finnes. DPIA, databehandleravtale og særskilt håndtering av mindreåriges data må på plass. |

---

## Det kravspekken ikke nevner, men som vi tar med

| Tema | Begrunnelse |
|---|---|
| Universell utforming, WCAG 2.1 AA | Lovkrav for norske publikumsrettede nettsteder. §17 nevner bare skjermstørrelser. |
| Særskilt vern av mindreåriges data | Databasen inneholder navn, fødselsdato, klubb og resultathistorikk for barn fra tiårsalderen, publisert åpent. GDPR og NIFs personvernbestemmelser gjelder begge. |
| Beredskap ved topplast | Trafikken topper under NM, Bislett Games og store mosjonsløp. Dimensjonering og SLA må hensynta dette. |
| Exit og ikke-innelåsing | Standardteknologi og full overlevering. Reell forskjell mot en proprietær internasjonal plattform. |
