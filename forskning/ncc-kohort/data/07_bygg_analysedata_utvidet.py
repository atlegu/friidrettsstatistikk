"""
Steg 7: Bygg analysedata for utvidet kohort (1998-2002).

Inkluderer alle originale variabler PLUSS behavioral engagement-variabler:
- Konkurransevolum per aldersår (13-17)
- HHI per aldersår (spesialiserings-trajectory)
- Antall mesterskap-typer per aldersår
- Performance peak og slope før milepælen
- Helårs-deltakelse

Leser: kohort_utvidet.csv, karrieredata_utvidet.csv, Tyrvingtabellen
Skriver: analysedata_utvidet.csv
"""

import logging
from pathlib import Path

import pandas as pd
import numpy as np

from tyrvingtabellen import parse_tyrving_xls, beregn_tyrving_poeng

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent
KOHORT_FILE = DATA_DIR / "kohort_utvidet.csv"
KARRIERE_FILE = DATA_DIR / "karrieredata_utvidet.csv"
OUTPUT_FILE = DATA_DIR / "analysedata_utvidet.csv"

# Hele serien med ungdomsleker
LEKENE_EDITIONS = {
    "ncc_2011": 2011, "ncc_2012": 2012,
    "peab_2013": 2013, "peab_2014": 2014,
    "bendit_2015": 2015, "ungdomslekene_2016": 2016,
}

STEVNE_NAME_PATTERNS = {
    "ncc_2011": "NCC", "ncc_2012": "NCC",
    "peab_2013": "PEAB", "peab_2014": "eab",
    "bendit_2015": "endit", "ungdomslekene_2016": "ngdomsleken",
}

# Datakvalitetsfilter — minimumstider i centisekunder
MIN_PERFORMANCE_CS = {
    "60m": 600, "80m": 800, "100m": 1000, "200m": 2000,
    "300m": 3500, "400m": 4500, "600m": 8000, "800m": 11000,
    "1000m": 15000, "1500m": 23000, "2000m": 32000, "3000m": 50000,
    "60mh": 700, "80mh": 1000, "200mh": 2500, "300mh": 4000,
    "1500msc": 25000, "2000msc": 35000,
}

# Capping av urealistiske Tyrving-poeng (datakvalitet)
TYRVING_CAP = 1500


# =============================================================================
# Helper functions
# =============================================================================

def beregn_alder_kalender(birth_year, competition_year):
    """Norsk friidrett: alder = konkurranseår − fødselsår."""
    if pd.isna(birth_year):
        return None
    return int(competition_year) - int(birth_year)


def _filtrer_ugyldige_tider(df):
    """Fjern resultater med åpenbart feilregistrerte tider."""
    mask = pd.Series(True, index=df.index)
    for ec, min_cs in MIN_PERFORMANCE_CS.items():
        feil = (df["event_code"] == ec) & (df["performance_value"] < min_cs)
        mask &= ~feil
    return df[mask].copy()


# =============================================================================
# Data loading
# =============================================================================

def last_data():
    kohort = pd.read_csv(KOHORT_FILE)
    karriere = pd.read_csv(KARRIERE_FILE)
    karriere["date"] = pd.to_datetime(karriere["date"])
    karriere["year"] = karriere["date"].dt.year

    # Beregn alder ved hvert resultat
    kohort_lookup = kohort.set_index("athlete_id")["birth_year"].to_dict()
    karriere["birth_year"] = karriere["athlete_id"].map(kohort_lookup)
    karriere["age"] = karriere["year"] - karriere["birth_year"]

    return kohort, karriere


# =============================================================================
# 1. FRAFALL
# =============================================================================

def beregn_frafall(kohort, karriere):
    """Frafallsvariabler per utøver."""
    logger.info("Beregner frafall...")

    per_utover_ar = (
        karriere.groupby(["athlete_id", "year"])
        .agg(antall_resultater=("id", "count"), antall_stevner=("meet_id", "nunique"))
        .reset_index()
    )

    aktive_sesonger = per_utover_ar[per_utover_ar["antall_resultater"] >= 2]

    frafall = {}
    for _, row in kohort.iterrows():
        aid = row["athlete_id"]
        birth_year = row["birth_year"]
        stevne_aar = LEKENE_EDITIONS.get(row["forste_utgave"], 2012)

        utover_aktive = aktive_sesonger[aktive_sesonger["athlete_id"] == aid]
        utover_alle = per_utover_ar[per_utover_ar["athlete_id"] == aid]

        siste_aktive = int(utover_aktive["year"].max()) if len(utover_aktive) > 0 else stevne_aar
        siste_resultat = int(utover_alle["year"].max()) if len(utover_alle) > 0 else stevne_aar

        karriere_lengde = siste_aktive - stevne_aar
        alder_ved_slutt = siste_aktive - birth_year

        frafall[aid] = {
            "stevne_aar": stevne_aar,
            "siste_aktive_ar": siste_aktive,
            "siste_resultat_ar": siste_resultat,
            "karriere_ar": karriere_lengde,
            "alder_ved_slutt": alder_ved_slutt,
            "aktiv_17": int(siste_aktive >= birth_year + 17),
            "aktiv_18": int(siste_aktive >= birth_year + 18),
            "aktiv_20": int(siste_aktive >= birth_year + 20),
            "aktiv_senior": int(siste_aktive >= birth_year + 20),
            "aktiv_naa": int(siste_aktive >= 2024),
            "antall_aktive_sesonger": len(utover_aktive),
        }

    return pd.DataFrame.from_dict(frafall, orient="index").reset_index().rename(
        columns={"index": "athlete_id"}
    )


# =============================================================================
# 2. PRESTASJON (Tyrving + percentile)
# =============================================================================

def beregn_baseline_prestasjon(kohort, karriere, tyrving_table):
    """Baseline-prestasjon ved første lekene-deltakelse."""
    logger.info("Beregner baseline prestasjonsnivå...")

    baseline_results = []
    for _, row in kohort.iterrows():
        aid = row["athlete_id"]
        utgave = row["forste_utgave"]
        if utgave not in LEKENE_EDITIONS:
            continue
        stevne_aar = LEKENE_EDITIONS[utgave]
        pattern = STEVNE_NAME_PATTERNS[utgave]

        utover_res = karriere[
            (karriere["athlete_id"] == aid)
            & (karriere["year"] == stevne_aar)
            & (karriere["meet_name"].str.contains(pattern, case=False, na=False))
        ]
        for _, r in utover_res.iterrows():
            baseline_results.append({
                "athlete_id": aid,
                "event_code": r["event_code"],
                "event_category": r["event_category"],
                "result_type": r["result_type"],
                "performance_value": r["performance_value"],
                "gender": row["gender"],
                "birth_year": row["birth_year"],
                "stevne_aar": stevne_aar,
            })

    if not baseline_results:
        logger.warning("Ingen baseline-resultater funnet!")
        return pd.DataFrame()

    bl = pd.DataFrame(baseline_results)
    bl = _filtrer_ugyldige_tider(bl)

    def calc_tyrving(row):
        if pd.isna(row["performance_value"]) or pd.isna(row["gender"]):
            return None
        age = beregn_alder_kalender(row["birth_year"], row["stevne_aar"])
        pts = beregn_tyrving_poeng(
            int(row["performance_value"]), row["event_code"],
            row["result_type"], row["gender"], age, tyrving_table
        )
        if pts is not None:
            pts = max(0, min(pts, TYRVING_CAP))
        return pts

    bl["tyrving_poeng"] = bl.apply(calc_tyrving, axis=1)

    # Percentile innen kjønn + øvelse + stevne_aar
    bl["percentile"] = np.nan
    for (gender, ec, yr), idx in bl.groupby(["gender", "event_code", "stevne_aar"]).groups.items():
        sub = bl.loc[idx]
        n = len(sub)
        if n < 2:
            bl.loc[idx, "percentile"] = 50.0
            continue
        rt = sub["result_type"].iloc[0]
        ascending = rt == "time"
        ranks = sub["performance_value"].rank(method="min", ascending=ascending)
        bl.loc[idx, "percentile"] = (1 - (ranks - 1) / (n - 1)) * 100

    prest = (
        bl.groupby("athlete_id")
        .agg(
            tyrving_best=("tyrving_poeng", "max"),
            tyrving_mean=("tyrving_poeng", "mean"),
            baseline_pctile_best=("percentile", "max"),
            baseline_pctile_mean=("percentile", "mean"),
            baseline_n_ovelser=("event_code", "nunique"),
            baseline_n_kategorier=("event_category", "nunique"),
        )
        .reset_index()
    )

    prest["prestasjonskategori"] = pd.cut(
        prest["tyrving_best"],
        bins=[-np.inf, 600, 800, 1000, 1200, np.inf],
        labels=["Svak", "Under snitt", "Middels", "God", "Sterk"],
    )

    return prest


# =============================================================================
# 3. ALLSIDIGHET / SPESIALISERING
# =============================================================================

def beregn_allsidighet(kohort, karriere):
    """Allsidighet over de første aktive årene."""
    logger.info("Beregner allsidighet...")

    allsidighet = {}
    for _, row in kohort.iterrows():
        aid = row["athlete_id"]
        stevne_aar = LEKENE_EDITIONS.get(row["forste_utgave"], 2012)

        utover = karriere[karriere["athlete_id"] == aid]
        if len(utover) == 0:
            continue

        early = utover[utover["year"] <= stevne_aar + 2]
        early_cats = early["event_category"].value_counts()
        early_n_kat = len(early_cats) if len(early_cats) > 0 else 0

        if len(early_cats) > 0:
            shares = early_cats / early_cats.sum()
            hhi_early = (shares ** 2).sum()
        else:
            hhi_early = None

        all_cats = utover["event_category"].value_counts()
        if len(all_cats) > 0:
            shares_all = all_cats / all_cats.sum()
            hhi_karriere = (shares_all ** 2).sum()
            primaer_kat = all_cats.index[0]
        else:
            hhi_karriere = None
            primaer_kat = None

        baseline = utover[utover["year"] == stevne_aar]
        baseline_cats = baseline["event_category"].value_counts()
        primaer_baseline = baseline_cats.index[0] if len(baseline_cats) > 0 else None

        siste_aar = utover["year"].max()
        siste = utover[utover["year"] == siste_aar]
        siste_cats = siste["event_category"].value_counts()
        primaer_siste = siste_cats.index[0] if len(siste_cats) > 0 else None

        byttet_kat = int(primaer_baseline != primaer_siste) if primaer_baseline and primaer_siste else None

        allsidighet[aid] = {
            "early_n_kategorier": early_n_kat,
            "hhi_early": round(hhi_early, 3) if hhi_early else None,
            "hhi_karriere": round(hhi_karriere, 3) if hhi_karriere else None,
            "primaer_kategori_baseline": primaer_baseline,
            "primaer_kategori_siste": primaer_siste,
            "byttet_kategori": byttet_kat,
        }

    return pd.DataFrame.from_dict(allsidighet, orient="index").reset_index().rename(
        columns={"index": "athlete_id"}
    )


# =============================================================================
# 4. RAE
# =============================================================================

def beregn_rae(kohort):
    """Relative Age Effect-variabler."""
    logger.info("Beregner RAE...")
    kohort = kohort.copy()
    bd = pd.to_datetime(kohort["birth_date"], errors="coerce")

    kohort["fodt_maaned"] = bd.dt.month
    kohort["fodt_kvartal"] = pd.cut(
        bd.dt.month, bins=[0, 3, 6, 9, 12], labels=["Q1", "Q2", "Q3", "Q4"]
    )
    kohort["fodt_halvaar"] = pd.cut(
        bd.dt.month, bins=[0, 6, 12], labels=["H1", "H2"]
    )
    return kohort[["athlete_id", "fodt_maaned", "fodt_kvartal", "fodt_halvaar"]]


# =============================================================================
# 5. KONKURRANSEFREKVENS (basic + behavioral per alder)
# =============================================================================

def beregn_frekvens(kohort, karriere):
    """Konkurransefrekvens-variabler."""
    logger.info("Beregner konkurransefrekvens...")

    frekvens = {}
    for _, row in kohort.iterrows():
        aid = row["athlete_id"]
        stevne_aar = LEKENE_EDITIONS.get(row["forste_utgave"], 2012)

        utover = karriere[karriere["athlete_id"] == aid]
        if len(utover) == 0:
            continue

        baseline = utover[utover["year"] == stevne_aar]
        stevner_baseline = baseline["meet_id"].nunique()

        early = utover[utover["year"].isin([stevne_aar, stevne_aar + 1])]
        early_by_year = early.groupby("year").agg(
            n_stevner=("meet_id", "nunique"),
            n_resultater=("id", "count"),
        )
        stevner_per_ar_tidlig = early_by_year["n_stevner"].mean() if len(early_by_year) > 0 else 0
        resultater_per_ar_tidlig = early_by_year["n_resultater"].mean() if len(early_by_year) > 0 else 0

        if len(early_by_year) >= 2:
            s1 = early_by_year.iloc[0]["n_stevner"]
            s2 = early_by_year.iloc[1]["n_stevner"]
            frekvens_trend = s2 - s1
        else:
            frekvens_trend = None

        frekvens[aid] = {
            "stevner_baseline_ar": stevner_baseline,
            "stevner_per_ar_tidlig": round(stevner_per_ar_tidlig, 1),
            "resultater_per_ar_tidlig": round(resultater_per_ar_tidlig, 1),
            "frekvens_trend": frekvens_trend,
        }

    return pd.DataFrame.from_dict(frekvens, orient="index").reset_index().rename(
        columns={"index": "athlete_id"}
    )


# =============================================================================
# 6. BEHAVIORAL ENGAGEMENT (key new variables for PSE)
# =============================================================================

def beregn_behavioral_engagement(kohort, karriere):
    """
    Behavioral engagement-variabler per aldersår.

    Kjernen i PSE-historien:
    - vol_age_X: Antall stevner som X-åring (X = 13..18)
    - res_age_X: Antall resultater som X-åring
    - hhi_age_X: HHI per aldersår (spesialiseringsgrad)
    - nkat_age_X: Antall øvelseskategorier som X-åring
    - n_msk_typer: Antall typer mesterskap (UM/JrNM/NM/regional) før alder 17
    - helaars_X: Helårsdeltakelse (utendørs + innendørs) som X-åring
    """
    logger.info("Beregner behavioral engagement-variabler...")

    # Forhåndsberegn deltakelser per utøver per aldersår
    AGES = [13, 14, 15, 16, 17, 18]
    MILEPÆL_AGE = 15  # første kvalifikasjonsmilepæl (UM)

    # Mesterskap-deteksjon
    karriere["er_um"] = karriere["meet_name"].str.contains(
        "UM|U-mester|Ungdomsmesterskap", case=False, na=False, regex=True
    )
    karriere["er_jrm"] = karriere["meet_name"].str.contains(
        "JrNM|Jr NM|Junior NM|Juniormesterskap|Jr.NM", case=False, na=False, regex=True
    )
    karriere["er_nm"] = karriere["meet_name"].str.contains(
        r"\bNM\b|Norgesmesterskap", case=False, na=False, regex=True
    ) & ~karriere["er_jrm"] & ~karriere["er_um"]
    karriere["er_km"] = karriere["meet_name"].str.contains(
        "KM|Kretsmester|Distriktsmester", case=False, na=False, regex=True
    )

    beh = {}
    for _, row in kohort.iterrows():
        aid = row["athlete_id"]
        utover = karriere[karriere["athlete_id"] == aid]
        if len(utover) == 0:
            continue

        rec = {}

        # Volum og diversifisering per aldersår
        for age in AGES:
            ut_age = utover[utover["age"] == age]
            rec[f"vol_age_{age}"] = ut_age["meet_id"].nunique()
            rec[f"res_age_{age}"] = len(ut_age)

            cats = ut_age["event_category"].value_counts()
            rec[f"nkat_age_{age}"] = len(cats)
            if len(cats) > 0:
                shares = cats / cats.sum()
                rec[f"hhi_age_{age}"] = round((shares ** 2).sum(), 3)
            else:
                rec[f"hhi_age_{age}"] = None

            # Helårsdeltakelse: hadde både utendørs og innendørs?
            if len(ut_age) > 0:
                ute = (~ut_age["meet_indoor"]).any()
                inne = ut_age["meet_indoor"].any()
                rec[f"helaars_age_{age}"] = int(ute and inne)
            else:
                rec[f"helaars_age_{age}"] = 0

        # Sammensatte mål
        # Konkurransevolum i milepælperioden (15-16)
        rec["vol_milepael"] = rec.get("vol_age_15", 0) + rec.get("vol_age_16", 0)
        # Pre-milepæl volum (13-14)
        rec["vol_pre_milepael"] = rec.get("vol_age_13", 0) + rec.get("vol_age_14", 0)
        # Trajektori: endring fra pre til milepæl
        rec["vol_trend_milepael"] = rec["vol_milepael"] - rec["vol_pre_milepael"]

        # Helårs-sum (13-16)
        rec["helaars_sum_13_16"] = sum(
            rec.get(f"helaars_age_{a}", 0) for a in [13, 14, 15, 16]
        )

        # Mesterskaps-typer før alder 17
        pre_17 = utover[utover["age"] < 17]
        typer = 0
        if pre_17["er_um"].any():
            typer += 1
        if pre_17["er_jrm"].any():
            typer += 1
        if pre_17["er_nm"].any():
            typer += 1
        if pre_17["er_km"].any():
            typer += 1
        rec["n_msk_typer"] = typer

        # UM-deltakelse alder 15-16
        msk_15_16 = utover[utover["age"].isin([15, 16])]
        rec["um_15_16"] = int(msk_15_16["er_um"].any())
        rec["jrm_17_19"] = int(utover[utover["age"].isin([17, 18, 19])]["er_jrm"].any())

        # HHI-trajectory: endring fra age 13-14 til age 15-16
        hhi_pre = rec.get("hhi_age_13") or rec.get("hhi_age_14")
        hhi_post = rec.get("hhi_age_15") or rec.get("hhi_age_16")
        if hhi_pre is not None and hhi_post is not None:
            rec["hhi_change"] = round(hhi_post - hhi_pre, 3)
        else:
            rec["hhi_change"] = None

        beh[aid] = rec

    return pd.DataFrame.from_dict(beh, orient="index").reset_index().rename(
        columns={"index": "athlete_id"}
    )


# =============================================================================
# 7. PERFORMANCE TRAJECTORY (Tyrving over alder)
# =============================================================================

def beregn_performance_trajectory(kohort, karriere, tyrving_table):
    """
    Performance-trajektori variabler:
    - tyrving_peak_pre15: Beste Tyrving før alder 15
    - tyrving_age_X: Beste Tyrving som X-åring (13..16)
    - tyrving_slope_13_16: Lineær trend over alder 13-16
    """
    logger.info("Beregner performance-trajectory...")

    # Beregn Tyrving for alle resultater (eller subset av relevante år)
    rel = karriere[karriere["age"].isin([13, 14, 15, 16, 17, 18])].copy()
    rel = _filtrer_ugyldige_tider(rel)

    # Map kjønn fra kohort
    gender_lookup = kohort.set_index("athlete_id")["gender"].to_dict()
    rel["gender"] = rel["athlete_id"].map(gender_lookup)

    def calc_tyrving(row):
        if pd.isna(row["performance_value"]) or pd.isna(row["gender"]) or pd.isna(row["age"]):
            return None
        pts = beregn_tyrving_poeng(
            int(row["performance_value"]), row["event_code"],
            row["result_type"], row["gender"], int(row["age"]), tyrving_table
        )
        if pts is not None:
            pts = max(0, min(pts, TYRVING_CAP))
        return pts

    logger.info(f"  Beregner Tyrving for {len(rel)} resultater (alder 13-18)...")
    rel["tyrving"] = rel.apply(calc_tyrving, axis=1)

    traj = {}
    for aid, group in rel.groupby("athlete_id"):
        rec = {}
        # Peak Tyrving pre-15
        pre15 = group[group["age"] < 15]
        if len(pre15) > 0 and pre15["tyrving"].notna().any():
            rec["tyrving_peak_pre15"] = pre15["tyrving"].max()
        else:
            rec["tyrving_peak_pre15"] = None

        # Per aldersår
        for age in [13, 14, 15, 16]:
            ut = group[group["age"] == age]
            if len(ut) > 0 and ut["tyrving"].notna().any():
                rec[f"tyrving_age_{age}"] = ut["tyrving"].max()
            else:
                rec[f"tyrving_age_{age}"] = None

        # Slope 13-16
        ages = [13, 14, 15, 16]
        peaks = [rec.get(f"tyrving_age_{a}") for a in ages]
        valid_pairs = [(a, p) for a, p in zip(ages, peaks) if p is not None]
        if len(valid_pairs) >= 2:
            xs = np.array([p[0] for p in valid_pairs])
            ys = np.array([p[1] for p in valid_pairs])
            slope = np.polyfit(xs, ys, 1)[0]
            rec["tyrving_slope_13_16"] = round(slope, 1)
        else:
            rec["tyrving_slope_13_16"] = None

        traj[aid] = rec

    return pd.DataFrame.from_dict(traj, orient="index").reset_index().rename(
        columns={"index": "athlete_id"}
    )


# =============================================================================
# 8. KLUBBSTØRRELSE
# =============================================================================

def beregn_klubb_storrelse(kohort, karriere):
    """Klubbstørrelse i stevneåret."""
    logger.info("Beregner klubbstørrelse...")

    storrelse = {}
    for _, row in kohort.iterrows():
        aid = row["athlete_id"]
        stevne_aar = LEKENE_EDITIONS.get(row["forste_utgave"], 2012)
        klubb = row.get("klubb")
        if pd.isna(klubb) or not klubb:
            storrelse[aid] = None
            continue

        klubb_utovere = karriere[
            (karriere["club_name"] == klubb) & (karriere["year"] == stevne_aar)
        ]["athlete_id"].nunique()
        storrelse[aid] = klubb_utovere

    return pd.Series(storrelse, name="klubb_storrelse").reset_index().rename(
        columns={"index": "athlete_id"}
    )


# =============================================================================
# MAIN
# =============================================================================

def main():
    kohort, karriere = last_data()
    logger.info(f"Lastet kohort: {len(kohort)} utøvere, karriere: {len(karriere)} resultater")

    tyrving_table = parse_tyrving_xls()

    frafall = beregn_frafall(kohort, karriere)
    prestasjon = beregn_baseline_prestasjon(kohort, karriere, tyrving_table)
    allsidighet = beregn_allsidighet(kohort, karriere)
    rae = beregn_rae(kohort)
    frekvens = beregn_frekvens(kohort, karriere)
    klubb = beregn_klubb_storrelse(kohort, karriere)
    behavioral = beregn_behavioral_engagement(kohort, karriere)
    trajectory = beregn_performance_trajectory(kohort, karriere, tyrving_table)

    # Slå sammen
    kohort_cols = [c for c in ["athlete_id", "gender", "birth_date", "birth_year",
                               "forste_utgave", "region", "deltok_begge_aar", "klubb"]
                   if c in kohort.columns]
    analyse = kohort[kohort_cols].copy()

    for df in [frafall, prestasjon, allsidighet, rae, frekvens, klubb, behavioral, trajectory]:
        if len(df) > 0:
            analyse = analyse.merge(df, on="athlete_id", how="left")

    analyse.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    logger.info(f"Lagret {len(analyse)} rader, {len(analyse.columns)} kolonner -> {OUTPUT_FILE}")

    # Oppsummering
    logger.info("\n=== OPPSUMMERING ===")
    logger.info(f"Totalt: {len(analyse)} utøvere")
    for by in sorted(analyse["birth_year"].dropna().unique()):
        sub = analyse[analyse["birth_year"] == by]
        n_m = (sub["gender"] == "M").sum()
        n_f = (sub["gender"] == "F").sum()
        logger.info(f"  f. {int(by)} (n={len(sub)}): M={n_m}, F={n_f}, "
                    f"aktiv_senior={sub['aktiv_senior'].sum()} "
                    f"({sub['aktiv_senior'].mean()*100:.1f}%)")


if __name__ == "__main__":
    main()
