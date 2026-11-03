"""
bygg_jsams.py — setter sammen JSAMS-versjonen (Journal of Science and Medicine in Sport,
Original Research) av A3 «Does starting age predict who stays?» fra det fryste manuset
../manus/main.tex.

Det fryste manuset røres ikke. Innledning, metode, resultater og diskusjon kopieres linje for
linje med noen få ordbytter (Methods-overskrift, tabell 3 og 4 ut av hovedteksten for å komme
under JSAMS' tak på seks visningselementer). Strukturert sammendrag, nøkkelord, konklusjon,
praktiske implikasjoner, sluttdel, tittelside og supplement er skrevet her. Ingen tall endres;
tallkontroll_jsams.py sjekker det.

JSAMS-krav (forfatterveiledningen, lest 01.11.2026): ≤5 000 ord uten sammendrag/tabeller/
figurtekster/takk/referanser; høyst 6 tabeller+figurer; ≤40 referanser; strukturert sammendrag
≤250 ord (Objectives, Design, Methods, Results, Conclusions); ≤6 nøkkelord, minst 4 MeSH, ikke ord
fra tittelen; Introduction–Methods–Results–Discussion–Conclusion–Practical implications–
Acknowledgments–KI-erklæring–References; dobbelt anonymisert (egen tittelside); «p» liten med
ledende null; ikke «subjects».
"""
import re
import sys
from pathlib import Path

HER = Path(__file__).resolve().parent
sys.path.insert(0, str(HER.parent.parent))
from audit_felles import ordtelling  # noqa: E402

ORIG = (HER.parent / "manus" / "main.tex").read_text(encoding="utf-8").split("\n")


def finn(start):
    for i, l in enumerate(ORIG, 1):
        if l.startswith(start):
            return i
    raise SystemExit(f"fant ikke {start!r}")


def linjer(a, b):
    return "\n".join(ORIG[a - 1:b])


def bytt(tekst, gammel, ny, antall=1):
    n = tekst.count(gammel)
    if n != antall:
        raise SystemExit(f"ventet {antall} forekomst(er), fant {n}: {gammel[:70]!r}")
    return tekst.replace(gammel, ny)


# ── Linjekart (stopper hvis det fryste manuset er omorganisert) ──────────────
L_INTRO = finn(r"\section{Introduction}")
L_METODE = finn(r"\section{Materials and methods}")
L_RESULT = finn(r"\section{Results}")
L_DISK = finn(r"\section{Discussion}")
L_PERSP = finn(r"\section{Perspective}")
L_DEKL = finn(r"\section*{Declarations}")

intro = linjer(L_INTRO, L_METODE - 1)
metode = linjer(L_METODE, L_RESULT - 1)
resultat = linjer(L_RESULT, L_DISK - 1)
disk = linjer(L_DISK, L_PERSP - 1)
persp = linjer(L_PERSP, L_DEKL - 1)

# ── Metode ───────────────────────────────────────────────────────────────────
metode = bytt(metode, r"\section{Materials and methods}", r"\section{Methods}")

# ── De to manusene som ennå ikke er antatt: JSAMS vil ha dem som «unpublished data» i teksten,
#    ikke i referanselisten; og «companion» røper forfatteren i et dobbelt anonymisert manus ──
intro = bytt(intro, r"and that exit is preceded by behavioural withdrawal \cite{guttormsen2026dropout}.",
             "and that exit is preceded by behavioural withdrawal (unpublished data).")
intro = bytt(intro, r"A companion study of performance trajectories found that progression predicts retention beyond volume, but that, here too, the \emph{recent} window dominates the earlier one \cite{guttormsen2026progression}.",
             r"A further study of performance trajectories in the registry found that progression predicts retention beyond volume, but that, here too, the \emph{recent} window dominates the earlier one (unpublished data).")
intro = bytt(intro, r"current behaviour dominates history \cite{guttormsen2026dropout,guttormsen2026progression}?",
             "current behaviour dominates history (unpublished data)?")
metode = bytt(metode, r"identical to the companion studies \cite{guttormsen2026dropout,guttormsen2026progression}",
              "identical to the earlier studies of this registry (unpublished data)")
metode = bytt(metode, "As for the companion registry studies, the study is not",
              "As for the earlier studies of the same registry, the study is not")
resultat = bytt(resultat, r"what the companion studies found for early competition volume \cite{guttormsen2026dropout} and early performance \cite{guttormsen2026progression}:",
                "what earlier analyses of this registry found for early competition volume and early performance (unpublished data):")
disk = bytt(disk, "a pattern that companion analyses of this registry found with two other exposures.",
            "a pattern that earlier analyses of this registry found with two other exposures (unpublished data).")
disk = bytt(disk, r"but later volume dominates it \cite{guttormsen2026dropout}.", "but later volume dominates it.")
disk = bytt(disk, r"but through the most recent window \cite{guttormsen2026progression}.", "but through the most recent window.")
for t in (intro, metode, resultat, disk):
    if "companion" in t or "guttormsen2026dropout" in t or "guttormsen2026progression" in t:
        raise SystemExit("gjenstående «companion» eller sitering av upublisert manus")

# ── Resultater: tabell 3 (varighet) og tabell 4 (robusthet) ut av hovedteksten ──
m = re.search(r"\\begin\{table\}\[H\]\n\\centering\n\\caption\{Proportion still competing.*?\\end\{table\}\n\n", resultat, re.S)
if not m:
    raise SystemExit("fant ikke varighetstabellen")
resultat = resultat.replace(m.group(0), "")   # tallene står i teksten, figur 3 og tabell S3

m = re.search(r"\\begin\{table\}\[H\]\n\\centering\n\\caption\{Robustness analyses\..*?\\end\{table\}\n\n", resultat, re.S)
if not m:
    raise SystemExit("fant ikke robusthetstabellen")
tabell_robust = m.group(0)
resultat = resultat.replace(m.group(0), "")

resultat = bytt(resultat, r"Aligned on time since debut (Table~\ref{tab:retention}; Figure~\ref{fig:retk})",
                r"Aligned on time since debut (Figure~\ref{fig:retk})")
resultat = bytt(resultat, r"Table~\ref{tab:robust}", "Supplementary Table S5", antall=3)
for t in (intro, metode, resultat, disk):
    if r"\ref{tab:retention}" in t or r"\ref{tab:robust}" in t:
        raise SystemExit("gjenstående henvisning til flyttet tabell")

# Tabellfilene ligger i ../manus
for navn in ("metode", "resultat", "tabell_robust"):
    globals()[navn] = globals()[navn].replace(r"\input{t", r"\input{../manus/t")

# ── Nye deler ────────────────────────────────────────────────────────────────
PREAMBLE = r"""%% Journal of Science and Medicine in Sport — Original Research (anonymised manuscript)
%% Built by bygg_jsams.py from the frozen ../manus/main.tex. Do not edit by hand.
\documentclass[12pt,a4paper]{article}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{times}
\usepackage[margin=2.5cm]{geometry}
\usepackage{setspace}
\doublespacing

\usepackage{graphicx}
\graphicspath{{../figures/}}
\usepackage{float}
\usepackage{placeins}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{caption}
\usepackage{enumitem}
\usepackage[colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}
\usepackage[numbers,sort&compress]{natbib}
\usepackage{lineno}
\linenumbers

\begin{document}
"""

TITTEL = r"""
\begin{center}
{\LARGE\bfseries Does starting age predict who stays? Competition debut and long-term participation in youth track and field\par}
\vspace{0.5em}
{\normalsize Anonymised manuscript (Original Research)\par}
\end{center}
"""

SAMMENDRAG = r"""
\section*{Abstract}

\noindent\textbf{Objectives:} To test whether age at first registered competition predicts long-term participation, and whether entry history adds information beyond current engagement.

\noindent\textbf{Design:} Registry-based cohort study.

\noindent\textbf{Methods:} All athletes born 2001--2005 with a first registered competition at ages 10--16 (n = 17\,496; 50\,\% female) were followed in the national athletics registry to October 2026. The outcome was senior activity (two or more results in a season from age 20). Debut age was modelled categorically and linearly by logistic regression adjusted for sex, cohort and club size; persistence was compared at equal career length; a landmark analysis at age 17 added current competition volume.

\noindent\textbf{Results:} 546 (3.1\,\%) became active seniors. Conversion was U-shaped (non-linearity p $<$ 0.001): relative to debut at 10, adjusted odds were lowest for debuts at 11--14 (odds ratio 0.53--0.75) and equal by 15, with a null linear trend (odds ratio 0.99 per year, 95\,\% confidence interval [CI] 0.94--1.04). At equal career length, later starters persisted less: 20.4\,\% of those debuting at 10 competed four or more years later, against 4.5--6.6\,\% for debuts at 14--16 (odds ratio 0.70 per year, 95\,\% CI 0.68--0.72). At the age-17 landmark, earlier debut appeared advantageous (odds ratio 0.85 per year, 95\,\% CI 0.80--0.90) but not after adjusting for current volume (odds ratio 0.99, 95\,\% CI 0.92--1.05).

\noindent\textbf{Conclusions:} Early competitive entry did not undermine retention: per year of career, early entrants persisted longest. Among older adolescents, current engagement predicted retention better than entry history.

\vspace{0.5em}
\noindent\textbf{Keywords:} Athletes$^\dagger$; Adolescent$^\dagger$; Child$^\dagger$; Registries$^\dagger$; Cohort studies$^\dagger$; attrition

\noindent{\footnotesize $^\dagger$Medical Subject Headings (MeSH) term.}

\newpage
"""

KONKLUSJON = r"""
% ════════════════════════════════════════════════════════════
\section{Conclusion}

In the complete entry population of Norwegian youth track and field, age at first registered competition carried no simple message about who would still be competing as an adult, and early entry carried no retention penalty: per year of career, the earliest entrants persisted longest, and no entry age from 10 to 19 failed to produce senior athletes. The decisive window was the first season or two after entry, whatever the entry age, and among athletes competing at 17, current engagement carried most of the predictive information that entry history might have offered. The latest entrants' high per-head conversion at a fixed adult age plausibly reflects their short distance to that age and self-selection rather than an advantage of entering late, so adolescents recruited into entry who would not have come on their own cannot be assumed to convert at the observed 6.6\,\% (5.4\,\% among debuts outside the COVID-19 seasons), and the late channel as observed is male-tilted. All of these statements concern participation in registered athletics, not sport participation or physical activity in general.

\section{Practical implications}

\begin{itemize}[leftmargin=*]
\item Starting competitive athletics at the earliest allowed age did not make children more likely to quit. Those who started at 10 stayed longest, year for year.
\item No age is too late to start: every entry age from 10 to 19 produced athletes who were still competing as adults.
\item Most leaving happens in the first season or two after entry, whatever the starting age. Effort to keep young athletes is better aimed at the newcomer's first seasons than at the timing of entry.
\item By late adolescence, how much an athlete currently competes says more about who stays than when they started.
\end{itemize}
"""

SLUTT = r"""
\section*{Acknowledgments}

\noindent The author thanks the Norwegian Athletics Federation, whose systematic registration of competition results makes population research of this kind possible. This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors. Declarations of interest: none; the author maintains an open, non-commercial statistics platform built on the federation's public results database.

\section*{Data availability}

\noindent The competition records used in this study are publicly accessible via the Norwegian Athletics Federation's online register for ages 13 and above; records for the 10--12 age classes are not publicly released by the federation. The derived analysis dataset cannot be publicly shared because it contains personal data (athlete dates of birth) under the EU General Data Protection Regulation (GDPR). The full analysis code, with the time-stamped analysis plan, will be deposited in a public repository upon acceptance. Supplementary Tables S1--S5 accompany the submission.

\section*{Declaration of generative AI and AI-assisted technologies in the writing process}

\noindent During the preparation of this work the author used Anthropic Claude (Claude Opus 5.5) in order to improve language and readability, assist with structuring the text, check analysis code and identify errors. After using this tool, the author reviewed and edited the content as needed and takes full responsibility for the content of the publication.

\bibliographystyle{jsams}
\bibliography{references}

\end{document}
"""

hoved = PREAMBLE + TITTEL + SAMMENDRAG + intro + "\n" + metode + "\n" + resultat + "\n" + disk + "\n" + KONKLUSJON + SLUTT
(HER / "main_anonymised.tex").write_text(hoved, encoding="utf-8")

# ── Kontroller på den ferdige hovedfilen ─────────────────────────────────────
n_tab = hoved.count(r"\begin{table}")
n_fig = hoved.count(r"\begin{figure}")
if n_tab + n_fig > 6:
    raise SystemExit(f"{n_tab} tabeller + {n_fig} figurer > 6")
abs_m = re.search(r"\\section\*\{Abstract\}(.*?)\\vspace\{0\.5em\}", hoved, re.S)
abs_tekst = re.sub(r"\\[a-zA-Z]+\*?|[{}$\\]", " ", abs_m.group(1))
abs_ord = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’.,–-]*", abs_tekst.replace(r"\,", "")))
if abs_ord > 250:
    raise SystemExit(f"sammendraget har {abs_ord} ord (> 250)")
ord_hoved = ordtelling(HER / "main_anonymised.tex", fra=r"\section{Introduction}", til=r"\section*{Acknowledgments}")
if ord_hoved > 5000:
    raise SystemExit(f"hovedteksten har {ord_hoved} ord (> 5 000)")
n_ref = len(re.findall(r"^@", (HER / "references.bib").read_text(encoding="utf-8"), re.M))
for key in re.findall(r"^@\w+\{([^,]+),", (HER / "references.bib").read_text(encoding="utf-8"), re.M):
    if ("\\cite{" + key) not in hoved and ("," + key) not in hoved:
        raise SystemExit(f"referanse uten sitering: {key}")
if "subjects" in hoved:
    raise SystemExit("«subjects» forekommer")
for cite in re.findall(r"\\cite\{([^}]*)\}", hoved):
    if cite.count(",") >= 3:
        raise SystemExit(f"mer enn tre referanser på ett punkt: {cite}")


def avrund_hundre(n):
    return f"{int(round(n, -2)):,}".replace(",", "\\,")


# ── Tittelside ───────────────────────────────────────────────────────────────
TITTELSIDE = r"""%% JSAMS title page (not for review). Built by bygg_jsams.py.
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
\noindent\textbf{Article type:} Original Research. \textbf{Sub-discipline:} Physical activity and public health.

\medskip
\noindent\textbf{Word count (excluding abstract and references):} $\sim$__ORD__ \\
\textbf{Abstract word count:} __ABS__ \\
\textbf{Number of tables:} __TAB__ (main text); 5 supplementary tables \\
\textbf{Number of figures:} __FIG__ \\
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
TITTELSIDE = (TITTELSIDE.replace("__ORD__", avrund_hundre(ord_hoved)).replace("__ABS__", str(abs_ord))
              .replace("__TAB__", str(n_tab)).replace("__FIG__", str(n_fig)).replace("__REF__", str(n_ref)))
(HER / "title_page.tex").write_text(TITTELSIDE, encoding="utf-8")

# ── Supplement: S1–S4 fra det fryste supplementet + S5 (robusthet) ───────────
supp_orig = (HER.parent / "manus" / "supplement.tex").read_text(encoding="utf-8")
m = re.search(r"\\section\*\{Supporting Information\}\n(.*?)\\end\{document\}", supp_orig, re.S)
if not m:
    raise SystemExit("fant ikke tabellene i det fryste supplementet")
s1_4 = m.group(1).replace(r"\input{s", r"\input{../manus/s")
s5 = (tabell_robust.replace(r"\caption{Robustness analyses.", r"\caption*{\textbf{Table S5.} Robustness analyses.")
      .replace("\\label{tab:robust}\n", ""))
SUPP = r"""%% JSAMS supplementary material (anonymised). Built by bygg_jsams.py.
\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{times}
\usepackage[margin=2.5cm]{geometry}
\usepackage{float}
\usepackage{booktabs}
\usepackage{caption}
\begin{document}

\noindent\textbf{Supplementary material}

\bigskip
\noindent{\large\bfseries Does starting age predict who stays? Competition debut and long-term participation in youth track and field\par}

\medskip
\noindent Anonymised manuscript. Tables S1--S4 are numbered in the order of first citation in the main text; Table S5 collects the robustness analyses cited in Sections 3.2 and 3.5.

""" + s1_4 + "\n" + s5 + r"""
\end{document}
"""
(HER / "supplement.tex").write_text(SUPP, encoding="utf-8")

print(f"skrev main_anonymised.tex ({ord_hoved} ord hovedtekst, sammendrag {abs_ord} ord, "
      f"{n_tab} tabeller + {n_fig} figurer, {n_ref} referanser), title_page.tex og supplement.tex")
