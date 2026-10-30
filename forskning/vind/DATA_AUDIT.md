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
