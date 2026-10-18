#!/usr/bin/env python3
"""Fyll ut NFIFs avklaringsskjema med svarene våre.

    python3 svar.py              # utkast, priser uthevet i gult
    python3 svar.py --endelig    # til innsending, uten utheving

Leser «Avklaringsspørsmål – Athlete Mindset.docx» i NFIFProsjekt/, bytter ut
plassholderne i rekkefølge og skriver «Svar – Avklaringsspørsmål – Athlete
Mindset.docx» i denne mappen. Formatet er det NFIF sendte; bare
plassholderne endres.

Markering i teksten:
  **fet**        fet skrift
  ==tall==       gul utheving (priser som skal kontrolleres før innsending)
  linje som starter med «- » blir et kulepunkt
"""

import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

HER = Path(__file__).resolve().parent
KILDE = HER.parent / 'Avklaringsspørsmål – Athlete Mindset.docx'
UT = HER / ('Svar – Avklaringsspørsmål – Athlete Mindset' + (' – endelig' if '--endelig' in sys.argv else '') + '.docx')

SVAR = [
# 1.1 Involvering fra Norsk Friidrett i kvalitetssikring
"""Utgangspunktet er at Norsk Friidrett bare skal ha de oppgavene som ligger til forbundet etter regelverket: godkjenne rekorder og bestenoteringer, avklare uregelmessigheter og underkjenne resultater. Resten tar vi.
Athlete Mindset AS har solid kjennskap til friidrett og vil avklare de aller fleste avvik på egen hånd. Plattformen kontrollerer alle nye resultater hver natt. Vi holder også kontakten med arrangørene når det er spørsmål om resultatlister. Da slipper forbundet et ledd. Arrangementene som mangler, finner vi ved å kontrollere terminlisten mot basen hver natt, jf. svar 1.5.
Oppgavene for Norsk Friidrett:
- **Godkjenning av rekorder og bestenoteringer.** Vi legger frem resultat, vind, tidtaking og stevnestatus ferdig utredet.
- **Underkjenning av stevner og resultater.** Vi registrerer underkjenningen med årsak, og resultatet holdes utenfor lister og rekorder.
- **Regeltolkning i tvilstilfeller.** For eksempel redskap, blandede heat og utenlandske utøvere.
**Tidsbruk.** Samlet bør dette ta under én time i uken i høysesongen. Anslaget bygger på 2026-sesongen. De automatiske kontrollene fant 301 avvik i 54 198 baneresultater, fra 5 til 20 i uken. Om lag 45 av dem var mulige rekorder eller bestenoteringer, altså 1–2 saker i uken som krever forbundets godkjenning. Resten kan vi avklare selv.
**Kompetanse.** Det som trengs, er den kompetansen statistikkansvarlig og SRU har i dag: rekordregler og regelverk. Det trengs ingen teknisk kompetanse.
**Endring over tid.** Første sesong kan behovet bli noe større, fordi kontrollene skal justeres etter NFIFs praksis. Vi har heller ikke full klarhet i hvilke resultater som skal registreres, særlig for løp utenfor bane. Alle eldre resultater ligger i basen, men det trengs noen grensedragninger, blant annet for vind. Etter første sesong, og når lisensregisteret er koblet til, går behovet ned mot ren godkjenning av rekorder.
I tillegg kommer noen engangsoppgaver ved oppstart:
- klubbenes kretstilhørighet
- tilgang til lisensregisteret
- hjelp til å få tilgang til API-ene i iSonen
- en grundig gjennomgang av eldre statistikk, for eksempel sammen med SRU. Deler av den gamle statistikken har svakheter, og en felles gjennomgang sikrer at listene er riktige per 1.1.2027.""",

# 1.2 Gjenstående arbeid for løp utenfor bane
"""Siden presentasjonen har vi bygget en første versjon av løp utenfor bane. Den kan ses på friidrettsresultater.no/gatelop. Den omfatter:
- **Datamodell for løp** med arrangement, løp, distanse, løypegradering og resultater. Den er adskilt fra baneresultatene, men koblet til det samme utøverregisteret.
- **Automatisk import fra EQ Timing** av alle arrangementer under Norges Friidrettsforbund. Fra 1. januar til 14. oktober 2026 gir det 640 arrangementer, 1 582 løp og 158 793 resultater.
- **Import fra Ultimate Sport Service**, som tar tid i blant annet Oslo Maraton. Importen er bygget, med netto- og bruttotid, og testet på de første løpene i 2026.
- **Metadata per løp**, slik kravspesifikasjonens punkt 8 ber om: distanse, løpstype (gate, terreng, motbakke, fjell, ultra, stafett), løypemåling, tidtaker, arrangør, sted, dato, antall deltakere og fullførte, og klubb. Kjønns- og aldersfordeling kan regnes ut fra resultatene.
- **Kvalitetsnivå A, B og C, satt maskinelt** ut fra tidtakerens løypegradering (sertifisert målt løype, A-, B- eller C-måling), distansen og typen løp. Terreng-, motbakke- og fjelløp regnes foreløpig som registrert aktivitet (nivå C). Løp der vinnertiden er umulig for oppgitt distanse, flagges og settes også til nivå C.
- **Årsbeste på 5 km, 10 km, halvmaraton og maraton**, én rad per løper, med filter på kvalitetsnivå, kjønn og aldersklasse. Utenlandske løpere står bare med når de representerer en norsk klubb, og merkes da med stjerne.
- **Kobling til utøverregisteret** på navn, kjønn og fødselsår. 13 159 resultater er koblet automatisk.
- **Kontroll mot terminlisten.** Gateløpene på terminlisten kontrolleres mot basen hver natt, slik som banestevnene (svar 1.5).
Dette gjenstår:
- **Avklaring med NFIF om hvilke resultater som skal inn i statistikken.** Det er ikke gitt at alle deltakere i et mosjonsløp skal med. Resten av 2026 fra Ultimate Sport Service importeres når dette er avklart.
- **Flere tidtakere**, blant annet Racedays, der API-nøkkel er etterspurt. Q1 2027.
- **Løyperegister.** Nivå A bør bygge på NFIFs egne løypemålinger, ikke bare tidtakerens merking. Q1 2027.
- **Terreng-, motbakke- og fjelløp.** Disse løpene får lister per løp og løype i stedet for per distanse, og motbakkeløpene får høydemeter. Q2 2027.
- **Rekordlister og rekordgodkjenning** for de offisielle distansene. Q2 2027.
- **Samlet utøverprofil** med bane og løp, og løpene med i aktivitetsstatistikken. Q2 2027.
- **Eldre resultater fra løp utenfor bane**, særlig rekorder fra før 2013. Etter kartlegging.
Løpssider og årsbeste kan dermed være i drift fra sesongstart 2027, og hele løsningen innen utgangen av andre kvartal 2027. Veikartet leveres innen 31.12.2026, slik kravspesifikasjonen krever.""",

# 1.3 Status for administrasjonsverktøyet
"""Administrasjonsverktøyet er i drift, med innlogging og roller for administrator og superadministrator. Skjermbilder ligger ved.
Det dekker i dag:
- **Avvik:** arbeidslisten fra de nattlige kontrollene. Hvert avvik godkjennes som riktig, rettes eller underkjennes, med kommentar og registrering av hvem som gjorde det. Mulige rekorder og bestenoteringer legges frem her.
- **Ikke godkjente resultater:** resultater som ikke er godkjent, for eksempel på grunn av kort bane, manglende medlemskap i NFIF eller feil i startutstyret, registreres med årsak. De holdes utenfor alle lister og rekorder, men vises med årsak på utøver- og stevnesidene.
- **Terminliste:** hvilke arrangementer i terminlisten som mangler resultater, hvor lenge de har manglet, og om arrangøren er purret. En purreliste samler det som mangler per arrangør, med ferdig e-postutkast.
- **Utøvere:** søk, redigering og sammenslåing av dubletter.
- **Resultater:** redigering og sletting av feilregistreringer.
- **Stevner og klubber:** redigering av navn, dato, sted og tilhørighet.
- **Import:** opplasting av resultatlister på friidrettens standardmal i Excel, som CSV eller som tekstfil, med godkjenning før publisering. Utøverne kobles automatisk på navn, fødselsår og kjønn, og rader som alt ligger inne, hoppes over. Importen er prøvd på en resultatliste som kom inn til resultater@friidrett.no 17. oktober: alle 48 resultatene og de 15 utøverne ble koblet automatisk.
- **Brukere og nedlasting:** oversikt over brukere og roller. Lister kan lastes ned som CSV for Excel, men bare av administratorer, og hver nedlasting logges med hvem, hva og når.
Avvik, ikke godkjente resultater, terminliste, brukere og nedlasting er nye siden presentasjonen.
Dette gjenstår:
- Rekordgodkjenning med dokumentasjon og status. Desember 2026.
- Underkjenning og manuell overstyring av kvalitetsnivå direkte i verktøyet. Desember 2026.
- Roller for NFIF og kretsene, og logg over alle endringer. Q1 2027.
- Administrasjon av løp utenfor bane: løyperegister, løp og kobling av løpere. Q1–Q2 2027.""",

# 1.4 Egen database for masters
"""Vi anbefaler én felles database, med egne lister og egne rekorder for masters. Vi har vurdert spørsmålet på nytt etter presentasjonen, og bygget masterstatistikken på den måten for å prøve det ut.
Resultatet ligger på friidrettsresultater.no/statistikk/masters. Siden viser beste norske resultat per øvelse i hver femårsklasse fra 35 år, ute og inne. Den bygger på om lag 96 000 masters-resultater som allerede ligger i basen.
**Kontroll mot de godkjente mastersrekordene.** Vi har gått gjennom de offisielle rekordlistene, ute og inne for menn og kvinner, linje for linje mot basen. Av 1 085 rekordlinjer fantes 503 allerede. 551 manglet og er lagt inn. De godkjente rekordene er merket i basen og vises på masterssiden, også der eldre rekorder mangler vindmåling eller er håndtidtatt. Masterssiden viser nå samme rekord som rekordlistene i 912 av 1 004 klasser og øvelser. Resten er samlet i en avviksliste. Omtrent halvparten er nyere resultater som kan være nye rekorder. Resten er blant annet resultater som ikke er godkjent, og feil i eldre data. Disse skal avklares med rekordansvarlig.
Fordelene med én database:
- **Det er de samme utøverne.** En 35-åring er både senior og masters i samme løp. Med to databaser må utøveren, resultatet og hver rettelse føres to steder, og basene vil gli fra hverandre.
- **Masters følger av dataene.** Klassen regnes ut fra fødselsår og konkurranseår, og redskap og hekkehøyde ligger allerede i øvelsen. Det trengs ingen ekstra registrering.
- **Samme import og samme kontroller** gjelder for alle.
Argumentene for egen database, og hvordan de møtes:
- **Mastersmiljøet vil forvalte sin egen statistikk.** Det løses med en egen administratorrolle for masters, ikke med en egen base.
- **Mastersklassene har eget regelverk.** WMA-reglene for redskap og hekkehøyder legges inn som regler for klassene. Særtilfeller er allerede tatt hensyn til, for eksempel at kastøvelsene på innendørsmesterskap regnes som utendørs, slik rekordlistene gjør.
Ulempen med én database er at mastersklassene må holdes adskilt i presentasjonen, så seniorlistene ikke blir uoversiktlige. Det er gjort i løsningen.
**Mastersmiljøet.** Blir vi valgt, tar vi straks kontakt med mastersmiljøet. Vi vil finne ut hva de ønsker seg, hvordan statistikk og rekorder bør presenteres, og om det er noe spesifikt de savner i dag. Løsningen tilpasses etter det.""",

# 1.5 Integrasjoner og automatisert resultatinnsamling
"""Resultatene skal samles inn fra to steder:
- **Resultatlister som kommer inn til Norsk Friidrett.** De fleste kommer gjennom iSonen, resten fra FriRes og LiveRes, OpenTrack og tidtakerne. Plattformen tar imot alle, og alle går gjennom de samme kontrollene. Lister som sendes på e-post til resultater@friidrett.no, kan legges inn samme dag. Når stevnet senere kommer gjennom den ordinære importen, kjennes radene igjen, så det ikke blir dubletter.
- **Resultater vi henter selv.** Et eget system søker opp norske utøveres resultater rundt i verden. Søket tar utgangspunkt i utøveren, ikke i stevnet: World Athletics-profiler, TFRRS for collegeutøvere i USA, og resultattjenestene i andre land. Utøvere og klubber kan i tillegg melde inn resultater med dokumentasjon.
**Kontroll av at alt er kommet inn.** Terminlisten hentes hver natt, og hvert avholdt arrangement kontrolleres mot resultatene i basen. Arrangementer som mangler resultater tre dager etter siste stevnedag, vises i administrasjonsverktøyet, og arrangøren purres etter en uke. Dette er i drift, både for banestevner og gateløp.
**Avtaler med leverandørene.** Vi har ingen formell rolle for Norsk Friidrett i dag, og har derfor ikke kunnet forhandle om API-er eller diskutere integrasjoner med leverandørene av resultater. Blir vi valgt, tar vi straks kontakt med iSonen, OpenTrack, FriRes/LiveRes, EQ Timing og Ultimate Sport Service, for å sikre at resultatene kan listeføres umiddelbart etter hvert stevne. Vi har testet dataformatene der det har vært mulig, og vet at importen fungerer. De endelige løsningene må likevel avtales med hver leverandør.
Status for de enkelte systemene:
- **iSonen:** API-tilgang forutsetter avtale med NFIF og Buypass. Frem til da brukes den åpne terminlisten, med arrangement, arrangør og krets, til kontrollen over. Resultatoverføring fra Q1 2027, etter at tilgang er gitt.
- **FriRes og LiveRes:** vi har fått tilgang til LiveRes' datastrøm fra utvikleren, og har testet formatet. Den gir stevnelisten og fullstendige resultatlister per stevnedag, med FriSys-id, fødselsdato, klubb, vind og hvert forsøk. Importen bygges når bruken er avtalt.
- **OpenTrack:** ikke utviklet, og ikke testet ennå. OpenTrack har et åpent API, så integrasjonen bør ikke avhenge av særskilt tilrettelegging. Q1–Q2 2027.
- **EQ Timing:** fungerer. Importen bruker EQ Timings åpne resultattjeneste og er testet på hele 2026, jf. svar 1.2. For varig drift ønsker vi en avtale om grensesnittet og varsling ved endringer.
- **Ultimate Sport Service:** formatet er testet, og importen er bygget, med netto- og bruttotid. Hvilke løp og resultater som skal inn, avklares med NFIF (svar 1.2), og grensesnittet avtales med leverandøren.
Dersom API-tilgang ikke blir gitt, stopper ikke løsningen opp. Resultatlister kan lastes opp som fil (CSV, Excel eller tekstfil) i administrasjonsverktøyet, og de går gjennom de samme kontrollene. Offentlige resultatsider kan hentes der tidtakeren tillater det. Det gir mer manuelt arbeid, men terminlistekontrollen sikrer at ingenting faller ut i det stille. Uten lisensregisteret settes kvalitetsnivået ut fra stevnenivå og tidtaking, og det overstyres manuelt der det trengs.""",

# 1.6 Kvalitetssikring og avvikshåndtering
"""Athlete Mindset har ansvaret for å behandle avvikene i ordinær drift. NFIF trekkes inn bare der saken krever forbundets myndighet.
Plattformen kontrollerer alle nye resultater hver natt: tider som er umulige for distansen, mulige rekorder og bestenoteringer, uvanlig store forbedringer, og manglende vind, kjønn eller fødselsår. Avvikene legges i arbeidslisten i administrasjonsverktøyet, og vi behandler dem fortløpende i sesongen.
Innenfor den årlige driftsprisen:
- Registreringsfeil: feil øvelse, redskap, enhet eller distanse, og tider i feil format.
- Resultater registrert på feil utøver, for eksempel når flere har samme navn.
- Dubletter av resultater, stevner og utøvere, og sammenslåing av utøvere.
- Manglende kjønn, fødselsår eller vind, kontrollert mot resultatlisten.
- Retting når en arrangør sender en korrigert resultatliste.
- Oppfølging og purring av arrangører som ikke har sendt resultater, ut fra terminlisten.
- Kobling av løpere i gateløp til utøverregisteret.
Krever avgjørelse fra NFIF. Vi utreder og dokumenterer sakene:
- Godkjenning av rekorder og bestenoteringer.
- Underkjenning av stevner eller resultater. Når NFIF har avgjort saken, registrerer vi underkjenningen med årsak, og resultatet holdes utenfor lister og rekorder.
- Regeltolkning i tvilstilfeller, for eksempel blandede heat og utenlandske utøvere.
Faktureres særskilt. Dette prises i hvert enkelt tilfelle og avtales på forhånd:
- **Kretsenes egne statistikker.** Flere kretser har utvidede kretsstatistikker, blant annet Oslo og Akershus, som har en omfattende statistikk. Mye av dette er historisk statistikk som ikke ligger i basen. Den finnes i krevende formater og er av ulik kvalitet, og en integrering krever mye tid, særlig til kvalitetssikring.
- **Historisk statistikk fra forbundet.** Også her er det stor forskjell i kvalitet og format, og arbeidet kan være tidkrevende.
- Større oppryddingsprosjekter i historiske data.
- Nye kontrollregler som krever utvikling.""",

# 1.7 Leveranseplan og funksjonalitet ved oppstart
"""**Allerede utviklet, i produksjon 1. januar 2027:**
- Nasjonal statistikk: årslister, alle-tiders-lister og rekorder, ute og inne, med filter for kjønn, aldersklasse, vind og tidtaking.
- Utøverprofiler, klubbsider med klubbstatistikk og klubbrekorder, og stevnesider med arrangør, arrangementstype og krets.
- NM-kvalifisering, oppdatert fortløpende.
- Masterstatistikk per femårsklasse, kontrollert mot de godkjente mastersrekordene (svar 1.4).
- Aktivitet og deltakelse.
- Ikke godkjente resultater registrert med årsak, holdt utenfor lister og rekorder.
- Eksport til Excel og CSV fra årslister, alle-tiders-lister, klubb- og stevnesider og aktivitetssiden, for administratorer og med logg.
- Automatiske kontroller med avviksliste, og nattlig kontroll mot terminlisten med purreliste.
- Administrasjonsverktøy for avvik, terminliste, utøvere, resultater, stevner, klubber, import og brukere.
- Første versjon av løp utenfor bane, med import fra EQ Timing (svar 1.2).
**Gjenstår, leveres før 1. januar 2027:**
- Kvalitetsnivå A, B og C for baneresultater, med filter.
- Dokumentert API for godkjente brukere.
- Rekordgodkjenning og underkjenning direkte i administrasjonsverktøyet.
- Dokumentasjon, personvernvurdering og databehandleravtale.
- Første versjon av søket etter norske resultater i utlandet.
**Leveres i 2027:**
- Løp utenfor bane i full drift, jf. svar 1.2. Q1–Q2.
- Integrasjoner, jf. svar 1.5. Q1–Q3.
- Roller for NFIF og kretsene, og logg over alle endringer. Q1.
- Eldre statistikk og kretsenes statistikker, etter NFIFs valg (svar 1.6).
**Avhengig av eksterne:**
- Kretsstatistikk: klubbenes kretstilhørighet fra NFIF. Når den foreligger, kan kretsstatistikken være på plass i løpet av få uker.
- Maskinelt kvalitetsnivå: tilgang til lisensregisteret fra NFIF og Buypass. Terminlisten er allerede i bruk.
- Løp utenfor bane: NFIFs avklaring av hvilke resultater som skal inn i statistikken (svar 1.2).
- Integrasjoner mot iSonen, FriRes/LiveRes, OpenTrack og Ultimate Sport Service: avtale og tilgang fra leverandørene (svar 1.5).
- EQ Timing i varig drift: avtale med EQ Timing.""",

# 2.1 Stabilitet og kontinuitet over tid
"""**Kapasitet og nøkkelpersoner.** Leveransen bemannes av tre navngitte personer: Atle Guttormsen (data og analyse), Simen Guttormsen (systemutvikling) og Sondre Guttormsen (idrettsfaglig ledelse og produkt). To av dem har full teknisk tilgang og kjenner hele løsningen. Den daglige driften er automatisert: import, avstemming og kontroller går hver natt uten manuell innsats, og avvik legges i arbeidslisten. Alle endringer i data og kode dokumenteres i en driftslogg og i versjonskontroll.
**Økonomisk soliditet.** Athlete Mindset AS inngår i Fire S Invest AS og har flere forretningsområder. Selskapet står derfor ikke og faller med én kontrakt. Løsningen bygger på standard skytjenester med lave driftskostnader. Vi legger gjerne frem regnskap og eierforhold.
**Tilgang til data, dokumentasjon og videre drift.** Med den reduserte oppstartsprisen (svar 3.1) justerer vi også exit-klausulen i tilbudets kapittel 11. Den skiller nå mellom dataene, som er NFIFs, og nettstedet og programvaren som presenterer dem, som er Athlete Mindset AS':
- **Data.** NFIF eier alle data og har full eksportrett når som helst, i åpne formater og uten gebyr, slik kravspesifikasjonens punkt 4 krever.
- **Ved opphør av avtalen,** uansett årsak, overleveres komplette data med dokumentasjon av datamodellen, slik at de kan tas i bruk i en annen løsning. Nettstedet og programvaren følger ikke med. Vi bistår ved overgangen etter nærmere avtale.
- **Hvis Athlete Mindset AS ikke lenger kan levere,** for eksempel ved konkurs eller avvikling, utleveres kildekode og driftsdokumentasjon fra deponi hos tredjepart, slik at driften kan videreføres.
- Løsningen bygger på standard teknologi (PostgreSQL, Next.js og Python).
For et tidsperspektiv på 5–10 år foreslår vi i tillegg et årlig statusmøte med gjennomgang av drift, datakvalitet og kontinuitetsplan.""",

# 3.1 Oppstartspris
"""Vi har gått gjennom oppstartsprisen. For nasjonal banestatistikk reduserer vi den fra 710 000 kr til ==350 000 kr==, en reduksjon på ==51 prosent==.
**Hva oppstartsprisen er.** Oppstartsprisen er i hovedsak betaling for en løsning som allerede er utviklet. NFIF får fra første dag en plattform i drift: utøver-, klubb- og stevnesider, årslister, alle-tiders-lister og rekorder, masterstatistikk, NM-kvalifisering, aktivitetsstatistikk, automatiske kontroller og et administrasjonsverktøy. Bak dette ligger svært mange timers arbeid, som vi har tatt på egen risiko. At deler av løsningen, som masterstatistikken, allerede er ferdig, gjør den ikke mindre verdt.
**Hva som driver kostnaden:**
- Den ferdig utviklede løsningen, inkludert masterstatistikken, og arbeidet med å hente inn, kontrollere og strukturere dataene: ==150 000 kr==.
- Det som gjenstår før 1. januar 2027: dokumentert API ==80 000 kr==, kvalitetsnivå for resultater ==50 000 kr==, dokumentasjon, personvernvurdering og databehandleravtale ==40 000 kr==, og kretsstatistikk ==30 000 kr==. Til sammen ==200 000 kr==.
**Hva vi har justert.** Vi har satt ned prisen for den ferdige løsningen betydelig, fordi vi ønsker et langsiktig samarbeid med NFIF. I tillegg er omfanget justert: opphenting av eldre statistikk er tatt ut av fastprisen. Kvalitet og format varierer mye mellom kildene, så dette prises i hvert enkelt tilfelle, jf. svar 1.6.
Årlig drift av banestatistikken er uendret, ==300 000 kr== per år. Den omfatter også behandlingen av avvik, jf. svar 1.6.
Ønsker NFIF lavest mulig oppstartskostnad, kan posten for den ferdige løsningen fordeles på driftsprisen, med ==30 000 kr== per år i fem år. Da blir oppstartsprisen ==200 000 kr==.
For gateløp gir vi nå fastpris på etableringen, ==300 000 kr==, mot 450 000–600 000 kr tidligere. Se svar 3.2.
Alle priser er eks. mva.""",

# 3.2 Etablering av gateløp: integrasjoner
"""Etableringsprisen for gateløp omfatter integrasjonen mot EQ Timing, som tar tid i flest løp. Den er bygget og testet på hele 2026, jf. svar 1.2. EQ Timing var den største usikkerheten bak det opprinnelige intervallet. Den er nå avklart, og vi kan derfor gi fastpris: ==300 000 kr==. Det er ikke lenger et intervall for selve etableringen.
Fastprisen omfatter datamodell, import fra EQ Timing, løyperegister, kvalitetsnivå, årsbeste og rekordlister, terreng- og motbakkeløp, løpssider og samlet utøverprofil med bane og løp.
Andre tidtakere kommer i tillegg, med ==30 000–50 000 kr== per system. De relevante er Ultimate Sport Service, som tar tid i blant annet Oslo Maraton, og mindre systemer som Racedays. For Ultimate er importen bygget og formatet testet. Hvilke løp og resultater som skal inn, avklares med NFIF (svar 1.2), og grensesnittet med leverandøren (svar 1.5). Samlet forventet tillegg er ==30 000–100 000 kr==.
Prisen forutsetter at tidtakeren tilbyr et dokumentert API eller en strukturert datafil, slik at arbeidet blir begrenset. Hvor i intervallet prisen havner, avgjøres av hvor godt grensesnittet er dokumentert. Må resultatene hentes fra resultatsider, krever det mer arbeid, både ved etablering og når tidtakeren endrer sidene, og det prises særskilt. Avgifter som tidtakeren eventuelt krever for tilgang, er ikke med i prisen og avtales særskilt.
Årlig registrering og vedlikehold av gateløp er ==200 000 kr== per år, som før.""",

# 3.3 Samlet kostnad over fem år
"""Alle beløp er eks. mva. og før KPI-regulering fra år fire. Banestatistikk og gateløp kan velges hver for seg.
**Nasjonal banestatistikk:**
- Etablering: ==350 000 kr== (fast pris)
- Drift i fem år à ==300 000 kr==: ==1 500 000 kr== (fast pris)
- Integrasjon mot iSonen, terminliste og lisensregister: inntil ==80 000 kr==
- Direkte overføring fra LiveRes: inntil ==50 000 kr==
- **Sum banestatistikk over fem år: høyst ==1 980 000 kr==**, hvorav ==1 850 000 kr== er faste priser.
**Gateløp og andre løp utenfor bane:**
- Etablering, inkludert integrasjonen mot EQ Timing: ==300 000 kr== (fast pris)
- Drift i fem år à ==200 000 kr==: ==1 000 000 kr== (fast pris)
- Integrasjon mot Ultimate Sport Service: inntil ==50 000 kr==
- **Sum gateløp over fem år: høyst ==1 350 000 kr==**, hvorav ==1 300 000 kr== er faste priser.
**Samlet over fem år: høyst ==3 330 000 kr==**, hvorav ==3 150 000 kr== er faste priser.
**Integrasjonene er gitt med tak.** Beløpene er øvre grenser, ikke anslag som kan øke. De forutsetter at leverandøren tilbyr et dokumentert API eller en strukturert datafil. For LiveRes og Ultimate Sport Service er formatet allerede testet. Avgifter som leverandørene eventuelt krever for tilgang til sine grensesnitt, er ikke med og avtales særskilt. Finnes det ikke et grensesnitt, slik at resultatene må hentes fra offentlige resultatsider, prises det særskilt.
**Tillegg etter behov:**
- OpenTrack: inntil ==50 000 kr==
- Andre tidtakere for løp utenfor bane, for eksempel Racedays: inntil ==50 000 kr== per system, jf. svar 3.2.
- Eldre statistikk og kretsenes statistikker: prises i hvert enkelt tilfelle, jf. svar 1.6.
- Øvrig utvikling: ==950 kr== per time. Analyse og utredning: ==1 100 kr== per time.
**NFIFs egen arbeidstid.** Prisene omfatter behandlingen av avvik og kontakten med arrangørene (svar 1.6). NFIFs egen innsats er anslått til under én time i uken i høysesongen, i hovedsak godkjenning av rekorder (svar 1.1). I en løsning der forbundet selv kvalitetssikrer resultatene, kommer den arbeidstiden i tillegg til prisen.""",
]

VEDLEGG = [
    'Ingen',
    'Vedlegg 2: Skjermbilder av gateløp',
    'Vedlegg 1: Skjermbilder av administrasjonsverktøyet',
    'Vedlegg 3: Skjermbilde av masterstatistikken',
    'Ingen', 'Ingen', 'Ingen', 'Ingen', 'Ingen', 'Ingen', 'Ingen',
]

KOMMENTAR = """Siden presentasjonen har vi bygget tre av tingene dere spør om, slik at svarene kan kontrolleres i løsningen og ikke bare leses: avvikslisten i administrasjonsverktøyet, masterstatistikken og første versjon av løp utenfor bane. Se friidrettsresultater.no/statistikk/masters og friidrettsresultater.no/gatelop. Vi viser gjerne administrasjonsverktøyet i et kort møte."""


ENDELIG = '--endelig' in sys.argv     # uten gul utheving, til innsending


def runs(tekst: str) -> str:
    """Tekst med **fet** og ==utheving== til w:r-elementer."""
    ut = []
    for del_ in re.split(r'(\*\*.+?\*\*)', tekst):
        fet = del_.startswith('**') and del_.endswith('**')
        if fet:
            del_ = del_[2:-2]
        for bit in re.split(r'(==.+?==)', del_):
            if not bit:
                continue
            gul = bit.startswith('==') and bit.endswith('==')
            if gul:
                bit = bit[2:-2]
                gul = not ENDELIG
            rpr = ('<w:b/><w:bCs/>' if fet else '') + ('<w:highlight w:val="yellow"/>' if gul else '')
            ut.append(f'<w:r>{"<w:rPr>" + rpr + "</w:rPr>" if rpr else ""}'
                      f'<w:t xml:space="preserve">{escape(bit)}</w:t></w:r>')
    return ''.join(ut)


def avsnitt(tekst: str) -> str:
    ps = []
    for linje in [l for l in tekst.split('\n') if l.strip()]:
        if linje.startswith('- '):
            ppr = ('<w:pPr><w:spacing w:before="0" w:after="40"/>'
                   '<w:ind w:left="284" w:hanging="227"/></w:pPr>')
            ps.append(f'<w:p>{ppr}<w:r><w:t xml:space="preserve">–\t</w:t></w:r>{runs(linje[2:])}</w:p>')
        else:
            ppr = '<w:pPr><w:spacing w:before="60" w:after="80"/></w:pPr>'
            ps.append(f'<w:p>{ppr}{runs(linje)}</w:p>')
    return ''.join(ps)


def erstatt(xml: str, plassholder: str, nye: list[str]) -> str:
    for ny in nye:
        i = xml.find(plassholder)
        if i < 0:
            raise SystemExit(f'Fant ikke flere «{plassholder}»')
        s = xml.rfind('<w:p ', 0, i)
        e = xml.find('</w:p>', i) + len('</w:p>')
        xml = xml[:s] + ny + xml[e:]
    if plassholder in xml:
        raise SystemExit(f'Flere «{plassholder}» enn svar')
    return xml


def main():
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(KILDE) as z:
            z.extractall(tmp)
        dok = Path(tmp) / 'word' / 'document.xml'
        xml = dok.read_text(encoding='utf-8')
        xml = erstatt(xml, '[Leverandøren skriver sitt svar her]', [avsnitt(s) for s in SVAR])
        xml = erstatt(xml, '[Navn på vedlegg, eller «Ingen»]', [avsnitt(v) for v in VEDLEGG])
        xml = erstatt(xml, '[Eventuelle kommentarer eller presiseringer som ikke hører inn under spørsmålene over]',
                      [avsnitt(KOMMENTAR)])
        dok.write_text(xml, encoding='utf-8')
        if UT.exists():
            UT.unlink()
        subprocess.run(['zip', '-q', '-X', '-r', str(UT), '.'], cwd=tmp, check=True)
    print(UT.name)


if __name__ == '__main__':
    main()
