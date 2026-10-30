r"""
06_manustabeller.py — A3: manustabellene 1–4 og S1–S3 som LaTeX, rett fra modell- og datafilene.

Ingen tall skrives for hånd (audit 30.10.2026): tabellene \input-es i manus/main.tex.
"""

import json
import logging
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
DATA = HERE / "data_private"
MOD = HERE / "tables" / "modeller"
UT = HERE / "manus"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def tusen(n):
    return f"{int(n):,}".replace(",", "\\,")


def ki(o, lo, hi, d=2):
    return f"{o:.{d}f} ({lo:.{d}f}--{hi:.{d}f})"


def prik(x):
    """.512-format (tre desimaler, uten innledende null)."""
    return f"{x:.3f}".lstrip("0") if x < 1 else f"{x:.3f}"


def tabular(hode, rader, kolfmt, midtlinjer=()):
    linjer = [f"\\begin{{tabular}}{{{kolfmt}}}", "\\toprule", " & ".join(hode) + " \\\\", "\\midrule"]
    for i, r in enumerate(rader):
        if i in midtlinjer:
            linjer.append("\\midrule")
        linjer.append(" & ".join(r) + " \\\\")
    linjer += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(linjer) + "\n"


def prim_utvalg():
    d = pd.read_csv(DATA / "analysedata.csv")
    return d[d["kohort_primar"] & d["debut_10_16"]].copy()


def miqr(s):
    return f"{s.median():.0f} ({s.quantile(0.25):.0f}--{s.quantile(0.75):.0f})"


def t1():
    p = prim_utvalg()
    gr = [p[p["debut_alder"].between(10, 11)], p[p["debut_alder"].between(12, 13)],
          p[p["debut_alder"].between(14, 16)]]
    medq = [g[g["kvartal"].notna()] for g in gr]
    rader = [["n"] + [tusen(len(g)) for g in gr],
             ["Female, \\%"] + [f"{(g['gender'] == 'F').mean() * 100:.1f}" for g in gr],
             ["Exact birth date available, \\%"] + [f"{g['kvartal'].notna().mean() * 100:.1f}" for g in gr],
             ["Born Q1, \\% of those with birth date"] + [f"{(q['kvartal'] == 1).mean() * 100:.1f}" for q in medq],
             ["Born Q4, \\% of those with birth date"] + [f"{(q['kvartal'] == 4).mean() * 100:.1f}" for q in medq],
             ["Competition days in debut season, median (IQR)"] + [miqr(g["vol_debutaar"]) for g in gr],
             ["Career length, seasons, median (IQR)"] + [miqr(g["karriere_aar"]) for g in gr],
             ["Debut season 2020--2021, \\%"] + [f"{g['covid_debut'].mean() * 100:.1f}" for g in gr]]
    return tabular(["Characteristic", "Debut 10--11", "Debut 12--13", "Debut 14--16"], rader, "lccc")


def t2():
    """Seniorutfallet (fast alder) og utfallet ved lik karrierelengde (D = 4), side om side."""
    h1 = pd.read_csv(MOD / "h1_debutalder.csv")
    va = pd.read_csv(MOD / "r2_varighet_andeler.csv")
    vm = pd.read_csv(MOD / "r2_varighet_modeller.csv")
    p = prim_utvalg()

    def or_rad(df, analyse, var):
        t = df[(df["analyse"] == analyse) & (df["variabel"] == var)].iloc[0]
        return ki(t["OR"], t["KI_lav"], t["KI_hoy"])

    rader = []
    for a in range(10, 17):
        g = p[p["debut_alder"] == a]
        v = va[(va["D"] == 4) & (va["debut_alder"] == a)].iloc[0]
        rader.append([str(a), tusen(len(g)), f"{g['senior'].mean() * 100:.1f}",
                      "1.00 (ref.)" if a == 10 else or_rad(h1, "H1_kategorisk", f"debut_kat_{a}"),
                      f"{v['andel'] * 100:.1f}",
                      "1.00 (ref.)" if a == 10 else or_rad(vm, "varighet_4_kategorisk", f"debut_kat_{a}")])
    rader.append(["Linear trend, per +1 year", "", "", or_rad(h1, "H1_trend", "debut_alder"), "",
                  or_rad(vm, "varighet_4", "debut_alder")])
    hode = ["Debut age", "n", "\\%", "OR (95\\,\\% CI)", "\\%", "OR (95\\,\\% CI)"]
    linjer = ["\\begin{tabular}{lrcccc}", "\\toprule",
              " & & \\multicolumn{2}{c}{Active senior (age $\\geq$20)} & "
              "\\multicolumn{2}{c}{Competing $\\geq$4 years after debut} \\\\",
              "\\cmidrule(lr){3-4}\\cmidrule(lr){5-6}", " & ".join(hode) + " \\\\", "\\midrule"]
    for i, r in enumerate(rader):
        if i == 7:
            linjer.append("\\midrule")
        linjer.append(" & ".join(r) + " \\\\")
    linjer += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(linjer) + "\n"


def retention():
    return pd.read_csv(MOD / "r1_retention_ci.csv")


def t3():
    r = retention()
    rader = []
    for a in range(10, 17):
        g = r[(r["debut_alder"] == a) & (r["k"] >= 1)].sort_values("k")
        n1 = int(r[(r["debut_alder"] == a) & (r["k"] == 1)]["n"].iloc[0])
        rader.append([str(a), tusen(n1)] + [f"{x:.2f}" for x in g["andel"]])
    return tabular(["Debut age", "n"] + [f"$k$={k}" for k in range(1, 6)], rader, "lcccccc")


def t4():
    h1 = pd.read_csv(MOD / "h1_debutalder.csv")
    rob = pd.read_csv(MOD / "robusthet.csv")
    d17 = pd.read_csv(MOD / "r1_debut1719.csv")
    cov = pd.read_csv(MOD / "r1_covid_flagg.csv")
    u01 = pd.read_csv(MOD / "r2_uten_2001.csv")
    ukj = pd.read_csv(MOD / "r2_ukjent_kjonn.csv")

    def rad(df, an, var="debut_alder"):
        t = df[(df["analyse"] == an) & (df["variabel"] == var)].iloc[0]
        return [tusen(t["n"]), tusen(t["hendelser"]), ki(t["OR"], t["KI_lav"], t["KI_hoy"])]

    rader = [
        ["Primary linear trend"] + rad(h1, "H1_trend"),
        ["Excluding debuts in 2020--2021"] + rad(rob, "uten_covid_debut"),
        ["Excluding the 2001 cohort (debut at 10 in 2011)"] + rad(u01, "uten_2001_trend"),
        ["Including athletes without registered sex"] + rad(ukj, "med_ukjent_kjonn_trend"),
        ["Outcome: $\\geq$1 result at age $\\geq$20"] + rad(rob, "utfall_min1"),
        ["Outcome: any result at age $\\geq$17 (debuts 10--14)"] + rad(rob, "utfall_aktiv17_debut_10_14"),
        ["Adding debut-season competition days"] + rad(rob, "betinget_debutvolum"),
        ["Cohorts born 2001--2003"] + rad(rob, "kohort_2001_2003"),
        ["Cohorts born 2004--2005"] + rad(rob, "kohort_2004_2005"),
        ["Debut at 17--19 vs.\\ debut at 10 (categorical)"] + rad(d17, "r1_debut_17_19", "debut_kat_17"),
        ["Adding the COVID-19 debut flag (linear trend)"] + rad(cov, "r1_med_covid_flagg"),
        ["Club-clustered robust SE (trend)"] + rad(h1, "H1_trend_klubbrobust"),
    ]
    return tabular(["Analysis", "n", "Events", "OR (95\\,\\% CI)"], rader, "lccc")


def s1():
    f = json.loads((DATA / "flyt.json").read_text())
    p = prim_utvalg()
    d = pd.read_csv(DATA / "analysedata.csv")
    beskr = int((d["debut_10_16"] & ~d["kohort_primar"]).sum())
    rader = [
        ["Athletes born 2001--2008 in the registry extract", tusen(f["utovere_fodt_2001_2008"])],
        ["Result rows extracted (2011 -- 29 Oct 2026)", tusen(f["resultatrader"])],
        ["\\quad excluded: non-approved rows", tusen(f["rader_ikke_ok"])],
        ["\\quad excluded: rows below age 10", tusen(f["rader_alder_under_10"])],
        ["Debutants with an approved result at age $\\geq$10", tusen(f["debutanter_alder_10plus"])],
        ["\\quad excluded: missing sex", tusen(f["uten_kjonn"])],
        # flyt.json teller debut 17+ før kjønnsfiltreringen (732); flyten her er sekvensiell (731)
        ["\\quad set aside: debut at age $\\geq$17 (sensitivity analyses)", tusen(int((d["debut_alder"] >= 17).sum()))],
        ["Debutants at ages 10--16 with known sex", tusen(int(d["debut_10_16"].sum()))],
        ["\\quad primary sample: born 2001--2005", tusen(len(p))],
        ["\\quad descriptive only: born 2006--2008", tusen(beskr)],
        ["Active seniors in the primary sample", tusen(p["senior"].sum())],
    ]
    return tabular(["Step", "n"], rader, "lr")


def s2():
    r = retention()
    rader = []
    for a in range(10, 17):
        g = r[(r["debut_alder"] == a) & (r["k"] >= 1)].sort_values("k")
        n1 = int(r[(r["debut_alder"] == a) & (r["k"] == 1)]["n"].iloc[0])
        rader.append([str(a), tusen(n1)] + [f"{prik(t['andel'])} ({prik(t['ki_lav'])}--{prik(t['ki_hoy'])})"
                                            for _, t in g.iterrows()])
    return tabular(["Debut age", "n"] + [f"$k$={k}" for k in range(1, 6)], rader, "lcccccc")


def s3():
    kk = pd.read_csv(MOD / "r1_kjonn_konvertering.csv")
    rader = []
    for a in range(10, 17):
        rad = [str(a)]
        for kj in ["F", "M"]:
            t = kk[(kk["debut_alder"] == a) & (kk["gender"] == kj)].iloc[0]
            lo, hi = str(t["ki"]).replace("–", "-").split("-")
            rad += [tusen(t["n"]), f"{t['andel_pst']:.1f} ({lo}--{hi})"]
        rader.append(rad)
    return tabular(["Debut age", "Girls, n", "Girls, \\% (CI)", "Boys, n", "Boys, \\% (CI)"], rader, "lcccc")


def s4():
    """Utfallet ved lik karrierelengde, D = 4, 5 og 6 år etter debut."""
    va = pd.read_csv(MOD / "r2_varighet_andeler.csv")
    vm = pd.read_csv(MOD / "r2_varighet_modeller.csv")
    rader = []
    for a in range(10, 17):
        rad = [str(a)]
        for D in (4, 5, 6):
            v = va[(va["D"] == D) & (va["debut_alder"] == a)].iloc[0]
            rad.append(f"{v['andel'] * 100:.1f} ({tusen(v['n'])})")
        rader.append(rad)
    trend = ["Linear trend, OR per +1 year"]
    for D in (4, 5, 6):
        t = vm[(vm["analyse"] == f"varighet_{D}") & (vm["variabel"] == "debut_alder")].iloc[0]
        trend.append(ki(t["OR"], t["KI_lav"], t["KI_hoy"]))
    rader.append(trend)
    return tabular(["Debut age", "4 years: \\% (n)", "5 years: \\% (n)", "6 years: \\% (n)"], rader, "lccc",
                   midtlinjer=(7,))


def main():
    for navn, fn in [("t1", t1), ("t2", t2), ("t3", t3), ("t4", t4), ("s1", s1), ("s2", s2), ("s3", s3),
                     ("s4", s4)]:
        (UT / f"{navn}.tex").write_text(fn())
    logger.info(f"t1–t4 og s1–s4 skrevet til {UT}/")


if __name__ == "__main__":
    main()
