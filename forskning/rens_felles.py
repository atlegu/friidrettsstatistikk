"""
rens_felles.py — fjerning av importkopier i registeruttrekk (audit 30.10.2026).

To regler, brukt likt i A1 og A6 og speilet uavhengig i audit/uavhengig.R:

  Sonetvilling (datafunn D1): en OK-rad i lengde/tresteg som har en identisk OK-rad i
    lengde_sone_05m/tresteg_sone_05m (samme utøver, dato, resultat og vind) er en
    importkopi. Kopiene kom inn ved reimportene 19.05.2026 og 24.08–06.09.2026; kilden
    viser hoppene bare under sonekoden. Brettraden fjernes.
  Eksakt dublett (datafunn D3): OK-rader som er like på utøver, dato, øvelse, resultat,
    vind og runde, for det meste stevner lagret som to stevneposter. Raden med lavest
    resultat-id beholdes. Rader med ulik runde (forsøk og finale) regnes ikke som dubletter.

Rader med annen status enn OK berøres ikke, og radrekkefølgen bevares.
"""

import pandas as pd

SONEPAR = [("lengde", "lengde_sone_05m"), ("tresteg", "tresteg_sone_05m")]


def fjern_kopier(r):
    """Returnerer (r uten kopier, {"sonetvilling": n, "eksakt_dublett": n})."""
    ok = r["status"] == "OK"
    k = pd.DataFrame({"athlete_id": r["athlete_id"], "dato": pd.to_datetime(r["date"]),
                      "pv": r["performance_value"], "vind": r["wind"].round(1).fillna(-99.0),
                      "kode": r["event_code"], "runde": r["round"].fillna("NA").astype(str),
                      "id": r["id"].astype(str)}, index=r.index)
    felles = ["athlete_id", "dato", "pv", "vind"]
    tvilling = pd.Series(False, index=r.index)
    for brett, sone in SONEPAR:
        s = k.loc[ok & (k["kode"] == sone), felles].drop_duplicates()
        treff = k.loc[ok & (k["kode"] == brett)].reset_index().merge(s, on=felles)["index"]
        tvilling.loc[treff] = True
    igjen = ok & ~tvilling
    sortert = k[igjen].sort_values("id", kind="mergesort")
    dublett = sortert.duplicated(["athlete_id", "dato", "kode", "pv", "vind", "runde"])
    fjern = tvilling.copy()
    fjern.loc[dublett[dublett].index] = True
    return r[~fjern], {"sonetvilling": int(tvilling.sum()), "eksakt_dublett": int(dublett.sum())}
