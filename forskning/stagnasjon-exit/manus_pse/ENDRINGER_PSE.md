# PSE-versjonen av A1 «Stagnation before exit»

Laget 31.10.2026, Word-versjoner 01.11.2026, for innsending til *Psychology of Sport and Exercise* (Elsevier, FEPSAC; NMBU-avtale ut 2027). Det fryste manuset i `../manus/` er ikke rørt. Alt her bygges fra det med `kompiler.sh`, som kjører `bygg_pse.py` og så pdflatex/biber.

## Filer

| Fil | Innhold |
|---|---|
| `main_anonymised.tex` / `.pdf` | Anonymisert hovedfil (sammendrag, hovedtekst, tabell 1–3, figur 1–4, referanser) |
| `title_page.tex` / `.pdf` | Egen tittelside med forfatter, ORCID, CRediT, interessekonflikter, finansiering, etikk, takk |
| `supplement.tex` / `.pdf` | Tabell S1 (utvalgsflyt), tabell S2 (robusthet, tidligere tabell 4), S3 (avvik fra analyseplanen) |
| `abstract.docx` | Sammendrag med nøkkelord som egen fil (eget punkt i opplastingen; hentes automatisk fra hovedfilen) |
| `highlights.md` / `.docx` | Fem punkter, alle ≤ 85 tegn |
| `cover_letter.md` / `.docx` | Følgebrev med begrunnelse for lengden |
| `declaration_of_interests.md` / `.docx` | Interesseerklæring (Elseviers skjema fylles ut i innsendingssystemet; dette er teksten) |
| `main_anonymised.docx`, `title_page.docx`, `supplement.docx` | **Word-versjonene som lastes opp** (Elsevier vil ha .docx som kildefil). Lages av `lag_docx.py` fra de samme .tex-filene: pandoc + citeproc (APA 7 fra CSL), Times New Roman 12, dobbel linjeavstand, «Table N.»/«Figure N.» i bildetekstene, henvisninger som ren tekst |
| `references.bib` | APA-klar kopi av referanselisten, med tre nye referanser (Ryan & Deci 2000, Harter 1978, Hsieh mfl. 1998; CrossRef-verifisert 31.10.2026) |
| `bygg_pse.py` | Setter sammen hovedfil og supplement fra det fryste manuset |
| `tallkontroll_pse.py` | Alle tall i PSE-versjonen må stå i det fryste manuset eller i hvitlisten |
| `lag_docx.py` | Word-versjonene (kjøres etter `kompiler.sh`; trenger pandoc og python-docx) |

## Hva som er endret, og hvorfor

1. **Innledningen er skrevet om med teorien først.** Mestringserfaring (Bandura 1977), opplevd kompetanse i selvbestemmelsesteori (Ryan & Deci 2000), effektansmotivasjon (Harter 1978) og oppgave- mot ego-orientering (Nicholls 1984) står nå i innledningen, og H2 avledes derfra som forsterkningskorollaret. Dette sto før bare i diskusjonen. PSE krever at kvantitative studier er teoretisk begrunnet.
2. **Sammendraget** er ustrukturert og på 247 ord (grense 250). «Key Points» (SMO-krav) er tatt ut; PSE bruker highlights i egen fil.
3. **Ny metodedel «Sample size and precision».** PSE ber om a priori styrkeberegning. Grunnlaget er planstadiets kjente tall (3 808 utøvere, 648 hendelser, dokumentert i `OSF_PREREGISTRATION.md` før modellene ble kjørt) og effektstørrelsen fra IJSSC-manuset (OR 2,04 per SD). Med Hsieh mfl. (1998), hendelsesandel 0,17 og antatt R² = 0,25 mellom progresjon og kovariater: 80 % styrke for OR ≈ 1,15 per SD, 90 % for ≈ 1,18; interaksjon 80 % for OR ≈ 1,14 per kvartal (SD kvartal 1,09, uavhengighet antatt). **Atle bør vurdere R²-antagelsen**; regnestykket står i kommentaren til denne filen nederst.
4. **Tabell 4 (robusthet) er flyttet til supplementet som tabell S2**, og listen over avvik fra analyseplanen er flyttet dit som S3. Dette er PSEs anbefalte vei for å holde lengden nede. Teksten i resultatdelen viser til tabell S2.
5. **Tredje person om egne arbeider.** «companion study», «this research programme» og liknende er byttet med sitering i tredje person, slik APA og Elsevier anbefaler for dobbelt anonymisert vurdering. Ingen «Author (2026)»-maskering, siden de publiserte arbeidene uansett er sporbare.
6. **APA 7** via biblatex-apa. RAE-artikkelen siteres som (Guttormsen, in press); JSAMS-artikkelen og det innsendte frafallsmanuset blir 2026a og 2026b. Frafallsmanuset står som «Manuscript submitted for publication».
7. **Sluttdel etter PSE-mal.** Data availability, Supplementary material og «Declaration of generative AI and AI-assisted technologies in the manuscript preparation process» står i hovedfilen før referansene. CRediT, interessekonflikter, finansiering, etikk og takk står på tittelsiden (anonymitet). Abbreviations-listen (SMO) er tatt ut.
8. **Én ny setning i diskusjonen** (mestringsdelen): at dataene ikke kan skille om kompetanse ble opplevd gjennom egen fremgang eller gjennom rangen fremgangen også gir. Første avsnitt i samme del er kortet, siden teorien nå står i innledningen.

Ingen tall er endret. `tallkontroll_pse.py` finner åtte nye tall, alle fra styrkeberegningen, og de eneste tallene som er falt bort er ORCID, postadresse, ordtelling og en seksjonshenvisning.

## Lengde

| | Ord |
|---|---|
| PSE-versjonen totalt, Word-telling av .docx (sammendrag, tekst, tabeller, figurtekster, referanser) | 8 690 |
| Samme, talt fra PDF-en uten linjenumre | 8 854 |
| Hovedtekst (Introduction til Data availability) | 6 373 |
| Fryst SMO-versjon totalt, samme måte | 8 866 |
| PSE-grense | 8 000 |

Overskridelsen begrunnes i følgebrevet. Vil Atle under grensen, er de nærmeste kuttene: figur 4 (Kaplan–Meier) til supplementet (~100 ord), robusthetsavsnittet i resultatdelen kortet til tabellhenvisning (~250 ord), og «Relation to the earlier studies»-delen slått sammen med «Principal findings» (~150 ord).

## Atle må gjøre før innsending

- [x] Sikt: ingen referansenummer eller dato oppgis (Atles beslutning 01.11.2026); klammene er fjernet.
- [x] KI-erklæringen oppgir Claude Opus 5.5 (01.11.2026).
- [ ] Vurder R² = 0,25 i styrkeberegningen og om interaksjonsberegningen skal stå.
- [ ] Godta at tabell 4 ligger i supplementet, eller flytt den tilbake (én linje i `bygg_pse.py`).
- [ ] STROBE-sjekklisten (nevnt i teksten og følgebrevet) legges ved som egen fil.
- [ ] Figurene lastes opp som egne filer (`../figures/fig1–4*.png`). Alle er 300 dpi og 2 421–3 108 piksler brede, over PSEs krav på 2 244 for full bredde.
- [x] Følgebrev datert 1. november 2026; ingen forslag til fagfeller.
- [ ] Les gjennom innledningen og den nye metodedelen; de er nye tekster, ikke flyttet tekst.

## Bygging

```bash
./kompiler.sh && python3 tallkontroll_pse.py && python3 lag_docx.py
```

PDF-ene er kontrollversjoner; det er .docx-filene som sendes inn. Figurene lastes i tillegg opp som egne PNG-filer.

biber fra TeX Live feiler på denne maskinen (lipo-utpakkingen). `kompiler.sh` bruker en utpakket arm64-biber; stien kan overstyres med `BIBER=...`. Lag den slik om den mangler:
`lipo /usr/local/texlive/2025/bin/universal-darwin/biber -thin arm64 -output <sti>`.

<!-- Styrkeberegning (Hsieh mfl. 1998): n = (z_{1-α/2} + z_{1-β})² / [(1-R²) p (1-p) β²], p = 648/3808 = 0,170.
     80 %: (1,960+0,842)² = 7,85 → β = sqrt(7,85 / (3808·0,75·0,170·0,830)) = 0,1395 → OR 1,150.
     90 %: (1,960+1,282)² = 10,51 → β = 0,1614 → OR 1,175.
     Interaksjon Δ×kvartal: Var(Δ·Q_c) ≈ Var(Q) = 1,088² = 1,184 → β = sqrt(7,85 / (3808·0,75·0,141·1,184)) = 0,128 → OR 1,137. -->
