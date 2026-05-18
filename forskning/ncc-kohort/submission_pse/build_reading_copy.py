"""
Build a complete reading copy of the manuscript with tables and figures
embedded inline. The journal submission still uses the separate files
(manuscript with placeholders + TABLES.docx + figure files), but this
version is for the author's review convenience.
"""

import re
from pathlib import Path

HERE = Path(__file__).parent

FIG_FILES = {
    1: "fig1_conceptual_model.png",
    2: "fig2_volume_trajectory.png",
    3: "fig3_km_vol_quintile.png",
}

manuscript = (HERE / "MANUSCRIPT_ANONYMIZED.md").read_text()
tables_md = (HERE / "11_tables.md").read_text()
captions_md = (HERE / "12_figure_captions.md").read_text()


def extract_table(n):
    pattern = rf"## Table {n}\..*?(?=\n## Table |\Z)"
    m = re.search(pattern, tables_md, re.DOTALL)
    return m.group(0).strip() if m else f"[Table {n} not found]"


def extract_caption(n):
    pattern = rf"\*\*Figure {n}\.\*\*.*?(?=\n\n\*\*Figure |\n---|\Z)"
    m = re.search(pattern, captions_md, re.DOTALL)
    return m.group(0).strip() if m else f"[Caption {n} not found]"


def render_figure(n):
    fname = FIG_FILES.get(n, f"figN.png")
    return f"\n![Figure {n}](figures/{fname})\n\n{extract_caption(n)}\n"


out = manuscript

# Replace single table placeholders
out = re.sub(
    r"\[\*\*Table (\d+) about here\*\*\]",
    lambda m: "\n" + extract_table(int(m.group(1))) + "\n",
    out,
)

# Replace single figure placeholders
out = re.sub(
    r"\[\*\*Figure (\d+) about here\*\*\]",
    lambda m: render_figure(int(m.group(1))),
    out,
)

# Replace double figure placeholders ("Figures X and Y")
out = re.sub(
    r"\[\*\*Figures (\d+) and (\d+) about here\*\*\]",
    lambda m: render_figure(int(m.group(1))) + render_figure(int(m.group(2))),
    out,
)

# Replace double table placeholders ("Tables X and Y")
out = re.sub(
    r"\[\*\*Tables (\d+) and (\d+) about here\*\*\]",
    lambda m: "\n" + extract_table(int(m.group(1))) + "\n\n" + extract_table(int(m.group(2))) + "\n",
    out,
)

(HERE / "MANUSCRIPT_FULL.md").write_text(out)
print(f"Wrote MANUSCRIPT_FULL.md ({len(out)} chars)")
remaining = re.findall(r"\[\*\*.*?about here\*\*\]", out)
print(f"Unreplaced placeholders: {len(remaining)}")
if remaining:
    for r in remaining:
        print(f"  {r}")
