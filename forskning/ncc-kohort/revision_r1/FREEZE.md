# Code and data freeze — IJSSC SPO-26-1604.R1

Frozen 3 October 2026, after the final check (independent data, number, claims and letter reviews; independent R implementation). From here on only text changes (manuscript sections, captions, Supplementary Methods, the response letter and the cover letter).

## What is frozen

- `FREEZE_data.sha256`: the saved May 2026 extract and the original analysis files (main checkout, `../data/`), the re-extraction, the corrected data built by `r1_00` (`data_private/corrected/`), `r1_variables.csv`, the register-population frequencies, and the Tyrving workbook and parameters.
- `FREEZE_code.sha256`: `RUN_ALL.sh`, `analysis/` (r1_00 to r1_06 and helpers), the build and citation scripts, `audit/`, and the original scripts 07–16 that `r1_00` and `r1_02` run.
- `FREEZE_outputs.sha256`: every table (CSV and the rendered `11_tables.md`), `r1_results.json`, `r1_text_numbers.json`, all figures, `MANUSCRIPT_R1.md` and the response letter (.txt). The .docx files are not hashed (they carry timestamps).

`RUN_ALL.sh` checks the data and code hashes before anything runs, re-runs r1_01 to r1_06 and the build, checks that the outputs are identical to the frozen ones, that both letters state the build's word count, and that there are no unconverted citations, and then runs the independent R implementation (0 mismatches, estimates within 1e-3) and the letter-quote check. `RUN_ALL.sh --rebuild` also rebuilds the corrected data from the register with `r1_00` and checks it against `FREEZE_data.sha256`.

A text change alters `MANUSCRIPT_R1.md` or the letter and therefore `FREEZE_outputs.sha256`; renew that file after any text change and say so in the log.

## Changing a frozen file

Change a frozen file only for a verified error, not for a preference. Then:

1. Write the reason, the file and the expected effect in the log below *before* editing.
2. Make the change, run the affected scripts, compare the outputs with the frozen ones, and update every number in the text and the letter that moved.
3. Renew the hashes with `make_freeze.sh` and run `RUN_ALL.sh` until every check is green. Record the effect in the log.

## Log

| Date | File | Reason | Effect on results |
|---|---|---|---|
| 3 Oct 2026 | — | Freeze set after the final check: championship types corrected (r1_00, 318 athletes), HHI from every result (r1_01, 1 athlete), level forms and the final-season count stored (r1_03), two text numbers stored (r1_04), table notes (r1_06), word-count and citation checks (RUN_ALL), championship types and the landmark model added to the R implementation (audit_06) | See REVISION_TRACKING_R1.md, "Errors found and corrected" |
| 3 Oct 2026 | `RUN_ALL.sh` | The new citation check used the build's list of parentheses with a year, which also lists non-citations such as "(birth years 1998–2002)", and stopped the first run. Replaced by an author–year pattern (name, optional "et al." or second author, comma, year), which finds 49 citations in the section sources and none in the built main text | Checks only |
| 3 Oct 2026 | `analysis/r1_00_corrected_data.py`, `audit/audit_06_r_independent.R` | Final narrow review (agent G), verified on the data: Finnmark's district championship ("FM", "Finnmarksmesterskapet") and Norwegian "DM" were missed; every result of 15–16-year-olds at NM relay meets is a 100 m side event (31 of 31); "NM Mangekamp inne 2018" entries are youth classes (U18, "Ungdom"); district championships for ages 11–14 were credited to 15–16-year-olds (and senior-only ones to 13–14-year-olds); a general rule for meets abroad is needed once "DM" counts (Swedish DMs). Rules refined in both implementations | n_msk_typer for about 50 athletes; post-baseline Cox tables (5, S1, S2, S5–S8, S11), Figures S3–S4, and possibly §3.7, §4.5, §4.9 by about 0.01 |
| 3 Oct 2026 | `analysis/r1_03_reviewer_analyses.py`, `analysis/r1_06_tables.py` | Final narrow review: the Table S22 note and the letter say the association holds within clubs, but S22 had no within-club estimate (random intercepts are not one). Club fixed effects (conditional logit) added to S22. Also table wording: S19 note ("no predictor is measured after exit"), S6 note ("essentially unchanged"), S15 title and S27 label ("baseline-window" instead of "time-aligned"), Table 4 note ("added little", with its p = .056, instead of "added nothing") | New row in S22; notes and labels only |
| 3 Oct 2026 | `analysis/r1_04_text_numbers.py` | S-M12 states the remaining ambiguity of the district type: athletes whose type rests only on meets with embedded district-championship events ("innlagt KM"). Counted by re-applying the r1_00 rules, with an assertion that they reproduce n_msk_typer | New stored number only |
| 3 Oct 2026 | `FREEZE_data.sha256`, `FREEZE_code.sha256`, `FREEZE_outputs.sha256` | Hashes renewed after the logged changes above (analysis file changed in n_msk_typer and um_15_16 only; the other corrected files are identical) | — |
| 3 Oct 2026 | `FREEZE_outputs.sha256` | The previous renewal hashed the response letter (.txt) before it was rebuilt with the new word count, so RUN_ALL stopped at the output check; renewed after the build | — |
| 3 Oct 2026 | `analysis/r1_00_corrected_data.py`, `audit/audit_06_r_independent.R`, `analysis/r1_06_tables.py` | Re-review (agent H): in "KM Hedmark og Oppland/Indoor games 12-14" (2017) the range belongs to the indoor games, as with Kretskarusell (1 athlete); "/TYR" is Istanbul, not a Norwegian venue (no effect). S22 note: conclusion moved after the evidence | About 25 post-baseline cells by one unit in the last digit (predicted by the reviewer: §3.7 upper CI 0.78, §4.9 χ² 263.1, S-M12 360) |
| 3 Oct 2026 | `FREEZE_data.sha256`, `FREEZE_code.sha256`, `FREEZE_outputs.sha256` | Renewed after the indoor-games fix; the rerun reproduced the reviewer's predicted values exactly (360 athletes; S8 upper CI 0.78; S1 χ² 263.12 and 8.14; Table 5 C-index 0.664, 0.595); text updated (§3.7, §4.9, S-M12) and rebuilt before hashing | — |
