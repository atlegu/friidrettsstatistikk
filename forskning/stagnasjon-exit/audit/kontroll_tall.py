"""
kontroll_tall.py — A1-audit fase 4: hvert tall i manus og svarbrev mot modell- og datafilene.

Kjøres etter 03–07 (og R-kontrollene audit/sammenlign.py og audit/delong_bro.R). Ankrede
fraser bygget fra filene; dekningskontroll av alle tall; sitatkontroll av brevet.
Tallene fra følgestudiene (OR 2,04; 12/23 %; trend 1,16) er kontrollert mot IJSSC-manuset
(ncc-kohort/IJSSC_R1_opplasting/MANUSCRIPT_R1_clean.docx) og står som eksterne fakta.
"""

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as scst

HER = Path(__file__).resolve().parent
PROSJ = HER.parent
sys.path.insert(0, str(PROSJ.parent))
from audit_felles import Kontroll, avrund as f, ordtelling, sitatkontroll  # noqa: E402

MOD, ROB, TABM, DATA = (PROSJ / "tables" / "modeller", PROSJ / "tables" / "robusthet",
                        PROSJ / "tables" / "manus", PROSJ / "data_private")


def les(mappe, n, **kw):
    return pd.read_csv(mappe / n, **kw)


flyt = json.loads((DATA / "flyt.json").read_text())
ad = pd.read_csv(DATA / "analysedata.csv")
prim = ad[ad["kohort_primar"] & ad["skaarbar"] & ~ad["liten_gruppecelle"]]
ret, dro = prim[prim["senior"] == 1], prim[prim["senior"] == 0]
h1 = les(MOD, "h1_or.csv")
auc = les(MOD, "h1_auc.csv").set_index("modell")
kal = les(MOD, "kalibrering.csv").iloc[0]
h2 = les(MOD, "h2_interaksjon.csv")
h3 = les(MOD, "h3_auc.csv").set_index("modell")
dl = les(MOD, "r1_delong.csv").set_index("kontrast")
med = les(MOD, "r1_mediering.csv").set_index("modell")
dpk = les(MOD, "r1_delta_per_kvartal.csv").set_index("kvartal")
mo = les(MOD, "r1_moderasjon.csv")
def tall_eller_tekst(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return x


sd = les(MOD, "r1_sd_og_andeler.csv", index_col=0)["verdi"].map(tall_eller_tekst)
sw = les(MOD, "r1_switcher_flyt.csv", index_col=0)["verdi"].map(tall_eller_tekst)
fn = les(MOD, "r1_fig1_n_per_alder.csv").set_index("alder")
rob = les(ROB, "robusthet_or.csv")
cox = les(ROB, "cox_landmark.csv").set_index("covariate")
ev = les(ROB, "e_verdi.csv").iloc[0]
f1 = les(TABM, "fig1_data.csv")
f2 = les(TABM, "fig2_data.csv")
f3 = les(TABM, "fig3_data.csv")


def orv(modell, var):
    return h1[(h1["modell"] == modell) & (h1["variabel"] == var)].iloc[0]


def ki(t, d=2, o="OR", lo="KI_lav", hi="KI_hoy"):
    return f"{f(t[o], d)} ({f(t[lo], d)}--{f(t[hi], d)})"


def robr(an, eks=None, utf=None):
    m = rob["analyse"] == an
    if eks:
        m &= rob["eksponering"] == eks
    if utf:
        m &= rob["utfall"] == utf
    return rob[m].iloc[0]


def moder(an, var="delta_z"):
    return mo[(mo["analyse"] == an) & (mo["variabel"] == var)].iloc[0]


def pst(x, d=1):
    return f(100 * x, d)


k = Kontroll(PROSJ / "manus" / "main.tex", "A1 manus")


def krav(b, hvorfor):
    if b:
        k.n_ok += 1
    else:
        k.feil.append(f"PÅSTAND holder ikke: {hvorfor}")


m2d = orv("M2", "delta_z")
dlm, dlh = dl.loc["M2_minus_M1"], dl.loc["volum+fremgang_minus_volum+niva"]
kvint = mo[mo["analyse"] == "delta_kvintiler_vs_Q1"].set_index("variabel")["OR"]
inter = h2[(h2["modell"] == "H2_interaksjon") & (h2["variabel"] == "delta_x_kvartal")].iloc[0]
s12 = h2[(h2["modell"] == "H2_strata_Q1-Q2") & (h2["variabel"] == "delta_z")].iloc[0]
s34 = h2[(h2["modell"] == "H2_strata_Q3-Q4") & (h2["variabel"] == "delta_z")].iloc[0]
ols = med.loc["delta_z_paa_kvartal_c_OLS"]
p_ols = 2 * (1 - scst.norm.cdf(abs(ols["OR_per_kvartal"] / ((ols["KI_hoy"] - ols["KI_lav"]) / 3.92))))
krav(p_ols < 0.001, f"mediering p < 0.001 ({p_ols:.2e})")
nk = robr("eksponeringsvariant", "delta_nk_1314_z")
a_, b_ = robr("kohort_A"), robr("kohort_B")
fig2p = f2[f2["panel"] == "Age-graded performance"].set_index("t")
fig2v = f2[f2["panel"] == "Competition volume"].set_index("t")

# ================================================================ ABSTRACT + KEY POINTS
k.need("abstract", f"(n = {flyt['primaerutvalg_fodt_1998_2005']}; {pst((prim['gender'] == 'F').mean(), 0)}% female; "
       f"{flyt['primaerutvalg_seniorer']} [{pst(prim['senior'].mean())}%] later active as seniors", "utvalg")
k.need("abstract", f"OR = {f(m2d['OR'], 2)} per SD (95% CI {f(m2d['KI_lav'], 2)}--{f(m2d['KI_hoy'], 2)}; "
       f"one SD ≈ {f(sd['sd_delta_poeng_pooled'], 0)} age-graded points)", "H1")
k.need("abstract", f"(cross-validated AUC {f(auc.loc['M1', 'cv_auc'], 3)} to {f(auc.loc['M2', 'cv_auc'], 3)}; "
       f"paired DeLong 95% CI for the difference {f(dlm['ki_lav'], 3)}--{f(dlm['ki_hoy'], 3)})", "AUC")
k.need("abstract", f"(OR {f(a_['OR'], 2)} and {f(b_['OR'], 2)})", "kohorter")
k.need("abstract", f"specification check was null (OR {f(nk['OR'], 2)})", "spesifikasjonssjekk")
k.need("abstract", f"The E-value was {f(ev['E_verdi_punkt'], 2)}", "E-verdi")
k.need("abstract", f"fell {f(-fig2p.loc['T-1', 'median'], 0)} below their own level in the penultimate season and "
       f"{f(-fig2p.loc['T-0', 'median'], 0)} ---", "slide")
k.need("abstract", f"{pst(sd['andel_negativ_delta_dropouts'])}% of future dropouts versus "
       f"{pst(sd['andel_negativ_delta_retainers'])}% of retainers", "negativ Δ")
k.need("abstract", f"(OR {f(inter['OR'], 2)}, 95% CI {f(inter['KI_lav'], 2)}--{f(inter['KI_hoy'], 2)})", "H2")
k.need("abstract", f"older (OR {f(s12['OR'], 2)}) and relatively younger athletes (OR {f(s34['OR'], 2)})", "strata")
k.need("abstract", f"(+{f(ols['OR_per_kvartal'], 2)} SD per quarter, p < 0.001)", "mediering")
k.need("abstract", f"(OR {f(med.loc['uten_delta', 'OR_per_kvartal'], 2)} to {f(med.loc['med_delta', 'OR_per_kvartal'], 2)})",
       "trend")
k.need("abstract", f"(DeLong p = {f(dlh['p'], 2)})", "H3")
for s in ["(2.04 per SD)"]:
    k.need("abstract", s, "følgestudien (IJSSC-manus)")
k.need("key points", f"following {flyt['primaerutvalg_fodt_1998_2005']} athletes", "KP utvalg")
k.need("key points", f"odds ratio of {f(m2d['OR'], 1)} per SD", "KP OR")
k.need("key points", "(2.04 per SD)", "følgestudien")
k.need("key points", f"fell {f(-fig2p.loc['T-1', 'median'], 0)} points below their own earlier level in the penultimate "
       f"season and {f(-fig2p.loc['T-0', 'median'], 0)} points", "KP slide")

# ================================================================ BACKGROUND (følgestudier)
k.need("background", "discriminated senior retention somewhat less well than a simple behavioural signal", "IJSSC: «somewhat better»")
k.need("background", "though it added complementary information", "IJSSC: OR 1.75")
for s in ["fell 12% below their own earlier level two seasons before exit and 23% one season before",
          "a 14-year cohort study", "established at age 10 and stable to age 25"]:
    k.need("background", s, "følgestudie (IJSSC/RAE-manus)")

# ================================================================ METHODS
k.need("methods", f"(n = {flyt['utovere_fodt_1998_2006']}); {flyt['ok_resultat_13_14']} had at least one", "flyt 1")
k.need("methods", f"was met by {flyt['landmark_13_14_og_15_16']} athletes, of whom {flyt['landmark_med_kjonn']} had known sex",
       "flyt 2")
k.need("methods", f"We excluded {flyt['uten_skaarbar_tyrving_i_hovedgruppen']} athletes", "flyt 3")
k.need("methods", f"and {flyt['ekskludert_gruppecelle_under_20']} athletes in sex × event-group cells with fewer than 20",
       "flyt 4")
k.need("methods", f"The primary sample comprises {flyt['primaerutvalg_fodt_1998_2005']} athletes", "flyt 5")
k.need("methods", f"Of the primary sample, {flyt['primaerutvalg_seniorer']} ({pst(prim['senior'].mean())}%)", "flyt 6")
krav(int(sd["primaer_uten_kvartal"]) == 27 and int(med.loc["uten_delta", "n"]) == 3781, "27 uten fødselsdato / 3781")
k.need("methods", f"Within the primary sample, {int(sd['primaer_uten_kvartal'])} athletes lacked an exact birth date and were "
       f"excluded from the birth-quarter analyses only (n = {int(med.loc['uten_delta', 'n'])}); in the wider landmark sample "
       f"the corresponding number is {flyt['landmark_uten_fodselsdato']}", "fødselsdato")
lo_c, hi_c = str(sd["sd_delta_poeng_cellespenn"]).replace("–", "-").split("-")
k.need("methods", f"approximately {f(sd['sd_delta_poeng_pooled'], 0)} age-graded points for progression (range "
       f"{lo_c}--{hi_c} across sex × event-group cells), {f(sd['sd_niva_poeng'], 0)} points for baseline level, and "
       f"{f(sd['sd_vol1314_dager'], 0)} competition days for each volume window", "SD-skala")
krav(f(sd["sd_vol1314_dager"], 0) == f(sd["sd_vol1516_dager"], 0), "begge volumvinduer ~17 dager")
krav(ad["region"].isna().all(), "region er NA for alle (A1-1)")
k.need("methods", "the registry records the competition district for under 1% of meets", "region")
k.need("methods", f"common ({pst(prim['senior'].mean())}%)", "utfallsandel")
k.need("methods", f"with p$_0$ = {f(ev['utfallsandel'], 2)}", "p0")
import sklearn, lifelines, statsmodels  # noqa: E402,E401
k.need("methods", f"Python {sys.version.split()[0]} with pandas {pd.__version__}, numpy {np.__version__}, statsmodels "
       f"{statsmodels.__version__}, scikit-learn {sklearn.__version__} and lifelines {lifelines.__version__}", "versjoner")
k.need("methods", "stratified 5-fold cross-validation repeated 20 times", "CV-oppsett (03: 5×20)")

# ================================================================ RESULTS
k.need("results", f"(median {f(ret['vol1314'].median(), 0)} vs. {f(dro['vol1314'].median(), 0)} competition days)", "dager")
krav(1.9 <= ret["vol1314"].median() / dro["vol1314"].median() <= 2.4, "«twice as often»")
k.need("results", f"(median {f(ret['niva_w1'].median(), 0)} vs. {f(dro['niva_w1'].median(), 0)} age-graded points)", "poeng")
k.need("results", f"rose to {f(ret['niva_w2'].median(), 0)} while dropouts' fell to {f(dro['niva_w2'].median(), 0)}", "W2")
k.need("results", f"progression was +{f(ret['delta'].median(), 0)} points against {f(dro['delta'].median(), 0)}", "Δ median")
g1 = f1.set_index(["senior", "alder"])["median"]
k.need("results", f"(median {f(g1[(1, 13)], 0)} points at 13, {f(g1[(1, 16)], 0)} at 16)", "fig1 retainers")
k.need("results", f"started about 100 points lower (median {f(g1[(0, 13)], 0)} at 13)", "fig1 dropouts 13")
krav(90 <= g1[(1, 13)] - g1[(0, 13)] <= 110, "«about 100 points lower» ved 13")
k.need("results", f"({f(g1[(0, 16)], 0)} at 16, {f(g1[(0, 18)], 0)} at 18)", "fig1 dropouts sen")
k.need("results", f"Exact birth dates exist for {int(med.loc['uten_delta', 'n'])} of the {len(prim)} "
       f"({pst(int(med.loc['uten_delta', 'n']) / len(prim))}%); among these, the full quarter distribution is Q1 "
       f"{pst(sd['kvartal_Q1'])}, Q2 {pst(sd['kvartal_Q2'])}, Q3 {pst(sd['kvartal_Q3'])}, Q4 {pst(sd['kvartal_Q4'])}%", "kvartaler")
k.need("results", f"the dropout curve rests on {int(fn.loc[13, 'dropouts'])} athletes at 13, {int(fn.loc[15, 'dropouts'])} at 15, "
       f"{int(fn.loc[17, 'dropouts'])} at 17 and {int(fn.loc[18, 'dropouts'])} at 18, while the retainer curve spans "
       f"{int(fn.loc[[13, 14], 'retainers'].min())}--{int(fn.loc[[13, 14], 'retainers'].max())} at 13--14 and "
       f"{int(fn.loc[18, 'retainers'])} at 18", "fig1 n")
k.need("results", f"gave OR = {f(m2d['OR'], 2)} per SD (95% CI {f(m2d['KI_lav'], 2)}--{f(m2d['KI_hoy'], 2)}; $p < .001$)", "H1 tekst")
krav(m2d["p"] < 0.001, "H1 p < .001")
v15 = orv("M2", "vol1516_g")
k.need("results", f"(OR {f(v15['OR'], 2)} per SD, 95% CI {f(v15['KI_lav'], 2)}--{f(v15['KI_hoy'], 2)})", "volum 15-16")
k.need("results", f"given later volume (OR {f(orv('M2', 'vol1314_g')['OR'], 2)})", "volum 13-14")
gm = orv("M2", "gender_M")
k.need("results", f"(OR {f(1 / gm['OR'], 2)}, 95% CI {f(1 / gm['KI_hoy'], 2)}--{f(1 / gm['KI_lav'], 2)}; a conditional", "kvinner")
k.need("results", f"rose from {f(orv('M1', 'niva_w1_z')['OR'], 2)} in M1 to {f(orv('M2', 'niva_w1_z')['OR'], 2)} in M2", "nivå M1/M2")
k.need("results", f"rose from AUC {f(auc.loc['M1', 'cv_auc'], 3)} (M1) to {f(auc.loc['M2', 'cv_auc'], 3)} (M2), a gain of "
       f"{f(dlm['diff'], 3)} (paired DeLong 95% CI {f(dlm['ki_lav'], 3)}--{f(dlm['ki_hoy'], 3)}, p = {f(dlm['p'], 3)}; spread "
       f"across CV repetitions {f(auc.loc['M2-M1', 'p2_5'], 3)}--{f(auc.loc['M2-M1', 'p97_5'], 3)}), with good calibration "
       f"(slope {f(kal['kalibreringsslope'], 2)}; Brier {f(kal['brier'], 3)})", "diskriminering")
k.need("results", f"quintiles 2--5 were {f(kvint['dq_Q2'], 2)}, {f(kvint['dq_Q3'], 2)}, {f(kvint['dq_Q4'], 2)} and "
       f"{f(kvint['dq_Q5'], 2)}", "kvintiler")
krav(kvint.is_monotonic_increasing, "kvintil-OR monotone")
f3p = f3.pivot(index="kvintil", columns="voltertil", values="andel_pst")
f3m = f3.groupby("voltertil")[["vol_min", "vol_maks"]].first()
k.need("results", f"(≥{int(f3m.loc['High volume 15–16', 'vol_min'])} competition days over ages 15--16), senior retention rose from "
       f"{f(f3p.loc[1, 'High volume 15–16'], 1)}% in the lowest progression quintile to {f(f3p.loc[5, 'High volume 15–16'], 1)}% "
       f"in the highest; within the middle tertile from {f(f3p.loc[1, 'Mid volume 15–16'], 1)}% to "
       f"{f(f3p.loc[5, 'Mid volume 15–16'], 1)}%. In the lowest-volume tertile (≤{int(f3m.loc['Low volume 15–16', 'vol_maks'])} days) "
       f"retention was {f(f3p['Low volume 15–16'].min(), 1)}--{f(f3p['Low volume 15–16'].max(), 1)}%", "fig3")
k.need("results", f"equal-sized tertiles by rank: {int(f3m.loc['Low volume 15–16', 'vol_min'])}--"
       f"{int(f3m.loc['Low volume 15–16', 'vol_maks'])}, {int(f3m.loc['Mid volume 15–16', 'vol_min'])}--"
       f"{int(f3m.loc['Mid volume 15–16', 'vol_maks'])} and {int(f3m.loc['High volume 15–16', 'vol_min'])}--"
       f"{int(f3m.loc['High volume 15–16', 'vol_maks'])} competition days", "fig3 tertiler")
k.need("results", "boundary values 5 and 19 split", "fig3 grenseverdier")
nt = {t: moder(f"nivastrata_{t}") for t in ["lav", "midt", "hoy"]}
ni = moder("nivainteraksjon", "delta_x_niva")
k.need("results", f"OR {ki(nt['lav'])} in the lowest, {ki(nt['midt'])} in the middle and {ki(nt['hoy'])} in the highest tertile, "
       f"with a non-significant progression × level interaction (OR {f(ni['OR'], 2)}, {f(ni['KI_lav'], 2)}--{f(ni['KI_hoy'], 2)})",
       "nivåstrata")
kf, km = moder("kjonnsstrata_F"), moder("kjonnsstrata_M")
kxi = moder("kjonnsinteraksjon", "delta_x_kvinne")
k.need("results", f"OR {ki(kf)} in women and {ki(km)} in men, interaction OR {f(kxi['OR'], 2)} ({f(kxi['KI_lav'], 2)}--"
       f"{f(kxi['KI_hoy'], 2)})", "kjønn")
k.need("results", f"(n = {flyt['primaerutvalg_fodt_1998_2005']}; {flyt['primaerutvalg_seniorer']} events)", "tabell 2 tittel")
k.need("results", f"(OR {f(inter['OR'], 2)} per quarter, 95% CI {f(inter['KI_lav'], 2)}--{f(inter['KI_hoy'], 2)}, $p$ = "
       f"{f(inter['p'], 2)})", "H2 tekst")
k.need("results", f"OR {ki(s12)} among athletes born in Q1--Q2 and {ki(s34)} among those born in Q3--Q4", "H2 strata")
k.need("results", f"from {f(dpk.loc[1, 'delta_poeng_median'], 1)} points (Q1) to +{f(dpk.loc[4, 'delta_poeng_median'], 1)} "
       f"points (Q4), a gradient of +{f(ols['OR_per_kvartal'], 2)} SD per quarter (p < 0.001)", "mediering tekst")
krav(dpk["delta_poeng_median"].is_monotonic_increasing, "median Δ monoton over kvartaler")
u, w = med.loc["uten_delta"], med.loc["med_delta"]
k.need("results", f"OR {f(u['OR_per_kvartal'], 2)} per quarter ({f(u['KI_lav'], 2)}--{f(u['KI_hoy'], 2)}) without progression", "trend uten")
k.need("results", "weaker than the 1.16 reported in the companion cohort", "følgestudien")
k.need("results", f"attenuated to {f(w['OR_per_kvartal'], 2)} ({f(w['KI_lav'], 2)}--{f(w['KI_hoy'], 2)}) when progression", "trend med")
k.need("results", f"cross-validated AUC {f(h3.loc['volum+fremgang', 'cv_auc'], 3)} with progression versus "
       f"{f(h3.loc['volum+niva', 'cv_auc'], 3)} with level (paired DeLong difference {f(dlh['diff'], 3)}, 95% CI "
       f"{f(dlh['ki_lav'], 3)} to {f(dlh['ki_hoy'], 3)}, p = {f(dlh['p'], 2)}; repetition spread {f(h3.loc['differanse', 'p2_5'], 3)} "
       f"to {f(h3.loc['differanse', 'p97_5'], 3)})", "H3 tekst")
k.need("results", f"(median +{f(fig2p.loc['T-2', 'median'], 1)} points against the season three years before exit, 95% CI "
       f"{f(fig2p.loc['T-2', 'ki_lav'], 1)} to +{f(fig2p.loc['T-2', 'ki_hoy'], 1)}; n = {int(fig2p.loc['T-2', 'n'])}", "slide T-2")
k.need("results", f"it fell {f(-fig2p.loc['T-1', 'median'], 1)} points below (CI {f(fig2p.loc['T-1', 'ki_lav'], 1)} to "
       f"{f(fig2p.loc['T-1', 'ki_hoy'], 1)}) --- about {f(-fig2p.loc['T-1', 'median'] / sd['sd_delta_poeng_pooled'], 2)} progression-SDs",
       "slide T-1")
k.need("results", f"in the final season {f(-fig2p.loc['T-0', 'median'], 1)} points below (CI {f(fig2p.loc['T-0', 'ki_lav'], 1)} to "
       f"{f(fig2p.loc['T-0', 'ki_hoy'], 1)})", "slide T0")
k.need("results", f"(median {f(fig2v.loc['T-1', 'median'], 0)} days in the penultimate and {f(fig2v.loc['T-0', 'median'], 0)} days in "
       f"the final season; n = {int(fig2v.loc['T-1', 'n'])})", "slide volum")
k.need("results", f"{pst(sd['andel_negativ_delta_dropouts'])}% of future dropouts had negative progression across the two windows, "
       f"against {pst(sd['andel_negativ_delta_retainers'])}% of retainers", "negativ Δ tekst")
k.need("results", f"(points; n = {int(fig2p.loc['T-2', 'n'])} of the {int(fig2p.loc['T-2', 'n_kandidater'])} non-censored "
       f"dropouts with a final season at 16--19", "fig2 tekst")
k.need("results", f"Right: competition volume (days; n = {int(fig2v.loc['T-1', 'n'])})", "fig2 volum")
k.need("results", f"(HR {f(cox.loc['delta_z', 'exp(coef)'], 2)} per SD, 95% CI {f(cox.loc['delta_z', 'exp(coef) lower 95%'], 2)}--"
       f"{f(cox.loc['delta_z', 'exp(coef) upper 95%'], 2)}), alongside level (HR {f(cox.loc['niva_w1_z', 'exp(coef)'], 2)}), "
       f"dominant later volume (HR {f(cox.loc['vol1516_g', 'exp(coef)'], 2)} per SD), null earlier volume given later "
       f"(HR {f(cox.loc['vol1314_g', 'exp(coef)'], 2)}), and a higher hazard for women (HR {f(cox.loc['kvinne', 'exp(coef)'], 2)}, "
       f"95% CI {f(cox.loc['kvinne', 'exp(coef) lower 95%'], 2)}--{f(cox.loc['kvinne', 'exp(coef) upper 95%'], 2)})", "Cox")
mx, vi = robr("eksponeringsvariant", "delta_max_z"), robr("eksponeringsvariant", "delta_vind_z")
k.need("results", f"(season best {f(mx['OR'], 2)}; wind-legal marks {f(vi['OR'], 2)};", "eksponeringsvarianter")
krav(int(sw["prim_uten_bg2"]) == 94, "94 primærutøvere faller ut")
krav(int(sw["prim_i_modell"]) + int(sw["ekskluderte_734_i_modell"]) == int(sw["inklusiv_n"]),
     "inklusivt utvalg: primær med bg2 + gjenvunne i modell = n")
krav(len(prim) - int(sw["prim_uten_bg2"]) == int(sw["prim_i_modell"]), "3808 − 94 = 3714")
k.need("results", f"n = {int(sw['inklusiv_n'])}, recovering {int(sw['ekskluderte_734_i_modell'])} of the "
       f"{flyt['uten_skaarbar_tyrving_i_hovedgruppen']} excluded from the primary definition while {int(sw['prim_uten_bg2'])} primary "
       f"athletes drop out of it --- {f(float(sw['inklusiv_OR']), 2)}, 95% CI {f(float(sw['inklusiv_KI_lav']), 2)}--"
       f"{f(float(sw['inklusiv_KI_hoy']), 2)})", "switcher")
k2, uc, ci_ = robr("k_minst_2"), robr("uten_covid_kull"), robr("covid_interaksjon")
k.need("results", f"at least two results per window ({f(k2['OR'], 2)}), held without the COVID-affected cohorts ({f(uc['OR'], 2)}) "
       f"with no clear COVID interaction ({f(ci_['OR'], 2)}, CI {f(ci_['KI_lav'], 2)}--{f(ci_['KI_hoy'], 2)})", "covid")
uts = [robr("utfallsvariant", utf="senior_min1")["OR"], robr("utfallsvariant", utf="senior_20_21")["OR"]]
k.need("results", f"held across outcome definitions ({f(min(uts), 2)}--{f(max(uts), 2)}; attenuated to "
       f"{f(robr('utfallsvariant_inkl_2006')['OR'], 2)} for the nearer outcome", "utfall")
k.need("results", f"two cohort halves ({f(a_['OR'], 2)} and {f(b_['OR'], 2)})", "kohorter tekst")
k.need("results", f"check was null (OR {f(nk['OR'], 2)}, 95% CI {f(nk['KI_lav'], 2)}--{f(nk['KI_hoy'], 2)})", "spes. tekst")
k.need("results", f"was {f(ev['E_verdi_punkt'], 2)} ({f(ev['E_verdi_KI_grense'], 2)} for the CI bound)", "E-verdi tekst")
k.need("results", f"risk-ratio association of about {f(ev['E_verdi_punkt'], 1)}", "E-verdi RR")
cl = robr("klubb_klusterrobust")
krav(abs(cl["OR"] - m2d["OR"]) < 0.005, "«unchanged under club-clustered inference»")

# ================================================================ DISCUSSION
k.need("discussion", f"odds ratio of {f(m2d['OR'], 1)} per SD", "OR diskusjon")
k.need("discussion", "(2.04 per SD at ages 13--14", "følgestudien")
k.need("discussion", f"(OR {f(v15['OR'], 2)}) --- independently", "volum")
k.need("discussion", f"is modest (+{f(dlm['diff'], 3)} AUC)", "ΔAUC")
k.need("discussion", f"(OR {f(nt['lav']['OR'], 2)}, {f(nt['midt']['OR'], 2)}, {f(nt['hoy']['OR'], 2)} from lowest to highest tertile)",
       "nivå diskusjon")
k.need("discussion", f"(+{f(ols['OR_per_kvartal'], 2)} SD per quarter)", "mediering")
k.need("discussion", f"(OR {f(1 / gm['OR'], 2)}; Cox HR {f(cox.loc['kvinne', 'exp(coef)'], 2)})", "kjønn")
k.need("discussion", f"similar in women and men (stratified ORs {f(kf['OR'], 2)} and {f(km['OR'], 2)}; interaction p = "
       f"{f(kxi['p'], 2)})", "kjønn interaksjon")
k.need("discussion", f"roughly {f(sd['sd_delta_poeng_pooled'], 0)} age-graded points", "SD")
k.need("discussion", "about twice the odds", "OR ~2") if 1.8 <= m2d["OR"] <= 2.3 else k.feil.append("«twice the odds»")
r_neg = sd["andel_negativ_delta_dropouts"] / sd["andel_negativ_delta_retainers"]
krav(1.7 <= r_neg <= 1.95, f"«nearly twice as common» ({r_neg:.2f})")
k.need("discussion", f"nearly twice as common among future dropouts as among retainers ({pst(sd['andel_negativ_delta_dropouts'])} vs. "
       f"{pst(sd['andel_negativ_delta_retainers'])}%)", "negativ Δ diskusjon")
k.need("discussion", f"(-{f(-fig2p.loc['T-1', 'median'], 0)} points, ≈{f(-fig2p.loc['T-1', 'median'] / sd['sd_delta_poeng_pooled'], 2)} SD)",
       "slide diskusjon")
k.need("discussion", "the four processes above cannot be separated", "fire prosesser")
krav("Four processes" in k.tekst, "Discussion lister fire prosesser")

# ================================================================ ORDTELLING
ord_n = ordtelling(PROSJ / "manus" / "main.tex", fra=r"\section{Background}")
k.need("tittelside", f"Word count: $\\sim${int(round(ord_n, -2))}", f"ordtelling ({ord_n})")

# ================================================================ DEKNING
UNNTAK = [
    r"\\vspace\*?\{[^}]*\}", r"\d*\.?\d+\\textwidth", r"orcid\.org/[\d-]+\}\{ORCID: [\d-]+\}", r"Box 5003, 1432",
    r"\$\^\{?1,?\*?\}?\$", r"\$\^1\$", r"\\begin\{titlepage\}", r"leftmargin=1\.2em",
    r"\b(19|20)\d\d\b", r"\b(19|20)\d\d--(19|20)\d\d\b", r"\bH[1-3]\b", r"\bS1\b", r"\b(13|15)--(14|16)\b", r"\b13--16\b",
    r"k_\{1[35]\}", r"Q[1-4](--Q[1-4])?", r"age 1[03]", r"ages? (16|17|18|20)(--(19|21))?\b", r"age ≥(18|20)", r"≥(18|20)\b",
    r"age-16", r"\(age 13 to 14\)", r"below 13", r"below age 13", r"95% (CIs?|confidence)", r"95% CI", r"COVID-19",
    r"29 October( 2026)?", r"fewer than 20 athletes", r"nine years", r"\b20 repetitions", r"\\S4\.4",
    r"\b(1 - p\$_0\$ \+ p\$_0\$)", r"\$\\alpha\$ = 0\.05", r"\$k \\geq 2\$", r"at least two", r"at age 13--14",
    r"at 13, 969 at 16", r"Tables? [1-4]", r"Figures? [1-4]", r"\bstratified 5-fold",
]
kode_m = k.rapport(UNNTAK)

# ================================================================ SVARBREV
b = Kontroll.__new__(Kontroll)
b.navn, b.feil, b.dekket, b.n_ok = "A1 svarbrev", [], [], 0
b.raa = (PROSJ / "manus" / "RESPONSE_PANEL1.md").read_text()
b.tekst = re.sub(r"(?<=\d),(?=\d{3}\b)", "", b.raa)
b.seksjoner = {"brev": (0, len(b.tekst))}
for s, hvorfor in [
    (f"OR {f(ni['OR'], 2)} ({f(ni['KI_lav'], 2)}–{f(ni['KI_hoy'], 2)})", "R1-2 interaksjon"),
    (f"{f(nt['lav']['OR'], 2)} / {f(nt['midt']['OR'], 2)} / {f(nt['hoy']['OR'], 2)}", "R1-2 strata"),
    (f"one progression-SD ≈ {f(sd['sd_delta_poeng_pooled'], 0)} age-graded points (range {lo_c}–{hi_c} across cells; level ≈ "
     f"{f(sd['sd_niva_poeng'], 0)} points; volumes ≈ {f(sd['sd_vol1314_dager'], 0)} days)", "R1-4"),
    (f"({pst(sd['andel_negativ_delta_dropouts'])} vs {pst(sd['andel_negativ_delta_retainers'])} %)", "R1-4 andeler"),
    (f"OR {f(kxi['OR'], 2)} ({f(kxi['KI_lav'], 2)}–{f(kxi['KI_hoy'], 2)}); strata {f(kf['OR'], 2)} (women) / {f(km['OR'], 2)} (men)",
     "R1-5"),
    (f"the number is {int(sd['primaer_uten_kvartal'])} (n = {int(med.loc['uten_delta', 'n'])})", "R2-1"),
    (f"ΔAUC(M2−M1) = {f(dlm['diff'], 3)} ({f(dlm['ki_lav'], 3)}–{f(dlm['ki_hoy'], 3)}, p = {f(dlm['p'], 3)}); H3 difference "
     f"{f(dlh['diff'], 3)} ({f(dlh['ki_lav'], 3)} to {f(dlh['ki_hoy'], 3)}, p = {f(dlh['p'], 2)})".replace("-", "−"), "R2-2"),
    (f"OR {f(v15['OR'], 2)}", "R2-3"),
    (f"(RR = OR/(1 − p₀ + p₀·OR), p₀ = {f(ev['utfallsandel'], 2)})", "R2-5"),
    (f"OR {f(robr('fast_vindu_kohort_A') if False else moder('fast_vindu_kohort_A')['OR'], 2)} (A) and "
     f"{f(moder('fast_vindu_kohort_B')['OR'], 2)} (B)", "R2-6"),
    (f"(n = {int(sw['inklusiv_n'])}; {int(sw['ekskluderte_734_i_modell'])} of the {flyt['uten_skaarbar_tyrving_i_hovedgruppen']} "
     f"recovered ({int(sw['ekskluderte_734_med_bg2'])} have a best-group score, but "
     f"{int(sw['ekskluderte_734_med_bg2']) - int(sw['ekskluderte_734_i_modell'])} lack a scorable baseline level); "
     f"{int(sw['prim_uten_bg2'])} primary athletes", "R2 minor switcher"),
    (f"OR {f(float(sw['inklusiv_OR']), 2)} ({f(float(sw['inklusiv_KI_lav']), 2)}–{f(float(sw['inklusiv_KI_hoy']), 2)})", "switcher OR"),
    (f"(ORs {f(kvint['dq_Q2'], 2)}/{f(kvint['dq_Q3'], 2)}/{f(kvint['dq_Q4'], 2)}/{f(kvint['dq_Q5'], 2)} vs the lowest quintile)", "kvintiler"),
    (f"({int(fig2p.loc['T-2', 'n'])} of the {int(fig2p.loc['T-2', 'n_kandidater'])} eligible dropouts)", "exit-aligned"),
    (f"median {f(dpk.loc[1, 'delta_poeng_median'], 1)} (Q1) to +{f(dpk.loc[4, 'delta_poeng_median'], 1)} points (Q4); "
     f"+{f(ols['OR_per_kvartal'], 2)} SD per quarter (95 % CI {f(ols['KI_lav'], 2)}–{f(ols['KI_hoy'], 2)})".replace("-", "−"),
     "R3-1a"),
    (f"the −{f(-fig2p.loc['T-1', 'median'], 0)}-point median (≈{f(-fig2p.loc['T-1', 'median'] / sd['sd_delta_poeng_pooled'], 2)} SD)",
     "R1-4 median"),
    ("2026 contributes through 29 October", "R2-6 dato"),
    (f"the upper bound of the birth-quarter trend is {f(u['KI_hoy'], 2)}, not 1.21 (rounded twice)", "auditnote trend"),
    ("for under 1 % of meets", "auditnote region"),
    ("1–5, 5–19 and 19–106 days", "fig2-grenser i brevet"),
    (f"OR {f(u['OR_per_kvartal'], 2)} ({f(u['KI_lav'], 2)}–{f(u['KI_hoy'], 2)}), weaker than the companion cohort's 1.16 --- "
     f"attenuates to {f(w['OR_per_kvartal'], 2)} ({f(w['KI_lav'], 2)}–{f(w['KI_hoy'], 2)})".replace(" --- ", " — "), "R3-1b"),
    (f"({pst(sd['kvartal_Q1'])}/{pst(sd['kvartal_Q2'])}/{pst(sd['kvartal_Q3'])}/{pst(sd['kvartal_Q4'])} %)", "R3 minor kvartaler"),
    (f"(≈{f(-fig2p.loc['T-1', 'median'] / sd['sd_delta_poeng_pooled'], 2)} SD)", "R3-5"),
]:
    b.need("brev", s, hvorfor)
UNNTAK_B = [r"\b(19|20)\d\d\b", r"R[1-3]-\d", r"Table [1-4]", r"\bS1\b", r"\bH[1-3]\b", r"§\d\.\d", r"\d\d_\w+\.py",
            r"r1_\w+", r"\b(13|15)--(14|16)\b", r"Q[1-4]", r"\b2\.04\b", r"\b3\.15\b", r"\b1\.16\b",
            r"\b43\b", r"\b27\b", r"95 % (DeLong )?CIs?", r"Reviewer [1-3]", r"Bandura 1977", r"Nicholls 1984",
            r"round[- ]1", r"Tables 2 and 3", r"Figures? [1-4]('s)?", r"§3\.2", r"Table-2-fallacy", r'"48"']
kode_b = b.rapport(UNNTAK_B)
TILLATT = {"That prediction failed": "runde 1-frase, sitert som erstattet",
           "switchers included": "runde 1-radnavn, sitert som rettet",
           "doubles the odds": "runde 1-frase", "48": "kort", "as strong as competition volume": "runde 1-frase"}
kode_s = sitatkontroll(PROSJ / "manus" / "RESPONSE_PANEL1.md", k, TILLATT)
print(f"\nA1 TOTALT: {k.n_ok + b.n_ok} sjekker OK, {len(k.feil) + len(b.feil)} feil")
sys.exit(1 if (kode_m or kode_b or kode_s) else 0)
