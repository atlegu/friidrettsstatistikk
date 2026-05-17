"""
Parser og bruker Tyrvingtabellen for poengberegning.

Tyrvingtabellen er NFIFs offisielle poengtabell for ungdomsfriidrett.
1000 poeng = «utmerket» for gitt alder, kjønn og øvelse.

Formel:
  Tidsøvelser:  Poeng = 1000 + (referanse_cs - resultat_cs) × kvotient
  Feltøvelser:  Poeng = 1000 + (resultat_cm - referanse_cm) × kvotient

  der cs = hundredeler (centiseconds), cm = centimeter.
  DB bruker: performance_value = hundredeler for tid, millimeter for felt.
"""

import xlrd
from pathlib import Path

TYRVING_XLS = Path(__file__).parent / "poengtabell-tyrvingtabellen.xls"

EVENT_CODE_TO_TYRVING = {
    "60m": "60 m",
    "80m": "80 m",
    "100m": "100 m",
    "200m": "200 m",
    "300m": "300 m",
    "400m": "400 m",
    "600m": "600 m",
    "800m": "800 m",
    "1000m": "1000 m",
    "1500m": "1500 m",
    "2000m": "2000 m",
    "3000m": "3000 m",
    "5000m": "5000 m",
    "60mh": "60 m hekk",
    "80mh": "80 m hekk",
    "200mh": "200 m hekk",
    "300mh": "300 m hekk",
    "1500msc": "1500 m hinder",
    "2000msc": "2000 m hinder",
    "hoyde": "Høyde",
    "stav": "Stav",
    "lengde": "Lengde",
    "tresteg": "Tresteg",
    "kule": "Kule",
    "diskos": "Diskos",
    "slegge": "Slegge",
    "spyd": "Spyd",
    "liten_ball": "Liten ball",
}

TIME_EVENTS = {
    "60 m", "80 m", "100 m", "200 m", "300 m", "400 m",
    "600 m", "800 m", "1000 m", "1500 m", "2000 m", "3000 m", "5000 m",
    "60 m hekk", "80 m hekk", "200 m hekk", "300 m hekk",
    "1500 m hinder", "2000 m hinder",
}


def parse_tyrving_xls(path=None):
    """Parse Tyrvingtabellen XLS. Returns dict[gender][age][event] = (ref_1000, kvotient)."""
    path = path or TYRVING_XLS
    wb = xlrd.open_workbook(str(path))
    table = {}

    for sheet_name in wb.sheet_names():
        if sheet_name == "Forside":
            continue
        parts = sheet_name.split()
        if len(parts) < 3:
            continue

        gender = "M" if parts[0] == "Gutter" else "F"
        try:
            age = int(parts[1])
        except ValueError:
            continue

        table.setdefault(gender, {}).setdefault(age, {})
        sheet = wb.sheet_by_name(sheet_name)

        for row in range(5, sheet.nrows):
            event_name = str(sheet.cell_value(row, 1)).strip()
            if not event_name or event_name.startswith("Sett inn") or event_name.startswith("©"):
                continue

            ref_1000 = sheet.cell_value(row, 7)
            kvotient = sheet.cell_value(row, 8)

            if isinstance(ref_1000, (int, float)) and ref_1000 > 0 and isinstance(kvotient, (int, float)) and kvotient > 0:
                if event_name not in table[gender][age]:
                    table[gender][age][event_name] = (float(ref_1000), float(kvotient))

    return table


def beregn_tyrving_poeng(performance_value, event_code, result_type, gender, age, table):
    """
    Beregn Tyrving-poeng for en enkeltprestasjon.

    Args:
        performance_value: int, fra DB (hundredeler for tid, mm for felt)
        event_code: str, f.eks. "100m", "hoyde"
        result_type: str, "time" eller "distance"/"height"
        gender: "M" eller "F"
        age: int, alder (kalenderår)
        table: dict fra parse_tyrving_xls()

    Returns:
        float eller None hvis øvelsen ikke finnes i tabellen.
    """
    if performance_value is None or gender not in table:
        return None

    tyrving_name = EVENT_CODE_TO_TYRVING.get(event_code)
    if not tyrving_name:
        return None

    age_clamped = max(10, min(19, age))
    age_table = table.get(gender, {}).get(age_clamped)
    if not age_table or tyrving_name not in age_table:
        return None

    ref_1000, kvotient = age_table[tyrving_name]

    if result_type == "time":
        ref_cs = ref_1000 * 100
        return 1000 + (ref_cs - performance_value) * kvotient
    else:
        ref_cm = ref_1000 * 100
        result_cm = performance_value / 10
        return 1000 + (result_cm - ref_cm) * kvotient


if __name__ == "__main__":
    table = parse_tyrving_xls()
    print("Parsed Tyrvingtabellen:")
    for gender in sorted(table):
        for age in sorted(table[gender]):
            events = list(table[gender][age].keys())
            print(f"  {gender} {age} år: {len(events)} øvelser")

    print("\nEksempler (Gutter 14 år):")
    examples = [
        (1300, "100m", "time", "M", 14, "100m 13.00s"),
        (1100, "100m", "time", "M", 14, "100m 11.00s"),
        (5000, "lengde", "distance", "M", 14, "Lengde 5.00m"),
        (1720, "hoyde", "height", "M", 14, "Høyde 1.72m"),
        (10000, "kule", "distance", "M", 14, "Kule 10.00m"),
    ]
    for pv, ec, rt, g, a, desc in examples:
        pts = beregn_tyrving_poeng(pv, ec, rt, g, a, table)
        print(f"  {desc:20s} → {pts:.0f} poeng" if pts else f"  {desc:20s} → N/A")
