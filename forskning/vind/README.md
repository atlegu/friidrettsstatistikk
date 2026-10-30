# A6 — Vindeffekten etter alder, kjønn og nivå

Within utøver × sesong-estimering av hva vinden er verdt i sprint og
horisontale hopp, over hele alders- (10–34) og nivåspennet — det eksisterende
vindlitteraturen bare dekker for gode seniorer. Full plan i
[ANALYSEPLAN.md](ANALYSEPLAN.md) (committet før estimering, 506a82a).

## Kjørerekkefølge

| Steg | Skript | Innhold |
|---|---|---|
| 0 | `00_uttrekk.py` | Frosset uttrekk: ni vindøvelser, alle rader 2011→ (per øvelse × år mot Postgres-timeout) |
| 1 | `01_variabler.py` | Filtre med flyt, enhetsautodeteksjon, celler (utøver × år × øvelse), nivå-z, aldersbånd |
| 2 | `02_deskriptiv.py` | Heaping (0,0-andel, hele m/s), dekning per øvelse × år, celletellinger |
| 3 | `03_estimering.py` | Hovedeffekter, alder × kjønn-skalering, nivåtertiler, asymmetri, kvadratisk, robusthet (inkl. to-veis FE), +2,0 m/s-fordelen |
| 4 | `04_figurer_tabeller.py` | β(alder)-figuren, asymmetri, nivå, manustabeller |
| 0b | `00b_uttrekk_hekk.py` | Tillegg 29.10 (Atles forespørsel): ti korthekk-koder med vinddata |
| 5 | `05_hekk.py` | Hekkestimering per kode (= per klassespesifikasjon) + fig5 med flat sprint-referanse |
| 7–10 | `07_revisjon_r1.py`, `07b_revisjon_r2.py`, `08_r1_figurer_tabeller.py`, `09_r1_supptex.py`, `10_eiv_kalibrering.py` | Revisjons- og auditanalysene (stevneklynget, drag-referanse, H5 med robust skala, Lybbert & Zheng-testen, EIV), figurer og alle tabeller som LaTeX |
| 11 | `11_eliteende.py` | Tillegg 30.10 (Atles beslutning): eliteenden med samme estimator — TFRRS (fellesbyggingen `Covid/tfrrs_shared` v1.2) og Tilastopaja-finalistene (`2026Host/Idrettsanlyser/Alder`), norske referanserader; tabell S8. Inndataene hash-kontrolleres mot `eliteende_input.sha256`; speilet i R (`audit/uavhengig.R`) |

Hele kjeden med frysekontroll, LaTeX, R-speil og tallkontroll: `bash RUN_ALL.sh` (se `FREEZE.md`).

Python: `scraper/venv`. Data i `data_private/` (git-ignorert, regenererbart). Tilastopaja-radene i `data_private/eliteende_analyseklar.csv` er utøvernivådata som ikke kan deles videre; bruk i A6 krever Tilastopaja Oys tillatelse (se `DATA_AUDIT.md`).

## Nøkkeldesign

- **Identifikasjon:** demeaning innen utøver × år × øvelse; måneds- og rundedummyer; klyngerobuste SE på utøver (stevne som robusthet); to-veis FE (celle + stevne) som robusthet via iterativ demeaning.
- **Effektmål:** gevinst per +1 m/s medvind i sekunder/cm og i prosent; estimater leses som nedre grenser pga. målefeil i vind (attenuering).
- **Etikk:** prestasjonsdata ved 10–12 brukes til å estimere målebetingelser, ikke til å rangere barn; ingen lister eller individnivåfunn under 13.
