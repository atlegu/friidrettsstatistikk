# A1 — Stagnasjon før exit: analyseplan

*Versjon 1, 29. oktober 2026. Utkast til forhåndsregistrering (OSF-teksten skrives på engelsk fra dette dokumentet før noen eksponering–utfall-modell estimeres). Arbeidstittel: «Stagnation before exit? Within-athlete performance progression, relative age, and retention in youth track and field — a population register study».*

---

## 1. Bakgrunn og motivasjon

Tre funn fra registeret peker mot samme uprøvde spørsmål:

1. **RAE-artikkelen** (Sports Medicine – Open, antatt) lanserer mastery-tolkningen — synlig egen fremgang holder utøvere i idretten, uavhengig av rangering — og varsler testen eksplisitt: *«A direct test of the mastery-experience interpretation would ask whether within-athlete performance progression, rather than performance level, predicts retention among relatively younger athletes specifically; the registry contains the necessary data, and this is a natural next step.»*
2. **JSAMS-artikkelen** viser at topplistene tømmes og fylles av utskifting, men studerer ikke hvem som forsvinner eller hvorfor.
3. **Frafallsartikkelen** (IJSSC, resubmittert) viser at volumet faller 12 %/23 % to/én sesong før exit, og at *nivå* ved ett stevne legger lite til volum — men prestasjons**banen** (fremgang/stagnasjon) er aldri målt som prediktor.

Ingen populasjonsstudie har koblet objektive progresjonsbaner til senere frafall. Planen under tester det, med prediksjonene skrevet ned før dataene ses (jf. testnotatets krav om forhåndsregistrering).

## 2. Spørsmål og hypoteser

**H1 (hovedtest).** Blant utøvere som fortsatt er aktive ved 15–16, predikerer within-utøver-fremgang fra 13–14 til 15–16 senere seniorstatus, utover nivå, konkurransevolum (nivå og endring) og kjønn. Estimand: OR per SD fremgang, med 95 % KI, og ΔAUC når fremgang legges til modellen.

**H2 (mastery-spesifikk).** Sammenhengen i H1 er sterkere hos relativt yngre utøvere (født sent i året). Estimand: interaksjon fremgang × fødselskvartal (lineær trend Q1→Q4; forventet positivt fortegn), pluss stratifiserte OR (Q1–Q2 mot Q3–Q4).

**H3 (innramming).** Er fremgang den virksomme prestasjonskomponenten? Sammenlign diskriminering: (kjønn + volum + fremgang) mot (kjønn + volum + nivå).

**Forhåndsdefinert tolkningsasymmetri (fra RAE-diskusjonen):** et svakt eller null-funn i H1 *falsifiserer ikke* mastery-mekanismen, fordi registeret ikke skiller disengasjement fra idrettsbytte — en utøver kan ha fremgang i en annen idrett. Et positivt H1+H2 styrker mekanismen; et nullfunn etterlater volum som engasjementssignal og svekker mekanismens mest direkte observerbare støtte uten å avgjøre den. Dette skrives inn i forhåndsregistreringen.

**Kobling til mekanismekartet** (arbeidsnotatet om tre påstander, avsnitt 3.3): H2 skiller delvis mellom mastery (mekanismeslekt med søk/match) og ren omvendt årsaksretning; fødselskvartal-mønstre i fremgang 15→19 taler til mekanisme 5 (modningstidspunkt). Full mekanismeavklaring loves ikke.

## 3. Data og utvalg

- **Kilde:** friidrettsregisteret (Supabase), uttrekk per fast dato etter oppryddingen oktober 2026. NB: `created_at`-filtre gjenskaper ikke historiske tilstander — uttrekket fryses som CSV med uttreksdato i filnavnet, og alle analyser kjøres fra frosne filer (samme regime som IJSSC-arbeidet).
- **Kohorter:** født 1998–2005 (alle har nådd minst alder 20 innen 2025-sesongen). Replikasjonssplitt: kohort A født 1998–2001, kohort B født 2002–2005.
- **Landmark-design:** inklusjon krever ≥1 OK-resultat ved alder 13–14 **og** ≥1 ved alder 15–16 («aktiv ved landmark»). Prediksjon skjer fra slutten av 16-årssesongen; dette gjør betingingen eksplisitt i stedet for skjult. **Flyt fra det frosne uttrekket (29.10.2026):** 32 447 utøvere født 1998–2006 → 12 938 med OK-resultat ved 13–14 → 4 910 også aktive ved 15–16 → 4 909 med kjent kjønn → 734 uten skårbar Tyrving i hovedgruppen i begge vinduer (herunder utøvere som helt forlot 13–14-hovedgruppen; fanges av bytter-sensitiviteten) og 3 i kjønn × gruppe-celler under 20 → **primærutvalg 3 808** (født 1998–2005), hvorav **648 (17,0 %) aktive seniorer**. 43 i landmark-utvalget mangler fødselsdato og inngår ikke i H2.
- **Eksklusjoner:** utøvere uten kjønn eller fødselsår; resultater med status IKKE_GODKJENT; manuelle tider (`is_manual_time IS NOT TRUE`-regelen); vindøvelser skåres primært på alle merker, med vindgyldig-only som sensitivitet (se §6).

## 4. Variabler

**Utfall (primær):** aktiv senior = ≥2 resultater i samme kalenderår ved alder ≥20 (identisk med frafallsartikkelen). Oppfølging t.o.m. uttreksdato; born 2005 har alder 20 i 2025 (komplett utendørssesong).
**Utfall (sekundære):** ≥1 resultat ved ≥20; aktiv ved ≥18 (tillater å ta inn født 2006); fast vindu 20–21 år.

**Eksponering (primær): fremgang.** Δ = (gj.snitt av de 3 beste Tyrving-skårede resultatene i utøverens hovedøvelsesgruppe ved 15–16) − (tilsvarende ved 13–14), standardisert innen kjønn × hovedøvelsesgruppe. Hovedøvelsesgruppe = gruppen med flest resultater ved 13–14 (likt antall: alfabetisk først, deterministisk). Kjønn × gruppe-celler med færre enn 20 utøvere i primærutvalget ekskluderes (gjelder 3 utøvere: hekk/kappgang som hovedgruppe).
- **Gj.snitt-av-3-beste, ikke maksimum**, for å dempe maks-av-n-skjevheten (flere starter → bedre beste resultat mekanisk; testnotatets test 4-poeng anvendt på oss selv). Antall resultater per vindu (k13, k15) inngår som kontroll i alle modeller. Færre enn 3 resultater: snitt av det som finnes, flagget; sensitivitet ekskluderer k<2.
- Tyrving-skåring gjenbruker den validerte implementasjonen fra IJSSC-arbeidet (tyrving_r2; 1 596/1 596 mot fasit). Tyrving er alders- og øvelsesnormert, så Δ måler fremgang *utover* forventet aldersutvikling. Normene er ulikt krevende mellom øvelsesgrupper; standardisering innen gruppe × kjønn håndterer nivåforskjellen, og differansen tas innen samme gruppe.
- **Øvelsesbyttere:** primæranalysen måler fremgang i 13–14-hovedgruppen. Sensitivitet: fremgang i beste gruppe ved 15–16. (Selve byttemønsteret er A2s tema og analyseres ikke her.)

**Nivå:** Tyrving (gj.snitt av 3 beste, hovedgruppe) ved 13–14, standardisert.
**Volum:** konkurransedager ved 13–14 og ved 15–16 (nivå og endring, som i frafallsartikkelen).
**Relativ alder:** fødselskvartal (krever fødselsdato; dekning 93–100 % i disse kullene — manglende kvartal ekskluderes fra H2, rapporteres).
**Øvrige kontroller:** kjønn, fødselsår (kohort), region (krets ved baseline), klubbstørrelse; klubb som random intercept i egen spesifikasjon.

## 5. Modeller

1. **M0:** kjønn + kohort (+ region + klubbstørrelse).
2. **M1:** M0 + nivå 13–14 + volum 13–14 + volum 15–16 + k13 + k15.
3. **M2 (H1):** M1 + Δ. Rapport: OR per SD med 95 % KI; ΔAUC M2 mot M1 med 5-fold kryssvalidering × 20 repetisjoner (og klubbgrupperte folder som sensitivitet); kalibrering (slope, Brier).
4. **H2:** M2 + Δ × kvartalstrend; stratifiserte OR Q1–Q2 / Q3–Q4. Interaksjonen er retningsbestemt og ventes upresist estimert; KI rapporteres uansett utfall.
5. **H3:** AUC(kjønn+volum+Δ) mot AUC(kjønn+volum+nivå), med KI for differansen (parret bootstrap).
6. **Sekundært:** Cox fra landmark (klokke fra fylte 17) med samme kovariater; exit-justerte baner — median standardisert Tyrving ved T−3…T−0 relativt til utøverens eget tidligere nivå (prestasjonsanalogen til volumfiguren i frafallsartikkelen: *stagnerer de før de slutter, utover at de starter sjeldnere?*); E-verdier for H1.
7. **Replikasjon:** alle hovedestimater separat i kohort A og B.

**Styrke (grovt):** 4 503 observasjoner og 820 hendelser gir god presisjon for H1 (detekterbar OR per SD i størrelsesorden 1,15 ved konvensjonell styrke) og romslig hendelser-per-variabel. H2 er svakere stilt og behandles som retningstest med replikasjon, ikke som alt-eller-intet.

## 6. Robusthet og sensitivitet (forhåndsdefinert)

- **Covid:** født 2004–2005 har 15–16-vinduet i 2019–2021. Hovedanalyse med kohortdummyer; sensitivitet ekskluderer født 2004–2005; interaksjon Δ × covid-vindu rapporteres.
- **Eksponeringsvarianter:** sesongbeste (maks), snitt av alle resultater, og — for de fire JSAMS-øvelsene — residual mot panelkurvene (within-utøver forventning).
- **Vind:** Tyrving fra kun vindgyldige merker i vindøvelser.
- **Utfallsvarianter:** som i §4.
- **k-krav:** k≥2 i begge vinduer.
- **Byttere:** fremgang i beste 15–16-gruppe.
- **Negativkontrollaktig rimelighetssjekk:** Δ målt 13→14 (innen baselinevinduet) mot samme utfall, for å se om «fremgang» bare er re-parametrisert volum/nivå allerede før landmark.

## 7. Forhåndsregistrering og arbeidsflyt

1. **Tillatt før registrering:** dekningstall, flytdiagram, missingness, fordelinger av Δ/k/kvartal — ingen eksponering–utfall-krysninger.
2. OSF-registrering (engelsk oversettelse av dette dokumentet, med hypoteser, estimander, modeller og tolkningsregler). *Besluttet 29.10.2026 (Atle): ingen ekstern registrering — tidsskriftene krever det ikke. Planen står som tidsstemplet plan committet før estimering (367f03f); beslutningen er dokumentert i `FRIGITT_FOR_MODELLERING.txt`, og manuset oppgir dette.*
3. Uttrekk → frossent datasett → variabler → modeller. Kode i `forskning/stagnasjon-exit/`: `00_uttrekk.py`, `01_variabler.py`, `02_deskriptiv.py`, `03_modeller.py`, `04_robusthet.py`, `RUN_ALL.sh`, med logg og frossen CSV i `data_private/` (git-ignorert; aggregerte tabeller i repo).
4. Manus: mål **Sports Medicine – Open** (naturlig oppfølger til RAE-artikkelen; samme leserkrets, åpen tilgang); alternativer JSAMS og Psychology of Sport and Exercise (hvis mekanismerammen løftes).

**Anslått omfang:** uttrekk + variabler ca. 1 uke; registrering 2–3 dager; modeller + robusthet 1–2 uker; manus 2 uker.

## 8. Etikk og personvern

Offentlige konkurranseresultater; ingen nivåanalyse under 13 år (baseline starter ved 13–14, i tråd med barneidrettsbestemmelsene); ingen enkeltutøvere identifiseres, og frafall omtales aldri på individnivå; samme hjemmelsvurdering som IJSSC-arbeidet (utenfor helseforskningslovens virkeområde; Sikt-vurdering foreligger). Flaggings-/tiltaksspørsmål (jf. frafallsartikkelens §4.8) berøres ikke av denne studien.

## 9. Hva studien ikke gjør

Ingen kausal effekt av fremgang estimeres; idrettsbytte kan ikke skilles fra disengasjement; trenings-, skade- og modningsdata finnes ikke. Studien rangerer forklaringer og leverer den direkte testen RAE-artikkelen etterlyser — den avgjør ikke mekanismen alene.
