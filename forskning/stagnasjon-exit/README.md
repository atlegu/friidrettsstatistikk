# A1 — Stagnasjon før exit

Tester mastery-tolkningen fra RAE-artikkelen: predikerer utøverens egen *fremgang*
(ikke nivå) fortsatt deltakelse — særlig hos dem som er født sent på året?
Full plan i [ANALYSEPLAN.md](ANALYSEPLAN.md); engelsk forhåndsregistreringstekst i
[OSF_PREREGISTRATION.md](OSF_PREREGISTRATION.md).

## Kjørerekkefølge

| Steg | Skript | Status |
|---|---|---|
| 0 | `00_uttrekk.py` | Kjørt 29.10.2026 → frosset uttrekk i `data_private/` (git-ignorert, regenererbart) |
| 1 | `01_variabler.py` | Kjørt → `data_private/analysedata.csv` + `data_private/flyt.json` |
| 2 | `02_deskriptiv.py` | Kjørt → `tables/` (kun prereg-trygge aggregater) |
| — | Frigivelse | Besluttet 29.10.2026 (Atle): ingen ekstern registrering; planen var committet før estimering. Se `FRIGITT_FOR_MODELLERING.txt` |
| 3 | `03_modeller.py --kjor` | Kjørt 29.10.2026 → `tables/modeller/` |
| 4 | `04_robusthet.py --kjor` | Kjørt 29.10.2026 → `tables/robusthet/` |

`RUN_ALL.sh` kjører steg 0–2. Python: `scraper/venv` (pandas, statsmodels, sklearn, lifelines).

## Hovedresultater (29.10.2026)

- **H1 støttet:** fremgang 13–14 → 15–16 predikerer seniorstatus, OR **2,03 per SD** [1,73–2,37],
  utover nivå, volum (nivå og endring), k-ene og struktur. CV-AUC 0,855 → 0,864 (+0,009).
  Kalibreringsslope 0,97, Brier 0,098.
- **H2 ikke støttet:** interaksjon med fødselskvartal OR 0,95 [0,85–1,07]; fremgang beskytter
  i begge strata (Q1–Q2: 2,19; Q3–Q4: 1,89). Den relative-alder-spesifikke mastery-prediksjonen
  fikk ikke støtte — sammenhengen er generell.
- **H3:** gitt volum diskriminerer fremgang og nivå likt (ΔAUC −0,001 [−0,002, −0,001]).
- **Robusthet:** kohort A 2,00 / B 2,03; uten covid-kull 1,95; k≥2 2,18; byttegruppe 1,92;
  vindgyldig 2,00; klubbklynger uendret; negativkontrollen (Δ 13→14 i baselinevinduet) **null**
  (OR 1,00); E-verdi 2,84 (KI-grense 2,45). Landmark-Cox: HR 0,86 per SD fremgang;
  volum 15–16 dominerer (HR 0,47); kvinner HR 1,19.

Gjenstår for manus: exit-justerte Tyrving-baner (deskriptiv figur), tabeller/figurer og tekst.

## Nøkkeltall fra det frosne uttrekket (29.10.2026)

32 447 utøvere født 1998–2006 → 12 938 med OK-resultat ved 13–14 → 4 910 landmark
(også aktive ved 15–16) → **primærutvalg 3 808** (født 1998–2005, skårbar Tyrving i
hovedgruppen i begge vinduer), hvorav **648 (17,0 %) aktive seniorer**.

## Viktige valg (begrunnet i ANALYSEPLAN.md)

- Fremgang = Δ snitt-av-3-beste Tyrving i hovedgruppen (ikke maksimum → maks-av-n-skjevhet);
  k13/k15 som kontroller i alle modeller.
- Tyrving-skåringen gjenbruker den validerte `tyrving_r2` fra IJSSC-revisjonen.
- Volum = konkurransedager; standardiseres globalt. Prestasjonsvariabler standardiseres
  innen kjønn × hovedgruppe.
- Ingen eksponering–utfall-analyse før OSF-registrering; 03/04 har teknisk sperre.
- Tolkningsasymmetri forhåndsdefinert: nullfunn falsifiserer ikke mastery (idrettsbytte).

## PSE-versjon (31.10.2026)

`manus_pse/` inneholder innsendingsversjonen for *Psychology of Sport and Exercise* (Atles valg 31.10.2026 på grunn av publiseringsavgiftene i SMO/EJSS/SJMSS): anonymisert hovedfil med teorien i innledningen, APA 7, egen tittelside, supplement (S1–S3), highlights, følgebrev. Bygges fra det fryste manuset med `manus_pse/kompiler.sh`; `manus_pse/tallkontroll_pse.py` sikrer at ingen tall avviker. Se `manus_pse/ENDRINGER_PSE.md`.
