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
| 30.10.2026 | `05b_revisjon_r2.py`, `04_figurer_tabeller.py`, `06_manustabeller.py`, `RUN_ALL.sh`, `audit/uavhengig.R`, `audit/sammenlign.py`, `audit/kontroll_tall.py` | Atles beslutning («Gjør det andre»; endringsrapporten avsnitt 8, punkt 1, og formkravene). (1) **Debut-16-armen:** Alle 107 debut-16-utøvere i kull 2004–2005 debuterte i 2020–2021. Den kategoriske kontrasten regnes uten koronadebuter, med koronaflagg og per kohorthalvdel; LRT uten koronadebuter og per halvdel; konvertering ved debut 16 etter koronastatus (05b, tabell 4 i 06, speilet i R). (2) **Figurfilene** får trykkrekkefølgens nummer: `fig4_retention_k` → `fig3_retention_k` (04), `fig3_shares_by_age` → `fig4_shares_by_age` (05b). (3) **Supplementet** (S1–S4) flyttes til egen fil `manus/supplement.tex`, fordi SJMSS vil ha Supporting Information i egne filer og grensen er 8 visningselementer. S2 og S3 bytter nummer etter første sitering (06). RUN_ALL bygger også supplementet, og kontrollen sjekker begge filene. (4) Sammendraget kortes til høyst 250 ord, og ankrene følger den nye ordlyden. | Nye rader i tabell 4 og ny tekst om debut 16; ingen eksisterende tall endres |
| 30.10.2026 | `audit/kontroll_tall.py` | Siste smale gjennomgang: ordlyd rettet der den var usann eller sa mer enn tallene (B2–B7, C2–C4, C7), og ankrene følger den nye ordlyden. Nye kontrollpåstander: Q4 under 25 % ved hver debutalder, 2008-kullet mistet nesten halvparten av 12-årsdebutene, det relative gapet øker fra k = 1 til k = 5, nedgangen ved lik karrierelengde stanser etter 14, og U-formen i rå konvertering for begge kjønn. Lifelines er tatt ut av programvarelisten (ingen overlevelsesmodell rapporteres). | Ingen tall endres |
| 30.10.2026 | `audit/kontroll_tall.py` | Atles beskjed: Sikt er godkjent som tidligere, og datatilgangen skal være som i de andre artiklene på disse dataene. Etikk- og datatilgangssetningene følger nå dropout-artikkelen (IJSSC R1): ikke helseforskning etter helseforskningsloven §§ 2 og 4, Sikt har bekreftet at bruken ikke reiser personvernspørsmål, analysedatasettet deles ikke (GDPR), og koden deponeres ved aksept. Aldersklassene 10–12 er ikke offentlige, og det står i datatilgangen. Kontrollen har fått unntak for paragrafhenvisningen. | Ingen tall endres; ordtellingen på tittelsiden er oppdatert |
