"""
a1_tyrving.py — A1: Tyrving-skåring med den validerte modulen (tyrving_r2.py) og komplett
kobling av øvelseskoder til tabellens spesifikasjoner.

tyrving_r2._SPEC mangler koblingen for flere standardredskaper og -øvelser som
parametertabellen har rader for ved 13–16 år. Uten kobling returnerer modulen None, så
16-årige gutters kule 5 kg, diskos 1,5 kg, slegge 5 kg og spyd 700 g, jentenes spyd 500 g
(15–16) og liten ball 150 g (13–14) ble aldri poengsatt: mannlige kastere hadde null
poengsatte resultater ved 16 år (audit 30.10.2026, datafunn D2). Modulen i ncc-kohort er
fryst for IJSSC og endres ikke; utvidelsen gjelder bare A1. Spesifikasjonen må fortsatt
stemme med tabellraden for utøverens kjønn og alder, så en kode gir bare poeng der
tabellen har en norm.
"""

import sys

sys.path.insert(0, "/Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/Statistikk/"
                   "forskning/ncc-kohort/revision_r1/analysis")
import tyrving_r2 as _t  # noqa: E402

EKSTRA_SPEC = {
    "kule_5kg": ("Kule", "5kg"), "diskos_1_5kg": ("Diskos", "1,5kg"),
    "spyd_500g": ("Spyd", "0,5kg"), "spyd_700g": ("Spyd", "0,7kg"),
    "slegge_50kg/120cm": ("Slegge", "5kg/120cm"), "liten_ball_150gram": ("Liten ball", "150g"),
    "80mh_76_2cm": ("80 m hekk", "76,2cm"), "100mh_84cm": ("100 m hekk", "84,0cm"),
    "100mh_91_4cm": ("100 m hekk", "91,4cm"),
    "300mh_76_2cm": ("300 m hekk", "76,2cm"), "300mh_84cm": ("300 m hekk", "84,0cm"),
    "1500mhinder_76_2cm": ("1500 m hinder", "76,2cm"),
    "2000mg": ("2000 m", "Kappgang"), "kappgang_2000_m": ("2000 m", "Kappgang"),
    "3000mg": ("3000 m", "Kappgang"), "kappgang_3000_m": ("3000 m", "Kappgang"),
    "kappgang_5000_m": ("5000 m", "Kappgang"), "kappgang_10000_m": ("10000 m", "Kappgang"),
}
EKSTRA_MSS = {"1500mhinder_76_2cm", "2000mg", "kappgang_2000_m", "3000mg", "kappgang_3000_m",
              "kappgang_5000_m", "kappgang_10000_m"}

_t._SPEC.update(EKSTRA_SPEC)
_t._MSS_CODES.update(EKSTRA_MSS)

beregn_tyrving_poeng = _t.beregn_tyrving_poeng
parse_tyrving_xls = _t.parse_tyrving_xls
