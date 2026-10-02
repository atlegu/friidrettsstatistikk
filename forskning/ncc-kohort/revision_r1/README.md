# IJSSC revision R1 (SPO-26-1604) — working folder

Decision 1 Oct 2026: revise (one reviewer, 15 comments). Everything for the revision lives here; the original
submission in `../submission_pse/` (main checkout) is untouched. Data are read from `../data/` in the main
checkout (read-only); athlete-level files are in `data_private/` and `_rerun/` (git-ignored, GDPR).

## Run order (Python: scraper/venv)

1. `analysis/r1_01_build_variables.py` — HHI from ages 13–14; corrected Tyrving scoring (`tyrving_r1.py`)
2. `analysis/r1_02_rerun_original_scripts.py` — re-runs data/08–16 unchanged in a sandbox with the corrected
   variables (the same sandbox with the original data reproduces every submitted table byte-for-byte)
3. `analysis/r1_03_reviewer_analyses.py` — new analyses for comments 1–14 (CV procedures, AUC differences,
   MI, unknown sex, birth quarter, change models, fixed-effects event study, threshold validation,
   gaps/returns, target population, Table 7, HHI stress tests) → `tables/r1_results.json`
   (needs `data_private/register_population_1998_2002.csv`, extracted from Supabase 2026-10-01)
4. `analysis/r1_04_text_numbers.py` — correlations and quartile table quoted in Section 3.6
5. `analysis/r1_05_figures.py` — Figure 1 (SDT box replaced), S0, S4 (from table), S5; copies unchanged figures
6. `analysis/r1_06_tables.py` — writes `manuscript/11_tables.md` from the CSVs, highlighting changed cells
7. `manuscript/build_r1.py` — highlighted and clean Word files in `submission_r1/`

Changed text in the section files is wrapped in `{+ ... +}`; the build prints it in blue (highlighted
version) or strips the markers (clean version).

## Deliverables (`submission_r1/`)

- `MANUSCRIPT_R1_highlighted.docx` (changes in blue, as the editor requested) and `MANUSCRIPT_R1_clean.docx`
- `SUPPLEMENT_R1_highlighted.docx` / `SUPPLEMENT_R1_clean.docx` (methods, Tables S1–S32, Figures S0–S5)
- `RESPONSE_TO_REVIEWER_R1.docx` / `.txt` (paste into the ScholarOne response box)
- `figures/` (main Figures 1–3 and supplementary S0–S5, 300 dpi)
- `../REVISION_TRACKING_R1.md` (comment-by-comment ledger)
