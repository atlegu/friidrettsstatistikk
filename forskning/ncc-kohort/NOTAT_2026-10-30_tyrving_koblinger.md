# Notat: Tyrving-koblinger i IJSSC-artikkelen (SPO-26-1604)

30.10.2026. Grunnlag for neste revisjon. Ingenting er sendt til tidsskriftet, og den innsendte R1-versjonen er ikke rørt.

## Konklusjon

**Feilen endrer ingen konklusjon, ingen tall i sammendraget og ingenting i hovedtabellene.**

- Baseline-Tyrving er uberørt, og dermed også volum-OR 2,04, Tyrving-OR 1,75, CV-AUC 0,767 og AUC-gapet 0,040. Grunnen er at ingen av øvelseskodene som manglet kobling forekommer i baseline-stevnet med en norm. Av 7 400 baseline-resultater får 0 endret poengsum.
- Ved neste revisjon trengs **ett tall i løpende tekst**: avsnitt 3.6, n = 1 721 blir 1 722.
- Celler i fem supplementstabeller endres, alle i siste siffer: S12, S15, S17, S18 og S27. Disse oppdateres automatisk fordi tabellene genereres av koden.
- Teksten i Supplementary Methods S-M3 beskriver allerede riktig regel («Every result is scored when its event and implement or hurdle specification match a row of the Tyrving table»). Det var koden som ikke fulgte den fullt ut, så S-M3 trenger ingen endring.

Det er ikke nødvendig å kontakte tidsskriftet nå. Rettingen kan nevnes med én setning i svarbrevet ved neste revisjon.

## Hva var feil

Poengmodulen `tyrving_r2.py`, som R1 bruker, manglet kobling fra registerets øvelseskoder til tabellrader for flere standardredskaper og -øvelser, selv om tabellen har normer for dem. Modulen ga da ingen poeng. Ved 13–16 år gjelder det 5 707 resultater:

| Øvelse (kode) | Kjønn, alder | Resultater som nå får poeng |
|---|---|---|
| Spyd 500 g | jenter 15–16 | 1 063 |
| 80 m hekk 76,2 cm | jenter 15–16 | 888 |
| 300 m hekk 76,2 cm | 14–16 | 638 |
| Kule 5 kg | gutter 16 | 619 |
| Liten ball 150 g | 13–14 | 500 |
| Spyd 700 g | gutter 16 | 479 |
| Diskos 1,5 kg | gutter 16 | 391 |
| 100 m hekk 84 cm | gutter 15 | 238 |
| Slegge 5 kg/120 cm | gutter 16 | 222 |
| 100 m hekk 91,4 cm | gutter 16 | 178 |
| 1500 m hinder | 14–16 | 140 |
| 300 m hekk 84 cm | gutter 16 | 93 |
| Kappgang 2000–10 000 m | 13–16 | 258 |

Resultater med poeng ved 13–16 år øker dermed fra 130 422 til 136 129 av 141 835. Det som fortsatt står uten poeng, mangler norm for kjønn og alder, for eksempel 800 m ved 13 år, 3000 m før 16 og slegge 3 kg på 110 cm wire.

**To forhold ved mai-uttrekket:**
- **Liten ball** er lagret med resultattype «tid» og verdi i centimeter (resultat × 100). Dagens register har rettet dette. Uten reparasjon ville ballkastene fått 0 poeng; med reparasjonen er medianen 436 poeng.
- **Sonekopiene** som ble funnet i registeret 30.10, finnes ikke i IJSSC-dataene, fordi mai-uttrekket er eldre enn reimportene.

## Hva endres i variablene

Endringene gjelder bare maksimum per alder over alle stevner og det som bygger på det:

| Variabel | Utøvere endret | Merknad |
|---|---|---|
| Baseline-Tyrving (beste, snitt, uten sone) | 0 | |
| Tyrving-maksimum ved 13 år | 8 | |
| Tyrving-maksimum ved 14 år | 34 | |
| Tyrving-maksimum ved 15 år | 159 | snitt 888,8 → 897,7 |
| Tyrving-maksimum ved 16 år | 221 | 48 flere med poeng; snitt 901,4 → 914,5 |
| Topp før 15 år | 31 | |
| Stigningstall 13–16 år | 304 | |

## Gammelt → nytt: alt rapportert som flytter seg

| Hvor | R1 | Med komplett kobling |
|---|---|---|
| Avsnitt 3.6 (løpende tekst): utvalget med Tyrving ved både 13 og 14 år | n = 1 721 | **n = 1 722** |
| Avsnitt 3.6: AUC med utvikling 13→14 mot volum | 0,737 mot 0,736; KI for differansen −0,04 til 0,04 | uendret |
| Tabell S15 og S27, samme sammenligning | n 1 721; differanse −0,001 (KI −0,042 til 0,039); p 0,943 | n 1 722; −0,001 (KI −0,042 til 0,040); p 0,953 |
| Tabell S12 (utvalgskart) | utvikling 1 721; S18 B/C 2 135 | 1 722; 2 136 |
| Tabell S17 (gjenkjørt originaltabell 5), full modell med 22 prediktorer | AUC 0,83 (±0,02) | 0,84 (±0,02) |
| Tabell S18 B: Tyrving (z) | KI [0,92; 1,49], p 0,193 | [0,92; 1,48], p 0,202 |
| Tabell S18 B: HHI | p 0,302 | p 0,305 |
| Tabell S18 B/C: Tyrving i primærkategori | 1,80 [1,36; 2,38] / 2,07 [1,70; 2,51] | 1,81 [1,37; 2,40] / 2,07 [1,71; 2,52] |
| Tabell S18 C: HHI og volum før milepæl | p 0,390; volum [1,60; 2,09] | p 0,392; [1,59; 2,09] |
| Note til tabell S18 | «OR 1.80–2.07» | «OR 1.81–2.07» |

S18 påvirkes fordi «Tyrving in primary category» i det opprinnelige skriptet (`data/15`) er beste poeng i primærkategorien fra alle stevner ved 13–14 år, ikke bare baseline-stevnet. Der kommer blant annet 300 m hekk, hinder og kappgang ved 14 år inn.

**Uendret:** hovedtekst ellers, sammendrag og hovedtabellene 1–5; det bygde manuset er byte-identisk bortsett fra n i avsnitt 3.6.

**Endret, men ikke rapportert:**
- To korrelasjoner som lagres, men ikke siteres: volum før milepæl mot topp før 15 år går fra 0,518 til 0,522, og volum ved milepæl mot poeng ved 15 år fra 0,626 til 0,640.
- Den gjenkjørte viktighetstabellen fra random forest, der stigningstallet går fra 4. til 3. plass. Den vises ikke i supplementet.

Svarbrevet til R1 siterer «−0.001 (−0.042 to 0.039)» for utviklingssammenligningen; med rettingen er øvre grense 0,040. Brevet er sendt, og jeg har ikke endret det.

## Forslag til minimale endringer ved neste revisjon

1. Avsnitt 3.6: n = 1 721 blir 1 722. Dette er gjort i kopien.
2. Supplementstabellene S12, S15, S17, S18 og S27 oppdateres med koden. Dette er gjort i kopien.
3. S-M3 trenger ingen endring.
4. Hvis du vil, en setning i listen over datarettinger i S-M12 og én linje i svarbrevet, for eksempel: «Implements and hurdle specifications that the R1 scoring left unmapped (e.g., shot 5 kg, javelin 500/700 g, 80 m hurdles 76.2 cm) are now scored; baseline scores are unchanged, and only supplementary cells move in the last digit.» Det er ditt valg; du har tidligere ønsket at datarettinger beskrives kort.
5. Når neste revisjon starter, må markeringen av endringer settes mot R1 i stedet for mot originalinnsendingen. Det avgjøres da.

## Hvor filene ligger

`revision_r2_tyrving/` er en kopi av den innsendte R1 (worktree-commit 60b5720, identisk med `IJSSC_R1_opplasting/`). `revision_r1/`, frysingen og opplastingsfilene er ikke endret.

| Fil | Innhold |
|---|---|
| `analysis/tyrving_r3.py` | komplett kobling, samme formler og parametere |
| `analysis/r2_kontroll_koblinger.py` → `tables/r2_koblinger.csv` | hver kobling kontrollert mot tabellrader for kjønn og alder |
| `analysis/r2_sammenlign.py` → `tables/r2_endringer_resultater.csv`, `r2_endringer_tabeller.csv`, `r2_diff_tabeller.txt`, `r2_diff_manus.txt` | alle utdata mot R1 |
| `RUN_ALL_R2.sh` | hele kjeden med kontroller |
| `README_R2.md` | beskrivelse på engelsk |

**Nullkjøring:** Med uendret modul reproduserte den nye mappen alle R1-utdata. Analysefilen var byte-identisk, og tabeller, tekst og manus var identiske; `r1_results.json` hadde største relative avvik 1,6e-13 (flyttallsstøy fra nyere numerikkbiblioteker). Alle forskjellene over skyldes derfor koblingen alene.

**Sluttkjøring (`RUN_ALL_R2.sh`, 30.10.2026):** Kjøringen er grønn. Den startet fra de frosne R1-inndataene (hash-kontrollert) og bygget analysefilen på nytt uten spørringer mot registeret.
- Ordtellingen (5 994) står i begge brevene, og det er ingen forfatter–år-sitater igjen.
- Den uavhengige R-implementasjonen og sitatkontrollen av svarbrevet består.
- Manusdiffen mot R1 er én linje: n i avsnitt 3.6.
