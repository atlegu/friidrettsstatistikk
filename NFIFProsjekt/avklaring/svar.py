#!/usr/bin/env python3
"""Fyll ut NFIFs avklaringsskjema med svarene våre.

    python3 svar.py

Leser «Avklaringsspørsmål – Athlete Mindset.docx» i NFIFProsjekt/, bytter ut
plassholderne i rekkefølge og skriver «Svar – Avklaringsspørsmål – Athlete
Mindset.docx» i denne mappen. Formatet er det NFIF sendte; bare
plassholderne endres.

Markering i teksten:
  **fet**        fet skrift
  ==tall==       gul utheving (priser som skal kontrolleres før innsending)
  linje som starter med «- » blir et kulepunkt
"""

import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

HER = Path(__file__).resolve().parent
KILDE = HER.parent / 'Avklaringsspørsmål – Athlete Mindset.docx'
UT = HER / 'Svar – Avklaringsspørsmål – Athlete Mindset.docx'

SVAR = [
# 1.1 Involvering fra Norsk Friidrett i kvalitetssikring
"""I en typisk uke i stevnesesongen trenger vi lite tid fra Norsk Friidrett. Plattformen kontrollerer alle nye resultater hver natt, og vi behandler det meste selv. Det som krever forbundets myndighet, legger vi frem ferdig utredet.
Anslaget bygger på 2026-sesongen. Vi kjørte de automatiske kontrollene på alle 54 198 baneresultater fra 2026. De fant 301 avvik, fra 5 til 20 i uken i sesongen. Om lag 45 av dem var mulige rekorder eller bestenoteringer.
Oppgavene for Norsk Friidrett:
- **Godkjenning av rekorder og bestenoteringer.** 1–2 saker i uken i sesongen. Vi legger frem resultat, vind, tidtaking og stevnestatus. Om lag 15 minutter per sak.
- **Underkjenning av stevner og resultater.** Sjelden. NFIF melder fra, og vi registrerer underkjenningen med årsakskode.
- **Regeltolkning i tvilstilfeller.** For eksempel redskap, blandede heat og utenlandske utøvere. Vi foreslår at fagrådet i tilbudets kapittel 9.4 tar disse.
Samlet anslår vi 1–2 timer i uken i høysesongen, og under én time i uken ellers. Kompetansen som trengs, er den statistikkansvarlig og SRU har i dag: rekordregler og regelverk. Det trengs ingen teknisk kompetanse.
Første sesong blir behovet noe større, anslagsvis 2–3 timer i uken, fordi kontrollene skal justeres etter NFIFs praksis. Når terminlisten og lisensregisteret er koblet til, settes kvalitetsnivået maskinelt. Da går behovet ned mot ren rekordgodkjenning.
I tillegg kommer to engangsoppgaver ved oppstart: klubbenes kretstilhørighet, og tilgang til terminliste og lisensregister.""",

# 1.2 Gjenstående arbeid for løp utenfor bane
"""Siden presentasjonen har vi bygget en første versjon av løp utenfor bane. Den kan ses på friidrettsresultater.no/gatelop. Den omfatter:
- **Datamodell for løp** med arrangement, løp, distanse, løypegradering og resultater. Den er adskilt fra baneresultatene, men koblet til det samme utøverregisteret.
- **Automatisk import fra EQ Timing** av alle arrangementer under Norges Friidrettsforbund. Fra 1. september til 14. oktober 2026 gir det 155 arrangementer, 367 løp og 38 893 resultater.
- **Kvalitetsnivå A, B og C, satt maskinelt** ut fra EQ Timings løypegradering (sertifisert målt løype, A-, B- eller C-måling), distansen og typen løp. Terreng-, motbakke- og fjelløp regnes foreløpig som registrert aktivitet (nivå C). Løp der vinnertiden er umulig for oppgitt distanse, flagges og settes også til nivå C.
- **Årsbeste på 5 km, 10 km, halvmaraton og maraton**, én rad per løper, med filter på kvalitetsnivå.
- **Kobling til utøverregisteret** på navn, kjønn og fødselsår. 3 396 løpere er koblet automatisk.
Dette gjenstår:
- **Flere tidtakere**, først Ultimate Sport Service. Q1 2027.
- **Løyperegister.** Nivå A bør bygge på NFIFs egne løypemålinger, ikke bare tidtakerens merking. Q1 2027.
- **Terreng-, motbakke- og fjelløp.** Disse løpene får lister per løp og løype i stedet for per distanse, og motbakkeløpene får høydemeter. Q2 2027.
- **Rekordlister og rekordgodkjenning** for de offisielle distansene. Q2 2027.
- **Samlet utøverprofil** med bane og gate, og deltakerstatistikk til aktivitetsmodulen. Q2 2027.
- **Eldre gateløpsresultater**, særlig rekorder fra før 2013. Etter kartlegging.
Løpssider og årsbeste kan dermed være i drift fra sesongstart 2027, og hele løsningen innen utgangen av andre kvartal 2027. Veikartet leveres innen 31.12.2026, slik kravspesifikasjonen krever.""",

# 1.3 Status for administrasjonsverktøyet
"""Administrasjonsverktøyet er i drift, med innlogging og roller for administrator og superadministrator. Skjermbilder ligger ved.
Det dekker i dag:
- **Avvik:** arbeidslisten fra de nattlige kontrollene. Hvert avvik godkjennes som riktig, rettes eller underkjennes, med kommentar og registrering av hvem som gjorde det. Denne delen er ny siden presentasjonen.
- **Utøvere:** søk, redigering og sammenslåing av dubletter.
- **Resultater:** redigering og sletting av feilregistreringer.
- **Stevner og klubber:** redigering av navn, dato, sted og tilhørighet.
- **Import:** opplasting av resultatlister fra FriRes og Excel, med validering og godkjenningskø før publisering.
Dette gjenstår:
- Rekordgodkjenning med dokumentasjon og status. Desember 2026.
- Manuell overstyring av kvalitetsnivå, og underkjenning med årsakskode. Desember 2026.
- Brukere og roller for NFIF og kretsene, med logg over alle endringer. Q1 2027.
- Administrasjon av gateløp: løyperegister, løp og kobling av løpere. Q1–Q2 2027.""",

# 1.4 Egen database for masters
"""Vi anbefaler én felles database, med egne lister og egne rekorder for masters. Vi har vurdert spørsmålet på nytt etter presentasjonen, og bygget masterstatistikken på den måten for å prøve det ut.
Resultatet ligger på friidrettsresultater.no/statistikk/masters. Siden viser beste norske resultat per øvelse i hver femårsklasse fra 35 år, ute og inne. Den bygger på om lag 96 000 masters-resultater som allerede ligger i basen.
Fordelene med én database:
- **Det er de samme utøverne.** En 35-åring er både senior og masters i samme løp. Med to databaser må utøveren, resultatet og hver rettelse føres to steder, og basene vil gli fra hverandre.
- **Masters følger av dataene.** Klassen regnes ut fra fødselsår og konkurranseår, og redskap og hekkehøyde ligger allerede i øvelsen. Det trengs ingen ekstra registrering.
- **Samme import og samme kontroller** gjelder for alle.
Argumentene for egen database, og hvordan de møtes:
- **Mastersmiljøet vil forvalte sin egen statistikk.** Det løses med en egen administratorrolle for masters, ikke med en egen base.
- **Mastersklassene har eget regelverk.** WMA-reglene for redskap og hekkehøyder legges inn som regler for klassene.
Ulempen med én database er at mastersklassene må holdes adskilt i presentasjonen, så seniorlistene ikke blir uoversiktlige. Det er gjort i løsningen.""",

# 1.5 Integrasjoner og automatisert resultatinnsamling
"""I dag hentes alle baneresultater automatisk hver natt. De siste seks ukene kontrolleres i tillegg på nytt mot kilden, slik at rettelser kommer med. Status for de enkelte systemene:
- **iSonen (terminliste og lisensregister):** ikke utviklet. Avhenger av tilgang fra NFIF og Buypass. Integrasjonen trengs for å sette kvalitetsnivå maskinelt. Q1 2027, etter at tilgang er gitt.
- **FriRes og LiveRes:** resultatlister fra FriRes kan lastes opp som fil i administrasjonsverktøyet i dag. Direkte overføring fra LiveRes krever et avtalt format, og vi vil gjerne utforme det sammen med utvikleren.
- **OpenTrack:** ikke utviklet. OpenTrack har et åpent API, så integrasjonen avhenger ikke av tilrettelegging. Q1–Q2 2027.
- **EQ Timing:** fungerer som prototype, jf. svar 1.2. Importen bruker EQ Timings åpne resultattjeneste. For varig drift ønsker vi en avtale med EQ Timing om grensesnittet og varsling ved endringer.
- **Ultimate Sport Service:** ikke kartlagt. Avhenger av tilgang fra leverandøren.
Dersom API-tilgang ikke blir gitt, stopper ikke løsningen opp. Resultatlister kan lastes opp som fil (CSV, Excel eller FriRes) i administrasjonsverktøyet, og de går gjennom de samme kontrollene. Offentlige resultatsider kan hentes der tidtakeren tillater det. Det gir mer manuelt arbeid, men ikke tapte resultater. Uten terminliste og lisensregister settes kvalitetsnivået ut fra stevnenivå og tidtaking, og det overstyres manuelt der det trengs.""",

# 1.6 Kvalitetssikring og avvikshåndtering
"""Athlete Mindset har ansvaret for å behandle avvikene i ordinær drift. NFIF trekkes inn bare der saken krever forbundets myndighet.
Innenfor den årlige driftsprisen:
- Registreringsfeil: feil øvelse, redskap, enhet eller distanse, og tider i feil format.
- Dubletter av resultater, stevner og utøvere, og sammenslåing av utøvere.
- Manglende kjønn, fødselsår eller vind, kontrollert mot kilden.
- Avstemming mot kilden, og retting når kilden endres.
- Kobling av løpere i gateløp til utøverregisteret.
Krever avgjørelse fra NFIF. Vi utreder og dokumenterer sakene:
- Godkjenning av rekorder og bestenoteringer.
- Underkjenning av stevner eller resultater, med årsakskode.
- Regeltolkning i tvilstilfeller, for eksempel blandede heat og utenlandske utøvere.
Faktureres særskilt, etter timepris og bare etter forhåndsgodkjenning:
- Større oppryddingsprosjekter i historiske data.
- Nye kontrollregler som krever utvikling.""",

# 1.7 Leveranseplan og funksjonalitet ved oppstart
"""**Allerede utviklet, i produksjon 1. januar 2027:**
- Nasjonal statistikk: årslister, alle-tiders-lister og rekorder, ute og inne, med filter for kjønn, aldersklasse, vind og tidtaking.
- Utøverprofiler, stevnesider, og klubbsider med klubbstatistikk og klubbrekorder.
- NM-kvalifisering, oppdatert fortløpende.
- Aktivitet og deltakelse, med eksport til Excel.
- Masterstatistikk per femårsklasse.
- Nattlig import og avstemming mot kilden, med automatiske kontroller og avviksliste.
- Administrasjonsverktøy for utøvere, resultater, stevner, klubber, import og avvik.
**Gjenstår, leveres før 1. januar 2027:**
- Kvalitetsnivå A, B og C for baneresultater, med filter.
- Dokumentert API, og eksport til Excel og CSV fra alle lister.
- Kretsstatistikk.
- Rekordgodkjenning og underkjenning med årsakskode i administrasjonsverktøyet.
- Dokumentasjon, personvernvurdering og databehandleravtale.
- Egen innsamling av resultatlister direkte fra arrangører og tidtakere, i parallell drift med dagens kilde til NFIF bekrefter overgangen.
**Leveres i 2027:**
- Løp utenfor bane i full drift, jf. svar 1.2. Q1–Q2.
- Integrasjoner, jf. svar 1.5. Q1–Q3.
- Brukere og roller for kretsene, og logg over endringer. Q1.
- Eldre statistikk, etter NFIFs valg.
**Avhengig av eksterne:**
- Maskinelt kvalitetsnivå: tilgang til terminliste og lisensregister fra NFIF og Buypass.
- Kretsstatistikk: klubbenes kretstilhørighet fra NFIF.
- Integrasjoner mot iSonen, LiveRes og Ultimate Sport Service: tilgang fra leverandørene.
- EQ Timing i varig drift: avtale med EQ Timing.""",

# 2.1 Stabilitet og kontinuitet over tid
"""**Kapasitet og nøkkelpersoner.** Leveransen bemannes av tre navngitte personer: Atle Guttormsen (data og analyse), Simen Guttormsen (systemutvikling) og Sondre Guttormsen (idrettsfaglig ledelse og produkt). To av dem har full teknisk tilgang og kjenner hele løsningen. Den daglige driften er automatisert: import, avstemming og kontroller går hver natt uten manuell innsats, og avvik legges i arbeidslisten. Alle endringer i data og kode dokumenteres i en driftslogg og i versjonskontroll.
**Økonomisk soliditet.** Athlete Mindset AS inngår i Fire S Invest AS og har flere forretningsområder. Selskapet står derfor ikke og faller med én kontrakt. Løsningen bygger på standard skytjenester med lave driftskostnader. Vi legger gjerne frem regnskap og eierforhold.
**Tilgang til data, dokumentasjon og videre drift:**
- NFIF eier alle data og har full eksportrett når som helst, uten gebyr.
- Kildekode og databasestruktur deponeres hos tredjepart (escrow).
- Exit-klausul: ved opphør overleveres kildekode, komplette data og driftsdokumentasjon vederlagsfritt, uansett årsak og uansett hvem som sier opp.
- Vi tilbyr at kontoene for database og drift opprettes i NFIFs navn, med oss som driftsleverandør. Da har NFIF tilgang til alt til enhver tid, også uten oss.
- Løsningen bygger på standard teknologi (PostgreSQL, Next.js og Python) som enhver kompetent leverandør kan overta.
For et tidsperspektiv på 5–10 år foreslår vi i tillegg et årlig statusmøte med gjennomgang av drift, datakvalitet og kontinuitetsplan.""",

# 3.1 Oppstartspris
"""Vi har gått gjennom oppstartsprisen. For nasjonal banestatistikk reduserer vi den fra 710 000 kr til ==350 000 kr==, en reduksjon på ==51 prosent==.
Kostnaden var drevet av tre poster: verdien av plattformen og datagrunnlaget som overføres, masters og eldre statistikk. Slik er postene justert:
- Plattformen og datagrunnlaget som overføres: fra 250 000 kr til ==150 000 kr==.
- Masters: fra 100 000 kr til ==0 kr==. Masterstatistikken er bygget og i drift, jf. svar 1.4.
- Opphenting av eldre statistikk: tas ut av fastprisen og tilbys som valgfritt tillegg til ==100 000 kr==.
- Dokumentert API og eksport: fra 100 000 kr til ==80 000 kr==.
- Dokumentasjon, personvernvurdering og databehandleravtale: fra 80 000 kr til ==40 000 kr==.
- Kvalitetsnivå for resultater (==50 000 kr==) og kretsstatistikk (==30 000 kr==) er uendret.
Årlig drift av banestatistikken er uendret, ==300 000 kr== per år. Den omfatter også behandlingen av avvik, jf. svar 1.6.
Ønsker NFIF lavest mulig oppstartskostnad, kan overføringen av plattformen fordeles på driftsprisen, med ==30 000 kr== per år i fem år. Da blir oppstartsprisen ==200 000 kr==.
For gateløp gir vi nå fastpris på etableringen, ==300 000 kr==, mot 450 000–600 000 kr tidligere. Se svar 3.2.
Alle priser er eks. mva.""",

# 3.2 Etablering av gateløp: integrasjoner
"""Etableringsprisen for gateløp omfatter integrasjonen mot EQ Timing. Den er bygget og i drift som prototype, jf. svar 1.2. EQ Timing var den største usikkerheten bak det opprinnelige intervallet, og vi kan derfor gi fastpris: ==300 000 kr==.
Fastprisen omfatter datamodell, import fra EQ Timing, løyperegister, kvalitetsnivå, årsbeste og rekordlister, terreng- og motbakkeløp, løpssider og samlet utøverprofil med bane og gate.
Andre tidtakere kommer i tillegg, med ==60 000–100 000 kr== per system. Det relevante systemet er Ultimate Sport Service. Etter kartleggingen kan ett mindre tidtakersystem komme til. Samlet forventet tillegg er ==60 000–200 000 kr==.
Det er ikke lenger et intervall for selve etableringen. Årlig registrering og vedlikehold av gateløp er ==200 000 kr== per år, som før.""",

# 3.3 Samlet kostnad over fem år
"""Alle beløp er eks. mva. og før KPI-regulering fra år fire.
**Faste priser:**
- Nasjonal banestatistikk, etablering: ==350 000 kr==
- Nasjonal banestatistikk, drift i fem år à ==300 000 kr==: ==1 500 000 kr==
- Gateløp, etablering: ==300 000 kr==
- Gateløp, drift i fem år à ==200 000 kr==: ==1 000 000 kr==
- **Sum faste priser: ==3 150 000 kr==**
**Estimater for nødvendige integrasjoner:**
- iSonen, terminliste og lisensregister: ==90 000–150 000 kr==
- Direkte overføring fra LiveRes: ==60 000–100 000 kr==
- Ultimate Sport Service: ==60 000–100 000 kr==
- **Sum estimater: ==210 000–350 000 kr==**
**Tillegg etter behov:**
- OpenTrack: ==60 000–100 000 kr==
- Eldre statistikk: ==100 000 kr==
- Øvrig utvikling: ==950 kr== per time. Analyse og utredning: ==1 100 kr== per time.
**Forventet samlet kostnad over fem år**, med faste priser og nødvendige integrasjoner: ==3,36–3,50 mill. kr==.""",
]

VEDLEGG = [
    'Ingen',
    'Vedlegg 2: Skjermbilder av gateløp',
    'Vedlegg 1: Skjermbilder av administrasjonsverktøyet',
    'Vedlegg 3: Skjermbilde av masterstatistikken',
    'Ingen', 'Ingen', 'Ingen', 'Ingen', 'Ingen', 'Ingen', 'Ingen',
]

KOMMENTAR = """Siden presentasjonen har vi bygget tre av tingene dere spør om, slik at svarene kan kontrolleres i løsningen og ikke bare leses: avvikslisten i administrasjonsverktøyet, masterstatistikken og første versjon av løp utenfor bane. Se friidrettsresultater.no/statistikk/masters og friidrettsresultater.no/gatelop. Vi viser gjerne administrasjonsverktøyet i et kort møte."""


def runs(tekst: str) -> str:
    """Tekst med **fet** og ==utheving== til w:r-elementer."""
    ut = []
    for del_ in re.split(r'(\*\*.+?\*\*)', tekst):
        fet = del_.startswith('**') and del_.endswith('**')
        if fet:
            del_ = del_[2:-2]
        for bit in re.split(r'(==.+?==)', del_):
            if not bit:
                continue
            gul = bit.startswith('==') and bit.endswith('==')
            if gul:
                bit = bit[2:-2]
            rpr = ('<w:b/><w:bCs/>' if fet else '') + ('<w:highlight w:val="yellow"/>' if gul else '')
            ut.append(f'<w:r>{"<w:rPr>" + rpr + "</w:rPr>" if rpr else ""}'
                      f'<w:t xml:space="preserve">{escape(bit)}</w:t></w:r>')
    return ''.join(ut)


def avsnitt(tekst: str) -> str:
    ps = []
    for linje in [l for l in tekst.split('\n') if l.strip()]:
        if linje.startswith('- '):
            ppr = ('<w:pPr><w:spacing w:before="0" w:after="40"/>'
                   '<w:ind w:left="284" w:hanging="227"/></w:pPr>')
            ps.append(f'<w:p>{ppr}<w:r><w:t xml:space="preserve">–\t</w:t></w:r>{runs(linje[2:])}</w:p>')
        else:
            ppr = '<w:pPr><w:spacing w:before="60" w:after="80"/></w:pPr>'
            ps.append(f'<w:p>{ppr}{runs(linje)}</w:p>')
    return ''.join(ps)


def erstatt(xml: str, plassholder: str, nye: list[str]) -> str:
    for ny in nye:
        i = xml.find(plassholder)
        if i < 0:
            raise SystemExit(f'Fant ikke flere «{plassholder}»')
        s = xml.rfind('<w:p ', 0, i)
        e = xml.find('</w:p>', i) + len('</w:p>')
        xml = xml[:s] + ny + xml[e:]
    if plassholder in xml:
        raise SystemExit(f'Flere «{plassholder}» enn svar')
    return xml


def main():
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(KILDE) as z:
            z.extractall(tmp)
        dok = Path(tmp) / 'word' / 'document.xml'
        xml = dok.read_text(encoding='utf-8')
        xml = erstatt(xml, '[Leverandøren skriver sitt svar her]', [avsnitt(s) for s in SVAR])
        xml = erstatt(xml, '[Navn på vedlegg, eller «Ingen»]', [avsnitt(v) for v in VEDLEGG])
        xml = erstatt(xml, '[Eventuelle kommentarer eller presiseringer som ikke hører inn under spørsmålene over]',
                      [avsnitt(KOMMENTAR)])
        dok.write_text(xml, encoding='utf-8')
        if UT.exists():
            UT.unlink()
        subprocess.run(['zip', '-q', '-X', '-r', str(UT), '.'], cwd=tmp, check=True)
    print(UT.name)


if __name__ == '__main__':
    main()
