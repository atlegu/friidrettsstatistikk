# Status — A1 «Stagnation before exit: performance progression and retention in youth track and field»

**Sist oppdatert:** 1. november 2026

## Hvor artikkelen står

| Dato | Hendelse |
|---|---|
| 29.10.2026 | Analyseplan committet før estimering; modeller, robusthet, figurer og førsteutkast (SMO-format) |
| 29.10.2026 | Simulert fagfellerunde 1 og revisjon (`manus/REFEREE_RUNDE1.md`, `manus/RESPONSE_PANEL1.md`) |
| 30.10.2026 | Full dataaudit (`DATA_AUDIT.md`), datafeil rettet i koden, teksten skrevet om, kode og data fryst (`FREEZE.md`) |
| 31.10.2026 | Tidsskrift byttet fra Sports Medicine – Open til *Psychology of Sport and Exercise* (Elsevier; NMBU har les-og-publiser-avtale ut 2027). PSE-versjonen bygget i `manus_pse/` |
| 01.11.2026 | Referansekontroll mot kildenes sammendrag (`manus_pse/REFERANSEKONTROLL.md`); åtte setninger rettet i både PSE- og SMO-versjonen; Enoksen (2011) lagt inn |
| **01.11.2026** | **Innsendt til Psychology of Sport and Exercise via Editorial Manager** |

Manuskriptnummer fra Editorial Manager: *(føres inn når bekreftelsen kommer)*

## Hva som ble sendt inn

Alt ligger i `manus_pse/` og bygges reproduserbart fra det fryste manuset med `kompiler.sh` og `lag_docx.py`:

- `main_anonymised.docx` — anonymisert manus, APA 7, om lag 7 400 ord uten sammendrag og referanser (oppgitt i skjemaet)
- `title_page.docx` — tittelside med forfatter, ORCID, erklæringer, CRediT og ordtelling
- `abstract.docx` (247 ord), `highlights.docx`, `cover_letter.docx` (datert Ås, 1. november 2026), `declaration_of_interests.docx`
- `supplement.docx` — tabell S1 (flyt), S2 (robusthet, tidligere tabell 4) og S3 (planavvik)
- `strobe_checklist.docx`
- `figurer_opplasting/Figure_1.png`–`Figure_4.png` (300 dpi), lastet opp enkeltvis

KI-erklæringen oppgir Anthropic Claude (Claude Opus 5.5) til språk, struktur og kodekontroll (Atles egen tekst). Sikt er oppgitt uten referansenummer (Atles beslutning).

## Kontroller som var grønne ved innsending

- `RUN_ALL.sh` med frysingskontroll av kode og data
- `audit/kontroll_tall.py`: 148 sjekker OK, 0 feil, ingen udekkede tall i det fryste manuset
- `manus_pse/tallkontroll_pse.py`: alle tall i PSE-versjonen finnes i det fryste manuset eller tabellene (unntak bare for styrkeberegningen, se hviteliste i skriptet)
- Referanser CrossRef-verifisert (29.10 og 01.11)

## Hovedresultater (etter audit 30.10.2026)

- Primærutvalg 3 877 utøvere, 654 aktive seniorer
- H1 støttet: fremgang 13–14 → 15–16 gir OR 2,24 per SD [1,90–2,63] for seniorstatus, utover nivå, volum og struktur
- H2 ikke støttet: ingen interaksjon med fødselskvartal; fremgangen beskytter i begge strata
- H3: gitt volum diskriminerer fremgang og nivå likt
- Konklusjonen er at lav fremgang følger og går foran exit («Low progression accompanies and precedes exit»)

## Når svaret kommer

- Revisjon gjøres i teksten i `manus/main.tex` og `manus_pse/bygg_pse.py`; kode og data endres bare for en verifisert feil (loggføres i `FREEZE.md`)
- Kjør `audit/kontroll_tall.py` og `manus_pse/tallkontroll_pse.py` til grønt etter hver tekstendring
- Ved aksept: kode deponeres offentlig med DOI (lovet i manuset); upubliserte følgestudier (JSAMS 2026a, IJSSC-manus 2026b, RAE in press) oppdateres med endelige referanser

## Sideløpende

- SMO-versjonen (`manus/main.tex`) holdes i takt med PSE-versjonen tekstlig, men er ikke sendt inn
- A3 (debutalder) er anbefalt sendt til J Sports Sci, IJSSC eller ESMQ, ikke PSE
