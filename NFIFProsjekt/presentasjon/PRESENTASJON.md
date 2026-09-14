# Ny statistikk- og aktivitetsplattform
## Athlete Mindset AS · 17. september 2026

---

# Hvem vi er

**Athlete Mindset AS** · org.nr. 937 878 818 · del av Fire S Invest AS

Idrettsteknologi og idrettsdata · agentvirksomhet · trenervirksomhet

| | |
|---|---|
| **Atle Guttormsen** | PhD anvendt økonometri · WA-dommer · styreerfaring klubb, krets og forbund |
| **Simen Guttormsen** | PhD-stipendiat kvantitativ finans · Princeton, Duke · olympier |
| **Sondre Guttormsen** | Sport management, UT Austin · gründer Athlete Mindset Inc. · olympier |

Vi driver **friidrettsresultater.no** i dag.

---

# Utgangspunktet

## 1 953 356

resultater i drift, normalisert og søkbare

| | |
|---|---:|
| Fra 2013 og senere | 1 704 877 |
| Alle-tiders-materiale før 2013 | 248 479 |
| Utøvere | 87 939 |
| Stevner, tilbake til 1922 | 48 548 |
| Siste stevne inne | 2. september 2026 |

**Migreringen er ikke et estimat. Den er gjennomført.**

---

# Demo

friidrettsresultater.no

1. Forsiden
2. En utøverprofil
3. Årsliste med filtre
4. NM-kvalifisering
5. Administrasjon og datakvalitet

---

# Migrering: hva som er gjort

| | |
|---|---|
| **2013–2026** | Fulldybde. Hvert stevne kontrollert mot kilden, stevne for stevne. |
| **2011–2012** | Kildens oppstartsperiode. Kontrolleres nå. |
| **Før 2011** | Finnes ikke som sesongdata hos kilden. Alle-tiders-lister er importert. |

### Hva kontrollen avdekket

Importen regnet et stevne som ferdig når det hadde mer enn ti resultater.
Delvis importerte stevner ble derfor aldri hentet på nytt.

**Over en halv million resultater manglet.** Feilen er rettet i importlogikken,
og kontrollen mot kilden kjøres nå rutinemessig.

---

# Opprydding: hva vi vet mangler

| Sak | Omfang |
|---|---:|
| Utøvere uten registrert kjønn | 2 268 av 87 939 |
| Resultater uten klubbtilknytning | 2 202 |
| Resultater uten beregnet prestasjonsverdi | 2 448 |
| Utøvere uten fødselsår | 68 |
| Navn med tegnfeil eller klubbnavn i navnestrengen | 37 |
| Dubletter av utøvere og klubber | løpende |

**Basen er ikke ferdig kvalitetssikret.** Arbeidet har vært prioritert mot
innsamling og fullstendighet først. Man kan ikke vaske data man ikke har.

---

# Opprydding: hvordan vi lukker det

### 1. Systemet finner feilene, ikke menneskene

Resultat bedre enn norsk rekord · urimelig persforbedring · manglende vind i
vindavhengig øvelse · presisjon som ikke stemmer med tidtakingsmetode ·
aldersklasse mot fødselsår · redskapsvekt mot klasse · samme utøver to steder
samme dag

Hver kontroll gir en oppgave med begrunnelse, ikke en stille avvisning.

### 2. Sammenligning mot uavhengig kilde

Vi kjørte basen mot SRUs NM-regneark for 100 m kvinner.
Regnearket hadde 101 navn, vi fant 97, **89 var de samme.**

Avvikene var navnevarianter, en navneendring, en utenlandsk utøver i norsk
klubb. Det er arbeidslisten.

---

# Tidsplan for opprydding

| Når | Hva |
|---|---|
| **Okt–des 2026** | Kjønn, klubbtilknytning, fødselsår. Automatiske kontroller i drift. |
| **Okt–des 2026** | Dublettverktøy for utøvere og klubber, med sporing av hver sammenslåing. |
| **Fra 2027** | Kvartalsvis kontroll mot kilden og mot uavhengige lister. Datakvalitetsrapport til NFIF årlig. |

Vi lover ikke en feilfri base 01.01.2027.
Vi lover at feilene er **kjente, tellbare og synkende**, og at det finnes
verktøy for å rette dem.

---

# Veien til 1. januar 2027

| Frist | Leveranse |
|---|---|
| **Okt** | **Egen innsamling av resultatlister, uavhengig av dagens base** |
| Nov | Kvalitetsnivå A/B/C med regelmotor og filtrering |
| Nov | Generisk importrammeverk · eksport til Excel og CSV |
| Des | Flagging: bane TR14.1/TR43.1, World Rankings, blandede heat, utenlandske utøvere, WMA, ikke-ratifisert |
| Des | Dokumentert JSON-API · regions- og kretsstatistikk |
| Des | Masters og aldersklasserekorder · WCAG 2.1 AA · DPIA og databehandleravtale |

**Den viktigste milepælen er innsamlingen, ikke funksjonaliteten.**
Vi henter i dag fra den basen som skal erstattes. Egen innhenting må være i
drift før overgangen, ikke ved den. Vi kjører begge kilder parallelt ut året.

---

# Integrasjoner

Prioritet etter §13: API først, strukturerte filer, så Excel og CSV.
Manuell behandling kun som siste utvei.

### Vi tar imot enden av dataflyten

NFIF arbeider allerede med Buypass om iSonen mot OpenTrack og FriRes, og mot
EQ Timing for løp utenfor bane. Plattformen skal koble seg på det arbeidet,
ikke definere det på nytt.

### Det vi ønsker oss

En avtalt måte å levere resultatlister fra stevnesystemene rett inn, med
stevne, øvelse, klasse, utøver, klubb, resultat, vind og tidtakingsmetode.

Vi stiller gjerne på et teknisk møte og blir enige om formatet.

---

# Etter nyttår

| Fase | Innhold | Periode |
|---|---|---|
| 2 | Integrasjoner · automatisert import · rollestyring for forbund, krets, klubb og arrangør | Q1–Q3 2027 |
| 3 | **Løp utenfor bane**: datamodell, import fra tidtakere, rankinglister, løpssider | Q1–Q3 2027 |
| 3 | **Aktivitetsmodul**: unike deltakere, starter, fullførte, utvikling over tid, per klubb, krets, alder og kjønn | Q2–Q4 2027 |
| 4 | Historisk utvidelse etter kartlegging | 2028 |

Løp utenfor bane avgrenses til **løp på den offisielle terminlisten**.

---

# Det vi trenger fra NFIF

| | Til hva | Når |
|---|---|---|
| Terminlisten, løpende | Avgjør godkjenning, og dermed kvalitetsnivå etter §6 | Snarest |
| Lisensregisteret | Lisenskriteriet i nivå A | Snarest |
| Klubb-til-krets-mapping | Kretsstatistikk. Kan ikke utledes trygt fra klubbnavn. | Snarest |
| Kontaktpunkt mot arrangører og tidtakere | Egen innsamling av resultatlister | September |
| Melding om underkjente stevner | Oppdatering av kvalitetsnivå og §7-koder | Fra oppstart |

---

# Oppsummert

### Plattformen finnes, med norske data i

Migreringen er gjennomført. Åtte av fjorten obligatoriske krav er i drift.

### Vi er åpne om det som ikke er ferdig

Basen er ikke ferdig kvalitetssikret, og løp utenfor bane må bygges.
Begge deler står i tilbudet, med plan og frister.

### Vi er miljøet dette gjelder

Doktorgrad i anvendt økonometri og WA-dommerkompetanse i samme person.
To olympiere med egne resultater i basen.

**Takk. Spørsmål?**
