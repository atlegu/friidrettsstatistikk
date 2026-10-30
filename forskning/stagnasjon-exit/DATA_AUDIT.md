# DATA_AUDIT — A1 «Stagnation before exit»

Audit startet 30.10.2026 etter `paper-data-audit`-skillen. Status: fase 0–1 ferdig; funn nederst.

## Fase 0 — Inventar

Alle data leses fra `data_private/` (frosset uttrekk 29.10.2026, 19:59–20:01 UTC, produsert av `00_uttrekk.py` mot Supabase `lwkykthpnthfcldifixg`). Levende base per uttrekksdato; `created_at`-filtre brukes ikke (gjenskaper ikke historiske tilstander — se uttrekksinfo.json).

| Fil | sha256 |
|---|---|
| analysedata.csv | 9da7a7c4c275a812b3ebdd584486f3b22b6d69a5463a2a066d4e12b10f1d2efa |
| clubs.csv | 156e04f08c1e0aeb25017daf051a3b0b6b2276f70c4a1f9d620514ac7da9b188 |
| events.csv | 17ba16a6b64f2765727b61b45f4ceb190b5c79f78bc5268d2514991f30e9405e |
| meets.csv | 56dbb1bdf7c70f8023020c7fb27c458758898e7af1d06400e487af0f640e6b24 |
| resultater.csv | 154079444763c25ee58fbefe5e99abaf674347f933f276ec87a13f6c4a772737 |
| resultater_raa.csv | 545811ef8710ef9e854e68713d6cbf6d29a58f1ea472adac72363ae29e98b23a |
| utovere.csv | c5aebc91ce62d807ab545177ba582ec72a3d97905e043031378c613a31d3cb7f |
| flyt.json | d517b4240a9c1c1ad0897ead9c9c99f7840178fe819ec2683c0988f9779c6a3d |
| uttrekksinfo.json | dae9b79e3fc999165276e1ff87cc1994c76898854b1315cedb8bcf9b1ace16bd |

**Fullstendighet mot kilden (kontrollert mot levende base 30.10.2026):** utøvere født 1998–2006: 32 447 = basen (eksakt). Resultater per kull fra året utøveren fylte 13 t.o.m. 29.10.2026: alle ni kull eksakt like basen (1998: 50 795 … 2006: 42 898; sum 493 532). Ingen drift siden frysing. clubs.csv/meets.csv har samme hash som A3s (samme uttrekksmåte).

**Dekning:** registeret elektronisk komplett fra 2011; eldste kull (1998) fyller 13 i 2011, så ingen venstresensur ved konstruksjon. Kull 2006 ekskludert fra primærutvalget (høyresensur på seniorutfallet); 2026 observert t.o.m. 29.10.

## Fase 1 — Kode mot metodetekst

| Sjekkliste | Koden (01_variabler.py) | Teksten | Status |
|---|---|---|---|
| Operasjonsrekkefølge | status=OK → vinduer → landmark → kjønn → Tyrving → celler<20 → z på primærutvalget | §2 i samme rekkefølge | OK |
| Tidsorigo | W1=13–14, W2=15–16 (kalenderårsalder) | lik | OK |
| Venstresensur | kull 1998 = 2011 ved 13 | «complete from 2011» | OK |
| Høyresensur | senior=≥2 res. samme kalenderår ved 20+; kull 2006 ute av primær; fast vindu 20–21 per kohorthalvdel som robusthet | lik (R2-6-svaret) | OK |
| Identitet | alle merger på unike nøkler; analysedata 4 909 rader = 4 909 unike athlete_id | — | OK |
| Enheter/kategorier | Tyrving kun elektronisk, i modal hovedgruppe; mean-av-3-beste (ikke maks); k13/k15 = antall skårbare merker per vindu | lik | OK |
| Volum | konkurransedager (nunique date), alle OK-resultater inkl. manuelle | lik | OK |
| Ugyldige verdier | manuell tid ute av skåring; vindugyldig-variant delta_vind | lik | OK |
| Standardiseringsceller | kjønn×hovedgruppe, celler<20 ekskludert FØR z; z-parametre fra primærutvalget | lik | OK |
| COVID | covid_w1 (kull 2006–07), covid_w2 (2004–06), robusthet | lik | OK |
| Parsing | birth_date coerce; Int64-kvartal | — | OK |
| **Region** | modal krets ved 13–14 — men meets.krets er utfylt for 415 av 44 971 stevner i basen → region = NA for alle 4 909, fillna «ukjent» = konstant → null dummier, null numerisk effekt | §2 hevder justering for «region (modal competition district at 13–14)»; tabellnote «adjust for birth cohort, region, and club size» | **FUNN A1-1** |

NA-mønsteret i analysedata stemmer med flyten (43 uten fødselsdato; 734 uten skårbar Tyrving; z-varianter med småcelle-NA). `delta_nk_1314` (negativkontroll) har 1 604 NA — utøvere uten skårbare merker i begge enkeltår; modellen bruker komplette rader.

## Funn

1. **A1-1 (tekst mot kode, må rettes):** «region»-kovariaten er vakuøs — kildefeltet (meets.krets) er tomt for 99,1 % av stevnene, og klubbtabellen har ingen geografi (county: 0 av 2 484). Konstant kovariat → fjerning endrer ingen estimater (verifiseres bit-eksakt i fase 3). Retting: fjern «region» fra kovariatlistene i §2 og tabellnoten; geografi står allerede som umålt begrensning. Ingen tall endres.
2. **A1-2 (info):** `region`-kolonnen i analysedata beholdes som runde 1-spor; R-reimplementasjonen estimerer uten den og reproduserer publiserte tall eksakt.
