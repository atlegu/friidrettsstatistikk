# KRITISK: Fiks feil kjønn på utøvere

## Problemet

Nesten alle norgesrekorder for damer og alle tiders lister for damer viser MENN i stedet for kvinner.

Eksempel: 5000m kvinner alle tiders viser:
- Arvid Hansen, Oliver Andersen Vedvik, Ola Krangnes, Sverre Dombu, etc.
- Kun Karoline Bjerkeli Grøvdal og Ingrid Kristiansen er faktiske kvinner

## Årsak

Et batch-script (`fix_missing_gender_batch.py`) infererte kjønn basert på medkonkurrenter i samme heat. Scriptet antok at alle i samme løp har samme kjønn - men dette var feil fordi:
1. Noen løp er mixed
2. Feil i kildedataene propagerte seg

Scriptet kjørte 5+ runder og satte tusenvis av utøvere til feil kjønn.

## Status per 27. jan 2026

- ~46140 utøvere totalt
- Mange menn er feilaktig satt til gender='F'
- Alle kvinnelister er ødelagt

## Løsning som må implementeres

### Steg 1: Reset alle feilaktige inferenser
Sett gender=NULL for alle utøvere som IKKE har resultater i autoritative kjønnsspesifikke øvelser.

### Steg 2: Sett kjønn basert på autoritative øvelser
Disse øvelsene er 100% kjønnsspesifikke:

**Herreøvelser (sett gender='M'):**
- Alle øvelser med 91,4cm, 100cm, 106,7cm (hekkhøyder)
- 110 meter hekk (alle varianter)
- 10-kamp

**Dameøvelser (sett gender='F'):**
- Alle øvelser med 76,2cm, 84cm (hekkhøyder)
- 100 meter hekk (IKKE de med herrehøyder)
- 7-kamp

### Steg 3: Sett kjønn basert på norske fornavn
Norske navn har klare kjønnsmønstre:
- Mannsnavn: Ole, Per, Jan, Lars, Erik, Anders, Bjørn, Tor, Knut, Arvid, Oliver, etc.
- Kvinnenavn: Anna, Anne, Eva, Liv, Kari, Marit, Ingrid, Karoline, etc.

### Steg 4: Manuell gjennomgang
For utøvere som ikke kan klassifiseres automatisk.

## Eksisterende scripts

1. `fix_gender_authoritative.py` - Bruker høydespesifikke øvelser (fungerer delvis)
2. `fix_missing_gender_batch.py` - IKKE KJØR IGJEN - dette skapte problemet
3. `fix_missing_gender.py` - Første versjon, også problematisk

## SQL for å sjekke status

```sql
-- Tell utøvere per kjønn
SELECT gender, COUNT(*) FROM athletes GROUP BY gender;

-- Sjekk 5000m kvinner (skal IKKE ha mannsnavn)
SELECT athlete_name, performance_value, season_year
FROM results_full
WHERE event_name = '5000 meter'
AND gender = 'F'
AND meet_indoor = false
ORDER BY performance_value
LIMIT 20;
```

## Neste steg

1. Lag et nytt script som:
   - Først setter gender=NULL for alle som ikke har autoritative øvelser
   - Deretter setter kjønn basert på fornavn
   - Til slutt kjører forsiktig inferens kun for de som fortsatt mangler

2. Verifiser at kvinnelistene er korrekte

## Kontakt

Dette arbeidet ble startet 27. januar 2026. Hvis du fortsetter, les denne filen først!
