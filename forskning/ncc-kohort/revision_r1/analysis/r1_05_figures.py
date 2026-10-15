"""
r1_05_figures.py — Figures for the revised submission.

  * Figures 2, 3, S2, S3: redrawn from the corrected data (r1_00) with the code of the original
    pipeline (data/12 polish_figure_1 for Figure 2; data/08 kaplan_meier_plots for 3, S2, S3);
    the annotations of Figure 2 are now computed instead of typed in, and its in-figure title no
    longer says that divergence emerges at the milestone (the groups already differ at 13-14).
  * Figure 1 (conceptual model): SDT box replaced by Kretchmar (cited in the text); a dashed box
    adds the other reasons for competing less (reviewer comment 12).
  * Figure S0 (flow diagram): all counts computed from the corrected data, including the exclusions.
  * Figure S1 (calibration): now the cross-validated calibration of the primary model, drawn by r1_03
    (the original was the apparent fit of a post-baseline logistic model, mislabelled as Cox).
  * Figure S4 (time-varying hazard ratios): now drawn from the re-run table
    (tableS8_time_varying.csv) instead of hard-coded values.
  * Figure S5 (within-athlete event study): new, produced by r1_03.
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from lifelines import KaplanMeierFitter  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

HERE = Path(__file__).parent
R1 = HERE.parent
sys.path.insert(0, str(HERE))
from r1_paths import CDATA, PRIV  # noqa: E402

FIG = R1 / "figures"
RERUN = R1 / "tables" / "rerun"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5, "axes.titlesize": 10, "axes.labelsize": 9.5})


def conceptual_model():
    """Figure 1, as submitted except: the SDT box (a framework not used or cited in the text)
    is replaced by Kretchmar's meaning-in-movement account (cited in Section 1.1), the
    centre box is labelled a behavioral marker of (not a measure of) disengagement, and a dashed
    box shows that competing less can have other reasons (reviewer comment 12)."""
    fig, ax = plt.subplots(figsize=(8, 5.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.5, 6)
    ax.axis("off")
    ax.text(5, 5.7, "A behavioral-marker model of youth-sport disengagement", fontsize=11, fontweight="bold", ha="center")

    def box(x, y, w, h, text, color, fontsize=9, fc="white", ls="-"):
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.05", linewidth=1.4,
                                    edgecolor=color, facecolor=fc, alpha=0.95, linestyle=ls))
        ax.text(x, y, text, ha="center", va="center", fontsize=fontsize)

    ax.text(1.5, 4.85, "Theoretical mechanisms\n(not directly observed)", fontsize=8.5, ha="center", style="italic", color="#555555")
    box(1.5, 4.0, 2.5, 0.55, "Engagement balance\n(Scanlan SCM)", "#1976D2", 8.5)
    box(1.5, 3.2, 2.5, 0.55, "Meaning in movement\n(Kretchmar)", "#1976D2", 8.5)
    box(1.5, 2.4, 2.5, 0.55, "Role-exit deliberation\n(Ebaugh; Eliasson)", "#1976D2", 8.5)
    ax.text(5, 4.85, "Observable behavioral marker\n(this study)", fontsize=8.5, ha="center", style="italic", color="#555555")
    box(5, 3.2, 2.5, 1.5, "Annual competition\nvolume\n\n(meets per year,\nages 13–18)", "#2E7D32", 9.5, fc="#E8F5E9")
    ax.text(8.5, 4.85, "Outcome\n(this study)", fontsize=8.5, ha="center", style="italic", color="#555555")
    box(8.5, 3.2, 2.5, 1.5, "Active senior\nretention\n\n(≥ 2 results in\nany year, age ≥ 20)", "#C62828", 9.5, fc="#FFEBEE")
    ax.annotate("", xy=(3.7, 3.2), xytext=(2.85, 3.2), arrowprops=dict(arrowstyle="->", color="#888", lw=1.4))
    ax.annotate("", xy=(7.15, 3.2), xytext=(6.3, 3.2), arrowprops=dict(arrowstyle="->", color="#888", lw=1.4))
    ax.text(3.3, 3.4, "produces\nfootprint in", fontsize=7.5, ha="center", color="#555")
    ax.text(6.75, 3.4, "precedes", fontsize=7.5, ha="center", color="#555")
    box(1.5, 1.35, 2.5, 0.55, "Other reasons for competing less\n(injury, another sport, school)", "#9E9E9E", 8,
        fc="#FAFAFA", ls="--")
    ax.annotate("", xy=(3.72, 2.52), xytext=(2.85, 1.55),
                arrowprops=dict(arrowstyle="->", color="#9E9E9E", lw=1.2, linestyle="--"))
    ax.text(5, 0.2, "Prediction: future retainers and future dropouts should differ in measurable competition behavior\n"
            "before formal exit, with divergence intensifying at qualification-milestone years (age 15–16).",
            fontsize=8.5, ha="center", style="italic",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#FAFAFA", edgecolor="#BDBDBD"))
    fig.tight_layout()
    fig.savefig(FIG / "fig1_conceptual_model.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def load():
    df = pd.read_csv(CDATA / "analysedata_utvidet.csv", low_memory=False)
    return df.merge(pd.read_csv(PRIV / "r1_variables.csv"), on="athlete_id", how="left")


def volume_trajectory(df):
    """Figure 2: data/12 polish_figure_1 on the corrected data; annotation values computed."""
    ages = [13, 14, 15, 16, 17, 18]
    cols = [f"vol_age_{a}" for a in ages]
    med = df.groupby("aktiv_senior")[cols].median()
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    for retainer, color, label, marker in [(1, "#1B5E20", "Senior retainers (active ≥ age 20)", "o"),
                                           (0, "#B71C1C", "Future dropouts (last active < age 20)", "s")]:
        sub = df[df["aktiv_senior"] == retainer]
        ax.plot(ages, [sub[c].median() for c in cols], marker=marker, color=color, linewidth=2.5, markersize=8,
                label=f"{label} (n = {len(sub):,})", zorder=3)
        ax.fill_between(ages, [sub[c].quantile(0.25) for c in cols], [sub[c].quantile(0.75) for c in cols],
                        color=color, alpha=0.13, zorder=1)
    ax.axvspan(14.5, 16.5, color="gray", alpha=0.08, zorder=0)
    ax.axvline(15, color="#424242", linestyle="--", alpha=0.6, linewidth=1, zorder=2)
    ax.annotate("Qualification\nmilestone\n(UM, age 15–16)", xy=(15.4, 28), xytext=(17.6, 27), fontsize=8.5,
                color="#424242", ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color="#424242", alpha=0.5, lw=0.8))
    d14, d16 = med.loc[0, "vol_age_14"], med.loc[0, "vol_age_16"]
    r13, r15 = med.loc[1, "vol_age_13"], med.loc[1, "vol_age_15"]
    ax.annotate(f"Future dropouts\ncollapse: {d14:g} → {d16:g} meets", xy=(15.3, 3), xytext=(16.0, 11), fontsize=8.5,
                color="#B71C1C", ha="left", va="center", arrowprops=dict(arrowstyle="->", color="#B71C1C", alpha=0.7, lw=0.9))
    ax.annotate(f"Retainers expand:\n{r13:g} → {r15:g} meets", xy=(15, 19), xytext=(12.8, 23.5), fontsize=8.5,
                color="#1B5E20", ha="left", va="center", arrowprops=dict(arrowstyle="->", color="#1B5E20", alpha=0.7, lw=0.9))
    ax.set_xlim(12.5, 19.0)
    ax.set_ylim(0, 30)
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Competition days per year (median; IQR shaded)")
    ax.set_title("Competition volume by age and senior-retention status")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, fontsize=8.5, frameon=False)
    ax.grid(alpha=0.25)
    ax.set_xticks(ages)
    fig.tight_layout()
    fig.savefig(FIG / "fig2_volume_trajectory.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return med


def km_figures(df):
    """Figures 3, S2, S3: data/08 kaplan_meier_plots on the corrected data (same specification)."""
    d = df.copy()
    d["event"] = (d["aktiv_naa"] == 0).astype(int)
    d["duration_age"] = (d["alder_ved_slutt"] - (d["stevne_aar"] - d["birth_year"])).clip(lower=0.5)
    kmf = KaplanMeierFitter()
    out = {}
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    kmf.fit(d["duration_age"], d["event"], label="All athletes")
    kmf.plot_survival_function(ax=axes[0], ci_show=True)
    axes[0].set_title("A. Overall retention")
    axes[0].set_xlabel("Years since baseline (age 13/14)")
    for sex, label, ls in [("M", "Male", "-"), ("F", "Female", "--")]:
        sub = d[d["gender"] == sex]
        kmf.fit(sub["duration_age"], sub["event"], label=label)
        kmf.plot_survival_function(ax=axes[1], ci_show=False, linestyle=ls)
    axes[1].set_title("B. By sex")
    axes[1].set_xlabel("Years since baseline")
    axes[1].legend(loc="upper right", fontsize=8)
    for a in axes:
        a.set_ylabel("Proportion still active")
        a.set_ylim(0, 1)
        a.set_xlim(0, 14)
        a.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "figS2_km_overall_sex.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    bins = [-0.5, 0.5, 5.5, 15.5, 30.5, np.inf]
    labels = ["0 (none)", "1-5 (very low)", "6-15 (moderate)", "16-30 (high)", "31+ (very high)"]
    d["vol_q"] = pd.cut(d["vol_milepael"], bins=bins, labels=labels)
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    colors = plt.cm.viridis(np.linspace(0.1, 0.9, 5))
    for i, q in enumerate(labels):
        sub = d[d["vol_q"] == q]
        kmf.fit(sub["duration_age"], sub["event"], label=f"{q} (n={len(sub)})")
        kmf.plot_survival_function(ax=ax, ci_show=False, color=colors[i])
        out[q] = dict(n=len(sub), s14=float(kmf.survival_function_at_times(14).iloc[0]),
                      senior=float(sub["aktiv_senior"].mean()))
    ax.set_title("Retention by competition volume at ages 15–16")
    ax.set_xlabel("Years since baseline (age 13/14)")
    ax.set_ylabel("Proportion still active")
    ax.set_ylim(0, 1)
    ax.set_xlim(0, 14)
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "fig3_km_vol_quintile.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4.5))
    for n_typer, color in zip([0, 1, 2, 3, 4], plt.cm.plasma(np.linspace(0.1, 0.9, 5))):
        sub = d[d["n_msk_typer"] == n_typer]
        if len(sub) < 10:
            continue
        kmf.fit(sub["duration_age"], sub["event"], label=f"{n_typer} type{'' if n_typer == 1 else 's'} (n={len(sub)})")
        kmf.plot_survival_function(ax=ax, ci_show=False, color=color)
    ax.set_title("Retention by number of championship types (pre-age 17)")
    ax.set_xlabel("Years since baseline (age 13/14)")
    ax.set_ylabel("Proportion still active")
    ax.set_ylim(0, 1)
    ax.set_xlim(0, 14)
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "figS3_km_msk_typer.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out


def flow_diagram(df, n_participants):
    fig, ax = plt.subplots(figsize=(10, 9.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    def box(x, y, w, h, text, color, fc="white", fontsize=9):
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.05",
                                    linewidth=1.4, edgecolor=color, facecolor=fc))
        ax.text(x, y, text, ha="center", va="center", fontsize=fontsize)

    def arrow(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", color="#424242", lw=1.2))

    n = len(df)
    sex = df["gender"].value_counts()
    n_unknown = int(df["gender"].isna().sum())
    a, b = int((df["birth_year"] <= 2000).sum()), int((df["birth_year"] >= 2001).sum())
    n_ret = int(df["aktiv_senior"].sum())
    cc = df[df["gender"].notna() & df["tyrving_best_r1"].notna()]
    n_tyr_missing = int(df["gender"].notna().sum() - len(cc))
    fu = {c: (2025 - df.loc[m, "stevne_aar"].max(), 2025 - df.loc[m, "stevne_aar"].min())
          for c, m in [("A", df["birth_year"] <= 2000), ("B", df["birth_year"] >= 2001)]}
    n_both = int(df["deltok_begge_aar"].fillna(0).astype(int).sum())
    box(3, 9.3, 5.5, 0.7, f"Athletes aged 13–14 with a result at the regional 13–14 meet, 2011–2016\n"
        f"(three venues; identified by venue and date): N = {n_participants:,}", "#1565C0", "#E3F2FD")
    arrow(3, 8.9, 3, 8.35)
    box(3, 8.0, 5.5, 0.6, "Restrict birth years to 1998–2002", "#1565C0", "#E3F2FD")
    arrow(5.8, 8.0, 6.2, 8.0)
    box(8.0, 8.0, 3.5, 0.6, f"Excluded: born 1997 or 2003\n(only one eligible edition): n = {n_participants - n:,}",
        "#C62828", "#FFEBEE", fontsize=8.5)
    arrow(3, 7.65, 3, 7.1)
    box(3, 6.75, 5.5, 0.6, f"De-duplicate athletes in both a 13- and a 14-year-old edition\n"
        f"(n = {n_both:,}; earlier edition = baseline)", "#1565C0", "#E3F2FD")
    arrow(3, 6.4, 3, 5.85)
    box(3, 5.5, 5.5, 0.6, f"Total cohort: N = {n:,} ({sex.get('M', 0):,} male, {sex.get('F', 0):,} female, "
        f"{n_unknown} sex not registered)", "#2E7D32", "#E8F5E9", fontsize=9.5)
    arrow(2.0, 5.15, 1.6, 4.65)
    arrow(4.0, 5.15, 4.4, 4.65)
    box(1.6, 4.3, 2.6, 0.6, f"Cohort A (1998–2000)\nn = {a:,}", "#2E7D32", "#E8F5E9", fontsize=8.5)
    box(4.4, 4.3, 2.6, 0.6, f"Cohort B (2001–2002)\nn = {b:,}", "#2E7D32", "#E8F5E9", fontsize=8.5)
    box(3, 3.25, 5.5, 0.6, "Predictors observed at ages 13–14 only (primary analysis)", "#6A1B9A", "#F3E5F5", fontsize=8.5)
    arrow(3, 3.95, 3, 3.6)
    box(3, 2.0, 5.5, 0.7, "Outcome window: ages 20+ (follow-up through 2025)\nPrimary: ≥2 results in any senior-age year "
        f"(retainers: n = {n_ret}, {100 * n_ret / n:.1f}%)", "#C62828", "#FFEBEE", fontsize=8.5)
    arrow(3, 2.9, 3, 2.4)
    box(8.0, 3.6, 3.5, 0.7, f"Follow-up after baseline:\n{fu['A'][0]}–{fu['A'][1]} years (Cohort A)\n"
        f"{fu['B'][0]}–{fu['B'][1]} years (Cohort B)", "#757575", "#FAFAFA", fontsize=8.5)
    box(3, 0.6, 5.5, 0.75, f"Complete-case analysis: n = {len(cc):,}\n(excluded: {n_unknown} without registered sex; "
        f"{n_tyr_missing} further without a baseline Tyrving score)", "#757575", "#FAFAFA", fontsize=8.5)
    arrow(3, 1.6, 3, 1.0)
    fig.tight_layout()
    fig.savefig(FIG / "figS0_flow_diagram.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def forest_time_varying():
    t = pd.read_csv(RERUN / "tableS8_time_varying.csv")
    names = {"vol_milepael_z": "Volume at ages 15–16 (per SD)", "n_msk_typer": "Championship types (per type)",
             "tyrving_best_z": "Tyrving (per SD)", "hhi_early_z": "HHI, ages 13–14 (per SD)", "female": "Female"}
    periods = list(dict.fromkeys(t["Period"]))
    # ages as in Table 5 (baseline at 13 or 14, so years 3-6 span ages 16-20; the script's label says 16-19)
    labels = {p: p.replace("16-19", "16-20").replace("-", "–").replace("age ", "approx. ages ") for p in periods}
    colors = dict(zip(periods, ["#2a78d6", "#eb6834", "#898781"]))
    offset = dict(zip(periods, [0.22, 0.0, -0.22]))
    covs = list(names)
    fig, ax = plt.subplots(figsize=(7.8, 5.2))
    for i, c in enumerate(covs):
        for p in periods:
            r = t[(t["Covariate"] == c) & (t["Period"] == p)].iloc[0]
            y = len(covs) - i + offset[p]
            ax.plot([r["CI low"], r["CI high"]], [y, y], color=colors[p], lw=1.6)
            ax.plot(r["HR"], y, "o", color=colors[p], ms=6.5)
    ax.axvline(1.0, color="#52514e", ls="--", lw=0.9)
    ax.set_yticks(range(1, len(covs) + 1))
    ax.set_yticklabels([names[c] for c in covs][::-1])
    ax.set_xscale("log")
    ax.set_xticks([0.1, 0.2, 0.5, 1.0, 2.0])
    ax.set_xticklabels(["0.1", "0.2", "0.5", "1.0", "2.0"])
    ax.set_xlim(0.08, 2.2)
    ax.set_xlabel("Hazard ratio (log scale)")
    ax.grid(axis="x", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    handles = [plt.Line2D([0], [0], marker="o", color=colors[p], lw=1.6, ms=6.5, label=labels[p]) for p in periods]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=8.5, title="Follow-up window",
              title_fontsize=8.5, frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "figS4_time_varying_forest.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    df = load()
    med = volume_trajectory(df)
    km = km_figures(df)
    conceptual_model()
    summary = pd.read_csv(R1 / "audit" / "r1_00_summary.csv").set_index("Check")["Value"]
    flow_diagram(df, int(summary["participants aged 13-14 at the venue-days (any birth year)"]))
    forest_time_varying()
    print(med.to_string())
    print(pd.DataFrame(km).T.round(3).to_string())
    print(sorted(p.name for p in FIG.glob("*.png")))


if __name__ == "__main__":
    main()
