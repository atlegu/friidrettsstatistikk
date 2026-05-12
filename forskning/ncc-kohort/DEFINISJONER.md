# Variabeldefinisjoner — NCC/PEAB-kohortstudien

## 1. Frafall og karrierelengde

### Operasjonelle definisjoner

**Aktiv sesong** = et kalenderår der utøveren har ≥2 registrerte resultater.
- Begrunnelse: Én enkelt start kan være tilfeldig (følge en venn, teststart). To eller flere indikerer reell deltakelse.

**Siste aktive sesong** (`siste_aktive_ar`) = siste kalenderår med ≥2 resultater.
- For sensitivitetsanalyse: `siste_resultat_ar` = siste år med minst ett resultat (mildere krav).

**Karrierelengde** (`karriere_ar`) = `siste_aktive_ar` - `stevne_ar`
- `stevne_ar` = det første året utøveren deltok i NCC/PEAB (2011, 2012, 2013 eller 2014).

**Binære utfallsvariabler:**
| Variabel | Definisjon |
|---|---|
| `aktiv_17` | Hadde aktiv sesong i en alder av ≥17 |
| `aktiv_senior` | Hadde aktiv sesong i en alder av ≥20 |
| `aktiv_naa` | Hadde aktiv sesong i 2024 eller 2025 |
| `deltok_begge_aar` | Deltok i NCC/PEAB to år på rad (som 13- og 14-åring) |

**Sensurering (for survival analysis):**
- Utøvere med `aktiv_naa = TRUE` er høyre-sensurerte (karrieren er ikke over).
- COVID-perioden 2020–2021 behandles som spesialtilfelle (sensitivitetsanalyse ekskl. denne perioden).

---

## 2. Prestasjonsnivå

### Relativt (prosentil innen kohort)

For hver prestasjon ved NCC/PEAB: rangeres innen samme øvelse + kjønn + stevne-år.
Prosentil = (rank − 1) / (n − 1) × 100, der rank 1 = best.

| Variabel | Definisjon |
|---|---|
| `baseline_pctile_best` | Beste prosentil blant alle øvelser utøveren deltok i |
| `baseline_pctile_mean` | Gjennomsnittlig prosentil på tvers av øvelser |

### Absolutt (Tyrving-poeng)

Tyrvingtabellen konverterer prestasjoner til alders- og kjønnsnormerte poeng der 1000 = «utmerket».

**Formel:**
- Tidsøvelser: `Poeng = 1000 + (referanse_cs − resultat_cs) × kvotient`
  - `referanse_cs` = 1000-poeng-verdien i hundredeler (f.eks. 12.35s → 1235)
  - `resultat_cs` = performance_value fra databasen
- Feltøvelser: `Poeng = 1000 + (resultat_cm − referanse_cm) × kvotient`
  - `referanse_cm` = 1000-poeng-verdien i centimeter (f.eks. 5.75m → 575)
  - `resultat_cm` = performance_value / 10 (da DB lagrer i mm)

| Variabel | Definisjon |
|---|---|
| `tyrving_best` | Beste Tyrving-poeng blant alle øvelser i NCC/PEAB |
| `tyrving_mean` | Gjennomsnitt av Tyrving-poeng på tvers av øvelser |

### Prestasjonskategorier

Basert på `tyrving_best`:
| Kategori | Tyrving-poeng | Beskrivelse |
|---|---|---|
| Svak | <600 | Godt under aldersnorm |
| Under snitt | 600–799 | Under middels |
| Middels | 800–999 | Rundt aldersnorm |
| God | 1000–1199 | Over aldersnorm |
| Sterk | ≥1200 | Langt over aldersnorm |

---

## 3. Allsidighet vs. spesialisering

Øvelseskategorier fra databasen: `sprint`, `middle_distance`, `long_distance`, `hurdles`, `jumps`, `throws`, `combined`, `walking`, `relay`.

### Ved baseline (NCC/PEAB)

| Variabel | Definisjon |
|---|---|
| `baseline_n_kategorier` | Antall distinkte øvelseskategorier utøveren deltok i |
| `baseline_n_ovelser` | Antall distinkte øvelser (mer granulert) |

### Over karrieren (første 3 aktive år)

| Variabel | Definisjon |
|---|---|
| `early_n_kategorier` | Distinkte kategorier i de 3 første aktive sesongene |
| `hhi_early` | Herfindahl-Hirschman-indeks for øvelseskonsentrasjon |

**HHI-beregning:** For en utøver med resultater fordelt på k kategorier:
`HHI = Σ(si²)` der `si = andel resultater i kategori i`.
- HHI = 1.0 → alle resultater i én kategori (ren spesialist)
- HHI = 1/k → lik fordeling over k kategorier (mest allsidig)

### Øvelsesskifte

| Variabel | Definisjon |
|---|---|
| `primaer_kategori_baseline` | Kategori med flest resultater ved NCC/PEAB |
| `primaer_kategori_siste` | Kategori med flest resultater i siste aktive sesong |
| `byttet_kategori` | Boolean: `primaer_kategori_baseline ≠ primaer_kategori_siste` |

---

## 4. Relative Age Effect (RAE)

| Variabel | Definisjon |
|---|---|
| `fodt_kvartal` | Q1 (jan–mar), Q2 (apr–jun), Q3 (jul–sep), Q4 (okt–des) |
| `fodt_halvaar` | H1 (jan–jun), H2 (jul–des) |
| `fodt_maaned` | 1–12 |

Krever `birth_date` (tilgjengelig for 93–97% av kohorten).

---

## 5. Konkurransefrekvens

| Variabel | Definisjon |
|---|---|
| `stevner_baseline_ar` | Antall distinkte stevner i NCC/PEAB-året |
| `stevner_per_ar_tidlig` | Gjennomsnittlig stevner/år i de 2 første aktive sesongene |
| `resultater_per_ar_tidlig` | Gjennomsnittlig antall resultater/år i de 2 første aktive sesongene |
| `frekvens_trend` | Endring i stevner/år fra sesong 1 til 2 (positiv=økning) |

---

## 6. Kontrollvariabler

| Variabel | Definisjon |
|---|---|
| `kjonn` | M/F |
| `fodt_aar` | 1998/1999/2000 |
| `ncc_region` | Østlandet / Midt-Norge / Vestlandet (basert på NCC/PEAB-sted) |
| `klubb_storrelse` | Antall aktive utøvere i klubben i stevneåret |
| `stevne_utgave` | NCC 2011 / NCC 2012 / PEAB 2013 / PEAB 2014 |

---

## 7. Øvelsesspesifikt frafall

For utøvere med ≥5 resultater totalt:

| Variabel | Definisjon |
|---|---|
| `siste_sprint_ar` | Siste år med sprintresultat (NULL hvis aldri sprint) |
| `siste_hopp_ar` | Siste år med hoppresultat |
| `siste_kast_ar` | Siste år med kastresultat |
| ... | (tilsvarende for øvrige kategorier) |
