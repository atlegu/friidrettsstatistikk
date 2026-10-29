"""
06_manusfigurer_tabeller.py — A6 «Vind»: publiseringsklare figurer og tabeller.

Gjør om fig3 (asymmetri) og fig4 (nivå) til to-panels figurer med riktige
enheter per panel, og bygger de engelske manustabellene fra estimerings-CSV-ene.

Output: figures/fig3_asymmetry.png, figures/fig4_level.png (overskrives),
        tables/manus/table1..6 + tableS_*.csv
"""

import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
DATA = HERE / "data_private"
EST = HERE / "tables" / "estimering"
FIG = HERE / "figures"
TABM = HERE / "tables" / "manus"
TABM.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

GRONN, ROD, GRAA, BLAA = "#1b6e1b", "#b22222", "#666666", "#1f4e79"
plt.rcParams.update({"figure.dpi": 300, "savefig.dpi": 300, "font.size": 11,
                     "axes.grid": True, "grid.alpha": 0.3, "axes.titlesize": 12})

SPRINT = ["60m", "80m", "100m", "150m", "200m"]
HOPPREKKE = ["lengde", "lengde_sone_05m", "tresteg", "tresteg_sone_05m"]
NAVN = {"60m": "60 m", "80m": "80 m", "100m": "100 m", "150m": "150 m", "200m": "200 m",
        "lengde": "Long jump", "lengde_sone_05m": "Long jump (zone)",
        "tresteg": "Triple jump", "tresteg_sone_05m": "Triple jump (zone)"}
REKKE = SPRINT + HOPPREKKE


def fmt(g, lo, hi, des=3):
    return f"{g:.{des}f} ({lo:.{des}f}–{hi:.{des}f})"


def fig3_asym():
    a = pd.read_csv(EST / "asym.csv")
    spr = [k for k in ["60m", "100m", "200m"] if k in set(a["event"])]
    hop = [k for k in ["lengde", "lengde_sone_05m", "tresteg"] if k in set(a["event"])]
    fig, akser = plt.subplots(1, 2, figsize=(11.2, 4.9))
    for ax, koder, enhet in [(akser[0], spr, "Seconds per m/s"),
                             (akser[1], hop, "Centimetres per m/s")]:
        x = np.arange(len(koder))
        med = [a.loc[a["event"] == k, "medvind_gevinst_per_ms"].iloc[0] for k in koder]
        mot = [-a.loc[a["event"] == k, "motvind_kost_per_ms"].iloc[0] for k in koder]
        ax.bar(x - 0.18, med, width=0.36, color=GRONN, label="Gain per +1 m/s tailwind")
        ax.bar(x + 0.18, mot, width=0.36, color=ROD, label="Loss per −1 m/s headwind")
        ax.set_xticks(x, [NAVN[k] for k in koder])
        ax.set_ylabel(enhet)
        ax.axhline(0, color=GRAA, lw=0.8)
    akser[0].set_title("Sprints: headwind costs more than tailwind gives")
    akser[1].set_title("Horizontal jumps")
    akser[0].legend(frameon=False, fontsize=9)
    fig.suptitle("Asymmetry of the wind effect (within athlete × season)", fontsize=13)
    fig.tight_layout()
    fig.savefig(FIG / "fig3_asymmetry.png", bbox_inches="tight")
    plt.close(fig)


def fig4_niva():
    n = pd.read_csv(EST / "niva.csv")
    spr = [k for k in ["60m", "100m", "200m"] if k in set(n["event"])]
    hop = [k for k in ["lengde", "tresteg"] if k in set(n["event"])]
    farger = {"lav": ROD, "midt": GRAA, "hoy": GRONN}
    navn_t = {"lav": "Lowest ability tertile", "midt": "Middle", "hoy": "Highest"}
    fig, akser = plt.subplots(1, 2, figsize=(11.2, 4.9))
    for ax, koder, enhet in [(akser[0], spr, "Seconds per m/s"),
                             (akser[1], hop, "Centimetres per m/s")]:
        x = np.arange(len(koder))
        for i, tert in enumerate(["lav", "midt", "hoy"]):
            v = [n[(n["event"] == k) & (n["tertil"] == tert)]["gevinst_per_ms"].iloc[0]
                 if len(n[(n["event"] == k) & (n["tertil"] == tert)]) else np.nan
                 for k in koder]
            ax.bar(x + (i - 1) * 0.26, v, width=0.26, color=farger[tert], label=navn_t[tert])
        ax.set_xticks(x, [NAVN[k] for k in koder])
        ax.set_ylabel(enhet)
    akser[0].set_title("Sprints: weaker athletes gain more per m/s")
    akser[1].set_title("Horizontal jumps")
    akser[0].legend(frameon=False, fontsize=9)
    fig.suptitle("Wind effect by within-group ability tertile", fontsize=13)
    fig.tight_layout()
    fig.savefig(FIG / "fig4_level.png", bbox_inches="tight")
    plt.close(fig)


def tabeller():
    d = pd.read_csv(DATA / "analyseklar.csv",
                    usecols=["event_code", "athlete_id", "celle", "n_i_celle", "y", "wind"])
    rader = []
    for kode in REKKE:
        g = d[d["event_code"] == kode]
        g2 = g[g["n_i_celle"] >= 2]
        rader.append({"Event": NAVN[kode],
                      "Results": f"{len(g):,}",
                      "In cells ≥2": f"{len(g2):,}",
                      "Athlete-seasons": f"{g2['celle'].nunique():,}",
                      "Athletes": f"{g2['athlete_id'].nunique():,}",
                      "Median mark": f"{g['y'].median():.2f}",
                      "Wind, median (p5–p95)":
                          f"{g['wind'].median():+.1f} ({g['wind'].quantile(0.05):+.1f}–"
                          f"{g['wind'].quantile(0.95):+.1f})"})
    pd.DataFrame(rader).to_csv(TABM / "table1_sample.csv", index=False)

    h = pd.read_csv(EST / "hoved.csv")
    rader = []
    for kode in REKKE:
        nat = h[(h["analyse"] == "hoved") & (h["event"] == kode) & (h["enhet"] != "%")]
        pst = h[(h["analyse"] == "hoved") & (h["event"] == kode) & (h["enhet"] == "%")]
        if not len(nat):
            continue
        t, p = nat.iloc[0], pst.iloc[0]
        skala = 1
        rader.append({"Event": NAVN[kode], "Unit": t["enhet"],
                      "Gain per +1 m/s (95% CI)": fmt(t["gevinst_per_ms"] * skala,
                                                      t["ki_lav"] * skala, t["ki_hoy"] * skala),
                      "Percent per +1 m/s (95% CI)": fmt(p["gevinst_per_ms"], p["ki_lav"],
                                                         p["ki_hoy"]),
                      "n": f"{t['n']:,}", "Athlete-seasons": f"{t['celler']:,}"})
    pd.DataFrame(rader).to_csv(TABM / "table2_main.csv", index=False)

    a = pd.read_csv(EST / "alder.csv")
    band = ["10-11", "12-13", "14-15", "16-17", "18-19", "20-34"]
    rader = []
    for kode in ["60m", "100m", "200m"]:
        for kj in ["M", "F"]:
            rad = {"Event": NAVN[kode], "Sex": "Boys/men" if kj == "M" else "Girls/women"}
            for b in band:
                t = a[(a["event"] == kode) & (a["kjonn"] == kj)
                      & (a["aldersband"] == b) & (a["enhet"] == "s")]
                rad[b] = fmt(*t.iloc[0][["gevinst_per_ms", "ki_lav", "ki_hoy"]]) if len(t) else "—"
            rader.append(rad)
    pd.DataFrame(rader).to_csv(TABM / "table3_age_sprints.csv", index=False)

    rader = []
    for kode in ["lengde", "lengde_sone_05m", "tresteg"]:
        for enh in ["cm", "%"]:
            rad = {"Event": NAVN[kode], "Unit": enh}
            for b in band:
                t = a[(a["event"] == kode) & (a["aldersband"] == b) & (a["enhet"] == enh)]
                if len(t) == 2:   # begge kjønn
                    t = t.sort_values("kjonn")
                rad[b] = " / ".join(fmt(*x[["gevinst_per_ms", "ki_lav", "ki_hoy"]], des=2)
                                    for _, x in t.iterrows()) if len(t) else "—"
            rader.append(rad)
    pd.DataFrame(rader).to_csv(TABM / "tableS_jumps_age.csv", index=False)

    asym = pd.read_csv(EST / "asym.csv")
    asym["Event"] = asym["event"].map(NAVN)
    asym["Unit"] = asym["event"].map(lambda k: "s" if k in SPRINT else "cm")
    (asym[["Event", "Unit", "medvind_gevinst_per_ms", "medvind_ki",
           "motvind_kost_per_ms", "motvind_ki", "p_lik_stigning", "n"]]
     .rename(columns={"medvind_gevinst_per_ms": "Tailwind gain per +1 m/s",
                      "medvind_ki": "95% CI", "motvind_kost_per_ms":
                      "Headwind loss per −1 m/s", "motvind_ki": "95% CI ",
                      "p_lik_stigning": "p equal slopes"})
     .to_csv(TABM / "table4_asymmetry.csv", index=False))

    hekk = pd.read_csv(EST / "hekk.csv")
    hk = hekk[hekk["kjonn"] != "begge"].copy()
    hk["Event (hurdle height)"] = hk["navn"]
    hk["Sex"] = hk["kjonn"].map({"M": "Boys/men", "F": "Girls/women"})
    hk["Gain per +1 m/s (95% CI), s"] = hk.apply(
        lambda t: fmt(t["gevinst_s_per_ms"], t["ki_lav"], t["ki_hoy"]), axis=1)
    hk["Flat sprint reference, s"] = hk["flat_sprint_ref_s"]
    (hk[["Event (hurdle height)", "Sex", "modal_aldersband",
         "Gain per +1 m/s (95% CI), s", "Flat sprint reference, s", "n", "celler"]]
     .rename(columns={"modal_aldersband": "Modal age band", "celler": "Athlete-seasons"})
     .to_csv(TABM / "table5_hurdles.csv", index=False))

    f2 = pd.read_csv(EST / "fordel2ms.csv")
    rader = []
    for kode in ["60m", "100m", "200m"]:
        for kj in ["M", "F"]:
            rad = {"Event": NAVN[kode], "Sex": "Boys/men" if kj == "M" else "Girls/women"}
            for b in band:
                t = f2[(f2["event"] == kode) & (f2["kjonn"] == kj) & (f2["aldersband"] == b)]
                rad[b] = (f"{t['fordel_2ms'].iloc[0]:.2f} s ({t['fordel_2ms_i_sd'].iloc[0]:.2f} SD)"
                          if len(t) else "—")
            rader.append(rad)
    pd.DataFrame(rader).to_csv(TABM / "table6_advantage_sd.csv", index=False)

    rob = pd.read_csv(EST / "robusthet.csv")
    piv = rob.pivot_table(index="event", columns="analyse", values="gevinst_per_ms")
    rekke = [k for k in REKKE if k in piv.index]
    piv = piv.loc[rekke].round(4)
    piv.index = [NAVN[k] for k in piv.index]
    piv.to_csv(TABM / "tableS_robustness.csv")

    logger.info(f"tabeller skrevet til {TABM}/")


def main():
    fig3_asym()
    fig4_niva()
    tabeller()
    logger.info("fig3/fig4 oppdatert; manustabeller ferdig")


if __name__ == "__main__":
    main()
