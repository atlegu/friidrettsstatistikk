# Kravsporingsmatrise

**Versjon:** 2.0 — 17.10.2026 (erstatter 1.0 av 09.08.2026)
**Status verifisert mot kodebase og produksjonsbase 17.10.2026**

Gjennomgang av NFIFs kravspesifikasjon («New Statistics and Activity Platform for
Norwegian Athletics», 10 sider) punkt for punkt, mot det som faktisk finnes på
friidrettsresultater.no og i basen i dag.

**Statuskoder**
`I DRIFT` — finnes i produksjon ·
`DELVIS` — deler finnes, må ferdigstilles ·
`MANGLER` — må bygges ·
`AVTALE` — løses kontraktuelt, ikke teknisk

**Basen i tall (17.10.2026):** 1 468 731 baneresultater (1 245 489 fra 2013, 223 242
før 2013, eldste 1921), 87 842 utøvere, 302 øvelser, 44 945 stevner. Løp utenfor bane:
646 arrangementer, 1 608 løp, 159 465 resultater (EQ Timing og Ultimate).

---

## §22 Obligatoriske krav

| # | Krav | Status | Hva finnes / hva mangler |
|---|---|---|---|
| 1 | NFIF eier alle data | AVTALE | Formaliseres i kontrakt (eksportrett, exit). Alt ligger i standard Postgres og kan eksporteres. |
| 2 | Offisiell statistikkplattform | AVTALE | — |
| 3 | Banestatistikk | I DRIFT | Inne og ute, alle øvelser og aldersklasser, årslister, alle tiders, rekorder, masters. |
| 4 | Løpsstatistikk | DELVIS | Endret fra MANGLER. /gatelop: løpssider, årsbeste på 5 km, 10 km, halvmaraton og maraton, kvalitetsnivå A/B/C, aldersklasser. Gjenstår: flere tidtakere, løyperegister, terreng/motbakke/fjell, rekorder (svar 1.2). |
| 5 | Utøverprofiler | I DRIFT | PB, SB, alle resultater, utviklingskurve, klubbhistorikk, NM-krav, medaljer, ikke godkjente resultater med årsak. Gateløp vises ikke på profilen ennå. |
| 6 | Nasjonal statistikk | I DRIFT | Årsstatistikk, alle tiders, rekorder, masters. |
| 7 | Klubbstatistikk | I DRIFT | Klubbside med årsstatistikk, alle tiders, klubbrekorder, antall utøvere og resultater. |
| 8 | Regionsstatistikk | MANGLER | Ingen klubber har krets/fylke (0 av 2 484). Krever klubb-til-krets-liste fra NFIF. Når den finnes, er regionstatistikk en filtrering på eksisterende data. |
| 9 | Stevnesider | I DRIFT | 44 945 stevner med resultater og lenker til utøvere. Fra 17.10: arrangør, arrangementstype, krets og iSonen-lenke fra terminlisten (stevner fra 2026, oppdateres hver natt), og ikke godkjente resultater merket med årsak. Eldre stevner har ingen kilde for arrangør. |
| 10 | Historiske data | I DRIFT | Fullt fra 2013 (kravets førsteprioritet). 223 242 resultater før 2013, tilbake til 1921. 1 006 godkjente mastersrekorder kontrollert og merket. |
| 11 | Kvalitetsklassifisering A/B/C | DELVIS | Endret fra MANGLER. I drift for løp utenfor bane, med filter. Mangler for bane: der gjelder i praksis «godkjent/ikke godkjent» + vind/håndtid, men ikke A/B/C-merking. |
| 12 | API-støtte | MANGLER | Ingen offentlig API eller dokumentasjon. Basen har et internt REST-grensesnitt (Supabase/PostgREST) som et dokumentert JSON-API kan bygges på. |
| 13 | Eksportfunksjonalitet | I DRIFT | CSV (Excel-vennlig) fra årslister, alle tiders, klubbens årsliste, stevnesider og aktivitetssiden. Bare for administratorer, hver nedlasting logges (personvern). Kan utvides med roller, f.eks. klubber for egne lister. |
| 14 | Mobilvennlig løsning | I DRIFT | Responsivt grensesnitt. WCAG 2.1 AA bør dokumenteres. |

**Oppsummert:** 9 i drift, 2 delvis, 2 mangler (region, API), 2 avtale. Ingen er
teknisk risikofylte; region avhenger av en liste fra NFIF.

---

## §5–§19 Kapittelkrav

| § | Krav | Status | Hva finnes / hva mangler |
|---|---|---|---|
| §5 | Skille prestasjon / rekord / aktivitet | DELVIS | Løp utenfor bane: nivå C = registrert aktivitet. Bane: godkjente resultater mot ikke godkjente (status IKKE_GODKJENT). Aktivitetssiden teller deltakelse uavhengig av godkjenning. |
| §6 | Kvalitetsnivå A/B/C med filter | DELVIS | Se §22 nr. 11. Nivå A krever lisens (lisensregisteret) og godkjent stevne (iSonen) for å settes fullt maskinelt. |
| §7 | Inne og ute, alle øvelser, alle aldre | I DRIFT | 302 øvelser, aldersklasser etter kalenderår, barn til og med 11 år lagret men ikke vist. |
| §7 | Senior, junior, ungdom, masters | I DRIFT | Masters med egne rekorder (godkjente rekorder merket). |
| §7 | Bevare kjernefunksjonen i dagens plattform | I DRIFT | Årslister, alle tiders, utøver-, klubb- og stevnesider, rekorder. |
| §7 | Egne rekorder for standardbane og kort bane (TR14.1/TR43.1) | DELVIS | Inne og ute holdes adskilt. For stor innendørsbane fanges via kildens underkjenning. Baneregister per anlegg mangler. |
| §7 | Flagg: innendørs | I DRIFT | Rettet 16.10: 55 innendørsmesterskap sto som ute. |
| §7 | Flagg: World Ranking-stevne | DELVIS | Løp utenfor bane: ja (fra EQ Timing). Bane: mangler. |
| §7 | Flagg: mixed heats | MANGLER | Kilden har ikke opplysningen. |
| §7 | Flagg: utenlandske utøvere i norsk klubb | DELVIS | I bruk i listene (vist med *, ikke i rekorder). Men nasjonalitet er bare satt for 32 utøvere; resten står som norske. Krever lisensregisteret. |
| §7 | Flagg: masters etter WMA-regler | DELVIS | Godkjente mastersrekorder merket; kast på innendørsmesterskap regnes som ute. Ikke eget flagg per stevne. |
| §7 | Flagg: ikke ratifisert, med årsakskode | I DRIFT | Endret fra MANGLER. Status IKKE_GODKJENT med kildens årsak (kort bane, ikke medlem av NFIF, feil startutstyr, ekstraløp …). Hentes fra kildens utøversider; full gjennomgang pågår, deretter nattlig. Kodeverket er «TBD» hos NFIF; i dag lagres årsaken som tekst. |
| §7 | Flagg: håndtid | I DRIFT | Presisjonsbasert, løp under 800 m. Ryddet 16.–17.10. |
| §8 | Utenbaneløp: distanser | DELVIS | 5 km, 10 km, halvmaraton, maraton rangeres. 3 km, ultra, stafett, terreng, fjell: registreres (nivå C), ikke egne lister. |
| §8 | Metadata per løp | DELVIS | Distanse, type (gren), løypemåling (A/B/C), arrangør, sted, dato, antall deltakere og fullførte, klubb: ja. Tidtakingsmetode, kjønns- og aldersfordeling: kan utledes, vises ikke. |
| §9 | Utøverprofil med alle punkter | DELVIS | Alt unntatt løp utenfor bane på profilen. |
| §9 | Navneendring, klubbovergang, dubletter | DELVIS | Sammenslåing av utøvere (admin og skript), klubbhistorikk utledet fra resultatene. Navnehistorikk mangler. Tabellen club_memberships er tom. |
| §10 | Klubbstatistikk | DELVIS | Lister, resultathistorikk, aktive utøvere, antall resultater, utvikling. Mangler antall arrangerte stevner (arrangør mangler, se §11). |
| §10 | Regionsstatistikk og sammenligning | MANGLER | Se §22 nr. 8. |
| §11 | Stevneside: navn, dato, sted, resultater, lenker | I DRIFT | — |
| §11 | Stevneside: arrangør, type, godkjennings-/statusinfo | I DRIFT | Fra terminlisten for stevner fra 2026; World Ranking-stevner merkes; ikke godkjente resultater merket med årsak. |
| §12 | Aktivitet: stevner, starter, unike deltakere, klubb, alder, kjønn, øvelse, utvikling | I DRIFT | /aktivitet med kube over kjønn, alder og kategori, CSV-eksport. |
| §12 | Aktivitet per region | MANGLER | Krets mangler. |
| §12 | Antall fullførte | DELVIS | Løp utenfor bane ja; bane ikke relevant på samme måte. |
| §13 | iSonen | DELVIS | Terminlisten (iSonen-data) hentes hver natt og kobles mot resultatene. Resultat-API først etter tildeling. |
| §13 | OpenTrack | MANGLER | — |
| §13 | FriRes/LiveRes | MANGLER | Tilgang til feeden er avklart (frisys.json), importør ikke bygget. |
| §13 | EQ Timing | I DRIFT | Åpent API, importør i drift. Ikke lagt inn i den nattlige jobben ennå. |
| §13 | Ultimate Sport Service | DELVIS | Importør bygget; 2026 delvis importert. |
| §13 | Andre (Racedays m.fl.) | MANGLER | API-nøkkel etterspurt. |
| §14 | Forberedt for iSonen-arbeidsflyt | DELVIS | Arkitekturen tar imot strukturerte data; avhenger av Buypass/iSonen. |
| §15 | Import 2013+ | I DRIFT | — |
| §15 | Import 2001–2012 og eldre | DELVIS | Importert fra alle tiders-listene. Kvalitetsfeil funnet og rettet 16.–17.10 (resultater på feil utøver med samme etternavn, avkortede tider). |
| §15 | Beskrive import, validering og videreutvikling | I DRIFT | Skript med tørrkjøring, reserve og logg; nattlige kontroller (test_fullstendighet). |
| §16 | Norske rekorder | I DRIFT | Bare norske statsborgere (rettet 16.10). |
| §16 | Aldersklasserekorder | DELVIS | Senior og junior; per aldersklasse finnes alle tiders-lister, ikke offisielle rekorder. |
| §16 | Mastersrekorder | I DRIFT | 1 006 godkjente rekorder merket; 902–912 av 1 004 stemmer, avvik dokumentert. |
| §16 | Bestenoteringer | I DRIFT | — |
| §16 | Godkjenningsstatus | DELVIS | Avviksliste med godkjenning i admin (mulige rekorder). Ikke en full rekordprotokoll. |
| §16 | Dokumentasjon og historikk | MANGLER | Rekordprogresjon og dokumentasjon per rekord. |
| §16 | Skille rekordgodkjent / statistikkgodkjent / aktivitet | DELVIS | Se §6. |
| §17 | Mobil, nettbrett, PC | I DRIFT | — |
| §17 | Filter: utøver, klubb, alder, kjønn, øvelse, sesong, dato, stevne | I DRIFT | — |
| §17 | Filter: distanse, kvalitetsnivå | DELVIS | For løp utenfor bane. |
| §17 | Filter: region | MANGLER | Krets mangler. |
| §18 | Dokumentert JSON-API | MANGLER | Se §22 nr. 12. |
| §18 | Eksport Excel/CSV | I DRIFT | Se §22 nr. 13. |
| §19 | Personvern og sikkerhet | DELVIS | Radnivåsikkerhet, roller, skriverett bare for administratorer (strammet inn 16.10), barn til og med 11 år ikke vist. Mangler skriftlig beskrivelse/DPIA og databehandleravtale. |

---

## §20 Faser

| Fase | Innhold | Status |
|---|---|---|
| 1 Kjerne | Bane- og løpsstatistikk, profiler, nasjonal, stevner, klubb og region | Alt unntatt region og løp i full bredde er i drift. |
| 2 Integrasjoner | API, automatisk import, validering, admin | Admin og validering i drift (avvik, terminliste, import, utøvere, stevner, brukere). Nattlig import fra dagens kilde; EQ Timing og Ultimate kjøres foreløpig manuelt. API mangler. |
| 3 Aktivitet | Unike deltakere, utvikling, klubb, region, distanse, dashbord | Aktivitetssiden dekker alt unntatt region og gatedistanser. |
| 4 Historikk | Mer historikk, datavask | I gang: masterrekorder, etternavnsfeil, avkortede tider, ikke godkjente resultater. |

## §23 Ønskede tilleggsfunksjoner

| Krav | Status | Kommentar |
|---|---|---|
| Fullautomatisk resultatimport | DELVIS | Nattlig import og avstemming mot dagens kilde, terminlistekontroll og ikke godkjente resultater. Avhenger av iSonen/FriRes for full automatisering. |
| Analysemoduler | DELVIS | Aktivitetssiden og publiserte analyser (trenerartikkel, NCC-kohort). Produktmodul gjenstår. |
| Grafiske utviklingskurver | I DRIFT | — |
| Avansert aktivitetsanalyse | DELVIS | Aktivitetskube; region mangler. |
| Datavaskverktøy | I DRIFT | Avviksliste i admin, sammenslåing, opprydningsskript med tørrkjøring og reserve. |
| Offentlige dashbord | DELVIS | /aktivitet er offentlig. |
| Utvidet historisk statistikk | DELVIS | Se §15. |
| Åpne API-er for partnere | MANGLER | Se §18. |

## §24 Tidslinje

| Krav | Status |
|---|---|
| Løsning som dekker alle baneresultater innen 01.01.2027 | Oppfylt i dag. |
| Veikart for løp utenfor bane innen 31.12.2026 | Planlagt (svar 1.2). |

---

## Prioritert mangelliste

**Før 01.01.2027 (obligatorisk eller lett synlig for NFIF):**

| # | Mangel | Krav | Avhengighet | Omfang |
|---|---|---|---|---|
| 1 | Dokumentert JSON-API (lesetilgang for godkjente brukere) | §18, §22 nr. 12 | — | Middels |
| 2 | ~~Eksport til CSV/Excel~~ — i drift 17.10 | §18, §22 nr. 13 | — | — |
| 3 | Regionsstatistikk og regionfilter | §10, §17, §22 nr. 8 | Klubb-til-krets-liste fra NFIF | Lite når listen finnes |
| 4 | ~~Stevneside: arrangør, type, merking~~ — i drift 17.10 | §11, §22 nr. 9 | — | — |
| 5 | Kvalitetsnivå for bane (A/B/C) med filter | §6, §16 | Delvis lisensregisteret | Middels |
| 6 | Personvernbeskrivelse og DPIA | §19 | — | Lite |

**Etter 01.01.2027 (veikart):**

| # | Mangel | Krav |
|---|---|---|
| 7 | Løp utenfor bane: flere tidtakere, løyperegister, terreng/motbakke/fjell, rekorder, på utøverprofilen | §8, §9 |
| 8 | Integrasjoner: FriRes/LiveRes, OpenTrack, iSonen-resultater | §13, §14 |
| 9 | Rekorder per aldersklasse, rekordprogresjon og dokumentasjon | §16 |
| 10 | Flagg: World Ranking (bane), mixed heats, WMA per stevne; nasjonalitet fra lisensregisteret | §7 |
| 11 | Baneregister (TR14.1/TR43.1) | §7 |
| 12 | Navnehistorikk | §9 |

---

## Det kravspekken ikke nevner, men som vi tar med

| Tema | Begrunnelse |
|---|---|
| Universell utforming, WCAG 2.1 AA | Lovkrav for norske publikumsrettede nettsteder. |
| Særskilt vern av mindreåriges data | Barn til og med 11 år lagres, men vises ikke offentlig. |
| Beredskap ved topplast | NM, Bislett Games og store mosjonsløp. |
| Exit og ikke-innelåsing | Standardteknologi og full overlevering. |
