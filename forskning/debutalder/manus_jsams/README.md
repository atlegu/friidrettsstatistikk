
## JSAMS-versjon (01.11.2026)

`manus_jsams/` inneholder innsendingsversjonen for *Journal of Science and Medicine in Sport* (anbefalt i `TIDSSKRIFTVURDERING_2026-11-01.md`: Elsevier-avtale ut 2027, nivå 2 fra 2027): anonymisert manus med strukturert sammendrag, MeSH-nøkkelord, Conclusion og Practical implications, egen tittelside, supplement (S1–S5), følgebrev, STROBE-sjekkliste og TIFF-figurer. Bygges fra det fryste manuset med `manus_jsams/kompiler.sh`; `manus_jsams/tallkontroll_jsams.py` sikrer at ingen tall avviker; `python3 manus_jsams/lag_docx.py` lager Word-filene. Se `manus_jsams/ENDRINGER_JSAMS.md`. SJMSS-versjonen i `manus/` er uendret.
