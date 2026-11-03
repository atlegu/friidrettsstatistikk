# Brief Report-versjonen av A3 for JSAMS

Bygget 3. november 2026 etter redaktøravvisningen av JSAMS-D-26-02238 (Tim Meyer: «A brief report seems possible … would need substantial shortening»). Grenser for Brief Reports i JSAMS: 1 500 ord hovedtekst (uten tittel, sammendrag, tabeller/figurer, figurtekster, takk og referanser), høyst 2 tabeller/figurer, høyst 20 referanser, sammendrag ≤100 ord uten struktur.

## Filer

| Fil | Innhold | Lastes opp som |
|---|---|---|
| `main_brief.docx` / `.pdf` | Anonymisert Brief Report: sammendrag, nøkkelord, Introduction, Methods, Results, Discussion, Conclusion, Acknowledgments, Data availability, KI-erklæring, referanser; tabell 1 (senior og lik karrierelengde etter debutalder) og figur 1 (retention k år etter debut) | Manuscript |
| `title_page_brief.docx` / `.pdf` | Tittelside; artikkeltype Brief Report med henvisning til JSAMS-D-26-02238; ordtellinger | Title page |
| `supplement_brief.docx` / `.pdf` | Tabell S1–S5 som før, S6 (utvalgskarakteristikk, tidligere tabell 1) og figur S1–S3 (debutalder etter kull, U-formen, aldersklokken) | e-Component |
| `cover_letter_brief.docx` / `.md` | Følgebrev til Meyer, datert 3. november 2026, viser til forslaget hans | Cover letter |
| `declaration_of_interests.docx`, `acknowledgement_funding_ethics.docx`, `credit_author_statement.docx` | Uendret fra fullversjonen | De tre erklæringene |
| `figurer_opplasting/Figure_3.tiff` | Figur 1 i Brief Report-en (retention k år etter debut) | Figure |

Bygges med `./kompiler.sh` (kontroll + pdflatex/bibtex) og `python3 lag_docx.py`. `kontroll_brief.py` sjekker at alle tall finnes i det fryste manuset, at grensene holdes, og skriver tittelsiden med tellingene. Referansestil og bibliografi deles med fullversjonen (`../manus_jsams/jsams.bst`, `jsams.csl`, `references.bib`).

## Hva som er beholdt, og hva som er flyttet

- **Beholdt i teksten:** debutmønsteret i to setninger; U-formen med LR-testen, kategoriestimatene og nulltrenden; koronaforbeholdet for debut 16; varighetsklokken (51 mot 26–40 prosent etter ett år, 17 mot 3–10 etter fem; 20,4 mot 4,5–6,6 ved lik karrierelengde, OR 0,70); landmark ved 17 (0,85 → 0,99); robusthetsspennet 0,94–1,00. Diskusjonen beholder de to klokkene, seleksjonslesningen, første-sesong-filteret, «nåtilstand slår historie» og begrensningene.
- **Flyttet til supplementet:** tabell 1 (karakteristikk) → S6; figur 1, 2 og 4 → S1–S3; robusthetstabellen er S5 som før.
- **Tatt ut:** kjønnsinteraksjonen (står i S2), debut 17–19-analysen, aldersklokkens tall, mekanismediskusjonen om de to armene, Practical implications. Referansene er redusert fra 11 til 7 (Korn, Larson, Crane og Espedalen ut).
- **Ikke endret:** ingen analyse, ingen tall. Teksten er kondensert fra det fryste manuset, ikke skrevet på nytt.

## Mot grensene

| | Brief Report | Grense |
|---|---|---|
| Hovedtekst | 1 319 ord | 1 500 |
| Sammendrag | 93 ord | 100 |
| Tabeller + figurer | 1 + 1 | 2 |
| Referanser | 7 | 20 |

Editorial Manager teller om lag 4 prosent flere ord enn vår teller (ved forrige innsending 261 mot 250 i sammendraget), så sammendraget er holdt under 95.

## Atle må avgjøre før innsending

- [ ] Les hele teksten; den er kondensert, så hver setning bærer mer enn før.
- [ ] Preprint av fullversjonen (SportRxiv eller lignende) før innsending, slik at de fulle analysene forblir siterbare? Tittelsiden sier nå «not available on a preprint server»; endres hvis preprint legges ut.
- [ ] Editorial Manager: velg artikkeltype Brief Report; oppgi manuskriptnummeret JSAMS-D-26-02238 i følgebrevet (står der) og i skjemaets felt for tidligere innsending hvis det finnes.
- [ ] Figur 1 lastes opp som `figurer_opplasting/Figure_3.tiff` (filnavnet følger fullversjonens nummerering; døp om til Figure_1 ved opplasting).
