"""
kontroll_tall.py — A3-audit fase 4: hvert tall i manus mot modell- og datafilene.

Kjøres etter 01–06 (og R-kontrollen audit/sammenlign.py). Ankrede fraser fra filene og
dekningskontroll av alle tall. Svarbrevet til den simulerte refereerunden vedlikeholdes ikke
etter auditen 30.10.2026 (Atles beslutning) og kontrolleres ikke. Van Yperen-tallene (1 762;
senere start blant frafallere) er kontrollert mot artikkelens abstract i CrossRef.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HER = Path(__file__).resolve().parent
PROSJ = HER.parent
sys.path.insert(0, str(PROSJ.parent))
from audit_felles import Kontroll, avrund as f, ordtelling  # noqa: E402

MOD, TAB, DATA = PROSJ / "tables" / "modeller", PROSJ / "tables", PROSJ / "data_private"


def les(n, **kw):
    return pd.read_csv(MOD / n, **kw)


flyt = json.loads((DATA / "flyt.json").read_text())
ad = pd.read_csv(DATA / "analysedata.csv")
prim = ad[ad["kohort_primar"] & ad["debut_10_16"]]
h1 = les("h1_debutalder.csv")
h3 = les("r1_h3_landmark.csv")
h3i = les("r1_h3_landmark_info.csv")
lrt = les("r1_lrt.csv").iloc[0]
d17 = les("r1_debut1719.csv")
fd17 = les("r1_debut17plus_fordeling.csv").set_index("debut_alder")["n"]
kk = les("r1_kjonn_konvertering.csv")
kxi = les("r1_kjonn_interaksjon.csv")
rc = les("r1_retention_ci.csv")
rob = les("robusthet.csv")
fors = les("r1_debutforskyvning.csv").iloc[0]
da = les("r2_andel_etter_alder.csv").set_index(["alder", "gruppe"])["andel"]
va = les("r2_varighet_andeler.csv")
vm = les("r2_varighet_modeller.csv")
u01 = les("r2_uten_2001.csv")
ukj = les("r2_ukjent_kjonn.csv")
sel = les("r2_seleksjon_kvartal.csv").set_index("gruppe")["andel_med_fodselsdato"]
dfo = pd.read_csv(TAB / "debutfordeling.csv").set_index("birth_year")


def rad(df, an, var="debut_alder"):
    return df[(df["analyse"] == an) & (df["variabel"] == var)].iloc[0]


def pst(x, d=1):
    return f(100 * x, d)


def konv(a):
    return prim[prim["debut_alder"] == a]["senior"].mean()


def ret(a, k_):
    return rc[(rc["debut_alder"] == a) & (rc["k"] == k_)].iloc[0]


def vandel(D, a):
    return va[(va["D"] == D) & (va["debut_alder"] == a)].iloc[0]["andel"]


k = Kontroll(PROSJ / "manus" / "main.tex", "A3 manus")


def krav(b, hvorfor):
    if b:
        k.n_ok += 1
    else:
        k.feil.append(f"PÅSTAND holder ikke: {hvorfor}")


kat = {a: rad(h1, "H1_kategorisk", f"debut_kat_{a}") for a in range(11, 17)}
tr = rad(h1, "H1_trend")
lav = [kat[a]["OR"] for a in range(11, 15)]
h3u, h3m = rad(h3, "r1_H3_uten_volum"), rad(h3, "r1_H3_med_volum")
info = h3i.set_index("mål")
n_lm = int(info.loc[[i for i in info.index if "ny def" in i][0], "n"])
s_lm = int(info.loc[[i for i in info.index if "ny def" in i][0], "seniorer"])
idle = int(info.loc[[i for i in info.index if "UTENFOR" in i][0], "n"])
k5 = {a: ret(a, 5)["andel"] for a in range(10, 17)}
k1 = {a: ret(a, 1)["andel"] for a in range(10, 17)}
v4 = {a: vandel(4, a) for a in range(10, 17)}
vt = {D: rad(vm, f"varighet_{D}") for D in (4, 5, 6)}
v4_sen = [v4[a] for a in (14, 15, 16)]
s12_16 = [k5[a] for a in range(12, 17)]

# ================================================================ ABSTRACT
k.need("abstract", f"(n = {len(prim)}; {pst((prim['gender'] == 'F').mean(), 0)}% female) to the end of 2026; "
       f"{int(prim['senior'].sum())} ({pst(prim['senior'].mean())}%)", "utvalg")
krav(float(lrt["p"]) < 0.001, "LRT p < 0.001")
k.need("abstract", "(non-linearity LR test p < 0.001)", "LRT")
k.need("abstract", f"relative to debut at age 10 ({pst(konv(10))}%), adjusted odds were lowest for debuts at 11--14 "
       f"(OR {f(min(lav), 2)}--{f(max(lav), 2)}) and highest for debut at 16 ({pst(konv(16))}%; OR {f(kat[16]['OR'], 2)}, "
       f"95% CI {f(kat[16]['KI_lav'], 2)}--{f(kat[16]['KI_hoy'], 2)})", "U-form")
k.need("abstract", f"null linear trend (OR {f(tr['OR'], 2)} per year, 95% CI {f(tr['KI_lav'], 2)}--{f(tr['KI_hoy'], 2)})", "trend")
k.need("abstract", f"{pst(v4[10])}% of those who started at 10 still competed on at least two days in a season four or more "
       f"years after debut, against {pst(min(v4_sen))}--{pst(max(v4_sen))}% of those who started at 14--16 (OR "
       f"{f(vt[4]['OR'], 2)} per year of later debut, 95% CI {f(vt[4]['KI_lav'], 2)}--{f(vt[4]['KI_hoy'], 2)})",
       "lik karrierelengde")
krav(vt[4]["KI_hoy"] < 1, "senere debut → lavere utholdenhet ved lik karrierelengde")
krav(v4[10] == max(v4.values()), "debut 10 høyest ved lik karrierelengde («early entrants persisted longest»)")
k.need("abstract", f"(OR {f(h3u['OR'], 2)} per year of later debut, 95% CI {f(h3u['KI_lav'], 2)}--{f(h3u['KI_hoy'], 2)})", "H3 uten")
k.need("abstract", f"controlled (OR {f(h3m['OR'], 2)}, 95% CI {f(h3m['KI_lav'], 2)}--{f(h3m['KI_hoy'], 2)})", "H3 med")
krav(h3m["KI_lav"] < 1 < h3m["KI_hoy"], "H3 med volum: KI inkluderer 1 («little association remained»)")

# ================================================================ INTRODUCTION
k.need("introduction", "among 1762 Dutch football players", "Van Yperen (CrossRef-abstract)")
k.need("introduction", "A 14-year cohort study", "følgestudien")

# ================================================================ METHODS
k.need("materials", f"(n = {flyt['utovere_fodt_2001_2008']}, with {flyt['resultatrader']} result rows; {flyt['rader_ikke_ok']} "
       f"non-approved rows and {flyt['rader_alder_under_10']} rows below age 10 were excluded). The "
       f"{flyt['debutanter_alder_10plus']} athletes", "flyt 1")
kjent = len(ad)
sent = int((ad["debut_alder"] >= 17).sum())
d1016 = int(ad["debut_10_16"].sum())
krav(flyt["debutanter_alder_10plus"] - flyt["uten_kjonn"] == kjent, "28339 − 865 = 27474")
krav(kjent - sent == d1016, "27474 − 731 = 26743")
k.need("materials", f"{flyt['uten_kjonn']} without registered sex", "uten kjønn")
k.need("materials", f"of the remaining {kjent}, {sent} ({pst(sent / kjent)}%) whose debut fell at age 17 or later", "debut 17+")
k.need("materials", f"Of the remaining {d1016} debutants, the primary sample comprises the {len(prim)} born 2001--2005", "primær")
k.need("materials", f"of whom {pst((prim['gender'] == 'F').mean())}% were female and {int(prim['senior'].sum())} "
       f"({pst(prim['senior'].mean())}%)", "kjønn/seniorer")
k.need("materials", f"the other {d1016 - len(prim)}, born 2006--2008", "beskrivende")
k.need("materials", f"{int(fors['primaer_med_tidligere_utelatte_rader'])} athletes in the primary sample "
       f"({pst(fors['primaer_med_tidligere_utelatte_rader'] / len(prim))}%) had earlier excluded rows, which would change the "
       f"debut age of {int(fors['av_disse_annen_debutalder'])} of them", "debutforskyvning")
krav(ad["region"].isna().sum() >= len(ad) - 60 and prim["region"].isna().all(), "region NA i hele primærutvalget (A3-1)")
k.need("materials", "the registry records the competition district for under 1% of meets", "region")
krav(va.groupby("D")["n"].sum().loc[4] == len(prim), "D = 4 observerbart for hele primærutvalget")
k.need("materials", "four or more years after the debut season (five and six years as sensitivity analyses)", "varighetsutfall")
k.need("materials", f"exact birth dates exist for {pst(sel['senior=1'])}% of the seniors but {pst(sel['senior=0'])}% of the "
       "other athletes", "fødselsdato-seleksjon")
import statsmodels, lifelines  # noqa: E402,E401
k.need("materials", f"Python {sys.version.split()[0]} with pandas {pd.__version__}, numpy {np.__version__}, statsmodels "
       f"{statsmodels.__version__} and lifelines {lifelines.__version__}", "versjoner")

# ================================================================ RESULTS
k.need("results", f"with a share rising from {pst(dfo.loc[2001, '10'] / dfo.loc[2001, 'totalt'])}% of debutants born 2001 to "
       f"{pst(dfo.loc[2008, '10'] / dfo.loc[2008, 'totalt'])}% of those born 2008", "debut 10-andel")
d12 = {c: dfo.loc[c, "12"] / dfo.loc[c, "totalt"] for c in (2006, 2007, 2008)}
k.need("results", f"({pst(d12[2008])}% debuted at 12, against {pst(min(d12[2006], d12[2007]))}--"
       f"{pst(max(d12[2006], d12[2007]))}% in the two preceding cohorts)", "2008 og 2020")
d10 = {c: dfo.loc[c, "10"] / dfo.loc[c, "totalt"] for c in range(2001, 2006)}
krav(d10[2001] == min(d10.values()), "2001-kullet lavest andel debut ved 10 (2011-dekning)")
sen_andel = dfo[["14", "15", "16"]].sum().sum() / dfo["totalt"].sum()
krav(0.14 <= sen_andel <= 0.19, f"«one in six» ({sen_andel:.3f})")
k.need("results", "roughly one debutant in six entered at 14 or later", "sen debut")
g = [prim[prim["debut_alder"].between(10, 11)], prim[prim["debut_alder"].between(12, 13)],
     prim[prim["debut_alder"].between(14, 16)]]
k.need("results", f"(female share {pst((g[0]['gender'] == 'F').mean())}% for debut at 10--11 against "
       f"{pst((g[2]['gender'] == 'F').mean())}% for 14--16)", "kjønnsandel")
krav(all(x["vol_debutaar"].median() == 1 for x in g), "median debutant: én dag")
krav(g[0]["karriere_aar"].median() == 2 and g[1]["karriere_aar"].median() == 1 and g[2]["karriere_aar"].median() == 1,
     "karrierelengde 2/1/1")
k.need("results", "the median debutant competed on a single day in the debut season, and median career length was two "
       "seasons for debut at 10--11 and one season otherwise", "debutsesong")
k.need("results", f"existed for {pst(g[0]['kvartal'].notna().mean())}% of early, {pst(g[1]['kvartal'].notna().mean())}% of mid, "
       f"and {pst(g[2]['kvartal'].notna().mean())}% of late debutants", "fødselsdato")
pq = prim[prim["kvartal"].notna()]
qs = pq.groupby("debut_alder")["kvartal"].agg(q1=lambda x: (x == 1).mean(), q4=lambda x: (x == 4).mean())
krav((qs["q1"] > qs["q4"]).all(), "Q1 > Q4 ved hver debutalder")
k.need("results", f"(Q1 {pst(qs['q1'].min(), 0)}--{pst(qs['q1'].max(), 0)}% against Q4 {pst(qs['q4'].min(), 0)}--"
       f"{pst(qs['q4'].max(), 0)}%)", "kvartaler")
krav(prim[prim["debut_alder"] <= 14]["covid_debut"].sum() == 0, "covid-debut bare ved 15–16 år")
k.need("results", f"Of the {len(prim)} debutants, {int(prim['senior'].sum())} ({pst(prim['senior'].mean())}%) were active", "H1 n")
n10, s10 = len(prim[prim["debut_alder"] == 10]), int(prim[prim["debut_alder"] == 10]["senior"].sum())
n16, s16 = len(prim[prim["debut_alder"] == 16]), int(prim[prim["debut_alder"] == 16]["senior"].sum())
k.need("results", f"it was {pst(konv(10))}% for debut at 10 ({s10}/{n10}), fell to {pst(konv(11))}% at 11, {pst(konv(12))}% at 12, "
       f"{pst(konv(13))}% at 13 and {pst(konv(14))}% at 14, and rose to {pst(konv(15))}% at 15 and {pst(konv(16))}% at 16 "
       f"({s16}/{n16})", "rå konvertering")
k.need("results", f"(LR = {f(lrt['LR'], 1)}, df = {int(lrt['df'])}, p = {float(lrt['p']):.1e}".replace("e-0", " × 10$^{-")
       .replace("p = 3.3 × 10$^{-8", "p = 3.3 × 10$^{-8}$"), "LRT tekst")
sign = [a for a in [11, 12, 14] if kat[a]["KI_hoy"] < 1]
krav(sign == [11, 12, 14] and kat[13]["KI_hoy"] > 1, "11/12/14 signifikante, 13 ikke")
k.need("results", "debuts at 11, 12 and 14 had significantly lower odds", "signifikante debutaldre")
k.need("results", f"(OR {f(min(kat[a]['OR'] for a in [11, 12, 14]), 2)}--{f(max(kat[a]['OR'] for a in [11, 12, 14]), 2)}), "
       f"debut at 13 directionally lower odds (OR {f(kat[13]['OR'], 2)}, 95% CI {f(kat[13]['KI_lav'], 2)}--{f(kat[13]['KI_hoy'], 2)}), "
       f"debut at 15 the same odds (OR {f(kat[15]['OR'], 2)}), and debut at 16 markedly higher odds (OR {f(kat[16]['OR'], 2)}, "
       f"95% CI {f(kat[16]['KI_lav'], 2)}--{f(kat[16]['KI_hoy'], 2)}, resting on {s16} events)", "H1 kategorier")
k.need("results", f"correspondingly null (OR {f(tr['OR'], 2)} per year, 95% CI {f(tr['KI_lav'], 2)}--{f(tr['KI_hoy'], 2)})",
       "H1 trend tekst")
k.need("results", "between four (debut at 16) and ten (debut at 10) seasons to cover before the outcome window",
       "avstand til utfallsalder (20 − debutalder)")
kv = kk.set_index(["debut_alder", "gender"])["andel_pst"]
krav(all(kv[(a, "M")] > kv[(a, "F")] for a in range(10, 17)), "gutter høyere ved hver debutalder")
k.need("results", f"({f(kv[(10, 'M')], 1)} vs. {f(kv[(10, 'F')], 1)}% at debut 10; {f(kv[(16, 'M')], 1)} vs. {f(kv[(16, 'F')], 1)}% "
       f"at debut 16; Supplementary Table S3)", "kjønn")
k.need("results", f"({pst((g[2]['gender'] == 'F').mean())}% female at debut 14--16)", "kjønn 14-16")
xi = rad(kxi, "r1_kjonnsinteraksjon", "debut_x_kvinne")
k.need("results", f"(OR {f(xi['OR'], 2)} per year, 95% CI {f(xi['KI_lav'], 2)}--{f(xi['KI_hoy'], 2)})", "kjønnsinteraksjon")
k.need("results", f"(n = {len(prim)}; {int(prim['senior'].sum())} senior events, {int(vt[4]['hendelser'])} equal-career-length events)",
       "tabell 2 tittel")
k.need("results", f"(LR = {f(lrt['LR'], 1)}, df = {int(lrt['df'])}, p < 0.001); the debut-16 senior estimate rests on {s16} events",
       "tabell 2 tekst")
k.need("results", f"{pst(k1[10], 0)}% of those who debuted at 10 were still competing, against {pst(min(k1[a] for a in range(11, 15)), 0)}--"
       f"{pst(max(k1[a] for a in range(11, 15)), 0)}% of those who debuted at 11--14, {pst(k1[15], 0)}% at 15, and "
       f"{pst(k1[16], 0)}% at 16", "retention k1")
k.need("results", f"widened to {pst(k5[10], 0)}% (debut 10) and {pst(k5[11], 0)}% (debut 11) against {pst(min(s12_16), 0)}--"
       f"{pst(max(s12_16), 0)}% (debuts 12--16)", "retention k5 tekst")
n16k = {k_: int(ret(16, k_)["n"]) for k_ in range(1, 6)}
krav(all(int(ret(a, k_)["n"]) == int(ret(a, 1)["n"]) for a in range(10, 16) for k_ in range(1, 6)), "nevnere like unntatt debut 16")
krav(all(n16k[k_] == n16k[1] for k_ in range(1, 5)), "debut 16: k ≤ 4 lik nevner")
k.need("results", f"({n16k[1]} at $k$ = 1 to {n16k[5]} at $k$ = 5)", "nevnere tekst")
k.need("results", f"shrink from {n16k[1]} ($k \\leq 4$) to {n16k[5]} ($k$ = 5)", "nevnere tabelltekst")
k.need("results", f"{pst(v4[10])}% of those who debuted at 10 competed on at least two days in a season four or more years later, "
       f"against {pst(v4[11])}% at 11, {pst(min(v4[12], v4[13]))}--{pst(max(v4[12], v4[13]))}% at 12--13 and "
       f"{pst(min(v4_sen))}--{pst(max(v4_sen))}% at 14--16, an adjusted OR of {f(vt[4]['OR'], 2)} per year of later debut "
       f"(95% CI {f(vt[4]['KI_lav'], 2)}--{f(vt[4]['KI_hoy'], 2)}), essentially unchanged at five ({f(vt[5]['OR'], 2)}) and six "
       f"years ({f(vt[6]['OR'], 2)}; Supplementary Table S4)", "lik karrierelengde tekst")
krav(abs(vt[5]["OR"] - vt[4]["OR"]) < 0.05 and abs(vt[6]["OR"] - vt[4]["OR"]) < 0.05, "«essentially unchanged» ved 5 og 6 år")
k.need("results", f"({pst(da[(16, '14-16')])}% with a result at 16 or later, against {pst(da[(16, '10-11')])} and "
       f"{pst(da[(16, '12-13')])}% in the earlier groups)", "andel ved 16")
k.need("results", f"at 20, {pst(da[(20, '10-11')])}, {pst(da[(20, '12-13')])} and {pst(da[(20, '14-16')])}% of the three groups "
       f"were still competing, and at 21, {pst(da[(21, '10-11')])}, {pst(da[(21, '12-13')])} and {pst(da[(21, '14-16')])}%",
       "andel ved 20 og 21")
for t in (19, 20, 21):
    krav(abs(da[(t, "10-11")] - da[(t, "14-16")]) < 0.01, f"«close from about 19» ved {t} (tidlig mot sen < 1 pp)")
k.need("results", f"Of the {len(prim)} debutants, {n_lm} ({pst(n_lm / len(prim))}%) competed in the age-17 season itself; {s_lm} of these "
       f"({pst(s_lm / n_lm)}%) became active seniors, while {idle} seniors", "landmark")
k.need("results", f"OR {f(h3u['OR'], 2)} per year of later debut (95% CI {f(h3u['KI_lav'], 2)}--{f(h3u['KI_hoy'], 2)})", "H3 uten tekst")
k.need("results", f"(OR {f(h3m['OR'], 2)}, 95% CI {f(h3m['KI_lav'], 2)}--{f(h3m['KI_hoy'], 2)})", "H3 med tekst")
ro = {n: rad(rob, n) for n in ["uten_covid_debut", "utfall_min1", "utfall_aktiv17_debut_10_14", "betinget_debutvolum",
                               "kohort_2001_2003", "kohort_2004_2005"]}
ut01, uk = rad(u01, "uten_2001_trend"), rad(ukj, "med_ukjent_kjonn_trend")
k.need("results", f"Excluding COVID-era debuts gave {f(ro['uten_covid_debut']['OR'], 2)} (95% CI {f(ro['uten_covid_debut']['KI_lav'], 2)}--"
       f"{f(ro['uten_covid_debut']['KI_hoy'], 2)}); excluding the 2001 cohort, whose debut-at-10 season fell in the thinly "
       f"covered 2011, gave {f(ut01['OR'], 2)}; including the {int(uk['n_ukjent'])} athletes without registered sex as a separate "
       f"category gave {f(uk['OR'], 2)}, with debut-10 conversion {pst(uk['konvertering_debut10'])} instead of {pst(konv(10))}%; "
       f"the one-result senior outcome gave {f(ro['utfall_min1']['OR'], 2)}; activity at 17 among debuts at 10--14 gave "
       f"{f(ro['utfall_aktiv17_debut_10_14']['OR'], 2)}; conditioning on debut-season volume gave a borderline "
       f"{f(ro['betinget_debutvolum']['OR'], 2)} (95% CI {f(ro['betinget_debutvolum']['KI_lav'], 2)}--"
       f"{f(ro['betinget_debutvolum']['KI_hoy'], 2)}); and the cohort halves agreed ({f(ro['kohort_2001_2003']['OR'], 2)} and "
       f"{f(ro['kohort_2004_2005']['OR'], 2)})", "robusthet")
krav(all(0.9 <= x <= 1.1 for x in [ro[n]["OR"] for n in ro] + [ut01["OR"], uk["OR"]]), "ingen variant langt fra null")
t17 = rad(d17, "r1_debut_17_19", "debut_kat_17")
k.need("results", f"excluding the {int(fd17.get(20, 0))} athletes whose first registered result came at age 20 or later", "debut 20+")
k.need("results", f"(OR {f(t17['OR'], 2)} vs. debut at 10, 95% CI {f(t17['KI_lav'], 2)}--{f(t17['KI_hoy'], 2)}; within the late group, "
       f"{int(fd17[17])} debuted at 17, {int(fd17[18])} at 18 and {int(fd17[19])} at 19)", "debut 17-19")
k.need("results", "Estimates are for debut age (per +1 year, linear)", "tabell 4 tekst")

# ================================================================ DISCUSSION / PERSPECTIVE
krav(konv(10) > max(konv(a) for a in range(11, 15)), "debut 10 konverterer bedre enn 11–14")
k.need("discussion", "highest for the earliest (10) and the latest (16, and 17+) entrants", "U-armer")
q14_16 = [k1[a] for a in [14, 15, 16]]
krav(abs(k1[10] - 0.5) < 0.03 and 0.24 <= min(q14_16) and max(q14_16) <= 0.36, "«half … a quarter to a third»")
k.need("discussion", "half of the ten-year-old debutants surviving the first year against roughly a quarter to a third of those "
       "debuting at 14--16", "k1 diskusjon")
k.need("discussion", f"the odds of still competing were {int(round((1 - vt[4]['OR']) * 100, -1))}% lower per year of later debut",
       "1 − OR, avrundet til tier")
krav(v4[15] < v4[10] and v4[16] < v4[10] and t17["OR"] > 1, "sene: høy fast-alder-konvertering, lav ved lik karrierelengde")
utl = [1 - k1[a] for a in range(10, 17)]
krav(0.45 <= min(utl) and max(utl) <= 0.76, f"«half and three quarters» ({min(utl):.2f}–{max(utl):.2f})")
k.need("discussion", "between half and three quarters of each entry cohort never established themselves", "første sesong")
k.need("discussion", f"The senior outcome is rare ({pst(prim['senior'].mean())}%)", "sjeldent utfall")
k.need("discussion", f"{pst(sel['senior=1'])}% of the seniors but {pst(sel['senior=0'])}% of the other athletes have one",
       "fødselsdato-seleksjon diskusjon")
alle = ad[ad["kohort_primar"]]
krav(all(alle[alle["debut_alder"] == a]["senior"].sum() > 0 for a in range(10, 20)), "hver debutalder 10–19 ga seniorer")
k.need("perspective", "every entry age from 10 to 19 produced senior athletes", "hver alder")
k.need("perspective", f"convert at the observed {pst(konv(16))}%", "6,6 %")
k.need("perspective", "between half and three quarters of every entry cohort resolves within two seasons", "første sesonger")

# ================================================================ SUPPLEMENT-NOTER
k.need("supplementary material", f"Denominators equal the debut-age n except debut 16 at $k$ = 5 (n = {n16k[5]})", "S2-tekst")
k.need("supplementary material", f"OR {f(xi['OR'], 2)} per year for girls relative to boys, 95% CI {f(xi['KI_lav'], 2)}--"
       f"{f(xi['KI_hoy'], 2)}", "S3-note")

# ================================================================ ORDTELLING
ord_n = ordtelling(PROSJ / "manus" / "main.tex")
k.need("tittelside", f"Word count: $\\sim${int(round(ord_n, -2))}", f"ordtelling ({ord_n})")

# ================================================================ DEKNING
UNNTAK = [
    r"\\vspace\*?\{[^}]*\}", r"\d*\.?\d+\\textwidth", r"orcid\.org/[\d-]+\}\{ORCID: [\d-]+\}", r"Box 5003, 1432",
    r"\$\^\{?1,?\*?\}?\$", r"\$\^1\$", r"\\begin\{titlepage\}",
    r"\b(19|20)\d\d\b", r"\b(19|20)\d\d--(19|20)\d\d\b", r"\bH[1-3]\b", r"\bS[1-4]\b",
    r"\b(10|11|12|13|14|15|16|17)--(11|13|14|16|17|19)\b", r"\bages? (10|13|14|16|17|20|21)\b", r"age ≥(17|20)", r"≥(4|17|20)\b",
    r"age-1[07]", r"17\+", r"\(10\)", r"\b17-year-old", r"survival to 17", r"debut at 1[0-6]\b", r"debuts? at 1[0-6]\b",
    r"debuted at 1[0-6]\b", r"debut 1[0-6]\b", r"debuts 1[0-6]--1[0-6]", r"at 1[0-6]\b", r"\$k\$ ?= ?[1-5](--5)?", r"\$k\$=\d",
    r"\$k \\leq 4\$", r"\+1 year", r"95% (CIs?|confidence|intervals)", r"95% CI\b", r"COVID-19", r"29 October( 2026)?",
    r"10 to 19", r"from age 10", r"begins at age 10", r"age 10 or older", r"rows below age 10",
    r"below age 13", r"Wilson 95%", r"\bten-year-old", r"\btwofold", r"one debutant in six", r"\bthree\b",
    r"10\$\^\{-8\}\$", r"age 20 or later", r"at age 20\b", r"at age 17 or later", r"in the age-17 season",
    r"competing at 17", r"active at age 17", r"at ages 15 and 16", r"sub-age-10", r"10--12 age classes",
    r"Section 3\.3", r"at least 4, 5 and 6 years", r"result at 16 or later", r"from about 19", r"at 20, ", r"at 21, ",
    r"before age 20", r"\bat 19\b", r"debut-at-10", r"debut-10", r"debut-16", r"age 21 for everyone",
    r"At 16 the late group",
]
kode_m = k.rapport(UNNTAK)
print(f"\nA3 TOTALT: {k.n_ok} sjekker OK, {len(k.feil)} feil")
sys.exit(1 if kode_m else 0)
