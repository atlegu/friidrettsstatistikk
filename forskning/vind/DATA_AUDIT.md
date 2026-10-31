# DATA_AUDIT — A6 «How much is the wind worth?»

Audit startet 30.10.2026 etter `paper-data-audit`-skillen. Status 30.10.2026: fase 0–7 ferdig, teksten omskrevet (fase 6 nederst), fryst (`FREEZE.md`).

## Fase 0 — Inventar

Alle data leses fra `data_private/` (frosset uttrekk 29.10.2026, 21:06–21:15 UTC, `00_uttrekk.py` + `00b_uttrekk_hekk.py` mot Supabase `lwkykthpnthfcldifixg`; per øvelse × år pga. statement-timeout).

| Fil | sha256 |
|---|---|
| analyseklar.csv | 36d29e3c1a24f54861e2b5cbd5493387786e2302800ede7b6edfa453f924f34b |
| events.csv | 17ba16a6b64f2765727b61b45f4ceb190b5c79f78bc5268d2514991f30e9405e |
| meets.csv | 6e15efd063f05ad6f1ad2a8b0e576673bfaf05e82de61af8b0775a2ae011e9b6 |
| missing.csv | d7aaa430407f686ea616ab6165c2a6db37c7dca3c89dc462d2c0350b16d6b602 |
| resultater.csv | 77f7cdf54a6d169e8319990dffd5dc0b95d58189363d960ef1b3c938b29ae989 |
| resultater_hekk.csv | 8770aba1ee51374de4cf3e5eab7ee78c7fa336c2ed8d4348e5ca916f39a775ce |
| utovere.csv | 079a5109d518eb7b5be7ca850ea8734a1d8b88e12f1e4c44401b461c7641d9e4 |
| flyt.json | 3592f91f21b0b3e32f6c8190e54f7d57e37ac24f3a893ec52bd5def07f873f6b |
| uttrekksinfo.json | 9067890e586edb5d9ef44ae756268e0bec561a5733b81b5f225419f5b12bf2a4 |
| uttrekksinfo_hekk.json | c220cd5d78e0da3315560f5e36ec9c631aebbcc14394c7d0a78e74d57983ea4b |

**Fullstendighet mot kilden (kontrollert mot levende base 30.10.2026):** alle ni hovedkoder eksakt like basen per kode (sum 670 803); hekkuttrekket 45 464 eksakt. Ingen drift siden frysing.

**Flyt-aritmetikk:** 670 803 − 1 755 (ikke OK) − 189 801 (innendørs) − 14 418 (manuell) − 2 429 (uten kjønn) − 16 (uten fødselsår) − 9 744 (alder utenfor 10–34) − 18 692 (uten vind) − 21 (|vind|>8) − 361 (urimelig) = 433 566 — eksakt. Estimeringsgrunnlag 315 288 i celler ≥2 (79 330 celler).

**Dekning per år:** 2011 lavere (34 386; første elektroniske år), 2020–21 lave (33 202 / 30 028; pandemi — 2020 holdt utenfor periodesplitten, forklart i §2), 2026 delår (24 641 t.o.m. 29.10; utendørssesongen fullført). Enhetstolkning per øvelse dokumentert i flyt.json (hundredeler→s; mm→m) og verifisert mot kjente størrelser.

## Fase 1 — Kode mot metodetekst

Kjernen ble gjennomgått i revisjonsrunden (stevneklynging, medvindsgren-H5, vindjusterte tertiler, bunching, manglende vind). Tilleggskontroller i auditen:

| Sjekkliste | Koden | Teksten | Status |
|---|---|---|---|
| Identitet | ingen merger som kan duplisere (utovere/meets/events unike); radtall mot basen eksakt | — | OK |
| Døde kolonner | analyseklar.krets 97 % NA, level konstant «local» — ingen av dem brukes i estimering (estimer bruker celle/maaned/runde/meet_id) | ikke omtalt | OK |
| Innendørs per øvelse | r1_innendors_per_ovelse teller brutto innendørsrader (190 690); flytens 189 801 er sekvensielt (etter ikke-OK) — manus siterer bruttotallene som «largest exclusions», ikke flytsummen | konsistent slik skrevet | OK (dokumentert) |
| **Manglende vind, andel** | ute-basen (OK + utendørs) = 479 247 rader, 23 435 uten vind = **4,89 %**; flytens 18 692 er ved eksklusjonspunktet (basis 452 640 → 4,13 %) | manus §2.1 skriver «18 692 outdoor rows without a wind value (**4.3 % of outdoor rows**)» — 4,31 % er 18 692/433 566, feil nevner | **FUNN A6-1** |
| Størrelsestertiler | 9,1 %/4,0 %/1,5 % på ute-basen (479 247) | «9.1 % … smallest third … 1.5 % … largest» | OK (samme basis som 4,89 %) |

## Funn

1. **A6-1 (tekst, må rettes):** «(4.3 % of outdoor rows)» har feil nevner (analysefilen). Riktig med samme basis som tertilsetningen: **4,9 % av godkjente utendørsrader** (23 435 av 479 247); flytens 18 692 er antallet ved eksklusjonspunktet. Rettes i §2.1.

## Fase 2–4 (30.10.2026) — retting, uavhengig implementasjon, tallsporing

- **A6-2 (rettet):** nivåtertilene var radbaserte (like mange resultater per tertil, lavtertilen fikk om lag 50 % flere celler, og en grensecelle kunne deles). Nå tertiler av utøversesonger med celle-id som deterministisk tie-break (`07_revisjon_r1.py`).
- **A6-3 (rettet):** flatreferansen for hekk ble tatt fra samlet modalbånd (20–34 for guttene i 100 m hekk 84 cm, som alle er 14–15); nå kjønnets eget modalbånd.
- **Dobbel avrunding (rettet):** estimatfilene lagret avrundede tall som tabellene avrundet på nytt; nå lagres full presisjon og avrundes én gang ved visning.
- **Tabeller fra kode:** t1–t6 og s1–s5 genereres av `09_r1_supptex.py` og `\input`-es; ingen tall skrives for hånd.
- **Uavhengig R** (`audit/uavhengig.R`, data.table + fixest, skrevet fra metodeteksten) reproduserer utvalget som eksakt multisett og alle estimater; `audit/sammenlign.py` passerer.
- **Tallsporing** (`audit/kontroll_tall.py`): hver tabellcelle, ankrede fraser i sammendrag, tekst og supplement, alle tall i svarbrevet, sitatene i brevet og ordtellingen.

## Fase 7 (30.10.2026) — uavhengige agenter, verifisert med egen kode og rettet

Agentenes rapporter: data, statistikk og filer. Hvert funn under er kontrollert med egne skript før retting.

**D1 Sonehopp lagret to ganger (rettet i koden).**
- **Omfang:** 42 691 lengde- og 5 271 trestegrader har en identisk OK-tvilling under sonekoden (utøver, dato, resultat, vind), 92 % i samme stevne. Nesten alle er ved 11–13 år, i alle år 2011–2025.
- **Opphav:** I databasen har alle 3 865 par fra 2016 en sonerad fra januar 2026 og en brettrad fra 19.05.2026 eller 28.–31.08.2026 (reimportene). Kildens utøversider viser hoppet bare under «Lengde (Sone 0,5m)» (9 av 10 kontrollerte; det tiende mangler vind).
- **Retting:** `forskning/rens_felles.py` fjerner brettkopien (47 962 rader). Regelen er speilet uavhengig i R, som finner de samme 47 962.
- **Følger:**
  - Lengde går fra 2,88 til 3,15 cm per m/s (2,91–3,39), tresteg fra 4,10 til 4,16.
  - Lengdehoppets asymmetri går fra p = 0,999 til 0,226 (medvind 2,98 / motvind 3,54).
  - 12–13 år i lengde: gutter fra 2,69 til 3,46, jenter fra 1,90 til 2,63.
  - Utvalget går fra 433 566 / 315 288 / 79 330 til 401 240 / 300 989 / 76 048.
  - Sprint er uendret.

**D3 Eksakte dubletter (rettet).**
- **Omfang:** 771 rader like på utøver, dato, øvelse, resultat, vind og runde, de fleste fra stevner lagret som to stevneposter; lavest id beholdes. Hekkuttrekket har 190.
- **Følge:** Sprintestimatene er uendret på rapportert presisjon.

**Grove feil i 100 m (ikke rettet i data; robust skala foreslått).** 37 rader avviker mer enn 3 s fra cellens median, for eksempel 21,90 s for en 18-åring. Dette er trolig 200 m-tider med feil kode. Rimelighetsgrensene gjelder hele øvelsen. Helningene påvirkes ikke merkbart, men den klassiske SD-nevneren i H5 blåses opp (menn 100 m 18–19 år: 0,346 mot robust 0,126).

**Statistikk (krever Atles beslutning om tekst; alternativene i `11_audit_alternativer.py` → `tables/audit/`):**
- **v²-referansen (A6-1):** (2v+1)/(2v−1) er forholdet ved ±1 m/s, ikke for estimatoren. Drag-sannhet gjennom estimatoren gir 1,84 / 1,72 / 1,85 (60 / 100 / 200 m), mot observert 1,52 / 1,66 / 2,36.
- **«Medvind verdt» er symmetriske helninger (A6-2):** Medvindsgrenen 0,047 / 0,065 / 0,078 s er 20–36 % lavere.
- **H5 (A6-4/5):** Robust skala gir 0,24–1,12. For menn på 100 m stiger andelen fra 0,58 til 1,12 med alderen. 0–2-segmentet gir 0,113 / 0,139 / 0,194 s.
- **Valg av beste forsøk (A6-6):** Egen simulering gir demping (2,4–2,9 cm mot sann 3,0), ikke økning.
- **«Bracketing … both lower bounds» og EIV-kalibreringen (A6-3):** Påstanden er logisk uholdbar, og kalibreringen er tilpasset, ikke testet. Aldersgradienten overlever stevne-FE.
- **Standardfeil (A6-7):** Med de absorberte cellene talt i småutvalgskorreksjonen (fixest-standard) blir SE 12–17 % større (60/100/200 m) og 34–37 % større (80/150 m).
- **Toveis demeaning (A6-8, rettet):** stoppet etter 25 runder uten å konvergere. Nå itereres det til toleranse 1e-10 med rask numpy-implementasjon. Estimatene er like på fem siffer; absorberte kolonner fjernes med relativ grense.
- **Tekst:** «Month dummies equivalent to year × month» er usant.

**D4 Dekning 2011.** Stevner med resultater i juni, august og september var 164, 118 og 143 i 2011, mot 238, 197 og 201 i 2012. «Electronically complete from 2011» må mykes opp.

## Fase 6 (30.10.2026) — omskriving etter Atles beslutning

Atle godtok punkt 1–5, 20 og 21 i `../AUDIT_2026-10-30_endringsrapport.md`. Svarbrevet oppdateres ikke (Atles beskjed); `manus/RESPONSE_PANEL1.md` er historisk.

- **Asymmetri:** drag-referansen sendes gjennom estimatoren (`drag_referanse` i `07_revisjon_r1.py`); tabell 4 og figur 3 viser den. Forklaringen om selektiv atferd er fjernet.
- **Medvind:** medvindsgrenen brukes der teksten sier medvind; de lineære helningene kalles «per m/s of wind».
- **H5:** verdsatt fra 0–2 m/s-segmentet med robust skala (1,4826 · MAD · √(n/frihetsgrader)).
- **Stevne-FE etter alder** i `07b_revisjon_r2.py` (tidligere `11_audit_alternativer.py`); kalibreringen omtales som illustrasjon.
- **Standardfeil:** de absorberte cellene telles i småutvalgskorreksjonen (fixest-standard `fixef.K = "nested"`), i `03_estimering.py`. Toveis demeaning itererer til 1e-10.
- **Lister:** omstokkingen måles som inn og ut av topp 10; teksten om månedsdummyer er rettet.
- **Uavhengig R** speiler alt (fixef.K nested, drag, 0–2-segmentet, MAD, stevne-FE etter alder). `audit/sammenlign.py` passerer; KI for stevne-FE sammenlignes med toleranse 1e-3 fordi regressortellingen skiller seg i én celle (200 m menn 10–11).
- **Tallsporing:** `audit/kontroll_tall.py` er skrevet om etter den nye teksten; 133 ankrede sjekker, 0 feil, 0 udekkede tall. Brevdelen er fjernet.
- **Ordtelling:** ~4 200 (skript).

## Fase 5 — RUN_ALL.sh

`RUN_ALL.sh` (`set -eo pipefail`, hashkontroll mot FREEZE-filene, `SOURCE_DATE_EPOCH`) kjører 01, 02, 03, 05, 07, 07b, 10, 08 og 09, full LaTeX-syklus med kontroll av udefinerte referanser og «??», deretter uavhengig R, sammenligning og tallkontroll. 04 og 06 er erstattet av 08/09 og kjøres ikke. Avledede filer (analyseklar.csv, flyt.json, missing.csv) har nye hasher etter D1/D3; råuttrekket er uendret og fryst.

**Determinisme (30.10.2026):** To kjøringer ga like hasher på alle Python-utdata (tabeller, figurer, PDF, avledede data). Bare R-filen `stevne_fe_alder.csv` skilte seg, med 1e-13 i KI-ene. Fixest kjører nå med én tråd, men toveis FE (utøversesong + stevne) ga fortsatt maskinpresisjonsstøy (1,8e-16) mellom R-prosesser med samme radrekkefølge. Den filen avrundes derfor til 10 gjeldende siffer før skriving. Nå er alle R-utdata like mellom kjøringer.

## Fase 8 (30.10.2026) — siste smale gjennomgang

En uavhengig agent gikk gjennom definisjoner, noter og påstander (`final_review_A6.md` i øktens kladdemappe). Hvert funn er verifisert med egen kode; kodeendringene står i `FREEZE.md`.

- **Rettet i koden:**
  - sonekopier fra flerdagsstevner (8 907, `rens_felles.py`);
  - sonehopp under brettkoden i 2026 (1 597 rader ved 11–13 år tatt ut);
  - 2025-listene (nå bare lovlige merker, åpen seniorklasse og seniorkvinner med);
  - ±0,2-kontrollen (flyttall);
  - aksen i figur 5.
- **Følge:** Brettestimatene ved 12–13 år forsvinner; de var artefakter av feilkodede sonehopp. Lengde går fra 3,15 til 3,16 cm, og sprint er uendret.
- **Ordlyd rettet:**
  - dragsamsvaret gjelder 100 m;
  - kalibreringen av drag-referansen er beskrevet;
  - avvik fra planen er opplyst;
  - tresteg er unntaket i periodekontrollen;
  - eksponeringstid-ordbruken er dempet;
  - hekkesammenligningen er presisert;
  - den usanne «senior tables are steeper» er fjernet.
- **Status:** 140 ankrede sjekker, 0 feil, 0 udekkede tall; R-speilet passerer.
- **Atles beslutning:** H5-påstandene om at vinduet er størst for de yngste, og poengsetningen i Implications. Se endringsrapportens avsnitt 8.

## Lybbert & Zheng (2023), Atles beskjed 30.10.2026

Vurderingen står i `VURDERING_Lybbert_Zheng_2023.md`. De tolker at motvind koster amerikanske high school-løpere mer enn en drag-modell for elitemenn tilsier, som psykologi. Drag-asymmetrien vokser når farten faller, og de bruker referanse ved elitefart.

- **Ny analyse (lagt til etter planen):** motvind/medvind på 100 m per kjønn og aldersbånd mot drag ved egen fart gjennom A6-estimatoren, med og uten stevne-FE (`07b_revisjon_r2.py` → `r2_asym_100m.csv`, `r2_drag_fart.csv`; tabell S7). R-speilet gir de samme tallene (`audit/r_out/lz_*.csv`).
- **Resultat:**
  - Jenter og kvinner 1,77 (1,58–1,96) mot drag 1,73; gutter og menn 1,54 (1,36–1,71) mot 1,67.
  - Drag ligger innenfor intervallet i 9 av 10 kjønns- og aldersgrupper, og unntaket ligger under.
  - Innen stevne er forholdet 1,59 og 1,46.
  - Drag ved fast fart: 1,43 (10,0 s), 1,57 (12,60 s), 1,69 (14,56 s).
- **Tekst:** Nyhetspåstanden er rettet, studien er nevnt i innledningen, avviket står i Methods, kjønnsforskjellen i H4 og et eget diskusjonsavsnitt er lagt til. Tallkontroll: 160 ankrede sjekker, 0 udekkede tall.

## Eliteenden — eksterne utvalg til tabell S8 (30.10.2026, Atles beslutning «Inn i A6»)

Piloten i `2026Host/Idrettsanlyser/Vind/02_pilot_eliteenden.md` viste at 100 m-eliten ligger på Moinats nivåformel, ikke på per-sekund-loven i tabell S4. Atle valgte å ta eliteenden inn i A6 som ekstern validering. Piloten brukte Simens råskrap av TFRRS; A6 bruker fellesbyggingen `Covid/tfrrs_shared` v1.2 (PAPERS.md-regelen; A6 er registrert der). Skript: `11_eliteende.py` → `tables/estimering/r3_eliteende*.csv`, `data_private/eliteende_analyseklar.csv` og `eliteende_flyt.json`; tabell S8 fra `09_r1_supptex.py`.

**Kilder og hashkontroll** (`eliteende_input.sha256`, sjekkes av `RUN_ALL.sh` og av skriptet før noe leses):

| Kilde | Fil | sha256 |
|---|---|---|
| TFRRS | `Covid/tfrrs_shared/v1.2/output/results_clean.csv` | `d8070e63…9ed89` (= VERSION.md, v1.2) |
| Tilastopaja | `2026Host/Idrettsanlyser/Alder/data/processed/season_results.csv` (Alder-prosjektets uttrekk av finalistenes sesongsider, hentet 19.10.2026) | `d7babded…8b1` |

**Regler TFRRS, mot fellesbyggingens sjekkliste:**
- Sesong fra byggingen (`season`, ikke `season_tfrrs`) = outdoor; øvelsene 100, 200, 100H, 110H, LJ, TJ; utøver = `athlete_id`.
- Utelatt: `is_xc`, `is_multi_sub` (mangekampdeløvelser), `valid = FALSE` / `mark_numeric` NA, `hand`, sprintmerker uten hundredeler (`\d{1,2}\.\d{2}`, A6s elektronisk-regel), `flag_error`, `wind_missing`, |vind| > 8, utenfor rimelighetsgrensene (100 m 9,5–14,5 s; 200 m 19–30; 100 mH 11–20; 110 mH 12–20; lengde 3–9 m; tresteg 8–18,5), ukjent kjønn, eksakte dubletter på (utøver, øvelse, dato, stevne, runde, merke, vind). `result_id` er en stevne-id i byggingen (deles av runder og av mangekampens deløvelser) og brukes ikke som nøkkel.
- Beholdt med vilje: `flag_wind` (vindhjulpne merker er studieobjektet) og alle collegiate sesonger (ingen `is_di`-avgrensning; studien handler ikke om Division I).
- År = kalenderår for stevnedatoen (første dag for flerdagsstevner); celle = utøver × år × øvelse; runde F/P/ukjent.
- Flyt: 647 440 utendørsrader i de seks øvelsene → 593 809 uten mangekamp → 567 286 med merke → 566 728 elektroniske → 566 252 uten feilflagg → 549 332 med vind → 549 168 innen ±8 → 548 361 rimelige → 546 885 med kjønn → 546 854 uten eksakte dubletter; 36 540 utøvere, 2008–2026.
- Innsamlingshullet (README, «Known limitation»: korte karrierer med inngang 2015–17) påvirker sammensetningen, ikke within-sesong-helninger; robusthet uten sesongene 2016–2017: 100/200 m innen 3 % (`r3_eliteende_robusthet.csv`). Opplyst i S8-noten.

**Regler Tilastopaja:** øvelsene som over; dedup på (utøver, øvelse, dato, raw, cid); `indoor = 0`; plass D/H (mangekamp) ut; `hand = 0` og `annulled = 0`; numerisk verdi og vind, |vind| ≤ 8; rimelighetsgrensene over; år og måned fra datoen; runde fra plasskoden (h → heat, s → semi, q → kval, r → runde, «-»/tom → ukjent, ellers finale); stevne = `cid`, ellers venue + dato; kjønn M/W → M/F. Flyt: 261 396 rader (5 800 utøvere, alle øvelser) → 82 619 i de seks øvelsene → 82 580 uten dubletter → 74 655 utendørs → 69 387 uten mangekamp → 69 225 elektroniske og ikke annullerte → 68 367 med merke → 66 624 med vind → 66 615 innen ±8 → 66 589 rimelige (alle med kjønn); 2 219 utøvere, 1983–2026; 9,0 % av radene har medvind over +2,0. Utvalget er topp-8-finalister i VM/OL (hovedfilen) og finalister i andre mesterskap (replikasjonsfilen: EM, lag-EM, innendørs-VM/EM, Diamond League-finaler m.m.) i alle øvelser; her bare deres resultater i de seks vindøvelsene (1 636 av de 2 350 med slike resultater var finalister i en vindøvelse). Utøvernivådata som ikke kan deles videre. **Tillatelse:** Ifølge Atle (30.10.2026) foreligger tillatelsen fra tidligere. TODO-merknaden i `main.tex` er fjernet, og takken til Tilastopaja Oy står på tittelsiden.

**Spesifikasjon:** `03_estimering.py` importert urørt (within utøver × år × øvelse, måneder klippet 4–10, topp-5 runder, stevneklynget med fixest-lik småutvalgskorreksjon). Per kilde × øvelse × kjønn: lineær og prosent, grenhelninger med delta-metode-KI for forholdet og drag-forhold ved egen fart (100/200 m), knekkmodell (motvind, 0–2, over 2) med dragprediksjon av forholdet over 2 / 0–2, stevne-FE; TFRRS-tertiler (A6-revisjonens definisjon); robusthet (celler ≥ 3, uten 0,0, utøverklynger, TFRRS uten 2016–17). Norske referanserader (alle aldre og 20–34, per kjønn) regnes med samme kode fra `analyseklar.csv`; tallkontrollen krever at de er like tabell 3 og S7 til 1e-9. Snittmerket i S8 er over alle analyserte rader, som i S4 (S7 bruker cellene ≥ 2; derfor 12,40 s mot 12,08 s for gutter og menn 100 m).

**Funn underveis — feil i estimatoren, rettet i fryst fil:** med stevne-FE for Tilastopaja kvinner 100 m ble SE for vind 0,28 (punkt 0,053; ikke-klynget SE 0,0016). Årsak: rundedummyene summerer til 1 når referansekategorien («ukjent») bare finnes i stevner med én rad, som stevne-FE absorberer; X'X blir nær-singulær og klyngevariansen eksploderer. `estimer` tar nå ut kontrollkolonner som er lineærkombinasjoner av de andre (SVD, relativ toleranse 1e-8; vindkolonnene holdes fast), som fixest gjør. Ingen eksisterende A6-estimat endres (kontrollert: R-speilet og tallkontrollen er grønne etter RUN_ALL, og r1_/r2_-filene er uendret i git). Logget i `FREEZE.md`.

**Uavhengig implementasjon:** `audit/uavhengig.R` bygger begge utvalg på nytt fra kildene etter reglene over, sammenligner dem som multisett mot Pythons `eliteende_analyseklar.csv` (0 avvikende nøkler) og estimerer alt med fixest; `audit/sammenlign.py` (del «eliteende»): 78 enheter innenfor toleransene (2e-4 s, 2e-2 cm, forhold 1e-3, stevne-FE-KI 1e-3). `audit/kontroll_tall.py`: hvert tall i den nye teksten og hver S8-rad mot R.

**Resultat:** 100 m-eliteenden ligger der Moinats nivåformel sier, ikke der per-sekund-loven peker: TFRRS 0,054 (0,053–0,056) menn og 0,058 (0,056–0,060) kvinner; Tilastopaja 0,048 (0,045–0,051) og 0,059 (0,055–0,063), mot S4-lovens 0,061–0,077 ved deres snittider. Per sekund løpstid 0,0062–0,0064 i registeret mot 0,0047–0,0052 eksternt (15–27 % lavere); ved lik løpstid gir registerets seniorer 0,071/0,072 mot 0,057/0,060 for den langsomste college-tertilen. College matcher drag-asymmetrien (1,62/1,61 mot 1,67/1,76), finalistene overskrider den (1,93/1,86 mot 1,45/1,49) — på medvindssiden. Over +2,0 er medvindshelningen 12–33 % lavere enn over 0–2 i alle tre kilder, mot drag-predikerte 26–36 %: ingen knekk ved lovlighetsgrensen utover fysikken. **Pilotens punkt 4 («medvind over +2,0 gir nesten ingenting») var modellavhengig** (tosegmentmodell med motvind i samme segment) og er rettet i pilotnotatet. Stevne-FE demper 100 m med 10–20 % i alle kilder.

**Tekst:** nytt avsnitt sist i Methods 2.1, tillegg i Results (H1, H2/H3, H4), Discussion (4.1, 4.2), Strengths/limitations, Conclusion, Data availability og Acknowledgements; tabell S8 med note. Ordtelling 5 823 (var 5 200 før eliteenden, 4 898 før dagens øvrige omskriving) — grensen må avklares av Atle.

## H5 og JSS-kravene, Atles beslutning 30.10.2026 («Ja, skriv inn»)

Endringsrapportens avsnitt 8, punkt 2–3, er skrevet inn. Ingen tall er endret; bare påstandene om tallene.

- **H5 (Results):** Fra 12 år er vinduet verdt 0,11–0,25 s på 100 og 200 m.
  - **Gutter:** ingen klar aldersgradient i sekunder (100 m 0,14–0,16 s, 200 m 0,13–0,19 s i båndene 12–13 til 20–34, med felles KI-overlapp). Aldersfallet i den lineære helningen ligger i motvindshelningen.
  - **Jenter:** større før seniorårene (100 m 0,15 mot 0,11 s, 200 m 0,25 mot 0,14 s), med overlappende intervaller.
  - **Som andel av løpstid:** 1,10 mot 1,27 % for gutter og menn, 0,95 mot 0,87 % for jenter og kvinner.
  - **Tyrving-poengene:** ungdomsmarginen har omtrent samme forhold som i sekunder.
- **Implications og Conclusion:**
  - «Largest contribution in seconds and share of race time», «similar points … raw-seconds» og kalibreringssetningen er fjernet.
  - Talentsetningen gjelder nå den lineære helningen.
- **JSS:** Sammendraget har 197 ord (grense 200), det er 6 nøkkelord, og Methods har fått «Sample size estimation and justification» med KI-halvbredder.
- **Tallkontroll:** 193 ankrede sjekker, 0 feil, 0 udekkede tall, kjørt på commit-tilstanden.
  - Kontrollen teller også ordene i sammendraget og antall nøkkelord.
  - PDF-en er bygget fra samme tilstand: 29 sider, ingen udefinerte referanser.
- **Samtidig arbeid:** En annen økt legger inn eliteenden (tabell S8) i samme mappe. Den er ikke med i denne kontrollen, og `RUN_ALL.sh` kjøres når den er ferdig.

## Etikk, datatilgang og anonymisering, Atles beskjed 30.10.2026

- **Etikk og datatilgang (commit e1efd61):** Teksten følger dropout-artikkelen (IJSSC R1).
  - Studien er ikke helseforskning etter helseforskningsloven §§ 2 og 4, og Sikt har bekreftet at bruken ikke reiser personvernspørsmål.
  - Samtykke var ikke nødvendig. Helsinki-erklæringen er nevnt (JSS).
  - Analysedatasettet deles ikke (GDPR). Koden og de aggregerte estimeringsfilene deponeres ved aksept.
- **Dobbeltanonym vurdering (JSS):**
  - `manus/title_page.tex` er en egen fil med forfatteropplysninger og erklæringene som identifiserer forfatteren (Disclosure of interest, Funding, Author contributions, KI-bruk og Acknowledgements).
  - `main.tex` har en anonymiseringsnotis i stedet for forfatterblokken, «by a post-plan decision» og «available on request».
  - RUN_ALL stopper ved forfatteropplysninger i manus-PDF-en eller metadataene. Kontrollen sjekker at main.tex er anonym og at tittelsiden er komplett (284 sjekker).

## Medforfatter, Atles beslutning 30.10.2026

- Simen Guttormsen er medforfatter med samme tilknytning som Atle (Handelshøyskolen, NMBU). Atle er fortsatt korresponderende forfatter. E-posten og ORCID-en til Simen (0009-0002-2533-8561) står på tittelsiden. Kontrollsifferet stemmer, og ORCID-registeret har navnet hans.
- Erklæringene på tittelsiden står i flertall. Plattformsetningen gjelder bare AGG; git-loggen for friidrettsresultater.no har bare Atle som forfatter.
- Bidragssetningen følger høydeartikkelen. SG samlet inn TFRRS-profilene som `tfrrs_shared` bygger på (den eksterne valideringen, tabell S8), og reviderte manus kritisk. Begge godkjenner endelig versjon. **Atle og Simen må bekrefte setningen før innsending.**
- Simen står selv i registerutvalget: 75 av 392 797 rader i `analyseklar.csv` (36 651 utøvere). Det er ungdomsresultater fra 2011–2020 (alder 10–19), mest lengde og 60 m. Én utøver kan ikke flytte estimatene, så det er ikke skrevet inn i erklæringen. I høydeartikkelen ble det opplyst «for full transparency».
- Anonymitetskontrollene i RUN_ALL og kontrollskriptet ser nå også etter «Simen» og «SG».

## Tittel, Atles valg 30.10.2026

- Tittelen er forkortet fra 22 til 16 ord: «How much is the wind worth? Sprints and horizontal jumps from age 10 to senior level». Den korte tittelen øverst på sidene er uendret.
- «age 10» er den nedre aldersgrensen i utvalget (alder 10–34, `ekskl_alder_utenfor_10_34` i `flyt.json`). Tallkontrollen dekker den med unntaket `age 1[03]`, som for «from age 10» i teksten.
- Arbeidstittelen i `ANALYSEPLAN.md` og i den simulerte fagfellevurderingen (`manus/REFEREE_RUNDE1.md`) er historisk og står urørt.

## Innsending til JSS, Atles bestilling 31.10.2026

Atle bestilte: «Bygg opp A6 så den kan sendes til Journal of Sports Sciences». Arbeidet er målt mot JSS' forfatterveiledning, oppdatert 26.10.2026. Den ble lest i nettleseren fordi nettstedet stengte ute skriptet, og den stemmer med teksten Atle limte inn. Delavsnittet om utvalgsstørrelse er i tillegg målt mot redaksjonens krav (Abt mfl. 2025, doi 10.1080/02640414.2025.2499403). Kodeendringene står i `FREEZE.md`.

- **Krav som alt var oppfylt:**
  - Manus er dobbeltanonymt og har løpende linjenummer.
  - Sammendraget har under 200 ord, og det er 6 nøkkelord.
  - Methods har etikksetning med Helsinki-erklæringen, og manus har Data availability.
  - Disclosure of interest, Funding og KI-erklæringen står på tittelsiden.
  - Stavemåten er konsekvent britisk, og alle referansene er sitert i teksten.
- **Rettet:**
  - **Figurer:** Figur 3 og 4 viser punktestimater med KI, fordi JSS fraråder stolpediagrammer. Filnavnene følger trykkrekkefølgen. Bildene har ikke lenger egne titler, og forklaringen i figur 5 dekket nederste rad og står nå under plottet. Tallene i figurene er de samme.
  - **Supplementet** er en egen fil, `manus/supplement.tex`. S-tabellene er nummerert etter første sitering i manus (gammel → ny: S7→S1, S8→S2, S2→S3, S4→S4, S1→S5, S5→S6, S3→S7, S6→S8). Kontrollen sjekker nummereringen mot `supplement.aux`. Eliteenden er derfor tabell S2, ikke S8 som i avsnittene over.
  - **Delavsnittet om utvalgsstørrelse** har fått en følsomhetsanalyse med alle inndata redaksjonen ber om: formål, tidspunkt, utfall, test, programvare, α og styrke, minste effekt av interesse med begrunnelse, effekttype og frafall. Analysen ligger i `12_utvalgsstorrelse.py`, som skriver `tables/estimering/r4_mde.csv`.
    - Minste påvisbare effekt (MDE) per øvelse: 0,003 s (60 m), 0,004 s (100 m), 0,013 s (200 m), 0,018 og 0,053 s (80 og 150 m), 0,4 og 0,3 cm (lengde fra brett og fra sone) og 0,9 og 1,4 cm (tresteg fra brett og fra sone).
    - I aldersbåndene for 60, 100 og 200 m er MDE 0,004–0,086 s (median 0,014), størst for 200 m ved 10–11 år.
    - Minste effekt av interesse er én registreringsenhet over +2,0-vinduet: 0,005 s og 0,5 cm per m/s. 60 m, 100 m og lengde (begge varianter) ligger under den.
    - De samme tallene regnes fra R-speilets KI og gir like viste verdier.
    - Lakens (2022) er lagt til og sjekket mot CrossRef.
  - **Tallkontrollen:** Tittelsatsen fra 30.10.2026 (`\hyphenpenalty=10000`) ga et udekket tall, men kontrollen ble ikke kjørt til grønt etter den endringen. Den har nå et eget unntak, og ingen tall i teksten er berørt.
- **Nye filer:** `12_utvalgsstorrelse.py`, `13_jss_pakke.py`, `manus/supplement.tex` og `manus/cover_letter.tex` (utkast). I tillegg mappen `JSS_opplasting/` med README, svar til portalen og `MANIFEST.sha256`. Mappen bygges sist i RUN_ALL.
- **Status:** `RUN_ALL.sh` er grønn.
  - Tallkontrollen ga 312 ankrede sjekker (307 i manus, 5 i supplementet), 0 feil og 0 udekkede tall.
  - R-speilet passerer, og to kjøringer ga like hasher på alle 91 utdatafiler.
  - Manus har 26 sider, supplementet 5, tittelsiden 1 og følgebrevet 1.
- **Ordtelling:** 6 008 ord løpende tekst. JSS anbefaler om lag 4 000, men kaller det «a guideline and not a limit». Atle avgjør om teksten skal kortes.

## Til MPEES i stedet for JSS, Atles beslutning 31.10.2026

Atle skrev: «La oss prøve denne for vind artikkelen» og la ved forfatterveiledningen til *Measurement in Physical Education and Exercise Science* (MPEES). Han har allerede to artikler inne hos JSS. Tidsskriftets side om omfang og seksjoner og Taylor & Francis' KI-regler er lest i nettleseren 31.10.2026. Kodeendringene står i `FREEZE.md`. JSS-versjonen ligger i commit 3b8911e.

- **MPEES-kravene og hvordan de er møtt:**
  - **Fagfellevurdering:** MPEES bruker enkeltanonym vurdering, så tittelsiden med forfatterne er side 1 i manus. Den egne tittelsiden og anonymitetskontrollen er tatt bort.
  - **Sammendrag:** høyst 150 ord. Sammendraget er kortet fra 197 til 150 ord. Disse delene er tatt ut: «linear fit»-merknaden, de fem sprintøvelsene og fire hoppøvelsene, asymmetritallene for 100 m, «in both sexes» og H5-setningen om gutter, jenter og 2025-listene. Alle tallene står fortsatt i resultatdelen.
  - **Nøkkelord:** 4–5 kreves. Det er nå 5: «registry study» og «age-group competition» er erstattet med «performance measurement».
  - **Staving:** MPEES krever amerikansk staving (metre → meter, analysed → analyzed, standardise → standardize med flere), også i figuraksene. Kontrollen leter etter britiske former.
  - **Oppsett:**
    - dobbel linjeavstand med 25 linjer per side (MPEES: 23–25), hvert element på ny side, alle avsnitt med innrykk, alle sider nummerert og linjenummer;
    - rekkefølge: tittelside, sammendrag, tekst, erklæringer, referanser, tabeller (én per side), figurer, figurtekster som liste.
  - **Lengde:** høyst om lag 30 sider inkludert alt. JSS-teksten ga 36 sider i dette oppsettet. Disse delene er derfor flyttet ordrett til supplementet:
    - hekkeutvidelsen med tabell og figur (S6, figur S2);
    - asymmetritabellen (S2) og evnefiguren (figur S1);
    - detaljene om dublettfjerningen, MDE-avsnittet og listen over planavvik, som «Supplementary Methods».
    Manus har nå korte henvisninger og en to-setningers oppsummering av MDE. Etikkavsnittet i erklæringene var dobbelt og er tatt bort; Helsinki-setningen står i Methods. Bidragssetningen er tatt ut, fordi rollene føres inn i portalen. Manus har 30 sider og om lag 5 500 ord.
  - **Figurer:** egne filer på 300 dpi. Fargetrykk koster £300 per figur, så markører og linjetyper skiller seriene også i gråtoner.
  - **Seksjon og etikk:**
    - Forfatterne skal oppgi seksjon. Manus og følgebrevet foreslår Exercise Science.
    - MPEES ber om en IRB-setning. Methods forklarer at godkjenning ikke var nødvendig etter norsk lov, slik T&F' etikkregler åpner for, og følgebrevet sier det samme.
  - **Følgebrev:** MPEES-versjonen sier at manus ikke er publisert eller sendt samtidig andre steder. Den oppgir seksjon, sidetall, ordtelling og antall tabeller og figurer, og kontrollen sjekker disse tallene.
- **T&F' KI-regler:** Taylor & Francis tillater ikke at generativ KI lager førsteutkast til et manus eller deler av det. Erklæringen skal ha verktøy og versjon, si at bruksvilkårene er sjekket, og si at forfatterne tar fullt ansvar, også for referansene.
  - Erklæringen i manus har nå alle disse delene. Den sier fortsatt sannferdig at Claude er brukt til å «draft and edit text».
  - Modellene er hentet fra øktloggene: Claude Opus 5.5, Fable 5 og 5.1 og Haiku 5.5, september–oktober 2026.
  - Atle avgjør om A6 kan sendes til et T&F-tidsskrift med denne erklæringen. Regelen gjelder også JSS.
- **Nye og endrede filer:** `13_opplasting.py` (var `13_jss_pakke.py`), `MPEES_opplasting/` (README, PDF-er, TIFF-figurer, MANIFEST), `manus/main.tex`, `manus/supplement.tex` og `manus/cover_letter.tex`. `manus/title_page.tex` og `JSS_opplasting/` er fjernet; begge ligger i 3b8911e. `figures/fig5_hurdles.png` er en mellomfil fra `05_hekk.py` og brukes ikke.
- **Status:** `RUN_ALL.sh` er grønn.
  - Tallkontrollen ga 310 ankrede sjekker (285 i manus, 25 i supplementet), 0 feil og 0 udekkede tall.
  - R-speilet passerer, og to kjøringer ga like hasher på alle 102 utdatafiler.
  - Manus har 30 sider, supplementet 9 og følgebrevet 1.
- **KI-erklæringen, Atles tekst 31.10.2026:** «Anthropic Claude (Opus 5.5) was used during the preparation of this manuscript to improve language and readability, assist with structuring the text, check analysis code and identify errors. All output was reviewed, edited, and verified by the authors, who take full responsibility for the content of the manuscript.» Den erstatter utkastet over. Kontrollen krever verktøy og versjon og forfatternes ansvar.
