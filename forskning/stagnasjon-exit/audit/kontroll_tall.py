"""
kontroll_tall.py — A1-audit fase 4: hvert tall i manus mot modell- og datafilene.

Kjøres etter 03–07 (og R-kontrollene audit/sammenlign.py og audit/delong_bro.R). Ankrede
fraser bygget fra filene; dekningskontroll av alle tall. Svarbrevet til den simulerte
refereerunden vedlikeholdes ikke etter auditen 30.10.2026 (Atles beslutning) og kontrolleres ikke.
Tallene fra følgestudiene (OR 2,04; 12/23 %; trend 1,16) er kontrollert mot IJSSC-manuset
(ncc-kohort/IJSSC_R1_opplasting/MANUSCRIPT_R1_clean.docx) og står som eksterne fakta.
"""

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HER = Path(__file__).resolve().parent
PROSJ = HER.parent
sys.path.insert(0, str(PROSJ.parent))
from audit_felles import Kontroll, avrund as f, normaliser, ordtelling  # noqa: E402

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
fs = les(MOD, "r2_h1_folsomhet.csv").set_index("analyse")
mr = les(MOD, "r2_mediering.csv").set_index("storrelse")
ntr = les(MOD, "r2_nivatertiler.csv")
kj = les(MOD, "r2_kjonn.csv").set_index("gruppe")


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
nk = robr("eksponeringsvariant", "delta_nk_1314_z")
a_, b_ = robr("kohort_A"), robr("kohort_B")
fig2p = f2[f2["panel"] == "Age-graded performance"].set_index("t")
fig2r = f2[f2["panel"] == "ujustert"].set_index("t")
fig2m = f2[f2["panel"] == "sesongmedian"].set_index("t")
fig2k = f2[f2["panel"] == "antall_resultater"].set_index("t")
fig2v = f2[f2["panel"] == "Competition volume"].set_index("t")
abet, aubet = mr.loc["a_sti_betinget_M1_SD_per_kvartal"], mr.loc["a_sti_ubetinget_SD_per_kvartal"]
tot, nivq = mr.loc["kvartal_OR_bare_M0"], mr.loc["niva_1314_SD_per_kvartal"]
nta = ntr[ntr["utvalg"] == "alle"].set_index("tertil")
nt3 = ntr[ntr["utvalg"] == "k_minst_3"].set_index("tertil")
neg = {s: (g["delta"] < 0).mean() for s, g in [(1, ret), (0, dro)]}
negl = {s: (g["delta_lik"] < 0).mean() for s, g in [(1, ret), (0, dro)]}

# ================================================================ ABSTRACT + KEY POINTS
# Sammendraget kortet 30.10.2026 (SMO: høyst 350 ord; overskriftene Background, Results, Conclusions)
# og konklusjonen omskrevet etter Atles beslutning (endringsrapporten avsnitt 8, punkt 4).
sammendrag = k.raa.split("\\section*{Abstract}", 1)[1].split("\\textbf{Keywords:}", 1)[0]
abs_ord = len([x for x in re.sub(r"\\[a-zA-Z]+\s*", " ", normaliser(sammendrag)).split()
               if re.search(r"[A-Za-z0-9]", x)])
krav(abs_ord <= 350, f"sammendraget har høyst 350 ord (SMO): {abs_ord}")
krav(re.findall(r"\\textbf\{(\w+)\.\}", sammendrag) == ["Background", "Results", "Conclusions"],
     "SMO-overskriftene Background, Results, Conclusions")
k.need("abstract", "Low progression accompanies and precedes exit from youth track and field", "hovedsetning (Atles beslutning)")
k.need("abstract", f"and remained among athletes still competing after age 16 ({f(fs.loc['aktiv_etter_16', 'OR'], 2)})",
       "aktive etter 16")
k.need("abstract", f"(n = {flyt['primaerutvalg_fodt_1998_2005']}; {pst((prim['gender'] == 'F').mean(), 0)}% female; "
       f"{flyt['primaerutvalg_seniorer']} [{pst(prim['senior'].mean())}%] later active as seniors", "utvalg")
k.need("abstract", f"OR = {f(m2d['OR'], 2)} per SD (95% CI {f(m2d['KI_lav'], 2)}--{f(m2d['KI_hoy'], 2)}; "
       f"one SD ≈ {f(sd['sd_delta_poeng_pooled'], 0)} age-graded points)", "H1")
k.need("abstract", f"(cross-validated AUC {f(auc.loc['M1', 'cv_auc'], 3)} to {f(auc.loc['M2', 'cv_auc'], 3)}; "
       f"paired DeLong 95% CI for the difference {f(dlm['ki_lav'], 3)}--{f(dlm['ki_hoy'], 3)})", "AUC")
k.need("abstract", f"(OR {f(a_['OR'], 2)} and {f(b_['OR'], 2)})", "kohorter")
k.need("abstract", f"at equal numbers of results ({f(fs.loc['like_mange_resultater', 'OR'], 2)}), with event-equated points "
       f"({f(fs.loc['ovelsesjusterte_poeng', 'OR'], 2)}) and with outdoor marks only ({f(fs.loc['bare_utendors', 'OR'], 2)})",
       "følsomhet")
k.need("abstract", f"until the penultimate season (+{f(fig2p.loc['T-1', 'median'], 0)} points) and fell "
       f"{f(-fig2p.loc['T-0', 'median'], 0)} points below it in the final season", "exit like mange")
krav(fig2p.loc["T-1", "ki_lav"] > 0 and fig2p.loc["T-0", "ki_hoy"] < 0, "T−1 over eget nivå, T0 under (KI)")
k.need("abstract", f"(OR {f(inter['OR'], 2)}, 95% CI {f(inter['KI_lav'], 2)}--{f(inter['KI_hoy'], 2)})", "H2")
ind_b = np.exp(abet["estimat"] * np.log(m2d["OR"]))
ind_u = np.exp(aubet["estimat"] * np.log(m2d["OR"]))
krav(ind_u < 1.10, f"«weak»: selv ujustert a-sti gir indirekte OR under 1,10 per kvartal ({ind_u:.3f})")
k.need("abstract", f"an implied indirect association of about OR {f(ind_b, 2)} per quarter", "indirekte (betinget)")
k.need("results", f"this implies an indirect association of about OR {f(ind_b, 2)} per quarter", "indirekte (betinget), tekst")
k.need("results", f"even it implies only about OR {f(ind_u, 2)} per quarter", "indirekte (ubetinget), øvre grense")
krav(tot["ki_lav"] < 1 < tot["ki_hoy"], "kvartal M0: KI inkluderer 1")
krav(dlh["p"] > 0.05, "H3: «discriminated similarly» (DeLong p over 0,05)")
k.need("abstract", "Given volume, progression and level discriminated similarly", "H3 (krav over)")
k.need("abstract", "(2.04 per SD)", "følgestudien (IJSSC-manus)")
k.need("key points", f"following {flyt['primaerutvalg_fodt_1998_2005']} athletes", "KP utvalg")
k.need("key points", f"odds ratio of {f(m2d['OR'], 1)} per SD", "KP OR")
k.need("key points", f"then fell about {f(-fig2p.loc['T-0', 'median'], 0)} points below their own earlier level", "KP exit")

# ================================================================ BACKGROUND (følgestudier)
k.need("background", "discriminated senior retention somewhat less well than a simple behavioural signal", "IJSSC: «somewhat better»")
k.need("background", "though it added complementary information", "IJSSC: OR 1.75")
for s in ["fell 12% below their own earlier level two seasons before exit and 23% one season before",
          "a 14-year cohort study", "established at age 10 and stable to age 25"]:
    k.need("background", s, "følgestudie (IJSSC/RAE-manus)")

# ================================================================ METHODS
k.need("methods", f"we removed {flyt['fjernet_sonetvilling_brettkode']} board-jump results", "sonetvillinger")
k.need("methods", f"and {flyt['fjernet_eksakt_dublett']} exact duplicates", "eksakte dubletter")
k.need("methods", f"{flyt['fjernet_flerdagskopi_brettkode']} such copies from multi-day meets", "flerdagskopier (rens_felles)")
# første estimering (commit 9f1d922, DATA_AUDIT fase 7): 3 808 i primærutvalget, H1 OR 2,02
k.need("methods", f"enlarged the primary sample from 3808 to {flyt['primaerutvalg_fodt_1998_2005']} athletes and raised the H1 "
       f"odds ratio from 2.02 to {f(m2d['OR'], 2)}", "rettinger etter første estimering")
n_lite = int(((prim["k13"] < 3) | (prim["k15"] < 3)).sum())
k.need("methods", f"which applies to {n_lite} athletes in at least one window", "færre enn tre resultater")
krav(set(prim["hovedgruppe"]) == {"sprint", "jumps", "middle_distance", "throws"}, "fire hovedgrupper i primærutvalget")
k.need("methods", f"(n = {flyt['utovere_fodt_1998_2006']}); {flyt['ok_resultat_13_14']} had at least one", "flyt 1")
k.need("methods", f"was met by {flyt['landmark_13_14_og_15_16']} athletes, of whom {flyt['landmark_med_kjonn']} had known sex",
       "flyt 2")
k.need("methods", f"of whom {flyt['landmark_med_kjonn']} had known sex, {flyt['landmark_fodt_1998_2005']} of them born 1998--2005",
       "flyt 2b")
k.need("methods", f"Among these, we excluded {flyt['uten_skaarbar_tyrving_i_hovedgruppen']} athletes", "flyt 3")
krav(flyt["landmark_fodt_1998_2005"] - flyt["uten_skaarbar_tyrving_i_hovedgruppen"] - flyt["ekskludert_gruppecelle_under_20"]
     == flyt["primaerutvalg_fodt_1998_2005"], "flyten summerer (S1)")
k.need("methods", f"the {flyt['landmark_med_kjonn'] - flyt['landmark_fodt_1998_2005']} athletes born 2006 were retained", "2006-kullet")
k.need("methods", f"and {flyt['ekskludert_gruppecelle_under_20']} athletes in sex × event-group cells with fewer than 20",
       "flyt 4")
k.need("methods", f"The primary sample comprises {flyt['primaerutvalg_fodt_1998_2005']} athletes", "flyt 5")
k.need("methods", f"Of the primary sample, {flyt['primaerutvalg_seniorer']} ({pst(prim['senior'].mean())}%)", "flyt 6")
n_kv = int(mr.loc["a_sti_ubetinget_SD_per_kvartal", "n"])
krav(len(prim) - int(sd["primaer_uten_kvartal"]) == n_kv, f"{len(prim)} − {int(sd['primaer_uten_kvartal'])} = {n_kv}")
k.need("methods", f"Within the primary sample, {int(sd['primaer_uten_kvartal'])} athletes lacked an exact birth date and were "
       f"excluded from the birth-quarter analyses only (n = {n_kv}); in the wider landmark sample "
       f"the corresponding number is {flyt['landmark_uten_fodselsdato']}", "fødselsdato")
lo_c, hi_c = str(sd["sd_delta_poeng_cellespenn"]).replace("–", "-").split("-")
k.need("methods", f"approximately {f(sd['sd_delta_poeng_pooled'], 0)} age-graded points for progression (range "
       f"{lo_c}--{hi_c} across sex × event-group cells), {f(sd['sd_niva_poeng'], 0)} points for baseline level, and "
       f"{f(sd['sd_vol1314_dager'], 0)} and {f(sd['sd_vol1516_dager'], 0)} competition days for the two volume windows", "SD-skala")
krav(ad["region"].isna().all(), "region er NA for alle (A1-1)")
k.need("methods", "the registry records the competition district for under 1% of meets", "region")
k.need("methods", "the expected mean of the three best over all subsets of the smaller of the two counts from each "
       "window, computed exactly", "like mange: eksakt forventning (01)")
k.need("methods", "the expected value over all subsets of the smaller of the two counts, computed exactly",
       "like mange: eksakt forventning (05)")
k.need("results", "(expected value over all subsets of that size)", "tabell 1-note")
k.need("methods", "boys' throwing implements change at age 16, so these offsets are identified only within the two sets",
       "øvelsessett (06b: kast menn 2 sett)")
k.need("methods", f"common ({pst(prim['senior'].mean())}%)", "utfallsandel")
import sklearn, lifelines, statsmodels  # noqa: E402,E401
k.need("methods", f"Python {sys.version.split()[0]} with pandas {pd.__version__}, numpy {np.__version__}, statsmodels "
       f"{statsmodels.__version__}, scikit-learn {sklearn.__version__} and lifelines {lifelines.__version__}", "versjoner")
k.need("methods", "stratified 5-fold cross-validation repeated 20 times", "CV-oppsett (03: 5×20)")

# ================================================================ RESULTS
k.need("results", f"(median {f(ret['vol1314'].median(), 0)} vs. {f(dro['vol1314'].median(), 0)} competition days)", "dager")
krav(ret["vol1314"].median() / dro["vol1314"].median() > 2, "«more than twice as often»")
k.need("results", f"(median {f(ret['niva_w1'].median(), 0)} vs. {f(dro['niva_w1'].median(), 0)} age-graded points)", "poeng")
k.need("results", f"median progression was +{f(ret['delta'].median(), 0)} points against {f(dro['delta'].median(), 0)} for dropouts",
       "Δ median")
k.need("results", f"(median {f(dro['k15'].median(), 0)} against {f(ret['k15'].median(), 0)})", "k15")
k.need("results", f"dropouts' median progression was +{f(dro['delta_lik'].median(), 0)} points against "
       f"+{f(ret['delta_lik'].median(), 0)} for retainers, and {pst(negl[0])}% of dropouts against {pst(negl[1])}% of "
       f"retainers had negative progression ({pst(neg[0])} and {pst(neg[1])}% without equalising", "like mange tabell 1")
g1 = f1.set_index(["senior", "alder"])["median"]
k.need("results", f"(median {f(g1[(1, 13)], 0)} points at 13, {f(g1[(1, 16)], 0)} at 16)", "fig1 retainers")
k.need("results", f"started about 110 points lower (median {f(g1[(0, 13)], 0)} at 13)", "fig1 dropouts 13")
krav(105 <= g1[(1, 13)] - g1[(0, 13)] <= 115, "«about 110 points lower» ved 13")
k.need("results", f"({f(g1[(0, 16)], 0)} at 16, {f(g1[(0, 18)], 0)} at 18)", "fig1 dropouts sen")
q = {i: (prim.loc[prim["kvartal"].notna(), "kvartal"] == i).mean() for i in range(1, 5)}
k.need("results", f"Exact birth dates exist for {n_kv} of the {len(prim)} ({pst(n_kv / len(prim))}%); among these, the full "
       f"quarter distribution is Q1 {pst(q[1])}, Q2 {pst(q[2])}, Q3 {pst(q[3])}, Q4 {pst(q[4])}%", "kvartaler")
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
       f"{f(dlm['diff'], 3)} (paired DeLong 95% CI {f(dlm['ki_lav'], 3)}--{f(dlm['ki_hoy'], 3)}, p < 0.001; spread "
       f"across CV repetitions {f(auc.loc['M2-M1', 'p2_5'], 3)}--{f(auc.loc['M2-M1', 'p97_5'], 3)}), with good calibration "
       f"(slope {f(kal['kalibreringsslope'], 2)}; Brier {f(kal['brier'], 3)})", "diskriminering")
krav(dlm["p"] < 0.001, "DeLong M2−M1 p < 0.001")
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
k.need("results", f"OR {ki(nta.loc['lav'])} in the lowest, {ki(nta.loc['midt'])} in the middle and {ki(nta.loc['hoy'])} in the "
       f"highest tertile, with a non-significant progression × level interaction (OR {f(nta.loc['interaksjon', 'OR'], 2)}, "
       f"{f(nta.loc['interaksjon', 'KI_lav'], 2)}--{f(nta.loc['interaksjon', 'KI_hoy'], 2)})", "nivåstrata")
k.need("results", f"the median athlete had only {f(nta.loc['lav', 'median_k15'], 0) == '3' and 'three' or 'FEIL'} scored results at 15--16",
       "median k15 laveste tertil")
k.need("results", f"the tertile ORs were {f(nt3.loc['lav', 'OR'], 2)}, {f(nt3.loc['midt', 'OR'], 2)} and {f(nt3.loc['hoy', 'OR'], 2)} "
       f"(interaction {f(nt3.loc['interaksjon', 'OR'], 2)}, {f(nt3.loc['interaksjon', 'KI_lav'], 2)}--"
       f"{f(nt3.loc['interaksjon', 'KI_hoy'], 2)})", "nivå k≥3")
krav(nta.loc["lav", "sd_delta_z"] > nta.loc["hoy", "sd_delta_z"], "Δ mer støyfull i laveste tertil")
k.need("results", f"OR {ki(kj.loc['kvinner'])} and {ki(kj.loc['menn'])}, interaction p = {f(kj.loc['menn', 'p_interaksjon'], 2)}",
       "kjønn én modell")
k.need("results", f"(n = {flyt['primaerutvalg_fodt_1998_2005']}; {flyt['primaerutvalg_seniorer']} events)", "tabell 2 tittel")
k.need("results", f"(OR {f(inter['OR'], 2)} per quarter, 95% CI {f(inter['KI_lav'], 2)}--{f(inter['KI_hoy'], 2)}, $p$ = "
       f"{f(inter['p'], 2)})", "H2 tekst")
k.need("results", f"OR {ki(s12)} among athletes born in Q1--Q2 and {ki(s34)} among those born in Q3--Q4", "H2 strata")
k.need("results", f"from {f(dpk.loc[1, 'delta_poeng_median'], 1)} points (Q1) to +{f(dpk.loc[4, 'delta_poeng_median'], 1)} "
       f"points (Q4), +{f(aubet['estimat'], 3)} SD per quarter unadjusted", "mediering ubetinget")
k.need("results", f"({f(nivq['estimat'], 3)} SD per quarter in baseline level)", "nivå per kvartal")
k.need("results", f"the gradient was +{f(abet['estimat'], 3)} SD per quarter (95% CI {f(abet['ki_lav'], 3)} to {f(abet['ki_hoy'], 3)}; "
       f"p = {f(abet['p'], 2)})", "mediering betinget")
k.need("results", f"(OR {f(tot['estimat'], 2)} per quarter, {f(tot['ki_lav'], 2)}--{f(tot['ki_hoy'], 2)})", "kvartal M0 tekst")
k.need("results", f"cross-validated AUC {f(h3.loc['volum+fremgang', 'cv_auc'], 3)} with progression and "
       f"{f(h3.loc['volum+niva', 'cv_auc'], 3)} with level (paired DeLong difference {f(dlh['diff'], 3)}, 95% CI "
       f"{f(dlh['ki_lav'], 3)} to {f(dlh['ki_hoy'], 3)}, p = {f(dlh['p'], 2)}; repetition spread {f(h3.loc['differanse', 'p2_5'], 3)} "
       f"to {f(h3.loc['differanse', 'p97_5'], 3)})", "H3 tekst")
kk = [int(fig2k.loc[t, "median"]) for t in ["T-3", "T-2", "T-1", "T-0"]]
k.need("results", f"(median {kk[0]}, {kk[1]}, {kk[2]} and {kk[3]} scored results in the four last seasons)", "antall per sesong")
k.need("results", f"(median +{f(fig2p.loc['T-2', 'median'], 1)} points, 95% CI {f(fig2p.loc['T-2', 'ki_lav'], 1)} to "
       f"{f(fig2p.loc['T-2', 'ki_hoy'], 1)}; n = {int(fig2p.loc['T-2', 'n'])}", "exit T-2")
k.need("results", f"still in the penultimate season (+{f(fig2p.loc['T-1', 'median'], 1)}, {f(fig2p.loc['T-1', 'ki_lav'], 1)} to "
       f"{f(fig2p.loc['T-1', 'ki_hoy'], 1)})", "exit T-1")
k.need("results", f"only in the final season ({f(fig2p.loc['T-0', 'median'], 1)}, {f(fig2p.loc['T-0', 'ki_lav'], 1)} to "
       f"{f(fig2p.loc['T-0', 'ki_hoy'], 1)})", "exit T0")
k.need("results", f"(median {f(fig2v.loc['T-1', 'median'], 0)} days in the penultimate and {f(fig2v.loc['T-0', 'median'], 0)} days in "
       f"the final season; n = {int(fig2v.loc['T-1', 'n'])})", "exit volum")
k.need("results", f"(+{f(fig2m.loc['T-1', 'median'], 1)} in the penultimate and {f(fig2m.loc['T-0', 'median'], 1)} in the final season)",
       "sesongmedian")
k.need("results", f"the mean of the three best fell {f(-fig2r.loc['T-1', 'median'], 1)} points in the penultimate and "
       f"{f(-fig2r.loc['T-0', 'median'], 1)} points in the final season", "ujustert")
k.need("results", f"(points; n = {int(fig2p.loc['T-2', 'n'])} of the {int(fig2p.loc['T-2', 'n_kandidater'])} non-censored "
       f"dropouts with a final season at 16--19", "fig2 tekst")
k.need("results", f"Right: competition volume (days; n = {int(fig2v.loc['T-1', 'n'])})", "fig2 volum")
k.need("results", f"(HR {f(cox.loc['delta_z', 'exp(coef)'], 2)} per SD, 95% CI {f(cox.loc['delta_z', 'exp(coef) lower 95%'], 2)}--"
       f"{f(cox.loc['delta_z', 'exp(coef) upper 95%'], 2)}), alongside level (HR {f(cox.loc['niva_w1_z', 'exp(coef)'], 2)}), "
       f"later volume (HR {f(cox.loc['vol1516_g', 'exp(coef)'], 2)} per SD), null earlier volume given later "
       f"(HR {f(cox.loc['vol1314_g', 'exp(coef)'], 2)}), and a higher hazard for women (HR {f(cox.loc['kvinne', 'exp(coef)'], 2)}, "
       f"95% CI {f(cox.loc['kvinne', 'exp(coef) lower 95%'], 2)}--{f(cox.loc['kvinne', 'exp(coef) upper 95%'], 2)})", "Cox")
n17 = int((prim["siste_alder"] >= 17).sum())
krav(int(cox_n) == n17 if (cox_n := n17) else True, "Cox-utvalg")
a16 = fs.loc["aktiv_etter_16"]
krav(int(a16["n"]) == n17, "H1 aktiv etter 16: samme utvalg som Cox")
k.need("results", f"In the landmark Cox model among the {n17} athletes still competing after age 16", "Cox-utvalg tekst")
k.need("results", f"remained clear among the {n17} athletes still competing after age 16, whose final season lies beyond the "
       f"progression window ({f(a16['OR'], 2)}, 95% CI {f(a16['KI_lav'], 2)}--{f(a16['KI_hoy'], 2)})", "aktiv etter 16")
k.need("discussion", f"the association was smaller but clear (OR {f(a16['OR'], 2)})", "aktiv etter 16, diskusjon")
krav(a16["KI_lav"] > 1 and a16["OR"] < m2d["OR"], "aktiv etter 16: mindre, men klar")
mx, vi = robr("eksponeringsvariant", "delta_max_z"), robr("eksponeringsvariant", "delta_vind_z")
k.need("results", f"(season best {f(mx['OR'], 2)}; wind-legal marks {f(vi['OR'], 2)}; equal numbers of results in both windows "
       f"{f(fs.loc['like_mange_resultater', 'OR'], 2)}; event-equated points {f(fs.loc['ovelsesjusterte_poeng', 'OR'], 2)}; "
       f"outdoor marks only {f(fs.loc['bare_utendors', 'OR'], 2)};", "eksponeringsvarianter")
krav(int(sw["prim_i_modell"]) + int(sw["ekskluderte_734_i_modell"]) == int(sw["inklusiv_n"]),
     "inklusivt utvalg (planen): primær med bg2 + gjenvunne i modell = n")
krav(len(prim) - int(sw["prim_uten_bg2"]) == int(sw["prim_i_modell"]), "primær − uten bg2 = primær i modell")
# gruppekonsistent spesifikasjon som hovedtall, planens variant ved siden av (Atles beslutning 30.10.2026)
krav(int(sw["kons_prim_i_modell"]) + int(sw["kons_gjenvunnet_578"]) + int(sw["kons_gjenvunnet_smaa_celler"])
     == int(sw["kons_n"]), "konsistent utvalg: primær + gjenvunne fra 578 + fra små celler = n")
krav(len(prim) - int(sw["kons_prim_utenfor"]) == int(sw["kons_prim_i_modell"]), "konsistent: primær − utenfor = i modell")
krav(int(sw["kons_gjenvunnet_smaa_celler"]) <= flyt["ekskludert_gruppecelle_under_20"], "gjenvunnet fra småcellene ≤ 20")
k.need("results", f"n = {int(sw['kons_n'])}, recovering {int(sw['kons_gjenvunnet_578'])} of the "
       f"{flyt['uten_skaarbar_tyrving_i_hovedgruppen']} excluded from the primary definition and "
       f"{int(sw['kons_gjenvunnet_smaa_celler'])} of the {flyt['ekskludert_gruppecelle_under_20']} in small cells while "
       f"{int(sw['kons_prim_utenfor'])} primary athletes drop out of it --- {f(float(sw['kons_OR']), 2)}, 95% CI "
       f"{f(float(sw['kons_KI_lav']), 2)}--{f(float(sw['kons_KI_hoy']), 2)}; {f(float(sw['inklusiv_OR']), 2)}, 95% CI "
       f"{f(float(sw['inklusiv_KI_lav']), 2)}--{f(float(sw['inklusiv_KI_hoy']), 2)}, under the analysis plan's specification, "
       f"which keeps level and counts from the original main group although the best group differs from it for "
       f"{pst(int(sw['kons_ulik_gruppe']) / int(sw['kons_n']), 0)}% of the sample)", "switcher")
k.need("results", f"held with spline terms for result counts and volumes ({f(fs.loc['splines_k_og_volum', 'OR'], 2)})", "splines")
k2, uc, ci_ = robr("k_minst_2"), robr("uten_covid_kull"), robr("covid_interaksjon")
k.need("results", f"at least two or three results per window ({f(k2['OR'], 2)} and {f(fs.loc['k13_og_k15_minst_3', 'OR'], 2)}),",
       "k ≥ 2 og ≥ 3")
k.need("results", f"held without the COVID-affected cohorts ({f(uc['OR'], 2)}) with no clear COVID interaction "
       f"({f(ci_['OR'], 2)}, CI {f(ci_['KI_lav'], 2)}--{f(ci_['KI_hoy'], 2)})", "covid")
k.need("methods", "(and at 17--19 for the descriptive trajectories)", "aldre i figurene (05: 13-19)")
uts = [robr("utfallsvariant", utf="senior_min1")["OR"], robr("utfallsvariant", utf="senior_20_21")["OR"]]
k.need("results", f"held across outcome definitions ({f(min(uts), 2)}--{f(max(uts), 2)}; attenuated to "
       f"{f(robr('utfallsvariant_inkl_2006')['OR'], 2)} for the nearer outcome", "utfall")
k.need("results", f"two cohort halves ({f(a_['OR'], 2)} and {f(b_['OR'], 2)})", "kohorter tekst")
l1 = fs.loc["tidlig_niva_per_100p_gitt_senere"]
k.need("results", f"(OR {f(l1['OR'], 2)} per 100 points, 95% CI {f(l1['KI_lav'], 2)}--{f(l1['KI_hoy'], 2)})", "tidlig gitt senere")
krav(l1["KI_hoy"] < 1, "tidligere nivå gitt senere: negativ koeffisient")
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
k.need("discussion", f"(tertile ORs {f(nt3.loc['lav', 'OR'], 2)}, {f(nt3.loc['midt', 'OR'], 2)} and {f(nt3.loc['hoy', 'OR'], 2)} among "
       f"athletes with at least three results per window)", "nivå diskusjon")
k.need("discussion", f"(OR {f(1 / gm['OR'], 2)}; Cox HR {f(cox.loc['kvinne', 'exp(coef)'], 2)})", "kjønn")
krav(kj.loc["menn", "p_interaksjon"] > 0.5, "kjønn: ingen tegn til interaksjon")
k.need("discussion", f"(OR {f(kj.loc['menn', 'OR'], 2)} in men and {f(kj.loc['kvinner', 'OR'], 2)} in women, interaction p = "
       f"{f(kj.loc['menn', 'p_interaksjon'], 2)})", "kjønn én modell")
k.need("discussion", f"roughly {f(sd['sd_delta_poeng_pooled'], 0)} age-graded points", "SD")
k.need("discussion", "about twice the odds", "OR ~2") if 1.8 <= m2d["OR"] <= 2.3 else k.feil.append("«twice the odds»")
r_neg = negl[0] / negl[1]
krav(1.7 <= r_neg <= 1.98, f"«nearly twice as common» ({r_neg:.2f})")
k.need("discussion", f"compared at equal numbers of results ({pst(negl[0])} vs. {pst(negl[1])}%)", "negativ Δ diskusjon")
k.need("discussion", f"(about {f(-fig2p.loc['T-0', 'median'], 0)} points, ≈{f(-fig2p.loc['T-0', 'median'] / sd['sd_delta_poeng_pooled'], 1)} SD)",
       "sluttsesong diskusjon")
k.need("discussion", f"event-equated points (OR {f(fs.loc['ovelsesjusterte_poeng', 'OR'], 2)})", "øvelsesjustert")
k.need("discussion", f"(outdoor marks only: OR {f(fs.loc['bare_utendors', 'OR'], 2)})", "utendørs")
k.need("discussion", "the four processes above cannot be separated", "fire prosesser")
krav("Four processes" in k.tekst, "Discussion lister fire prosesser")

# ================================================================ ORDTELLING
# løpende tekst: Background til og med Conclusions (forkortelseslisten fra 30.10.2026 regnes ikke med)
ord_n = ordtelling(PROSJ / "manus" / "main.tex", fra=r"\section{Background}", til=r"\section*{Abbreviations}")
k.need("tittelside", f"Word count: $\\sim${int(round(ord_n, -2))}", f"ordtelling ({ord_n})")

# ================================================================ DEKNING
UNNTAK = [
    r"Additional file 1\b", r"Table S1\b", r"\\S\\S 2 and 4",   # helseforskningsloven §§ 2 og 4
    r"\\vspace\*?\{[^}]*\}", r"\d*\.?\d+\\textwidth", r"orcid\.org/[\d-]+\}\{ORCID: [\d-]+\}", r"Box 5003, 1432",
    r"\$\^\{?1,?\*?\}?\$", r"\$\^1\$", r"\\begin\{titlepage\}", r"leftmargin=1\.2em",
    r"\b(19|20)\d\d\b", r"\b(19|20)\d\d--(19|20)\d\d\b", r"\bH[1-3]\b", r"\bS1\b", r"\b(13|15)--(14|16)\b", r"\b13--16\b",
    r"k_\{1[35]\}", r"Q[1-4](--Q[1-4])?", r"age 1[03]", r"ages? (16|17|18|20)(--(19|21))?\b", r"age ≥(18|20)", r"≥(18|20)\b",
    r"age-1[36]", r"\(age 13 to 14\)", r"below 13", r"below age 13", r"95% (CIs?|confidence)", r"95% CI", r"COVID-19",
    r"29 October( 2026)?", r"fewer than 20 athletes", r"nine years", r"\b20 repetitions", r"\\S4\.4",
    r"\$\\alpha\$ = 0\.05", r"\$k \\geq 2\$", r"at least two", r"at age 13--14", r"at age 13\b",
    r"Tables? [1-4]", r"Figures? [1-4]", r"\bstratified 5-fold", r"one-SD", r"at least three",
    r"per 100 points", r"two or three", r"three seasons before exit",
]
# ================================================================ ADDITIONAL FILE 1 (egen fil, SMO)
ka = Kontroll(PROSJ / "manus" / "additional_file_1.tex", "A1 Additional file 1")
krav("\\input{s1}" not in k.raa and "\\input{s1}" in ka.raa, "S1 står i Additional file 1, ikke i hovedfila")
krav("Sports Medicine -- Open" in ka.raa and "Guttormsen" in ka.raa, "forside med tidsskrift, tittel og forfatter")
kode_m = k.rapport(UNNTAK)
kode_a = ka.rapport(UNNTAK)
print(f"\nA1 TOTALT: {k.n_ok + ka.n_ok} sjekker OK, {len(k.feil) + len(ka.feil)} feil")
sys.exit(1 if (kode_m or kode_a) else 0)
