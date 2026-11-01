# Referansekontroll før innsending til PSE

01.11.2026. Grunnlag: `../RefStag.pdf` (sammendragene av alle siterte arbeider), Enoksen (2011) i fulltekst (`../../DropEnoksen.pdf`), JSAMS-artikkelens resultatdel (`DrPhilos/utvikling/JSAMS-D-26-00955.pdf`) og RAE-manuset (`../../RAE/revisjon3/discussion.tex`). Hver setning i PSE-versjonen som siterer en kilde, er lest mot kilden. Rettelsene er lagt inn i `bygg_pse.py` og gjelder PSE-versjonen; fire av dem gjelder setninger som også står i det fryste SMO-manuset (merket *SMO*).

| Referanse | Hva manuset sier | Kilden | Vurdering og tiltak |
|---|---|---|---|
| Anderson mfl. 1983 | Landmark-betinging gjøres eksplisitt | Responder-/non-responder-skjevhet; to gyldige metoder, landmark er én | Dekket |
| Bandura 1977 | Mestringserfaring er den viktigste kilden til mestringsforventning | Fire kilder; «performance accomplishments» er den mest innflytelsesrike; suksess hever, gjentatte nederlag senker; forventningen styrer innsats og utholdenhet | **Rettet.** 1977-terminologien (performance accomplishments) brukes, og «seeing oneself improve» er gjort til en avledning, ikke et sitat |
| Barth mfl. 2022, Güllich mfl. 2025, Kearney & Hayes 2018 | Juniorprestasjon predikerer seniorprestasjon dårlig | Kearney: 9–13 % av topp-20 senior var topp-20 U13; Barth: motsatte prediktorer; Güllich: to atskilte populasjoner | Dekket |
| Crane & Temple 2015 | (a) «dominant prospective predictor»; (b) «qualitative work»; (c) «qualitative literature» om pubertet; (d) «normative sampling» | Systematisk oversikt, mest tverrsnitt og kvantitativt; fem områder: glede, opplevd kompetanse, sosialt press, konkurrerende prioriteringer, fysiske faktorer (modning, skade) | **Rettet alle fire.** (a) «most consistently reported reason» (Crane) skilt fra «main prospective predictor» (Van Yperen); (b) ikke lenger kalt kvalitativ, viser til opplevd kompetanse; (c) *SMO* «competing priorities and physical factors around puberty documented in the dropout literature»; (d) *SMO* «competing priorities or a change of activity rather than failure» |
| Enoksen 2011 | Skade var vanligste oppgitte årsak i den eneste langtidsoppfølgingen i norsk friidrett | Fulltekst tabell 3: skade 24,3 %, skole 21,4 %, motivasjon 20,7 %; stagnasjon i prestasjon nevnt som viktig grunn i intervjuene | **Dekket, og utvidet.** Ny setning: stagnasjon i prestasjon var selv blant årsakene utøverne oppga |
| Espedalen & Seippel 2024 | Kostnader og sosial bakgrunn former hvem som slutter | Studerer hvordan *oppgitte grunner* varierer med SØS, etnisitet og kjønn blant dem som har sluttet | **Rettet** til «shape the reasons young people give for leaving» |
| Filó 2026 | Deseleksjon i talentsystemer | Strukturreform, klubbskifte og lagnivå predikerer frafall etter U20; deseleksjon måles ikke | **Rettet** til «much of the attrition at the youth-to-senior transition is structural rather than individual» |
| Fraser-Thomas mfl. 2008 | Kvalitativt arbeid om opplevd kompetanse og glede | Retrospektive intervjuer, 25 + 25 svømmere: frafallerne var yngst i treningsgruppen, nådde milepæler tidligere, mindre én-til-én-trening | **Rettet.** Funnene gjengis slik de står (yngst i gruppen, tidlige milepæler); det er dessuten relevant for H2 |
| Güllich & Barth 2026 | Stor del av turnover er systemets egen deseleksjon | 36 % årlig turnover, hyppig seleksjon, deseleksjon og erstatning | Dekket |
| Guttormsen 2026, JSAMS | Topp-100 domineres av sammensetningsutskifting; de beste ved én alder er stort sett andre enn ved neste | Årlig turnover 33–59 %; platået er et artefakt av sammensetningen; sier ikke noe om seleksjon | **Presisert** med turnovertallene; «early rankings mislead» endret til «understate later development» (*SMO*) |
| Guttormsen under vurdering, IJSSC | 12 %/23 % volumfall, OR 2,04, volum > nivå, styringsrammer | Kontrollert mot IJSSC-manuset i dataauditen 30.10 | Dekket |
| Guttormsen in press, SMO | Skjevheten etablert ved 10 og stabil til 25; foreslo testen | Ordrett i revisjon 3: «fully established by age 10 and remain stable through age 25»; testsetningen står ordrett | Dekket |
| Harter 1978 | Vellykkede mestringsforsøk gir positiv affekt som motiverer nye forsøk | Utvidelse av Whites modell: utfordring og glede, virkning av suksess og nederlag, opplevd kompetanse som korrelat | Dekket |
| Hsieh mfl. 1998 | Styrkeberegning med variansinflasjon | Enkel formel pluss VIF for multippel logistisk regresjon | Dekket |
| Larson mfl. 2019 | Tidlig spesialisering predikerte ikke frafall | 137 svømmere 12–13 år; ES-markører ikke positivt relatert til utbrenthet eller frafall | Dekket |
| Nicholls 1984 | Oppgave- mot ego-oppfatning av dyktighet | Ordrett i sammendraget | Dekket |
| Ryan & Deci 2000 | Kompetanse som grunnleggende behov | Tre medfødte behov: kompetanse, autonomi, tilhørighet | Dekket |
| VanderWeele & Ding 2017 | E-verdi; kvadratrot-omregning ved vanlig utfall | E-verdien definert på RR-skala; sqrt-tilnærmingen anbefales i samme artikkel | Dekket |
| Van Yperen mfl. 2022 | Glede er den viktigste prospektive prediktoren | «enjoyment was the main predictor», prospektiv, 1 762 spillere | Dekket. Bib-nøkkelen heter 2021, men siteres som 2022 (publiseringsår), riktig |
| von Elm mfl. 2007 | STROBE | — | Dekket |
| NFIF 2014 | Tyrvingtabellen | — | Dekket |

## Det fryste SMO-manuset

Setningene merket *SMO* ble rettet også i `../manus/main.tex` 01.11.2026 (Atles beslutning), sammen med turnovertallene fra JSAMS-artikkelen; `main.pdf` er bygd på nytt og `audit/kontroll_tall.py` kjørt.
