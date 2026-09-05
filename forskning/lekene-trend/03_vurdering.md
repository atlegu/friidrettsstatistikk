# Utviklingen i 13–14-årslekene 2012–2025: en samlet vurdering

*Arbeidsnotat, 2026-09-05. Grunnlag for artikkel til trenerforeningens tidsskrift. Tallene er hentet fra `tables/` (produsert av `02_deskriptiv.py` og `03_trender.py`); vedleggstabellen med alle 56 seriene ligger i `tables/vedlegg_trender.md`.*

## Grunnlag og metode i korte trekk

Datasettet omfatter alle 14 utgavene av lekene (NCC-lekene 2012, PEAB-lekene 2013–2014, Bendit-lekene 2015, Ungdomslekene 2016, Lerøy-lekene 2017–2025): 30 078 resultater fra 5 705 utøvere, ett beste resultat per utøver, øvelse og år. Manuelle tider er utelatt. Kappgang er holdt utenfor. Antall øvelser per utøver er ikke brukt som indikator, siden det styres av kretsenes deltakerregler, som både varierer med kretsstørrelse og er endret i perioden.

Trenden i hver øvelse og klasse (56 serier) er estimert med kvantilregresjon av logaritmen til resultatet på kalenderår, for medianen («bredden») og for beste desil («toppen»). Stigningen er uttrykt som prosent bedre per tiår, med fortegnet snudd for løp slik at positivt alltid betyr raskere, lengre eller høyere. I tillegg er nivået tidlig (2012–2014) og sent (2023–2025) sammenlignet i sekunder og meter, og utviklingstakten fra 13 til 14 år er målt hos utøvere som deltok i samme øvelse to år på rad (gjentakere). For kast, lengde og høyde er trenden dessuten kontrollert mot hele landet: sesongbeste for alle norske 13- og 14-åringer i samme øvelser, uavhengig av lekene.

Alt dette er beskrivende trender uten justering for eksakt alder, arena og vind. Den justeringen kommer i neste fase (modell C i planen). Hovedmønsteret er så tydelig at det neppe endres av justeringen, men enkeltstørrelser kan flytte seg.

## 1. Totalbildet

**Det har ikke vært noen generell fremgang i 13–14-årsklassene siden 2012.** Av 56 serier har 46 negativ mediantrend. Seksten er signifikant negative, ingen er signifikant positive. Gjennomsnittet over alle serier er −3,3 % per tiår, men medianen over seriene er bare −1,5 %: totalbildet trekkes ned av kastene, som faller mye, mens de fleste andre øvelser ligger nær null.

**Toppen holder seg bedre enn bredden.** For beste desil er 32 av 56 serier negative, 13 signifikant negative (ni av dem kast) og fem signifikant positive. De fem positive er alle løp for gutter: 60 m (G13 og G14), 200 m (G14), 600 m (G14) og 1500 m (G13). I sprint og mellomdistanse er toppen i snitt 0,8 og 1,2 % bedre per tiår, samtidig som bredden er uendret eller svakt svakere. Mønsteret «toppen holder, bredden sklir» er det samme som i trenerartikkelen for eldre klasser, men utslagene er små utenom kast.

**Kjønn.** Jentene har en svakere utvikling i bredden enn guttene: 26 av 28 jenteserier er negative mot 20 av 28 gutteserier, og de eneste signifikante tilbakegangene i sprint og 600 m er hos jenter (J14 60 m og 200 m, J13 600 m). I toppen har guttene fem signifikant positive serier, jentene ingen. Det er ingen systematisk forskjell mellom 13- og 14-årsklassen.

**Utviklingstakten fra 13 til 14 år er uendret.** Samme utøver forbedrer seg i median med 4–7 % i løp og 5–9 % i hopp hos gutter, og med 2–3 % i løp og 1–3 % i hopp hos jenter, og disse tallene er like i 2013–2016 som i 2023–2025. Ingen øvelse har signifikant trend i gjentakerforbedringen. Det er et viktig funn for tolkningen: det som skjer med utøverne *mellom* 13 og 14 år, altså det trenerne i denne aldersgruppen rår over, ser ikke ut til å ha endret seg. Nivåforskjellene oppstår før 13 år, eller i hvem som kommer inn i friidretten.

**Covid.** Deltakelsen falt fra 594–664 utøvere (2012–2019) til 452 i 2020, og ligger etterpå på 523–573. Nivået i 2021–2022 skiller seg ikke fra årene rundt, og forbedringen fra 2020 til 2021 hos gjentakerne ligger innenfor det normale spennet i alle øvelser. Det er ikke noe varig covid-spor i resultatene.

**Sammensetning.** Gjennomsnittlig eksakt alder innen klassene er stabil gjennom hele perioden (0,23–0,27 år over klassealderen), og andelen født i første kvartal ligger på 28–35 % alle år. Den relative alderseffekten er altså til stede, men konstant, og kan ikke forklare trendene.

## 2. Øvelsesgruppene

### Sprint (60 m, 200 m)
Bredden er stabil for guttene (innenfor ±0,3 % per tiår i alle fire serier) og svakt tilbake for jentene: J14 taper 2,0 % per tiår på 60 m og 2,7 % på 200 m (begge p < 0,01), J13 1,2 % på 200 m (p < 0,05). I sekunder: J14-medianen har gått fra 8,78 til 9,02 på 60 m og fra 28,97 til 29,83 på 200 m (snitt 2012–2014 mot 2023–2025). Toppen er svakt bedre for guttene (1,5–1,6 % per tiår på 60 m i begge klasser og på 200 m for G14, alle p < 0,05; G14-toppen på 60 m fra 7,85 til 7,74) og uendret for jentene.

### Hekk (60 m, 80 m, 200 m)
Ingen av de åtte seriene har signifikant trend, verken i bredden eller toppen; alle ligger innenfor ±2,5 % per tiår. Jentenes 60 m hekk har gått noe tilbake i median (J13 fra 11,24 til 11,57, J14 fra 10,68 til 10,91), men feltene er på rundt 30 per år, og usikkerheten er stor. Hekk er den øvelsesgruppen som har endret seg minst.

### Mellomdistanse (600 m, 1500 m)
Bredden er flat for guttene og svakt tilbake for J13 på 600 m (−1,9 % per tiår, p < 0,05; fra 112,9 til 115,6 sekunder). Toppen er blitt litt bedre: G14 600 m +2,1 % (p < 0,01; beste desil fra 94,0 til 92,3 sekunder), G13 1500 m +2,1 % (p < 0,05), og beste desil på 1500 m er 5–9 sekunder raskere i tre av fire klasser. Mellomdistanse er dermed den gruppen der toppen har utviklet seg klarest positivt.

### Horisontale hopp (lengde, tresteg)
Alle åtte serier er negative i bredden, tre signifikant: lengde J13 −4,3 % og J14 −2,7 % per tiår (p < 0,05), tresteg G14 −5,6 % (p < 0,01). I meter: lengde J13 fra 4,14 til 3,98, tresteg G14 fra 10,16 til 9,40. Samme svake tilbakegang i lengde finnes nasjonalt (−1,3 til −3,5 % per tiår), så dette er ikke særegent for lekene. Toppen spriker: G14 i lengde er blitt bedre (+3,3 % per tiår, p = 0,06; beste desil fra 5,32 til 5,54), mens toppen i tresteg for gutter har gått tilbake (−4,6 og −5,5 %, p < 0,05).

### Vertikale hopp (høyde, stav)
Høyde er flat i median i tre av fire klasser; G13 har gått tilbake med 4,2 % per tiår (fra 1,39 til 1,31 m, p < 0,01), og toppen er svakere for G13 og J14 (−3,9 og −4,1 %, p < 0,05). Nasjonalt er høyde uendret i alle klasser, og høydemedianene er grovt kvantisert (1,31, 1,36, 1,41 …), så G13-signalet bør tolkes med varsomhet inntil den justerte analysen er gjort. Stav har flat median og beste fjerdedel i alle klasser, en topp som er blitt bedre for jenter (J14 +8,2 % per tiår, p = 0,07; beste desil fra 2,41 til 2,64 m), og en gjentakerforbedring som stiger for jenter fra 7,8 % i 2013–2016 til 11,9 % i 2023–2025. Stav er den eneste øvelsen med en tydelig positiv utvikling for jenter.

### Kast (kule, spyd, diskos, slegge)
Kastene er artikkelens viktigste funn. Alle 16 serier er negative i bredden, åtte signifikant; i toppen er ni signifikant negative. Utslagene er store:

- **Spyd** faller 14–17 % per tiår i alle fire klasser (alle p < 0,001). I meter: G13-medianen fra 30,2 til 24,6, G14 fra 31,1 til 26,8, J13 fra 21,3 til 18,4, J14 fra 26,1 til 20,8. Toppen faller like mye (12–15 %; beste desil G13 fra 38,7 til 32,9).
- **Kule** faller 5–8 % per tiår i median (G13 fra 8,85 til 8,17, J13 fra 8,63 til 8,08, J14 fra 8,03 til 7,56), og toppen for G14 hele 16,6 % (beste desil fra 11,59 til 9,83).
- **Diskos** faller 5–11 % i median og 8–14 % i toppen; sterkest for G13 (fra 22,6 til 20,3 m).
- **Slegge** faller for guttene (G13 −14 %, G14 −10 %; fra 22,3 og 23,7 m til 20,5 m i begge klasser), men er flat for jentene, og jentenes topp har gått *opp* (beste desil J13 fra 28,6 til 33,5 m, J14 fra 28,6 til 32,7). Jenteslegge er unntaket i kastgruppen, trolig båret av noen få klubbmiljøer.

**Nedgangen i kast er nasjonal, ikke et lekene-fenomen.** Sesongbeste for alle norske 13–14-åringer viser samme retning og nesten samme størrelse: spyd −7 til −12 % per tiår, kule −5 til −6 %, diskos −3 til −7 % (alle klasser med nok data, de fleste p < 0,01). Andelen av utøverne på lekene som stiller i kast er dessuten stabil gjennom hele perioden (kule 20–33 % av G13 alle år, spyd 17–29 %), og den svake halen i fordelingene er ikke kuttet i tidlige år. Redskapene er de samme innen hver klasse hele perioden. Det som gjenstår av forklaringer, er reelle: mindre kasttrening og færre kasttrenere i klubbene, en generell svekkelse av kastferdighet hos barn før 13 år, og at friidretten rekrutterer færre av de store og sterke ungdommene. Dataene kan ikke skille mellom disse, og artikkelen bør presentere funnet som empiri og drøfte årsakene med forbehold.

## 3. Er det generelle trender for øvelser og øvelsesgrupper?

Ja, og de sorterer seg etter hva øvelsen krever:

1. **Løp og hekk (alle distanser, begge kjønn): stabilt nivå.** Utslagene er tideler over 14 år, og toppen for gutter er svakt bedre. Løpsøvelsene ser ut til å være det friidretten i denne aldersgruppen har vedlikeholdt best.
2. **Hopp: svak tilbakegang i bredden**, 0,1–0,2 m i lengde og tresteg over perioden, med sprikende topp. Stav skiller seg ut positivt for jenter.
3. **Kast: markert tilbakegang i både bredde og topp**, 10–20 % i spyd, 5–10 % i kule og diskos, og det samme i hele landet. Unntaket er jenteslegge.

Oppsummert: jo mer en øvelse hviler på kraft og teknikk med redskap, desto større er tilbakegangen; jo mer den hviler på løpskapasitet, desto mer stabil er den. Guttenes topp i løp har blitt bedre, jentenes bredde i sprint svakt dårligere. Og utviklingstakten mellom 13 og 14 år er den samme som før i alle øvelser, noe som peker på at endringene har røtter før inngangen til 13-årsklassen.

## 4. Forbehold som må med i artikkelen

- Kretsreglene for antall øvelser per utøver varierer med kretsstørrelse og er endret. De påvirker hvem som stiller i hvilken øvelse. Stabil deltakerandel per øvelse og den nasjonale kontrollen gjør at dette neppe forklarer kastfunnet, men det kan påvirke enkeltserier.
- Vind og arena er ikke justert for; det gjelder sprint, hekk og horisontale hopp. Arenaene har flyttet i alle tre regioner. Modell C tar høyde for dette.
- Små felt gir vide konfidensintervaller i stav, slegge og diskos (8–35 per klasse og år). Enkeltår skal ikke tolkes.
- Høydemedianene er grovt kvantisert; små forskyvninger kan gi store prosentutslag.
- Den nasjonale kontrollen bygger på databasens dekning, som er svakere i 2012 og etter 2019; retningen er likevel entydig for kast.

## 5. Forslag til budskap i artikkelen

1. Nivået i løp og hekk blant 13–14-åringer er stabilt over 14 år, og toppen i sprint og mellomdistanse for gutter er litt bedre.
2. Hopp viser en svak tilbakegang i bredden.
3. Kastene har hatt et markert fall i både bredde og topp, og fallet er like stort i hele landet. Dette bør være artikkelens hovedfunn og hovedanliggende for trenere.
4. Utøverne utvikler seg like mye fra 13 til 14 år som før. Aldersgruppens trenbarhet er intakt; det er inngangsnivået og rekrutteringen som har endret seg.
5. Jentenes bredde i sprint går svakt tilbake, mens stav er en positiv jentehistorie.
