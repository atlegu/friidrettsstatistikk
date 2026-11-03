# A3 — Debutalder og varig deltakelse

Tester «startalder-strengen» i spesialiseringsdebatten på populasjonsdata:
predikerer alderen ved første registrerte konkurranse (10–16) hvem som
fortsatt er aktiv som senior — og i hvilken retning? Van Yperen m.fl. (2022,
fotball) fant at frafallerne hadde begynt *senere*; spesialiserings­linjen
antar det motsatte. Ren deltakelsesstudie — ingen prestasjonsvariabler.

Full plan i [ANALYSEPLAN.md](ANALYSEPLAN.md) (committet før estimering, b2b717a).

## Kjørerekkefølge

| Steg | Skript | Innhold |
|---|---|---|
| 0 | `00_uttrekk.py` | Frosset uttrekk: født 2001–2008, alle OK-resultater 2011→, kun deltakelsesfelter |
| 1 | `01_variabler.py` | Debutalder, utfall, sensur, region/klubb, årsvolum |
| 2 | `02_deskriptiv.py` | Eksponeringssiden: debutfordeling, kvartal, debutvolum |
| 3 | `03_modeller.py` | H1 (logit, kategorisk + trend), H2 (alders-Cox med forsinket inntreden), H3 (landmark 17), robusthet, retention-k |
| 4 | `04_figurer_tabeller.py` | Fire figurer + fire manustabeller (engelsk) |

Python: `scraper/venv`. Data i `data_private/` (git-ignorert, regenererbart).

## Nøkkeldesign

- **Debut = første godkjente resultat**, alder ≥10 (kalenderår). Register komplett fra 2011 → ingen venstretrunkering for født 2001+. Konkurransedebut ≠ idrettsstart — står i tolkningsreglene.
- **Primærutvalg:** født 2001–2005 (full oppfølging til 20+), debut 10–16.
- **H2 bruker alder som tidsskala med inntreden ved debut** — håndterer at sene debutanter ikke kan falle fra før de har begynt.
- **Ingen nivådata brukes overhodet** (barneidrettsbestemmelsene; studien trenger dem ikke).
- Måltidsskrift: Scandinavian Journal of Medicine & Science in Sports / EJSS.

## Brief Report (03.11.2026)

Etter redaktøravvisningen (JSAMS-D-26-02238, «a brief report seems possible») er en Brief Report-versjon bygget i `manus_jsams_brief/`: 1 319 ord, én tabell og én figur, resten i supplementet. `kontroll_brief.py` sjekker tall mot det fryste manuset og JSAMS' grenser. Se `manus_jsams_brief/ENDRINGER_BRIEF.md`.
