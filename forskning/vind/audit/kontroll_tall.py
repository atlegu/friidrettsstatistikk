"""
kontroll_tall.py — A6-audit fase 4: hvert tall i manus og svarbrev mot estimeringsfilene.

Kjøres etter 07–10 (og R-kontrollen audit/sammenlign.py). Hver sjekk er en ankret frase
bygget fra filene; dekningskontrollen lister tall som ingen sjekk dekker. Tabellene
genereres av 09 og kontrolleres her mot R-implementasjonens fullpresisjonsverdier.
Avslutter med kode 1 ved avvik.
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
from audit_felles import Kontroll, avrund as f, ordtelling, sitatkontroll, tall_i  # noqa: E402

EST = PROSJ / "tables" / "estimering"
DATA = PROSJ / "data_private"
R = HER / "r_out"
SPRINT = ["60m", "80m", "100m", "150m", "200m"]
HOPP = ["lengde", "lengde_sone_05m", "tresteg", "tresteg_sone_05m"]


def les(n):
    return pd.read_csv(EST / n)


def pst(x, d=0):
    return f(100 * x, d)


# ---------------------------------------------------------------- kilder
hov = les("r1_hoved_meet.csv")
al = les("r1_alder_meet.csv")
asy = les("r1_asym_meet.csv").set_index("event")
vin = les("r1_vindu_medvind.csv")
hk = les("r1_hekk_meet.csv")
ter = les("r1_tertil_adj.csv")
kv = les("r1_kvad_meet.csv").set_index("event")
ps = les("r1_per_sekund.csv").set_index("event")
bun = les("r1_bunching.csv").set_index("intervall")["andel"]
mvs = les("r1_missingvind_storrelse.csv").set_index("stevnestr")["mean"]
mvn = les("r1_missingvind_nivaa.csv").iloc[0]
mva = les("r1_missingvind_aar.csv")
inn = les("r1_innendors_per_ovelse.csv").set_index("event_code")["innendorsrader"]
tyr = les("r1_tyrvingpoeng.csv")
oms = les("r1_listeomstokk.csv")
eiv = les("r1_eiv.csv").set_index("event")
ins = les("r1_innen_stevne.csv").set_index("event")["andel_innen_stevne"]
rob = les("robusthet.csv").pivot_table(index="event", columns="analyse", values="gevinst_per_ms")
u2 = les("r1_uten_2.csv").set_index("event")["gevinst_per_ms"]
hut = les("hoved.csv")
flyt = json.loads((DATA / "flyt.json").read_text())
d = pd.read_csv(DATA / "analyseklar.csv",
                usecols=["event_code", "wind", "y", "gender", "aldersband", "n_i_celle"])


def h(k, pct=False):
    return hov[(hov["analyse"] == ("hoved_meet_pst" if pct else "hoved_meet"))
               & (hov["event"] == k)].iloc[0]


def a(e, k, b, u="s"):
    return al[(al["event"] == e) & (al["kjonn"] == k) & (al["aldersband"] == b)
              & (al["enhet"] == u)].iloc[0]


def v(e, k, b):
    return vin[(vin["event"] == e) & (vin["kjonn"] == k) & (vin["aldersband"] == b)].iloc[0]


def tt(e, t):
    return ter[(ter["event"] == e) & (ter["tertil"] == t)].iloc[0]


def snitt(e, k, b):
    return d[(d["event_code"] == e) & (d["gender"] == k) & (d["aldersband"] == b)]["y"].mean()


def ki_s(r, dd=3, enhet=" s"):
    return f"{f(r['gevinst_per_ms'], dd)}{enhet} ({f(r['ki_lav'], dd)}--{f(r['ki_hoy'], dd)})"


k = Kontroll(PROSJ / "manus" / "main.tex", "A6 manus")
FEIL = k.feil


def krav(betingelse, hvorfor):
    """En påstand som ikke er et enkelt tall (monotoni, overlapp, «essentially unchanged»)."""
    if betingelse:
        k.n_ok += 1
    else:
        FEIL.append(f"PÅSTAND holder ikke: {hvorfor}")


# ================================================================ ABSTRACT
k.need("abstract", f"{flyt['rader_analyseklar']} analysed results, of which "
       f"{flyt['rader_i_celler_min2']}, lying in {flyt['celler_min2']} athlete-season-event cells",
       "utvalg")
k.need("abstract", f"A +1 m/s tailwind was worth {f(h('60m')['gevinst_per_ms'], 3)} s on 60 m, "
       f"{f(h('100m')['gevinst_per_ms'], 3)} s on 100 m, {f(h('200m')['gevinst_per_ms'], 3)} s on "
       f"200 m, {f(h('lengde')['gevinst_per_ms'], 1)} cm in the long jump and "
       f"{f(h('tresteg')['gevinst_per_ms'], 1)} cm in the triple jump", "hovedeffekter")
k.need("abstract", f"(200 m, males: {f(a('200m', 'M', '10-11')['gevinst_per_ms'], 3)} s per m/s "
       f"at 10--11 to {f(a('200m', 'M', '20-34')['gevinst_per_ms'], 3)} at 20--34)", "200 m alder")
rett = [ps.loc[e, "per_sekund"] for e in ["60m", "80m", "100m"]]
sving = [ps.loc[e, "per_sekund"] for e in ["150m", "200m"]]
per_sek = (f"{f(min(rett), 4)}--{f(max(rett), 4)} s per m/s in the straight sprints against "
           f"{f(min(sving), 4)}--{f(max(sving), 4)} in the bend events")
k.need("abstract", per_sek, "per sekund")
k.need("abstract", f"(100 m: {f(asy.loc['100m', 'motvind'], 3)} vs. "
       f"{f(asy.loc['100m', 'medvind'], 3)} s per m/s, p < 0.001)", "asymmetri 100 m")
krav(asy.loc["100m", "p_lik_meet"] < 0.001, "100 m p < 0.001")
h100 = hk[(hk["kjonn"] != "begge") & hk["kode"].str.startswith(("100mh", "110mh"))
          & hk["flat_ref"].notna()].copy()
h100["ratio"] = h100["gevinst_s_per_ms"] / h100["flat_ref"] - 1
h60 = hk[(hk["kjonn"] != "begge") & hk["kode"].str.startswith("60mh")].copy()
h60["ratio"] = h60["gevinst_s_per_ms"] / h60["flat_ref"] - 1
k.need("abstract", f"mostly exceeded the flat 100 m (by up to {pst(h100['ratio'].max())}%)",
       "hekk maks")
krav((h100["ratio"] > 0).sum() > len(h100) / 2, "100/110 m hekk «mostly exceeded»")
v12 = [v("100m", kj, "12-13")["fordel_2ms_s"] for kj in ["M", "F"]]
vs = [v("100m", kj, "20-34")["fordel_2ms_s"] for kj in ["M", "F"]]
k.need("abstract", f"worth {f(min(v12), 2)}--{f(max(v12), 2)} s on the 100 m at 12--13 against "
       f"{f(min(vs), 2)}--{f(max(vs), 2)} s among seniors --- everywhere "
       f"{f(vin['fordel_i_sd'].min(), 1)}--{f(vin['fordel_i_sd'].max(), 1)} of the athlete's own",
       "H5 abstract")

# ================================================================ INTRODUCTION
k.need("introduction", "roughly 0.04--0.06 s per m/s in the 100 m", "litteraturverdi (elite)")
r12 = snitt("100m", "M", "12-13") / snitt("100m", "M", "20-34")
krav(1.28 <= r12 <= 1.38, f"«roughly a third more time» (forhold {r12:.3f})")
k.need("introduction", "a 12-year-old needs roughly a third more time over 100 m", "tidsforhold")

# ================================================================ METHODS
k.need("methods", f"Of {flyt['rader_uttrekk']} extracted rows in the main events, "
       f"{flyt['rader_analyseklar']} entered the analysis", "flyt")
k.need("methods", f"the indoor 60 m ({inn['60m']} rows), long jump ({inn['lengde']}) and 200 m "
       f"({inn['200m']})", "innendørs")
krav(list(inn.sort_values(ascending=False).index[:3]) == ["60m", "lengde", "200m"],
     "innendørs: 60 m, lengde, 200 m er de tre største")
k.need("methods", f"{flyt['uten_vindverdi']} outdoor rows without a wind value (overall, "
       f"{pst(mvn['mean'], 1)}% of approved outdoor results lack a reading)", "manglende vind")
k.need("methods", f"({pst(mvs['minste tredel'], 1)}% of rows in the smallest third of meets by "
       f"size, against {pst(mvs['storste tredel'], 1)}% in the largest third)", "stevnestørrelse")
k.need("methods", f"fluctuates between {pst(mva['mangler'].min())} and "
       f"{pst(mva['mangler'].max())}%", "per år")
k.need("methods", f"Of the analysed rows, {flyt['rader_i_celler_min2']} lie in", "celler")
hr = pd.read_csv(DATA / "resultater_hekk.csv", low_memory=False, parse_dates=["date"])
utv = pd.read_csv(DATA / "utovere.csv").rename(columns={"id": "athlete_id"})
me = pd.read_csv(DATA / "meets.csv").rename(columns={"id": "meet_id"})
hr = hr.merge(utv, on="athlete_id", how="left").merge(me[["meet_id", "indoor"]], on="meet_id",
                                                     how="left")
hr = hr[(hr["status"] == "OK") & (hr["indoor"].astype(str) != "True")
        & (hr["is_manual_time"].astype(str) != "True") & hr["gender"].isin(["M", "F"])
        & hr["birth_year"].notna()]
hr["alder"] = hr["date"].dt.year - hr["birth_year"]
hr = hr[hr["alder"].between(10, 34) & hr["wind"].notna() & (hr["wind"].abs() <= 8)]
hy = hr["performance_value"] / 100
gr = {"60mh": (7.5, 20), "80mh": (10, 26), "100mh": (12, 32), "110mh": (13, 34)}
dist = hr["event_code"].str.split("_").str[0]
n_hekk = int(((hy >= dist.map(lambda x: gr[x][0])) & (hy <= dist.map(lambda x: gr[x][1]))).sum())
k.need("methods", f"the hurdles extension contributed {n_hekk} analysed rows", "hekk rader")
sys.path.insert(0, str(PROSJ))
import importlib.util  # noqa: E402
spec = importlib.util.spec_from_file_location("m03", PROSJ / "03_estimering.py")
m03 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m03)
k.need("methods", f"{flyt['celler_min2']} athlete-season-event cells contribute at least two wind-measured "
       f"results, and estimates are reported only where at least {m03.MIN_N} results in "
       f"{m03.MIN_CELLER} athlete-seasons contribute", "terskel")
hu = hut[(hut["analyse"] == "hoved") & (hut["enhet"] != "%")].set_index("event")
hm = hov[hov["analyse"] == "hoved_meet"].set_index("event")
bredde = (hm["ki_hoy"] - hm["ki_lav"]) / (hu["ki_hoy"] - hu["ki_lav"])
krav(all(1.4 <= bredde[e] <= 2.1 for e in ["60m", "100m", "200m"])
     and all(0.75 <= bredde[e] <= 1.25 for e in ["80m", "150m"] + HOPP),
     f"KI-bredde stevne/utøver: {bredde.round(2).to_dict()}")
k.need("methods", "intervals roughly half as wide in the large sprints and similar ones elsewhere",
       "klyngebredde")
import statsmodels  # noqa: E402
k.need("methods", f"Python {sys.version.split()[0]} with pandas {pd.__version__}, numpy "
       f"{np.__version__} and statsmodels {statsmodels.__version__}", "versjoner")

# ================================================================ RESULTS
w = d["wind"]
k.need("results", f"(median {w.median():+.1f} m/s; 5th--95th percentile {w.quantile(.05):+.1f} to "
       f"{w.quantile(.95):+.1f})", "vindfordeling")
k.need("results", f"{pst(bun['eksakt 0.0'], 1)}% of readings are exactly 0.0", "nuller")
k.need("results", f"and {pst((w == w.round()).mean())}% fall on whole metres per second", "heltall")
k.need("results", f"{pst(bun['(1.8,2.0]'], 1)}% of readings lie in (1.8, 2.0] against "
       f"{pst(bun['(2.0,2.2]'], 1)}% in (2.0, 2.2], with {pst(bun['eksakt 2.0'], 1)}% exactly +2.0",
       "bunching")
d60 = d[d["event_code"] == "60m"]
krav(d["event_code"].value_counts().idxmax() == "60m", "60 m største øvelse")
k.need("results", f"({len(d60)} analysed results, of which {int((d60['n_i_celle'] >= 2).sum())} lie in",
       "60 m")
pr = [h(e, True)["gevinst_per_ms"] for e in SPRINT + HOPP]
k.need("results", f"A +1 m/s tailwind was worth {ki_s(h('60m'))[:-1].replace(' s (', ' s (95% CI ')}",
       "H1 60 m") if False else None
k.need("results", f"A +1 m/s tailwind was worth {f(h('60m')['gevinst_per_ms'], 3)} s (95% CI "
       f"{f(h('60m')['ki_lav'], 3)}--{f(h('60m')['ki_hoy'], 3)}) on 60 m, {ki_s(h('100m'))} on "
       f"100 m, {ki_s(h('200m'))} on 200 m, {ki_s(h('lengde'), 1, ' cm')} in the long jump and "
       f"{ki_s(h('tresteg'), 1, ' cm')} in the triple jump; in percentage terms, "
       f"{f(min(pr), 2)}--{f(max(pr), 2)}% per m/s", "H1 tekst")
k.need("results", f"our 100 m estimate falls to {f(a('100m', 'M', '20-34')['gevinst_per_ms'], 3)} s "
       f"per m/s for men and {f(a('100m', 'F', '20-34')['gevinst_per_ms'], 3)} for women", "senior")
k.need("results", f"averaging about {f(snitt('100m', 'M', '20-34'), 1)} s on the 100 m", "senior tid")
k.need("results", "published figures of roughly 0.04--0.06 s per m/s", "litteraturverdi")
# monotoni
brudd = []
for e in ["60m", "100m", "200m"]:
    for kj in ["M", "F"]:
        s = al[(al["event"] == e) & (al["kjonn"] == kj) & (al["enhet"] == "s")].sort_values("aldersband")
        g = s["gevinst_per_ms"].to_numpy()
        brudd += [f"{e} {kj} {s['aldersband'].iloc[i]}" for i in range(len(g) - 1) if g[i + 1] > g[i]]
krav(brudd == ["200m F 10-11"], f"monotoni-unntak: {brudd}")
k.need("results", "monotonically in every series except the sparse girls' 200 m at 10--11",
       "monotoni")
k.need("results", f"on 200 m for boys and men from {f(a('200m', 'M', '10-11')['gevinst_per_ms'], 3)} s "
       f"per m/s at 10--11 to {f(a('200m', 'M', '20-34')['gevinst_per_ms'], 3)} at 20--34; on 60 m from "
       f"{f(a('60m', 'M', '10-11')['gevinst_per_ms'], 3)} at 10--11 to "
       f"{f(a('60m', 'M', '16-17')['gevinst_per_ms'], 3)} at 16--17; on 100 m from "
       f"{f(a('100m', 'M', '12-13')['gevinst_per_ms'], 3)} at 12--13 to "
       f"{f(a('100m', 'M', '20-34')['gevinst_per_ms'], 3)} at 20--34", "H2 tekst")
t12, t20 = snitt("100m", "M", "12-13"), snitt("100m", "M", "20-34")
rv = a("100m", "M", "12-13")["gevinst_per_ms"] / a("100m", "M", "20-34")["gevinst_per_ms"]
k.need("results", f"(men's 100 m, {f(t12, 2)} s at 12--13 vs. {f(t20, 2)} s at 20--34, a ratio of "
       f"{f(t12 / t20, 2)}, against a wind-effect ratio of {f(rv, 2)})", "eksponeringstid")
k.need("results", f"from {f(a('100m', 'M', '12-13', '%')['gevinst_per_ms'], 2)} to "
       f"{f(a('100m', 'M', '20-34', '%')['gevinst_per_ms'], 2)}% per m/s on the men's 100 m and from "
       f"{f(a('60m', 'M', '10-11', '%')['gevinst_per_ms'], 2)} to "
       f"{f(a('60m', 'M', '16-17', '%')['gevinst_per_ms'], 2)}% on the 60 m", "prosent")
k.need("results", f"the straight sprints line up at {f(min(rett), 4)}--{f(max(rett), 4)} s per m/s "
       f"per second of race time, while the bend events sit a third lower (150 m "
       f"{f(ps.loc['150m', 'per_sekund'], 4)}, 200 m {f(ps.loc['200m', 'per_sekund'], 4)})", "svingløp")
lavere = 1 - np.mean(sving) / np.mean(rett)
krav(0.27 <= lavere <= 0.40, f"«a third lower» ({lavere:.3f})")
lf12, lf20 = a("lengde", "F", "12-13", "cm")["gevinst_per_ms"], a("lengde", "F", "20-34", "cm")["gevinst_per_ms"]
k.need("results", f"(long jump, girls/women: {f(lf12, 1)} cm per m/s at 12--13 to {f(lf20, 1)} at "
       f"20--34; boys/men flatter)", "lengde")
lm = al[(al["event"] == "lengde") & (al["enhet"] == "cm")]
spenn = lm.groupby("kjonn")["gevinst_per_ms"].agg(lambda s: s.max() - s.min())
krav(spenn["M"] < spenn["F"], "lengde: gutter flatere enn jenter")
k.need("results", f"(100 m: {f(tt('100m', 'lav')['gevinst_per_ms'], 3)} s against "
       f"{f(tt('100m', 'hoy')['gevinst_per_ms'], 3)} in the highest tertile; 60 m: "
       f"{f(tt('60m', 'lav')['gevinst_per_ms'], 3)} against {f(tt('60m', 'hoy')['gevinst_per_ms'], 3)}; "
       f"200 m: {f(tt('200m', 'lav')['gevinst_per_ms'], 3)} against "
       f"{f(tt('200m', 'hoy')['gevinst_per_ms'], 3)})", "tertiler")
alle_sprint = [e for e in SPRINT if set(ter[ter["event"] == e]["tertil"]) == {"lav", "midt", "hoy"}]
krav(all(tt(e, "lav")["gevinst_per_ms"] == ter[ter["event"] == e]["gevinst_per_ms"].max()
         for e in alle_sprint), f"lavtertil høyest i hver sprint ({alle_sprint})")
k.need("results", "the lowest tertile gained most per m/s in every sprint", "tertil-påstand")
for e in ["lengde", "lengde_sone_05m", "tresteg"]:
    tj = ter[ter["event"] == e]
    krav(tj["ki_lav"].max() <= tj["ki_hoy"].min(), f"hopptertiler overlapper ({e})")
k.need("results", "the jump tertiles did not separate", "hopp-tertiler")
k.need("results", f"cost {f(asy.loc['100m', 'motvind'], 3)} s against a +1 m/s tailwind's "
       f"{f(asy.loc['100m', 'medvind'], 3)} s (p < 0.001 for equal slopes); on 200 m, "
       f"{f(asy.loc['200m', 'motvind'], 3)} against {f(asy.loc['200m', 'medvind'], 3)}; on 60 m, "
       f"{f(asy.loc['60m', 'motvind'], 3)} against {f(asy.loc['60m', 'medvind'], 3)}", "H4")
krav(all(asy.loc[e, "motvind"] > asy.loc[e, "medvind"] for e in ["60m", "100m", "200m"]),
     "motvind > medvind i store sprintøvelser")
k.need("results", f"(200 m: +{f(kv.loc['200m', 'beta_kvad'], 4)} s per (m/s)$^2$, SE "
       f"{f(kv.loc['200m', 'se_kvad'], 4)}; Table S5)", "kvadratisk")
teor = asy.loc[SPRINT, "ratio_teoretisk_v2"]
k.need("results", f"{f(teor.min(), 2)}--{f(teor.max(), 2)}, while the observed ratios are "
       f"{f(asy.loc['60m', 'ratio_obs'], 2)} (60 m), {f(asy.loc['100m', 'ratio_obs'], 2)} (100 m) and "
       f"{f(asy.loc['200m', 'ratio_obs'], 2)} (200 m)", "benchmark")
k.need("results", f"(long jump, p = {f(asy.loc['lengde', 'p_lik_meet'], 3)})", "lengde p")
krav(hk[hk["kjonn"] == "begge"]["kode"].nunique() == 10, "ti hekkoder")
k.need("results", "Across the ten codes with wind data", "ti koder")
k.need("results", f"0.055--0.067 s per m/s against 0.056--0.070".replace(
    "0.055", f(h60["gevinst_s_per_ms"].min(), 3)).replace("0.067", f(h60["gevinst_s_per_ms"].max(), 3))
    .replace("0.056", f(h60["flat_ref"].min(), 3)).replace("0.070", f(h60["flat_ref"].max(), 3))
    + f", point estimates from {pst(-h60['ratio'].min())}% below to {pst(h60['ratio'].max())}% above",
    "60 m hekk")
krav(h60["ki_overlapper_flat"].astype(bool).all(), "60 m hekk: alle KI overlapper")
k.need("results", f"from {pst(-h100['ratio'].min())}% below to {pst(h100['ratio'].max())}% above",
       "100/110 hekk")
ikke_ov = h100[~h100["ki_overlapper_flat"].astype(bool)]
krav(sorted(zip(ikke_ov["kode"], ikke_ov["kjonn"])) == [("100mh_76_2cm", "F"), ("100mh_84cm", "M")],
     f"ikke-overlappende: {list(zip(ikke_ov['kode'], ikke_ov['kjonn']))}")
g76 = hk[(hk["kode"] == "100mh_76_2cm") & (hk["kjonn"] == "F")].iloc[0]
b84 = hk[(hk["kode"] == "100mh_84cm") & (hk["kjonn"] == "M")].iloc[0]
w84 = hk[(hk["kode"] == "100mh_84cm") & (hk["kjonn"] == "F")].iloc[0]
k.need("results", f"girls' 76.2 cm ({f(g76['gevinst_s_per_ms'], 3)} against {f(g76['flat_ref'], 3)}) "
       f"and boys' 84 cm ({f(b84['gevinst_s_per_ms'], 3)} against {f(b84['flat_ref'], 3)})", "to klasser")
hp = hk[hk["kjonn"] == "begge"]["per_sekund"]
k.need("results", f"the pooled hurdle codes ({f(hp.min(), 4)}--{f(hp.max(), 4)} s per m/s)", "hekk/s")
krav(hp.min() <= min(rett) and hp.max() >= max(rett), "hekk spenner rettløpsratene")
k.need("results", f"{f(g76['gevinst_s_per_ms'], 3)} s per m/s for girls' 76.2 cm at "
       f"{g76['modal_aldersband'].replace('-', '--')} and {f(b84['gevinst_s_per_ms'], 3)} for boys' 84 cm "
       f"at {b84['modal_aldersband'].replace('-', '--')}, against {f(w84['gevinst_s_per_ms'], 3)} for the "
       f"senior women's 84 cm", "aldersgradient hekk")
k.need("results", f"{f(v('100m', 'M', '12-13')['fordel_2ms_s'], 2)} s on the boys' 100 m at 12--13 and "
       f"{f(v('100m', 'F', '12-13')['fordel_2ms_s'], 2)} s for girls, against "
       f"{f(v('100m', 'M', '20-34')['fordel_2ms_s'], 2)} and {f(v('100m', 'F', '20-34')['fordel_2ms_s'], 2)} "
       f"s among seniors; {f(v('200m', 'M', '10-11')['fordel_2ms_s'], 2)} s on the boys' 200 m at 10--11 "
       f"against {f(v('200m', 'M', '20-34')['fordel_2ms_s'], 2)} s for senior men", "H5 sekunder")
k.need("results", f"the window is worth {f(vin['fordel_i_sd'].min(), 1)}--"
       f"{f(vin['fordel_i_sd'].max(), 1)} SD across events, sexes and ages", "H5 SD")
ty = tyr.set_index(["kjonn", "aldersband"])["tyrvingpoeng_for_2ms"]
t13 = [ty[(kj, "12-13")] for kj in ["M", "F"]]
t19 = [ty[(kj, "20-34")] for kj in ["M", "F"]]
krav(set(tyr["tabellalder"]) == {13, 19}, "tabellalder 13 og 19")
k.need("results", f"converts to {int(min(t13))}--{int(max(t13))} points at age 13 against "
       f"{int(min(t19))}--{int(max(t19))} points on the oldest (age-19) table", "Tyrving")
om = oms.set_index(["kjonn", "liste"])
o14 = [om.loc[(kj, "klasse 14"), "plassendringer_topp10"] for kj in ["M", "F"]]
k.need("results", f"changes the athlete occupying {min(o14)}--{max(o14)} of the top-10 places in the "
       f"class-14 lists and {om.loc[('M', 'senior'), 'plassendringer_topp10']} of 10 in the senior men's "
       f"list, where {pst(om.loc[('M', 'senior'), 'andel_topp50_vind_over_1'])}% of top-50 marks",
       "listeomstokk")
fe = rob["stevne_fe"] / rob["primaer"] - 1
k.need("results", f"attenuated the 60, 100 and 200 m estimates by "
       f"{pst(-fe[['60m', '100m', '200m']].max())}--{pst(-fe[['60m', '100m', '200m']].min())}% "
       f"(100 m: {f(rob.loc['100m', 'primaer'], 3)} to {f(rob.loc['100m', 'stevne_fe'], 3)} s per m/s)",
       "stevne-FE sprint")
krav(fe[["80m", "150m"]].abs().max() < 0.05, f"80/150 m «essentially unchanged» ({fe[['80m', '150m']].round(3).to_dict()})")
k.need("results", f"raised the jump estimates by {pst(fe[HOPP].min())}--{pst(fe[HOPP].max())}%", "stevne-FE hopp")
k.need("results", f"only {pst(ins[SPRINT].min())}--{pst(ins[SPRINT].max())}% of their wind variance lies "
       f"within meets ({pst(ins[HOPP].min())}--{pst(ins[HOPP].max())}% in the jumps", "innen stevne")
sig = eiv["sigma_implisert"]
k.need("results", f"a gauge-error SD of {f(sig.min(), 2)}--{f(sig.max(), 2)} m/s (60 to 200 m)", "σ")
krav(sig.is_monotonic_increasing if list(eiv.index) == ["60m", "100m", "200m"] else False, "σ stiger 60→200")
k.need("results", f"reliability falling from {f(eiv['reliabilitet_primaer'].min(), 2)}--"
       f"{f(eiv['reliabilitet_primaer'].max(), 2)} to {f(eiv['reliabilitet_stevnefe'].min(), 2)}--"
       f"{f(eiv['reliabilitet_stevnefe'].max(), 2)}", "reliabilitet")
varianter = ["celler_min3", "uten_vind_0", "periode_2011_2019", "periode_2021_2026"]
endr = {(e, vv): rob.loc[e, vv] / rob.loc[e, "primaer"] - 1 for e in ["60m", "100m", "200m"]
        for vv in varianter if not pd.isna(rob.loc[e].get(vv))}
endr.update({(e, "uten2"): u2[e] / rob.loc[e, "primaer"] - 1 for e in ["60m", "100m", "200m"]})
krav(max(abs(x) for x in endr.values()) < 0.08,
     f"«essentially unchanged» i store sprint: maks {max(abs(x) for x in endr.values()):.3f}")
k.need("results", "Estimates were essentially unchanged when cells required three or more results",
       "robusthet (kvalitativ; tall i S2)")

# ================================================================ DISCUSSION / CONCLUSION
def relv(e, kj, b):
    return a(e, kj, b)["gevinst_per_ms"] / a(e, kj, "20-34")["gevinst_per_ms"] - 1


gutt = [relv("100m", "M", "12-13"), relv("200m", "M", "10-11")]
jente = [relv("100m", "F", "12-13"), relv("200m", "F", "12-13")]
k.need("discussion", f"worth {pst(min(gutt))}--{pst(max(gutt))}% more, in absolute terms, to a boy "
       f"sprinter than to a senior man --- {f(a('100m', 'M', '12-13')['gevinst_per_ms'], 2)} versus "
       f"{f(a('100m', 'M', '20-34')['gevinst_per_ms'], 2)} s on 100 m at 12--13, "
       f"{f(a('200m', 'M', '10-11')['gevinst_per_ms'], 2)} versus "
       f"{f(a('200m', 'M', '20-34')['gevinst_per_ms'], 2)} s on 200 m at 10--11 --- and "
       f"{pst(min(jente))}--{pst(max(jente))}% more among girls aged 12--13", "ungdom vs senior")
under = max((al[(al["event"] == e) & (al["kjonn"] == kj) & (al["enhet"] == "s")]["gevinst_per_ms"].max()
             - a(e, kj, "20-34")["gevinst_per_ms"])
            / al[(al["event"] == e) & (al["kjonn"] == kj) & (al["enhet"] == "s")]["gevinst_per_ms"].max()
            for e in ["100m", "200m"] for kj in ["M", "F"])
krav(0.37 <= under <= 0.43, f"«up to two-fifths» ({under:.3f})")
k.need("discussion", "understates youth wind effects by up to two-fifths", "undervurdering")
k.need("discussion", f"a broadly similar {f(vin['fordel_i_sd'].min(), 1)}--{f(vin['fordel_i_sd'].max(), 1)} SD",
       "H5 diskusjon")
k.need("discussion", f"({flyt['rader_analyseklar']} analysed results, {flyt['rader_i_celler_min2']} of them "
       f"identifying; {flyt['celler_min2']} athlete-season-event cells)", "styrker")
k.need("discussion", f"missing wind ({pst(mvn['mean'], 1)}% of approved outdoor results", "begrensning")
k.need("conclusion", f"They are {pst(min(gutt + jente))}--{pst(max(gutt + jente))}% larger for child "
       f"sprinters than for seniors", "konklusjon")

# ================================================================ SUPPLEMENT-NOTER
k.need("supplementary material", f"$1.8 \\times {f(v('100m', 'F', '12-13')['medvind_s_per_ms'], 3)} = "
       f"{f(1.8 * v('100m', 'F', '12-13')['medvind_s_per_ms'], 2)}$", "regneeksempel")
k.need("supplementary material", f"Straight flat sprints cluster at {f(min(rett), 4)}--{f(max(rett), 4)}",
       "S4-note")
k.need("supplementary material", f"e.g. {f(kv.loc['lengde', 'beta_lin'], 4)} m = {f(100 * kv.loc['lengde', 'beta_lin'], 2)} cm", "S5-tekst")
krav(rob.loc["150m"][["celler_min3", "periode_2011_2019", "periode_2021_2026"]].isna().all(),
     "S2-note: 150 m mangler celler≥3 og periodekolonner")

# ================================================================ TABELLER mot R (uavhengig)
rh = pd.read_csv(R / "hoved.csv")
for tex in ["t2"]:
    linjer = (PROSJ / "manus" / f"{tex}.tex").read_text().splitlines()
    for e, navn in [("60m", "60 m"), ("100m", "100 m"), ("200m", "200 m"), ("lengde", "Long jump")]:
        rad = [ln for ln in linjer if ln.startswith(navn + " &")][0]
        vist = tall_i(rad.split("&", 1)[1])
        rr = rh[(rh["event"] == e) & (rh["analyse"] == "hoved")].iloc[0]
        dd = 3 if e in SPRINT else 2
        forvent = [f(rr["gevinst"], dd), f(rr["ki_lav"], dd), f(rr["ki_hoy"], dd)]
        if vist[:3] != forvent:
            FEIL.append(f"t2 {navn}: vist {vist[:3]}, R gir {forvent}")
        else:
            k.n_ok += 1
for t in ["t1", "t2", "t3", "t4", "t5", "t6", "s1", "s2", "s3", "s4", "s5"]:
    krav(f"\\input{{{t}}}" in k.raa, f"\\input{{{t}}} i manus (genererte tabeller)")

# ================================================================ ORDTELLING
ord_n = ordtelling(PROSJ / "manus" / "main.tex")
k.need("tittelside", f"Word count: $\\sim${int(round(ord_n, -2))}", f"ordtelling ({ord_n})")

# ================================================================ DEKNING
UNNTAK = [
    r"\\vspace\*?\{[^}]*\}", r"\d*\.?\d+\\textwidth", r"width=\d*\.?\d+\\textwidth",
    r"orcid\.org/[\d-]+\}\{ORCID: [\d-]+\}", r"Box 5003, 1432", r"\$\^\{?1,?\*?\}?\$", r"\$\^1\$",
    r"\\setcounter\{table\}\{0\}", r"\\begin\{titlepage\}", r"\{S\\arabic\{table\}\}",
    r"\b(10|12|14|16|18|20)--(11|13|15|17|19|34)\b",
    r"\b(60|80|100|110|150|200)( m|m)\b", r"\b(68|76\.2|84|91\.4|100|106\.7) cm\b",
    r"\b(19|20)\d\d\b", r"\bH[1-5]\b", r"Table S\d", r"Section \d\.\d",
    r"±2\.0 m/s", r"\+2\.0 m/s", r"\+2\.0\b", r"\b2\.0 m/s", r"±8 m/s", r"±0\.2 of \+2\.0", r"[+-±]?1 m/s",
    r"\+1\.8 m/s", r"exactly 0\.0", r"exactly \+2\.0", r"95% CIs?", r"5th--95th percentile", r"\(1\.8, 2\.0\]",
    r"\(2\.0, 2\.2\]", r"\$\(2v\+1\)/\(2v-1\)\$?", r"\$v\^2\$", r"\(m/s\)\$\^2\$", r"\$2 \\times\$",
    r"age 1[03]", r"under 13", r"12-year-old", r"age-19", r"class-14", r"top-10", r"top-50",
    r"29 October 2026", r"\bS[1-5]\b", r"10 s from", r"13 s in", r"5 s per attempt", r"60 and 80 m",
    r"\\times 10\^\{-2\}", r"\$\\sim\$", r"\bten\b", r"ten-year-olds", r"\(60 to 200 m\)",
    r"0\.0\b(?= m/s| readings|,| more)", r"p < 0\.001", r"cells with at least three", r"at least two",
    r"\bstratum is 20--34\b",
    r"\b(60|80|100|110|150|200)( and |/)(60|80|100|110|150|200) ?m\b", r"\b20(11|21)--20(19|26)\b",
    r"60 m above 17", r"cells-≥3", r"10--12 age classes", r"In cells ≥2",
]
k.need("results", f"Dashes: fewer than {m03.MIN_N} results in {m03.MIN_CELLER} athlete-seasons", "tabellnote 3")
k.need("results", f"Codes with fewer than {m03.MIN_N} results for one sex", "tabellnote 5")
kode_m = k.rapport(UNNTAK)

# ================================================================ SVARBREVET
b = Kontroll.__new__(Kontroll)
b.navn, b.feil, b.dekket, b.n_ok = "A6 svarbrev", [], [], 0
b.raa = (PROSJ / "manus" / "RESPONSE_PANEL1.md").read_text()
b.tekst = re.sub(r"(?<=\d),(?=\d{3}\b)", "", b.raa)  # tusenskiller i brevet
b.seksjoner = {"brev": (0, len(b.tekst))}
for s, hvorfor in [
    (per_sek.replace(" s per m/s in the straight sprints against", " s per m/s per second of race time, the bend events at")
     .replace(" in the bend events", ""), "R1-2"),
    (f"(1.51 / 1.66 / 2.37 on 60/100/200 m)".replace("1.51", f(asy.loc['60m', 'ratio_obs'], 2))
     .replace("1.66", f(asy.loc['100m', 'ratio_obs'], 2)).replace("2.37", f(asy.loc['200m', 'ratio_obs'], 2)), "R1-3"),
    (f"({f(teor.min(), 2)}--{f(teor.max(), 2)})", "R1-3 benchmark"),
    (f"({pst(ins[SPRINT].min())}--{pst(ins[SPRINT].max())} % sprints, {pst(ins[HOPP].min())}--{pst(ins[HOPP].max())} % jumps)", "R1-4"),
    (f"an SD of {f(sig.min(), 2)}--{f(sig.max(), 2)} m/s from 60 to 200 m", "R1-4 σ"),
    (f"(girls' long jump {f(lf12, 1)} → {f(lf20, 1)} cm per m/s)", "R1 minor 3"),
    (f"run {f(hp.min(), 4)}--{f(hp.max(), 4)} s per m/s (Table S4)", "R1 minor 4"),
    (f"(0.055--0.067 against 0.056--0.070; {pst(-h60['ratio'].min())} % below to {pst(h60['ratio'].max())} % above".replace(
        "0.055", f(h60['gevinst_s_per_ms'].min(), 3)).replace("0.067", f(h60['gevinst_s_per_ms'].max(), 3))
     .replace("0.056", f(h60['flat_ref'].min(), 3)).replace("0.070", f(h60['flat_ref'].max(), 3)), "R2-2 60 m"),
    (f"({pst(-h100['ratio'].min())} % below to {pst(h100['ratio'].max())} % above)", "R2-2 100/110"),
    ("boys' 100 m hurdles at 84 cm, 709 results", "R2-2 utelatt rad") if b84["n"] == 709 else ("FEIL N", "R2-2 n"),
    ("all thirteen sex-specific rows", "R2-2 tretten") if (hk["kjonn"] != "begge").sum() == 13 else ("FEIL 13", ""),
    (f"meet-clustered intervals are {f(bredde[['60m', '100m', '200m']].min(), 1)}--{f(bredde[['60m', '100m', '200m']].max(), 1)} times wider", "R2-3"),
    (f"{f(sig['60m'], 2)} m/s (60 m), {f(sig['100m'], 2)} m/s (100 m) and {f(sig['200m'], 2)} m/s (200 m)", "R2-4 σ"),
    (f"from {f(eiv.loc['60m', 'reliabilitet_primaer'], 2)}/{f(eiv.loc['100m', 'reliabilitet_primaer'], 2)}/"
     f"{f(eiv.loc['200m', 'reliabilitet_primaer'], 2)} to {f(eiv.loc['60m', 'reliabilitet_stevnefe'], 2)}/"
     f"{f(eiv.loc['100m', 'reliabilitet_stevnefe'], 2)}/{f(eiv.loc['200m', 'reliabilitet_stevnefe'], 2)}", "R2-4 λ"),
    (f"this reproduces {f(rob.loc['100m', 'primaer'], 3)} → {f(rob.loc['100m', 'stevne_fe'], 3)}", "R2-4 100 m"),
    (f"as {pst(-fe[['60m', '100m', '200m']].max())}--{pst(-fe[['60m', '100m', '200m']].min())} % for 60/100/200 m", "R2-4 FE"),
    (f"by {pst(fe[HOPP].min())}--{pst(fe[HOPP].max())} %", "R2-4 hopp"),
    (f"worth {f(vin['fordel_i_sd'].min(), 1)}--{f(vin['fordel_i_sd'].max(), 1)} SD across events", "R2-5"),
    (f"100 m {f(tt('100m', 'lav')['gevinst_per_ms'], 3)} / {f(tt('100m', 'midt')['gevinst_per_ms'], 3)} / "
     f"{f(tt('100m', 'hoy')['gevinst_per_ms'], 3)} (low/mid/high), 60 m {f(tt('60m', 'lav')['gevinst_per_ms'], 3)} / "
     f"{f(tt('60m', 'midt')['gevinst_per_ms'], 3)} / {f(tt('60m', 'hoy')['gevinst_per_ms'], 3)}, 200 m "
     f"{f(tt('200m', 'lav')['gevinst_per_ms'], 3)} / {f(tt('200m', 'midt')['gevinst_per_ms'], 3)} / "
     f"{f(tt('200m', 'hoy')['gevinst_per_ms'], 3)}", "R2-6"),
    (f"the {pst(bun['eksakt 0.0'], 1)} % exact zeros", "R2-7a"),
    (f"({pst(bun['(1.8,2.0]'], 1)} % in (1.8, 2.0] vs {pst(bun['(2.0,2.2]'], 1)} % in (2.0, 2.2]; "
     f"{pst(bun['eksakt 2.0'], 1)} % exactly +2.0)", "R2-7b"),
    (f"{pst(mvn['mean'], 1)} % of approved outdoor results lack a reading ({flyt['uten_vindverdi']} rows", "R2-7c"),
    (f"{pst(mvs['minste tredel'], 1)} % in the smallest third of meets vs {pst(mvs['storste tredel'], 1)} % in "
     f"the largest, and between {pst(mva['mangler'].min())} and {pst(mva['mangler'].max())} % by year", "R2-7c"),
    (f"({flyt['rader_i_celler_min2']} in cells ≥ 2)", "R2-7e"),
    (f"Python {sys.version.split()[0]}, pandas {pd.__version__}, numpy {np.__version__}, statsmodels "
     f"{statsmodels.__version__}", "versjoner"),
    (f"indoor 60 m ({inn['60m']} rows), then long jump ({inn['lengde']}) and 200 m ({inn['200m']})", "R2 minor 7"),
    (f"1.8 × {f(v('100m', 'F', '12-13')['medvind_s_per_ms'], 3)} = {f(1.8 * v('100m', 'F', '12-13')['medvind_s_per_ms'], 2)} s", "R3-1"),
    (f"changes the athlete occupying {min(o14)}--{max(o14)} of the top-10 places in the class-14 lists "
     f"(boys and girls) and {om.loc[('M', 'senior'), 'plassendringer_topp10']} of 10 in the senior men's list, "
     f"where {pst(om.loc[('M', 'senior'), 'andel_topp50_vind_over_1'])} % of top-50 marks", "R3-2"),
    (f"converts to {int(min(t13))}--{int(max(t13))} points at age 13 and {int(min(t19))}--{int(max(t19))} points "
     f"on the oldest (age-19) table", "R3-4"),
    ("Results 3.6", "seksjonsnummer H5"),
]:
    b.need("brev", s, hvorfor)
krav(("F", "senior") not in om.index, "R3-2: seniorkvinner under terskel")
krav("Results 3.7" not in b.raa, "brev: ingen henvisning til feil seksjon 3.7")
for lab in ["Sample and wind exposure", "What a metre per second is worth", "The effect falls with age",
            "Headwinds cost more", "Short hurdles", "What the legal window is worth", "Robustness"]:
    pass
seks = re.findall(r"\\subsection\{([^}]*)\}", k.raa.split("\\section{Results}")[1].split("\\section{Discussion}")[0])
krav(seks[5].startswith("What the legal window"), f"Results 3.6 er H5 ({seks[5]})")
UNNTAK_B = [
    r"\b(19|20)\d\d\b", r"R[1-3]-\d", r"\b(60|80|100|110|150|200)( m\b| m/s|/)", r"\d\d_\w+\.py",
    r"Tables? [1-6]", r"\bS[1-5]\b", r"S1--S5", r"\bH[1-5]\b", r"\b(10|12|14|16|18|20)--(11|13|15|17|19|34)\b",
    r"\(\d\)", r"\(i+\)", r"60/80 m", r"60/100/200 m", r"(76\.2|84|91\.4) cm", r"\+2\.0", r"±0\.2", r"[+-]?1 m/s",
    r"10 s from the gun", r"13 s in the short hurdles", r"10 s from entering", r"5 s per attempt",
    r"Moulton 1986", r"Vaeyens et al\. \(2008\)", r"age-19", r"class-14", r"top-10", r"top-50", r"top-10",
    r"under-13", r"60-athlete threshold", r"c₄", r"n = 2", r"≥ 3 results", r"≥ 2\)", r"\$v\^2\$",
    r"Results 3\.6", r"Figures? [2-5]", r"Figures 3 and 4", r"Figures 3--4", r"Tables 2--6", r"Tables 3, 4 and 6",
    r"0\.144 vs 0\.143", r"0\.144", r"0\.143 replaces", r"10--30 %", r"15--40 %", r"0\.04--0\.06", r"two",
    r"\bS2\b", r"1\.8 × ", r"\(4\)", r"p < 0\.001", r"thirteen", r"20--34 senior ceiling", r"Python 3\.13\.7",
]
UNNTAK_B += [r"round[- ]1", r"Reviewer [1-3]", r"95 % CIs?", r"`0[89]`", r"\+1\.8 m/s",
             r"0\.9--1\.1 SD at 12--13 vs 0\.5--0\.8 senior", r"\(round 1 said 15--40 %\)"]
b.need("brev", f"The within-meet share of wind variance is {pst(ins[SPRINT].min())}--{pst(ins[SPRINT].max())} % "
       f"in the sprints and {pst(ins[HOPP].min())}--{pst(ins[HOPP].max())} % in the jumps", "R2-4 andel")
kode_b = b.rapport(UNNTAK_B)
TILLATT = {
    "exactly as drag physics predicts": "runde 1-frase, sitert som fjernet",
    "Exactly as drag physics predicts": "runde 1-frase, sitert som fjernet",
    "behave like flat sprints": "runde 1-frase, sitert som erstattet",
    "0.9--1.1 SD at 12--13 vs 0.5--0.8 senior": "runde 1-tall, sitert som forkastet",
    "no rule changes": "refereens frase (overskrift)",
    "mild": "runde 1-ord, sitert som fjernet",
    "deposited": "runde 1-ord, sitert som erstattet",
    "available from the author": "frase, sjekket separat",
}
kode_s = sitatkontroll(PROSJ / "manus" / "RESPONSE_PANEL1.md", k, TILLATT)

feil_totalt = len(k.feil) + len(b.feil)
print(f"\nA6 TOTALT: {k.n_ok + b.n_ok} sjekker OK, {feil_totalt} feil")
sys.exit(1 if (kode_m or kode_b or kode_s) else 0)
