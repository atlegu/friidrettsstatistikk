"""
05_nasjonal_kontroll.py - Nasjonal kontroll av trendene på lekene.

Sesongbeste for ALLE norske 13- og 14-åringer (ikke bare lekene) i kast, lengde og høyde,
per år, kjønn og klasse, hentet fra Supabase. Brukes til å sjekke om trendene på lekene
skyldes hvem som kommer til stevnet. Samme logikk som nasjonal_kontroll.sql, men sonehopp
(«Lengde (Sone 0,5m)») føres som lengde, slik 01_uttrekk.py gjør; sesongbeste per utøver
gjør at samme hopp under to koder teller én gang.

Trend: OLS av log(median) og log(90. persentil) på kalenderår; stigning x 1000 = prosent
per tiår. Sammenlignes med lekene-trendene i tables/trender_per_serie.csv.

Ut: tables/nasjonal_13_14_per_aar.csv, tables/nasjonal_kontroll.csv
Kjør: ../../scraper/venv/bin/python 05_nasjonal_kontroll.py
"""

import logging
import os
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from scipy import stats
from supabase import create_client

from felles import START_AAR

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
TAB = HERE / "tables"
(HERE / "logs").mkdir(exist_ok=True)
logger.addHandler(logging.FileHandler(HERE / "logs" / f"nasjonal_{datetime.now():%Y%m%d_%H%M%S}.log"))

load_dotenv(ROOT / "scraper" / ".env")
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

KODER = ["spyd_400g", "spyd_600g", "kule_2kg", "kule_3kg", "kule_4kg",
         "diskos_600g", "diskos_750g", "diskos_1kg", "lengde", "lengde_sone_05m", "hoyde"]
SONE = {"lengde_sone_05m": "lengde"}
MIN_N = 10   # minste snitt-antall utøvere per år for at en serie tas med i sammenligningen


def _alle(q):
    """Alle rader fra en spørring (paginert, ordnet på id)."""
    ut, page, size = [], 0, 1000
    while True:
        res = q.order("id").range(page * size, (page + 1) * size - 1).execute()
        ut.extend(res.data)
        if len(res.data) < size:
            return ut
        page += 1


def hent() -> pd.DataFrame:
    """Alle resultater av 13- og 14-åringer i øvelsene.

    Går via utøverne (fødselsår), i bolker: en direkte spørring på øvelse og dato får
    databasen til å velge en indeks som gir tidsavbrudd.
    """
    ev = pd.DataFrame(sb.table("events").select("id,code").in_("code", KODER).execute().data)
    kode = dict(zip(ev["id"], ev["code"]))
    siste = int(pd.read_csv(HERE / "data" / "lekene.csv", usecols=["yr"])["yr"].max())
    aar = list(range(START_AAR - 14, siste - 13 + 1))
    utovere = pd.DataFrame(_alle(sb.table("athletes").select("id,birth_year,gender")
                                 .in_("birth_year", aar).in_("gender", ["M", "F"])))
    logger.info(f"Utøvere født {aar[0]}-{aar[-1]}: {len(utovere)}")
    fodt, kjonn = dict(zip(utovere["id"], utovere["birth_year"])), dict(zip(utovere["id"], utovere["gender"]))
    ids, ut = utovere["id"].tolist(), []
    for i in range(0, len(ids), 150):
        rader = _alle(sb.table("results").select("id,athlete_id,event_id,date,performance_value")
                      .in_("athlete_id", ids[i:i + 150]).in_("event_id", list(kode)))
        for r in rader:
            yr = int(r["date"][:4])
            klasse = yr - fodt[r["athlete_id"]]
            if klasse in (13, 14) and START_AAR <= yr <= siste and (r["performance_value"] or 0) > 0:
                ut.append((r["athlete_id"], kode[r["event_id"]], yr, klasse, kjonn[r["athlete_id"]],
                           r["performance_value"]))
        if (i // 150) % 40 == 0:
            logger.info(f"  {i}/{len(ids)} utøvere, {len(ut)} resultater")
    d = pd.DataFrame(ut, columns=["athlete_id", "code", "yr", "klasse", "gender", "pv"])
    d["code"] = d["code"].replace(SONE)
    return d


def per_aar(d: pd.DataFrame) -> pd.DataFrame:
    best = d.groupby(["athlete_id", "code", "yr", "klasse", "gender"], as_index=False)["pv"].max()
    t = (best.groupby(["code", "gender", "klasse", "yr"])["pv"]
         .agg(n="size", med="median", p90=lambda s: s.quantile(0.9)).round(1).reset_index())
    t["gruppe"] = np.where(t["gender"] == "M", "G", "J") + t["klasse"].astype(str)
    return t.sort_values(["code", "gender", "klasse", "yr"])


def kontroll(t: pd.DataFrame) -> pd.DataFrame:
    lek = pd.read_csv(TAB / "trender_per_serie.csv").set_index(["kode", "gruppe"])
    rader = []
    for (code, gruppe), g in t.groupby(["code", "gruppe"]):
        if len(g) < 5:
            continue
        m, p = stats.linregress(g["yr"], np.log(g["med"])), stats.linregress(g["yr"], np.log(g["p90"]))
        l = lek.loc[(code, gruppe)] if (code, gruppe) in lek.index else None
        rader.append({"kode": code, "gruppe": gruppe, "n_snitt": int(round(g["n"].mean())), "aar": len(g),
                      "nasjonal_median": 1000 * m.slope, "p_nm": m.pvalue,
                      "nasjonal_p90": 1000 * p.slope, "p_nt": p.pvalue,
                      "lekene_median": l["median_pct_tiaar"] if l is not None else np.nan,
                      "lekene_topp": l["topp_pct_tiaar"] if l is not None else np.nan})
    return pd.DataFrame(rader)


def main():
    d = hent()
    logger.info(f"Resultater: {len(d)}, utøvere: {d['athlete_id'].nunique()}")
    t = per_aar(d)
    t.to_csv(TAB / "nasjonal_13_14_per_aar.csv", index=False)
    k = kontroll(t)
    k.to_csv(TAB / "nasjonal_kontroll.csv", index=False)
    vis = k[k["n_snitt"] >= MIN_N].round(2)
    logger.info("Serier med minst %d utøvere per år:\n%s", MIN_N, vis.to_string(index=False))


if __name__ == "__main__":
    main()
