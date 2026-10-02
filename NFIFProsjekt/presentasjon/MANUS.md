# Manus og tidsplan

**Teams, 17:30–17:55.** 15–20 min presentasjon, deretter 5–10 min spørsmål.

Budsjett: **18 minutter**, som gir sju til spørsmål.

---

## Hovedgrepet

De skal ikke huske at vi har en stor database. Alle som byr har det, eller
skaffer det. De skal huske **fire ting de kan stole på**, og at vi allerede
gjør dem.

| | Det de skal sitte igjen med | Lysbilde |
|---|---|---:|
| 1 | Alt kommer inn, hver natt, og alt kvalitetssikres | 5, 6 |
| 2 | Visningen er laget av folk som kjenner idretten, også for klubb og krets | 7–11 |
| 3 | Rapporter og analyser, på tre måter | 12–14 |
| 4 | Stabilt, raskt, levert fortløpende, med kapasitet | 15 |

Lysbilde 4 sier de fire punktene høyt. Alt etter er dokumentasjon.

**Snakk aldri om feil vi selv har hatt.** Det gjør basen mindre troverdig, ikke
mer. Snakk om hva systemet gjør: henter på nytt, avstemmer, flagger, sletter
aldri.

---

## Tidsplan

| Min | Del | Lysbilde |
|---:|---|---:|
| 0:00 | Åpning | 1 |
| 0:30 | Hvem vi er | 2 |
| 1:15 | Utgangspunktet | 3 |
| 2:00 | **Fire ting dere skal kunne stole på** | 4 |
| 3:00 | 1 · Alt kommer inn: tre innsamlingsløp | 5 |
| 4:30 | 1 · Alt kvalitetssikres | 6 |
| 6:00 | **2 · Demo** | 7 |
| 12:00 | 2 · Tre sider i drift: profil, klubb, aktivitet | 8–10 |
| 13:00 | 2 · Samme base, sju behov | 11 |
| 13:45 | 3 · Rapporter og analyser, tre måter | 12 |
| 14:45 | 3 · §12, telle og forstå | 13 |
| 15:45 | 3 · Hva analysene ellers kan brukes til | 14 |
| 16:15 | **4 · Stabilt, raskt, levert siden tilbudet** | 15 |
| 17:00 | Veien til nyttår · integrasjoner · behov | 16–18 |
| 17:45 | Oppsummering | 19 |

---

## Hvem er i rommet

| Person | Rolle | Hva de lytter etter |
|---|---|---|
| **Thor Gjesdal** | NFIF, teknisk kontakt | Datamodell, regelverk, flagging, API. Kjenner kravspekken best. |
| **Magnus Trosdahl** | Seksjonsleder NFIF | Kostnad, risiko, leveranseevne, hva NFIF må stille med. |
| **Roar Holen** | Laget FriSys / LiveRes, stevnesystemet arrangørene bruker | Hvordan vi tenker om integrasjon. Han er motparten i §13. |
| **Hilde Trageton** | `‹rolle ukjent — finn ut før møtet›` | |

### Roar Holen er det viktigste å planlegge for

Han har bygget systemet resultatene våre skal komme fra, og er den i rommet
som kjenner dataflyten best.

**Gjør:** behandle LiveRes som en kilde vi gleder oss til å koble oss på.
Spørre ham direkte hva han mener er riktig måte å levere resultatlister på.

**Ikke gjør:** si at vi ikke kan prise integrasjoner «før motparten stiller
med dokumentert API». Det står i tilbudet, og det er riktig, men sagt høyt med
motparten til stede blir det en anklage.

---

## Del for del

### Åpning · 30 sekunder

> Takk for invitasjonen. Jeg bruker mesteparten av tiden på å vise løsningen,
> for den finnes allerede og er lettere å se enn å beskrive. Underveis går jeg
> gjennom fire ting dere skal kunne stole på: at alt kommer inn og
> kvalitetssikres, at visningen er god, at dere får rapporter og analyser, og
> at det er stabilt, raskt og levert fortløpende.

### Hvem vi er · 45 sekunder

Tre navn, én setning hver. Det som skal feste seg:

> Doktorgrad i anvendt økonometri og World Athletics-dommerkompetanse i samme
> person. To av oss konkurrerer selv internasjonalt og har egne resultater i
> basen.

### Utgangspunktet · 45 sekunder

Ett tall. Ikke dvel.

> Migreringen er gjennomført. Det betyr at vi skal ferdigstille, ikke bygge fra
> bunnen, og at vi kan bruke tiden i dag på hva vi gjør med dataene.

### Fire ting dere skal kunne stole på · 1 minutt

**Dette er dreiepunktet.** Ta det rolig, si alle fire.

> Én: alt kommer inn. Norske stevner, utenlandske stevner og løp utenfor bane,
> hentet fortløpende av automatiske agenter, og kvalitetssikret før det vises.
>
> To: visningen. Her mener vi at vi er bedre enn andre, fordi vi kjenner idretten
> og vet hva som er ønskelig.
>
> Tre: rapporter og analyser. Standardrapporter, skreddersøm, og et system der
> klubb, krets og utøver lager sine egne.
>
> Fire: stabilt, raskt, og levert fortløpende. Med kapasitet til å holde det
> gående gjennom hele avtaleperioden.

### 1 · Alt kommer inn · 90 sekunder

Tre rader i tabellen, én setning hver, og så poenget om agenter.

> Norske stevner er det enkle: alt sendes til samme sted. Formatene varierer
> noe, og det håndterer vi. Fra oktober er plattformen selv førstemottaker.
> I dag hentes de hver natt klokken kvart over fire, avstemmes mot kilden, og
> tolv kontroller kjøres etterpå. Forsiden viser når det sist skjedde.
>
> Utenlandske stevner krever egne agenter per kildetype: TFRRS for
> collegeutøverne, World Athletics og European Athletics, de nordiske basene,
> og stevnenes egne sider. Vi følger de norske utøverne, ikke hvert stevne i
> verden. Det er forskjellen som gjør det gjennomførbart.
>
> Løp utenfor bane knytter vi til den offisielle terminlisten, for det er de
> resultatene som skal inn. Og de får en egen inngangsside, så det ikke drukner
> banestatistikken.
>
> Agentene kjører kontinuerlig. Innsamling er en driftsfunksjon, og den ligger
> i driftsavtalen.

Det siste er et kommersielt poeng Magnus vil merke seg.

### 1 · Alt kvalitetssikres · 90 sekunder

Det viktigste for Thor. Begynn med det få tenker på:

> Kilden endres i ukene etter et stevne. Vind legges til, plasseringer rettes.
> Derfor henter vi hvert stevne på nytt i seks uker og avstemmer rad for rad.
> Endret oppdateres, nytt legges inn, og det som forsvinner fra kilden slettes
> aldri hos oss. Det merkes og havner i arbeidslisten.
>
> Så kontrollerer systemet hver rad mot det som er fysisk og regelmessig rimelig,
> og menneskene ser på unntakene.
>
> Og vi måler. Mot SRUs NM-regneark for 100 meter kvinner: 101 navn, vi fant 97,
> 89 var de samme. Avvikene var navnevarianter og en navneendring, nettopp det
> §7 og §9 ber om.

### 2 · Demo · 6 minutter

Se `DEMO.md`. Si hva du skal vise før du klikker. Innled med én setning:

> Dette er punktet der vi mener vi er bedre enn andre. Ikke teknologien, men at
> vi vet hva folk leter etter.

### 2 · Tre sider i drift, og sju behov · 1 minutt 45

Tre skjermbilder, raskt. Poenget er at skissene i tilbudet ble til sider på tre
uker:

> Dette var skisser i tilbudet. Nå er det sidene. Utøverprofilen, klubbsiden
> som er skreddersømmen for klubb og krets, og aktivitetsdashbordet som er §12.

Så tabellen:

> Det er den samme basen. Forskjellen er hva man løfter fram, og det er
> domenekunnskap mer enn teknologi. Kretsene får klubbsiden for sine klubber
> den dagen vi har klubb-til-krets-koblingen fra dere.

### 3 · Rapporter og analyser · 1 minutt

De tre måtene, og så klubbrapportene som bevis.

> Rapporter blir til på tre måter. Vi ser noe i tallene og lager det. Noen ber
> om noe bestemt. Eller klubb, krets og utøver velger en standardrapport og får
> den på egne tall.
>
> Fire klubber har allerede fått sitt. De fikk ulikt fordi de ba om ulikt, ikke
> fordi vi bygget fire ganger. En ny klubb er rundt tjue linjer konfigurasjon.

### 3 · §12 · 1 minutt

**Ikke hopp over dette.** Det eneste stedet kravspekken sier «particularly
important».

> Tallene er hentet fra basen i dag. Men: teller man klubber med resultater,
> faller tallet over tjue prosent fra 2024 til 2025. Det er ikke klubber som
> legger ned. Det som forsvant var skoler og små lag innom ett stevne. Klubber
> med minst tjue resultater i året er 271 mot 262. Et dashbord som rapporterer
> tjue prosent som klubbdød, gir dere feilinformasjon. Det er forskjellen på å
> telle og å forstå.

### 3 · Ellers · 30 sekunder

Stopp på simuleringen:

> Konsekvensen av å endre et kvalifiseringskrav kan beregnes før vedtaket
> fattes, i stedet for å observeres to år etter.

### 4 · Stabilt, raskt, levert siden tilbudet · 45 sekunder

> Norges største stevneside leveres på 1,2 sekunder. Målt, ikke anslått. Tolv
> automatiske kontroller etter hver import. Og siden vi sendte tilbudet
> 31. august har vi levert ny utøverprofil, aktivitetsdashbord, klubbstatistikk,
> NM-medaljer og nattlig innsamling. Små, ferdige steg, rullet ut samme dag.
> Slik jobber vi, og leveransen ligger hos tre navngitte personer.

Om kapasitet i timer kommer opp: ha tallet klart. Se `README.md`.

### Resten · 45 sekunder

Frister, integrasjoner, hva vi trenger. Raskt. Se til Roar Holen når du
snakker om stevnesystemene, og still ham gjerne spørsmålet:

> Roar, hva ville vært den enkleste veien ut av LiveRes for dere?

### Oppsummering · 15 sekunder

De fire punktene én gang til, og så stille. Ikke fyll pausen.

---

## Praktisk

- **Logg inn i admin på forhånd.** Ikke skriv passord på delt skjerm.
- Steng varsler og e-post. Del **fane**, ikke hele skjermen.
- Om demoen henger: gå videre. Skjermbildene i `reserve/` viser det samme.
- Ha `TILBUD.pdf` åpen i tilfelle noen refererer til et kapittel.
