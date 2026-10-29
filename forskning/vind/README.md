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

Python: `scraper/venv`. Data i `data_private/` (git-ignorert, regenererbart).

## Nøkkeldesign

- **Identifikasjon:** demeaning innen utøver × år × øvelse; måneds- og rundedummyer; klyngerobuste SE på utøver (stevne som robusthet); to-veis FE (celle + stevne) som robusthet via iterativ demeaning.
- **Effektmål:** gevinst per +1 m/s medvind i sekunder/cm og i prosent; estimater leses som nedre grenser pga. målefeil i vind (attenuering).
- **Etikk:** prestasjonsdata ved 10–12 brukes til å estimere målebetingelser, ikke til å rangere barn; ingen lister eller individnivåfunn under 13.
