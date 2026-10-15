"""audit_07_letter_quotes.py - every passage the response letter quotes must be in the current text.

Text edits late in a revision break quotes silently (paper-data-audit, phase 4). The script takes
every quoted passage of three or more words from RESPONSE_TO_REVIEWER_R1.md and looks it up in the
clean manuscript, the supplement (section sources, markers stripped) and the decision letter
(quotes of the reviewer). Passages found nowhere are listed and the script exits with code 1.
"""

import re
import sys
from pathlib import Path

R1 = Path(__file__).resolve().parent.parent
LETTER = R1 / "submission_r1" / "RESPONSE_TO_REVIEWER_R1.md"
SOURCES = {
    "manuscript": [R1 / "submission_r1" / "MANUSCRIPT_R1.md"],
    "supplement": [R1 / "manuscript" / f for f in ("11_tables.md", "12_figure_captions.md", "15_supplementary_methods.md")],
    "submission": [R1.parent / "submission_pse" / "MANUSCRIPT_IJSSC.md"],
}


def norm(s):
    s = s.replace("{+", "").replace("+}", "").replace("*", "")
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip().lower()


def main():
    letter = LETTER.read_text()
    reviewer = "\n".join(l for l in letter.splitlines() if l.startswith("**Comment"))   # the reviewer's own words
    texts = {k: norm("\n".join(p.read_text() for p in v if p.exists())) for k, v in SOURCES.items()}
    texts["reviewer"] = norm(reviewer)
    quotes = re.findall(r"[\"“]([^\"“”]{8,400})[\"”]", letter)
    missing, n = [], 0
    for q in quotes:
        if len(q.split()) < 3:
            continue
        n += 1
        found = [k for k, t in texts.items() if norm(q) in t]
        if not found:
            missing.append(q)
        print(f"{'OK ' if found else 'MISSING'}  {', '.join(found) or '-':24s} {q[:90]}")
    print(f"\n{n} quoted passages, {len(missing)} not found")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
