"""
tyrving_r1.py — Corrected Tyrving scoring for the IJSSC revision (R1).

Why: the original routine (data/tyrvingtabellen.py) mapped only generic event
codes ("kule", "60mh", "spyd") to the Tyrving table, but the register stores
specification-coded events ("kule_3kg", "60mh_76_2cm", "spyd_400g",
"lengde_sone_05m", "kappgang_1000_m"). All throws, hurdles, take-off-zone jumps
and race walking were therefore left unscored, and athletes whose baseline-meet
results were all in those events had no Tyrving score (19.7% of the cohort).

This module scores every result whose event and implement/hurdle specification
match a row of the Tyrving table (NFIF 2014) for the athlete's sex and calendar
age. Same interface as tyrvingtabellen.py (parse_tyrving_xls, beregn_tyrving_poeng),
so the original analysis scripts can be re-run with it unchanged.

Rules:
  * The specification must match the table row for that sex x age (kule_3kg is
    scored for boys 13 and girls 14, whose table row is "Kule 3kg", but not for
    boys 14, whose table implement is 4 kg).
  * Take-off-zone jumps (lengde_sone_05m, tresteg_sone_05m) have no row of their
    own in the 2014 table; they are scored against the board-jump norm when
    ZONE_AS_BOARD is True (an approximation; the sensitivity analysis sets it False).
  * Race-walk and middle-distance times stored as M.SS (e.g. "6.57" = 6:57,
    performance_value 657) are repaired before scoring.
  * Scores are capped to [0, 1500] by the calling code, as in the original pipeline.

Register units: time = hundredths of a second; field events = millimetres.
"""

import re
from pathlib import Path

import xlrd

DATA_DIR = Path("/Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/Statistikk/forskning/ncc-kohort/data")
TYRVING_XLS = DATA_DIR / "poengtabell-tyrvingtabellen.xls"
ZONE_AS_BOARD = True

_RUNS = {"60m": "60 m", "80m": "80 m", "100m": "100 m", "200m": "200 m", "300m": "300 m",
         "400m": "400 m", "600m": "600 m", "800m": "800 m", "1000m": "1000 m", "1500m": "1500 m",
         "2000m": "2000 m", "3000m": "3000 m", "5000m": "5000 m"}
_FIELD = {"hoyde": "Høyde", "stav": "Stav", "lengde": "Lengde", "tresteg": "Tresteg",
          "hoyde_ut": "Høyde uten tilløp", "lengde_ut": "Lengde uten tilløp"}
# DB code -> (table event, spec token that the table's spec column must start with)
_SPEC = {
    "kule_2kg": ("Kule", "2kg"), "kule_3kg": ("Kule", "3kg"), "kule_4kg": ("Kule", "4kg"),
    "diskos_600g": ("Diskos", "0,6kg"), "diskos_750g": ("Diskos", "0,75kg"), "diskos_1kg": ("Diskos", "1kg"),
    "spyd_400g": ("Spyd", "0,4kg"), "spyd_600g": ("Spyd", "0,6kg"),
    "slegge_20kg/110cm": ("Slegge", "2kg/110cm"), "slegge_30kg_1195cm": ("Slegge", "3kg/119,5cm"),
    "slegge_40kg/1195cm": ("Slegge", "4kg/119,5cm"),
    "60mh_76_2cm": ("60 m hekk", "76,2cm"), "80mh_84cm": ("80 m hekk", "84,0cm"),
    "200mh_68cm": ("200 m hekk", "68,0cm"), "200mh_76_2cm": ("200 m hekk", "76,2cm"),
    "kappgang_1000_m": ("1000 m", "kappgang"), "1000mg": ("1000 m", "kappgang"),
}
_ZONE = {"lengde_sone_05m": "Lengde", "tresteg_sone_05m": "Tresteg"}
TIME_EVENTS = {"60 m", "80 m", "100 m", "200 m", "300 m", "400 m", "600 m", "800 m", "1000 m",
               "1500 m", "2000 m", "3000 m", "5000 m", "60 m hekk", "80 m hekk", "200 m hekk",
               "300 m hekk", "1500 m hinder"}
_MSS_CODES = {"600m", "800m", "1000m", "1500m", "2000m", "3000m", "5000m", "kappgang_1000_m", "1000mg"}
SCORABLE_CODES = set(_RUNS) | set(_FIELD) | set(_SPEC) | set(_ZONE)


def _norm(s):
    return re.sub(r"\s+", "", str(s)).lower()


def parse_tyrving_xls(path=None):
    """dict[gender][age][(event, spec)] = (ref_1000, kvotient); spec '' when the row has none."""
    wb = xlrd.open_workbook(str(path or TYRVING_XLS))
    table = {}
    for sheet_name in wb.sheet_names():
        parts = sheet_name.split()
        if sheet_name == "Forside" or len(parts) < 3:
            continue
        gender = "M" if parts[0] == "Gutter" else "F"
        try:
            age = int(parts[1])
        except ValueError:
            continue
        rows = table.setdefault(gender, {}).setdefault(age, {})
        sh = wb.sheet_by_name(sheet_name)
        for r in range(5, sh.nrows):
            event = str(sh.cell_value(r, 1)).strip()
            ref, kv = sh.cell_value(r, 7), sh.cell_value(r, 8)
            if not event or event.startswith(("Sett inn", "Når", "Kun", "©")):
                continue
            if isinstance(ref, (int, float)) and ref > 0 and isinstance(kv, (int, float)) and kv > 0:
                rows.setdefault((event, _norm(sh.cell_value(r, 2))), (float(ref), float(kv)))
    return table


def _lookup(age_table, event, spec_token):
    for (ev, spec), val in age_table.items():
        if ev == event and ((spec_token is None and spec == "") or
                            (spec_token is not None and spec.startswith(_norm(spec_token)))):
            return val
    return None


def repair_time(performance_value, event_code):
    """M.SS stored as seconds (657 = '6.57' = 6:57) -> hundredths; other values unchanged."""
    if event_code in _MSS_CODES and performance_value is not None and performance_value < 6000:
        minutes, secs = int(performance_value // 100), int(performance_value % 100)
        return (minutes * 60 + secs) * 100 if secs < 60 else None
    return performance_value


def beregn_tyrving_poeng(performance_value, event_code, result_type, gender, age, table):
    """Tyrving points for one result; None if the event/spec has no row for this sex x age."""
    if performance_value is None or gender not in table or age is None:
        return None
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
    age_table = table.get(gender, {}).get(max(10, min(19, int(age))))
    val = _lookup(age_table, event, spec) if age_table else None
    if val is None:
        return None
    ref_1000, kvotient = val
    if event in TIME_EVENTS:
        pv = repair_time(performance_value, event_code)
        return None if pv is None else 1000 + (ref_1000 * 100 - pv) * kvotient
    return 1000 + (performance_value / 10 - ref_1000 * 100) * kvotient
