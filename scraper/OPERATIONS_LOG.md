# Operasjonslogg — Scraper

Logg over alle kjøringer som endrer data. **Oppdater denne filen etter hver operasjon.**

Format: Dato, script, parametre, resultat, eventuelle problemer.

---

## 2026-08-24/25 — Utendørs 2026 verifisert, og NM-medaljer koblet til utøvere

### Utendørssesongen 2026 mot kilden

- **Script:** `update_results.py --outdoor --season 2026 --from-date 2026-04-01 --verify`
- **598 stevner kontrollert — 224 var ufullstendige.** Det er 37 %, mot 23 %
  innendørs. Terskelen på ti resultater har altså skjult et stort etterslep.
- 6 971 resultater skrapet, **4 517 nye importert**, 2 270 lå allerede inne.
  107 nye utøvere opprettet. 144 falt ut på umappet øvelse, 19 feilet.

Base etter kjøring: 1 418 058 resultater (+4 517), 87 492 utøvere,
43 818 i sesong 2026.

### NM-medaljer koblet til utøvere

- **Script:** `link_championship_medals.py --apply --yes` (dry-run først)
- **Utgangspunkt:** 5 102 av 13 609 medaljer manglet `athlete_id` og vistes
  derfor ikke på utøverprofilen.
- **Metode:** navn normalisert (aksenter foldet, tegnsetting fjernet), og
  treffet må være entydig. Utøveren må dessuten plausibelt kunne tatt
  medaljen: kjønn må stemme der begge kilder har det, og utøveren må ha
  resultater innenfor ±5 år av mesterskapet eller et fødselsår som gir alder
  mellom 15 og 55. To personer med samme navn er vanlig nok i norsk friidrett
  til at gjetting ikke forsvares — en feilkoblet medalje er verre enn en
  ukoblet.
- **Resultat:** 1 080 medaljer koblet, fordelt på 312 utøvere.
  Koblet totalt 8 507 → **9 587**. Utøvere med medalje 1 772 → 1 997.

**Står igjen, 4 022 ukoblede:**

| Årsak | Antall |
|---|---:|
| Ingen utøver med det navnet i basen | 3 889 |
| Ingen kandidat passer i tid | 90 |
| Flere kandidater — ikke entydig | 43 |

2 245 av de ukoblede er fra før 1970, der resultatdataene i praksis ikke
finnes. Det er forventet. De 1 777 fra 1970 og senere er en reell restanse
som krever navneopprydding eller manuelt arbeid.

### Rettet: årstall 2923

Tre medaljer i NM maraton kvinner hadde årstall `2923`. Kilden
(`epi-new.nif.no/.../kmar.htm`) er nå borte (404), så det ble avgjort med
interne data: medaljeserien har 2019, 2021, 2022 og hopper så til «2923» —
**2023 manglet helt** — og både Kristin Waaktaar Opland og Siri Schøne Ness
konkurrerte i 2023. Rettet til 2023. Basen har nå ingen medaljer med
årstall utenfor 1890–2026.

### GJENSTÅR

- `--verify` er bare kjørt på 2026. **Tidligere sesonger er ikke kontrollert**,
  og terskelfeilen har ligget der hele tiden.
- 144 + 42 resultater falt ut på umappede øvelser i de to kjøringene.
- 1 777 medaljer fra 1970 og senere er fortsatt ukoblet.

---

## 2026-08-22 — Delvis importerte stevner funnet og hentet inn

- **Utløser:** Lina Svarlien manglet hele innendørssesongen 2026. Kilden viste
  Høyde 1,75 og Kule 4,0 kg 10,93 fra Norgeslekene 25.01.2026; basen hadde
  ingenting for henne i januar–mars.
- **Årsak:** Feilen lå ikke i utøveren, men i stevnet. «Hvam, Norgeslekene»
  hadde **188 resultater i basen mot 539 i kilden**. Hele øvelser manglet —
  800 m, 400 m og stav var ikke importert i det hele tatt, og 60 m hadde 48
  av 151.

### Rotfeil: terskelen fanget bare tomme stevner

`find_missing_meets()` regnet et stevne som ufullstendig kun hvis det hadde
færre enn `MIN_RESULTS_THRESHOLD = 10` resultater. Norgeslekene lå langt over,
og ble derfor aldri hentet på nytt selv om to tredjedeler manglet. Terskelen
fanger tomme stevner, men er blind for delvis importerte.

### Ny `--verify`-modus

`finn_ufullstendige_mot_kilden()` henter hvert kildestevne og teller radene i
stedet for å bruke en fast terskel. Et stevne hentes på nytt når mer enn 5 %
av resultatene mangler (`VERIFY_MANGEL_ANDEL`). Terskelen er ikke null fordi
basen noen ganger slår sammen to kildestevner til én stevnerad, og da har vi
legitimt flere rader enn kildestevnet.

Koster ett HTTP-kall per stevne, så den kjøres bare med `--verify`:

```bash
python update_results.py --indoor --season 2026 --from-date 2026-01-01 --verify
```

### Resultat for innendørssesongen 2026

| | |
|---|---|
| Stevner kontrollert | 244 |
| Ufullstendige | **56** |
| Resultater skrapet | 11 268 |
| Nye resultater importert | **1 511** |
| Allerede i basen (hoppet over) | 9 676 |
| Feil | 30 |
| Umappede øvelser | 42 |

Verstingene: Norgeslekene manglet 351, Opent KM for Møre og Romsdal 258,
Innendørsstevne 2 Haugesund 69, Distriktskampen 58, Januarsprint 51,
Masters innendørs II 40.

Norgeslekene 188 → 726 resultater. Lina Svarlien har nå både Høyde 1,75 og
Kule 4,0 kg 10,93, som stemmer med kilden.

Base: 1 413 541 resultater (+1 518), 87 385 utøvere, 39 301 i sesong 2026.

### GJENSTÅR

- **Kjør `--verify` på utendørssesongen 2026 og på tidligere år.** Det er
  ingen grunn til å tro at dette er begrenset til én sesong. Terskelen på ti
  har vært der hele tiden.
- 42 resultater falt ut på umappet øvelse: Kappgang 1000 m, Kappgang 2000 m og
  «7 Kamp (60m-Lengde-Kule-Høyde-60mhekk-Stav-1000m)». De to første finnes i
  `EVENT_NAME_TO_CODE`, så her er det trolig navnevariasjon i kilden.
- 30 rader feilet ved innsetting og bør undersøkes.

---

## 2026-08-21 — Enkeltrettelse: femkampsum importert som 60 meter

- **Symptom:** Malene Kollberg hadde et resultat «60 meter: 3904» fra
  NM-UM mangekamp innendørs 17.01.2026, med `performance_value = NULL`.
- **Årsak:** Femkampens poengsum (3904) er importert både som femkampresultat
  (korrekt, `5kamp`) og som en flat 60 meter. Femkamp innendørs for kvinner
  består av 60 m hekk, høyde, kule, lengde og 800 m — det finnes ingen flat
  60 meter i øvelsen, så raden kunne ikke være ekte.
- **Utført:** raden slettet (`34990be3-2732-49b5-956a-c29265ac3393`).

### Samme mønster finnes 37 andre steder

877 resultater har et tresifret til femsifret heltall i `performance` og
`performance_value = NULL` på en øvelse som ikke er poengbasert. Av disse har
**38** en identisk mangekampsum registrert på samme utøver og samme stevne —
altså samme duplisering som hos Kollberg (29 på løpsøvelser, 9 på tekniske).

De øvrige ~839 er noe annet: mangekamper der øvelsens `result_type` er satt til
`distance` i stedet for `points`. Da er ikke dataene feil, men
øvelseskonfigurasjonen. Begge deler gjenstår.

---

## 2026-08-21 — Ugyldige fødselsår og feil århundre i stevnedato (DELVIS)

- **Script:** `fix_ugyldig_alder.py --apply --yes` (fire dry-run-runder først)
- **Utgangspunkt:** 333 resultater ga umulig alder (under 5 eller over 100 år)
  når man regner konkurranseår minus fødselsår.

### Metodefeil rettet underveis — les denne

**1. Fast årstallsgrense flagget ekte utøvere.** Første forsøk brukte
«fødselsår < 1890» som feilkriterium. Det flagget 8 ekte utøvere født
1878–1889 — blant dem Ferdinand Bie og Edvard Larsen, som konkurrerte rundt
1912. Kriteriet ble byttet ut med en prinsipiell test: er fødselsåret forenlig
med utøverens EGNE resultater? Alder mellom 5 og 100 år godtas.

**2. Paginering uten sortering mistet rader.** `fetch_all()` brukte
`.range()` uten `order by`. PostgREST garanterer da ikke stabil rekkefølge, og
over 1,4 millioner resultatrader ble rader hoppet over — konkret forsvant
Kasper Ellingsens rad, den vi visste skulle være der. Rettet til nøkkelbasert
paginering (`order('id')` + `gt('id', forrige)`). **Dette mønsteret finnes i
flere av vedlikeholdsskriptene og bør rettes der også.**

**3. Automatisk sammenslåing på navn var for aggressiv.** Første regel slo
sammen enhver navnetvilling med gyldig fødselsår. Den foreslo blant annet
«Sondre Loftås Kåstad (2013) → 1996» og «Reidar Jørgensen (1953) → 1904» —
sannsynligvis to forskjellige personer med samme navn. Regelen ble strammet
til å kreve at det ødelagte årstallet er en *forvansket utgave* av det ekte
(ett siffer feil, ombyttede sifre, eller avkortet), eller at verdien er 0.

### Utført

| Tiltak | Antall |
|---|---:|
| Stevnedatoer med feil århundre rettet (1926 → 2026) | 4 stevner, 28 resultater |
| Fødselsår utledet fra `birth_date` (Marianne Vikne 1867 → 1967) | 1 |
| Dubletter slått sammen (752→1952, 1070→1970, 9171→1971, 9194→1994, 0→…) | 10 |
| Fødselsår satt til NULL (ukjent er ærlig, 0 er en løgn) | 38 |
| **Kasper Ellingsen** | slått sammen til én post, `birth_date` = 2003-01-20 |

De fire stevnene var «Distriktskampen», «Kengurukarusellen 1», «Nyttårsstevnet»
og «Sprintstevne», alle januar 2026 lagret som 1926. Bekreftet ved at samtlige
utøvere på dem har resultater på nøyaktig samme dato i 2026. De 14 gjenværende
1926-resultatene er ekte historiske stevner og ble ikke rørt.

### Forebygging

Databasesperre lagt inn:

```sql
alter table athletes add constraint athletes_birth_year_rimelig
  check (birth_year is null or birth_year between 1860 and 2100);
```

### GJENSTÅR — 121 utøvere krever manuell vurdering

Disse har et fødselsår som *ser plausibelt ut*, men som strider mot deres egne
resultater. Da kan feilen like gjerne ligge i et resultat, eller i at to
personer er slått sammen til én post. Det er en vurdering, ikke en regel, og de
er derfor ikke rørt. Liste:
`backups/fix_ugyldig_alder_20260821_171844_til_gjennomgang.csv`
med navn, fødselsår, første og siste resultatår og alder ved begge.

Eksempler: «A. Kvalheim» (født 1973, resultat fra 1967), «Adrian Nilsen»
(født 2009, resultat fra 2013 — 4 år gammel), «Albert Jacobsen» (født 1893,
resultat fra 2025).

---

## 2026-08-21 — Sesongoppdatering august (FULLFØRT)

- **Script:** `update_results.py --outdoor --season 2026` (dry-run først)
- **Utgangspunkt:** basen sto på 2026-08-01, tre uker av utendørssesongen manglet.
- **Første kjøring:** 29 stevner i kilden, 25 manglende. 1 246 resultater skrapet,
  1 187 importert. **44 feilet og 11 falt ut på øvelsesmapping.**

### BUG 1 FUNNET OG FIKSET: ' M'-markøren for manuell tidtaking

- **Symptom:** `invalid input syntax for type numeric: "14.9(-0.2) M"` (22P02).
  Andre varianter: `"40.0(ok) M"`, `"26.7(+0.6) M"`, `"5.01.7 M"`.
- **Årsak:** `parse_result_wind()` krevde at strengen SLUTTET med `)`:
  `re.match(r'(.+?)\(([+-]?\d+[,.]?\d*)\)$', ...)`. Kilden legger på ` M` etter
  parentesen for manuelt tidtatte løp, så regexen bommet og hele strengen ble
  liggende i `performance`. Databasetriggeren `calculate_performance_value`
  kaller `parse_performance()` som caster til numeric — og innsettingen feilet.
  Feilen var altså i scraperen, men viste seg først i databasen.
- **Fikset:** `parse_result_wind()` returnerer nå `(resultat, vind, is_manual)`.
  Den stripper ` M` først, og godtar ikke-numerisk innhold i parentesen
  (`(ok)` = godkjent uten registrert vindverdi) i stedet for å feile.
- **Bonus — vi kastet bort autoritativ informasjon:** `is_manual_time` ble ikke
  satt i det hele tatt i `update_results.py`. Kilden *forteller* oss hvilke
  resultater som er håndtidtatt; vi utledet det i stedet fra presisjon
  (CLAUDE.md punkt 7). Flagget settes nå fra kilden, men kun for øvelser der
  manuell tidtaking faktisk er mulig — løp under 800 m, 56 av 299 øvelser.
  Tekniske øvelser og 800 m+ kan aldri få flagget.
- **Testet:** åtte varianter, inkludert alle fire som feilet i produksjon.

### BUG 2 FUNNET OG FIKSET: umappet kast-femkamp

- **Symptom:** `Unmapped event: Kast 5 Kamp (Slegge-Kule-Diskos-Spyd-Vektkast)
  Veteran / Ungdom` — 11 resultater falt ut.
- **Årsak:** Øvelsene *finnes* i basen med kodene `..._veteran` og `..._ungdom`,
  men heter «Kast-femkamp Veteran» der, mens kilden bruker full beskrivelse med
  klassesuffiks. `COMBINED_EVENT_PATTERNS` traff ikke fordi navnet starter med
  «Kast 5 Kamp», ikke «5 Kamp».
- **Fikset:** tre linjer lagt til i `EVENT_NAME_TO_CODE`.

### Etter reimport

- 38 av de 55 tapte resultatene hentet inn, resten var duplikater av rader som
  allerede lå inne. 0 feil, 0 umappede øvelser.
- 6 resultater fikk `is_manual_time` fra kilden — første gang flagget settes ved
  import. 0 resultater med bokstavhale i `performance`.

### Status etter kjøring

| | |
|---|---|
| Resultater | 1 412 023 |
| Utøvere | 87 375 |
| Stevner | 47 924 |
| Klubber | 2 464 |
| Sesong 2026 | 37 755 |
| Siste stevne | 2026-08-15 |

---

## 2026-08-09 — Diagnose og backfill: utøvere uten klubb (FULLFØRT)

### Diagnose

18 432 utøvere hadde `current_club_id = NULL`. 18 386 av dem ble opprettet i
januar 2026 — altså i den opprinnelige bulkimporten, der 24,4 % manglet klubb.
De deler seg i to helt ulike populasjoner:

**A) 6 499 — klubben fantes allerede i basen.** De har resultater der
`results.club_id` er satt; koblingen var bare ikke løftet opp på utøveren.
Dette er det kjente punktet «Mangler kobling mellom athletes og
current_club_id» fra `ACTIVITY_LOG.md`.

**B) 11 423 — ingen resultater i det hele tatt.** 11 414 av dem har
`external_id`, altså står de i kildens utøverregister. 11 093 er født i 2000
eller senere.

**Hypotesen ble testet mot kilden, ikke antatt.** Fire tilfeldige utøvere ble
slått opp på `UtoverStatistikk.php`, både utendørs og innendørs:

| Utøver | Utendørs | Innendørs |
|---|---|---|
| Hermine Sofie Stende (40389) | tom | tom |
| Hanne Tufta (14711) | tom | tom |
| Peter M Nyen (25530) | tom | tom |
| Lara Elise Gúl (20408) | tom | — |

Positiv kontroll (id 6895) ga 15 rader, så metoden fanger resultater når de
finnes. **Konklusjon: de er tomme i kilden også.** Dette er ekte personer i
utøverregisteret uten registrerte resultater — ikke importrester.
**De skal ikke slettes.**

Merk for NFIF-arbeidet: differansen mellom registrerte og aktive utøvere er
direkte §12-materiale (rekruttering), og grensetilfellet treffer §6-skillet
mellom prestasjonsstatistikk og *registrert aktivitet*. Anbefalt håndtering er
å skille på «utøvere med resultater» i lister og tellinger, ikke å skjule dem.

### Backfill (gruppe A)

- **Script:** `backfill_current_club.py --apply --yes` (dry-run kjørt først)
- **Metode:** klubb hentes fra utøverens *nyeste* resultat med klubb, slik at
  den som har byttet klubb får den siste. Ingen data hentet utenfra.
- **Resultat:** 6 499 utøvere oppdatert, fordelt på 455 klubber.
  Utøvere uten klubb 18 432 → 11 933.
  Kontroll: 0 gjenstående backfillbare, 0 som peker på slettet klubb,
  utøver- og resultattotal uendret.
- **Står igjen:** 11 423 uten resultater (gruppe B, urørt) + 510 som har
  resultater, men uten klubb på noen av dem. De siste må hentes fra kilden.
- **Sikkerhetskopi:** `backups/backfill_current_club_20260809_200013.json`
  (feltet var NULL for alle før kjøring; angring er å sette tilbake til NULL).

---

## 2026-08-09 — Sammenslåing av dublette klubber (FULLFØRT)

- **Script:** `merge_duplicate_clubs.py --apply --yes` (dry-run kjørt to ganger først)
- **Omfang:** Klubber som er identiske når tegnsetting, mellomrom og
  bokstavstørrelse ignoreres. 34 grupper, 41 overtallige klubbrader.
- **Resultat:**
  - 348 resultater og 52 utøvere flyttet til den beholdte klubben
  - 41 klubbrader slettet — klubber 2 505 → 2 464
  - 1 klubbnavn korrigert: «Leksvik Il» → «Leksvik IL»
  - Kontroll etterpå: 0 gjenstående dubletter, 0 døde klubbreferanser,
    resultattotal uendret (1 410 798).
    «IL i BUL Tromsø» 19 154 → 19 253, som er summen av de fem variantene.
- **Valgregler:** Raden som beholdes er den med flest resultater (færrest rader
  å flytte). Navnet som beholdes er *samme* variant, med kun bokstavstørrelse
  rettet på entydige klubbforkortelser (IL, IF, IK, SK …).
- **Lærdom — første heuristikk var for smart:** en scorefunksjon som belønnet
  mellomrom foreslo «IL Stjørdals-Blink» → «IL Stjørdals- Blink» og
  «IL Norna-Salhus» → «IL Norna Salhus». Regelen ble byttet ut med den
  konservative varianten over. **Aldri finn opp en skrivemåte som ikke
  allerede finnes i basen.**
- **Ytelse:** første versjon hentet alle 1,4 mill. resultatrader for å telle
  (4+ minutter). Endret til å telle kun for klubber i dublettgrupper — 8 sekunder.
- **Sikkerhetskopi:** `backups/merge_duplicate_clubs_20260809_192616.json`

### IKKE GJORT — krever domenevurdering

Klubber der det ene navnet er et prefiks av det andre ble bevisst *ikke* rørt.
Kartleggingen viser at klassen er en blanding:

- **Samme klubb, «Friidrett»-suffiks** (8+ par): «Kongsvinger IL» /
  «Kongsvinger IL Friidrett», «Førde IL» / «Førde IL Friidrett», «Rena IL» /
  «Rena IL Friidrett», «Kragerø IF» / «Kragerø IF Friidrett», m.fl.
  Bør trolig slås sammen, men er en avgjørelse om hvorvidt friidrettsgruppa
  skal være egen enhet.
- **Helt ulike klubber som ligner** (må IKKE slås sammen): «IL Sand» /
  «IL Sandvin», «IL Nor» / «IL Norodd» / «IL Nordlys» / «IL Norrøna»,
  «IL Fri» / «IL Fri-Kameratene», «IL Try» / «IL Trysilgutten»,
  **«IL i BUL» (Oslo) / «IL i BUL Tromsø»**.
- **Reelt tvetydig:** «Eidsvåg IL, Romsdal» og «Eidsvåg IL, Åsane» er to ulike
  klubber — og «Eidsvåg IL» (153 res.) kan være enten.

---

## 2026-08-09 — Reparasjon av mangekamp-korrupsjon (FULLFØRT)

- **Script:** `fix_mangekamp_korrupsjon.py --apply --yes` (dry-run kjørt først)
- **Symptom:** Klubbregisteret inneholdt 133 «klubber» med navn som «01», «61»,
  «55-DNF». Synlig som søppel i klubboversikten på nettsiden.
- **Årsak:** Importparseren for mangekampstevner splittet ikke kolonnene. Hele
  strengen `"Navn, Klubb<delresultater>"` havnet i `athletes.full_name`, og halen
  av strengen ble opprettet som egen klubb. Eksempel:
  `"Maiken Rose Bjerknesli, IL i BUL14,23-7,40-16,56-14,43-4"` med klubb `"61"`.
  Hver slik rad skapte en falsk utøverpost med nøyaktig ett resultat.
- **Omfang:** 660 falske utøverposter, 133 falske klubber, 660 berørte resultater.
- **Metode:** Ekte navn og klubb ble trukket ut av den korrupte strengen,
  ekte utøver slått opp på navn + fødselsår, resultatet flyttet dit.
  Nasjonalitetskoder som `(DEN)`, `(GER)`, `(SWE)` ble strippet før oppslag.
- **Resultat:**
  - 318 resultater flyttet til riktig utøver og klubb
  - 275 duplikatresultater slettet (fantes allerede korrekt importert)
  - 656 falske utøverposter slettet — utøvere 88 016 → 87 360
  - 131 av 133 falske klubber slettet — klubber 2 636 → 2 505
  - Resultater 1 411 073 → 1 410 798. Ingen foreldreløse resultater.
- **Står igjen, krever manuell vurdering (4 poster, 2 klubber):**
  - «Siv Sundt (12)» — strengen mangler komma å dele på
  - «Alfred Lund Stende» (2 rader) — 4 navnelike utøvere i basen
  - «Linnea Elise Westre» — 3 navnelike utøvere i basen
- **Første kjøring stoppet** etter 63 rader på unik-constrainten
  `results_innhold_unik`. Det avdekket at 275 av postene var rene duplikater.
  Skriptet ble endret til å la databasen avgjøre: ved 23505 slettes duplikatet
  i stedet for å flyttes. Ingen data gikk tapt.
- **Sikkerhetskopi:** `backups/fix_mangekamp_korrupsjon_20260809_18*.json`
  (alle berørte utøvere, resultater og klubber før endring).
### ROT-ÅRSAK FUNNET OG FIKSET

- **Skyldig:** `import_youth_stats.py` linje 462 (kjørt mai 2026 — 659 av de 660
  korrupte radene ble opprettet da). *Ikke* `update_results.py`; dagens kilde på
  `StevneResultater.php` leverer navn og klubb i separate kolonner og er ren.
- **Feilen:** `name_club_text.rsplit(',', 1)`. Cellen har formen `"Navn, Klubb"`,
  men for mangekamp limes delresultatene på i samme celle med komma som
  desimaltegn. `rsplit` tok da *siste* komma:

      "Maiken Rose Bjerknesli, IL i BUL14,23-7,40-16,56-14,43-4,61"
        -> navn  = "Maiken Rose Bjerknesli, IL i BUL14,23-7,40-16,56-14,43-4"
        -> klubb = "61"

- **Fikset:**
  1. `split(',', 1)` — splitter på *første* komma. Strengt tryggere enn `rsplit`
     også for klubbnavn som inneholder komma.
  2. Ny `strip_combined_event_results()` kutter påhengte delresultater fra
     klubbnavnet. Kutter på desimaltall (`14,23`) og statuskoder (`DNF-`), men
     ikke på rene sifre — ekte klubber som «3T» overlever.
  3. Ny `is_valid_club_name()` i **både** `import_youth_stats.py` og
     `update_results.py` som siste forsvarslinje: et klubbnavn må inneholde
     minst én bokstav og kan ikke bestå kun av sifre, skilletegn og statuskoder.
     Ugyldige navn gir `None` og en advarsel i loggen i stedet for en ny klubb.
- **Verifisert mot sikkerhetskopien:** klubbnavnet gjenvinnes korrekt fra alle
  659 korrupte strenger, alle 133 kjente søppelklubber avvises av begge
  skriptene, og ingen av de testede ekte klubbnavnene avvises.

---

## 2026-08-07 — Sesongoppdatering mai–august (FULLFØRT)

### Import
- **Script:** `update_results.py --outdoor --season 2026`
- **Formål:** Basen sto på 17. mai; hele sommersesongen manglet.
- **Omfang:** 411 stevner i kilden, 28 i basen → 396 manglende/ufullstendige.
  392 stevner behandlet, 17 358 resultater skrapet.
- **Resultat:** 16 411 nye resultater etter 17. mai, 350 nye stevner,
  16 834 utøvere matchet, 376 nye utøvere opprettet. Siste dato nå 2026-08-01.
  Sesong 2026 totalt: 36 110 resultater. Base totalt: 1 412 964.
- **Forarbeid:** Slettet 31 resultater for 9 stevner som lå ufullstendige i basen
  og skulle re-importeres i sin helhet (ren re-import framfor duplikater).
  NB: «Hopp til Musikk» (11.05, 7 res.) hadde også <10 resultater, men sto IKKE
  på kildens liste — den ble bevisst *ikke* slettet.

### BUG FUNNET OG FIKSET: duplikater fra batch-retry
- **Symptom:** Skriptet rapporterte 17 653 importert av 17 358 skrapet — flere enn
  det fantes. 839 duplikatgrupper i basen etterpå.
- **Årsak:** `import_meet_results()` hadde `try/except` rundt HELE chunk-løkken.
  Feilet chunk 3 av 5, kjørte feilhåndteringen `result_batch` på nytt én og én —
  altså ble chunk 1–2 satt inn en gang til.
- **Hvorfor constrainten ikke fanget det:** `results` har
  `UNIQUE (athlete_id, event_id, meet_id, round, heat_number)`, men importen setter
  aldri `round`/`heat_number`. 19 241 av 19 301 2026-rader har begge NULL, og
  NULL er aldri lik NULL i Postgres. **Constrainten er i praksis inert for denne
  importveien.**
- **Opprydding:** Slettet 813 duplikater (nøkkel: athlete+event+meet+performance
  +place+wind, beholdt eldste `created_at`). 26 par som avvek på plass/vind ble
  BEVART — det er ekte heat+finale med samme tid, verifisert ved at de har
  identisk `created_at`, altså samme batch fra kilden.
- **Fiks:** `try/except` flyttet inn i chunk-løkken, slik at kun det feilende
  chunket retries. Kommentar lagt inn i koden.
- **Gjenstående duplikater etter opprydding:** 0 (verifisert).

### Kjente svakheter (ikke fikset)
- **357 importfeil** på ferdigparsede verdier: `9.5(+0.0) M`, `9.14()`,
  `18.16.1 M`. Håndtidsmarkør «M» og tomme/doble vindparenteser strippes ikke av
  `parse_result_wind()`/`fix_performance_format()`. Disse resultatene mangler.
- **148 resultater hoppet over** pga. manglende øvelsesmapping: kappgang
  (1000/1500/2000 m), 7-kamp/10-kamp-varianter, 400 m Racerunning,
  Kast 5-kamp veteran.
- **Løst samme dag — se neste bolk.**

### Duplikatsperre i databasen (FULLFØRT 2026-08-07)
- **Problem:** Den gamle constrainten
  `UNIQUE (athlete_id, event_id, meet_id, round, heat_number)` var inert:
  36 050 av 36 110 2026-rader har NULL i både `round` og `heat_number`, og
  `NULL = NULL` gir NULL (ikke true) i Postgres. Sperren låste aldri.
- **Hvorfor ikke bare `NULLS NOT DISTINCT` på den gamle?** Den ville da slått ut
  ekte heat+finale-par. Kilden (`StevneResultater.php`) har bare fire kolonner
  — plass, resultat, navn, klubb — og gir *ingen* rundeinfo, så `round` kan ikke
  fylles ut herfra. Heat og finale skilles kun ved ulik plass/vind.
- **Løsning:** Ny indeks på innholdet i stedet for runden:
  ```sql
  CREATE UNIQUE INDEX CONCURRENTLY results_innhold_unik
  ON results (athlete_id, event_id, meet_id, performance, place, wind)
  NULLS NOT DISTINCT;
  ```
  Blokkerer eksakte duplikater, men slipper gjennom heat+finale som avviker på
  plass eller vind.
- **Forarbeid:** Måtte rydde 1 891 eksisterende duplikatrader (1 736 grupper) i
  hele basen, ellers ville indeksen ikke la seg bygge. Fordeling: 345 grupper var
  NULL-runde mot utfylt runde (beholdt den utfylte — mest informasjon), 1 389 var
  identiske uten runde (beholdt eldste). **Ingen gruppe hadde ulik `status`**, så
  ingen risiko for å beholde et godkjent og slette et diskvalifisert resultat.
  1 170 av gruppene lå i 2026 (innendørs/vår), altså samme bug fra tidligere kjøringer.
- **Verifisert:** Forsøk på å sette inn kopi av en ekte rad avvises med
  `23505 duplicate key value violates unique constraint "results_innhold_unik"`.
- **Importskript:** `update_results.py` teller nå avviste duplikater som
  `skipped_duplicate` i stedet for `errors`. Importen er dermed trygt
  re-kjørbar — en ny kjøring over samme periode legger ikke inn noe på nytt.
- **Loggfiler:** `logs/update_20260807.log`, `logs/dryrun_20260807.log`

---

## 2026-07-03/04 — Kjønnsopprydding (FULLFØRT)

### Fase 1: Klassebevis fra kilden
- **Script:** `fix_gender_from_source.py --seasons 2013-2026`
- **Formål:** Sette kjønn autoritativt fra klasseoverskrifter på stevnesidene
  (minfriidrettsstatistikk.info). Kun stevner med resultater fra NULL-utøvere
  ble hentet (hjelpetabell `gender_fix_target_meets`, 10 265 stevner).
- **Resultat:** 8 437/10 265 stevner matchet mot kilden (navn+dato), 671 000
  bevisrader høstet. 775 utøvere → M, 305 → F. 2 konflikter, 109 motsigelser
  rapportert. `meets.external_id` populert for 8 437 stevner (ny kolonne +
  RPC `set_meet_external_ids`).
- **Problemer:** (1) Første kjøring krasjet på partial upsert mot meets
  (NOT NULL sjekkes før konfliktløsning) — løst med RPC. (2) Maskinsøvn drepte
  kjøringen ved 4 700 stevner og etterlot trunkert gzip-bevisfil — 367 459 rader
  berget, resume-logikk + `caffeinate` la til. (3) Hovedfunn: kildens stevnesider
  viser IKKE 10-12-årsklassene (barneidrettsbestemmelsene), så ~29k utøvere
  (nesten alle 10-12 år) kan aldri få kjønn fra klassebevis.
- **Bevisfiler:** `new_meets_data/gender_evidence_*.jsonl.gz` (kan gjenbrukes
  til aldersklasse-backfill uten ny scraping!)
- **Loggfiler:** `logs/fix_gender_from_source_*.log`, `logs/fix_gender_report_*.json`

### Fase 2: Fornavnsklassifisering
- **Script:** `fix_gender_by_firstname.py --contradictions-report logs/fix_gender_report_20260704_004330_contradictions.json`
- **Formål:** Klassifisere 10-12-åringene (uten klassebevis) på fornavn, trent
  på 668 436 klassebevisrader + 58 503 utøvere med kjent kjønn.
- **Validering:** Leave-one-out mot kjente utøvere: **99,76 %** treff (55 669/55 805).
- **Terskler:** >= 5 obs og >= 98 % samme kjønn, eller >= 3 obs og 100 %.
- **Resultat:** 14 075 → M, 12 789 → F. 67 motsigelser rettet (enstemmig
  klassebevis >= 5 mot feil DB-kjønn — rest fra batch-korrupsjonen jan 2026).
  2 273 forblir NULL (sjeldne/utenlandske navn) — liste i rapporten.
- **Sluttstatus:** M=47 859, F=37 508, NULL=2 273 (fra 30 217).
  Kvinnelister verifisert rene (100m/5000m).

### Forebygging
- `update_results.py` `match_athlete()` backfiller nå kjønn på eksisterende
  utøvere med gender=NULL når importen har autoritativt klasse-kjønn.

### Restanser
- 2 273 NULL (sjeldne navn) — manuell liste i `logs/fix_gender_by_firstname_report_*.json`
- 1 828 målstevner umatchet mot kilden (navneavvik) — kan diagnostiseres via
  `meets.external_id IS NULL`
- 42 motsigelser med svakt/blandet bevis — samme rapportfil
- Hjelpetabell `gender_fix_target_meets` droppet etter kjøring

---

## 2026-02-13

### Backfill fødselsår
- **Script:** `backfill_birth_years.py`
- **Status:** Kjører (startet av bruker)
- **Formål:** Hente fødselsår for utøvere som mangler birth_year
- **Resultat:** _Oppdater når ferdig_

---

## 2026-02-12

### Oppdatering av nye stevner
- **Script:** `update_results.py` (antatt basert på new_results CSV)
- **Output:** `new_meets_data/new_results_20260212_134837.csv`
- **Resultat:** Nye resultater importert

---

## Rekonstruert historikk (fra git-log og loggfiler)

### 2026-02-09 — Historisk import og all-time disclaimer
- **Commit:** ed713d9
- **Script:** `import_historical.py`
- **Formål:** Import av historiske all-time statistikk fra friidrett.no
- **Detaljer:** 3-nivå dedup (normalisert navn+dato, fuzzy, cross-meet)

### 2026-02-07 — Footer, championship layout, klubboppdateringer
- **Commit:** 69f5bfc
- **Endringer:** Oppdatert footer, mesterskap-layout, utøver-klubb-oppdateringer

### 2026-02-06 — Fix sammenlign-side lasting
- **Commit:** f2bbbf8
- **Problem:** Utøvernavn lastet ikke på sammenligningssiden
- **Løsning:** Fix i sammenlign/page.tsx

### 2026-02-02 — Manglende øvelser + unified update script
- **Commit:** 7f3ba82
- **Endringer:** Fix manglende øvelser på forsiden, opprettet `update_results.py`

### 2026-01-31 — Mesterskap-medaljer (NM)
- **Commit:** 501d0f9
- **Endringer:** Lagt til NM-medaljer på utøversider

### 2026-01-26 — Import og duplikat-opprydding
- **Logget i README.md**
- **Resultater:** 885 resultater importert, 19 duplikat-resultater slettet, 57 duplikat-stevner merget
- **Scripts brukt:** `import_scraped_results.py`, `merge_duplicate_meets.py`
- **Loggfiler:** `import_log.txt`

### 2026-01-25 — Massiv duplikat-opprydding
- **Scripts kjørt (i rekkefølge):**
  1. `cleanup_duplicates.py` → `cleanup_log.txt` (815 KB)
  2. `cleanup_duplicates_v2.py` → `cleanup_v2_log.txt` (1.4 MB)
  3. `cleanup_duplicates_v3.py` → `cleanup_v3_log.txt` (37 MB!)
  4. `cleanup_final.py` → `cleanup_final_log.txt` (3.5 MB)
  5. `cleanup_crossmeet.py` → `cleanup_crossmeet_log.txt` (3.5 MB)
- **Lærdom:** Trengte 5 iterasjoner. Burde vært gjort riktig i import-steget.

### 2026-01-25 — Cleanup final
- **Loggfil:** `cleanup_final.log` (6 KB)

### 2026-01-27 — Kjønnsfiks (MISLYKKET)
- **Dokumentert i:** `FIX_GENDER_README.md`
- **Problem:** `fix_missing_gender_batch.py` ødela kjønnsdata
- **Status:** UFIKSET. Mange utøvere har fortsatt feil kjønn.
- **VIKTIG:** Ikke kjør batch-kjønnsinferens igjen.

### 2026-01-22/24 — Data recovery
- **Loggfiler:** `recover_output.log` til `recover_output5.log`
- **Formål:** Ukjent — sannsynligvis recovery etter feilaktig sletting/oppdatering

### 2026-01-19 — Scraping
- **Loggfil:** `scrape_output.log` (158 KB)
- **Formål:** Stor scraping-kjøring

### Ca. jan 2026 — Diverse fikser
- Flere iterasjoner av tidsformat-fiks (fix_all_times v1/v2/v3/robust)
- Hekke-fiks (fix_hurdle_events/times/fast)
- Vekt-øvelse-fiks (fix_weight_events/fast)
- Kjønnsinferens (fix_missing_gender/batch/authoritative/complete)

---

## Mal for nye innføringer

```
### [Kort beskrivelse]
- **Script:** `script_name.py [--flagg]`
- **Formål:** Hva og hvorfor
- **Resultat:** Antall endringer, status
- **Problemer:** Eventuelle feil eller uventede ting
- **Loggfil:** `logs/script_name_YYYYMMDD.log` (hvis relevant)
```

## 2026-09-14 — Gjeldende klubb rettet for 2 225 utøvere

**Symptom.** Sondre Guttormsen sto på Ski IL Friidrett, som han forlot i 2018,
mens broren Simen — som byttet til SK Vidar samtidig — sto riktig.

**Årsak.** `_update_athlete_club()` i `update_results.py` satte
`current_club_id` til klubben i det stevnet som ble behandlet akkurat da, uten
datosjekk, og `_athlete_club_updated` låste den for resten av kjøringen. Da
sesongene 2013–2018 ble kontrollert mot kilden, stemplet det utøvere med
klubber de forlot for år siden. 3 602 utøvere var berørt.

**Regel som ble forkastet.** «Klubben i nyeste resultat vinner» ble prøvd
først. Den flyttet utøvere fra klubben til en skole hvis siste start var et
skolestevne (`Austevoll IK Friidrett` → `Austevoll Ungdomsskule`), og til
«ukjent» der siste resultat manglet klubbnavn.

**Regel som ble brukt.** Klubben utøveren har flest resultater for i sin siste
aktive sesong, med skoler og «ukjent» utelatt som mål. Et klubbskifte viser seg
ved gjentatt deltakelse for den nye klubben, ikke ved én start.

**Utført.** 2 225 rettet — de med minst to resultater for den nye klubben.
1 377 holdt tilbake fordi de hviler på ett enkelt resultat; de ligger i
`backups/rett_gjeldende_klubb_20260914_155653.json` under `holdt_tilbake`.

**Roten er rettet.** Importen setter ikke lenger klubben underveis. Den merker
berørte utøvere og utleder klubben til slutt via
`gjeldende_klubb_for_utover()`, som bruker samme regel.

**Merk.** De hyppigste treffene er dubletter av samme klubb («Idrettslaget
Skjalg» → «IL Skjalg», 48 stk). Det er klubbsammenslåing, en annen oppgave.

## 2026-09-14 — Gjennomgangsliste for klubbdubletter

`finn_klubbdubletter.py` lager underlag for opprydding i klubbregisteret. Den
foreslår ingenting og endrer ingenting.

Navn normaliseres ved å fjerne organisasjonsledd, og klubber med samme kjerne
listes som kandidater. Avgjørende signal er **felles utøvere** — antall utøvere
med resultater for begge postene — ikke navnelikheten.

| Gruppe | Par | Avgjørelse |
|---|---:|---|
| A Trolig samme klubb | 36 | Slå sammen |
| B Friidrettsgruppa som egen enhet | 52 | Domenevalg, avklares med NFIF |
| C Svakt grunnlag | 123 | La ligge |

Gruppe B er den interessante: «Kristiansands IF Friidrett» mot «Kristiansands
IF» med 61 felles utøvere. Det er ikke en skrivefeil, men spørsmålet om
friidrettsgruppa i et fleridrettslag skal være egen enhet. Påvirker
klubbstatistikk, klubbrekorder og §10.

Resultat: `scraper/opprydding/KLUBBDUBLETTER.md` og tilhørende CSV.

Underveis ble `klubb_bruk` gjort om til materialisert visning; som vanlig
visning aggregerte den over hele `results` ved hvert kall og tidsavbrøt.

## 2026-09-15 — is_wind_legal utledes nå av en regel, ikke av en standardverdi

**Funn.** Kolonnen `results.is_wind_legal` hadde standardverdi `true`, og
importene satte den bare til `false` ved vind over 2,0. Alt annet sto som
«lovlig» — også 34 166 utendørsresultater uten vindmåling. Tørrkjøring før
reparasjon, over alle 1,95 millioner rader:

| Sto som | Skulle vært | Rader | Betydning |
|---|---|---:|---|
| true | NULL | 1 272 302 | ikke-vindpåvirket øvelse, eller umålt vind |
| NULL | true | 44 169 | målt, lovlig vind — falt ut av årslistene |
| false | NULL | 5 547 | hekk med vind over 2,0 (regelen manglet hekk) |
| true | false | 2 842 | medvind over 2,0 vist som lovlig |

**Regel** (WA 17.9), nå ett sted: `er_vindpaavirket(code)` i basen og
`erVindpaavirket()` i `web/src/lib/vind.ts`. Sprint t.o.m. 200 m, hekk
t.o.m. 200 m, lengde og tresteg med tilløp. Ikke høyde/stav (tidligere fikk
de vindkrav via kategorien «jumps»: 5 204 høyde- og 1 550 stavresultater var
utelatt), ikke hopp uten tilløp, ikke mangekamp.

**Tiltak.**
- Trigger `trg_sett_vindflagg` på `results` setter flagget fra `wind` og
  øvelse ved insert og ved endring av wind/event_id. Alle importveier.
- Standardverdien fjernet. `update_results.py` og `import_historical.py`
  setter ikke lenger flagget selv.
- Reparasjon med `rett_vindflagg(event_id)` per øvelse, 20 minutter.
  Telleren viste 1 128 711 rader; 60 m (277 920 rader) fullførte på
  serveren etter at klienten ga opp, så den ble ikke telt. Kontrollen
  `test_vindflagg_avvik()` gir 0/0/0/0 etterpå.
- `test_fullstendighet.py` sjekker konsistensen ved hver kjøring.

**Synlig effekt.** Årslistene (nasjonalt og per klubb) viser nå resultater
med ukjent vind i egen liste nederst, og utøverprofilen skiller dem ut
nederst i resultatlista. Medvindsløp over 2,0 er borte fra de lovlige
listene. `personal_bests_detailed` regnet allerede fra `wind` direkte og er
upåvirket.

## 2026-09-15 — Kilden rettes i etterkant, og importen oppdaterer nå vinden

**Sak.** Trym Blindheim, 100 m, Gneistspelen 2026 (22.08.): sto med ukjent
vind i basen, mens kilden viser `11,95(+0,1)`. Raden ble importert 6. sept.
i samme INSERT som naboradene, som fikk vind, av samme parser — og dagens
parser gir riktig vind på nøyaktig den strengen. Inndata må altså ha vært
annerledes den dagen: kilden ble rettet etter at vi hentet den. Vi kan ikke
se kildens versjon fra 6. sept., så dette er slutning, ikke bevis, men det
er den eneste forklaringen som stemmer med alle observasjonene.

**Omfang.** Sammenlikning av alle 2026-stevner utendørs mot kilden i dag:
99 vindpåvirkede rader uten vind i basen på stevner som ellers har vind.
1 av dem (Tryms) har vind i kilden nå. De 98 andre mangler vind i kilden
også — arrangøren målte ikke. Ikke et parserproblem.

**Hvorfor en ny import ikke hjalp.** Den unike indeksen
`results_innhold_unik` omfatter `wind`, så `(11.95, NULL)` og `(11.95, +0.1)`
er to ulike rader. En gjenkjøring ville lagt inn en dublett ved siden av den
gamle, ikke rettet den.

**Tiltak i `update_results.py`.**
- `_oppdater_vind_hvis_rettet()`: finnes det en rad for stevnet med samme
  utøver, øvelse, resultat og plass, men uten vind, og kilden nå har vind,
  oppdateres raden i stedet for at det legges inn en ny. Telles som
  `updated_wind`. Triggeren setter `is_wind_legal`.
- `--kun-stevner` så bare stevner fra siste uke (startdato = siste stevne
  minus 7 dager), så «Gneistspelen 2026», 24 dager gammelt, ga «up to date».
  Navngitte stevner søkes nå i hele sesongen.

**Kjørt.** `--kun-stevner` på Gneistspelen 2026: 1 rad oppdatert, 263
hoppet over som allerede i basen, 0 dubletter, 264 rader som før.

## 2026-09-15 — Importen avstemmer mot kilden, og oppryddingen det utløste

**Krav fra Atle:** alt skal inn riktig fra start, og feil skal rettes.

**Avstemming** (`_avstem_stevne` i `update_results.py`). Ved hver kjøring
hentes stevner fra de siste 6 ukene på nytt (`--avstem-uker`, kildelista
utvides tilsvarende), og hvert stevne avstemmes: rader som er endret i
kilden oppdateres (resultat, plass, vind), nye legges inn, og rader kilden
ikke lenger har får `verified=false` — **ingenting slettes**. Flagging bare
når kilden dekker ≥ 90 % av stevnet og øvelsen finnes i kilden: basen slår
sammen kildestevner med samme navn/dato til ett, og parseren hopper over
enkelte øvelser. `--kun-stevner` søker nå hele sesongen.

**Utøvermatching.** `match_athlete()` nøkler på (navn, fødselsår, kjønn);
der den lagrede utøveren manglet år/kjønn, opprettet importen en ny utøver
og la resultatet inn en gang til. Avstemmingen kjenner nå igjen raden på
navn innenfor stevnet og gjenbruker den utøver-id-en. Kontroll:
`test_utoveravdrift(event_id)`.

**Kjørt.** Hele 2026 utendørs (720 stevner, 31 156 kilderader): 4 rader
rettet, 17 nye, 14 utøver-id-avvik fanget, 0 feil. De 123 eldre stevnene
med dubletter (2012–2025) via `--kun-stevner` per sesong.

**Feil jeg lagde, og rettet samme dag:** en kjøring før navnegjenkjenningen
la inn 56 resultater under 16 nye dublettutøvere — alle slettet. Første
flaggeregel (50 %) flagget 1 468 rader feil — tilbakestilt.

**Opprydding av det som lå der fra før:**
- 187 resultatpar like på alt unntatt vind (`rydd_innholdsdubletter.py`):
  49 slettet (raden uten vind, der kilden har vind). 138 par med hver sin
  målte vind lar vi stå — kan være forsøk og finale med samme tid.
- 414 utøverpar med samme navn og felles resultater
  (`slaa_sammen_utoverdubletter.py`): 331 slått sammen (eldste beholdes,
  236 resultater flyttet, 547 dublettresultater slettet). 58 par med ulikt
  fødselsår må vurderes for hånd: `opprydding/utoveravdrift_par.json`.
- Kilden har *mistet* resultater for enkelte stevner siden vi hentet dem
  (Tyrvinglekene 2026: 39 stavresultater for 15+ er borte fra kildesiden).
  Vi beholder våre, flagget `verified=false`. Synlig bare i admin.

**Tunge jobber ut av forespørselen.** Supabase-gatewayen kutter alle kall
etter 120 s uansett `statement_timeout`. `refresh_plattform_statistikk()`
gjør nå bare forsidetallene og merker `vedlikehold.klubb_bruk`; pg_cron
`refresh_klubb_bruk` (hvert kvarter, med `set statement_timeout` i selve
jobb-kommandoen) oppdaterer `klubb_bruk`. Verifisert: fire vellykkede
kjøringer à ~2 min. Analyser over hele `results` deles per øvelse.

**Kontroller** i `test_fullstendighet.py`: vindflagg, innholdsdubletter,
utøveravdrift — alle skal være 0.

## 2026-09-18 — Samme stevne to ganger i basen (funnet, rot rettet, opprydding klar)

**Funn.** På utøversidene lå samme resultat to ganger, fra to «stevner» samme
dag: «Stjørdal, UM 2025» og «UM 2025». Importkjøringene 20.–26. januar 2026
la stevnene inn både med og uten sted foran navnet, og slo dessuten stevner
med samme navn samme dag («Treningsstevne» i to byer) sammen til én post.
Omfang: 4 925 stevnepar med felles resultater, ca. 196 000 dobbeltrader
(2012–2026, mest 2019–2025), pluss 964 par som er to deler av samme stevne
uten felles rader («Fana, Fanalekene 2026» 36 rader / «Fanalekene 2026»
315 rader). Etter 1. februar 2026 er det ikke oppstått nye par.

**Rot** (`get_or_create_meet` i `update_results.py`): stevnet ble funnet på
navn + dato alene, og kildens stevne-id ble ikke lagret. Nå: kildens
stevne-id først, så navn + dato med samme sted, så «Sted, navn», så navn
uten sted i basen. Posten som finnes igjen får kilde-id og sted fylt inn.
Testet mot basen: finner riktig post i alle tre tilfellene.

**Opprydding** (`rydd_stevnedubletter.py`, funksjon `rydd_stevnepar` i
basen, grunnlag i tabellen `opprydding_stevnepar`). Regel: behold posten
med kilde-id, ellers den med sted i navnet, ellers den største. Tvillinger
slettes (vind kopieres først dit den mangler). Resten flyttes bare når
navnene er samme stevne og posten ikke inngår i flere par. Par med ulik
dato, med kilde-id på begge, eller med ulike navn uten kilde-id røres ikke.

**Kjørt 18.09.2026 (klarsignal fra Atle), 5 889 par:** 4 848 par
utført, 189 400 dobbeltrader slettet, 153 176 rader flyttet til riktig
stevnepost, 3 751 tomme stevneposter slettet, vind kopiert inn på 173
rader. 812 rader kunne ikke flyttes (unik indeks på utøver/øvelse/
stevne/runde/heat i mottakerposten) og 55 850 rader står igjen i poster
som inngår i flere par eller har ulikt navn — de er ikke dobbeltlagret,
bare under en mindre presis stevnepost. 1 041 par urørt (ulik dato, kilde-id
på begge, eller ulike navn uten kilde-id). Alt ligger i
`opprydding_stevnepar` (vedtak, utfort, resultat per par).

**Kontroll:** `test_fullstendighet.py --bare stevnedubletter`
(`test_stevnedubletter(dato)`, siste 400 dager).

## 2026-09-18 — Runde i importen, og NM-medaljer 2026

**Funn.** Utøverprofilen manglet medaljer fra NM 2026. `championship_medals`
ble fylt én gang (februar 2026) fra friidrett.no sine medaljesider, som nå
er borte (404). Å regne medaljer av våre egne rader gikk ikke: importen
lagret ikke runde, så heatvinnere så ut som vinnere.

**Rot.** Kilden har runden i plasseringskolonnen («1-h2», «1-hsf1»,
«1-fi», «1-kv1»). `parse_runde()` i `update_results.py` leser den, nye
rader får `round`/`heat_number`, og avstemmingen fyller inn runde på
eksisterende rader (`updated_round`). Kjørt for Hovedmesterskapet 2026
(659 rader) og Inne-NM 2026 (443 rader).

**Medaljer** (`nm_medaljer_fra_kilden.py`, regel fra Atle): bare
finaler; A-heat (heatet med best vinnertid) der det bare er heat; sprint
uten finale innendørs rangeres på tid; «Menn Senior»/«Kvinner Senior»
bare. Lagt inn 112 medaljer NM utendørs 2026 og 69 NM innendørs 2026.
**Manuelt:** 200 m innendørs 2026 (kilden merker ikke finaleheatene) og
Lisa Wilker (bronse lengde inne, ingen entydig utøverpost).

**Personlig rekord** peker nå på første gangen resultatet ble satt
(`personal_bests_detailed`: dato som tilleggskriterium).

**Etterspill 18.09.2026.** Sammenslåingen la rader som før lå i to
stevneposter under hver sin utøver-id i samme post, så
`test_fullstendighet.py` meldte 130 rader med utøveravdrift.
`slaa_sammen_utoverdubletter.py --kartlegg` (ny) bygger parlista på nytt:
40 par, alle med samme navn, fødselsår og kjønn. Slått sammen: 40 utøvere,
77 resultater flyttet, 130 dublettresultater slettet. Kontrollene
vindflagg, dubletter og avdrift er grønne igjen; `stevnedubletter` viser
7 par (74 rader) som er de manuelle («Asker, Kastmangekamp» / «Heggedal,
Kastmangekamp» og lignende, ulike navn uten kilde-id).

## 2026-09-18 — Sider som feilet stille, og tider lest som sekunder

**Spørsmål fra Atle:** klubbrekorden på 800 m for Ski IL manglet – kan det
være mange slike? Gjennomgang av alle sidene som kjørte én spørring per
element og lot feil passere stille:

| Side | Før | Nå |
|---|---|---|
| Klubbrekorder | ~300 spørringer, 12 s, feilet øvelse forsvant | `klubbrekorder()` i ett kall, under 1 s |
| Norgesrekorder (`/statistikk/rekorder`) | 60–100 spørringer, feilet øvelse forsvant | `norgesrekorder()` i ett kall, 0,3 s |
| NM-kvalifisering, tellingene i sidestolpen | 20–40 sidevise uttrekk bare for å telle | `tell_kvalifiserte()` i ett kall; ny indeks `idx_results_event_date_perf` |
| Forsiden, årsbeste | 36 spørringer | uendret, men en feilet øvelse vises med strek (rettet tidligere i dag) |

Serverklienten logger nå alle svar fra basen som ikke er OK
(`lib/supabase/server.ts`), med sti og melding, uansett om siden sjekker
feilen. 51 steder i koden leser bare `data`; de er ikke lenger usynlige.

**Tider lest som sekunder.** Under gjennomgangen viste norgesrekorden på
800 m «2,25». Kilden skriver tider uten hundredeler som «2.25» (2:25), og
`fix_performance_format` leste todelte tider som sekunder. 3 776 rader i
løp over ett minutt (kappgang 1000 m alene 1 865). Rot rettet: funksjonen
kjenner nå øvelsen (`er_langt_loep`). Ryddet med `rett_minuttider(false)`:
3 639 rader rettet, 137 slettet som dubletter av rader som alt lå riktig.
Kontroll: `test_fullstendighet.py --bare tider` (`test_urimelige_tider`).

**NM-listen** regnet «utendørs» som `meet_indoor = false` og utelot stevner
uten bane-flagg; nå `IS NOT TRUE`, som tellingen.

## 2026-09-20 — Nattlig oppdatering via GitHub Actions

`.github/workflows/oppdater.yml` kjører hver natt kl. 04.15 norsk tid (og
ved behov for hånd): `update_results.py` (nye stevner, avstemming siste seks
uker, forsidetall) og deretter `test_fullstendighet.py` med kontrollene mot
basen. Feiler en kontroll, feiler jobben. Loggen lagres som artefakt i 30
dager. Hemmelighetene SUPABASE_URL og SUPABASE_SERVICE_KEY ligger i
repoets secrets. Importen skriver tidsstempel i `vedlikehold` (nøkkel
`import`), og forsiden viser «Oppdatert i dag kl. …».

**Første kjøring 20.09.2026:** 181 resultater inn, 19 rader fikk runde,
0 feil, 3 minutter. Kontrollen `stevnedubletter` stoppet på de sju parene
som sto til manuell vurdering; de er nå avgjort (samme stevne, ulikt navn:
KM Masters/Kaststevne, HBT-stevnet, Kastmangekamp Asker/Heggedal, European
Masters på tre baner, Sandnes innendørs, Pfungstadt) og slått sammen med
`rydd_stevnepar`. 74 dobbeltrader slettet, 11 rader ble stående i «Asker,
Kastmangekamp» (unik indeks).

## 2026-09-21 — Kilden med samme stevne under to id-er

Nattkjøringen (57 resultater inn, 1 forbigående nettfeil mot kilden) stoppet
på to nye stevnepar: «Aider Mjøssprinten» 22.08.2026 lå i kilden både som
Moelv (10009370) og Lillehammer (10009371) med 50 felles resultater, og
Abendsportfest i Pfungstadt under to id-er. Oppslag på kilde-id alene ga to
poster. Rot rettet i to lag:

- `finn_tvilling()` i `update_results.py`: samme navn og dato under en annen
  kilde-id, og minst halvparten av kildens rader ligger der alt → samme
  stevne, posten gjenbrukes. Navn + dato alene holder ikke («Treningsstevne»
  i to byer deler ingen rader).
- Tabellen `stevne_alias`: kilde-id → stevne, fylles av `rydd_stevnepar` når
  en post slettes, og slås opp av `get_or_create_meet`. Uten den ville den
  slettede posten blitt opprettet på nytt neste natt.

De to parene er slått sammen (53 dobbeltrader slettet). Verifisert med
`--kun-stevner` på begge: alle fire kildestevner går til én post hver, 0 nye.
Planlagt kjøring flyttet til 03.37 (GitHub startet 02.15-jobben først 09.58;
hele klokkeslett har lang kø).

## 2026-09-21 — Rekordsiden: tider lest feil, fire klasser

Atle fant på norgesrekordsiden: 400 m hekk kvinner «1.08» (Guro Kvamme),
300 m, 600 m og 300 m hekk med samme feil, maraton kvinner 2:40.00 (Marthe
Katrine Myhre) og 5000 m kvinner 10:45.45 (Grøvdal). Fire årsaker, alle i
`fix_performance_format`:

1. **Minutter i korte løp.** «1.08» på 400 m hekk er 1:08. Regelen fra
   18.09 gjaldt bare 800 m og lengre. Nå: en todelt tid i en øvelse der ingen
   løper under 20 sekunder, og som ligger under gulvet for distansen
   (`_minste_sekunder`, distanse/10), er minutter og sekunder. «21.05» på
   200 m er sekunder, «1.05» på 300 m er 1:05. Dekker også 1600_m, 500_m,
   rullestol-øvelsene og tresifrede minutter i kappgang («113.20» = 1:53:20).
   `rett_minuttider()` utvidet: 219 rader rettet, 27 slettet som dubletter.
2. **Timer på maraton og kappgang.** «2.40.00» ble 2:40.00 (2 min 40 s).
   Tredelt tid under gulvet for distansen er timer:minutter:sekunder.
   `rett_timetider()`: 221 rader rettet (maraton, halvmaraton, 10/20/30/50 km
   kappgang).
3. **Skrivefeil i kilden.** Grøvdal 5000 m Novi Sad 2009 sto som 10:45.45;
   hun vant på 15:45.45 (EM junior). Rettet for hånd.
4. **Fysisk umulige rester** (27 rader: 100 m «1.00»–«9.99», 60 m «1.39»,
   200 m «19.7», 600 m «2.1») satt til status NM, så de ikke vises i lister.
   Ligger i basen for gjennomsyn.

`test_urimelige_tider()` bruker nå gulvet per distanse og er 0.

**Veiøvelser tatt ut av norgesrekordsiden** (maraton, halvmaraton, 3/5/10 km,
100 km) til det historiske veimaterialet er inne (fase 3). Basen har ikke
Ingrid Kristiansens 2:21:06 fra 1985, og en «rekord» fra 2014 ville vært feil.

**Dabaya Badhaso** lå som to utøvere, den ene med feil kjønn. Slått sammen,
kjønn rettet til mann.
