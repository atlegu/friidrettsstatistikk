"""
07_revisjon_r1.py — A6: analyser til revisjon etter referee-runde 1.

  R2-3: stevneklyngede SE som primærvisning (hoved, alder, asymmetri, hekk).
  R2-5/R1-3: H5 fra medvindsgrenen per bånd; SD-nevner = poolet within-celle
             residual-SD av VINDJUSTERTE merker, celler med n>=3 (Bessel-korrigert).
  R2-6: ferdighetstertiler på vindjustert sesongsnitt; gradienttest på nytt.
  R1-2/R1-m4: effekt per sekund løpstid (flat + hekk) — målerprotokoll-poenget.
  R1-3: teoretisk asymmetriforhold (2v+w)/(2v-w) ved øvelsens snittfart.
  R2-7: bunching rundt 0,0 og +2,0; robusthet uten |vind-2,0|<=0,2;
        manglende vind etter stevnenivå og år; innendørsrader per øvelse.
  R3-4: +2,0 m/s i Tyrving-poeng (100 m; tabellalder 13 mot eldste tabell 19).
  R3-2: listeomstokking 2025 (klasse 14 og senior, 100 m) etter medvindskorreksjon.

Output: tables/estimering/r1_*.csv. Punktestimatene er identiske med runde 1
(klynging endrer bare SE); alle KI-er her er stevneklynget der annet ikke er sagt.
"""

import importlib.util
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as scst

HERE = Path(__file__).parent
DATA = HERE / "data_private"
EST = HERE / "tables" / "estimering"

spec = importlib.util.spec_from_file_location("m03", HERE / "03_estimering.py")
m03 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m03)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

TIDS = m03.TIDSKODER
DIST = {"60m": 60, "80m": 80, "100m": 100, "150m": 150, "200m": 200}
GRENSER = {"60mh": (7.5, 20), "80mh": (10, 26), "100mh": (12, 32), "110mh": (13, 34)}


def rad_av(res, kode, merk, ekstra=None):
    b, se = res["wind"]
    s = -1 if kode in TIDS else 1
    skala = 1 if kode in TIDS else 100
    g = s * b * skala
    return {"analyse": merk, "event": kode, "enhet": "s" if kode in TIDS else "cm",
            "gevinst_per_ms": round(g, 4),
            "ki_lav": round(g - 1.96 * se * skala, 4),
            "ki_hoy": round(g + 1.96 * se * skala, 4),
            "n": res["n"], "celler": res["celler"], **(ekstra or {})}


def pst_rad(res, kode, merk, ekstra=None):
    b, se = res["wind"]
    s = -1 if kode in TIDS else 1
    return {"analyse": merk, "event": kode, "enhet": "%",
            "gevinst_per_ms": round(s * 100 * b, 4),
            "ki_lav": round(s * 100 * b - 1.96 * 100 * se, 4),
            "ki_hoy": round(s * 100 * b + 1.96 * 100 * se, 4),
            "n": res["n"], "celler": res["celler"], **(ekstra or {})}


def main():
    import statsmodels
    logger.info(f"versjoner: python {sys.version.split()[0]}, pandas {pd.__version__}, "
                f"numpy {np.__version__}, statsmodels {statsmodels.__version__}")
    d = pd.read_csv(DATA / "analyseklar.csv", low_memory=False)
    d["logy"] = np.log(d["y"])
    d["wind_pos"] = d["wind"].clip(lower=0)
    d["wind_neg"] = d["wind"].clip(upper=0)
    koder = sorted(d["event_code"].unique())

    # ---- Stevneklynget: hoved + alder + asymmetri -------------------------------------
    hoved, alder, asym = [], [], []
    for kode in koder:
        g = d[d["event_code"] == kode]
        r = m03.estimer(g, "y", cluster="meet_id")
        if r:
            hoved.append(rad_av(r, kode, "hoved_meet"))
        rl = m03.estimer(g, "logy", cluster="meet_id")
        if rl:
            hoved.append(pst_rad(rl, kode, "hoved_meet_pst"))
        ra = m03.estimer(g, "y", vindkolonner=("wind_pos", "wind_neg"), cluster="meet_id")
        if ra and "wind_pos" in ra and "wind_neg" in ra:
            s = -1 if kode in TIDS else 1
            skala = 1 if kode in TIDS else 100
            bp, sep = ra["wind_pos"]
            bn, sen = ra["wind_neg"]
            m, navn = ra["_modell"], ra["_navn"]
            i, j = navn.index("wind_pos"), navn.index("wind_neg")
            diff = m.params[i] - m.params[j]
            se_d = float(np.sqrt(m.cov_params()[i, i] + m.cov_params()[j, j]
                                 - 2 * m.cov_params()[i, j]))
            if kode in DIST:
                vbar = DIST[kode] / float(g["y"].mean())
                teor = round((2 * vbar + 1) / (2 * vbar - 1), 2)
            else:
                teor = np.nan
            asym.append({"event": kode,
                         "medvind": round(s * bp * skala, 4),
                         "medvind_ki_lav": round(s * bp * skala - 1.96 * sep * skala, 4),
                         "medvind_ki_hoy": round(s * bp * skala + 1.96 * sep * skala, 4),
                         "motvind": round(s * bn * skala, 4),
                         "motvind_ki_lav": round(s * bn * skala - 1.96 * sen * skala, 4),
                         "motvind_ki_hoy": round(s * bn * skala + 1.96 * sen * skala, 4),
                         "ratio_obs": round(abs(bn / bp), 2) if bp != 0 else np.nan,
                         "ratio_teoretisk_v2": teor,
                         "p_lik_meet": round(float(2 * (1 - scst.norm.cdf(abs(diff / se_d)))), 5)
                         if se_d > 0 else np.nan,
                         "n": ra["n"], "celler": ra["celler"]})
        for kj in ["M", "F"]:
            for band, gg in g[g["gender"] == kj].groupby("aldersband"):
                r = m03.estimer(gg, "y", cluster="meet_id")
                if r:
                    alder.append(rad_av(r, kode, "alder_meet",
                                        {"kjonn": kj, "aldersband": band}))
                rl = m03.estimer(gg, "logy", cluster="meet_id")
                if rl:
                    alder.append(pst_rad(rl, kode, "alder_meet",
                                         {"kjonn": kj, "aldersband": band}))
    pd.DataFrame(hoved).to_csv(EST / "r1_hoved_meet.csv", index=False)
    pd.DataFrame(alder).to_csv(EST / "r1_alder_meet.csv", index=False)
    pd.DataFrame(asym).to_csv(EST / "r1_asym_meet.csv", index=False)
    logger.info("stevneklynget hoved/alder/asym ferdig")

    # ---- Vindjusterte merker; tertiler på nytt (R2-6) -----------------------------------
    beta = {r["event"]: r["gevinst_per_ms"] for r in hoved if r["analyse"] == "hoved_meet"}
    er_tid = d["event_code"].isin(list(TIDS))
    d["y_adj"] = np.where(er_tid,
                          d["y"] + d["event_code"].map(beta) * d["wind"],
                          d["y"] - d["event_code"].map(beta).fillna(0) / 100 * d["wind"])

    cm_adj = d.groupby("celle")["y_adj"].transform("mean")
    d["prest_adj"] = np.where(er_tid, -cm_adj, cm_adj)
    grp = d.groupby(["event_code", "gender", "aldersband"])["prest_adj"]
    d["adj_z"] = (d["prest_adj"] - grp.transform("mean")) / grp.transform("std")

    def tertil(s):
        if s.notna().sum() < 30 or s.nunique() < 3:
            return pd.Series(index=s.index, dtype="object")
        return pd.qcut(s.rank(method="first"), 3, labels=["lav", "midt", "hoy"])

    d["tert_adj"] = (d.groupby(["event_code", "gender", "aldersband"])["adj_z"]
                     .transform(tertil))
    tert = []
    for kode in koder:
        for t, gg in d[d["event_code"] == kode].groupby("tert_adj", observed=True):
            r = m03.estimer(gg, "y", cluster="meet_id")
            if r:
                tert.append(rad_av(r, kode, "tertil_adj", {"tertil": t}))
    pd.DataFrame(tert).to_csv(EST / "r1_tertil_adj.csv", index=False)
    logger.info("vindjusterte tertiler ferdig")

    # ---- H5: begge vindgrener per bånd + presis SD-nevner (R2-5, R3-1) -------------------
    res_adj = d["y_adj"] - cm_adj
    d["_res2"] = res_adj ** 2
    dm_raa = d["y"] - d.groupby("celle")["y"].transform("mean")
    vindu = []
    for kode in ["60m", "100m", "200m"]:
        for kj in ["M", "F"]:
            for band, gg in d[(d["event_code"] == kode) & (d["gender"] == kj)].groupby("aldersband"):
                r = m03.estimer(gg, "y", vindkolonner=("wind_pos", "wind_neg"),
                                cluster="meet_id")
                if not r or "wind_pos" not in r or "wind_neg" not in r:
                    continue
                bp, sep = r["wind_pos"]
                bn, sen = r["wind_neg"]
                g3 = gg[gg["n_i_celle"] >= 3]
                nn = g3.groupby("celle")["y"].count()
                frih = max(int((nn - 1).sum()), 1)
                sd_pool = float(np.sqrt(g3["_res2"].sum() / frih))
                sd_gammel = float(dm_raa[gg.index].std())
                fordel = -2 * bp
                vindu.append({"event": kode, "kjonn": kj, "aldersband": band,
                              "medvind_s_per_ms": round(-bp, 4),
                              "medvind_ki_lav": round(-bp - 1.96 * sep, 4),
                              "medvind_ki_hoy": round(-bp + 1.96 * sep, 4),
                              "motvind_s_per_ms": round(-bn, 4),
                              "motvind_ki_lav": round(-bn - 1.96 * sen, 4),
                              "motvind_ki_hoy": round(-bn + 1.96 * sen, 4),
                              "fordel_2ms_s": round(fordel, 3),
                              "sd_poolet_adj": round(sd_pool, 3),
                              "fordel_i_sd": round(fordel / sd_pool, 2) if sd_pool > 0 else np.nan,
                              "sd_runde1": round(sd_gammel, 3),
                              "n": r["n"], "celler": r["celler"]})
    vv = pd.DataFrame(vindu)
    vv.to_csv(EST / "r1_vindu_medvind.csv", index=False)
    logger.info("H5 vindgrener per bånd ferdig")

    # ---- Hekk: stevneklynget + snittid per kode (R1-m4) ----------------------------------
    hr = pd.read_csv(DATA / "resultater_hekk.csv", parse_dates=["date"], low_memory=False)
    utv = pd.read_csv(DATA / "utovere.csv").rename(columns={"id": "athlete_id"})
    me = pd.read_csv(DATA / "meets.csv").rename(columns={"id": "meet_id"})
    hr = hr.merge(utv, on="athlete_id", how="left")
    hr = hr.merge(me[["meet_id", "indoor"]], on="meet_id", how="left")
    hr["aar"] = hr["date"].dt.year
    hr["maaned"] = hr["date"].dt.month
    hr = hr[(hr["status"] == "OK") & (hr["indoor"].astype(str) != "True")
            & (hr["is_manual_time"].astype(str) != "True")
            & hr["gender"].isin(["M", "F"]) & hr["birth_year"].notna()]
    hr["alder"] = (hr["aar"] - hr["birth_year"]).astype(int)
    hr = hr[hr["alder"].between(10, 34) & hr["wind"].notna() & (hr["wind"].abs() <= 8)]
    hr["y"] = hr["performance_value"] / 100
    dist = hr["event_code"].str.split("_").str[0]
    hr = hr[hr["y"].between(dist.map(lambda k: GRENSER[k][0]),
                            dist.map(lambda k: GRENSER[k][1]))].copy()
    hr["logy"] = np.log(hr["y"])
    hr["celle"] = (hr["athlete_id"].astype(str) + "_" + hr["aar"].astype(str)
                   + "_" + hr["event_code"])
    hr["n_i_celle"] = hr.groupby("celle")["id"].transform("count")
    hr["runde"] = hr["round"].fillna("ukjent").astype(str)
    hekk = []
    for kode, g in hr.groupby("event_code"):
        for kj in ["begge", "M", "F"]:
            gg = g if kj == "begge" else g[g["gender"] == kj]
            res = m03.estimer(gg, "y", cluster="meet_id")
            if not res:
                continue
            b, se = res["wind"]
            hekk.append({"kode": kode, "kjonn": kj,
                         "gevinst_s_per_ms": round(-b, 4),
                         "ki_lav": round(-b - 1.96 * se, 4),
                         "ki_hoy": round(-b + 1.96 * se, 4),
                         "snitt_tid_s": round(float(gg["y"].mean()), 2),
                         "per_sekund": round(-b / gg["y"].mean(), 5),
                         "n": res["n"], "celler": res["celler"]})
    pd.DataFrame(hekk).to_csv(EST / "r1_hekk_meet.csv", index=False)
    logger.info("hekk stevneklynget ferdig")

    # ---- Effekt per sekund løpstid, flat sprint (R1-2) -----------------------------------
    perdur = []
    for kode in sorted(DIST):
        g = d[d["event_code"] == kode]
        if kode in beta and len(g):
            snitt = float(g["y"].mean())
            perdur.append({"event": kode, "snitt_tid_s": round(snitt, 2),
                           "gevinst_per_ms": beta[kode],
                           "per_sekund": round(beta[kode] / snitt, 5)})
    pd.DataFrame(perdur).to_csv(EST / "r1_per_sekund.csv", index=False)

    # ---- Bunching og robusthet rundt +2,0 (R2-7) -----------------------------------------
    w = d["wind"]
    bunch = [{"intervall": lab, "andel": round(float(m), 5)} for lab, m in [
        ("[1.6,1.8]", ((w >= 1.6) & (w <= 1.8)).mean()),
        ("(1.8,2.0]", ((w > 1.8) & (w <= 2.0)).mean()),
        ("(2.0,2.2]", ((w > 2.0) & (w <= 2.2)).mean()),
        ("(2.2,2.4]", ((w > 2.2) & (w <= 2.4)).mean()),
        ("eksakt 0.0", (w == 0).mean()),
        ("eksakt 2.0", (w == 2.0).mean()),
    ]]
    rob2 = []
    for kode in koder:
        g = d[(d["event_code"] == kode) & ((d["wind"] - 2.0).abs() > 0.2)]
        r = m03.estimer(g, "y", cluster="meet_id")
        if r:
            rob2.append(rad_av(r, kode, "uten_vindu_rundt_2.0"))
    pd.DataFrame(bunch).to_csv(EST / "r1_bunching.csv", index=False)
    pd.DataFrame(rob2).to_csv(EST / "r1_uten_2.csv", index=False)

    # ---- Manglende vind etter stevnenivå; innendørsrader per øvelse ----------------------
    r0 = pd.read_csv(DATA / "resultater.csv", low_memory=False,
                     usecols=["event_code", "meet_id", "wind", "status"])
    r0 = r0.merge(me[["meet_id", "indoor", "level"]], on="meet_id", how="left")
    ute = r0[(r0["status"] == "OK") & (r0["indoor"].astype(str) != "True")].copy()
    ute["mangler"] = ute["wind"].isna()
    (ute.groupby(ute["level"].fillna("ukjent"))["mangler"].agg(["mean", "count"])
     .round(4).to_csv(EST / "r1_missingvind_nivaa.csv"))
    (r0[r0["indoor"].astype(str) == "True"].groupby("event_code").size()
     .rename("innendorsrader").to_csv(EST / "r1_innendors_per_ovelse.csv"))

    # ---- Tyrving-poeng for +2,0 på 100 m (R3-4) ------------------------------------------
    sys.path.insert(0, str(Path("/Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/Statistikk/"
                                "forskning/ncc-kohort/revision_r1/analysis")))
    from tyrving_r2 import parse_tyrving_xls, beregn_tyrving_poeng
    tabell = parse_tyrving_xls()
    rows = []
    for kj in ["M", "F"]:
        for band, t_alder in [("12-13", 13), ("20-34", 19)]:
            t = vv[(vv["event"] == "100m") & (vv["kjonn"] == kj) & (vv["aldersband"] == band)]
            g = d[(d["event_code"] == "100m") & (d["gender"] == kj)
                  & (d["aldersband"] == band)]
            if not len(t) or not len(g):
                continue
            fordel = float(t["fordel_2ms_s"].iloc[0])
            snitt = float(g["y"].mean())
            p0 = beregn_tyrving_poeng(round(snitt * 100), "100m", "time", kj, t_alder, tabell)
            p1 = beregn_tyrving_poeng(round((snitt - fordel) * 100), "100m", "time",
                                      kj, t_alder, tabell)
            if p0 is None or p1 is None:
                continue
            rows.append({"kjonn": kj, "aldersband": band, "tabellalder": t_alder,
                         "snitt_tid_s": round(snitt, 2), "fordel_2ms_s": fordel,
                         "poeng_uten": p0, "poeng_med": p1,
                         "tyrvingpoeng_for_2ms": round(p1 - p0, 1)})
    pd.DataFrame(rows).to_csv(EST / "r1_tyrvingpoeng.csv", index=False)
    logger.info(f"tyrvingpoeng: {rows}")

    # ---- Listeomstokking 2025: 100 m klasse 14 og senior (R3-2) --------------------------
    b_band = {(r["kjonn"], r["aldersband"]): r["medvind_s_per_ms"]
              for r in vindu if r["event"] == "100m"}
    oms = []
    for kj in ["M", "F"]:
        for navn, lo, hi, band in [("klasse 14", 14, 14, "14-15"), ("senior", 20, 34, "20-34")]:
            if (kj, band) not in b_band:
                continue
            g = d[(d["event_code"] == "100m") & (d["gender"] == kj) & (d["aar"] == 2025)
                  & d["alder"].between(lo, hi)].copy()
            if g["athlete_id"].nunique() < 60:
                continue
            g["y_korr"] = g["y"] + b_band[(kj, band)] * g["wind"].clip(lower=0)
            topp = (g.sort_values("y").drop_duplicates("athlete_id")
                    .nsmallest(50, "y").reset_index(drop=True))
            topp2 = (g.sort_values("y_korr").drop_duplicates("athlete_id")
                     .nsmallest(50, "y_korr").reset_index(drop=True))
            f10 = list(topp["athlete_id"].head(10))
            e10 = list(topp2["athlete_id"].head(10))
            oms.append({"kjonn": kj, "liste": navn,
                        "n_utovere": int(g["athlete_id"].nunique()),
                        "plassendringer_topp10": sum(a != b for a, b in zip(f10, e10)),
                        "nye_i_topp50": len(set(topp2["athlete_id"]) - set(topp["athlete_id"])),
                        "andel_topp50_vind_over_1": round(float((topp["wind"] > 1).mean()), 2)})
    pd.DataFrame(oms).to_csv(EST / "r1_listeomstokk.csv", index=False)

    logger.info(f"ferdig; r1-filer i {EST}/")


if __name__ == "__main__":
    main()
