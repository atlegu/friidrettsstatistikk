# Sonehopp lagret to ganger: tørrkjøring 30.10.2026

**Ingenting er slettet.** Tallene under er fra tørrkjøringen
(`python rydd_kryssdubletter.py --kartlegg`, logg `logs/rydd_kryssdubletter_20261030_102916.log`).
Ryddingen kjøres først når Atle har sagt ja.

## Kort fortalt

- **56 931 brettrader** i lengde og tresteg er kopier av et sonehopp som alt ligger i basen under
  `lengde_sone_05m`/`tresteg_sone_05m`. 99,7 % gjelder 11–13-åringer, i alle år 2010–2025.
- Sonerakene kom inn i januar 2026 fra kildens utøversider. Senere importer oversatte
  «Lengde (Sone 0,5m)» til `lengde` og sjekket dubletter bare innen én øvelseskode, så hoppet kom
  inn en gang til under brettkoden. Kilden viser hoppene bare under sonen.
- Roten er rettet og committet: importene gir nå sonekoden, og de legger ikke inn et resultat som
  alt ligger under en beslektet kode (`kodegrupper.py`). Kontrollen er
  `python test_fullstendighet.py --bare kryssdubletter`.
- Forslaget er å slette brettraden og beholde sonen, med reserve som kan legges tilbake.

## Det Atle må ta stilling til

| | Regel | Rader | Kommando |
|---|---|---:|---|
| 1 | **Samme dato**: sonen har samme utøver, dato, resultat og vind. Samme regel som `forskning/rens_felles.py`. | 48 085 | `python rydd_kryssdubletter.py --apply --regel samme_dato` |
| 2 | **Flerdagsstevner**: brettraden har stevnets startdato, sonen ligger 1–6 dager senere i en søskenpost (samme navn uten sted foran, eller samme sted). Ikke med i forskningsregelen. | 8 846 | `python rydd_kryssdubletter.py --apply --regel flerdagsstevne` |
| | Begge | 56 931 | `python rydd_kryssdubletter.py --apply` |

I tillegg blir **81 stevneposter tomme** (bare kopier i dem). De lagres i
`opprydding_kryssposter` og slettes. Fire av dem har kildens stevne-id og får et alias til posten med
sonehoppene, slik at importen ikke oppretter dem på nytt.

## Antall per kodepar og år

Året er konkurranseåret. 2010 er innendørssesongen 2010/11.

| År | Lengde, samme dato | Tresteg, samme dato | Lengde, flerdagsstevne | Tresteg, flerdagsstevne | Sum |
|---|---:|---:|---:|---:|---:|
| 2010 | 126 | 0 | 0 | 0 | 126 |
| 2011 | 1 744 | 137 | 0 | 0 | 1 881 |
| 2012 | 3 171 | 328 | 544 | 123 | 4 166 |
| 2013 | 3 737 | 453 | 571 | 164 | 4 925 |
| 2014 | 3 733 | 401 | 553 | 153 | 4 840 |
| 2015 | 3 681 | 438 | 573 | 153 | 4 845 |
| 2016 | 3 865 | 511 | 606 | 186 | 5 168 |
| 2017 | 3 550 | 527 | 578 | 177 | 4 832 |
| 2018 | 3 335 | 473 | 523 | 170 | 4 501 |
| 2019 | 3 321 | 436 | 517 | 132 | 4 406 |
| 2020 | 2 395 | 311 | 153 | 131 | 2 990 |
| 2021 | 2 174 | 231 | 218 | 87 | 2 710 |
| 2022 | 2 392 | 336 | 454 | 166 | 3 348 |
| 2023 | 2 229 | 308 | 446 | 126 | 3 109 |
| 2024 | 1 920 | 230 | 515 | 178 | 2 843 |
| 2025 | 1 421 | 149 | 465 | 183 | 2 218 |
| 2026 | 20 | 2 | 1 | 0 | 23 |
| **Sum** | **42 814** | **5 271** | **6 717** | **2 129** | **56 931** |

Alle tall per år står i `kryssdubletter_20261030_102916.csv`. Forskningsauditen talte 47 962 i
sitt uttrekk; den levende basen har 48 085 etter samme regel. For 2016 er tallet likt: 3 865.

Andre kjennetegn ved samme-dato-regelen: 44 358 av kopiene (92 %) ligger i samme stevnepost som
sonen, og 3 727 i en annen post (oftest poster ungdomsimporten laget, som «PEAB-lekene»/Osterøy).
Åtte sonerader har to kopier hver. Ingen av kopiene er koblet til mastersrekorder, avvikslisten eller
rekordflagg.

## Hvor kopiene kom fra

| Importdag | Importvei | Kopier |
|---|---|---:|
| 13.02.2026 | `update_results.py` (første versjon) | 7 |
| 14.02.2026 | `import_historical.py`, alle tiders-listene fra friidrett.no. De skiller ikke sone fra brett. | 117 |
| 19.05.2026 | `import_youth_stats.py`, kildens statistikklister for 10–12 år | 27 752 |
| 22.08.2026 | `update_results.py --verify`, innendørs 2026 | 3 |
| 24.08–06.09.2026 | `update_results.py --verify`, historiske sesonger | 29 052 |

Både `update_results.py` og `import_youth_stats.py` hadde `'Lengde (Sone 0,5m)': 'lengde'` i
oversettelsestabellen. I flerdagsstevner ga augustimporten alle resultater startdatoen og la dem i
posten med kildens stevne-id, mens sonehoppet fra januar ligger i dagsposten med riktig dato. Det er
samme mekanisme som i ryddingen 03.10.2026, men på tvers av koder, og derfor fant den ikke disse.

## Kontroll mot kilden

Kildens utøversider ligger hurtiglagret i `logs/kilde_utover/` (547 sider med sonehopp).

- **Samme dato, kopi og sone i ulike poster** (den mest usikre gruppen): 14 av 14 tilfeldig valgte
  står i kilden bare under «Lengde/Tresteg (Sone 0,5m)» på samme dato, og ikke som brett.
  Forskningsauditen kontrollerte 10 fra samme post: 9 bekreftet, det tiende manglet vind i kilden.
- **Flerdagsstevner**: 12 av 12 står i kilden bare under sonen, på den senere datoen. Ingen brettrad
  på startdatoen.

## Hva ryddingen gjør

- Brettraden slettes og lagres i `opprydding_kryssdubletter` med `beholdt_id` (sonen), `kodepar` og
  `regel`. Den kan legges tilbake med en `insert ... select` av kolonnene fra `results`.
- Plassen kopieres til sonen der sonen mangler den og radene ligger i samme post (om lag 8 200 rader;
  kopien kom fra kildens resultatside, så plassen gjelder sonehoppet).
- Tomme stevneposter lagres i `opprydding_kryssposter` og slettes; fire får alias.
- Forsidetallene oppdateres (`refresh_plattform_statistikk`).
- Etterpå skal `python test_fullstendighet.py --bare kryssdubletter` gi 0. I dag melder den
  42 814 / 5 271 / 6 717 / 2 129.

## Andre kodepar med samme mønster (ikke med i ryddingen)

Samme utøver, dato, resultat og vind under to koder, i hele basen. Dette er samme øvelse under to
koder: januarimporten laget koden av kildenavnet, de andre importene brukte koden i
oversettelsestabellen. Her må det først avgjøres hvilken kode som gjelder, og helst slås kodene
sammen. Importene stopper nye kopier for alle parene.

| Kodepar | Rader | Nyeste rad under | År |
|---|---:|---|---|
| `slegge_20kg/110cm` / `slegge_2kg` | 1 356 | `slegge_2kg` | 2011–2025 |
| `3000mhinder` / `3000mhinder_91_4cm` | 977 | `3000mhinder` | 1950–2013 |
| `3000mg` / `kappgang_3000_m` | 339 | `3000mg` | 2012–2025 |
| `1000mg` / `kappgang_1000_m` | 238 | `1000mg` | 2012–2025 |
| `3000mhinder` / `3000mhinder_76_2cm` | 113 | `3000mhinder` | 2000–2013 |
| `1500mg` / `kappgang_1500_m` | 60 | `1500mg` | 2012–2025 |
| `80_m_h_840cm/85m` / `80mh_84cm` | 29 | `80mh_84cm` | 2015 |
| `2000mg` / `kappgang_2000_m` | 23 | `2000mg` | 2012–2025 |
| `1_mile` / `1mile` | 21 | begge | 1962–2022 |
| `7_k` / full sjukampkode (sju koder) | 132 | `7_k` | 2012–2025 |
| `10_k` / full tikampkode (fire koder) | 91 | `10_k` | 2022–2025 |

Kappgangkopiene kom inn 24.08–06.09.2026 (`update_results.py` gir `1000mg`), mens
`import_youth_stats.py` fortsatt gir `kappgang_1000_m`. De to importveiene er altså uenige om koden.
80 m hekk-parene er begge fra januar. Mangekamp: `get_event_id()` faller tilbake til den generelle
koden når klassen ikke finnes. De fulle mangekampkodene står dessuten med resultattypen «distance»,
ikke «points». Par med under ti rader i kartleggingen (`kryssdubletter_kart_*.csv`) er stort sett
tilfeldig like verdier (diskos/spyd), men to hekkepar fra september er ekte: kilden rettet
hekkehøyden, og importen la inn en ny rad under den nye koden ved siden av den gamle.

## Funn utenfor ryddingen: 2026-sesongen

Fra februar 2026 la `update_results.py` alle nye sonehopp under `lengde`/`tresteg`. Det er ikke
kopier, men feil kode: `lengde_sone_05m` har 35 rader i 2026 mot 2 380 i 2025. Etter rettingen
kommer nye sonehopp under sonekoden, men 2026-hoppene fra februar til oktober ligger fortsatt under
brettkoden. Hvilke det gjelder, kan bare avgjøres mot kilden. Når nattjobben henter et stevne på
nytt, legger sperren ikke inn sonehoppet en gang til. Brettraden kan da få `verified = false`, fordi
kilden ikke har den under brettkoden. Å flytte 2026-hoppene til sonekoden er en egen beslutning.

## Analyser som kan være berørt

Analyser som har brukt basen etter 19.05.2026 med lengde eller tresteg for 11–13-åringer har
kopiene: RAE-revisjonen, Lekene-trend, fagnytt og trenerartikkelen. Regelen i
`forskning/rens_felles.py` fjerner bare samme-dato-kopiene; de 8 846 i flerdagsstevner er fortsatt
med i A1/A6-dataene. Ingen av dem er endret her.

## Etter Atles ja

1. Kjør ryddingen med regelen eller reglene han godkjenner, og deretter
   `python test_fullstendighet.py --bare kryssdubletter`.
2. Legg `kryssdubletter` til i `--bare`-listen i `.github/workflows/oppdater.yml`.
3. Sperren virker i nattkjøringen først når endringene er pushet.
