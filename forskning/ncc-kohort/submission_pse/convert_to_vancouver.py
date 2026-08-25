"""
Convert MANUSCRIPT_ANONYMIZED.md (APA author-year) to Sage Vancouver
(superscript numbers by order of first appearance) for IJSSC submission.

Produces MANUSCRIPT_IJSSC.md. The APA section files remain the working
sources; rerun compile_manuscript.py + this script after any edit, and
update the mapping tables below if citations are added/removed/reordered.

Numbering (order of first appearance, revised 2026-08-25 post-panel):
 1 Eime 2013            14 Cobley 2009          27 Cox 1972
 2 Crane & Temple 2015  15 DiFiori 2014         28 van Houwelingen 2007
 3 Enoksen 2011         16 Jayanthi 2015        29 VanderWeele & Ding 2017
 4 Battaglia 2024       17 Côté & Hancock 2016  30 Davidson-Pilon 2019
 5 Eliasson & Joh. 2021 18 Güllich 2022         31 Pedregosa 2011
 6 Scanlan 1993         19 Kuokkanen 2026       32 Hunter 2007
 7 Scanlan 2016         20 Worley & Smith 2026  33 Heidari 2016
 8 Kretchmar 2000       21 Zhong 2026           34 Raedeke 1997
 9 Ebaugh 1988          22 Back 2022            35 Espedalen 2025
10 Espedalen & S. 2024  23 Kearney & Hayes 2018 36 Larson 2019
11 Bakken 2019          24 von Elm 2007         37 Baker 2021
12 Wall & Côté 2007     25 NFIF 2026 (rules)
13 Sarrazin 2002        26 NFIF 2024 (Tyrving)
"""

import re
from pathlib import Path

HERE = Path(__file__).parent

def sup(*nums):
    return "<sup>" + ",".join(str(n) for n in nums) + "</sup>"

# Parenthetical citations: (exact APA string incl. leading space, replacement).
# Applied longest-first; a trailing "." or "," in the text is hopped over.
PAREN = [
    (" (DiFiori et al., 2014; Jayanthi et al., 2015; Côté & Hancock, 2016; Güllich et al., 2022)", "<sup>15–18</sup>"),
    (" (Kuokkanen et al., 2026; Worley & Smith, 2026; Zhong et al., 2026)", "<sup>19–21</sup>"),
    (" (Ebaugh, 1988; Eliasson & Johansson, 2021)", sup(5, 9)),
    (" (Bakken, 2019; Scanlan et al., 2016)", sup(7, 11)),
    (" (Côté & Hancock, 2016; Güllich et al., 2022)", sup(17, 18)),
    ("(24.3%; Enoksen, 2011)", "(24.3%)<sup>3</sup>"),
    (" (Scanlan et al., 1993, 2016)", sup(6, 7)),
    (" (Scanlan et al., 2016)", sup(7)),
    (" (Eime et al., 2013)", sup(1)),
    (" (Crane & Temple, 2015)", sup(2)),
    (" (Enoksen, 2011)", sup(3)),
    (" (Eliasson & Johansson, 2021)", sup(5)),
    (" (Kretchmar, 2000)", sup(8)),
    (" (Espedalen & Seippel, 2024)", sup(10)),
    (" (Espedalen, 2025)", sup(35)),
    (" (Bakken, 2019)", sup(11)),
    (" (Wall & Côté, 2007)", sup(12)),
    (" (Cobley et al., 2009)", sup(14)),
    (" (Back et al., 2022)", sup(22)),
    (" (Kearney & Hayes, 2018)", sup(23)),
    (" (von Elm et al., 2007)", sup(24)),
    (" (Norges Friidrettsforbund, 2026)", sup(25)),
    (" (Norges Friidrettsforbund, 2024)", sup(26)),
    (" (Cox, 1972)", sup(27)),
    (" (van Houwelingen, 2007)", sup(28)),
    (" (VanderWeele & Ding, 2017)", sup(29)),
    (" (Davidson-Pilon, 2019)", sup(30)),
    (" (Pedregosa et al., 2011)", sup(31)),
    (" (Hunter, 2007)", sup(32)),
    (" (Heidari et al., 2016)", sup(33)),
    (" (Raedeke, 1997)", sup(34)),
    (" (Larson et al., 2019)", sup(36)),
    (" (Baker et al., 2021)", sup(37)),
]

# Narrative citations: author name kept, year dropped, number attached (with
# punctuation hop for a trailing "." or ",").
NARRATIVE = [
    ("Battaglia et al. (2024)", "Battaglia et al." + sup(4)),
    ("Eliasson and Johansson (2021)", "Eliasson and Johansson" + sup(5)),
    ("Ebaugh's (1988)", "Ebaugh's" + sup(9)),
    ("Enoksen's (2011)", "Enoksen's" + sup(3)),
    ("Kretchmar's (2000)", "Kretchmar's" + sup(8)),
    ("Sarrazin et al.'s (2002)", "Sarrazin et al.'s" + sup(13)),
]

REFERENCES = """## References

1. Eime RM, Young JA, Harvey JT, et al. A systematic review of the psychological and social benefits of participation in sport for children and adolescents: informing development of a conceptual model of health through sport. *Int J Behav Nutr Phys Act* 2013; 10: 98. DOI: 10.1186/1479-5868-10-98.
2. Crane J and Temple V. A systematic review of dropout from organized sport among children and youth. *Eur Phys Educ Rev* 2015; 21: 114–131. DOI: 10.1177/1356336X14555294.
3. Enoksen E. Drop-out rate and drop-out reasons among promising Norwegian track and field athletes: a 25 year study. *Scand Sport Stud Forum* 2011; 2: 19–43.
4. Battaglia A, Kerr G and Tamminen K. The dropout from youth sport crisis: not as simple as it appears. *Kinesiol Rev* 2024; 13: 345–356. DOI: 10.1123/kr.2023-0024.
5. Eliasson I and Johansson A. The disengagement process among young athletes when withdrawing from sport: a new research approach. *Int Rev Sociol Sport* 2021; 56: 537–557. DOI: 10.1177/1012690219899614.
6. Scanlan TK, Carpenter PJ, Simons JP, et al. An introduction to the sport commitment model. *J Sport Exerc Psychol* 1993; 15: 1–15. DOI: 10.1123/jsep.15.1.1.
7. Scanlan TK, Chow GM, Sousa C, et al. The development of the Sport Commitment Questionnaire-2 (English version). *Psychol Sport Exerc* 2016; 22: 233–246. DOI: 10.1016/j.psychsport.2015.08.002.
8. Kretchmar RS. Movement subcultures: sites for meaning. *J Phys Educ Recreat Dance* 2000; 71(5): 19–25. DOI: 10.1080/07303084.2000.10605140.
9. Ebaugh HRF. *Becoming an ex: the process of role exit*. Chicago: University of Chicago Press, 1988.
10. Espedalen LE and Seippel Ø. Dropout and social inequality: young people's reasons for leaving organized sports. *Ann Leis Res* 2024; 27: 197–214. DOI: 10.1080/11745398.2022.2070512.
11. Bakken A. *Idrettens posisjon i ungdomstida: hvem deltar og hvem slutter i ungdomsidretten?* [The position of sport in adolescence: who participates and who drops out of youth sport?]. NOVA Rapport 2/2019. Oslo: Oslo Metropolitan University, 2019.
12. Wall M and Côté J. Developmental activities that lead to dropout and investment in sport. *Phys Educ Sport Pedagogy* 2007; 12: 77–87. DOI: 10.1080/17408980601060358.
13. Sarrazin P, Vallerand R, Guillet E, et al. Motivation and dropout in female handballers: a 21-month prospective study. *Eur J Soc Psychol* 2002; 32: 395–418. DOI: 10.1002/ejsp.98.
14. Cobley S, Baker J, Wattie N, et al. Annual age-grouping and athlete development: a meta-analytical review of relative age effects in sport. *Sports Med* 2009; 39: 235–256. DOI: 10.2165/00007256-200939030-00005.
15. DiFiori JP, Benjamin HJ, Brenner JS, et al. Overuse injuries and burnout in youth sports: a position statement from the American Medical Society for Sports Medicine. *Clin J Sport Med* 2014; 24: 3–20. DOI: 10.1097/JSM.0000000000000060.
16. Jayanthi NA, LaBella CR, Fischer D, et al. Sports-specialized intensive training and the risk of injury in young athletes: a clinical case-control study. *Am J Sports Med* 2015; 43: 794–801. DOI: 10.1177/0363546514567298.
17. Côté J and Hancock DJ. Evidence-based policies for youth sport programmes. *Int J Sport Policy Polit* 2016; 8: 51–65. DOI: 10.1080/19406940.2014.919338.
18. Güllich A, Macnamara BN and Hambrick DZ. What makes a champion? Early multidisciplinary practice, not early specialization, predicts world-class performance. *Perspect Psychol Sci* 2022; 17: 6–29. DOI: 10.1177/1745691620974772.
19. Kuokkanen J, Phipps DJ, Saarinen M, et al. Trajectories of sport exhaustion, cynicism and inadequacy among adolescent student-athletes: a three-year longitudinal study of social influences in the Finnish dual career context. *Psychol Sport Exerc* 2026; 82: 103015. DOI: 10.1016/j.psychsport.2025.103015.
20. Worley JT and Smith AL. Positive peer relationships, social identity, and adaptive sport motivation in youth athletes. *Psychol Sport Exerc* 2026; 82: 102996. DOI: 10.1016/j.psychsport.2025.102996.
21. Zhong J, Wang Q, Bao H, et al. Effects of basic psychological needs on Chinese youth athlete burnout under coach burnout: using hierarchical linear modeling. *Psychol Sport Exerc* 2026; 85: 103099. DOI: 10.1016/j.psychsport.2026.103099.
22. Back J, Johnson U, Svedberg P, et al. Drop-out from team sport among adolescents: a systematic review and meta-analysis of prospective studies. *Psychol Sport Exerc* 2022; 61: 102205. DOI: 10.1016/j.psychsport.2022.102205.
23. Kearney PE and Hayes PR. Excelling at youth level in competitive track and field athletics is not a prerequisite for later success. *J Sports Sci* 2018; 36: 2502–2509. DOI: 10.1080/02640414.2018.1465724.
24. von Elm E, Altman DG, Egger M, et al. The Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) statement: guidelines for reporting observational studies. *Ann Intern Med* 2007; 147: 573–577. DOI: 10.7326/0003-4819-147-8-200710160-00010.
25. Norges Friidrettsforbund. Konkurranseregler og bestemmelser [Competition rules and regulations], https://www.friidrett.no/lover-og-regler/ (2026, accessed 25 August 2026).
26. Norges Friidrettsforbund. Tyrvingtabellen: poengtabell for ungdomsfriidrett [Tyrving table: scoring table for youth athletics], https://www.friidrett.no/arrangement/arrangementshjelp/poengtabeller/tyrvingtabellen/ (2024, accessed 25 August 2026).
27. Cox DR. Regression models and life-tables. *J R Stat Soc Series B Stat Methodol* 1972; 34: 187–202. DOI: 10.1111/j.2517-6161.1972.tb00899.x.
28. van Houwelingen HC. Dynamic prediction by landmarking in event history analysis. *Scand J Stat* 2007; 34: 70–85. DOI: 10.1111/j.1467-9469.2006.00529.x.
29. VanderWeele TJ and Ding P. Sensitivity analysis in observational research: introducing the E-value. *Ann Intern Med* 2017; 167: 268–274. DOI: 10.7326/M16-2607.
30. Davidson-Pilon C. lifelines: survival analysis in Python. *J Open Source Softw* 2019; 4(40): 1317. DOI: 10.21105/joss.01317.
31. Pedregosa F, Varoquaux G, Gramfort A, et al. Scikit-learn: machine learning in Python. *J Mach Learn Res* 2011; 12: 2825–2830.
32. Hunter JD. Matplotlib: a 2D graphics environment. *Comput Sci Eng* 2007; 9(3): 90–95. DOI: 10.1109/MCSE.2007.55.
33. Heidari S, Babor TF, De Castro P, et al. Sex and Gender Equity in Research: rationale for the SAGER guidelines and recommended use. *Res Integr Peer Rev* 2016; 1: 2. DOI: 10.1186/s41073-016-0007-6.
34. Raedeke TD. Is athlete burnout more than just stress? A sport commitment perspective. *J Sport Exerc Psychol* 1997; 19: 396–417. DOI: 10.1123/jsep.19.4.396.
35. Espedalen LE. *Organized sport in the lives of young Norwegians: participation, exit, and social inequality*. PhD Thesis, Norwegian School of Sport Sciences, Norway, 2025.
36. Larson HK, Young BW, McHugh TLF, et al. Markers of early specialization and their relationships with burnout and dropout in swimming. *J Sport Exerc Psychol* 2019; 41: 46–54. DOI: 10.1123/jsep.2018-0305.
37. Baker J, Mosher A and Fraser-Thomas J. Is it too early to condemn early sport specialisation? *Br J Sports Med* 2021; 55: 179–180. DOI: 10.1136/bjsports-2020-102053.
"""

text = (HERE / "MANUSCRIPT_ANONYMIZED.md").read_text()

# Swap the reference section (everything from "## References")
head, _ = text.split("## References", 1)
text = head + REFERENCES

# Narrative citations; hop a trailing "." or "," per Sage style
for old, new in NARRATIVE:
    m = re.match(r"^(.*?)(<sup>[\d,–-]+</sup>)$", new)
    text = re.sub(re.escape(old) + r"([.,]?)",
                  m.group(1).replace("\\", "\\\\") + r"\1" + m.group(2), text)

# Parenthetical citations; hop a trailing "." or ","
for old, new in PAREN:
    if new.startswith("("):
        text = text.replace(old, new)
    else:
        text = re.sub(re.escape(old) + r"([.,]?)", r"\1" + new, text)

(HERE / "MANUSCRIPT_IJSSC.md").write_text(text)

# Build the Word file via pandoc. Pandoc's docx writer DROPS raw-HTML <sup>
# tags from markdown input (numbers would render as plain text), so convert
# to pandoc's native superscript syntax (^5^) first.
import subprocess
pandoc_md = re.sub(r"<sup>([^<]+)</sup>", r"^\1^", text)
tmp = HERE / ".MANUSCRIPT_IJSSC_pandoc.md"
tmp.write_text(pandoc_md)
subprocess.run(["pandoc", str(tmp), "-o", str(HERE / "MANUSCRIPT_IJSSC.docx")], check=True)
tmp.unlink()

# Verify: no APA-style citations should remain in the body
body = text[: text.index("## References")]
leftovers = [m.group(0) for m in re.finditer(r"\([^()]*\b(?:19|20)\d{2}[^()]*\)", body)
             if re.search(r"[A-Za-z]{3,}[^()]*\d{4}|\d{4}[^()]*[A-Za-z]{3,}", m.group(0))]
sups = len(re.findall(r"<sup>", body))
main = body[body.index("## 1. Introduction"): body.index("## Acknowledgements")]
print(f"Wrote MANUSCRIPT_IJSSC.md + .docx ({sups} superscript citations; main text {len(main.split())} words)")
print("Parenthesized year-strings remaining (must NOT be citations):")
for l in leftovers:
    print(f"  {l}")
