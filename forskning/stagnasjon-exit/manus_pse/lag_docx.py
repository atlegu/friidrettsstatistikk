"""
lag_docx.py — Word-versjoner av PSE-filene (Elsevier vil ha .docx som kildefil).

Kjøres etter kompiler.sh. Forbereder LaTeX-filene for pandoc (tabellfilene limes inn,
resizebox/parbox fjernes, tabellnoter blir avsnitt under tabellen), kjører pandoc med
citeproc (APA 7 fra CSL) og setter Times New Roman 12 pkt med dobbel linjeavstand.
"""
import re, subprocess, sys
from pathlib import Path
import docx
from docx.shared import Pt
from docx.enum.text import WD_LINE_SPACING

HER = Path(__file__).resolve().parent
CSL = "/usr/local/texlive/2025/texmf-dist/tex/latex/citation-style-language/styles/apa.csl"
TMP = HER / "_pandoc_tmp"; TMP.mkdir(exist_ok=True)


def forbered(tex: str) -> str:
    tex = re.sub(r"\\resizebox\{\\textwidth\}\{!\}\{(\\input\{[^}]*\})\}", r"\1", tex)
    tex = re.sub(r"\\input\{([^}]*)\}", lambda m: (HER / (m.group(1) + ".tex")).read_text(encoding="utf-8"), tex)
    # tabellnoter ut av table-miljøet, som eget avsnitt
    tex = re.sub(r"\\vspace\{0\.3em\}\n\\parbox\{[0-9.]*\\textwidth\}\{\\footnotesize (.*?)\}\n\\end\{table\}",
                 r"\\end{table}\n\n\\noindent\\emph{Note.} \1\n", tex, flags=re.S)
    tex = re.sub(r"\\vspace\{0\.2em\}\n\\parbox\{[0-9.]*\\textwidth\}\{\\footnotesize (.*?)\}\n\\end\{table\}",
                 r"\\end{table}\n\n\\noindent\\emph{Note.} \1\n", tex, flags=re.S)
    # Word nummererer ikke selv: sett «Table N.»/«Figure N.» i bildeteksten og skriv henvisningene som tall
    tabeller = re.findall(r"\\label\{(tab:[^}]*)\}", tex)
    figurer = re.findall(r"\\label\{(fig:[^}]*)\}", tex)
    for i, lab in enumerate(tabeller, 1):
        tex = tex.replace(f"Table~\\ref{{{lab}}}", f"Table {i}")
        tex = re.sub(r"\\caption\{(?=[^}]*\}\n\\label\{" + re.escape(lab) + r"\})", lambda m, i=i: f"\\caption{{Table {i}. ", tex)
    for i, lab in enumerate(figurer, 1):
        tex = tex.replace(f"Figure~\\ref{{{lab}}}", f"Figure {i}")
        tex = re.sub(r"\\caption\{(?=(?:(?!\\caption).)*?\\label\{" + re.escape(lab) + r"\})", lambda m, i=i: f"\\caption{{Figure {i}. ", tex, count=1, flags=re.S)
    tex = tex.replace("\\S\\ref{sec:sex}", "Section 4.4")
    rest = re.findall(r"\\ref\{[^}]*\}", tex)
    if rest:
        sys.exit(f"uløste henvisninger: {rest}")
    tex = tex.replace("\\small\n", "").replace("\\linenumbers", "").replace("\\doublespacing", "")
    tex = re.sub(r"\\multicolumn\{2\}\{c\}\{([^}]*)\}", r"\1 &", tex)   # pandoc mister tabellen ellers
    tex = tex.replace("\\printbibliography[heading=none]", "\\printbibliography")
    tex = tex.replace("\\printbibliography", "\\section*{References}\n\\printbibliography")
    return tex


def pandoc(kilde: Path, maal: Path, nummerer: bool):
    tmp = TMP / kilde.name
    tmp.write_text(forbered(kilde.read_text(encoding="utf-8")), encoding="utf-8")
    cmd = ["pandoc", str(tmp), "-f", "latex", "-t", "docx", "--citeproc",
           "--bibliography", str(HER / "references.bib"), "--csl", CSL,
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
    for navn in ("Normal", "Body Text", "First Paragraph", "Compact Text"):
        try:
            s = d.styles[navn]
        except KeyError:
            continue
        s.font.name = "Times New Roman"; s.font.size = Pt(12)
        s.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    for navn in ("Heading 1", "Heading 2", "Heading 3", "Title", "Table Caption", "Image Caption", "Caption", "Bibliography"):
        try:
            s = d.styles[navn]
        except KeyError:
            continue
        s.font.name = "Times New Roman"
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


# Sammendraget som egen fil (eget opplastingselement i Editorial Manager), hentet fra hovedfilen
hoved = (HER / "main_anonymised.tex").read_text(encoding="utf-8")
m = re.search(r"\\section\*\{Abstract\}(.*?)\\newpage", hoved, re.S)
if not m:
    sys.exit("fant ikke sammendraget")
(HER / "abstract.tex").write_text(
    "\\documentclass{article}\n\\begin{document}\n\\section*{Abstract}\n" + m.group(1).strip() + "\n\\end{document}\n", encoding="utf-8")

for navn, nummerer in (("main_anonymised", True), ("supplement", False), ("title_page", False), ("abstract", False)):
    pandoc(HER / f"{navn}.tex", HER / f"{navn}.docx", nummerer)
    stil(HER / f"{navn}.docx")
    print(f"{navn}.docx")
