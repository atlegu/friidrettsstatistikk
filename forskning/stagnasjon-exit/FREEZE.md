# Kode- og datafrysing — A1 «Stagnation before exit»

Fryst 30.10.2026 etter dataauditen (`DATA_AUDIT.md`) og omskrivingen. Herfra endres bare teksten i `manus/main.tex`, med mindre en verifisert feil krever en kodeendring.

## Hva er fryst

- **`FREEZE_code.sha256`:** `RUN_ALL.sh`, uttrekket (`00_uttrekk.py`, kjøres ikke), analysekjeden 01–07 med 06b, `a1_tyrving.py`, kontroll- og speilskriptene i `audit/` (Python og R) og de delte modulene `../rens_felles.py`, `../audit_felles.py` og `../ncc-kohort/revision_r1/analysis/tyrving_r2.py`.
- **`FREEZE_data.sha256`:** råuttrekket i `data_private/` (29.10.2026, se `uttrekksinfo.json`) og Tyrving-parameterne `../ncc-kohort/revision_r1/analysis/tyrving_params_2014.csv`.

`RUN_ALL.sh` kontrollerer begge før noe kjøres, og stopper hvis en fil er endret eller hashfilene mangler. Avledede filer (`analysedata.csv`, `flyt.json`) bygges på nytt ved hver kjøring. Kjeden er deterministisk: to kjøringer 30.10.2026 ga like hasher på alle utdata (tabeller, figurer, PDF, R-utdata og avledede data).

## Endre en fryst fil

Bare for en verifisert feil, ikke for en preferanse:

1. Skriv grunn, fil og ventet virkning i loggen under *før* endringen.
2. Gjør endringen og lag hashene på nytt:
   `shasum -a 256 $(awk '{print $2}' FREEZE_code.sha256) > FREEZE_code.sha256`
   (og `FREEZE_data.sha256` på samme måte hvis data endres).
3. Kjør `bash RUN_ALL.sh` til alt er grønt, og før gamle og nye resultater inn i loggen.

En tekstendring som endrer en setning tallkontrollen ankrer på, krever også en endring i `audit/kontroll_tall.py`. Det er en endring i en fryst fil og logges her.

## Logg

| Dato | Fil | Grunn | Virkning |
|---|---|---|---|
| 30.10.2026 | — | Frysing etter audit og omskriving | — |
| 30.10.2026 | `../rens_felles.py`, `01_variabler.py`, `audit/uavhengig.R`, `audit/sammenlign.py`, `audit/kontroll_tall.py` | Ryddeøkten i `scraper/` (`opprydding/KRYSSDUBLETTER_2026-10-30.md`) fant 8 846 brettkopier av sonehopp fra flerdagsstevner: brettraden har stevnets startdato, sonehoppet ligger 1–6 dager senere, og kilden viser hoppet bare under sonen (12 av 12 kontrollert). Samme-dato-regelen fanger dem ikke. I A1-uttrekket: 5 780 slike brettrader, mot 1 treff i en placebovariant med sonen før brettraden. Ny regel i `fjern_kopier`: brettrad med identisk OK-sonerad (utøver, resultat, vind) 1–6 dager senere fjernes. Speiles i R. | Ventet: små endringer; 1 236 utøvere i primærutvalget har slike rader (mest ved 13 år). |
| 30.10.2026 | `01_variabler.py`, `audit/uavhengig.R` | Siste smale gjennomgang (A-1): følsomhetsanalysen «wind-legal marks only» regnet merker uten registrert vind som lovlige (`is_wind_legal` mangler → lovlig). Planen sier «wind-legal marks only in wind-affected events». Nå er et merke vindlovlig når øvelsen ikke måler vind, når det er satt innendørs (ingen vind), eller når lovlig vind er registrert. Utendørs vindmerker uten vindmåling faller ut av denne varianten. | Én rad i tabell 4 og én i teksten (gjennomgangen anslo 2,15 → om lag 2,03) |
| 30.10.2026 | `04_robusthet.py`, `05_figurer_tabeller.py`, `06b_revisjon_r2.py`, `07_manustabeller.py`, `audit/uavhengig.R`, `audit/sammenlign.py`, `audit/kontroll_tall.py` | Siste smale gjennomgang (B-1): landmark-Cox og KM-figuren «fra 17 år» tok med frafallere som sluttet ved 15–16 år, som hendelser ved t = 0,1 (54 % av hendelsene). En landmark-analyse skal bare ha med dem som er under risiko ved landmark-tidspunktet, så nå er det utøvere med resultater etter fylte 16. Gjennomgangen viste også at 58 % av frafallerne har siste sesong inne i 15–16-vinduet. H1 blant dem som er aktive etter fylte 16, er lagt til som robusthetsrad (lagt til etter estimeringen). Ordlyden i teksten er rettet etter gjennomgangens B/C-funn, og ankrene følger med. | Cox-HR og KM-figur endres (gjennomgangen anslo HR 0,84); ny rad i tabell 4 (anslått OR 1,81) |
| 30.10.2026 | `01_variabler.py`, `07_manustabeller.py`, `audit/uavhengig.R`, `audit/sammenlign.py`, `audit/kontroll_tall.py` | Siste smale gjennomgang (C-10): S1 summerte ikke, fordi «uten skårbare poeng» ble talt over alle kull (642, med 2006) og småcellene bare over 1998–2005 (20). Nå telles begge eksklusjonene blant de 4 475 født 1998–2005 (578 og 20), og 2006-kullet vises som eget trinn. | S1 og flyttallene i Methods; ingen estimater endres |
