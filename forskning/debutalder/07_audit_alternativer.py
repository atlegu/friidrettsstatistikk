"""
07_audit_alternativer.py — A3: alternativene statistikk- og datagjennomgangen (audit 30.10.2026)
ba om, som grunnlag for Atles beslutning om påstandene.

  A3-1  direkte andel fortsatt aktiv (resultat ved alder >= t) per debutgruppe og debutalder,
        kull 2001–2004 (fullt observert til 21), mot KM med forsinket inngang.
  A3-2  utfall ved lik karrierelengde: >= 2 konkurransedager i et år minst D år etter debut
        (D = 4, 5, 6; bare utøvere der debutalder + D er observert ut 2025).
  2011  H1 uten 2001-kullet (debut ved 10 i 2011, året med tynnest dekning).
  A3-5  seleksjon i fødselskvartal-utvalget (andel med fødselsdato etter utfall og debutalder).

Output: tables/audit/*.csv
"""

import importlib.util
import logging
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
DATA = HERE / "data_private"
MOD = HERE / "tables" / "modeller"
UT = HERE / "tables" / "audit"
UT.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("m03", HERE / "03_modeller.py")
m03 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m03)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
SISTE_HELE_SESONG = 2025


def last():
    d = pd.read_csv(DATA / "analysedata.csv")
    d["region"] = d["region"].fillna("ukjent")
    d["log_klubbstorrelse"] = d["log_klubbstorrelse"].fillna(d["log_klubbstorrelse"].median())
    d["debut_kat"] = pd.Categorical(d["debut_alder"].clip(upper=17), categories=range(10, 18))
    return d, d[d["kohort_primar"] & d["debut_10_16"]].copy()


def direkte_andeler(p):
    s = p[p["birth_year"].between(2001, 2004)].copy()
    s["gruppe"] = pd.cut(s["debut_alder"], [9, 11, 13, 16], labels=["10-11", "12-13", "14-16"])
    km = pd.read_csv(MOD / "r1_km_alder.csv")
    rader = []
    for t in range(14, 22):
        for g, x in s.groupby("gruppe", observed=True):
            k = km[(km["gruppe"] == g) & (km["alder"] == t)]
            rader.append({"alder": t, "gruppe": g, "n": len(x), "direkte_andel": (x["siste_alder"] >= t).mean(),
                          "km_forsinket_inngang": float(k["overlevelse"].iloc[0]) if len(k) else np.nan})
        for a, x in s.groupby("debut_alder"):
            rader.append({"alder": t, "gruppe": f"debut {a}", "n": len(x),
                          "direkte_andel": (x["siste_alder"] >= t).mean(), "km_forsinket_inngang": np.nan})
    return pd.DataFrame(rader)


def lik_varighet(p):
    v = pd.read_csv(DATA / "arsvolum.csv").merge(p[["athlete_id", "debut_alder"]], on="athlete_id")
    rader, modeller = [], []
    for D in (4, 5, 6):
        q = p[p["debut_alder"] + D <= SISTE_HELE_SESONG - p["birth_year"]].copy()
        ok = v[(v["alder"] >= v["debut_alder"] + D) & (v["dager"] >= 2)]["athlete_id"].unique()
        q["utfall"] = q["athlete_id"].isin(set(ok)).astype(int)
        for a, x in q.groupby("debut_alder"):
            rader.append({"D": D, "debut_alder": a, "n": len(x), "andel": x["utfall"].mean()})
        tr = m03.logit_rader(q, ["debut_alder"] + m03.JUST, "utfall", f"varighet_{D}")
        kat = m03.logit_rader(q, ["debut_kat"] + m03.JUST, "utfall", f"varighet_{D}_kategorisk")
        modeller.append(pd.concat([tr, kat]))
    return pd.DataFrame(rader), pd.concat(modeller)


def uten_2001(p):
    q = p[p["birth_year"] != 2001]
    return pd.concat([m03.logit_rader(q, ["debut_kat"] + m03.JUST, "senior", "uten_2001_kategorisk"),
                      m03.logit_rader(q, ["debut_alder"] + m03.JUST, "senior", "uten_2001_trend")])


def seleksjon_kvartal(p):
    rader = [{"gruppe": f"senior={s}", "andel_med_fodselsdato": x["kvartal"].notna().mean(), "n": len(x)}
             for s, x in p.groupby("senior")]
    rader += [{"gruppe": f"debut {a}", "andel_med_fodselsdato": x["kvartal"].notna().mean(), "n": len(x)}
              for a, x in p.groupby("debut_alder")]
    return pd.DataFrame(rader)


def main():
    _, p = last()
    direkte_andeler(p).to_csv(UT / "a3_direkte_andeler.csv", index=False)
    andel, mod = lik_varighet(p)
    andel.to_csv(UT / "a3_lik_varighet_andeler.csv", index=False)
    mod.to_csv(UT / "a3_lik_varighet_modeller.csv", index=False)
    uten_2001(p).to_csv(UT / "a3_uten_2001.csv", index=False)
    seleksjon_kvartal(p).to_csv(UT / "a3_seleksjon_kvartal.csv", index=False)
    logger.info(f"ferdig; filer i {UT}/")


if __name__ == "__main__":
    main()
