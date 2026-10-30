# Kode- og datafrysing — A6 «How much is the wind worth?»

Fryst 30.10.2026 etter dataauditen (`DATA_AUDIT.md`) og omskrivingen. Herfra endres bare teksten i `manus/main.tex`, med mindre en verifisert feil krever en kodeendring.

## Hva er fryst

- **`FREEZE_code.sha256`:** `RUN_ALL.sh`, uttrekkene (`00_uttrekk.py`, `00b_uttrekk_hekk.py`, kjøres ikke), analysekjeden (01, 02, 03, 05, 07, 07b, 08, 09, 10), kontroll- og speilskriptene i `audit/` (Python og R) og de delte modulene `../rens_felles.py`, `../audit_felles.py` og `../ncc-kohort/revision_r1/analysis/tyrving_r2.py`. 04 og 06 er erstattet av 08 og 09, kjøres ikke og er ikke fryst.
- **`FREEZE_data.sha256`:** råuttrekkene i `data_private/` (29.10.2026, se `uttrekksinfo.json` og `uttrekksinfo_hekk.json`) og Tyrving-parameterne `../ncc-kohort/revision_r1/analysis/tyrving_params_2014.csv`.

`RUN_ALL.sh` kontrollerer begge før noe kjøres, og stopper hvis en fil er endret eller hashfilene mangler. Avledede filer (`analyseklar.csv`, `flyt.json`, `missing.csv`) bygges på nytt ved hver kjøring. Kjeden er deterministisk: to kjøringer 30.10.2026 ga like hasher på alle utdata (tabeller, figurer, PDF, R-utdata og avledede data).

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
| 30.10.2026 | `audit/uavhengig.R` | Fixest med én tråd, og stevne-FE-filen avrundes til 10 gjeldende siffer: toveis FE ga maskinpresisjonsstøy mellom R-prosesser, så filen fikk ny hash ved hver kjøring | Ingen; R-utdata nå like mellom kjøringer |
| 30.10.2026 | `../rens_felles.py`, `01_variabler.py`, `audit/uavhengig.R`, `audit/sammenlign.py`, `audit/kontroll_tall.py` | Ryddeøkten i `scraper/` (`opprydding/KRYSSDUBLETTER_2026-10-30.md`) fant 8 846 brettkopier av sonehopp fra flerdagsstevner: brettraden har stevnets startdato, sonehoppet ligger 1–6 dager senere, og kilden viser hoppet bare under sonen (12 av 12 kontrollert). Samme-dato-regelen fanger dem ikke. I A6-uttrekket: 8 906 slike brettrader, mot 6 treff i en placebovariant med sonen før brettraden. Ny regel i `fjern_kopier`: brettrad med identisk OK-sonerad (utøver, resultat, vind) 1–6 dager senere fjernes. Speiles i R. | Ventet: endring i lengde og tresteg (brett) for 11–13 år |
| 30.10.2026 | `01_variabler.py`, `audit/uavhengig.R`, `audit/kontroll_tall.py` | Fra februar 2026 la importen alle nye sonehopp under brettkoden. Det er feil kode, ikke kopier, og det kan bare avgjøres mot kilden. Uttrekket har 0 utendørs sonerader i 2026, mot 1 736 ved 11–13 år i 2025. Brettkodede lengde- og trestegrader i 2026 ved 11–13 år ekskluderes derfor. Speiles i R. | Ventet: om lag 1 600 rader færre; små endringer i brettøvelsene for 11–13 år |
| 30.10.2026 | `07_revisjon_r1.py`, `audit/kontroll_tall.py` | Siste smale gjennomgang (A2): 2025-listene tok med medvind over +2,0 (64 % av topp 50 hos seniormenn), «senior» var 20–34 år, og lister med under 60 utøvere falt stille ut (seniorkvinner, 57). Nasjonale årslister rangerer lovlige merker i åpen klasse. Nå: bare merker med vind ≤ +2,0, senior = alle aldre i filen, og hver rad korrigeres med medvindshelningen 0–2 for egen kjønns- og aldersgruppe. Gjennomgangen (C2) fant også at ±0,2-kontrollen rundt +2,0 tok ut 1,8–2,1 og beholdt +2,2 (flyttall); nå regnes avstanden i tideler. | Listetallene i Results og Implications endres; ±0,2-kontrollen endres lite |
| 30.10.2026 | `08_r1_figurer_tabeller.py` | Siste smale gjennomgang (B5): aksen i figur 5 sa «per +1 m/s tailwind», men figuren viser lineære helninger over med- og motvind | Bare aksetekst |
| 30.10.2026 | `07b_revisjon_r2.py`, `09_r1_supptex.py`, `audit/uavhengig.R`, `audit/sammenlign.py`, `audit/kontroll_tall.py` | Atles beskjed: Lybbert & Zheng (2023, JQAS) må behandles grundig. De tolker at motvind koster amerikanske high school-løpere mer enn en drag-modell for elitemenn tilsier, mest for jenter, som psykologi. Ny analyse (lagt til etter planen): motvind/medvind-forholdet for 100 m per kjønn og aldersbånd mot drag-fysikk ved løpernes egen fart gjennom samme estimator, med og uten stevne-FE, og drag-forholdet ved fast fart (eliten og gjennomsnittene i deres tabell 1). Ny tabell S7. Speiles i R. | Ny tabell S7 og tekst; ingen eksisterende tall endres |
| 30.10.2026 | `audit/kontroll_tall.py` | Atles beslutning («Ja, skriv inn»; endringsrapporten avsnitt 8, punkt 2–3). For gutter er vinduet i sekunder ikke størst for de yngste, og som andel av løpstid er det ikke størst for dem. Tyrving-poengene speiler sekundene og er ikke «similar». Sammendraget, H5-avsnittet, Implications og Conclusion er derfor skrevet om, og den udokumenterte kalibreringssetningen er fjernet. JSS-krav: sammendraget har nå 197 ord, «measurement» er tatt ut av nøkkelordene (nå 6), og Methods har fått delavsnittet «Sample size estimation and justification». Kontrollen har fått nye sammendragsankre og nye krav: ingen aldersfall for gutter (felles KI-overlapp, 12–13 under 1,2 × senior), jenter over seniorkvinnene i hvert bånd, andel av løpstid, poengforhold ≈ sekundforhold, minst en tidel i alle bånd, KI-halvbredder, ordtelling i sammendraget og antall nøkkelord. | Ingen tall endres. Kontrollen ga 193 ankrede sjekker, 0 feil og 0 udekkede tall, kjørt på commit-tilstanden uten S8-arbeidet |
