# DATA_AUDIT — A1 «Stagnation before exit»

Audit startet 30.10.2026 etter `paper-data-audit`-skillen. Status 30.10.2026: fase 0–7 ferdig, teksten omskrevet (fase 6 nederst), fryst (`FREEZE.md`).

## Fase 0 — Inventar

Alle data leses fra `data_private/` (frosset uttrekk 29.10.2026, 19:59–20:01 UTC, produsert av `00_uttrekk.py` mot Supabase `lwkykthpnthfcldifixg`). Levende base per uttrekksdato; `created_at`-filtre brukes ikke (gjenskaper ikke historiske tilstander — se uttrekksinfo.json).

| Fil | sha256 |
|---|---|
| analysedata.csv | 9da7a7c4c275a812b3ebdd584486f3b22b6d69a5463a2a066d4e12b10f1d2efa |
| clubs.csv | 156e04f08c1e0aeb25017daf051a3b0b6b2276f70c4a1f9d620514ac7da9b188 |
| events.csv | 17ba16a6b64f2765727b61b45f4ceb190b5c79f78bc5268d2514991f30e9405e |
| meets.csv | 56dbb1bdf7c70f8023020c7fb27c458758898e7af1d06400e487af0f640e6b24 |
| resultater.csv | 154079444763c25ee58fbefe5e99abaf674347f933f276ec87a13f6c4a772737 |
| resultater_raa.csv | 545811ef8710ef9e854e68713d6cbf6d29a58f1ea472adac72363ae29e98b23a |
| utovere.csv | c5aebc91ce62d807ab545177ba582ec72a3d97905e043031378c613a31d3cb7f |
| flyt.json | d517b4240a9c1c1ad0897ead9c9c99f7840178fe819ec2683c0988f9779c6a3d |
| uttrekksinfo.json | dae9b79e3fc999165276e1ff87cc1994c76898854b1315cedb8bcf9b1ace16bd |

**Fullstendighet mot kilden (kontrollert mot levende base 30.10.2026):** utøvere født 1998–2006: 32 447 = basen (eksakt). Resultater per kull fra året utøveren fylte 13 t.o.m. 29.10.2026: alle ni kull eksakt like basen (1998: 50 795 … 2006: 42 898; sum 493 532). Ingen drift siden frysing. clubs.csv/meets.csv har samme hash som A3s (samme uttrekksmåte).

**Dekning:** registeret elektronisk komplett fra 2011; eldste kull (1998) fyller 13 i 2011, så ingen venstresensur ved konstruksjon. Kull 2006 ekskludert fra primærutvalget (høyresensur på seniorutfallet); 2026 observert t.o.m. 29.10.

## Fase 1 — Kode mot metodetekst

| Sjekkliste | Koden (01_variabler.py) | Teksten | Status |
|---|---|---|---|
| Operasjonsrekkefølge | status=OK → vinduer → landmark → kjønn → Tyrving → celler<20 → z på primærutvalget | §2 i samme rekkefølge | OK |
| Tidsorigo | W1=13–14, W2=15–16 (kalenderårsalder) | lik | OK |
| Venstresensur | kull 1998 = 2011 ved 13 | «complete from 2011» | OK |
| Høyresensur | senior=≥2 res. samme kalenderår ved 20+; kull 2006 ute av primær; fast vindu 20–21 per kohorthalvdel som robusthet | lik (R2-6-svaret) | OK |
| Identitet | alle merger på unike nøkler; analysedata 4 909 rader = 4 909 unike athlete_id | — | OK |
| Enheter/kategorier | Tyrving kun elektronisk, i modal hovedgruppe; mean-av-3-beste (ikke maks); k13/k15 = antall skårbare merker per vindu | lik | OK |
| Volum | konkurransedager (nunique date), alle OK-resultater inkl. manuelle | lik | OK |
| Ugyldige verdier | manuell tid ute av skåring; vindugyldig-variant delta_vind | lik | OK |
| Standardiseringsceller | kjønn×hovedgruppe, celler<20 ekskludert FØR z; z-parametre fra primærutvalget | lik | OK |
| COVID | covid_w1 (kull 2006–07), covid_w2 (2004–06), robusthet | lik | OK |
| Parsing | birth_date coerce; Int64-kvartal | — | OK |
| **Region** | modal krets ved 13–14 — men meets.krets er utfylt for 415 av 44 971 stevner i basen → region = NA for alle 4 909, fillna «ukjent» = konstant → null dummier, null numerisk effekt | §2 hevder justering for «region (modal competition district at 13–14)»; tabellnote «adjust for birth cohort, region, and club size» | **FUNN A1-1** |

NA-mønsteret i analysedata stemmer med flyten (43 uten fødselsdato; 734 uten skårbar Tyrving; z-varianter med småcelle-NA). `delta_nk_1314` (negativkontroll) har 1 604 NA — utøvere uten skårbare merker i begge enkeltår; modellen bruker komplette rader.

## Funn

1. **A1-1 (tekst mot kode, må rettes):** «region»-kovariaten er vakuøs — kildefeltet (meets.krets) er tomt for 99,1 % av stevnene, og klubbtabellen har ingen geografi (county: 0 av 2 484). Konstant kovariat → fjerning endrer ingen estimater (verifiseres bit-eksakt i fase 3). Retting: fjern «region» fra kovariatlistene i §2 og tabellnoten; geografi står allerede som umålt begrensning. Ingen tall endres.
2. **A1-2 (info):** `region`-kolonnen i analysedata beholdes som runde 1-spor; R-reimplementasjonen estimerer uten den og reproduserer publiserte tall eksakt.

## Fase 2–4 (30.10.2026) — retting, uavhengig implementasjon, tallsporing

- **A1-3 (tertilkonvensjon, dokumentert):** `pd.qcut` bruker `np.percentile` med q = 0,33333333333333326 (1 ULP under 1/3), mens R type 7 har fuzz. Grenseverdier havner derfor i ulik tertil. R-koden replikerer pandas-konvensjonen eksplisitt.
- **Dobbel avrunding (rettet):** Modellfilene lagret avrundede tall som tabellene avrundet på nytt. Nå lagres full presisjon og avrundes én gang ved visning.
- **Tabeller fra kode:** t1–t4 og s1 genereres av `07_manustabeller.py` og `\input`-es; ingen tall skrives for hånd.
- **Uavhengig R** (`audit/uavhengig.R`, data.table + survival, skrevet fra metodeteksten; Tyrving-poengene leses fra den delte, validerte komponenten via `audit/eksport_tyrving.py`) reproduserer utvalget rad for rad og alle OR-er. DeLong er verifisert med pROC (`audit/delong_bro.R`).
- **Tallsporing** (`audit/kontroll_tall.py`): tabellceller, ankrede fraser, svarbrevet, sitatene og ordtellingen.

## Fase 7 (30.10.2026) — uavhengige agenter, verifisert med egen kode og rettet

**D1 Sonehopp lagret to ganger (rettet).**
- **Omfang:** 12 990 brettrader (11 354 lengde, 1 636 tresteg) er kopier av sonehopp (samme utøver, dato, resultat, vind), nesten alle ved 13 år. Begge radene ble poengsatt (sonehopp mot brettnormen), så samme hopp kunne fylle to av de tre beste plassene i W1 og telle dobbelt i valget av hovedgruppe.
- **Opphav og verifisering:** som i A6 (reimportene 19.05 og 24.08–06.09.2026; kilden viser bare sonekoden).
- **Retting:** `forskning/rens_felles.py`, speilet uavhengig i R. R finner de samme 12 990.

**D2 Redskaper uten Tyrving-poeng (rettet).**
- **Feilen:** `tyrving_r2._SPEC` manglet kule 5 kg, diskos 1,5 kg, slegge 5 kg/120 cm og spyd 700 g (gutter 16), spyd 500 g (jenter 15–16), liten ball 150 g (13–14) og flere hekke-, hinder- og kappgangkoder, selv om parametertabellen har radene. Mannlige kastere hadde derfor null poengsatte resultater ved 16 år; 43,5 % av resultatene deres ved 15–16 var uten poeng.
- **Retting:** `a1_tyrving.py` kompletterer koblingen bare for A1 (IJSSC-modulen er fryst og uendret). Hver ny kobling er kontrollert mot tabellrader for kjønn og alder.

**D3 Eksakte dubletter (rettet).** 746 rader like på utøver, dato, øvelse, resultat, vind og runde; lavest id beholdes.

**Følger av D1–D3:**
- n går fra 3 808 til 3 856, og seniorene fra 648 til 652.
- H1 går fra OR 2,02 (1,73–2,37) til 2,20 (1,87–2,59), og ΔAUC fra 0,009 til 0,011.
- Hovedgrupper (sprint / hopp / mellomdistanse / kast) går fra 34,1 / 33,4 / 18,9 / 13,6 % til 37,5 / 28,0 / 19,5 / 15,1 %.
- Median fremgang går fra −10 (+30 / −18) til −4 (+36 / −14).
- Spesifikasjonskontrollen går fra 1,00 til 1,02.
- Uavhengig R reproduserer alt på nytt; `audit/sammenlign.py` leser nå utvalgstallene fra flyt.json og oppsummering.json i stedet for innskrevne konstanter.

**Statistikk (krever Atles beslutning om tekst; alternativene i `08_audit_alternativer.py` → `tables/audit/`):**
- **«Nedgangen før exit» (A1-1):** Den skyldes færre resultater (median 10, 10, 8 og 3 fra T−3 til T0). Med like mange resultater er nest siste sesong +5,0 (1,0–9,0) og siste sesong −11,8 (−17,2 til −7,1).
- **Mediering (A1-2):** Betinget a-sti er +0,025 (−0,001 til 0,051), og kvartal i M0 har OR 0,97 (0,90–1,05).
- **Nivågradienten (A1-3):** Med k ≥ 3 blir den 2,60 / 2,16 / 2,73, med interaksjon 1,01.
- **E-verdi (A1-4):** √OR gir 2,33 (2,08).
- **Kjønn i én modell (A1-6):** 2,20 mot 2,20, p = 0,99.
- **Tidligere nivå gitt senere nivå:** OR 0,76 per 100 poeng (0,67–0,86).
- **Følsomhet for H1:**

  | Analyse | OR |
  |---|---|
  | Like mange resultater | 1,85 |
  | Splines | 2,12 |
  | k ≥ 3 | 2,49 |
  | Bare utendørs | 1,96 |
  | Øvelsesjusterte poeng | 1,91 |

  Poengene er ikke sammenlignbare på tvers av øvelser; liten ball har median 156–286.
- **Avvik fra ANALYSEPLAN** (klubbgrupperte folder, parret bootstrap, residualvariant, tilfeldig klubbintercept) må beskrives.

**D4 Dekning 2011.** 1998-kullets 13-årssesong er 2011, året med tynnest dekning. «Electronically complete from 2011» må mykes opp. Kohortdummiene tar opp nivåforskjellen.

## Fase 6 (30.10.2026) — omskriving etter Atles beslutning

Atle godtok punkt 6–13 i `../AUDIT_2026-10-30_endringsrapport.md`. Svarbrevet oppdateres ikke (Atles beskjed); `manus/RESPONSE_PANEL1.md` er historisk.

- **Nye analyser** i `06b_revisjon_r2.py` (tidligere `08_audit_alternativer.py`) → `tables/modeller/r2_*.csv`: følsomhet for H1, mediering (betinget a-sti, kvartal i M0, nivå per kvartal), nivåtertiler med k ≥ 3, kjønn i én modell og tidligere nivå gitt senere nivå. E-verdien bruker √OR (`04_robusthet.py`).
- **Like mange resultater:** Tabell 1 (`01_variabler.py`, `delta_lik`) og figur 2 (`05_figurer_tabeller.py`) sammenligner sesongene ved like mange resultater.
- **Like mange resultater, eksakt (rettet under speilingen):** Først ble snittet av 30 tilfeldige trekk brukt. Trekkstøyen ga 24,2 mot 25,5 % negativ fremgang blant seniorene i Python og R, altså mer presisjon i teksten enn tallene har. Nå brukes forventet snitt av tre beste over alle utvalg på min(k) resultater, regnet eksakt; formelen er kontrollert mot full opptelling (største avvik 5e-13). Endrede tall: OR 1,85 → 1,86; exit T−2 / T−1 / T0 +8,0 / +5,0 / −11,8 → +8,2 / +5,0 / −12,3. Tabell 1 og sammendragets avrundede tall er uendret.
- **Øvelsesjusterte poeng (rettet under speilingen):** Guttenes kastredskaper skifter ved 16 år. Kast menn har derfor to sett av øvelser som aldri deler en utøversesong (4 og 9 koder), og forskyvningen mellom settene er ikke identifisert. Python (minste norm) og R (utelatt kolonne) normerte den ulikt: OR 1,912 mot 1,910. Nå beholder hvert sett snittpoengene sine, og begge gir 1,9123. Én setning er lagt til i Methods.
- **Uavhengig R** speiler alle nye analyser. `audit/sammenlign.py` sammenligner Δ ved like mange resultater per utøver (1e-6, ingen rader bare i én implementasjon), alle følsomhetsmodeller, medieringen, tertilene med median k15 og SD, kjønnsmodellen og exit-banene (prestasjon i fire varianter og volum). Alt passerer.
- **Tallsporing:** `audit/kontroll_tall.py` er skrevet om etter den nye teksten; 126 ankrede sjekker, 0 feil, 0 udekkede tall. Brevdelen er fjernet.
- **Ordtelling:** ~5 500 (skript), mot ~4 900 før omskrivingen.

## Fase 5 — RUN_ALL.sh

Det gamle `RUN_ALL.sh` kjørte uttrekket på nytt og er erstattet. Det nye (`set -eo pipefail`, hashkontroll mot FREEZE-filene, `SOURCE_DATE_EPOCH`) kjører 01–07 med 06b, full LaTeX-syklus med kontroll av udefinerte referanser og «??», eksport av Tyrving-poeng, uavhengig R, DeLong-broen, sammenligning og tallkontroll. Avledede filer (analysedata.csv, flyt.json) har nye hasher etter D1–D3; råuttrekket er uendret og fryst.

**Determinisme (30.10.2026):** Kjeden er grønn fra start til slutt. R-speilet kjører fixest med én tråd, og to R-kjøringer ga like hasher på alle utdata, identiske med RUN_ALL-kjøringen.

## Fase 8 (30.10.2026) — siste smale gjennomgang

En uavhengig agent gikk gjennom definisjoner, noter og påstander (`final_review_A1.md` i øktens kladdemappe). Hvert funn er verifisert med egen kode; kodeendringene står i `FREEZE.md`.

- **Rettet i koden:**
  - sonekopier fra flerdagsstevner (5 780, `rens_felles.py`);
  - «wind-legal» regnet merker uten vindmåling som lovlige (nå: innendørs lovlig, ute kreves registrert lovlig vind);
  - landmark-Cox og KM-figuren tok med frafallere som sluttet ved 15–16 år (nå bare de 2 001 som konkurrerte etter fylte 16);
  - S1 summerte ikke (begge eksklusjonene telles nå blant kull 1998–2005).
- **Ny analyse:** H1 blant dem som konkurrerte etter fylte 16 er OR 1,83 (1,55–2,17), fordi 58 % av frafallerne har siste sesong i eksponeringsvinduet. Den er lagt til etter estimeringen og merket slik.
- **Ordlyd rettet:** post hoc-analyser og avvik fra planen er opplyst, tolkningsregelen er presisert, kohortbeskrivelsen og exit-delutvalget presisert, «equally»/«same» er dempet, «equalised» er rettet og de praktiske påstandene uten dekning er tatt ut. Medieringen er begrunnet med størrelse (indirekte OR om lag 1,02, høyst 1,06), siden KI for den betingede a-stien nå utelukker null.
- **Status:** 143 ankrede sjekker, 0 feil, 0 udekkede tall; R-speilet passerer.
- **Atles beslutning:** tittel og hovedsetning («Stagnation precedes exit»), switcher-spesifikasjonen og interesseerklæringen. Se endringsrapportens avsnitt 8.
