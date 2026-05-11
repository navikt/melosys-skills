---
name: review-loop
description: Run a self-review loop on the current PR — iterates review/fix/commit cycles until clean
disable-model-invocation: true
---

# Review-loop — Selvreview av nåværende PR

Start en selvreview-loop for den åpne PR-en på nåværende branch.

## Steg 1: Finn PR

```bash
gh pr list --head $(git branch --show-current) --json number,title,url,body --jq '.[0]'
```

Hvis ingen PR finnes, si ifra og stopp.

## Steg 2: Review-loop

Kjør denne syklusen:

```
runde = 1

LOOP:
  1. Kjør /review og sjekk for feil og mangler og at dokumentasjon er oppdatert, følg så Steg 2 derfra
     (spawn subagent med prompten definert der).
     VIKTIG: ALDRI inkluder kontekst om hvilken runde det er,
     hva som ble fikset forrige gang, eller andre hint.
     Subagenten skal ha helt ren kontekst hver gang.

  2. Subagent returnerer funn (eller "GODKJENT")
  3. Hvis GODKJENT → gå til Steg 3

  4. For HVERT funn — VURDER KRITISK:
     a. Høy: Bugs, sikkerhetshull, manglende auth, feil logikk → FIKS
     b. Middels: Manglende error handling, dårlig navngiving, ubrukt kode → FIKS som regel
     c. Lav: Stilpreferanser, "nice to have", kosmetiske ting → IGNORER som regel
     d. Ting du IKKE skal fikse:
        - Forslag om å legge til kommentarer/docstrings du ikke endret
        - Forslag om å refaktorere kode utenfor PR-ens scope
        - Rene smakssaker uten faktisk forbedring
        - Ting som krever arkitekturendringer

  5. Hvis du fikset noe:
     a. Kjør relevant build/test (npm run build, pytest, etc.)
     b. Commit + push
     c. runde += 1
     d. GÅ TIL 1 — ny review er PÅKREVD etter endringer

  6. Hvis du vurderte alle funn og ingen var verdt å fikse → gå til Steg 3
  7. Hvis runde > 5: STOPP og informer brukeren
```

## Steg 3: Oppsummer

Si ifra til brukeren:

```
Review-loop ferdig for PR #{NR}.
- Runder: {runde}
- Funn fikset: {antall}
- Status: Godkjent / Stoppet etter 5 runder
- Link: {PR-URL}
```
