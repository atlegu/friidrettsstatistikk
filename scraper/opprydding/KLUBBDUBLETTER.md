# Opprydding i klubbregisteret

Underlag fra `finn_klubbdubletter.py`. Full liste med id-er: `opprydding/klubbdubletter_20260914_161324.csv`

**Skriptet foreslår ingenting.** Navnelikhet er ikke bevis. Det som betyr noe er
**felles utøvere**: antall utøvere med resultater for begge postene. Er tallet
høyt, er det som regel to skrivemåter av samme klubb. Er det null, er det
oftere to reelle klubber med lignende navn.

| Gruppe | Par | Avgjørelse |
|---|---:|---|
| [A · Trolig samme klubb](#a--trolig-samme-klubb) | 36 | Slå sammen. Behold skrivemåten som dominerer i nyere resultater. |
| [B · Friidrettsgruppa som egen enhet](#b--friidrettsgruppa-som-egen-enhet) | 52 | Domenevalg, ikke skrivefeil. Bør avklares med NFIF. |
| [C · Svakt grunnlag](#c--svakt-grunnlag) | 123 | Under tre felles utøvere. Anbefaling: la ligge. |

---

## Slik bekrefter du

1. Åpne CSV-en i Excel eller Numbers.
2. Legg til en kolonne helt til høyre med overskriften **`handling`**.
3. Skriv i radene du tar stilling til:

   | Verdi | Betyr |
   |---|---|
   | `ja` | Slå sammen. Den mindre posten forsvinner, resultatene flyttes til den større. |
   | `ja-motsatt` | Slå sammen, men behold den **mindre** posten. Brukes når den lille har riktig navn. |
   | `navn` | Ikke slå sammen, bare rett navnet på den større posten. |
   | `nei` | La begge stå. |
   | *(tom)* | Ikke bestemt. Hoppes over. |

4. **Vil du ha et helt annet navn** enn begge de to som står der, legg til en
   kolonne `nytt_navn`. Klubben som overlever får det navnet.

   | handling | nytt_navn |
   |---|---|
   | `ja` | IL Skjalg, Stavanger |
   | `navn` | Kristiansands IF Friidrett |

   Står `nytt_navn` tomt, beholder den overlevende klubben navnet sitt.

5. Lagre som CSV, og kjør:

```bash
cd scraper && source venv/bin/activate
python slaa_sammen_gjennomgatte.py opprydding/klubbdubletter_20260914_161324.csv
```

Det er en tørrkjøring: den viser hva som ville skjedd, uten å endre noe.
Er listen riktig, kjør samme kommando med `--apply`.

Du trenger ikke fylle ut alt på én gang. Rader uten `handling` røres ikke, og
du kan kjøre så mange ganger du vil.

---

## A · Trolig samme klubb

Samme klubb under to skrivemåter, der forskjellen bare er organisasjonsleddet:
«Idrettslaget Skjalg» mot «IL Skjalg». Mange felles utøvere og overlappende år.

Dette er gruppa det er verdt å bruke tid på.

| Større post | Mindre post | Felles utøvere | Res. i mindre | År |
|---|---|---:|---:|---|
| Idrettslaget Skjalg | IL Skjalg | 107 | 572 | 1955–2026 / 1938–2021 |
| Norna-Salhus IL | IL Norna-Salhus | 66 | 289 | 1959–2026 / 1954–2022 |
| IL Dalebrand | Idrettslaget Dalebrand | 32 | 272 | 1958–2026 / 2013–2026 |
| Stålkameratene IL | IL Stålkameratene | 26 | 139 | 1963–2026 / 1959–1997 |
| Lye IL | Lye Idrettslag | 24 | 672 | 2000–2026 / 2012–2026 |
| Larvik Turn & IF | Larvik TIF | 23 | 124 | 1949–2026 / 1950–2020 |
| FIK BFG Fana | BFG Fana | 21 | 76 | 1958–2012 / 1984–2011 |
| Torvastad IL | Torvastad Idrettslag | 19 | 151 | 1988–2026 / 2012–2023 |
| Stein FIK | IL Stein | 17 | 623 | 1961–2026 / 1965–2023 |
| Torodd IF | IF Torodd | 16 | 84 | 1928–2025 / 1927–2025 |
| Vadsø Turnforening | Vadsø TIF | 15 | 350 | 2011–2025 / 1956–2023 |
| Sandefjord Turn & IF | Sandefjord TIF | 15 | 73 | 1945–2026 / 1935–2016 |
| Torvikbukt IL | Torvikbukt Idrettslag | 11 | 98 | 1987–2025 / 2013–2026 |
| IF Minerva | TIF Minerva | 11 | 93 | 1966–2011 / 1954–1985 |
| Idrettsklubben Grane | IK Grane | 9 | 69 | 1952–2026 / 1931–2012 |
| Jotun IL | IL Jotun | 9 | 69 | 1957–2026 / 1952–1993 |
| IL Nidelv | Nidelv IL | 9 | 62 | 1960–2026 / 1961–2013 |
| IL Sørfjell | Sørfjell IL | 8 | 48 | 1971–2006 / 1971–2025 |
| Stovnerkameratene | IL Stovnerkameratene | 7 | 62 | 1977–2026 / 1974–1990 |
| Yrjar IL | IL Yrjar | 7 | 28 | 1959–2026 / 1936–2001 |
| Skarphedin IL | IL Skarphedin | 7 | 19 | 1978–2026 / 1954–2013 |
| Tvedestrand Turn & IF | Tvedestrand TIF | 6 | 26 | 1966–2026 / 1969–2005 |
| Heimdal IF | Heimdal IL | 5 | 55 | 1958–2006 / 1955–2024 |
| IF Kamp-Vestheim | Kamp/Vestheim IF | 5 | 53 | 1956–2026 / 2018–2026 |
| Gausdal FIK | Gausdal IL | 5 | 52 | 1971–2026 / 1971–1993 |
| Larvik Turn & IF | Larvik FIK | 5 | 44 | 1949–2026 / 1984–2014 |
| IL Ulvungen | Ulvungen IL | 5 | 43 | 1934–2026 / 1996–2025 |
| Mogutten IL | IL Mogutten | 4 | 36 | 1967–2015 / 1969–2009 |
| Leksvik IL | Leksvik Il | 4 | 31 | 1960–2025 / 2013–2025 |
| Velledalen IL | Velledalen Idrettslag | 4 | 7 | 2011–2025 / 2012–2026 |
| Namdalseid | Namdalseid IL | 3 | 37 | 1969–2025 / 1983–2005 |
| Valder IL | IL Valder | 3 | 16 | 1977–2026 / 1977–1999 |
| Varegg IL | IL Varegg | 3 | 12 | 1961–2026 / 1961–2010 |
| Tambarskjelvar IL | IL Tambarskjelvar | 3 | 11 | 1956–2026 / 1954–1994 |
| Fri Kameratene | IL Fri-Kameratene | 3 | 11 | 1975–2012 / 1975–1982 |
| Jerven FIK | FIK Jerven | 3 | 7 | 1961–1991 / 1958–1966 |

---

## B · Friidrettsgruppa som egen enhet

Her skiller navnene seg ved ordet «Friidrett». Det er ikke en skrivefeil, men
et spørsmål om hvordan norsk friidrett skal representeres: er friidrettsgruppa
i et fleridrettslag en egen enhet, eller samme klubb som hovedlaget?

Valget påvirker klubbstatistikk, klubbrekorder og §10 i kravspekken, og bør
avklares med NFIF før noe slås sammen.

| Større post | Mindre post | Felles utøvere | Res. i mindre | År |
|---|---|---:|---:|---|
| Kristiansands IF Friidrett | Kristiansands IF | 61 | 287 | 1927–2026 / 1927–2013 |
| Urædd Friidrett | IF Urædd | 53 | 192 | 1938–2026 / 1935–2013 |
| Stavanger Friidrettsklubb | Stavanger IF Friidrett | 43 | 395 | 2013–2021 / 1942–2020 |
| Raufoss Idrettslag Friidrett | Raufoss IL | 35 | 199 | 1972–2026 / 1970–2011 |
| Tingvoll Idrettslag | Tingvoll Friidrettsklubb | 29 | 788 | 1928–2026 / 1988–2026 |
| Herkules Friidrett | IF Herkules | 29 | 119 | 1982–2026 / 1956–2013 |
| Mosjøen Friidrettsklubb | Mosjøen Idrettslag | 25 | 592 | 1960–2026 / 2019–2026 |
| Kongsvinger IL Friidrett | Kongsvinger IL | 18 | 94 | 1938–2026 / 1930–2012 |
| Veldre Friidrett | Veldre IL | 14 | 64 | 1960–2025 / 1960–2005 |
| Førde IL Friidrett | Førde IL | 12 | 69 | 1939–2026 / 1957–2010 |
| Bryne Friidrettsklubb | Bryne IL | 11 | 135 | 1968–2026 / 1960–2020 |
| Sola Friidrettsklubb | Sola IL | 11 | 58 | 1974–2026 / 1968–2005 |
| Snøgg Friidrett | SK Snøgg | 10 | 45 | 1932–2026 / 1948–2013 |
| Ask Friidrett | Ask IL | 8 | 37 | 1953–2026 / 1958–1999 |
| Løten Friidrett | Løten IL | 7 | 52 | 1966–2026 / 1967–2010 |
| Mosjøen Friidrettsklubb | Mosjøen IL | 7 | 30 | 1960–2026 / 1959–1984 |
| Storsteinnes IL Friidrett | Storsteinnes IL | 7 | 15 | 1981–2024 / 1981–1989 |
| Sunndal IL Friidrett | Sunndal IL | 6 | 30 | 1966–2026 / 1967–1999 |
| Verdal Friidrettsklubb | Verdal IL | 6 | 28 | 1983–2026 / 1926–2021 |
| Horten Friidrettsklubb | Horten IF | 5 | 14 | 1977–2026 / 1974–1999 |
| Austevoll IK Friidrett | Austevoll IK | 5 | 10 | 1990–2026 / 1990–2000 |
| IF Minerva | Minerva Friidrett | 4 | 168 | 1966–2011 / 1995–2014 |
| Kragerø IF Friidrett | Kragerø IF | 3 | 20 | 1972–2026 / 1955–1985 |
| Trondheim Friidrett | Trondheim FIK | 3 | 7 | 1992–2026 / 2000–2011 |
| Rena IL Friidrett | Rena IL | 2 | 26 | 1978–2026 / 1973–1993 |
| Sortland Friidrettsklubb | Sortland IL | 2 | 9 | 1967–2026 / 1961–1976 |
| Hamar IL | Hamar Friidrett | 2 | 2 | 1927–2026 / 2016–2018 |
| Lånke IL Friidrett | Lånke IL | 1 | 8 | 2010–2026 / 1998–2013 |
| Skrautvål IL friidrett | Skrautvål IL | 1 | 8 | 1994–2026 / 1993–2006 |
| Sandnes IL | Sandnes Atletklubb | 1 | 6 | 1948–2026 / 1979–1979 |
| IL Driv Friidrett | IL Driv | 1 | 6 | 1965–2026 / 1965–1995 |
| Gjerstad IL Friidrett | Gjerstad IL | 1 | 4 | 1949–2026 / 1950–1976 |
| Ålesund Friidrettsklubb | Ålesund IL | 1 | 2 | 1988–2026 / 1981–2014 |
| Salangen Friidrett | Salangen IL | 1 | 2 | 2011–2026 / 2007–2007 |
| Snøgg Friidrett | Snøgg | 1 | 1 | 1932–2026 / 2007–2007 |
| Hinna IL | Hinna friidrett | 1 | 1 | 1931–2026 / 1980–1980 |
| Sola Friidrettsklubb | Sola Friidrett | 1 | 1 | 1974–2026 / 2011–2011 |
| Drøbak-Frogn IL Friidrett | IL Drøbak-Frogn | 1 | 1 | 1947–2026 / 1963–1963 |
| Ballangen Friidrett | Ballangen IL | 1 | 1 | 1990–2024 / 1990–1990 |
| Stavanger Friidrettsklubb | Stavanger IF | 0 | 51 | 2013–2021 / 1934–2020 |
| Nordre Land friidrett | Nordre Land IL | 0 | 15 | 1969–2026 / 1966–2003 |
| Kråkstad IL - Friidrett | Kråkstad IL | 0 | 6 | 2012–2022 / 1969–1983 |
| Fet Friidrettsklubb | Fet IL | 0 | 3 | 1971–2026 / 1934–1973 |
| Gulset IF Friidrett | Gulset IF | 0 | 2 | 2011–2021 / 2021–2021 |
| Eik IF | Eik Friidrett | 0 | 2 | 1976–1977 / 2018–2018 |
| Kongsvinger IL Friidrett | Kongsvinger IF | 0 | 1 | 1938–2026 / 1962–1962 |
| Vindbjart Friidrett | IL Vindbjart | 0 | 1 | 1965–2026 / 1993–1993 |
| Stavanger Friidrettsklubb | Stavanger IL | 0 | 1 | 2013–2021 / 2019–2019 |
| Gulset IF Friidrett | Gulset IL | 0 | 1 | 2011–2021 / 1984–1984 |
| Korgen IL - Friidrett | Korgen IL | 0 | 1 | 2012–2021 / 1999–1999 |
| Molde IL | Molde Atletklubb | 0 | 1 | 2020–2020 / 2026–2026 |
| Vikersund IF | Vikersund Friidrett | 0 | 1 | 1955–1971 / 2019–2019 |

---

## C · Svakt grunnlag

Under tre felles utøvere. Navnene ligner, men dataene gir ikke belegg for at
det er samme klubb. Flere av dem er trolig ekte naboklubber.

| Større post | Mindre post | Felles utøvere | Res. i mindre | År |
|---|---|---:|---:|---|
| Vadsø Turnforening | Vadsø Atletklubb | 2 | 128 | 2011–2025 / 2016–2019 |
| Ivrig | IL Ivrig | 2 | 18 | 1971–2026 / 1970–1999 |
| Sokna IF | Sokna IL | 2 | 12 | 1970–1983 / 1972–2023 |
| IL Bjarg | Bjarg IL | 2 | 9 | 1980–2026 / 2006–2008 |
| Hamar IL | Hamar Skiklubb | 2 | 8 | 1927–2026 / 2012–2020 |
| Imås IL | IL Imås | 2 | 6 | 1976–2017 / 1966–1984 |
| Stein FIK | FIK Stein | 2 | 4 | 1961–2026 / 2000–2010 |
| Lunner IL | Lunner IF | 2 | 4 | 1952–1982 / 1975–1980 |
| IK Junkeren | IL Junkeren | 2 | 4 | 1978–2024 / 1978–1980 |
| Flekkefjord IF | Flekkefjord IL | 2 | 3 | 1969–2024 / 1990–1994 |
| Ullensaker-Sørum IL | Ullensaker-Sørum FIK | 2 | 3 | 1987–1993 / 1990–1991 |
| FIK Orion | Orion FIK | 2 | 2 | 1986–2026 / 1994–1996 |
| Vollan Idrettsklubb | Vollan IK | 2 | 2 | 2007–2026 / 1985–2005 |
| Oslo Politis IL | Oslo Politis Idrettslag | 2 | 2 | 1930–2026 / 2012–2012 |
| Ørnar | Idrettslaget Ørnar | 2 | 2 | 1974–2026 / 2016–2023 |
| Gol IL | Gol Idrettslag | 2 | 2 | 1974–2020 / 2019–2020 |
| Oslo-Studentenes IL | Oslo-Studentenes IK | 1 | 19 | 1950–1992 / 1992–2011 |
| Eidsvold Turnforening | Eidsvold IF | 1 | 14 | 1971–2025 / 1958–2022 |
| Mjøndalen IF | Mjøndalen IL | 1 | 14 | 1963–1985 / 1964–2022 |
| Trysilgutten | IL Trysilgutten | 1 | 13 | 1955–2024 / 1959–1986 |
| Idrettslaget Skade | IL Skade | 1 | 13 | 1978–2026 / 1966–1998 |
| Svint IL | IL Svint | 1 | 12 | 1982–2024 / 1954–1984 |
| Idrettslaget Ilar | IL Ilar | 1 | 9 | 2006–2026 / 2002–2008 |
| Halden IL | Halden Skiklubb | 1 | 8 | 1931–2026 / 2014–2024 |
| IL Molde-Olymp | Molde-Olymp | 1 | 8 | 1958–2026 / 2007–2013 |
*Viser 25 av 123. Resten i CSV-en.*
