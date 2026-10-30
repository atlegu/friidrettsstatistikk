"""
05b_revisjon_r2.py — A3: analysene etter dataauditen 30.10.2026 (endringsrapporten, punkt 14–19).

Analyseplanens H2 (Cox med alder som tidsskala og KM med forsinket inngang ved debut) er
erstattet: frafallsrisikoen avhenger av tid siden debut, så proporsjonalitetsantakelsen brytes
per konstruksjon, og produktgrense-estimatoren ganger sammen førstesesongsfallene til ulike
debutaldre i én kurve. H2 besvares i stedet

  - på varighetsklokken: andel aktiv k år etter debut (05_revisjon_r1.py) og et utfall målt ved
    lik karrierelengde: >= 2 konkurransedager i en sesong minst D år etter debut (D = 4 primært,
    5 og 6 som følsomhet; bare utøvere der debutalder + D er observert ut 2025);
  - på aldersklokken: direkte andel av hver debutgruppe med resultat ved alder t eller senere,
    kull 2001–2004 (fullt observert til 21 år) — figur 3.

I tillegg: H1 uten 2001-kullet (tynnest dekning i 2011), H1 med utøvere uten registrert kjønn
(kjønn som «ukjent»), andelen med fødselsdato etter utfall og debutalder (seleksjonen som gjør
fødselskvartal-interaksjonen uegnet), og debut 16-armen mot koronadebutene (Atles beslutning
30.10.2026, endringsrapporten avsnitt 8, punkt 1).

Output: tables/modeller/r2_*.csv, figures/fig4_shares_by_age.png
"""

import importlib.util
import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats as scst
from statsmodels.stats.proportion import proportion_confint

HERE = Path(__file__).parent
DATA = HERE / "data_private"
MOD = HERE / "tables" / "modeller"
FIG = HERE / "figures"

spec = importlib.util.spec_from_file_location("m03", HERE / "03_modeller.py")
m03 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m03)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
SISTE_HELE_SESONG = 2025
GRUPPER = [("10-11", 10, 11), ("12-13", 12, 13), ("14-16", 14, 16)]
GRONN, ROD, GRAA = "#1b6e1b", "#b22222", "#666666"
plt.rcParams.update({"figure.dpi": 300, "savefig.dpi": 300, "font.size": 11,
                     "axes.grid": True, "grid.alpha": 0.3, "axes.titlesize": 13})


def forbered(d):
    d = d.copy()
    d["region"] = d["region"].fillna("ukjent")
    d["log_klubbstorrelse"] = d["log_klubbstorrelse"].fillna(d["log_klubbstorrelse"].median())
    d["debut_kat"] = pd.Categorical(d["debut_alder"].clip(upper=17), categories=range(10, 18))
    return d


def last():
    d = forbered(pd.read_csv(DATA / "analysedata.csv"))
    return d, d[d["kohort_primar"] & d["debut_10_16"]].copy()


def direkte_andeler(p):
    s = p[p["birth_year"].between(2001, 2004)]
    rader = []
    for t in range(14, 22):
        for navn, lo, hi in GRUPPER:
            x = s[s["debut_alder"].between(lo, hi)]
            k = int((x["siste_alder"] >= t).sum())
            ki = proportion_confint(k, len(x), method="wilson")
            rader.append({"alder": t, "gruppe": navn, "n": len(x), "aktive": k, "andel": k / len(x),
                          "ki_lav": ki[0], "ki_hoy": ki[1]})
    return pd.DataFrame(rader)


def fig4(da):
    fig, ax = plt.subplots(figsize=(8.2, 5.4))
    for (navn, _, _), farge, mark in zip(GRUPPER, [GRONN, GRAA, ROD], ["o", "s", "^"]):
        g = da[(da["gruppe"] == navn) & (da["alder"] >= 16)]
        ax.plot(g["alder"], 100 * g["andel"], color=farge, marker=mark, lw=2.4, ms=7,
                label=f"Debut {navn.replace('-', '–')} (n = {int(g['n'].iloc[0]):,})")
        ax.fill_between(g["alder"], 100 * g["ki_lav"], 100 * g["ki_hoy"], color=farge, alpha=0.13)
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Registered result at this age or later (%)")
    ax.set_title("Share of each debut group still competing, by age (born 2001–2004)")
    ax.set_xticks(range(16, 22))
    ax.legend(frameon=False, fontsize=9.5)
    fig.tight_layout()
    fig.savefig(FIG / "fig4_shares_by_age.png", bbox_inches="tight")   # figur 4 i trykk
    plt.close(fig)


def lik_varighet(p):
    v = pd.read_csv(DATA / "arsvolum.csv").merge(p[["athlete_id", "debut_alder"]], on="athlete_id")
    andeler, modeller = [], []
    for D in (4, 5, 6):
        q = p[p["debut_alder"] + D <= SISTE_HELE_SESONG - p["birth_year"]].copy()
        ok = v[(v["alder"] >= v["debut_alder"] + D) & (v["dager"] >= 2)]["athlete_id"].unique()
        q["utfall"] = q["athlete_id"].isin(set(ok)).astype(int)
        for a, x in q.groupby("debut_alder"):
            ki = proportion_confint(int(x["utfall"].sum()), len(x), method="wilson")
            andeler.append({"D": D, "debut_alder": a, "n": len(x), "hendelser": int(x["utfall"].sum()),
                            "andel": x["utfall"].mean(), "ki_lav": ki[0], "ki_hoy": ki[1]})
        modeller.append(m03.logit_rader(q, ["debut_alder"] + m03.JUST, "utfall", f"varighet_{D}"))
        modeller.append(m03.logit_rader(q, ["debut_kat"] + m03.JUST, "utfall", f"varighet_{D}_kategorisk"))
    return pd.DataFrame(andeler), pd.concat(modeller)


def uten_2001(p):
    q = p[p["birth_year"] != 2001]
    return pd.concat([m03.logit_rader(q, ["debut_kat"] + m03.JUST, "senior", "uten_2001_kategorisk"),
                      m03.logit_rader(q, ["debut_alder"] + m03.JUST, "senior", "uten_2001_trend")])


def med_ukjent_kjonn():
    """H1 med utøvere uten registrert kjønn (kjønn = «ukjent»). Klubbstørrelsen telles som i
    hovedanalysen, over alle debutanter, nå inkludert dem uten registrert kjønn."""
    a = pd.read_csv(DATA / "analysedata.csv")
    u = pd.read_csv(DATA / "analysedata_ukjent_kjonn.csv").assign(gender="ukjent")
    s = pd.concat([a.drop(columns=["klubbstorrelse", "log_klubbstorrelse"]), u], ignore_index=True)
    s["klubbstorrelse"] = s.groupby("club_id")["athlete_id"].transform("count")
    s["log_klubbstorrelse"] = np.log1p(s["klubbstorrelse"])
    s = forbered(s)
    s = s[s["kohort_primar"] & s["debut_10_16"]]
    ut = pd.concat([m03.logit_rader(s, ["debut_alder"] + m03.JUST, "senior", "med_ukjent_kjonn_trend"),
                    m03.logit_rader(s, ["debut_kat"] + m03.JUST, "senior", "med_ukjent_kjonn_kategorisk")])
    ut["n_ukjent"] = int((s["gender"] == "ukjent").sum())
    ut["konvertering_debut10"] = s.loc[s["debut_alder"] == 10, "senior"].mean()
    return ut


def seleksjon_kvartal(p):
    rader = [{"gruppe": f"senior={s}", "andel_med_fodselsdato": x["kvartal"].notna().mean(), "n": len(x)}
             for s, x in p.groupby("senior")]
    rader += [{"gruppe": f"debut {a}", "andel_med_fodselsdato": x["kvartal"].notna().mean(), "n": len(x)}
              for a, x in p.groupby("debut_alder")]
    return pd.DataFrame(rader)


def lrt(q):
    """Kategorisk mot lineær debutalder (samme justering som H1)."""
    xl, xk = m03.design(q, ["debut_alder"] + m03.JUST), m03.design(q, ["debut_kat"] + m03.JUST)
    ml, mk = sm.Logit(q["senior"], xl).fit(disp=0), sm.Logit(q["senior"], xk).fit(disp=0)
    lr, df = 2 * (mk.llf - ml.llf), xk.shape[1] - xl.shape[1]
    return {"LR": lr, "df": df, "p": float(1 - scst.chi2.cdf(lr, df)), "n": len(q),
            "hendelser": int(q["senior"].sum())}


def covid_debut16(p):
    """Debut 16-armen mot koronadebutene. Kull 2004 og 2005 fylte 16 i 2020 og 2021, så hele
    debut-16-gruppen deres er koronadebuter. Den kategoriske kontrasten (primærvisningen) regnes
    derfor uten 2020–2021-debuter, med koronaflagg og per kohorthalvdel; robusthetsanalysene i
    03 gjaldt bare den lineære trenden."""
    q = p[~p["covid_debut"]]
    pc = p.copy()
    pc["covid_debut"] = pc["covid_debut"].astype(float)
    halv = {"kohort_2001_2003": p[p["birth_year"].between(2001, 2003)],
            "kohort_2004_2005": p[p["birth_year"].between(2004, 2005)]}
    mod = pd.concat([m03.logit_rader(q, ["debut_kat"] + m03.JUST, "senior", "uten_covid_kategorisk"),
                     m03.logit_rader(pc, ["debut_kat", "covid_debut"] + m03.JUST, "senior",
                                     "covid_flagg_kategorisk")]
                    + [m03.logit_rader(g, ["debut_kat"] + m03.JUST, "senior", f"{navn}_kategorisk")
                       for navn, g in halv.items()])
    lr = pd.DataFrame([{"utvalg": "uten_covid_debut", **lrt(q)}]
                      + [{"utvalg": navn, **lrt(g)} for navn, g in halv.items()])
    d16 = p[p["debut_alder"] == 16]
    konv = (d16.groupby("covid_debut")["senior"].agg(n="size", seniorer="sum").reset_index()
            .assign(andel=lambda x: x["seniorer"] / x["n"]))
    konv["kull_2004_2005"] = [int(((d16["covid_debut"] == c) & d16["birth_year"].between(2004, 2005)).sum())
                              for c in konv["covid_debut"]]
    return mod, lr, konv


def main():
    _, p = last()
    da = direkte_andeler(p)
    da.to_csv(MOD / "r2_andel_etter_alder.csv", index=False)
    fig4(da)
    andel, mod = lik_varighet(p)
    andel.to_csv(MOD / "r2_varighet_andeler.csv", index=False)
    mod.to_csv(MOD / "r2_varighet_modeller.csv", index=False)
    uten_2001(p).to_csv(MOD / "r2_uten_2001.csv", index=False)
    med_ukjent_kjonn().to_csv(MOD / "r2_ukjent_kjonn.csv", index=False)
    seleksjon_kvartal(p).to_csv(MOD / "r2_seleksjon_kvartal.csv", index=False)
    cmod, clr, ckonv = covid_debut16(p)
    cmod.to_csv(MOD / "r2_covid_kategorisk.csv", index=False)
    clr.to_csv(MOD / "r2_covid_lrt.csv", index=False)
    ckonv.to_csv(MOD / "r2_debut16_covid.csv", index=False)
    t = cmod[(cmod["analyse"] == "uten_covid_kategorisk") & (cmod["variabel"] == "debut_kat_16")].iloc[0]
    logger.info(f"debut 16 uten koronadebuter: OR {t['OR']:.2f} [{t['KI_lav']:.2f}, {t['KI_hoy']:.2f}]")
    logger.info(f"r2-filer i {MOD}/ og figur 4 i {FIG}/")


if __name__ == "__main__":
    main()
