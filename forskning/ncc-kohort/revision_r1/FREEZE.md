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
