"""
r2_sammenlign.py — every output of the R2 run (complete Tyrving mapping) against the frozen R1 outputs.

Reference: the submitted R1 build (worktree claude/nervous-brahmagupta-3cddb8, commit 60b5720; the
uploaded files in IJSSC_R1_opplasting/ are identical to it). A null run of this folder with the
unchanged tyrving_r2 reproduced every R1 output (largest relative difference 1.6e-13, floating-point
noise), so every difference below comes from the mapping alone.

Output (tables/):
  r2_endringer_resultater.csv  numeric keys of r1_results.json and r1_text_numbers.json that moved
                               (relative difference > 1e-9), old and new
  r2_endringer_tabeller.csv    table cells (CSV) that moved, old and new
  r2_diff_tabeller.txt         unified diff of the rendered tables (manuscript/11_tables.md)
  r2_diff_manus.txt            unified diff of the built manuscript (submission_r1/MANUSCRIPT_R1.md)
"""

import difflib
import json
import math
from pathlib import Path

import pandas as pd

R2 = Path(__file__).parent.parent
R1 = Path("/Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/Statistikk/.claude/worktrees/"
          "nervous-brahmagupta-3cddb8/forskning/ncc-kohort/revision_r1")
TOL = 1e-9


def flat(d, p=""):
    if isinstance(d, dict):
        for k, v in d.items():
            yield from flat(v, f"{p}/{k}")
    elif isinstance(d, list):
        for i, v in enumerate(d):
            yield from flat(v, f"{p}[{i}]")
    else:
        yield p, d


def moved(x, y):
    if isinstance(x, bool) or isinstance(y, bool) or not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        return x != y
    if isinstance(x, float) and isinstance(y, float) and math.isnan(x) and math.isnan(y):
        return False
    return abs(x - y) > TOL * max(abs(x), abs(y), 1e-12)


def json_diff():
    rader = []
    for fil in ["tables/r1_results.json", "tables/r1_text_numbers.json"]:
        a = dict(flat(json.loads((R1 / fil).read_text())))
        b = dict(flat(json.loads((R2 / fil).read_text())))
        for k in sorted(set(a) | set(b)):
            if moved(a.get(k), b.get(k)):
                rader.append({"fil": Path(fil).name, "nokkel": k, "R1": a.get(k), "R2": b.get(k)})
    return pd.DataFrame(rader, columns=["fil", "nokkel", "R1", "R2"])


def csv_diff():
    rader = []
    for f1 in sorted((R1 / "tables").rglob("*.csv")):
        rel = f1.relative_to(R1)
        f2 = R2 / rel
        if not f2.exists():
            rader.append({"fil": str(rel), "rad": "", "kolonne": "", "R1": "fil", "R2": "mangler"})
            continue
        a, b = pd.read_csv(f1, dtype=str, keep_default_na=False), pd.read_csv(f2, dtype=str, keep_default_na=False)
        if a.shape != b.shape or list(a.columns) != list(b.columns):
            rader.append({"fil": str(rel), "rad": "", "kolonne": "", "R1": f"{a.shape}", "R2": f"{b.shape}"})
            continue
        for c in a.columns:
            for i, (x, y) in enumerate(zip(a[c], b[c])):
                if x == y:
                    continue
                try:
                    if not moved(float(x), float(y)):
                        continue
                except ValueError:
                    pass
                rader.append({"fil": str(rel), "rad": i, "kolonne": c, "R1": x, "R2": y,
                              "etikett": a.iloc[i, 0]})
    return pd.DataFrame(rader, columns=["fil", "rad", "kolonne", "etikett", "R1", "R2"])


def tekst_diff(rel):
    a = (R1 / rel).read_text().splitlines()
    b = (R2 / rel).read_text().splitlines()
    return "\n".join(difflib.unified_diff(a, b, fromfile=f"R1/{rel}", tofile=f"R2/{rel}", lineterm="", n=0))


def main():
    tab = R2 / "tables"
    j = json_diff()
    j.to_csv(tab / "r2_endringer_resultater.csv", index=False)
    c = csv_diff()
    c.to_csv(tab / "r2_endringer_tabeller.csv", index=False)
    (tab / "r2_diff_tabeller.txt").write_text(tekst_diff("manuscript/11_tables.md") + "\n")
    (tab / "r2_diff_manus.txt").write_text(tekst_diff("submission_r1/MANUSCRIPT_R1.md") + "\n")
    print(f"resultatnøkler som flyttet seg: {len(j)}; tabellceller: {len(c)} i {c['fil'].nunique()} filer")
    print(c.groupby("fil").size().to_string() if len(c) else "")


if __name__ == "__main__":
    main()
