# Status og gjenstående arbeid

**Sist oppdatert:** 2026-08-31

Denne filen holder oversikt over hva som pågår og hva som gjenstår, slik at
arbeidet kan tas opp igjen uten å måtte rekonstruere sammenhengen.
Historikken over hva som er gjort ligger i `scraper/OPERATIONS_LOG.md`.

---

## Importen er komplett

**Alle sesonger 2013–2026 er kontrollert mot kilden.** Ingen løpende kjøring.

| Runde | Resultat |
|---|---|
| Sesongkontroll, alle år | Basen vokste fra 1 418 058 til over 1,9 mill. resultater |
| Markørrader (`mx`, `L`, `A`, `+`) | 1 678 hentet inn, 26 sesong-/moduskombinasjoner |
| 2018 utendørs | 1 222 stevner kontrollert, 179 hentet inn |
| Firedelte tider (`H.MM.SS.hh`) | ~25 rader, 18 stevner — `scraper/kjor_timeformat.sh` |

Tre feilkilder ble funnet og rettet **i importlogikken**, ikke i etterkant:

1. **`MIN_RESULTS_THRESHOLD = 10`** i `find_missing_meets()` gjorde at delvis
   importerte stevner aldri ble hentet på nytt. «Hvam, Norgeslekene» hadde 188
   resultater i basen mot 539 i kilden. Ny `--verify` teller mot kilden per
   stevne.
2. **Kildemarkører på resultatverdien** («20.37.52mx», «4.43 L») fikk
   databasetriggeren til å avvise raden. `_skill_ut_markor()` skiller nå tall
   fra markør, og markøren lagres ordrett i `results.source_marker`.
3. **Tider over én time** («1.25.29.2») ble sendt uendret til basen.
   `fix_performance_format()` konverterer nå til `H:MM:SS.hh`.

**Markørene er bevisst ikke tolket.** Kildesiden har ingen tegnforklaring.
`mx` er etter alt å dømme blandet heat, jf. kravspekkens §7, men det er ikke
bekreftet, og en gjetning i et datafelt er verre enn en ærlig råverdi. Manuell
tidtaking (` M`) tolkes derimot, fordi det mønsteret er verifisert.

Tre rader lar seg ikke redde automatisk: «3.320.78» er en skrivefeil i kilden,
og to verdier er registrert i feil øvelsestype.

### Nye verktøy

| Skript | Bruk |
|---|---|
| `update_results.py --verify` | Tell mot kilden per stevne, hent det som mangler |
| `update_results.py --kun-stevner FIL` | Hent bare navngitte stevner. Billig når man vet hva som mangler. |

Ny `--verify`-modus teller mot kilden per stevne. Resultatet så langt: så godt
som **samtlige stevner i alle kontrollerte sesonger var ufullstendige**, og
basen har vokst fra 1 418 058 til over 1 820 000 resultater.

---

## Gjenstår

### Import og datakvalitet

| Sak | Omfang | Merknad |
|---|---|---|
| Markørrader + 2018 utendørs | pågår | se over |
| Sesonger før 2013 | ikke vurdert | Dekningen er ujevn; må vurderes separat |
| 121 utøvere med fødselsår som strider mot egne resultater | krever skjønn | `scraper/backups/fix_ugyldig_alder_20260821_171844_til_gjennomgang.csv` |
| 1 777 NM-medaljer fra 1970+ uten `athlete_id` | krever navnearbeid | 2 245 fra før 1970 er forventet ukoblet |
| 4 korrupte utøvernavn | manuell | Alfred Lund Stende (×2), Linnea Elise Westre, Siv Sundt (12) |
| 2 søppelklubber | manuell | holder de fire postene over |
| 12 klubber med etternavn/stedsnavn | krever skjønn | Franklin, Siggerud, Stange, Rjukan, Fåberg m.fl. |
| Prefiks-dubletter blant klubber | domenevalg | «Kongsvinger IL» vs «Kongsvinger IL Friidrett» — skal friidrettsgruppa være egen enhet? |
| 2 091 resultater uten `performance_value` | delvis kjent | mest mangekamp-poeng; 38 er duplikater av poengsummer |

### Presentasjon

| Sak | Merknad |
|---|---|
| «ukjent» som klubb | 1 289 resultater, 309 utøvere. Vises nå som «Annet» i klubblisten — vurder å skjule |
| Pikenavn i parentes | «Toril Lauritsen (Nyborg)» — §9-data, beholdt i basen. Bør presenteres pent, ikke fjernes |
| 11 542 utøvere uten resultater | Ekte personer i kildens register. Skal ikke slettes. Bør skilles ut i lister og tellinger |
| Øvrige sider enn klubblisten | Bare `/klubber` er gjennomgått. Utøver-, stevne- og statistikksider gjenstår |

---

## NFIF-tilbudet

Frist **31.08.2026**. Underlag i `NFIFProsjekt/`, start med `01_STRATEGI.md`.

**Tallene i tilbudsdokumentene er utdaterte.** De sier 1 190 655 resultater fra
2013 og senere. Etter opprydningen er tallet vesentlig høyere og stiger fortsatt.
Oppdater når kjøringen er ferdig — historien er sterkere enn før: vi kan
dokumentere at vi fant og tettet et etterslep på over 400 000 resultater.

Se også `NFIFProsjekt/02_ARBEIDSPLAN.md` for de fire beslutningene som fortsatt
er åpne (bemanning, språk, prisnivå, kontakt med NFIF).

---

## Klubbrapporter

`analyse/klubbrapport/` er fellesmodulen. Ferdige klubber: `vidar/`, `Tjalve/`,
`bul/`, `fana/`. Ny klubb er ca. tjue linjer konfigurasjon — se
`analyse/klubbrapport/README.md`.

Rapportene bør bygges på nytt når importen er ferdig, siden tallene har endret
seg betydelig:

```bash
cd analyse/vidar && ./kjor.py
```
