# Forberedte svar

Fem til ti minutter med spørsmål. Under er de som er mest sannsynlige, og de
som er vanskeligst.

**Regel:** svar kort. Et langt svar på et enkelt spørsmål ser ut som
usikkerhet. Vet du ikke, si det og lov å komme tilbake.

---

## De vanskelige

### «Hvordan vet vi at statistikken faktisk er oppdatert?»

> Den henter seg selv. Hver natt klokken kvart over fire kjører innsamlingen:
> nye stevner inn, de siste seks ukene hentes på nytt og avstemmes mot
> kilden, forsidetallene oppdateres, og tolv kontroller kjøres mot basen.
> Forsiden viser klokkeslettet. Feiler en kontroll, feiler kjøringen, og vi
> ser det om morgenen. Loggen fra hver kjøring tas vare på i tretti dager.
>
> Og det er ingen som må huske å starte den. Det er poenget.

Vis gjerne forsiden: «Oppdatert i dag kl. 04.15».

### «Hva gjør dere når et stevne mangler i statistikken?»

> Det skjer, og det skal være lett å melde. I dag: én melding til oss, så
> hentes stevnet i neste kjøring, eller med én kommando samme dag. Fra
> oktober har plattformen en innmeldingskanal for arrangører og utøvere,
> og alt som meldes inn havner i arbeidslisten med sporing.


### «Hvor mye tid har dere egentlig til dette?»

Det skarpeste spørsmålet i rommet, og det kommer trolig fra Magnus. Alle tre
har annet arbeid, og NFIF er brent på personavhengighet.

Ikke bagatelliser det. Svar med struktur i stedet for entusiasme:

> Vi er tre, ikke én, og det er et bevisst svar på nettopp det §1 beskriver.
> Arbeidet fram til nyttår er avgrenset og planlagt med frister per leveranse.
> Vi har dimensjonert bemanningen for det.
>
> Og i motsetning til en løsning som skal bygges, er det meste av arbeidet
> allerede gjort. Det som gjenstår er ferdigstilling.

`‹Avklar før møtet: hvor mange timer per uke hver av dere faktisk stiller med
i oktober, november og desember. Ha tallet klart, selv om dere ikke oppgir det
uoppfordret.›`

### «Hva koster det?»

Tilbudet ber om forhandling og oppgir ingen tall. Det blir de neppe fornøyd
med å høre to ganger, så ha en retning klar.

> Vi ønsker å avtale prisen i forhandling, og grunnen er at flere poster ikke
> kan prises redelig fra utsiden. Integrasjonene avhenger av grensesnitt vi
> ikke har sett, og løp utenfor bane av tidtakernes datakilder. Setter vi tall
> på dem nå, priser vi inn vår egen usikkerhet, og dere betaler for den enten
> den inntreffer eller ikke.
>
> Etablering og årlig drift kan vi derimot fastprise. Vi stiller gjerne med
> gjennomarbeidede estimater og går gjennom dem linje for linje.

Blir de stående på det: tilby et konkret møte med Magnus om budsjettrammen.
Ikke improviser et tall i møtet.

### «Hva skjer hvis dere slutter, eller selskapet forsvinner?»

> Kildekode og databasestruktur deponeres hos tredjepart. Exit-klausulen sier
> at NFIF får kildekode, komplette data og driftsdokumentasjon vederlagsfritt
> ved opphør, uansett årsak og uansett hvem som sier opp.
>
> Vi bruker PostgreSQL og Next.js. Ingen egenutviklet database, ingen
> proprietære formater. Løsningen kan overtas av enhver kompetent leverandør
> uten omskriving. Det er et bevisst valg.

### «Dere er et nystartet selskap uten referansekunder.»

> Selskapet er nytt. Arbeidet er det ikke. Norske friidrettsdata har vært
> grunnlag for fagfellevurderte studier siden 2015, og plattformen har to års
> utvikling og nær to millioner produksjonsdata bak seg.
>
> Vi har ingen forbundsreferanser, og det skal vi ikke late som. Det vi har,
> er en løsning dere kan ta på i dag.

---

## Teknisk

### «Håndterer dere paraidrett?»

**Nei, ikke ennå. Vær ærlig om dette.** I én sesong hoppet importen over 43
resultater i Racerunning- og rullestolklasser fordi de mangler egen øvelse i
datamodellen.

> Nei. Para-øvelsene blir i dag ikke importert, fordi de ikke har en egen
> datamodell hos oss. Det er en reell mangel, og vi vet nøyaktig hvor mange
> resultater det gjelder fordi importen teller dem.
>
> Klassifisering gjør para-statistikk til en annen oppgave enn å legge til en
> øvelse. Vi vil gjerne ha NFIFs syn på hvor det hører hjemme i prioriteringen.

Å kjenne sitt eget hull presist er mer tillitvekkende enn å ikke ha hullet.

### «Hvordan avgjør dere kvalitetsnivå A, B og C?»

> Nivået følger av stevnet, ikke av en manuell vurdering. Et stevne på
> terminlisten eller på World Athletics' liste er per definisjon godkjent, med
> mindre det underkjennes i etterkant.
>
> Med løpende tilgang til terminlisten og lisensregisteret klassifiseres alt
> maskinelt i det resultatet importeres. Ingen skal godkjenne 130 000
> resultater i året.
>
> Unntakene er arbeidet: underkjenning registreres med årsakskode, og systemet
> løfter fram det som ikke henger sammen.

### «Hva med navneendringer og dubletter?»

> Klubbtilhørighet over tid ligger i egen tabell, så klubbskifter er historikk
> og ikke en overskriving. Utøversammenslåing finnes som verktøy.
> Navneendringshistorikk bygges.
>
> Vi fant en navneendring i den ene kontrollen vi kjørte mot SRUs regneark.
> Slike finner man bare ved å sammenligne mot en uavhengig kilde, og det blir
> en fast del av kvalitetsarbeidet.

### «Hvilket API?»

> Dokumentert JSON-API med OpenAPI-spesifikasjon, nøkkelhåndtering, rate
> limiting og tilgangsstyring per konsument. Utøverdata, resultater, stevner,
> klubb- og regionsstatistikk, statistikklister og aktivitetsdata.
>
> Eksport til Excel og CSV eksponeres i grensesnittet på alle lister, ikke
> bare via API.

### «Hva skjer med dagens lenker?»

`‹Ikke avklart. Vær ærlig.›`

> Det har vi ikke tatt stilling til ennå. Varige lenker til utøvere og stevner
> er verdt å bevare hvis det finnes et mønster å oversette fra, og vi tar det
> gjerne som et punkt i oppstarten.

---

## Fra Roar Holen

Han har bygget stevnesystemet. Behandle spørsmålene hans som fra en kollega,
ikke som angrep.

### «Hvordan har dere tenkt å få data ut av LiveRes?»

Ikke svar med hva vi krever. Svar med hva vi tilbyr, og gi ordet tilbake.

> Vi har ikke forutsatt en bestemt løsning, og vi vil helst bli enige om den
> med deg framfor å finne på noe. Det vi trenger er stevne, øvelse, klasse,
> utøver, klubb, resultat, vind og tidtakingsmetode.
>
> Vi tar imot det i den formen som er minst arbeid for dere: et API, en
> strukturert fil, eller en eksport. Hva ville vært enklest fra din side?

### «Hvorfor ikke bare bygge videre på det som finnes?»

> Vi bygger videre på det som finnes. Det er nettopp poenget vårt: dataene fra
> 2013 og fram til i dag er allerede importert og normalisert, og mye av dem
> stammer fra stevnesystemene.
>
> Det anskaffelsen etterspør er en plattform som holder helheten samlet og
> presenterer den, med eierskap hos NFIF. Stevnesystemene løser en annen
> oppgave, og de to bør snakke sammen framfor å overlappe.

### «Har dere sett på OpenTrack sitt API?»

> Ikke i detalj, og jeg vil ikke påstå noe jeg ikke har verifisert. Vi har
> bygget importrammeverket generisk, med JSON, XML, CSV og Excel, validering og
> godkjenningskø, nettopp fordi vi ikke vet hvilke grensesnitt som blir
> tilgjengelige.

### «Live-resultater under stevnet?»

Ikke lov noe her. Det er stevnesystemets oppgave.

> Det er stevnesystemets domene, ikke vårt. Vi er statistikkplattformen, og
> skal ta imot resultatene når de er klare. Blir det aktuelt å vise dem
> løpende, må det bygges på en flyt fra deres side, og det er en samtale vi
> gjerne tar.

---

## Om vi blir presset på noe vi ikke vet

> Det vet jeg ikke sikkert, og jeg vil ikke gjette på det. Jeg kommer tilbake
> til dere med svar i morgen.

Bruk den. Et ærlig «vet ikke» fra noen som ellers er presis, er verdt mer enn
et raskt svar som viser seg å være feil.

---

## Spørsmål vi bør stille dem

Hvis det blir tid, og som avslutning. Det viser at vi har lest kravspekken.

1. Hvordan meldes underkjenning av stevner og enkeltresultater til
   plattformen, og hvem har myndighet til det?
2. Foreligger et kodeverk for ikke-ratifiserte resultater, eller skal vi
   utarbeide et forslag? Kravspekken sier «TBD».
3. Finnes klubb-til-krets-mapping, og når kan vi få den?
4. Hvor i prioriteringen hører paraidrett hjemme?

De ligger i vedlegg E av tilbudet. Å stille ett eller to av dem muntlig er
bedre enn å stille alle.
