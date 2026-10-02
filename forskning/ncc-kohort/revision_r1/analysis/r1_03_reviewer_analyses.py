"""
r1_03_reviewer_analyses.py — New analyses for the IJSSC revision (SPO-26-1604.R1),
reviewer comments 1-14. Uses the corrected variables from r1_01_build_variables.py:
HHI from ages 13-14 only (comment 1) and corrected Tyrving scoring (comment 4).

Outputs: revision_r1/tables/*.csv, revision_r1/figures/figS5_event_study.png,
         revision_r1/tables/r1_results.json (every number quoted in the revised text)
"""

import json
import logging
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import statsmodels.api as sm  # noqa: E402
from lifelines import CoxPHFitter  # noqa: E402
from scipy import stats  # noqa: E402
from sklearn.experimental import enable_iterative_imputer  # noqa: E402,F401
from sklearn.impute import IterativeImputer  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold  # noqa: E402
from sklearn.pipeline import make_pipeline  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

HERE = Path(__file__).parent
R1 = HERE.parent
DATA = Path("/Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/Statistikk/forskning/ncc-kohort/data")
TAB, FIG, PRIV = R1 / "tables", R1 / "figures", R1 / "data_private"
TAB.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
SEED, REPEATS, B = 20261001, 20, 2000
RES = {}

L4 = ["female", "tyr_z", "hhi_z", "vol_z"]


# ----------------------------------------------------------------------------- data
def z(s):
    return (s - s.mean()) / s.std()


def load():
    df = pd.read_csv(DATA / "analysedata_utvidet.csv", low_memory=False)
    df = df.merge(pd.read_csv(PRIV / "r1_variables.csv"), on="athlete_id", how="left")
    df["female"] = df["gender"].map({"M": 0, "F": 1})
    df["cohort"] = np.where(df["birth_year"] <= 2000, "A", "B")
    df["tyr"], df["hhi"], df["vol"] = df["tyrving_best_r1"], df["hhi_13_14"], df["vol_pre_milepael"]
    df["tyr_sub"], df["hhi_sub"] = df["tyrving_best"], df["hhi_early"]           # as submitted
    df["tyr_d1314"] = df["tyrving_age_14_r1"] - df["tyrving_age_13_r1"]
    for c in ["tyr", "hhi", "vol", "tyr_sub", "hhi_sub", "tyr_d1314", "klubb_storrelse"]:
        df[c + "_z"] = z(df[c])
    kar = pd.read_csv(DATA / "karrieredata_utvidet.csv", low_memory=False,
                      usecols=["athlete_id", "date", "meet_id", "event_category"])
    kar["year"] = pd.to_datetime(kar["date"], errors="coerce").dt.year
    kar = kar.merge(df[["athlete_id", "birth_year"]], on="athlete_id", how="inner")
    kar["age"] = kar["year"] - kar["birth_year"]
    return df, kar


# ----------------------------------------------------------------------------- helpers
def logit(d, cov, y="aktiv_senior"):
    dd = d[cov + [y]].dropna()
    return sm.Logit(dd[y], sm.add_constant(dd[cov])).fit(disp=0), dd


def orci(m, t):
    ci = m.conf_int().loc[t]
    return float(np.exp(m.params[t])), float(np.exp(ci[0])), float(np.exp(ci[1])), float(m.pvalues[t])


def fmt(o):
    return f"{o[0]:.2f} [{o[1]:.2f}, {o[2]:.2f}]"


def pfmt(p):
    return "< .001" if p < .001 else f"{p:.3f}".lstrip("0")


def model():
    return make_pipeline(StandardScaler(), LogisticRegression(penalty=None, max_iter=5000))


def cv_run(X, y, splitter, groups=None, scale_in_fold=True):
    """Fold-mean AUC (as reported in the submission) + pooled out-of-fold predictions."""
    p, aucs = np.zeros(len(y)), []
    for tr, te in splitter.split(X, y, groups):
        m = model() if scale_in_fold else LogisticRegression(penalty=None, max_iter=5000)
        m.fit(X[tr], y[tr])
        p[te] = m.predict_proba(X[te])[:, 1]
        aucs.append(roc_auc_score(y[te], p[te]))
    return float(np.mean(aucs)), p


def calib(y, p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    lp = np.log(p / (1 - p))
    slope = float(sm.Logit(y, sm.add_constant(lp)).fit(disp=0).params[1])
    citl = float(sm.GLM(y, np.ones((len(y), 1)), family=sm.families.Binomial(), offset=lp).fit().params[0])
    return slope, citl, float(np.mean((p - y) ** 2))


def nb_ci(values, test_over_train=0.25):
    """Mean and 95% CI over repeated k-fold CV estimates, with the Nadeau & Bengio (2003)
    corrected resampled t (variance inflated by n_test/n_train for overlapping training sets)."""
    v = np.asarray(values, dtype=float)
    J, m, var = len(v), float(v.mean()), float(v.var(ddof=1))
    se = np.sqrt((1 / J + test_over_train) * var)
    t = stats.t.ppf(0.975, J - 1)
    p = float(2 * stats.t.sf(abs(m) / se, J - 1)) if se > 0 else np.nan
    return m, m - t * se, m + t * se, p


def splitter(r, groups):
    return (StratifiedGroupKFold(5, shuffle=True, random_state=SEED + r) if groups is not None
            else StratifiedKFold(5, shuffle=True, random_state=SEED + r))


def repeated_cv(X, y, groups=None, R=REPEATS):
    """R repeats of 5-fold CV (stratified, or stratified-grouped by club when groups are given).
    AUC = mean of the R x 5 fold-level AUCs (as in the submission) with a corrected-t 95% CI;
    calibration from the out-of-fold predictions averaged over repeats."""
    fold_aucs, P = [], np.zeros((R, len(y)))
    for r in range(R):
        for tr, te in splitter(r, groups).split(X, y, groups):
            m = model().fit(X[tr], y[tr])
            P[r, te] = m.predict_proba(X[te])[:, 1]
            fold_aucs.append(roc_auc_score(y[te], P[r, te]))
    rep_means = np.array(fold_aucs).reshape(R, 5).mean(axis=1)
    mean, lo, hi, _ = nb_ci(fold_aucs)
    pbar = P.mean(axis=0)
    slope, citl, brier = calib(y, pbar)
    return dict(auc=mean, auc_lo=lo, auc_hi=hi, auc_min=float(rep_means.min()), auc_max=float(rep_means.max()),
                slope=slope, citl=citl, brier=brier, n=len(y)), pbar


# ----------------------------------------------------------------------------- comment 1: primary model
def primary(df):
    logger.info("=== Primary L1-L4 (corrected variables) ===")
    d = df[["aktiv_senior"] + L4].dropna()
    y = d["aktiv_senior"].values
    rows, oofs = [], {}
    for name, cov in [("L1: Sex", ["female"]), ("L2: + Performance (Tyrving)", ["female", "tyr_z"]),
                      ("L3: + Event concentration (HHI, ages 13-14)", ["female", "tyr_z", "hhi_z"]),
                      ("L4: + Pre-milestone volume", L4)]:
        m, _ = logit(d, cov)
        cvr, p = repeated_cv(d[cov].values, y)
        oofs[name[:2]] = p
        for t in cov:
            o = orci(m, t)
            rows.append({"Model": name, "Covariate": t, "OR": round(o[0], 2), "95% CI": f"[{o[1]:.2f}, {o[2]:.2f}]",
                         "p": pfmt(o[3]), "CV-AUC (5-fold x 20)": f"{cvr['auc']:.3f}",
                         "CV-AUC 95% CI": f"[{cvr['auc_lo']:.3f}, {cvr['auc_hi']:.3f}]",
                         "McFadden pseudo-R2": round(float(m.prsquared), 3), "n": len(d)})
        RES[f"primary_{name[:2]}"] = dict(cv=cvr, r2=float(m.prsquared), **{t: orci(m, t) for t in cov})
        logger.info(f"  {name}: AUC={cvr['auc']:.3f} [{cvr['auc_lo']:.3f},{cvr['auc_hi']:.3f}]")
    pd.DataFrame(rows).to_csv(TAB / "table3_primary_r1.csv", index=False)
    RES["primary_n"] = len(d)
    return d, oofs


# ----------------------------------------------------------------------------- comments 2-3: CV procedure
def cv_procedures(df):
    logger.info("=== CV procedures (comments 2-3) ===")
    rows = []
    # (a/b) submitted variables, global z vs in-fold standardisation, seed 42 as submitted
    sub = df[["aktiv_senior", "female", "tyr_sub_z", "hhi_sub_z", "vol_z"]].dropna()
    Xs, ys = sub[["female", "tyr_sub_z", "hhi_sub_z", "vol_z"]].values, sub["aktiv_senior"].values
    for lab, inf in [("Submitted variables; standardised on full data before CV (as submitted)", False),
                     ("Submitted variables; standardised within training folds", True)]:
        a, p = cv_run(Xs, ys, StratifiedKFold(5, shuffle=True, random_state=42), scale_in_fold=inf)
        s, c, b = calib(ys, p)
        rows.append({"Procedure": lab, "n": len(ys), "CV-AUC": f"{a:.3f}", "Calibration slope": f"{s:.2f}",
                     "Calibration-in-the-large": f"{c:.2f}", "Brier": f"{b:.3f}"})
        RES[f"cvproc_{'infold' if inf else 'global'}_submitted"] = dict(auc=a, slope=s, citl=c, brier=b)
    # (c) corrected variables, athlete-level, repeated; (d) club-grouped, repeated
    d = df[["aktiv_senior", "klubb"] + L4].dropna()
    X, y = d[L4].values, d["aktiv_senior"].values
    groups = pd.factorize(d["klubb"])[0]
    for lab, g in [("R1 variables; athlete-level stratified 5-fold, 20 repeats", None),
                   ("R1 variables; club-grouped stratified 5-fold, 20 repeats", groups)]:
        r, _ = repeated_cv(X, y, g)
        rows.append({"Procedure": lab, "n": len(y),
                     "CV-AUC": f"{r['auc']:.3f} [{r['auc_lo']:.3f}, {r['auc_hi']:.3f}]; repeat range {r['auc_min']:.3f}-{r['auc_max']:.3f}",
                     "Calibration slope": f"{r['slope']:.2f}", "Calibration-in-the-large": f"{r['citl']:.2f}",
                     "Brier": f"{r['brier']:.3f}"})
        RES[f"cvproc_{'club' if g is not None else 'athlete'}"] = r
        logger.info(f"  {lab}: {r}")
    RES["n_clubs"] = int(d["klubb"].nunique())
    RES["club_size_max"] = int(d["klubb"].value_counts().max())
    pd.DataFrame(rows).to_csv(TAB / "tableS26_cv_procedures.csv", index=False)


# ----------------------------------------------------------------------------- comment 10: AUC differences
def auc_differences(df):
    logger.info("=== Paired AUC differences (comment 10) ===")
    comps = [
        ("Sex + Tyrving vs. sex", ["female"], ["female", "tyr_z"], None),
        ("+ HHI vs. sex + Tyrving", ["female", "tyr_z"], ["female", "tyr_z", "hhi_z"], None),
        ("+ volume vs. sex + Tyrving + HHI (L4 vs. L3)", ["female", "tyr_z", "hhi_z"], L4, None),
        ("Sex + volume vs. sex + Tyrving (time-aligned)", ["female", "tyr_z"], ["female", "vol_z"], None),
        ("Sex + Tyrving + volume vs. sex + volume", ["female", "vol_z"], ["female", "tyr_z", "vol_z"], None),
        ("Full L4 vs. sex + volume", ["female", "vol_z"], L4, None),
        ("Sex + volume vs. sex + Tyrving + Tyrving change 13-14", ["female", "tyr_z", "tyr_d1314_z"],
         ["female", "vol_z"], ["tyr_d1314_z"]),
    ]
    rows = []
    for lab, ca, cb, extra in comps:
        need = sorted(set(ca + cb + (extra or []) + ["aktiv_senior"]))
        d = df[need].dropna()
        y, Xa, Xb = d["aktiv_senior"].values, d[ca].values, d[cb].values
        aa, ab = [], []
        for r in range(REPEATS):                                   # identical folds for A and B
            for tr, te in splitter(r, None).split(Xa, y):
                pa = model().fit(Xa[tr], y[tr]).predict_proba(Xa[te])[:, 1]
                pb = model().fit(Xb[tr], y[tr]).predict_proba(Xb[te])[:, 1]
                aa.append(roc_auc_score(y[te], pa))
                ab.append(roc_auc_score(y[te], pb))
        diff, lo, hi, pval = nb_ci(np.array(ab) - np.array(aa))
        rows.append({"Comparison (B vs. A)": lab, "n": len(y), "CV-AUC A": f"{np.mean(aa):.3f}",
                     "CV-AUC B": f"{np.mean(ab):.3f}", "Difference (B - A)": f"{diff:+.3f}",
                     "95% CI": f"[{lo:+.3f}, {hi:+.3f}]", "p": pfmt(pval)})
        RES[f"dauc::{lab}"] = dict(n=len(y), auc_a=float(np.mean(aa)), auc_b=float(np.mean(ab)), diff=diff,
                                    lo=lo, hi=hi, p=pval)
        logger.info(f"  {lab}: {np.mean(aa):.3f} -> {np.mean(ab):.3f}, diff {diff:+.3f} [{lo:+.3f},{hi:+.3f}], p={pval:.4f}")
    pd.DataFrame(rows).to_csv(TAB / "tableS27_auc_differences.csv", index=False)


# ----------------------------------------------------------------------------- comment 4: missing data / MI
def rubin(b, se):
    b, se = np.asarray(b), np.asarray(se)
    qbar, ubar, bvar = b.mean(), (se ** 2).mean(), b.var(ddof=1)
    return qbar, np.sqrt(ubar + (1 + 1 / len(b)) * bvar)


def mi_estimates(d, feats, impute_cols, covars, aux=None, m=20):
    out = {c: ([], []) for c in covars}
    use = feats + (aux or [])
    for i in range(m):
        imp = IterativeImputer(random_state=i, max_iter=15, sample_posterior=True)
        arr = pd.DataFrame(imp.fit_transform(d[use]), columns=use, index=d.index)
        di = d.copy()
        for c in impute_cols:
            di[c] = arr[c]
        for c in impute_cols + ["vol"]:
            di[c + "_z"] = z(di[c])
        mm, _ = logit(di, covars)
        for c in covars:
            out[c][0].append(mm.params[c])
            out[c][1].append(mm.bse[c])
    res = {}
    for c in covars:
        q, t = rubin(*out[c])
        res[c] = (float(np.exp(q)), float(np.exp(q - 1.96 * t)), float(np.exp(q + 1.96 * t)))
    return res


def mi_prediction(d, feats, covars_raw, m=20):
    """Imputation inside each training fold (outcome excluded), 5-fold CV per imputation."""
    y = d["aktiv_senior"].values
    X = d[feats].values
    aucs, slopes, citls, briers = [], [], [], []
    for i in range(m):
        sp = StratifiedKFold(5, shuffle=True, random_state=SEED + i)
        p, fa = np.zeros(len(y)), []
        for tr, te in sp.split(X, y):
            imp = IterativeImputer(random_state=i, max_iter=15, sample_posterior=True).fit(X[tr])
            Xtr, Xte = imp.transform(X[tr]), imp.transform(X[te])
            mdl = model().fit(Xtr, y[tr])
            p[te] = mdl.predict_proba(Xte)[:, 1]
            fa.append(roc_auc_score(y[te], p[te]))
        aucs.append(np.mean(fa))
        s, c, b = calib(y, p)
        slopes.append(s)
        citls.append(c)
        briers.append(b)
    return dict(auc=float(np.mean(aucs)), auc_min=float(np.min(aucs)), auc_max=float(np.max(aucs)),
                slope=float(np.mean(slopes)), citl=float(np.mean(citls)), brier=float(np.mean(briers)), n=len(y))


def missing_data(df):
    logger.info("=== Missing data and MI (comment 4) ===")
    known = df[df["female"].notna()].copy()
    RES["miss"] = dict(
        tyr_sub_missing_all=int(df["tyr_sub"].isna().sum()), tyr_sub_missing_sexknown=int(known["tyr_sub"].isna().sum()),
        tyr_r1_missing_all=int(df["tyr"].isna().sum()), tyr_r1_missing_sexknown=int(known["tyr"].isna().sum()),
        hhi_missing=int(df["hhi"].isna().sum()), vol_missing=int(df["vol"].isna().sum()),
        outcome_missing=int(df["aktiv_senior"].isna().sum()), sex_unknown=int(df["female"].isna().sum()))
    rows = []
    feats = ["aktiv_senior", "female", "tyr", "hhi", "vol"]
    cc, _ = logit(known, L4)
    rows.append({"Data / model": "R1 scoring: complete case (primary)", "n": int(cc.nobs),
                 "Volume OR": fmt(orci(cc, "vol_z")), "HHI OR": fmt(orci(cc, "hhi_z")),
                 "Tyrving OR": fmt(orci(cc, "tyr_z")), "CV-AUC": f"{RES['primary_L4']['cv']['auc']:.3f}"})
    mi = mi_estimates(known, feats, ["tyr"], L4)
    rows.append({"Data / model": "R1 scoring: multiple imputation (m = 20)", "n": len(known),
                 "Volume OR": fmt(mi["vol_z"]), "HHI OR": fmt(mi["hhi_z"]), "Tyrving OR": fmt(mi["tyr_z"]), "CV-AUC": ""})
    # submitted scoring (19% missing Tyrving): MI estimation + predictive performance
    s = known.copy()
    s["tyr"] = s["tyr_sub"]
    s["tyr_z"] = z(s["tyr"])
    cc2, _ = logit(s, L4)
    cv2, _ = repeated_cv(s[L4].dropna().values, s[L4 + ["aktiv_senior"]].dropna()["aktiv_senior"].values)
    rows.append({"Data / model": "Submitted scoring: complete case", "n": int(cc2.nobs),
                 "Volume OR": fmt(orci(cc2, "vol_z")), "HHI OR": fmt(orci(cc2, "hhi_z")),
                 "Tyrving OR": fmt(orci(cc2, "tyr_z")), "CV-AUC": f"{cv2['auc']:.3f}"})
    mi2 = mi_estimates(s, feats, ["tyr"], L4)
    pr2 = mi_prediction(s, ["female", "tyr", "hhi", "vol"], L4)
    rows.append({"Data / model": "Submitted scoring: MI (m = 20), outcome in imputation model", "n": len(s),
                 "Volume OR": fmt(mi2["vol_z"]), "HHI OR": fmt(mi2["hhi_z"]), "Tyrving OR": fmt(mi2["tyr_z"]),
                 "CV-AUC": f"{pr2['auc']:.3f} ({pr2['auc_min']:.3f}-{pr2['auc_max']:.3f})"})
    # auxiliary-variable imputation model
    s2 = s.copy()
    s2["region_e"] = (s2["region"] == "Østlandet").astype(int)
    s2["region_m"] = (s2["region"] == "Midt-Norge").astype(int)
    s2["cohort_b"] = (s2["cohort"] == "B").astype(int)
    cats = pd.get_dummies(s2["primaer_kategori_baseline"], prefix="cat", drop_first=True).astype(int)
    s2 = pd.concat([s2, cats], axis=1)
    aux = ["region_e", "region_m", "cohort_b", "klubb_storrelse", "res_13_14"] + list(cats.columns)
    mi3 = mi_estimates(s2, feats, ["tyr"], L4, aux=aux)
    rows.append({"Data / model": "Submitted scoring: MI with auxiliary variables (baseline event category, region, cohort, club size, result count)",
                 "n": len(s2), "Volume OR": fmt(mi3["vol_z"]), "HHI OR": fmt(mi3["hhi_z"]),
                 "Tyrving OR": fmt(mi3["tyr_z"]), "CV-AUC": ""})
    RES["mi"] = dict(r1=mi, submitted=mi2, submitted_aux=mi3, submitted_pred=pr2, submitted_cc_auc=cv2["auc"],
                     submitted_cc_n=int(cc2.nobs))
    pd.DataFrame(rows).to_csv(TAB / "tableS21_missing_data_r1.csv", index=False)
    logger.info(pd.DataFrame(rows).to_string(index=False))


# ----------------------------------------------------------------------------- comment 5: unknown sex
def unknown_sex(df):
    logger.info("=== Unknown sex (comment 5) ===")
    u = df[df["female"].isna()]
    RES["sex_unknown"] = dict(n=len(u), senior=float(u["aktiv_senior"].mean()), vol_median=float(u["vol"].median()),
                              tyr_scored=int(u["tyr"].notna().sum()))
    d = df.copy()
    d["sex_unknown"] = d["female"].isna().astype(int)
    d["female3"] = d["female"].fillna(0)
    m1, d1 = logit(d[d["sex_unknown"] == 0], ["female", "hhi_z", "vol_z"])
    m2, d2 = logit(d, ["female3", "sex_unknown", "hhi_z", "vol_z"])
    RES["sex_unknown"].update(vol_or_known=orci(m1, "vol_z"), n_known=len(d1),
                              vol_or_all=orci(m2, "vol_z"), n_all=len(d2), unknown_or=orci(m2, "sex_unknown"))
    logger.info(f"  {RES['sex_unknown']}")


# ----------------------------------------------------------------------------- comment 6: birth quarter
def birth_quarter(df):
    logger.info("=== Birth quarter coding (comment 6) ===")
    d = df[df["female"].notna() & df["tyr"].notna()].copy()
    q = d["fodt_kvartal"]
    d["q1"], d["q2"], d["q3"], d["q4"] = [(q == f"Q{i}").astype(int) for i in (1, 2, 3, 4)]
    d["q_missing"] = q.isna().astype(int)
    d["reg_e"] = (d["region"] == "Østlandet").astype(int)
    d["reg_m"] = (d["region"] == "Midt-Norge").astype(int)
    base = L4 + ["reg_e", "reg_m", "klubb_storrelse_z"]
    rows = []
    RES["bq_counts"] = df["fodt_kvartal"].value_counts(dropna=False).to_dict()
    RES["bq_missing"] = dict(n=int(df["fodt_kvartal"].isna().sum()), senior=float(df.loc[df["fodt_kvartal"].isna(), "aktiv_senior"].mean()),
                             vol_median=float(df.loc[df["fodt_kvartal"].isna(), "vol"].median()))
    dk = d[d["q_missing"] == 0].copy()
    dk["q_lin"] = dk["fodt_kvartal"].str[1].astype(int)
    specs = [("As submitted: Q1 and Q4 indicators vs. Q2-Q3 (unknown quarter coded to the reference)", d, ["q1", "q4"]),
             ("Q1 and Q4 indicators vs. Q2-Q3, known quarter only", dk, ["q1", "q4"]),
             ("Full coding: Q2, Q3, Q4 vs. Q1, known quarter only", dk, ["q2", "q3", "q4"]),
             ("Linear trend across quarters 1-4, known quarter only", dk, ["q_lin"])]
    for lab, data, qs in specs:
        m0, _ = logit(data, base)
        m, dd = logit(data, base + qs)
        lr = 2 * (m.llf - m0.llf)
        p_lr = float(stats.chi2.sf(lr, len(qs)))
        for t in qs + ["vol_z"]:
            o = orci(m, t)
            rows.append({"Specification": lab, "Covariate": t, "OR": round(o[0], 2), "95% CI": f"[{o[1]:.2f}, {o[2]:.2f}]",
                         "p": pfmt(o[3]), "LR test of quarter terms": f"chi2({len(qs)}) = {lr:.2f}, p = {p_lr:.2f}",
                         "n": len(dd)})
        RES[f"bq::{lab}"] = dict(vol=orci(m, "vol_z"), lr=float(lr), df=len(qs), p=p_lr,
                                 **{q: orci(m, q) for q in qs}, n=len(dd))
    pd.DataFrame(rows).to_csv(TAB / "tableS13b_birth_quarter.csv", index=False)
    logger.info(pd.DataFrame(rows).to_string(index=False))


# ----------------------------------------------------------------------------- comment 7: change scores
def change_models(df):
    logger.info("=== Level and change models (comment 7) ===")
    rows = []
    a14 = df[(df["res_age_14"] >= 1) & df["female"].notna() & df["tyr"].notna()].copy()
    a14["d1415"] = a14["vol_age_15"] - a14["vol_age_14"]           # later minus earlier: positive = increase
    sd14, sdd = a14["vol_age_14"].std(), a14["d1415"].std()
    a14["v14_z"], a14["d1415_z"], a14["tyr_zs"] = z(a14["vol_age_14"]), z(a14["d1415"]), z(a14["tyr"])
    y = a14["aktiv_senior"].values
    m1, _ = logit(a14, ["female", "tyr_zs", "v14_z"])
    m2, _ = logit(a14, ["female", "tyr_zs", "v14_z", "d1415_z"])
    cv1, _ = repeated_cv(a14[["female", "tyr_zs", "v14_z"]].values, y)
    cv2, _ = repeated_cv(a14[["female", "tyr_zs", "v14_z", "d1415_z"]].values, y)
    for name, m, cv in [("M1: level at 14", m1, cv1), ("M2: level at 14 + change 14->15", m2, cv2)]:
        for t in m.params.index[1:]:
            o = orci(m, t)
            rows.append({"Sample": f"Active at 14 (>=1 result), n = {int(m.nobs)}", "Model": name, "Covariate": t,
                         "OR per SD": fmt(o), "p": pfmt(o[3]), "McFadden pseudo-R2": round(float(m.prsquared), 3),
                         "CV-AUC": f"{cv['auc']:.3f}"})
    oc = orci(m2, "d1415_z")
    b = m2.params["d1415_z"] / sdd                                     # per meet
    RES["t4"] = dict(n=int(m2.nobs), sd_vol14=float(sd14), sd_change=float(sdd), mean_change=float(a14["d1415"].mean()),
                     level=orci(m2, "v14_z"), change=oc, change_decline_or=(1 / oc[0], 1 / oc[2], 1 / oc[1]),
                     change_per5_increase=float(np.exp(5 * b)), change_per5_decline=float(np.exp(-5 * b)),
                     r2_m1=float(m1.prsquared), r2_m2=float(m2.prsquared), auc_m1=cv1["auc"], auc_m2=cv2["auc"],
                     m1_level=orci(m1, "v14_z"))
    # equivalent level parameterisation: logit = a + b1*vol14 + b2*(vol15 - vol14) = a + (b1-b2)*vol14 + b2*vol15
    lv, _ = logit(a14.assign(v14=a14["vol_age_14"], v15=a14["vol_age_15"]), ["female", "tyr_zs", "v14", "v15"])
    RES["t4"]["levels_param_v15_per_meet"] = float(np.exp(lv.params["v15"]))
    RES["t4"]["change_param_per_meet"] = float(np.exp(b))
    # contamination-free change model, active at 16 (>=2 results at 16)
    a16 = df[(df["res_age_16"] >= 2) & df["female"].notna()].copy()
    a16["d1516"] = a16["vol_age_16"] - a16["vol_age_15"]
    sd16 = a16["d1516"].std()
    a16["v15_z"], a16["d1516_z"] = z(a16["vol_age_15"]), z(a16["d1516"])
    m3, _ = logit(a16, ["female", "v15_z", "d1516_z"])
    cv3, _ = repeated_cv(a16[["female", "v15_z", "d1516_z"]].values, a16["aktiv_senior"].values)
    for t in m3.params.index[1:]:
        o = orci(m3, t)
        rows.append({"Sample": f"Active at 16 (>=2 results), n = {int(m3.nobs)}", "Model": "Level at 15 + change 15->16",
                     "Covariate": t, "OR per SD": fmt(o), "p": pfmt(o[3]),
                     "McFadden pseudo-R2": round(float(m3.prsquared), 3), "CV-AUC": f"{cv3['auc']:.3f}"})
    o3 = orci(m3, "d1516_z")
    b3 = m3.params["d1516_z"] / sd16
    RES["s19"] = dict(n=int(m3.nobs), level=orci(m3, "v15_z"), change=o3, change_decline_or=(1 / o3[0], 1 / o3[2], 1 / o3[1]),
                      sd_change=float(sd16), change_per5_decline=float(np.exp(-5 * b3)), auc=cv3["auc"])
    pd.DataFrame(rows).to_csv(TAB / "table4_level_change_r1.csv", index=False)
    logger.info(f"  T4: {RES['t4']}\n  S19: {RES['s19']}")


# ----------------------------------------------------------------------------- comment 8: event study
def event_study(df, kar):
    logger.info("=== Within-athlete event study (comment 8) ===")
    vol = kar[kar["age"].between(13, 19)].groupby(["athlete_id", "age"])["meet_id"].nunique()
    ids = df[["athlete_id", "alder_ved_slutt", "aktiv_naa", "female"]].copy()
    grid = pd.MultiIndex.from_product([ids["athlete_id"], range(13, 20)], names=["athlete_id", "age"])
    p = vol.reindex(grid, fill_value=0).rename("meets").reset_index().merge(ids, on="athlete_id")
    p["exited"] = (p["aktiv_naa"] == 0).astype(int)
    p["final"] = p["alder_ved_slutt"]
    p = p[(p["exited"] == 0) | (p["age"] <= p["final"])]               # no post-exit seasons
    p["k"] = np.where(p["exited"] == 1, p["age"] - p["final"], -99)
    for kk in [0, 1, 2, 3]:
        p[f"D{kk}"] = (p["k"] == -kk).astype(int)
    for a in range(14, 20):
        p[f"age{a}"] = (p["age"] == a).astype(int)
    p["y"] = np.log1p(p["meets"])
    p = p[p.groupby("athlete_id")["age"].transform("size") >= 2]
    xs = [f"D{k}" for k in [3, 2, 1, 0]] + [f"age{a}" for a in range(14, 20)]
    out_rows, fits = [], {}
    for lab, yv, sub in [("log(1 + meets), all athletes", "y", p),
                         ("meets (linear), all athletes", "meets", p),
                         ("log(1 + meets), exits at ages 17-19 only (reference seasons observed)", "y",
                          p[(p["exited"] == 0) | p["final"].between(17, 19)])]:
        dm = sub[[yv] + xs].sub(sub.groupby("athlete_id")[[yv] + xs].transform("mean"))
        f = sm.OLS(dm[yv], dm[xs]).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(sub["athlete_id"])[0]})
        fits[lab] = f
        for kk in [3, 2, 1, 0]:
            t = f"D{kk}"
            est, lo, hi = f.params[t], f.conf_int().loc[t, 0], f.conf_int().loc[t, 1]
            pct = (lambda v: 100 * (np.exp(v) - 1)) if yv == "y" else (lambda v: v)
            out_rows.append({"Outcome / sample": lab, "Season": "T" if kk == 0 else f"T-{kk}",
                             "Estimate": round(float(est), 3), "95% CI": f"[{lo:.3f}, {hi:.3f}]",
                             "As % change in (1 + meets)" if yv == "y" else "Meets": f"{pct(est):.0f}" if yv == "y" else f"{est:.1f}",
                             "p": pfmt(float(f.pvalues[t])), "athletes": sub["athlete_id"].nunique(), "athlete-seasons": len(sub)})
        w = f.wald_test("D1 = D3", scalar=True)
        RES[f"es::{lab}"] = {**{f"D{k}": (float(f.params[f'D{k}']), float(f.conf_int().loc[f'D{k}', 0]),
                                             float(f.conf_int().loc[f'D{k}', 1])) for k in [3, 2, 1, 0]},
                                  "wald_D1_eq_D3_p": float(w.pvalue), "n_athletes": int(sub["athlete_id"].nunique()),
                                  "n_obs": len(sub), "n_exits": int(sub.loc[sub["exited"] == 1, "athlete_id"].nunique())}
    pd.DataFrame(out_rows).to_csv(TAB / "tableS28_event_study.csv", index=False)
    f = fits["log(1 + meets), all athletes"]
    ks = [-3, -2, -1, 0]
    est = [100 * (np.exp(f.params[f"D{-k}"]) - 1) for k in ks]
    lo = [100 * (np.exp(f.conf_int().loc[f"D{-k}", 0]) - 1) for k in ks]
    hi = [100 * (np.exp(f.conf_int().loc[f"D{-k}", 1]) - 1) for k in ks]
    fig, ax = plt.subplots(figsize=(6, 3.6))
    ax.axhline(0, color="#898781", lw=1)
    ax.errorbar(ks, est, yerr=[np.array(est) - np.array(lo), np.array(hi) - np.array(est)], fmt="o-", color="#2a78d6",
                ecolor="#2a78d6", capsize=4, lw=2, ms=6)
    ax.set_xticks(ks)
    ax.set_xticklabels(["T−3", "T−2", "T−1", "T (final\nactive season)"])
    ax.set_ylabel("Within-athlete change in competition\nvolume, % of (1 + meets) [95% CI]")
    ax.set_xlabel("Season relative to the athlete's own final active season")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e1e0d9", lw=0.6)
    fig.tight_layout()
    fig.savefig(FIG / "figS5_event_study.png", dpi=300)
    plt.close(fig)
    logger.info(pd.DataFrame(out_rows).to_string(index=False))


# ----------------------------------------------------------------------------- comment 11: thresholds
def thr_metrics(y_ret, v, t):
    flag, drop = v < t, y_ret == 0
    tp, fp = (flag & drop).sum(), (flag & ~drop).sum()
    fn, tn = (~flag & drop).sum(), (~flag & ~drop).sum()
    return dict(flagged=float(flag.mean()), sens=tp / max(tp + fn, 1), spec=tn / max(tn + fp, 1),
                ppv=tp / max(tp + fp, 1), npv=tn / max(tn + fn, 1),
                ret_flag=float(y_ret[flag].mean()) if flag.any() else np.nan, ret_unflag=float(y_ret[~flag].mean()))


def threshold_validation(df):
    logger.info("=== Threshold derivation/validation across cohorts (comment 11) ===")
    rng = np.random.default_rng(SEED)
    rows = []
    sets = {c: df[df["cohort"] == c][["aktiv_senior", "vol"]].dropna() for c in ["A", "B"]}

    def youden(d):
        best = max(range(2, 41), key=lambda t: (lambda m: m["sens"] + m["spec"] - 1)(
            thr_metrics(d["aktiv_senior"].values, d["vol"].values, t)))
        return best

    def boot_row(d, t, label):
        y, v = d["aktiv_senior"].values, d["vol"].values
        m0 = thr_metrics(y, v, t)
        bs = {k: [] for k in m0}
        for _ in range(B):
            i = rng.integers(0, len(y), len(y))
            mb = thr_metrics(y[i], v[i], t)
            for k in bs:
                bs[k].append(mb[k])
        ci = {k: np.nanpercentile(bs[k], [2.5, 97.5]) for k in bs}
        rows.append({"Analysis": label, "Threshold (vol <)": t, "n": len(y), "Flagged %": f"{100 * m0['flagged']:.1f}",
                     "Sensitivity": f"{m0['sens']:.2f} [{ci['sens'][0]:.2f}, {ci['sens'][1]:.2f}]",
                     "Specificity": f"{m0['spec']:.2f} [{ci['spec'][0]:.2f}, {ci['spec'][1]:.2f}]",
                     "PPV": f"{m0['ppv']:.2f} [{ci['ppv'][0]:.2f}, {ci['ppv'][1]:.2f}]",
                     "Retention, flagged": f"{100 * m0['ret_flag']:.1f}% [{100 * ci['ret_flag'][0]:.1f}, {100 * ci['ret_flag'][1]:.1f}]",
                     "Retention, unflagged": f"{100 * m0['ret_unflag']:.1f}% [{100 * ci['ret_unflag'][0]:.1f}, {100 * ci['ret_unflag'][1]:.1f}]"})
        return m0

    # capacity rule "flag the lowest volume quartile": cut-off = 25th percentile in the derivation cohort
    qA = int(np.floor(sets["A"]["vol"].quantile(0.25))) + 1          # flag vol <= P25  <=>  vol < P25 + 1
    qB = int(np.floor(sets["B"]["vol"].quantile(0.25))) + 1
    RES["thr_quartile"] = dict(cut_A=qA, cut_B=qB)
    RES["thr_quartile"]["A_derive"] = boot_row(sets["A"], qA, "Lowest-quartile rule derived in Cohort A")
    RES["thr_quartile"]["A_to_B"] = boot_row(sets["B"], qA, "Cohort-A lowest-quartile cut-off applied to Cohort B (validation)")
    RES["thr_quartile"]["B_derive"] = boot_row(sets["B"], qB, "Lowest-quartile rule derived in Cohort B")
    RES["thr_quartile"]["B_to_A"] = boot_row(sets["A"], qB, "Cohort-B lowest-quartile cut-off applied to Cohort A (validation)")
    tA, tB = youden(sets["A"]), youden(sets["B"])
    RES["thr"] = dict(youden_A=tA, youden_B=tB)
    RES["thr"]["A_derive"] = boot_row(sets["A"], tA, "Derived in Cohort A (Youden's J)")
    RES["thr"]["A_to_B"] = boot_row(sets["B"], tA, "Cohort-A threshold applied to Cohort B (validation)")
    RES["thr"]["B_derive"] = boot_row(sets["B"], tB, "Derived in Cohort B (Youden's J)")
    RES["thr"]["B_to_A"] = boot_row(sets["A"], tB, "Cohort-B threshold applied to Cohort A (validation)")
    RES["thr"]["cand10_A"] = boot_row(sets["A"], 10, "Candidate < 10 meets, Cohort A")
    RES["thr"]["cand10_B"] = boot_row(sets["B"], 10, "Candidate < 10 meets, Cohort B")
    pd.DataFrame(rows).to_csv(TAB / "tableS29_threshold_validation.csv", index=False)
    logger.info(pd.DataFrame(rows).to_string(index=False))


# ----------------------------------------------------------------------------- comment 14: gaps and returns
def gaps_and_returns(df, kar):
    logger.info("=== Temporary gaps, returns and outcome definitions (comment 14) ===")
    per = kar.groupby(["athlete_id", "year"]).size().rename("n").reset_index()
    act = per[per["n"] >= 2].groupby("athlete_id")["year"].apply(set).to_dict()
    recs = []
    for _, r in df.iterrows():
        s = act.get(r["athlete_id"], set())
        base = int(r["stevne_aar"])
        years = list(range(base, 2026))
        a = [y in s for y in years]
        last = max([y for y in s if y >= base], default=base)
        # gaps = inactive years strictly between baseline and last active season
        gaps, run, gap_lengths = 0, 0, []
        for y, on in zip(years, a):
            if y > last:
                break
            if not on:
                run += 1
            elif run:
                gap_lengths.append(run)
                run = 0
        # first inactive season after baseline -> event at the season before it
        first_gap = next((y for y, on in zip(years, a) if not on), None)
        # first sustained exit: first active season followed by >=2 inactive seasons
        sustained = None
        for i, (y, on) in enumerate(zip(years, a)):
            if on and i + 2 < len(a) and not a[i + 1] and not a[i + 2]:
                sustained = y
                break
        recs.append(dict(athlete_id=r["athlete_id"], n_gaps=len(gap_lengths),
                         max_gap=max(gap_lengths) if gap_lengths else 0, last=last,
                         first_gap_year=first_gap, sustained_year=sustained))
    g = pd.DataFrame(recs)
    d = df.merge(g, on="athlete_id")
    RES["gaps"] = dict(any_gap=float((d["n_gaps"] > 0).mean()), n_any_gap=int((d["n_gaps"] > 0).sum()),
                       gap2plus_return=float((d["max_gap"] >= 2).mean()), n_gap2plus=int((d["max_gap"] >= 2).sum()),
                       gap3plus_return=float((d["max_gap"] >= 3).mean()))
    # empirical return risk after two inactive seasons (observable windows: two inactive seasons ending <= 2021)
    retn, tot = 0, 0
    for _, r in d.iterrows():
        s = act.get(r["athlete_id"], set())
        for y in range(int(r["stevne_aar"]), 2020):
            if y in s and (y + 1) not in s and (y + 2) not in s:
                tot += 1
                retn += int(any(yy in s for yy in range(y + 3, 2026)))
                break
    RES["gaps"]["return_after_two_inactive"] = retn / max(tot, 1)
    RES["gaps"]["n_two_inactive"] = tot
    # Cox (baseline-only predictors) under three event definitions
    d["base_age"] = d["stevne_aar"] - d["birth_year"]
    out = []
    defs = {
        "Final active season (primary; censored if active 2024+)":
            (d["alder_ved_slutt"] - d["base_age"], (d["aktiv_naa"] == 0).astype(int)),
        "First sustained exit (active season followed by >=2 inactive seasons)":
            (np.where(d["sustained_year"].notna(), d["sustained_year"] - d["stevne_aar"], d["last"] - d["stevne_aar"]),
             (d["sustained_year"].notna() & (d["sustained_year"] <= 2023)).astype(int)),
        "First inactive season (any one-season gap ends the spell)":
            (np.where(d["first_gap_year"].notna(), d["first_gap_year"] - 1 - d["stevne_aar"], 2025 - d["stevne_aar"]),
             d["first_gap_year"].notna().astype(int)),
    }
    for lab, (dur, ev) in defs.items():
        c = d.assign(dur=np.clip(np.asarray(dur, dtype=float), 0.5, None), ev=np.asarray(ev))
        c = c[["dur", "ev"] + L4].dropna()
        cph = CoxPHFitter().fit(c, duration_col="dur", event_col="ev")
        s = cph.summary.loc["vol_z"]
        out.append({"Event definition": lab, "n": len(c), "events": int(c["ev"].sum()),
                    "Volume HR per SD [95% CI]": f"{s['exp(coef)']:.2f} [{s['exp(coef) lower 95%']:.2f}, {s['exp(coef) upper 95%']:.2f}]",
                    "HHI HR per SD": f"{cph.summary.loc['hhi_z', 'exp(coef)']:.2f}",
                    "C-index": f"{cph.concordance_index_:.3f}"})
        RES[f"cox::{lab[:20]}"] = dict(hr=float(s["exp(coef)"]), lo=float(s["exp(coef) lower 95%"]),
                                       hi=float(s["exp(coef) upper 95%"]), events=int(c["ev"].sum()), n=len(c))
    pd.DataFrame(out).to_csv(TAB / "tableS30_gaps_outcome_definitions.csv", index=False)
    logger.info(f"  gaps: {RES['gaps']}\n" + pd.DataFrame(out).to_string(index=False))


# ----------------------------------------------------------------------------- comment 13: target population
def target_population(df):
    logger.info("=== Target population (comment 13) ===")
    pop = pd.read_csv(PRIV / "register_population_1998_2002.csv")
    pop["female"] = pop["gender"].map({"M": 0, "F": 1})
    chk = df[["athlete_id", "vol"]].merge(pop, on="athlete_id")
    RES["pop_volume_db_minus_analysis"] = float((chk["vol_13_14"] - chk["vol"]).mean())
    rows = []
    for lab, sub in [("Cohort (attended the baseline meet)", pop[pop["cohort"] == 1]),
                     ("Not in cohort (same birth years, >=1 result at 13-14)", pop[pop["cohort"] == 0]),
                     ("All athletes born 1998-2002 with >=1 result at 13-14", pop)]:
        d = sub.dropna(subset=["female"])
        d = d.assign(v10=d["vol_13_14"] / 10)
        m, _ = logit(d, ["female", "v10"], y="senior")
        cvr, _ = repeated_cv(d[["female", "v10"]].values, d["senior"].values)
        o = orci(m, "v10")
        rows.append({"Group": lab, "n": len(sub), "Female %": f"{100 * sub['female'].mean():.1f}",
                     "Meets at 13-14, median [IQR]": f"{sub['vol_13_14'].median():.0f} [{sub['vol_13_14'].quantile(.25):.0f}-{sub['vol_13_14'].quantile(.75):.0f}]",
                     ">= 10 meets at 13-14 (%)": f"{100 * (sub['vol_13_14'] >= 10).mean():.1f}",
                     "Senior retention %": f"{100 * sub['senior'].mean():.1f}",
                     "Volume OR per 10 meets (sex-adjusted)": fmt(o), "CV-AUC (sex + volume)": f"{cvr['auc']:.3f}"})
        RES[f"pop::{lab[:10]}"] = dict(n=len(sub), senior=float(sub["senior"].mean()), med=float(sub["vol_13_14"].median()),
                                       or10=o, auc=cvr["auc"], ge10=float((sub["vol_13_14"] >= 10).mean()))
    seniors = pop[pop["senior"] == 1]
    RES["pop_share_cohort"] = float(pop["cohort"].mean())
    RES["pop_share_seniors_from_cohort"] = float(seniors["cohort"].mean())
    RES["pop_n_seniors"] = len(seniors)
    act = pop[pop["vol_13_14"] >= 10]
    RES["pop_share_active10_in_cohort"] = float(act["cohort"].mean())
    pd.DataFrame(rows).to_csv(TAB / "tableS31_target_population.csv", index=False)
    logger.info(pd.DataFrame(rows).to_string(index=False) + f"\n  share cohort {RES['pop_share_cohort']:.3f}, "
                f"seniors from cohort {RES['pop_share_seniors_from_cohort']:.3f}, >=10 meets in cohort {RES['pop_share_active10_in_cohort']:.3f}")


# ----------------------------------------------------------------------------- tables 7 and S20
def cohort_replication(df):
    logger.info("=== Internal cohort replication, Table 7 (comment 15) ===")
    rows = []
    for c in ["A", "B"]:
        m, d = logit(df[df["cohort"] == c], L4)
        for t in L4:
            o = orci(m, t)
            rows.append({"Cohort": "A (births 1998-2000)" if c == "A" else "B (births 2001-2002)", "n": len(d),
                         "Covariate": t, "OR": round(o[0], 2), "95% CI": f"[{o[1]:.2f}, {o[2]:.2f}]", "p": pfmt(o[3])})
            RES[f"t7::{c}::{t}"] = o
        RES[f"t7::{c}::n"] = len(d)
    pd.DataFrame(rows).to_csv(TAB / "table7_internal_replication_r1.csv", index=False)


def hhi_stress(df):
    logger.info("=== HHI count-dependence stress tests (S20) ===")
    rows = []
    m, d = logit(df, L4)
    rows.append({"Model": "Primary L4 (all)", "n": len(d), "HHI OR": fmt(orci(m, "hhi_z")), "Volume OR": f"{orci(m, 'vol_z')[0]:.2f}"})
    for cut in [5, 8]:
        s = df[df["res_13_14"] >= cut].copy()
        for c in ["tyr", "hhi", "vol"]:
            s[c + "_z"] = z(s[c])
        m, d = logit(s, L4)
        rows.append({"Model": f">= {cut} results at ages 13-14", "n": len(d), "HHI OR": fmt(orci(m, "hhi_z")),
                     "Volume OR": f"{orci(m, 'vol_z')[0]:.2f}"})
        RES[f"hhi_ge{cut}"] = orci(m, "hhi_z")
    s = df[df["res_13_14"] >= 2].copy()
    s["hhi_c"] = (s["hhi"] - 1 / s["res_13_14"]) / (1 - 1 / s["res_13_14"])
    for c in ["tyr", "hhi_c", "vol"]:
        s[c + "_z"] = z(s[c])
    m, d = logit(s, ["female", "tyr_z", "hhi_c_z", "vol_z"])
    rows.append({"Model": "Finite-sample-corrected HHI* = (HHI - 1/n)/(1 - 1/n)", "n": len(d),
                 "HHI OR": fmt(orci(m, "hhi_c_z")), "Volume OR": f"{orci(m, 'vol_z')[0]:.2f}"})
    RES["hhi_corrected"] = orci(m, "hhi_c_z")
    RES["hhi_rho_res"] = float(df[["hhi", "res_13_14"]].corr("spearman").iloc[0, 1])
    RES["hhi_rho_vol"] = float(df[["hhi", "vol"]].corr("spearman").iloc[0, 1])
    RES["hhi_r_tyr"] = float(df[["hhi", "tyr"]].corr().iloc[0, 1])
    pd.DataFrame(rows).to_csv(TAB / "tableS20_hhi_stress_r1.csv", index=False)
    logger.info(pd.DataFrame(rows).to_string(index=False))


def evalues():
    o = RES["primary_L4"]["vol_z"]
    rr, rr_lo = np.sqrt(o[0]), np.sqrt(o[1])
    ev = lambda r: r + np.sqrt(r * (r - 1))  # noqa: E731
    RES["evalue"] = dict(rr=float(rr), e=float(ev(rr)), e_ci=float(ev(rr_lo)))


def main():
    df, kar = load()
    primary(df)
    cv_procedures(df)
    auc_differences(df)
    missing_data(df)
    unknown_sex(df)
    birth_quarter(df)
    change_models(df)
    event_study(df, kar)
    threshold_validation(df)
    gaps_and_returns(df, kar)
    target_population(df)
    cohort_replication(df)
    hhi_stress(df)
    evalues()
    with open(TAB / "r1_results.json", "w") as f:
        json.dump(RES, f, indent=1, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o))
    logger.info("=== R1 analyses done ===")


if __name__ == "__main__":
    main()
