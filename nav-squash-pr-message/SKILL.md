---
name: nav-squash-pr-message
disable-model-invocation: true
description: |
  NAV-spesifikk squash merge commit-melding med Jira-nummer krav.
  Triggers: "/nav-squash-pr-message"
  Use when: Generating squash commit messages with NAV conventions (Jira prefix required).
---

# Squash PR Message

> Skript-stier under er relative til denne skill-mappen.

1. Run `gh pr view --json title,number,body`

2. Valider PR-tittel med scriptet:
   ```bash
   python scripts/validate_pr_title.py "<title>" <pr_number>
   ```
   - Må starte med Jira-nummer (`1234`, minst 3 sifre) eller en grunnkode: `TEK` (kun tekniske endringer), `DOK` (dokumentasjon), `VAKT` eller `PRODFIX`. En avhengighetskode kan stå foran (`DAPI 7990 Beskrivelse`)
   - **`NOJIRA` brukes ikke.** Mangler Jira-sak, må grunnen stå i tittelen. Anbefalt: `TEK` eller `DOK`
   - Tilleggskoder: `TOGGLE`, `G4P`, og avhengighetskoder `DAPI`/`DWEB`/`DB`/`DDOKGEN` (avhenger av endring i et annet repo). **`G4P` og `TOGGLE` står aldri alene, og kommer etter Jira-nummer eller grunnkode.** Avhengighetskoder er ikke en grunn i seg selv.
   - Kan kombineres: `1234 TOGGLE DWEB Beskrivelse`, `1234 G4P Beskrivelse` eller `TEK G4P Beskrivelse`
   - Nye grunnkoder legges i `REASON_CODES` i scriptet
   - Totalt maks 72 tegn (inkludert ` (#number)` som legges til)
   - Vis feil/advarsler fra scriptet til brukeren

3. Hvis tittel er for lang (over 72 tegn):
   - Generer 2-3 kortere alternativer som beholder essensen
   - Bruk **AskUserQuestion** med multiple choice:
     - Header: "Tittel for lang"
     - Question: "Tittelen er X tegn (maks 72). Velg en kortere versjon:"
     - Options: De genererte alternativene
   - Brukeren kan også velge "Other" for å skrive egen

4. Hvis tittelen mangler Jira-nummer eller grunnkode (også når den starter med `NOJIRA`, eller med `G4P`/`TOGGLE` alene):
   - Bruk **AskUserQuestion** med multiple choice:
     - Header: "Jira-nummer"
     - Question: "Tittelen mangler Jira-nummer. Hva skal brukes?"
     - Options:
       - "Angi nummer" (lar bruker skrive inn)
       - "TEK (Anbefalt)" (kun tekniske endringer, trenger ikke Jira)
       - "DOK (Anbefalt)" (dokumentasjon uten Jira-sak)
       - "VAKT" (vaktarbeid uten Jira-sak)
     - Tilby aldri `NOJIRA`. `PRODFIX` (rask fiks av prodfeil) og andre grunnkoder oppgis via "Other".
   - Behold eventuell `G4P`/`TOGGLE` etter den nye koden (`TEK G4P Beskrivelse`)
   - Valider på nytt etter brukerens valg
   - Står `G4P`/`TOGGLE` foran Jira-nummer eller grunnkode (`G4P TEK Rydd`, `G4P 1234 …`), flytt koden bak ankeret uten å spørre (`TEK G4P Rydd`), og valider på nytt

5. Create commit message following git best practices:
   - **Tittel**: `1234 [KODER] Beskrivelse (#number)` - maks 72 tegn totalt
   - Blank linje etter tittel
   - **Body** (VIKTIG - begge deler MÅ være med):
     - Første avsnitt: **Hva** som er gjort (kort oppsummering)
     - Blank linje
     - Andre avsnitt: **Hvorfor** - bakgrunn/motivasjon (ALLTID PÅKREVD!)
     - Valgfritt: Bullet points med detaljer til slutt
   - Plain text (ingen markdown)
   - Bruk norske tegn (øæå) — IKKE erstatt med oe/ae/aa
   - Ikke wrap linjer i body — la hvert avsnitt stå på én linje
   - Imperativ form: "Legg til", "Fiks", "Oppdater" (ikke "Legger til")

6. Copy to clipboard with `pbcopy`

## Eksempel på ferdig commit-melding

```
1234 Legg til validering av fødselsnummer (#456)

Legger til validering av fødselsnummer i skjema for ny søknad.

Brukere kunne tidligere sende inn ugyldige fødselsnummer som
førte til feil i backend-prosessering.
```

## Eksempel med flere koder og detaljer

```
7553 TOGGLE A008 CDM 4.4: Legg til formål og SED-versjon (#811)

Legger til støtte for CDM 4.4-endringer i A008 SED med nytt formål-felt og oppdatert SED-versjon bak feature toggle.

CDM 4.4-spesifikasjonen krever at A008 har et formål-felt for å skille mellom "endringsmelding" og "arbeid_flere_land". Styres av toggle for kontrollert utrulling.

Endringer:
- Nytt formål-felt i MedlemskapA008
- SED-versjon 4.4 når toggle er aktivert
- Nytt felt a008Formaal i SedDataDto
```