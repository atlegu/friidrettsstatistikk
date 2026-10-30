# DATA_AUDIT — A3 «Does starting age predict who stays?»

Audit startet 30.10.2026 etter `paper-data-audit`-skillen. Status: fase 0–1 ferdig; funn nederst.

## Fase 0 — Inventar

Alle data leses fra `data_private/` (frosset uttrekk 29.10.2026, 20:45–20:48 UTC, `00_uttrekk.py` mot Supabase `lwkykthpnthfcldifixg`). Ren deltakelse: resultatfilen har kun id, athlete_id, meet_id, club_id, date, status — ingen prestasjonskolonner.

| Fil | sha256 |
|---|---|
| analysedata.csv | 20b0ccad2dd41f8ef9b245b7c960f3741843a6ffb5becb8f7967df3da64899ce |
| arsvolum.csv | 20c8e605602081d114672a3f84c4904cc648cc770c6571e857f8c4bca6a022ab |
| clubs.csv | 156e04f08c1e0aeb25017daf051a3b0b6b2276f70c4a1f9d620514ac7da9b188 |
| meets.csv | 56dbb1bdf7c70f8023020c7fb27c458758898e7af1d06400e487af0f640e6b24 |
| resultater.csv | f3ee0b77c7664dd9a1760f0c533884ca086c716464051d02436d407d1a2cb82a |
| utovere.csv | 76cf9659376b932c76c5aa4234db8e77b130522692ca31c87f64e3a1fecd8231 |
| flyt.json | 5fa796085c026275fa9c037846248033c364c56c0c1367ba3d6bb3f6901e2d47 |
| uttrekksinfo.json | 5617e07b1c689bf32c1c0a6de29590fcf08854b696e31aede2969e689566de56 |

**Fullstendighet mot kilden (kontrollert mot levende base 30.10.2026):** utøvere født 2001–2008: 33 666 = basen (eksakt). Resultater per kull 2011-01-01–2026-10-29: alle åtte kull eksakt like basen (sum 675 707). Ingen drift siden frysing.

**Dekning:** kull 2001 er 10 år i 2011 (registerstart) → ingen venstresensur for debut ved 10+. Primærkull 2001–2005: alder 20 fullt observert t.o.m. 2025 for alle; 2026 (t.o.m. 29.10) gir det yngste kullet et noe kortere seniorvindu — adressert med kohortkovariat + kohortsplitt (står i §2). Debutår 2020–21 mulig først fra alder 14 i primærkullene (tabellnote i manus).

## Fase 1 — Kode mot metodetekst

| Sjekkliste | Koden (01_variabler.py) | Teksten | Status |
|---|---|---|---|
| Debutdefinisjon | første OK-resultat ETTER at rader med alder<10 er fjernet (116 rader) → debut = første resultat fra fylte 10 | «first approved registered result (10–16)» | OK (presist implementert; få/ingen reelle <10-debuter — se A3-2) |
| Tidsorigo | debutår/debutalder på kalenderår | lik | OK |
| Høyresensur | retention-k med per-k-nevnere observerbare t.o.m. 2025; Cox sensurerer aktive 2025–26; exit krever to hele tomme år | lik | OK |
| Identitet | analysedata 27 474 = unike athlete_id; arsvolum unik på (athlete_id, alder) | — | OK |
| Landmark (H3) | analysedata-kolonnen `aktiv17` er runde 1-definisjonen (alder≥17, betinger på fremtiden); manusets H3 bruker korrigert sett fra 05_revisjon_r1.py (resultat i 17-årssesongen) | §2 beskriver den korrigerte | OK (sporbarhet dokumentert her; se A3-3) |
| Volum | dager = nunique(date) per athlete×alder | lik | OK |
| COVID | covid_debut 2020–21; robusthet ekskluderer/flagger | lik | OK |
| Parsing | coerce på birth_date; Int64-kvartal | — | OK |
| **Region** | modal krets i debutsesongen — meets.krets tomt for 99,1 % → region NA for 27 419 av 27 474, fillna «ukjent» = konstant → null numerisk effekt | §2 hevder «region (modal competition district in the debut season; **18 districts plus unknown**)»; H1 «adjusted for sex, cohort, region, and club size» | **FUNN A3-1** |

## Funn

1. **A3-1 (tekst mot kode, må rettes):** region-kovariaten er vakuøs (konstant), og formuleringen «18 districts plus unknown» er ikke sann for noen fil i prosjektet — feltet finnes ikke i registeret (meets.krets 0,9 % utfylt; clubs uten geografi). Fjerning endrer ingen estimater (verifiseres i fase 3). Retting: fjern region fra §2 og tabellnoter/-tekster; begrensningsavsnittet («geography … none of which the registry measures») blir da konsistent i stedet for selvmotsigende.
2. **A3-2 (kvantifiseres i fase 3):** antall utøvere med reelt første resultat før fylte 10 (debut forskjøvet til 10+) telles og dokumenteres her; ventet ≤ noen titalls (116 rader totalt under 10).
3. **A3-3 (info):** `aktiv17`-kolonnen i analysedata er runde 1-sporet; manusets tall kommer fra 05_revisjon_r1.py. R-reimplementasjonen bygger landmarken fra manusdefinisjonen og skal reprodusere r1-tallene.
