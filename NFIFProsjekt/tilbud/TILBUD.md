# Ny statistikk- og aktivitetsplattform for norsk friidrett

## Tilbud fra Athlete Mindset AS

**Til:** Norges Friidrettsforbund
**Kontaktpersoner hos NFIF:** Thor Gjesdal (teknisk), Magnus Trosdahl (kommersielt)
**Tilbudsfrist:** 31.08.2026
**Dato:** 31.08.2026
**Versjon:** 1.0

---

> **STATUS: UTKAST — PRIS IKKE UTFYLT.**
> Kapittel 12 står med struktur, men uten tall. Punkter merket `‹AVKLARES›`
> må fylles ut eller strykes før dokumentet sendes. Se sjekklisten i
> `../02_ARBEIDSPLAN.md`.

---

# Sammendrag

Norsk friidrett har siden 2013 hatt en verdifull statistikktjeneste bygget på
frivillig innsats. Kravspesifikasjonen slår fast at modellen ikke lenger er
bærekraftig. Det NFIF nå kjøper, er ikke først og fremst programvare — det er
sikkerheten for at statistikkfunksjonen finnes også om fem år, uavhengig av
enkeltpersoners kapasitet.

Athlete Mindset AS tilbyr en plattform som allerede er i drift, med norske data i.

| | |
|---|---:|
| Resultater i basen | **1 922 634** |
| Herav fra 2013 og senere — kravspekkens §15 førsteprioritet | **1 701 902** |
| Utøvere | 87 872 |
| Stevner | 48 494, fra 06.08.1922 til i dag |
| Utøvere med resultater fra 2013 og senere | 59 131 |
| Klubber med registrerte resultater | 2 428 |
| Øvelser med regelverksspesifikasjon per aldersklasse | 302 |

*Tall hentet fra produksjonsbasen 31.08.2026.*

Migrering av historiske data er normalt den dyreste og mest risikofylte posten i
en anskaffelse som denne. Hos oss er den gjennomført. Det er grunnen til at vi
kan love en løsning i drift for alle baneresultater innen 01.01.2027 uten
forbehold — vi skal ferdigstille, ikke bygge fra bunnen.

**Åtte av fjorten obligatoriske krav i §22 er i drift i dag.** De seks
gjenstående er arbeidsmengde, ikke teknisk risiko. Kravsporingen ligger i
vedlegg A og B.

I tillegg tilbyr vi noe en ren plattformleverandør ikke kan tilby: **et
fagmiljø som kan lese databasen.** Vi har allerede levert mesterskapsanalyser,
en bredde- og rekrutteringsanalyse av norsk friidrett 2013–2025, og
fagfellevurdert forskning på det samme datagrunnlaget. NFIF får ikke bare en
database — NFIF får analysemiljøet som hører til.

---

# 1. Hva vi har forstått at NFIF skal løse

Kravspesifikasjonen har 24 kapitler. Bak dem ligger tre spørsmål som avgjør om
en leverandør er riktig:

**Kan løsningen være i drift for alle baneresultater innen 01.01.2027?**
Fra kontraktsinngåelse i september er det knapt fire måneder. En leverandør som
skal bygge plattformen og deretter migrere over 1,7 millioner resultater, rekker
det ikke. Vi er ferdige med migreringen. Se kapittel 8.

**Finnes leverandøren fortsatt i 2031?**
§1 sier rett ut at dagens løsning ikke lar seg vedlikeholde med de frivillige
ressursene som finnes. NFIF er brent på personavhengighet, og skal ikke kjøpe
den på nytt i ny innpakning. Vi tar dette opp uoppfordret i kapittel 9, fordi
det er den innvendingen vi selv mener er mest berettiget.

**Hva koster det, og hva får forbundet igjen?**
NFIF har drevet dette på dugnad i tretten år. Vi mener kostnaden må forsvares
med mer enn drift av en nettside, og har derfor bygget analysetjenesten inn i
grunnavtalen fremfor å selge den separat. Se kapittel 4 og 12.

Dette dokumentet er strukturert etter disse spørsmålene, ikke etter
kravspekkens kapittelnummerering. Punkt-for-punkt-dekningen finnes i vedlegg A
og B.

---

# 2. Et konkret eksempel: NM-kvalifiseringslisten

Vi begynner med noe NFIF kjenner igjen fra egen hverdag.

Foran hvert NM sendes det ut et regneark med oversikt over alle utøvere som har
klart kvalifiseringskravet. Utgaven for 2026, utarbeidet av Jo Nesse i SRU,
inneholder 2 594 rader, 56 øvelsesblokker og 1 984 utøveroppføringer, med
kvalifiseringskrav og deltakertall år for år tilbake til 2002.

Dette er ikke et hobbyprosjekt. Det er en kritisk forbundsfunksjon — dokumentet
utøvere, trenere, klubber og arrangører bruker for å vite hvem som kan stille
til start i et norsk mesterskap. Kvaliteten er høy, og arbeidet fortjener
respekt.

Det er samtidig en presis illustrasjon av §1: en verdifull funksjon som hviler
på frivillige ressurser, vedlikeholdes manuelt, distribueres som e-postvedlegg,
og der rettelser samles inn via én persons private adresse. Listen er utdatert
i det øyeblikket neste stevne er ferdig.

## 2.1 Vi har bygget den automatiske versjonen

Kvalifiseringsreglene fra *Reglement for norske mesterskap 2026* er implementert
i løsningen: kravsatser per øvelse og kjønn, aldersklasseoverstyringer for U20
og U23, regler for om innendørsresultater teller, og øvelser som kvalifiserer
til andre øvelser — for eksempel 5 km gateløp som kvalifisering til 5000 m, jf.
regelendringen fra 2023. Sidene `/mesterskap` er i drift.

## 2.2 Kontrollen vi kjørte

For å teste datagrunnlaget kjørte vi vår base mot regnearket for 100 meter
kvinner. Krav 12,80, kvalifiseringsperiode 01.01.2025–09.07.2026, vindgrense
2,0 m/s, uten håndtidtaking.

| | Antall |
|---|---:|
| Utøvere i regnearket | 101 |
| Utøvere i vår base som klarer kravet, etter 16-årsgrensen | 97 |
| **Navn som matcher på begge lister** | **89** |
| Kun i vår base | 8 |
| Kun i regnearket | 12 |

Åttini av rundt hundre navn stemmer overens med en uavhengig, manuelt
sammenstilt liste laget fra andre kilder. Det er en ekstern validering av
datakvalitet som er verdt mer enn en påstand vi kan skrive selv.

**Avvikene er det egentlige funnet.** Da vi gikk gjennom de tjue avvikene, viste
nesten alle seg å være nøyaktig de datakvalitetsproblemene kravspesifikasjonen
ber plattformen løse:

| Avvik | Årsak | Krav |
|---|---|---|
| «Hedda Ensjø» / «Hedda Endsjø» | Skrivemåte | §9 dubletthåndtering |
| «Thale Bremseth» / «Thale Leirfall Bremset» | Mellomnavn | §9 |
| «Lakeri Ertzgaard» / «Astri Ayo Lakeri Ertzgaard» | Fornavn utelatt | §9 |
| **«Thanida Ingebrigtsen» / «Thanida Promwang»** | **Navneendring** | **§9 «shall be able to manage name changes»** |
| Utøver kun i vår base | Sannsynlig utenlandsk utøver i norsk klubb | §7 flagging |
| Tre utøvere født 2011 | Ulik anvendelse av 16-årsgrensen | §6 kvalitetsnivå |
| Ett resultat kun i regnearket | Mulig hull i vårt datagrunnlag | Vår arbeidsliste |

Én øvelse av 56 avdekket navneendring, dublettvarianter, nasjonalitetsflagging,
aldersregelanvendelse og ett hull hos oss. Kjørt på alle 56 blir dette en
systematisk kvalitetsrevisjon av basen — og det er slik vi mener datavask skal
gjøres: mot en uavhengig kilde, ikke ved å stole på seg selv.

## 2.3 Hva vi tilbyr, og hva vi ikke rører

| I dag | Med plattformen |
|---|---|
| Regneark sendt ut noen ganger i året | Status oppdatert i det resultatet importeres |
| Utøveren venter på neste utsendelse | Utøveren ser på egen profil hva hun er kvalifisert i, og hva som mangler |
| Klubben leter i regnearket | Klubbsiden viser klubbens kvalifiserte |
| Påmeldte telles for hånd | Kobles mot påmelding fra iSonen (§13, §14) |
| Ingen kildesporing | Hvert resultat lenker til stevnet det ble oppnådd i |
| Historikken finnes i én fil | Kravsatser og deltakertall 2002–2026 blir en varig, søkbar tidsserie |
| Ingen konsekvensanalyse | Simulering: «hvor mange kvalifiserer hvis kravet endres fra 12,80 til 12,75?» |
| Rettinger på privat e-post | Registrert avviksbehandling med sporing |
| Kun regneark | Eksport til Excel i samme format — som nedlasting, ikke som arbeid |

Simuleringspunktet fortjener en egen setning. Regnearket dokumenterer selv at
NFIFs styre justerte kvalifiseringskravene i 2023, og at endret øvelsesutvalg
for yngre utøvere får som konsekvens at færre nå oppnår NM-kravene. Slike vedtak
fattes i dag uten mulighet til å regne på virkningen på forhånd. Med databasen
kan konsekvensen beregnes før vedtaket fattes, ikke observeres to år etter.

**Én presisering:** vårt mål er ikke å erstatte det arbeidet SRU gjør, men å
fjerne det manuelle i det. Regelverket og de faglige vurderingene skal fortsatt
eies av SRU. Vi foreslår at SRU får en definert rolle som fagansvarlig for
regelverk og kvalitetsvurderinger i løsningen. Plattformen skal gjøre
innsamlingen, sammenstillingen og distribusjonen — kontinuerlig, sporbart, og
med eksport i det formatet miljøet allerede kjenner.

---

# 3. Teknisk løsning

*Besvarer §21: teknisk løsning, datamodell, integrasjonsløsning, brukergrensesnitt.*

## 3.1 Arkitektur

| Lag | Teknologi | Begrunnelse |
|---|---|---|
| Database | PostgreSQL | Bransjestandard, åpen kildekode, ingen lisensbinding |
| Applikasjonsplattform | Supabase (managed PostgreSQL, autentisering, radnivå-tilgangskontroll, lagring) | Kan flyttes til hvilken som helst PostgreSQL-drift |
| Frontend | Next.js (React, TypeScript), serverside-rendret | Rask, søkemotorvennlig, mobilvennlig fra bunnen |
| Import og databehandling | Python | Etablert i drift mot dagens kilder |
| Drift | Skytjeneste innenfor EU/EØS | Personvernkrav, jf. kapittel 7 |

**Et bevisst valg:** Vi bruker alminnelig, godt dokumentert teknologi. Ingen
egenutviklet database, ingen proprietære formater, ingen komponenter bare vi
forstår. Konsekvensen er at løsningen kan overtas av enhver kompetent
leverandør, uten omskriving. Det er en reell forskjell fra en proprietær
plattform, og det er en del av vår risikohåndtering — se kapittel 9 og 11.

## 3.2 Datamodell

Kjernen er i drift i dag:

| Enhet | Innhold |
|---|---|
| `athletes` | Navn, fødselsdato/-år, kjønn, nasjonalitet, klubbtilhørighet, klubbhistorikk |
| `results` | Prestasjon, vind, plassering, dato, tidtakingsmetode, kildemarkør, kobling til utøver, øvelse, stevne og klubb |
| `meets` | Stevne med dato, sted, arrangør, inne/ute, sesong |
| `events` | 302 øvelser med spesifikasjon per aldersklasse — redskapsvekt, hekkehøyde, spydtype |
| `clubs` | Klubb med type og sted |
| `club_memberships` | Klubbtilhørighet over tid, jf. §9 klubboverganger |
| `seasons` | Innendørs- og utendørssesong, med norsk sesongdefinisjon |
| `import_batches` | Importsporing med validering, status og manuell gjennomgang |

**Norske regler er implementert, ikke tilpasset i etterkant:**

- **Aldersklasser etter kalenderår.** Alder = konkurranseår − fødselsår, uten
  justering for om bursdagen har vært. En utøver født i 1999 er G14 i hele 2013.
  Dette er en norsk særregel som gir feil aldersklasse hvis den behandles som
  eksakt alder.
- **Håndtidtaking**, med presisjonsbasert deteksjon, og kun for løpsøvelser
  under 800 m — der distinksjonen faktisk gjelder. 18 769 resultater er i dag
  merket som håndtidtatt.
- **Vindregler**, med 677 100 resultater med registrert vindmåling.
- **Spydtype fra 1999**, hekkehøyde og redskapsvekt per aldersklasse.

Gjenstår å bygge inn i modellen: kretsdimensjon (§10), baneklassifisering etter
TR14.1/TR43.1 (§7), kvalitetsnivå A/B/C (§6), og datamodellen for utenbaneløp
(§8). Disse er beskrevet i henholdsvis kapittel 3.5, 5 og 8.

### Kildetrofasthet som prinsipp

Ett designvalg fortjener omtale, fordi det sier noe om hvordan vi arbeider.
Kilden vi importerer fra henger av og til markører på selve resultatverdien —
`20.37.52mx`, `4.43 L`, `7.83A`. Kildesiden har ingen tegnforklaring. `mx` er
etter alt å dømme blandet heat, altså nøyaktig det §7 ber om å flagge.

Vi tolker dem likevel ikke. Markøren lagres ordrett i et eget felt, med den
opplysningen at betydningen ikke er bekreftet. Når NFIF bekrefter kodeverket,
tolkes de i ett strøk — men vi setter ikke en gjetning inn i et datafelt der den
senere leses som et faktum. Det samme prinsippet gjelder de ikke-ratifiserte
resultatene i §7, der kravspekken selv sier at kodeverket er «TBD».

## 3.3 Brukergrensesnitt

I drift i dag: utøverprofiler med personlige rekorder, sesongbeste,
resultathistorikk, utviklingskurver og klubbhistorikk; klubbsider med
årsstatistikk, alle-tiders-lister og klubbrekorder; stevnesider med
resultatlister og lenker til utøverprofiler; nasjonal årsstatistikk,
alle-tiders-lister og rekordoversikter; og et sammenligningsverktøy mellom
utøvere.

Grensesnittet er responsivt og fungerer på mobil, nettbrett og desktop, jf. §17.

**Filtrering.** §17 lister elleve dimensjoner. Åtte er i drift i dag: utøver,
klubb, alder, kjønn, øvelse, sesong, dato og stevne. Tre gjenstår: region,
distanse og kvalitetsnivå — alle tre avhenger av datamodellutvidelser som er
planlagt i fase 1 og 2.

**Universell utforming.** §17 nevner bare skjermstørrelser. Vi tar likevel
WCAG 2.1 AA inn som eksplisitt leveranse. Publikumsrettede norske nettsteder er
underlagt kravene til universell utforming av IKT — dette er et lovkrav, ikke en
ekstravaganse, og en plattform som er offisiell kanal for et særforbund bør
oppfylle det.

## 3.4 API og eksport

*§18, §22.*

Vi leverer et dokumentert JSON-API med OpenAPI-spesifikasjon, nøkkelhåndtering,
rate limiting og tilgangsstyring per konsument. API-et dekker utøverdata,
resultater, stevner, klubbstatistikk, regionsstatistikk, statistikklister og
aktivitetsdata.

Eksport til Excel og CSV eksponeres i grensesnittet på alle lister, ikke bare
via API.

**Vår modell, sagt rett ut:** Alle data eies av NFIF. All statistikk er fritt
tilgjengelig for utøvere, klubber, trenere, media og publikum. NFIF kan når som
helst eksportere, gjenbruke og videreformidle datagrunnlaget uten begrensninger
fra vår side. Vi tar aldri betalt av forbundets medlemmer for tilgang til
forbundets egne tall.

## 3.5 Kvalitetsnivåer og flagging

*§6, §7, §16.*

### Kvalitetsnivå A/B/C

Dette er en regelmotor, ikke et datafelt. Kriteriene i nivå A — godkjent og
terminlistet stevne, gyldig lisens, målt løype, godkjent tidtaking, offisiell
distanse, nødvendig dokumentasjon — utledes automatisk der grunnlaget finnes,
og registreres manuelt der det ikke gjør det. Hvert resultat får nivå,
begrunnelse og sporing av hvem som har satt eller overstyrt det.

Brukere kan filtrere statistikken på nivå, jf. §6.

`‹AVKLARES med NFIF›` Hvem eier vurderingen når kriteriene ikke lar seg utlede
automatisk — forbundet sentralt, kretsen, eller stevnearrangøren? Dette er en
arbeidsflyt- og rollespørsmål mer enn et teknisk, og vi vil ikke låse det uten
NFIFs syn.

### Flagging

| Flagg | Status i dag |
|---|---|
| Innendørs / overbygd anlegg | I drift |
| Håndtidtaking i løpsøvelser | I drift |
| Utenlandske utøvere i norsk klubb | Delvis — nasjonalitet er registrert, må eksponeres i lister |
| Bane etter TR14.1 / TR43.1 | Bygges. Krever baneregister med klassifisering per anlegg. |
| World Rankings-stevne | Bygges |
| Blandede heat | Bygges. Norsk særregel: tillatt i alle løpsøvelser utenom World Ranking-stevner. |
| WMA-masters | Bygges |
| Ikke-ratifisert, med årsakskode | Bygges. `‹AVKLARES›` Kodeverket er «TBD» i kravspekken. |

## 3.6 Integrasjoner og dataimport

*§13, §14.*

Vi bygger først et generisk importrammeverk som tar imot JSON, XML, CSV og
Excel, med skjemavalidering, dublettkontroll, godkjenningskø og full sporing av
hvilken kilde hvert resultat kom fra. Alle integrasjoner bygger på dette. Et
delvis rammeverk er i drift i dag.

Deretter integreres kildene i den prioritetsrekkefølgen §13 angir: API først,
strukturerte filer deretter, Excel/CSV som tredje valg, og manuell behandling
kun som siste utvei.

**Et forbehold vi mener er nødvendig å ta:** Vi fastpriser ikke integrasjoner mot
systemer vi ikke har sett grensesnittdokumentasjonen til. iSonen, OpenTrack,
FriRes/LiveRes, EQ Timing og Ultimate Sport Service prises som separate
opsjoner med timepott, med forbehold om at motparten stiller med et dokumentert
API. En leverandør som fastpriser fem ukjente integrasjoner, har ikke gjort
jobben — og regningen kommer uansett, bare senere og som en tvist.

**Om §14, fremtidig iSonen-arbeidsflyt:** Kravspekken beskriver en arbeidsflyt
som ennå ikke finnes. Vi lover forberedt arkitektur og deltakelse i
spesifikasjonsarbeidet, ikke en ferdig integrasjon mot noe som ikke er
definert.

---

# 4. Mer enn en plattform: NFIFs analyse- og kunnskapsfunksjon

En plattform er infrastruktur. Den blir sammenlignet på funksjonspunkter og
pris. Et analysemiljø er noe annet — det er en kapasitet, og den kan ikke skrus
på som en modul.

> **NFIF får ikke bare en database. NFIF får et fagmiljø som kan lese den.**

Dette er ikke en idé vi presenterer. Det er en praksis vi dokumenterer.

## 4.1 Mesterskapsanalyse

«56 til Birmingham» — en ferdig analyse av hele den norske EM-troppen 2026,
bygget direkte på databasen: lagsammensetning, kvinner og menn hver for seg,
uttaksveien inn, terrengløps-EM, persutvikling i forkant, nivåvurdering mot
europeisk og internasjonal ranking, og øvelsesprofil for troppen.

Dette er produktet en kommunikasjonsavdeling og en presselosje trenger uken før
et mesterskap, og som ingen rekker å lage manuelt. Vedlagt som vedlegg C.

## 4.2 Bredde- og rekrutteringsanalyse

«Norsk friidrett 2013–2025» — analyse av samtlige registrerte resultater i
perioden. Sentralt funn: aktive utøvere i alderen 10–19 år falt fra 8 745 i 2019
til 6 418 i 2025, en nedgang på 27 prosent, nesten utelukkende konsentrert i de
yngste årsklassene, mens seniorgruppen er stabil.

§12 sier at aktivitetsdata er «particularly important for Norwegian Athletics'
strategic work related to recruitment and membership development». Vi har
allerede gjort den analysen.

## 4.3 Forskning på datagrunnlaget

`‹AVKLARES — oppgi korrekt publiseringsstatus per 31.08.2026, aldri mer enn det
som faktisk er tilfelle›`

Fagfellevurdert arbeid basert på samme datagrunnlag, om relativ alderseffekt i
norsk friidrett fra 10 til 25 år, og om prestasjonsutvikling hos unge utøvere.
I tillegg idrettsfaglige og idrettsøkonomiske arbeider om reaksjonstid og
tyvstartregelen, skoteknologi og talentallokering.

Poenget dette beviser: databasen holder ikke bare presentasjonskvalitet, den
holder forskningskvalitet — verifisert av uavhengige fagfeller.

## 4.4 Tjenestekatalog

| Tjeneste | Innhold | Frekvens |
|---|---|---|
| Mesterskapspakke | Troppanalyse, rankingposisjon, formkurver, historisk sammenligning, uttaksstatistikk. Som nettside og som pressemateriell. | Før NM, EM, VM, OL, EM terrengløp |
| Presse- og kringkastingsstøtte | Faktapakker, rekordvarsler, «dette kan skje i dag»-notater | Under mesterskap |
| Årsrapport for norsk friidrett | Aktivitet, rekruttering, frafall, bredde og topp, per krets og aldersklasse | Årlig |
| Krets- og klubbrapporter | Samme analyse brutt ned lokalt, som verktøy for utviklingsarbeid | Årlig eller på bestilling |
| Strategisk analyse på bestilling | Underlag til NFIFs egne prosesser: rekrutteringstiltak, terminliste, klasseinndeling, regelverksvirkninger | Ved behov |
| Forskningssamarbeid | Databasen som forskningsinfrastruktur, med NFIF kreditert | Løpende |

To mesterskapspakker og én årsrapport per år inngår i grunnavtalen. Se
kapittel 12.

## 4.5 Et forbehold vi tar opp selv

Vi vil samtidig være NFIFs leverandør og et uavhengig forskningsmiljø som
publiserer funn om norsk friidrett. Noen av de funnene er ubehagelige for
oppdragsgiveren — rekrutteringsgrunnlaget har krympet med en fjerdedel, og
relativt yngre barn faller fra før de rekker å konkurrere.

> Athlete Mindset AS forbeholder seg full akademisk uavhengighet i
> forskningsarbeid basert på datagrunnlaget, uavhengig av kundeforholdet. Vi
> mener det er en styrke for NFIF: en analysepartner som bare bekrefter det
> oppdragsgiveren ønsker å høre, er ingen analysepartner.

Vi foreslår at avtalen regulerer publiseringsrett, kreditering av NFIF,
forhåndsvarsling til forbundet før publisering av funn som angår dem, og at
forhåndsvarsel ikke gir vetorett. Dette er standard i forskningssamarbeid.

---

# 5. Utenbaneløp — veikart

*§8, §12, §24.*

Dette er vårt største enkeltgap, og vi sier det rett ut. Løsningen dekker i dag
banestatistikk. Utenbaneløp må bygges.

§24 krever et troverdig veikart innen 31.12.2026 dersom løsningen ikke dekker
utenbaneløp fra start. Dette kapittelet er det veikartet, og vi leverer det med
tilbudet fremfor å komme tilbake til det.

## 5.1 Hvorfor utenbaneløp er en annen oppgave

§5 peker selv på kjernen: for utenbaneløp oppfyller ikke alle arrangementer,
distanser og løyper de samme tekniske kravene. Et 10 km gateløp på sertifisert
løype og et terrengløp på en uoppmålt runde er begge reell aktivitet, men bare
det ene kan rangeres mot en rekord.

Skillet mellom **prestasjonsstatistikk**, **rekorder** og **registrert
aktivitet** er derfor ikke en presentasjonsdetalj — det er selve datamodellen.
Det er også grunnen til at kvalitetsnivåene i §6 må bygges før utenbaneløpene,
ikke etter.

## 5.2 Leveranseplan

| Trinn | Innhold | Periode |
|---|---|---|
| 1 | Datamodell for løp, løype, oppmåling, tidtaking, arrangør og deltakerstatistikk. All metadata i §8: distanse, arrangementstype, løypetype, oppmålingsstatus, tidtakingsmetode, arrangør, sted, dato, antall påmeldte, antall fullførte, kjønns- og aldersfordeling, klubbtilhørighet. | Q1 2027 |
| 2 | Import fra norske tidtakere — EQ Timing og Ultimate Sport Service prioritert, som de største datakildene | Q1–Q2 2027 |
| 3 | Rankinglister for offisielle rekorddistanser: 3 km, 5 km, 10 km, halvmaraton, maraton | Q2 2027 |
| 4 | Registrering av deltakelse på ikke-offisielle distanser, ultraløp, stafetter, terreng-, motbakke- og fjelløp | Q2 2027 |
| 5 | Løpssider, filtrering og presentasjon, integrert med utøverprofilene slik at bane og utenbane vises samlet | Q3 2027 |

Vi anbefaler at NFIF ikke kjøper dette som fastpris nå. Datakildene er mange og
ujevne, og de norske tidtakerselskapenes grensesnitt er ikke kartlagt. En pris
satt i august 2026 vil enten være for høy, eller sprekke.

`‹AVKLARES med NFIF›` Hvilke løpsarrangementer regnes som «approved athletics
events» i §2? Omfanget av utenbanedelen avhenger helt av om dette betyr
terminlistede løp, alle løp med lisensierte deltakere, eller all mosjonsløping.

---

# 6. Historiske data

*§15.*

## 6.1 Førsteprioriteten er levert

§15 setter full dybde fra 2013 og senere som førsteprioritet. **1 701 902
resultater fra 2013 og senere er importert, normalisert og søkbare i dag**, fra
26 910 stevner og 59 131 utøvere.

Dette tallet er verdt en kommentar, fordi det illustrerer hvordan vi arbeider
med datakvalitet.

## 6.2 Et etterslep vi fant og tettet

Importrutinen vår regnet lenge et stevne som ferdig importert hvis det hadde mer
enn ti resultater. Delvis importerte stevner ble derfor aldri hentet på nytt.
Feilen ble oppdaget da én utøver savnet ett resultat: et innendørs høydehopp.

Vi bygget derfor en kontrollmodus som teller resultater mot kilden stevne for
stevne, og kjørte den mot samtlige sesonger fra 2013 til 2026. Så godt som
hvert eneste stevne viste seg å være ufullstendig. «Hvam, Norgeslekene» hadde
188 resultater i basen mot 539 i kilden — hele øvelser manglet.

Basen vokste fra 1 418 058 til 1 922 634 resultater. **Over en halv million
resultater ble hentet inn.**

Vi tar dette med i et tilbud fordi det sier mer om leverandøren enn et
kvalitetsløfte gjør: feilen ble funnet fordi vi undersøkte ett savnet
høydehopp, årsaken ble rettet i importlogikken fremfor med et
opprydningsskript, og kontrollen kjøres nå rutinemessig.

## 6.3 Eldre data

Vi har allerede data tilbake til 06.08.1922, men dekningen før 2013 er ujevn —
historiske lister er ofte begrenset til resultater over visse terskler, og er
ikke fulldybde.

Vi vil derfor ikke love en dekningsgrad for perioden 2001–2012 før den er
kartlagt. Vi foreslår i stedet at fase 4 starter med en kartleggingsleveranse:
hvilke kilder finnes, hvilken dybde har de, og hva koster full import. Deretter
kan NFIF ta et opplyst valg. Prises som opsjon.

---

# 7. Personvern, sikkerhet og universell utforming

*§19, §17.*

## 7.1 Personvern for mindreårige

Databasen inneholder navn, fødselsdato, klubb og full resultathistorikk for barn
helt ned i tiårsalderen, publisert åpent. Dette er GDPR-relevant på et annet
nivå enn seniorstatistikk, og NIFs egne personvernbestemmelser kommer i tillegg.

Kravspesifikasjonen nevner det ikke. Vi mener det er det viktigste
personvernspørsmålet i hele anskaffelsen, og foreslår konkret:

- Behandlingsgrunnlag og databehandleravtale på plass fra dag én, med NFIF som
  behandlingsansvarlig og Athlete Mindset AS som databehandler
- All lagring og behandling innenfor EU/EØS
- Vurdering av personvernkonsekvenser (DPIA) som del av leveransen, ikke som
  noe som kommer etterpå
- Differensiert eksponering for de yngste årsklassene — for eksempel fødselsår i
  stedet for full fødselsdato offentlig, med full dato kun tilgjengelig internt
- Dokumentert rutine for innsyn, retting og sletting, med definert
  saksbehandlingstid

`‹AVKLARES med NFIF›` Punktet om differensiert eksponering er et forbundsvedtak,
ikke et teknisk valg. Vi bygger det NFIF bestemmer, men mener spørsmålet må
stilles.

## 7.2 Sikkerhet

Autentisering og radnivå-tilgangskontroll er i drift. Rollestyring for
forbund, krets, klubb og arrangør bygges i fase 2. Kryptering i transitt og
hvile, loggføring av administrative endringer, og regelmessig sikkerhetskopi med
dokumentert gjenopprettingsrutine.

## 7.3 Beredskap ved topplast

Trafikken topper under NM, Bislett Games og de store mosjonsløpene. Løsningen
dimensjoneres for dette, og vi foreslår at det avtales særskilt beredskap under
mesterskapshelger — der responstid er noe annet enn i en vanlig uke.

---

# 8. Leveranseplan

*§21 tidsplan, §20 faser, §24 frister.*

## 8.1 Frem til 01.01.2027

§24 krever en operativ løsning som dekker minst alle baneresultater innen
01.01.2027. Under er det som gjenstår for å oppfylle det.

| Leveranse | Krav | Frist |
|---|---|---|
| Kvalitetsnivå A/B/C med regelmotor og filtrering | §6, §16, §22 | Nov 2026 |
| Flaggingsregime: bane TR14.1/TR43.1, World Rankings, blandede heat, utenlandske utøvere, WMA, ikke-ratifisert | §7 | Des 2026 |
| Dokumentert JSON-API med OpenAPI | §18, §22 | Des 2026 |
| Eksport til Excel/CSV eksponert i grensesnittet | §22 | Nov 2026 |
| Regions- og kretsstatistikk | §10, §22 | Des 2026 |
| Masters, aldersklasserekorder, rekordgodkjenning | §16, §22 | Des 2026 |
| Generisk importrammeverk | §13 | Nov 2026 |
| Datavask og kvalitetsverktøy | §23 | Løpende |
| WCAG 2.1 AA-samsvar, dokumentert | §17 | Des 2026 |
| Personvern: DPIA, databehandleravtale, driftsdokumentasjon | §19, §21 | Des 2026 |
| Veikart utenbaneløp — levert med dette tilbudet | §24 | Levert |

**Kritisk avhengighet:** Kretsstatistikk krever en klubb-til-krets-mapping fra
NFIF. Vi kan ikke utlede kretstilhørighet fra klubbnavn med tilstrekkelig
sikkerhet. Vi ber om denne så tidlig som mulig etter kontraktsinngåelse.

## 8.2 2027 og senere

| Fase | Innhold | Periode |
|---|---|---|
| 2 | Integrasjoner (opsjoner), automatisert import, utvidede administrasjonsverktøy, rollestyring | Q1–Q3 2027 |
| 3 | Aktivitetsmodul: unike deltakere, starter, fullførte, utvikling over tid, fordelt på klubb, krets, aldersgruppe, kjønn og øvelse. Dashbord for forbund og kretser. | Q2–Q4 2027 |
| 3 | Utenbaneløp, jf. veikartet i kapittel 5 | Q1–Q3 2027 |
| 4 | Historisk utvidelse — kartlegging først, deretter import etter NFIFs valg | 2028, opsjon |

Aktivitetsmodulen i fase 3 er produktifisering av metodikk som allerede er
utviklet og validert i «Norsk friidrett 2013–2025». Det er ikke forskning fra
bunnen, og det er en reell kostnadsfordel.

## 8.3 Overgang og parallelldrift

Vi foreslår at dagens løsning holdes i drift parallelt frem til NFIF selv
bekrefter at den nye dekker behovet — ikke til en dato satt på forhånd. Det
koster lite og fjerner den eneste virkelig alvorlige risikoen ved
overgangen: at noe forsvinner uten at noen oppdager det før det trengs.

---

# 9. Organisasjon, bemanning og risiko

## 9.1 Om Athlete Mindset AS

Athlete Mindset AS er et norsk aksjeselskap innen idrettsteknologi og
idrettsdata. Selskapet leverer i tillegg laserbaserte måleprodukter for Athlete
Mindset Inc. og konsulenttjenester.

`‹AVKLARES›` Organisasjonsnummer, etableringsdato, aksjekapital, styre,
revisor.

## 9.2 Innvendingen vi tar opp selv

Athlete Mindset AS er et nystartet selskap. En innkjøper som skal binde seg for
tre til fem år må vurdere hva som skjer hvis leverandøren forsvinner. Vi mener
den innvendingen er berettiget, og at den fortjener et svar før den stilles.

| Innvending | Vårt svar |
|---|---|
| Nystartet selskap uten historikk | Selskapet er nytt. Plattformen er det ikke. To års utvikling og 1,9 millioner produksjonsdata er referansen. |
| Personavhengighet | `‹AVKLARES — navngitt utvikler nr. 2 fra kontraktsstart›` Estimatet i kapittel 8 tilsvarer halvannet til to årsverk frem til 01.01.2027. Leveransen forutsetter to utviklere, og det sier vi fremfor å love den med én. |
| Hva skjer ved opphør | Kildekode- og databaseescrow hos tredjepart. Exit-klausul: NFIF får kildekode, data og driftsdokumentasjon vederlagsfritt ved opphør, uansett årsak. Se kapittel 11. |
| Innelåsing | PostgreSQL, Next.js, åpne formater. Løsningen kan overtas av enhver kompetent leverandør. |
| Er dette et sideprosjekt | Selskapet har flere ben å stå på, og er dermed ikke økonomisk avhengig av én kontrakt. Statistikkplattformen er samtidig definert som strategisk kjerneprodukt, ikke som et enkeltoppdrag. |
| Ingen referansekunder | Vi har ingen forbundsreferanser. Vi har en løsning i drift med norske data, akademisk bruk av databasen og publisert analysearbeid. `‹AVKLARES — referanseuttalelse fra klubb, krets eller trener som bruker friidrett.live i dag›` |

Vi ber ikke NFIF kjøpe et konsulentoppdrag. Vi ber NFIF bli ankerkunde i et
produkt som skal leve videre — det er forskjellen som forklarer både hvorfor vi
kan prise dette lavere enn et konsulenthus, og hvorfor vi blir værende.

## 9.3 Om det frivillige miljøet

Statistikkarbeidet som er gjort siden 2013 er grunnlaget for at denne
anskaffelsen i det hele tatt er mulig — dataene finnes fordi noen har holdt dem
i hevd i tretten år uten betaling.

Vi foreslår at det etableres et fagråd med plass til dette miljøet og til SRU,
med reell innflytelse over regelverkstolkning, kvalitetsvurderinger og
prioritering av videreutvikling. Ikke som en høflighetsgest, men fordi
domenekunnskapen deres er vanskelig å erstatte, og fordi en plattform uten
tillit i statistikkmiljøet blir en plattform ingen bruker.

## 9.4 Risiko

| Risiko | Tiltak |
|---|---|
| Integrasjonene krever mer enn antatt | Prises som opsjoner med timepott, med forbehold om dokumentert API fra motparten |
| Utenbaneløp viser seg mer omfattende | Veikart levert nå, bygging i 2027, ingen fastpris før datakildene er kartlagt |
| Kretsmapping kommer sent fra NFIF | Flagget som kritisk avhengighet i kapittel 8.1 |
| Kvalitetsnivå A/B/C krever manuell registrering i større omfang enn antatt | Regelmotoren bygges for både automatisk utledning og manuell overstyring fra start |
| Kapasitet | To utviklere fra kontraktsstart |
| Datakvalitet i importert historikk | Kontroll mot kilden kjøres rutinemessig, jf. kapittel 6.2 |

---

# 10. Support og vedlikehold

*§21.*

| Element | Innhold |
|---|---|
| Support | E-post og telefon, norsk språk, norsk arbeidstid |
| Responstid, kritiske feil | `‹AVKLARES›` — foreslått: samme virkedag |
| Responstid, øvrige henvendelser | `‹AVKLARES›` — foreslått: to virkedager |
| Beredskap under mesterskap | Utvidet tilgjengelighet under NM, Bislett Games og terminfestede mesterskap |
| Vedlikehold | Sikkerhetsoppdateringer, driftsovervåkning, sikkerhetskopi med testet gjenoppretting |
| Videreutvikling | Fast årlig timepott til endringer NFIF prioriterer, jf. kapittel 12 |
| Datainnhenting | Løpende import og kvalitetskontroll av nye stevner, inkludert i driftsavtalen |
| Rapportering | Årlig statusmøte med driftsrapport, datakvalitetsrapport og prioritering av videreutvikling |

Videreutviklingspotten er bevisst. En driftsavtale uten utviklingskapasitet blir
en avtale der hver endring må forhandles, og resultatet er at endringene ikke
gjøres. Vi foreslår heller en fast pott NFIF disponerer.

---

# 11. Dataeierskap, exit og escrow

*§4, §22.*

- **NFIF eier alle data** som samles inn, importeres, behandles og vises i
  plattformen. Uten unntak og uten forbehold.
- **Full eksportrett** når som helst, i åpne formater, uten gebyr og uten at
  NFIF må be om det.
- **Ingen betalingsmur.** All statistikk er fritt tilgjengelig for utøvere,
  klubber, trenere, media og publikum. Vi tar ikke betalt av forbundets
  medlemmer for tilgang til forbundets egne tall.
- **Escrow.** Kildekode og databasestruktur deponeres hos tredjepart.
- **Exit-klausul.** Ved opphør av avtalen, uansett årsak og uansett hvem som
  sier opp, overleveres kildekode, komplette data og driftsdokumentasjon
  vederlagsfritt, i et format som lar en annen leverandør overta driften.
- `‹AVKLARES›` Vi er åpne for at NFIF selv eier skykontoene, slik at
  infrastrukturen står i forbundets navn fra dag én. Det er den sterkeste
  formen for eierskap, og vi har ingen innvending.

---

# 12. Pris

> **`‹IKKE UTFYLT›`** Prisen settes etter avklaring av budsjettramme med Magnus
> Trosdahl. Strukturen under følger §21, som ber om etablerings- og
> implementeringskostnader samt årlige driftskostnader for en periode på tre til
> fem år.

## 12.1 Etablering og implementering

| Post | Innhold | Pris |
|---|---|---:|
| Etablering | Ferdigstilling av leveransene i kapittel 8.1, frem til operativ løsning 01.01.2027 | `‹ ›` |
| Overtakelse av datagrunnlag | Overføring av eierskap til eksisterende base, inkludert historikk | `‹ ›` |
| Dokumentasjon | Drifts-, system- og API-dokumentasjon, DPIA, databehandleravtale | `‹ ›` |
| **Sum etablering** | | **`‹ ›`** |

## 12.2 Årlig drift

| Post | Innhold | Pris/år |
|---|---|---:|
| Drift og forvaltning | Hosting, overvåkning, sikkerhetskopi, oppdateringer | `‹ ›` |
| Support | Etter kapittel 10 | `‹ ›` |
| Løpende datainnhenting og kvalitetskontroll | Import av nye stevner, kontroll mot kilden | `‹ ›` |
| Videreutvikling | Fast timepott NFIF disponerer | `‹ ›` |
| Analysetjeneste | To mesterskapspakker og én årsrapport | inngår |
| **Sum årlig** | | **`‹ ›`** |

Prisen holdes fast i tre år, deretter regulering etter konsumprisindeks.

## 12.3 Opsjoner

| Opsjon | Grunnlag | Pris |
|---|---|---:|
| Integrasjon per system (§13) | Timepott, med forbehold om dokumentert API | `‹ ›` |
| Utenbaneløp, jf. veikartet i kapittel 5 | Prises etter kartlegging av datakildene | `‹ ›` |
| Aktivitetsmodul og dashbord (fase 3) | | `‹ ›` |
| Historisk utvidelse 2001–2012 (fase 4) | Kartlegging først, deretter import | `‹ ›` |
| Utvidet analyseavtale | Alle mesterskap, pressestøtte, kretsrapporter | `‹ ›` |
| Analyse og utredning på bestilling | Timepris | `‹ ›` |

## 12.4 Totalbilde 3–5 år

`‹Fylles ut når postene over er satt.›`

---

# 13. Forbehold og forutsetninger

1. **Integrasjoner** (§13) fastprises ikke før grensesnittdokumentasjon
   foreligger fra motparten. Prises som opsjoner med timepott.
2. **§14, fremtidig iSonen-arbeidsflyt**, beskriver en arbeidsflyt som ennå ikke
   er definert. Vi lover forberedt arkitektur og deltakelse i
   spesifikasjonsarbeidet, ikke ferdig integrasjon.
3. **Kretsstatistikk** (§10) forutsetter at NFIF leverer klubb-til-krets-mapping.
4. **Kvalitetsnivå A/B/C** (§6) forutsetter at NFIF avklarer hvem som eier
   vurderingen der kriteriene ikke lar seg utlede automatisk, og at
   lisensopplysninger og terminlistestatus gjøres tilgjengelig.
5. **Årsakskoder for ikke-ratifiserte resultater** (§7) er «TBD» i
   kravspekken og må fastsettes av NFIF.
6. **Utenbaneløp** (§8) leveres etter veikartet i kapittel 5, med pris etter
   kartlegging. Omfanget avhenger av NFIFs definisjon av «approved athletics
   events».
7. **Historikk før 2013** (§15) prises etter kartlegging av kildenes
   dekningsgrad.
8. **Differensiert eksponering av mindreåriges data** (kapittel 7.1) er et
   forbundsvedtak. Vi bygger det NFIF bestemmer.

---

# Vedlegg

| | Innhold |
|---|---|
| **A** | Kravsporing §22 obligatoriske krav og §23 ønskede tilleggsfunksjoner |
| **B** | Full kravsporing per kapittel |
| **C** | «56 til Birmingham» — mesterskapsanalyse EM 2026 |
| **D** | «Norsk friidrett 2013–2025» — bredde- og rekrutteringsanalyse, lederrettet sammendrag |
| **E** | Veikart utenbaneløp (utdypning av kapittel 5) |
| **F** | Spørsmål til NFIF — punktene merket `‹AVKLARES›` samlet |

---

# Vedlegg A — Kravsporing §22 og §23

**Statuskoder:** `I DRIFT` finnes i produksjon i dag · `DELVIS` deler finnes,
må ferdigstilles · `BYGGES` leveres i perioden · `AVTALE` løses kontraktuelt.

## §22 Obligatoriske krav

| # | Krav | Status | Leveranse |
|---|---|---|---|
| 1 | NFIF eier alle data | AVTALE | Kapittel 11 |
| 2 | Offisiell statistikkplattform for NFIF | AVTALE | — |
| 3 | Banestatistikk | I DRIFT | 1 922 634 resultater, 302 øvelser, inne og ute, alle aldersklasser |
| 4 | Løpsstatistikk, utenbane | BYGGES | Veikart i kapittel 5, jf. §24 |
| 5 | Utøverprofiler | I DRIFT | PB, SB, resultathistorikk, utviklingskurver, klubbhistorikk |
| 6 | Nasjonal statistikk | I DRIFT | Årsstatistikk, alle-tiders, rekorder |
| 7 | Klubbstatistikk | I DRIFT | Klubbside med årsstatistikk, alle-tiders og klubbrekorder |
| 8 | Regionsstatistikk | BYGGES | Krever kretsmapping fra NFIF. Des 2026. |
| 9 | Stevnesider | I DRIFT | 48 494 stevner med resultatlister og lenker til utøverprofiler |
| 10 | Historiske data | I DRIFT | 1 701 902 resultater fra 2013 og senere — §15 førsteprioritet. Data tilbake til 1922. |
| 11 | Kvalitetsklassifisering A/B/C | BYGGES | Regelmotor, kapittel 3.5. Nov 2026. |
| 12 | API-støtte | BYGGES | Dokumentert JSON-API, kapittel 3.4. Des 2026. |
| 13 | Eksportfunksjonalitet | BYGGES | Excel/CSV eksponert i grensesnittet. Nov 2026. |
| 14 | Mobilvennlig løsning | I DRIFT | Responsivt grensesnitt. WCAG 2.1 AA dokumenteres i tillegg. |

**Åtte av fjorten er i drift i dag.** De seks gjenstående er arbeidsmengde, ikke
teknisk risiko.

## §23 Ønskede tilleggsfunksjoner

| Krav | Status | Kommentar |
|---|---|---|
| Fullautomatisk resultatimport | DELVIS | Importrammeverk med validering og godkjenningskø i drift. Full automatisering avhenger av §13. |
| Analysemoduler | DELVIS | Finnes som analysekode og publisert analyse. Produktifiseres i fase 3. |
| Grafiske utviklingskurver | I DRIFT | Progresjonsdiagram og sammenligningsverktøy |
| Avansert aktivitetsanalyse | DELVIS | Metodikk utviklet og validert. Fase 3. |
| Datavaskverktøy | DELVIS | Utøversammenslåing og administrasjonsverktøy i drift. Utvides i fase 2. |
| Offentlige dashbord | BYGGES | Fase 3 |
| Utvidet historisk statistikk | BYGGES | Fase 4, opsjon |
| Åpne API-er for partnere | BYGGES | Sammen med §18 |

---

# Vedlegg B — Full kravsporing per kapittel

| § | Krav | Status | Merknad |
|---|---|---|---|
| §4 | Dataeierskap | AVTALE | Kapittel 11 |
| §5 | Skille prestasjon / rekord / aktivitet | BYGGES | Grunnlaget for både §6 og §8 |
| §6 | Kvalitetsnivå A/B/C med filtrering | BYGGES | Regelmotor med automatisk utledning og manuell overstyring |
| §7 | Bane TR14.1 / TR43.1 | BYGGES | Krever baneregister med klassifisering per anlegg |
| §7 | Flagg: innendørs | I DRIFT | |
| §7 | Flagg: World Rankings | BYGGES | |
| §7 | Flagg: blandede heat | BYGGES | Norsk særregel: tillatt i alle løpsøvelser utenom World Ranking-stevner |
| §7 | Flagg: utenlandske utøvere i norsk klubb | DELVIS | Nasjonalitet registrert, må eksponeres i lister |
| §7 | Flagg: WMA-masters | BYGGES | |
| §7 | Flagg: ikke-ratifisert med årsakskode | BYGGES | Kodeverk «TBD» — avklares med NFIF |
| §7 | Flagg: håndtidtaking | I DRIFT | Presisjonsbasert deteksjon, kun løp under 800 m. 18 769 resultater merket. |
| §8 | Utenbaneløp med full metadata | BYGGES | Veikart kapittel 5 |
| §9 | Utøverprofiler | I DRIFT | |
| §9 | Navneendring, klubbovergang, dubletter | DELVIS | Klubbhistorikk og utøversammenslåing i drift. Navneendringshistorikk bygges. |
| §10 | Klubbstatistikk | I DRIFT | |
| §10 | Regionsstatistikk | BYGGES | Krever kretsmapping |
| §11 | Stevnesider | I DRIFT | |
| §11 | Godkjennings- og statusinformasjon | BYGGES | Avhenger av §6 |
| §12 | Aktivitets- og deltakerdata | BYGGES | Metodikk validert, produktmodul i fase 3 |
| §13 | Integrasjoner, fem navngitte systemer | BYGGES | Opsjoner, forbehold om dokumentert API |
| §14 | Fremtidig iSonen-arbeidsflyt | BYGGES | Forberedt arkitektur |
| §15 | Historisk import 2013+ | I DRIFT | 1 701 902 resultater |
| §15 | Historisk import 2001–2012 | BYGGES | Fase 4, kartlegging først |
| §16 | Norske rekorder | I DRIFT | |
| §16 | Aldersklasserekorder, masters, godkjenningsstatus | BYGGES | Des 2026 |
| §17 | Mobil, nettbrett, desktop | I DRIFT | |
| §17 | Filtrering på elleve dimensjoner | DELVIS | Åtte i drift. Region, distanse og kvalitetsnivå bygges. |
| §17 | WCAG 2.1 AA | BYGGES | Ikke nevnt i kravspekken, men lovkrav |
| §18 | Dokumentert JSON-API | BYGGES | |
| §18 | Eksport Excel/CSV | BYGGES | |
| §19 | Personvern og sikkerhet | DELVIS | Tilgangskontroll i drift. DPIA, databehandleravtale og særskilt vern av mindreårige bygges. |
| §20 | Faseinndeling | — | Kapittel 8 |
| §21 | Tilbudets innhold | — | Dette dokumentet |
| §24 | Frister | — | Kapittel 8 |
