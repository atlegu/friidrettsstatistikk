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
| — | **OSF-registrering** | Oversett/registrer OSF_PREREGISTRATION.md; legg URL i `OSF_REGISTRERT.txt` |
| 3 | `03_modeller.py --post-registration` | **Sperret** til markørfilen finnes |
| 4 | `04_robusthet.py --post-registration` | **Sperret** til markørfilen finnes |

`RUN_ALL.sh` kjører steg 0–2. Python: `scraper/venv` (pandas, statsmodels, sklearn, lifelines).

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
