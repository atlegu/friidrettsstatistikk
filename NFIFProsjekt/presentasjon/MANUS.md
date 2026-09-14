# Manus og tidsplan

**Torsdag 17.09.2026, 17:30–17:55 på Teams.**
15–20 min presentasjon, deretter 5–10 min spørsmål.

Budsjett: **18 minutter**, som gir sju til spørsmål.

---

## Hovedgrepet

De skal ikke huske at vi har en stor database. Alle som byr har det, eller
skaffer det. De skal huske at **vi vet hva man gjør med den**.

> Å bygge basen er håndverk og rutiner. Det må ligge i bunn, og vi regner med
> at alle som byr på dette klarer det. Forskjellen ligger i å forstå hvordan
> dataene bør behandles, kunne rette det som er galt, og vite hva folk faktisk
> er ute etter.

Det er lysbilde 4, og det er dreiepunktet i hele presentasjonen. Alt før er
oppvarming, alt etter er dokumentasjon av påstanden.

**Snakk aldri om feil vi selv har hatt.** Det gjør basen mindre troverdig, ikke
mer, og det er ikke det de skal sitte igjen med.

### De tre spørsmålene alt skal svare på

| | Spørsmål | Lysbilde |
|---|---|---|
| 1 | Hvordan kommer siden til å se ut? | Demo, 6, 7 |
| 2 | Kan vi stole på at alle resultater kommer inn framover? | 8, 9 |
| 3 | Hva kan statistikken brukes til? | 7, 10 |

---

## Tidsplan

| Min | Del | Lysbilde |
|---:|---|---:|
| 0:00 | Åpning | 1 |
| 0:30 | Hvem vi er | 2 |
| 1:15 | Utgangspunktet | 3 |
| 2:00 | **Hva som egentlig skiller** | 4 |
| 3:00 | **Demo** | 5 |
| 10:00 | Slik presenterer vi tallene | 6 |
| 11:00 | Presentasjon er en kapasitet | 7 |
| 12:00 | Trygghet for at alt kommer inn | 8 |
| 13:30 | Å finne og rette | 9 |
| 14:45 | Hva statistikken kan brukes til | 10 |
| 16:00 | Veien til nyttår | 11 |
| 16:45 | Integrasjoner og videre | 12 |
| 17:20 | Det vi trenger | 13 |
| 17:45 | Oppsummering | 14 |

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
> for den finnes allerede og er lettere å se enn å beskrive. Underveis svarer
> jeg på tre ting: hvordan siden ser ut, hvordan dere kan være trygge på at alt
> kommer inn framover, og hva statistikken kan brukes til.

Å si de tre punktene med én gang gjør at de vet hva de får, og det er nettopp
det de spurte om.

### Hvem vi er · 45 sekunder

Tre navn, én setning hver. Det som skal feste seg:

> Doktorgrad i anvendt økonometri og World Athletics-dommerkompetanse i samme
> person. To av oss konkurrerer selv internasjonalt og har egne resultater i
> basen.

### Utgangspunktet · 45 sekunder

Ett tall: **1 953 356**. Ikke dvel.

> Migreringen er gjennomført. Det betyr at vi skal ferdigstille, ikke bygge fra
> bunnen — og at vi kan bruke tiden i dag på noe mer interessant enn hvordan vi
> har tenkt å få dataene inn.

Den siste setningen leder rett inn i lysbilde 4.

### Hva som egentlig skiller · 1 minutt

**Dette er det viktigste minuttet.** Ta det rolig.

> Å bygge selve basen er håndverk og rutiner. Det må ligge i bunn, og jeg går
> ut fra at alle som byr på dette klarer det. En database med resultater i er
> ikke et konkurransefortrinn.
>
> Forskjellen ligger tre andre steder. Å forstå hvordan dataene bør behandles —
> aldersklasser etter kalenderår, håndtidtaking bare under 800 meter, redskap og
> hekkhøyde per klasse. Det er regelverk, ikke programmering.
>
> Å kunne rette det som er galt. Feil oppstår i alle baser. Spørsmålet er om
> noen finner dem.
>
> Og å vite hva folk faktisk er ute etter. En utøver, en trener, en klubb, en
> statistikker og en journalist vil ha helt ulike ting ut av de samme tallene.

Å si at konkurrentene klarer grunnarbeidet er sjenerøst, og det leses som
selvtillit. Det flytter samtalen dit vi er sterkest.

### Demo · 7 minutter

Se `DEMO.md`. Si hva du skal vise før du klikker.

### Slik presenterer vi tallene · 1 minutt

Seks brukere, seks behov. Gå gjennom tabellen raskt.

> Det er den samme basen. Forskjellen er hva man løfter fram, og det er
> domenekunnskap mer enn teknologi.

### Presentasjon er en kapasitet · 1 minutt

Klubbrapportene. Dette er det beste konkrete beviset vi har.

> Fire klubber har fått skreddersydde rapporter. Vidar ville ha yngste først
> med markering av klubbskifte, Tjalve ville ha stipendgruppene A til D, Fana
> ville ha seksten navngitte utøvere øverst i sin egen rekkefølge.
>
> De deler felles maskineri. En ny klubb er rundt tjue linjer konfigurasjon.
> De fikk ulikt fordi de ba om ulikt, ikke fordi vi bygget fire ganger.

### Trygghet for at alt kommer inn · 90 sekunder

Spørsmål 2, og det viktigste for Thor og Magnus.

> Vi henter i dag resultatene fra den basen som skal erstattes. Fra oktober
> blir plattformen selv førstemottaker, direkte fra arrangør og tidtakersystem,
> og vi kjører begge kilder parallelt ut året så vi ser at ingenting faller ut.
>
> Så er det rutinene. Hvert stevne telles mot kilden, ikke bare sjekkes om det
> finnes. Det er en viktig forskjell. Og systemet kontrollerer hver rad mot det
> som er fysisk og regelmessig rimelig.

Avslutt med at innsamling ligger i driftsavtalen, ikke som opsjon. Det er et
kommersielt poeng Magnus vil merke seg.

### Å finne og rette · 75 sekunder

SRU-eksempelet er konkret og gjenkjennelig for alle i rommet.

> Vi kjørte basen mot SRUs NM-regneark for 100 meter kvinner. Regnearket hadde
> 101 navn, vi fant 97, og 89 var de samme. Avvikene var navnevarianter, en
> navneendring og en utenlandsk utøver i norsk klubb — nettopp det §9 og §7 ber
> plattformen håndtere.
>
> Vi lover ikke en feilfri base. Vi lover at feilene er kjente, tellbare og
> synkende, og at det finnes verktøy for å rette dem.

### Hva statistikken kan brukes til · 75 sekunder

Spørsmål 3. Mesterskap og media, klubb og krets, forbundets egne beslutninger,
forskning.

Stopp på simuleringen:

> Konsekvensen av å endre et kvalifiseringskrav kan beregnes før vedtaket
> fattes, i stedet for å observeres to år etter.

Det er den setningen som pleier å få folk til å se opp.

### Resten · 2,5 minutter

Frister, integrasjoner, hva vi trenger. Raskt. Se til Roar Holen når du
snakker om stevnesystemene, og still ham gjerne spørsmålet:

> Roar, hva ville vært den enkleste veien ut av LiveRes for dere?

### Oppsummering · 15 sekunder

Tre punkter, og så stille. Ikke fyll pausen.

---

## Praktisk

- **Rull ut forsidefiksen før møtet.** Se `README.md`.
- **Logg inn i admin på forhånd.** Ikke skriv passord på delt skjerm.
- Steng varsler og e-post. Del **fane**, ikke hele skjermen.
- Om demoen henger: gå videre. Skjermbildene i `reserve/` viser det samme.
- Ha `TILBUD.pdf` åpen i tilfelle noen refererer til et kapittel.
