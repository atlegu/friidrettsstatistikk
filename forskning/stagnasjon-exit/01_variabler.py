"""
01_variabler.py — A1 «Stagnasjon før exit»: bygg analysedatasettet.

Leser det frosne uttrekket i data_private/ og bygger én rad per landmark-utøver
(>=1 OK-resultat ved 13-14 OG >=1 OK-resultat ved 15-16), med alle eksponerings-
varianter forhåndsberegnet slik at 03/04 er ren modellering. Se ANALYSEPLAN.md §4.

Vinduer (kalenderårsalder): W1 = 13-14, W2 = 15-16.
Primærutvalg: født 1998-2005 med skårbar Tyrving i hovedgruppen i begge vinduer.

Output:
  data_private/analysedata.csv   (utøvernivå; ikke i git)
  data_private/flyt.json         (flyttelling, aggregat)
"""

import json
import logging
import sys
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
DATA = HERE / "data_private"
sys.path.insert(0, str(HERE.parent))
from a1_tyrving import beregn_tyrving_poeng, parse_tyrving_xls  # noqa: E402
from rens_felles import fjern_kopier  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PRIMAER_KULL = (1998, 2005)


def modal(serie):
    """Hyppigste verdi med deterministisk tie-break (flest, deretter alfabetisk)."""
    s = serie.dropna()
    if s.empty:
        return None
    telling = s.value_counts()
    beste = telling[telling == telling.max()]
    return sorted(beste.index.astype(str))[0]


def mean3(poeng):
    """Snitt av de tre beste poengsummene (eller av dem som finnes)."""
    if not poeng:
        return np.nan
    return float(np.mean(sorted(poeng, reverse=True)[:3]))


def forventet_mean3(poeng, n):
    """Forventet snitt av tre beste i et tilfeldig utvalg på n av poengsummene (uten
    tilbakelegging), regnet eksakt: verdi nr. j i synkende rekkefølge teller med sannsynligheten
    for at den er i utvalget sammen med færre enn m = min(3, n) av de j høyere verdiene."""
    x = sorted(poeng, reverse=True)
    k, m = len(x), min(3, n)
    alle = comb(k, n)
    return sum(xj * sum(comb(j, i) * comb(k - 1 - j, n - 1 - i) for i in range(m)) / alle
               for j, xj in enumerate(x)) / m


def delta_like_mange(p1, p2):
    """Fremgang med like mange resultater i begge vinduer (audit 30.10.2026, funn A1-1).

    Snitt av tre beste stiger mekanisk med antall poengsatte resultater, og frafallere har
    færre resultater ved 15–16. Begge vinduer vurderes ved min(k13, k15) resultater uten
    tilbakelegging, som forventet snitt av tre beste over alle slike utvalg. Eksakt i stedet
    for snitt av 30 tilfeldige trekk: trekkstøyen ga 24,2 mot 25,5 % negativ fremgang blant
    seniorene i Python og R."""
    if not isinstance(p1, list) or not isinstance(p2, list):
        return np.nan
    n = min(len(p1), len(p2))
    return forventet_mean3(p2, n) - forventet_mean3(p1, n)


def main():
    utv = pd.read_csv(DATA / "utovere.csv")
    r = pd.read_csv(DATA / "resultater.csv", parse_dates=["date"], low_memory=False)
    flyt = {"utovere_fodt_1998_2006": len(utv)}
    r, kopier = fjern_kopier(r)   # sonetvillinger og eksakte dubletter (rens_felles.py)
    flyt["fjernet_sonetvilling_brettkode"] = kopier["sonetvilling"]
    flyt["fjernet_flerdagskopi_brettkode"] = kopier["flerdagskopi"]
    flyt["fjernet_eksakt_dublett"] = kopier["eksakt_dublett"]

    r = r.drop(columns=["birth_year"], errors="ignore")
    r = r.merge(utv.rename(columns={"id": "athlete_id"}), on="athlete_id", how="inner")
    r["alder"] = r["date"].dt.year - r["birth_year"]
    r["aar"] = r["date"].dt.year
    r = r[r["status"] == "OK"].copy()
    r["manuell"] = r["is_manual_time"].astype(str) == "True"

    ev = pd.read_csv(DATA / "events.csv")
    vindovelser = set(ev.loc[ev["wind_measured"].astype(str) == "True", "code"])
    me = pd.read_csv(DATA / "meets.csv")
    kl = pd.read_csv(DATA / "clubs.csv").rename(columns={"id": "club_id", "name": "club_name"})
    r = r.merge(me.rename(columns={"id": "meet_id"})[["meet_id", "krets", "indoor"]], on="meet_id", how="left")
    r["inne"] = r["indoor"].astype(str) == "True"

    # ---- Flyt: kvalifisering og landmark -------------------------------------------------
    har1314 = r.loc[r["alder"].isin([13, 14])].groupby("athlete_id").size()
    har1516 = r.loc[r["alder"].isin([15, 16])].groupby("athlete_id").size()
    flyt["ok_resultat_13_14"] = int(len(har1314))
    landmark_ids = set(har1314.index) & set(har1516.index)
    flyt["landmark_13_14_og_15_16"] = len(landmark_ids)

    base = utv[utv["id"].isin(landmark_ids)].rename(columns={"id": "athlete_id"}).copy()
    uten_kjonn = base["gender"].isna() | ~base["gender"].isin(["M", "F"])
    flyt["landmark_uten_kjonn"] = int(uten_kjonn.sum())
    base = base[~uten_kjonn]

    bd = pd.to_datetime(base["birth_date"], errors="coerce")
    base["kvartal"] = ((bd.dt.month - 1) // 3 + 1).astype("Int64")
    flyt["landmark_uten_fodselsdato"] = int(base["kvartal"].isna().sum())

    rl = r[r["athlete_id"].isin(set(base["athlete_id"]))].copy()
    w1 = rl[rl["alder"].isin([13, 14])]
    w2 = rl[rl["alder"].isin([15, 16])]

    # ---- Hovedøvelsesgruppe ved 13-14 ----------------------------------------------------
    hovedgruppe = w1.groupby("athlete_id")["event_category"].agg(modal)
    base["hovedgruppe"] = base["athlete_id"].map(hovedgruppe)

    # ---- Tyrving-skåring (elektronisk tid; alle merker + vindgyldig-variant) -------------
    tab = parse_tyrving_xls()
    sc = rl[rl["alder"].between(13, 16) & ~rl["manuell"]].copy()
    sc["tyrving"] = [
        beregn_tyrving_poeng(pv, kode, rt, kj, al, tab)
        for pv, kode, rt, kj, al in zip(sc["performance_value"], sc["event_code"],
                                        sc["result_type"], sc["gender"], sc["alder"])
    ]
    sc = sc[sc["tyrving"].notna()].copy()
    # vindlovlig: øvelsen måler ikke vind, merket er satt innendørs, eller lovlig vind er
    # registrert. Utendørs vindmerker uten vindmåling regnes ikke som lovlige (audit 30.10.2026;
    # før ble manglende is_wind_legal tolket som lovlig, 21 063 merker i primærutvalget).
    lovlig = ((sc["is_wind_legal"].astype(str) == "True")
              | (sc["is_wind_legal"].isna() & (sc["wind"] <= 2.0)))   # 171 rader har vind uten flagg
    sc["vindgyldig"] = ~sc["event_code"].isin(vindovelser) | sc["inne"] | lovlig

    def vindu_poeng(d, gruppe_map, aldre, kun_vindgyldig=False):
        """{athlete_id: liste med tyrvingpoeng i utøverens gruppe og aldersvindu}."""
        dd = d[d["alder"].isin(aldre)]
        if kun_vindgyldig:
            dd = dd[dd["vindgyldig"]]
        dd = dd[dd["event_category"] == dd["athlete_id"].map(gruppe_map)]
        return dd.groupby("athlete_id")["tyrving"].agg(list)

    g_hoved = base.set_index("athlete_id")["hovedgruppe"]
    p13, p14 = vindu_poeng(sc, g_hoved, [13]), vindu_poeng(sc, g_hoved, [14])
    p_w1, p_w2 = vindu_poeng(sc, g_hoved, [13, 14]), vindu_poeng(sc, g_hoved, [15, 16])
    p_w1v = vindu_poeng(sc, g_hoved, [13, 14], kun_vindgyldig=True)
    p_w2v = vindu_poeng(sc, g_hoved, [15, 16], kun_vindgyldig=True)

    # Beste gruppe ved 15-16 (sensitivitet for byttere): gruppen med høyest mean3 i W2
    w2sc = sc[sc["alder"].isin([15, 16])]
    bg = (w2sc.groupby(["athlete_id", "event_category"])["tyrving"]
          .agg(lambda s: mean3(list(s))).reset_index()
          .sort_values(["athlete_id", "tyrving", "event_category"], ascending=[True, False, True])
          .drop_duplicates("athlete_id").set_index("athlete_id"))
    p_w1bg = vindu_poeng(sc, bg["event_category"], [13, 14])
    p_w2bg = vindu_poeng(sc, bg["event_category"], [15, 16])

    def kol(serie, fn):
        return base["athlete_id"].map(serie).map(lambda x: fn(x) if isinstance(x, list) else np.nan)

    base["k13"] = kol(p_w1, len).fillna(0).astype(int)
    base["k15"] = kol(p_w2, len).fillna(0).astype(int)
    base["niva_w1"] = kol(p_w1, mean3)
    base["niva_w2"] = kol(p_w2, mean3)
    base["delta"] = base["niva_w2"] - base["niva_w1"]
    base["delta_max"] = kol(p_w2, max) - kol(p_w1, max)
    base["delta_all"] = kol(p_w2, np.mean) - kol(p_w1, np.mean)
    base["delta_vind"] = kol(p_w2v, mean3) - kol(p_w1v, mean3)
    base["delta_bg2"] = kol(p_w2bg, mean3) - kol(p_w1bg, mean3)
    # gruppekonsistent switcher-variant (Atles beslutning 30.10.2026): nivå og antall i samme
    # gruppe som fremgangen, ikke i hovedgruppen ved 13-14 (gruppene er ulike for ~1/3)
    base["bestgruppe"] = base["athlete_id"].map(bg["event_category"])
    base["niva_w1_bg"] = kol(p_w1bg, mean3)
    base["k13_bg"] = kol(p_w1bg, len).fillna(0).astype(int)
    base["k15_bg"] = kol(p_w2bg, len).fillna(0).astype(int)
    base["delta_nk_1314"] = kol(p14, mean3) - kol(p13, mean3)   # negativkontroll innen W1
    lik = {a: delta_like_mange(p_w1.get(a), p_w2.get(a)) for a in base["athlete_id"]}
    base["delta_lik"] = base["athlete_id"].map(lik)

    # ---- Volum: konkurransedager (alle OK-resultater, også manuelle/stafett) -------------
    for navn, aldre in [("vol1314", [13, 14]), ("vol1516", [15, 16])]:
        dager = rl[rl["alder"].isin(aldre)].groupby("athlete_id")["date"].nunique()
        base[navn] = base["athlete_id"].map(dager).fillna(0).astype(int)

    # ---- Utfall ---------------------------------------------------------------------------
    senior_res = rl[rl["alder"] >= 20]
    per_aar = senior_res.groupby(["athlete_id", "aar"]).size()
    min2 = per_aar[per_aar >= 2].reset_index()["athlete_id"].unique()
    base["senior"] = base["athlete_id"].isin(set(min2)).astype(int)
    base["senior_min1"] = base["athlete_id"].isin(set(senior_res["athlete_id"])).astype(int)
    base["aktiv18"] = base["athlete_id"].isin(set(rl.loc[rl["alder"] >= 18, "athlete_id"])).astype(int)
    v2021 = senior_res[senior_res["alder"].isin([20, 21])].groupby(["athlete_id", "aar"]).size()
    base["senior_20_21"] = base["athlete_id"].isin(
        set(v2021[v2021 >= 2].reset_index()["athlete_id"])).astype(int)
    siste = rl.groupby("athlete_id")["alder"].max()
    base["siste_alder"] = base["athlete_id"].map(siste)

    # ---- Struktur: region, klubb, klubbstørrelse (kohortproxy) ---------------------------
    base["region"] = base["athlete_id"].map(w1.groupby("athlete_id")["krets"].agg(modal))
    base["club_id"] = base["athlete_id"].map(w1.groupby("athlete_id")["club_id"].agg(modal))
    base = base.merge(kl, on="club_id", how="left")
    kstr = base.groupby("club_id")["athlete_id"].transform("count")
    base["klubbstorrelse"] = kstr
    base["log_klubbstorrelse"] = np.log1p(base["klubbstorrelse"])

    # ---- Kohorter og covid-flagg ----------------------------------------------------------
    base["kohort"] = np.where(base["birth_year"] <= 2001, "A", "B")
    base["kohort_primar"] = base["birth_year"].between(*PRIMAER_KULL)
    base["covid_w1"] = base["birth_year"].isin([2006, 2007])          # W1 berører 2020-21
    base["covid_w2"] = base["birth_year"].isin([2004, 2005, 2006])    # W2 berører 2020-21

    # ---- Primærutvalg og standardisering --------------------------------------------------
    base["skaarbar"] = (base["k13"] >= 1) & (base["k15"] >= 1)
    flyt["landmark_med_kjonn"] = len(base)
    # begge eksklusjonene telles blant primærkullene, så flyten (S1) summerer (audit 30.10.2026)
    flyt["landmark_fodt_1998_2005"] = int(base["kohort_primar"].sum())
    flyt["uten_skaarbar_tyrving_i_hovedgruppen"] = int((base["kohort_primar"] & ~base["skaarbar"]).sum())
    prim0 = base["kohort_primar"] & base["skaarbar"]
    celler = base.loc[prim0].groupby(["gender", "hovedgruppe"]).size()
    smaa = {k for k, v in celler.items() if v < 20}
    base["liten_gruppecelle"] = [(g, h) in smaa for g, h in
                                 zip(base["gender"], base["hovedgruppe"])]
    flyt["ekskludert_gruppecelle_under_20"] = int((prim0 & base["liten_gruppecelle"]).sum())
    prim = prim0 & ~base["liten_gruppecelle"]
    flyt["primaerutvalg_fodt_1998_2005"] = int(prim.sum())
    flyt["primaerutvalg_seniorer"] = int(base.loc[prim, "senior"].sum())

    ref = base[prim]
    for kolonne in ["delta", "delta_max", "delta_all", "delta_vind", "delta_bg2",
                    "delta_nk_1314", "delta_lik", "niva_w1", "vol1314", "vol1516"]:
        grp = ref.groupby(["gender", "hovedgruppe"])[kolonne]
        mu, sd = grp.transform("mean"), grp.transform("std")
        z = pd.Series(np.nan, index=base.index)
        z.loc[ref.index] = (ref[kolonne] - mu) / sd.replace(0, np.nan)
        # utenfor primærutvalget: standardiser mot primærutvalgets parametre per celle
        stats = ref.groupby(["gender", "hovedgruppe"])[kolonne].agg(["mean", "std"])
        andre = base.index.difference(ref.index)
        nokkel = list(zip(base.loc[andre, "gender"], base.loc[andre, "hovedgruppe"]))
        mu_a = [stats["mean"].get(k, np.nan) for k in nokkel]
        sd_a = [stats["std"].get(k, np.nan) for k in nokkel]
        z.loc[andre] = (base.loc[andre, kolonne].to_numpy() - np.array(mu_a)) / np.array(sd_a)
        base[kolonne + "_z"] = z

    base.to_csv(DATA / "analysedata.csv", index=False)
    with open(DATA / "flyt.json", "w") as f:
        json.dump(flyt, f, indent=2, ensure_ascii=False)
    logger.info(f"analysedata: {len(base)} landmark-utøvere, "
                f"{flyt['primaerutvalg_fodt_1998_2005']} i primærutvalget "
                f"({flyt['primaerutvalg_seniorer']} seniorer)")


if __name__ == "__main__":
    main()
