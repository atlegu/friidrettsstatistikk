# DATA_AUDIT — A3 «Does starting age predict who stays?»

Audit startet 30.10.2026 etter `paper-data-audit`-skillen. Status 30.10.2026: fase 0–7 ferdig, teksten omskrevet (fase 6 nederst), fryst (`FREEZE.md`).

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

## Fase 2–4 (30.10.2026) — retting, uavhengig implementasjon, tallsporing

- **A3-2 (kvantifisert):** 33 debuter er forskjøvet av ekskluderte tidligere rader: 8 fra resultater før fylte 10 og 25 fra ikke-godkjente resultater (`r1_debutforskyvning.csv`). Teksten er oppdatert.
- **Dobbel avrunding (rettet):** Full presisjon lagres og avrundes én gang ved visning.
- **Tabeller fra kode:** t1–t4 og s1–s3 genereres av `06_manustabeller.py`. S1 bruker sekvensiell flyt (731 med debut ≥ 17 blant dem med kjent kjønn).
- **Uavhengig R** (`audit/uavhengig.R`) reproduserer utvalg, logit, retention og Cox. `audit/sammenlign.py` passerer.
- **Tallsporing** (`audit/kontroll_tall.py`) passerer: 112 punkter, inkludert svarbrev og sitater.

## Fase 7 (30.10.2026) — uavhengige agenter, verifisert med egen kode

**Data:** Sonetvillingene (D1) og de eksakte dublettene (D3) i A1/A6 berører ikke A3. Det finnes ingen sonehopp ved 20 år eller eldre, og debut og volum bruker datoer. Kontrollert mot A1-uttrekket: av 449 A3-seniorer som kan kontrolleres, mister ingen status når kopiene fjernes. A3-uttrekket har ikke øvelse og resultat, så eksakte dubletter kan ikke fjernes direkte; virkningen er null der den kan måles.

**D4 Dekning 2011.**
- Stevner med resultater i juni, august og september var 164, 118 og 143 i 2011, mot 238, 197 og 201 i 2012.
- Kull 2001 har lavest andel debut ved 10 år (32,6 %, mot 36–42 % i kull 2002–2005). «No left truncation» og «measured exactly» er for sterkt.
- H1 uten 2001-kullet: OR 0,60 / 0,51 / 0,74 / 0,63 / 1,05 / 1,84 for debut 11–16, trend 0,995.

**Statistikk (krever Atles beslutning om tekst; alternativene i `07_audit_alternativer.py` → `tables/audit/`):**
- **KM med forsinket inngang (A3-1):** Estimatoren er ugyldig når frafallsrisikoen avhenger av tid siden debut. Direkte andel aktiv ved 20 år (kull 2001–2004) er 4,2 / 3,3 / 4,5 %, mot KM 2,7 / 1,7 / 1,3. Ved 16 år er de direkte andelene 14,0 / 13,7 / 31,0 %.
- **Høyre arm av U-en (A3-2):** Den forklares av avstanden til den faste utfallsalderen. Ved lik karrierelengde (minst to konkurransedager i et år minst fire år etter debut) faller andelen fra 20,4 % (debut 10) til 4,5–6,6 % (14–16), justert OR 0,70 per år (0,68–0,73). Etter fem og seks år er OR 0,69 og 0,66.
- **Cox på alderskala, HR 1,32 (A3-3):** Proporsjonalitetsantakelsen er brutt per konstruksjon, og alder = debutalder + varighet.
- **«The U is formal» (A3-4):** LR-testen viser bare ikke-linearitet.
- **Fødselskvartal-interaksjonen (A3-5):** Utvalget er selektert. 98,5 % av seniorene har fødselsdato, mot 51,9 % av de andre; andelen er 39 % ved debut 10 og 94 % ved debut 16.
- **Mindre punkter:** H3-ordbruk; «altered nothing material» ved siden av p = 0,03; følsomhetsanalyse for manglende kjønn (549 i primærkullene, konsentrert ved debut 10–12).

## Fase 6 (30.10.2026) — omskriving etter Atles beslutning

Atle godtok punkt 14–19 i `../AUDIT_2026-10-30_endringsrapport.md`. Svarbrevet oppdateres ikke (Atles beskjed); `manus/RESPONSE_PANEL1.md` er historisk.

- **Nye analyser** i `05b_revisjon_r2.py` (tidligere `07_audit_alternativer.py`) → `tables/modeller/r2_*.csv`:
  - direkte andeler aktive etter alder (ny figur 3, `figures/fig3_shares_by_age.png`);
  - lik karrierelengde som medprimært utfall (minst to konkurransedager i en sesong minst D år etter debut, D = 4, 5, 6);
  - H1 uten 2001-kullet;
  - følsomhet for ukjent kjønn, der klubbstørrelsen telles over alle debutanter (OR 0,98 → 0,99, teksten rettet);
  - seleksjonen i fødselskvartal-analysen.
- **Tatt ut:** Kaplan–Meier med forsinket inngang (figur 3) og Cox på alderskala (04, 05).
- **Tabeller:** t2 (to utfall), t4 og s4 fra `06_manustabeller.py`.
- **Uavhengig R** speiler de nye analysene (debutgrunnlag, varighetsutfall D = 4–6, uten 2001, ukjent kjønn, andeler etter alder). `audit/sammenlign.py` passerer.
- **Tallsporing:** `audit/kontroll_tall.py` er skrevet om etter den nye teksten; 93 ankrede sjekker, 0 feil, 0 udekkede tall. Brevdelen er fjernet.
- **Ordtelling:** ~4 100 (skript).

## Fase 5 — RUN_ALL.sh

`RUN_ALL.sh` (`set -eo pipefail`, hashkontroll mot FREEZE-filene, `SOURCE_DATE_EPOCH`) kjører 01, 02, 03, 04, 05, 05b og 06, full LaTeX-syklus med kontroll av udefinerte referanser og «??», deretter uavhengig R, sammenligning og tallkontroll. Grønn og deterministisk 30.10.2026 (to kjøringer gir like hasher på alle utdata).

## Fase 8 (30.10.2026) — siste smale gjennomgang

En uavhengig agent gikk gjennom definisjoner, noter og påstander (`final_review_A3.md` i øktens kladdemappe). Hvert funn er verifisert med egen kode.

- **Ordlyd rettet:**
  - LR-testen er merket som lagt til etter planen;
  - Q4-underskuddet erstatter den usanne Q1-påstanden;
  - 2020-sesongen er «COVID-disrupted», ikke «cancelled»;
  - det relative gapet er presisert;
  - datoen er «October 2026»;
  - formen på gradienten ved lik karrierelengde er beskrevet (bratt fall 10→14, flat etter 14), og «persisted least» er rettet;
  - kausal ordbruk er dempet;
  - første-sesong-ordlyden er presisert;
  - «replicated three times» er dempet;
  - avvik fra planen er opplyst.
- **Typografi:** caption-pakken er lagt inn, så PDF-en ikke lenger viser «Table 5: *».
- **Status:** 102 ankrede sjekker, 0 feil, 0 udekkede tall.
- **Atles beslutning:** debut-16-armen hviler på debutanter fra koronaårene (uten debuter i 2020–21: OR 1,32, 0,79–2,19). Se endringsrapportens avsnitt 8.

## Debut-16-armen og formkravene, Atles beslutning 30.10.2026 («Gjør det andre»)

- **Ny analyse (lagt til etter planen):** `05b_revisjon_r2.py::covid_debut16` → `r2_covid_kategorisk.csv`, `r2_covid_lrt.csv`, `r2_debut16_covid.csv`; speilet i R, og `sammenlign.py` passerer.
  - Alle 107 debut-16-utøvere i kull 2004–2005 debuterte i 2020–2021. 10,3 % ble seniorer, mot 5,4 % av de 317 andre.
  - Debut 16 mot 10 uten koronadebuter: OR 1,32 (0,79–2,19). Med koronaflagg: 1,38 (0,86–2,19).
  - Kohorthalvdelene gir 1,35 (0,80–2,26) mot 3,08 (1,59–5,96). Ikke-lineariteten holder uten koronadebuter (LR 30,5, p = 1,2e-5) og i begge halvdeler.
- **Tekst:**
  - Debut 16 er tatt ut av sammendraget.
  - Results, tabell 2 og 4, Principal findings, avsnittet om hva marginen kan teste, Strengths og Perspective sier at forhøyelsen ved 16 hviler på koronadebutene.
  - Methods opplyser at koronavariantene på kategorisk koding er lagt til etter planen.
- **Formkrav (SJMSS):**
  - Sammendraget har 242 ord (grense 250).
  - S1–S4 ligger i egen fil `manus/supplement.tex`, med S2 og S3 nummerert etter første sitering.
  - Figurfilene har trykkrekkefølgens nummer (`fig3_retention_k`, `fig4_shares_by_age`).
  - Tabellene har forkortelsesnoter.
- **Status:** `RUN_ALL.sh` er grønn, og to kjøringer ga like hasher på alle 52 utdatafiler. Kontrollen ga 125 ankrede sjekker (123 i manus, 2 i supplementet), 0 feil og 0 udekkede tall. Kontrollen teller også ordene i sammendraget.
