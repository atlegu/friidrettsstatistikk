"""
10_eiv_kalibrering.py — A6: målefeilsaritmetikken bak lesningen av stevne-FE-attenueringen.

For hver sprintøvelse: variansen i vind som identifiserer β under primærspesifikasjonen
(celle-FE + måned + runde) og under stevne-FE (celle-FE + stevne-FE + runde), og hvilken
klassisk målefeil-SD σ (løpsnivå, uavhengig av alt annet) som gjør forholdet mellom
reliabilitetene lik det observerte forholdet β_FE/β_primær.

Feilvariansen som overlever demeaningen anslås med frihetsgradsandelen
(N − parametre)/N for hver spesifikasjon. Resultatet er en illustrasjon under eksplisitte
antakelser, ikke et estimat av målerfeilen.

Output: tables/estimering/r1_eiv.csv
"""

import importlib.util
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq

HERE = Path(__file__).parent
DATA = HERE / "data_private"
EST = HERE / "tables" / "estimering"

spec = importlib.util.spec_from_file_location("m03", HERE / "03_estimering.py")
m03 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m03)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def resid_var(g, meet_fe):
    """Residualvarians i vind etter FE + kontroller, og frihetsgradsandel."""
    dum = m03.dummies(g)
    if meet_fe:
        dum = dum[[c for c in dum.columns if c.startswith("r_")]]
    M = pd.concat([g[["wind"]], dum], axis=1)
    Md = m03.demean(M, g["celle"], g["meet_id"] if meet_fe else None)
    Md = Md.loc[:, (Md.abs() > 1e-12).any(axis=0)]
    X = Md.drop(columns=["wind"]).to_numpy()
    w = Md["wind"].to_numpy()
    if X.shape[1]:
        w = w - X @ np.linalg.lstsq(X, w, rcond=None)[0]
    n = len(g)
    k = g["celle"].nunique() + X.shape[1] + (g["meet_id"].nunique() if meet_fe else 0)
    return float(np.mean(w ** 2)), (n - k) / n


def main():
    d = pd.read_csv(DATA / "analyseklar.csv", low_memory=False)
    d = d[d["n_i_celle"] >= 2]
    rob = pd.read_csv(EST / "robusthet.csv")
    rader = []
    for kode in ["60m", "100m", "200m"]:
        g = d[d["event_code"] == kode]
        v_m, df_m = resid_var(g, meet_fe=False)
        v_f, df_f = resid_var(g, meet_fe=True)
        b_m = float(rob[(rob["event"] == kode) & (rob["analyse"] == "primaer")]["gevinst_per_ms"].iloc[0])
        b_f = float(rob[(rob["event"] == kode) & (rob["analyse"] == "stevne_fe")]["gevinst_per_ms"].iloc[0])
        r_obs = b_f / b_m

        def gap(sigma):
            lam_m = (v_m - sigma ** 2 * df_m) / v_m
            lam_f = (v_f - sigma ** 2 * df_f) / v_f
            return lam_f / lam_m - r_obs

        hi = np.sqrt(v_f / df_f) * 0.999
        sigma = brentq(gap, 1e-6, hi) if gap(1e-6) * gap(hi) < 0 else np.nan
        lam_m = (v_m - sigma ** 2 * df_m) / v_m if not np.isnan(sigma) else np.nan
        lam_f = (v_f - sigma ** 2 * df_f) / v_f if not np.isnan(sigma) else np.nan
        rader.append({"event": kode, "sd_vind_primaer": np.sqrt(v_m), "sd_vind_stevnefe": np.sqrt(v_f),
                      "andel_varians_innen_stevne": v_f / v_m, "beta_primaer": b_m,
                      "beta_stevnefe": b_f, "forhold_obs": r_obs, "sigma_implisert": sigma,
                      "reliabilitet_primaer": lam_m, "reliabilitet_stevnefe": lam_f})
        logger.info(f"{kode}: σ = {sigma:.3f} m/s, λ {lam_m:.2f} → {lam_f:.2f}, forhold {r_obs:.2f}")
    pd.DataFrame(rader).to_csv(EST / "r1_eiv.csv", index=False)

    # Rå andel av vindvariansen innen stevne (celler >= 2), alle øvelser
    andel = []
    for kode, g in d.groupby("event_code"):
        tot = g["wind"].var()
        innen = (g["wind"] - g.groupby("meet_id")["wind"].transform("mean")).var()
        andel.append({"event": kode, "andel_innen_stevne": innen / tot})
    pd.DataFrame(andel).to_csv(EST / "r1_innen_stevne.csv", index=False)


if __name__ == "__main__":
    main()
