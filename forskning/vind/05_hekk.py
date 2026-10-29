"""
05_hekk.py — A6-tillegg: vindeffekten i korthekk, per øvelseskode.

Kodene bærer klassespesifikasjonen (distanse + hekkehøyde), så estimatene
er per aldersklasse-spesifikasjon. Gjenbruker estimer() fra 03 (samme
within utøver x sesong-design). Flat sprint på samme distanse og modalt
aldersbånd hentes fra tables/estimering/alder.csv som referanse.

Output: tables/estimering/hekk.csv, figures/fig5_hurdles.png
"""

import importlib.util
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

spec = importlib.util.spec_from_file_location("est03", HERE / "03_estimering.py")
est03 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(est03)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

GRENSER = {"60mh": (7.5, 20), "80mh": (10, 26), "100mh": (12, 32), "110mh": (13, 34)}
BAND = est03.__dict__.get("BAND") or None  # ikke definert i 03; bruk lokal
BANDDEF = [(10, 11, "10-11"), (12, 13, "12-13"), (14, 15, "14-15"),
           (16, 17, "16-17"), (18, 19, "18-19"), (20, 34, "20-34")]
FLAT = {"60mh": "60m", "80mh": None, "100mh": "100m", "110mh": "100m"}
NAVN = {"60mh_68cm": "60 m hekk 68 cm", "60mh_76_2cm": "60 m hekk 76,2 cm",
        "80mh_76_2cm": "80 m hekk 76,2 cm", "80mh_84cm": "80 m hekk 84 cm",
        "100mh_76_2cm": "100 m hekk 76,2 cm", "100mh_84cm": "100 m hekk 84 cm",
        "100mh_91_4cm": "100 m hekk 91,4 cm", "110mh_91_4cm": "110 m hekk 91,4 cm",
        "110mh_100cm": "110 m hekk 100 cm", "110mh_106_7cm": "110 m hekk 106,7 cm"}


def aldersband(a):
    for lo, hi, navn in BANDDEF:
        if lo <= a <= hi:
            return navn
    return None


def main():
    r = pd.read_csv(DATA / "resultater_hekk.csv", parse_dates=["date"], low_memory=False)
    utv = pd.read_csv(DATA / "utovere.csv").rename(columns={"id": "athlete_id"})
    me = pd.read_csv(DATA / "meets.csv").rename(columns={"id": "meet_id"})
    r = r.merge(utv, on="athlete_id", how="left")
    r = r.merge(me[["meet_id", "indoor"]], on="meet_id", how="left")
    r["aar"] = r["date"].dt.year
    r["maaned"] = r["date"].dt.month

    n0 = len(r)
    r = r[(r["status"] == "OK") & (r["indoor"].astype(str) != "True")
          & (r["is_manual_time"].astype(str) != "True")
          & r["gender"].isin(["M", "F"]) & r["birth_year"].notna()]
    r["alder"] = (r["aar"] - r["birth_year"]).astype(int)
    r = r[r["alder"].between(10, 34) & r["wind"].notna() & (r["wind"].abs() <= 8)]
    r["y"] = r["performance_value"] / 100
    dist = r["event_code"].str.split("_").str[0]
    lo = dist.map(lambda d: GRENSER[d][0])
    hi = dist.map(lambda d: GRENSER[d][1])
    r = r[r["y"].between(lo, hi)].copy()
    logger.info(f"analyseklare hekkerader: {len(r)} (av {n0} i uttrekket)")

    r["logy"] = np.log(r["y"])
    r["aldersband"] = r["alder"].map(aldersband)
    r["celle"] = (r["athlete_id"].astype(str) + "_" + r["aar"].astype(str)
                  + "_" + r["event_code"])
    r["n_i_celle"] = r.groupby("celle")["id"].transform("count")
    r["runde"] = r["round"].fillna("ukjent").astype(str)

    flat = pd.read_csv(EST / "alder.csv")
    rader = []
    for kode, g in r.groupby("event_code"):
        modal_band = g["aldersband"].mode().iloc[0]
        andel_f = float((g["gender"] == "F").mean())
        for kj in ["begge", "M", "F"]:
            gg = g if kj == "begge" else g[g["gender"] == kj]
            res = est03.estimer(gg, "y")
            if not res:
                continue
            b, se = res["wind"]
            resl = est03.estimer(gg, "logy")
            pct = round(-100 * resl["wind"][0], 3) if resl else np.nan
            ref = np.nan
            fk = FLAT[kode.split("_")[0]]
            if fk is not None and kj in ("M", "F"):
                m = flat[(flat["event"] == fk) & (flat["kjonn"] == kj)
                         & (flat["aldersband"] == modal_band) & (flat["enhet"] == "s")]
                if len(m):
                    ref = float(m["gevinst_per_ms"].iloc[0])
            rader.append({"kode": kode, "navn": NAVN[kode], "kjonn": kj,
                          "modal_aldersband": modal_band, "andel_jenter": round(andel_f, 2),
                          "gevinst_s_per_ms": round(-b, 4),
                          "ki_lav": round(-b - 1.96 * se, 4),
                          "ki_hoy": round(-b + 1.96 * se, 4),
                          "gevinst_pst_per_ms": pct,
                          "flat_sprint_ref_s": ref if not np.isnan(ref) else "",
                          "flat_ref_ovelse": fk if fk else "",
                          "n": res["n"], "celler": res["celler"]})
    ut = pd.DataFrame(rader)
    ut.to_csv(EST / "hekk.csv", index=False)
    logger.info(f"estimert {ut['kode'].nunique()} koder; tabell i {EST}/hekk.csv")

    # ---- Figur: punktplott per kode (pooled), flat sprint som referansediamant --------
    p = ut[ut["kjonn"] == "begge"].copy()
    rekkef = [k for k in NAVN if k in set(p["kode"])]
    p = p.set_index("kode").loc[rekkef].reset_index()
    yposs = np.arange(len(p))[::-1]
    fig, ax = plt.subplots(figsize=(9.0, 6.0))
    ax.errorbar(p["gevinst_s_per_ms"], yposs,
                xerr=[p["gevinst_s_per_ms"] - p["ki_lav"],
                      p["ki_hoy"] - p["gevinst_s_per_ms"]],
                fmt="o", color="#1f4e79", ms=7, capsize=3, lw=1.8,
                label="Short hurdles (within athlete × season)")
    # referanser fra kjønnsspesifikke rader
    refs = ut[(ut["kjonn"] != "begge") & (ut["flat_sprint_ref_s"] != "")]
    for _, t in refs.iterrows():
        if t["kode"] in rekkef:
            yp = yposs[rekkef.index(t["kode"])]
            ax.plot(float(t["flat_sprint_ref_s"]), yp, marker="D", ms=6,
                    color="#1b6e1b" if t["kjonn"] == "M" else "#b22222",
                    linestyle="none", alpha=0.85)
    ax.plot([], [], marker="D", color="#1b6e1b", linestyle="none",
            label="Flat sprint reference, boys/men (same distance class, modal age band)")
    ax.plot([], [], marker="D", color="#b22222", linestyle="none",
            label="Flat sprint reference, girls/women")
    etiketter = [f"{NAVN[k]}  ({p.set_index('kode').loc[k,'modal_aldersband']})"
                 for k in rekkef]
    ax.set_yticks(yposs, etiketter, fontsize=9)
    ax.axvline(0, color="#666666", lw=1, ls="--")
    ax.set_xlabel("Seconds faster per +1 m/s tailwind")
    ax.set_title("Wind effect in short hurdles, by class-specific event code")
    ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG / "fig5_hurdles.png", bbox_inches="tight")
    plt.close(fig)
    logger.info("figur: figures/fig5_hurdles.png")


if __name__ == "__main__":
    main()
