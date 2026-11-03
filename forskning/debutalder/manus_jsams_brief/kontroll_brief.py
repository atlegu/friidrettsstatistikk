"""
kontroll_brief.py — kontrollerer Brief Report-versjonen mot JSAMS' grenser og mot det fryste
manuset, og skriver tittelsiden med ordtellingene.

1. Alle tall i main_brief.tex og supplement_brief.tex skal finnes i det fryste manuset
   (../manus/main.tex, supplement.tex, tabellfilene), unntatt hvitlisten.
2. Hovedtekst ≤ 1 500 ord (Introduction til og med Conclusion), sammendrag ≤ 100 ord,
   høyst 2 tabeller/figurer, høyst 20 referanser.
3. title_page_brief.tex skrives fra malen nederst med tallene satt inn.
"""
import re
import sys
from pathlib import Path

HER = Path(__file__).resolve().parent
FRYST = HER.parent / "manus"
sys.path.insert(0, str(HER.parent.parent))
from audit_felles import ordtelling  # noqa: E402


def tall(sti_liste):
    s = set()
    for sti in sti_liste:
        t = Path(sti).read_text(encoding="utf-8")
        t = re.sub(r"(?<!\\)%.*", "", t)
        t = t.split(r"\begin{document}", 1)[-1]
        t = re.sub(r"\\(cite[pt]?|ref|label|input|includegraphics|graphicspath|bibliography|bibliographystyle|usepackage|geometry)\*?(\[[^\]]*\])?\{[^}]*\}", " ", t)
        t = t.replace(r"\,", "")
        s |= set(re.findall(r"\d+(?:[.,]\d+)*", t))
    return s


tabeller = sorted(FRYST.glob("t?.tex")) + sorted(FRYST.glob("s?.tex"))
fryst = tall([FRYST / "main.tex", FRYST / "supplement.tex"] + tabeller)
brief = tall([HER / "main_brief.tex", HER / "supplement_brief.tex"] + tabeller)
HVITLISTE = {"5": "Tabell S5", "6": "Tabell S6", "5.5": "Claude Opus 5.5 i KI-erklæringen", "3": "Figur S3",
             "0.5": "\\vspace{0.5em}", "0.85": "includegraphics width (og OR 0,85 finnes i fryst)"}
nye = sorted(brief - fryst, key=lambda x: (len(x), x))
feil = [n for n in nye if n not in HVITLISTE]
print(f"tall i Brief Report: {len(brief)}; nye mot fryst: {len(nye)}; uforklarte: {feil}")

hoved = (HER / "main_brief.tex").read_text(encoding="utf-8")
ord_hoved = ordtelling(HER / "main_brief.tex", fra=r"\section{Introduction}", til=r"\section*{Acknowledgments}")
abs_m = re.search(r"\\section\*\{Abstract\}(.*?)\\vspace\{0\.5em\}", hoved, re.S)
abs_tekst = re.sub(r"\\[a-zA-Z]+\*?|[{}$\\]", " ", abs_m.group(1).replace(r"\,", ""))
abs_ord = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’.,–-]*", abs_tekst))
n_tab, n_fig = hoved.count(r"\begin{table}"), hoved.count(r"\begin{figure}")
keys = set(k for c in re.findall(r"\\cite\{([^}]*)\}", hoved) for k in c.split(","))
print(f"hovedtekst {ord_hoved} ord (≤1500), sammendrag {abs_ord} ord (≤100), {n_tab} tabell + {n_fig} figur (≤2), {len(keys)} referanser (≤20)")
if "companion" in hoved or "subjects" in hoved:
    feil.append("ordet «companion» eller «subjects» forekommer")
if ord_hoved > 1500 or abs_ord > 100 or n_tab + n_fig > 2 or len(keys) > 20:
    feil.append("en JSAMS-grense er overskredet")

TITTELSIDE = r"""%% JSAMS Brief Report title page (not for review). Written by kontroll_brief.py.
\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{times}
\usepackage[margin=2.5cm]{geometry}
\usepackage{setspace}
\doublespacing
\usepackage[colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}
\begin{document}

\noindent{\large Title page}

\bigskip
\noindent{\LARGE\bfseries Does starting age predict who stays? Competition debut and long-term participation in youth track and field\par}

\bigskip
\noindent\textbf{Running head:} Debut age and retention in youth athletics

\bigskip
\noindent\textbf{Author:} Atle G.\ Guttormsen$^{a}$ (\href{https://orcid.org/0000-0003-0188-8462}{ORCID 0000-0003-0188-8462})

\medskip
\noindent $^{a}$School of Economics and Business, Norwegian University of Life Sciences (NMBU), P.O.\ Box 5003, 1432 Ås, Norway

\medskip
\noindent\textbf{Corresponding author:} Atle G.\ Guttormsen, School of Economics and Business, Norwegian University of Life Sciences (NMBU), P.O.\ Box 5003, 1432 Ås, Norway. E-mail: atle.guttormsen@nmbu.no

\bigskip
\noindent\textbf{Article type:} Brief Report (resubmission of JSAMS-D-26-02238 in the format suggested by the Editor-in-Chief). \textbf{Sub-discipline:} Physical activity and public health.

\medskip
\noindent\textbf{Word count (excluding abstract and references):} __ORD__ \\
\textbf{Abstract word count:} __ABS__ \\
\textbf{Number of tables:} __TAB__ (main text); 6 supplementary tables \\
\textbf{Number of figures:} __FIG__ (main text); 3 supplementary figures \\
\textbf{Number of references:} __REF__

\medskip
\noindent\textbf{Preprint:} The manuscript is not available on a preprint server.

\medskip
\noindent\textbf{Declarations of interest:} none. The author maintains an open, non-commercial statistics platform built on the federation's public results database.

\medskip
\noindent\textbf{Funding:} This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.

\medskip
\noindent\textbf{Ethics:} The study analyses competition results registered by the Norwegian Athletics Federation and is not medical or health research as defined by Norway's Health Research Act (Helseforskningsloven \S\S~2 and 4), so approval by a Regional Committee for Medical and Health Research Ethics was not required. Sikt (the Norwegian Agency for Shared Services in Education and Research) confirmed that the use of the data raises no data-protection concerns. No participants were contacted or recruited, and informed consent was not required. No individual athlete is identified.

\medskip
\noindent\textbf{Author contributions:} AGG conceived the study, performed all analyses, and wrote the manuscript.

\medskip
\noindent\textbf{Related work:} A longitudinal performance-development study of the same registry is published in this journal (\emph{J Sci Med Sport} 2026, \href{https://doi.org/10.1016/j.jsams.2026.07.006}{doi:10.1016/j.jsams.2026.07.006}); it concerns performance trajectories, not retention, and is cited in the Introduction. Three further studies of the registry are cited in the manuscript: a relative-age study in press (\emph{Sports Medicine -- Open}), a competition-volume cohort study under review (\emph{International Journal of Sports Science \& Coaching}), and a performance-progression study under review (\emph{Psychology of Sport and Exercise}). They use different exposures and samples, and no text or result overlaps with the present manuscript.

\medskip
\noindent\textbf{Social media handle:} none.

\end{document}
"""
(HER / "title_page_brief.tex").write_text(
    TITTELSIDE.replace("__ORD__", str(ord_hoved)).replace("__ABS__", str(abs_ord))
    .replace("__TAB__", str(n_tab)).replace("__FIG__", str(n_fig)).replace("__REF__", str(len(keys))), encoding="utf-8")
print("skrev title_page_brief.tex")
if feil:
    print("FEIL:", feil)
    sys.exit(1)
