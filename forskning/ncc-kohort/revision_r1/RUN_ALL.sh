#!/usr/bin/env bash
# RUN_ALL.sh - the whole IJSSC R1 pipeline, from the frozen data to the Word files, then all checks.
#
#   ./RUN_ALL.sh              # verify the freeze, run r1_01 ... r1_06, build, run the checks
#   ./RUN_ALL.sh --rebuild    # also rebuild the corrected data with r1_00 (queries the register:
#                             # rows created on or before 18 May 2026; must reproduce FREEZE_data)
#
# Stops at the first failure (set -eo pipefail). See FREEZE.md before changing anything.
set -euo pipefail
cd "$(dirname "$0")"
PY=/Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/Statistikk/scraper/venv/bin/python

echo "== 1. Freeze: data and code hashes"
shasum -a 256 -c FREEZE_data.sha256 --quiet
shasum -a 256 -c FREEZE_code.sha256 --quiet
echo "   ok"

if [[ "${1:-}" == "--rebuild" ]]; then
  echo "== 2. r1_00 corrected data (register)"
  (cd analysis && "$PY" r1_00_corrected_data.py)
  shasum -a 256 -c FREEZE_data.sha256 --quiet
fi

echo "== 3. Analyses"
for s in r1_01_build_variables r1_02_rerun_original_scripts r1_03_reviewer_analyses r1_04_text_numbers r1_05_figures r1_06_tables; do
  echo "   $s"
  (cd analysis && "$PY" "$s.py" > "../tables/$s.log" 2>&1)
done

echo "== 4. Word files"
BUILD=$(cd manuscript && "$PY" build_r1.py)
echo "$BUILD"
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

echo "== 5. Outputs identical to the frozen outputs"
shasum -a 256 -c FREEZE_outputs.sha256 --quiet
echo "   ok"

echo "== 6. Checks"
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
