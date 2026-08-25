#!/usr/bin/env bash
# Sesongene som falt ut av hovedkjøringen 25.08.2026.
# 2023 utendørs falt på HTTP/2-grensen, 2019 og nedover på et DNS-fall.
set -uo pipefail
cd "$(dirname "$0")"
source venv/bin/activate

./verify_alle_sesonger.sh 2013 2019          # 2019 ned til 2013, begge sesonger
python update_results.py --outdoor --season 2023 --from-date 2023-01-01 \
    --verify > logs/verify_outdoor_2023_omkjoring.log 2>&1
echo "2023 utendørs:"
grep -E "Kontrollert|Results imported|Errors:" logs/verify_outdoor_2023_omkjoring.log \
  | sed 's/.*INFO - /  /'
