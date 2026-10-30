"""
08_r1_figurer_tabeller.py — A6: figurer og manustabeller for revisjon 1.

Alt bygges fra r1_*-filene (stevneklyngede KI; punktestimatene er identiske
med runde 1). Endringer mot 04/06: feilstolper i fig3/fig4 (R2-3), engelske
etiketter i fig5 (R3-m), tertiler på vindjustert sesongsnitt i fig4 (R2-6),
tabell 4 med observert og teoretisk asymmetriforhold (R1-3), tabell 6 fra
medvindsgrenen med poolet justert SD (R2-5), og nye S-tabeller: per sekund
løpstid, korreksjonstabell, kvadratisk form.
"""

import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
DATA = HERE / "data_private"
EST = HERE / "tables" / "estimering"
FIG = HERE / "figures"
TABM = HERE / "tables" / "manus"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

GRONN, ROD, GRAA, BLAA = "#1b6e1b", "#b22222", "#666666", "#1f4e79"
plt.rcParams.update({"figure.dpi": 300, "savefig.dpi": 300, "font.size": 11,
                     "axes.grid": True, "grid.alpha": 0.3, "axes.titlesize": 12})

SPRINT = ["60m", "80m", "100m", "150m", "200m"]
HOPPREKKE = ["lengde", "lengde_sone_05m", "tresteg", "tresteg_sone_05m"]
REKKE = SPRINT + HOPPREKKE
BANDREKKE = ["10-11", "12-13", "14-15", "16-17", "18-19", "20-34"]
NAVN = {"60m": "60 m", "80m": "80 m", "100m": "100 m", "150m": "150 m", "200m": "200 m",
        "lengde": "Long jump", "lengde_sone_05m": "Long jump (zone)",
        "tresteg": "Triple jump", "tresteg_sone_05m": "Triple jump (zone)"}
FARGER = {"60m": BLAA, "100m": GRONN, "200m": ROD,
          "lengde": "#6a3d9a", "lengde_sone_05m": GRAA, "tresteg": "#e6850e"}
STIL = {"lengde": ("s--", 1.8), "lengde_sone_05m": ("s--", 1.8), "tresteg": ("^--", 1.8)}
HEKKNAVN = {"60mh_68cm": "60 m hurdles 68 cm", "60mh_76_2cm": "60 m hurdles 76.2 cm",
            "80mh_76_2cm": "80 m hurdles 76.2 cm", "80mh_84cm": "80 m hurdles 84 cm",
            "100mh_76_2cm": "100 m hurdles 76.2 cm", "100mh_84cm": "100 m hurdles 84 cm",
            "100mh_91_4cm": "100 m hurdles 91.4 cm", "110mh_91_4cm": "110 m hurdles 91.4 cm",
            "110mh_100cm": "110 m hurdles 100 cm", "110mh_106_7cm": "110 m hurdles 106.7 cm"}


def fmt(g, lo, hi, des=3):
    return f"{g:.{des}f} ({lo:.{des}f}–{hi:.{des}f})"


def alder_panel(a, koder, enhet, tittel, fil, ylab):
    fig, akser = plt.subplots(1, 2, figsize=(11.5, 5.0), sharey=False)
    x = np.arange(len(BANDREKKE))
    for ax, kj, kjnavn in [(akser[0], "M", "Boys/men"), (akser[1], "F", "Girls/women")]:
        for kode in koder:
            g = a[(a["event"] == kode) & (a["kjonn"] == kj) & (a["enhet"] == enhet)]
            g = g.set_index("aldersband").reindex(BANDREKKE).reset_index()
            ax.errorbar(x, g["gevinst_per_ms"],
                        yerr=[g["gevinst_per_ms"] - g["ki_lav"],
                              g["ki_hoy"] - g["gevinst_per_ms"]],
                        fmt=STIL.get(kode, ("o-", 2.2))[0], lw=STIL.get(kode, ("o-", 2.2))[1], ms=6,
                        capsize=3, color=FARGER.get(kode, GRAA), label=NAVN[kode])
        ax.axhline(0, color=GRAA, lw=1, ls="--")
        ax.set_xticks(x, BANDREKKE)
        ax.set_xlabel("Age band")
        ax.set_title(kjnavn)
        ax.set_ylabel(ylab)
    handles, labels = akser[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=len(labels), frameon=False, fontsize=9.5,
               bbox_to_anchor=(0.5, -0.02))
    fig.suptitle(tittel, fontsize=13)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(FIG / fil, bbox_inches="tight")
    plt.close(fig)


def fig3_asym(a):
    spr = [k for k in ["60m", "100m", "200m"] if k in set(a["event"])]
    hop = [k for k in ["lengde", "lengde_sone_05m", "tresteg"] if k in set(a["event"])]
    fig, akser = plt.subplots(1, 2, figsize=(11.2, 4.9))
    for ax, koder, enhet in [(akser[0], spr, "Seconds per m/s"),
                             (akser[1], hop, "Centimetres per m/s")]:
        x = np.arange(len(koder))
        t = a.set_index("event").loc[koder]
        for off, kol, farge, lab in [(-0.18, "medvind", GRONN, "Gain per +1 m/s tailwind"),
                                     (0.18, "motvind", ROD, "Loss per −1 m/s headwind")]:
            v = t[kol].to_numpy()
            lo = t[f"{kol}_ki_lav"].to_numpy()
            hi = t[f"{kol}_ki_hoy"].to_numpy()
            ax.bar(x + off, v, width=0.36, color=farge, label=lab,
                   yerr=[v - lo, hi - v], capsize=3,
                   error_kw={"ecolor": "#333333", "lw": 1.2})
            if enhet.startswith("Seconds"):
                ax.scatter(x + off, t[f"drag_{kol}"].to_numpy(), marker="D", s=46, color="black",
                           zorder=5, label="Drag-only prediction" if kol == "medvind" else None)
        ax.set_xticks(x, [NAVN[k] for k in koder])
        ax.set_ylabel(enhet)
        ax.axhline(0, color=GRAA, lw=0.8)
    akser[0].set_title("Sprints: observed slopes and drag-only prediction")
    akser[1].set_title("Horizontal jumps")
    akser[0].legend(frameon=False, fontsize=9)
    fig.suptitle("Asymmetry of the wind effect (within athlete × season; "
                 "95% CI, meet-clustered)", fontsize=13)
    fig.tight_layout()
    fig.savefig(FIG / "fig3_asymmetry.png", bbox_inches="tight")
    plt.close(fig)


def fig4_niva(n):
    spr = [k for k in ["60m", "100m", "200m"] if k in set(n["event"])]
    hop = [k for k in ["lengde", "tresteg"] if k in set(n["event"])]
    farger = {"lav": ROD, "midt": GRAA, "hoy": GRONN}
    navn_t = {"lav": "Lowest ability tertile", "midt": "Middle", "hoy": "Highest"}
    fig, akser = plt.subplots(1, 2, figsize=(11.2, 4.9))
    for ax, koder, enhet in [(akser[0], spr, "Seconds per m/s"),
                             (akser[1], hop, "Centimetres per m/s")]:
        x = np.arange(len(koder))
        for i, tert in enumerate(["lav", "midt", "hoy"]):
            v, lo, hi = [], [], []
            for k in koder:
                t = n[(n["event"] == k) & (n["tertil"] == tert)]
                v.append(t["gevinst_per_ms"].iloc[0] if len(t) else np.nan)
                lo.append(t["ki_lav"].iloc[0] if len(t) else np.nan)
                hi.append(t["ki_hoy"].iloc[0] if len(t) else np.nan)
            v, lo, hi = map(np.array, (v, lo, hi))
            ax.bar(x + (i - 1) * 0.26, v, width=0.26, color=farger[tert],
                   label=navn_t[tert], yerr=[v - lo, hi - v], capsize=3,
                   error_kw={"ecolor": "#333333", "lw": 1.2})
        ax.set_xticks(x, [NAVN[k] for k in koder])
        ax.set_ylabel(enhet)
    akser[0].set_title("Sprints: weaker athletes gain more per m/s")
    akser[1].set_title("Horizontal jumps")
    akser[0].legend(frameon=False, fontsize=9)
    fig.suptitle("Wind effect by wind-adjusted ability tertile "
                 "(95% CI, meet-clustered)", fontsize=13)
    fig.tight_layout()
    fig.savefig(FIG / "fig4_level.png", bbox_inches="tight")
    plt.close(fig)


def fig5_hekk(hk):
    p = hk[hk["kjonn"] == "begge"].copy()
    rekkef = [k for k in HEKKNAVN if k in set(p["kode"])]
    p = p.set_index("kode").loc[rekkef].reset_index()
    yposs = np.arange(len(p))[::-1]
    fig, ax = plt.subplots(figsize=(9.0, 6.0))
    ax.errorbar(p["gevinst_s_per_ms"], yposs,
                xerr=[p["gevinst_s_per_ms"] - p["ki_lav"],
                      p["ki_hoy"] - p["gevinst_s_per_ms"]],
                fmt="o", color=BLAA, ms=7, capsize=3, lw=1.8,
                label="Short hurdles (within athlete × season; 95% CI, meet-clustered)")
    refs = hk[(hk["kjonn"] != "begge") & hk["flat_ref"].notna()]
    for _, t in refs.iterrows():
        if t["kode"] in rekkef:
            yp = yposs[rekkef.index(t["kode"])]
            ax.plot(float(t["flat_ref"]), yp, marker="D", ms=6,
                    color=GRONN if t["kjonn"] == "M" else ROD,
                    linestyle="none", alpha=0.85)
    ax.plot([], [], marker="D", color=GRONN, linestyle="none",
            label="Flat sprint reference, boys/men (same distance class, own modal age band)")
    ax.plot([], [], marker="D", color=ROD, linestyle="none",
            label="Flat sprint reference, girls/women")
    etiketter = [f"{HEKKNAVN[k]}  ({p.set_index('kode').loc[k, 'modal_aldersband']})"
                 for k in rekkef]
    ax.set_yticks(yposs, etiketter, fontsize=9)
    ax.axvline(0, color=GRAA, lw=1, ls="--")
    ax.set_xlabel("Effect per m/s of wind (s; linear fit over head- and tailwinds)")
    ax.set_title("Wind effect in short hurdles, by class-specific event code")
    ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG / "fig5_hurdles.png", bbox_inches="tight")
    plt.close(fig)


def main():
    a = pd.read_csv(EST / "r1_alder_meet.csv")
    hoved = pd.read_csv(EST / "r1_hoved_meet.csv")
    asym = pd.read_csv(EST / "r1_asym_meet.csv")
    tert = pd.read_csv(EST / "r1_tertil_adj.csv")
    vindu = pd.read_csv(EST / "r1_vindu_medvind.csv")
    hk = pd.read_csv(EST / "r1_hekk_meet.csv")

    # ---- Figurer -------------------------------------------------------------------------
    alder_panel(a, ["60m", "100m", "200m"], "s",
                "Effect per m/s of wind by age (linear fit): sprints (seconds; within athlete × season)",
                "fig1_effect_by_age.png", "Seconds per m/s")
    alder_panel(a, ["60m", "100m", "200m", "lengde", "tresteg"], "%",
                "Effect per m/s of wind by age (linear fit): percent of performance",
                "fig2_effect_by_age_pct.png", "Percent per m/s")
    fig3_asym(asym)
    fig4_niva(tert)
    fig5_hekk(hk)
    logger.info("fig1–fig5 regenerert med stevneklyngede KI")

    # ---- Tabell 2: hovedeffekter ---------------------------------------------------------
    rader = []
    for kode in REKKE:
        nat = hoved[(hoved["analyse"] == "hoved_meet") & (hoved["event"] == kode)]
        pst = hoved[(hoved["analyse"] == "hoved_meet_pst") & (hoved["event"] == kode)]
        if not len(nat):
            continue
        t, p = nat.iloc[0], pst.iloc[0]
        rader.append({"Event": NAVN[kode], "Unit": t["enhet"],
                      "Per m/s, linear (95% CI)": fmt(t["gevinst_per_ms"],
                                                      t["ki_lav"], t["ki_hoy"]),
                      "Percent per m/s (95% CI)": fmt(p["gevinst_per_ms"], p["ki_lav"],
                                                      p["ki_hoy"]),
                      "n": f"{t['n']:,}", "Athlete-seasons": f"{t['celler']:,}"})
    pd.DataFrame(rader).to_csv(TABM / "table2_main.csv", index=False)

    # ---- Tabell 3: alder x kjønn, sprint -------------------------------------------------
    rader = []
    for kode in ["60m", "100m", "200m"]:
        for kj in ["M", "F"]:
            rad = {"Event": NAVN[kode], "Sex": "Boys/men" if kj == "M" else "Girls/women"}
            for b in BANDREKKE:
                t = a[(a["event"] == kode) & (a["kjonn"] == kj)
                      & (a["aldersband"] == b) & (a["enhet"] == "s")]
                rad[b] = fmt(*t.iloc[0][["gevinst_per_ms", "ki_lav", "ki_hoy"]]) if len(t) else "—"
            rader.append(rad)
    pd.DataFrame(rader).to_csv(TABM / "table3_age_sprints.csv", index=False)

    # ---- Tabell S1: hopp etter alder -----------------------------------------------------
    rader = []
    for kode in ["lengde", "lengde_sone_05m", "tresteg"]:
        for enh in ["cm", "%"]:
            rad = {"Event": NAVN[kode], "Unit": enh}
            for b in BANDREKKE:
                t = a[(a["event"] == kode) & (a["aldersband"] == b) & (a["enhet"] == enh)]
                if len(t) == 2:
                    t = t.sort_values("kjonn")
                rad[b] = " / ".join(fmt(*x[["gevinst_per_ms", "ki_lav", "ki_hoy"]], des=2)
                                    for _, x in t.iterrows()) if len(t) else "—"
            rader.append(rad)
    pd.DataFrame(rader).to_csv(TABM / "tableS_jumps_age.csv", index=False)

    # ---- Tabell 4: asymmetri med teoretisk forhold ---------------------------------------
    t4 = asym.copy()
    t4["Event"] = t4["event"].map(NAVN)
    t4["Unit"] = t4["event"].map(lambda k: "s" if k in SPRINT else "cm")
    t4["Tailwind gain per +1 m/s (95% CI)"] = t4.apply(
        lambda t: fmt(t["medvind"], t["medvind_ki_lav"], t["medvind_ki_hoy"]), axis=1)
    t4["Headwind loss per −1 m/s (95% CI)"] = t4.apply(
        lambda t: fmt(t["motvind"], t["motvind_ki_lav"], t["motvind_ki_hoy"]), axis=1)
    t4["ratio_obs"] = t4["ratio_obs"].map(lambda x: f"{x:.2f}")
    t4["ratio_drag_estimator"] = t4["ratio_drag_estimator"].map(
        lambda x: "—" if pd.isna(x) else f"{x:.2f}")
    t4["p_lik_meet"] = t4["p_lik_meet"].map(lambda p: "<0.001" if p < 0.001 else f"{p:.3f}")
    t4 = t4.set_index("event").loc[[k for k in REKKE if k in set(t4["event"])]].reset_index()
    (t4[["Event", "Unit", "Tailwind gain per +1 m/s (95% CI)",
         "Headwind loss per −1 m/s (95% CI)", "ratio_obs", "ratio_drag_estimator",
         "p_lik_meet", "n"]]
     .rename(columns={"ratio_obs": "Ratio head/tail", "ratio_drag_estimator":
                      "Drag-only ratio (same estimator)", "p_lik_meet": "p equal slopes"})
     .to_csv(TABM / "table4_asymmetry.csv", index=False))

    # ---- Tabell 5: hekk ------------------------------------------------------------------
    t5 = hk[hk["kjonn"] != "begge"].copy()
    t5["_rekke"] = t5["kode"].map({k: i for i, k in enumerate(HEKKNAVN)})
    t5 = t5.sort_values(["_rekke", "kjonn"], ascending=[True, False])
    t5["Event (hurdle height)"] = t5["kode"].map(HEKKNAVN)
    t5["Sex"] = t5["kjonn"].map({"M": "Boys/men", "F": "Girls/women"})
    t5["Gain per +1 m/s (95% CI), s"] = t5.apply(
        lambda t: fmt(t["gevinst_s_per_ms"], t["ki_lav"], t["ki_hoy"]), axis=1)
    t5["Flat sprint reference (95% CI), s"] = t5.apply(
        lambda t: "—" if pd.isna(t["flat_ref"])
        else fmt(t["flat_ref"], t["flat_ref_ki_lav"], t["flat_ref_ki_hoy"]), axis=1)
    (t5[["Event (hurdle height)", "Sex", "modal_aldersband",
         "Gain per +1 m/s (95% CI), s", "Flat sprint reference (95% CI), s", "n", "celler"]]
     .rename(columns={"modal_aldersband": "Modal age band", "celler": "Athlete-seasons"})
     .to_csv(TABM / "table5_hurdles.csv", index=False))

    # ---- Tabell 6: +2,0-fordelen fra medvindsgrenen --------------------------------------
    rader = []
    for kode in ["60m", "100m", "200m"]:
        for kj in ["M", "F"]:
            rad = {"Event": NAVN[kode], "Sex": "Boys/men" if kj == "M" else "Girls/women"}
            for b in BANDREKKE:
                t = vindu[(vindu["event"] == kode) & (vindu["kjonn"] == kj)
                          & (vindu["aldersband"] == b)]
                rad[b] = (f"{t['fordel_0_2_s'].iloc[0]:.2f} s "
                          f"({t['fordel_0_2_i_robust_skala'].iloc[0]:.2f})" if len(t) else "—")
            rader.append(rad)
    pd.DataFrame(rader).to_csv(TABM / "table6_advantage_sd.csv", index=False)

    # ---- Tabell S2: robusthet (+ uten vindu rundt 2,0) -----------------------------------
    rob = pd.read_csv(EST / "robusthet.csv")
    uten2 = pd.read_csv(EST / "r1_uten_2.csv").assign(analyse="uten_2.0_pm0.2")
    rob = pd.concat([rob, uten2[["analyse", "event", "gevinst_per_ms"]]])
    piv = rob.pivot_table(index="event", columns="analyse", values="gevinst_per_ms")
    rekke = [k for k in REKKE if k in piv.index]
    piv = piv.loc[rekke].round(4)
    piv.index = [NAVN[k] for k in piv.index]
    piv.to_csv(TABM / "tableS_robustness.csv")

    # ---- Tabell S3: korreksjonstabell (vindgren per gruppe) ------------------------------
    rader = []
    for _, t in vindu.iterrows():
        rader.append({"Event": NAVN[t["event"]],
                      "Sex": "Boys/men" if t["kjonn"] == "M" else "Girls/women",
                      "Age band": t["aldersband"],
                      "Tailwind slope, s per +1 m/s (95% CI)":
                          fmt(t["medvind_s_per_ms"], t["medvind_ki_lav"], t["medvind_ki_hoy"]),
                      "Headwind slope, s per −1 m/s (95% CI)":
                          fmt(t["motvind_s_per_ms"], t["motvind_ki_lav"], t["motvind_ki_hoy"]),
                      "n": f"{t['n']:,}"})
    for _, t in asym[~asym["event"].isin(SPRINT)].iterrows():
        rader.append({"Event": NAVN[t["event"]], "Sex": "Both", "Age band": "all",
                      "Tailwind slope, s per +1 m/s (95% CI)":
                          fmt(t["medvind"], t["medvind_ki_lav"], t["medvind_ki_hoy"], des=2)
                          + " cm",
                      "Headwind slope, s per −1 m/s (95% CI)":
                          fmt(t["motvind"], t["motvind_ki_lav"], t["motvind_ki_hoy"], des=2)
                          + " cm",
                      "n": f"{t['n']:,}"})
    pd.DataFrame(rader).to_csv(TABM / "tableS_correction.csv", index=False)

    # ---- Tabell S4: effekt per sekund løpstid --------------------------------------------
    pdur = pd.read_csv(EST / "r1_per_sekund.csv")
    pdur = pdur.set_index("event").loc[[k for k in SPRINT if k in set(pdur["event"])]].reset_index()
    pdur["Event"] = pdur["event"].map(NAVN)
    flat = pdur[["Event", "snitt_tid_s", "gevinst_per_ms", "per_sekund"]]
    hkb = hk[hk["kjonn"] == "begge"].copy()
    hkb = hkb.set_index("kode").loc[[k for k in HEKKNAVN if k in set(hkb["kode"])]].reset_index()
    hkb["Event"] = hkb["kode"].map(HEKKNAVN)
    hkb = hkb.rename(columns={"gevinst_s_per_ms": "gevinst_per_ms"})[
        ["Event", "snitt_tid_s", "gevinst_per_ms", "per_sekund"]]
    s4 = pd.concat([flat, hkb])
    s4["snitt_tid_s"] = s4["snitt_tid_s"].map(lambda x: f"{x:.2f}")
    s4["gevinst_per_ms"] = s4["gevinst_per_ms"].map(lambda x: f"{x:.3f}")
    s4["per_sekund"] = s4["per_sekund"].map(lambda x: f"{x:.5f}")
    (s4
     .rename(columns={"snitt_tid_s": "Mean time, s",
                      "gevinst_per_ms": "Gain per +1 m/s, s",
                      "per_sekund": "Gain per +1 m/s per second of race time"})
     .to_csv(TABM / "tableS_perduration.csv", index=False))

    # ---- Tabell S5: kvadratisk form ------------------------------------------------------
    kv = pd.read_csv(EST / "r1_kvad_meet.csv")
    kv["Event"] = kv["event"].map(NAVN)
    kv["Linear term (SE)"] = kv.apply(lambda t: f"{t['beta_lin']:.4f} ({t['se_lin']:.4f})",
                                      axis=1)
    kv["Quadratic term (SE)"] = kv.apply(lambda t: f"{t['beta_kvad']:.4f} ({t['se_kvad']:.4f})",
                                         axis=1)
    kv[["Event", "Linear term (SE)", "Quadratic term (SE)", "n"]].to_csv(
        TABM / "tableS_quadratic.csv", index=False)

    logger.info(f"manustabeller skrevet til {TABM}/")


if __name__ == "__main__":
    main()
