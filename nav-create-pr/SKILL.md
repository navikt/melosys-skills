---
name: nav-create-pr
disable-model-invocation: true
description: |
  NAV-spesifikk PR med Jira-nummer krav og norsk format.
  Triggers: "/nav-pr", "/nav-create-pr", "lag pr", "opprett pr"
  Use when: Creating PRs with NAV conventions (Jira prefix required, Norwegian, Jira links).
---

# Create Pull Request

> Skript-stier under er relative til denne skill-mappen.

## Workflow

1. **Samle informasjon**
   ```bash
   # Kjør parallelt:
   git status
   git diff --stat
   git log origin/master..HEAD --oneline
   git log origin/master..HEAD --pretty=format:"%s%n%n%b%n---"
   git log @{u}..HEAD --oneline 2>/dev/null  # Sjekk upushede commits
   ```

2. **Sjekk at alt er pushet**
   - Sjekk om branchen har en upstream: `git rev-parse --abbrev-ref @{u} 2>/dev/null`
   - Sjekk om det finnes commits som ikke er pushet: `git log @{u}..HEAD --oneline`
   - Hvis branchen ikke har upstream, eller det finnes upushede commits:
     Bruk AskUserQuestion:
     - Header: "Push først?"
     - Question: "Det finnes upushede commits på branchen. Skal jeg pushe før PR opprettes?"
     - Options: "Ja, push og opprett PR" / "Avbryt"
   - Ved "Ja": kjør `git push -u origin HEAD` og fortsett
   - Ved "Avbryt": stopp uten å opprette PR

3. **Sjekk om endringene er bak feature toggle**
   - Søk i diffen og commit-meldinger etter toggle-indikatorer:
     ```bash
     git diff origin/master..HEAD | grep -iE '(toggle|unleash|feature.?flag|isEnabled|erAktivert)' | head -20
     git log origin/master..HEAD --oneline --grep='toggle' -i
     ```
   - Hvis toggle-referanser finnes: bruk AskUserQuestion:
     - Header: "TOGGLE?"
     - Question: "Endringene ser ut til å være bak feature toggle. Skal tittelen ha TOGGLE-prefix? (f.eks. '7911 TOGGLE Beskrivelse')"
     - Options: "Ja, legg til TOGGLE" / "Nei, uten TOGGLE"
   - Hvis bruker velger ja: legg til `TOGGLE` etter Jira-nummeret i tittelen

4. **Valider PR-tittel**:
   ```bash
   python scripts/validate_pr_title.py "<title>"
   ```
   - Samme regler som for squash: Jira-nummer først, maks 72 tegn
   - Format med toggle: `1234 TOGGLE Beskrivelse`
   - Format uten toggle: `1234 Beskrivelse`
   - Ved mangler/feil: bruk AskUserQuestion

5. **Generer PR-beskrivelse** i markdown:

   ```markdown
   Kort beskrivelse av hva PR-en gjør (1-3 setninger).

   Hvorfor denne endringen er nødvendig. Kontekst og motivasjon
   som forklarer bakgrunnen for endringen.
   [MELOSYS-1234](https://jira.adeo.no/browse/MELOSYS-1234)

   - Hovedendring 1
   - Hovedendring 2
   - ...

   ## Testing
   - [ ] Enhetstester
   - [ ] Manuell testing lokalt
   - [ ] E2E-tester (hvis relevant)
   ```

   `## Notater` kun hvis nødvendig (avhengigheter, spesielle hensyn, etc.)

   **Jira-lenke**: Legg til etter bakgrunn-teksten (kun hvis Jira-nummer, ikke ved NOJIRA).
   Hvis bakgrunnen er uklar fra koden, spør bruker om Jira-teksten med AskUserQuestion.

6. **Vis forslag og vent på godkjenning**
   Vis tittel og body i markdown-format. Bruk AskUserQuestion:
   - Header: "Opprett PR?"
   - Question: "Er dette OK?"
   - Options: "Ja, opprett PR" / "Nei, juster"

7. **Opprett PR** (kun etter godkjenning)
   ```bash
   gh pr create --title "<tittel>" --body "$(cat <<'EOF'
   <markdown body>
   EOF
   )"
   ```

8. **Vis resultat** - inkluder PR-URL i svaret

## Retningslinjer

### Tittel
- Følg samme format som squash-pr-message: `1234 Beskrivelse`
- Med toggle: `1234 TOGGLE Beskrivelse`
- Maks 72 tegn
- Imperativ form: "Legg til", "Fiks", "Oppdater"

### Beskrivelse
Rekkefølge:
1. **Sammendrag**: Kort beskrivelse (1-3 setninger)
2. **Bakgrunn**: Forklaring av HVORFOR + Jira-lenke på slutten (kun ved Jira-nummer)
3. **Endringer**: Kun overordnede hovedpunkter (2-4 bullets, maks 5). Ikke detaljer - det ser reviewer i diffen.
4. `## Testing` alltid, `## Notater` kun hvis nødvendig

- Hvis bakgrunn er uklar fra commits/kode: spør bruker om Jira-teksten
- Inkluder screenshots ved GUI-endringer (be bruker om disse)

### Tilpasning
- For små endringer: minimal beskrivelse er OK
- For store endringer: vær grundig med bakgrunn og testing
- Spør bruker hvis noe er uklart

## Eksempel

**Tittel:** `7553 Legg til CDM 4.4-støtte for A008`

**Body:**
```markdown
Legger til støtte for CDM 4.4-endringer i A008 SED med nytt formål-felt.

CDM 4.4-spesifikasjonen krever at A008 har et formål-felt for å skille
mellom "endringsmelding" og "arbeid_flere_land". Implementert bak
feature toggle for kontrollert utrulling.
[MELOSYS-7553](https://jira.adeo.no/browse/MELOSYS-7553)

- Nytt `formaal`-felt i MedlemskapA008
- SED-versjon 4.4 ved aktivert toggle
- Oppdatert SedDataDto med `a008Formaal`

### Testing
- [x] Enhetstester for ny mapping
- [x] Manuell testing mot mock
- [ ] E2E-test for A008-flyt

### Notater
Avhenger av at `MELOSYS_CDM_4_4` toggle er aktivert i Unleash.
```
