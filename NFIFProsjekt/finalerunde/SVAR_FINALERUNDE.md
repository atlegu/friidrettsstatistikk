# Ny statistikkplattform – avsluttende avklaringer

**Svar fra Athlete Mindset AS** · Finalerunde november 2026 · UTKAST

Svarene følger rekkefølgen i NFIFs dokument. Der noe er planlagt og ikke ferdig, står det.

# 1. Funksjonalitet og tilgangsstyring

## 1a. Demonstrasjon

Vi viser hvordan NFIF og statistikkutvalget arbeider i løsningen:

1. **Avvikslisten.** En mulig rekord legges frem og godkjennes eller underkjennes. Dette er NFIFs og SRUs viktigste oppgave.
2. **Import av en innsendt resultatliste.** Utøverne kobles automatisk, og rader som allerede ligger inne, hoppes over.
3. **Ikke godkjente resultater** med årsak, slik de vises på utøver- og stevnesidene.
4. **Terminlisten.** Hva som mangler resultater, og purring av arrangører.
5. **Statistikk og uttrekk.** Årslister, masters, klubbstatistikk og nedlasting til Excel med logg.

Arbeidsdelingen er den samme som i forrige svarrunde. NFIF og SRU ser alt, avgjør det forbundet skal avgjøre, og melder feil. Vi gjør innlesingen, kvalitetssikringen og rettingene. NFIF skal ikke måtte lese inn og kvalitetssikre resultater selv. Det er det driftsavtalen dekker.

## 1b. Hva NFIF kan gjøre selv

**NFIF kan gjøre selv:**

- Se all statistikk og hente ut lister til Excel og CSV. Nedlastingene logges. *Finnes i dag for administratorer.*
- Godkjenne mulige rekorder og bestenoteringer, underkjenne resultater med årsak, og markere avvik som riktige. *Finnes i dag i avvikslisten. Rekordgodkjenning med dokumentasjon kommer i januar–februar 2027.*
- Følge opp terminlisten: markere arrangementer som purret, avlyst eller uten resultater. *Finnes i dag.*
- Laste opp resultatlister til en godkjenningskø. *Finnes i dag.*
- Administrere brukere i egen organisasjon, for eksempel krets og klubb. *Planlagt sammen med Idrettens ID.*

**NFIF bestemmer, vi legger inn:** regler og parametere som aldersgrense for synlighet, kodene for underkjenning og vindregler. Vi legger også inn kvalifiseringskravene til NM, og etter hvert til junior-NM og UM. Dette inngår i driften.

**Endringer i basen,** som retting av resultater, sammenslåing av utøvere og publisering av importer, gjør Athlete Mindset. Det gir én ansvarlig for at dataene er riktige, og alle endringer kan spores. Feil meldes til oss og rettes innen fristene for brukerstøtte. Dette inngår i driftsprisen.

**Koster ekstra:** nye funksjoner, nye rapporter og nye kontrollregler faktureres med 950 kr per time etter avtale på forhånd. Eldre statistikk og kretsenes egne statistikker prises per tilfelle.

**Brukerstøtte:** e-post og telefon på norsk i arbeidstiden. Kritiske feil behandles samme virkedag, andre henvendelser innen to virkedager. Under NM, Bislett Games og andre mesterskap er vi lettere tilgjengelige. Inngår i driftsprisen.

**Opplæring:** Ved oppstart inngår én digital opplæringsøkt på to–tre timer for superbrukerne og SRU, og en kort skriftlig brukerveiledning. Mer opplæring, for eksempel for kretser og klubber, faktureres per time.

## 1c. Roller og tilganger

| Rolle | Hva rollen kan gjøre | Status |
|---|---|---|
| Publikum, uten innlogging | All offentlig statistikk for utøvere fra 13 år | Finnes i dag |
| Klubb | Se og hente ut statistikk for egen klubb. Melde feil på egne utøvere. Laste opp resultatlister fra egne stevner til godkjenningskøen | Planlagt 2027 |
| Krets | Se og hente ut statistikk og aktivitet for klubbene i kretsen. Følge opp terminlisten for kretsens stevner | Planlagt 2027. Forutsetter klubbenes kretstilhørighet fra NFIF |
| SRU / statistikkutvalget | Nasjonal statistikk og uttrekk. Godkjenne rekorder og bestenoteringer, underkjenne resultater med årsak, behandle avvik | Finnes i dag gjennom administratorrollen. Egen rolle planlagt |
| Masters-ansvarlig | Som SRU, men bare for masters | Planlagt |
| NFIF-administrator | Alt SRU kan, pluss brukere og roller for NFIF og kretsene, og oppfølging av terminlisten | Finnes i dag |
| Stevneprogram (API-nøkkel) | Hente personlig rekord og årsbeste for påmeldte utøvere, til heatoppsett og startlister | Planlagt. Forutsetter tilpasning hos leverandørene |
| Athlete Mindset (drift) | Endringer i basen: retting, sammenslåing, publisering av importer | Finnes i dag |

**Prinsipper:**

- Ingen rolle utenfor Athlete Mindset endrer basen direkte. Alt de gjør, er avgjørelser, feilmeldinger eller opplastinger til godkjenningskøen.
- Alle avgjørelser og nedlastinger logges med hvem og når.
- Hver rolle ser bare det den trenger. Klubb og krets ser egne data.

Arrangørene trenger utøvernes personlige rekord og årsbeste ved påmelding, blant annet til heatoppsett. Vi skal lage en tilgang i API-et for dette, slik at stevneprogrammene, som Roster, OpenTrack og FriSys, kan hente tallene direkte. Hver leverandør får en egen API-nøkkel.

**Avklares med NFIF:** om klubbene skal se egne utøvere under 13 år, jf. 1e.

## 1d. Innlogging og Idrettens ID

**Ved oppstart:** De få brukerne i NFIF og SRU logger inn med e-post og passord, slik administrasjonsverktøyet fungerer i dag. Roller tildeles og fjernes manuelt av NFIFs administrator, og vi går gjennom tilgangene hvert år.

**Idrettens ID:** Når klubber og kretser skal inn, blir Idrettens ID hovedinnloggingen. NIF krever det for at vi skal få bruke oppslagene deres. Vi kan da hente personens roller fra idrettens register, slik at tilgangen følger vervet i klubben eller kretsen og forsvinner når vervet opphører. Der registeret ikke har en passende rolle, tildeles den manuelt.

**Status hos NIF:** Vi har vært i kontakt med NIF IT. De opplyser at tilgang krever aksept fra NFIF, og at prisen avhenger av om vi er offisiell leverandør til forbundet: fra 0 til om lag 30 000 kr i året. NIF gir ikke endelig pris før dette er avklart. Integrasjonen kan derfor ikke prises nå. Den prises når NFIF har gitt aksept og vi har fått pris og dokumentasjon fra NIF. Avgiftene til NIF betales av NFIF.

## 1e. Personvern og sikkerhet

**Roller:** NFIF er behandlingsansvarlig, og Athlete Mindset AS er databehandler. Databehandleravtale og vurdering av personvernkonsekvenser (DPIA) er på plass før driftsstart.

**Mindreårige:** Statistikk for utøvere under 13 år er ikke offentlig. Vi har strammet inn dette i løsningen, og innstrammingen pågår. Barn vil i dag likevel kunne finnes i resultatlistene fra stevnene, for eksempel ved søk på navn. Hvordan resultatlistene skal behandle utøvere under 13 år, hvem som skal kunne se dem, og om utøvere under 10 år bare skal registreres med deltakelse, vil vi sette oss ned med NFIF og lage en klar og tydelig policy for. Løsningen tilpasses deretter. Grensene ligger ett sted i løsningen og kan endres uten ny utvikling. Offentlig vises bare fødselsår, ikke full fødselsdato.

**Tilgangslogg:** Nedlastinger og avgjørelser i avvikslisten logges i dag med hvem og når. Full logg over alle endringer kommer sammen med rollene i 2027.

**Lagring:** Databasen ligger i EU, i Stockholm. Underleverandører som behandler personopplysninger, listes i databehandleravtalen, og personopplysninger behandles innenfor EU/EØS eller med gyldig overføringsgrunnlag.

**Innsyn, retting og sletting:** Henvendelser fra utøvere eller foresatte behandles etter en fast rutine med frister, og NFIF holdes orientert.

# 2. API og integrasjoner

## 2a. Status per integrasjon

**Slik kommer resultatene inn:** Arrangøren velger stevneprogram, ikke vi. Plattformen tar derfor imot resultater fra alle stevner, uansett system:

- **Stevner som bruker FriSys:** Vi har fått tilgang til FriSys-dataene og testet formatet. Resultatene hentes direkte.
- **Øvrige stevner:** Resultatlistene som kommer inn via iSonen til resultater@friidrett.no, behandles av oss og legges inn med automatisk kobling av utøvere og kontroll mot dubletter. Over 90 prosent av listene kommer i fire kjente formater: NFIFs mal, FriSys, OpenTrack og Roster.
- **Målet over tid** er at flest mulig stevneprogrammer sender resultatene direkte til basen. Det gir raskere og sikrere listeføring. Roster sender allerede resultater direkte til andre statistikktjenester, så et tilsvarende oppsett mot oss bør være enkelt å få på plass. OpenTrack har et åpent API.

**Løp utenfor bane:**

- **EQ Timing:** Importen fungerer og er testet på hele 2026 (640 arrangementer, 158 793 resultater).
- **Ultimate Sport Service:** Importen er bygget og formatet testet. Hvilke løp som skal inn, avklares med NFIF.
- **Andre tidtakere,** for eksempel Racedays: planlagt.

**Øvrige:**

- **iSonen:** NIF IT har bekreftet at arrangementer og deltakere kan hentes via API. Tilgang krever aksept fra NFIF.
- **Norske resultater i utlandet:** World Athletics, internasjonale resultatdatabaser, og TFRRS for utøvere ved universiteter i USA. Vi samarbeider gjerne med SRU, som følger med på resultater i utlandet i dag.

## 2b. Tredjeparter, ansvar og tidslinje

Vi har undersøkt hva som er teknisk mulig, men vi kan ikke forhandle avtaler med tredjeparter før vi har en avtale med NFIF. Leverandørene og NIF gir ikke tilgang eller priser til en aktør som ikke er NFIFs leverandør. NIF har bekreftet dette for iSonen.

**Ansvar:** Athlete Mindset følger opp alle leverandørene. NFIF bidrar med en skriftlig bekreftelse på at vi er NFIFs leverandør, som vi kan vise til, og aksept overfor NIF for iSonen og Idrettens ID.

**Tidslinje fra signering:**

- **Desember 2026:** Kontakt med leverandørene av stevneprogrammer (FriSys, Roster, OpenTrack), med tidtakerne og med NIF om iSonen.
- **Q1 2027:** Avtaler med EQ Timing og Ultimate. iSonen når NFIF har gitt aksept.
- **Gjennom 2027:** Direkte overføring fra flere stevneprogrammer, i det tempoet leverandørene klarer.

Frem til overtakelsen oppdateres basen hver natt fra dagens statistikk. Fra en avtalt overtakelsesdato samler vi inn alle nye resultater selv: direkte fra stevneprogrammene der det er mulig, og ellers fra resultatlistene som kommer via iSonen og resultater@friidrett.no. Dagens statistikk forblir tilgjengelig som historisk arkiv. Ingen stevner faller ut, fordi terminlisten kontrolleres mot basen hver natt.

# 3. Implementering og oppstart

## 3a. Tidsplan

Tidsplanen i tilbudet forutsatte en avtale tidligere i høst. Vi har bevisst ventet med arbeid som krever avtale med NFIF og med tredjeparter. Med signering innen utgangen av november er planen denne:

**Desember 2026: mottak og kvalitetssikring.** Hele teamet settes på mottaket av resultatlister:

- En egen e-postkonto for resultatlister, med automatisk henting og tolkning av vedleggene.
- Kontroll og godkjenning før publisering.
- Direkte henting fra stevneprogrammene der det er mulig.
- De fire formatene som dekker over 90 prosent av listene: NFIFs mal, FriSys, OpenTrack og Roster.
- Databehandleravtale og personvernvurdering signeres.

**1. januar 2027: overtakelse.** All banestatistikk er i drift med egen innsamling fra innendørssesongens start. Større stevner prioriteres, og resultatene legges inn senest dagen etter.

**Januar–februar 2027: kontroll og ferdigstilling.**

- Basen kontrolleres mot dagens statistikk, i samarbeid med dagens statistikkansvarlig, slik at overføringen er komplett og riktig.
- Dokumentert API, kvalitetsnivå A, B og C, og rekordgodkjenning i administrasjonsverktøyet.
- Første versjon av søket etter norske resultater i utlandet.

**Vinteren 2027:** Kvalitetssikring av eldre data, og innhenting av mer historikk etter NFIFs valg.

**Q1–Q2 2027:** Løp utenfor bane og integrasjoner, jf. 2a.

**Kritiske avhengigheter:**

- Signering innen utgangen av november.
- At resultatlistene fra iSonen og arrangørene sendes til vår adresse fra overtakelsen.
- Samarbeid med dagens statistikkansvarlig om overgangen og kontrollen.
- Aksept overfor NIF for iSonen og Idrettens ID.

## 3b. Historiske data

**Allerede overført:** Alle resultater fra dagens statistikk fra 2013, og alle tiders-listene fra før 2013. Til sammen rundt 1,47 millioner baneresultater. Overføringen kontrolleres i januar–februar mot dagens statistikk, slik at den er komplett og riktig.

**Ansvar:** Athlete Mindset har ansvaret for overføring og kvalitetssikring. NFIF avgjør hva mer som skal hentes inn.

**Ikke inkludert i etableringsprisen:** Eldre statistikk utover dette, og kretsenes egne statistikker. Kvalitet og format varierer mye, så dette prises per tilfelle etter avtale med NFIF.

## 3c. Hva vi trenger fra NFIF

**Ved signering:**

- Et oppstartsmøte så snart avtalen er signert.
- En skriftlig bekreftelse på at vi er NFIFs leverandør, som vi kan vise til overfor leverandører og tidtakere.
- Aksept overfor NIF for tilgang til iSonen, Idrettens ID og lisensregisteret.
- At resultatlistene fra iSonen og arrangørene sendes til vår adresse fra overtakelsen. Enten videresender NFIF resultater@friidrett.no, eller så endres mottakeradressen i iSonen.
- Databehandleravtale signert.
- Overtakelsesdato, avtalt sammen med dagens statistikkansvarlig.

**Kontaktpersoner:**

- Én kontaktperson i NFIF for avtalen og beslutninger.
- En kontakt i SRU for rekorder og regeltolkning.
- Den som er ansvarlig for mastersrekordene, for å gå gjennom avvikslisten.
- Dagens statistikkansvarlig, for overgangen og kontrollen av at overføringen er komplett.

**Data:**

- Klubbenes kretstilhørighet, som trengs for kretsstatistikken.
- Kodene for underkjente resultater, som kravspesifikasjonen har satt som «TBD».
- Kvalifiseringskravene til NM, junior-NM og UM når de vedtas.

**Beslutninger, i januar 2027:**

- Policy for barn: hvordan utøvere under 13 år vises i resultatlistene, og om utøvere under 10 år bare registreres med deltakelse.
- Omfanget av løp utenfor bane: hvilke løp og resultater som skal inn, og hvordan løpere uten klubb og uten kjent alder skal behandles.
- Grensedragninger for eldre data, blant annet vind.
- Hvilken historikk som skal hentes inn utover det som allerede er overført.
- Regler for kvalitetsnivå A, B og C.
- Hvem som skal ha hvilke roller ved oppstart.

# 4. Økonomisk soliditet og sårbarhet

## 4a. Deponering

Ja. All programvaren, både for innsamling og kvalitetssikring og for presentasjon, deponeres hos en uavhengig deponeringsagent og oppdateres jevnlig. Athlete Mindset dekker kostnaden.

NFIF får i avtalen en bruksrett til programvaren som gjelder ved konkurs eller avvikling. Ved en slik hendelse utleveres programvaren og driftsdokumentasjonen fra deponiet, og NFIF kan drive plattformen videre selv eller med en leverandør NFIF velger. Bruksretten gjelder NFIFs egen drift av statistikken, ikke videresalg.

I tillegg eier NFIF dataene fullt ut. Vi tilbyr en automatisk kopi av hele databasen til et lagringssted NFIF eier, slik at dataene alltid ligger hos NFIF.

## 4b. Sikkerhetsstillelse og ansvar

NFIFs risiko holdes lav gjennom selve avtalen:

- Etableringen faktureres med halvparten ved signering og halvparten ved driftsstart. Første halvdel dekker løsningen som allerede er utviklet og som NFIF får tilgang til fra signering. Driften faktureres kvartalsvis.
- Dataene ligger alltid også hos NFIF, og programvaren er deponert, jf. 4a.
- Avtalen kan ikke overdras til andre uten NFIFs samtykke.

Ansvarsforsikring kan tegnes dersom NFIF krever det. Kostnaden legges da til prisen.

**Ansvarsbegrensning:** Indirekte tap dekkes ikke. Samlet erstatning per avtaleår er begrenset til ett års vederlag. Begrensningen gjelder ikke ved grov uaktsomhet eller forsett. Ansvar knyttet til personopplysninger reguleres i databehandleravtalen. Vi svarer ikke for tjenester vi ikke styrer, som NIF, iSonen, tidtakere og skyleverandører, eller for feil i resultatlistene vi mottar.

# 5. Avtalevilkår

## 5a. Avtaleperiode og priser

Vi bekrefter en avtaleperiode på fem år, med opsjon for NFIF på forlengelse to år av gangen, med varsel seks måneder før utløp.

**Priser for femårsperioden, eks. mva.:**

- **Nasjonal banestatistikk:** etablering 350 000 kr og drift 300 000 kr i året.
- **Gateløp:** etablering 300 000 kr, inkludert integrasjon mot inntil fire tidtakere med API eller datafil, og drift 200 000 kr i året.
- **Integrasjon mot iSonen og lisensregisteret:** inntil 80 000 kr. NIFs avgifter kommer i tillegg.
- **Idrettens ID:** prises når NIF har gitt pris, jf. 1d.

Prisene reguleres etter konsumprisindeksen fra år fire, slik vi oppga i forrige svarrunde. Ved forlengelse gjelder de KPI-regulerte prisene.

## 5b. Oppsigelse

- **Ved vesentlig mislighold** kan begge parter heve avtalen etter skriftlig varsel og en frist på 30 dager til å rette forholdet.
- **Uten særskilt grunn** kan NFIF si opp avtalen med seks måneders varsel. Etableringsprisen er redusert fordi vi har lagt til grunn et samarbeid i fem år. Ved oppsigelse før det betaler NFIF derfor en forholdsmessig del av reduksjonen på 360 000 kr: 4/5 etter ett år, 3/5 etter to år og så videre.
- **Athlete Mindset** kan ikke si opp i avtaleperioden, bortsett fra ved mislighold. Ved utløp gir vi 12 måneders varsel hvis vi ikke ønsker å fortsette.
- **Ved heving på grunn av vårt mislighold** betales ingenting tilbake.

## 5c. Eierskap, utlevering og sletting

Løsningen har tre deler:

- **Dataene,** det vil si hvert resultat med utøver, stevne, dato, klubb og øvrige opplysninger, eies av NFIF.
- **Programvaren for innsamling og kvalitetssikring** eies av Athlete Mindset AS.
- **Programvaren for presentasjon** eies av Athlete Mindset AS.

**Ved avslutning, uansett årsak,** får NFIF alle data utlevert i åpne formater (CSV og en standard PostgreSQL-dump) innen 30 dager. Utleveringen følger med en overordnet dokumentasjon av datamodellen og reglene, og er uten gebyr. Ved ordinær oppsigelse eller utløp følger ikke programvaren med. Ved konkurs eller avvikling får NFIF bruksrett til programvaren fra deponiet, jf. 4a.

**Sletting:** Når NFIF har bekreftet at dataene er mottatt, slettes de hos oss og hos våre underleverandører. Vi gir skriftlig bekreftelse på slettingen, i tråd med databehandleravtalen.

## 5d. Overgang til ny leverandør

Vi bistår ved overgang til NFIF eller en ny leverandør etter timepris, 950 kr per time, etter avtale på forhånd. En ny leverandør kan ta dataene i bruk med en gang gjennom de åpne formatene, det dokumenterte API-et og dokumentasjonen av datamodellen.

# 6. Økonomi

## 6a og 6b. Ytterligere reduksjon

Vi har allerede redusert etableringsprisen med 51 prosent, og driftsprisen er satt lavt for den jobben den dekker: innsamling, kvalitetssikring og avviksbehandling, slik at NFIFs egen innsats holdes under én time i uken. Vi ser ikke rom for ytterligere reduksjon uten å kutte i omfanget.

I stedet gir vi NFIF mer trygghet. Ved konkurs eller avvikling får NFIF bruksrett til all programvaren, både innsamling, kvalitetssikring og presentasjon, fra et deponi som Athlete Mindset betaler for, jf. 4a. NFIF kan da drive plattformen videre uten avbrudd. Sammen med at NFIF eier dataene og har en løpende kopi av dem, fjerner dette risikoen ved å velge en mindre leverandør.

## 6c. Revidert tilbud

Etter møtet sender vi et revidert, skriftlig tilbud der prisene og det som er avtalt i møtet, fremgår tydelig.
