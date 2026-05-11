---
name: nav-commit
disable-model-invocation: true
description: |
  NAV-spesifikk commit med norsk format og valgfritt Jira-nummer.
  Triggers: "/nav-commit", "nav commit", "lag commit", "committ endringene"
  Use when: User wants to commit with NAV conventions (Norwegian, optional Jira number).
---

# Commit

> Skript-stier under er relative til denne skill-mappen.

## Workflow

1. **Sjekk branch**
   ```bash
   git branch --show-current
   ```
   Hvis `master` eller `main`:
   - Analyser endringene og foreslå et branch-navn (f.eks. `feature/legg-til-validering`)
   - Bruk AskUserQuestion:
     - Header: "Branch"
     - Question: "Du er på master/main. Vil du lage branch `<foreslått-navn>`?"
     - Options: "Ja, lag branch" / "Nei, commit på master/main"
   - Hvis ja: `git checkout -b <branch-navn>`

2. **Samle informasjon**
   ```bash
   # Kjør parallelt:
   git status
   git diff --staged
   git diff  # unstaged endringer
   ```

3. **Valider commit-tittel**:
   ```bash
   python scripts/validate_commit_title.py "<title>"
   ```
   - Maks 72 tegn (ingen krav om Jira-nummer)

4. **Generer commit-melding** (plain text, IKKE markdown, ikke wrap linjer):
   ```
   Kort beskrivelse av endringen

   Hva som er gjort i denne commiten. Kort oppsummering av endringene.

   Hvorfor denne endringen er nødvendig. Bakgrunn og motivasjon for endringen.
   ```

5. **Stage og commit**
   ```bash
   git add <filer>  # Kun relevante filer, ikke -A
   git commit -m "$(cat <<'EOF'
   <commit message>
   EOF
   )"
   ```

6. **Vis resultat** med `git log -1`

## Retningslinjer

### Tittel
- Maks 72 tegn
- Imperativ form: "Legg til", "Fiks", "Oppdater"
- Jira-nummer valgfritt (f.eks. `1234 Beskrivelse`)

### Body
- **Hva**: Kort oppsummering av endringene (første avsnitt)
- **Hvorfor**: Bakgrunn/motivasjon (andre avsnitt, ALLTID påkrevd)
- Plain text
- Ingen markdown-formattering
- Bruk norske tegn (øæå) — IKKE erstatt med oe/ae/aa
- Ikke wrap linjer — la hvert avsnitt stå på én linje

### Staging
- Stage kun relevante filer, IKKE bruk `git add -A`
- Unngå å committe sensitive filer (.env, credentials)

## Eksempel

```
Legg til CDM 4.4-støtte for A008

Legger til støtte for CDM 4.4-endringer i A008 SED med nytt formål-felt og oppdatert SED-versjon bak feature toggle.

CDM 4.4-spesifikasjonen krever at A008 har et formål-felt for å skille mellom "endringsmelding" og "arbeid_flere_land". Styres av toggle for kontrollert utrulling.
```
