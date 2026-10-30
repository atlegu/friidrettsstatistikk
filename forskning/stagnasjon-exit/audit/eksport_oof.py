"""
eksport_oof.py — A1-audit: eksporter out-of-fold-prediksjoner (første CV-repetisjon,
samme frø som 03/06) for de fire modellene i DeLong-kontrastene, slik at
DeLong-implementasjonen i 06 kan kontrolleres mot pROC i R.
Output: audit/oof.csv
"""

import importlib.util
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent.parent
spec = importlib.util.spec_from_file_location("m03", HERE / "03_modeller.py")
m03 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m03)


def main():
    d = m03.last_primaer()
    felles = ["gender", "vol1314_g", "vol1516_g", "k13", "k15"]
    ut = pd.DataFrame({"athlete_id": d["athlete_id"].to_numpy(), "y": d["senior"].to_numpy()})
    for navn, kol in [("m1", m03.M1_KOL), ("m2", m03.M2_KOL),
                      ("frem", felles + ["delta_z"]), ("niva", felles + ["niva_w1_z"])]:
        per_rep, oof = m03.cv_auc(d, kol)
        ut[navn] = oof
        ut.attrs[navn] = per_rep.mean()
        print(f"{navn}: CV-AUC snitt over 20 rep = {per_rep.mean():.4f}")
    ut.to_csv(HERE / "audit" / "oof.csv", index=False)


if __name__ == "__main__":
    main()
