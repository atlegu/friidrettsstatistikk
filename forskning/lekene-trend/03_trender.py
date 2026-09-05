"""
03_trender.py - Trendestimater per øvelse x klasse 2012-2025, samlet i øvelsesgrupper.

Metode: kvantilregresjon (Koenker & Bassett, 1978) av log(resultat) på kalenderår
per øvelse x klasse, for medianen (q = 0,5) og toppen (beste desil: q = 0,9 for
hopp/kast, q = 0,1 for løp). Stigning x 1000 = prosent endring per tiår; fortegnet
snus for løp slik at positivt alltid betyr "bedre". Robusthetsmål: nivå 2022-2025
mot 2012-2019 (covid-årene 2020-2021 utelatt).

Inn: data/lekene_2012_2025.csv, tables/gjentakere_forbedring.csv (fra 02_deskriptiv.py)
Ut:  tables/trender_per_serie.csv, tables/trender_per_gruppe.csv, tables/trender_per_klasse.csv,
     figures/fig9_trendoversikt.png
"""

import importlib
import logging
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from matplotlib.lines import Line2D

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=UserWarning)   # QuantReg-konvergens ved mange like verdier

HERE = Path(__file__).parent
desk = importlib.import_module("02_deskriptiv")   # gjenbruker øvelseslister, tokens og load()
FIG, TAB, GROUPS, LABEL, COL, STYLE = desk.FIG, desk.TAB, desk.GROUPS, desk.LABEL, desk.COL, desk.STYLE
INK, INK2, MUTED, GRID, AXIS = desk.INK, desk.INK2, desk.MUTED, desk.GRID, desk.AXIS

GRUPPER = [
    ("Sprint", ["60 m", "200 m"]),
    ("Hekk", ["60 m hekk", "80 m hekk", "200 m hekk"]),
    ("Mellomdistanse", ["600 m", "1500 m"]),
    ("Horisontale hopp", ["Lengde", "Tresteg"]),
    ("Vertikale hopp", ["Høyde", "Stav"]),
    ("Kast", ["Kule", "Spyd", "Diskos", "Slegge"]),
]
FOR_ALLE = 0.4      # for korte serier (stav, kast) kreves minst så mange resultater totalt
MIN_TOTAL = 120


def serier():
    """(øvelse, kode, resultattype, gruppe) for alle serier som skal estimeres."""
    out = [(name, code, rtype, g) for code, name, rtype in desk.SHARED for g in GROUPS]
    for name, codes in desk.FAMILIES:
        rtype = "time" if "hekk" in name else "distance"
        out += [(name, c, rtype, g) for g, c in codes.items() if c]
    return out


def qreg(yr, logv, q):
    """Kvantilregresjon av log(resultat) på år; returnerer stigning, 95 %-KI og p per år."""
    X = sm.add_constant(yr - 2012.0)
    r = sm.QuantReg(logv, X).fit(q=q, max_iter=5000)
    b, se, p = r.params[1], r.bse[1], r.pvalues[1]
    return b, b - 1.96 * se, b + 1.96 * se, p


def trend_serie(d, name, code, rtype, g):
    sub = d[(d.ovelse == code) & (d.klasse_kjonn == g)]
    if len(sub) < MIN_TOTAL:
        return None
    yr, logv = sub.yr.to_numpy(float), np.log(sub.verdi.to_numpy(float))
    sign = -1.0 if rtype == "time" else 1.0
    q_topp = 0.1 if rtype == "time" else 0.9
    row = dict(ovelse=name, kode=code, gruppe=g, n=len(sub), aar=sub.yr.nunique())
    for lab, q in [("median", 0.5), ("topp", q_topp)]:
        b, lo, hi, p = qreg(yr, logv, q)
        est = sign * 1000 * np.array([b, lo, hi])            # % per tiår, positivt = bedre
        row[f"{lab}_pct_tiaar"], row[f"{lab}_ki_lo"], row[f"{lab}_ki_hi"] = est[0], est.min(), est.max()
        row[f"{lab}_p"] = p
        # nivåsammenligning før/etter covid
        v0 = sub[sub.yr.between(2012, 2019)].verdi.quantile(q)
        v1 = sub[sub.yr.between(2022, 2025)].verdi.quantile(q)
        row[f"{lab}_endring_2022_25_vs_2012_19_pct"] = sign * 100 * (v1 / v0 - 1)
    return row


def gruppe_av(ovelse):
    return next(gr for gr, evs in GRUPPER if ovelse in evs)


def oppsummer(t, by):
    """Snitt, spredning og fortegnstelling per gruppering."""
    rows = []
    for key, sub in t.groupby(by):
        r = {by if isinstance(by, str) else "_".join(by): key, "serier": len(sub)}
        for lab in ["median", "topp"]:
            x = sub[f"{lab}_pct_tiaar"]; p = sub[f"{lab}_p"]
            r[f"{lab}_snitt_pct_tiaar"] = x.mean()
            r[f"{lab}_median_pct_tiaar"] = x.median()
            r[f"{lab}_andel_negativ"] = (x < 0).mean()
            r[f"{lab}_sign_neg"] = int(((x < 0) & (p < 0.05)).sum())
            r[f"{lab}_sign_pos"] = int(((x > 0) & (p < 0.05)).sum())
        rows.append(r)
    return pd.DataFrame(rows)


def fig_trendoversikt(t):
    order = [ev for _, evs in GRUPPER for ev in evs]
    ypos = {ev: i for i, ev in enumerate(order)}
    off = {"G13": -0.27, "G14": -0.09, "J13": 0.09, "J14": 0.27}
    fig, axes = plt.subplots(1, 2, figsize=(11, 8), sharey=True)
    for ax, lab, title in [(axes[0], "median", "Bredden: medianen"), (axes[1], "topp", "Toppen: beste desil")]:
        for _, r in t.iterrows():
            y = ypos[r.ovelse] + off[r.gruppe]
            c = COL[r.gruppe[0]]; st = STYLE[int(r.gruppe[1:])]
            ax.plot([r[f"{lab}_ki_lo"], r[f"{lab}_ki_hi"]], [y, y], color=c, lw=1.2, alpha=0.7, solid_capstyle="butt")
            ax.plot(r[f"{lab}_pct_tiaar"], y, marker=st["marker"], color=c, ls="none", ms=5.5,
                    mfc=c if r[f"{lab}_p"] < 0.05 else "white", mew=1.4)
        ax.axvline(0, color=INK2, lw=1)
        # gruppeskiller og -navn
        i = 0
        for gr, evs in GRUPPER:
            if i > 0:
                ax.axhline(i - 0.5, color=AXIS, lw=0.8)
            ax.text(1.01, i + len(evs) / 2 - 0.5, gr, transform=ax.get_yaxis_transform(),
                    fontsize=7.5, color=MUTED, rotation=270, va="center", ha="left") if ax is axes[1] else None
            i += len(evs)
        ax.set_yticks(range(len(order))); ax.set_yticklabels(order)
        ax.set_ylim(len(order) - 0.5, -0.5)
        ax.set_xlabel("% bedre per tiår (95 % KI)")
        ax.set_title(title, loc="left", color=INK, fontweight="bold")
        ax.grid(axis="y", visible=False)
    lim = max(abs(np.nanmin(t[["median_ki_lo", "topp_ki_lo"]].to_numpy())),
              abs(np.nanmax(t[["median_ki_hi", "topp_ki_hi"]].to_numpy())))
    for ax in axes:
        ax.set_xlim(-lim * 1.05, lim * 1.05)
    hs = [Line2D([], [], color=COL[g[0]], marker=STYLE[int(g[1:])]["marker"], ls="none", ms=5.5) for g in GROUPS]
    hs += [Line2D([], [], color=INK2, marker="o", ls="none", ms=5.5, mfc="white", mew=1.4)]
    fig.legend(hs, [LABEL[g] for g in GROUPS] + ["åpen markør = ikke signifikant (p ≥ 0,05)"],
               loc="lower center", ncol=5, bbox_to_anchor=(0.5, -0.01))
    top = desk.header(fig, "Trend 2012–2025 per øvelse og klasse: prosent bedre per tiår",
                      "Kvantilregresjon av log(resultat) på år. Positivt = bedre (raskere, lenger, høyere). "
                      "Kast og hekk: redskap/høyde konstant innen hver klasse.")
    fig.tight_layout(rect=(0, 0.05, 0.98, top))
    fig.savefig(FIG / "fig9_trendoversikt.png", dpi=300); plt.close(fig)
    logger.info("lagret fig9_trendoversikt.png")


def main():
    d = desk.load()
    rows = [r for r in (trend_serie(d, *s) for s in serier()) if r]
    t = pd.DataFrame(rows)
    t["ovelsesgruppe"] = t.ovelse.map(gruppe_av)
    t["kjonn"] = t.gruppe.str[0]; t["klasse"] = t.gruppe.str[1:].astype(int)
    t.round(3).to_csv(TAB / "trender_per_serie.csv", index=False)
    oppsummer(t, "ovelsesgruppe").round(3).to_csv(TAB / "trender_per_gruppe.csv", index=False)
    pd.concat([oppsummer(t, "gruppe"), oppsummer(t, "kjonn"), oppsummer(t, "klasse")]) \
        .round(3).to_csv(TAB / "trender_per_klasse.csv", index=False)
    tot = oppsummer(t.assign(alle="alle"), "alle").round(2)
    logger.info(f"{len(t)} serier estimert\n" + tot.T.to_string())
    fig_trendoversikt(t)
    logger.info("ferdig")


if __name__ == "__main__":
    main()
