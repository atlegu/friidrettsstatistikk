# Kode- og datafrysing — A3 «Does starting age predict who stays?»

Fryst 30.10.2026 etter dataauditen (`DATA_AUDIT.md`) og omskrivingen. Herfra endres bare teksten i `manus/main.tex`, med mindre en verifisert feil krever en kodeendring.

## Hva er fryst

- **`FREEZE_code.sha256`:** `RUN_ALL.sh`, uttrekket (`00_uttrekk.py`, kjøres ikke), analysekjeden 01–06 med 05b, kontroll- og speilskriptene i `audit/` (Python og R) og den delte modulen `../audit_felles.py`.
- **`FREEZE_data.sha256`:** råuttrekket i `data_private/` (29.10.2026, se `uttrekksinfo.json`).

`RUN_ALL.sh` kontrollerer begge før noe kjøres, og stopper hvis en fil er endret eller hashfilene mangler. Avledede filer (`analysedata.csv`, `analysedata_ukjent_kjonn.csv`, `arsvolum.csv`, `flyt.json`) bygges på nytt ved hver kjøring. Kjeden er deterministisk: to kjøringer 30.10.2026 ga like hasher på alle utdata (tabeller, figurer, PDF, R-utdata og avledede data).

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
