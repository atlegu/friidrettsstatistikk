"""
kontroll_tall.py — A6-audit fase 4: hvert tall i manus mot estimeringsfilene.

Kjøres etter 07–10 (og R-kontrollen audit/sammenlign.py). Hver sjekk er en ankret frase
bygget fra filene; dekningskontrollen lister tall som ingen sjekk dekker. Tabellene
genereres av 09 og kontrolleres her mot R-implementasjonens fullpresisjonsverdier.
Svarbrevet til den simulerte refereerunden vedlikeholdes ikke etter auditen 30.10.2026
(Atles beslutning) og kontrolleres ikke. Avslutter med kode 1 ved avvik.
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
from audit_felles import Kontroll, avrund as f, normaliser, ordtelling, tall_i  # noqa: E402
from rens_felles import fjern_kopier  # noqa: E402

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
fe_a = les("r2_stevne_fe_alder.csv")
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
# Sammendraget skrevet om 30.10.2026 etter Atles beslutning om H5 (endringsrapporten avsnitt 8,
# punkt 2–3) og JSS-kravene. Nyhets- og drag-påstanden ankres i Lybbert & Zheng-blokken nederst,
# påstandene om gutter og jenter i H5-blokken.
sammendrag = k.raa.split("\\section*{Abstract}", 1)[1].split("\\textbf{Keywords:}", 1)
abs_ord = len([x for x in re.sub(r"\\[a-zA-Z]+\s*", " ", normaliser(sammendrag[0])).split()
               if re.search(r"[A-Za-z0-9]", x)])
krav(abs_ord <= 200, f"sammendraget har høyst 200 ord (JSS): {abs_ord}")
nokkelord = sammendrag[1].split("\n", 1)[0].split(";")
krav(len(nokkelord) <= 6, f"høyst 6 nøkkelord (JSS): {len(nokkelord)}")
k.need("abstract", f"at ages 10--34 ({flyt['rader_analyseklar']} results)", "utvalg")
k.need("abstract", f"results changed by {f(h('60m')['gevinst_per_ms'], 3)} s on 60 m, "
       f"{f(h('100m')['gevinst_per_ms'], 3)} s on 100 m, {f(h('200m')['gevinst_per_ms'], 3)} s on "
       f"200 m, {f(h('lengde')['gevinst_per_ms'], 1)} cm in the long jump and "
       f"{f(h('tresteg')['gevinst_per_ms'], 1)} cm in the triple jump", "hovedeffekter")
elite = [asy.loc["100m", "medvind"] / 0.06, asy.loc["100m", "medvind"] / 0.04]
k.need("abstract", f"(200 m, males: {f(a('200m', 'M', '10-11')['gevinst_per_ms'], 3)} s per m/s "
       f"at 10--11 to {f(a('200m', 'M', '20-34')['gevinst_per_ms'], 3)} at 20--34)", "200 m alder")
rett = [ps.loc[e, "per_sekund"] for e in ["60m", "80m", "100m"]]
sving = [ps.loc[e, "per_sekund"] for e in ["150m", "200m"]]
k.need("abstract", f"(100 m: {f(asy.loc['100m', 'motvind'], 3)} vs. "
       f"{f(asy.loc['100m', 'medvind'], 3)} s per m/s)", "asymmetri 100 m")
krav(asy.loc["100m", "p_lik_meet"] < 0.001, "100 m p < 0.001")
rel = {e: asy.loc[e, "ratio_obs"] / asy.loc[e, "ratio_drag_estimator"] for e in ["60m", "100m", "200m"]}
krav(abs(rel["100m"] - 1) < 0.05 and rel["60m"] < 0.9 and rel["200m"] > 1.15,
     f"100 m ≈ drag, 60 m under, 200 m over ({ {e: round(x, 3) for e, x in rel.items()} })")
h100 =hk[(hk["kjonn"] != "begge") & hk["kode"].str.startswith(("100mh", "110mh"))
          & hk["flat_ref"].notna()].copy()
h100["ratio"] = h100["gevinst_s_per_ms"] / h100["flat_ref"] - 1
h60 = hk[(hk["kjonn"] != "begge") & hk["kode"].str.startswith("60mh")].copy()
h60["ratio"] = h60["gevinst_s_per_ms"] / h60["flat_ref"] - 1
krav((h100["ratio"] > 0).sum() > len(h100) / 2, "100/110 m hekk «mostly exceeded»")
FRA12 = ["12-13", "14-15", "16-17", "18-19", "20-34"]
vf = vin[vin["event"].isin(["100m", "200m"]) & vin["aldersband"].isin(FRA12)]
spenn12 = f"{f(vf['fordel_0_2_s'].min(), 2)}--{f(vf['fordel_0_2_s'].max(), 2)} s on the 100 and 200 m"
vindu12 = f"{spenn12} from age 12"
k.need("abstract", f"A legal +2.0 m/s tailwind was worth {vindu12}, roughly equal across ages for boys, larger for "
       "girls than for senior women, and enough to reorder 2025 season lists at youth and senior ages",
       "H5 sammendrag (gutter/jenter og listene: krav i H5-blokken)")
r12 = [v("100m", kj, "12-13")["fordel_0_2_i_robust_skala"] for kj in ["M", "F"]]
r20 = [v("100m", kj, "20-34")["fordel_0_2_i_robust_skala"] for kj in ["M", "F"]]
krav(max(r12) < min(r20), "robust andel: seniorer over 12–13 på 100 m («most … among seniors»)")

# ================================================================ INTRODUCTION
k.need("introduction", "roughly 0.04--0.06 s per m/s in the 100 m", "litteraturverdi (elite)")
r12t = snitt("100m", "M", "12-13") / snitt("100m", "M", "20-34")
krav(1.28 <= r12t <= 1.38, f"«roughly a third more time» (forhold {r12t:.3f})")
k.need("introduction", "a 12-year-old needs roughly a third more time over 100 m", "tidsforhold")

# ================================================================ METHODS
k.need("methods", f"we removed duplicate records: {flyt['ekskl_sonetvilling_brettkode']} board-jump rows",
       "sonetvillinger")
k.need("methods", f"{flyt['ekskl_flerdagskopi_brettkode']} such copies from multi-day meets, dated to the meet's first day",
       "flerdagskopier (rens_felles)")
k.need("methods", f"the {flyt['ekskl_2026_brettkode_11_13']} board-event jumps at ages 11--13 in 2026 were also excluded",
       "2026: sonehopp under brettkoden")
k.need("methods", f"and {flyt['ekskl_eksakt_dublett']} exact duplicates", "eksakte dubletter")
k.need("methods", f"Of {flyt['rader_uttrekk']} extracted rows in the main events, "
       f"{flyt['rader_analyseklar']} entered the analysis", "flyt")
k.need("methods", f"the indoor 60 m ({inn['60m']} rows), 200 m ({inn['200m']}) and long jump "
       f"({inn['lengde']})", "innendørs")
krav(list(inn.sort_values(ascending=False).index[:3]) == ["60m", "200m", "lengde"],
     "innendørs: 60 m, 200 m, lengde er de tre største")
k.need("methods", f"{flyt['uten_vindverdi']} outdoor rows without a wind value (overall, "
       f"{pst(mvn['mean'], 1)}% of approved outdoor results lack a reading)", "manglende vind")
k.need("methods", f"({pst(mvs['minste tredel'], 1)}% of rows in the smallest third of meets by "
       f"size, against {pst(mvs['storste tredel'], 1)}% in the largest third)", "stevnestørrelse")
k.need("methods", f"fluctuates between {pst(mva['mangler'].min())} and "
       f"{pst(mva['mangler'].max())}%", "per år")
k.need("methods", f"Of the analysed rows, {flyt['rader_i_celler_min2']} lie in", "celler")
hr = pd.read_csv(DATA / "resultater_hekk.csv", low_memory=False, parse_dates=["date"])
hr, _ = fjern_kopier(hr)
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
rb = les("robusthet.csv").set_index(["analyse", "event"])
bredde = {e: (rb.loc[("primaer", e), "ki_hoy"] - rb.loc[("primaer", e), "ki_lav"])
          / (rb.loc[("kluster_stevne", e), "ki_hoy"] - rb.loc[("kluster_stevne", e), "ki_lav"])
          for e in SPRINT + HOPP}
krav(all(0.4 <= bredde[e] <= 0.6 for e in ["60m", "100m", "200m"])
     and all(0.7 <= bredde[e] < 0.95 for e in ["80m", "150m"] + HOPP),
     f"KI-bredde utøver/stevne: { {e: round(x, 2) for e, x in bredde.items()} }")
k.need("methods", "intervals roughly half as wide in the large sprints and somewhat narrower ones elsewhere",
       "klyngebredde")
# «Sample size estimation and justification» (JSS-krav, lagt til 30.10.2026)
krav(all(bredde[e] < 1 for e in SPRINT + HOPP), "stevneklynger gir bredere KI enn utøverklynger i alle øvelser")
k.need("methods", f"estimates are reported only where at least {m03.MIN_N} results in {m03.MIN_CELLER} "
       "athlete-seasons contribute, and standard errors are clustered on meet, which gives wider intervals than the "
       "athlete clustering of the analysis plan", "utvalgsstørrelse: regler")
hmeet = hov[hov["analyse"] == "hoved_meet"].set_index("event")
halvb = (hmeet["ki_hoy"] - hmeet["ki_lav"]) / 2
store = ["60m", "100m", "200m"]
k.need("methods", f"95% confidence intervals have half-widths of {f(halvb[store].min(), 3)}--"
       f"{f(halvb[store].max(), 3)} s per m/s in the 60, 100 and 200 m ({f(halvb['80m'], 3)} and "
       f"{f(halvb['150m'], 3)} in the small 80 and 150 m events) and {f(halvb[HOPP].min(), 1)}--"
       f"{f(halvb[HOPP].max(), 1)} cm in the four jump events", "utvalgsstørrelse: presisjon")
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
k.need("results", f"Per m/s of wind, results changed by {f(h('60m')['gevinst_per_ms'], 3)} s (95% CI "
       f"{f(h('60m')['ki_lav'], 3)}--{f(h('60m')['ki_hoy'], 3)}) on 60 m, {ki_s(h('100m'))} on "
       f"100 m, {ki_s(h('200m'))} on 200 m, {ki_s(h('lengde'), 1, ' cm')} in the long jump and "
       f"{ki_s(h('tresteg'), 1, ' cm')} in the triple jump; in percentage terms, "
       f"{f(min(pr), 2)}--{f(max(pr), 2)}% per m/s", "H1 tekst")
k.need("results", "The published elite figures of roughly 0.04--0.06 s per m/s on the 100 m", "litteraturverdi")
k.need("results", f"the population slopes were {f(asy.loc['60m', 'medvind'], 3)} s (60 m), "
       f"{f(asy.loc['100m', 'medvind'], 3)} s (100 m) and {f(asy.loc['200m', 'medvind'], 3)} s (200 m) per m/s",
       "medvindsgren tekst")
k.need("results", f"so the 100 m figure is about {f(elite[0], 1)}--{f(elite[1], 1)} times the elite range",
       "elite-forhold tekst")
k.need("results", f"the 100 m tailwind slope was {f(v('100m', 'M', '20-34')['medvind_s_per_ms'], 3)} s for men "
       f"and {f(v('100m', 'F', '20-34')['medvind_s_per_ms'], 3)} s for women", "senior medvind")
krav(v("100m", "M", "20-34")["medvind_s_per_ms"] <= 0.066 and v("100m", "F", "20-34")["medvind_s_per_ms"] <= 0.066,
     "«at or just above the elite range»")
k.need("results", f"averaging about {f(snitt('100m', 'M', '20-34'), 1)} s on the 100 m", "senior tid")
brudd = []
for e in ["60m", "100m", "200m"]:
    for kj in ["M", "F"]:
        s = al[(al["event"] == e) & (al["kjonn"] == kj) & (al["enhet"] == "s")].sort_values("aldersband")
        g = s["gevinst_per_ms"].to_numpy()
        brudd += [f"{e} {kj} {s['aldersband'].iloc[i]}" for i in range(len(g) - 1) if g[i + 1] > g[i]]
krav(brudd == ["200m F 10-11"], f"monotoni-unntak: {brudd}")
k.need("results", "monotonically in every series except the sparse girls' 200 m at 10--11", "monotoni")
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
# brettøvelsene har ikke estimat under 14-15 år etter at sonekopiene og 2026-sonehoppene under
# brettkoden er tatt ut (audit 30.10.2026): de yngste hopper fra sone
krav(al[(al["event"].isin(["lengde", "tresteg"])) & (al["aldersband"].isin(["10-11", "12-13"]))].empty,
     "ingen brettestimat under 14-15 år")
lf14, lf20 = a("lengde", "F", "14-15", "cm")["gevinst_per_ms"], a("lengde", "F", "20-34", "cm")["gevinst_per_ms"]
lm14, lm20 = a("lengde", "M", "14-15", "cm")["gevinst_per_ms"], a("lengde", "M", "20-34", "cm")["gevinst_per_ms"]
k.need("results", f"(long jump: {f(lf14, 1)} cm per m/s at 14--15 to {f(lf20, 1)} at 20--34)", "lengde jenter")
k.need("results", f"but not for boys and men ({f(lm14, 1)} at 14--15, {f(lm20, 1)} at 20--34)", "lengde gutter")
krav(lf20 > lf14 and lm20 <= lm14, "lengde: stiger for jenter, ikke for gutter")
k.need("results", "below 14 nearly all horizontal jumps are made from a take-off zone", "brett fra 14-15")
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
k.need("results", f"$(2v+1)/(2v-1) \\approx$ {f(teor.min(), 2)}--{f(teor.max(), 2)} describes a wind of exactly",
       "±1-forholdet")
k.need("results", f"predicts head/tail ratios of {f(asy.loc['60m', 'ratio_drag_estimator'], 2)} (60 m), "
       f"{f(asy.loc['100m', 'ratio_drag_estimator'], 2)} (100 m) and {f(asy.loc['200m', 'ratio_drag_estimator'], 2)} "
       f"(200 m), against observed {f(asy.loc['60m', 'ratio_obs'], 2)}, {f(asy.loc['100m', 'ratio_obs'], 2)} and "
       f"{f(asy.loc['200m', 'ratio_obs'], 2)}, and quadratic terms of {f(asy.loc['60m', 'drag_kvad'], 4)}, "
       f"{f(asy.loc['100m', 'drag_kvad'], 4)} and {f(asy.loc['200m', 'drag_kvad'], 4)} against observed "
       f"{f(kv.loc['60m', 'beta_kvad'], 4)}, {f(kv.loc['100m', 'beta_kvad'], 4)} and {f(kv.loc['200m', 'beta_kvad'], 4)}",
       "drag-referanse")
k.need("results", f"({f(asy.loc['lengde', 'medvind'], 2)} against {f(asy.loc['lengde', 'motvind'], 2)} cm, "
       f"p = {f(asy.loc['lengde', 'p_lik_meet'], 2)})", "lengde asymmetri")
krav(asy.loc["lengde", "p_lik_meet"] > 0.05, "lengde: ikke signifikant asymmetri")
krav(all(asy.loc[e, "medvind"] > asy.loc[e, "motvind"] for e in ["lengde_sone_05m", "tresteg_sone_05m"]),
     "sonevariantene: medvindsgrenen brattest")
k.need("results", f"The simpler ratio $(2v+1)/(2v-1)$ for a wind of exactly ±1 m/s is {f(teor.min(), 2)}--"
       f"{f(teor.max(), 2)}", "tabell 4-note")
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
krav(list(zip(ikke_ov["kode"], ikke_ov["kjonn"])) == [("100mh_76_2cm", "F")],
     f"bare jentenes 76,2 cm uten overlapp: {list(zip(ikke_ov['kode'], ikke_ov['kjonn']))}")
g76 = hk[(hk["kode"] == "100mh_76_2cm") & (hk["kjonn"] == "F")].iloc[0]
b84 = hk[(hk["kode"] == "100mh_84cm") & (hk["kjonn"] == "M")].iloc[0]
w84 = hk[(hk["kode"] == "100mh_84cm") & (hk["kjonn"] == "F")].iloc[0]
krav(b84["ki_lav"] > b84["flat_ref"], "gutter 84 cm: KI over flat punktestimat")
k.need("results", f"in the girls' 76.2 cm class ({f(g76['gevinst_s_per_ms'], 3)} against {f(g76['flat_ref'], 3)}) "
       f"the hurdle interval lies entirely above the flat interval, and in the boys' 84 cm class "
       f"({f(b84['gevinst_s_per_ms'], 3)} against {f(b84['flat_ref'], 3)})", "hekk to klasser")
hp = hk[hk["kjonn"] == "begge"]["per_sekund"]
k.need("results", f"the pooled hurdle codes ({f(hp.min(), 4)}--{f(hp.max(), 4)} s per m/s)", "hekk/s")
krav(hp.min() <= min(rett) and hp.max() >= max(rett), "hekk spenner rettløpsratene")
k.need("results", f"{f(g76['gevinst_s_per_ms'], 3)} s per m/s for girls' 76.2 cm at "
       f"{g76['modal_aldersband'].replace('-', '--')} and {f(b84['gevinst_s_per_ms'], 3)} for boys' 84 cm "
       f"at {b84['modal_aldersband'].replace('-', '--')}, against {f(w84['gevinst_s_per_ms'], 3)} for the "
       f"senior women's 84 cm", "aldersgradient hekk")
# H5 etter Atles beslutning 30.10.2026 (endringsrapporten avsnitt 8, punkt 2): i sekunder er vinduet
# ikke størst for de yngste guttene; bare jentene har et fall, og intervallene overlapper.
k.need("results", f"From age 12 the window was worth {spenn12}", "H5 spenn fra 12 år")
gutt_v = {e: vf[(vf["event"] == e) & (vf["kjonn"] == "M")].set_index("aldersband").sort_index()
          for e in ["100m", "200m"]}
for e, g in gutt_v.items():
    krav(g["fordel_0_2_ki_lav"].max() <= g["fordel_0_2_ki_hoy"].min(),
         f"gutter {e}: alle bånd fra 12–13 har et felles KI-overlapp")
    krav(not g["fordel_0_2_s"].is_monotonic_decreasing, f"gutter {e}: ingen fallende aldersrekke")
    krav(g.loc["12-13", "fordel_0_2_s"] / g.loc["20-34", "fordel_0_2_s"] < 1.2,
         f"gutter {e}: 12–13 under 1,2 × seniorene («about as much»)")
k.need("results", f"For boys and men it showed no clear age trend in seconds: "
       f"{f(gutt_v['100m']['fordel_0_2_s'].min(), 2)}--{f(gutt_v['100m']['fordel_0_2_s'].max(), 2)} s on the 100 m "
       f"and {f(gutt_v['200m']['fordel_0_2_s'].min(), 2)}--{f(gutt_v['200m']['fordel_0_2_s'].max(), 2)} s on the "
       "200 m in the bands from 12--13 to 20--34, with overlapping intervals", "H5 gutter (krav over)")
g100 = (v("100m", "M", "12-13"), v("100m", "M", "20-34"))
fall = {s: g100[0][s] - g100[1][s] for s in ["motvind_s_per_ms", "medvind_s_per_ms", "medvind_0_2_s_per_ms"]}
krav(fall["motvind_s_per_ms"] > 3 * max(fall["medvind_s_per_ms"], fall["medvind_0_2_s_per_ms"]),
     f"gutter 100 m: aldersfallet ligger i motvindshelningen ({ {s: round(x, 4) for s, x in fall.items()} })")
k.need("results", "On the boys' 100 m the age decline of the linear slope (Section 3.3) lies mainly in the headwind "
       "slope (Table S3)", "H5 motvind (krav over)")
jente_v = {e: vf[(vf["event"] == e) & (vf["kjonn"] == "F")].set_index("aldersband").sort_index()
           for e in ["100m", "200m"]}
for e, g in jente_v.items():
    sen, ung = g.loc["20-34"], g.drop("20-34")
    krav((ung["fordel_0_2_s"] > sen["fordel_0_2_s"]).all(), f"jenter {e}: hvert bånd 12–19 over seniorkvinnene")
    krav((ung["fordel_0_2_ki_lav"] <= sen["fordel_0_2_ki_hoy"]).all(), f"jenter {e}: KI overlapper seniorkvinnenes")
k.need("results", f"For girls and women the window was larger before senior age, also with overlapping intervals: "
       f"{f(jente_v['100m'].loc['12-13', 'fordel_0_2_s'], 2)} s on the 100 m at 12--13 against "
       f"{f(jente_v['100m'].loc['20-34', 'fordel_0_2_s'], 2)} s at 20--34, and "
       f"{f(jente_v['200m'].loc['12-13', 'fordel_0_2_s'], 2)} against "
       f"{f(jente_v['200m'].loc['20-34', 'fordel_0_2_s'], 2)} s on the 200 m", "H5 jenter (krav over)")
tyi = tyr.set_index(["kjonn", "aldersband"])
for kj in ["M", "F"]:
    for b in ["12-13", "20-34"]:
        krav(abs(tyi.loc[(kj, b), "fordel_0_2_s"] - v("100m", kj, b)["fordel_0_2_s"]) < 1e-12
             and abs(tyi.loc[(kj, b), "snitt_tid_s"] - snitt("100m", kj, b)) < 1e-6,
             f"poengfila bruker samme vindu og snittid som analysen ({kj} {b})")
andel = {(kj, b): tyi.loc[(kj, b), "fordel_0_2_s"] / tyi.loc[(kj, b), "snitt_tid_s"]
         for kj in ["M", "F"] for b in ["12-13", "20-34"]}
krav(andel[("M", "12-13")] < andel[("M", "20-34")], "andel av løpstid: gutter 12–13 under seniormenn")
krav(0 < andel[("F", "12-13")] - andel[("F", "20-34")] < 0.002, "andel av løpstid: jenter bare litt over seniorkvinnene")
k.need("results", f"As a share of race time it was smaller for boys aged 12--13 than for senior men on the 100 m "
       f"({pst(andel[('M', '12-13')], 2)} against {pst(andel[('M', '20-34')], 2)}% of the mean time) and only "
       f"slightly larger for girls than for senior women ({pst(andel[('F', '12-13')], 2)} against "
       f"{pst(andel[('F', '20-34')], 2)}%)", "H5 andel av løpstid (krav over)")
ra = vin["fordel_0_2_i_robust_skala"]
k.need("results", f"the window is worth {f(ra.min(), 2)}--{f(ra.max(), 2)} of the robust scale across events, "
       "sexes and ages", "H5 robust spenn")
krav(ra.idxmax() == vin[(vin["event"] == "100m") & (vin["kjonn"] == "M") & (vin["aldersband"] == "20-34")].index[0],
     "størst for senior sprintere (menn 100 m 20–34)")
k.need("results", f"(men's 100 m: {f(v('100m', 'M', '12-13')['fordel_0_2_i_robust_skala'], 2)} at 12--13 against "
       f"{f(v('100m', 'M', '20-34')['fordel_0_2_i_robust_skala'], 2)} at 20--34)", "H5 menn 100 m")
ty = tyr.set_index(["kjonn", "aldersband"])["tyrvingpoeng_for_2ms"]
t13 = [ty[(kj, "12-13")] for kj in ["M", "F"]]
t19 = [ty[(kj, "20-34")] for kj in ["M", "F"]]
krav(set(tyr["tabellalder"]) == {13, 19}, "tabellalder 13 og 19")
k.need("results", f"converts to {int(min(t13))}--{int(max(t13))} points at age 13 against "
       f"{int(min(t19))}--{int(max(t19))} points on the oldest (age-19) table", "Tyrving")
# endringsrapporten avsnitt 8, punkt 3: poengene speiler sekundene (ikke «similar points»)
prop = {kj: (ty[(kj, "12-13")] / ty[(kj, "20-34")],
             tyi.loc[(kj, "12-13"), "fordel_0_2_s"] / tyi.loc[(kj, "20-34"), "fordel_0_2_s"]) for kj in ["M", "F"]}
krav(all(abs(p - s) < 0.1 for p, s in prop.values()),
     f"poengforholdet ≈ sekundforholdet: { {kj: (round(p, 3), round(s, 3)) for kj, (p, s) in prop.items()} }")
k.need("results", "on the oldest (age-19) table, a youth margin of about the same proportion as in seconds",
       "Tyrving-proporsjon (krav over)")
om = oms.set_index(["kjonn", "liste"])
krav(om.loc[("F", "klasse 14"), "nye_i_topp10"] == 1 and om.loc[("M", "senior"), "nye_i_topp10"] == 1
     and om.loc[("F", "senior"), "nye_i_topp10"] == 2 and om.loc[("M", "klasse 14"), "nye_i_topp10"] == 0,
     "nye i topp 10: 1 (jenter 14), 1 (senior menn), 2 (senior kvinner), 0 (gutter 14)")
k.need("results", "(legal marks only, wind ≤ +2.0 m/s; senior lists open to all ages)", "lovlige lister, åpen klasse")
krav(flyt["ekskl_vind_over_8"] >= 0, "vindgrense ±8 i flyten")
k.need("methods", "the linear model uses readings within ±8 rather than ±5 m/s", "planavvik vindspenn (ANALYSEPLAN §4)")
k.need("results", "brings one new athlete into the top 10 of the girls' class-14 list and of the senior men's list and two "
       "into the senior women's list (none in the boys' class-14 list)", "listeomstokk (krav over)")
k.need("results", f"in the senior lists {pst(om.loc[('M', 'senior'), 'andel_topp50_vind_over_1'])}% (men) and "
       f"{pst(om.loc[('F', 'senior'), 'andel_topp50_vind_over_1'])}% (women) of top-50 marks", "andel med medvind")
fe = rob["stevne_fe"] / rob["primaer"] - 1
k.need("results", f"attenuated the 60, 100 and 200 m estimates by "
       f"{pst(-fe[['60m', '100m', '200m']].max())}--{pst(-fe[['60m', '100m', '200m']].min())}% "
       f"(100 m: {f(rob.loc['100m', 'primaer'], 3)} to {f(rob.loc['100m', 'stevne_fe'], 3)} s per m/s)",
       "stevne-FE sprint")
krav(fe[["80m", "150m"]].abs().max() < 0.05, f"80/150 m «essentially unchanged» ({fe[['80m', '150m']].round(3).to_dict()})")
k.need("results", f"raised the jump estimates by {pst(fe[HOPP].min())}--{pst(fe[HOPP].max())}%", "stevne-FE hopp")
k.need("results", f"Only {pst(ins[SPRINT].min())}--{pst(ins[SPRINT].max())}% of the sprint wind variance lies "
       f"within meets ({pst(ins[HOPP].min())}--{pst(ins[HOPP].max())}% in the jumps", "innen stevne")
fa = fe_a.set_index(["event", "kjonn", "aldersband"])
ok_fe = []
for (e, kj), g in fe_a.groupby(["event", "kjonn"]):
    g = g[g["stevne_fe_se"] < 0.02].sort_values("aldersband")
    ok_fe.append(g["stevne_fe_s"].iloc[0] > g["stevne_fe_s"].iloc[-1])
krav(all(ok_fe), "stevne-FE: yngste godt målte bånd over 20–34 (eller eldste) i hver serie")
k.need("results", f"(men's 100 m: {f(fa.loc[('100m', 'M', '12-13'), 'stevne_fe_s'], 3)} s per m/s at 12--13 to "
       f"{f(fa.loc[('100m', 'M', '20-34'), 'stevne_fe_s'], 3)} at 20--34; Table S6)", "stevne-FE alder")
varianter = ["celler_min3", "uten_vind_0", "periode_2011_2019", "periode_2021_2026"]
endr = {(e, vv): rob.loc[e, vv] / rob.loc[e, "primaer"] - 1 for e in ["60m", "100m", "200m"]
        for vv in varianter if not pd.isna(rob.loc[e].get(vv))}
endr.update({(e, "uten2"): u2[e] / rob.loc[e, "primaer"] - 1 for e in ["60m", "100m", "200m"]})
krav(max(abs(x) for x in endr.values()) < 0.08,
     f"«essentially unchanged» i store sprint: maks {max(abs(x) for x in endr.values()):.3f}")
k.need("results", "Estimates were essentially unchanged when cells required three or more results",
       "robusthet (kvalitativ; tall i S2)")
tj = [rob.loc[e, "periode_2021_2026"] / rob.loc[e, "primaer"] - 1 for e in ["tresteg", "tresteg_sone_05m"]]
k.need("results", f"except the triple jumps, whose 2021--2026 estimates were {pst(min(tj))}--{pst(max(tj))}% higher",
       "tresteg i periodehalvdelene")


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
mg = (v("100m", "M", "12-13"), v("100m", "M", "20-34"))
mj = (v("100m", "F", "12-13"), v("100m", "F", "20-34"))
k.need("discussion", f"the boys' 100 m contrast was small ({f(mg[0]['medvind_s_per_ms'], 3)} versus "
       f"{f(mg[1]['medvind_s_per_ms'], 3)} s, overlapping intervals) and the girls' larger "
       f"({f(mj[0]['medvind_s_per_ms'], 3)} versus {f(mj[1]['medvind_s_per_ms'], 3)} s)", "medvind gutter/jenter")
krav(mg[0]["medvind_ki_lav"] <= mg[1]["medvind_ki_hoy"], "gutter 100 m medvind: KI overlapper")
krav(mj[0]["medvind_s_per_ms"] / mj[1]["medvind_s_per_ms"] > 1.3, "jenter 100 m medvind: klart større punktestimat («larger»)")
under = max((al[(al["event"] == e) & (al["kjonn"] == kj) & (al["enhet"] == "s")]["gevinst_per_ms"].max()
             - a(e, kj, "20-34")["gevinst_per_ms"])
            / al[(al["event"] == e) & (al["kjonn"] == kj) & (al["enhet"] == "s")]["gevinst_per_ms"].max()
            for e in ["100m", "200m"] for kj in ["M", "F"])
krav(0.37 <= under <= 0.43, f"«up to two-fifths» ({under:.3f})")
k.need("discussion", "understates youth wind effects by up to two-fifths", "undervurdering")
k.need("discussion", f"(on the 100 m, {f(min(r12), 2)}--{f(max(r12), 2)} of the robust scale at 12--13 against "
       f"{f(min(r20), 2)}--{f(max(r20), 2)} at 20--34)", "H5 diskusjon")
# Implications etter Atles beslutning 30.10.2026 (endringsrapporten avsnitt 8, punkt 2–3)
k.need("discussion", "In seconds, a legal tailwind is worth about as much to boys aged 12--13 as to senior men and "
       "more to girls than to senior women", "vindu gutter/jenter (krav i H5-blokken)")
r12_200 = [v("200m", kj, "12-13")["fordel_0_2_i_robust_skala"] for kj in ["M", "F"]]
r20_200 = [v("200m", kj, "20-34")["fordel_0_2_i_robust_skala"] for kj in ["M", "F"]]
krav(max(r12_200) < min(r20_200), "robust andel: seniorer over 12–13 også på 200 m")
k.need("discussion", "relative to athletes' own within-season variability it is worth less for the young than for "
       "seniors", "robust andel (krav over og i sammendragsblokken)")
krav(vin[vin["event"].isin(["100m", "200m"])]["fordel_0_2_s"].min() > 0.10,
     "vinduet er over en tidel i alle aldersbånd på 100 og 200 m")
k.need("discussion", "What it does in every age band is move 100 and 200 m marks by more than a tenth of a second",
       "en tidel (krav over)")
krav(all(a(e, kj, b)["gevinst_per_ms"] > a(e, kj, "20-34")["gevinst_per_ms"]
         for e in ["100m", "200m"] for kj in ["M", "F"] for b in FRA12[:-1]),
     "lineær helning 12–19 over 20–34 på 100 og 200 m, begge kjønn")
k.need("discussion", "a metre per second of wind moves those times by more seconds than at senior level",
       "talentsetningen (krav over)")
k.need("discussion", f"({flyt['rader_analyseklar']} analysed results, {flyt['rader_i_celler_min2']} of them "
       f"identifying; {flyt['celler_min2']} athlete-season-event cells)", "styrker")
k.need("discussion", f"missing wind ({pst(mvn['mean'], 1)}% of approved outdoor results", "begrensning")
k.need("conclusion", f"Per m/s of wind they are {pst(min(gutt + jente))}--{pst(max(gutt + jente))}% larger for "
       f"child sprinters than for seniors", "konklusjon")
k.need("conclusion", f"a +2.0 m/s tailwind is worth {vindu12} --- roughly the same across ages for boys and men, "
       "more for girls than for senior women --- enough to reorder season lists at youth and senior ages alike",
       "konklusjon H5 (krav i H5-blokken)")

# ================================================================ SUPPLEMENT-NOTER
k.need("supplementary material", f"$1.8 \\times {f(v('100m', 'F', '12-13')['medvind_0_2_s_per_ms'], 3)} = "
       f"{f(1.8 * v('100m', 'F', '12-13')['medvind_0_2_s_per_ms'], 2)}$", "regneeksempel")
k.need("supplementary material", f"Straight flat sprints cluster at {f(min(rett), 4)}--{f(max(rett), 4)}",
       "S4-note")
k.need("supplementary material", f"e.g. {f(kv.loc['lengde', 'beta_lin'], 4)} m = {f(100 * kv.loc['lengde', 'beta_lin'], 2)} cm", "S5-tekst")
krav(rob.loc["150m"][["celler_min3", "periode_2011_2019", "periode_2021_2026"]].isna().all(),
     "S2-note: 150 m mangler celler≥3 og periodekolonner")
krav(fa.loc[("200m", "M", "10-11"), "stevne_fe_se"] > 0.03, "S6-note: 200 m 10–11 uinformativ med stevne-FE")

# ================================================================ LYBBERT & ZHENG (2023)
la = les("r2_asym_100m.csv")
df = les("r2_drag_fart.csv").set_index("gruppe")["forhold_drag"]
la_alle = la[la["aldersband"] == "alle"].set_index(["kjonn", "stevne_fe"])
Fa, Ma = la_alle.loc[("F", False)], la_alle.loc[("M", False)]
Ff, Mf = la_alle.loc[("F", True)], la_alle.loc[("M", True)]
band = la[la["aldersband"] != "alle"]
inne = ((band["forhold_drag"] >= band["ki_lav"]) & (band["forhold_drag"] <= band["ki_hoy"]))
ute = band[~inne]
krav(len(ute) == 1 and (ute["ki_hoy"] < ute["forhold_drag"]).all(), "ett bånd utenfor, og det ligger under drag")
krav(Fa["forhold"] > Ma["forhold"] and Fa["forhold_drag"] > Ma["forhold_drag"], "jenter mer asymmetriske, som drag")
krav(Fa["ki_lav"] <= Fa["forhold_drag"] <= Fa["ki_hoy"], "jenter: drag innenfor KI («equals the drag prediction»)")
krav(Ma["forhold"] < Ma["forhold_drag"], "gutter: under drag («falls short»)")
krav(Ff["forhold"] < Fa["forhold"] and Mf["forhold"] < Ma["forhold"], "mindre asymmetri innen stevner")
krav(df["elite_menn"] < df["us_hs_gutter"] < df["us_hs_jenter"], "drag-asymmetrien vokser når farten faller")
k.need("results", f"(head/tail ratio {f(Fa['forhold'], 2)}, 95% CI {f(Fa['ki_lav'], 2)}--{f(Fa['ki_hoy'], 2)}, against "
       f"{f(Ma['forhold'], 2)}, {f(Ma['ki_lav'], 2)}--{f(Ma['ki_hoy'], 2)})", "asymmetri etter kjønn")
k.need("results", f"({f(Fa['forhold_drag'], 2)} and {f(Ma['forhold_drag'], 2)} at their own speeds)", "drag etter kjønn")
k.need("results", f"in {int(inne.sum())} of the {len(band)} sex × age bands the drag-only ratio lay inside the observed "
       "interval, and the exception lay below it", "bånd innenfor")
k.need("results", f"the ratios were {f(Ff['forhold'], 2)} and {f(Mf['forhold'], 2)} against drag-only "
       f"{f(Ff['forhold_drag'], 2)} and {f(Mf['forhold_drag'], 2)}", "stevne-FE asymmetri")
# Lybbert & Zheng tabell 2 (FE): medvind −0,050/−0,049; motvind × vind −0,037/−0,053 (gutter/jenter)
lz_g, lz_j = (0.050 + 0.037) / 0.050, (0.049 + 0.053) / 0.049
k.need("discussion", f"head/tail ratios of {f(lz_g, 2)} for boys and {f(lz_j, 2)} for girls", "Lybbert & Zheng tabell 2")
k.need("discussion", f"gives a ratio of {f(df['elite_menn'], 2)} at a uniform elite 10.0 s, {f(df['us_hs_gutter'], 2)} at their "
       f"boys' mean of 12.60 s and {f(df['us_hs_jenter'], 2)} at their girls' mean of 14.56 s", "drag ved fast fart")
k.need("discussion", f"({f(Ma['forhold_drag'], 2)} for our boys and men, averaging {f(Ma['snitt_tid'], 2)} s, and "
       f"{f(Fa['forhold_drag'], 2)} for our girls and women, averaging {f(Fa['snitt_tid'], 2)} s)", "drag i blandet utvalg")
krav(abs(lz_g - Ma["forhold_drag"]) < 0.10, "gutter i USA ≈ drag for blandet utvalg («about what drag predicts»)")
k.need("discussion", f"Their girls' ratio remains above the {f(Fa['forhold_drag'], 2)} of our faster girls and women",
       "jenter i USA over drag")
krav(Fa["snitt_tid"] < 14.557, "våre jenter raskere enn de amerikanske (14,56 s)")
k.need("introduction", "it did not examine how the effects scale with age or ability", "Lybbert & Zheng i innledningen")
k.need("abstract", "Almost all wind-effect estimates in athletics come from elite seniors", "nyhetspåstand")
krav(Ma["ki_lav"] <= Ma["forhold_drag"] <= Ma["ki_hoy"], "gutter: drag innenfor KI («in both sexes»)")
k.need("abstract", "on the 100 m by about as much as drag physics predicts at athletes' own speeds, in both sexes",
       "drag-påstand (krav: begge kjønn innenfor KI; 100 m samlet innen 5 %)")
k.need("methods", "the sex- and age-specific asymmetry comparison (Table S7) and the external-sample comparison (Table S8) were "
       "added after the plan", "planavvik S7 og S8")

# ================================================================ ELITEENDEN (tabell S8, 11_eliteende.py)
ee = les("r3_eliteende.csv").set_index(["kilde", "event", "kjonn"])
eet = les("r3_eliteende_tertil.csv").set_index(["event", "kjonn", "tertil"])
eer = les("r3_eliteende_robusthet.csv")
eef = json.loads((DATA / "eliteende_flyt.json").read_text())
tfm, tff = ee.loc[("TFRRS", "100m", "M")], ee.loc[("TFRRS", "100m", "F")]
tpm, tpf = ee.loc[("Tilastopaja", "100m", "M")], ee.loc[("Tilastopaja", "100m", "F")]
nom, nof = ee.loc[("Norge", "100m", "M")], ee.loc[("Norge", "100m", "F")]
snm, snf = ee.loc[("Norge_20_34", "100m", "M")], ee.loc[("Norge_20_34", "100m", "F")]
seks = [nom, nof, tfm, tff, tpm, tpf]
tl = lambda kj, t: eet.loc[("100m", kj, t)]
# Norge-radene i S8 er regnet med samme kode som tabell 2-4/S7 og skal gi de samme tallene
krav(abs(snm["gevinst_per_ms"] - a("100m", "M", "20-34")["gevinst_per_ms"]) < 1e-9
     and abs(snf["gevinst_per_ms"] - a("100m", "F", "20-34")["gevinst_per_ms"]) < 1e-9, "S8: Norge 20-34 = tabell 3")
krav(all(abs(x["ratio_drag"] - la_alle.loc[(kj, False), "forhold_drag"]) < 1e-9 for x, kj in [(nom, "M"), (nof, "F")]),
     "S8: Norge alle aldre drag-forhold = S7")
k.need("methods", f"NCAA Division I athletes, {eef['TFRRS']['aar_fra']}--{eef['TFRRS']['aar_til']}, read from a cleaned, "
       f"hash-checked shared build of the profiles ({eef['TFRRS']['uten_eksakte_dubletter']} results of "
       f"{eef['TFRRS']['utovere']} athletes", "TFRRS-utvalg")
k.need("methods", f"final between {eef['Tilastopaja']['aar_fra']} and {eef['Tilastopaja']['aar_til']} "
       f"({eef['Tilastopaja']['med_kjonn']} results of {eef['Tilastopaja']['utovere']} athletes)", "Tilastopaja-utvalg")
k.need("results", f"on the 100 m, {f(tfm['gevinst_per_ms'], 3)} s per m/s (95% CI {f(tfm['ki_lav'], 3)}--"
       f"{f(tfm['ki_hoy'], 3)}) for collegiate men and {f(tff['gevinst_per_ms'], 3)} ({f(tff['ki_lav'], 3)}--"
       f"{f(tff['ki_hoy'], 3)}) for collegiate women, {f(tpm['gevinst_per_ms'], 3)} ({f(tpm['ki_lav'], 3)}--"
       f"{f(tpm['ki_hoy'], 3)}) and {f(tpf['gevinst_per_ms'], 3)} ({f(tpf['ki_lav'], 3)}--{f(tpf['ki_hoy'], 3)}) for "
       f"championship finalists", "eliteenden 100 m")
andel = [x["gevinst_per_ms"] / h("100m")["gevinst_per_ms"] for x in (tfm, tff, tpm, tpf)]
k.need("results", f"{pst(min(andel))}--{pst(max(andel))}% of the registry's {f(h('100m')['gevinst_per_ms'], 3)}",
       "andel av registeret")
krav(max(abs(x["gevinst_per_ms"] - x["moinat_plus1"]) for x in (tfm, tpm, tpf)) < 0.002
     and abs(tff["gevinst_per_ms"] - tff["moinat_plus1"]) > 0.002, "Moinat: tre av fire innen 0,002 s")
k.need("results", "for three of the four groups within 0.002 s of the level formula of", "Moinat-avvik (krav over)")
ps6 = [tl(kj, t)["per_sekund"] for kj in "MF" for t in ("lav", "midt", "hoy")]
k.need("results", f"its ability tertiles sit at {f(min(ps6), 4)}--{f(max(ps6), 4)} per second of race time",
       "tertiler per sekund")
krav(max(ps6) - min(ps6) < 0.0006, "tertiler «flat» per sekund")
rel = [1 - x["per_sekund"] / ref["per_sekund"] for x, ref in [(tfm, nom), (tff, nof), (tpm, nom), (tpf, nof)]]
reg = [nom["per_sekund"], nof["per_sekund"]]
eks = [x["per_sekund"] for x in (tfm, tff, tpm, tpf)]
k.need("results", f"the 100 m rate is {f(min(reg), 4)}--{f(max(reg), 4)} in the registry against {f(min(eks), 4)}--"
       f"{f(max(eks), 4)} in the external samples, {pst(min(rel))}--{pst(max(rel))}% lower for the same sex",
       "per sekund tre kilder")
lov = [x["a6_lov_lav"] for x in (tfm, tff, tpm, tpf)] + [x["a6_lov_hoy"] for x in (tfm, tff, tpm, tpf)]
obs = [x["gevinst_per_ms"] for x in (tfm, tff, tpm, tpf)]
k.need("results", f"predicts {f(min(lov), 3)}--{f(max(lov), 3)} s per m/s at their mean times against the observed "
       f"{f(min(obs), 3)}--{f(max(obs), 3)}", "S4-loven mot observert")
krav(min(lov) > max(obs), "S4-loven over alle observerte")
k.need("results", f"the registry's seniors gained {f(snm['gevinst_per_ms'], 3)} s per m/s ({f(snm['ki_lav'], 3)}--"
       f"{f(snm['ki_hoy'], 3)}) against {f(tl('M', 'lav')['gevinst_per_ms'], 3)} ({f(tl('M', 'lav')['ki_lav'], 3)}--"
       f"{f(tl('M', 'lav')['ki_hoy'], 3)}) for the slowest collegiate tertile of men, at "
       f"{f(snm['snitt'], 1)} and {f(tl('M', 'lav')['snitt'], 1)} s, and {f(snf['gevinst_per_ms'], 3)} "
       f"({f(snf['ki_lav'], 3)}--{f(snf['ki_hoy'], 3)}) against {f(tl('F', 'lav')['gevinst_per_ms'], 3)} "
       f"({f(tl('F', 'lav')['ki_lav'], 3)}--{f(tl('F', 'lav')['ki_hoy'], 3)}) for women, at {f(snf['snitt'], 1)} and "
       f"{f(tl('F', 'lav')['snitt'], 1)} s", "lik løpstid")
krav(snm["ki_lav"] > tl("M", "lav")["ki_hoy"] and snf["ki_lav"] > tl("F", "lav")["ki_hoy"],
     "lik løpstid: intervallene overlapper ikke")
krav(abs(snm["snitt"] - tl("M", "lav")["snitt"]) < 0.25 and abs(snf["snitt"] - tl("F", "lav")["snitt"]) < 0.25,
     "lik løpstid: snittider innen 0,25 s")
k.need("results", f"({f(tfm['ratio_obs'], 2)} and {f(tff['ratio_obs'], 2)} against {f(tfm['ratio_drag'], 2)} and "
       f"{f(tff['ratio_drag'], 2)}, men and women)", "TFRRS asymmetri")
krav(all(x["ratio_ki_lav"] <= x["ratio_drag"] <= x["ratio_ki_hoy"] for x in (tfm, tff)), "college: drag innenfor KI («matched»)")
k.need("results", f"({f(tpm['ratio_obs'], 2)} and {f(tpf['ratio_obs'], 2)} against {f(tpm['ratio_drag'], 2)} and "
       f"{f(tpf['ratio_drag'], 2)}; Table S8)", "Tilastopaja asymmetri")
krav(all(x["ratio_drag"] < x["ratio_ki_lav"] for x in (tpm, tpf)), "finalister: drag under KI («exceeded»)")
fall = [1 - x["over_2_vs_0_2"] for x in seks]
fall_d = [1 - x["over_2_vs_0_2_drag"] for x in seks]
k.need("results", f"was {pst(min(fall))}--{pst(max(fall))}% lower than over 0 to +2 m/s, against the {pst(min(fall_d))}--"
       f"{pst(max(fall_d))}% that drag-only physics predicts", "knekk over +2")
krav(min(fall) > 0 and max(fall) <= max(fall_d), "medvindshelningen over +2 lavere enn over 0-2 i alle seks grupper, "
     "og det største fallet ligger innenfor dragspennet")
prim = eer[eer["analyse"] == "primaer"].set_index(["kilde", "event", "kjonn"])["gevinst_per_ms"]
sp = eer[eer["event"].isin(["100m", "200m"]) & (eer["analyse"] != "primaer")]
maks = max(abs(r["gevinst_per_ms"] / prim[(r["kilde"], r["event"], r["kjonn"])] - 1) for _, r in sp.iterrows())
k.need("supplementary material", f"the 100 and 200 m slopes moved by at most {pst(maks)}%", "ekstern robusthet (S8-note)")
demp = [1 - x["stevne_fe"] / x["gevinst_per_ms"] for x in seks]
k.need("supplementary material", f"attenuated the 100 m slopes by {pst(min(demp))}--{pst(max(demp))}% in all three samples",
       "ekstern stevne-FE (S8-note)")
k.need("discussion", f"and the {f(min(obs), 3)}--{f(max(obs), 3)} s per m/s that the same estimator returns in collegiate "
       "and world-class 100 m samples", "eliteenden i diskusjonen")
k.need("discussion", f"the collegiate and world-class 100 m slopes lie {pst(min(rel))}--{pst(max(rel))}% below the registry's",
       "per sekund i diskusjonen")
mer = [snm["gevinst_per_ms"] / tl("M", "lav")["gevinst_per_ms"] - 1, snf["gevinst_per_ms"] / tl("F", "lav")["gevinst_per_ms"] - 1]
krav(0.18 <= min(mer) and max(mer) <= 0.27, f"«a fifth to a quarter more» ({[round(x, 3) for x in mer]})")
k.need("discussion", "gain a fifth to a quarter more than the slowest collegiate tertile", "lik løpstid i diskusjonen")
krav(f(tpm["ratio_obs"], 1) == f(tpf["ratio_obs"], 1), "begge finalistforhold runder til samme verdi med én desimal")
k.need("discussion", f"only the championship finalists exceed it ({f(tpm['ratio_obs'], 1)} against {f(tpm['ratio_drag'], 2)}--"
       f"{f(tpf['ratio_drag'], 2)})", "finalister i diskusjonen")
k.need("discussion", f"a tailwind is worth least to them ({f(tpm['medvind'], 3)} and {f(tpf['medvind'], 3)} s per m/s) while "
       f"their headwind slopes ({f(tpm['motvind'], 3)} and {f(tpf['motvind'], 3)}) are about the collegiate ones "
       f"({f(tfm['motvind'], 3)} and {f(tff['motvind'], 3)})", "medvind/motvind finalister")
krav(tpm["medvind"] < min(tfm["medvind"], nom["medvind"], snm["medvind"])
     and tpf["medvind"] < min(tff["medvind"], nof["medvind"], snf["medvind"]), "finalistene: minst medvindsgevinst")
krav(abs(tpm["motvind"] - tfm["motvind"]) < 0.01 and abs(tpf["motvind"] - tff["motvind"]) < 0.01,
     "finalistenes motvindshelning ≈ college (innen 0,01 s)")
k.need("conclusion", f"the same estimator gives {f(min(obs), 3)}--{f(max(obs), 3)} s per m/s on the 100 m in collegiate and "
       f"world-class samples against {f(h('100m')['gevinst_per_ms'], 3)} in the registry", "konklusjon eliteenden")
# tabell S8 mot R: utvalg, snittmerke og lineært estimat med KI, rad for rad
if not (R / "eliteende.csv").exists():
    FEIL.append("R-utdata audit/r_out/eliteende.csv mangler (kjør audit/uavhengig.R)")
rs = pd.read_csv(R / "eliteende.csv") if (R / "eliteende.csv").exists() else pd.DataFrame(columns=["kilde", "event", "kjonn"])
navn_k = {"Registry, all ages": "Norge", "Registry, 20--34": "Norge_20_34", "US collegiate (TFRRS)": "TFRRS",
          "Championship finalists (Tilastopaja)": "Tilastopaja"}
ev_k = {"100 m": "100m", "200 m": "200m", "100 m hurdles": "100mH", "110 m hurdles": "110mH", "Long jump": "LJ",
        "Triple jump": "TJ"}
ev_s8, kj_s8, n_s8 = None, None, 0
for ln in (PROSJ / "manus" / "s8.tex").read_text().splitlines():
    m_ = re.match(r"\\multicolumn\{11\}\{l\}\{\\textit\{(.+), (men|women)\}\}", ln)
    if m_:
        ev_s8, kj_s8 = ev_k[m_.group(1)], {"men": "M", "women": "F"}[m_.group(2)]
        continue
    lab = ln.split(" &")[0]
    if lab not in navn_k:
        continue
    n_s8 += 1
    rr = rs[(rs["kilde"] == navn_k[lab]) & (rs["event"] == ev_s8) & (rs["kjonn"] == kj_s8)]
    if not len(rr):
        continue
    rr = rr.iloc[0]
    vist = tall_i(ln.split("&", 1)[1])
    dd = 3 if ev_s8 in ("100m", "200m", "100mH", "110mH") else 2
    forvent = [str(int(rr["n"])), f(rr["snitt"], 2), f(rr["gevinst"], dd), f(rr["ki_lav"], dd), f(rr["ki_hoy"], dd)]
    if vist[:5] != forvent:
        FEIL.append(f"s8 {lab} {ev_s8} {kj_s8}: vist {vist[:5]}, R gir {forvent}")
    else:
        k.n_ok += 1
krav(n_s8 == len(ee), f"S8 har like mange rader som estimeringsfilen ({n_s8} mot {len(ee)})")

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
for t in ["t1", "t2", "t3", "t4", "t5", "t6", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8"]:
    krav(f"\\input{{{t}}}" in k.raa, f"\\input{{{t}}} i manus (genererte tabeller)")

# ================================================================ ORDTELLING
ord_n = ordtelling(PROSJ / "manus" / "main.tex")
k.need("tittelside", f"Word count: $\\sim${int(round(ord_n, -2))}", f"ordtelling ({ord_n})")

# ================================================================ DEKNING
UNNTAK = [
    r"\$\(2v\+w\)/\(2v-w\)\$",
    r"\\S\\S 2 and 4", r"ages 13 and above",   # helseforskningsloven §§ 2 og 4; datatilgang (30.10.2026)
    r"\\vspace\*?\{[^}]*\}", r"\d*\.?\d+\\textwidth", r"width=\d*\.?\d+\\textwidth",
    r"orcid\.org/[\d-]+\}\{ORCID: [\d-]+\}", r"Box 5003, 1432", r"\$\^\{?1,?\*?\}?\$", r"\$\^1\$",
    r"\\setcounter\{table\}\{0\}", r"\\begin\{titlepage\}", r"\{S\\arabic\{table\}\}",
    r"\b(10|12|14|16|18|20)--(11|13|15|17|19|34)\b",
    r"\b(60|80|100|110|150|200)( m|m)\b", r"\b(68|76\.2|84|91\.4|100|106\.7) cm\b",
    r"\b(19|20)\d\d\b", r"\bH[1-5]\b", r"Table~?S\d", r"Section \d\.\d",
    r"±2\.0 m/s", r"\+2\.0 m/s", r"\+2\.0\b", r"\b2\.0 m/s", r"±8 m/s", r"±0\.2 of \+2\.0", r"[+-±]?1 m/s",
    r"\+1\.8 m/s", r"exactly 0\.0", r"exactly \+2\.0", r"95% CIs?", r"5th--95th percentile", r"\(1\.8, 2\.0\]",
    r"\(2\.0, 2\.2\]", r"\$\(2v\+1\)/\(2v-1\)\$?", r"\$v\^2\$", r"\(m/s\)\$\^2\$", r"\$2 \\times\$",
    r"age 1[03]", r"under 13", r"12-year-old", r"age-19", r"class-14", r"top-10", r"top-50", r"top 10",
    r"29 October 2026", r"\bS[1-6]\b", r"10 s from", r"13 s in", r"5 s per attempt", r"60 and 80 m",
    r"\\times 10\^\{-2\}", r"\$\\sim\$", r"\bten\b", r"ten-year-olds",
    r"0\.0\b(?= m/s| readings|,| more)", r"p < 0\.001", r"cells with at least three", r"at least two",
    r"\bstratum is 20--34\b",
    r"\b(60|80|100|110|150|200)( and |/)(60|80|100|110|150|200) ?m\b", r"\b20(11|21)--20(19|26)\b",
    r"60 m above 17", r"cells-≥3", r"10--12 age classes", r"In cells ≥2",
    r"ages 11--13", r"0 to \+2 m/s", r"above \+2\b", r"\+2\b(?= \()", r"1\.4826( times| \$\\times\$)",
    r"200 m times filed as 100 m", r"exactly ±1 m/s", r"20--34 \(", r"1\.4826 ×",
    r"version 1\.2", r"\b(19|20)\d\d--(19|20)\d\d\b",
]
k.need("results", f"Dashes: fewer than {m03.MIN_N} results in {m03.MIN_CELLER} athlete-seasons", "tabellnote 3")
k.need("results", f"Codes with fewer than {m03.MIN_N} results for one sex", "tabellnote 5")
# ================================================================ ANONYMITET (JSS, dobbeltanonym)
# Forfatteropplysninger og identifiserende erklæringer står i title_page.tex (egen fil, 30.10.2026).
for s in ["Atle", "Simen", "NMBU", "ORCID", "nmbu.no", "AGG", "Ås", "author's initiative", "from the author",
          "Acknowledgements", "Competing interests", "Author contributions"]:
    krav(s not in k.raa, f"anonymt manus: «{s}» står ikke i main.tex")
krav(not re.search(r"\bSG\b", k.raa), "anonymt manus: «SG» står ikke i main.tex")
# Simen Guttormsen medforfatter med samme tilknytning (Atles beslutning 30.10.2026): to forfattere,
# erklæringene i flertall
kt = Kontroll(PROSJ / "manus" / "title_page.tex", "A6 tittelside")
for s in ["Guttormsen", "Simen Guttormsen$^{1}$", "ORCID", "Disclosure of interest", "Funding",
          "Author contributions", "Both authors approved", "Declaration of AI use", "Acknowledgements",
          "Tilastopaja Oy"]:
    krav(s in kt.raa, f"tittelsiden har «{s}»")
for s in ["The author ", "The author's", "takes full responsibility"]:
    krav(s not in kt.raa, f"tittelsiden står i flertall («{s}» finnes ikke)")
kode_m = k.rapport(UNNTAK)
kode_t = kt.rapport(UNNTAK)
print(f"\nA6 TOTALT: {k.n_ok + kt.n_ok} sjekker OK, {len(k.feil) + len(kt.feil)} feil")
sys.exit(1 if (kode_m or kode_t) else 0)
