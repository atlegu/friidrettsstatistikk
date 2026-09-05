"""
04_vedleggstabell.py - Lager vedleggstabellen til 03_vurdering.md fra tabellene,
slik at ingen tall i vedlegget er skrevet for hånd.

Inn: tables/trender_per_serie.csv, tables/nivaa_tidlig_sent.csv, tables/vinduer.json
Ut:  tables/vedlegg_trender.md
"""

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
TAB = HERE / "tables"
LABEL = {"G13": "Gutter 13", "G14": "Gutter 14", "J13": "Jenter 13", "J14": "Jenter 14"}
ORDER = ["60 m", "200 m", "60 m hekk", "80 m hekk", "200 m hekk", "600 m", "1500 m",
         "Lengde", "Tresteg", "Høyde", "Stav", "Kule", "Spyd", "Diskos", "Slegge"]


def stjerne(p):
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""


def no(x, dec=1, sign=False):
    """Norsk tallformat: komma som desimaltegn, valgfritt fortegn."""
    s = f"{x:+.{dec}f}" if sign else f"{x:.{dec}f}"
    return s.replace(".", ",")


def niva(x):
    return no(x, 1 if x >= 100 else 2)


def main():
    t = pd.read_csv(TAB / "trender_per_serie.csv")
    niv = pd.read_csv(TAB / "nivaa_tidlig_sent.csv")
    vin = json.loads((TAB / "vinduer.json").read_text(encoding="utf-8"))
    (t0, t1), (s0, s1) = vin["tidlig"], vin["sent"]
    niv["ovelse_kort"] = niv["ovelse"].str.replace(r" \(.*\)", "", regex=True)
    t = t.merge(niv[["ovelse_kort", "gruppe", "median_tidlig", "median_sent"]],
                left_on=["ovelse", "gruppe"], right_on=["ovelse_kort", "gruppe"], how="left")
    t["_o"] = t["ovelse"].map(ORDER.index)
    t = t.sort_values(["_o", "gruppe"])
    lines = [f"# Vedlegg: trend per øvelse og klasse, lekene {t0}–{s1}", "",
             "Kvantilregresjon av log(resultat) på år; prosent bedre per tiår med 95 % konfidensintervall. "
             f"Nivå = snitt av årsmedianene {t0}–{t1} og {s0}–{s1} (sekunder for løp, meter ellers). "
             "Signifikans: \\* p < 0,05, \\*\\* p < 0,01, \\*\\*\\* p < 0,001.", "",
             "| Øvelse | Klasse | n | Median, % per tiår [KI] | Topp (beste desil), % per tiår [KI] "
             f"| Median {t0}–{str(t1)[2:]} → {s0}–{str(s1)[2:]} |",
             "|---|---|---:|---|---|---|"]
    for _, r in t.iterrows():
        nivaa = f"{niva(r['median_tidlig'])} → {niva(r['median_sent'])}" \
            if pd.notna(r["median_tidlig"]) else ""
        lines.append(
            f"| {r['ovelse']} | {LABEL[r['gruppe']]} | {int(r['n'])} "
            f"| {no(r['median_pct_tiaar'], sign=True)} [{no(r['median_ki_lo'])}; {no(r['median_ki_hi'])}]{stjerne(r['median_p'])} "
            f"| {no(r['topp_pct_tiaar'], sign=True)} [{no(r['topp_ki_lo'])}; {no(r['topp_ki_hi'])}]{stjerne(r['topp_p'])} "
            f"| {nivaa} |")
    (TAB / "vedlegg_trender.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"skrev {len(t)} rader til tables/vedlegg_trender.md")


if __name__ == "__main__":
    main()
