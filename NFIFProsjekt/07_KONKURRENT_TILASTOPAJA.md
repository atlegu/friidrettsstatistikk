# Konkurrentanalyse: Tilastopaja

**Versjon:** 1.0 — 09.08.2026
**Vurdering:** Mest sannsynlige hovedkonkurrent

> **Advarsel om kildegrunnlag:** Opplysningene nedenfor er hentet fra offentlig
> tilgjengelige nettsider (tilastopaja.info, friidrottsstatistik.se) i august 2026.
> **Ingen påstand om en konkurrent skal inn i tilbudsteksten før den er verifisert
> direkte.** En feilaktig påstand om en konkurrent er både uredelig og farlig — den
> kan koste oss kontrakten alene. Bruk observasjonene til å forme *vårt* tilbud, ikke
> til å angripe deres.

---

## 1. Hva Tilastopaja er

Finsk statistikkleverandør, European Athletics' statistikkleverandør, med en database
som oppgis å inneholde i størrelsesorden 1,3 millioner utøvere og 18 millioner
resultater internasjonalt. Samarbeider med OpenTrack om nasjonale rankinglister og
utøverbiografier. De er den mest kompetente statistikkaktøren i europeisk friidrett,
og det skal vi si rett ut — også i tilbudet.

## 2. Referansen deres: Sverige

`friidrottsstatistik.se` er den referansen NFIF sannsynligvis vil bli vist. Observasjoner:

| Observasjon | Hva det betyr for oss |
|---|---|
| Innholdet er sammenstilt av navngitte enkeltpersoner (Bo Nordin, Jonas Hedman) | Den svenske løsningen er i praksis **også** en ildsjelsdrevet statistikktjeneste, med en database bak. Det er nøyaktig modellen NFIF forlater i §1. |
| Deler av innholdet ligger bak medlemskap/abonnement | Se punkt 3 — dette er det viktigste funnet. |
| Omfang oppgitt til ca. 70 000 utøvere og ca. 1 million resultater | **Vi har 88 016 utøvere og 1 411 073 resultater for Norge**, et land med halve Sveriges befolkning. Vår norske dekning er dypere enn den svenske. |
| Struktur: årsbestelister, alle-tiders, rekorder, distrikter, veteraner, para | Solid statistikkprodukt. Det er her de er sterke, og vi skal ikke late som noe annet. |
| Ingen synlig aktivitets- eller deltakerstatistikk | §12 er udekket. |
| Ingen synlig åpen API eller eksportfunksjon | §18 og §22 er udekket. |
| Utenbaneløp kun som resultatlister for landeveisløp | §8 er i beste fall delvis dekket. |

## 3. Den strukturelle svakheten: betalingsmuren

Tilastopajas forretningsmodell er abonnementsbasert. Dypere historikk, utøverprofiler
og resultatarkiv ligger bak innlogging.

Det kolliderer med kravspekken på to punkter, og det er ikke en smaksak:

- **§4 Data Ownership:** «All data collected, imported, processed and displayed within
  the platform shall be owned by Norwegian Athletics» med «full access to export,
  analyse and reuse the data».
- **§2 Purpose:** plattformen skal gi «athletes, clubs, coaches, media and athletics
  enthusiasts» tilgang til offisiell statistikk.

En modell der forbundets egen statistikk selges tilbake til forbundets egne
medlemmer, er vanskelig å forene med begge deler. **Dette er trolig vårt sterkeste
enkeltargument mot Tilastopaja** — men det må fremføres som en beskrivelse av *vår*
modell, ikke som en anklage mot deres:

> «Athlete Mindset AS leverer plattformen som en tjeneste til NFIF. Alle data eies av
> NFIF, all statistikk er fritt tilgjengelig for utøvere, klubber, trenere, media og
> publikum, og NFIF kan når som helst eksportere, gjenbruke og videreformidle
> datagrunnlaget uten begrensninger fra vår side. Vi tar aldri betalt av forbundets
> medlemmer for tilgang til forbundets egne tall.»

Den siste setningen gjør jobben helt uten å nevne noen.

## 4. Der de er sterkere enn oss — og hva vi gjør med det

| Deres fortrinn | Vårt svar |
|---|---|
| Referanser fra flere nasjonale forbund | Vi har ingen. Vi må erstatte referanser med **demonstrasjon** — en løsning i drift med norske data, som NFIF kan ta på. |
| European Athletics-forankring, internasjonal ranking | Vi konkurrerer ikke på det. Vi kan hente internasjonale rankingdata inn, og bør si at vi samarbeider gjerne med internasjonale kilder fremfor å erstatte dem. |
| Organisatorisk soliditet og lang historikk | Vår motvekt: selskap, navngitt utvikler nr. 2, escrow, exit-klausul, standardteknologi. |
| Dyp internasjonal historikk | Vi har dypere *norsk* historikk, som er det NFIF faktisk kjøper. |

## 5. Der vi er strukturelt sterkere

Fire ting Tilastopaja ikke bare mangler, men vanskelig kan levere uten å endre
forretningsmodell:

1. **Utenbaneløp (§8).** Deres produkt er banestatistikk. Norsk mosjons-, terreng- og
   motbakkeløping med EQ Timing og Ultimate Sport Service som datakilder er et helt
   annet marked. §8 og §12 gjør dette til en stor del av anskaffelsen.
2. **Aktivitets- og deltakeranalyse (§12).** De leverer rangering av prestasjoner. NFIF
   ber om analyse av deltakelse, rekruttering og frafall. Det er en annen fagdisiplin.
3. **Åpent API og fri eksport (§18, §22).** Vanskelig å forene med abonnementsmodellen.
4. **Skreddersøm og responstid.** En leverandør som betjener et dusin forbund fra et
   felles produkt, kan ikke bygge norske særregler på bestilling. Vi kan.

## 6. Konsekvens for tilbudet

Vinnersetningen vår, som Tilastopaja strukturelt ikke kan skrive:

> **Vi selger ikke tilgang til en database. Vi drifter NFIFs egen plattform, og vi er
> forbundets analysemiljø.**

Det leder rett inn i `08_ANALYSE_OG_MEDIETJENESTE.md`, som er den delen av tilbudet
ingen konkurrent kan kopiere.

### Praktiske grep

- Verifiser påstandene i punkt 2 og 3 før noe av det brukes. Sjekk gjerne med noen som
  kjenner svensk friidrett.
- Omtal Tilastopaja med respekt gjennom hele tilbudet. Innkjøperen kjenner dem, og
  nedsnakking slår tilbake.
- Ikke konkurrer på internasjonal ranking. Tilby heller å integrere mot den.
- Legg vekt på det de ikke gjør: utenbaneløp, aktivitetsanalyse, åpen tilgang,
  skreddersøm og mesterskapsanalyser.
