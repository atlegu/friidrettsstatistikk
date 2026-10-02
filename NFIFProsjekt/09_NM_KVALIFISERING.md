# Case: NM-kvalifiseringslisten — tilbudets beste enkeltbevis

**Versjon:** 1.0 — 09.08.2026
**Kilde:** `NM 2026 sortert.xlsx`, utarbeidet av Jo Nesse, SRU

---

## 1. Hva dokumentet er

Foran hvert NM sendes det ut et regneark med oversikt over alle utøvere som har klart
kvalifiseringskravet. Utgaven for 2026 inneholder:

| | |
|---|---|
| Rader | 2 594 |
| Øvelsesblokker | 56, inkludert para og kappgang |
| Utøveroppføringer | 1 984 |
| Historikk per øvelse | Kvalifiseringskrav, antall kvalifiserte og antall påmeldte, år for år tilbake til 2002 |
| Per utøver | Klubb, fødselsår, årsbeste for hvert år tilbake til 2002, personlig rekord med årstall |
| Per utøver | Matrise over hvilke av de siste ti årene utøveren har stått på listen |
| Merking | Påmeldt, ubekreftet resultat, innendørsresultat, sertifisert gateløp |
| Retting | Sendes på e-post til utarbeiderens private adresse |

Dette er ikke et hobbyprosjekt. Det er en **kritisk forbundsfunksjon**: det er dette
dokumentet utøvere, trenere, klubber og arrangør bruker for å vite hvem som kan stille
til start i et norsk mesterskap. Kvaliteten er høy, og arbeidet fortjener respekt.

Det er også en nøyaktig illustrasjon av kravspekkens §1: en verdifull funksjon som
hviler på frivillige ressurser, vedlikeholdt manuelt, distribuert som vedlegg, med
rettelser samlet inn via én persons private e-post.

---

## 2. Hva som er galt med formen, ikke med arbeidet

| Problem | Konsekvens |
|---|---|
| **Øyeblikksbilde** | Listen er utdatert i det øyeblikket neste stevne er ferdig. I kvalifiseringsperioden kommer det resultater hver helg. |
| **Manuell innsamling** | Utarbeideren har ikke databasetilgang og henter alt for hånd. Det er dobbeltarbeid mot data som allerede finnes strukturert. |
| **Én person** | Faller personen fra, forsvinner funksjonen. |
| **Ingen kobling til påmelding** | Kolonnene «48+2 (21)» — påmeldte, kvalifiserte i annen øvelse, og nye siden i fjor — telles for hånd. |
| **Distribusjon som vedlegg** | Ingen vet hvem som sitter på hvilken versjon. |
| **Ingen kildesporing** | Et resultat i regnearket kan ikke klikkes tilbake til stevnet det ble oppnådd i. |
| **Formatinkonsistens** | Resultater står dels som `12.14`, dels som `12,14`. Uunngåelig ved manuell føring av 1 984 rader. |
| **Historikken er innelåst** | Kvalifiseringskrav og deltakertall 2002–2026 er verdifulle tidsserier som bare finnes i denne ene filen. |

---

## 3. Vi har allerede bygget den automatiske versjonen

`web/src/lib/championship-config.ts` (478 linjer) implementerer kvalifiseringsreglene
fra *Reglement for norske mesterskap 2026*: kravsatser per øvelse og kjønn,
aldersklasseoverstyringer for U20 og U23, regler for om innendørsresultater teller, og
øvelser som kvalifiserer til andre øvelser — for eksempel 5 km gateløp som
kvalifisering til 5000 m, jf. regelendringen fra 2023 som regnearket selv omtaler.

Sidene `/mesterskap` og `/mesterskap/[id]` viser dette i drift.

---

## 4. Kontrollen vi kjørte: 100 meter kvinner

For å teste datagrunnlaget kjørte vi vår base mot regnearket for én øvelse. Kravet er
12,80, kvalifiseringsperioden 01.01.2025–09.07.2026, med vindgrense 2,0 m/s og uten
håndtidtaking.

| | Antall |
|---|---:|
| Utøvere i regnearket | 101 |
| Utøvere i vår base som klarer kravet | 102 |
| Etter aldersgrense på 16 år | 97 |
| **Navn som matcher på begge lister** | **89** |
| Kun i vår base | 8 |
| Kun i regnearket | 12 |

**Åttini av rundt hundre navn stemmer overens** med en uavhengig, manuelt sammenstilt
liste laget fra andre kilder. Det er en ekstern validering av datakvaliteten vår som
er verdt mer enn noen påstand vi kan skrive selv.

### Og avvikene er selve poenget

Da vi gikk gjennom de tjue avvikene, viste nesten alle seg å være **kjente
datakvalitetsproblemer som kravspekken eksplisitt ber plattformen løse** — ikke
feil i noen av listene:

| Avvik | Årsak | Kravspekk |
|---|---|---|
| «Hedda Ensjø» / «Hedda Endsjø» | Skrivemåte | §9 dubletthåndtering |
| «Kajsa Sol Fagerland» / «Kaisa Sol Fagerland» | Skrivemåte | §9 |
| «Thale Bremseth» / «Thale Leirfall Bremset» | Skrivemåte og mellomnavn | §9 |
| «Hanna Murai-Ubby» / «Hannah Rebekah Murai-Ubby» | Navneform | §9 |
| «Lakeri Ertzgaard» / «Astri Ayo Lakeri Ertzgaard» | Fornavn utelatt | §9 |
| **«Thanida Ingebrigtsen» / «Thanida Promwang»** | **Navneendring** | **§9: «shall be able to manage name changes»** |
| Naomi van den Broeck står kun hos oss | Sannsynlig utenlandsk utøver i norsk klubb — egen NM-status | §7 flagging av utenlandske utøvere |
| Tre utøvere født 2011 står kun hos oss eller kun hos ham | Ulik anvendelse av 16-årsgrensen | §6 kvalitetsnivå og regelanvendelse |
| Tre utøvere hos ham uten 2026-resultat | Kvalifisert på 2025-resultat eller i annen øvelse | Regelavklaring |
| Pernille Sina Lund, 12,76, kun hos ham | Mulig manglende resultat i vår base | Reell datajobb for oss |

Dette er den mest verdifulle opplysningen i hele øvelsen: **avvikene er ikke støy, de
er en arbeidsliste.** Én øvelse av 56 avdekket navneendring, dublettvarianter,
nasjonalitetsflagging, aldersregelanvendelse og ett mulig hull i datagrunnlaget.
Kjørt på alle 56 øvelser blir dette en systematisk kvalitetsrevisjon av basen.

> **Handling før tilbudsfrist:** kjør denne sammenligningen på alle 56 øvelsesblokker.
> Underlaget ligger i `underlag/` (`cmp.py`, `nesse_100mK.json`, `ours.txt`). Det gir
> oss to ting samtidig: en prioritert datavaskliste, og et tall vi kan oppgi i
> tilbudet — «vår base reproduserer X prosent av SRUs manuelle liste automatisk».

---

## 5. Hva vi tilbyr i stedet

| I dag | Med plattformen |
|---|---|
| Regneark sendt ut noen ganger i året | Kvalifiseringsstatus oppdatert i det resultatet importeres |
| Utøveren venter på neste utsendelse | Utøveren ser på egen profil hvilke øvelser hun er kvalifisert i, og hvor mye som mangler i de øvrige |
| Klubben leter i et regneark | Klubbsiden viser klubbens kvalifiserte |
| Påmeldte telles for hånd | Kobles automatisk mot påmelding fra iSonen (§13, §14) |
| Ingen kildesporing | Hvert resultat lenker til stevnet det ble oppnådd i |
| Historikken finnes i én fil | Kvalifiseringskrav og deltakertall 2002–2026 blir en varig, søkbar tidsserie |
| Ingen konsekvensanalyse | **Simulering: «hvor mange kvalifiserer hvis kravet endres fra 12,80 til 12,75?»** |
| Rettinger på privat e-post | Registrert avviksbehandling med sporing |
| Kun regneark | Eksport til Excel — i samme format, som nedlasting i stedet for som arbeid |

Simuleringspunktet fortjener en egen setning i tilbudet. Regnearket dokumenterer selv
at **styret i NFIF justerte kvalifiseringskravene i 2023**, og at øvelsesutvalget for
yngre utøvere er endret med den konsekvens at «færre utøvere nå vil oppnå NM-kravene».
Slike vedtak fattes i dag uten mulighet til å regne på virkningen på forhånd. Med
databasen kan konsekvensen beregnes før vedtaket fattes, ikke observeres to år etter.

---

## 6. Hvordan dette skal formuleres i tilbudet

Dette er et politisk følsomt punkt. Jo Nesse og SRU har gjort denne jobben i årevis,
de er respektert i miljøet, og de vil ha innflytelse på hvem NFIF velger. **Et tilbud
som fremstår som om vi skal erstatte dem, kan koste oss kontrakten.**

Riktig innramming:

> «Kvalifiseringsoversikten som SRU utarbeider foran hvert NM, er en av de mest brukte
> og mest verdifulle tjenestene i norsk friidrett. Vårt mål er ikke å erstatte det
> arbeidet, men å fjerne det manuelle i det. Regelverket og de faglige vurderingene
> skal fortsatt eies av SRU. Plattformen skal gjøre innsamlingen, sammenstillingen og
> distribusjonen — kontinuerlig, sporbart og med Excel-eksport i det formatet miljøet
> allerede kjenner.»

Konkret foreslår vi at SRU får en definert rolle som fagansvarlig for regelverk og
kvalitetsvurderinger i løsningen. Det er både faglig riktig, og det gjør et potensielt
motstandsmiljø til en alliert. Se R7 i `01_STRATEGI.md`.

---

## 7. Plass i tilbudet

Dette caset bør stå tidlig i tilbudsdokumentet, som konkret eksempel rett etter
innledningen. Grunnen er enkel: det er den eneste delen av tilbudet der NFIF kjenner
igjen sin egen hverdag, ser problemet beskrevet presist, og får løsningen demonstrert
i samme åndedrag.

En internasjonal leverandør som ikke kjenner norske mesterskapsregler, SRU eller dette
regnearket, kan ikke skrive dette kapittelet.
