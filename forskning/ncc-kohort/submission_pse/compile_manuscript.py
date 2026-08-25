"""
Compile MANUSCRIPT_ANONYMIZED.md from the constituent section files.

Reads 01_highlights through 09_declarations and produces a single
anonymized manuscript file suitable for conversion to docx.

Tables go in 11_tables.md and figure captions in 12_figure_captions.md
(separate files for PSE submission). Placeholders stay in the manuscript
to indicate intended position.
"""

import re
from pathlib import Path

HERE = Path(__file__).parent

TITLE = "# Pulling back before dropping out: Behavioral disengagement precedes exit from Norwegian youth track and field — a 14-year register study"
META = """
**Running title:** Behavioral disengagement precedes youth-sport dropout

**Keywords:** youth sport, dropout, athlete retention, longitudinal, track and field, behavioral indicators, sport commitment
"""

def section(filename, drop_heading_line=True):
    text = (HERE / filename).read_text()
    if drop_heading_line:
        lines = text.split("\n", 1)
        if lines[0].startswith("# "):
            return lines[1] if len(lines) > 1 else ""
    return text


abstract = section("02_abstract.md")
# Abstract file has explanatory header text — extract only the final version.
# Match any "## Final version" heading regardless of suffix.
m = re.search(r"^## Final version[^\n]*\n", abstract, re.MULTILINE)
if m:
    abstract = abstract[m.end():].strip().lstrip("-\n ").strip()

intro = section("03_introduction.md")
methods = section("04_methods.md")
results = section("05_results.md")
discussion = section("06_discussion.md")
references = section("07_references.md")
# References file has subtitle "(APA 7th edition format)" — keep it
# IJSSC/SAGE structure: Acknowledgements + Statements and Declarations
# (with mandatory subheadings) come after the Discussion, before References.
declarations = section("09_declarations.md").strip()

manuscript = f"""{TITLE}
{META}
---

## Abstract

{abstract}

---

## 1. Introduction

{intro}

---

## 2. Method

{methods}

---

## 3. Results

{results}

---

## 4. Discussion

{discussion}

---

{declarations}

---

## References

{references}
"""

# Remove section file titles that leaked through
manuscript = manuscript.replace("# Introduction\n\n", "")
manuscript = manuscript.replace("# Methods\n\n", "")
manuscript = manuscript.replace("# Results\n\n", "")
manuscript = manuscript.replace("# Discussion\n\n", "")

# Save
(HERE / "MANUSCRIPT_ANONYMIZED.md").write_text(manuscript)
print(f"Wrote MANUSCRIPT_ANONYMIZED.md ({len(manuscript.split())} words)")
