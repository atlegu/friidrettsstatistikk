"""
audit_01_reextract.py — Audit of the career-data extraction (data/karrieredata_utvidet.csv).

The original extraction paginated with .order("date"), which is not unique: rows tied on
date across a page boundary can be returned twice or skipped. 332 result ids occur twice in
the extract, so a similar number of rows may be missing. This script re-extracts every
result of the 2,123 cohort athletes with deterministic pagination (order by id), keeps rows
created before the original extraction (created_at <= 2026-05-18), and saves them for
comparison (audit_02).

Output: revision_r1/data_private/audit_reextract.csv (athlete-level; not in git)
"""

import logging
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

HERE = Path(__file__).parent
R1 = HERE.parent
DATA = Path("/Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/Statistikk/forskning/ncc-kohort/data")
load_dotenv("/Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/Statistikk/scraper/.env")
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
CUTOFF = "2026-05-18T00:00:00+00:00"
SEL = "id,athlete_id,meet_id,date,performance,performance_value,round,created_at,events(code,category)"


def main():
    ids = pd.read_csv(DATA / "analysedata_utvidet.csv", usecols=["athlete_id"])["athlete_id"].tolist()
    rows = []
    for i in range(0, len(ids), 40):
        batch = ids[i:i + 40]
        offset = 0
        while True:
            res = (sb.table("results").select(SEL).in_("athlete_id", batch).lte("created_at", CUTOFF)
                   .order("id").range(offset, offset + 999).execute())
            rows.extend(res.data)
            if len(res.data) < 1000:
                break
            offset += 1000
        if (i // 40) % 10 == 0:
            logger.info(f"athletes {i + len(batch)}/{len(ids)}: {len(rows)} rows")
    d = pd.DataFrame(rows)
    ev = pd.json_normalize(d["events"]).rename(columns={"code": "event_code", "category": "event_category_db"})
    d = pd.concat([d.drop(columns="events"), ev], axis=1)
    d.to_csv(R1 / "data_private" / "audit_reextract.csv", index=False)
    logger.info(f"done: {len(d)} rows, {d['id'].nunique()} unique ids, {d['athlete_id'].nunique()} athletes")


if __name__ == "__main__":
    main()
