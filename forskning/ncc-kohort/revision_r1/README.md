# IJSSC revision R1 (SPO-26-1604) — working folder

Decision 1 Oct 2026: revise (one reviewer, 15 comments). Everything for the revision lives here; the original
submission in `../submission_pse/` (main checkout) is untouched. The original pipeline in `../data/` (main
checkout) is read-only; athlete-level files are in `data_private/`, `_rebuild/` and `_rerun/` (git-ignored, GDPR).

## Data audit (2 Oct 2026)

`audit/` holds the audit of the original data pipeline (extraction, cohort definition, Tyrving formulas), and
`analysis/r1_00_corrected_data.py` rebuilds the cohort, career and analysis data with every correction
(listed in its docstring and in Supplementary Methods S-M12). Summary of the rebuild: `audit/r1_00_summary.csv`.

- `audit/audit_01_reextract.py` — deterministic re-extraction (order by id, rows created ≤ 2026-05-18)
- `audit/audit_02_compare_extracts.py` — original vs. re-extracted data; re-derives 07's variables
- `audit/audit_03_tyrving.py` — validates `tyrving_r2.py` against LibreOffice-recomputed copies of the workbook
- `audit/audit_04_cohort_membership.py` — venue-and-date identification of the baseline meet vs. the cohort

## Run order (Python: scraper/venv)

0. `analysis/r1_00_corrected_data.py` — corrected `kohort`, `karrieredata`, `analysedata` in
   `data_private/corrected/` (needs `data_private/audit_reextract.csv` from audit_01; runs a patched copy of
   data/07 in `_rebuild/`)
1. `analysis/r1_01_build_variables.py` — HHI from ages 13–14; exact Tyrving scoring (`tyrving_r2.py`);
   within-event percentile at the baseline meet
2. `analysis/r1_02_rerun_original_scripts.py` — re-runs data/08–16 in a sandbox on the corrected data
   (the same sandbox with the original data reproduces every submitted table byte-for-byte)
3. `analysis/r1_03_reviewer_analyses.py` — new analyses for comments 1–14 and the audit (CV procedures, AUC
   differences, MI, unknown sex, birth quarter, change models, fixed-effects event study, thresholds,
   gaps/returns, correctly timed Cox and landmark models, club-robust models, target population, Table 7,
   HHI stress tests, Figure S1) → `tables/r1_results.json`
   (needs `data_private/register_population_freq.csv`, from `analysis/register_population.sql`)
4. `analysis/r1_04_text_numbers.py` — correlations, quartile table, zone-jump sensitivity, event-group means
5. `analysis/r1_05_figures.py` — Figures 1–3 and S0, S2–S4 from the corrected data (S1, S5 from r1_03)
6. `analysis/r1_06_tables.py` — writes `manuscript/11_tables.md` from the result files; every count in the
   notes is computed; changed cells and changed words in titles and notes are highlighted
7. `manuscript/build_r1.py` — highlighted and clean Word files in `submission_r1/`

Shared paths are in `analysis/r1_paths.py`. Changed text in the section files is wrapped in `{+ ... +}`; the
build prints it in blue (highlighted version) or strips the markers (clean version).

## Deliverables (`submission_r1/`)

- `MANUSCRIPT_R1_highlighted.docx` (changes in blue, as the editor requested) and `MANUSCRIPT_R1_clean.docx`
- `SUPPLEMENT_R1_highlighted.docx` / `SUPPLEMENT_R1_clean.docx` (methods, Tables S1–S32, Figures S0–S5)
- `RESPONSE_TO_REVIEWER_R1.docx` / `.txt` (paste into the ScholarOne response box)
- `figures/` (main Figures 1–3 and supplementary S0–S5, 300 dpi)
- `../REVISION_TRACKING_R1.md` (comment-by-comment ledger, including the audit corrections)
