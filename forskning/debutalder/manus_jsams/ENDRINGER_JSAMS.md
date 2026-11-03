# JSAMS-versjonen av A3 «Does starting age predict who stays?»

Innsendingsversjon for *Journal of Science and Medicine in Sport* (Elsevier; Original Research), bygget 1. november 2026 fra det fryste manuset `../manus/main.tex`. Det fryste manuset er ikke endret. Tidsskriftvalget er begrunnet i `../TIDSSKRIFTVURDERING_2026-11-01.md`.

## Filer

| Fil | Innhold | Lastes opp som |
|---|---|---|
| `main_anonymised.docx` / `.pdf` | Anonymisert manus: strukturert sammendrag, nøkkelord, Introduction, Methods, Results, Discussion, Conclusion, Practical implications, Acknowledgments, Data availability, KI-erklæring, referanser; 2 tabeller og 4 figurer i teksten | Manuscript |
| `title_page.docx` / `.pdf` | Tittelside med forfatter, ORCID, adresse, artikkeltype og underdisiplin, ordtellinger, antall tabeller/figurer/referanser, preprint, interesser, finansiering, etikk, bidrag, beslektede manus | Title page |
| `supplement.docx` / `.pdf` | Tabell S1–S4 (som i SJMSS-supplementet) og S5 (robusthetstabellen, tidligere tabell 4) | Supplementary material |
| `cover_letter.docx` / `.md` | Følgebrev med kategori, underdisiplin, finansiering, etikk, ikke-under-vurdering-erklæring, KI-bruk, preprint og beslektede manus | Cover letter |
| `declaration_of_interests.docx`, `acknowledgement_funding_ethics.docx`, `credit_author_statement.docx` | De tre erklæringene Editorial Manager krever som egne filer (interesser; takk, finansiering og etisk samsvar; CRediT) | Declaration of Interest; Acknowledgement/Funding/Ethical Compliance; CRediT Author Statement |
| `strobe_checklist.docx` / `.md` | STROBE-sjekkliste med henvisninger til avsnitt i JSAMS-manuset | Supplementary material |
| `references.bib`, `jsams.bst`, `jsams.csl` | JSAMS-kopi av bibliografien (forkortede journaltitler, uten de to upubliserte manusene) og de to stilfilene | — |
| `figurer_opplasting/Figure_1–4.tiff` | Figurene som LZW-komprimert TIFF, 300 dpi, 2 421–2 541 piksler brede, 0,2–0,4 MB | Figure |

Bygges med `./kompiler.sh` (bygg + pdflatex/bibtex), kontrolleres med `tallkontroll_jsams.py` (kjør med scraper-venv) og konverteres til Word med `python3 lag_docx.py` (system-Python, som har python-docx).

## Hva som er endret, og hvorfor

- **Sammendraget** er strukturert (Objectives, Design, Methods, Results, Conclusions) og på 250 ord, JSAMS' grense. Alle tall er fra det fryste sammendraget; ordlyden er strammet.
- **Nøkkelord** er byttet, fordi JSAMS krever inntil seks ord, minst fire fra MeSH, og ingen ord fra tittelen: Athletes, Adolescent, Child, Registries, Cohort studies (alle MeSH, merket †) og attrition.
- **«Materials and methods» heter «Methods»** (JSAMS-krav).
- **Visningselementer 8 → 6.** Tabell 3 (andel som fortsatt konkurrerer k år etter debut) er tatt ut av hovedteksten, siden figur 3 viser de samme tallene og tabell S3 gir dem med konfidensintervaller; teksten viser til figur 3. Tabell 4 (robusthet) er flyttet til supplementet som tabell S5, og de tre henvisningene peker dit.
- **«Perspective»-delen er erstattet** av en kort Conclusion og fire punkter under Practical implications, i lekmannsspråk og uten forskningsanbefalinger, slik JSAMS vil ha det. Innholdet er det samme: tidlig inngang gir ingen straff, ingen alder er for sen, første sesong er filteret, og nåværende aktivitet slår historie.
- **Erklæringene** følger JSAMS' rekkefølge: Acknowledgments (takk, finansieringssetningen Elsevier ber om, interesser), Data availability, KI-erklæringen med JSAMS' obligatoriske tittel og formulering (Atles tekst med Claude Opus 5.5). Etikk står i Methods som før og på tittelsiden. Forfatterbidrag står bare på tittelsiden (dobbel anonymisering).
- **Referansene** følger JSAMS' eksempel (Vancouver): nummerert etter første sitering, forfattere som «Hanna CM, Fulcher ML, Elley CR et al», journaltitler forkortet etter Index Medicus, DOI som https://doi.org/…. PDF-en bruker `jsams.bst` (TeX Lives vancouver.bst med «et al» etter tre forfattere og DOI slått på), Word-filen `jsams.csl` (vancouver.csl med samme to endringer). Bibliografien er en JSAMS-kopi, `references.bib`, med forkortede titler. **De to manusene som ennå ikke er antatt** (frafallsartikkelen under vurdering i IJSSC og A1 innsendt til PSE) er tatt ut av listen og omtales i teksten som «unpublished data», slik JSAMS krever; det fjerner samtidig «companion»-ordet, som ville røpet forfatteren i et dobbelt anonymisert manus. RAE-artikkelen («in press», antatt i Sports Medicine – Open) står i listen. 11 referanser; ingen setning har mer enn to.
- **Tittelsiden** oppgir det JSAMS ber om: ordtelling uten sammendrag og referanser, sammendragets ordtelling, antall tabeller og figurer, preprintstatus, interesser. Underdisiplin er satt til «Physical activity and public health»; se sjekklisten.

## Lengde og grenser

| | Manuset | JSAMS-grense |
|---|---|---|
| Hovedtekst (Introduction til og med Practical implications) | 4 497 ord | 5 000 |
| Sammendrag | 250 ord | 250 |
| Tabeller + figurer i hovedteksten | 2 + 4 = 6 | 6 |
| Referanser | 12 | 40 |
| Nøkkelord | 6 (5 MeSH) | 6, minst 4 MeSH |

Tallkontrollen (`tallkontroll_jsams.py`) viser at alle tall i JSAMS-versjonen står i det fryste manuset eller tabellene, med to forklarte unntak (avsnittshenvisningen 3.5 og modellversjonen 5.5). PDF-ene er bygget i full syklus uten udefinerte referanser eller manglende nummer.

## Innsendt

Manuset ble sendt inn til JSAMS via Editorial Manager 1. november 2026 (Original Research, Physical Activity & Public Health, klassifisering Physical activity; supplement og STROBE som e-Component, figurene som TIFF enkeltvis). Sammendraget ble kortet til 239 ord fordi Editorial Manager telte 261 ved 250 i vår telling.

## Sjekkliste før innsending (gjennomført)

- [x] Underdisiplin: «Physical activity and public health (as relevant to sport and exercise)» er valgt; «Sports science» er alternativet. Står på tittelsiden og i følgebrevet.
- [x] Følgebrevet er datert Ås, 1 November 2026.
- [x] Les Conclusion og Practical implications; de er nye tekster, ikke flyttet tekst.
- [x] Godta at tabell 3 er tatt ut og tabell 4 ligger i supplementet (ellers må to figurer ut i stedet).
- [x] Sammendraget er nøyaktig 250 ord etter vår telling; Word kan telle «n», «=» og «[CI]» annerledes. Sjekk tellingen i Word før opplasting.
- [x] JSAMS ber om etisk godkjenningsnummer og dato; manuset forklarer at godkjenning ikke var påkrevd og at Sikt bekreftet bruken uten referansenummer (Atles beslutning 01.11.2026 for A1).
- [x] Editorial Manager vil ha figurene som egne filer (TIFF-ene i `figurer_opplasting/`) og trolig sammendraget i et eget felt.

## Tynning 01.11.2026

Resultatdelen gjengir ikke lenger tabellene: konverteringsprosent per debutalder, kjønnstall, retention-andeler per k og robusthetsestimatene med intervaller står nå bare i tabell 2, figur 3 og 4 og tabell S2–S5, og teksten viser dit. Tallene som bærer argumentet er beholdt. Endringen er gjort i det fryste manuset (logget i `../FREEZE.md`), så SJMSS- og JSAMS-versjonen har samme tekst. Hovedteksten gikk fra 392 til 291 tall, resultatdelen fra 262 til 161.
