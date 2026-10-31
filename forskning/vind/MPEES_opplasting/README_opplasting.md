# A6 til Measurement in Physical Education and Exercise Science — opplasting

`13_opplasting.py` bygger denne mappen til slutt i `RUN_ALL.sh`, etter at alle kontrollene er grønne. Mappen viser derfor alltid en kontrollert tilstand. Ikke rediger filene her. Rediger kildene i `manus/` og kjør `bash RUN_ALL.sh` på nytt.

Kravene er hentet fra MPEES' forfatterveiledning og tidsskriftets side om omfang og seksjoner, begge lest 31.10.2026. JSS-pakken fra samme dag ligger i commit 3b8911e.

## Før du sender

1. **KI-erklæringen** er Atles egen tekst (31.10.2026): «Anthropic Claude (Opus 5.5) was used … to improve language and readability, assist with structuring the text, check analysis code and identify errors …». Atle har sjekket bruksvilkårene, og erklæringen bekrefter det, slik Taylor & Francis krever.
2. **Simen** må godkjenne den endelige versjonen. Følgebrevet sier at begge forfatterne har godkjent innsendingen. Bidragssetningen er tatt ut av manus. Rollene føres i stedet inn i portalen (se under).
3. **Les gjennom** manus og supplement. Disse delene er nye:
   - sammendraget (150 ord);
   - én setning om måling i innledningen;
   - korte henvisninger der stoff er flyttet til supplementet;
   - avsnittene «Supplementary Methods» i supplementet, med tekst som er flyttet dit ordrett.
4. **Følgebrevet** er et utkast. Rediger `manus/cover_letter.tex`. Kontrollen krever at sidetall, ordtelling og antall tabeller og figurer stemmer med manus.
5. **Seksjon:** Manus og følgebrevet foreslår *Exercise Science*. Alternativet er *Research Methodology and Statistics*. Endrer du seksjon, må både tittelsiden og følgebrevet endres. Kontrollen sjekker at de er like.
6. **Etikk:** MPEES ber om en setning om at en etisk komité (IRB) har godkjent studien, eller lignende. A6 trengte ikke godkjenning etter norsk lov. Methods sier dette, slik T&F' etikkregler åpner for, og følgebrevet forklarer det.

## Filene og hvor de skal i portalen

Portalen er Routledge Submission Portal: <https://rp.tandfonline.com/submission/create?journalCode=HMPE>. Forfatterveiledningen sier enkeltanonym vurdering, men portalen krever både «Manuscript – with author details» og «Manuscript – anonymous» (skjermbilde fra Atle 31.10.2026). Begge versjonene bygges fra `manus/main.tex`. Veiledningen sier at manus kan sendes i Word. Godtar ikke portalen PDF, kan LaTeX-kilden (`manus/main.tex` med tabellfilene og figurene) lastes opp i stedet.

| Fil | Portalfelt | Merknad |
|---|---|---|
| `01_Manuscript_with_author_details.pdf` | Manuscript – with author details | 30 sider i MPEES-formatet. Side 1 er tittelsiden (forfattere, ORCID, korresponderende forfatter, løpetittel, ordtelling, seksjon), og side 2 har sammendrag og nøkkelord. Deretter kommer teksten med linjenummer, erklæringene og referansene. Til slutt kommer tabellene (én per side), figurene og listen over figurtekster. |
| `02_Manuscript_anonymous.pdf` | Manuscript – anonymous | Samme manus. Side 1 har tittel, seksjon, løpetittel og ordtelling, men ingen forfatteropplysninger. Disclosure-setningen om AGGs statistikkplattform er tatt ut. Selvsiteringen står i tredje person. |
| `03_Supplementary_material.pdf` | Supplemental material | Supplementary Methods, tabell S1–S10 og figur S1–S2, nummerert etter første sitering i manus. Uten forfatteropplysninger. Publiseres på nett (Figshare). |
| `04_Cover_letter.pdf` | Cover letter | Utkast; se punkt 4 over. |
| `Figure1.tif` | Figure | Effekt per m/s etter alder, sekunder |
| `Figure2.tif` | Figure | Samme i prosent, sprint og hopp |
| `Figure3.tif` | Figure | Motvind mot medvind, med drag-prediksjon |

MPEES vil ha figurene som egne filer. Filene følger trykkrekkefølgen og har 300 dpi i farger. Markører og linjetyper skiller seriene, så figurene kan leses i gråtoner på trykk.

## Svar i portalen

- **Article type:** Original Article.
- **Tittel, sammendrag og nøkkelord:** kopier fra manus. Sammendraget er ustrukturert og har 150 ord, og det er 5 nøkkelord (MPEES: 4–5). Kontrollen sjekker begge.
- **Forfattere**, i rekkefølgen etter arbeidsinnsats, som MPEES krever:
  - Atle G. Guttormsen (korresponderende forfatter), ORCID 0000-0003-0188-8462, atle.guttormsen@nmbu.no.
  - Simen Guttormsen, ORCID 0009-0002-2533-8561, simen.guttormsen@nmbu.no.
  - Begge: School of Economics and Business, Norwegian University of Life Sciences (NMBU), Ås, Norway.
- **CRediT-roller.** Dette er et forslag. Det følger bidragssetningen fra JSS-tittelsiden, og dere må bekrefte det:
  - AGG: Conceptualization, Methodology, Software, Formal analysis, Data curation, Visualization, Writing – original draft, Writing – review & editing.
  - SG: Data curation (TFRRS-profilene), Resources, Writing – review & editing.
- **Funding:** ingen.
- **Disclosure statement:** som i manus.
- **Generative AI:** som erklæringen i manus.
- **«Is there a data set associated with the paper?»** Nei. Analysedatasettet kan ikke deles (GDPR), og koden deponeres ved aksept. Se Data availability i manus.
- **Farger i trykt utgave:** nei. Farger på nett er gratis, mens farger på trykk koster £300 per figur.
- **Open access (Open Select):** valgfritt, mot publiseringsavgift. Sjekk om NMBUs avtale med Taylor & Francis dekker den. Uten open access er publisering gratis.

## Hva `RUN_ALL.sh` har kontrollert før mappen ble bygget

- **Analysene og tallene:** frysekontroll av data og kode, så hele analysekjeden, R-speilet og tallkontrollen. Hvert tall i manus og supplement er ankret mot estimeringsfilene.
- **Henvisninger:** ingen udefinerte referanser og ingen «??». S-tabellene og S-figurene er nummerert etter første sitering, og figurfilene følger trykkrekkefølgen.
- **MPEES-formatet:**
  - Manus har høyst 30 sider, og tittelsiden med forfatterne er side 1.
  - Den anonyme versjonen og supplementet har ingen forfatteropplysninger i teksten eller PDF-metadataene.
  - Elementene står i MPEES-rekkefølgen.
  - Det er ingen britiske stavemåter i manus, supplement eller følgebrev.
  - KI-erklæringen oppgir verktøy og versjon.
- **Filene:** `MANIFEST.sha256` har hashen til hver opplastingsfil. Sjekk med `shasum -a 256 -c MANIFEST.sha256` i denne mappen.
