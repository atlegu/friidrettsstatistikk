# Import-spesifikasjon v1.0

> **Status:** Utkast - vil endres basert på tilbakemeldinger
> **Dato:** Januar 2025

---

## 1. Oversikt

Denne spesifikasjonen definerer formatet for innsending av resultater til statistikksystemet. Målet er et format som er:

- **Enkelt** - kan lages i Excel
- **Komplett** - fanger all nødvendig informasjon
- **Entydig** - minimerer tolkning og feil
- **Utvidbart** - kan legge til felter uten å brekke eksisterende

---

## 2. Støttede formater

| Format | Bruksområde |
|--------|-------------|
| **CSV** | Enkel innsending, Excel-eksport |
| **JSON** | Programmatisk innsending fra systemer |

Begge formater skal inneholde samme informasjon.

---

## 3. Datastruktur

### 3.1 Stevne-metadata (påkrevd)

Sendes én gang per fil, enten som header-rader (CSV) eller som eget objekt (JSON).

| Felt | Type | Påkrevd | Beskrivelse | Eksempel |
|------|------|---------|-------------|----------|
| `stevne_navn` | tekst | Ja | Offisielt navn på stevnet | "Trondheim Games 2025" |
| `stevne_dato` | dato | Ja | Startdato (YYYY-MM-DD) | "2025-06-14" |
| `stevne_dato_slutt` | dato | Nei | Sluttdato hvis flerdagers | "2025-06-15" |
| `stevne_sted` | tekst | Ja | By/sted | "Trondheim" |
| `stevne_arena` | tekst | Nei | Arenanavn | "Øya stadion" |
| `stevne_land` | tekst | Nei | ISO 3166-1 alpha-3, default "NOR" | "NOR" |
| `stevne_type` | tekst | Nei | Se kodeliste | "nasjonalt" |
| `innendors` | boolean | Ja | true/false | false |
| `arrangør` | tekst | Nei | Klubb/organisasjon | "Trondheim Friidrettsklubb" |

**Kodeliste `stevne_type`:**
- `lokalt` - Klubbstevne, kretskonkurranse
- `nasjonalt` - NM, NC, Landsstevner
- `internasjonalt` - Internasjonale stevner i Norge
- `mesterskap` - NM, EM, VM, OL

---

### 3.2 Resultat-rader

Én rad per resultat (én utøver, én øvelse, én runde).

#### Utøver-identifikasjon

| Felt | Type | Påkrevd | Beskrivelse | Eksempel |
|------|------|---------|-------------|----------|
| `fornavn` | tekst | Ja | | "Jakob" |
| `etternavn` | tekst | Ja | | "Ingebrigtsen" |
| `fodselsdato` | dato | Anbefalt | YYYY-MM-DD | "1990-09-19" |
| `fodselsaar` | tall | Alt. | Hvis ikke full dato | 1990 |
| `kjonn` | tekst | Ja | "M" eller "K" | "M" |
| `klubb` | tekst | Ja | Klubbnavn | "Sandnes IL" |
| `nasjonalitet` | tekst | Nei | ISO 3166-1 alpha-3, default "NOR" | "NOR" |

> **Utøver-matching:** Systemet matcher på `fornavn` + `etternavn` + `fodselsdato` + `klubb`. Ved usikker match flagges resultatet for manuell verifisering.

#### Øvelse

| Felt | Type | Påkrevd | Beskrivelse | Eksempel |
|------|------|---------|-------------|----------|
| `ovelse` | tekst | Ja | Standardisert øvelsesnavn (se kodeliste) | "100m" |
| `ovelse_klasse` | tekst | Nei | Aldersklasse hvis spesifikt heat | "U20" |

#### Prestasjon

| Felt | Type | Påkrevd | Beskrivelse | Eksempel |
|------|------|---------|-------------|----------|
| `resultat` | tekst | Ja | Se formateringsregler | "10.45" |
| `resultat_enhet` | tekst | Nei | Overstyrer default | "m", "sek", "poeng" |
| `vind` | tekst | Betinget | Påkrevd for vindmålte øvelser | "+1.5" eller "-0.3" |
| `plassering` | tall | Nei | 1, 2, 3... | 1 |
| `runde` | tekst | Nei | Se kodeliste | "finale" |
| `status` | tekst | Nei | Default "OK" | "OK" |

**Kodeliste `runde`:**
- `forsok` - Innledende heat
- `mellomheat` - Mellomrunde
- `semifinale`
- `finale`
- `a-finale`, `b-finale` - Ved delte finaler
- `kvalifisering` - Tekniske øvelser

**Kodeliste `status`:**
- `OK` - Godkjent resultat (default)
- `DNS` - Did Not Start
- `DNF` - Did Not Finish
- `DQ` - Diskvalifisert
- `NM` - No Mark (tekniske øvelser)

#### Tilleggsinformasjon

| Felt | Type | Påkrevd | Beskrivelse | Eksempel |
|------|------|---------|-------------|----------|
| `dato` | dato | Nei | Hvis annen enn stevnedato | "2025-06-15" |
| `heat` | tall | Nei | Heat-nummer | 3 |
| `bane` | tall | Nei | Banenummer | 5 |
| `reaksjon` | tekst | Nei | Reaksjonstid | "0.142" |
| `kommentar` | tekst | Nei | Fritekst | "Personlig rekord" |

---

## 4. Formateringsregler for resultater

### 4.1 Løpsøvelser (tid)

| Format | Eksempel | Brukes for |
|--------|----------|------------|
| `SS.hh` | `10.45` | Sprint (100m, 200m) |
| `SS.hh` | `45.67` | 400m |
| `M:SS.hh` | `1:45.23` | 800m, 1500m |
| `MM:SS.hh` | `13:05.45` | 5000m |
| `H:MM:SS` | `2:05:34` | Maraton (sekunder OK) |

> Hundredeler er standard. Tideler aksepteres for manuell tidtaking.

### 4.2 Tekniske øvelser (lengde/høyde)

| Format | Eksempel | Brukes for |
|--------|----------|------------|
| `M.cm` | `8.95` | Lengde, tresteg |
| `M.cm` | `2.10` | Høyde, stav |
| `MM.cm` | `23.12` | Kule, diskos, slegge, spyd |

### 4.3 Mangekamp (poeng)

| Format | Eksempel |
|--------|----------|
| `PPPP` | `8521` |

---

## 5. Øvelse-kodeliste

### 5.1 Løp

| Kode | Øvelse |
|------|--------|
| `60m` | 60 meter |
| `100m` | 100 meter |
| `200m` | 200 meter |
| `400m` | 400 meter |
| `800m` | 800 meter |
| `1500m` | 1500 meter |
| `3000m` | 3000 meter |
| `5000m` | 5000 meter |
| `10000m` | 10000 meter |
| `60mh` | 60 meter hekk |
| `100mh` | 100 meter hekk (kvinner) |
| `110mh` | 110 meter hekk (menn) |
| `400mh` | 400 meter hekk |
| `3000mhinder` | 3000 meter hinder |

### 5.2 Hopp

| Kode | Øvelse |
|------|--------|
| `hoyde` | Høyde |
| `stav` | Stav |
| `lengde` | Lengde |
| `tresteg` | Tresteg |

### 5.3 Kast

| Kode | Øvelse |
|------|--------|
| `kule` | Kule |
| `diskos` | Diskos |
| `slegge` | Slegge |
| `spyd` | Spyd |

### 5.4 Mangekamp

| Kode | Øvelse |
|------|--------|
| `5kamp` | Femkamp (innendørs) |
| `7kamp` | Sjukamp |
| `10kamp` | Tikamp |

### 5.5 Stafetter

| Kode | Øvelse |
|------|--------|
| `4x100m` | 4 x 100 meter |
| `4x400m` | 4 x 400 meter |

### 5.6 Gange

| Kode | Øvelse |
|------|--------|
| `3000mg` | 3000 meter gange |
| `5000mg` | 5000 meter gange |
| `10000mg` | 10000 meter gange |
| `20kmg` | 20 km gange |

> **Merk:** For aldersbestemte øvelser med andre spesifikasjoner (hekkehøyder, redskaper), bruk samme kode. Systemet bestemmer spesifikasjoner basert på kjønn og aldersklasse.

---

## 6. Vindmålte øvelser

Følgende øvelser krever `vind`-felt for at resultatet skal være gyldig for statistikk:

- 100m, 200m, 100mh, 110mh
- Lengde, tresteg

**Format:** `+1.5` eller `-0.3` eller `0.0`

**Spesialverdier:**
- Tom/mangler = ikke målt
- `NWI` = No Wind Information (eldre resultater)

---

## 7. CSV-format

### 7.1 Filstruktur

```csv
#STEVNE
stevne_navn,stevne_dato,stevne_sted,innendors,stevne_type
"NM innendørs 2025","2025-03-01","Ullevaal",true,"mesterskap"

#RESULTATER
fornavn,etternavn,fodselsdato,kjonn,klubb,ovelse,resultat,vind,plassering,runde,status
"Jakob","Ingebrigtsen","1990-09-19","M","Sandnes IL","1500m","3:32.45","",1,"finale","OK"
"Karsten","Warholm","1996-02-28","M","Dimna IL","400mh","47.12","",1,"finale","OK"
```

### 7.2 Regler

- Encoding: UTF-8
- Separator: Komma (`,`)
- Tekstfelt med komma eller anførselstegn: Omslutt med `""`
- Første rad etter `#STEVNE` er header
- Første rad etter `#RESULTATER` er header
- Tomme felter: tomt (ikke mellomrom)

---

## 8. JSON-format

```json
{
  "format_versjon": "1.0",
  "stevne": {
    "navn": "NM innendørs 2025",
    "dato": "2025-03-01",
    "dato_slutt": null,
    "sted": "Oslo",
    "arena": "Ullevaal",
    "land": "NOR",
    "type": "mesterskap",
    "innendors": true,
    "arrangor": "Norges Friidrettsforbund"
  },
  "resultater": [
    {
      "utover": {
        "fornavn": "Jakob",
        "etternavn": "Ingebrigtsen",
        "fodselsdato": "1990-09-19",
        "kjonn": "M",
        "klubb": "Sandnes IL",
        "nasjonalitet": "NOR"
      },
      "ovelse": "1500m",
      "resultat": "3:32.45",
      "plassering": 1,
      "runde": "finale",
      "status": "OK"
    },
    {
      "utover": {
        "fornavn": "Karsten",
        "etternavn": "Warholm",
        "fodselsdato": "1996-02-28",
        "kjonn": "M",
        "klubb": "Dimna IL",
        "nasjonalitet": "NOR"
      },
      "ovelse": "400mh",
      "resultat": "47.12",
      "plassering": 1,
      "runde": "finale",
      "status": "OK"
    }
  ]
}
```

---

## 9. Validering

Ved import valideres følgende:

### 9.1 Påkrevde felter
- Alle påkrevde felter må være utfylt
- Stevne må ha navn, dato, sted, innendørs-flag
- Resultat må ha utøver (navn, kjønn, klubb), øvelse, resultat

### 9.2 Formatvalidering
- Datoer må være gyldige (YYYY-MM-DD)
- Resultater må matche forventet format for øvelsen
- Vind må være numerisk med fortegn

### 9.3 Logisk validering
- Vindmålte øvelser utendørs bør ha vind (advarsel hvis mangler)
- Resultat må være "rimelig" for øvelsen (fanger opplagte feil)
- Plassering må være unik per øvelse/runde

### 9.4 Utøver-matching
- Søker etter eksakt match på navn + fødselsdato
- Ved usikkerhet: fuzzy matching på navn + klubb
- Ukjente utøvere flagges for manuell godkjenning

---

## 10. Feilhåndtering

Ved feil returneres:

```json
{
  "status": "delvis_importert",
  "importert": 45,
  "feilet": 3,
  "advarsler": 12,
  "feil": [
    {
      "rad": 23,
      "felt": "resultat",
      "verdi": "10.456",
      "melding": "Ugyldig resultatformat for 100m (forventet SS.hh)"
    },
    {
      "rad": 31,
      "felt": "vind",
      "verdi": "",
      "melding": "Mangler vindmåling for 200m utendørs"
    }
  ],
  "advarsler": [
    {
      "rad": 15,
      "melding": "Utøver 'Jon Hansen' ikke funnet - opprettet som ny"
    }
  ]
}
```

---

## 11. Stafetter (spesialtilfelle)

For stafetter inkluderes alle lagmedlemmer:

```json
{
  "ovelse": "4x100m",
  "resultat": "38.45",
  "plassering": 1,
  "lag": {
    "navn": "Sandnes IL",
    "medlemmer": [
      {"fornavn": "Ola", "etternavn": "Nordmann", "etappe": 1},
      {"fornavn": "Kari", "etternavn": "Nordmann", "etappe": 2},
      {"fornavn": "Per", "etternavn": "Hansen", "etappe": 3},
      {"fornavn": "Lise", "etternavn": "Jensen", "etappe": 4}
    ]
  }
}
```

CSV-variant:
```csv
ovelse,resultat,plassering,lag_navn,etappe1_fornavn,etappe1_etternavn,etappe2_fornavn,...
"4x100m","38.45",1,"Sandnes IL","Ola","Nordmann","Kari","Nordmann",...
```

---

## 12. Tekniske øvelser med forsøk

For tekniske øvelser kan alle forsøk inkluderes:

```json
{
  "utover": {...},
  "ovelse": "lengde",
  "resultat": "8.12",
  "vind": "+0.5",
  "plassering": 1,
  "forsok": [
    {"nr": 1, "resultat": "7.85", "vind": "+1.2"},
    {"nr": 2, "resultat": "x", "vind": null},
    {"nr": 3, "resultat": "8.12", "vind": "+0.5"},
    {"nr": 4, "resultat": "7.95", "vind": "-0.3"},
    {"nr": 5, "resultat": "x", "vind": null},
    {"nr": 6, "resultat": "8.01", "vind": "+0.8"}
  ]
}
```

> **Merk:** `forsok` er valgfritt. Hvis ikke inkludert, lagres kun beste resultat.

---

## 13. Høyde/stav med høyder

```json
{
  "utover": {...},
  "ovelse": "hoyde",
  "resultat": "2.10",
  "plassering": 1,
  "hoyder": [
    {"hoyde": "1.90", "forsok": "o"},
    {"hoyde": "1.95", "forsok": "o"},
    {"hoyde": "2.00", "forsok": "xo"},
    {"hoyde": "2.05", "forsok": "xxo"},
    {"hoyde": "2.10", "forsok": "o"},
    {"hoyde": "2.15", "forsok": "xxx"}
  ]
}
```

**Forsøk-notasjon:**
- `o` = godkjent
- `x` = bommet
- `-` = hoppet over
- Kombineres: `xo` = bom, godkjent

---

## 14. Endringslogg

| Versjon | Dato | Endring |
|---------|------|---------|
| 1.0 | 2025-01 | Første utkast |

---

## 15. Åpne spørsmål

1. **Utøver-ID:** Bør arrangører kunne sende med en nasjonal utøver-ID hvis kjent?
2. **Stevne-ID:** Bør det kobles til iSonen-ID for terminlisten?
3. **Reaksjonstider:** Skal disse lagres systematisk?
4. **Mellomtider:** Skal splits lagres for mellom-/langdistanse?
5. **Elektronisk vs. manuell tidtaking:** Bør dette flagges?

---

## Eksempel: Komplett CSV-fil

```csv
#STEVNE
stevne_navn,stevne_dato,stevne_sted,stevne_arena,innendors,stevne_type,arrangor
"Trondheim Games 2025","2025-06-14","Trondheim","Øya stadion",false,"nasjonalt","Trondheim Friidrettsklubb"

#RESULTATER
fornavn,etternavn,fodselsdato,kjonn,klubb,ovelse,resultat,vind,plassering,runde,heat,bane,status,kommentar
"Salum","Kashafali","1993-04-14","M","Norna-Salhus IL","100m","10.12","+1.2",1,"finale","",4,"OK","Sesongbeste"
"Henrik","Larsson","1998-07-22","M","IK Tjalve","100m","10.34","+1.2",2,"finale","",5,"OK",""
"Thomas","Olsen","1995-03-11","M","Sturla IF","100m","10.45","+1.2",3,"finale","",6,"OK",""
"Petter","Nilsen","2001-08-30","M","Ull/Kisa","100m","","",0,"finale","",3,"DNS",""
"Marie","Hansen","1999-05-15","K","SK Vidar","hoyde","1.85","",1,"finale","","","OK","Pers"
"Sondre","Guttormsen","2001-06-12","M","Lillehammer IF","stav","5.81","",1,"finale","","","OK","NR"
```
