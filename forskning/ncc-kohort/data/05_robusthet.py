"""
Steg 5: Robusthetsanalyser for NCC/PEAB-kohortstudien.

1. Fikser brudd på PH-antakelsen (stratifisering, binning)
2. Sensitivitetsanalyser (COVID, alternativ frafallsdefinisjon)
3. Mediatoranalyse (engasjement som mediator mellom prestasjon og frafall)

Bruk: python 05_robusthet.py
"""

import logging
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from lifelines import CoxPHFitter, KaplanMeierFitter
from lifelines.statistics import logrank_test

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent
OUTPUT_DIR = DATA_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.size": 11,
    "figure.dpi": 150,
    "savefig.bbox": "tight",
})


def last_data():
    df = pd.read_csv(DATA_DIR / "analysedata.csv")
    df["event_observed"] = 1 - df["aktiv_naa"]
    df["duration"] = df["karriere_ar"].clip(lower=0)
    return df


def forbered_cox_df(df):
    """Forbered standardiserte kovariater for Cox-modell."""
    cox = df[["athlete_id", "duration", "event_observed"]].copy()
    cox["kjonn_f"] = (df["gender"] == "F").astype(float)
    cox["tyrving_z"] = (df["tyrving_best"] - df["tyrving_best"].mean()) / df["tyrving_best"].std()
    cox["hhi_z"] = (df["hhi_early"] - df["hhi_early"].mean()) / df["hhi_early"].std()
    cox["n_kategorier"] = df["baseline_n_kategorier"].astype(float)
    cox["fodt_kvartal_num"] = df["fodt_kvartal"].map(
        {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}
    ).astype(float)
    cox["stevner_baseline"] = df["stevner_baseline_ar"].astype(float)
    cox["deltok_begge"] = df["deltok_begge_aar"].astype(float)
    cox["fodt_aar_c"] = (df["birth_year"] - 1999).astype(float)
    return cox


# =======================================================================
# 1. FIKSET COX-MODELL — stratifisering for PH-brudd
# =======================================================================

def cox_stratifisert(df):
    """Cox-modell med stratifisering på deltok_begge og binnet stevner."""
    logger.info("=== 1. STRATIFISERT COX-MODELL ===")

    cox = forbered_cox_df(df)

    # Bin stevner_baseline (PH-brudd ved kontinuerlig)
    cox["stevner_bin"] = pd.cut(
        cox["stevner_baseline"],
        bins=[0, 5, 10, 15, 100],
        labels=["1-5", "6-10", "11-15", "16+"],
    )

    cox_clean = cox.drop(columns=["athlete_id", "stevner_baseline"]).dropna()
    n_orig = len(cox)
    n_clean = len(cox_clean)
    logger.info(f"  n={n_clean} (droppet {n_orig - n_clean} med manglende verdier)")

    # Stratifiser på deltok_begge og stevner_bin (begge brøt PH)
    # Kovariater som testes: kjonn, tyrving, hhi, n_kategorier, RAE, fødselsår
    strata_cols = ["deltok_begge", "stevner_bin"]
    covariate_cols = ["kjonn_f", "tyrving_z", "hhi_z", "n_kategorier",
                      "fodt_kvartal_num", "fodt_aar_c"]

    model_df = cox_clean[["duration", "event_observed"] + covariate_cols + strata_cols].copy()

    cph = CoxPHFitter()
    cph.fit(
        model_df,
        duration_col="duration",
        event_col="event_observed",
        strata=strata_cols,
    )

    print("\n--- Stratifisert Cox (strata: deltok_begge, stevner_bin) ---")
    cph.print_summary(columns=["coef", "exp(coef)", "se(coef)", "z", "p",
                                "lower 0.95", "upper 0.95"])

    cph.summary.to_csv(OUTPUT_DIR / "cox_stratifisert.csv")
    logger.info(f"  Lagret {OUTPUT_DIR / 'cox_stratifisert.csv'}")

    # Sjekk PH på nytt
    logger.info("  Sjekker PH-antakelse for stratifisert modell...")
    try:
        cph.check_assumptions(model_df, p_value_threshold=0.05, show_plots=False)
    except Exception as e:
        logger.info(f"  PH-test: {e}")

    # Forest plot
    fig, ax = plt.subplots(figsize=(8, 4))
    cph.plot(ax=ax, hazard_ratios=True)
    ax.set_title("Stratifisert Cox PH: Hazard ratios\n(stratifisert på deltok_begge og stevnefrekvens)")
    ax.axvline(1, color="gray", linestyle="--", alpha=0.5)
    fig.savefig(OUTPUT_DIR / "cox_stratifisert_forest.png")
    plt.close(fig)

    return cph


# =======================================================================
# 2. SENSITIVITETSANALYSER
# =======================================================================

def sensitivitet_frafallsdefinisjon(df):
    """Alternativ frafallsdefinisjon: ≥1 resultat = aktiv sesong."""
    logger.info("\n=== 2a. SENSITIVITET: Alternativ frafallsdefinisjon (≥1 resultat) ===")

    karriere = pd.read_csv(DATA_DIR / "karrieredata.csv")
    karriere["year"] = pd.to_datetime(karriere["date"]).dt.year

    NCC = {"ncc_2011": 2011, "ncc_2012": 2012, "peab_2013": 2013, "peab_2014": 2014}

    # Beregn siste år med minst 1 resultat (mildere krav)
    siste_resultat = karriere.groupby("athlete_id")["year"].max().reset_index()
    siste_resultat.columns = ["athlete_id", "siste_resultat_ar_mild"]

    df_alt = df.merge(siste_resultat, on="athlete_id", how="left")
    df_alt["siste_resultat_ar_mild"] = df_alt["siste_resultat_ar_mild"].fillna(
        df_alt["birth_year"] + 13
    )

    stevne_aar = df_alt["forste_utgave"].map(NCC)
    df_alt["duration_mild"] = (df_alt["siste_resultat_ar_mild"] - stevne_aar).clip(lower=0)
    df_alt["event_mild"] = (df_alt["siste_resultat_ar_mild"] < 2024).astype(int)

    # Sammenlign med streng definisjon
    logger.info(f"  Streng (≥2 res): median karriere = {df['karriere_ar'].median():.0f} år")
    logger.info(f"  Mild (≥1 res):   median karriere = {df_alt['duration_mild'].median():.0f} år")
    logger.info(f"  Streng: aktiv senior = {df['aktiv_senior'].mean()*100:.1f}%")

    alder_siste_mild = df_alt["siste_resultat_ar_mild"] - df_alt["birth_year"]
    senior_mild = (alder_siste_mild >= 20).mean() * 100
    logger.info(f"  Mild:   aktiv senior = {senior_mild:.1f}%")

    # Cox med mild definisjon
    cox = forbered_cox_df(df_alt)
    cox["duration"] = df_alt["duration_mild"]
    cox["event_observed"] = df_alt["event_mild"]
    cox["stevner_bin"] = pd.cut(
        cox["stevner_baseline"], bins=[0, 5, 10, 15, 100], labels=["1-5", "6-10", "11-15", "16+"]
    )

    covariate_cols = ["kjonn_f", "tyrving_z", "hhi_z", "n_kategorier",
                      "fodt_kvartal_num", "fodt_aar_c"]
    strata_cols = ["deltok_begge", "stevner_bin"]
    model_df = cox[["duration", "event_observed"] + covariate_cols + strata_cols].dropna()

    cph = CoxPHFitter()
    cph.fit(model_df, duration_col="duration", event_col="event_observed", strata=strata_cols)

    print("\n--- Cox med mild frafallsdefinisjon (≥1 resultat = aktiv) ---")
    cph.print_summary(columns=["coef", "exp(coef)", "p"])
    cph.summary.to_csv(OUTPUT_DIR / "cox_mild_definisjon.csv")

    return cph


def sensitivitet_covid(df):
    """Ekskluder COVID-perioden 2020–2021."""
    logger.info("\n=== 2b. SENSITIVITET: Ekskluder COVID 2020–2021 ===")

    karriere = pd.read_csv(DATA_DIR / "karrieredata.csv")
    karriere["year"] = pd.to_datetime(karriere["date"]).dt.year

    # Fjern resultater fra 2020-2021
    karriere_no_covid = karriere[~karriere["year"].isin([2020, 2021])]

    NCC = {"ncc_2011": 2011, "ncc_2012": 2012, "peab_2013": 2013, "peab_2014": 2014}

    # Reberegn aktive sesonger uten COVID
    per_utover_ar = (
        karriere_no_covid.groupby(["athlete_id", "year"])
        .agg(n_res=("id", "count"))
        .reset_index()
    )
    aktive = per_utover_ar[per_utover_ar["n_res"] >= 2]

    siste_aktive = aktive.groupby("athlete_id")["year"].max().reset_index()
    siste_aktive.columns = ["athlete_id", "siste_aktive_nocovid"]

    df_nc = df.merge(siste_aktive, on="athlete_id", how="left")
    stevne_aar = df_nc["forste_utgave"].map(NCC)
    df_nc["siste_aktive_nocovid"] = df_nc["siste_aktive_nocovid"].fillna(stevne_aar)

    df_nc["duration_nc"] = (df_nc["siste_aktive_nocovid"] - stevne_aar).clip(lower=0)
    df_nc["event_nc"] = (df_nc["siste_aktive_nocovid"] < 2024).astype(int)

    logger.info(f"  Med COVID:  median karriere = {df['karriere_ar'].median():.0f} år")
    logger.info(f"  Uten COVID: median karriere = {df_nc['duration_nc'].median():.0f} år")

    # Cox uten COVID
    cox = forbered_cox_df(df_nc)
    cox["duration"] = df_nc["duration_nc"]
    cox["event_observed"] = df_nc["event_nc"]
    cox["stevner_bin"] = pd.cut(
        cox["stevner_baseline"], bins=[0, 5, 10, 15, 100], labels=["1-5", "6-10", "11-15", "16+"]
    )

    covariate_cols = ["kjonn_f", "tyrving_z", "hhi_z", "n_kategorier",
                      "fodt_kvartal_num", "fodt_aar_c"]
    strata_cols = ["deltok_begge", "stevner_bin"]
    model_df = cox[["duration", "event_observed"] + covariate_cols + strata_cols].dropna()

    cph = CoxPHFitter()
    cph.fit(model_df, duration_col="duration", event_col="event_observed", strata=strata_cols)

    print("\n--- Cox uten COVID 2020–2021 ---")
    cph.print_summary(columns=["coef", "exp(coef)", "p"])
    cph.summary.to_csv(OUTPUT_DIR / "cox_uten_covid.csv")

    return cph


# =======================================================================
# 3. MEDIATORANALYSE
# =======================================================================

def mediatoranalyse(df):
    """Test om engasjement medierer effekten av prestasjon på frafall."""
    logger.info("\n=== 3. MEDIATORANALYSE: Prestasjon → Engasjement → Frafall ===")

    cox_base = df[["duration", "event_observed"]].copy()
    cox_base["tyrving_z"] = (df["tyrving_best"] - df["tyrving_best"].mean()) / df["tyrving_best"].std()
    cox_base["stevner_baseline"] = df["stevner_baseline_ar"].astype(float)
    cox_base["deltok_begge"] = df["deltok_begge_aar"].astype(float)
    cox_base["kjonn_f"] = (df["gender"] == "F").astype(float)
    cox_base = cox_base.dropna()

    logger.info(f"  n = {len(cox_base)}")

    # Steg 1: Total effekt (tyrving → frafall, uten mediatorer)
    cph1 = CoxPHFitter()
    cph1.fit(
        cox_base[["duration", "event_observed", "tyrving_z", "kjonn_f"]],
        duration_col="duration", event_col="event_observed",
    )
    total = cph1.summary.loc["tyrving_z"]
    print(f"\n  Steg 1 — Total effekt (Tyrving → frafall):")
    print(f"    HR = {total['exp(coef)']:.3f} ({total['exp(coef) lower 95%']:.3f}–{total['exp(coef) upper 95%']:.3f}), p = {total['p']:.4f}")

    # Steg 2: Tyrving → engasjement (OLS)
    from scipy import stats as sp_stats
    r_stevner, p_stevner = sp_stats.pearsonr(cox_base["tyrving_z"], cox_base["stevner_baseline"])
    r_deltok, p_deltok = sp_stats.pointbiserialr(cox_base["tyrving_z"], cox_base["deltok_begge"])

    print(f"\n  Steg 2 — Tyrving → Engasjement:")
    print(f"    Tyrving ↔ stevner_baseline:  r = {r_stevner:.3f}, p = {p_stevner:.4f}")
    print(f"    Tyrving ↔ deltok_begge:      r = {r_deltok:.3f}, p = {p_deltok:.4f}")

    # Steg 3: Direkte effekt (tyrving → frafall, kontrollert for engasjement)
    cph3 = CoxPHFitter()
    cph3.fit(
        cox_base[["duration", "event_observed", "tyrving_z", "stevner_baseline",
                  "deltok_begge", "kjonn_f"]],
        duration_col="duration", event_col="event_observed",
    )
    direkte = cph3.summary.loc["tyrving_z"]
    print(f"\n  Steg 3 — Direkte effekt (kontrollert for engasjement):")
    print(f"    HR = {direkte['exp(coef)']:.3f} ({direkte['exp(coef) lower 95%']:.3f}–{direkte['exp(coef) upper 95%']:.3f}), p = {direkte['p']:.4f}")

    # Oppsummering
    total_coef = total["coef"]
    direkte_coef = direkte["coef"]
    indirekte = total_coef - direkte_coef
    pct_mediert = (indirekte / total_coef) * 100 if total_coef != 0 else 0

    print(f"\n  === MEDIATORANALYSE OPPSUMMERING ===")
    print(f"  Total effekt (log-HR):    {total_coef:.4f}")
    print(f"  Direkte effekt (log-HR):  {direkte_coef:.4f}")
    print(f"  Indirekte (mediert):      {indirekte:.4f}")
    print(f"  Andel mediert:            {pct_mediert:.1f}%")

    if abs(pct_mediert) > 50:
        print(f"\n  → Engasjement medierer >{abs(pct_mediert):.0f}% av prestasjonseffekten.")
        print(f"    Prestasjon påvirker frafall primært GJENNOM engasjement.")
    else:
        print(f"\n  → Delvis mediering ({abs(pct_mediert):.0f}%). Prestasjon har også en direkte effekt.")

    # Figur: mediatordiagram
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    # Bokser
    boxes = {
        "Prestasjon\n(Tyrving-poeng)": (1, 3),
        "Engasjement\n(stevner, deltok begge)": (5, 5),
        "Frafall\n(karrierelengde)": (9, 3),
    }
    for label, (x, y) in boxes.items():
        ax.add_patch(plt.Rectangle((x - 1.2, y - 0.6), 2.4, 1.2,
                                    facecolor="lightblue", edgecolor="black", linewidth=1.5))
        ax.text(x, y, label, ha="center", va="center", fontsize=10, fontweight="bold")

    # Piler
    # a-sti: Prestasjon → Engasjement
    ax.annotate("", xy=(3.8, 4.8), xytext=(2.2, 3.6),
                arrowprops=dict(arrowstyle="->", lw=2, color="blue"))
    ax.text(2.5, 4.5, f"r = {r_stevner:.2f}***\nr = {r_deltok:.2f}***",
            fontsize=9, color="blue")

    # b-sti: Engasjement → Frafall
    ax.annotate("", xy=(7.8, 3.6), xytext=(6.2, 4.8),
                arrowprops=dict(arrowstyle="->", lw=2, color="blue"))
    ax.text(7.2, 4.5, f"HR={cph3.summary.loc['stevner_baseline','exp(coef)']:.2f}***\n"
                       f"HR={cph3.summary.loc['deltok_begge','exp(coef)']:.2f}***",
            fontsize=9, color="blue")

    # c'-sti: Prestasjon → Frafall (direkte)
    ax.annotate("", xy=(7.8, 3), xytext=(2.2, 3),
                arrowprops=dict(arrowstyle="->", lw=2,
                                color="red" if direkte["p"] > 0.05 else "green"))
    p_label = "ns" if direkte["p"] > 0.05 else f"p={direkte['p']:.3f}"
    ax.text(5, 2.3, f"Direkte: HR={direkte['exp(coef)']:.2f} ({p_label})\n"
                     f"Total: HR={total['exp(coef)']:.2f}***\n"
                     f"Mediert: {pct_mediert:.0f}%",
            ha="center", fontsize=9, fontweight="bold",
            color="red" if direkte["p"] > 0.05 else "green")

    ax.set_title("Mediatoranalyse: Prestasjon → Engasjement → Frafall", fontsize=13, pad=20)
    fig.savefig(OUTPUT_DIR / "mediatoranalyse.png")
    plt.close(fig)
    logger.info(f"  Lagret {OUTPUT_DIR / 'mediatoranalyse.png'}")

    # Lagre resultater
    results = pd.DataFrame({
        "Steg": ["Total", "Direkte", "Indirekte"],
        "log-HR": [total_coef, direkte_coef, indirekte],
        "HR": [total["exp(coef)"], direkte["exp(coef)"], np.exp(indirekte)],
        "p": [total["p"], direkte["p"], None],
        "andel_mediert": [None, None, f"{pct_mediert:.1f}%"],
    })
    results.to_csv(OUTPUT_DIR / "mediatoranalyse_resultater.csv", index=False)


# =======================================================================
# 4. SAMMENLIGNING AV ALLE MODELLER
# =======================================================================

def sammenlign_modeller(df):
    """Sammenlign resultater på tvers av alle modellspesifikasjoner."""
    logger.info("\n=== 4. MODELLSAMMENLIGNING ===")

    filer = {
        "Hovedmodell": "cox_resultater.csv",
        "Stratifisert": "cox_stratifisert.csv",
        "Mild definisjon": "cox_mild_definisjon.csv",
        "Uten COVID": "cox_uten_covid.csv",
    }

    rows = []
    for modell, fil in filer.items():
        path = OUTPUT_DIR / fil
        if not path.exists():
            continue
        res = pd.read_csv(path, index_col=0)
        for var in res.index:
            if var in ["deltok_begge", "stevner_baseline", "stevner_bin"]:
                continue
            hr = res.loc[var, "exp(coef)"]
            p = res.loc[var, "p"]
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            rows.append({"Modell": modell, "Variabel": var,
                         "HR": f"{hr:.3f}{sig}", "p": f"{p:.4f}"})

    sammenligning = pd.DataFrame(rows)
    pivot = sammenligning.pivot(index="Variabel", columns="Modell", values="HR")
    print("\n--- Hazard Ratios på tvers av modeller ---")
    print(pivot.to_string())
    pivot.to_csv(OUTPUT_DIR / "modellsammenligning.csv")
    logger.info(f"  Lagret {OUTPUT_DIR / 'modellsammenligning.csv'}")


def main():
    df = last_data()
    logger.info(f"Lastet {len(df)} utøvere")

    cox_stratifisert(df)
    sensitivitet_frafallsdefinisjon(df)
    sensitivitet_covid(df)
    mediatoranalyse(df)
    sammenlign_modeller(df)

    logger.info(f"\nAlle robusthetsanalyser lagret i {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
