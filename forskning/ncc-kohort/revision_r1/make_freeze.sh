#!/usr/bin/env bash
# make_freeze.sh - write the hash files that RUN_ALL.sh checks (FREEZE_data, FREEZE_code, FREEZE_outputs).
# Run only when deliberately (re)freezing, and log the reason in FREEZE.md first.
set -euo pipefail
cd "$(dirname "$0")"
DATA=/Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/Statistikk/forskning/ncc-kohort/data

shasum -a 256 \
  data_private/audit_reextract.csv data_private/corrected/*.csv data_private/r1_variables.csv \
  data_private/register_population_freq.csv analysis/tyrving_params_2014.csv \
  "$DATA"/analysedata_utvidet.csv "$DATA"/karrieredata_utvidet.csv "$DATA"/kohort_utvidet.csv \
  "$DATA"/poengtabell-tyrvingtabellen.xls > FREEZE_data.sha256

shasum -a 256 \
  analysis/*.py analysis/register_population.sql manuscript/build_r1.py manuscript/convert_to_vancouver.py \
  audit/*.py audit/*.R RUN_ALL.sh \
  "$DATA"/07_bygg_analysedata_utvidet.py "$DATA"/08_analyser_pse.py "$DATA"/09_sensitivity_pse.py \
  "$DATA"/10_time_varying_cox.py "$DATA"/11_landmark_calibration.py "$DATA"/13_reviewer_response_analyses.py \
  "$DATA"/15_specialization_confound_check.py "$DATA"/16_revision_analyses.py > FREEZE_code.sha256

shasum -a 256 \
  tables/*.csv tables/rerun/*.csv tables/r1_results.json tables/r1_text_numbers.json figures/*.png \
  manuscript/11_tables.md submission_r1/MANUSCRIPT_R1.md submission_r1/RESPONSE_TO_REVIEWER_R1.txt \
  submission_r1/figures/*.png > FREEZE_outputs.sha256

wc -l FREEZE_data.sha256 FREEZE_code.sha256 FREEZE_outputs.sha256
