# A6 til Journal of Sports Sciences — opplasting

Mappen bygges av `13_jss_pakke.py` til slutt i `RUN_ALL.sh`, etter at alle kontrollene er grønne. Den viser derfor alltid en kontrollert tilstand. Ikke rediger filene her. Rediger kildene i `manus/` og kjør `bash RUN_ALL.sh` på nytt. Kravene er hentet fra JSS' forfatterveiledning (oppdatert 26.10.2026).

## Før du sender

1. **Simen** må bekrefte bidragssetningen på tittelsiden og godkjenne den endelige versjonen. Følgebrevet sier at begge forfatterne har godkjent innsendingen.
2. **Lengden:** Løpende tekst er på om lag 6 000 ord (ordtellingen står på forsiden av manus). JSS anbefaler om lag 4 000 ord, men skriver at det er en veiledning og ikke en grense. Følgebrevet begrunner lengden og tilbyr å korte. Det andre valget er å korte før innsending.
3. **Les gjennom** manus og supplement.
4. **Følgebrevet** er et utkast. Rediger `manus/cover_letter.tex`. Kontrollen krever at ordtellingen og antall tabeller og figurer stemmer med manus.

## Filene og hvor de skal i portalen

Portalen er Routledge Submission Portal: <https://rp.tandfonline.com/submission/create?journalCode=RJSP>. JSS bruker formatfri innsending, så PDF godtas ved første innsending. Først ved revisjon trengs en redigerbar versjon (Word eller LaTeX).

| Fil | Portalfelt | Merknad |
|---|---|---|
| `01_Manuscript_anonymised.pdf` | Anonymt manus (hoveddokument) | Uten forfatteropplysninger, med løpende linjenummer (JSS krever det). Figurer og tabeller står i teksten. |
| `02_Title_page.pdf` | Tittelside | Forfattere, tilknytning, ORCID, korresponderende forfatter og erklæringene: Disclosure of interest, Funding, Author contributions, KI-bruk og Acknowledgements. |
| `03_Supplementary_material.pdf` | Supplemental material | Tabell S1–S8, nummerert etter første sitering i manus. Publiseres på nett (Figshare). |
| `04_Cover_letter.pdf` | Cover letter | Utkast; se punkt 4 over. |
| `Figure1.tif` | Figure | Effekt per m/s etter alder, sekunder |
| `Figure2.tif` | Figure | Samme i prosent |
| `Figure3.tif` | Figure | Evnetertiler |
| `Figure4.tif` | Figure | Motvind mot medvind, med drag-prediksjon |
| `Figure5.tif` | Figure | Korthekk |

Figurfilene er valgfrie ved innsending, fordi figurene står i manus. De følger trykkrekkefølgen og holder 300 dpi i farger ved full sidebredde, som JSS krever.

## Svar i portalen

- **Article type:** Original Article.
- **Tittel, sammendrag og nøkkelord:** kopier fra manus. Sammendraget er ustrukturert og under 200 ord, og det er 6 nøkkelord (JSS: 3–6). Kontrollen sjekker begge.
- **Forfattere:**
  - Atle G. Guttormsen (korresponderende forfatter), ORCID 0000-0003-0188-8462, atle.guttormsen@nmbu.no.
  - Simen Guttormsen, ORCID 0009-0002-2533-8561, simen.guttormsen@nmbu.no.
  - Begge: School of Economics and Business, Norwegian University of Life Sciences (NMBU), Ås, Norway.
- **CRediT-roller** (forslag; må bekreftes av dere og stemme med bidragssetningen på tittelsiden):
  - AGG: Conceptualization, Methodology, Software, Formal analysis, Data curation, Visualization, Writing – original draft, Writing – review & editing.
  - SG: Data curation (TFRRS-profilene), Resources, Writing – review & editing.
- **Funding:** ingen.
- **Disclosure of interest:** som på tittelsiden.
- **Generative AI:** som erklæringen på tittelsiden.
- **«Is there a data set associated with the paper?»** Nei. Analysedatasettet kan ikke deles (GDPR), og koden deponeres ved aksept; se Data availability i manus.
- **Farger i trykt utgave:** nei. Farger på nett er gratis. Farger på trykk koster £300 per figur, og figur 5 og videre £50 per figur.
- **Preprint:** ingen. Ikke legg ut preprint før vurderingen er ferdig, fordi JSS skriver at anonymiteten da ikke kan garanteres.
- **Open access (Open Select):** valgfritt, mot publiseringsavgift. Sjekk om NMBUs avtale med Taylor & Francis dekker den. Uten open access er publisering gratis.
- **Forslag til fagfeller:** valgfritt.

## Hva `RUN_ALL.sh` har kontrollert før mappen ble bygget

- Frysekontroll av data og kode, deretter hele analysekjeden, R-speilet og tallkontrollen. Hvert tall i manus og supplement er ankret mot estimeringsfilene.
- Ingen udefinerte referanser og ingen «??» i manus eller supplement.
- Ingen forfatteropplysninger i manus, supplement eller PDF-metadataene.
- S-tabellene er nummerert etter første sitering, og figurfilene følger trykkrekkefølgen.
- `MANIFEST.sha256` har hashen til hver opplastingsfil. Sjekk med `shasum -a 256 -c MANIFEST.sha256` i denne mappen.
