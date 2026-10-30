"""
tyrving_r3.py — tyrving_r2.py with the complete event-code mapping (prepared 30 Oct 2026 for the next
IJSSC revision; revision_r1 and its frozen tyrving_r2.py are unchanged).

The formulas and parameters are those of tyrving_r2.py (validated against the 2014 workbook, see
audit/audit_03_tyrving.py). What changes is the mapping from register event codes to table rows:
tyrving_r2._SPEC had no entry for several standard implements and hurdle/steeplechase/race-walk
codes that tyrving_params_2014.csv has rows for, so beregn_tyrving_poeng() returned None for them,
although Supplementary Methods S-M3 states that every result is scored when its event and
specification match a table row for the athlete's sex and age. Added (each verified against the
table rows for the athlete's sex and age, see r2_kontroll_koblinger.py):
  boys 16: shot 5 kg, discus 1.5 kg, javelin 700 g, hammer 5 kg/120 cm; girls 15-16: javelin 500 g;
  ball throw 150 g (13-14); 80 m hurdles 76.2 cm (girls 15-16); 100 m hurdles 84.0 cm (boys 15) and
  91.4 cm (boys 16); 300 m hurdles 76.2 cm (14-16) and 84.0 cm (boys 16); 1500 m steeplechase 76.2 cm;
  race walk 2000/3000/5000/10000 m (codes 2000mg, 3000mg and kappgang_*), with the M.SS repair.
Ball-throw values stored in centimetres in the May 2026 extract are converted (see _CM_KODER).
No baseline-meet result is affected (none of these codes occurs at the baseline meet with a norm).

The original module docstring follows.
"""

"""
tyrving_r2.py — Exact replication of the NFIF Tyrving table (2014 workbook) for the IJSSC revision.

Audit (2026-10-02) of the workbook's cell formulas showed four formula types, two of which
were implemented incorrectly both in the submitted pipeline (data/tyrvingtabellen.py) and in
the first revision (tyrving_r1.py):

  time_sec        (≤ 400 m, hurdles ≤ 400 m):   P = 1000 + (ref_cs − result_cs) · I      [hundredths]
  time_minsec     (≥ 600 m, steeplechase, walk): P = 1000 + (ref_ds − result_ds) · I      [TENTHS of a second]
  field_linear    (high, long, triple jump):     P = 1000 − (ref_cm − result_cm) · I
  field_piecewise (throws, pole vault):          three slopes, per cm:
        result > ref:                 P = 1000 − (ref − result) · J        (J = "Faktor 1")
        0.8·ref ≤ result ≤ ref:       P = 1000 − (ref − result) · K
        result < 0.8·ref:             P = 1000 − [0.2·ref · K + (ref − result − 0.2·ref) · L]
  Points are truncated (ROUNDDOWN) and floored at 0, as in the workbook.

The earlier code used hundredths for time_minsec (a ten-fold too steep slope: points collapsed
to 0 or hit the 1,500 cap) and the steepest slope L everywhere for field_piecewise.

Parameters per sex × age × event × specification are read from tyrving_params_2014.csv, which
was extracted from the workbook's cells (see audit/audit_03_tyrving.py for the validation against
LibreOffice-computed workbook values). Event-code matching (specification must match the table
row for the athlete's sex and age; take-off-zone jumps scored against the board-jump norm;
M.SS time repair) is unchanged from tyrving_r1.py.
"""

import math
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
PARAMS = HERE / "tyrving_params_2014.csv"
ZONE_AS_BOARD = True

_RUNS = {"40m": "40 m", "60m": "60 m", "80m": "80 m", "100m": "100 m", "200m": "200 m", "300m": "300 m",
         "400m": "400 m", "600m": "600 m", "800m": "800 m", "1000m": "1000 m", "1500m": "1500 m",
         "2000m": "2000 m", "3000m": "3000 m", "5000m": "5000 m"}
_FIELD = {"hoyde": "Høyde", "stav": "Stav", "lengde": "Lengde", "tresteg": "Tresteg",
          "hoyde_ut": "Høyde uten tilløp", "lengde_ut": "Lengde uten tilløp"}
_SPEC = {
    "kule_2kg": ("Kule", "2kg"), "kule_3kg": ("Kule", "3kg"), "kule_4kg": ("Kule", "4kg"),
    "diskos_600g": ("Diskos", "0,6kg"), "diskos_750g": ("Diskos", "0,75kg"), "diskos_1kg": ("Diskos", "1kg"),
    "spyd_400g": ("Spyd", "0,4kg"), "spyd_600g": ("Spyd", "0,6kg"),
    "slegge_20kg/110cm": ("Slegge", "2kg/110cm"), "slegge_30kg_1195cm": ("Slegge", "3kg/119,5cm"),
    "slegge_40kg/1195cm": ("Slegge", "4kg/119,5cm"),
    "60mh_76_2cm": ("60 m hekk", "76,2cm"), "80mh_84cm": ("80 m hekk", "84,0cm"),
    "200mh_68cm": ("200 m hekk", "68,0cm"), "200mh_76_2cm": ("200 m hekk", "76,2cm"),
    "kappgang_1000_m": ("1000 m", "kappgang"), "1000mg": ("1000 m", "kappgang"),
    # complete mapping (30 Oct 2026): codes with table rows that tyrving_r2 left unmapped
    "kule_5kg": ("Kule", "5kg"), "diskos_1_5kg": ("Diskos", "1,5kg"),
    "spyd_500g": ("Spyd", "0,5kg"), "spyd_700g": ("Spyd", "0,7kg"),
    "slegge_50kg/120cm": ("Slegge", "5kg/120cm"), "liten_ball_150gram": ("Liten ball", "150g"),
    "80mh_76_2cm": ("80 m hekk", "76,2cm"), "100mh_84cm": ("100 m hekk", "84,0cm"),
    "100mh_91_4cm": ("100 m hekk", "91,4cm"),
    "300mh_76_2cm": ("300 m hekk", "76,2cm"), "300mh_84cm": ("300 m hekk", "84,0cm"),
    "1500mhinder_76_2cm": ("1500 m hinder", "76,2cm"),
    "2000mg": ("2000 m", "kappgang"), "kappgang_2000_m": ("2000 m", "kappgang"),
    "3000mg": ("3000 m", "kappgang"), "kappgang_3000_m": ("3000 m", "kappgang"),
    "kappgang_5000_m": ("5000 m", "kappgang"), "kappgang_10000_m": ("10000 m", "kappgang"),
}
_ZONE = {"lengde_sone_05m": "Lengde", "tresteg_sone_05m": "Tresteg"}
# Ball throws are stored with result_type "time" and value = metres x 100 in the May 2026 extract (every
# liten_ball row; the register has since corrected them to distance in millimetres). A value below
# 10,000 (10 m in millimetres) is read as centimetres.
_CM_KODER = {"liten_ball_150gram"}
_MSS_CODES = {"600m", "800m", "1000m", "1500m", "2000m", "3000m", "5000m", "kappgang_1000_m", "1000mg",
               "1500mhinder_76_2cm", "2000mg", "kappgang_2000_m", "3000mg", "kappgang_3000_m",
               "kappgang_5000_m", "kappgang_10000_m"}


def _norm(s):
    return re.sub(r"\s+", "", str(s)).lower()


def parse_tyrving_xls(path=None):
    """dict[gender][age] -> list of parameter rows (same call signature as the old modules)."""
    t = pd.read_csv(PARAMS)
    t["spec_n"] = t["spec"].fillna("").map(_norm)
    table = {}
    for r in t.to_dict("records"):
        table.setdefault(r["sex"], {}).setdefault(int(r["age"]), []).append(r)
    return table


def _row(age_rows, event, spec_token):
    for r in age_rows:
        if r["event"] != event:
            continue
        if spec_token is None and r["spec_n"] == "":
            return r
        if spec_token is not None and r["spec_n"].startswith(_norm(spec_token)):
            return r
    return None


def repair_time(performance_value, event_code):
    """M.SS stored as seconds (657 = '6.57' = 6:57) -> hundredths; other values unchanged."""
    if event_code in _MSS_CODES and performance_value is not None and performance_value < 6000:
        minutes, secs = int(performance_value // 100), int(performance_value % 100)
        return (minutes * 60 + secs) * 100 if secs < 60 else None
    return performance_value


def points(row, value):
    """Workbook formula for one row. value: seconds (time) or metres (field)."""
    ref = float(row["ref"])
    typ = row["type"]
    if typ == "time_sec":
        p = 1000 + (ref * 100 - value * 100) * float(row["I"])
    elif typ == "time_minsec":
        p = 1000 + (ref * 10 - value * 10) * float(row["I"])
    elif typ == "field_linear":
        p = 1000 - (ref * 100 - value * 100) * float(row["I"])
    else:  # field_piecewise
        n, m = ref * 100, value * 100
        o = n - m
        J, K, L = float(row["J"]), float(row["K"]), float(row["L"])
        if value < 0.8 * ref:
            p = 1000 - ((n - 0.8 * n) * K + (o - (n - n * 0.8)) * L)
        else:
            p = 1000 - o * (J if value > ref else K)
    p = math.floor(p + 1e-9)  # ROUNDDOWN to integer (float tolerance)
    return max(0, p)


def beregn_tyrving_poeng(performance_value, event_code, result_type, gender, age, table):
    """Tyrving points for one register result (time: hundredths; field: millimetres)."""
    if performance_value is None or gender not in table or age is None:
        return None
    if isinstance(performance_value, float) and math.isnan(performance_value):
        return None
    if event_code in _CM_KODER and performance_value < 10000:
        performance_value = performance_value * 10   # stored as centimetres, see _CM_KODER
    if event_code in _RUNS:
        event, spec = _RUNS[event_code], None
    elif event_code in _FIELD:
        event, spec = _FIELD[event_code], None
    elif event_code in _SPEC:
        event, spec = _SPEC[event_code]
    elif ZONE_AS_BOARD and event_code in _ZONE:
        event, spec = _ZONE[event_code], None
    else:
        return None
    rows = table.get(gender, {}).get(max(10, min(19, int(age))))
    row = _row(rows, event, spec) if rows else None
    if row is None:
        return None
    if row["type"].startswith("time"):
        pv = repair_time(performance_value, event_code)
        if pv is None:
            return None
        return points(row, pv / 100.0)
    return points(row, performance_value / 1000.0)
