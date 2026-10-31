"""
tallkontroll_pse.py — kontrollerer at PSE-versjonen ikke inneholder tall som ikke står i det
fryste manuset (main.tex + additional_file_1.tex + manustabellene). Nye tall må stå i HVITLISTE
med begrunnelse. Kjøres etter bygg_pse.py.
"""
import re, sys
from pathlib import Path
HER = Path(__file__).resolve().parent
FRYST = HER.parent / "manus"

def tall(sti_liste):
    s = set()
    for sti in sti_liste:
        t = Path(sti).read_text(encoding="utf-8")
        t = re.sub(r"(?<!\\)%.*", "", t)                 # kommentarer
        t = t.split(r"\begin{document}", 1)[-1]           # preamble bort
        t = re.sub(r"\\(cite[pt]?|ref|label|input|includegraphics|graphicspath|addbibresource|usepackage|geometry)\*?(\[[^\]]*\])?\{[^}]*\}", " ", t)
        t = t.replace(r"\,", "")                          # 3\,877 → 3877
        s |= set(re.findall(r"\d+(?:[.,]\d+)*", t))
    return s

fryst = tall([FRYST / "main.tex", FRYST / "additional_file_1.tex"] + sorted(FRYST.glob("t*.tex")) + [FRYST / "s1.tex"])
pse = tall([HER / "main_anonymised.tex", HER / "supplement.tex"] + sorted(FRYST.glob("t*.tex")) + [FRYST / "s1.tex"])

HVITLISTE = {
    "648": "antall seniorer i utvalget på planstadiet (OSF_PREREGISTRATION.md, avsnitt 2)",
    "1.09": "observert SD for fødselskvartal i primærutvalget (analysedata.csv, 1,088)",
    "0.17": "hendelsesandel 648/3808 brukt i styrkeberegningen",
    "0.25": "antatt R² mellom progresjon og kovariater i styrkeberegningen",
    "1.15": "minste påviselig OR per SD, 80 % styrke (Hsieh 1998)",
    "1.18": "minste påviselig OR per SD, 90 % styrke",
    "1.14": "minste påviselig interaksjons-OR per kvartal, 80 % styrke",
    "80": "styrke 80 %", "90": "styrke 90 %", "0.05": "alfa",
    "1": "S1/H1-nummerering", "2": "S2/H2-nummerering", "3": "S3/H3-nummerering",
}
nye = sorted(pse - fryst, key=lambda x: (len(x), x))
ikke_forklart = [n for n in nye if n not in HVITLISTE]
print(f"tall i PSE-versjonen: {len(pse)}; i det fryste manuset: {len(fryst)}; nye: {len(nye)}")
for n in nye:
    print(f"  {n:>8}  {'OK: ' + HVITLISTE[n] if n in HVITLISTE else 'IKKE FORKLART'}")
mangler = sorted(fryst - pse, key=lambda x: (len(x), x))
print(f"tall i det fryste manuset som ikke lenger står i PSE-versjonen ({len(mangler)}): {' '.join(mangler)}")
sys.exit(1 if ikke_forklart else 0)
