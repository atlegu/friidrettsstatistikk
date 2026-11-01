# A2 — Søk og match innen friidrett

Tester søk-og-match-mekanismen (Gøran-notatets test 1, med test 2 som tillegg): bytter utøverne
mot den øvelsesgruppen der de alt var relativt best ved 13–14, og følges byttet av fremgang?
Full plan i [ANALYSEPLAN.md](ANALYSEPLAN.md); engelsk forhåndsregistreringstekst i
[OSF_PREREGISTRATION.md](OSF_PREREGISTRATION.md).

## Status

| Dato | Hendelse |
|---|---|
| 01.11.2026 | Analyseplan v1 og OSF-utkast skrevet. **Ingenting er kjørt.** |

## Før noe kjøres

1. Avtal rammen med Gøran (medforfatterskap, tilknytning, hvem gjør hva).
2. Beslutt OSF-registrering (anbefalt i planen; A1 og A3 ble ikke registrert eksternt).
3. Skriv OSF-teksten ferdig og registrer. Deretter `FRIGITT_FOR_MODELLERING.txt` som i A1.
4. Start etter at revisjonene på A1 (PSE) og A3 (JSAMS) er besvart.

## Data og kode

Bruker A1s fryste uttrekk (`../stagnasjon-exit/data_private/`, 29.10.2026) og A1s Tyrving-skåring
(`../stagnasjon-exit/a1_tyrving.py`, `../ncc-kohort/revision_r1/analysis/tyrving_r2.py`). Nytt uttrekk
tas ikke. Planlagte skript: `01_variabler.py`, `02_deskriptiv.py`, `03_modeller.py`, `04_robusthet.py`,
`05_figurer_tabeller.py`, `RUN_ALL.sh`, `audit/kontroll_tall.py` — samme regime som A1/A3 (teknisk sperre
før eksponering–utfall-modeller, frysing, tallkontroll, R-speil).
