# Arbeidsplan frem til tilbudsfrist 31.08.2026

**Versjon:** 1.0 — 09.08.2026
**Dager igjen:** 22

Prinsippet gjennom hele planen: **demoen er viktigere enn dokumentet.** Hvis tiden
blir knapp, kutt i tekst — aldri i det NFIF får se og ta på.

---

## Uke 1 (9.–16. august) — beslutninger, kontakt og datavask

Dette er uken som avgjør om vi har et tilbud i det hele tatt.

### Må gjøres først (dag 1–2)

| # | Oppgave | Hvorfor |
|---|---|---|
| 1 | **Avklar utvikler nummer to.** Navn, rolle, tilgjengelighet fra oktober. | Uten dette er tilbudet vesentlig svakere. Se R1. |
| 2 | **Send avklaringsspørsmål til Thor Gjesdal** (se `06_SPORSMAL_TIL_NFIF.md`) og be om et kort møte der vi viser løsningen. | Anskaffelsen er trolig privatrettslig. Relasjon slår formalia. |
| 3 | **Avklar budsjettramme med Magnus Trosdahl.** | Uten dette priser vi i blinde. Se R5. |
| 4 | Beslutt språk i tilbudet. Anbefaling: norsk hoveddokument, engelsk sammendrag på to sider. | Kravspekken er på engelsk; kunden er norsk. |

### Datavask før demo (dag 3–7)

Rekkefølgen er etter hvor synlig problemet er, ikke hvor stort det er.

| # | Oppgave | Estimat |
|---|---|---|
| 5 | Rydd klubbregisteret: 133 poster med sifferstart, DNS/DNF-koder og startnumre. Flytt berørte resultater til riktig klubb der mulig, ellers til «ukjent klubb». | 6–10 t |
| 6 | Legg inn **validering i importrutinen** slik at søppelklubber ikke gjenoppstår. Fiks roten, ikke symptomet. | 4–6 t |
| 7 | Filtrer klubboversikten på klubber med reelle resultater. | 2 t |
| 8 | Kjønn: reduser de 2 271 uten kjønn med autoritative metoder (øvelsesbaserte, navnemønstre). Aldri inferens fra medkonkurrenter. | 8–12 t |
| 9 | Rydd ugyldige stevnedatoer (år 0573 og lignende). | 3–4 t |
| 10 | Gå gjennom forsiden, utøverprofil, klubbside, stevneside og rekordsider med kritisk blikk. Noter alt som ser rotete ut. | 4 t |

### Parallelt (dag 5–7)

| # | Oppgave |
|---|---|
| 11 | Start `04_KRAVSPORING.md`: fyll ut status for hvert eneste punkt i §22 og §23. Denne matrisen styrer resten av skrivearbeidet — den avdekker hva vi ikke kan svare på. |
| 12 | Sett opp NFIF-demoinstans på egen URL, adskilt fra friidrett.live. |
| 12b | **Kjør NM-sammenligningen på alle 56 øvelsesblokker** i `NM 2026 sortert.xlsx` mot vår base. Gir både en prioritert datavaskliste og et tall til tilbudet: hvor stor andel av SRUs manuelle liste vi reproduserer automatisk. Pilot på 100 m kvinner er kjørt — 89 av 101 navn matcher. Se `09_NM_KVALIFISERING.md`. Estimat 10–16 t. |

**Milepæl fredag 14.08:** demoen er presentabel, og vi vet hva vi ikke har.

---

## Uke 2 (17.–23. august) — bygge det som må vises, og skrive

### Demoforsterkning — bare det som er synlig i et møte

Målet er at ingen av kravspekkens **mandatory**-punkter (§22) er ren tekst i tilbudet.
Alt skal ha noe å peke på, om aldri så enkelt.

| # | Oppgave | Estimat |
|---|---|---|
| 13 | **JSON-API v0**: fire–fem endepunkter (utøver, resultat, stevne, klubb, statistikkliste) med enkel dokumentasjon. Trenger ikke være ferdig — det må eksistere. | 16–24 t |
| 14 | **Kvalitetsnivå A/B/C som synlig filter** på statistikklister, foreløpig regelbasert på det vi allerede vet (godkjent stevne, tidtaking, distanse). | 12–16 t |
| 15 | **Eksport til Excel/CSV** fra statistikklister. `xlsx` er allerede i prosjektet. | 6–8 t |
| 16 | **Kretsdimensjon**: enkel klubb-til-krets-mapping og én regionsside, slik at §10 kan demonstreres. | 10–14 t |
| 17 | Én **aktivitetsside** basert på analysen fra `analyse/trenerartikkel/`: aktive utøvere per år, aldersgruppe og kjønn. Dette er §12, og det er vårt sterkeste kort. | 12–16 t |

### Skriving (parallelt)

| # | Kapittel | Kravspekk |
|---|---|---|
| 18 | Teknisk løsning og arkitektur | §21 |
| 19 | Datamodell | §21 |
| 20 | Integrasjonsløsning, med forbehold og opsjonsstruktur | §13, §14, §21 |
| 21 | Brukergrensesnitt, mobil og universell utforming | §17, §21 |
| 22 | Referanseprosjekter: friidrett.live, rekrutteringsanalysen, RAE-forskningen | §21 |
| 22b | **Hovedkapittel: «Mer enn en plattform — NFIFs analyse- og kunnskapsfunksjon».** Plasseres rett etter teknisk løsning, ikke som vedlegg. Se `08_ANALYSE_OG_MEDIETJENESTE.md`. | §12, §23 |
| 22c | Klargjør «56 til Birmingham» (`web/public/EM2026/`) som vedlegg eller demolenke. Oppdater publikasjonsstatus for de vitenskapelige artiklene til august 2026 — aldri mer enn det som faktisk stemmer. | §21 |

**Milepæl søndag 23.08:** alle §22-punkter har noe demonstrerbart, og halve
tilbudsteksten er skrevet.

---

## Uke 3 (24.–30. august) — vedlegg, pris og ferdigstilling

| # | Oppgave | Kravspekk |
|---|---|---|
| 23 | **Vedlegg: veikart utenbaneløp.** Datamodell, kildekartlegging, faseplan. §24 krever kun et troverdig veikart innen 31.12.2026 — dette vedlegget innfrir det allerede ved tilbudsfrist. Prioritert høyt: det er her konkurrentene er svakest. | §8, §24 |
| 24 | **Vedlegg: personvern og sikkerhet.** Behandlingsgrunnlag, databehandleravtale, EU/EØS-lagring, særskilt håndtering av mindreåriges data, DPIA, innsyn og sletting. | §19 |
| 25 | **Vedlegg: risiko og bærekraft.** Bemanning, escrow, exit-klausul, dataoverlevering, SLA, ingen innelåsing. | §21, §22 |
| 26 | **Vedlegg: datamigrering.** Dokumentasjon på at 1 190 655 resultater fra 2013 og senere allerede er importert og validert, med metode og kvalitetsrapport. | §15 |
| 27 | **Vedlegg: rekrutteringsanalyse** — lederrettet sammendrag av «Norsk friidrett 2013–2025». Avklar publiseringshensyn først. | §12, §23 |
| 28 | Tidsplan og faseplan | §20, §21, §24 |
| 29 | Pris, støtte- og vedlikeholdsmodell | §21 |
| 30 | Ferdigstill kravsporingsmatrisen som vedlegg | §22, §23 |
| 31 | **Videogjennomgang av demoen, 3 minutter.** Halve styringsgruppen logger aldri inn. | — |

**Milepæl fredag 28.08:** komplett utkast, klart for gjennomlesing.

---

## Sluttspurt (29.–31. august)

| # | Oppgave |
|---|---|
| 32 | Kritisk gjennomlesing. Les tilbudet som en skeptisk innkjøper som allerede er blitt skuffet av én løsning før. |
| 33 | Korrektur og konsistens: tall, datoer, priser, kapittelhenvisninger. |
| 34 | PDF-produksjon, ryddig forside, innholdsfortegnelse. |
| 35 | Innsending med følgebrev. Tilby konkret et presentasjonsmøte i uke 36. |

Dag 30–31 er ren buffer. Den er ikke arbeidstid, den er forsikring.

---

## Prioriteringsregel hvis vi kommer på etterskudd

Kutt i denne rekkefølgen — nedenfra:

1. Aktivitetsside (17) — kan erstattes av figurer fra rekrutteringsanalysen
2. Kretsdimensjon (16) — kan beskrives i tekst
3. Kvalitetsnivåfilter (14) — kan vises som skisse
4. Engelsk sammendrag
5. Videogjennomgang

Følgende kan **ikke** kuttes: datavask (5–9), NM-sammenligningen (12b), JSON-API v0 (13), analysekapittelet
(22b–22c), veikart utenbaneløp (23), personvernvedlegg (24), risiko- og
bærekraftvedlegg (25), pris (29), kravsporing (30).

---

## Etter innsending

Anskaffelsen slutter ikke ved fristen. Planlegg:

- oppfølgingshenvendelse i uke 36 med tilbud om presentasjon
- beredskap for avklaringsrunde og eventuell forhandling
- svarberedskap på det vi vet vil bli utfordret: bemanning, soliditet og
  integrasjonsforbeholdene
