# DATA_AUDIT — A6 «How much is the wind worth?»

Audit startet 30.10.2026 etter `paper-data-audit`-skillen. Status: fase 0–1 ferdig; funn nederst.

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
