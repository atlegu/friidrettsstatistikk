# Status og gjenstående arbeid

**Sist oppdatert:** 2026-08-29

Denne filen holder oversikt over hva som pågår og hva som gjenstår, slik at
arbeidet kan tas opp igjen uten å måtte rekonstruere sammenhengen.
Historikken over hva som er gjort ligger i `scraper/OPERATIONS_LOG.md`.

---

## Pågår nå

**Komplettering — de to siste hullene etter sesongkontrollen.**
Skript: `scraper/kjor_komplettering.sh` (egen prosess, uavhengig av terminal).

1. **Markørradene.** 1 028 resultater fordelt på 322 stevner ble kastet ved
   hver kjøring fordi kilden henger markører på selve resultatverdien
   («20.37.52mx», «4.43 L», «7.83A», «24.56+») og databasetriggeren caster
   `performance` til numeric. Parseren skiller nå tall fra markør og lagrer
   markøren ordrett i `results.source_marker`. Stevnene er hentet ut av
   loggene til `scraper/markorlister/`, og bare de hentes på nytt — vi teller
   ikke hele sesonger mot kilden om igjen.
2. **2018 utendørs.** Sesongen ble aldri kontrollert. Alle tre forsøkene døde
   på første kall til Supabase mens DNS var nede, fordi `vent_pa_nett()` sto
   *etter* `load_events()`. Rekkefølgen er rettet, og sesongen kjøres fullt ut.

Sjekk status:

```bash
pgrep -f update_results.py && echo kjører
tail -30 scraper/logs/komplettering_*.log
```

Kan trygt avbrytes og startes igjen — importen hopper over resultater som
allerede finnes.

**Markørene er bevisst ikke tolket.** Kildesiden har ingen tegnforklaring.
`mx` er etter alt å dømme blandet heat, jf. kravspekkens §7, men det er ikke
bekreftet, og en gjetning i et datafelt er verre enn en ærlig råverdi. Manuell
tidtaking (` M`) tolkes derimot, fordi det mønsteret er verifisert.

---

## Bakgrunn: hvorfor alle sesonger kontrolleres

`find_missing_meets()` regnet et stevne som ufullstendig kun hvis det hadde
under 10 resultater (`MIN_RESULTS_THRESHOLD`). Delvis importerte stevner ble
derfor aldri hentet på nytt. «Hvam, Norgeslekene» hadde 188 resultater i basen
mot 539 i kilden — hele øvelser manglet.

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
