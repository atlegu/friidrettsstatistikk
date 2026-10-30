"""
06_revisjon_r1.py — A1: analyser til revisjon etter referee-runde 1.

Nytt (jf. manus/REFEREE_RUNDE1.md):
  R3-1: mediering — Δ-fordeling per fødselskvartal, og kvartalstrenden på
        retention med og uten Δ i modellen (attenuasjon).
  R1-2: rang/nivå-moderasjon — Δ x nivå-interaksjon + nivåtertil-strata.
  R1-5: kjønn — Δ x kvinne-interaksjon + kjønnsstrata.
  R2-2: DeLong-KI for parede AUC-differanser (M2-M1 og H3) på out-of-fold.
  R2-6c: fast vindu 20-21 per kohorthalvdel.
  R1-4/R3-5: SD-er i poeng/dager; andel med negativ Δ per utfall.
  R2-minor: kvintildummyer for Δ (formtest); switcher-flyt (inklusiv bg2).
  R3-minor: kvartilfordeling Q1-Q4; per-alders-n til figur 1.

Output: tables/modeller/r1_*.csv
"""

import importlib.util
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats as scst

HERE = Path(__file__).parent
DATA = HERE / "data_private"
TAB = HERE / "tables" / "modeller"

spec = importlib.util.spec_from_file_location("m03", HERE / "03_modeller.py")
m03 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m03)

_design0 = m03.design


def _design_safe(dd, kolonner):
    """Som 03s design, men dropper tomme/konstante dummykolonner (strata-sikkert)."""
    X = _design0(dd, kolonner)
    behold = [c for c in X.columns
              if c == "const" or ((X[c].abs() > 1e-12).any() and X[c].nunique() > 1)]
    return X[behold]


m03.design = _design_safe

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------- DeLong (paret AUC)
def _midrank(x):
    orden = np.argsort(x)
    rx = np.empty(len(x))
    i = 0
    xs = x[orden]
    while i < len(x):
        j = i
        while j < len(x) and xs[j] == xs[i]:
            j += 1
        rx[orden[i:j]] = 0.5 * (i + j - 1) + 1
        i = j
    return rx


def delong_diff(y, p_a, p_b):
    """DeLong-KI for AUC(a) - AUC(b) på samme utvalg (parede prediksjoner)."""
    y = np.asarray(y)
    pos, neg = y == 1, y == 0
    m, n = pos.sum(), neg.sum()
    aucs, v10, v01 = [], [], []
    for p in (p_a, p_b):
        p = np.asarray(p)
        r_alt = _midrank(p)
        r_pos = _midrank(p[pos])
        r_neg = _midrank(p[neg])
        auc = (r_alt[pos].sum() - m * (m + 1) / 2) / (m * n)
        aucs.append(auc)
        v10.append((r_alt[pos] - r_pos) / n)
        v01.append(1 - (r_alt[neg] - r_neg) / m)
    v10 = np.vstack(v10)
    v01 = np.vstack(v01)
    s10 = np.cov(v10)
    s01 = np.cov(v01)
    S = s10 / m + s01 / n
    diff = aucs[0] - aucs[1]
    var = S[0, 0] + S[1, 1] - 2 * S[0, 1]
    se = np.sqrt(max(var, 0))
    z = diff / se if se > 0 else np.nan
    p = 2 * (1 - scst.norm.cdf(abs(z))) if se > 0 else np.nan
    return aucs[0], aucs[1], diff, diff - 1.96 * se, diff + 1.96 * se, p


def main():
    TAB.mkdir(parents=True, exist_ok=True)
    d = m03.last_primaer()
    y = d["senior"].to_numpy()
    rader_or = []

    def legg(res_df, merk):
        r = res_df.copy()
        r.insert(0, "analyse", merk)
        rader_or.append(r)

    # ---- R2-2: DeLong på out-of-fold ---------------------------------------------------
    _, oof1 = m03.cv_auc(d, m03.M1_KOL)
    _, oof2 = m03.cv_auc(d, m03.M2_KOL)
    felles = ["gender", "vol1314_g", "vol1516_g", "k13", "k15"]
    _, oof_f = m03.cv_auc(d, felles + ["delta_z"])
    _, oof_n = m03.cv_auc(d, felles + ["niva_w1_z"])
    rader = []
    for navn, pa, pb in [("M2_minus_M1", oof2, oof1),
                         ("volum+fremgang_minus_volum+niva", oof_f, oof_n)]:
        a1, a2, diff, lo, hi, p = delong_diff(y, pa, pb)
        rader.append({"kontrast": navn, "auc_a": (a1), "auc_b": (a2),
                      "diff": (diff), "ki_lav": (lo),
                      "ki_hoy": (hi), "p": (float(p))})
        logger.info(f"DeLong {navn}: diff {diff:.4f} [{lo:.4f}, {hi:.4f}], p={p:.3f}")
    pd.DataFrame(rader).to_csv(TAB / "r1_delong.csv", index=False)

    # ---- R3-1: mediering ----------------------------------------------------------------
    dq = d.dropna(subset=["kvartal"]).copy()
    dq["kvartal_c"] = dq["kvartal"].astype(float) - 2.5
    ford = dq.groupby("kvartal").agg(n=("delta", "size"),
                                     delta_poeng_median=("delta", "median"),
                                     delta_poeng_snitt=("delta", "mean"),
                                     delta_z_snitt=("delta_z", "mean"))
    trend = sm.OLS(dq["delta_z"], sm.add_constant(dq["kvartal_c"])).fit(
        cov_type="cluster", cov_kwds={"groups": dq["club_id"].fillna("ukjent")})
    ford.to_csv(TAB / "r1_delta_per_kvartal.csv")
    uten = m03.logit_or(dq, m03.M1_KOL + ["kvartal_c"])[1]
    med = m03.logit_or(dq, m03.M2_KOL + ["kvartal_c"])[1]
    kv_u = uten[uten["variabel"] == "kvartal_c"].iloc[0]
    kv_m = med[med["variabel"] == "kvartal_c"].iloc[0]
    pd.DataFrame([
        {"modell": "uten_delta", "OR_per_kvartal": (kv_u["OR"]),
         "KI_lav": (kv_u["KI_lav"]), "KI_hoy": (kv_u["KI_hoy"]), "n": len(dq)},
        {"modell": "med_delta", "OR_per_kvartal": (kv_m["OR"]),
         "KI_lav": (kv_m["KI_lav"]), "KI_hoy": (kv_m["KI_hoy"]), "n": len(dq)},
        {"modell": "delta_z_paa_kvartal_c_OLS",
         "OR_per_kvartal": (float(trend.params["kvartal_c"])),
         "KI_lav": (float(trend.conf_int().loc["kvartal_c"][0])),
         "KI_hoy": (float(trend.conf_int().loc["kvartal_c"][1])), "n": len(dq)},
    ]).to_csv(TAB / "r1_mediering.csv", index=False)
    logger.info(f"kvartalstrend uten Δ: {kv_u['OR']:.3f} [{kv_u['KI_lav']:.3f},{kv_u['KI_hoy']:.3f}]; "
                f"med Δ: {kv_m['OR']:.3f} [{kv_m['KI_lav']:.3f},{kv_m['KI_hoy']:.3f}]; "
                f"Δz~kvartal: {trend.params['kvartal_c']:+.4f} per kvartal "
                f"(p={trend.pvalues['kvartal_c']:.3f})")

    # ---- R1-2: nivåmoderasjon -----------------------------------------------------------
    di = d.copy()
    di["delta_x_niva"] = di["delta_z"] * di["niva_w1_z"]
    _, ut = m03.logit_or(di, m03.M2_KOL + ["delta_x_niva"])
    legg(ut[ut["variabel"].isin(["delta_z", "delta_x_niva"])], "nivainteraksjon")
    di["nivatert"] = pd.qcut(di["niva_w1_z"], 3, labels=["lav", "midt", "hoy"])
    for t, g in di.groupby("nivatert", observed=True):
        _, u = m03.logit_or(g, m03.M2_KOL)
        legg(u[u["variabel"] == "delta_z"].assign(n=len(g), hendelser=int(g["senior"].sum())),
             f"nivastrata_{t}")

    # ---- R1-5: kjønn ---------------------------------------------------------------------
    di["kvinne"] = (di["gender"] == "F").astype(float)
    di["delta_x_kvinne"] = di["delta_z"] * di["kvinne"]
    _, ut = m03.logit_or(di, m03.M2_KOL + ["delta_x_kvinne"])
    legg(ut[ut["variabel"].isin(["delta_z", "delta_x_kvinne"])], "kjonnsinteraksjon")
    kol_uten_kjonn = [c for c in m03.M2_KOL if c != "gender"]
    for kj, g in di.groupby("gender"):
        _, u = m03.logit_or(g, kol_uten_kjonn)
        legg(u[u["variabel"] == "delta_z"].assign(n=len(g), hendelser=int(g["senior"].sum())),
             f"kjonnsstrata_{kj}")

    # ---- R2-minor: kvintildummyer for Δ --------------------------------------------------
    di["delta_kvint"] = pd.qcut(di["delta_z"].rank(method="first"), 5,
                                labels=["Q1", "Q2", "Q3", "Q4", "Q5"])
    dkv = pd.get_dummies(di["delta_kvint"], prefix="dq", drop_first=True, dtype=float)
    dd = pd.concat([di, dkv], axis=1)
    _, ut = m03.logit_or(dd, m03.M1_KOL + list(dkv.columns))
    legg(ut[ut["variabel"].str.startswith("dq_")], "delta_kvintiler_vs_Q1")

    # ---- R2-6c: fast vindu per kohorthalvdel ---------------------------------------------
    for k in ["A", "B"]:
        _, u = m03.logit_or(di[di["kohort"] == k], m03.M2_KOL, utfall="senior_20_21")
        legg(u[u["variabel"] == "delta_z"].assign(
            n=len(di[di["kohort"] == k]),
            hendelser=int(di.loc[di["kohort"] == k, "senior_20_21"].sum())),
            f"fast_vindu_kohort_{k}")

    pd.concat(rader_or).to_csv(TAB / "r1_moderasjon.csv", index=False)

    # ---- SD-er og negative Δ ----------------------------------------------------------
    base = pd.read_csv(DATA / "analysedata.csv")
    prim = base[base["kohort_primar"] & base["skaarbar"] & ~base["liten_gruppecelle"]]
    sd = {
        "sd_delta_poeng_pooled": (float(prim["delta"].std())),
        "sd_delta_poeng_cellespenn": f"{prim.groupby(['gender','hovedgruppe'])['delta'].std().min():.0f}"
                                     f"–{prim.groupby(['gender','hovedgruppe'])['delta'].std().max():.0f}",
        "sd_niva_poeng": (float(prim["niva_w1"].std())),
        "sd_vol1314_dager": (float(prim["vol1314"].std())),
        "sd_vol1516_dager": (float(prim["vol1516"].std())),
        "andel_negativ_delta_dropouts": (float((prim.loc[prim["senior"] == 0, "delta"] < 0).mean())),
        "andel_negativ_delta_retainers": (float((prim.loc[prim["senior"] == 1, "delta"] < 0).mean())),
        "kvartal_Q1": (float((prim["kvartal"] == 1).sum() / prim["kvartal"].notna().sum())),
        "kvartal_Q2": (float((prim["kvartal"] == 2).sum() / prim["kvartal"].notna().sum())),
        "kvartal_Q3": (float((prim["kvartal"] == 3).sum() / prim["kvartal"].notna().sum())),
        "kvartal_Q4": (float((prim["kvartal"] == 4).sum() / prim["kvartal"].notna().sum())),
        "primaer_uten_kvartal": int(prim["kvartal"].isna().sum()),
    }
    pd.DataFrame([sd]).T.rename(columns={0: "verdi"}).to_csv(TAB / "r1_sd_og_andeler.csv")
    logger.info(f"SD Δ (poeng): {sd['sd_delta_poeng_pooled']}; negativ Δ dropouts/retainers: "
                f"{sd['andel_negativ_delta_dropouts']}/{sd['andel_negativ_delta_retainers']}")

    # ---- Switcher-flyt: inklusiv bg2-variant ---------------------------------------------
    base["region"] = base["region"].fillna("ukjent")
    base["log_klubbstorrelse"] = base["log_klubbstorrelse"].fillna(base["log_klubbstorrelse"].median())
    for v in ["vol1314", "vol1516"]:
        mu, s = prim[v].mean(), prim[v].std()
        base[v + "_g"] = (base[v] - mu) / s
    inkl = base[base["kohort_primar"] & ~base["liten_gruppecelle"]
                & base["delta_bg2_z"].notna() & base["niva_w1_z"].notna()].copy()
    flyt = {
        "prim_med_bg2": int((prim["delta_bg2_z"].notna()).sum()),
        "prim_uten_bg2": int((prim["delta_bg2_z"].isna()).sum()),
        "ekskluderte_734_med_bg2": int(base[base["kohort_primar"] & ~base["skaarbar"]
                                            & base["delta_bg2_z"].notna()].shape[0]),
        "inklusiv_n": len(inkl),
        "inklusiv_hendelser": int(inkl["senior"].sum()),
        # av de 734 med bg2-skår: hvor mange som faktisk kommer i modellen (krever også nivå 13-14)
        "ekskluderte_734_i_modell": int((~inkl["skaarbar"]).sum()),
        "prim_i_modell": int(inkl["skaarbar"].sum()),
    }
    kol = [c for c in m03.M2_KOL if c != "delta_z"] + ["delta_bg2_z"]
    _, u = m03.logit_or(inkl, kol)
    t = u[u["variabel"] == "delta_bg2_z"].iloc[0]
    flyt["inklusiv_OR"] = (float(t["OR"]))
    flyt["inklusiv_KI"] = f"{t['KI_lav']:.3f}–{t['KI_hoy']:.3f}"
    flyt["inklusiv_KI_lav"] = float(t["KI_lav"])
    flyt["inklusiv_KI_hoy"] = float(t["KI_hoy"])
    pd.DataFrame([flyt]).T.rename(columns={0: "verdi"}).to_csv(TAB / "r1_switcher_flyt.csv")
    logger.info(f"inklusiv bg2: n={flyt['inklusiv_n']} (hvorav {flyt['ekskluderte_734_med_bg2']} "
                f"fra de 734), OR {flyt['inklusiv_OR']} [{flyt['inklusiv_KI']}]")

    # ---- Per-alders-n til figur 1 ---------------------------------------------------------
    spec5 = importlib.util.spec_from_file_location("m05", HERE / "05_figurer_tabeller.py")
    m05 = importlib.util.module_from_spec(spec5)
    spec5.loader.exec_module(m05)
    b2, sesong = m05.last_grunnlag()
    p2 = b2[b2["prim"]]
    s = sesong.merge(p2[["athlete_id", "senior"]], on="athlete_id", how="inner")
    s = s[s["tyrving_m3"].notna() & s["alder"].between(13, 18)]
    ns = s.groupby(["alder", "senior"])["athlete_id"].nunique().unstack()
    ns.columns = ["dropouts", "retainers"]
    ns.to_csv(TAB / "r1_fig1_n_per_alder.csv")

    logger.info(f"ferdig; r1-tabeller i {TAB}/")


if __name__ == "__main__":
    main()
