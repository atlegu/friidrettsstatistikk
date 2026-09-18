# Presentasjon for NFIF

**Teams, 17:30–17:55.**
15–20 min presentasjon, 5–10 min spørsmål.

| Fil | Innhold |
|---|---|
| `PRESENTASJON.pdf` | 18 lysbilder i 16:9, bygget rundt fire punkter: alt inn og kvalitetssikret · visningen · rapporter og analyser · stabilt, raskt og fortløpende. Bygges med `./lag_lysbilder.py` fra `PRESENTASJON.md`. |
| `MANUS.md` | Tidsplan minutt for minutt, hvem som er i rommet, hva som skal sies |
| `DEMO.md` | Klikkmanus for de sju demominuttene |
| `SPORSMAL.md` | Forberedte svar, også på de vanskelige |
| `reserve/` | Skjermbilder av demosidene, i tilfelle nettet svikter |
| `skisser/` | Designskisser i Norsk Friidretts profil. HTML som kan vises live, og PNG som ligger i lysbilde 6 og 7. Bygg om med `lag_skisser.sh`. |

## Må gjøres før møtet

| | Hva | Hvorfor |
|---|---|---|
| 1 | Finn ut hvilken rolle **Hilde Trageton** har | Fjerde deltaker. Vi vet ikke hva hun ser etter. |
| 2 | Avklar **kapasitet i timer per uke** for hver av de tre i okt–des | Det skarpeste spørsmålet som kan komme. Ha tallet klart. |
| 3 | Logg inn i admin før møtet starter | Ikke skriv passord på delt skjerm. |
| 4 | Øv på demoen én gang med klokke | Sju minutter er kortere enn det høres ut. |

## Deltakere

| Person | Rolle |
|---|---|
| Thor Gjesdal | NFIF, teknisk kontakt |
| Magnus Trosdahl | Seksjonsleder NFIF, kommersielt |
| Roar Holen | Laget FriSys/LiveRes, stevnesystemet arrangørene bruker |
| Hilde Trageton | Rolle ukjent |

**Roar Holen er den viktigste å planlegge for.** Han har bygget systemet
resultatene skal komme fra, og er motparten i §13-integrasjonen. Se avsnittet
om ham i `MANUS.md` og de forberedte svarene i `SPORSMAL.md`.

## Bygge på nytt

```bash
./lag_lysbilder.py
```

Tallene i lysbilde 3 og 7 er hentet fra basen 14.09.2026. Sjekk dem på nytt
rett før møtet hvis importen har kjørt i mellomtiden.
