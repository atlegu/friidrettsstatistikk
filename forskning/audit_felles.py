"""
audit_felles.py — felles verktøy for tallsporingen i A1/A3/A6 (paper-data-audit fase 4).

Mønster som i Covid/Perform/resubmission/code/13_check_prose.py: hvert sitert tall
kontrolleres med en ankret frase (tallet sammen med teksten rundt, så et foreldet tall
ikke kan passere ved en tilfeldighet), bygget fra estimeringsfilene. I tillegg en
dekningskontroll: ethvert tall i teksten som ingen sjekk har dekket, listes og må enten
få en sjekk eller stå på en eksplisitt unntaksliste med begrunnelse.
"""

import re
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

ERSTATT = [("$+$", "+"), ("$-$", "-"), ("$<$", "<"), ("$>$", ">"), ("$\\pm$", "±"),
           ("$\\times$", "×"), ("$\\geq$", "≥"), ("$\\leq$", "≤"), ("$\\approx$", "≈"),
           ("\\%", "%"), ("~", " "), ("\\,", ""), ("{,}", ","), ("\\&", "&"), ("\\ ", " "),
           ("$\\to$", "→"), ("$\\rightarrow$", "→")]


def normaliser(t, kommentarer=True):
    """LaTeX → sammenlignbar tekst. Kommentarfjerningen må bare kjøres på rå LaTeX:
    etter avkodingen er «%» et prosenttegn, ikke en kommentar."""
    if kommentarer:
        t = re.sub(r"(?m)(?<!\\)%.*$", "", t)
    for a, b in ERSTATT:
        t = t.replace(a, b)
    t = re.sub(r"\\(cite[pt]?|ref|label|citep|citet)\{[^}]*\}", "", t)
    t = re.sub(r"\\(textbf|textit|emph|mbox|text)\{([^{}]*)\}", r"\2", t)
    return t


def avrund(x, d):
    """Korrekt avrunding av den eksakte binære verdien — samme regel som tabellgeneratorene
    (Python-formatering), så prosa og tabeller avrundes likt."""
    return format(float(x), f".{d}f")


def f(x, d):
    s = avrund(x, d)
    return s if not s.startswith("-") else "-" + s[1:]


class Kontroll:
    def __init__(self, tex_sti, navn):
        self.navn = navn
        self.raa = Path(tex_sti).read_text()
        kropp = self.raa.split("\\begin{document}", 1)[1]
        foran, etter = (kropp.split("\\bibliographystyle", 1) if "\\bibliographystyle" in kropp
                        else (kropp, ""))
        # supplement etter referansene tas med; står det før, er det allerede i «foran»
        tillegg = ""
        for merke in ["\\appendix", "\\section*{Supplementary material}"]:
            if merke in etter:
                tillegg = etter.split(merke, 1)[1]
                break
        kropp = foran + tillegg
        self.tekst = normaliser(kropp)
        # for sitatkontrollen: teksten med de genererte tabellene (\input) satt inn
        mappe = Path(tex_sti).parent
        self.tekst_full = normaliser(re.sub(
            r"\\input\{([^}]+)\}",
            lambda m: (mappe / (m.group(1) + ".tex")).read_text()
            if (mappe / (m.group(1) + ".tex")).exists() else m.group(0), kropp))
        self.seksjoner = self._del_opp(self.tekst)
        self.feil, self.dekket, self.n_ok = [], [], 0

    @staticmethod
    def _del_opp(t):
        deler, navn, start = {}, "tittelside", 0
        for m in re.finditer(r"\\section\*?\{([^}]*)\}", t):
            deler[navn] = (start, m.start())
            navn, start = m.group(1).strip().lower(), m.start()
        deler[navn] = (start, len(t))
        return deler

    def seksjon(self, navn):
        for k, (a, b) in self.seksjoner.items():
            if k.startswith(navn.lower()):
                return a, b
        raise KeyError(f"{self.navn}: seksjon «{navn}» finnes ikke ({list(self.seksjoner)})")

    def need(self, hvor, s, hvorfor, alle=False):
        """Frasen s skal stå i seksjonen(e). Merker alle forekomster som dekket."""
        for h in ([hvor] if isinstance(hvor, str) else hvor):
            a, b = self.seksjon(h) if h != "*" else (0, len(self.tekst))
            treff = [m.start() for m in re.finditer(re.escape(s), self.tekst[a:b])]
            if not treff:
                self.feil.append(f"{h:<14} mangler {s!r}  ({hvorfor})")
                continue
            self.n_ok += 1
            for i in treff if alle or True else treff[:1]:
                self.dekket.append((a + i, a + i + len(s)))

    def dekk_omraade(self, start_tekst, slutt_tekst, hvorfor):
        """Marker et helt område (f.eks. en tabell kontrollert celle for celle) som dekket."""
        a = self.tekst.find(start_tekst)
        b = self.tekst.find(slutt_tekst, a)
        if a < 0 or b < 0:
            self.feil.append(f"område ikke funnet: {start_tekst!r} ({hvorfor})")
            return
        self.dekket.append((a, b + len(slutt_tekst)))

    def dekning(self, unntak):
        """Tall i teksten utenfor dekkede spenn og utenfor unntaksmønstrenes treff.
        Et unntak dekker bare tall som ligger INNE I et treff av mønsteret."""
        spenn = sorted(self.dekket)
        for p in unntak:
            spenn += [m.span() for m in re.finditer(p, self.tekst)]
        ikke = []
        for m in re.finditer(r"(?<![\w.\\])[-+]?\d+(?:\.\d+)?", self.tekst):
            a, b = m.span()
            if any(x <= a and b <= y for x, y in spenn):
                continue
            kontekst = self.tekst[max(0, a - 50):b + 50].replace("\n", " ")
            ikke.append((m.group(), kontekst))
        return ikke

    def rapport(self, unntak, vis_dekning=True):
        ikke = self.dekning(unntak) if vis_dekning else []
        print(f"{self.navn}: {self.n_ok} ankrede sjekker OK, {len(self.feil)} feil, "
              f"{len(ikke)} udekkede tall")
        for x in self.feil:
            print("  FEIL", x)
        for tall, kontekst in ikke:
            print(f"  UDEKKET {tall:>10}  …{kontekst}…")
        return 1 if (self.feil or ikke) else 0


def tall_i(s):
    """Tall i rekkefølge; «--» er et intervalltegn, ikke et minus."""
    s = normaliser(s, kommentarer=False).replace("--", " – ")
    return re.findall(r"(?<![\d.])[-+]?\d+(?:\.\d+)?", s)


def sjekk_tabellrad(k, etikett, tex_rad, kilde, hvorfor):
    """Alle tall i en tabellrad (i rekkefølge) mot kildeverdiene, avrundet til visningens
    desimaler. kilde: liste av tall (float/int) eller strenger som skal være eksakt like."""
    vist = tall_i(tex_rad)
    if len(vist) != len(kilde):
        k.feil.append(f"tabell {etikett}: {len(vist)} tall vist, {len(kilde)} i kilden "
                      f"({hvorfor}): {vist} mot {kilde}")
        return
    for v, x in zip(vist, kilde):
        if isinstance(x, str):
            ok = v == x
        else:
            d = len(v.split(".")[1]) if "." in v else 0
            ok = avrund(x, d) == v.lstrip("+") or avrund(x, d) == v
        if not ok:
            k.feil.append(f"tabell {etikett}: vist {v}, kilde {x} ({hvorfor})")
            return
    k.n_ok += 1


def ordtelling(tex_sti, fra=r"\section{Introduction}", til=r"\section*{Declarations}"):
    """Ord i løpende tekst: fra første hovedseksjon til erklæringene, uten tabeller,
    figurer, kommandoer og matematikk."""
    t = Path(tex_sti).read_text()
    t = t[t.index(fra):t.index(til)]
    t = re.sub(r"(?m)(?<!\\)%.*$", "", t)
    t = re.sub(r"\\begin\{(table|figure)\}.*?\\end\{\1\}", " ", t, flags=re.S)
    t = re.sub(r"\\(cite[pt]?|ref|label)\{[^}]*\}", " ", t)
    t = re.sub(r"\$[^$]*\$", " x ", t)
    t = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", t)
    t = re.sub(r"[{}\\]", " ", t)
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’.,–-]*", t))


def sitatkontroll(brev_sti, k, tillatt=None, min_lengde=12):
    """Hvert sitat i brevet (doble anførselstegn) skal stå ordrett i manus."""
    tillatt = tillatt or {}

    def norm(t, latex):
        t = normaliser(t, kommentarer=False) if latex else t
        t = t.replace("---", "—").replace("--", "–")
        t = re.sub(r"\$([^$]*)\$", r"\1", t).replace("\\", "").replace("{", "").replace("}", "")
        t = t.replace("’", "'").replace("“", '"').replace("”", '"').replace("*", "")
        t = re.sub(r"\s+", " ", t).replace(" %", "%")
        return t.strip().lower()

    ms = norm(k.tekst_full, latex=True)
    linjer = [ln for ln in Path(brev_sti).read_text().splitlines()
              if not ln.lstrip().startswith((">", "#"))]
    sitater = [q for q in re.findall(r'"([^"]*)"', " ".join(linjer)) if len(q) >= min_lengde]
    def finnes(q):
        """«…» i et sitat er en utelatelse: delene må stå i rekkefølge i manus."""
        deler = [d.strip(",.;: ") for d in norm(q, latex=False).split("…") if d.strip(",.;: ")]
        pos = 0
        for d in deler:
            i = ms.find(d, pos)
            if i < 0:
                return False
            pos = i + len(d)
        return True

    mangler = [q for q in sitater if q not in tillatt and not finnes(q)]
    print(f"{k.navn} sitatkontroll: {len(sitater)} sitater, "
          + ("alle ordrett i manus" if not mangler else f"{len(mangler)} IKKE FUNNET"))
    for q in mangler:
        print("  MANGLER:", q[:150])
    return 1 if mangler else 0


def avslutt(koder):
    sys.exit(1 if any(koder) else 0)
