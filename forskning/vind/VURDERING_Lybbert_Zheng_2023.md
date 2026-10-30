# Lybbert & Zheng (2023): vurdering og hva det betyr for A6

Lybbert, T. J. og Zheng, G. (2023). Feeling fast? Beliefs and performance among high school sprinters. *Journal of Quantitative Analysis in Sports* 19(3), 153–170. doi:10.1515/jqas-2022-0084 (metadata kontrollert mot CrossRef).

30.10.2026. Hele artikkelen er lest, også tabeller og figurer. Påstandene er testet på A6-dataene med A6s egen estimator.

## Konklusjon

**Tolkningen i del 1 holder ikke.** At motvind koster amerikanske high school-løpere mer enn en drag-modell for elitemenn tilsier, er i hovedsak fysikk, ikke psykologi. Drag-asymmetrien vokser når farten faller, og de sammenligner med en referanse ved elitefart. I våre data, der referansen er beregnet ved løpernes egen fart og gjennom samme estimator, er asymmetrien på 100 m akkurat så stor som drag tilsier for jenter og kvinner, og mindre for gutter og menn. Kjønnsforskjellen følger fartsforskjellen.

**Del 2 (Boling-effekten) er svak.** Den bygger på premisset fra del 1, og identifikasjonen har flere alvorlige problemer, se under.

**Artikkelen må likevel inn i A6.** Den er den eneste befolkningsstudien av vind hos løpere under elitenivå. A6s åpningssetning («Every empirical estimate … comes from elite seniors») var derfor ikke sann. Den er rettet, og A6 drøfter nå tolkningen deres med egne tall (tabell S7).

## Hva de gjør

**Data:** 100 m-resultater fra amerikanske high school-stevner 2018–2019 (athletic.net). Med elektronisk tid og vind er det 102 920 resultater for gutter og 90 510 for jenter. Snittid 12,60 s for gutter og 14,56 s for jenter.

**Del 1, vind og «mindset slack»:**
- **Modell:** stykkevis lineær modell i vind (medvindshelning + tillegg for motvind), med utøver-FE (over begge sesonger, ikke utøver × sesong), lineær dato og kontroller for heat og stevnestørrelse. Kontrollene omfatter også tidsavstanden til nestemann i mål.
- **Resultat (FE):** medvind −0,050 og −0,049 s per m/s (gutter/jenter); motvindstillegg −0,037 og −0,053.
  - Motvind/medvind-forhold: **1,74 for gutter og 2,08 for jenter**.
  - Kvadratisk: 6 m/s motvind gjør gutter 3,2 % og jenter 3,8 % tregere.
- **Referanse:** Mureikas kvasi-fysiske modell for elitemenn (figur 4, venstre), og et drag-plott der høyre panel bruker high school-fart og justert luftmotstandsareal.
- **Tolkning:** Motvindstapet utover elitereferansen er psykologi («slack»), sterkest hos jenter.

**Del 2, Boling-effekten:**
- **Oppsett:** Matthew Bolings 9,98 (+4,2 m/s) 27. april 2019 gikk viralt. Forskjell-i-forskjell 2019 mot 2018, bare California, etterperiode etter stevnet.
- **Metode:** Entropibalansering, «sharpened» q-verdier, og forskjeller etter predikert rase via navn og skole (BIFSG) og lagets rasesammensetning.
- **Funn:** Blandede fortegn. Begge kjønn løp 0,183 s **tregere** i medvindsløp etter Boling, og det tolkes som overmot («feeling fast»). Raskere tider finnes bare i enkelte undergrupper.

## Innvendinger mot del 1

1. **Referansen er beregnet ved feil fart.**
   - Ved samme vind w gir drag (∝ (v−w)²) asymmetrien omtrent (2v+w)/(2v−w), og den vokser når farten v faller.
   - Over den observerte 100 m-vindfordelingen i registeret gir ren drag-fysikk gjennom A6-estimatoren forholdet **1,43 ved elitens 10,0 s, 1,57 ved deres gutters 12,60 s og 1,69 ved deres jenters 14,56 s**.
   - I utvalg med blandet fart blir det mer, fordi de tregeste har størst forhold: 1,67 for våre gutter og menn (snitt 12,08 s) og 1,73 for våre jenter og kvinner (13,53 s).
   - **Følge:** Elitereferansen undervurderer den fysiske asymmetrien hos tregere løpere systematisk, mest hos jenter. Det er nøyaktig mønsteret de tolker som psykologi.
2. **Knekken i figur 4 (høyre) er bygd inn i modellen.**
   - Ren drag gir en tidsendring som er lineær i luftmotstanden, og dermed kvadratisk i vind.
   - En modell som er stykkevis lineær i vind med knekk i 0, gir en knekk i drag-planet uansett. Knekken er altså ingen test.
3. **Estimatoren og referansen er ikke den samme størrelsen.**
   - Helninger midlet over en vindfordeling er ikke det samme som modellens respons ved én vind.
   - A6-auditen viste at forholdet (2v+1)/(2v−1) ved ±1 m/s (1,14–1,18) er langt under det ren drag gir gjennom estimatoren (1,72 for 100 m).
   - Vindfordelingen deres er ikke rapportert, så referansen kan ikke beregnes riktig for deres data.
4. **Vær og stevne er ikke kontrollert.**
   - Motvind kommer ofte med kaldt og vått vær, og de har bare utøver-FE og lineær dato.
   - I A6 faller motvindshelningen mer enn medvindshelningen når sammenligningen gjøres innen stevne.
   - Innen stevne er forholdet om noe lavere: 1,59 for kvinner og 1,46 for menn, mot drag 1,70 og 1,63.
5. **Svakere design enn nødvendig.** Utøver-FE over to sesonger med lineær dato tar ikke formutviklingen gjennom sesongen. Tidsavstanden til nestemann i mål er dessuten en «dårlig kontroll»: den er selv påvirket av vind og prestasjon.
6. **Tolkning ved eliminasjon.** De måler verken tro eller oppfatning. Psykologien er det som blir igjen når fysikken er trukket fra. Da står og faller konklusjonen på at fysikkreferansen er riktig, og det er den ikke (punkt 1–3).

## Våre tester (A6-dataene)

Alle med A6-estimatoren (FE utøver × sesong, måned og runde, stevneklynger). Drag-referansen er beregnet ved hver utøversesongs egen fart. Tallene står i tabell S7 og `tables/estimering/r2_asym_100m.csv` og `r2_drag_fart.csv`, og R-speilet gir de samme tallene.

| 100 m | Motvind/medvind (95 % KI) | Drag ved egen fart |
|---|---|---|
| Jenter og kvinner, alle aldre | 1,77 (1,58–1,96) | 1,73 |
| Gutter og menn, alle aldre | 1,54 (1,36–1,71) | 1,67 |
| Jenter og kvinner, stevne-FE | 1,59 (1,35–1,83) | 1,70 |
| Gutter og menn, stevne-FE | 1,46 (1,18–1,74) | 1,63 |

- I 9 av 10 kjønns- og aldersgrupper ligger drag-forholdet innenfor intervallet. Unntaket (menn 20–34 år) er *mindre* asymmetrisk enn drag tilsier.
- Jentene har større asymmetri enn guttene, slik Lybbert & Zheng fant. Det er det fysikken gir for tregere løpere, og det er ikke noe overskudd utover drag.
- Deres guttetall (1,74) er omtrent drag-forholdet for et blandet utvalg med samme fart.
- Deres jentetall (2,08) ligger over våre jenters 1,73. Men deres jenter er tregere (14,56 mot 13,53 s), og vindfordeling og stevneforhold er ukjent. Resten kan være fysikk og vær.

**«Feeling fast»-testen (kladdeanalyse, ikke i manus).** Hvis løpere slakker av i sterk medvind, skulle gevinsten over +2 m/s flate ut mer enn drag tilsier.
- **100 m:** helningen over +2 er 0,75 av helningen 0–2, mot 0,71 fra drag, altså som fysikken.
- **60 m og 200 m:** utflatingen er sterkere (0,44 og 0,42 mot 0,60 og 0,66). Det forklares bedre av måling: på 200 m måler vindmåleren bare oppløpet, og målte verdier over +2 er ofte kast, der målefeil demper helningen mest. Testen gir ingen ren støtte til overmot.

## Innvendinger mot del 2

1. **Hviler på del 1.** «Slack» er premisset for at et selvtillitsløft skal kunne endre tidene.
2. **Balansering på utfallet.** Entropivektene matcher snittid, spredning og årsbeste også for etterperioden. Det er tall som inneholder utfallet selv.
3. **Det er uklart om vindstyrken er kontrollert i forskjell-i-forskjell-analysen.**
   - Ligning (2) nevner bare tidsavstand, dato, heat og stevnestørrelse og elektronisk tid. Tabellnotene sier «other control variables from Table 2», som kan omfatte vind.
   - Er vindstyrken ikke med, slår en forskjell i vindstyrke eller vær mellom etterperiodene 2018 og 2019 rett ut som «Boling-effekt» når de deler i medvinds- og motvindsløp. Været er uansett ikke kontrollert.
   - At gutter og jenter får nøyaktig samme effekt i medvindsløp (+0,183 s), peker mot felles stevneforhold, ikke psykologi.
4. **Sammensetning.** Etterperioden er sluttspill der bare de raskeste kvalifiserer seg, og sammensetningen kan skille seg mellom år.
5. **Mange tester og etterpåforklaringer.** Mange undergrupper (kjønn × vind × tertil × rase) gir blandede fortegn. Tregere tider forklares som overmot og raskere som selvtillit, slik at nesten ethvert mønster kan tolkes.
6. **Rase predikert fra navn og skole.** Gir støy, og forfatterne nevner selv de etiske sidene.

## Det som er nyttig for A6

- Det er den eneste befolkningsstudien av vind hos løpere under elitenivå. Nyhetspåstanden i A6 er rettet til «Almost every empirical estimate …», og innledningen nevner studien og at den ikke ser på skalering med alder eller nivå.
- Kjønnsforskjellen i asymmetri finnes også hos oss. Forklaringen (fart) gir et godt diskusjonspunkt og tabell S7.
- Medvindshelningen deres (0,050 s per m/s) er lavere enn vår (0,065 på 100 m). Det kan skyldes design (utøver-FE uten sesong, dårlig kontroll, ulik måling). Ikke tatt inn i manus.
- Vindmåleren måler 10 s fra start. For tregere løpere dekker den dermed en mindre del av løpet (14–15 s på 100 m for de yngste). Det er verdt å huske ved tolkning av aldersgradienten. Ikke tatt inn i manus.

## Endret i A6 (logget i FREEZE.md; RUN_ALL grønn, R-speilet passerer)

- **Ny analyse:**
  - `07b_revisjon_r2.py`: asymmetri for 100 m per kjønn og aldersbånd mot drag ved egen fart, med og uten stevne-FE, og drag ved fast fart.
  - Ny tabell S7 (`09_r1_supptex.py`), speilet i `audit/uavhengig.R` og sammenlignet i `audit/sammenlign.py`.
- **Tekst:**
  - Åpningssetningen i sammendraget.
  - Lybbert & Zheng i innledningen.
  - Avviket i Methods (lagt til etter planen).
  - Nytt avsnitt i H4-resultatene.
  - Nytt diskusjonsavsnitt: «A headwind penalty is not a psychological effect».
  - Referansen er lagt til.
- **Tallkontroll:** 160 ankrede sjekker, 0 udekkede tall. Ordtelling ~4 900.

## Til din vurdering

- Tonen i diskusjonsavsnittet. Overskriften er bastant, og en mildere variant er for eksempel «Asymmetry, speed and the psychological interpretation».
- Om «feeling fast»-testen (utflating over +2) skal inn som en setning eller tabell. Den støtter fysikktolkningen på 100 m, men er uklar på 60 og 200 m.
- A6-beslutningene fra auditen (H5-påstandene og poengsetningen) står fortsatt åpne, se endringsrapportens avsnitt 8.
