# Presentasjon for NFIF

**Torsdag 17.09.2026, 17:30–17:55 på Teams.**
15–20 min presentasjon, 5–10 min spørsmål.

| Fil | Innhold |
|---|---|
| `PRESENTASJON.pdf` | 13 lysbilder i 16:9. Bygges med `./lag_lysbilder.py` fra `PRESENTASJON.md`. |
| `MANUS.md` | Tidsplan minutt for minutt, hvem som er i rommet, hva som skal sies |
| `DEMO.md` | Klikkmanus for de sju demominuttene |
| `SPORSMAL.md` | Forberedte svar, også på de vanskelige |
| `reserve/` | Skjermbilder av demosidene, i tilfelle nettet svikter |

## Må gjøres før møtet

| | Hva | Hvorfor |
|---|---|---|
| 1 | **Rull ut forsidefiksen til Vercel** | Produksjon viser i dag «Resultater 0» og «Årslister 2025». Rettet i `web/`, men ikke utrullet. Uten dette må demoen kjøres lokalt. |
| 2 | Finn ut hvilken rolle **Hilde Trageton** har | Fjerde deltaker. Vi vet ikke hva hun ser etter. |
| 3 | Avklar **kapasitet i timer per uke** for hver av de tre i okt–des | Det skarpeste spørsmålet som kan komme. Ha tallet klart. |
| 4 | Logg inn i admin før møtet starter | Ikke skriv passord på delt skjerm. |
| 5 | Øv på demoen én gang med klokke | Sju minutter er kortere enn det høres ut. |

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

Tallene i lysbilde 3 og 6 er hentet fra basen 14.09.2026. Sjekk dem på nytt
rett før møtet hvis importen har kjørt i mellomtiden.
