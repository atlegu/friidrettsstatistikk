# A6 — Vindeffekten etter alder, kjønn og nivå: analyseplan

*Versjon 1, 29. oktober 2026. Committes FØR noen estimering (samme regime som A1/A3; ingen ekstern forhåndsregistrering). Arbeidstittel: «How much is the wind worth? Wind effects on sprint and horizontal-jump performance across age and ability in a national competition registry».*

---

## 1. Bakgrunn

Alt som finnes av empiriske vindestimater i friidrett — Linthorne-tradisjonens modeller og de resultatbaserte analysene av elitedata — bygger på gode seniorer. Hvordan effekten per m/s skalerer nedover i fart, alder og nivå er ukjent, og fysikken avgjør det ikke: en langsommere løper er eksponert for vinden lenger (flere sekunder på distansen), men bruker en mindre andel av kraften mot luftmotstand (drag ∝ fart²), og barn har større overflate per kilo. Nettoretningen for *absolutt* tidseffekt per m/s over alders- og nivåspennet er dermed et genuint empirisk spørsmål — og registeret er trolig alene i verden om å kunne svare: vind måles på utendørs 60 m for barn i Norge, og basen har ca. 458 000 vindmålte resultater der tyngden ligger ved 10–14 år, med over 31 000 utøver × sesong × øvelse-celler med minst tre elektronisk tidtatte løp (identifiserende variasjon).

Praktisk motivasjon: Tyrving-poeng, aldersrekorder, UM-krav og sesonglister behandler alle merker innenfor ±2,0 m/s likt. Hvis fordelen av medvind varierer systematisk med alder eller nivå, er værstøyen i ungdomsrangeringene ulikt fordelt — samme logikk som høydeartikkelens funn om kjønnsskjev høydekorreksjon. I tillegg gir estimatene vindkorreksjoner som A1/registerarbeidene og friidrettsresultater.no kan gjenbruke.

## 2. Spørsmål og prediksjoner (fastlagt på forhånd)

**H1 (retning/sanity).** Innen utøver × sesong × øvelse forbedrer medvind sprint- og lengde-/tresteg-resultater. (Entydig prediksjon; feil retning ville indikere datafeil.)

**H2 (kjernen — skalering med alder/fart).** Den *absolutte* effekten (sekunder per m/s; cm per m/s) endrer seg med alder. To navngitte, motsatte mekanismer: eksponeringstid (langsommere → lengre tid i vinden → større absolutt effekt hos de yngste) mot aerodynamisk andel (drag ∝ v² → mindre å spare hos de langsomme). To-sidig test; estimatene per aldersbånd er selve leveransen.

**H3 (relativ skala).** Den *relative* effekten (% per m/s) rapporteres parallelt; sammen avgjør H2+H3 hvilken skala som er stabil over utviklingsspennet — det er det en aldersuavhengig korreksjonsregel trenger å vite.

**H4 (asymmetri).** Motvind koster mer enn medvind gir, per m/s (retningsprediksjon fra litteraturen); testes med separate stigninger for vind < 0 og > 0.

**H5 (praktisk, estimering uten test).** Forventet fordel ved +2,0 m/s mot vindstille, per øvelse × kjønn × aldersbånd, i sekunder/cm og i andeler av within-celle-SD — tallgrunnlaget for å vurdere om ±2,0-regelen «koster» det samme i alle klasser.

**Tolkningsregler.** (i) Enkeltmåling med vindmåler (10/13 s-vindu) måler ikke vinden løperen faktisk møtte; målefeilen gir attenuering, så alle estimater leses som nedre grenser, trolig mest attenuert på små stevner. (ii) Vind er ikke tilfeldig tildelt; identifikasjonen er within utøver × sesong × øvelse med kontroll for sesongtidspunkt og runde, og trusselen «form og vær samvarierer over sesongen» adresseres med månedsdummyer og robusthet med stevnefaste effekter. (iii) Ingen kausal omtale utover «effekt av vind på registrert resultat» i denne design-forstanden.

## 3. Data

- **Frosset uttrekk per 29.10.2026**, alle årganger (alder 10–34 ved analyse), 2011→. Øvelser med vindmåling og substansielt volum: 60 m, 80 m, 100 m, 150 m, 200 m, lengde, lengde (sone), tresteg, tresteg (sone). Hekk utelates (vind registreres knapt i basen for hekkekodene).
- **Filtre i analysen:** status OK; utendørs (stevnets indoor-flagg ikke sant); elektronisk tid (`is_manual_time IS NOT TRUE`); kjent kjønn og fødselsår; alder 10–34; rimelighetsintervaller per øvelse (dokumenteres i koden); vind i [−8, +8] m/s. Resultater uten vindverdi beholdes bare i missingness-beskrivelsen.
- **Aldersbånd:** 10–11, 12–13, 14–15, 16–17, 18–19, 20–34.
- **Nivå:** utøverens gjennomsnittsresultat i cellen (utøver × år × øvelse), standardisert innen øvelse × kjønn × aldersbånd; tertiler.
- **Enheter:** tider i sekunder (performance_value/100); lengde/tresteg i meter (enhet verifiseres empirisk mot kjente størrelsesordener før bruk).

## 4. Modell

Primærspesifikasjon per øvelse (og per kjønn der det splittes):

resultat = FE(utøver × år) + β·vind + månedsdummyer + rundedummyer + ε,

estimert ved within-transformasjon (demeaning innen utøver × år × øvelse-celler), klyngerobuste SE på utøver (stevne-klynger som robusthet). β rapporteres som **gevinst per +1 m/s medvind** i sekunder (sprint) / cm (hopp) og i prosent (log-utfall).

- **H2/H3:** modellen estimeres separat per øvelse × aldersbånd (× kjønn); skaleringskurven β(alder) er hovedresultatet.
- **Nivå:** separat per nivåtertil innen øvelse × kjønn × aldersbånd.
- **H4:** β⁺ (vind > 0) og β⁻ (vind < 0) i samme celle; test β⁻ ≠ β⁺.
- **Form:** kvadratisk ledd som tillegg; lineær er primær innen [−5, +5].
- **Robusthet (forhåndsdefinert):** stevnefaste effekter i stedet for månedsdummyer; kun celler med ≥3 vindmålte løp; uten verdier der vind = 0,0 eksakt (heaping-sjekk); vindgyldighetsflagget ubrukt (alle vindverdier teller); 2011–2019 mot 2021–2026; ekskludere sonevariantene av hoppene; meet-level-kontroll.

## 5. Deskriptiv forhåndssjekk (før estimering, rapporteres)

Vindfordelingens heaping (andel eksakt 0,0; topper på hele tall), dekning per øvelse × år, celletellinger per øvelse × aldersbånd × kjønn, og andel av resultatene i vindøvelser som mangler vindverdi (med stevnestørrelse som deskriptiv dimensjon).

## 6. Leveranser, arbeidsflyt og etikk

Kode i `forskning/vind/`: `00_uttrekk.py` → `data_private/` (git-ignorert), `01_variabler.py`, `02_deskriptiv.py`, `03_estimering.py`, `04_figurer_tabeller.py`. Hovedfigur: β(alder) per øvelse med KI; asymmetrifigur; «+2,0 m/s-fordelen» som tabell per øvelse × kjønn × aldersbånd. Offentlige resultater; ingen individer identifiseres; prestasjonsdata ved 10–12 brukes her til å estimere *målebetingelser*, ikke til å rangere eller vurdere barn — ingen lister, persentiler eller individnivåfunn under 13 publiseres (barneidrettsbestemmelsenes formål respekteres; dette avsnittet står også i manuset). Samme hjemmelsgrunnlag som A1/A3. Manusets transparenssetning: plan committet før estimering, ikke eksternt registrert. Måltidsskrift: Journal of Sports Sciences, EJSS eller IJSPP. Naturlig medforfatter: Simen (Part I-profilen); avklares med Atle.

## 7. Hva studien ikke gjør

Ingen temperatur-/værkobling i v1 (MET-utvidelse er mulig oppfølging); ingen hekk; ingen korreksjonsformel «vedtas» — studien leverer estimatene og usikkerheten, og diskuterer regelimplikasjoner uten å foreskrive regelendring.
