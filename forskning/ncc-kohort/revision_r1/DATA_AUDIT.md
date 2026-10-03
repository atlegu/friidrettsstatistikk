# DATA_AUDIT — IJSSC SPO-26-1604.R1

Inventory of every data input, coverage, and the audit trail. Hashes: `FREEZE_data.sha256`.

## Inputs

| File | Produced by | Rows | Used for |
|---|---|---|---|
| `data_private/audit_reextract.csv` | `audit/audit_01_reextract.py`, register rows created ≤ 2026-05-18, paged by id | 226,760 | 334 rows the original extraction skipped |
| `../data/karrieredata_utvidet.csv`, `kohort_utvidet.csv`, `analysedata_utvidet.csv` (main checkout) | original pipeline, May 2026 extract | 230,868 / 2,123 / 2,123 | base of the corrected career data; "as submitted" comparisons |
| `data_private/corrected/*.csv` | `analysis/r1_00_corrected_data.py` | 231,144 results, 2,138 athletes | all R1 analyses |
| `data_private/r1_variables.csv` | `analysis/r1_01_build_variables.py` | 2,138 | Tyrving (exact workbook formulas), HHI 13–14, within-event percentile |
| `data_private/register_population_freq.csv` | `analysis/register_population.sql` (register as at extraction) | 364 cells | Table S31 |
| `../data/poengtabell-tyrvingtabellen.xls`, `analysis/tyrving_params_2014.csv` | Norwegian Athletics Federation workbook (2014) | — | Tyrving scoring (validated 1,596/1,596, `audit/audit_03`) |

The register itself is not frozen in place: the cleanup of 18 Sep 2026 kept newer copies of some results, so `created_at <= 2026-05-18` no longer reproduces the May 2026 state (4,110 rows of the May extract are no longer in the register with a creation date before the cutoff: deleted, merged into another athlete, or replaced by a newer copy). The analyses therefore start from the saved May extract. A full re-run on 3 Oct 2026, after the register cleanup of import duplicates, reproduced every output byte for byte.

## Coverage

Athletes by baseline year (edition of the 13–14 meet) and birth year:

| Baseline | 1998 | 1999 | 2000 | 2001 | 2002 | All |
|---|---|---|---|---|---|---|
| 2011 | 317 | | | | | 317 |
| 2012 | 125 | 330 | | | | 455 |
| 2013 | | 105 | 319 | | | 424 |
| 2014 | | | 113 | 321 | | 434 |
| 2015 | | | | 102 | 308 | 410 |
| 2016 | | | | | 98 | 98 |
| All | 442 | 435 | 432 | 423 | 406 | 2,138 |

Results and active cohort members per calendar year decline smoothly from 36,269 / 1,637 (2013) to 1,559 / 149 (2025). Pre-baseline 2010 holds 324 indoor results. 2020–2021 show the COVID-19 dip (4,788 and 3,275 results; indoor share 0.15 in 2021). The outcome counts any active senior season through 2025, so a pandemic gap followed by a return is not an exit (Table S30). Follow-up ends with the complete 2025 season; the partial 2026 season is removed.

## Checks

| Phase | Where | Result |
|---|---|---|
| Inventory, coverage | this file | above |
| Data use against the Methods | `audit/audit_01`–`05`, Supplementary Methods S-M12 | corrections listed there; championship types re-read meet name by meet name on 3 Oct 2026 (UM matched as letters, Junior-NM as senior, qualification/preparation/unofficial/veterans' meets counted: count changed for 361 athletes after the final narrow review added Finnmark's FM, Norwegian DM, relay and combined-events national meets, age-restricted district championships and meets abroad) |
| Independent implementation (R) | `audit/audit_06_r_independent.R` → `audit_06_summary.csv` | all 2,138 athletes and 17 variables identical, including HHI (now from every result; the run-time sanity filter had dropped one result of one athlete) and championship types (classified independently with word tokens); Table 3, 4, 7, Cox, landmark and fixed-effects estimates agree to 4 decimals |
| Letter quotes verbatim | `audit/audit_07_letter_quotes.py` | 23 of 23 found |
| Every number traced | independent agent reviews 2–3 Oct 2026 (number trace, data and model re-estimation, reviewer compliance, final narrow review) | findings fixed; see REVISION_TRACKING_R1.md |
| One pipeline, deterministic | `RUN_ALL.sh`, `FREEZE.md` | outputs hash-identical on re-run |

## Remains with the author

- Hand validation of a sample of cohort members against the source (results pages of the 13–14 meet and later careers).
- External facts: meet dates and venues 2011–2016, UM qualification rules, the AI-use and data statements.
- Completeness of the register itself (pre-2012 coverage, results missing from the source).
- The final read-through of the text.
