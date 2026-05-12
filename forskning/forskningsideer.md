# Forskningsideer — friidrett.live-data

Oversikt over mulige forskningsprosjekter basert på tilgjengelige data.

## 1. Prestasjonsutvikling og alder

**Spørsmål**: Når når norske friidrettsutøvere toppnivå, og hvordan varierer dette mellom øvelsesgrupper?
- Analysere alderskurver for personlige rekorder
- Sammenligne sprint vs. kast vs. utholdenhet
- Identifisere typisk «peak age» per øvelse
- **Data**: results_full + birth_date, ~1.25M resultater

## 2. Frafall og karrierelengde

**Spørsmål**: Hvilke faktorer predikerer om en ungdomsutøver fortsetter til seniorklassen?
- Definere «aktiv» basert på siste registrerte resultat
- Analysere overgangsrate fra J/G-klasser til senior
- Sammenligne på tvers av øvelsesgrupper og regioner
- **Data**: athletes + results (tidsserier per utøver)

## 3. Geografisk fordeling og regionale forskjeller

**Spørsmål**: Hvordan fordeler norsk friidrettsaktivitet seg geografisk?
- Kartlegge klubbtetthet per fylke/region
- Analysere prestasjonsnivå per region
- Undersøke om urbane/rurale forskjeller finnes
- **Data**: clubs (city, county) + results + athletes

## 4. Konkurransefrekvens og prestasjon

**Spørsmål**: Er det en sammenheng mellom antall konkurranser per sesong og prestasjonsutvikling?
- Telle stevnedeltakelser per utøver per sesong
- Korrelere med sesongbeste/PB-forbedring
- Optimal konkurransebelastning per aldersgruppe
- **Data**: results (antall per athlete_id per season), season_bests

## 5. Innendørs vs. utendørs prestasjoner

**Spørsmål**: Hvordan konverterer innendørs- til utendørsprestasjoner i norsk friidrett?
- Bygge konverteringstabeller basert på faktiske resultater
- Sammenligne med internasjonale konverteringstabeller
- **Data**: results_full (meet_indoor), personal_bests

## 6. Vindeffekt på sprintprestasjoner

**Spørsmål**: Hvor stor er vindeffekten på 100m og 200m i norsk kontekst?
- Regresjonsanalyse: prestasjon vs. vindstyrke
- Sammenligne med internasjonale modeller (Linthorne, etc.)
- **Data**: results_full med wind-data, ~sprint-øvelser

## 7. NM-medaljeprogresjon

**Spørsmål**: Hvordan har prestasjonsnivået i NM utviklet seg over tid?
- Trendanalyse av gull/sølv/bronse-prestasjoner per øvelse
- Bredde vs. topp (avstand mellom 1. og 8. plass)
- **Data**: championship_medals (~13 600 medaljer), results

## 8. Klubbstørrelse og sportslig suksess

**Spørsmål**: Produserer store klubber bedre utøvere, eller er det diminishing returns?
- Definere klubbstørrelse (aktive utøvere per sesong)
- Korrelere med toppresultater, NM-medaljer, landslagsuttak
- **Data**: clubs + results + championship_medals

## 9. Tidlig spesialisering vs. allsidighet

**Spørsmål**: Presterer utøvere som konkurrerer i flere øvelsesgrupper som unge bedre som seniorer?
- Måle øvelsesbredde i ungdomsårene (antall event_categories)
- Følge seniornivå for «spesialister» vs. «allroundere»
- **Data**: results_full, longitudinelt per utøver

## 10. Manuell vs. elektronisk tidtaking — systematisk avvik

**Spørsmål**: Hva er det faktiske avviket mellom manuell og elektronisk tidtaking i norsk friidrett?
- Utøvere med begge typer i samme sesong
- Sammenligne med FAT-korreksjon (+0.24s)
- **Data**: results med is_manual_time, sprint-øvelser <800m

---

## Metodiske hensyn

- **Kjønnsbias**: 30 000 utøvere mangler kjønn — alle kjønnsanalyser er ufullstendige
- **Seleksjonsbias**: Pre-2012-data inkluderer kun prestasjoner over visse terskler
- **Overlevelsebias**: Kun utøvere som konkurrerer finnes i datasettet
- **Manuell tidtaking**: Må filtreres eksplisitt for sammenlignbare analyser
