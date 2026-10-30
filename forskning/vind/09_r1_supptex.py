r"""
09_r1_supptex.py — A6: alle manustabeller (1–6) og supplementstabeller (S1–S5) som LaTeX.

Ingen verdier skrives for hånd (audit 30.10.2026): tabellene bygges her fra
estimeringsfilene i full presisjon og \input-es i manus/main.tex. Desimalvalget står
eksplisitt per kolonne; avrunding skjer én gang, ved visning.
"""

import logging
import re
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
DATA = HERE / "data_private"
EST = HERE / "tables" / "estimering"
UT = HERE / "manus"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

SPRINT = ["60m", "80m", "100m", "150m", "200m"]
HOPP = ["lengde", "lengde_sone_05m", "tresteg", "tresteg_sone_05m"]
REKKE = SPRINT + HOPP
BAND = ["10-11", "12-13", "14-15", "16-17", "18-19", "20-34"]
NAVN = {"60m": "60 m", "80m": "80 m", "100m": "100 m", "150m": "150 m", "200m": "200 m",
        "lengde": "Long jump", "lengde_sone_05m": "Long jump (zone)",
        "tresteg": "Triple jump", "tresteg_sone_05m": "Triple jump (zone)"}
HEKKNAVN = {"60mh_68cm": "60 m hurdles 68 cm", "60mh_76_2cm": "60 m hurdles 76.2 cm",
            "80mh_76_2cm": "80 m hurdles 76.2 cm", "80mh_84cm": "80 m hurdles 84 cm",
            "100mh_76_2cm": "100 m hurdles 76.2 cm", "100mh_84cm": "100 m hurdles 84 cm",
            "100mh_91_4cm": "100 m hurdles 91.4 cm", "110mh_91_4cm": "110 m hurdles 91.4 cm",
            "110mh_100cm": "110 m hurdles 100 cm", "110mh_106_7cm": "110 m hurdles 106.7 cm"}


def tusen(n):
    return f"{int(n):,}".replace(",", "\\,")


def tall(x, d):
    s = f"{x:.{d}f}"
    return s.replace("-", "$-$") if s.startswith("-") else s


def ki(g, lo, hi, d):
    return f"{tall(g, d)} ({tall(lo, d)}--{tall(hi, d)})"


def band_tex(b):
    return b.replace("-", "--")


def tabular(hode, rader, kolfmt):
    linjer = [f"\\begin{{tabular}}{{{kolfmt}}}", "\\toprule", " & ".join(hode) + " \\\\",
              "\\midrule"]
    linjer += [" & ".join(r) + " \\\\" for r in rader]
    linjer += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(linjer) + "\n"


def t1():
    d = pd.read_csv(DATA / "analyseklar.csv",
                    usecols=["event_code", "athlete_id", "celle", "n_i_celle", "y", "wind"])
    rader = []
    for k in REKKE:
        g = d[d["event_code"] == k]
        g2 = g[g["n_i_celle"] >= 2]
        enhet = "s" if k in SPRINT else "m"
        w = g["wind"]
        vf = lambda x: f"{x:+.1f}".replace("-", "$-$")
        rader.append([NAVN[k], tusen(len(g)), tusen(len(g2)), tusen(g2["celle"].nunique()),
                      tusen(g2["athlete_id"].nunique()), f"{g['y'].median():.2f} {enhet}",
                      f"{vf(w.median())} ({vf(w.quantile(.05))}--{vf(w.quantile(.95))})"])
    hode = ["Event", "Results", "In cells $\\geq$2", "Athlete-seasons", "Athletes",
            "Median mark", "Wind, median (p5--p95)"]
    return tabular(hode, rader, "lcccccc")


def t2():
    h = pd.read_csv(EST / "r1_hoved_meet.csv")
    rader = []
    for k in REKKE:
        a = h[(h["analyse"] == "hoved_meet") & (h["event"] == k)].iloc[0]
        p = h[(h["analyse"] == "hoved_meet_pst") & (h["event"] == k)].iloc[0]
        d, enhet = (3, "s") if k in SPRINT else (2, "cm")
        rader.append([NAVN[k],
                      f"{tall(a['gevinst_per_ms'], d)} {enhet} ({tall(a['ki_lav'], d)}--{tall(a['ki_hoy'], d)})",
                      ki(p["gevinst_per_ms"], p["ki_lav"], p["ki_hoy"], 3),
                      tusen(a["n"]), tusen(a["celler"])])
    hode = ["Event", "Gain per +1 m/s (95\\,\\% CI)", "Percent per +1 m/s (95\\,\\% CI)", "n",
            "Athlete-seasons"]
    return tabular(hode, rader, "lcccc")


def t3():
    a = pd.read_csv(EST / "r1_alder_meet.csv")
    rader = []
    for k in ["60m", "100m", "200m"]:
        for kj, navn in [("M", "Boys/men"), ("F", "Girls/women")]:
            rad = [NAVN[k], navn]
            for b in BAND:
                t = a[(a["event"] == k) & (a["kjonn"] == kj) & (a["aldersband"] == b)
                      & (a["enhet"] == "s")]
                rad.append(ki(*t.iloc[0][["gevinst_per_ms", "ki_lav", "ki_hoy"]], 3)
                           if len(t) else "---")
            rader.append(rad)
    hode = ["Event", "Sex"] + [band_tex(b) for b in BAND]
    return tabular(hode, rader, "llcccccc")


def t4():
    s = pd.read_csv(EST / "r1_asym_meet.csv")
    rader = []
    for k in REKKE:
        t = s[s["event"] == k]
        if not len(t):
            continue
        t = t.iloc[0]
        d, enhet = (3, "s") if k in SPRINT else (2, "cm")
        p = t["p_lik_meet"]
        rader.append([NAVN[k], enhet,
                      ki(t["medvind"], t["medvind_ki_lav"], t["medvind_ki_hoy"], d),
                      ki(t["motvind"], t["motvind_ki_lav"], t["motvind_ki_hoy"], d),
                      f"{t['ratio_obs']:.2f}",
                      "---" if pd.isna(t["ratio_teoretisk_v2"]) else f"{t['ratio_teoretisk_v2']:.2f}",
                      "$<$0.001" if p < 0.001 else f"{p:.3f}"])
    hode = ["Event", "Unit", "Tailwind gain per +1 m/s", "Headwind loss per $-$1 m/s", "Ratio",
            "$v^2$ benchmark", "p equal slopes"]
    return tabular(hode, rader, "llccccc")


def t5():
    hk = pd.read_csv(EST / "r1_hekk_meet.csv")
    hk = hk[hk["kjonn"] != "begge"].copy()
    hk["_r"] = hk["kode"].map({k: i for i, k in enumerate(HEKKNAVN)})
    hk = hk.sort_values(["_r", "kjonn"], ascending=[True, False])
    rader = []
    for _, t in hk.iterrows():
        voksen = t["modal_aldersband"] in ("18-19", "20-34")
        kjonn = {("M", False): "Boys", ("F", False): "Girls",
                 ("M", True): "Men", ("F", True): "Women"}[(t["kjonn"], voksen)]
        ref = "---" if pd.isna(t["flat_ref"]) else ki(t["flat_ref"], t["flat_ref_ki_lav"],
                                                      t["flat_ref_ki_hoy"], 3)
        rader.append([HEKKNAVN[t["kode"]], kjonn, band_tex(t["modal_aldersband"]),
                      ki(t["gevinst_s_per_ms"], t["ki_lav"], t["ki_hoy"], 3), ref, tusen(t["n"])])
    hode = ["Event (hurdle height)", "Sex", "Modal band", "Gain per +1 m/s (95\\,\\% CI), s",
            "Flat reference (95\\,\\% CI), s", "n"]
    return tabular(hode, rader, "llcccc")


def t6():
    v = pd.read_csv(EST / "r1_vindu_medvind.csv")
    rader = []
    for k in ["60m", "100m", "200m"]:
        for kj, navn in [("M", "Boys/men"), ("F", "Girls/women")]:
            rad = [NAVN[k], navn]
            for b in BAND:
                t = v[(v["event"] == k) & (v["kjonn"] == kj) & (v["aldersband"] == b)]
                rad.append(f"{t['fordel_2ms_s'].iloc[0]:.2f} s ({t['fordel_i_sd'].iloc[0]:.2f} SD)"
                           if len(t) else "---")
            rader.append(rad)
    hode = ["Event", "Sex"] + [band_tex(b) for b in BAND]
    return tabular(hode, rader, "llcccccc")


def s1():
    a = pd.read_csv(EST / "r1_alder_meet.csv")
    rader = []
    for k in ["lengde", "lengde_sone_05m", "tresteg"]:
        for enh in ["cm", "%"]:
            rad = [NAVN[k], "\\%" if enh == "%" else enh]
            for b in BAND:
                cel = []
                for kj in ["F", "M"]:
                    t = a[(a["event"] == k) & (a["aldersband"] == b) & (a["enhet"] == enh)
                          & (a["kjonn"] == kj)]
                    if len(t):
                        cel.append(ki(*t.iloc[0][["gevinst_per_ms", "ki_lav", "ki_hoy"]], 2))
                rad.append(" / ".join(cel) if cel else "---")
            rader.append(rad)
    return tabular(["Event", "Unit"] + [band_tex(b) for b in BAND], rader, "llcccccc")


def s2():
    rob = pd.read_csv(EST / "robusthet.csv")
    u2 = pd.read_csv(EST / "r1_uten_2.csv").assign(analyse="uten2")
    rob = pd.concat([rob[["analyse", "event", "gevinst_per_ms"]],
                     u2[["analyse", "event", "gevinst_per_ms"]]])
    piv = rob.pivot_table(index="event", columns="analyse", values="gevinst_per_ms")
    kol = [("primaer", "Primary"), ("celler_min3", "Cells $\\geq$3"),
           ("uten_vind_0", "No exact 0.0"), ("uten2", "Excl. $\\pm$0.2 of +2.0"),
           ("periode_2011_2019", "2011--19"), ("periode_2021_2026", "2021--26"),
           ("stevne_fe", "Meet FE")]
    rader = []
    for k in [k for k in REKKE if k in piv.index]:
        rader.append([NAVN[k]] + ["---" if pd.isna(piv.loc[k].get(c)) else f"{piv.loc[k, c]:.4f}"
                                  for c, _ in kol])
    return tabular(["Event"] + [n for _, n in kol], rader, "lccccccc")


def s3():
    v = pd.read_csv(EST / "r1_vindu_medvind.csv")
    s = pd.read_csv(EST / "r1_asym_meet.csv")
    rader = []
    for _, t in v.iterrows():
        rader.append([NAVN[t["event"]], "Boys/men" if t["kjonn"] == "M" else "Girls/women",
                      band_tex(t["aldersband"]),
                      ki(t["medvind_s_per_ms"], t["medvind_ki_lav"], t["medvind_ki_hoy"], 3),
                      ki(t["motvind_s_per_ms"], t["motvind_ki_lav"], t["motvind_ki_hoy"], 3),
                      tusen(t["n"])])
    for k in HOPP:
        t = s[s["event"] == k].iloc[0]
        rader.append([NAVN[k], "Both", "all",
                      ki(t["medvind"], t["medvind_ki_lav"], t["medvind_ki_hoy"], 2) + " cm",
                      ki(t["motvind"], t["motvind_ki_lav"], t["motvind_ki_hoy"], 2) + " cm",
                      tusen(t["n"])])
    hode = ["Event", "Sex", "Age band", "Tailwind slope per +1 m/s (95\\,\\% CI)",
            "Headwind slope per $-$1 m/s (95\\,\\% CI)", "n"]
    return tabular(hode, rader, "lllccc")


def s4():
    p = pd.read_csv(EST / "r1_per_sekund.csv").set_index("event")
    hk = pd.read_csv(EST / "r1_hekk_meet.csv")
    hk = hk[hk["kjonn"] == "begge"].set_index("kode")
    rader = [[NAVN[k], f"{p.loc[k, 'snitt_tid_s']:.2f}", f"{p.loc[k, 'gevinst_per_ms']:.3f}",
              f"{p.loc[k, 'per_sekund']:.5f}"] for k in SPRINT if k in p.index]
    rader += [[HEKKNAVN[k], f"{hk.loc[k, 'snitt_tid_s']:.2f}",
               f"{hk.loc[k, 'gevinst_s_per_ms']:.3f}", f"{hk.loc[k, 'per_sekund']:.5f}"]
              for k in HEKKNAVN if k in hk.index]
    return tabular(["Event", "Mean time (s)", "Gain per +1 m/s (s)", "Per second of race time"],
                   rader, "lccc")


def s5():
    kv = pd.read_csv(EST / "r1_kvad_meet.csv").set_index("event")
    rader = [[NAVN[k], f"{tall(kv.loc[k, 'beta_lin'], 4)} ({kv.loc[k, 'se_lin']:.4f})",
              f"{tall(kv.loc[k, 'beta_kvad'], 4)} ({kv.loc[k, 'se_kvad']:.4f})", tusen(kv.loc[k, "n"])]
             for k in REKKE if k in kv.index]
    return tabular(["Event", "Linear term (SE)", "Quadratic term (SE)", "n"], rader, "lccc")


def main():
    for navn, fn in [("t1", t1), ("t2", t2), ("t3", t3), ("t4", t4), ("t5", t5), ("t6", t6),
                     ("s1", s1), ("s2", s2), ("s3", s3), ("s4", s4), ("s5", s5)]:
        (UT / f"{navn}.tex").write_text(fn())
    logger.info(f"t1–t6 og s1–s5 skrevet til {UT}/")


if __name__ == "__main__":
    main()
