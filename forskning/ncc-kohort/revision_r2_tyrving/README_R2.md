# IJSSC SPO-26-1604 — R2 preparation: complete Tyrving mapping

Prepared 30 Oct 2026, after R1 was resubmitted. Nothing here has been sent to the journal; it is ready for the next revision. Summary in Norwegian, with the decision points: `../NOTAT_2026-10-30_tyrving_koblinger.md`.

## Why

The A1/A3/A6 data audit (30 Oct 2026) found that the shared scoring module `tyrving_r2.py` had no event-code mapping for several standard implements and hurdle/steeplechase/race-walk codes that the Tyrving table has rows for. They were returned as unscored, although Supplementary Methods S-M3 says every result is scored when its event and specification match a table row. Affected codes include shot 5 kg, discus 1.5 kg, javelin 500/700 g, hammer 5 kg, 80/100/300 m hurdles, steeplechase and race walk. The baseline meet is not affected; per-age maxima at 13–16 and the 13→14 change are.

## What this folder is

- A copy of the submitted R1 working folder (worktree branch `claude/nervous-brahmagupta-3cddb8`, commit 60b5720). The uploaded files in `../IJSSC_R1_opplasting/` are identical to that build.
- `../revision_r1/`, the R1 freeze and the uploaded files are untouched.
- The `FREEZE_*.sha256` and `FREEZE.md` files here are the R1 references. The R2 run is compared against them; they are not R2 freezes.

## Changes from R1

| File | Change |
|---|---|
| `analysis/tyrving_r3.py` | New: `tyrving_r2.py` plus the missing code mappings. Ball-throw values stored in centimetres in the May 2026 extract are converted. Formulas and parameters are unchanged. |
| `analysis/r1_00_corrected_data.py`, `r1_01_build_variables.py`, `r1_02_rerun_original_scripts.py`, `r1_04_text_numbers.py` | Score with `tyrving_r3` instead of `tyrving_r2` (shims and imports only). |
| `analysis/r2_kontroll_koblinger.py` | New: checks every added mapping against the table rows for the athlete's sex and age. It also checks that no baseline-meet score changes (0 of 7,400). |
| `analysis/r2_sammenlign.py` | New: compares every output with the frozen R1 outputs (JSON keys, table cells, rendered tables, manuscript). |

The athlete-level data in `data_private/` (git-ignored) are copies of the frozen R1 corrected data. `analysedata_utvidet.csv` is rebuilt by the 07 step of `r1_00` with `tyrving_r3`; no register query is needed.

## Null run

With the unchanged `tyrving_r2`, this folder reproduced every R1 output. The rebuilt analysis file was byte-identical. Tables, rendered text and manuscript were identical; `r1_results.json` differed by at most 1.6e-13 relative (floating-point noise from newer numerical libraries). Every difference in the R2 run therefore comes from the mapping alone.

## Run

```bash
./RUN_ALL_R2.sh
```
