"""
Build a CONSORT-style cohort flow diagram for Supplementary Figure S0.
"""

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as mpatches

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

FIG_DIR = Path(__file__).parent.parent / "submission_pse" / "figures"

mpl.rcParams["figure.dpi"] = 150
mpl.rcParams["savefig.dpi"] = 150
mpl.rcParams["savefig.bbox"] = "tight"
mpl.rcParams["font.size"] = 9
mpl.rcParams["font.family"] = "DejaVu Sans"


def main():
    fig, ax = plt.subplots(figsize=(8.5, 8.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 11)
    ax.axis("off")

    def box(x, y, w, h, text, color="#1976D2", fc="#E3F2FD", fontsize=9):
        rect = mpatches.FancyBboxPatch(
            (x - w/2, y - h/2), w, h,
            boxstyle="round,pad=0.05",
            linewidth=1.4, edgecolor=color, facecolor=fc, alpha=0.95,
        )
        ax.add_patch(rect)
        ax.text(x, y, text, ha="center", va="center", fontsize=fontsize)

    def excl(x, y, w, h, text):
        rect = mpatches.FancyBboxPatch(
            (x - w/2, y - h/2), w, h,
            boxstyle="round,pad=0.05",
            linewidth=1.0, edgecolor="#B71C1C", facecolor="#FFEBEE", alpha=0.9,
        )
        ax.add_patch(rect)
        ax.text(x, y, text, ha="center", va="center", fontsize=8, style="italic")

    def arrow(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color="#424242", lw=1.3))

    ax.text(5, 10.6, "Cohort construction flow", fontsize=12, fontweight="bold", ha="center")

    # 1. Source meets
    box(3, 9.5, 5.5, 0.7,
        "All participants in six regional youth meets\n"
        "(NCC 2011, 2012 · PEAB 2013, 2014 · Bendit 2015 · Ungdomslekene 2016)",
        fontsize=8.5)

    # Exclusion 1: boundary birth years
    excl(8, 9.5, 3.5, 0.6,
         "Excluded: birth years 1997 and 2003\n(only one possible eligible edition)")
    arrow(5.75, 9.5, 6.25, 9.5)

    # 2. Athletes born 1998-2002 in scope
    box(3, 8.0, 5.5, 0.7,
        "Athletes born 1998–2002 (cohort A: 1998–2000; cohort B: 2001–2002)\n"
        "13–14 years old in at least one meet edition",
        fontsize=8.5)
    arrow(3, 9.1, 3, 8.4)

    # Deduplication
    excl(8, 8.0, 3.5, 0.6,
         "Athletes attending both as 13 and 14:\nbaseline = earlier edition")
    arrow(5.75, 8.0, 6.25, 8.0)

    # 3. Deduplicated cohort
    box(3, 6.5, 5.5, 0.7,
        "Total analytical cohort: 2,123 athletes\n"
        "(996 male, 1,103 female, 24 sex unknown)",
        fontsize=8.5, color="#2E7D32", fc="#E8F5E9")
    arrow(3, 7.6, 3, 6.9)

    # 4. Sub-cohorts
    box(1.4, 5.0, 2.6, 0.6,
        "Cohort A (1998–2000)\nn = 1,301", color="#2E7D32", fc="#E8F5E9", fontsize=8.5)
    box(4.6, 5.0, 2.6, 0.6,
        "Cohort B (2001–2002)\nn = 822", color="#2E7D32", fc="#E8F5E9", fontsize=8.5)
    arrow(2.5, 6.15, 1.4, 5.35)
    arrow(3.5, 6.15, 4.6, 5.35)

    # 5. Predictor windows
    box(3, 3.6, 5.5, 0.7,
        "Baseline window: ages 13–14\n"
        "Predictors observed during baseline only (primary analysis)",
        fontsize=8.5)
    arrow(3, 4.7, 3, 4.0)

    # 6. Outcome
    box(3, 2.0, 5.5, 0.7,
        "Outcome window: ages 20+\n"
        "Primary: ≥2 results in any senior-age year (n_retainers = 348, 16.4%)",
        color="#C62828", fc="#FFEBEE", fontsize=8.5)
    arrow(3, 3.25, 3, 2.4)

    # Follow-up annotation
    box(8.0, 3.6, 3.5, 0.7,
        "Maximum follow-up:\n14 years (Cohort A)\n9 years (Cohort B)",
        color="#757575", fc="#FAFAFA", fontsize=8.5)

    # Missingness
    box(3, 0.6, 5.5, 0.7,
        "Complete-case analysis: n = 1,704\n"
        "(missing data: Tyrving ~20%, HHI ~10%)",
        color="#757575", fc="#FAFAFA", fontsize=8.5)
    arrow(3, 1.65, 3, 0.95)

    plt.tight_layout()
    fig.savefig(FIG_DIR / "figS0_flow_diagram.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("  -> figS0_flow_diagram.png")


if __name__ == "__main__":
    main()
