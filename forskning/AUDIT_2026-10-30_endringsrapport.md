# Dataaudit A1, A3 og A6 — endringsrapport

30.10.2026. Full `paper-data-audit` (fase 0–8) på manus, supplement og svarbrev for A1 (stagnasjon-exit), A3 (debutalder) og A6 (vind).

> **Status 30.10.2026, kveld:** Atle godtok alle forslagene i avsnitt 3, og teksten i alle tre manus er skrevet om etter dem. Svarbrevene oppdateres ikke (Atles beskjed; punkt 22 bortfaller). Avsnitt 6 viser status nå. Konklusjonen rett under gjaldt før omskrivingen.

## Konklusjon (før omskrivingen)

**Ingen av de tre manusene er klare til innsending.** Ikke les PDF-ene som ligger i mappene nå: tabellene er generert på nytt med rettede data, men teksten er ikke oppdatert.

- **Sporingen holder.** Alle tabeller lages nå av kode. Uavhengige R-implementasjoner reproduserer utvalg og estimater rad for rad, også etter rettingene.
- **To datafeil endrer tall i A1 og A6.** Begge er rettet i koden og verifisert mot kilden og databasen.
- **Hovedfunnene står:**
  - A1: fremgang predikerer seniordeltakelse, nå OR 2,20 mot 2,02 før.
  - A6: vindeffekten er større for yngre og saktere utøvere, også med stevne-FE.
  - A3: sammenhengen mellom debutalder og senioraktivitet er ikke-lineær.
- **Det som faller, er deler av fortolkningslaget i alle tre**, blant annet «nedgangen før exit» (A1), v²-sammenligningen (A6) og at overlevelseskurvene samles ved 16 år (A3).

Du må avgjøre punktene i avsnitt 3 før jeg skriver om teksten. Anbefalingen min er å godta alle; tallene for hvert alternativ er beregnet og ligger i `tables/audit/` i hver artikkel.

---

## 1. Datafeil (rettet i koden)

**D1 — Sonehopp lagret to ganger (A6, A1).**
- **Omfang:** 47 962 lengde- og trestegrader har en identisk tvilling under sonekoden (samme utøver, dato, resultat og vind). Nesten alle gjelder 11–13-åringer, og de finnes i alle år 2011–2025.
- **Opphav:** Sonedataene kom inn i januar 2026, og brettkopiene ved reimportene 19.05.2026 og 24.08–06.09.2026. Ryddingen 03.10 sammenlignet bare innen samme øvelseskode og fant dem derfor ikke.
- **Verifisert:**
  - I databasen har alle 3 865 par fra 2016 en sonerad fra januar og en brettrad lagt inn senere.
  - Kilden viser hoppet bare under «Lengde (Sone 0,5m)»: 9 av 10 kontrollerte utøversider. Det tiende hoppet ble ikke funnet fordi det mangler vind.
- **Retting:** Brettkopien fjernes (`forskning/rens_felles.py`, speilet uavhengig i R).
- **A3 berøres ikke.** Av 449 seniorer som kan kontrolleres, mister ingen status.

**D2 — Redskaper som aldri fikk Tyrving-poeng (A1).**
- **Feilen:** `tyrving_r2.py` manglet koblingen for kule 5 kg, diskos 1,5 kg, slegge 5 kg og spyd 700 g (gutter 16), spyd 500 g (jenter 15–16) og liten ball (13–14), selv om parametertabellen har radene.
- **Følge:** Mannlige kastere hadde null poengsatte resultater ved 16 år, så «fremgang 13–14 → 15–16» var for dem i praksis 13–14 → 15.
- **Retting:** Den komplette koblingen ligger i `stagnasjon-exit/a1_tyrving.py`. IJSSC-modulen er ikke endret, fordi den er fryst.

**D3 — Eksakte dubletter (A6, A1).** Rader som er like på utøver, dato, øvelse, resultat, vind og runde: 771 i A6 og 746 i A1. De fleste skyldes stevner som er lagret som to stevneposter. Forsøk og finale med lik tid beholdes. Effekten er liten.

**D4 — 2011 er tynnere enn senere år (alle tre).** Stevner med resultater i juni, august og september var 164, 118 og 143 i 2011, mot 238, 197 og 201 i 2012. «Electronically complete from 2011» og «no left truncation» må mykes opp. Dette er en tekstendring; A3s H1 er uendret uten 2001-kullet.

## 2. Gammelt → nytt (etter D1–D3)

**A6**

| Størrelse | Før | Etter |
|---|---|---|
| Analyserte / identifiserende resultater / celler | 433 566 / 315 288 / 79 330 | 401 240 / 300 989 / 76 048 |
| Lengde, cm per m/s | 2,88 (2,67–3,10) | 3,15 (2,91–3,39) |
| Tresteg, cm per m/s | 4,10 | 4,16 |
| Lengde, medvind / motvind (p for likhet) | 2,88 / 2,88 (0,999) | 2,98 / 3,54 (0,23) |
| Lengde 12–13 år, gutter / jenter | 2,69 / 1,90 | 3,46 / 2,63 |
| Tresteg 12–13 år, gutter / jenter | 4,71 / 3,31 | 6,58 / 2,36 |
| Sprint (60/100/200 m) | 0,059 / 0,082 / 0,121 s | uendret |

**A1**

| Størrelse | Før | Etter |
|---|---|---|
| Primærutvalg (seniorer) | 3 808 (648) | 3 856 (652) |
| H1, OR per SD fremgang | 2,02 (1,73–2,37) | 2,20 (1,87–2,59) |
| ΔAUC M2 − M1 | 0,009 | 0,011 |
| Hovedgruppe sprint / hopp / mellomdistanse / kast | 34,1 / 33,4 / 18,9 / 13,6 % | 37,5 / 28,0 / 19,5 / 15,1 % |
| Median fremgang (seniorer / andre) | −10 (+30 / −18) | −4 (+36 / −14) |
| Exit-justert T−1 / T0 (figur 2) | −7,0 / −47,7 | −5,0 / −45,3 |
| Spesifikasjonskontroll 13→14 | 1,00 (0,88–1,13) | 1,02 (0,90–1,15) |
| E-verdi (papirets formel) | 2,84 (2,45) | 3,06 (2,64) |

**A3:** Datarettingene endrer ingen tall. Alle 112 tallkontroller passerer fortsatt.

## 3. Påstander som ikke holder: din beslutning

Hvert punkt er verifisert med min egen kode. Under «Forslag» står det jeg vil skrive.

### A6 (vind)

1. **v²-referansen er beregnet for feil størrelse.**
   - **Problemet:** (2v+1)/(2v−1) = 1,14–1,18 er forholdet ved nøyaktig ±1 m/s. Papiret estimerer gjennomsnittlige helninger over hele vindfordelingen.
   - **Hva fysikken faktisk gir:** Når ren drag-fysikk sendes gjennom papirets egen estimator på det faktiske designet, blir forholdet mellom motvind og medvind 1,84 (60 m), 1,72 (100 m) og 1,85 (200 m). Observert er 1,52, 1,66 og 2,36.
   - **Forslag:** «På 100 m er asymmetrien av den størrelsen drag-fysikken tilsier, på 60 m litt mindre, og bare på 200 m større (trolig fordi måleren bare dekker oppløpet).» Forklaringen om «selektiv atferd» fjernes. Endringen gjelder sammendrag, avsnitt 3.4, tabell 4 og diskusjonen.
2. **«Medvind verdt» er egentlig symmetriske helninger.** Medvindsgrenen er 0,047 / 0,065 / 0,078 s, 20–36 % lavere enn 0,059 / 0,082 / 0,121.
   - **Forslag:** Kall det «per m/s vind (lineær over med- og motvind)», og bruk medvindsgrenen der teksten sier medvind.
   - «Roughly double elite» blir «ca. 1,1–1,6 ganger».
   - «42–70 % more to a boy» gjelder bare den symmetriske helningen. På medvindssiden er guttenes 100 m 0,072 mot 0,065 (+11 %, overlappende KI), mens jentene har 0,083 mot 0,057.
3. **H5 «0,2–0,7 SD ved alle aldre» skyldes grove feil i SD-nevneren.** 37 rader på 100 m avviker mer enn 3 s fra utøverens sesongmedian, for eksempel 21,90 s for en 18-åring.
   - **Med robust skala:** Andelene blir 0,24–1,12. For menn på 100 m stiger andelen med alderen, fra 0,58 til 1,12.
   - **Forslag:** Robust skala, og verdsetting fra 0–2 m/s-segmentet: 0,113 / 0,139 / 0,194 s mot 0,095 / 0,129 / 0,155 s. «No youth excess» erstattes med at seniorene, om noe, får mest i forhold til egen variasjon.
4. **Lengdehoppets asymmetri «absent» skyldtes kopiene.** Etter rettingen er p = 0,23.
   - **Forslag:** «ikke signifikant asymmetrisk».
   - Forklaringen om valg av beste forsøk fjernes. Min simulering gir *demping* av hoppestimatet (2,4–2,9 cm mot sann verdi 3,0), ikke økning.
5. **Stevne-FE «bracketing … both lower bounds» er selvmotsigende, og kalibreringen er tilpasset, ikke testet.**
   - **Forslag:** Stevne-FE presenteres som designets kontroll. Aldersgradienten overlever: menn 100 m går fra 0,107 til 0,060 s.
   - Kalibreringen omtales som en illustrasjon som ikke kan skille målefeil fra konfundering.

### A1 (stagnasjon-exit)

6. **«Nedgangen før exit» skyldes færre resultater.** Snitt av tre beste stiger mekanisk med antall resultater, og antallet faller fra 10 til 8 til 3.
   - **Med like mange resultater:** Nest siste sesong ligger +5,0 (1,0–9,0) over eget nivå, og siste sesong −11,8 (−17,2 til −7,1). Sesongmedianen gir +9,8 og −14,0.
   - **Forslag:** Ny figur 2 med like mange resultater. «Penultimate-season decline», «a season before athletes left» og «the cleaner signal» fjernes. Endringen gjelder sammendrag, Key Points og konklusjon.
   - Tabell 1: Frafalternes median fremgang går fra −14 til +6 med like mange resultater, og andelen med negativ fremgang fra 57 til 46 %.
7. **Medieringen holder ikke.**
   - +0,08 SD per kvartal er ubetinget og for en stor del regresjon mot middelet. Betinget på nivå og kovariater er effekten +0,025 (−0,001 til 0,051).
   - Kvartal uten nivå og volum gir OR 0,97 (0,90–1,05). Det finnes altså ingen samlet effekt å mediere.
   - **Forslag:** «Støtten for en mediert vei er svak.» «Both implications held» og «what survives is the mediated form» fjernes.
8. **Nivågradienten (1,76 / 2,11 / 2,65) er en reliabilitetseffekt.** Med minst tre resultater i begge vinduer blir den 2,60 / 2,16 / 2,73, med interaksjon 1,01.
   - **Forslag:** «ingen tegn til moderasjon etter nivå». «Opposite gradient», «strengthened» og «rejects» fjernes.
9. **E-verdien er for høy.** Med anbefalt √OR-konvertering for vanlig utfall blir den 2,33 (2,08).
10. **Kjønn:** «likt hos kvinner og menn (2,20 mot 2,20, p = 0,99)», fra én modell.
11. **Nye følsomhetsanalyser, med beskrivelse i Methods** (H1 holder i alle):

    | Analyse | OR |
    |---|---|
    | Like mange resultater | 1,85 |
    | Splines for antall og volum | 2,12 |
    | Minst tre resultater i hvert vindu | 2,49 |
    | Bare utendørs | 1,96 |
    | Øvelsesjusterte poeng | 1,91 |

    Øvelsesjusterte poeng trengs fordi Tyrving-poengene ikke er sammenlignbare på tvers av øvelser: liten ball gir median 156–286 poeng, mot 700–900 i andre øvelser.
12. **Regresjon mot middelet** dokumenteres direkte: Tidligere nivå gitt senere nivå har OR 0,76 per 100 poeng (0,67–0,86). Kontrollen 13→14 nedtones.
13. **Avvik fra analyseplanen** skrives i et eget avsnitt:
    - klubbgrupperte CV-folder er ikke kjørt;
    - H3 bruker DeLong i stedet for parret bootstrap;
    - residualvarianten er ikke kjørt;
    - GEE er brukt i stedet for tilfeldig klubbintercept.

    «Robust to every pre-specified variation» fjernes.

### A3 (debutalder)

14. **«Kurvene samles ved 16», og «2,7 mot 1,3 % ved 20», er artefakter av Kaplan–Meier med forsinket inngang.** I 14–16-gruppen ganges tre førstesesongsfall sammen til én kurve.
    - **Direkte andeler ved 20 år** (kull 2001–2004): 4,2 / 3,3 / 4,5 %.
    - **Forslag:** Ny figur 3 med direkte andeler etter alder. Teksten endres i sammendraget, avsnitt 3.3, diskusjonen og Perspective.
15. **Den høyre armen av U-en forklares av avstand til utfallsalderen.** En debut ved 16 har fire år igjen til 20 år; en debut ved 10 har ti.
    - **Ved lik karrierelengde** (minst to konkurransedager i et år minst fire år etter debut) faller andelen fra 20,4 % (debut 10) til 4,5–6,6 % (debut 14–16), OR 0,70 per år (0,68–0,73). Resultatet er stabilt fem og seks år etter debut.
    - **Forslag:** Dette blir et medprimært utfall. «Neither claim was supported» og «no wrong age to start» skrives om slik at de navngir estimanden (andel aktiv ved fast alder). Debut ved 17–19 (OR 3,36) omtales som nær mekanisk.
16. **Cox-modellen på alderskala (HR 1,32)** bryter proporsjonalitetsantakelsen per konstruksjon, siden alder = debutalder + varighet.
    - **Forslag:** Modellen tas ut eller flyttes til supplement med forbehold. «Evidentially cleaner» erstattes med at hver klokke blander debutalder med den andre tidsskalaen.
17. **«The U is formal»** blir «ikke-lineær (LR-test)».
18. **Fødselskvartal-interaksjonen** kjøres på et selektert utvalg: 98,5 % av seniorene har fødselsdato, mot 52 % av de andre (39 % ved debut 10 og 94 % ved debut 16).
    - **Forslag:** Analysen tas ut, eller seleksjonen rapporteres.
19. **Dekningen i 2011:**
    - «No left truncation» mykes opp.
    - Analysen uten 2001-kullet legges til (trend 0,995).
    - «Debut ved 10 steg fra 32,6 til 43,9 %» får forbehold.
    - Små ordendringer: H3 «disappeared» blir «little», og «altered nothing material» står i dag ved siden av p = 0,03.

### Metode og rapportering (endrer ingen konklusjon)

20. **A6-standardfeil:** De absorberte cellene telles i småutvalgskorreksjonen, slik fixest gjør som standard. KI-ene blir 12–17 % bredere (60/100/200 m) og 34–37 % bredere (80/150 m).
21. **A6-tekst:**
    - «Month dummies equivalent to year × month» er feil og må rettes.
    - Listeomstokkingen bør måles som inn og ut av topp 10.
22. **Svarbrevene** oppdateres så de beskriver de nye analysene og tallene.

## 4. Utenfor de tre manusene (din beslutning)

- **Plattformen har de samme kopiene.** 47 962 kopier ligger i databasen og vises på friidrettsresultater.no. Opprydding betyr sletting, så den krever ditt ja, og den bør gjøres med reservetabell som ved ryddingen 03.10. I tillegg trengs en sperre i importen.
- **IJSSC (til vurdering)** bruker samme `tyrving_r2.py` med de samme manglende koblingene. Det gjelder poeng per alder 13–16, blant annet `tyrving_slope_13_16` og poeng ved 15 år.
  - IJSSC-dataene har blant annet 1 483 resultater i spyd 500 g, 1 073 i kule 5 kg, 808 i spyd 700 g, 702 i diskos 1,5 kg og 1 515 i liten ball, som modulen ikke gir poeng.
  - Sonekopiene rammer derimot ikke IJSSC: dataene bygger på uttrekket fra mai 2026, før kopiene kom inn.
  - Virkningen på de rapporterte tallene er ikke kvantifisert.
- **Andre analyser på databasen etter 19.05.2026** med lengde eller tresteg for 11–13-åringer kan ha kopiene: RAE-revisjonen, Lekene-trend, fagnytt og trenerartikkelen.

## 5. Det koden ikke kan verifisere

- En stikkprøve av sonetvillinger mot kilden: jeg kontrollerte 10 av dem.
- At innsamlingen for 2011 er komplett.
- De 37 grove avvikene på 100 m mot kilden (sannsynligvis 200 m-tider med feil øvelseskode).
- Din gjennomlesing av den endelige teksten.

## 6. Status for revisjonsfasene (oppdatert 30.10.2026, kveld)

| Fase | Status |
|---|---|
| 0–4: inventar, dataregler, uavhengig R, tallsporing | Ferdig. R reproduserer alle analysene, også de nye. |
| 5: `RUN_ALL.sh` | Grønn for alle tre, deterministisk. Tallkontroll: A1 143, A3 102, A6 193 ankrede sjekker (etter Lybbert & Zheng og H5-omskrivingen), 0 feil, 0 udekkede tall. A6 kjøres helt på nytt med `RUN_ALL.sh` når eliteenden (S8, egen økt) er ferdig. |
| 6: endringsrapport og omskriving | Du godtok alle forslagene; teksten er skrevet om. Svarbrevene oppdateres ikke. |
| 7: uavhengige agenter | Ferdig. |
| 8: frysing og siste smale gjennomgang | Fryst (`FREEZE.md` og hashfiler i hver mappe, kontrollert først i `RUN_ALL.sh`). Gjennomgangen er gjort; rettingene står i avsnitt 7, og avsnitt 8 lister det du må avgjøre. |

Alternativskriptene er nå en del av kjedene: `stagnasjon-exit/06b_revisjon_r2.py`, `debutalder/05b_revisjon_r2.py` og `vind/07b_revisjon_r2.py` (og 07). Utdataene ligger som `r2_*.csv` i `tables/modeller/` (A1, A3) og `tables/estimering/` (A6).

## 7. Siste smale gjennomgang (fase 8): funnet og rettet

Tre uavhengige agenter gikk gjennom definisjoner, tabell- og figurnoter og påstander. Jeg verifiserte hvert funn med egen kode før retting. Alle kodeendringer står i `FREEZE.md` i hver mappe.

**Datafeil (rettet i koden, speilet i R):**
- **Sonekopier fra flerdagsstevner (A1, A6).** Ryddeøkten i `scraper/` fant 8 846 brettkopier av sonehopp der brettraden har stevnets startdato og sonehoppet ligger 1–6 dager senere. Samme-dato-regelen fanget dem ikke. `rens_felles.py` fjerner dem nå: 5 780 i A1 og 8 907 i A6. En placebovariant med sonen før brettraden ga 1 og 6 treff, så regelen er presis.
- **Sonehopp under brettkoden i 2026 (A6).** Fra februar 2026 la importen sonehopp under brettkoden. Det er feil kode, ikke kopier. 1 597 brettkodede hopp ved 11–13 år i 2026 er tatt ut.

**Følger:**
- A6: Brettestimatene for lengde og tresteg ved 12–13 år forsvinner, fordi gruppene faller under minstekravet. De besto stort sett av feilkodede sonehopp, så 3,46/2,63 cm var artefakter. Sonehoppene for 10–13 år og alle sprinttall er uendret. Lengde går fra 3,15 til 3,16 cm, og utvalget fra 401 240 til 392 797.
- A1: Primærutvalget går fra 3 856 (652) til 3 877 (654), og H1 fra OR 2,20 til 2,24 (1,90–2,63).

**Gjennomføringsfeil:**
- **A6, listene.** 2025-listene tok med medvind over +2,0, «senior» var 20–34 år, og seniorkvinnene falt stille ut. Med lovlige merker og åpen seniorklasse gir still-luft-korreksjonen 1 ny på topp 10 for jenter 14, 1 for seniormenn, 2 for seniorkvinner og 0 for gutter 14 (før: 2/2/–/0). Andelen av topp 50 med medvind over +1 er 66 % for menn og 56 % for kvinner (før: 86 % for menn).
- **A6, ±0,2-kontrollen.** På grunn av flyttall tok den ut 1,8–2,1 og beholdt +2,2.
- **A1, «wind-legal».** Merker uten vindmåling ble regnet som lovlige. Med riktig regel (innendørs er lovlig, ute kreves registrert lovlig vind) blir OR 2,17.
- **A1, landmark-Cox og KM-figuren.** Frafallere som sluttet ved 15–16 år kom inn som hendelser ved t = 0,1. Nå er bare de 2 001 som konkurrerte etter fylte 16 med: progresjon HR 0,84 (0,79–0,90), kvinner HR 1,29.
- **A1, S1.** Flyten summerte ikke, fordi to eksklusjoner var talt over ulike kull. Begge telles nå blant kull 1998–2005: 578 uten skårbare poeng og 20 i små celler.

**Fra R-speilingen (A1):**
- «Like mange resultater» regnes nå eksakt. Trekkstøyen ga 24,2 mot 25,5 % i Python og R.
- Øvelsesjusteringen er identifisert innen hvert redskapssett, fordi guttekastene skifter redskap ved 16 år.

**Ny robusthetsanalyse (A1).** 58 % av frafallerne har siste sesong inne i 15–16-vinduet. Blant de 2 001 som konkurrerte etter fylte 16, er H1 OR 1,83 (1,55–2,17): mindre, men klar.

**Mediering (A1).** Den betingede a-stien er nå +0,026 (0,001–0,052), så KI utelukker null. «Weak» begrunnes nå med størrelse: den implisitte indirekte effekten er om lag OR 1,02 per kvartal, og høyst 1,06 med ujustert a-sti.

**Ordlyd rettet uten at konklusjoner endres:**
- Avvik fra planen og analyser lagt til etter estimeringen er opplyst (alle tre).
- Det som ble sagt å gjelde «hver»/«samme»/«equally», er presisert til det tallene viser.
- Feil faktasetninger er rettet, for eksempel «cancelled 2020 season», «Q1 overrepresented at every debut age» og «straight sprints».
- Drag-referansens kalibrering er beskrevet.
- Tresteg er unntaket i periodekontrollen (+14–24 %).

## 8. Det du måtte avgjøre (alt avgjort og skrevet inn 30.10.2026)

Punkt 2–3 ble skrevet inn etter ditt «Ja, skriv inn». Punkt 1, 4 og 5 ble skrevet inn etter «Gjør det andre» (commit 49cf90d for A3 og c299517 for A1). Punkt 6 er avgjort: Athlete Mindset er ikke relevant, og erklæringen står uendret.

1. **A3, debut-16-armen. SKREVET INN 30.10.2026.**
   - **Funnet:** Alle 107 debut-16-utøvere i kull 2004–05 debuterte i koronaårene og konverterte 10,3 %, mot 5,4 % for de andre debut-16-utøverne. Uten debuter i 2020–21 er OR 1,32 (0,79–2,19), og med koronaflagg 1,38 (0,86–2,19). Kohorthalvdelene er 1,35 mot 3,08.
   - **Det som står:** U-formens venstre arm (debut 10 mot 11–14; LR 30,5, p = 1,2e-5 uten koronadebuter) og 17–19-armen.
   - **Skrevet inn:**
     - Debut 16 er tatt ut av sammendraget.
     - Estimatet uten koronadebuter og med flagg står i Results og i tabell 4, analysen ligger i `05b_revisjon_r2.py` og er speilet i R.
     - Forskjøvet debut i koronaårene er nevnt som forklaring.
     - «Replication across cohort halves» gjelder nå U-en, med debut 16 som unntak, og «observed 6.6 %» har fått tillegget 5,4 % utenfor koronaårene.
2. **A6, H5 «størst for de yngste». SKREVET INN 30.10.2026 etter Atles ja.**
   - **Funnet:** For gutter er vinduet flatt i sekunder (100 m: 0,165 / 0,146 / 0,139 / 0,158 / 0,146 s). Som andel av løpstid er det ikke størst for de yngste. Bare jentene har et fall, og KI-ene overlapper.
   - **Skrevet inn:** Sammendraget, H5-avsnittet, Implications og Conclusion sier nå «omtrent likt i sekunder for gutter, større for jenter enn for seniorkvinner». Andel av løpstid er oppgitt: 1,10 mot 1,27 % for gutter, 0,95 mot 0,87 % for jenter. «Largest share of race time», «exactly where raw marks are most used to rank and select» og kalibreringssetningen er fjernet.
3. **A6, Tyrving-poengene. SKREVET INN 30.10.2026.** «Similar points … so the inequity is specific to raw-seconds comparisons» er fjernet. H5 sier nå at ungdomsmarginen i poeng har omtrent samme forhold som i sekunder.
4. **A1, tittel og hovedsetning. SKREVET INN 30.10.2026.** Tittelen er beholdt. Sammendragets konklusjon er nå «Low progression accompanies and precedes exit», og sammendraget tar med at sammenhengen holder blant dem som konkurrerte etter fylte 16 (OR 1,83).
5. **A1, switcher-analysen. SKREVET INN 30.10.2026 (den konsistente varianten).**
   - **Definisjon:** fremgang, nivå og antall måles i beste gruppe og standardiseres innen kjønn × beste gruppe i det inklusive utvalget, som primærmålene innen kjønn × hovedgruppe. Celler under 20 tas ut.
   - **Resultat:** OR 2,53 (2,13–3,01), n = 3 990. Planens variant gir 1,87 (1,64–2,12) og står ved siden av i tabell 4. Avviket er opplyst i Methods, og R-speilet passerer.
   - **Merk:** Gjennomgangens 2,24 standardiserte nivået innen kjønn × hovedgruppe. Varianten som standardiserer begge innen beste gruppe, ble definert før tallet ble sett.
6. **A1, interesseerklæringen. AVGJORT:** Athlete Mindset er ikke relevant, og setningen står uendret i alle tre manus.

**Formkrav: rettet 30.10.2026:**
- **Sammendrag:** A1 om lag 345 ord mot 350, med SMOs overskrifter Background, Results og Conclusions. A3 242 mot 250. A6 197 mot 200.
- **A6:** 6 nøkkelord og avsnittet «Sample size estimation and justification».
- **Figurfiler:** har nå trykkrekkefølgens nummer i A1 og A3. A1-figurene har ingen innebygd tittel.
- **A3:** S1–S4 er i egen fil (`supplement.tex`), med S2 og S3 nummerert etter første sitering.
- **A1:**
  - S1 er Additional file 1 i egen fil med forside.
  - SMOs erklæringsoverskrifter, forkortelsesliste og forkortelsesnoter er på plass.
  - KI-bruken er omtalt i Methods.

## 9. Gjenstår før innsending (din handling eller beslutning)

Filgjennomgangen (fase 7) fant også disse formkravene, men de kom ikke med i listen over. De krever et valg eller en handling fra deg.

- **A6, JSS er dobbeltanonym: RETTET 30.10.2026.**
  - **Tittelside:** `manus/title_page.tex` er en egen fil med forfatter, ORCID og kontaktinformasjon. Den har også Disclosure of interest, Funding, Author contributions, KI-bruk og Acknowledgements.
  - **Manus:** Forfatterblokken er erstattet med en anonymiseringsnotis, «the author's initiative» er blitt «by a post-plan decision», og «available from the author» er blitt «available on request».
  - **Sjekk:** RUN_ALL stopper hvis manus-PDF-en har forfatteropplysninger i teksten eller metadataene. Selvsitering i tredje person, «Guttormsen (2026)», er tillatt.
- **A6, medforfatter: Simen Guttormsen LAGT INN 30.10.2026** (Atles beslutning). Han har samme tilknytning, og Atle er fortsatt korresponderende forfatter.
  - **Må bekreftes av deg og Simen:** «SG collected the TFRRS profiles used in the external validation and revised the manuscript critically. Both authors approved the final version.» Setningen følger høydeartikkelen.
  - Simen må godkjenne endelig versjon før innsending. E-posten og ORCID-en hans (0009-0002-2533-8561) står på tittelsiden. Kontrollsifferet stemmer, og ORCID-registeret har navnet hans.
  - Simen står selv i registerutvalget: 75 av 392 797 rader, ungdomsresultater fra 2011–2020. Det er ikke skrevet inn i erklæringen. I høydeartikkelen ble det opplyst «for full transparency».
- **Upubliserte følgestudier i referanselistene (A1 og A3).**
  - SMO godtar bare publiserte arbeider, «in press» eller preprint. SJMSS (AMA) lister ikke innsendte manus.
  - Dette gjelder dropout-artikkelen («under review») og A1, som A3 siterer som «in preparation».
  - Valg: legg ut preprint (for eksempel SportRxiv) og siter med DOI, eller siter i teksten som «unpublished work under journal review».
- **Data availability og Sikt (alle tre): AVKLART 30.10.2026.**
  - Atle: samme datatilgang som de andre artiklene på disse dataene, og Sikt er godkjent som tidligere.
  - Etikk- og datatilgangssetningene følger nå dropout-artikkelen (IJSSC R1): ikke helseforskning etter helseforskningsloven §§ 2 og 4, Sikt har bekreftet at bruken ikke reiser personvernspørsmål, og samtykke var ikke nødvendig.
  - Analysedatasettet deles ikke (GDPR), og koden deponeres ved aksept. Det finnes ikke noe Sikt-nummer i de tidligere artiklene heller.
  - A6 har i tillegg fått en setning om Helsinki-erklæringen, som JSS krever.
- **A3, SJMSS Section Specialty Area** må stå på tittelsiden. Velg fra SJMSS-listen.
- **A1, STROBE-sjekklisten** må fylles ut og lastes opp. Teksten sier at den følger med.
- **A6, lengde:** JSS oppgir om lag 4 000 ord løpende tekst som veiledning (ikke absolutt grense). Med eliteenden (S8, commit 6bfc077) er A6 nå ~5 800.
- **A6, øvrige formkrav:**
  - figurfilene har feil nummer (fig3/fig4);
  - S-tabellene er nummerert mot siteringsrekkefølgen.
- **Tilastopaja-tillatelsen for S8: AVKLART.** Tillatelsen foreligger fra tidligere, og merknaden i manus er fjernet.
