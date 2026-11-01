"""
tallkontroll_jsams.py — kontrollerer at JSAMS-versjonen ikke inneholder tall som ikke står i det
fryste manuset (main.tex + supplement.tex + tabellfilene). Nye tall må stå i HVITLISTE med
begrunnelse. Tittelsiden kontrolleres ikke (ordtellingen der regnes ut av bygg_jsams.py).
Kjøres etter bygg_jsams.py.
"""
import re
import sys
from pathlib import Path

HER = Path(__file__).resolve().parent
FRYST = HER.parent / "manus"


def tall(sti_liste):
    s = set()
    for sti in sti_liste:
        t = Path(sti).read_text(encoding="utf-8")
        t = re.sub(r"(?<!\\)%.*", "", t)
        t = t.split(r"\begin{document}", 1)[-1]
        t = re.sub(r"\\(cite[pt]?|ref|label|input|includegraphics|graphicspath|bibliography|usepackage|geometry)\*?(\[[^\]]*\])?\{[^}]*\}", " ", t)
        t = t.replace(r"\,", "")
        s |= set(re.findall(r"\d+(?:[.,]\d+)*", t))
    return s


tabeller = sorted(FRYST.glob("t?.tex")) + sorted(FRYST.glob("s?.tex"))
fryst = tall([FRYST / "main.tex", FRYST / "supplement.tex"] + tabeller)
jsams = tall([HER / "main_anonymised.tex", HER / "supplement.tex"] + tabeller)

HVITLISTE = {
    "5": "Tabell S5 (robusthetstabellen, flyttet til supplementet) og «3.5» (robusthetsavsnittet)",
    "3.5": "henvisning til avsnitt 3.5 i supplementet",
    "5.5": "Claude Opus 5.5 i KI-erklæringen",
}
nye = sorted(jsams - fryst, key=lambda x: (len(x), x))
ikke_forklart = [n for n in nye if n not in HVITLISTE]
print(f"tall i JSAMS-versjonen: {len(jsams)}; i det fryste manuset: {len(fryst)}; nye: {len(nye)}")
for n in nye:
    print(f"  {n:>8}  {'OK: ' + HVITLISTE[n] if n in HVITLISTE else 'IKKE FORKLART'}")
mangler = sorted(fryst - jsams, key=lambda x: (len(x), x))
print(f"tall i det fryste manuset som ikke lenger står i JSAMS-versjonen ({len(mangler)}): {' '.join(mangler)}")
sys.exit(1 if ikke_forklart else 0)
