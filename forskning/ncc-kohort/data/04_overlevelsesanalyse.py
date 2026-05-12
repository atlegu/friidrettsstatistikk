"""
Steg 4: Overlevelsesanalyse (survival analysis) for NCC/PEAB-kohorten.

Kaplan-Meier-kurver og Cox proportional hazards-regresjon.

Produserer:
  - Kaplan-Meier-figurer (samlet, per kjønn, prestasjon, allsidighet, RAE)
  - Cox-regresjonsresultater (konsoll + CSV)
  - Figurer i output/

Bruk: python 04_overlevelsesanalyse.py
"""

import logging
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter, CoxPHFitter
from lifelines.statistics import logrank_test, multivariate_logrank_test

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
    df["event_observed"] = 1 - df["aktiv_naa"]
    df["duration"] = df["karriere_ar"].clip(lower=0)
    return df


# === KAPLAN-MEIER ===

def km_samlet(df):
    """Kaplan-Meier: samlet overlevelseskurve."""
    logger.info("KM: Samlet overlevelseskurve...")

    kmf = KaplanMeierFitter()
    kmf.fit(df["duration"], df["event_observed"], label="Alle (n=1301)")

    fig, ax = plt.subplots()
    kmf.plot_survival_function(ax=ax, ci_show=True)
    ax.set_xlabel("År etter NCC/PEAB")
    ax.set_ylabel("Andel fremdeles aktive")
    ax.set_title("Kaplan-Meier: Frafall fra friidrett — NCC/PEAB-kohorten")
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)

    median = kmf.median_survival_time_
    ax.axhline(0.5, color="gray", linestyle=":", alpha=0.5)
    ax.axvline(median, color="gray", linestyle=":", alpha=0.5)
    ax.text(median + 0.3, 0.52, f"Median = {median:.1f} år", fontsize=10)

    fig.savefig(OUTPUT_DIR / "km_samlet.png")
    plt.close(fig)

    logger.info(f"  Median overlevelse: {median:.1f} år")
    logger.info(f"  5 år: {kmf.predict(5):.1%}")
    logger.info(f"  10 år: {kmf.predict(10):.1%}")


def km_per_gruppe(df, gruppevariabel, labels, tittel, filnavn, farger=None):
    """Generisk KM per grupperingsvariabel."""
    logger.info(f"KM: {tittel}...")

    valid = df.dropna(subset=[gruppevariabel])
    fig, ax = plt.subplots()

    grupper = sorted(valid[gruppevariabel].unique())
    if labels:
        grupper = [g for g in labels if g in valid[gruppevariabel].values]

    default_colors = ["#2196F3", "#F44336", "#4CAF50", "#FF9800", "#9C27B0"]
    colors = farger or default_colors

    for i, g in enumerate(grupper):
        sub = valid[valid[gruppevariabel] == g]
        kmf = KaplanMeierFitter()
        lab = f"{labels.get(g, g) if isinstance(labels, dict) else g} (n={len(sub)})"
        kmf.fit(sub["duration"], sub["event_observed"], label=lab)
        kmf.plot_survival_function(ax=ax, ci_show=False, color=colors[i % len(colors)])

    ax.set_xlabel("År etter NCC/PEAB")
    ax.set_ylabel("Andel fremdeles aktive")
    ax.set_title(f"Kaplan-Meier: {tittel}")
    ax.legend(loc="upper right", fontsize=9)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)

    # Log-rank test
    try:
        result = multivariate_logrank_test(
            valid["duration"], valid[gruppevariabel], valid["event_observed"]
        )
        p = result.p_value
        ax.text(0.02, 0.02, f"Log-rank p = {p:.4f}", transform=ax.transAxes,
                fontsize=10, verticalalignment="bottom")
        logger.info(f"  Log-rank p = {p:.4f}")
    except Exception as e:
        logger.warning(f"  Log-rank feilet: {e}")

    fig.savefig(OUTPUT_DIR / filnavn)
    plt.close(fig)


def km_analyser(df):
    """Alle KM-analyser."""

    # Per kjønn
    valid_kjonn = df[df["gender"].isin(["M", "F"])]
    km_per_gruppe(valid_kjonn, "gender",
                  labels=["M", "F"],
                  tittel="Frafall per kjønn",
                  filnavn="km_kjonn.png",
                  farger=["#2196F3", "#F44336"])

    # Per prestasjonskategori
    km_per_gruppe(df, "prestasjonskategori",
                  labels=["Svak", "Under snitt", "Middels", "God", "Sterk"],
                  tittel="Frafall per prestasjonsnivå (Tyrving)",
                  filnavn="km_prestasjon.png",
                  farger=["#F44336", "#FF9800", "#4CAF50", "#2196F3", "#9C27B0"])

    # Per fødselskvartal
    km_per_gruppe(df, "fodt_kvartal",
                  labels=["Q1", "Q2", "Q3", "Q4"],
                  tittel="Frafall per fødselskvartal (RAE)",
                  filnavn="km_rae.png")

    # Per allsidighet (dikotomisert)
    df_hhi = df.dropna(subset=["hhi_early"]).copy()
    df_hhi["spesialisering"] = pd.cut(
        df_hhi["hhi_early"],
        bins=[0, 0.33, 0.5, 1.01],
        labels=["Allsidig", "Moderat", "Spesialist"],
    )
    km_per_gruppe(df_hhi, "spesialisering",
                  labels=["Allsidig", "Moderat", "Spesialist"],
                  tittel="Frafall per spesialiseringsgrad (HHI)",
                  filnavn="km_allsidighet.png",
                  farger=["#4CAF50", "#FF9800", "#F44336"])

    # Deltok begge år
    km_per_gruppe(df, "deltok_begge_aar",
                  labels=[0, 1],
                  tittel="Frafall: deltok ett vs. to NCC/PEAB-år",
                  filnavn="km_begge_aar.png",
                  farger=["#F44336", "#2196F3"])


# === COX REGRESJON ===

def cox_regresjon(df):
    """Cox proportional hazards-regresjon."""
    logger.info("\n=== COX PROPORSJONAL HAZARD ===")

    # Forbered kovariater
    cox_df = df[["duration", "event_observed"]].copy()

    # Kjønn (M=0, F=1)
    cox_df["kjonn_f"] = (df["gender"] == "F").astype(float)

    # Tyrving (z-normalisert)
    tyrving = df["tyrving_best"].copy()
    cox_df["tyrving_z"] = (tyrving - tyrving.mean()) / tyrving.std()

    # Allsidighet (HHI, z-normalisert, høyere = mer spesialisert)
    hhi = df["hhi_early"].copy()
    cox_df["hhi_z"] = (hhi - hhi.mean()) / hhi.std()

    # Baseline antall kategorier
    cox_df["n_kategorier"] = df["baseline_n_kategorier"].astype(float)

    # RAE (kvartal som ordinal)
    kvartal_map = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}
    cox_df["fodt_kvartal_num"] = df["fodt_kvartal"].map(kvartal_map).astype(float)

    # Konkurransefrekvens (stevner baseline)
    cox_df["stevner_baseline"] = df["stevner_baseline_ar"].astype(float)

    # Deltok begge år
    cox_df["deltok_begge"] = df["deltok_begge_aar"].astype(float)

    # Fødselsår (sentrert)
    cox_df["fodt_aar_c"] = (df["birth_year"] - 1999).astype(float)

    # Dropp rader med manglende verdier
    n_before = len(cox_df)
    cox_df = cox_df.dropna()
    n_after = len(cox_df)
    logger.info(f"  Dropper {n_before - n_after} rader med manglende verdier ({n_after} gjenstår)")

    # Fit modell
    cph = CoxPHFitter()
    cph.fit(
        cox_df,
        duration_col="duration",
        event_col="event_observed",
    )

    print("\n--- Cox PH-resultater ---")
    cph.print_summary(columns=["coef", "exp(coef)", "se(coef)", "z", "p", "lower 0.95", "upper 0.95"])

    # Lagre
    summary = cph.summary
    summary.to_csv(OUTPUT_DIR / "cox_resultater.csv")
    logger.info(f"  Lagret Cox-resultater til {OUTPUT_DIR / 'cox_resultater.csv'}")

    # Sjekk proporsjonalitetsantakelse
    logger.info("\n  Sjekker proporsjonal hazards-antakelse...")
    try:
        ph_test = cph.check_assumptions(cox_df, p_value_threshold=0.05, show_plots=False)
        logger.info("  PH-test: se utskrift over")
    except Exception as e:
        logger.info(f"  PH-test: {e}")

    # Forest plot
    fig, ax = plt.subplots(figsize=(8, 5))
    cph.plot(ax=ax, hazard_ratios=True)
    ax.set_title("Cox PH: Hazard ratios for frafall")
    ax.axvline(1, color="gray", linestyle="--", alpha=0.5)
    fig.savefig(OUTPUT_DIR / "cox_forest_plot.png")
    plt.close(fig)
    logger.info(f"  Lagret {OUTPUT_DIR / 'cox_forest_plot.png'}")

    return cph


def cox_stegvis(df):
    """Stegvis Cox-modell: univariate + multivariat."""
    logger.info("\n=== UNIVARIATE COX-ANALYSER ===")

    cox_base = df[["duration", "event_observed"]].copy()

    variabler = {
        "kjonn_f": (df["gender"] == "F").astype(float),
        "tyrving_z": (df["tyrving_best"] - df["tyrving_best"].mean()) / df["tyrving_best"].std(),
        "hhi_z": (df["hhi_early"] - df["hhi_early"].mean()) / df["hhi_early"].std(),
        "n_kategorier": df["baseline_n_kategorier"].astype(float),
        "fodt_kvartal_num": df["fodt_kvartal"].map({"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}).astype(float),
        "stevner_baseline": df["stevner_baseline_ar"].astype(float),
        "deltok_begge": df["deltok_begge_aar"].astype(float),
    }

    rows = []
    for name, series in variabler.items():
        temp = cox_base.copy()
        temp[name] = series
        temp = temp.dropna()

        cph = CoxPHFitter()
        try:
            cph.fit(temp, duration_col="duration", event_col="event_observed")
            s = cph.summary.loc[name]
            rows.append({
                "Variabel": name,
                "HR": f"{s['exp(coef)']:.3f}",
                "95% KI": f"{s['exp(coef) lower 95%']:.3f}–{s['exp(coef) upper 95%']:.3f}",
                "p": f"{s['p']:.4f}",
                "n": len(temp),
            })
            logger.info(f"  {name:25s}  HR={s['exp(coef)']:.3f} ({s['exp(coef) lower 95%']:.3f}–{s['exp(coef) upper 95%']:.3f})  p={s['p']:.4f}")
        except Exception as e:
            logger.warning(f"  {name}: feilet ({e})")

    uni_tab = pd.DataFrame(rows)
    print("\n--- Univariate Cox-resultater ---")
    print(uni_tab.to_string(index=False))
    uni_tab.to_csv(OUTPUT_DIR / "cox_univariat.csv", index=False)


def main():
    df = last_data()
    logger.info(f"Lastet {len(df)} utøvere")

    # Kaplan-Meier
    km_samlet(df)
    km_analyser(df)

    # Cox
    cox_stegvis(df)
    cox_regresjon(df)

    logger.info(f"\nAlle resultater lagret i {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
