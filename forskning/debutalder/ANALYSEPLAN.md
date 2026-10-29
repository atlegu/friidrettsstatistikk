# A3 — Debutalder og varig deltakelse: analyseplan

*Versjon 1, 29. oktober 2026. Skrives og committes FØR noen eksponering–utfall-modell estimeres; ingen ekstern forhåndsregistrering (samme beslutning som A1, 29.10.2026). Arbeidstittel: «Does starting age predict who stays? Competition debut age and long-term participation in Norwegian youth track and field».*

---

## 1. Bakgrunn og motivasjon

To litteraturer gir motsatte prediksjoner om startalder. Spesialiserings­forsiktighets­linjen antyder at tidlig inngang øker risikoen for utbrenthet og frafall; den største prospektive frafallsstudien som måler startalder (Van Yperen m.fl. 2022, fotball) fant det motsatte — frafallerne hadde **begynt senere** — og anbefalte rekruttering fra seksårsalderen. Ingen populasjonsstudie har testet sammenhengen i en individuell idrett. Registeret er uvanlig godt egnet: komplett fra 2011, slik at alle født 2001 og senere har hele konkurransekarrieren registrert fra 10-årsalderen, uten venstretrunkering.

To egne funn skjerper spørsmålet. Trenerartikkelen (2026) viste at **tenåringsdebuten er halvert** (debut 14–19 år: ~900 → 300–500/år) mens 10-årsrekrutteringen er på vei tilbake — forbundet trenger å vite hva en sen debutant faktisk er verdt i seniorkonvertering. Og RAE-artikkelen (Sports Medicine – Open, antatt) legger seleksjonen til inngangsfasen; debutalder er inngangens andre dimensjon ved siden av fødselskvartal.

**Presisjonskrav (fastlagt på forhånd):** Eksponeringen er **konkurransedebut** — første godkjente resultat i registeret — ikke idrettsstart. Barn kan ha trent friidrett (eller andre idretter) i årevis før første stevne, og dette kan ikke observeres. Alle tolkninger formuleres deretter.

## 2. Spørsmål, estimander og tolkningsregler

**H1 (konvertering).** Blant alle debutanter 10–16 år (født 2001–2005): henger debutalder sammen med å bli aktiv senior? Estimander: OR per +1 års debutalder (lineær trend) og OR per debutalderskategori (referanse: debut ved 10), justert for kjønn, fødselskohort, region og klubbstørrelse. To-sidig: spesialiserings­forsiktighet predikerer at sen debut beskytter; early-engagement/Van Yperen predikerer at tidlig debut beskytter. En U-form er mulig; kategorisk visning er derfor primær, trenden sekundær.

**H2 (frafallstakt etter debut).** Går senere debutanter raskere ut *etter at de har begynt*? Estimand: HR per +1 års debutalder i en Cox-modell **med alder som tidsskala og forsinket inntreden ved debutalderen** (venstretrunkering håndtert eksplisitt; sensur for utøvere aktive i 2025–2026). Retningsprediksjon fra Van Yperen: HR > 1 for senere debut.

**H3 (landmark: historie mot nåtilstand).** Blant dem som fortsatt er aktive ved 17 år: tilfører debutalderen informasjon om seniorstatus utover kjønn, kohort og inneværende engasjement (konkurransedager ved 16–17)? A1/IJSSC-funnene tilsier at nåværende atferd dominerer historien; prediksjon: liten eller ingen tilleggseffekt.

**Tolkningsregler.** (i) Konkurransedebut ≠ idrettsstart; en «sen debutant» kan være en erfaren utøver fra annen idrett eller treningsgruppe — selvseleksjonen inn i sen debut er sannsynligvis sterk (motivert ungdom), og alle estimater er assosiasjoner. (ii) Exit fra registeret er ikke exit fra idrett (idrettsbytte usynlig), symmetrisk for tidlige og sene debutanter. (iii) Rå konverteringsandeler per debutalder sammenligner ulike seleksjonsregimer og rapporteres alltid sammen med de justerte estimatene og H2/H3, aldri alene.

## 3. Data og utvalg

- **Uttrekk:** frosset per 29.10.2026 (resultater t.o.m. dato), alle utøvere født **2001–2008**, alle godkjente resultater fra 2011. **Ingen prestasjonsvariabler hentes** — bare deltakelse (utøver, dato, stevne, klubb, status). I tråd med barneidrettsbestemmelsene brukes aldri nivådata under 13 år; i denne studien brukes nivådata ikke i det hele tatt.
- **Debut:** første dato med godkjent resultat, ved alder ≥10 (kalenderårsalder). Primærutvalg: debutalder 10–16. Debut ved 17+ rapporteres deskriptivt og inngår i en sensitivitet.
- **Kohorter:** primærutfall (senior ≥20) krever født **2001–2005** (alle har nådd 20 innen 2025-sesongen). Sekundærutfallet aktiv ved ≥17 bruker født 2001–2008.
- **Eksklusjoner:** ukjent kjønn; resultater med status ulik OK (telles i flyt).

## 4. Variabler

**Eksponering:** debutalder (10–16; kategorisk og lineær).
**Utfall:** primært *aktiv senior* (≥2 godkjente resultater i samme kalenderår ved ≥20, som A1/IJSSC); sekundært ≥1 ved ≥20; aktiv ved ≥17; karrierelengde (siste sesong − debutsesong + 1); «fortsatt aktiv» (resultat i 2025 eller 2026) som sensurindikator.
**Kovariater:** kjønn; fødselsår; region (modal krets i debutsesongen); klubb ved debut (modal klubb) og log klubbstørrelse (studieutøvere per klubb, proxy); fødselskvartal; debutårets konkurransedager (engasjement ved inngang — analyseres separat som «betinget på startengasjement», siden den kan ligge på årsaksveien); covid-flagg for debut i 2020–2021.

## 5. Modeller

1. **Deskriptivt:** debutanter per debutalder × fødselsår × kjønn; fødselskvartalsfordeling per debutalder (kobling til RAE-artikkelens inngangsseleksjon — eksplorativt); konverteringsandeler med KI.
2. **H1:** logistisk regresjon, født 2001–2005, debutalder kategorisk (ref. 10) og lineært; justeringssett som i §2; klubbklynge-robuste SE som sensitivitet.
3. **H2:** Cox med alder som tidsskala, inntreden ved debutalder, utgang ved siste aktive alder (+0,5 år), hendelse = ikke aktiv 2025/26; debutalder som kovariat (lineær; kategorisk som sensitivitet); Kaplan–Meier med forsinket inntreden per debutaldersgruppe (10–11, 12–13, 14–16).
4. **H3:** blant aktive ved 17 (født 2001–2005 for seniorutfallet): logit seniorstatus ~ debutalder + kjønn + kohort + konkurransedager ved 16–17.
5. **Robusthet:** uten covid-debutene (2020–21); utfallsvarianter; debut 17+ som egen kategori; betinget på debutårets volum; kohortsplitt (2001–2003 mot 2004–2005); fødselskvartal × debutalder (eksplorativt); retention k år etter debut (k = 1…5) per debutalder.

## 6. Styrke (grovt)

Fra dekningsspørringene 29.10.2026 (født 2001–2006): ca. 21 300 utøvere med debut 10–16 og ~800 seniorhendelser; født 2001–2005 anslås til ~17 000 med ~650–700 hendelser. Rikelig for kategoriske kontraster og interaksjoner.

## 7. Arbeidsflyt, etikk og åpenhet

Kode i `forskning/debutalder/`: `00_uttrekk.py` → `data_private/` (git-ignorert, regenererbart), `01_variabler.py`, `02_deskriptiv.py`, `03_modeller.py`, `04_figurer_tabeller.py`. Denne planen committes før 03 kjøres; manuset oppgir «analysis plan committed to version control before estimation; not externally preregistered». Offentlige konkurranseresultater; ingen enkeltpersoner identifiseres; ingen nivåanalyse (overhodet); samme hjemmelsvurdering som IJSSC/A1 (utenfor helseforskningsloven; Sikt-vurdering foreligger). Måltidsskrift: Scandinavian Journal of Medicine & Science in Sports eller European Journal of Sport Science.

## 8. Hva studien ikke gjør

Ingen kausal effekt av startalder; ingen observasjon av trening, andre idretter eller motivasjon; ingen prestasjonsanalyse. Studien leverer populasjonens faktiske konverterings- og frafallsmønstre etter konkurransedebutalder — tallgrunnlaget både spesialiserings­debatten og rekrutteringspolitikken mangler.
