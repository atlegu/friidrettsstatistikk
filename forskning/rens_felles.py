"""
rens_felles.py — fjerning av importkopier i registeruttrekk (audit 30.10.2026).

Tre regler, brukt likt i A1 og A6 og speilet uavhengig i audit/uavhengig.R:

  Sonetvilling (datafunn D1): en OK-rad i lengde/tresteg som har en identisk OK-rad i
    lengde_sone_05m/tresteg_sone_05m (samme utøver, dato, resultat og vind) er en
    importkopi. Kopiene kom inn ved reimportene 19.05.2026 og 24.08–06.09.2026; kilden
    viser hoppene bare under sonekoden. Brettraden fjernes.
  Flerdagskopi (D1, flerdagsstevner): som sonetvilling, men sonehoppet ligger 1–6 dager
    etter brettraden. Augustimporten ga alle resultater i et flerdagsstevne stevnets
    startdato, mens sonehoppet ligger på riktig dag (scraper/opprydding/
    KRYSSDUBLETTER_2026-10-30.md; kilden viser hoppet bare under sonen, 12 av 12). I
    uttrekkene ligger alle slike brettrader på stevnets startdato, og en placebovariant
    med sonen før brettraden gir 1 treff i A1 og 6 i A6, mot 5 780 og 8 906.
  Eksakt dublett (datafunn D3): OK-rader som er like på utøver, dato, øvelse, resultat,
    vind og runde, for det meste stevner lagret som to stevneposter. Raden med lavest
    resultat-id beholdes. Rader med ulik runde (forsøk og finale) regnes ikke som dubletter.

Rader med annen status enn OK berøres ikke, og radrekkefølgen bevares.
"""

import pandas as pd

SONEPAR = [("lengde", "lengde_sone_05m"), ("tresteg", "tresteg_sone_05m")]


def fjern_kopier(r):
    """Returnerer (r uten kopier, {"sonetvilling": n, "flerdagskopi": n, "eksakt_dublett": n})."""
    ok = r["status"] == "OK"
    k = pd.DataFrame({"athlete_id": r["athlete_id"], "dato": pd.to_datetime(r["date"]),
                      "pv": r["performance_value"], "vind": r["wind"].round(1).fillna(-99.0),
                      "kode": r["event_code"], "runde": r["round"].fillna("NA").astype(str),
                      "id": r["id"].astype(str)}, index=r.index)
    felles = ["athlete_id", "dato", "pv", "vind"]
    tvilling = pd.Series(False, index=r.index)
    flerdag = pd.Series(False, index=r.index)
    for brett, sone in SONEPAR:
        s = k.loc[ok & (k["kode"] == sone), felles].drop_duplicates()
        b = k.loc[ok & (k["kode"] == brett)].reset_index()
        treff = b.merge(s, on=felles)["index"]
        tvilling.loc[treff] = True
        b = b[~b["index"].isin(treff) & b["pv"].notna()]
        m = b.merge(s[s["pv"].notna()], on=["athlete_id", "pv", "vind"], suffixes=("", "_sone"))
        dager = (m["dato_sone"] - m["dato"]).dt.days
        flerdag.loc[m.loc[dager.between(1, 6), "index"].unique()] = True
    igjen = ok & ~tvilling & ~flerdag
    sortert = k[igjen].sort_values("id", kind="mergesort")
    dublett = sortert.duplicated(["athlete_id", "dato", "kode", "pv", "vind", "runde"])
    fjern = tvilling | flerdag
    fjern.loc[dublett[dublett].index] = True
    return r[~fjern], {"sonetvilling": int(tvilling.sum()), "flerdagskopi": int(flerdag.sum()),
                       "eksakt_dublett": int(dublett.sum())}
