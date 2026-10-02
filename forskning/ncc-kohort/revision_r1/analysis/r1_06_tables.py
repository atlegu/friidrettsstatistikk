"""
r1_06_tables.py — Builds manuscript/11_tables.md (main Tables 1-7 and Supplementary
Tables S1-S32) directly from the analysis outputs, so that no number is transcribed by hand.

Changed cells (relative to the submitted 11_tables.md) are wrapped in {+ ... +} so the
build script can print them in coloured text in the highlighted manuscript.

Every count in the notes is computed from the corrected data (r1_00) or read from the result
files (r1_results.json, rerun tables, rerun.log), so the notes cannot drift from the tables.
"""

import difflib
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
R1 = HERE.parent
sys.path.insert(0, str(HERE))
from r1_paths import CDATA, PRIV  # noqa: E402

TAB, RERUN = R1 / "tables", R1 / "tables" / "rerun"
SUBMITTED = Path("/Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/Statistikk/forskning/ncc-kohort/submission_pse/11_tables.md")
RES = json.loads((TAB / "r1_results.json").read_text())
TXT = json.loads((TAB / "r1_text_numbers.json").read_text())
LOG = (TAB / "rerun.log").read_text()
DF = pd.read_csv(CDATA / "analysedata_utvidet.csv", low_memory=False).merge(
    pd.read_csv(PRIV / "r1_variables.csv"), on="athlete_id", how="left")


def section(script):
    return LOG.split(f"##### {script}")[1].split("#####")[0]


def logged(script, pattern):
    return [float(x) for x in re.findall(pattern, section(script))]


K = dict(
    N=len(DF), sex_known=int(DF["gender"].notna().sum()), sex_unknown=int(DF["gender"].isna().sum()),
    primary_n=RES["primary_n"], prevalence=float(DF["aktiv_senior"].mean()),
    active14=int((DF["res_age_14"] >= 1).sum()), active16_any=int((DF["res_age_16"] >= 1).sum()),
    active16_two=int((DF["res_age_16"] >= 2).sum()),
    tyr_missing_known=int((DF["gender"].notna() & DF["tyrving_best_r1"].isna()).sum()),
    nosex_at_risk14=int(((DF["alder_ved_slutt"] >= 14) & DF["gender"].isna()).sum()),
    region_missing=int((DF["gender"].notna() & DF["region"].isna()).sum()),
    traj_n=RES["dauc::Sex + volume vs. sex + Tyrving + Tyrving change 13-14"]["n"],
    no_birth_date=RES["bq_missing"]["n"], clubs=RES["n_clubs"], club_max=RES["club_size_max"],
    cindex_tv=logged("10_time_varying_cox.py", r"C-index=([0-9.]+)"),
    cindex_sex=dict(zip(["Male", "Female"], logged("09_sensitivity_pse.py", r"(?:Male|Female) \(n=\d+\): C-index=([0-9.]+)"))),
    s18_n=[int(x) for x in logged("15_specialization_confound_check.py", r"n=(\d+), pseudo")],
    s18_r=dict(zip(["best_main", "best_hhi", "main_hhi"], [
        float(re.search(r"tyrving_best_z\s+1\.000\s+([-0-9.]+)\s+([-0-9.]+)", section("15_specialization_confound_check.py")).group(i)) for i in (1, 2)]
        + [float(re.search(r"tyrving_main_z\s+[-0-9.]+\s+1\.000\s+([-0-9.]+)", section("15_specialization_confound_check.py")).group(1))])),
)

NAMES = {"female": "Female", "tyrving_best_z": "Tyrving (z)", "tyr_z": "Tyrving (z)", "tyr_zs": "Tyrving (z)",
         "hhi_early_z": "HHI, ages 13–14 (z)", "hhi_z": "HHI, ages 13–14 (z)", "vol_pre_milepael_z": "Pre-milestone volume (z)",
         "vol_z": "Pre-milestone volume (z)", "vol_milepael_z": "Volume at ages 15–16 (z)", "n_msk_typer": "Championship types",
         "v14_z": "Volume at age 14 (z)", "d1415_z": "Volume change 14→15 (z)", "v15_z": "Volume at age 15 (z)",
         "d1516_z": "Volume change 15→16 (z)", "q1_born": "Q1 born", "q4_born": "Q4 born", "region_ostlandet": "Region: Østlandet",
         "region_midt": "Region: Midt-Norge", "klubb_storrelse_z": "Club size (z)", "tyrving_main_z": "Tyrving main category (z)",
         "q1": "Q1 (Jan–Mar)", "q2": "Q2 (Apr–Jun)", "q3": "Q3 (Jul–Sep)", "q4": "Q4 (Oct–Dec)", "q_lin": "Quarter (linear, 1–4)"}


def n(x):
    return f"{int(x):,}"


def p(v):
    v = float(v)
    return "< .001" if v < .001 else f"{v:.3f}".lstrip("0")


def ci(lo, hi, d=2):
    return f"[{lo:.{d}f}, {hi:.{d}f}]"


# ----------------------------------------------------------------------------- submitted tables (for highlighting)
def parse_submitted():
    text = SUBMITTED.read_text()
    out, notes, titles = {}, {}, {}
    for block in re.split(r"\n(?=## Table )", text):
        m = re.match(r"## Table (S?\d+)\. (.*)", block)
        if not m:
            continue
        rows = [l for l in block.split("\n") if l.startswith("|") and not re.match(r"^\|[-| ]+\|$", l)]
        out[m.group(1)] = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
        titles[m.group(1)] = m.group(2).strip()
        nl = [l for l in block.split("\n") if l.startswith("*Note.*")]
        notes[m.group(1)] = nl[0].strip() if nl else None
    return out, notes, titles


OLD, OLD_NOTE, OLD_TITLE = parse_submitted()


def hl_diff(new, old):
    """Highlight the words of `new` that differ from the submitted text `old` (word-level diff)."""
    plain = new.replace("{+", "").replace("+}", "")
    if not old:
        return new
    a, b = old.split(" "), plain.split(" ")
    out = []
    for op, _, _, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        seg = " ".join(b[j1:j2])
        if seg:
            out.append(seg if op == "equal" else "{+" + seg + "+}")
    return " ".join(out)


def _plain(c):
    return re.sub(r"\*\*", "", c).strip()


def _mark(c):
    """Wrap a cell in highlight markers (inside bold markup)."""
    c = c.replace("{+", "").replace("+}", "")
    if not c.strip():
        return c
    bold = c.startswith("**") and c.endswith("**")
    return f"**{{+{c[2:-2]}+}}**" if bold else f"{{+{c}+}}"


def render(num, title, header, rows, note, new=False):
    """Markdown table; header cells, cells and note words differing from the submitted version are
    highlighted, and a table that is new in the revision is highlighted throughout."""
    old = OLD.get(num)
    old_rows = old[1:] if old else None
    title = "{+" + title.replace("{+", "").replace("+}", "") + "+}" if new else hl_diff(title, OLD_TITLE.get(num))
    if new:
        note = "{+" + note.replace("{+", "").replace("+}", "") + "+}" if note else note
    elif note:
        note = hl_diff(note, OLD_NOTE.get(num))
    head = [h if (old is not None and j < len(old[0]) and _plain(old[0][j]) == _plain(h)) or "{+" in h else _mark(h)
            for j, h in enumerate(header)]
    lines = [f"## Table {num}. {title}", "",
             "| " + " | ".join(head) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    for i, r in enumerate(rows):
        cells = []
        for j, c in enumerate(r):
            c = str(c)
            same = (old_rows is not None and i < len(old_rows) and j < len(old_rows[i])
                    and _plain(old_rows[i][j]) == _plain(c))
            if new:
                cells.append(_mark(c))
            elif c.strip() == "" or same or "{+" in c:
                cells.append(c)
            else:
                cells.append(_mark(c))
        lines.append("| " + " | ".join(cells) + " |")
    lines += ["", note, "", "---", ""]
    return "\n".join(lines)


def hl(s):
    return "{+" + s + "+}"


def fmt_or(o):
    return f"{o[0]:.2f} [{o[1]:.2f}, {o[2]:.2f}]"


L4 = ["female", "tyr_z", "hhi_z", "vol_z"]


def dauc(k, close=True):
    """'0.069 (95% CI 0.047 to 0.091)' for a paired AUC difference in r1_results.json."""
    d = RES["dauc::" + k]
    f = lambda v: f"{v:.3f}".replace("-", "−")  # noqa: E731
    return f"{f(d['diff'])} (95% CI {f(d['lo'])} to {f(d['hi'])}" + (")" if close else "")


def s18_summary(t):
    h = t[t["Covariate"] == "hhi_early_z"].reset_index(drop=True)
    m = t[t["Covariate"] == "tyrving_main_z"].reset_index(drop=True)
    stable = all(h["p"] < .05)
    txt = (f"The HHI coefficient is {'stable' if stable else 'not stable'} across the three specifications "
           f"(OR {h['OR'].min():.2f}–{h['OR'].max():.2f}"
           + ("" if stable else f"; {h.loc[1, 'OR']:.2f} {ci(h.loc[1, 'CI low'], h.loc[1, 'CI high'])} once main-category Tyrving is added") + "); "
           f"main-category Tyrving has an independent association (OR {m['OR'].min():.2f}–{m['OR'].max():.2f}).")
    return txt


# ----------------------------------------------------------------------------- main tables
def table1():
    t = pd.read_csv(RERUN / "table1_descriptives.csv").set_index("Cohort")
    df = DF.copy()
    df["c"] = np.where(df["birth_year"] <= 2000, "1998-2000", "2001-2002")
    unk = df[df["gender"].isna()].groupby("c").size()
    med = df.groupby("c")["vol_pre_milepael"].median()
    cols = ["1998-2000", "2001-2002", "All"]
    g = lambda c, k: t.loc[c, k]  # noqa: E731
    rows = [["N", *[n(g(c, "N")) for c in cols]],
            ["Male (n)", *[n(g(c, "M")) for c in cols]],
            ["Female (n)", *[n(g(c, "F")) for c in cols]],
            ["Sex unknown (n)", str(unk.get("1998-2000", 0)), str(unk.get("2001-2002", 0)), str(int(unk.sum()))],
            ["Median career length (years)", *[f"{g(c, 'Median career (years)'):.1f}" for c in cols]],
            ["Active at age 17 or later (%)", *[f"{g(c, 'Active age 17 (%)'):.1f}" for c in cols]],
            ["Ever active at age 20+ (%)", *[f"{g(c, 'Active age 20 (%)'):.1f}" for c in cols]],
            ["Still active in 2024 or later (%)", *[f"{g(c, 'Still active 2024+ (%)'):.1f}" for c in cols]],
            ["Mean Tyrving best at baseline", *[f"{g(c, 'Mean Tyrving best'):.0f}" for c in cols]],
            ["Median total meets, ages 13–14 (pre-milestone volume)", f"{med['1998-2000']:.0f}", f"{med['2001-2002']:.0f}",
             f"{df['vol_pre_milepael'].median():.0f}"]]
    note = ("*Note.* " + hl('"Active at age 17 or later" indicates an active season (≥2 registered results in a calendar year) at age 17 or later')
            + '; "Ever active at age 20+" is the outcome prevalence (≥2 results in any calendar year at age 20 or later). '
            "Tyrving points = the Norwegian Athletics Federation's age-norm score, where 1,000 corresponds to the published "
            "reference performance for that event × sex × age combination" + hl("; all baseline events scored with implement- and "
            "hurdle-specific norms and the workbook's own formulas (Supplementary Methods S-M3). Meets are counted as competition days "
            "(Section 2.4.4). Follow-up through 2025") + ".")
    return render("1", "Cohort characteristics by birth-year cohort",
                  ["Characteristic", "Cohort A (1998–2000)", "Cohort B (2001–2002)", "All cohorts"], rows, note)


def table2():
    t = pd.read_csv(RERUN / "table2_volume_trajectory.csv").set_index("Group")
    fmt = lambda v: f"{v:g}"  # noqa: E731
    rows = []
    for g, lab in [("Senior retainers", "Senior retainers (active age ≥20)"), ("Dropouts", "Dropouts (last active age <20)")]:
        r = t.loc[g]
        rows.append([lab, n(r["N"]), *[f"{fmt(r[f'Age {a} median'])} [{r[f'Age {a} IQR'].replace('-', '–')}]" for a in range(13, 19)]])
    note = ("*Note.* Values are median number of meets (competition days) per year [IQR]. Future retainers and future dropouts "
            "already differ at ages 13–14; the gap widens further across the age-14-to-15 transition.")
    return render("2", "Competition volume trajectory by senior-retention status (median competitions per year and IQR)",
                  ["Group", "N", "Age 13", "Age 14", "Age 15", "Age 16", "Age 17", "Age 18"], rows, note)


def table3():
    t = pd.read_csv(TAB / "table3_primary_r1.csv")
    rows = []
    for model, g in t.groupby("Model", sort=False):
        for k, (_, r) in enumerate(g.iterrows()):
            name = NAMES[r["Covariate"]]
            vol = r["Covariate"] == "vol_z"
            lab = {"L1": "L1: Sex only", "L2": "L2: + Performance", "L3": "L3: + Event concentration",
                   "L4": "L4: + Pre-milestone volume"}[model[:2]] if k == 0 else ""
            auc = f"{float(r['CV-AUC (5-fold x 20)']):.3f} {r['CV-AUC 95% CI']}" if k == 0 else ""
            if model.startswith("L4") and k == 0:
                auc = f"**{float(r['CV-AUC (5-fold x 20)']):.3f}** {r['CV-AUC 95% CI']}"
            cells = [lab, f"**{name}**" if vol else name, f"**{r['OR']:.2f}**" if vol else f"{r['OR']:.2f}",
                     f"**{r['95% CI']}**" if vol else r["95% CI"], f"**{r['p']}**" if vol else r["p"], auc,
                     n(r["n"]) if k == 0 else ""]
            rows.append(cells)
    note = ("*Note.* Logistic regression for binary active senior status (≥2 registered results in any year at age 20+). "
            "Predictors are observed during the baseline window (ages 13–14) only" + hl(", including HHI (results at ages 13–14)")
            + ". Pre-milestone volume is the number of meets " + hl("(competition days)") + " at ages 13 and 14. Continuous covariates are "
            "z-standardized so ORs reflect per-SD effects. " + hl("CV-AUC: mean of fold-level AUCs from stratified 5-fold "
            "cross-validation repeated 20 times, with standardization inside the training folds; 95% CI from the corrected "
            f"resampled t (Supplementary Methods S-M4). Adding volume raised the AUC by {dauc('+ volume vs. sex + Tyrving + HHI (L4 vs. L3)', close=False)}; "
            "Supplementary Table S27). HHI is associated with retention only once volume is entered, does not improve "
            "discrimination, and is not robust to performance in the athlete's main event category (Supplementary Table S18; Discussion 4.6)."))
    return render("3", "Primary analysis: prospective logistic regression for active senior status (baseline-only predictors, ages 13–14)",
                  ["Model", "Covariate", "OR", "95% CI", "p", "CV-AUC [95% CI]", "n"], rows, note)


def table4():
    t = pd.read_csv(TAB / "table4_level_change_r1.csv")
    t = t[t["Sample"].str.startswith("Active at 14")]
    rows = []
    for model, g in t.groupby("Model", sort=False):
        for k, (_, r) in enumerate(g.iterrows()):
            name = NAMES[r["Covariate"]]
            vol = r["Covariate"] in ("v14_z", "d1415_z")
            orv, civ = r["OR per SD"].split(" ", 1)
            lab = ("M1: Volume at age 14 only" if model.startswith("M1") else "M2: + Volume change 14→15") if k == 0 else ""
            rows.append([lab, f"**{name}**" if vol else name, f"**{orv}**" if vol else orv, f"**{civ}**" if vol else civ,
                         f"**{r['p']}**" if vol else r["p"]])
    t4 = RES["t4"]
    d = t4["change_decline_or"]
    note = ("*Note.* " + hl(f"Change = volume at 15 minus volume at 14 (positive = increase; mean {format(t4['mean_change'], '.1f').replace('-', '−')}, SD "
            f"{t4['sd_change']:.1f} meets). The OR of {t4['change'][0]:.2f} per SD increase is equivalent to OR = {d[0]:.2f} "
            f"[{d[1]:.2f}, {d[2]:.2f}] per SD of greater decline (about {t4['sd_change']:.1f} fewer meets), conditional on "
            f"the level at age 14; per 5 fewer meets, OR = {t4['change_per5_decline']:.2f}. Because the model is linear in "
            f"the logit, it is identical to one with volume at 14 and volume at 15 as separate levels (the per-meet OR for "
            f"change equals the per-meet OR for volume at 15). Pseudo-R² (McFadden) rose from {t4['r2_m1']:.3f} (M1) to "
            f"{t4['r2_m2']:.3f} (M2); CV-AUC {t4['auc_m1']:.3f} → {t4['auc_m2']:.3f}. {K['active14'] - t4['n']} of the {K['active14']:,} athletes with a result at 14 "
            f"{'lacks' if K['active14'] - t4['n'] == 1 else 'lack'} registered sex or a Tyrving score (sample n = {t4['n']:,}).") + " Both baseline level and within-athlete "
            + hl("decline") + " contribute substantially and independently.")
    return render("4", "Level versus within-athlete change: volume at age 14 and change from 14 to 15",
                  ["Model", "Covariate", "OR per SD", "95% CI", "p"], rows, note)


def table5():
    t = pd.read_csv(RERUN / "tableS8_time_varying.csv")
    periods = list(dict.fromkeys(t["Period"]))
    order = ["vol_milepael_z", "n_msk_typer", "tyrving_best_z", "hhi_early_z", "female"]
    labels = {"vol_milepael_z": "Volume at age 15–16 (per SD)", "n_msk_typer": "Championship types (count)",
              "tyrving_best_z": "Tyrving (z)", "hhi_early_z": "HHI, ages 13–14 (z)", "female": "Female"}
    rows = []
    for c in order:
        cells = [labels[c]]
        for pr in periods:
            r = t[(t["Covariate"] == c) & (t["Period"] == pr)].iloc[0]
            cells.append(f"{r['HR']:.2f} {ci(r['CI low'], r['CI high'])}")
        rows.append(cells)
    first = t.drop_duplicates("Period")
    rows.append(["n at risk in interval", *[n(v) for v in first["n at risk"]]])
    rows.append(["events in interval", *[n(v) for v in first["events in interval"]]])
    rows.append(["C-index", *[f"{c:.3f}" for c in K["cindex_tv"]]])
    note = ("*Note.* Period-specific Cox estimates from the post-baseline specification with covariates measured at ages "
            "15–16 and ≤17. The early-window HR for ages-15–16 volume partly reflects operational overlap between predictor "
            "and outcome (low milestone volume is mechanical for athletes who drop out before age 15); this estimate should be "
            "read as descriptive of the time-varying association rather than as an independent prospective effect. "
            "Substantively, the protective association attenuates across follow-up, consistent with a proximal "
            "disengagement-marker interpretation. " + hl("All rows are generated directly from the analysis code (C-index per interval from the same models)."))
    return render("5", "Time-varying hazard ratios (post-baseline Cox specification, period-specific)",
                  ["Covariate", "Years 0–3 since baseline (approx. ages 13–17)", "Years 3–6 (approx. ages 16–20)",
                   "Years 6+ (approx. ages 19+)"], rows, note)


def table6():
    t = pd.read_csv(RERUN / "table6_NEW_prospective_calibration.csv")
    rows = []
    for _, r in t.iterrows():
        ppv, ppv_ci = r["PPV [95% CI]"].split(" ", 1)
        rows.append([f"{r['Threshold (vol <)']} meets", f"{r['Flagged %']:.1f}", r["Sensitivity [95% CI]"], r["Specificity [95% CI]"],
                     f"**{ppv}** {ppv_ci}", r["NPV [95% CI]"], r["Senior retention, flagged [95% CI]"],
                     r["Senior retention, unflagged [95% CI]"]])
    r10 = t[t["Threshold (vol <)"] == 10].iloc[0]
    f10 = float(r10["Senior retention, flagged [95% CI]"].split("%")[0])
    u10 = float(r10["Senior retention, unflagged [95% CI]"].split("%")[0])
    ppv10 = float(r10["PPV [95% CI]"].split(" ")[0])
    base = 1 - K["prevalence"]
    note = ("*Note.* Classification performance of pre-milestone (ages 13–14) competition volume as a prospective "
            "early-warning indicator, applicable at the end of an athlete's age-14 season, before the qualification window "
            f"opens. All metrics are computed on one denominator (full cohort, n = {K['N']:,}); brackets are 2,000-replicate "
            "bootstrap 95% CIs. PPV is the proportion of flagged athletes who subsequently failed to retain senior activity. "
            f"The final two columns give the absolute retention contrast: at the < 10 threshold, {f10:.1f}% among flagged vs. {u10:.1f}% "
            f"among unflagged athletes (a {u10 / f10:.1f}-fold difference). The high PPV partly reflects the population's {100 * base:.0f}% "
            f"non-retention base rate (the threshold improves precision by ~{100 * (ppv10 - base):.0f} percentage points over base-rate prediction), "
            "and the NPV of ≈ 0.20 means unflagged athletes are not \"safe\": roughly four in five of them also fail to retain. "
            + hl("The thresholds are candidate cut-offs chosen in the pooled data; derivation in one birth cohort and "
                 "validation in the other are reported in Supplementary Table S29. Calibration of the underlying model is "
                 "reported in Supplementary Table S23."))
    return render("6", "Prospective early-warning thresholds (pre-milestone volume, ages 13–14)",
                  ["Threshold (flag if vol <)", "Flagged %", "Sensitivity", "Specificity", "PPV", "NPV",
                   "Senior retention, flagged", "Senior retention, unflagged"], rows, note)


def table7():
    t = pd.read_csv(TAB / "table7_internal_replication_r1.csv")
    rows = []
    for coh, g in t.groupby("Cohort", sort=False):
        for k, (_, r) in enumerate(g.iterrows()):
            name = NAMES[r["Covariate"]]
            vol = r["Covariate"] == "vol_z"
            rows.append([coh.split(" (")[1].rstrip(")").replace("births ", "").replace("-", "–") if k == 0 else "",
                         n(r["n"]) if k == 0 else "", f"**{name}**" if vol else name,
                         f"**{r['OR']:.2f}**" if vol else f"{r['OR']:.2f}", f"**{r['95% CI']}**" if vol else r["95% CI"],
                         f"**{r['p']}**" if vol else r["p"]])
    hA, hB = RES["t7::A::hhi_z"], RES["t7::B::hhi_z"]
    hhi_txt = ("The HHI association is clear in the 2001–2002 cohort but not significant in the 1998–2000 cohort"
               if (hB[3] < .05) != (hA[3] < .05) else "The HHI association is " + ("present" if hA[3] < .05 else "not significant") + " in both cohorts")
    note = ("*Note.* The primary baseline-only logistic model re-estimated separately within each birth-year cohort. "
            + hl("ORs are per SD of the whole cohort, so the two cohorts are on the same scale. "
                 "Both cohorts come from the same register and national system, so this is an internal replication. The "
                 "pre-milestone volume effect and the performance association are reproduced at similar magnitude in both cohorts; "
                 f"female sex predicts lower retention in both. {hhi_txt} (see Section 3.9)."))
    return render("7", hl("Internal cohort replication") + " of the primary L4 logistic model",
                  ["Cohort", "n", "Covariate", "OR", "95% CI", "p"], rows, note)


# ----------------------------------------------------------------------------- supplementary tables
def cox_rows(path, hr_col="HR", lo="CI low", hi="CI high", pcol="p", order=None):
    t = pd.read_csv(path)
    rows = []
    for _, r in t.iterrows():
        rows.append([NAMES.get(r["Covariate"], r["Covariate"]), f"{r[hr_col]:.2f}", ci(r[lo], r[hi]), p(r[pcol])])
    return rows


def supp():
    out = ["# Supplementary Tables", ""]
    # S1
    t = pd.read_csv(RERUN / "tableS1_ph_test.csv").rename(columns={"Unnamed: 0": "cov"}).set_index("cov")
    order = ["female", "tyrving_best_z", "hhi_early_z", "vol_milepael_z", "n_msk_typer"]
    rows = [[NAMES[c] if c != "vol_milepael_z" else "Volume at age 15–16 (z)", f"{t.loc[c, 'test_statistic']:.2f}", p(t.loc[c, "p"])] for c in order]
    out.append(render("S1", "Proportional-hazards assumption test for the post-baseline Cox specification (Schoenfeld residuals)",
                      ["Covariate", "χ²₁", "p"], rows, ""))
    # S2
    t = pd.read_csv(RERUN / "tableS2_cluster_robust.csv")
    rows = [[NAMES[r["Covariate"]] if r["Covariate"] != "vol_milepael_z" else "Volume at age 15–16 (z)", f"{r['HR']:.2f}",
             ci(r["Robust CI low"], r["Robust CI high"]), p(r["p (robust)"])] for _, r in t.iterrows()]
    out.append(render("S2", "Cluster-robust SE Cox (clustered on club)", ["Covariate", "HR", "Robust 95% CI", "p (robust)"], rows,
                      "*Note.* Post-baseline specification; pooled HRs average over the strongly time-varying pattern shown in Table 5 and are descriptive."
                      + hl(" Club-clustered errors for the primary logistic model are in Supplementary Table S22.")))
    # S3
    ov, ev = RES["primary_L4"]["vol_z"], RES["evalue"]
    cv, cev = RES["cox14"]["main"]["vol_z"], RES["cox14"]["evalue"]
    rows = [["Pre-milestone volume, primary logistic (per SD)", f"OR {ov[0]:.2f} {ci(ov[1], ov[2])}", f"{ev['rr']:.2f}",
             f"{ev['e']:.2f}", f"{ev['e_ci']:.2f}"],
            [hl("Pre-milestone volume, baseline-only Cox from the end of age 14 (per SD)"), f"HR {cv[0]:.2f} {ci(cv[1], cv[2])}",
             f"{cev['rr']:.2f}", f"{cev['e']:.2f}", f"{cev['e_ci']:.2f}"]]
    out.append(render("S3", "E-values for the primary baseline-window volume effect (VanderWeele & Ding, 2017)",
                      ["Effect", "Estimate", "Approx. RR (common outcome; protective effects inverted)", "E-value (point)", "E-value (CI bound)"], rows,
                      f"*Note.* Because the outcome is common ({100 * K['prevalence']:.1f}%), the odds ratio is converted to an approximate risk ratio (RR ≈ √OR) before computing E = RR + √(RR(RR − 1)); the hazard ratio uses the common-outcome conversion RR ≈ (1 − 0.5^√HR)/(1 − 0.5^√(1/HR)), inverted because the association is protective (Supplementary Methods S-M5). E-values are reported for the primary baseline-window specification only; the post-baseline (ages-15–16) specification is not an admissible E-value input because it overlaps the outcome window and violates proportional hazards."))
    # S4
    det = RES["detect"]
    rows = [[c.replace("-", "–"), n(v["cox_n"]), n(v["cox_events"]), f"{v['hr_min']:.3f}", n(v["logit_n"]), n(v["retainers"]), f"{v['or_min']:.3f}"]
            for c, v in det.items()]
    out.append(render("S4", "Sample-size sensitivity: minimum detectable hazard and odds ratios", ["Cohort", "N (Cox)", "Events", "Min. detectable HR",
                                                                              hl("n (logistic)"), hl("Retainers"), hl("Min. detectable OR")], rows,
                      hl("*Note.* 80% power, α = .05, per SD of a standardized covariate. Cox: the baseline-only model with time zero at the end of the "
                         "age-14 season (Supplementary Table S10); log HR_min = (z₀.₉₇₅ + z₀.₈₀)/√events. Logistic: the primary model; "
                         "log OR_min = (z₀.₉₇₅ + z₀.₈₀)/√(n·p·(1 − p)), with p the retention rate (normal-covariate approximation). "
                         "Supplementary Methods S-M2.")))
    # S5
    t = pd.read_csv(RERUN / "tableS5_imputation.csv")
    rows = [[NAMES[r["Covariate"]] if r["Covariate"] != "vol_milepael_z" else "Volume at age 15–16 (z)",
             f"{r['HR (complete case)']:.2f}", f"{r['HR (mean imputation)']:.2f}"] for _, r in t.iterrows()]
    rows.append(["n", n(t["n (CC)"].iloc[0]), n(t["n (imputed)"].iloc[0])])
    out.append(render("S5", "Complete-case vs mean-imputation sensitivity", ["Covariate", "HR (complete case)", "HR (mean imputation)"], rows,
                      "*Note.* Post-baseline Cox specification (descriptive; see Table 5 note). The principal missing-data sensitivity for the primary logistic model is multiple imputation, Supplementary Table S21."
                      + hl(f" The mean-imputation model retains all {K['N']:,} athletes; the {K['sex_unknown']} without registered sex enter with the male reference code.")))
    # S6
    t = pd.read_csv(RERUN / "tableS6_stratified_cox.csv")
    rows = [[NAMES[r["Covariate"]] if r["Covariate"] != "vol_milepael_z" else "Volume at age 15–16 (z)",
             f"{r['HR (strat. by hhi_early_z)']:.2f}", p(r["p"])] for _, r in t.iterrows()]
    out.append(render("S6", "Cox model stratified on HHI tercile (sensitivity to PH violation)", ["Covariate", "HR", "p"], rows,
                      hl("*Note.* Post-baseline specification. HHI is one of the covariates that violate proportional hazards (Supplementary Table S1); "
                         "stratifying on it leaves the other estimates unchanged. The dominant violation, ages-15–16 volume, is addressed by the "
                         "period-specific estimates in Table 5, not by this model.")))
    # S7
    t = pd.read_csv(RERUN / "tableS7_subgroup_sex.csv")
    rows = []
    for sex, g in t.groupby("Sex", sort=False):
        for k, (_, r) in enumerate(g.iterrows()):
            rows.append([sex if k == 0 else "", n(r["n"]) if k == 0 else "",
                         NAMES[r["Covariate"]] if r["Covariate"] != "vol_milepael_z" else "Volume at age 15–16 (z)",
                         f"{r['HR']:.2f}", ci(r["CI low"], r["CI high"]), p(r["p"])])
    out.append(render("S7", "Sex-stratified Cox subgroup analyses", ["Sex", "n", "Covariate", "HR", "95% CI", "p"], rows,
                      "*Note.* Post-baseline specification (descriptive; see Table 5 note). "
                      + hl(f"C-index = {K['cindex_sex']['Male']:.3f} (male) and {K['cindex_sex']['Female']:.3f} (female).") +
                      " The dominant behavioral covariate is near-identical across sexes (volume HR "
                      + hl(" vs ".join(f"{float(t[(t['Sex'] == s) & (t['Covariate'] == 'vol_milepael_z')]['HR'].iloc[0]):.2f}" for s in ["Male", "Female"])) + ")."))
    # S8
    lm = RES["lm16"]
    lab16 = {"female": "Female", "tyr_z": "Tyrving (z)", "hhi_z": "HHI, ages 13–14 (z)", "vol1516_z": "**Volume at age 15–16 (z)**",
             "n_msk_typer": "Championship types"}
    rows = [[lab16[c], f"{lm[c][0]:.2f}", ci(lm[c][1], lm[c][2]), p(lm[c][3])] for c in lab16]
    rows += [["n complete", n(lm["n"]), "", ""], ["C-index", f"{lm['cindex']:.3f}", "", ""]]
    out.append(render("S8", f"Landmark analysis at age 16 (post-baseline Cox, n = {lm['n_at_risk']:,})", ["Covariate", "HR", "95% CI", "p"], rows,
                      "*Note.* " + hl("Athletes still in their career at age 16 (final active season at 16 or later), with follow-up time measured "
                                      f"from age 16 forward ({lm['events']:,} events). The earlier entry rule (≥1 result at 16) also admitted "
                                      f"{lm['n_old_entry_already_exited']} athletes whose final active season was earlier, so that their event preceded time zero.")
                      + " The age-16 share of the exposure window lies at the start of the at-risk window (see Supplementary Methods S-M1). The fully contamination-free logistic analogue is the change model in main-text Section 3.5 / Supplementary Table S19."))
    # S9
    t = pd.read_csv(RERUN / "tableS9_outcome_sensitivity.csv")
    rows = [[r["Outcome"], {"A": "≥1 senior-age (20+) result", "B": "≥2 results in any senior-age year (primary)",
                            "C": "≥2 results in each of two distinct senior-age years"}[r["Outcome"]],
             f"{n(r['Retainer n'])} ({r['Retainer %']}%)", f"{r['OR (pre-milestone volume, per SD)']:.2f}", r["95% CI"],
             f"{r['CV-AUC (L4)']:.3f}"] for _, r in t.iterrows()]
    out.append(render("S9", "Outcome-definition sensitivity (primary L4 specification, baseline-only predictors)",
                      ["Outcome", "Description", "Retainer n (%)", "OR (pre-milestone vol per SD)", "95% CI", "CV-AUC"], rows,
                      "*Note.* All three rows re-estimate the primary L4 model (sex, Tyrving, HHI, pre-milestone volume; " + hl(f"n = {K['primary_n']:,}") + ") with the alternative outcome definitions. The volume effect is stable across definitions." + hl(" CV-AUC here is from a single stratified 5-fold split, as in the original analysis, so it differs slightly from the repeated cross-validation in Table 3.")))
    # S10
    c14 = RES["cox14"]["main"]
    rows = [[f"**{NAMES[c]}**" if c == "vol_z" else NAMES[c], f"{c14[c][0]:.2f}", ci(c14[c][1], c14[c][2]), p(c14[c][3])] for c in L4]
    out.append(render("S10", "Lagged volume: pre-milestone (ages 13–14) alone (Cox)", ["Covariate", "HR", "95% CI", "p"], rows,
                      f"*Note.* {hl('n = ' + n(c14['n']) + ' (' + n(c14['events']) + ' events); C-index = ' + format(c14['cindex'], '.3f') + '. Time zero is the end of the age-14 season, when the predictor window closes; the ' + str(RES['cox14']['n_excluded']) + ' athletes whose final active season was at 13 had left before time zero and are not at risk.')}"))
    # S11
    t = pd.read_csv(RERUN / "tableS12_exclude_zero_vol.csv")
    rows = [[NAMES[r["Covariate"]] if r["Covariate"] != "vol_milepael_z" else "**Volume at age 15–16 (z)**", f"{r['HR']:.2f}",
             ci(r["CI low"], r["CI high"]), p(r["p"])] for _, r in t.iterrows()]
    out.append(render("S11", "Sensitivity excluding zero-volume athletes (post-baseline Cox)", ["Covariate", "HR", "95% CI", "p"], rows,
                      f"*Note.* {hl('Excludes ' + str(K['primary_n'] - int(t['n'].iloc[0])) + ' athletes with vol_milestone = 0; remaining n = ' + n(t['n'].iloc[0]) + '; C-index = ' + format(t['C-index'].iloc[0], '.3f') + '. Follow-up starts at baseline, and having any volume at 15–16 requires remaining active to 15–16, so this restriction does not remove the survival conditioning of the post-baseline specification; descriptive only. The landmark analysis (Supplementary Table S8) is the appropriate check.')}"))
    # S12
    es = RES["es::log(1 + meets), all athletes"]
    nest = pd.read_csv(RERUN / "table5_auc_comparison.csv")
    rows = [["Total cohort", n(K["N"]), "All included athletes"],
            ["Sex known", n(K["sex_known"]), f"Gender M/F registered ({K['sex_unknown']} unknown; excluded from regression models except the mean-imputation check in Table S5, included in cohort totals and unstratified KM curves)"],
            ["Primary logistic L1–L4", n(K["primary_n"]), "Complete case on sex, Tyrving, HHI, pre-milestone volume; L1–L3 fitted on the same fixed sample for AUC comparability"],
            ["Level-vs-change (Table 4)", n(RES["t4"]["n"]), f"Of {K['active14']:,} athletes with ≥1 result at age 14; complete case on sex and Tyrving"],
            ["Contamination-free change model", n(RES["s19"]["n"]), f"Of {K['active16_two']:,} athletes with ≥2 results at age 16; complete case on sex"],
            ["Baseline-only Cox (Supplementary Tables S10, S16, S30)", n(RES["cox14"]["main"]["n"]),
             f"Time zero at the end of the age-14 season; excludes the {RES['cox14']['n_excluded']} athletes whose final active season was at 13"
             + (f" and {K['nosex_at_risk14']} without registered sex" if K['nosex_at_risk14'] else "")
             + "; the first-inactive-season definition in Table S30 also requires an active season at 14"],
            ["Landmark Cox at age 16", n(RES["lm16"]["n"]), f"Of {RES['lm16']['n_at_risk']:,} athletes still in their career at 16 (final active season at 16 or later); complete case on model covariates"],
            ["Performance-trajectory comparison (Table S15)", n(K["traj_n"]), "Complete case on Tyrving at both age 13 and age 14"],
            ["Nested predictor subsets (Table S17)", n(nest["n"].iloc[0]), "Complete case on all 22 candidate predictors"],
            ["Multiple imputation", n(K["sex_known"]), "All athletes with known sex; Tyrving imputed (m = 20)"],
            ["Within-athlete fixed-effects model (Table S28)", n(es["n_athletes"]), f"Athletes with ≥2 athlete-seasons at ages 13–19 up to and including the final active season ({es['n_obs']:,} athlete-seasons)"],
            ["Specialization confound models (S18 B/C)", " / ".join(n(x) for x in K["s18_n"][1:]), "Complete case on primary-category Tyrving"]]
    out.append(render("S12", "Analysis sample flow", ["Analysis", "n", "Definition"], rows,
                      "*Note.* One map of every analysis sample in the manuscript; each n is derivable from the row's definition."))
    # S13
    t = pd.read_csv(RERUN / "tableS13_structural_controls.csv")
    rows = [[f"**{NAMES[r['Covariate']]}**" if r["Covariate"] == "vol_pre_milepael_z" else NAMES[r["Covariate"]],
             f"{r['OR']:.2f}", ci(r["CI low"], r["CI high"]), p(r["p"])] for _, r in t.iterrows()]
    bq = pd.read_csv(TAB / "tableS13b_birth_quarter.csv")
    tt = t.set_index("Covariate")
    sig = [NAMES[c] for c in ["q1_born", "q4_born", "region_ostlandet", "region_midt", "klubb_storrelse_z"] if tt.loc[c, "p"] < .05]
    ctrl = ("All structural controls non-significant." if not sig else
            f"Of the structural controls only {', '.join(sig)} reached p < .05 (" + "; ".join(
                f"OR {tt.loc[c, 'OR']:.2f} {ci(tt.loc[c, 'CI low'], tt.loc[c, 'CI high'])}" for c in tt.index if NAMES.get(c) in sig) + ").")
    note = ("*Note.* " + hl(f"n = {K['primary_n']:,}. Panel A (as submitted): Q1 and Q4 indicators against Q2–Q3, the relative-age extremes; "
            f"the {K['no_birth_date']} athletes registered with birth year but no birth date (none of whom retained) fall in the reference group. "
            f"Pre-milestone volume effect unchanged: OR {tt.loc['vol_pre_milepael_z', 'OR']:.2f} with controls vs. "
            f"{RES['primary_L4']['vol_z'][0]:.2f} without. {ctrl}"
            + (f" Region could not be determined for {K['region_missing']} athletes, who fall in the reference region (western Norway)."
               if K["region_missing"] else "")))
    blockA = render("S13", "Primary logistic regression with structural controls (Panel A) and birth-quarter coding (Panel B)",
                    ["Covariate", "OR", "95% CI", "p"], rows, note)
    rowsB, prev = [], None
    for _, r in bq.iterrows():
        spec = r["Specification"].replace("Q2-Q3", "Q2–Q3").replace("1-4", "1–4")
        lr = r["LR test of quarter terms"].replace("chi2", "χ²")
        first = spec != prev
        rowsB.append([spec if first else "", NAMES.get(r["Covariate"], "Pre-milestone volume (z)") if r["Covariate"] != "vol_z" else "Pre-milestone volume (z)",
                      f"{r['OR']:.2f}", r["95% CI"], r["p"], lr if first else "", n(r["n"]) if first else ""])
        prev = spec
    blockB = ["**" + hl("Panel B. Birth-quarter specifications (all models include sex, Tyrving, HHI, volume, region and club size)") + "**", "",
              "| Specification | Covariate | OR | 95% CI | p | LR test of quarter terms | n |", "|---|---|---|---|---|---|---|"]
    for r in rowsB:
        blockB.append("| " + " | ".join(hl(str(c)) if str(c) else "" for c in r) + " |")
    lin = RES["bq::Linear trend across quarters 1-4, known quarter only"]
    full = RES["bq::Full coding: Q2, Q3, Q4 vs. Q1, known quarter only"]
    vols = [RES[k]["vol"][0] for k in RES if k.startswith("bq::")]
    bq_txt = (f"Conditional on performance and volume, relatively younger athletes were somewhat more likely to be retained "
              f"(linear trend OR {lin['q_lin'][0]:.2f} per quarter {ci(lin['q_lin'][1], lin['q_lin'][2])}, LR p = {p(lin['p'])}; "
              f"full coding p = {p(full['p'])}); the volume coefficient is unchanged ({min(vols):.2f}–{max(vols):.2f})."
              if lin["p"] < .05 else
              f"Birth quarter is unrelated to retention under every coding; the volume coefficient is unchanged ({min(vols):.2f}–{max(vols):.2f}).")
    out.append(blockA.replace("\n---\n", "\n" + "\n".join(blockB) + "\n\n" + hl(bq_txt) + "\n\n---\n", 1))
    # S14
    t = pd.read_csv(TAB / "table4_level_change_r1.csv")
    t = t[t["Sample"].str.startswith("Active at 14")]
    rows = []
    for model, g in t.groupby("Model", sort=False):
        for k, (_, r) in enumerate(g.iterrows()):
            orv, civ = r["OR per SD"].split(" ", 1)
            rows.append([("M1: Volume at age 14 only" if model.startswith("M1") else "M2: + Volume change 14→15") if k == 0 else "",
                         NAMES[r["Covariate"]], orv, civ, r["p"], f"{r['McFadden pseudo-R2']:.3f}" if k == 0 else "",
                         r["CV-AUC"] if k == 0 else ""])
    out.append(render("S14", f"Level-versus-change analysis details (athletes with ≥1 result at age 14; complete-case n = {RES['t4']['n']:,})",
                      ["Model", "Covariate", "OR", "95% CI", "p", "Pseudo-*R*²", "CV-AUC"], rows,
                      "*Note.* Full coefficient detail for main-text Table 4" + hl(", with repeated cross-validated AUC. Change = volume at 15 minus volume at 14.")))
    # S15
    d = lambda k: RES["dauc::" + k]  # noqa: E731
    ta, tc, vt = "Sex + volume vs. sex + Tyrving (time-aligned)", "Sex + volume vs. sex + Tyrving + Tyrving change 13-14", "Sex + Tyrving + volume vs. sex + volume"
    pc = "Sex + volume vs. sex + within-event percentile at the meet"
    rows = [["Sex + baseline Tyrving", n(d(ta)["n"]), f"{d(ta)['auc_a']:.3f}"],
            ["Sex + Tyrving + performance trajectory (Δ13–14)", n(d(tc)["n"]), f"{d(tc)['auc_a']:.3f}"],
            ["Sex + within-event percentile at the baseline meet", n(d(pc)["n"]), f"{d(pc)['auc_a']:.3f}"],
            ["Sex + pre-milestone volume", n(d(ta)["n"]), f"{d(ta)['auc_b']:.3f}"],
            ["Sex + pre-milestone volume (trajectory subsample)", n(d(tc)["n"]), f"{d(tc)['auc_b']:.3f}"],
            ["Sex + Tyrving + pre-milestone volume", n(d(vt)["n"]), f"{d(vt)['auc_b']:.3f}"]]
    out.append(render("S15", "Time-aligned behavior versus performance (repeated 5-fold CV-AUC)", ["Predictor set (all ages 13–14 measurements)", "n", "CV-AUC"], rows,
                      "*Note.* " + hl("Both predictors are observed during the baseline window (ages 13–14). "
                                      f"Volume versus baseline Tyrving: difference {dauc(ta)}; adding Tyrving to volume: {dauc(vt)}; "
                                      f"volume versus Tyrving with its within-baseline trajectory (subsample with Tyrving at both ages): {dauc(tc)}; "
                                      f"volume versus the within-event percentile at the meet: {dauc(pc)}. Differences with corrected 95% CIs: Supplementary Table S27.")))
    # S16
    cs = RES["cox14"]["structural"]
    covs16 = L4 + ["q1_born", "q4_born", "region_ostlandet", "region_midt", "klubb_storrelse_z"]
    rows = [[f"**{NAMES[c]}**" if c == "vol_z" else NAMES[c], f"{cs[c][0]:.2f}", ci(cs[c][1], cs[c][2]), p(cs[c][3])] for c in covs16]
    out.append(render("S16", "Cox time-to-cessation with structural controls (baseline-only predictors)", ["Covariate", "HR", "95% CI", "p"], rows,
                      f"*Note.* {hl('n = ' + n(cs['n']) + ' (' + n(cs['events']) + ' events); C-index = ' + format(cs['cindex'], '.3f') + '; time zero at the end of the age-14 season (Supplementary Table S10 note)')}. "
                      + ("Higher HHI (specialization) associated with lower dropout hazard." if cs["hhi_z"][2] < 1 else "HHI not associated with dropout hazard.")))
    # S17
    t = pd.read_csv(RERUN / "table5_auc_comparison.csv")
    labs = ["Baseline only (sex + Tyrving best)", "Specialization only (sex + HHI + n categories)", "Volume only (sex + meets ages 13–16)",
            hl("Volume + specialization (behavioral, ages 13–16)"), "Full model (all 22 predictors)"]
    rr = pd.read_csv(R1 / "_rerun" / "data" / "analysedata_utvidet.csv", low_memory=False)
    rr["female"] = (rr["gender"] == "F").astype(int)
    feats = ["female", "birth_year", "tyrving_best", "baseline_n_kategorier", "stevner_baseline_ar", "stevner_per_ar_tidlig",
             "hhi_early", "early_n_kategorier", "vol_age_13", "vol_age_14", "vol_age_15", "vol_age_16", "vol_milepael",
             "vol_pre_milepael", "vol_trend_milepael", "hhi_age_15", "hhi_change", "n_msk_typer", "um_15_16",
             "helaars_sum_13_16", "tyrving_peak_pre15", "tyrving_slope_13_16"]
    cc = rr.dropna(subset=feats + ["aktiv_senior"])
    rows = [[lab, str(r["n features"]), n(r["n"]), f"{r['AUC (logistic)']:.2f} (±{r['AUC SD (logistic)']:.2f})"] for lab, (_, r) in zip(labs, t.iterrows())]
    out.append(render("S17", "Cross-validated AUC for nested predictor subsets predicting senior retention", ["Predictor set", "n features", "n", "AUC (logistic)"], rows,
                      "*Note.* Descriptive comparison on the subsample with complete data on all 22 candidate predictors (" + hl("n = " + n(t["n"].iloc[0])) + "; see Supplementary Table S12). This table includes post-baseline behavioral predictors (ages 15–16) and therefore overlaps with the early portion of the at-risk window; AUCs are descriptive rather than ordinary prospective prediction quantities."
                      + hl(f" The complete-case requirement (which includes HHI at age 15) keeps only athletes who competed at 15 "
                           f"(senior retention {100 * cc['aktiv_senior'].mean():.1f}% vs. {100 * K['prevalence']:.1f}% in the cohort), so every row, "
                           "including the baseline-only one, is computed on a sample selected on later participation.")))
    # S18
    t = pd.read_csv(RERUN / "tableS18_specialization_confound.csv")
    rows = []
    ns = dict(zip("ABC", [n(x) for x in K["s18_n"]]))
    for model, g in t.groupby("Model", sort=False):
        key = model.split(":")[0][-1]
        for k, (_, r) in enumerate(g.iterrows()):
            first = {"A": "**A**: Primary L4 (with tyrving_best)", "B": "**B**: + Tyrving in primary category",
                     "C": "**C**: Tyrving main replaces tyrving_best"}[key] if k == 0 else (f"n = {ns[key]}" if k == 1 else "")
            hh = r["Covariate"] == "hhi_early_z"
            rows.append([first, f"**{NAMES[r['Covariate']]}**" if hh else NAMES[r["Covariate"]],
                         f"**{r['OR']:.2f}**" if hh else f"{r['OR']:.2f}", f"**{ci(r['CI low'], r['CI high'])}**" if hh else ci(r["CI low"], r["CI high"]),
                         f"**{p(r['p'])}**" if hh else p(r["p"])])
    out.append(render("S18", "Specialization-vs-performance confound check: does HHI proxy for performance in the primary event category?",
                      ["Model", "Covariate", "OR", "95% CI", "p"], rows,
                      "*Note.* " + hl(f"Correlations: HHI vs. Tyrving best, r = {K['s18_r']['best_hhi']:.2f}; HHI vs. Tyrving main category, "
                                      f"r = {K['s18_r']['main_hhi']:.2f}; Tyrving best vs. Tyrving main, r = {K['s18_r']['best_main']:.2f}. "
                                      + s18_summary(t))))
    # S19
    t = pd.read_csv(RERUN / "tableS20_exit_aligned.csv")
    s19 = RES["s19"]
    rows = [[r["Quantity"].replace("T-0", "T (final season;").replace("T (final season; (median [IQR])", "T (final season; median [IQR])")
             .replace("T-", "T−").replace("15-19", "15–19").replace(">=16", "≥16").replace("15->16", "15→16"), r["Value"].replace("-", "–"), n(r["n"])]
            for _, r in t.iterrows() if not r["Quantity"].startswith(("Dropouts", "Change model"))]
    rows += [["Change model among active at 16: volume at 15 (per SD)", f"OR {s19['level'][0]:.2f} {ci(s19['level'][1], s19['level'][2])}", n(s19["n"])],
             ["Change model among active at 16: change 15→16 (per SD increase)", f"OR {s19['change'][0]:.2f} {ci(s19['change'][1], s19['change'][2])}", n(s19["n"])],
             ["Change model among active at 16: change 15→16 (per SD decline)", hl(f"OR {s19['change_decline_or'][0]:.2f} {ci(s19['change_decline_or'][1], s19['change_decline_or'][2])}"), n(s19["n"])]]
    n_drop = int(t.loc[t["Quantity"].str.startswith("Dropouts"), "n"].iloc[0])
    out.append(render("S19", "Exit-aligned volume trajectories among dropouts", ["Quantity", "Value", "n"], rows,
                      "*Note.* Each dropout's volume history aligned to their own final active season (T; last calendar year with ≥2 results); dropouts with final seasons at ages 15–19 (n = " + n(n_drop) + "; T−3 observable only where final age ≥16). \"Reduced-but-nonzero\" = penultimate volume above zero but below the athlete's earlier personal peak. The change model is a logistic regression for senior status among athletes with ≥2 results at age 16 (CV-AUC = "
                      + hl(f"{s19['auc']:.3f}; change = volume at 16 minus volume at 15") + "); all predictors are measured by 16, so neither predictor can be the exit itself. See Supplementary Methods S-M6."))
    # S20
    t = pd.read_csv(TAB / "tableS20_hhi_stress_r1.csv")
    rows = [[r["Model"].replace(">=", "≥"), n(r["n"]), r["HHI OR"], f"{float(r['Volume OR']):.2f}"] for _, r in t.iterrows()]
    out.append(render("S20", "HHI count-dependence stress tests", ["Model", "n", "HHI OR [95% CI]", "Volume OR"], rows,
                      "*Note.* " + hl(f"HHI computed from results at ages 13–14. Spearman correlations: HHI vs. result count at ages 13–14 ρ = {RES['hhi_rho_res']:.2f}; "
                                      f"HHI vs. pre-milestone volume ρ = {RES['hhi_rho_vol']:.2f}.") + " The HHI–retention association is unchanged under count restrictions and the corrected index; it is not a small-count artifact. See Supplementary Methods S-M8."))
    # S21
    t = pd.read_csv(TAB / "tableS21_missing_data_r1.csv")
    rows = [[r["Data / model"],
             n(r["n"]), r["Volume OR"], r["HHI OR"], r["Tyrving OR"], "" if pd.isna(r["CV-AUC"]) else str(r["CV-AUC"])] for _, r in t.iterrows()]
    out.append(render("S21", "Missing data: complete-case and multiple-imputation estimates and predictive performance",
                      ["Data / model", "n", "Volume OR [95% CI]", "HHI OR [95% CI]", "Tyrving OR [95% CI]", "CV-AUC"], rows,
                      "*Note.* " + hl(("In the corrected data no sex-known athlete lacks a baseline score" if K['tyr_missing_known'] == 0 else
                                       f"In the corrected data only {K['tyr_missing_known']} sex-known athletes lack a baseline score")
                                      + ", so imputation and complete-case analysis coincide. "
                                      f"The lower rows repeat the analysis on the submitted analysis file (n = {RES['miss']['n_sub']:,}; Tyrving missing for "
                                      f"{RES['miss']['tyr_sub_missing_sexknown']} sex-known athletes, "
                                      f"{100 * RES['miss']['tyr_sub_missing_sexknown'] / (RES['miss']['n_sub'] - RES['sex_unknown']['n_submitted']):.1f}%): "
                                      "chained-equation imputation (m = 20) with the outcome in the imputation model leaves the estimates essentially unchanged, and predictive "
                                      "performance with imputation fitted inside each training fold (outcome excluded) equals the complete-case CV-AUC. "
                                      "Details: Supplementary Methods S-M3.")))
    # S22
    t = pd.read_csv(RERUN / "tableS23_club_effects.csv")
    pn = n(K["primary_n"])
    rows = [["ICC of pre-milestone volume across baseline clubs", f"{float(t.loc[0, 'Value']):.2f}", f"{pn} athletes, {K['clubs']} clubs"],
            ["Volume OR, primary (no club terms)", t.loc[1, "Value"], pn],
            ["Volume OR, club random intercepts (variational Bayes)", t.loc[2, "Value"], pn],
            ["HHI OR, club random intercepts (variational Bayes)", t.loc[3, "Value"], pn],
            [hl("Volume OR, club-clustered standard errors"), hl(fmt_or(RES["club_robust"]["cluster_vol"])), pn],
            [hl("Volume OR, population-averaged GEE (exchangeable within club)"),
             hl(fmt_or(RES["club_robust"]["gee_vol"]) + "; within-club correlation " + f"{RES['club_robust']['gee_rho']:.3f}".replace("-", "−")), pn],
            ["CV-AUC, folds grouped by club (20 repeats)", hl(f"{RES['cvproc_club']['auc']:.3f} [{RES['cvproc_club']['auc_lo']:.3f}, {RES['cvproc_club']['auc_hi']:.3f}]"), pn]]
    out.append(render("S22", "Club-level analyses", ["Quantity", "Value", "n"], rows,
                      "*Note.* A quarter of the variance in pre-milestone volume lies between clubs, but the within-club volume effect is, if anything, slightly larger than the pooled estimate" + hl(", club-clustered and population-averaged estimates give the same odds ratio with wider intervals, and discrimination is unchanged when validation clubs are held out of fitting. Variational Bayes can understate posterior uncertainty, so the random-intercept interval is likely too narrow; the clustered interval is the conservative one") + ": the association is not a club-supply artifact. See Supplementary Methods S-M7."))
    # S23
    c = RES["cvproc_athlete"]
    rows = [["Calibration slope", f"{c['slope']:.2f}"], [hl("Calibration-in-the-large"), f"{abs(c['citl']) if abs(c['citl']) < 0.005 else c['citl']:.2f}"],
            ["Brier score", f"{c['brier']:.3f}"], ["n", n(c["n"])]]
    out.append(render("S23", "Calibration of the primary model (cross-validated)", ["Metric", "Value"], rows,
                      "*Note.* " + hl("Out-of-fold predictions averaged over 20 repeats of stratified 5-fold cross-validation; calibration-in-the-large is the intercept of a logistic model with the linear predictor as offset.")))
    # S24
    t = pd.read_csv(RERUN / "tableS25_fixed_window_outcome.csv")
    r = t.iloc[0]
    rows = [["≥2 results in any season at ages 20–22", f"{float(r['Prevalence']):.3f}", f"{float(r['Cohort A']):.3f}", f"{float(r['Cohort B']):.3f}",
             r["Volume OR [95% CI]"], f"{float(r['CV-AUC']):.3f}", n(r["n"])]]
    out.append(render("S24", "Fixed-window outcome (ages 20–22)", ["Outcome", "Prevalence", "Cohort A", "Cohort B", "Volume OR [95% CI]", "CV-AUC", "n"], rows,
                      "*Note.* This outcome window is fully observable for every athlete in both cohorts, removing the follow-up asymmetry of the open-ended senior definition; results are near-identical to the primary model." + hl(f" Prevalences are for all {K['N']:,} athletes; the model uses the {K['primary_n']:,} with complete data. CV-AUC from a single stratified 5-fold split, as in the original analysis.")))
    # S25
    t = pd.read_csv(RERUN / "tableS26_missing_comparison.csv").set_index("Variable")
    rows = [["Senior retention", f"{100 * t.loc['aktiv_senior', 'Included (complete case)']:.1f}%", f"{100 * t.loc['aktiv_senior', 'Excluded (any missing)']:.1f}%"],
            ["Female", f"{100 * t.loc['female', 'Included (complete case)']:.1f}%", hl(f"— ({K['sex_unknown']} of {K['N'] - K['primary_n']} have no registered sex)")],
            ["Pre-milestone volume (mean meets)", f"{t.loc['vol_pre_milepael', 'Included (complete case)']:.1f}", f"{t.loc['vol_pre_milepael', 'Excluded (any missing)']:.1f}"],
            ["HHI, ages 13–14 (mean)", f"{t.loc['hhi_early', 'Included (complete case)']:.2f}", f"{t.loc['hhi_early', 'Excluded (any missing)']:.2f}"]]
    out.append(render("S25", "Included versus excluded athletes (complete-case comparison)", ["Variable", "Included (complete case)", "Excluded (any missing)"], rows,
                      "*Note.* " + hl(f"n = {K['primary_n']:,} included, {K['N'] - K['primary_n']} excluded ({K['sex_unknown']} without registered sex, "
                                      f"{K['tyr_missing_known']} without a baseline Tyrving score). The excluded athletes are too few to affect the estimates; "
                                      "multiple imputation gives identical results (Supplementary Table S21).")))
    # S26-S32 (new)
    t = pd.read_csv(TAB / "tableS26_cv_procedures.csv", dtype=str)
    rows = [[r["Procedure"].replace("standardised", "standardized"), n(r["n"]), r["CV-AUC"].replace("range 0.", "range 0.").replace("-0.", "–0."), r["Calibration slope"], r["Calibration-in-the-large"].replace("-0.00", "0.00"), r["Brier"]] for _, r in t.iterrows()]
    out.append(render("S26", "Cross-validation procedure: standardization inside folds and club-grouped folds",
                      ["Procedure", "n", "CV-AUC", "Calibration slope", "Calibration-in-the-large", "Brier"], rows,
                      "*Note.* Rows 1–2 use the variables and the single 5-fold split (seed 42) of the original submission. Because the logistic models are unpenalized, standardizing inside the training folds is an affine re-parameterization that leaves out-of-fold predictions unchanged; the two procedures therefore agree to the third decimal. Rows 3–4 use the corrected data and revised variables (HHI from ages 13–14; complete Tyrving scoring) with 20 repeats; club-grouped folds keep every baseline club (" + f"{K['clubs']} clubs; largest {K['club_max']} athletes" + ") entirely in either the training or the validation fold.", new=True))
    t = pd.read_csv(TAB / "tableS27_auc_differences.csv", dtype=str)
    rows = [[r["Comparison (B vs. A)"].replace("13-14", "13–14"), n(r["n"]), r["CV-AUC A"], r["CV-AUC B"], r["Difference (B - A)"].replace("-", "−"), r["95% CI"].replace("-", "−"), r["p"]] for _, r in t.iterrows()]
    out.append(render("S27", "Differences in cross-validated AUC between models (paired, identical folds)",
                      ["Comparison (B vs. A)", "n", "CV-AUC A", "CV-AUC B", "Difference", "95% CI", "p"], rows,
                      "*Note.* Both models are fitted and validated on the same 100 folds (stratified 5-fold, 20 repeats); the difference is the mean of the 100 fold-level differences, with 95% CI and p from the corrected resampled t-statistic (Nadeau & Bengio, 2003), which inflates the variance for the overlap between training sets.", new=True))
    t = pd.read_csv(TAB / "tableS28_event_study.csv")
    rows = []
    for _, r in t.iterrows():
        if r["Outcome / sample"].startswith("meets (linear)"):
            eff = f"{r['Meets']:.1f} meets".replace("-", "−")
        else:
            eff = f"{int(r['As % change in (1 + meets)'])}%".replace("-", "−")
        rows.append([r["Outcome / sample"].replace("log(1 + meets)", "log(1 + meets)").replace("17-19", "17–19"), r["Season"].replace("T-", "T−"),
                     f"{r['Estimate']:.3f}".replace("-", "−"), r["95% CI"].replace("-", "−"), eff, r["p"], n(r["athletes"]), n(r["athlete-seasons"])])
    out.append(render("S28", "Within-athlete decline before exit: athlete and age fixed-effects model",
                      ["Outcome / sample", "Season", "Estimate", "95% CI", "Effect", "p", "Athletes", "Athlete-seasons"], rows,
                      "*Note.* Linear model with athlete fixed effects (within transformation), age fixed effects (ages 13–19), and indicators for the final active season (T) and the three preceding seasons of athletes whose exit was observed (final active season before 2024); seasons after the final active season are excluded, and the seasons of athletes still active, or more than three seasons before exit, form the reference. Estimates are deviations from the athlete's own reference-period volume net of the common age profile; for log(1 + meets) the effect column gives 100 × (exp(β) − 1). Standard errors are cluster-robust by athlete. The decline steepens towards exit (Wald test T−1 = T−3, p < .001). The final-season estimate is partly mechanical (the last season with ≥2 results is often a partial season). See Supplementary Methods S-M6 and Supplementary Figure S5.", new=True))
    t = pd.read_csv(TAB / "tableS29_threshold_validation.csv")
    rows = [[r["Analysis"].replace("'", "’"), f"< {r['Threshold (vol <)']}", n(r["n"]), r["Flagged %"], r["Sensitivity"], r["Specificity"], r["PPV"],
             r["Retention, flagged"], r["Retention, unflagged"]] for _, r in t.iterrows()]
    out.append(render("S29", "Early-warning thresholds derived in one birth cohort and validated in the other",
                      ["Analysis", "Threshold (meets)", "n", "Flagged %", "Sensitivity", "Specificity", "PPV", "Retention, flagged", "Retention, unflagged"], rows,
                      "*Note.* Cohort A: births 1998–2000; Cohort B: births 2001–2002. Lowest-quartile rule: flag athletes at or below the 25th percentile of pre-milestone volume in the derivation cohort (" + f"≤ {RES['thr_quartile']['cut_A'] - 1} meets in Cohort A, i.e. < {RES['thr_quartile']['cut_A']}; ≤ {RES['thr_quartile']['cut_B'] - 1} in Cohort B, i.e. < {RES['thr_quartile']['cut_B']}" + "). Youden’s J maximizes sensitivity + specificity − 1 over cut-offs 2–40. Brackets: 2,000-replicate bootstrap 95% CIs within the evaluation cohort; rows with the same cohort and cut-off are one computation" + (" (the lowest-quartile cut-off is < 10 in both cohorts, so the quartile rows and the candidate rows coincide)" if RES['thr_quartile']['cut_A'] == RES['thr_quartile']['cut_B'] == 10 else "") + ". Sensitivity and PPV refer to identifying athletes who did not retain senior activity.", new=True))
    t = pd.read_csv(TAB / "tableS30_gaps_outcome_definitions.csv")
    g = RES["gaps"]
    rows = [[r["Event definition"].replace(">=", "≥"), n(r["n"]), n(r["events"]), r["Volume HR per SD [95% CI]"], f"{float(r['HHI HR per SD']):.2f}", f"{float(r['C-index']):.3f}"] for _, r in t.iterrows()]
    out.append(render("S30", "Temporary gaps, returns, and alternative event definitions (baseline-only Cox model)",
                      ["Event definition", "n", "Events", "Volume HR per SD [95% CI]", "HHI HR per SD", "C-index"], rows,
                      f"*Note.* All models include sex, Tyrving, HHI (ages 13–14), and pre-milestone volume. An active season is a calendar year with ≥2 results. {100 * g['any_gap']:.1f}% of athletes ({g['n_any_gap']}) had at least one inactive season followed by a return, {100 * g['gap2plus_return']:.1f}% ({g['n_gap2plus']}) a gap of two or more seasons followed by a return, and {100 * g['gap3plus_return']:.1f}% a gap of three or more. Of {n(g['n_two_inactive'])} athletes with an active season in 2019 or earlier followed by two missed seasons, {100 * g['return_after_two_inactive']:.1f}% ever returned (at least four later seasons observable). Under the primary definition such returns are part of a continuing career; the alternative definitions instead end the spell at the first two-season gap or at the first inactive season (censored if no such pattern is observed through 2025). The first-inactive-season definition also requires an active season at 14, the season before time zero, which explains its smaller n.", new=True))
    t = pd.read_csv(TAB / "tableS31_target_population.csv")
    rows = [[r["Group"].replace(">=", "≥").replace("1998-2002", "1998–2002").replace("13-14", "13–14"), n(r["n"]), r["Female %"],
             r["Meets at 13-14, median [IQR]"].replace("-", "–"), r[">= 10 meets at 13-14 (%)"], r["Senior retention %"],
             r["Volume OR per 10 meets (sex-adjusted)"], f"{float(r['CV-AUC (sex + volume)']):.3f}"] for _, r in t.iterrows()]
    out.append(render("S31", "The cohort within the register population of the same birth years",
                      ["Group", "n", "Female %", "Meets at 13–14, median [IQR]", "≥10 meets at 13–14 (%)", "Senior retention %", "Volume OR per 10 meets", "CV-AUC (sex + volume)"], rows,
                      f"*Note.* All athletes born 1998–2002 with at least one registered result at ages 13–14, from the register as it stood at the data extraction (rows registered by 18 May 2026; results through 2025), with cohort membership defined as in the main analyses. The cohort comprises {100 * RES['pop_share_cohort']:.0f}% of these athletes but {100 * RES['pop_share_active10_in_cohort']:.0f}% of those with ten or more meets at 13–14 and {100 * RES['pop_share_seniors_from_cohort']:.0f}% of the {RES['pop_n_seniors']} who later had an active senior season. Meets are competition days, as in the main analyses; for cohort members the register counts reproduce the analysis data closely (mean {RES['pop_check']['vol_mean_register']:.1f} vs. {RES['pop_check']['vol_mean_analysis']:.1f} meets; senior retention {100 * RES['pop_check']['senior_register']:.1f}% vs. {100 * RES['pop_check']['senior_analysis']:.1f}%), the small differences reflecting rows re-registered after the extraction. Senior retention: ≥2 results in a calendar year at age 20 or later.", new=True))
    t = pd.read_csv(TAB / "tableS32_volume_by_performance.csv")
    rows = [[r["Baseline Tyrving quartile"], r["Senior retention, volume above median"], r["Senior retention, volume at or below median"]] for _, r in t.iterrows()]
    out.append(render("S32", "Senior retention by baseline performance quartile and pre-milestone volume",
                      ["Baseline Tyrving quartile", "Retention, volume above median", "Retention, volume at or below median"], rows,
                      f"*Note.* Median pre-milestone volume = {TXT['vol_median']:.0f} meets. Above-median volume is associated with higher senior retention in every performance quartile.", new=True))
    return "\n".join(out)


def main():
    head = ("# Tables\n\n(Submitted as editable text; in the final Word manuscript, each table on its own page after the "
            "references. Supplementary Tables S1–" + hl("S32") + " follow as supplementary material.)\n\n---\n\n")
    body = "".join([table1(), table2(), table3(), table4(), table5(), table6(), table7()])
    text = head + body + "\n" + supp()
    (R1 / "manuscript" / "11_tables.md").write_text(text)
    print("wrote 11_tables.md:", text.count("## Table"), "tables;", text.count("{+"), "highlighted spans")


if __name__ == "__main__":
    main()
