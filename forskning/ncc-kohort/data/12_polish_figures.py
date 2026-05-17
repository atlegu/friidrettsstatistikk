"""
Steg 12: Polerer Figur 1 + lager ny konseptuell modell-figur (Figur 2)
       + lager forest plot for time-varying HR (Figur 5, erstatter Table 5).
"""

import logging
import warnings
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as mpatches

warnings.filterwarnings("ignore", category=FutureWarning)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent
ANALYSE_FILE = DATA_DIR / "analysedata_utvidet.csv"
FIG_DIR = DATA_DIR.parent / "submission_pse" / "figures"

mpl.rcParams["figure.dpi"] = 150
mpl.rcParams["savefig.dpi"] = 150
mpl.rcParams["savefig.bbox"] = "tight"
mpl.rcParams["font.family"] = "DejaVu Sans"
mpl.rcParams["font.size"] = 9.5
mpl.rcParams["axes.titlesize"] = 10
mpl.rcParams["axes.labelsize"] = 9.5


# =============================================================================
# Figure 1 — POLISHED: trajectory divergence
# =============================================================================

def polish_figure_1():
    logger.info("Building polished Figure 1...")
    df = pd.read_csv(ANALYSE_FILE)
    df["retainer"] = df["aktiv_senior"]

    ages = [13, 14, 15, 16, 17, 18]
    vol_cols = [f"vol_age_{a}" for a in ages]

    fig, ax = plt.subplots(figsize=(7.5, 4.8))

    # Plot trajectories
    for retainer, color, label, marker in [
        (1, "#1B5E20", "Senior retainers (active ≥ age 20)", "o"),
        (0, "#B71C1C", "Future dropouts (last active < age 20)", "s"),
    ]:
        sub = df[df["retainer"] == retainer]
        n = len(sub)
        medians = [sub[c].median() for c in vol_cols]
        q25 = [sub[c].quantile(0.25) for c in vol_cols]
        q75 = [sub[c].quantile(0.75) for c in vol_cols]
        ax.plot(ages, medians, marker=marker, color=color, linewidth=2.5,
                markersize=8, label=f"{label} (n = {n})", zorder=3)
        ax.fill_between(ages, q25, q75, color=color, alpha=0.13, zorder=1)

    # Highlight divergence area with vertical band
    ax.axvspan(14.5, 16.5, color="gray", alpha=0.08, zorder=0)

    # Milestone marker
    ax.axvline(15, color="#424242", linestyle="--", alpha=0.6, linewidth=1, zorder=2)
    ax.annotate(
        "Qualification\nmilestone\n(UM, age 15–16)",
        xy=(15.4, 28),
        xytext=(17.6, 27),
        fontsize=8.5, color="#424242",
        ha="left", va="center",
        arrowprops=dict(arrowstyle="-", color="#424242", alpha=0.5, lw=0.8),
    )

    # Annotate the dropout collapse
    ax.annotate(
        "Future dropouts\ncollapse: 8 → 0 meets",
        xy=(15.3, 3), xytext=(16.0, 11),
        fontsize=8.5, color="#B71C1C", ha="left", va="center",
        arrowprops=dict(arrowstyle="->", color="#B71C1C", alpha=0.7, lw=0.9),
    )

    # Annotate the retainer trajectory
    ax.annotate(
        "Retainers expand:\n13 → 19 meets",
        xy=(15, 19), xytext=(12.8, 23.5),
        fontsize=8.5, color="#1B5E20", ha="left", va="center",
        arrowprops=dict(arrowstyle="->", color="#1B5E20", alpha=0.7, lw=0.9),
    )

    ax.set_xlim(12.5, 19.0)
    ax.set_ylim(0, 30)
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Competitions per year (median; IQR shaded)")
    ax.set_title("Behavioral divergence emerges at the qualification milestone")
    ax.legend(loc="upper left", fontsize=8.5, framealpha=0.92)
    ax.grid(alpha=0.25)
    ax.set_xticks(ages)

    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig1_volume_trajectory.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("  -> fig1_volume_trajectory.png (polished)")


# =============================================================================
# Figure 2 — NEW: conceptual model
# =============================================================================

def conceptual_model():
    logger.info("Building conceptual model figure...")
    fig, ax = plt.subplots(figsize=(8, 4.5))

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    # Title
    ax.text(5, 5.7, "A behavioral-marker model of youth-sport disengagement",
            fontsize=11, fontweight="bold", ha="center")

    # Boxes
    def box(x, y, w, h, text, color, fontsize=9, fc="white", text_color="black"):
        rect = mpatches.FancyBboxPatch(
            (x - w/2, y - h/2), w, h,
            boxstyle="round,pad=0.05",
            linewidth=1.4, edgecolor=color, facecolor=fc, alpha=0.95,
        )
        ax.add_patch(rect)
        ax.text(x, y, text, ha="center", va="center", fontsize=fontsize, color=text_color)

    # Theoretical mechanisms (left)
    ax.text(1.5, 4.85, "Theoretical mechanisms\n(not directly observed)",
            fontsize=8.5, ha="center", style="italic", color="#555555")
    box(1.5, 4.0, 2.5, 0.55, "Engagement balance\n(Scanlan SCM)", "#1976D2", 8.5)
    box(1.5, 3.2, 2.5, 0.55, "Motivational quality\n(Ryan & Deci SDT)", "#1976D2", 8.5)
    box(1.5, 2.4, 2.5, 0.55, "Role-exit deliberation\n(Ebaugh; Eliasson)", "#1976D2", 8.5)

    # Behavioral marker (middle)
    ax.text(5, 4.85, "Observable behavioral marker\n(this study)",
            fontsize=8.5, ha="center", style="italic", color="#555555")
    box(5, 3.2, 2.5, 1.5,
        "Annual competition\nvolume\n\n(meets per year,\nages 13–18)",
        "#2E7D32", 9.5, fc="#E8F5E9")

    # Outcome (right)
    ax.text(8.5, 4.85, "Outcome\n(this study)",
            fontsize=8.5, ha="center", style="italic", color="#555555")
    box(8.5, 3.2, 2.5, 1.5,
        "Active senior\nretention\n\n(≥ 2 results in\nany year, age ≥ 20)",
        "#C62828", 9.5, fc="#FFEBEE")

    # Arrows
    ax.annotate("", xy=(3.7, 3.2), xytext=(2.85, 3.2),
                arrowprops=dict(arrowstyle="->", color="#888", lw=1.4))
    ax.annotate("", xy=(7.15, 3.2), xytext=(6.3, 3.2),
                arrowprops=dict(arrowstyle="->", color="#888", lw=1.4))

    # Arrow labels
    ax.text(3.3, 3.4, "produces\nfootprint in", fontsize=7.5, ha="center", color="#555")
    ax.text(6.75, 3.4, "precedes", fontsize=7.5, ha="center", color="#555")

    # Bottom hypothesis
    ax.text(5, 0.85,
            "Prediction: future retainers and future dropouts should differ in measurable competition behavior\n"
            "before formal exit, with divergence intensifying at qualification-milestone years (age 15–16).",
            fontsize=8.5, ha="center", style="italic",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#FAFAFA", edgecolor="#BDBDBD"))

    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig2_conceptual_model.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("  -> fig2_conceptual_model.png")


# =============================================================================
# Figure 5 — NEW: forest plot for time-varying HR
# =============================================================================

def forest_plot_time_varying():
    logger.info("Building time-varying HR forest plot...")

    data = [
        # (covariate, period, HR, lo, hi)
        ("Volume at age 15–16 (per SD)", "Years 0–3 (age 13–17)", 0.14, 0.11, 0.16),
        ("Volume at age 15–16 (per SD)", "Years 3–6 (age 16–19)", 0.69, 0.60, 0.79),
        ("Volume at age 15–16 (per SD)", "Years 6+ (age 19+)", 0.96, 0.77, 1.19),
        ("Championship types (per type)", "Years 0–3 (age 13–17)", 0.61, 0.55, 0.69),
        ("Championship types (per type)", "Years 3–6 (age 16–19)", 0.88, 0.79, 0.99),
        ("Championship types (per type)", "Years 6+ (age 19+)", 0.97, 0.78, 1.21),
        ("Tyrving (per SD)", "Years 0–3 (age 13–17)", 1.07, 0.99, 1.15),
        ("Tyrving (per SD)", "Years 3–6 (age 16–19)", 0.92, 0.84, 1.01),
        ("Tyrving (per SD)", "Years 6+ (age 19+)", 0.94, 0.78, 1.13),
        ("HHI early (per SD)", "Years 0–3 (age 13–17)", 0.97, 0.91, 1.05),
        ("HHI early (per SD)", "Years 3–6 (age 16–19)", 0.93, 0.85, 1.02),
        ("HHI early (per SD)", "Years 6+ (age 19+)", 1.02, 0.85, 1.21),
        ("Female", "Years 0–3 (age 13–17)", 1.16, 1.02, 1.31),
        ("Female", "Years 3–6 (age 16–19)", 1.06, 0.91, 1.23),
        ("Female", "Years 6+ (age 19+)", 1.09, 0.85, 1.39),
    ]

    covariates = [
        "Volume at age 15–16 (per SD)",
        "Championship types (per type)",
        "Tyrving (per SD)",
        "HHI early (per SD)",
        "Female",
    ]
    periods = ["Years 0–3 (age 13–17)", "Years 3–6 (age 16–19)", "Years 6+ (age 19+)"]
    period_colors = {periods[0]: "#1565C0", periods[1]: "#6A1B9A", periods[2]: "#757575"}
    period_offset = {periods[0]: 0.25, periods[1]: 0.0, periods[2]: -0.25}

    fig, ax = plt.subplots(figsize=(7.5, 5.5))

    for i, cov in enumerate(covariates):
        for period in periods:
            rec = [d for d in data if d[0] == cov and d[1] == period][0]
            hr, lo, hi = rec[2], rec[3], rec[4]
            y = len(covariates) - i + period_offset[period]
            color = period_colors[period]
            ax.plot([lo, hi], [y, y], color=color, linewidth=1.5)
            ax.plot(hr, y, "o", color=color, markersize=7)

    ax.axvline(1.0, color="black", linestyle="--", alpha=0.5, linewidth=0.9)
    ax.set_yticks(range(1, len(covariates) + 1))
    ax.set_yticklabels(covariates[::-1])
    ax.set_xscale("log")
    ax.set_xticks([0.1, 0.2, 0.5, 1.0, 2.0])
    ax.set_xticklabels(["0.1", "0.2", "0.5", "1.0", "2.0"])
    ax.set_xlabel("Hazard ratio (log scale) — protective ← 1 → harmful")
    ax.set_title("Time-varying hazard ratios across follow-up periods")
    ax.grid(axis="x", which="major", alpha=0.25)
    ax.set_xlim(0.08, 2.2)

    # Legend (outside plot area, on right)
    handles = [plt.Line2D([0], [0], marker="o", color=period_colors[p], linewidth=1.5,
                          markersize=7, label=p) for p in periods]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.02, 1.0),
              fontsize=8.5, title="Follow-up window", title_fontsize=8.5,
              framealpha=0.92, borderaxespad=0)

    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig5_time_varying_forest.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("  -> fig5_time_varying_forest.png")


def main():
    polish_figure_1()
    conceptual_model()
    forest_plot_time_varying()
    logger.info("Done.")


if __name__ == "__main__":
    main()
