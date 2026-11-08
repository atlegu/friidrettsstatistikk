# Manus til demonstrasjonen (ca. 10 minutter)

Logg inn på friidrettsresultater.no før møtet. Ha fanene åpne i denne rekkefølgen.

## Innledning (30 sekunder)

> «Vi viser hvordan dere og statistikkutvalget arbeider i løsningen. Hovedpoenget er arbeidsdelingen: vi leser inn og kvalitetssikrer, dere avgjør det forbundet skal avgjøre.»

## 1. Avvikslisten (3 minutter)

**Side:** `/admin/avvik`

- Vis kortene øverst: mulige rekorder, urimelige tider, uvanlige forbedringer, manglende vind, kjønn og fødselsår.
  > «Alle nye resultater kontrolleres hver natt. Det som ikke henger sammen, havner her.»
- Pek på en «mulig rekord» i listen. Vis knappene Riktig, Rettet og Underkjent, og kommentarfeltet.
  > «Dette er NFIFs og SRUs viktigste oppgave: å godkjenne eller underkjenne. Alt logges med hvem og når. I 2026 ble det 1–2 slike saker i uken.»
- Klikk på fanen **Rettet** og vis Elea Jørstad Bock.
  > «Her hadde kilden feil hekkehøyde: 76,2 cm i stedet for 84 cm. Kontrollen fanget det, og resultatet er flyttet til riktig øvelse.»

**Ikke** klikk på noen knapp i de åpne avvikene.

## 2. Innsendt resultatliste (2 minutter)

**Side:** stevnesiden for Skansemyren kastkarusell 13 (`/stevner/68033c42-0084-4975-8d0d-779812ce810d`)

> «Denne lista kom på e-post til resultater@friidrett.no 17. oktober, i NFIFs Excel-mal. Alle 48 resultatene og de 15 utøverne ble koblet automatisk, også navn som var skrevet litt annerledes enn i registeret. Rader som allerede ligger inne, hoppes over, så det blir ikke dubletter når stevnet senere kommer fra et stevneprogram.»

Vis gjerne importsiden `/admin/import` med opplastingsfeltet.
  > «Over 90 prosent av listene kommer i fire formater. Det er dem vi gjør ferdig i desember.»

## 3. Ikke godkjente resultater (1 minutt)

**Side:** Lars Gausemel Stølen (`/utover/6d307efc-1c7d-4bab-a805-fcf8c14cf2a3`), kortet «Ikke godkjente resultater»

> «Resultater som ikke er godkjent, for eksempel på grunn av feil i startutstyret eller fordi utøveren ikke er medlem av NFIF, registreres med årsak. De holdes utenfor lister og rekorder, men vises med årsak her og på stevnesiden. Det gjelder i dag om lag 7 900 resultater.»

## 4. Terminlisten (2 minutter)

**Side:** `/admin/terminliste`

- Vis tallene: avholdt, resultater inne, mangler og til purring.
  > «Terminlisten hentes hver natt og kontrolleres mot basen. Mangler et stevne resultater etter tre dager, havner det her. Etter en uke kommer arrangøren på purrelisten, med ferdig e-postutkast. Slik faller ingen stevner ut i det stille.»
- Vis knappene Purret, Avlyst og Ingen resultater.

## 5. Statistikk og uttrekk (2 minutter)

- **Årsliste:** `/statistikk/2026`, velg en øvelse. Vis knappen **Last ned CSV**.
  > «Bare administratorer kan laste ned lister, og hver nedlasting logges. Lister med navn og fødselsår er personopplysninger.»
- **Masters:** `/statistikk/masters`.
  > «Kontrollert mot de godkjente mastersrekordene, linje for linje.»
- **Klubbside med klubbstatistikk og klubbrekorder.**
- Har dere tid: **aktivitet** (`/aktivitet`) og **løp utenfor bane** (`/gatelop`).

## Avslutning (30 sekunder)

> «Dette er i drift i dag. Det som gjenstår før 1. januar, er mottaket av resultatlister i alle de fire formatene. API, kvalitetsnivå og rekordgodkjenning kommer i januar–februar.»

## Hvis de spør om …

- **Barn:** «Statistikk under 13 år er ikke offentlig, og innstrammingen pågår. Hvordan resultatlistene skal behandle barn, vil vi lage en policy for sammen med dere.»
- **Rapporter:** Vis aktivitetssiden og klubbstatistikken. Ikke lov nye rapporter. Si at de prises etter behov.
- **Roller for klubb og krets:** «Planlagt i 2027, sammen med Idrettens ID.»

## Ikke vis

- Brukersiden (`/admin/users`). Den viser andres e-postadresser.
- Gjennomgangssiden for en import. Knappen «Godkjenn og importer» er aktiv.
