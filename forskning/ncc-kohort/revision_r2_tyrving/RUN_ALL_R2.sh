#!/usr/bin/env bash
# RUN_ALL_R2.sh - R2 preparation (complete Tyrving mapping): frozen R1 inputs -> rebuilt analysis file ->
# r1_01 ... r1_06 -> Word files -> mapping check, comparison with the frozen R1 outputs, and the R1 checks.
# Stops at the first failure. See README_R2.md.
set -euo pipefail
cd "$(dirname "$0")"
PY=/Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/Statistikk/scraper/venv/bin/python

echo "== 1. Frozen R1 inputs (the analysis file and r1_variables are rebuilt below)"
grep -v -E "data_private/(corrected/analysedata_utvidet|r1_variables|audit_reextract|baseline_venue_corrections)\.csv" \
  FREEZE_data.sha256 | shasum -a 256 -c --quiet
echo "   ok"

echo "== 2. Analysis file rebuilt with tyrving_r3 (07 step of r1_00; no register query)"
(cd analysis && "$PY" -c "import r1_00_corrected_data as m; m.build_analysis_data()")

echo "== 3. Analyses"
for s in r2_kontroll_koblinger r1_01_build_variables r1_02_rerun_original_scripts r1_03_reviewer_analyses \
         r1_04_text_numbers r1_05_figures r1_06_tables; do
  echo "   $s"
  (cd analysis && "$PY" "$s.py" > "../tables/$s.log" 2>&1)
done

echo "== 4. Word files"
BUILD=$(cd manuscript && "$PY" build_r1.py)
echo "$BUILD" | head -1
"$PY" - <<'EOF'
import re, sys
b = open("submission_r1/MANUSCRIPT_R1.md").read()
main = b[b.index("## 1. Introduction"): b.index("## Acknowledgements")]
left = re.findall(r"[A-Z][A-Za-zæøåÆØÅéüö'\-]+(?: et al\.)?(?: (?:&|and) [A-Z][A-Za-zæøåÆØÅéüö'\-]+)?, (?:19|20)\d{2}[a-z]?[;)]", main)
print("   author-year citations left in the main text:", left if left else "none")
sys.exit(1 if left else 0)
EOF
WC=$(printf '%s\n' "$BUILD" | sed -n 's/^main text \([0-9]*\) words.*/\1/p')
WCF=$("$PY" -c "print(f'{int(\"$WC\"):,}')")
for f in submission_r1/RESPONSE_TO_REVIEWER_R1.md manuscript/10_cover_letter_r1.md; do
  grep -q "$WCF words" "$f" || { echo "   $f does not state the main-text count ($WCF words)"; exit 1; }
done
echo "   word count stated in both letters: $WCF"

echo "== 5. Comparison with the frozen R1 outputs"
(cd analysis && "$PY" r2_sammenlign.py)
echo "   R1 outputs that differ:"
shasum -a 256 -c FREEZE_outputs.sha256 2>/dev/null | grep -v ": OK$" | sed 's/^/     /' || true

echo "== 6. R1 checks"
Rscript audit/audit_06_r_independent.R data_private tables/r1_results.json > /dev/null
"$PY" - <<'EOF'
import csv, sys
rows = list(csv.reader(open("audit/audit_06_summary.csv")))[1:]
bad = [r for r in rows if r[0].startswith("mismatches") and r[1] != "0"]
bad += [r for r in rows if r[0].endswith("max abs diff") and float(r[1]) > 1e-3]
print("   R re-implementation:", "ok" if not bad else bad)
sys.exit(1 if bad else 0)
EOF
"$PY" audit/audit_07_letter_quotes.py > /dev/null && echo "   letter quotes: ok"
echo "== done"
