"""
04_figurer_tabeller.py — A6 «Vind»: nøkkelfigurer og manustabeller (engelsk).

Kjøres etter 03. Samme visuelle språk som A1/A3.

Output:
  figures/fig1_effect_by_age.png        gevinst per +1 m/s etter aldersbånd (sprint, s)
  figures/fig2_effect_by_age_pct.png    samme i prosent (sprint + hopp)
  figures/fig3_asymmetry.png            medvindsgevinst mot motvindskostnad per øvelse
  figures/fig4_level.png                effekt per nivåtertil
  tables/manus/table_main.csv           hovedeffekter per øvelse
  tables/manus/table_advantage2ms.csv   +2,0 m/s-fordelen per øvelse x kjønn x aldersbånd
"""

import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
EST = HERE / "tables" / "estimering"
FIG = HERE / "figures"
TABM = HERE / "tables" / "manus"
FIG.mkdir(exist_ok=True)
TABM.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

GRONN, ROD, GRAA, BLAA = "#1b6e1b", "#b22222", "#666666", "#1f4e79"
plt.rcParams.update({"figure.dpi": 300, "savefig.dpi": 300, "font.size": 11,
                     "axes.grid": True, "grid.alpha": 0.3, "axes.titlesize": 13})

SPRINT = ["60m", "100m", "200m"]
HOPP = ["lengde", "lengde_sone_05m", "tresteg"]
BANDREKKE = ["10-11", "12-13", "14-15", "16-17", "18-19", "20-34"]
NAVN = {"60m": "60 m", "80m": "80 m", "100m": "100 m", "150m": "150 m", "200m": "200 m",
        "lengde": "Long jump", "lengde_sone_05m": "Long jump (zone)",
        "tresteg": "Triple jump", "tresteg_sone_05m": "Triple jump (zone)"}
FARGER = {"60m": BLAA, "100m": GRONN, "200m": ROD,
          "lengde": GRONN, "lengde_sone_05m": GRAA, "tresteg": ROD}


def alder_panel(a, koder, enhet, tittel, fil, ylab):
    fig, akser = plt.subplots(1, 2, figsize=(11.5, 5.0), sharey=False)
    for ax, kj, kjnavn in [(akser[0], "M", "Boys/men"), (akser[1], "F", "Girls/women")]:
        for kode in koder:
            g = a[(a["event"] == kode) & (a["kjonn"] == kj) & (a["enhet"] == enhet)]
            g = g.set_index("aldersband").reindex(BANDREKKE).reset_index()
            x = np.arange(len(BANDREKKE))
            ax.errorbar(x, g["gevinst_per_ms"],
                        yerr=[g["gevinst_per_ms"] - g["ki_lav"],
                              g["ki_hoy"] - g["gevinst_per_ms"]],
                        fmt="o-", lw=2.2, ms=6, capsize=3,
                        color=FARGER.get(kode, GRAA), label=NAVN[kode])
        ax.axhline(0, color=GRAA, lw=1, ls="--")
        ax.set_xticks(x, BANDREKKE)
        ax.set_xlabel("Age band")
        ax.set_title(kjnavn)
        ax.set_ylabel(ylab)
    akser[0].legend(frameon=False, fontsize=9)
    fig.suptitle(tittel, fontsize=13)
    fig.tight_layout()
    fig.savefig(FIG / fil, bbox_inches="tight")
    plt.close(fig)


def main():
    a = pd.read_csv(EST / "alder.csv")
    hoved = pd.read_csv(EST / "hoved.csv")
    asym = pd.read_csv(EST / "asym.csv")
    niva = pd.read_csv(EST / "niva.csv")

    alder_panel(a, SPRINT, "s",
                "Benefit of +1 m/s tailwind by age: sprints (seconds; within athlete × season)",
                "fig1_effect_by_age.png", "Seconds faster per +1 m/s")
    alder_panel(a, SPRINT + ["lengde", "tresteg"], "%",
                "Benefit of +1 m/s tailwind by age: percent of performance",
                "fig2_effect_by_age_pct.png", "Percent improvement per +1 m/s")

    # Asymmetri: medvindsgevinst mot motvindskostnad
    fig, ax = plt.subplots(figsize=(8.6, 5.2))
    koder = [k for k in SPRINT + HOPP if k in set(asym["event"])]
    x = np.arange(len(koder))
    med = [asym.loc[asym["event"] == k, "medvind_gevinst_per_ms"].iloc[0] for k in koder]
    mot = [-asym.loc[asym["event"] == k, "motvind_kost_per_ms"].iloc[0] for k in koder]
    ax.bar(x - 0.18, med, width=0.36, color=GRONN, label="Gain per +1 m/s tailwind")
    ax.bar(x + 0.18, mot, width=0.36, color=ROD, label="Loss per −1 m/s headwind")
    ax.set_xticks(x, [NAVN[k] for k in koder], rotation=15)
    ax.set_ylabel("Seconds (sprints) / cm (jumps)")
    ax.set_title("Asymmetry: headwind costs versus tailwind gains (within athlete × season)")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "fig3_asymmetry.png", bbox_inches="tight")
    plt.close(fig)

    # Nivåtertiler
    fig, ax = plt.subplots(figsize=(8.6, 5.2))
    farger = {"lav": ROD, "midt": GRAA, "hoy": GRONN}
    bredde = 0.26
    for i, tert in enumerate(["lav", "midt", "hoy"]):
        verdier = []
        for k in koder:
            g = niva[(niva["event"] == k) & (niva["tertil"] == tert)]
            verdier.append(g["gevinst_per_ms"].iloc[0] if len(g) else np.nan)
        ax.bar(x + (i - 1) * bredde, verdier, width=bredde, color=farger[tert],
               label={"lav": "Lowest ability tertile", "midt": "Middle",
                      "hoy": "Highest"}[tert])
    ax.set_xticks(x, [NAVN[k] for k in koder], rotation=15)
    ax.set_ylabel("Gain per +1 m/s tailwind (s / cm)")
    ax.set_title("Wind effect by within-group ability tertile")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "fig4_level.png", bbox_inches="tight")
    plt.close(fig)

    # Manustabeller
    h = hoved[hoved["analyse"] == "hoved"].copy()
    h["Event"] = h["event"].map(NAVN)
    h["Gain per +1 m/s (95% CI)"] = h.apply(
        lambda t: f"{t['gevinst_per_ms']:.3f} ({t['ki_lav']:.3f}–{t['ki_hoy']:.3f}) {t['enhet']}",
        axis=1)
    (h[["Event", "enhet", "Gain per +1 m/s (95% CI)", "n", "celler"]]
     .rename(columns={"enhet": "Unit", "celler": "Athlete-seasons"})
     .to_csv(TABM / "table_main.csv", index=False))

    f2 = pd.read_csv(EST / "fordel2ms.csv")
    f2["Event"] = f2["event"].map(NAVN)
    f2.to_csv(TABM / "table_advantage2ms.csv", index=False)

    logger.info(f"4 figurer i {FIG}/, 2 manustabeller i {TABM}/")


if __name__ == "__main__":
    main()
