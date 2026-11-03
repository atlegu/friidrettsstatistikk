"""
lag_docx.py — Word-versjoner av JSAMS-filene (JSAMS foretrekker Word; Times New Roman,
dobbel linjeavstand, 2,5 cm marger). Kjøres etter kompiler.sh.

Forbereder LaTeX-filene for pandoc (tabellfilene limes inn, tabellnoter blir avsnitt under
tabellen, «Table N.»/«Figure N.» settes inn i bildetekstene, henvisninger skrives som tall),
kjører pandoc med citeproc (Vancouver, nummerert etter første sitering) og setter skrift og
linjeavstand med python-docx.
"""
import re
import subprocess
import sys
from pathlib import Path

import docx
from docx.enum.text import WD_LINE_SPACING
from docx.shared import Pt, Cm

HER = Path(__file__).resolve().parent
CSL = HER.parent / "manus_jsams" / "jsams.csl"
if not CSL.exists():
    sys.exit(f"finner ikke {CSL}")
TMP = HER / "_pandoc_tmp"
TMP.mkdir(exist_ok=True)


def forbered(tex: str) -> str:
    tex = re.sub(r"\\input\{([^}]*)\}", lambda m: (HER / (m.group(1) + ".tex")).read_text(encoding="utf-8"), tex)
    tex = re.sub(r"\\vspace\{0\.[23]em\}\n\\parbox\{[0-9.]*\\textwidth\}\{\\footnotesize (.*?)\}\n\\end\{table\}",
                 lambda m: "\\end{table}\n\n\\noindent\\emph{Note.} " + m.group(1) + "\n", tex, flags=re.S)
    tabeller = re.findall(r"\\label\{(tab:[^}]*)\}", tex)
    figurer = re.findall(r"\\label\{(fig:[^}]*)\}", tex)
    for i, lab in enumerate(tabeller, 1):
        tex = tex.replace(f"Table~\\ref{{{lab}}}", f"Table {i}")
        tex = re.sub(r"\\caption\{(?=(?:(?!\\caption).)*?\\label\{" + re.escape(lab) + r"\})",
                     lambda m, i=i: f"\\caption{{Table {i}. ", tex, count=1, flags=re.S)
    for i, lab in enumerate(figurer, 1):
        tex = tex.replace(f"Figure~\\ref{{{lab}}}", f"Figure {i}")
        tex = re.sub(r"\\caption\{(?=(?:(?!\\caption).)*?\\label\{" + re.escape(lab) + r"\})",
                     lambda m, i=i: f"\\caption{{Figure {i}. ", tex, count=1, flags=re.S)
    rest = re.findall(r"\\ref\{[^}]*\}", tex)
    if rest:
        sys.exit(f"uløste henvisninger: {rest}")
    for k in ("\\small\n", "\\scriptsize\n", "\\linenumbers", "\\doublespacing"):
        tex = tex.replace(k, "")
    tex = re.sub(r"\\multicolumn\{2\}\{c\}\{([^}]*)\}", lambda m: m.group(1) + " &", tex)
    tex = re.sub(r"\\bibliographystyle\{[^}]*\}\n", "", tex)
    tex = re.sub(r"\\bibliography\{[^}]*\}", r"\\section*{References}", tex)
    return tex


def pandoc(kilde: Path, maal: Path, nummerer: bool):
    tmp = TMP / kilde.name
    tmp.write_text(forbered(kilde.read_text(encoding="utf-8")), encoding="utf-8")
    cmd = ["pandoc", str(tmp), "-f", "latex", "-t", "docx", "--citeproc",
           "--bibliography", str(HER.parent / "manus_jsams" / "references.bib"), "--csl", str(CSL),
           "--resource-path", f"{HER}:{HER.parent / 'figures'}:{HER.parent / 'manus'}", "-o", str(maal)]
    if nummerer:
        cmd.append("--number-sections")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr)
    if r.stderr.strip():
        print("  pandoc:", r.stderr.strip()[:300])


def stil(maal: Path):
    d = docx.Document(maal)
    for s in d.sections:
        s.left_margin = s.right_margin = s.top_margin = s.bottom_margin = Cm(2.5)
    for navn in ("Normal", "Body Text", "First Paragraph", "Compact Text", "Compact"):
        try:
            s = d.styles[navn]
        except KeyError:
            continue
        s.font.name = "Times New Roman"
        s.font.size = Pt(12)
        s.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    for navn in ("Heading 1", "Heading 2", "Heading 3", "Title", "Table Caption", "Image Caption", "Caption", "Bibliography"):
        try:
            d.styles[navn].font.name = "Times New Roman"
        except KeyError:
            pass
    for navn in ("Table Caption", "Image Caption", "Caption"):
        try:
            d.styles[navn].font.size = Pt(11)
        except KeyError:
            pass
    for t in d.tables:
        for row in t.rows:
            for c in row.cells:
                for p in c.paragraphs:
                    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
                    for r in p.runs:
                        r.font.size = Pt(10)
    d.save(maal)


for navn, nummerer in (("main_brief", True), ("supplement_brief", False), ("title_page_brief", False)):
    pandoc(HER / f"{navn}.tex", HER / f"{navn}.docx", nummerer)
    stil(HER / f"{navn}.docx")
    print(f"{navn}.docx")

if (HER / "cover_letter_brief.md").exists():
    r = subprocess.run(["pandoc", str(HER / "cover_letter_brief.md"), "-o", str(HER / "cover_letter_brief.docx")], capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr)
    stil(HER / "cover_letter_brief.docx")
    print("cover_letter_brief.docx")
