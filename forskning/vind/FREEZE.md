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
