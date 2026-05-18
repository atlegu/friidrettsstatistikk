"""
Compile MANUSCRIPT_ANONYMIZED.md from the constituent section files.

Reads 01_highlights through 09_declarations and produces a single
anonymized manuscript file suitable for conversion to docx.

Tables go in 11_tables.md and figure captions in 12_figure_captions.md
(separate files for PSE submission). Placeholders stay in the manuscript
to indicate intended position.
"""

from pathlib import Path

HERE = Path(__file__).parent

TITLE = "# Pulling back before dropout: Behavioral disengagement precedes youth-sport exit by years in a 14-year register study"
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
# Abstract file has explanatory header text — extract only the final version
abstract_marker = "## Final version (≤250 words)"
if abstract_marker in abstract:
    abstract = abstract.split(abstract_marker)[1].strip()
    # Drop "---" if present
    abstract = abstract.lstrip("-\n ").strip()

intro = section("03_introduction.md")
methods = section("04_methods.md")
results = section("05_results.md")
discussion = section("06_discussion.md")
references = section("07_references.md")
# References file has subtitle "(APA 7th edition format)" — keep it
declarations = section("09_declarations.md")

# Generative AI disclosure should be its own section before References
ai_marker = "## Declaration of generative AI"
if ai_marker in declarations:
    ai_section = declarations[declarations.index(ai_marker):]
    # Cut where next ## starts
    end = ai_section.find("\n## ", 5)
    if end > 0:
        ai_section = ai_section[:end].strip()
else:
    ai_section = ""

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

## {ai_section.split(chr(10))[0].lstrip('#').strip() if ai_section else 'Declaration of generative AI and AI-assisted technologies'}

{chr(10).join(ai_section.split(chr(10))[1:]).strip() if ai_section else 'During the preparation of this work the author used Claude Code (Anthropic) to assist with implementing statistical analyses in Python, generating figures using matplotlib, and editing the manuscript text for clarity and consistency. After using this tool, the author reviewed and edited the content as needed and takes full responsibility for the content of the published article.'}

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
