"""
Steg 2: Bygg analysedatasett fra kohort + karrieredata.

Leser:  kohort.csv, karrieredata.csv, Tyrvingtabellen
Skriver: analysedata.csv (én rad per utøver med alle variabler)

Bruk: python 02_bygg_analysedata.py
"""

import logging
from pathlib import Path

import pandas as pd
import numpy as np

from tyrvingtabellen import parse_tyrving_xls, beregn_tyrving_poeng

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent
KOHORT_FILE = DATA_DIR / "kohort.csv"
KARRIERE_FILE = DATA_DIR / "karrieredata.csv"
OUTPUT_FILE = DATA_DIR / "analysedata.csv"

REGION_MAP = {
    "Romerike Friidrettstadion": "Østlandet",
    "Jessheim Friidrettsstadion": "Østlandet",
    "Jessheim": "Østlandet",
    "Øverlands Minde": "Midt-Norge",
    "Osterøy Stadion": "Vestlandet",
    "Osterøy": "Vestlandet",
}

NCC_PEAB_EDITIONS = {
    "ncc_2011": 2011,
    "ncc_2012": 2012,
    "peab_2013": 2013,
    "peab_2014": 2014,
}

STEVNE_NAME_PATTERNS = {
    "ncc_2011": "NCC",
    "ncc_2012": "NCC",
    "peab_2013": "PEAB",
    "peab_2014": "eab",
}


def last_data():
    kohort = pd.read_csv(KOHORT_FILE)
    karriere = pd.read_csv(KARRIERE_FILE)
    karriere["date"] = pd.to_datetime(karriere["date"])
    karriere["year"] = karriere["date"].dt.year
    return kohort, karriere


def beregn_alder_kalender(birth_year, competition_year):
    """Norsk friidrett: alder = konkurranseår − fødselsår."""
    if pd.isna(birth_year):
        return None
    return int(competition_year) - int(birth_year)


# === FRAFALL ===

def beregn_frafall(kohort, karriere):
    """Beregn frafallsvariabler per utøver."""
    logger.info("Beregner frafall...")

    # Resultater per utøver per år
    per_utover_ar = (
        karriere.groupby(["athlete_id", "year"])
        .agg(
            antall_resultater=("id", "count"),
            antall_stevner=("meet_id", "nunique"),
        )
        .reset_index()
    )

    # Aktiv sesong: ≥2 resultater i året
    aktive_sesonger = per_utover_ar[per_utover_ar["antall_resultater"] >= 2]

    frafall = {}
    for aid in kohort["athlete_id"]:
        utover_aktive = aktive_sesonger[aktive_sesonger["athlete_id"] == aid]
        utover_alle = per_utover_ar[per_utover_ar["athlete_id"] == aid]
        birth_year = kohort.loc[kohort["athlete_id"] == aid, "birth_year"].iloc[0]
        stevne_aar = NCC_PEAB_EDITIONS.get(
            kohort.loc[kohort["athlete_id"] == aid, "forste_utgave"].iloc[0], 2012
        )

        if len(utover_aktive) > 0:
            siste_aktive = int(utover_aktive["year"].max())
        else:
            siste_aktive = stevne_aar

        if len(utover_alle) > 0:
            siste_resultat = int(utover_alle["year"].max())
        else:
            siste_resultat = stevne_aar

        karriere_lengde = siste_aktive - stevne_aar
        alder_ved_slutt = siste_aktive - birth_year

        aktiv_17 = int(siste_aktive >= birth_year + 17)
        aktiv_senior = int(siste_aktive >= birth_year + 20)
        aktiv_naa = int(siste_aktive >= 2024)

        frafall[aid] = {
            "siste_aktive_ar": siste_aktive,
            "siste_resultat_ar": siste_resultat,
            "karriere_ar": karriere_lengde,
            "alder_ved_slutt": alder_ved_slutt,
            "aktiv_17": aktiv_17,
            "aktiv_senior": aktiv_senior,
            "aktiv_naa": aktiv_naa,
            "antall_aktive_sesonger": len(utover_aktive),
        }

    return pd.DataFrame.from_dict(frafall, orient="index").reset_index().rename(
        columns={"index": "athlete_id"}
    )


# === DATAKVALITET ===

# Minimumstider i centisekunder — alt under er åpenbart feilregistrert
MIN_PERFORMANCE_CS = {
    "60m": 600, "80m": 800, "100m": 1000, "200m": 2000,
    "300m": 3500, "400m": 4500, "600m": 8000, "800m": 11000,
    "1000m": 15000, "1500m": 23000, "2000m": 32000, "3000m": 50000,
    "60mh": 700, "80mh": 1000, "200mh": 2500, "300mh": 4000,
    "1500msc": 25000, "2000msc": 35000,
}


def _filtrer_ugyldige_tider(bl):
    """Fjern resultater med åpenbart feilregistrerte tider."""
    mask = pd.Series(True, index=bl.index)
    for ec, min_cs in MIN_PERFORMANCE_CS.items():
        feil = (bl["event_code"] == ec) & (bl["performance_value"] < min_cs)
        n_feil = feil.sum()
        if n_feil > 0:
            logger.warning(f"  Fjerner {n_feil} ugyldige {ec}-tider (under {min_cs/100:.0f}s)")
            mask &= ~feil
    n_fjernet = (~mask).sum()
    if n_fjernet:
        logger.info(f"  Totalt fjernet {n_fjernet} ugyldige resultater")
    return bl[mask].copy()


# === PRESTASJONSNIVÅ ===

def beregn_baseline_prestasjon(kohort, karriere, tyrving_table):
    """Beregn baseline prestasjonsnivå (Tyrving + percentile) ved NCC/PEAB."""
    logger.info("Beregner baseline prestasjonsnivå...")

    # Identifiser NCC/PEAB-resultater
    baseline_results = []
    for _, row in kohort.iterrows():
        aid = row["athlete_id"]
        utgave = row["forste_utgave"]
        stevne_aar = NCC_PEAB_EDITIONS[utgave]
        pattern = STEVNE_NAME_PATTERNS[utgave]

        utover_res = karriere[
            (karriere["athlete_id"] == aid) &
            (karriere["year"] == stevne_aar) &
            (karriere["meet_name"].str.contains(pattern, case=False, na=False))
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

    # --- Tyrving-poeng ---
    def calc_tyrving(row):
        if pd.isna(row["performance_value"]) or pd.isna(row["gender"]):
            return None
        age = beregn_alder_kalender(row["birth_year"], row["stevne_aar"])
        pts = beregn_tyrving_poeng(
            int(row["performance_value"]), row["event_code"],
            row["result_type"], row["gender"], age, tyrving_table
        )
        if pts is not None:
            pts = max(0, pts)
        return pts

    bl["tyrving_poeng"] = bl.apply(calc_tyrving, axis=1)

    # --- Prosentil innen kjønn + øvelse + stevne_aar ---
    bl["percentile"] = np.nan
    for (gender, ec, yr), idx in bl.groupby(["gender", "event_code", "stevne_aar"]).groups.items():
        sub = bl.loc[idx]
        n = len(sub)
        if n < 2:
            bl.loc[idx, "percentile"] = 50.0
            continue
        rt = sub["result_type"].iloc[0]
        ascending = True if rt == "time" else False
        ranks = sub["performance_value"].rank(method="min", ascending=not ascending)
        bl.loc[idx, "percentile"] = (1 - (ranks - 1) / (n - 1)) * 100

    # Aggreger per utøver
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

    # Prestasjonskategori
    prest["prestasjonskategori"] = pd.cut(
        prest["tyrving_best"],
        bins=[-np.inf, 600, 800, 1000, 1200, np.inf],
        labels=["Svak", "Under snitt", "Middels", "God", "Sterk"],
    )

    return prest


# === ALLSIDIGHET ===

def beregn_allsidighet(kohort, karriere):
    """Beregn allsidighetsvariabler over de første 3 aktive årene."""
    logger.info("Beregner allsidighet...")

    allsidighet = {}
    for aid in kohort["athlete_id"]:
        utover = karriere[karriere["athlete_id"] == aid].copy()
        if len(utover) == 0:
            continue

        stevne_aar = NCC_PEAB_EDITIONS.get(
            kohort.loc[kohort["athlete_id"] == aid, "forste_utgave"].iloc[0], 2012
        )

        # Tidlige år (stevneår + 2 år etter)
        early = utover[utover["year"] <= stevne_aar + 2]
        early_cats = early["event_category"].value_counts()
        early_n_kat = early_cats.nunique() if len(early_cats) > 0 else 0

        # HHI for tidlig karriere
        if len(early_cats) > 0:
            shares = early_cats / early_cats.sum()
            hhi_early = (shares ** 2).sum()
        else:
            hhi_early = None

        # Over hele karrieren
        all_cats = utover["event_category"].value_counts()
        if len(all_cats) > 0:
            shares_all = all_cats / all_cats.sum()
            hhi_karriere = (shares_all ** 2).sum()
            primaer_kat = all_cats.index[0]
        else:
            hhi_karriere = None
            primaer_kat = None

        # Primærkategori ved baseline
        baseline_aar = stevne_aar
        baseline = utover[utover["year"] == baseline_aar]
        baseline_cats = baseline["event_category"].value_counts()
        primaer_baseline = baseline_cats.index[0] if len(baseline_cats) > 0 else None

        # Primærkategori siste aktive år
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


# === RAE ===

def beregn_rae(kohort):
    """Beregn Relative Age Effect-variabler."""
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


# === KONKURRANSEFREKVENS ===

def beregn_frekvens(kohort, karriere):
    """Beregn konkurransefrekvens-variabler."""
    logger.info("Beregner konkurransefrekvens...")

    frekvens = {}
    for aid in kohort["athlete_id"]:
        utover = karriere[karriere["athlete_id"] == aid]
        if len(utover) == 0:
            continue

        stevne_aar = NCC_PEAB_EDITIONS.get(
            kohort.loc[kohort["athlete_id"] == aid, "forste_utgave"].iloc[0], 2012
        )

        # Stevner i baseline-året
        baseline = utover[utover["year"] == stevne_aar]
        stevner_baseline = baseline["meet_id"].nunique()

        # Tidlige sesonger (stevneår og året etter)
        early = utover[utover["year"].isin([stevne_aar, stevne_aar + 1])]
        early_by_year = early.groupby("year").agg(
            n_stevner=("meet_id", "nunique"),
            n_resultater=("id", "count"),
        )
        stevner_per_ar_tidlig = early_by_year["n_stevner"].mean() if len(early_by_year) > 0 else 0
        resultater_per_ar_tidlig = early_by_year["n_resultater"].mean() if len(early_by_year) > 0 else 0

        # Trend: endring fra sesong 1 til 2
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


# === KLUBBSTØRRELSE ===

def beregn_klubb_storrelse(kohort, karriere):
    """Beregn klubbstørrelse i stevneåret."""
    logger.info("Beregner klubbstørrelse...")

    storrelse = {}
    for aid in kohort["athlete_id"]:
        stevne_aar = NCC_PEAB_EDITIONS.get(
            kohort.loc[kohort["athlete_id"] == aid, "forste_utgave"].iloc[0], 2012
        )
        klubb = kohort.loc[kohort["athlete_id"] == aid, "klubb"].iloc[0]
        if pd.isna(klubb) or not klubb:
            storrelse[aid] = None
            continue

        # Antall utøvere i samme klubb dette året
        klubb_utovere = karriere[
            (karriere["club_name"] == klubb) &
            (karriere["year"] == stevne_aar)
        ]["athlete_id"].nunique()

        storrelse[aid] = klubb_utovere

    return pd.Series(storrelse, name="klubb_storrelse").reset_index().rename(
        columns={"index": "athlete_id"}
    )


# === ØVELSESFRAFALL ===

def beregn_ovelsesfrafall(kohort, karriere):
    """Siste aktive år per øvelseskategori."""
    logger.info("Beregner øvelsesfrafall...")

    kategorier = ["sprint", "middle_distance", "hurdles", "jumps", "throws"]
    results = {}

    for aid in kohort["athlete_id"]:
        utover = karriere[karriere["athlete_id"] == aid]
        row = {}
        for kat in kategorier:
            kat_res = utover[utover["event_category"] == kat]
            if len(kat_res) > 0:
                row[f"siste_{kat}_ar"] = int(kat_res["year"].max())
            else:
                row[f"siste_{kat}_ar"] = None
        results[aid] = row

    return pd.DataFrame.from_dict(results, orient="index").reset_index().rename(
        columns={"index": "athlete_id"}
    )


# === HOVEDFUNKSJON ===

def main():
    kohort, karriere = last_data()
    logger.info(f"Lastet kohort: {len(kohort)} utøvere, karriere: {len(karriere)} resultater")

    tyrving_table = parse_tyrving_xls()

    # Beregn alle variabelgrupper
    frafall = beregn_frafall(kohort, karriere)
    prestasjon = beregn_baseline_prestasjon(kohort, karriere, tyrving_table)
    allsidighet = beregn_allsidighet(kohort, karriere)
    rae = beregn_rae(kohort)
    frekvens = beregn_frekvens(kohort, karriere)
    klubb = beregn_klubb_storrelse(kohort, karriere)
    ovelsesfrafall = beregn_ovelsesfrafall(kohort, karriere)

    # Slå sammen alt
    analyse = kohort[["athlete_id", "gender", "birth_date", "birth_year",
                       "forste_utgave", "region", "deltok_begge_aar", "klubb"]].copy()

    for df in [frafall, prestasjon, allsidighet, rae, frekvens, klubb, ovelsesfrafall]:
        if len(df) > 0:
            analyse = analyse.merge(df, on="athlete_id", how="left")

    # Lagre
    analyse.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    logger.info(f"Lagret analysedata til {OUTPUT_FILE}: {len(analyse)} rader, {len(analyse.columns)} kolonner")

    # Oppsummering
    logger.info("\n=== OPPSUMMERING ===")
    logger.info(f"Totalt: {len(analyse)} utøvere")
    for by in (1998, 1999, 2000):
        sub = analyse[analyse["birth_year"] == by]
        logger.info(f"\nf. {by} (n={len(sub)}):")
        logger.info(f"  Kjønn: {sub['gender'].value_counts().to_dict()}")
        if "karriere_ar" in sub.columns:
            logger.info(f"  Karrierelengde: median={sub['karriere_ar'].median():.0f}, snitt={sub['karriere_ar'].mean():.1f}")
        if "aktiv_senior" in sub.columns:
            logger.info(f"  Aktiv som senior: {sub['aktiv_senior'].sum()} ({sub['aktiv_senior'].mean()*100:.1f}%)")
        if "tyrving_best" in sub.columns:
            logger.info(f"  Tyrving best: median={sub['tyrving_best'].median():.0f}, snitt={sub['tyrving_best'].mean():.0f}")


if __name__ == "__main__":
    main()
