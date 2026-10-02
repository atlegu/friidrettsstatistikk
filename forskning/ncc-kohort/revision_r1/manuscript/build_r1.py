"""
build_r1.py — Builds the revised IJSSC submission (SPO-26-1604.R1).

Sources: the section files in this folder, in which every new or changed passage
is wrapped in {+ ... +}. Outputs (folder ../submission_r1/):

  MANUSCRIPT_R1_highlighted.docx  changes in blue text (editor's request)
  MANUSCRIPT_R1_clean.docx        same text, no highlighting
  SUPPLEMENT_R1_highlighted.docx / SUPPLEMENT_R1_clean.docx  (ends with the STROBE checklist)
  TITLE_PAGE_R1.docx              title page (08_title_page.md)
  COVER_LETTER_R1.docx            cover letter for the revision (10_cover_letter_r1.md)
  MANUSCRIPT_R1.md                Vancouver-converted markdown (clean)

Citation conversion (APA -> Sage Vancouver) reuses the mapping of convert_to_vancouver.py.
"""

import re
import shutil
import subprocess
import zipfile
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE.parent / "submission_r1"
FIG = HERE.parent / "figures"
OUT.mkdir(exist_ok=True)

TITLE = ("# Pulling back before dropping out: {+Declining competition participation+} precedes exit from "
         "Norwegian youth track and field — a 14-year register study")
META = """
**Running title:** {+Declining participation precedes exit from youth track and field+}

**Keywords:** youth sport, dropout, athlete retention, longitudinal, track and field, behavioral indicators, sport commitment
"""
REVISED_COLOR = "1F4FD8"

# ----------------------------------------------------------------------------- citation maps
src = (HERE / "convert_to_vancouver.py").read_text()
ns = {}
exec(src[src.index("def sup("):src.index('AUTHOR_BLOCK = """')], ns)
exec(src[src.index('AUTHOR_BLOCK = """'):src.index("text = (HERE")], ns)
PAREN, NARRATIVE, REFERENCES, AUTHOR_BLOCK = ns["PAREN"], ns["NARRATIVE"], ns["REFERENCES"], ns["AUTHOR_BLOCK"]


def to_vancouver(text):
    for old, new in NARRATIVE:
        m = re.match(r"^(.*?)(<sup>[\d,–-]+</sup>)$", new)
        text = re.sub(re.escape(old) + r"([.,]?)", m.group(1).replace("\\", "\\\\") + r"\1" + m.group(2), text)
    for old, new in PAREN:
        if new.startswith("("):
            text = text.replace(old, new)
        else:
            text = re.sub(re.escape(old) + r"([.,]?)", r"\1" + new, text)
    return text


# ----------------------------------------------------------------------------- assembling
def section(fn):
    t = (HERE / fn).read_text()
    lines = t.split("\n", 1)
    return lines[1] if lines[0].startswith("# ") else t


def compile_manuscript():
    abstract = section("02_abstract.md")
    abstract = abstract[re.search(r"^## Final version[^\n]*\n", abstract, re.M).end():].strip()
    decl = section("09_declarations.md").strip()
    ms = f"""{TITLE}
{AUTHOR_BLOCK}
{META}
---

## Abstract

{abstract}

---

## 1. Introduction

{section("03_introduction.md")}

---

## 2. Method

{section("04_methods.md")}

---

## 3. Results

{section("05_results.md")}

---

## 4. Discussion

{section("06_discussion.md")}

---

{decl}

---

"""
    ms = to_vancouver(ms) + REFERENCES
    tables = (HERE / "11_tables.md").read_text()
    main_tables = tables.split("# Supplementary Tables")[0].split("---", 1)[1].strip()
    ms += "\n\n## Tables\n\n" + main_tables + "\n"
    caps = (HERE / "12_figure_captions.md").read_text().split("# Supplementary figure captions")[0]
    caps = "\n".join(l for l in caps.split("\n") if l.startswith("**Figure") or l.strip() == "").strip()
    ms += "\n\n## Figure captions\n\n" + caps + "\n"
    return ms


def compile_supplement():
    tables = (HERE / "11_tables.md").read_text().split("# Supplementary Tables", 1)[1]
    caps = (HERE / "12_figure_captions.md").read_text().split("# Supplementary figure captions", 1)[1]
    figs = {"S0": "figS0_flow_diagram.png", "S1": "figS1_calibration.png", "S2": "figS2_km_overall_sex.png",
            "S3": "figS3_km_msk_typer.png", "S4": "figS4_time_varying_forest.png", "S5": "figS5_event_study.png"}
    fig_md = []
    for para in [p for p in caps.strip().split("\n\n") if p.strip()]:
        m = re.search(r"Figure (S\d)\.", para)
        if m:
            fig_md.append(f"![]({FIG / figs[m.group(1)]}){{width=15cm}}\n\n{para}\n")
    meth = (HERE / "15_supplementary_methods.md").read_text().split("\n", 1)[1]
    strobe = (HERE / "16_strobe_checklist.md").read_text()    # in the supplement since the original submission
    return ("# Supplementary Material\n\n**Pulling back before dropping out: {+Declining competition participation+} precedes "
            "exit from Norwegian youth track and field — a 14-year register study**\n\n"
            "Atle Guttormsen, Norwegian University of Life Sciences (NMBU)\n\n---\n\n"
            "# Supplementary Methods\n" + meth + "\n\n---\n\n# Supplementary Tables\n" + tables +
            "\n\n# Supplementary Figures\n\n" + "\n".join(fig_md) + "\n\n---\n\n" + strobe)


# ----------------------------------------------------------------------------- highlighting
SPAN = re.compile(r"\{\+(.*?)\+\}", re.S)


def clean(text):
    return SPAN.sub(lambda m: m.group(1), text)


def highlighted(text):
    def rep(m):
        parts = re.split(r"(\n\s*\n)", m.group(1))
        out = []
        for part in parts:
            if not part.strip() or re.fullmatch(r"\n\s*\n", part):
                out.append(part)
                continue
            lead = re.match(r"^(\s*(?:[-*] |\d+\. )?)", part).group(1)
            body = part[len(lead):]
            body = body.replace("[", r"\[").replace("]", r"\]")
            out.append(f'{lead}[{body}]{{custom-style="Revised"}}')
        return "".join(out)
    return SPAN.sub(rep, text)


def reference_docx():
    ref = OUT / ".reference_r1.docx"
    data = subprocess.run(["pandoc", "--print-default-data-file", "reference.docx"], capture_output=True, check=True).stdout
    ref.write_bytes(data)
    tmp = OUT / ".ref_tmp.docx"
    with zipfile.ZipFile(ref) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            buf = zin.read(item.filename)
            if item.filename == "word/styles.xml":
                s = buf.decode("utf-8")
                style = (f'<w:style w:type="character" w:customStyle="1" w:styleId="Revised"><w:name w:val="Revised"/>'
                         f'<w:rPr><w:color w:val="{REVISED_COLOR}"/></w:rPr></w:style>')
                s = s.replace("</w:styles>", style + "</w:styles>")
                buf = s.encode("utf-8")
            zout.writestr(item, buf)
    shutil.move(tmp, ref)
    return ref


def to_docx(md_text, out_name, ref):
    md = re.sub(r"<sup>([^<]+)</sup>", r"^\1^", md_text)
    md = re.sub(r"\n---\n(?=\S)", "\n---\n\n", md)
    tmp = OUT / f".{out_name}.md"
    tmp.write_text(md)
    subprocess.run(["pandoc", str(tmp), "-f", "markdown-yaml_metadata_block", "-o", str(OUT / out_name), f"--reference-doc={ref}"], check=True)
    tmp.unlink()


def main():
    ms = compile_manuscript()
    for f in ["02_abstract.md", "03_introduction.md", "04_methods.md", "05_results.md", "06_discussion.md",
              "11_tables.md", "12_figure_captions.md", "15_supplementary_methods.md", "16_strobe_checklist.md"]:
        t = (HERE / f).read_text()
        assert t.count("{+") == t.count("+}"), f"unbalanced markers in {f}"
        depth = 0
        for m in re.finditer(r"\{\+|\+\}", t):
            depth += 1 if m.group() == "{+" else -1
            assert 0 <= depth <= 1, f"nested or stray highlight marker in {f} at {m.start()}"
    ref = reference_docx()
    (OUT / "MANUSCRIPT_R1.md").write_text(clean(ms))
    to_docx(highlighted(ms), "MANUSCRIPT_R1_highlighted.docx", ref)
    to_docx(clean(ms), "MANUSCRIPT_R1_clean.docx", ref)
    sup = compile_supplement()
    to_docx(highlighted(sup), "SUPPLEMENT_R1_highlighted.docx", ref)
    to_docx(clean(sup), "SUPPLEMENT_R1_clean.docx", ref)
    # separate title page, as uploaded with the original submission (replaces TITLE_PAGE_IJSSC.docx);
    # the file's note to the author (above the first rule) is left out
    tp = (HERE / "08_title_page.md").read_text().split("\n---\n", 1)[1]
    to_docx(clean("# Title page\n" + tp), "TITLE_PAGE_R1.docx", ref)
    # cover letter for the revision (carries the AI-use declaration the Acknowledgements refer to)
    to_docx((HERE / "10_cover_letter_r1.md").read_text(), "COVER_LETTER_R1.docx", ref)
    resp = OUT / "RESPONSE_TO_REVIEWER_R1.md"
    subprocess.run(["pandoc", str(resp), "-f", "markdown-yaml_metadata_block", "-o", str(OUT / "RESPONSE_TO_REVIEWER_R1.docx"),
                    f"--reference-doc={ref}"], check=True)
    subprocess.run(["pandoc", str(resp), "-f", "markdown-yaml_metadata_block", "-t", "plain", "--wrap=none",
                    "-o", str(OUT / "RESPONSE_TO_REVIEWER_R1.txt")], check=True)
    (OUT / "figures").mkdir(exist_ok=True)
    for f in sorted((HERE.parent / "figures").glob("*.png")):
        shutil.copy(f, OUT / "figures" / f.name)
    ref.unlink()

    body = clean(ms)[: clean(ms).index("## References")]
    main_txt = body[body.index("## 1. Introduction"): body.index("## Acknowledgements")]
    leftovers = [m.group(0) for m in re.finditer(r"\([^()]*\b(?:19|20)\d{2}[^()]*\)", body)
                 if re.search(r"[A-Za-z]{3,}[^()]*\d{4}|\d{4}[^()]*[A-Za-z]{3,}", m.group(0))]
    print(f"main text {len(main_txt.split())} words; superscript citations {len(re.findall('<sup>', body))}; "
          f"highlighted spans in manuscript {ms.count('{+')}")
    print("APA-style citations left in body (must be none):", leftovers)


if __name__ == "__main__":
    main()
