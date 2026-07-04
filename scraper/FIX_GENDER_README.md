# Kjønnsdata — status og historikk

## Status per 4. juli 2026: OPPRYDDET ✅

- **M = 47 859, F = 37 508, NULL = 2 273** (av 87 640 utøvere)
- Kvinnelistene er verifisert rene (100m, 5000m alle-tiders)
- Full detalj: se `OPERATIONS_LOG.md` (2026-07-03/04)

## Hvordan kjønn ble satt (autoritativ rekkefølge)

1. **Klassebevis fra kilden** (`fix_gender_from_source.py`): Stevnesidene på
   minfriidrettsstatistikk.info har klasseoverskrift per øvelse ("Gutter 15",
   "Kvinner Senior"). Bevis aggregert per (navn, fødselsår) over 8 437 stevner
   2013–2026 → 671 000 bevisrader. Kjønn satt kun ved konsistente bevis.
   Bevisfilene ligger i `new_meets_data/gender_evidence_*.jsonl.gz` og kan
   gjenbrukes (f.eks. til aldersklasse-backfill) uten ny scraping.
2. **Fornavnsklassifisering** (`fix_gender_by_firstname.py`): For 10–12-åringene,
   som IKKE vises med klasse på kildens stevnesider (barneidrettsbestemmelsene —
   ingen nasjonal statistikk under 13 år). Trent på klassebevisene + kjente
   utøvere. Leave-one-out-validering: 99,76 %. Terskler: ≥5 obs / ≥98 %, eller
   ≥3 obs / 100 %.
3. **Løpende backfill** (`update_results.py`): `match_athlete()` setter nå kjønn
   på eksisterende NULL-utøvere når importen har autoritativt klasse-kjønn.

## Restanser

- **2 273 utøvere med NULL** — sjeldne/utenlandske fornavn der klassifisereren
  avstår. Liste: `logs/fix_gender_by_firstname_report_*.json` (`unresolved`).
  Manuell gjennomgang eller vent til de dukker opp i 13+-klasse.
- **42 svake motsigelser** (DB-kjønn vs. blandet klassebevis) — samme rapport.

## Viktige regler (lærdom fra januar 2026-korrupsjonen)

- **ALDRI infer kjønn fra medkonkurrenter i samme heat** — mixed heats gjorde at
  `fix_missing_gender_batch.py` (jan 2026) ødela tusenvis av rader. Korrupsjonen
  ble nullstilt i februar 2026 og re-utledet autoritativt i juli 2026.
- Kjønn settes KUN via: (a) klasseoverskrift for utøverens eget resultat,
  (b) fornavnsklassifisering med validerte terskler, (c) manuelt.
- Kildens utøversider/utøversøk viser IKKE kjønn — bare stevnesidenes
  klasseoverskrifter gjør det (og kun for 13 år og eldre).

## Historikk

- **Jan 2026:** `fix_missing_gender_batch.py` infererte kjønn fra heats → tusenvis
  feil (menn i kvinnelister). IKKE KJØR de gamle fix_missing_gender-scriptene.
- **Feb 2026:** Korrupte rader nullstilt → ~30 000 NULL.
- **Jul 2026:** Autoritativ re-utledning (denne oppryddingen). NULL: 30 217 → 2 273.
