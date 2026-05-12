"""
Steg 3: Deskriptiv statistikk for NCC/PEAB-kohorten.

Produserer:
  - Tabell 1: Kohortkarakteristikker
  - Tabell 2: Frafall og karrierelengde
  - Tabell 3: RAE-fordeling med kji-kvadrat-test
  - Konsollutskrift + figurer i output/

Bruk: python 03_deskriptiv_statistikk.py
"""

import logging
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent
OUTPUT_DIR = DATA_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.size": 11,
    "figure.figsize": (10, 6),
    "figure.dpi": 150,
    "savefig.bbox": "tight",
})


def last_data():
    df = pd.read_csv(DATA_DIR / "analysedata.csv")
    df["birth_date"] = pd.to_datetime(df["birth_date"], errors="coerce")
    return df


def tabell1_kohort(df):
    """Tabell 1: Kohortkarakteristikker."""
    logger.info("=== TABELL 1: Kohortkarakteristikker ===")

    rows = []

    rows.append(("N", "", len(df), ""))

    for by in (1998, 1999, 2000):
        n = (df["birth_year"] == by).sum()
        rows.append(("Fødselsår", str(by), n, f"{n/len(df)*100:.1f}%"))

    for g, label in [("M", "Gutt"), ("F", "Jente")]:
        n = (df["gender"] == g).sum()
        rows.append(("Kjønn", label, n, f"{n/len(df)*100:.1f}%"))
    n_null = df["gender"].isna().sum()
    if n_null:
        rows.append(("Kjønn", "Ukjent", n_null, f"{n_null/len(df)*100:.1f}%"))

    for region in ["Østlandet", "Midt-Norge", "Vestlandet"]:
        n = (df["region"] == region).sum()
        rows.append(("Region", region, n, f"{n/len(df)*100:.1f}%"))

    n2 = df["deltok_begge_aar"].sum()
    rows.append(("Deltok begge år", "Ja", int(n2), f"{n2/len(df)*100:.1f}%"))

    valid_tyrving = df["tyrving_best"].dropna()
    rows.append(("Tyrving best", f"Median (IQR)", "",
                  f"{valid_tyrving.median():.0f} ({valid_tyrving.quantile(0.25):.0f}–{valid_tyrving.quantile(0.75):.0f})"))

    for kat in ["Svak", "Under snitt", "Middels", "God", "Sterk"]:
        n = (df["prestasjonskategori"] == kat).sum()
        rows.append(("Prestasjonskategori", kat, n, f"{n/len(valid_tyrving)*100:.1f}%"))

    rows.append(("Baseline øvelser", "Median (IQR)", "",
                  f"{df['baseline_n_ovelser'].median():.0f} ({df['baseline_n_ovelser'].quantile(0.25):.0f}–{df['baseline_n_ovelser'].quantile(0.75):.0f})"))

    rows.append(("Baseline kategorier", "Median (IQR)", "",
                  f"{df['baseline_n_kategorier'].median():.0f} ({df['baseline_n_kategorier'].quantile(0.25):.0f}–{df['baseline_n_kategorier'].quantile(0.75):.0f})"))

    tab = pd.DataFrame(rows, columns=["Variabel", "Kategori", "n", "Verdi"])
    print("\n" + tab.to_string(index=False))
    tab.to_csv(OUTPUT_DIR / "tabell1_kohort.csv", index=False)
    return tab


def tabell2_frafall(df):
    """Tabell 2: Frafall og karrierelengde."""
    logger.info("\n=== TABELL 2: Frafall og karrierelengde ===")

    rows = []
    rows.append(("Karrierelengde (år)", "Median (IQR)", "",
                  f"{df['karriere_ar'].median():.0f} ({df['karriere_ar'].quantile(0.25):.0f}–{df['karriere_ar'].quantile(0.75):.0f})"))
    rows.append(("Karrierelengde (år)", "Snitt ± SD", "",
                  f"{df['karriere_ar'].mean():.1f} ± {df['karriere_ar'].std():.1f}"))

    rows.append(("Aktive sesonger", "Median (IQR)", "",
                  f"{df['antall_aktive_sesonger'].median():.0f} ({df['antall_aktive_sesonger'].quantile(0.25):.0f}–{df['antall_aktive_sesonger'].quantile(0.75):.0f})"))

    for var, label in [("aktiv_17", "Aktiv ≥17 år"),
                        ("aktiv_senior", "Aktiv ≥20 år"),
                        ("aktiv_naa", "Aktiv 2024/25")]:
        n = int(df[var].sum())
        rows.append((label, "n (%)", n, f"{n/len(df)*100:.1f}%"))

    # Frafall per kjønn
    for g, label in [("M", "Gutt"), ("F", "Jente")]:
        sub = df[df["gender"] == g]
        rows.append((f"Aktiv ≥20 ({label})", "n (%)",
                      int(sub["aktiv_senior"].sum()),
                      f"{sub['aktiv_senior'].mean()*100:.1f}%"))

    # Frafall per prestasjonskategori
    for kat in ["Svak", "Under snitt", "Middels", "God", "Sterk"]:
        sub = df[df["prestasjonskategori"] == kat]
        if len(sub) > 0:
            rows.append((f"Aktiv ≥20 ({kat})", "n (%)",
                          int(sub["aktiv_senior"].sum()),
                          f"{sub['aktiv_senior'].mean()*100:.1f}%"))

    tab = pd.DataFrame(rows, columns=["Variabel", "Mål", "n", "Verdi"])
    print("\n" + tab.to_string(index=False))
    tab.to_csv(OUTPUT_DIR / "tabell2_frafall.csv", index=False)
    return tab


def tabell3_rae(df):
    """Tabell 3: RAE-fordeling med test."""
    logger.info("\n=== TABELL 3: Relative Age Effect ===")

    valid = df.dropna(subset=["fodt_kvartal"])

    observed = valid["fodt_kvartal"].value_counts().sort_index()
    expected_freq = len(valid) / 4

    chi2, p = stats.chisquare(observed.values, f_exp=[expected_freq] * 4)

    rows = []
    for q in ["Q1", "Q2", "Q3", "Q4"]:
        n = observed.get(q, 0)
        rows.append(("Fødselskvartal", q, n, f"{n/len(valid)*100:.1f}%"))

    rows.append(("Kji-kvadrat-test", f"χ²={chi2:.1f}", "", f"p={p:.4f}"))

    # RAE etter kjønn
    for g, label in [("M", "Gutt"), ("F", "Jente")]:
        sub = valid[valid["gender"] == g]
        obs_g = sub["fodt_kvartal"].value_counts().sort_index()
        exp_g = len(sub) / 4
        chi2_g, p_g = stats.chisquare(obs_g.values, f_exp=[exp_g] * 4)
        for q in ["Q1", "Q2", "Q3", "Q4"]:
            n = obs_g.get(q, 0)
            rows.append((f"Kvartal ({label})", q, n, f"{n/len(sub)*100:.1f}%"))
        rows.append((f"Kji-kvadrat ({label})", f"χ²={chi2_g:.1f}", "", f"p={p_g:.4f}"))

    # RAE vs retention
    for q in ["Q1", "Q2", "Q3", "Q4"]:
        sub = valid[valid["fodt_kvartal"] == q]
        pct_senior = sub["aktiv_senior"].mean() * 100
        rows.append((f"Aktiv ≥20 ({q})", "n (%)",
                      int(sub["aktiv_senior"].sum()),
                      f"{pct_senior:.1f}%"))

    tab = pd.DataFrame(rows, columns=["Variabel", "Kategori", "n", "Verdi"])
    print("\n" + tab.to_string(index=False))
    tab.to_csv(OUTPUT_DIR / "tabell3_rae.csv", index=False)
    return tab


def figur_frafall_per_ar(df):
    """Figur: Andel aktive per alder."""
    logger.info("Lager figur: frafall per alder...")

    ages = range(13, 28)
    pct_all = []
    pct_m = []
    pct_f = []

    for age in ages:
        aktive = (df["alder_ved_slutt"] >= age).sum()
        pct_all.append(aktive / len(df) * 100)
        sub_m = df[df["gender"] == "M"]
        pct_m.append((sub_m["alder_ved_slutt"] >= age).sum() / len(sub_m) * 100)
        sub_f = df[df["gender"] == "F"]
        pct_f.append((sub_f["alder_ved_slutt"] >= age).sum() / len(sub_f) * 100)

    fig, ax = plt.subplots()
    ax.plot(list(ages), pct_all, "k-o", linewidth=2, label="Alle", markersize=5)
    ax.plot(list(ages), pct_m, "b--s", linewidth=1.5, label="Gutt", markersize=4)
    ax.plot(list(ages), pct_f, "r--^", linewidth=1.5, label="Jente", markersize=4)
    ax.set_xlabel("Alder")
    ax.set_ylabel("Andel fremdeles aktive (%)")
    ax.set_title("Frafall fra friidrett etter alder — NCC/PEAB-kohorten")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 105)
    fig.savefig(OUTPUT_DIR / "figur_frafall_alder.png")
    plt.close(fig)
    logger.info(f"  Lagret {OUTPUT_DIR / 'figur_frafall_alder.png'}")


def figur_rae(df):
    """Figur: RAE-fordeling."""
    logger.info("Lager figur: RAE-fordeling...")

    valid = df.dropna(subset=["fodt_kvartal"])

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Venstre: fordeling ved seleksjon
    counts = valid["fodt_kvartal"].value_counts().sort_index()
    colors = ["#2196F3", "#4CAF50", "#FF9800", "#F44336"]
    axes[0].bar(counts.index, counts.values, color=colors)
    axes[0].axhline(len(valid) / 4, color="gray", linestyle="--", label="Forventet (25%)")
    axes[0].set_title("Fødselskvartal ved NCC/PEAB-seleksjon")
    axes[0].set_ylabel("Antall utøvere")
    axes[0].legend()

    # Høyre: retention per kvartal
    retention = []
    for q in ["Q1", "Q2", "Q3", "Q4"]:
        sub = valid[valid["fodt_kvartal"] == q]
        retention.append(sub["aktiv_senior"].mean() * 100)

    axes[1].bar(["Q1", "Q2", "Q3", "Q4"], retention, color=colors)
    axes[1].set_title("Andel aktive som senior (≥20) per kvartal")
    axes[1].set_ylabel("Prosent aktive (%)")

    fig.suptitle("Relative Age Effect — NCC/PEAB-kohorten", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "figur_rae.png")
    plt.close(fig)
    logger.info(f"  Lagret {OUTPUT_DIR / 'figur_rae.png'}")


def figur_tyrving_vs_frafall(df):
    """Figur: Tyrving-poeng vs frafall."""
    logger.info("Lager figur: Tyrving vs frafall...")

    valid = df.dropna(subset=["tyrving_best", "prestasjonskategori"])

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Venstre: Tyrving-fordeling per frafall-status
    still_active = valid[valid["aktiv_senior"] == 1]["tyrving_best"]
    dropped = valid[valid["aktiv_senior"] == 0]["tyrving_best"]
    axes[0].hist(dropped, bins=30, alpha=0.6, label=f"Sluttet (n={len(dropped)})", color="gray")
    axes[0].hist(still_active, bins=30, alpha=0.7, label=f"Aktiv ≥20 (n={len(still_active)})", color="#2196F3")
    axes[0].set_xlabel("Tyrving-poeng (best ved NCC/PEAB)")
    axes[0].set_ylabel("Antall utøvere")
    axes[0].set_title("Prestasjon vs senioraktivitet")
    axes[0].legend()

    # Høyre: Karrierelengde per prestasjonskategori
    kat_order = ["Svak", "Under snitt", "Middels", "God", "Sterk"]
    data_box = [valid[valid["prestasjonskategori"] == k]["karriere_ar"].values for k in kat_order]
    bp = axes[1].boxplot(data_box, labels=kat_order, patch_artist=True)
    colors_box = ["#F44336", "#FF9800", "#4CAF50", "#2196F3", "#9C27B0"]
    for patch, color in zip(bp["boxes"], colors_box):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    axes[1].set_xlabel("Prestasjonskategori (Tyrving)")
    axes[1].set_ylabel("Karrierelengde (år)")
    axes[1].set_title("Karrierelengde per prestasjonsnivå")

    fig.suptitle("Prestasjonsnivå og frafall — NCC/PEAB-kohorten", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "figur_tyrving_frafall.png")
    plt.close(fig)
    logger.info(f"  Lagret {OUTPUT_DIR / 'figur_tyrving_frafall.png'}")


def figur_allsidighet(df):
    """Figur: Allsidighet vs frafall."""
    logger.info("Lager figur: allsidighet vs frafall...")

    valid = df.dropna(subset=["hhi_early"])

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Venstre: HHI-fordeling
    axes[0].hist(valid["hhi_early"], bins=20, color="#4CAF50", alpha=0.7, edgecolor="white")
    axes[0].set_xlabel("HHI (1.0 = ren spesialist, lavt = allsidig)")
    axes[0].set_ylabel("Antall utøvere")
    axes[0].set_title("Tidlig spesialisering (HHI)")
    axes[0].axvline(valid["hhi_early"].median(), color="red", linestyle="--",
                     label=f"Median = {valid['hhi_early'].median():.2f}")
    axes[0].legend()

    # Høyre: Senior-aktivitet per allsidighetsgruppe
    valid = valid.copy()
    valid["allsidig_gruppe"] = pd.cut(
        valid["hhi_early"],
        bins=[0, 0.33, 0.5, 1.01],
        labels=["Allsidig\n(HHI<0.33)", "Moderat\n(0.33-0.50)", "Spesialist\n(HHI>0.50)"],
    )
    grouped = valid.groupby("allsidig_gruppe", observed=True)["aktiv_senior"].agg(["sum", "count", "mean"])
    axes[1].bar(range(len(grouped)), grouped["mean"] * 100, color=["#4CAF50", "#FF9800", "#F44336"])
    axes[1].set_xticks(range(len(grouped)))
    axes[1].set_xticklabels(grouped.index)
    for i, (_, row) in enumerate(grouped.iterrows()):
        axes[1].text(i, row["mean"] * 100 + 1, f"{int(row['sum'])}/{int(row['count'])}",
                      ha="center", fontsize=9)
    axes[1].set_ylabel("Prosent aktive som senior (%)")
    axes[1].set_title("Senioraktivitet per spesialiseringsgrad")

    fig.suptitle("Allsidighet og frafall — NCC/PEAB-kohorten", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "figur_allsidighet.png")
    plt.close(fig)
    logger.info(f"  Lagret {OUTPUT_DIR / 'figur_allsidighet.png'}")


def main():
    df = last_data()
    logger.info(f"Lastet {len(df)} utøvere med {len(df.columns)} variabler")

    tabell1_kohort(df)
    tabell2_frafall(df)
    tabell3_rae(df)

    figur_frafall_per_ar(df)
    figur_rae(df)
    figur_tyrving_vs_frafall(df)
    figur_allsidighet(df)

    logger.info(f"\nAlle tabeller og figurer lagret i {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
