# Manus og tidsplan

**Torsdag 17.09.2026, 17:30–17:55 på Teams.**
15–20 min presentasjon, deretter 5–10 min spørsmål.

Budsjett: **18 minutter**, som gir sju til spørsmål. Det er stramt. Demoen er
det viktigste, så den får mest tid.

| Min | Del | Lysbilde |
|---:|---|---|
| 0:00–0:30 | Åpning | 1 |
| 0:30–1:30 | Hvem vi er | 2 |
| 1:30–2:30 | Utgangspunktet | 3 |
| 2:30–9:30 | **Demo** | 4 |
| 9:30–11:00 | Migrering | 5 |
| 11:00–13:30 | Opprydding | 6–8 |
| 13:30–15:30 | Veien til nyttår | 9 |
| 15:30–16:30 | Integrasjoner | 10 |
| 16:30–17:30 | Etter nyttår og behov | 11–12 |
| 17:30–18:00 | Oppsummering | 13 |

---

## Hvem er i rommet

| Person | Rolle | Hva de lytter etter |
|---|---|---|
| **Thor Gjesdal** | NFIF, teknisk kontakt | Datamodell, regelverk, flagging, API. Kjenner kravspekken best. |
| **Magnus Trosdahl** | Seksjonsleder NFIF | Kostnad, risiko, leveranseevne, hva NFIF må stille med. |
| **Roar Holen** | Laget FriSys / LiveRes, stevnesystemet arrangørene bruker | Hvordan vi tenker om integrasjon. Han er motparten i §13. |
| **Hilde Trageton** | `‹rolle ukjent — finn ut før møtet›` | |

### Roar Holen er det viktigste å planlegge for

Han har bygget systemet resultatene våre skal komme fra. Han kan være
samarbeidspartner, og han kan være konkurrent. Uansett er han den i rommet som
kjenner dataflyten best, og han vil høre nøye etter hvordan vi omtaler den.

**Gjør:** behandle LiveRes som en kilde vi gleder oss til å koble oss på.
Spørre ham direkte hva han mener er riktig måte å levere resultatlister på.

**Ikke gjør:** si at vi ikke kan prise integrasjoner «før motparten stiller
med dokumentert API». Det står i tilbudet, og det er riktig, men sagt høyt med
motparten til stede blir det en anklage. Si heller at vi vil bli enige om
formatet sammen.

`‹Finn ut hva Hilde Trageton har av rolle før møtet. Spør den som sendte
invitasjonen.›`

---

## Del for del

### Åpning · 30 sekunder

> Takk for invitasjonen. Jeg skal bruke mesteparten av tiden på å vise
> løsningen, for den finnes allerede og er lettere å se enn å beskrive.
> Så tar jeg migrering, opprydding og plan fram til nyttår.

Ikke bruk tid på høflighetsfraser. Alle vet hvorfor de sitter der.

### Hvem vi er · 1 minutt

Tre navn, tre kompetanser, én setning hver. Det som skal feste seg:

> Doktorgrad i anvendt økonometri og World Athletics-dommerkompetanse i samme
> person. To av oss konkurrerer selv internasjonalt og har egne resultater i
> basen.

Poenget er at §6 og §7 handler om regelverk, ikke om programmering. Hvilke
baner som tilfredsstiller TR14.1 mot TR43.1, når et blandet heat er tillatt,
hvordan WMA avviker fra WA — det er spørsmål som krever noen som har sittet i
jury.

### Utgangspunktet · 1 minutt

Ett tall stort på skjermen: **1 953 356**.

> Migrering av historiske data er normalt den dyreste og mest risikofylte
> posten i en slik anskaffelse. Hos oss er den gjennomført. Det er grunnen til
> at vi kan svare på fristen uten forbehold: vi skal ferdigstille, ikke bygge
> fra bunnen.

### Demo · 7 minutter

Se `DEMO.md`. Øv på den. Sju minutter går fort, og det er lett å bli sittende
for lenge på første side.

**Regel:** si hva du skal vise før du klikker, ikke etterpå.

### Migrering · 90 sekunder

Tre linjer: 2013–2026 er fulldybde, 2011–2012 er kildens oppstart, før 2011
finnes ikke sesongdata.

Så historien som sier noe om hvordan vi arbeider:

> Vi oppdaget at importen regnet et stevne som ferdig når det hadde mer enn ti
> resultater. Delvis importerte stevner ble aldri hentet på nytt. Det ble
> funnet fordi én utøver savnet ett innendørs høydehopp. Da vi kontrollerte
> alle sesonger mot kilden, manglet over en halv million resultater.
>
> Vi rettet det i importlogikken, ikke med et opprydningsskript, og kontrollen
> kjøres nå rutinemessig.

Dette er et sterkt punkt å ha med, men **ikke dvel ved det**. Poenget er
arbeidsmåten, ikke feilen.

### Opprydding · 2,5 minutter

Dette er et av de tre punktene de ba om, så gi det tid.

Vis tabellen med restansene. Si tallene rolig. Så:

> Basen er ikke ferdig kvalitetssikret, og det sier vi før dere spør. Arbeidet
> har vært prioritert mot innsamling først, fordi man ikke kan vaske data man
> ikke har.

Deretter metoden, som er det egentlige svaret: systemet finner feilene, og vi
sammenligner mot uavhengige kilder. SRU-eksempelet med 89 av 101 navn er
konkret og gjenkjennelig for alle i rommet.

Avslutt med formuleringen fra tilbudet:

> Vi lover ikke en feilfri base 1. januar. Vi lover at feilene er kjente,
> tellbare og synkende, og at det finnes verktøy for å rette dem.

### Veien til nyttår · 2 minutter

Gå gjennom tabellen raskt, men stopp på oktober:

> Den viktigste milepælen er ikke funksjonalitet, den er innsamling. Vi henter
> i dag resultatene fra den basen som skal erstattes. Egen innhenting må derfor
> være i drift før overgangen, ikke ved den. Vi har satt oktober, og kjører
> begge kilder parallelt ut året så vi ser at ingenting faller ut.

Det viser at vi har tenkt på overgangsrisikoen, som er den reelle risikoen i
prosjektet.

### Integrasjoner · 1 minutt

Her er Roar Holen i rommet. Se til ham når du sier dette.

> Vi merker oss at NFIF allerede arbeider med Buypass om iSonen mot OpenTrack
> og FriRes, og mot EQ Timing. Vi skal koble oss på det arbeidet, ikke
> definere det på nytt.
>
> Det vi trenger er en avtalt måte å få resultatlistene rett inn, med stevne,
> øvelse, klasse, utøver, klubb, resultat, vind og tidtakingsmetode. Vi stiller
> gjerne på et teknisk møte og blir enige om formatet.

Og så, hvis det er naturlig, still spørsmålet direkte:

> Roar, hva ville vært den enkleste veien ut av LiveRes for dere?

Å spørre ham i stedet for å snakke om ham er det som avgjør om han blir
alliert eller motstander.

### Etter nyttår og behov · 2 minutter

Fase 2 og 3 kort. Så hva vi trenger fra NFIF, som er en konkret liste og et
signal om at vi har planlagt, ikke bare lovet.

### Oppsummering · 30 sekunder

Tre punkter, og så stille. Ikke fyll pausen før spørsmålene kommer.

---

## Praktisk

- **Logg inn i admin før møtet.** Ikke skriv passord på delt skjerm.
- Ha to faner klare: forsiden og admin.
- Steng varsler og e-post.
- Om demoen henger: gå videre, ikke stå og vent. Skjermbildene i
  `reserve/` viser det samme.
- Del **fane**, ikke hele skjermen.
- Ha `TILBUD.pdf` åpen i tilfelle noen refererer til et kapittel.
