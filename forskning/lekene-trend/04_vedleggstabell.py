"""
04_vedleggstabell.py - Lager vedleggstabellen til 03_vurdering.md fra tabellene,
slik at ingen tall i vedlegget er skrevet for hånd.

Inn: tables/trender_per_serie.csv, tables/nivaa_tidlig_sent.csv
Ut:  tables/vedlegg_trender.md
"""

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
    niv["ovelse_kort"] = niv["ovelse"].str.replace(r" \(.*\)", "", regex=True)
    t = t.merge(niv[["ovelse_kort", "gruppe", "median_2012_14", "median_2023_25"]],
                left_on=["ovelse", "gruppe"], right_on=["ovelse_kort", "gruppe"], how="left")
    t["_o"] = t["ovelse"].map(ORDER.index)
    t = t.sort_values(["_o", "gruppe"])
    lines = ["# Vedlegg: trend per øvelse og klasse, lekene 2012–2025", "",
             "Kvantilregresjon av log(resultat) på år; prosent bedre per tiår med 95 % konfidensintervall. "
             "Nivå = snitt av årsmedianene 2012–2014 og 2023–2025 (sekunder for løp, meter ellers). "
             "Signifikans: \\* p < 0,05, \\*\\* p < 0,01, \\*\\*\\* p < 0,001.", "",
             "| Øvelse | Klasse | n | Median, % per tiår [KI] | Topp (beste desil), % per tiår [KI] | Median 2012–14 → 2023–25 |",
             "|---|---|---:|---|---|---|"]
    for _, r in t.iterrows():
        nivaa = f"{niva(r['median_2012_14'])} → {niva(r['median_2023_25'])}" \
            if pd.notna(r["median_2012_14"]) else ""
        lines.append(
            f"| {r['ovelse']} | {LABEL[r['gruppe']]} | {int(r['n'])} "
            f"| {no(r['median_pct_tiaar'], sign=True)} [{no(r['median_ki_lo'])}; {no(r['median_ki_hi'])}]{stjerne(r['median_p'])} "
            f"| {no(r['topp_pct_tiaar'], sign=True)} [{no(r['topp_ki_lo'])}; {no(r['topp_ki_hi'])}]{stjerne(r['topp_p'])} "
            f"| {nivaa} |")
    (TAB / "vedlegg_trender.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"skrev {len(t)} rader til tables/vedlegg_trender.md")


if __name__ == "__main__":
    main()
