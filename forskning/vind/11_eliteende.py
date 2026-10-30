r"""
11_eliteende.py — A6: eliteenden med samme estimator (tabell S8; lagt til etter planen 30.10.2026).

Spørsmålet: ligger de publiserte eliteverdiene der registerets gradient peker, og holder
proporsjonaliteten med løpstid (tabell S4) utenfor registeret? To eksterne utvalg av
vindmålte utendørsresultater i 100 m, 200 m, 100/110 m hekk, lengde og tresteg:

  TFRRS        amerikanske collegeresultater fra den hash-kontrollerte fellesbyggingen
               Covid/tfrrs_shared v1.2 (results_clean.csv; A6 er registrert i PAPERS.md der)
  Tilastopaja  karriereresultatene til mesterskapsfinalister (Alder-prosjektets uttrekk,
               season_results.csv); bruk i denne studien krever Tilastopaja Oys tillatelse

Estimatoren (03_estimering.py) importeres urørt: within utøver x kalenderår x øvelse, måneds-
(klippet 4-10) og rundedummyer, stevneklyngede SE med fixest-lik småutvalgskorreksjon.
Filtrene speiler 01_variabler.py: utendørs, elektronisk tid (hundredeler), vind innen ±8 m/s,
øvelsesvise rimelighetsgrenser; mangekampdeløvelser tas ut (TFRRS is_multi_sub, Tilastopaja
plass D/H). Norske referanserader (alle aldre og 20-34, per kjønn) regnes med samme kode fra
analyseklar.csv, så tabellen er internt konsistent med tabell 2-4 og S7.

Inndataene hash-kontrolleres mot eliteende_input.sha256 før noe leses.

Output: tables/estimering/r3_eliteende.csv          hoved, prosent, asymmetri med drag, knekk ved +2, stevne-FE
        tables/estimering/r3_eliteende_tertil.csv   TFRRS-tertiler på vindjustert sesongsnitt (A6-definisjonen)
        tables/estimering/r3_eliteende_robusthet.csv
        data_private/eliteende_analyseklar.csv      de eksterne radene (til R-speilet audit/uavhengig.R)
        data_private/eliteende_flyt.json            flyt per kilde
"""

import hashlib
import importlib.util
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as scst

HERE = Path(__file__).resolve().parent
DATA = HERE / "data_private"
EST = HERE / "tables" / "estimering"
HASHFIL = HERE / "eliteende_input.sha256"
TFRRS = (HERE / "../../../Covid/tfrrs_shared/v1.2/output/results_clean.csv").resolve()
TP = (HERE / "../../../../2026Host/Idrettsanlyser/Alder/data/processed/season_results.csv").resolve()

spec = importlib.util.spec_from_file_location("m03", HERE / "03_estimering.py")
m03 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m03)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

KODER = ["100m", "200m", "100mH", "110mH", "LJ", "TJ"]
TID = {"100m", "200m", "100mH", "110mH"}
GRENSER = {"100m": (9.5, 14.5), "200m": (19.0, 30.0), "100mH": (11.0, 20.0), "110mH": (12.0, 20.0),
           "LJ": (3.0, 9.0), "TJ": (8.0, 18.5)}
DIST = {"100m": 100, "200m": 200}
NORGE_KODE = {"100m": "100m", "200m": "200m", "lengde": "LJ", "tresteg": "TJ"}
# Moinat m.fl. (2018, lign. 7): fordelen ved +1 m/s for en løper med tid P er (0,009459 P - 0,0449) - 0,0042
MOINAT_A, MOINAT_B, MOINAT_Q = 0.009459, -0.0449, -0.0042
KOL = ["kilde", "event_code", "gender", "athlete_id", "aar", "maaned", "runde", "meet_id", "y", "wind"]


def sjekk_hasher():
    for linje in HASHFIL.read_text().splitlines():
        if not linje.strip():
            continue
        h, sti = linje.split(maxsplit=1)
        p = (HERE / sti.strip()).resolve()
        dig = hashlib.sha256()
        with open(p, "rb") as f:
            for blk in iter(lambda: f.read(1 << 24), b""):
                dig.update(blk)
        if dig.hexdigest() != h:
            raise SystemExit(f"FEIL: {p} stemmer ikke med {HASHFIL.name}")
    logger.info("inndata stemmer med eliteende_input.sha256")


def grenser_ok(r):
    lo = r["event_code"].map(lambda k: GRENSER[k][0])
    hi = r["event_code"].map(lambda k: GRENSER[k][1])
    return r["y"].between(lo, hi)


# ---------------------------------------------------------------- TFRRS (fellesbyggingen v1.2)
def les_tfrrs():
    kol = ["athlete_id", "gender", "event", "mark", "mark_numeric", "wind_num", "round", "meet_id", "date",
           "season", "is_xc", "is_multi_sub", "valid", "hand", "flag_error"]
    ev = {"100": "100m", "200": "200m", "100H": "100mH", "110H": "110mH", "LJ": "LJ", "TJ": "TJ"}
    deler = [ch[ch["event"].isin(ev) & (ch["season"] == "outdoor")]
             for ch in pd.read_csv(TFRRS, usecols=kol, dtype=str, chunksize=1_000_000)]
    r = pd.concat(deler, ignore_index=True)
    flyt = {"utendors_i_seks_ovelser": len(r), "utovere_utendors": int(r["athlete_id"].nunique())}
    r["event_code"] = r["event"].map(ev)
    r = r[(r["is_xc"] != "1") & (r["is_multi_sub"] != "1")]
    flyt["uten_mangekamp"] = len(r)
    r["y"] = pd.to_numeric(r["mark_numeric"], errors="coerce")
    r = r[(r["valid"] == "TRUE") & r["y"].notna()]
    flyt["med_merke"] = len(r)
    # elektronisk tid = hundredeler ("10.93"); 'h'-tider og tideler utelates (A6-regelen)
    hund = r["mark"].fillna("").str.fullmatch(r"\d{1,2}\.\d{2}")
    r = r[(r["hand"] != "TRUE") & (~r["event_code"].isin(TID) | hund)]
    flyt["elektronisk"] = len(r)
    r = r[r["flag_error"] != "TRUE"]
    flyt["uten_feilflagg"] = len(r)
    r["wind"] = pd.to_numeric(r["wind_num"], errors="coerce")
    r = r[r["wind"].notna()]
    flyt["med_vind"] = len(r)
    r = r[r["wind"].abs() <= 8]
    flyt["vind_innen_8"] = len(r)
    r = r[grenser_ok(r)]
    flyt["rimelig"] = len(r)
    r = r[r["gender"].isin(["M", "F"])]
    flyt["med_kjonn"] = len(r)
    r["runde"] = r["round"].map({"F": "finale", "P": "forsok"}).fillna("ukjent")
    r = r.drop_duplicates(["athlete_id", "event_code", "date", "meet_id", "runde", "mark", "wind"])
    flyt["uten_eksakte_dubletter"] = len(r)
    dt = pd.to_datetime(r["date"], errors="coerce")
    r = r[dt.notna()].copy()
    dt = dt[dt.notna()]
    r["aar"] = dt.dt.year.astype(int)
    r["maaned"] = dt.dt.month.astype(int)
    r["kilde"] = "TFRRS"
    flyt["utovere"] = int(r["athlete_id"].nunique())
    flyt["aar_fra"], flyt["aar_til"] = int(r["aar"].min()), int(r["aar"].max())
    logger.info(f"TFRRS flyt: {flyt}")
    return r[KOL].reset_index(drop=True), flyt


# ---------------------------------------------------------------- Tilastopaja (finalistenes karrierer)
def runde_tp(p):
    p = "" if pd.isna(p) else str(p)
    if p in ("", "-"):
        return "ukjent"
    for tegn, navn in [("h", "heat"), ("s", "semi"), ("q", "kval"), ("r", "runde")]:
        if tegn in p:
            return navn
    return "finale"


def les_tilastopaja():
    r = pd.read_csv(TP, dtype=str, low_memory=False)
    flyt = {"rader_alle_ovelser": len(r), "utovere_alle_ovelser": int(r["athlete_id"].nunique())}
    r = r[r["event"].isin(KODER)]
    flyt["seks_ovelser"] = len(r)
    r = r.drop_duplicates(["athlete_id", "event", "date", "raw", "cid"])
    flyt["uten_dubletter"] = len(r)
    r = r[r["indoor"] == "0"]
    flyt["utendors"] = len(r)
    r = r[~r["place"].isin(["D", "H"])]
    flyt["uten_mangekamp"] = len(r)
    r = r[(r["hand"] == "0") & (r["annulled"] == "0")]
    flyt["elektronisk_ikke_annullert"] = len(r)
    r["y"] = pd.to_numeric(r["value"], errors="coerce")
    r = r[r["y"].notna()]
    flyt["med_merke"] = len(r)
    r["wind"] = pd.to_numeric(r["wind"], errors="coerce")
    r = r[r["wind"].notna()]
    flyt["med_vind"] = len(r)
    r = r[r["wind"].abs() <= 8]
    flyt["vind_innen_8"] = len(r)
    r["event_code"] = r["event"]
    r = r[grenser_ok(r)]
    flyt["rimelig"] = len(r)
    dt = pd.to_datetime(r["date"], errors="coerce")
    r = r[dt.notna()].copy()
    dt = dt[dt.notna()]
    r["aar"] = dt.dt.year.astype(int)
    r["maaned"] = dt.dt.month.astype(int)
    r["runde"] = r["place"].map(runde_tp)
    har_cid = r["cid"].notna() & (r["cid"] != "")
    r["meet_id"] = r["cid"].where(har_cid, r["venue"].fillna("") + "_" + r["date"])
    r["gender"] = r["sex"].map({"M": "M", "W": "F"})
    r = r[r["gender"].notna()]
    flyt["med_kjonn"] = len(r)
    r["kilde"] = "Tilastopaja"
    flyt["utovere"] = int(r["athlete_id"].nunique())
    flyt["aar_fra"], flyt["aar_til"] = int(r["aar"].min()), int(r["aar"].max())
    flyt["andel_over_2"] = round(float((r["wind"] > 2).mean()), 4)
    logger.info(f"Tilastopaja flyt: {flyt}")
    return r[KOL].reset_index(drop=True), flyt


# ---------------------------------------------------------------- Norge (referanserader)
def les_norge():
    d = pd.read_csv(DATA / "analyseklar.csv", low_memory=False,
                    usecols=["event_code", "gender", "athlete_id", "aar", "maaned", "runde", "meet_id", "y",
                             "wind", "celle", "n_i_celle", "aldersband"])
    d = d[d["event_code"].isin(NORGE_KODE)].copy()
    d["event_code"] = d["event_code"].map(NORGE_KODE)
    # aldersbånd er konstant innen utøver x år, så 20-34-utvalget beholder hele celler
    return pd.concat([d.assign(kilde="Norge"), d[d["aldersband"] == "20-34"].assign(kilde="Norge_20_34")],
                     ignore_index=True)


# ---------------------------------------------------------------- estimering
def klargjor(r):
    r = r.copy()
    if "celle" not in r.columns:
        r["celle"] = r["athlete_id"].astype(str) + "_" + r["aar"].astype(str) + "_" + r["event_code"]
        r["n_i_celle"] = r.groupby("celle")["y"].transform("count")
    r["logy"] = np.log(r["y"])
    r["wind_pos"] = r["wind"].clip(lower=0)
    r["wind_neg"] = r["wind"].clip(upper=0)
    r["w02"] = r["wind"].clip(0, 2)
    r["w2p"] = (r["wind"] - 2).clip(lower=0)
    return r


def forhold_ki(res):
    """Motvind/medvind-forholdet med delta-metode-KI (som 07b_revisjon_r2.py)."""
    i, j = res["_navn"].index("wind_neg"), res["_navn"].index("wind_pos")
    bn, bp, V = res["wind_neg"][0], res["wind_pos"][0], res["_V"]
    R = bn / bp
    se = abs(R) * np.sqrt(V[i, i] / bn ** 2 + V[j, j] / bp ** 2 - 2 * V[i, j] / (bn * bp))
    return R, R - 1.96 * se, R + 1.96 * se


def drag_forhold(g, kode):
    """Drag-fysikk gjennom samme estimator ved utøversesongens egen fart (07_revisjon_r1.py): motvind/medvind-
    forholdet, og forholdet mellom medvindshelningen over +2 og over 0 til +2 i knekkmodellen."""
    g = g.copy()
    t = g.groupby("celle")["y"].transform("mean")
    v = DIST[kode] / t
    g["ysim"] = t * ((v - g["wind"]) ** 2 - v ** 2) / v ** 2
    r = m03.estimer(g, "ysim", vindkolonner=("wind_pos", "wind_neg"), cluster="meet_id")
    k = m03.estimer(g, "ysim", vindkolonner=("w02", "w2p", "wind_neg"), cluster="meet_id")
    return r["wind_neg"][0] / r["wind_pos"][0], k["w2p"][0] / k["w02"][0]


def rad(kilde, kode, kj, g, per_sek_rate):
    lin = m03.estimer(g, "y", cluster="meet_id")
    if not lin:
        return None
    s = -1 if kode in TID else 1
    sk = 1 if kode in TID else 100
    b, se = lin["wind"]
    snitt = float(g["y"].mean())          # alle analyserte rader, som i tabell S4
    gev = s * b * sk
    ut = {"kilde": kilde, "event": kode, "kjonn": kj, "enhet": "s" if kode in TID else "cm",
          "n_analysert": len(g), "n": lin["n"], "celler": lin["celler"],
          "utovere": int(g.loc[g["n_i_celle"] >= 2, "athlete_id"].nunique()),
          "stevner": int(g.loc[g["n_i_celle"] >= 2, "meet_id"].nunique()),
          "snitt": snitt, "gevinst_per_ms": gev, "ki_lav": gev - 1.96 * se * sk, "ki_hoy": gev + 1.96 * se * sk,
          "per_sekund": gev / snitt if kode in TID else np.nan,
          "andel_over_2": float((g.loc[g["n_i_celle"] >= 2, "wind"] > 2).mean())}
    p = m03.estimer(g, "logy", cluster="meet_id")
    bl, sel = p["wind"]
    lo, hi = sorted([s * 100 * (bl - 1.96 * sel), s * 100 * (bl + 1.96 * sel)])
    ut.update({"pst": s * 100 * bl, "pst_ki_lav": lo, "pst_ki_hoy": hi})
    a = m03.estimer(g, "y", vindkolonner=("wind_pos", "wind_neg"), cluster="meet_id")
    bp, sep = a["wind_pos"]
    bn, sen = a["wind_neg"]
    R, rlo, rhi = forhold_ki(a)
    i, j = a["_navn"].index("wind_pos"), a["_navn"].index("wind_neg")
    V = a["_V"]
    se_d = float(np.sqrt(V[i, i] + V[j, j] - 2 * V[i, j]))
    drag, drag_over2 = drag_forhold(g, kode) if kode in DIST else (np.nan, np.nan)
    ut.update({"medvind": s * bp * sk, "medvind_se": sep * sk, "motvind": s * bn * sk, "motvind_se": sen * sk,
               "ratio_obs": R, "ratio_ki_lav": rlo, "ratio_ki_hoy": rhi,
               "p_lik": float(2 * (1 - scst.norm.cdf(abs((bp - bn) / se_d)))), "ratio_drag": drag})
    k = m03.estimer(g, "y", vindkolonner=("w02", "w2p", "wind_neg"), cluster="meet_id")
    ut.update({"medvind_0_2": s * k["w02"][0] * sk, "medvind_0_2_se": k["w02"][1] * sk,
               "over_2": s * k["w2p"][0] * sk, "over_2_se": k["w2p"][1] * sk,
               "over_2_vs_0_2": k["w2p"][0] / k["w02"][0], "over_2_vs_0_2_drag": drag_over2})
    fe = m03.estimer(g, "y", meet_fe=True, cluster="meet_id")
    bf, sef = fe["wind"]
    ut.update({"stevne_fe": s * bf * sk, "stevne_fe_ki_lav": s * bf * sk - 1.96 * sef * sk,
               "stevne_fe_ki_hoy": s * bf * sk + 1.96 * sef * sk, "stevne_fe_n": fe["n"]})
    if kode == "100m":
        ut.update({"a6_lov_lav": per_sek_rate[0] * snitt, "a6_lov_hoy": per_sek_rate[1] * snitt,
                   "moinat_plus1": MOINAT_A * snitt + MOINAT_B + MOINAT_Q})
    ut["_beta"] = b
    return ut


def tertiler(r, beta):
    """TFRRS: tertiler av utøversesonger (celler >= 2) på vindjustert sesongsnitt innen øvelse x kjønn,
    som 07_revisjon_r1.py: rang med celle-id som tie-break, tertil = floor(3(rang-1)/m), m >= 30."""
    rader = []
    for (kode, kj), g in r.groupby(["event_code", "gender"]):
        if (kode, kj) not in beta:
            continue
        g = g.copy()
        g["y_adj"] = g["y"] - beta[(kode, kj)] * g["wind"]
        cel = g[g["n_i_celle"] >= 2].groupby("celle")["y_adj"].mean().rename("cm_adj").reset_index()
        cel["prest"] = -cel["cm_adj"] if kode in TID else cel["cm_adj"]
        cel = cel.sort_values(["prest", "celle"]).reset_index(drop=True)
        m = len(cel)
        if m < 30:
            continue
        cel["tert"] = np.array(["lav", "midt", "hoy"])[np.floor(3 * np.arange(m) / m).astype(int)]
        g["tert"] = g["celle"].map(cel.set_index("celle")["tert"])
        s = -1 if kode in TID else 1
        sk = 1 if kode in TID else 100
        for t, gg in g.groupby("tert"):
            res = m03.estimer(gg, "y", cluster="meet_id")
            if not res:
                continue
            b, se = res["wind"]
            gev = s * b * sk
            snitt = float(gg["y"].mean())
            rader.append({"kilde": "TFRRS", "event": kode, "kjonn": kj, "tertil": t, "n": res["n"],
                          "celler": res["celler"], "snitt": snitt, "gevinst_per_ms": gev,
                          "ki_lav": gev - 1.96 * se * sk, "ki_hoy": gev + 1.96 * se * sk,
                          "per_sekund": gev / snitt if kode in TID else np.nan})
    return pd.DataFrame(rader)


def robusthet(kilde, r):
    rader = []
    for (kode, kj), g in r.groupby(["event_code", "gender"]):
        s = -1 if kode in TID else 1
        sk = 1 if kode in TID else 100
        varianter = [("primaer", g, {}), ("celler_min3", g[g["n_i_celle"] >= 3], {}),
                     ("uten_vind_0", g[g["wind"] != 0], {}), ("kluster_utover", g, {"cluster": "athlete_id"})]
        if kilde == "TFRRS":
            # innsamlingens hull i korte karrierer 2015-17 (tfrrs_shared README): sesongene 2016-17 ut
            varianter.append(("uten_2016_2017", g[~g["aar"].isin([2016, 2017])], {}))
        for navn, gg, kw in varianter:
            gg = gg.copy()
            gg["n_i_celle"] = gg.groupby("celle")["y"].transform("count")
            res = m03.estimer(gg, "y", cluster=kw.get("cluster", "meet_id"))
            if res:
                b, se = res["wind"]
                gev = s * b * sk
                rader.append({"kilde": kilde, "event": kode, "kjonn": kj, "analyse": navn, "gevinst_per_ms": gev,
                              "ki_lav": gev - 1.96 * se * sk, "ki_hoy": gev + 1.96 * se * sk,
                              "n": res["n"], "celler": res["celler"]})
    return pd.DataFrame(rader)


def main():
    sjekk_hasher()
    ps = pd.read_csv(EST / "r1_per_sekund.csv").set_index("event")["per_sekund"]
    rate = (float(ps[["60m", "80m", "100m"]].min()), float(ps[["60m", "80m", "100m"]].max()))
    tf, flyt_tf = les_tfrrs()
    tp, flyt_tp = les_tilastopaja()
    pd.concat([tf, tp], ignore_index=True).to_csv(DATA / "eliteende_analyseklar.csv", index=False)
    (DATA / "eliteende_flyt.json").write_text(json.dumps({"TFRRS": flyt_tf, "Tilastopaja": flyt_tp}, indent=1))
    rader, beta_tf = [], {}
    for kilde, r in [("Norge", None), ("Norge_20_34", None), ("TFRRS", tf), ("Tilastopaja", tp)]:
        if r is None:
            no = les_norge()
            r = no[no["kilde"] == kilde]
        r = klargjor(r)
        for kode in KODER:
            for kj in ["M", "F"]:
                g = r[(r["event_code"] == kode) & (r["gender"] == kj)]
                if not len(g):
                    continue
                ut = rad(kilde, kode, kj, g, rate)
                if ut:
                    if kilde == "TFRRS":
                        beta_tf[(kode, kj)] = ut.pop("_beta")
                    else:
                        ut.pop("_beta")
                    rader.append(ut)
            logger.info(f"{kilde} {kode} ferdig")
        if kilde == "TFRRS":
            tertiler(r, beta_tf).to_csv(EST / "r3_eliteende_tertil.csv", index=False)
            rob = robusthet(kilde, r)
        elif kilde == "Tilastopaja":
            rob = pd.concat([rob, robusthet(kilde, r)], ignore_index=True)
    pd.DataFrame(rader).to_csv(EST / "r3_eliteende.csv", index=False)
    rob.to_csv(EST / "r3_eliteende_robusthet.csv", index=False)
    logger.info(f"ferdig; r3_eliteende*.csv i {EST}/")


if __name__ == "__main__":
    main()
