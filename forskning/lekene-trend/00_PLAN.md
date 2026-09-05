# Utviklingen i resultatene ved 13–14-årslekene 2012–2025 — forprosjekt

**Formål:** Norsk artikkel til trenerforeningens tidsskrift: er det en trend i resultatene i 13- og 14-årsklassene ved lekene (NCC/PEAB/Bendit/Ungdoms-/Lerøy-lekene), og hvordan kan utvikling måles forsvarlig med data KUN fra dette stevnet?
**Status:** 2026-09-05. Uttrekk (`01_uttrekk.py`), deskriptive figurer (`02_deskriptiv.py`, fig 1–8) og trendestimater per øvelse × klasse (`03_trender.py`, fig 9, kvantilregresjon) er kjørt, med nasjonal kontroll av kast/hopp mot hele databasen (`tables/nasjonal_kontroll.csv`). **Den samlede tekstlige vurderingen står i `03_vurdering.md`**; vedleggstabell fra `04_vedleggstabell.py`. Se §7 for datakvalitetsfunn og §8 for foreløpig lesning. Extralekene er utelatt (annet stevne), kappgang er tatt ut, og *antall øvelser per utøver* (fig 7) brukes ikke som indikator fordi det styres av kretsenes deltakerregler (varierer med kretsstørrelse og er endret i perioden).

---

## 1. Hva databasen faktisk har

**Serien er komplett, 14 utgaver 2012–2025**, under skiftende sponsornavn:

| År | Navn i basen | Arenaer |
|---|---|---|
| 2012 | NCC-lekene | Lillestrøm, Osterøy, Stjørdal |
| 2013–2014 | PEAB-lekene | Jessheim, Osterøy, Stjørdal |
| 2015 | Bendit-lekene | Jessheim, Osterøy, Stjørdal |
| 2016 | Ungdomslekene (uten sponsor) | Jessheim, Osterøy, Stjørdal |
| 2017–2025 | Lerøy-lekene / Lerøylekene / Lerøy-leikane | Øst: Jessheim → Hamar → Rjukan; Vest: Osterøy → Haugesund → Byrkjelo → Ålgård; Midt/Nord: Stjørdal → Måndalen → Trondheim → Kristiansund |

**NB «Extra-lekene»:** finnes i basen kun som *Extralekene* på Ålgård (juni, KM Rogaland, 2022–2025) — et annet stevne. Serien 2012–2025 er komplett uten den. Avklar om minnet om «Extra» gjelder noe annet.

**Deltakelse per år (13–14-åringer, deduplisert):** 2012–2019: 594–664 utøvere; 2020 (covid, tre arenaer, Haugesund utsatt til 8. sept.): 459; 2021–2025: 523–574. Fordelingen 13/14 er ~50/50 hvert år; jenter er i flertall alle år unntatt 2021. Alderfilteret (år − fødselsår ∈ {13, 14}) treffer nesten alle (0–7 «feilaldrede» per år).

**Datakvalitet som avgjør metodevalget:**
- **Fødselsdato finnes for 94–100 %** → eksakt alder i dager på stevnedagen kan beregnes. Dette er nøkkelen til modningsproblemet (se §2).
- **Vind** er registrert på ~50 % av resultatene (dvs. der det er relevant); `is_wind_legal` finnes.
- **Øvelseskodene bærer spesifikasjonen** (`kule_3kg`, `spyd_400g`, `60mh_76_2cm`, `slegge_30kg_1195cm` …). 25 øvelser har full dekning alle 14 år med uendret spesifikasjon. En regelendring ville vist seg som et kodeskifte, og det ser vi ikke — unntak: `1000mg` og `kappgang_1000_m` er trolig samme øvelse under to koder (må slås sammen), og slegge 3,0 kg starter først 2013.
- **Dubletter i stevnetabellen:** flere utgaver ligger både som aggregat («Lerøylekene», 2 313 resultater) og per arena/dag. Analysen må dedupliseres på utøver × øvelse × år (det er samme resultat registrert to ganger).
- **Gjentakere:** 62–75 % av 14-åringene deltok også som 13-åringer året før (160–210 per år, ~2 470 overganger totalt). Det gir et kvasi-longitudinelt design innenfor stevnet.

Kjerneøvelser med full dekning og størst felt: 60m, 200m, 600m, 1500m, lengde (m/ og u/ sone), høyde, tresteg, kule (2/3/4 kg etter klasse), spyd (400/600 g), diskos (600/750 g/1 kg), slegge, 60mh 76,2, 200mh 68/76,2, 80mh 84, stav, kappgang 1000 m.

## 2. Hvorfor rått klassesnitt er en dårlig indikator (og hva som forstyrrer)

1. **Biologisk modning.** Ved kronologisk 13–14 år spenner biologisk alder over ±2 år; spredningen i resultater domineres av modning, ikke trening. Et klassesnitt sier lite om «friidrettsnivået».
2. **Relativ alder.** Andelen tidlig- vs. sentfødte i klassen varierer år for år og påvirker snittet (Cobley et al., 2009).
3. **Sammensetning — hvem som kommer.** Kretskvoter, kretsenes uttak, covid, sportens popularitet i ulike landsdeler. En trend i «nivå» kan være en trend i *hvem som deltar*.
4. **Feltstørrelse.** Forventet beste resultat av n deltakere stiger med n. Vinner- og topp-3-mål er derfor feltstørrelsesavhengige.
5. **Arena og vær.** Arenaene har flyttet (Rjukan, Byrkjelo, Kristiansund …); vind og bane varierer. Vind kan kontrolleres for i sprint/hopp; arena kan inn som fast effekt.
6. **Spesifikasjoner og tidtaking.** Løst gjennom øvelseskodene (uendret) — men `is_manual_time` bør sjekkes for 600/1500 m.

## 3. Verktøykassen — hva som kan måles med bare dette stevnet

**A. Kvantilprofiler per øvelse × klasse × kjønn × år.** Median, 75. og 90. persentil pluss topp-8-snitt, per år. Trend estimeres med kvantilregresjon (Koenker & Bassett, 1978) med år som kontinuerlig variabel: gir separate svar for *bredden* (median) og *toppen* (90. persentil) — samme «topp vs. bredde»-logikk som trenerartikkel-prosjektet. Rapporter endring per tiår med bootstrap-KI.

**B. Feltstørrelseskorrigerte toppmål.** Bruk percentil-av-feltet i stedet for rangplass, eller standardiser topp-k til fast feltstørrelse ved nedsampling (bootstrap til minste årgangsfelt i øvelsen). Alternativt ordensstatistikk-korreksjon for forventet beste-av-n.

**C. Sammensetningsjustert nivå («nivå ved gitt alder»).** Modell per øvelse: resultat ~ kalenderår + eksakt alder (dager) + fødselskvartal + kjønn + arena (+ vind der relevant). Eksakt alder gjør at trenden måles *ved samme alder*, ikke i samme klasse — det er dette som svarer på innvendingen om at klassene er dårlige indikatorer. Kan estimeres for median og øvre kvantil.

**D. Kvasi-longitudinelt: 13→14-forbedringen hos gjentakere.** Samme utøver, samme øvelse, ett år senere. Gjennomsnittlig (og kvantilvis) forbedring per overgangsår 2012→13 … 2024→25. Robust mot seleksjon *inn* i stevnet fordi utøveren sammenlignes med seg selv; sier om *utviklingstakten* endres (treningskultur, spesialisering, treningsmengde) — et annet spørsmål enn nivået, og trolig det mest trenerrelevante. Justering for eksakt alder ved begge tidspunkt.

**E. Tyrving-normalisering til samleindeks.** Alle resultater → Tyrving-poeng (samme tabellversjon for alle år). Gir én nivåindeks per klasse × kjønn × år (median og 90. persentil), én hovedfigur, og muliggjør «beste øvelse per utøver» som mål på hvor gode deltakerne er i sin hovedøvelse. Forbehold: tabellen er selv alderskalibrert per klasse, så indeksen sammenligner *mot tabellen*, ikke mot biologisk alder — kombineres med C.

**F. Deltakerprofil, ikke bare nivå.** Antall øvelser per utøver, øvelseskombinasjoner (kobling til HHI-funnet i IJSSC-artikkelen), andel som stiller i tekniske øvelser vs. løp, andel jenter/gutter. Utvikling i *hva* 13–14-åringene gjør er ofte mer interessant for trenere enn tideler.

**G. Covid som naturlig eksperiment.** 13-åringene i 2020 mistet en normal sesong; 13→14-forbedringen 2020→2021 og nivået i 2021–2022 mot resten. Én tydelig figur.

## 4. Anbefalt design for artikkelen

- **Enhet:** øvelse × klasse × kjønn × år, deduplisert; eksakt alder og fødselskvartal per utøver; arena som faktor; vind der relevant.
- **Hovedfigur:** 8–10 kjerneøvelser i paneler (J13, J14, G13, G14): median og 90. persentil per år 2012–2025 med trendlinje og covid-markering.
- **Samlefigur:** Tyrving-indeks (median/90. persentil) per klasse × kjønn × år.
- **Robusthet (tre lag):** (i) eksakt-alder-justert trend (C), (ii) gjentaker-forbedring (D), (iii) feltkorrigert topp-8 (B). Konklusjonen står hvis alle tre peker samme vei.
- **Statistikk:** kvantilregresjon per øvelse; mange øvelser → rapporter *mønsteret* (andel øvelser med positiv/negativ trend, størrelse i prosent og i Tyrving-poeng) framfor p-verdijakt; bootstrap-KI.
- **Budskap å teste:** «Nivået ved gitt alder er stabilt/stigende/synkende», «toppen og bredden går hver sin vei/samme vei», «utviklingstakten 13→14 har endret seg», «deltakerprofilen har endret seg».

## 5. Fallgruver å håndtere i uttrekket

- Dedup (aggregat + arena + dag); behold ett resultat per utøver × øvelse × år (finaler vs. forsøk: bruk beste).
- Slå sammen `1000mg`/`kappgang_1000_m`; kontroller andre kodevarianter (lengde med/uten sone — behold begge som egne serier).
- Vind: begrens til `is_wind_legal` eller ta vind som kovariat (60 m, 200 m, hekk, lengde, tresteg).
- Manuell tid (`is_manual_time IS NOT TRUE`) i mellomdistanse.
- Arenaflyttinger i Midt/Nord og Vest; Rjukan (høyde over havet) for løp.
- 2020: færre deltakere, sen dato i vest.
- Kretskvoter/uttaksregler over tid (2025-reglementet finnes; eldre må hentes) — dokumenter, bruk som kontekst.
- Tyrving-tabellversjon: én versjon for alle år; noter at 2024-tabellen brukes.

## 6. Neste steg (arbeidsplan)

1. Uttrekk med `serie.sql` (denne mappen) → deduplisert datasett `lekene_2012_2025.csv` med eksakt alder, kjønn, klasse, øvelse, resultat, vind, arena.
2. Deskriptiv tabell: n per øvelse × klasse × kjønn × år; første kvantilfigur (A).
3. Gjentaker-datasett og 13→14-forbedring (D).
4. Tyrving-scoring (gjenbruk `data/tyrvingtabellen.py` fra ncc-kohort) → samleindeks (E).
5. Modell C for kjerneøvelsene; feltkorreksjon (B).
6. Utkast til artikkel (norsk, konservativt bokmål), 6–8 figurer, 2 tabeller.

Anslag: uttrekk + deskriptiv 1 dag; analyser 2–3 dager; artikkelutkast 1–2 dager.

## 7. Datakvalitet funnet i uttrekket (2026-09-05)

- **Tidsformat i kilden:** 920 av 2 031 kappgang-rader og 18 rader på 600 m er lagret som «M.SS» («5.41» = 5:41, «1.45» = 1:45) med `performance_value` = 541/145 — feil i basen (rammer også nettstedets kappganglister). Løst på analysesiden i `felles.parse_verdi()`: tid under 60 s på 600 m/1500 m/kappgang tolkes som minutter.sekunder. Roten bør fikses i `fix_performance_format()` i `update_results.py` (egen oppgave, ikke gjort her).
- **`1000mg` og `kappgang_1000_m` er samme øvelse** registrert dobbelt (aggregat + arena). Kodene slås sammen *før* dedup; kappgang-feltet halveres da til det reelle (ca. 75 per år).
- **Manuell tid:** 85 sprint-/hekketider i tideler var ikke flagget som manuelle; flagges etter presisjonsregelen og utelates.
- Endelig datasett: 30 163 resultater, 5 706 utøvere, 14 utgaver. Deltakelse per år: 594–664 (2012–2019), 452 (2020), 523–573 (2021–2025).

## 8. Foreløpig lesning av de deskriptive figurene (før modellering)

Enkle lineære trender 2012–2025 over de sju fellesøvelsene med store felt (60 m, 200 m, 600 m, 1500 m, lengde, høyde, tresteg):
- **Bredden (median):** svakt fallende, −1 til −2 % per tiår i snitt per klasse; tydeligst i hopp (lengde J13/J14 −3–4 %, tresteg G14 −6 %, høyde G13 −5 %, alle p < 0,05). Løp er flate (unntak: J14 60 m og 200 m ca. −2 %, p < 0,05).
- **Toppen (90. persentil):** flat til svakt stigende (G14 60 m +1,5 %, G14 lengde +3,9 %, G14 1500 m +2 %); unntak tresteg G14 −4,7 %. → Foreløpig hypotese: *topp og bredde går hver sin vei* — samme mønster som i trenerartikkelen.
- **Utviklingstakt 13→14 (gjentakere):** stabil. Gutter forbedrer seg ca. 5,5–6 % (median) i alle perioder; jenter 2–2,75 %, svakt fallende fra 2013–16 til 2020–25. Ingen øvelse har signifikant trend.
- **Deltakerprofil:** øvelser per utøver har økt fra ca. 3,3 (2012) til ca. 4,0 (2025) i alle klasser; jenter alltid i flertall; covid-fallet i 2020 er hentet inn til rundt 2015–2019-nivå minus ca. 10 %.
- **Stav (fig 8, egne regler pga. felt på 8–23):** median og beste fjerdedel er flate i alle fire klasser (−2 til +4 % per tiår, alle p > 0,4). Beste hopp per år svinger med enkeltutøvere: guttenes toppresultater var høyest 2014–2018, jentenes topp ligger stabilt rundt 2,8–3,1 m i J14. Gjentakerforbedringen 13→14 er stor (gutter ca. 18 %, jenter ca. 10 % i median) og *stigende* for jenter, fra 6,5 % i 2013-vinduet til 12,9 % i 2025-vinduet (p < 0,01; 3-årsvinduer). Kappgang er tatt ut av figurene etter avtale (2026-09-05).
- **Sammensetning:** eksakt alder i klassen er stabil (avvik fra klassealder 0,23–0,27 år mot 0,18 forventet ved jevn fødselsfordeling); andel født 1. kvartal ligger på 28–35 % (relativ alderseffekt, konstant). Sammensetning forklarer altså ikke nivåtrenden — men modell C må bekrefte.

## 9. Litteratur å vurdere (verifiser før bruk — ingen referanse inn uten sjekk)

- Kearney & Hayes (2018) — rankingbaserte prestasjonsbaner i friidrett ungdom→senior (verifisert i IJSSC-arbeidet).
- Cobley et al. (2009) — relativ alder, metaanalyse (verifisert).
- Malina et al. (2015, *Br J Sports Med*) — biologisk modning hos unge utøvere (**må verifiseres**).
- Koenker & Bassett (1978, *Econometrica*) — kvantilregresjon (kanonisk).
- Norges Friidrettsforbund — Tyrvingtabellen (verifisert).
