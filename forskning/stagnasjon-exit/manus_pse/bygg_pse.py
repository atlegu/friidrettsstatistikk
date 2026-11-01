"""
bygg_pse.py — setter sammen PSE-versjonen (Psychology of Sport and Exercise) av A1
«Stagnation before exit» fra det fryste manuset ../manus/main.tex.

Det fryste manuset røres ikke. Resultat- og metodetekst kopieres linje for linje med
noen få ordbytter (tredje person om følgestudiene, tabell 4 til supplement, avvik fra
analyseplanen til supplement). Innledning, sammendrag, teori-avsnittet i diskusjonen
og sluttdelen er skrevet på nytt her. Ingen tall endres; tallkontroll_pse.py sjekker det.
"""
import re
from pathlib import Path

HER = Path(__file__).resolve().parent
ORIG = (HER.parent / "manus" / "main.tex").read_text(encoding="utf-8").split("\n")


def linjer(a, b):
    """1-indekserte, inklusive linjenumre i det fryste manuset."""
    return "\n".join(ORIG[a - 1:b])


def finn(tekst, start):
    for i, l in enumerate(ORIG, 1):
        if l.startswith(start):
            return i
    raise SystemExit(f"fant ikke {start!r}")


# ── Linjekart (kontrolleres mot overskriftene, så en flytting i originalen stopper bygget) ──
L_METODE = finn(ORIG, r"\section{Methods}")
L_RESULT = finn(ORIG, r"\section{Results}")
L_DISK = finn(ORIG, r"\section{Discussion}")
L_PRINC = finn(ORIG, r"\subsection{Principal findings}")
L_REL = finn(ORIG, r"\subsection{Relation to the companion registry studies}")
L_MAST = finn(ORIG, r"\subsection{What this means for the mastery interpretation}")
L_SEX = finn(ORIG, r"\subsection{The sex gap persists}")
L_PRAK = finn(ORIG, r"\subsection{Practical implications}")
L_STYR = finn(ORIG, r"\subsection{Strengths and limitations}")
L_KONK = finn(ORIG, r"\section{Conclusions}")
L_ABBR = finn(ORIG, r"\section*{Abbreviations}")

metode = linjer(L_METODE, L_RESULT - 1)
resultat = linjer(L_RESULT, L_DISK - 1)
princ = linjer(L_PRINC, L_REL - 1)
rel = linjer(L_REL, L_MAST - 1)
mast = linjer(L_MAST, L_SEX - 1)
sex = linjer(L_SEX, L_PRAK - 1)
prak = linjer(L_PRAK, L_STYR - 1)
styr = linjer(L_STYR, L_KONK - 1)
konk = linjer(L_KONK, L_ABBR - 1)


def bytt(tekst, gammel, ny, antall=1):
    n = tekst.count(gammel)
    if n != antall:
        raise SystemExit(f"ventet {antall} forekomst(er), fant {n}: {gammel[:70]!r}")
    return tekst.replace(gammel, ny)


# ── Metode ───────────────────────────────────────────────────────────────────
metode = bytt(metode, r"identical to the companion cohort study \cite{guttormsen2026dropout}",
              r"identical to the earlier cohort study of this registry \cite{guttormsen2026dropout}")
metode = bytt(metode, "mirroring the companion study", "mirroring the earlier cohort study")
metode = bytt(metode, r"deliberately the same ``level and change'' logic the companion study applied to competition volume \cite{guttormsen2026dropout}",
              r"deliberately the same ``level and change'' logic that \citet{guttormsen2026dropout} applied to competition volume")
metode = bytt(metode, "As for the companion study of the same registry, the study is not",
              "As for the earlier studies of the same registry, the study is not")
metode = bytt(metode, " A large language model (Claude, Anthropic) assisted with programming and manuscript drafting; the author reviewed and verified all code, output and text.", "")

# Avvik fra analyseplanen → supplement S3
m = re.search(r"Deviations from the analysis plan: (.*?)\n", metode, re.S)
if not m:
    raise SystemExit("fant ikke avviksavsnittet")
avvik = m.group(1).strip()
metode = metode.replace(m.group(0), "Deviations from the analysis plan are listed in the Supplementary material (Section S3).\n")
avvik = bytt(avvik, r"Table~\ref{tab:robust}", "Table S2")

# Utvalgsstørrelse og presisjon (nytt, PSE-krav)
STYRKE = r"""
\subsection{Sample size and precision}

The sample is the complete national population meeting the landmark condition, so no sampling decision was open to a power calculation. The size of the primary sample and the number of senior retainers were, however, known and recorded in the analysis plan before any exposure--outcome model was estimated (3\,808 athletes and 648 events at the plan stage; 3\,877 and 654 after the data corrections described above), and the effect size anchoring the design was the odds ratio of 2.04 per SD for baseline competition volume reported for the same outcome in the same registry \citep{guttormsen2026dropout}. By the method of \citet{hsieh1998} for a standardised continuous predictor in logistic regression, with an event probability of 0.17 and allowing for a squared multiple correlation of 0.25 between progression and the covariates, the plan-stage sample gave 80\,\% power at two-sided $\alpha$ = 0.05 to detect an odds ratio of about 1.15 per SD, and 90\,\% power for about 1.18, both far below the benchmark. For the H2 interaction, assuming progression and birth quarter to be uncorrelated and taking the observed SD of birth quarter (1.09), the same sample gave 80\,\% power for an interaction odds ratio of about 1.14 per quarter. Precision is reported throughout as 95\,\% confidence intervals.
"""
metode = bytt(metode, "is given in Additional file 1 (Table S1)", "is given in the Supplementary material (Table S1)")
metode = bytt(metode, r"\subsection{Ethics and transparency}", STYRKE.strip() + "\n\n" + r"\subsection{Ethics and transparency}")

# ── Resultater ───────────────────────────────────────────────────────────────
resultat = bytt(resultat, r"revisited in \S4.4", r"revisited in \S\ref{sec:sex}")
resultat = bytt(resultat, r"Table~\ref{tab:robust} collects the robustness analyses",
                "Table S2 in the Supplementary material collects the robustness analyses")
# Tabell 4 (robusthet) flyttes til supplementet
m = re.search(r"\\begin\{table\}\[H\]\n\\centering\n\\caption\{Robustness of the progression.*?\\end\{table\}\n", resultat, re.S)
if not m:
    raise SystemExit("fant ikke robusthetstabellen")
tabell_robust = m.group(0)
resultat = resultat.replace(m.group(0), "")

# ── Diskusjon ────────────────────────────────────────────────────────────────
princ = bytt(princ, r"of the same order as the baseline competition-volume coefficient the companion study reported (2.04 per SD at ages 13--14 \cite{guttormsen2026dropout})",
             r"of the same order as the baseline competition-volume coefficient reported for the same outcome by \citet{guttormsen2026dropout} (2.04 per SD at ages 13--14)")
rel = bytt(rel, r"\subsection{Relation to the companion registry studies}", r"\subsection{Relation to the earlier studies of the registry}")
rel = bytt(rel, "exactly what the companion study found for participation", r"exactly what \citet{guttormsen2026dropout} found for participation")
rel = bytt(rel, "(both in the companion's volume models and in ours)", "(both in that study's volume models and in ours)")

MAST_FORSTE = r"""The study was designed as the direct test the relative-age paper called for \citep{guttormsen2026rae}, and the outcome is split in an informative way. What the mastery construct adds beyond a generic ``commitment'' story is the reinforcement claim set out in the Introduction: athletes stay where they can observe their own progress, and the account therefore predicts heterogeneity by access to other reinforcement, rank above all. In this system the signals are concrete: athletes most directly observe times, distances and placings, while age-graded points are printed on Norwegian youth result lists and used for club awards, so the registry's progression measure is an objective correlate of signals athletes actually receive, not a researcher-only abstraction (though it is not perception itself)."""
m = re.search(r"The study was designed as the direct test.*?\(though it is not perception itself\)\.", mast, re.S)
if not m:
    raise SystemExit("fant ikke første avsnitt i mestringsdelen")
mast = mast.replace(m.group(0), MAST_FORSTE)
mast = bytt(mast, "which would bias the test toward the null.",
            "which would bias the test toward the null. In the terms of achievement goal theory, the data also cannot tell whether retained athletes experienced competence through self-referenced improvement or through the rank that improvement also buys; the null moderation shows only that the first source did not visibly compensate for the second where the second was scarcest.")

sex = bytt(sex, r"\subsection{The sex gap persists}", r"\subsection{The sex gap persists}\label{sec:sex}")
sex = bytt(sex, r"As in the companion cohort \cite{guttormsen2026dropout}", r"As in the earlier cohort study \citep{guttormsen2026dropout}")

prak = bytt(prak, r"the companion development study shows precisely that early rankings understate later development \cite{guttormsen2026development}", r"the development study shows precisely that early rankings understate later development \cite{guttormsen2026development}")
prak = bytt(prak, "both of the early-warning signals this research programme has now documented",
            "both of the early-warning signals the registry studies have now documented")
prak = bytt(prak, r"discussed for behavioural monitoring in the companion paper (legal basis, designated recipients, opt-out) \cite{guttormsen2026dropout}",
            r"discussed for behavioural monitoring by \citet{guttormsen2026dropout} (legal basis, designated recipients, opt-out)")

styr = bytt(styr, "and the deviations from it are listed in Methods.",
            "and the deviations from it are listed in the Supplementary material.")

# ── Felles ordbytter på kopiert tekst ─────────────────────────────────────────
def felles(t):
    t = t.replace(r"\cite{", r"\citep{")
    t = t.replace(r"\input{t", r"\input{../manus/t")
    return t

for navn in ("metode", "resultat", "princ", "rel", "mast", "sex", "prak", "styr", "konk", "avvik", "tabell_robust"):
    globals()[navn] = felles(globals()[navn])
for t in (metode, resultat, princ, rel, mast, sex, prak, styr, konk):
    if "companion" in t or "research programme" in t:
        raise SystemExit("gjenstående «companion»/«research programme»: " + t[t.find("companion") - 80:t.find("companion") + 80])

# ── Nye deler ────────────────────────────────────────────────────────────────
PREAMBLE = r"""\documentclass[12pt,a4paper]{article}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{times}
\usepackage[margin=2.5cm]{geometry}
\usepackage{setspace}
\doublespacing
\usepackage[british]{babel}
\usepackage{csquotes}

\usepackage{graphicx}
\graphicspath{{../figures/}}
\usepackage{float}
\usepackage{placeins}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{makecell}
\usepackage{enumitem}
\usepackage[colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}
\usepackage[style=apa,backend=biber,natbib=true]{biblatex}
\addbibresource{references.bib}
\usepackage{lineno}
\linenumbers

\begin{document}
"""

TITTEL = r"""
\begin{center}
{\LARGE\bfseries Stagnation before exit: performance progression and retention in youth track and field\par}
\vspace{0.6em}
{\normalsize Anonymised manuscript\par}
\end{center}
"""

SAMMENDRAG = r"""
\section*{Abstract}

\noindent Declining competition volume foreshadows exit from organised youth sport; whether the athlete's own performance development adds information is untested in population data. Mastery-experience accounts of motivation predict that visible personal progress retains athletes, most strongly where rank-based competence is scarce, as for athletes born late in the selection year. Using the Norwegian Athletics Federation's registry, we followed athletes born 1998--2005 with scorable age-graded points in their main event group at ages 13--14 and 15--16 (n = 3\,877; 53\,\% female), of whom 654 (16.9\,\%) were later active as seniors (age $\geq$20). Progression was the change in age-graded points (mean of three best scores) between the two windows. In logistic regression adjusted for sex, cohort, performance level, competition volume and the number of scored results, progression predicted senior activity (odds ratio [OR] 2.24 per SD, 95\,\% CI 1.90--2.63) and modestly improved discrimination (cross-validated AUC 0.854 to 0.866). The association replicated across birth cohorts and held at equal numbers of results, with event-equated points, and among athletes still competing after age 16 (OR 1.83). Aligned at exit, dropouts held their performance level until the final season and fell about 12 points below it as their competition volume collapsed. The pre-specified progression $\times$ birth-quarter interaction was null (OR 0.95, 95\,\% CI 0.84--1.06), and evidence for a mediated pathway was weak. Low progression accompanies and precedes exit, beyond volume and level, but the relative-age-specific form of the mastery prediction was not supported. Current form, not early rank, is what the retention signal tracks.

\vspace{0.5em}
\noindent\textbf{Keywords:} youth sport; dropout; athlete retention; performance development; mastery experience; relative age; track and field

\newpage
"""

INNLEDNING = r"""
\section{Introduction}

Withdrawal from organised youth sport is extensive, and its documented predictors are mostly motivational and structural rather than performance-related. Loss of enjoyment is the most consistently reported reason for leaving \citep{crane2015} and the main prospective predictor \citep{vanyperen2021}; costs and social background shape the reasons young people give for leaving \citep{espedalen2022}; a large share of turnover in talent systems is the system's own de-selection \citep{gullichbarth2026}, and much of the attrition at the youth-to-senior transition is structural rather than individual \citep{filo2026}; and markers of early specialisation have failed to predict actual dropout when tested directly \citep{larson2019}. Performance itself has an ambiguous role. Junior performance predicts senior performance poorly \citep{kearney2018,barth2022,gullich2025}, and in the most direct registry test to date, performance level at a single early milestone discriminated senior retention somewhat less well than a simple behavioural signal, how often the athlete competed, though it added complementary information \citep{guttormsen2026dropout}.

\subsection{Mastery experience as a retention mechanism}

There is, however, a theoretical reason to expect performance to matter for retention in a particular form: not as rank, but as the athlete's own visible progress. In the self-efficacy theory of \citet{bandura1977}, performance accomplishments, the enactive mastery experiences, are the most influential of the four sources of efficacy expectations: successes raise them and repeated failures lower them, and efficacy expectations in turn determine how much effort is expended and how long it is sustained. Seeing oneself improve at a task is therefore the most direct route to persisting at it. Perceived competence occupies the same position in self-determination theory, as one of the basic psychological needs whose satisfaction supports intrinsic motivation and persistence \citep{ryan2000}, and in the developmental model of effectance motivation of \citet{harter1978}, in which successful mastery attempts generate the positive affect that motivates further attempts. Achievement goal theory adds the distinction that makes the prediction testable with performance records. Under a self-referenced (task) conception of ability, improvement over one's own previous performance signals competence; under an other-referenced (ego) conception, competence is signalled by outperforming others \citep{nicholls1984}. A task-involved athlete can therefore experience competence while ranked low, provided they are improving. These accounts converge on one prediction: athletes stay where they can observe their own progress. Retrospective comparisons of dropouts with engaged athletes point in a related direction: dropouts had been the youngest in their training groups and had reached developmental milestones earlier \citep{fraserthomas2008}, and perceptions of competence recur among the factors associated with dropout across studies \citep{crane2015}.

Track and field is an unusually clean setting for this prediction. Every result is an objective, repeatable measure of the athlete's own performance, and in Norway age-graded points printed on youth result lists and used for club awards translate those marks into a common scale. Visible personal progress is therefore not a researcher's abstraction but a signal athletes actually receive. The prediction also has a specific corollary. Competence can be fed from two sources, self-referenced progress and other-referenced rank, and relatively younger athletes in a calendar-year class, who are on average less mature than their classmates, have less access to the second. If mastery experience retains athletes, it should do so most where rank cannot: the progression--retention association should be stronger among athletes born late in the selection year. A population-wide analysis of relative age in this registry, which found the birth-quarter skew fully established at age 10 and stable to age 25, proposed exactly this interpretation and stated the test: whether within-athlete performance \emph{progression}, rather than performance level, predicts retention among relatively younger athletes specifically \citep{guttormsen2026rae}.

\subsection{The gap}

Two further analyses of the same national registry frame the gap. A longitudinal study of performance development showed that a third to more than half of a cross-sectional youth top list is replaced from one year to the next, so that the best performers at one age are largely different people from the best at the next, and that the apparent late-teen plateau in such lists is an artefact of this compositional turnover; it did not study who exits or why \citep{guttormsen2026development}. A 14-year cohort study showed that exit is behaviourally foreshadowed: future dropouts' competition volume fell 12\,\% below their own earlier level two seasons before exit and 23\,\% one season before, and volume at ages 13--14 predicted senior retention better than age-graded performance level did \citep{guttormsen2026dropout}. To our knowledge, no study with complete national coverage has linked objective within-athlete performance trajectories to a prospectively defined exit outcome while adjusting for the behavioural participation signal.

\subsection{The present study}

This study performs that test. Among athletes still competing at ages 15--16, we ask three pre-specified questions. \textbf{H1:} does within-athlete progression from ages 13--14 to 15--16 predict being active as a senior, beyond sex, performance level, competition volume (level and change), and the number of results the progression measure is computed from? \textbf{H2:} is the association stronger among relatively younger athletes, as the reinforcement corollary of the mastery account predicts? \textbf{H3:} does progression, rather than level, carry the performance-related signal? Interpretation rules were fixed in advance. In particular, a null or weak H1 would \emph{not} falsify the mastery account, because the registry cannot distinguish disengagement from transfer to another sport in which the athlete is also progressing. The plan framed H2 as the mastery-specific test, so a positive H1 with a null H2 is consistent with a general progression--retention link without supporting the relative-age-specific mechanism. The analysis plan, including hypotheses, estimands, model specifications, and these interpretation rules, was written and committed to version control before any exposure--outcome model was estimated; the study was not preregistered on an external registry.

% ════════════════════════════════════════════════════════════
"""

SLUTT = r"""
% ── End matter (PSE) ────────────────────────────────────────

\section*{Data availability}

\noindent The competition records used in this study are publicly accessible via the Norwegian Athletics Federation's online register. The derived analysis dataset cannot be publicly shared because it contains personal data (athlete dates of birth) under the EU General Data Protection Regulation (GDPR). The full analysis code, with the time-stamped analysis plan and the aggregate estimation files, will be deposited in a public repository upon acceptance.

\section*{Supplementary material}

\noindent Table S1 (sample flow), Table S2 (robustness analyses), Section S3 (deviations from the analysis plan) and the completed STROBE checklist accompany the submission.

\section*{Declaration of generative AI and AI-assisted technologies in the manuscript preparation process}

\noindent During the preparation of this work the author used Anthropic Claude (Claude Opus 5.5) to improve language and readability, assist with structuring the text, check analysis code and identify errors. The author has checked the terms of use of the tool. After using this tool, the author reviewed and edited the content as needed and takes full responsibility for the content of the published article.

\printbibliography

\end{document}
"""

hoved = (PREAMBLE + TITTEL + SAMMENDRAG + INNLEDNING + "\n" + metode + "\n" + resultat + "\n"
         + r"\section{Discussion}" + "\n\n" + princ + "\n" + rel + "\n" + mast + "\n" + sex + "\n" + prak + "\n" + styr
         + "\n" + konk + "\n" + SLUTT)
(HER / "main_anonymised.tex").write_text(hoved, encoding="utf-8")

# ── Supplement ───────────────────────────────────────────────────────────────
s1 = (HER.parent / "manus" / "additional_file_1.tex").read_text(encoding="utf-8")
m = re.search(r"\\begin\{table\}\[H\].*?\\end\{table\}", s1, re.S)
tabell_s1 = m.group(0).replace(r"\input{s1}", r"\input{../manus/s1}")
tabell_s2 = tabell_robust.replace(r"\caption{Robustness", r"\caption*{\textbf{Table S2.} Robustness").replace(r"\label{tab:robust}", "")
SUPP = r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{times}
\usepackage[margin=2.5cm]{geometry}
\usepackage{float}
\usepackage{booktabs}
\usepackage{makecell}
\usepackage{caption}
\usepackage{graphicx}
\usepackage[british]{babel}
\usepackage{csquotes}
\usepackage[style=apa,backend=biber,natbib=true]{biblatex}
\addbibresource{references.bib}
\begin{document}

\noindent\textbf{Supplementary material}

\bigskip
\noindent{\large\bfseries Stagnation before exit: performance progression and retention in youth track and field\par}

\medskip
\noindent Anonymised manuscript. Table and section numbers follow the order of first citation in the main text.

""" + tabell_s1.replace(r"\caption*{\textbf{Table S1.} Sample flow.}", r"\caption*{\textbf{Table S1.} Sample flow.}") + r"""

""" + tabell_s2 + r"""

\section*{S3. Deviations from the analysis plan}

\noindent """ + avvik + r"""

\printbibliography[heading=none]

\end{document}
"""
(HER / "supplement.tex").write_text(SUPP, encoding="utf-8")
print("skrev main_anonymised.tex og supplement.tex")
