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
sys.path.insert(0, str(HERE.parent))
from rens_felles import fjern_kopier  # noqa: E402

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
            "gevinst_per_ms": (g),
            "ki_lav": (g - 1.96 * se * skala),
            "ki_hoy": (g + 1.96 * se * skala),
            "n": res["n"], "celler": res["celler"], **(ekstra or {})}


def pst_rad(res, kode, merk, ekstra=None):
    b, se = res["wind"]
    s = -1 if kode in TIDS else 1
    return {"analyse": merk, "event": kode, "enhet": "%",
            "gevinst_per_ms": (s * 100 * b),
            "ki_lav": (s * 100 * b - 1.96 * 100 * se),
            "ki_hoy": (s * 100 * b + 1.96 * 100 * se),
            "n": res["n"], "celler": res["celler"], **(ekstra or {})}


def drag_referanse(g, kode):
    """Ren drag-fysikk lagt på de observerte vindene og estimert med de samme modellene.

    (2v+1)/(2v-1) er forholdet ved nøyaktig ±1 m/s, mens modellen gir helninger midlet over hele
    vindfordelingen på hver side (audit 30.10.2026, funn A6-1). Sannheten Δt = c·t·((v−w)² − v²)/v²
    (t = cellesnittet, v = distanse/t) estimeres som de observerte tidene; c kalibreres slik at den
    symmetriske helningen er lik den observerte, så grenhelninger og kvadratledd blir sammenlignbare.
    """
    g = g.copy()
    t = g.groupby("celle")["y"].transform("mean")
    v = DIST[kode] / t
    g["ysim"] = t * ((v - g["wind"]) ** 2 - v ** 2) / v ** 2
    g["wind2"] = g["wind"] ** 2
    c = (m03.estimer(g, "y", cluster="meet_id")["wind"][0]
         / m03.estimer(g, "ysim", cluster="meet_id")["wind"][0])
    ps = m03.estimer(g, "ysim", vindkolonner=("wind_pos", "wind_neg"), cluster="meet_id")
    qs = m03.estimer(g, "ysim", vindkolonner=("wind", "wind2"), cluster="meet_id")
    return {"ratio_drag": ps["wind_neg"][0] / ps["wind_pos"][0],
            "drag_medvind": -c * ps["wind_pos"][0], "drag_motvind": -c * ps["wind_neg"][0],
            "drag_kvad": c * qs["wind2"][0]}


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
            m, navn, V = ra["_modell"], ra["_navn"], ra["_V"]
            i, j = navn.index("wind_pos"), navn.index("wind_neg")
            diff = m.params[i] - m.params[j]
            se_d = float(np.sqrt(V[i, i] + V[j, j]
                                 - 2 * V[i, j]))
            if kode in DIST:
                vbar = DIST[kode] / float(g["y"].mean())
                teor = ((2 * vbar + 1) / (2 * vbar - 1))
                drag = drag_referanse(g, kode)
            else:
                teor, drag = np.nan, {}
            asym.append({"event": kode,
                         "medvind": (s * bp * skala),
                         "medvind_ki_lav": (s * bp * skala - 1.96 * sep * skala),
                         "medvind_ki_hoy": (s * bp * skala + 1.96 * sep * skala),
                         "motvind": (s * bn * skala),
                         "motvind_ki_lav": (s * bn * skala - 1.96 * sen * skala),
                         "motvind_ki_hoy": (s * bn * skala + 1.96 * sen * skala),
                         "ratio_obs": (abs(bn / bp)) if bp != 0 else np.nan,
                         "ratio_teoretisk_v2": teor,
                         "ratio_drag_estimator": drag.get("ratio_drag", np.nan),
                         "drag_medvind": drag.get("drag_medvind", np.nan),
                         "drag_motvind": drag.get("drag_motvind", np.nan),
                         "drag_kvad": drag.get("drag_kvad", np.nan),
                         "p_lik_meet": (float(2 * (1 - scst.norm.cdf(abs(diff / se_d)))))
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

    # ---- Kvadratisk form, stevneklynget (S5; runde 1 hadde utøverklynger) ----------------
    d["wind2"] = d["wind"] ** 2
    kvad = []
    for kode in koder:
        r = m03.estimer(d[d["event_code"] == kode], "y", vindkolonner=("wind", "wind2"),
                        cluster="meet_id")
        if r:
            kvad.append({"event": kode, "beta_lin": r["wind"][0], "se_lin": r["wind"][1],
                         "beta_kvad": r["wind2"][0], "se_kvad": r["wind2"][1],
                         "n": r["n"], "celler": r["celler"]})
    pd.DataFrame(kvad).to_csv(EST / "r1_kvad_meet.csv", index=False)

    # ---- Vindjusterte merker; tertiler på nytt (R2-6) -----------------------------------
    beta = {r["event"]: r["gevinst_per_ms"] for r in hoved if r["analyse"] == "hoved_meet"}
    er_tid = d["event_code"].isin(list(TIDS))
    d["y_adj"] = np.where(er_tid,
                          d["y"] + d["event_code"].map(beta) * d["wind"],
                          d["y"] - d["event_code"].map(beta).fillna(0) / 100 * d["wind"])

    cm_adj = d.groupby("celle")["y_adj"].transform("mean")

    # Tertiler av utøversesonger (celler med >=2 resultater), ikke av rader: analyseplanen
    # definerer nivå per celle. Radbaserte tertiler (audit 30.10.2026, funn A6-2) ga like
    # mange RESULTATER per tertil, så lavtertilen fikk ~50 % flere celler, og en grensecelle
    # kunne deles. Rang innen øvelse x kjønn x bånd med celle-id som deterministisk tie-break;
    # tertil = floor(3*(rang-1)/m), grupper under 30 celler får ingen tertil.
    gr = ["event_code", "gender", "aldersband"]
    celler = (d[d["n_i_celle"] >= 2].groupby("celle")
              .agg(event_code=("event_code", "first"), gender=("gender", "first"),
                   aldersband=("aldersband", "first"), cm_adj=("y_adj", "mean"))
              .reset_index())
    celler["prest_adj"] = np.where(celler["event_code"].isin(list(TIDS)),
                                   -celler["cm_adj"], celler["cm_adj"])
    celler = celler.sort_values(gr + ["prest_adj", "celle"]).reset_index(drop=True)
    celler["rang"] = celler.groupby(gr).cumcount() + 1
    celler["m"] = celler.groupby(gr)["celle"].transform("size")
    t_idx = np.floor(3 * (celler["rang"] - 1) / celler["m"]).astype(int)
    celler["tert_adj"] = np.where(celler["m"] >= 30,
                                  np.array(["lav", "midt", "hoy"])[t_idx], None)
    d["tert_adj"] = d["celle"].map(celler.set_index("celle")["tert_adj"])
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
                # Verdien av +2,0 m/s fra helningen over 0..+2 (knekk ved 0 og +2): helningen
                # flater ut over +2, så hele medvindsgrenen undervurderer vinduet (funn A6-5)
                r02 = m03.estimer(gg.assign(w02=gg["wind"].clip(0, 2), w2p=(gg["wind"] - 2).clip(lower=0)),
                                  "y", vindkolonner=("w02", "w2p", "wind_neg"), cluster="meet_id")
                b02, se02 = r02["w02"]
                b2p = r02["w2p"][0]
                g3 = gg[gg["n_i_celle"] >= 3]
                nn = g3.groupby("celle")["y"].count()
                frih = max(int((nn - 1).sum()), 1)
                sd_pool = float(np.sqrt(g3["_res2"].sum() / frih))
                # Robust skala (1,4826·MAD av residualene innen celle, frihetsgradskorrigert): noen
                # grove registreringsfeil (f.eks. 200 m-tider under 100 m) blåser opp den klassiske
                # SD-en (funn A6-4); helningene påvirkes ikke merkbart
                res = res_adj[g3.index]
                skala_robust = float(1.4826 * np.median(np.abs(res - res.median()))
                                     * np.sqrt(len(res) / frih))
                sd_gammel = float(dm_raa[gg.index].std())
                fordel = -2 * bp
                vindu.append({"event": kode, "kjonn": kj, "aldersband": band,
                              "medvind_0_2_s_per_ms": (-b02),
                              "over_2_s_per_ms": (-b2p),
                              "fordel_0_2_s": (-2 * b02),
                              "fordel_0_2_ki_lav": (-2 * b02 - 1.96 * 2 * se02),
                              "fordel_0_2_ki_hoy": (-2 * b02 + 1.96 * 2 * se02),
                              "skala_robust": skala_robust,
                              "fordel_0_2_i_robust_skala": (-2 * b02 / skala_robust),
                              "medvind_s_per_ms": (-bp),
                              "medvind_ki_lav": (-bp - 1.96 * sep),
                              "medvind_ki_hoy": (-bp + 1.96 * sep),
                              "motvind_s_per_ms": (-bn),
                              "motvind_ki_lav": (-bn - 1.96 * sen),
                              "motvind_ki_hoy": (-bn + 1.96 * sen),
                              "fordel_2ms_s": (fordel),
                              "sd_poolet_adj": (sd_pool),
                              "fordel_i_sd": (fordel / sd_pool) if sd_pool > 0 else np.nan,
                              "sd_runde1": (sd_gammel),
                              "n": r["n"], "celler": r["celler"]})
    vv = pd.DataFrame(vindu)
    vv.to_csv(EST / "r1_vindu_medvind.csv", index=False)
    logger.info("H5 vindgrener per bånd ferdig")

    # ---- Hekk: stevneklynget + snittid per kode (R1-m4) ----------------------------------
    hr = pd.read_csv(DATA / "resultater_hekk.csv", parse_dates=["date"], low_memory=False)
    hr, _ = fjern_kopier(hr)
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
    banddef = [(10, 11, "10-11"), (12, 13, "12-13"), (14, 15, "14-15"),
               (16, 17, "16-17"), (18, 19, "18-19"), (20, 34, "20-34")]
    hr["aldersband"] = hr["alder"].map(lambda a: next(n for lo, hi, n in banddef if lo <= a <= hi))
    # Flatreferansen tas fra kjønnets EGET modalbånd i koden (audit 30.10.2026, funn A6-3:
    # samlet modalbånd ga 20-34 for guttene i 100 m hekk 84 cm, som alle er 14-15).
    adf = pd.DataFrame(alder)
    flat_kode = {"60mh": "60m", "80mh": None, "100mh": "100m", "110mh": "100m"}
    hekk = []
    for kode, g in hr.groupby("event_code"):
        for kj in ["begge", "M", "F"]:
            gg = g if kj == "begge" else g[g["gender"] == kj]
            res = m03.estimer(gg, "y", cluster="meet_id")
            if not res:
                continue
            b, se = res["wind"]
            band_mod = gg["aldersband"].value_counts().sort_index().idxmax()
            fk = flat_kode[kode.split("_")[0]]
            ref = adf[(adf["event"] == fk) & (adf["kjonn"] == kj) & (adf["aldersband"] == band_mod)
                      & (adf["enhet"] == "s")] if (fk and kj != "begge") else adf.iloc[0:0]
            rad_h = {"kode": kode, "kjonn": kj,
                     "gevinst_s_per_ms": (-b),
                     "ki_lav": (-b - 1.96 * se),
                     "ki_hoy": (-b + 1.96 * se),
                     "snitt_tid_s": (float(gg["y"].mean())),
                     "per_sekund": (-b / gg["y"].mean()),
                     "modal_aldersband": band_mod, "flat_ref_ovelse": fk or "",
                     "flat_ref": float(ref["gevinst_per_ms"].iloc[0]) if len(ref) else np.nan,
                     "flat_ref_ki_lav": float(ref["ki_lav"].iloc[0]) if len(ref) else np.nan,
                     "flat_ref_ki_hoy": float(ref["ki_hoy"].iloc[0]) if len(ref) else np.nan,
                     "n": res["n"], "celler": res["celler"]}
            rad_h["ki_overlapper_flat"] = (bool(rad_h["ki_lav"] <= rad_h["flat_ref_ki_hoy"]
                                                and rad_h["ki_hoy"] >= rad_h["flat_ref_ki_lav"])
                                           if len(ref) else np.nan)
            hekk.append(rad_h)
    pd.DataFrame(hekk).to_csv(EST / "r1_hekk_meet.csv", index=False)
    logger.info("hekk stevneklynget ferdig")

    # ---- Effekt per sekund løpstid, flat sprint (R1-2) -----------------------------------
    perdur = []
    for kode in sorted(DIST):
        g = d[d["event_code"] == kode]
        if kode in beta and len(g):
            snitt = float(g["y"].mean())
            perdur.append({"event": kode, "snitt_tid_s": (snitt),
                           "gevinst_per_ms": beta[kode],
                           "per_sekund": (beta[kode] / snitt)})
    pd.DataFrame(perdur).to_csv(EST / "r1_per_sekund.csv", index=False)

    # ---- Bunching og robusthet rundt +2,0 (R2-7) -----------------------------------------
    w = d["wind"]
    bunch = [{"intervall": lab, "andel": (float(m))} for lab, m in [
        ("[1.6,1.8]", ((w >= 1.6) & (w <= 1.8)).mean()),
        ("(1.8,2.0]", ((w > 1.8) & (w <= 2.0)).mean()),
        ("(2.0,2.2]", ((w > 2.0) & (w <= 2.2)).mean()),
        ("(2.2,2.4]", ((w > 2.2) & (w <= 2.4)).mean()),
        ("eksakt 0.0", (w == 0).mean()),
        ("eksakt 2.0", (w == 2.0).mean()),
    ]]
    rob2 = []
    for kode in koder:
        # avstand i tideler: (vind - 2,0).abs() > 0,2 beholdt +2,2 og tok ut +1,8 (flyttall)
        g = d[(d["event_code"] == kode) & ((d["wind"] * 10).round() - 20).abs().gt(2)]
        r = m03.estimer(g, "y", cluster="meet_id")
        if r:
            rob2.append(rad_av(r, kode, "uten_vindu_rundt_2.0"))
    pd.DataFrame(bunch).to_csv(EST / "r1_bunching.csv", index=False)
    pd.DataFrame(rob2).to_csv(EST / "r1_uten_2.csv", index=False)

    # ---- Manglende vind etter stevnenivå; innendørsrader per øvelse ----------------------
    r0 = pd.read_csv(DATA / "resultater.csv", low_memory=False,
                     usecols=["id", "athlete_id", "event_code", "meet_id", "wind", "status",
                              "date", "performance_value", "round"])
    r0, _ = fjern_kopier(r0)
    r0 = r0.merge(me[["meet_id", "indoor", "level"]], on="meet_id", how="left")
    ute = r0[(r0["status"] == "OK") & (r0["indoor"].astype(str) != "True")].copy()
    ute["mangler"] = ute["wind"].isna()
    (ute.groupby(ute["level"].fillna("ukjent"))["mangler"].agg(["mean", "count"])
     .to_csv(EST / "r1_missingvind_nivaa.csv"))
    storr = ute.groupby("meet_id")["event_code"].transform("count")
    ute["stevnestr"] = pd.qcut(storr, 3, labels=["minste tredel", "midtre", "storste tredel"])
    (ute.groupby("stevnestr", observed=True)["mangler"].agg(["mean", "count"])
     .to_csv(EST / "r1_missingvind_storrelse.csv"))
    ute["aar"] = pd.to_datetime(ute["date"]).dt.year
    ute.groupby("aar")["mangler"].mean().to_csv(EST / "r1_missingvind_aar.csv")
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
            fordel = float(t["fordel_0_2_s"].iloc[0])
            snitt = float(g["y"].mean())
            p0 = beregn_tyrving_poeng(round(snitt * 100), "100m", "time", kj, t_alder, tabell)
            p1 = beregn_tyrving_poeng(round((snitt - fordel) * 100), "100m", "time",
                                      kj, t_alder, tabell)
            if p0 is None or p1 is None:
                continue
            rows.append({"kjonn": kj, "aldersband": band, "tabellalder": t_alder,
                         "snitt_tid_s": (snitt), "fordel_0_2_s": fordel,
                         "poeng_uten": p0, "poeng_med": p1,
                         "tyrvingpoeng_for_2ms": (p1 - p0)})
    pd.DataFrame(rows).to_csv(EST / "r1_tyrvingpoeng.csv", index=False)
    logger.info(f"tyrvingpoeng: {rows}")

    # ---- Listeomstokking 2025: 100 m klasse 14 og senior (R3-2) --------------------------
    # Som de nasjonale årslistene: bare lovlige merker (vind <= +2,0), og senior er åpen klasse
    # (alle aldre i filen). Hver rad korrigeres til stille luft med medvindshelningen over
    # 0..+2 for egen kjønns- og aldersgruppe (H5). Audit 30.10.2026: listene tok med medvind
    # over +2,0, senior var 20-34 år, og lister med under 60 utøvere falt stille ut.
    b02 = {(r["kjonn"], r["aldersband"]): r["medvind_0_2_s_per_ms"] for r in vindu if r["event"] == "100m"}
    oms = []
    for kj in ["M", "F"]:
        for navn, lo, hi in [("klasse 14", 14, 14), ("senior", 10, 34)]:
            g = d[(d["event_code"] == "100m") & (d["gender"] == kj) & (d["aar"] == 2025)
                  & d["alder"].between(lo, hi) & (d["wind"] <= 2.0)].copy()
            helning = g["aldersband"].map(lambda b: b02.get((kj, b), np.nan))
            uten = int(helning.isna().sum())
            g, helning = g[helning.notna()], helning[helning.notna()]
            if g["athlete_id"].nunique() < 50:
                logger.info(f"liste {kj} {navn}: bare {g['athlete_id'].nunique()} utøvere, hoppes over")
                continue
            g["y_korr"] = g["y"] + helning * g["wind"].clip(lower=0)
            topp = (g.sort_values("y").drop_duplicates("athlete_id")
                    .nsmallest(50, "y").reset_index(drop=True))
            topp2 = (g.sort_values("y_korr").drop_duplicates("athlete_id")
                     .nsmallest(50, "y_korr").reset_index(drop=True))
            f10 = list(topp["athlete_id"].head(10))
            e10 = list(topp2["athlete_id"].head(10))
            oms.append({"kjonn": kj, "liste": navn,
                        "n_utovere": int(g["athlete_id"].nunique()), "rader_uten_helning": uten,
                        "plassendringer_topp10": sum(a != b for a, b in zip(f10, e10)),
                        "nye_i_topp10": len(set(e10) - set(f10)),
                        "nye_i_topp50": len(set(topp2["athlete_id"]) - set(topp["athlete_id"])),
                        "andel_topp50_vind_over_1": (float((topp["wind"] > 1).mean()))})
    pd.DataFrame(oms).to_csv(EST / "r1_listeomstokk.csv", index=False)

    logger.info(f"ferdig; r1-filer i {EST}/")


if __name__ == "__main__":
    main()
