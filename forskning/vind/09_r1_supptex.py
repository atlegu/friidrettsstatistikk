r"""
09_r1_supptex.py — A6: supplerende tabeller S1–S5 som LaTeX, rett fra CSV.

Ingen verdier skrives for hånd: hver sX.tex bygges fra tilhørende
tables/manus/*.csv og \input-es i manus/main.tex.
"""

import re

import logging
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
TABM = HERE / "tables" / "manus"
UT = HERE / "manus"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def tex_tabular(df, kolfmt=None):
    kolfmt = kolfmt or "l" + "c" * (len(df.columns) - 1)
    linjer = [f"\\begin{{tabular}}{{{kolfmt}}}", "\\toprule",
              " & ".join(str(c) for c in df.columns) + " \\\\", "\\midrule"]
    for _, rad in df.iterrows():
        celler = ["---" if (pd.isna(v) or str(v) in ("", "nan")) else str(v) for v in rad]
        linjer.append(" & ".join(celler) + " \\\\")
    linjer += ["\\bottomrule", "\\end{tabular}"]
    tekst = "\n".join(linjer)
    tekst = (tekst.replace("%", "\\%").replace("–", "--")
             .replace("−", "$-$").replace("_", "\\_"))
    return re.sub(r"(?<=\d)-(?=\d)", "--", tekst)


def main():
    # S1: hopp etter alder
    s1 = pd.read_csv(TABM / "tableS_jumps_age.csv")
    (UT / "s1.tex").write_text(tex_tabular(s1))

    # S2: robusthet
    s2 = pd.read_csv(TABM / "tableS_robustness.csv")
    s2 = s2.rename(columns={s2.columns[0]: "Event", "primaer": "Primary",
                            "celler_min3": "Cells $\\geq$3", "uten_vind_0": "No exact 0.0",
                            "uten_2.0_pm0.2": "Excl. $\\pm$0.2 of +2.0",
                            "periode_2011_2019": "2011--19", "periode_2021_2026": "2021--26",
                            "stevne_fe": "Meet FE", "kluster_stevne": "Meet cluster"})
    s2 = s2[["Event", "Primary", "Cells $\\geq$3", "No exact 0.0",
             "Excl. $\\pm$0.2 of +2.0", "2011--19", "2021--26", "Meet FE"]]
    (UT / "s2.tex").write_text(tex_tabular(s2))

    # S3: korreksjonstabell
    s3 = pd.read_csv(TABM / "tableS_correction.csv")
    s3 = s3.rename(columns={"Tailwind slope, s per +1 m/s (95% CI)":
                            "Tailwind slope per +1 m/s (95% CI)",
                            "Headwind slope, s per −1 m/s (95% CI)":
                            "Headwind slope per −1 m/s (95% CI)"})
    (UT / "s3.tex").write_text(tex_tabular(s3))

    # S4: per sekund løpstid
    s4 = pd.read_csv(TABM / "tableS_perduration.csv")
    s4 = s4.rename(columns={"Mean time, s": "Mean time (s)",
                            "Gain per +1 m/s, s": "Gain per +1 m/s (s)",
                            "Gain per +1 m/s per second of race time": "Per second of race time"})
    (UT / "s4.tex").write_text(tex_tabular(s4))

    # S5: kvadratisk form
    s5 = pd.read_csv(TABM / "tableS_quadratic.csv")
    s5["n"] = s5["n"].map("{:,}".format)
    (UT / "s5.tex").write_text(tex_tabular(s5))

    logger.info(f"s1–s5.tex skrevet til {UT}/")


if __name__ == "__main__":
    main()
