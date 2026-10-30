"""
audit_03_tyrving.py — Validates tyrving_r2.points() against the NFIF workbook itself.

Writes test results into the input cells of a copy of the workbook (converted to .xlsx),
lets LibreOffice recalculate it headlessly, and compares the workbook's point cells (column F)
with tyrving_r2 for every row type, sex and age 13-16, at several result levels per row
(above the reference, between 80% and 100% of it, below 80%, and far below).

Requires: LibreOffice (soffice) and openpyxl. Output: audit/audit_03_tyrving.csv + summary.
"""

import subprocess
import sys
from pathlib import Path

import openpyxl
import pandas as pd

HERE = Path(__file__).parent
R1 = HERE.parent
sys.path.insert(0, str(R1 / "analysis"))
import tyrving_r2 as ty  # noqa: E402

WORK = Path("/private/tmp/claude-501/-Users-atleguttormsen-Dropbox-Aktuelt1-Florida25-Statistikk--claude-worktrees-nervous-brahmagupta-3cddb8/907c7734-c7e4-47a4-909e-3d2cb78187a2/scratchpad/xls")
LEVELS = [1.05, 1.00, 0.95, 0.85, 0.80, 0.75, 0.60]   # result as a share of the reference (field); time uses 1/share


def main():
    src = WORK / "tyrving.xlsx"
    wb = openpyxl.load_workbook(src)
    params = pd.read_csv(R1 / "analysis" / "tyrving_params_2014.csv")
    tests = []
    for ws in wb.worksheets:
        if ws.title == "Forside":
            continue
        sex = "M" if ws.title.startswith("Gutter") else "F"
        age = int(ws.title.split()[1])
        if age not in (13, 14, 15, 16):
            continue
        for r in range(6, ws.max_row + 1):
            ev = ws.cell(r, 2).value
            if not ev or not isinstance(ws.cell(r, 16).value, str):
                continue
            prow = params[(params.sex == sex) & (params.age == age) & (params.event == str(ev).strip())
                          & (params.spec.fillna("") == (str(ws.cell(r, 3).value).strip() if ws.cell(r, 3).value else ""))].iloc[0]
            # one test per row per sheet copy: use the level cycling over rows, plus a second pass below
            tests.append((ws.title, r, prow))
    results = []
    for k, lev in enumerate(LEVELS):
        wbk = openpyxl.load_workbook(src)
        for title, r, prow in tests:
            ws = wbk[title]
            ref = float(prow["ref"])
            if prow["type"].startswith("time"):
                val = round(ref / lev, 2)
            else:
                val = round(ref * lev, 2)
            if prow["type"] == "time_minsec":
                ws.cell(r, 4).value = int(val // 60)
                ws.cell(r, 5).value = round(val - 60 * int(val // 60), 2)
            else:
                ws.cell(r, 5).value = val
            results.append(dict(sheet=title, row=r, level=lev, event=prow["event"], spec=prow["spec"],
                                type=prow["type"], value=val, ours=ty.points(prow.to_dict(), val)))
        out = WORK / f"test_{k}.xlsx"
        wbk.save(out)
        conv = WORK / "recalc"
        conv.mkdir(exist_ok=True)
        subprocess.run(["soffice", f"-env:UserInstallation=file://{WORK.parent}/lo_profile", "--headless",
                        "--convert-to", "xlsx", "--outdir", str(conv), str(out)], capture_output=True, check=True)
        calc = openpyxl.load_workbook(conv / out.name, data_only=True)
        for res in results:
            if res["level"] == lev:
                res["workbook"] = calc[res["sheet"]].cell(res["row"], 6).value
    t = pd.DataFrame(results)
    t["diff"] = t["ours"] - t["workbook"]
    t.to_csv(HERE / "audit_03_tyrving.csv", index=False)
    print(f"tests: {len(t)}; exact matches: {(t['diff'] == 0).sum()}; max |diff|: {t['diff'].abs().max()}")
    print(t.groupby("type")["diff"].agg(["size", lambda s: (s == 0).mean(), lambda s: s.abs().max()]).to_string())
    if (t["diff"] != 0).any():
        print(t[t["diff"] != 0].head(20).to_string())


if __name__ == "__main__":
    main()
