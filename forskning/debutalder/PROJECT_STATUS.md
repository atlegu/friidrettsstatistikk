# Status — A3 «Does starting age predict who stays? Competition debut and long-term participation in youth track and field»

**Sist oppdatert:** 1. november 2026

## Hvor artikkelen står

| Dato | Hendelse |
|---|---|
| 29.10.2026 | Analyseplan committet før estimering; modeller, figurer, tabeller og førsteutkast i SJMSS-format |
| 29.10.2026 | Simulert fagfellerunde 1 og revisjon (`manus/REFEREE_RUNDE1.md`, `manus/RESPONSE_PANEL1.md`) |
| 30.10.2026 | Full dataaudit (`DATA_AUDIT.md`), tekst skrevet om, kode og data fryst (`FREEZE.md`) |
| 01.11.2026 | Referansekontroll mot sammendrag og fulltekster (`manus/REFERANSEKONTROLL.md`); Espedalen rettet fra «oversikt» til spørreundersøkelse, fire overdrivelser presisert |
| 01.11.2026 | Tidsskriftvurdering (`TIDSSKRIFTVURDERING_2026-11-01.md`): JSAMS valgt (Elsevier-avtale ut 2027, nivå 2 fra 2027) |
| 01.11.2026 | JSAMS-versjon bygget i `manus_jsams/`; tankestreker fjernet og resultatdelen tynnet for tall i det fryste manuset (begge versjoner) |
| **01.11.2026** | **Innsendt til Journal of Science and Medicine in Sport via Editorial Manager** (Original Research, Physical Activity & Public Health; klassifisering Physical activity) |

Manuskriptnummer fra Editorial Manager: *(føres inn når bekreftelsen kommer)*

## Hva som ble sendt inn

Alt ligger i `manus_jsams/` og bygges fra det fryste manuset med `kompiler.sh`, `tallkontroll_jsams.py` og `python3 lag_docx.py`:

- `main_anonymised.docx` — anonymisert manus, 4 497 ord hovedtekst, strukturert sammendrag 239 ord, 2 tabeller + 4 figurer, 11 referanser i Vancouver med DOI
- `title_page.docx`, `cover_letter.docx` (datert Ås, 1 November 2026)
- `declaration_of_interests.docx`, `acknowledgement_funding_ethics.docx`, `credit_author_statement.docx`
- `supplement.docx` (tabell S1–S5) og `strobe_checklist.docx`, lastet opp som e-Component
- `figurer_opplasting/Figure_1–4.tiff`, lastet opp enkeltvis

Upubliserte følgestudier (frafall i IJSSC, A1 i PSE) omtales i teksten som «unpublished data», slik JSAMS krever; RAE-artikkelen (in press, SMO) står i listen.

## Kontroller som var grønne ved innsending

- `audit/kontroll_tall.py`: 131 sjekker OK, 0 feil, ingen udekkede tall (etter tynningen; kontrollskriptet oppdatert og logget i `FREEZE.md`)
- `manus_jsams/tallkontroll_jsams.py`: alle tall i JSAMS-versjonen finnes i det fryste manuset eller tabellene
- Alle DOI-er CrossRef-verifisert 01.11.2026

## Hovedresultater

- 17 496 debutanter født 2001–2005, 546 (3,1 %) aktive seniorer
- U-form i konvertering: OR 0,53–0,75 for debut 11–14 mot debut 10, 1,00 ved 15; lineær trend null (0,99 per år)
- Ved lik karrierelengde fortsetter senere debutanter mindre: 20,4 % mot 4,5–6,6 %, OR 0,70 per år
- Landmark ved 17: 0,85 per år uten, 0,99 med nåværende konkurransevolum («nåtilstand slår historie»)

## Når svaret kommer

- Revisjon gjøres i teksten i `manus/main.tex` og i `manus_jsams/bygg_jsams.py`; kode og data endres bare for en verifisert feil (loggføres i `FREEZE.md`)
- Kjør `audit/kontroll_tall.py` og `manus_jsams/tallkontroll_jsams.py` til grønt etter hver tekstendring
- Ved aksept: kode deponeres offentlig med DOI; følgestudiene oppdateres med endelige referanser

## Sideløpende

- SJMSS-versjonen i `manus/` holdes i takt tekstlig, men er ikke sendt inn
