---
name: kommentar-standard
description: |
  Rydd kode for unødvendige kommentarer og intern sjargong, målt mot en senior-utvikler som leser
  navn, typer, annotasjoner og SQL selv. Fjerner review-historikk fra kildekoden (→ commit-melding),
  dupliserte forklaringer, Jira-referanser i prosa og plan-dokumenter i src/; skriver om KDoc,
  Swagger, feilmeldinger, loggmeldinger, testnavn og API-feltnavn til klarspråk uten udefinerte
  interne termer. Verifiserer mekanisk at koden er uendret (strippet diff) og at sjargongen er borte.
  Triggers: "rydd i kommentarene", "for mange kommentarer", "reduser kommentarer", "klarspråk",
  "selvdokumenterende", "kommentar-standard", "review sier det er for mye prosa/sjargong",
  "gjør PR-en lettere å lese", "comment cleanup", "too many comments", "plain language".
  Bruk denne også uoppfordret når en PR har vært gjennom flere review-runder og kommentarene har
  vokst, når en reviewer klager på uforståelige termer i KDoc/Swagger, eller før en PR med mye
  prosa sendes til menneskelig review — selv om brukeren bare sier «gjør dette enklere å forstå».
---

# Kommentar-standard

Én målestokk styrer alt: **leseren er en senior utvikler som ser navn, typer, annotasjoner og SQL
selv, og som ikke var med i utviklingsløpet.** En kommentar skal fortelle noe koden ikke kan, i ord
den leseren forstår uten kontekst. Alt annet er støy som skjuler det som faktisk er viktig.

Målt i praksis (melosys-api #3469, 2026-08-31): en PR som hadde vært gjennom to review-runder
hadde ~600 kommentarlinjer på ~1700 kodelinjer. Etter denne standarden: ~107. Koden var identisk.
Reviewer-tilbakemeldingen som utløste det: *«MEL-referansene bør vanligvis ikke være i koden.
Basestien er opplagt fra koden. Beskrivelsen er i en sjargong som er umulig å forstå ved øyekast.»*

## Arbeidsflyt

1. **Kartlegg.** Kjør `scripts/kommentar-sjekk.sh` på de berørte filene for en baseline: antall
   kommentarlinjer per fil og treff på sjargong-/historikk-lista. Les så alle kommentarene i ett
   strekk (`grep -n '^\s*//\|^\s*/\*\*\|^\s*\*' <fil>`) — ikke fil for fil mens du redigerer.
   Å se dem samlet er det som avslører dupliseringen.
2. **Sorter hver kommentar** i én av tre bunker (se «Hva ryker», «Hva blir igjen» under):
   *fjern*, *flytt til commit-melding*, *behold og stram inn*.
3. **Klarspråk-runde** på alt som blir igjen *og* på alt leservendt: KDoc, Swagger/OpenAPI-tekster,
   feilmeldinger, loggmeldinger, testnavn, lokale variabelnavn — og JSON-feltnavn hvis API-et ennå
   ikke har klienter (nye endepunkter i samme PR). Dette steget **endrer kode med vilje** (strenger
   og identifikatorer), og det er ikke en grunn til å la sjargongen stå: en operatør leser
   feilmeldingen uten å se KDoc-en. Gjør det som egen commit etter kommentar-rundene, slik at
   «kode identisk»-beviset gjelder de første commitene og denne får sin egen test-kjøring.
   Hopp bare over når feltet faktisk har klienter — og si det da eksplisitt i rapporten.
4. **Verifiser mekanisk**, aldri med øyemål:
   - `scripts/kommentar-sjekk.sh` igjen: for kommentar-commitene skal koden være **identisk** med
     strippet diff; for klarspråk-commiten skal den strippede diffen inneholde *kun* strenger og
     renames (les den og si det). Sjargong-grep skal være tomt; tellingen skal ha gått ned.
   - Kompiler. Endret du en feilmelding eller et feltnavn, grep test-treet etter gamle tekster
     (`containsString`-pins) og kjør testene — mot *fersk* kode (i Maven-multimodul:
     `mvn -pl <modul> install` før IT-en, ellers tester du en gammel jar fra `.m2`).
5. **Commit-meldingen bærer historikken** du fjernet: hvilken review fant hva, hvilke runder som
   feilet og hvorfor, hva som bevisst *ikke* er testet. Det er der den hører hjemme — git blame
   finner den, kildekoden slipper den. Oppgi tellingen før→etter i meldingen.

Gjør gjerne runden i flere commits (historikk-flytting → duplikat-fjerning → klarspråk → rename)
— hver er lett å reviewe alene, og en reviewer kan stoppe deg underveis uten å miste resten.

## Hva ryker

Fjern uten å nøle når kommentaren …

- **gjentar navn, type, annotasjon eller SQL** rett under. `/** Read-only preview */` over
  `@Transactional(readOnly = true) fun forhåndsvis` sier ingenting. «Nyest først» over en
  `ORDER BY … DESC`. «Tom liste = alle» over `if (liste.isEmpty()) ALLE_SQL`. Enum-verdi-docs
  på `EKTE` / `PATCHET_URØRT` / `PATCHET_ENDRET`.
- **peker på noe leseren ser**: «Se [X] for detaljer» når X injiseres i konstruktøren fem linjer
  ned. «Basestien er …» over `@RequestMapping`. Reviewer-sitat: *«Man ser jo raskt fra koden.»*
- **dupliserer en annen kilde** som leseren også får: felt-KDoc på DTO-en, Swagger-beskrivelsen,
  selens egen feilmelding, testnavnet. Én kilde per faktum — velg den nærmest bruken.
- **er review-arkeologi**: «bevisst etter review 20.08», «(Copilot-review 25.08)», «tidligere
  ble den brukt som …», «det var nettopp dette som gjorde tre runder til nye feil», «slik den ble
  før». Alt dette → commit-meldingen. Regressjonstester trenger ikke fortelle at de er
  regressjonstester; de skal si hvilken invariant de pinner.
- **er Jira/saksnummer i prosa**. Behold *ett* anker (klasse-KDoc på hovedklassen) og verdier som
  er datakontrakt (en markørstreng som allerede står i prod-rader). Alt annet ut.
- **gjenforteller assertionen under** i en test: `// kontrollen skal slå ut` over
  `.value(true)`. Seksjons-etiketter («Glemt scope skal ikke slette begge») i en test som allerede
  har et beskrivende navn.
- **er et plan-dokument i `src/`**. 300 linjer markdown ved siden av koden er review-last;
  fullversjonen hører hjemme i wiki/PR-beskrivelse. Fjern nummerering i koden som bare gir mening
  med dokumentet (Q4a/Q4b-stil).

## Hva blir igjen

Behold — og stram til én–tre linjer — når kommentaren forteller …

- **et rekkefølgekrav koden ikke håndhever**: «etter maks-kontrollen, så den mer presise
  meldingen vinner», «må måles før INSERT-en — etterpå kan før-bildet ikke gjenskapes».
- **en leverandør-/rammeverk-særegenhet**: Oracle `= NULL` er UNKNOWN; `NULLS LAST` i DESC;
  ORA-01795 og IN-lister; `@CreatedBy` settes kun ved insert mens `@LastModifiedBy` flyttes av
  enhver skriving; READ COMMITTED og re-evaluering.
- **hvorfor ikke det opplagte alternativet**: `>=` og ikke `>`; native SQL i stedet for JPA;
  `NULL` avvist fordi en `when` nedstrøms mangler null-gren.
- **en datakontrakt**: «verdien står i rader som allerede er satt inn i prod — kan ikke endres».
- **en fixture-invariant i en test** som gjør at testen ikke er vakuøs: «2024-raden må være nyest
  av de tre, ellers skiller ikke testen riktig modell fra feil», «MEL-8888 må ikke være prefiks av
  MEL-962 — containsString under må ikke kunne treffe saksnummeret».
- **arv fra tidligere fikser** som forklarer et magisk tall: «+42 dager følger Flyway V7.6_04».

Én lang KDoc per fil er greit når den forklarer selve mekanismen (hvorfor en tilnærmet dato lyver
systematisk oppover, hva `false` *ikke* garanterer). Alt annet skal ned til én–tre linjer.

## Klarspråk

Intern sjargong oppstår i utviklingsløpet og er usynlig for den som skrev den. Test hver term:
*ville en ny utvikler på teamet forstå den ved øyekast, uten å ha lest resten av fila?* Hvis ikke,
bytt — konsekvent, i alle kanaler, med samme erstatning overalt. Eksempler fra én runde:

| Sjargong | Klarspråk |
|---|---|
| sele / sikkerhetssele | kontroll |
| kaprer / tar nyeste-plassen | blir nyeste (i saken) |
| kvittere ut / kvittering | godkjenne / godkjenning |
| proxy(-dato) | tilnærmet dato / tilnærming |
| frikjenn | ingen garanti for at … |
| myntkast | vilkårlig utfall |

Kanalene, i prioritert rekkefølge — de første leses av flest uten kontekst:

1. **Swagger/OpenAPI-beskrivelser.** Start med *hva problemet er* i én setning, så hva
   endepunktet gjør, så feltene. Ingen udefinerte termer; ingen «VIKTIG:»-blokker; ikke gjenta
   felt-KDoc. En beskrivelse som bare gir mening «i konteksten modellen var i» er ikke ferdig.
2. **Feilmeldinger og loggmeldinger.** Operatøren leser dem uten koden. Si hva som skjedde og
   hva de skal gjøre.
3. **Testnavn.** De er dokumentasjon av oppførsel; `godkjenning av én sak blokkerer ikke de
   øvrige` slår `én kapret sak blokkerer ikke når den kvitteres ut`.
4. **API-feltnavn.** Gjør det bare når API-et ikke har klienter ennå (nye endepunkter i samme
   PR). Velg navn som sier konsekvensen for leseren: `trengerGodkjenning` slår
   `patchenVinnerNyeste`. Behold felt som allerede er klarspråk (`tillatSorteringsendring`).
5. **KDoc og inline-kommentarer.** Samme ordliste som resten.
6. **Lokale variabler** (`kaprer` → `blirNyeste`) — billig og trygt.

Termer som *er* API-kontrakt (`skarp`, en markørverdi) beholdes, men forklares der de brukes.

## Fallgruver

- **Strippet diff er beviset, ikke tsc/kompilering.** En hel-fil-omskriving av kommentarer kan
  flytte en linje kode uten at noe kompilerer annerledes. Skriptet sammenligner kode med alle
  kommentarer fjernet — kjør det, og lim resultatet inn i svaret.
- **Les hver kommentar mot koden den står ved — mange er stale.** Etter flere fiksrunder sier
  kommentarer ting som ikke lenger stemmer («delt av X og Y» når Y ikke bruker den; «alle tre» om
  to saker; en Swagger-tekst som nevner et felt som ikke finnes i responsen). Det er funn, ikke
  støy: rett eller fjern, og list dem i rapporten så reviewer ser at innholdet er sjekket.
- **Ikke refaktorer «mens du er der».** Å fjerne et ubrukt felt, forenkle en SQL eller slå sammen
  to metoder er kodeendring med egen risiko og hører i egen PR. Kommentar-runden skal kunne
  godkjennes på «strippet diff identisk» alene.
- **Døde referanser** når et dokument slettes eller et felt renames: grep etter navnet i
  kommentarer og Swagger etterpå (`fiksplanen`, gamle feltnavn).
- **Eldre tester pinner gamle meldinger.** Rename i en feilmelding = en `containsString` et sted.
  Kjør testene, ikke bare kompiler.
- **Ikke gjør det til én kjempe-commit.** Reviewer skal kunne godkjenne «historikk ut» uten å
  måtte mene noe om «feltnavn renamet».

## Rapportformat til brukeren

Kort, med tall — brukeren skal kunne lime det inn i PR-en:

```
Kommentarlinjer: <fil>: N → M (per fil)
Kode identisk (strippet diff): ja / nei — <hva som er endret hvis nei>
Fjernet: <kategorier, 1 linje hver>
Beholdt: <kategorier, 1 linje>
Klarspråk: <sjargong → erstatning>, <kanaler berørt>
Verifisert: <kompilert / tester kjørt, mot fersk jar>
Flyttet til commit-melding: <hva>
```
