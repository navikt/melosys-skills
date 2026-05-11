---
name: eux-rina-sed-mapping
description: |
  Expert knowledge of NAV SED to RINA SED mapping in eux-rina-api (CDM 4.4).
  Use when: (1) Creating or modifying SED mappers in melosys-eessi,
  (2) Mocking eux-rina-api responses for e2e or local testing,
  (3) Understanding the RINA template JSON structure and $nav/$medlemskap prefixes,
  (4) Debugging SED mapping issues between NAV format and EESSI format,
  (5) Understanding which fields map to which RINA paths for specific SED types (A001-A012, X001-X008),
  (6) Adding new fields during CDM version upgrades (e.g., CDM 4.3 → 4.4),
  (7) Understanding kodeverk/code mappings for enums and radio buttons,
  (8) Troubleshooting PDF generation for SEDs.
---

# EUX-RINA SED Mapping

## Architecture Overview

```
melosys-api/melosys-eessi (NAV SED)
         │
         ▼ SedMapper.mapTilSed()
   SED { nav: Nav, medlemskap: Medlemskap }
         │
         ▼ JSON serialization
         │
    eux-rina-api (NAV SED → RINA SED)
         │
         ▼ Template-based transformation (ACL)
   RINA SED (EU format)
         │
         ▼
       RINA
```

## Key Concepts

| Term | Description |
|------|-------------|
| NAV SED | Internal NAV format with `nav` and `medlemskap` objects |
| RINA SED | EU-standardized format used by EESSI |
| CDM | Common Data Model - EESSI schema version (current: 4.4) |
| ACL | Anti-Corruption Layer - transforms NAV ↔ EU format |
| Templates | JSON files defining field path mappings |
| Kodeverk | Code mappings (NAV values ↔ EU values) |

## Template Location

eux-rina-api templates:
```
src/main/resources/sedtemplates/v44/
├── legislationapplicable/   # A001-A012
├── administrative/          # X001-X013, X050, X100
├── horizontal/              # H001-H131
├── family/                  # F001-F027
├── pension/                 # P-series
└── awod/                    # DA-series
```

## Template Syntax

Templates use placeholder prefixes:

| Prefix | Source | Description |
|--------|--------|-------------|
| `$nav.` | `SED.nav` | Person, employer, work location |
| `$medlemskap.` | `SED.medlemskap` | Decision, period, legislation |
| `[x]` | Array index | Maps arrays (e.g., `pin[x]`) |

**Value wrapper for enums:**
```json
"sex": { "value": ["$nav.bruker.person.kjoenn"] }
```

## Common Mappings

**Person identification**:
```
$nav.bruker.person.fornavn           → forename
$nav.bruker.person.etternavn         → familyName
$nav.bruker.person.foedselsdato      → dateBirth
$nav.bruker.person.kjoenn            → sex.value
$nav.bruker.person.pin[x].identifikator → personalIdentificationNumber
$nav.bruker.person.pin[x].land       → country.value
```

**Employer**:
```
$nav.arbeidsgiver[x].navn            → name
$nav.arbeidsgiver[x].adresse.gate    → Address.street
$nav.arbeidsgiver[x].adresse.by      → Address.town
$nav.arbeidsgiver[x].adresse.land    → Address.country.value
```

**Decision (A003)**:
```
$medlemskap.vedtak.land              → memberStateWhichLegislationApplies
$medlemskap.vedtak.gjelderperiode.startdato → FixedPeriod.startDate
$medlemskap.vedtak.gjelderperiode.sluttdato → FixedPeriod.endDate
```

## SED Types for Melosys

| SED | Purpose | Key medlemskap fields |
|-----|---------|----------------------|
| A001 | Exception request (Art. 16) | `unntak`, `soeknadsperiode` |
| A003 | Determination (Art. 13) | `vedtak`, `andreland` |
| A008 | Change notification | `endring`, `kansellering` |
| X008 | Invalidation | `nav.sak.ugyldiggjoere` |

## melosys-eessi Mapper Pattern

```kotlin
class A003Mapper : LovvalgSedMapper<MedlemskapA003> {
    override fun getSedType() = SedType.A003

    override fun getMedlemskap(sedData: SedDataDto) = MedlemskapA003(
        vedtak = getVedtak(sedData),      // → $medlemskap.vedtak.*
        andreland = getAndreLand(sedData)
    )
}

interface SedMapper {
    fun mapTilSed(sedData: SedDataDto) = SED(
        nav = prefillNav(sedData),        // → $nav.*
        medlemskap = getMedlemskap(),
        sedType = getSedType().name
    )
}
```

## PDF Generation & Oversettelser

PDF-visning av SED styres av to separate ting i eux-rina-api:
1. **Templates** (`sedtemplates/`) - mapper NAV SED-felter til RINA SED-felter
2. **Oversettelser** (`sedoversettelser/`) - styrer PDF-layout (seksjonsoverskrifter, feltnavn, kodeverk-tekster)

### Oversettelser-filer

```
src/main/resources/sedoversettelser/v44/
├── A/   # A001_oversettelser.json, A008_oversettelser.json, ...
├── X/   # X001_oversettelser.json, ...
├── H/   # H001_oversettelser.json, ...
└── ...
```

Oversettelsene er en flat `Map<String, Object>` - **nøkkelnavnet og index-verdien** bestemmer plassering i PDF, ikke posisjonen i JSON-filen.

### Oversettelse-entry struktur

```json
"A008.PurposeofSED.InformationWorkingInTwoOrMoreMemberStates" : {
    "index" : "3.2.",
    "prompt" : "Informasjon om arbeid i to eller flere medlemsland",
    "valuetype" : "_uxFieldSetContainer"
}
```

| Felt | Beskrivelse |
|------|-------------|
| **key** | Full RINA JSON-path (f.eks. `A008.PurposeofSED.StatesResidence`) |
| **index** | Seksjonsnummer i PDF (f.eks. `3.2.1.`) |
| **prompt** | Overskrift/feltnavn vist i PDF |
| **valuetype** | Felttype for rendering |
| **codework** | Kodeverk-mapping for radioknapper/dropdowns |
| **enumName** | EESSI enum-navn |

### Valuetypes

| Valuetype | Vises som |
|-----------|-----------|
| `_uxFieldSetContainer` | Seksjonsoverskrift (container) |
| `_uxTextInput` | Tekstfelt |
| `_uxDateInput` | Datofelt |
| `_uxRadioButton` | Radioknapp med kodeverk |
| `_uxSelectAutoCompleteInput` | Dropdown med kodeverk |
| `_uxTextAreaInput` | Fritekstfelt |
| `_rinaArray` | Array-element |
| `_rinaRoot` | SED-tittel |

### Vanlig feil: Manglende container-overskrifter

Hvis en `_uxFieldSetContainer`-entry mangler i oversettelsene, hopper PDF-en over den seksjonsoverskriften. Barn-entries vises fortsatt, men uten mellomoverskrift.

Eksempel: Mangler entry for `3.2.` → PDF viser:
```
3. Formål med SED
3.2.1. Bostedsland        ← hopper rett hit
```

I stedet for:
```
3. Formål med SED
3.2. Informasjon om arbeid i to eller flere medlemsland
3.2.1. Bostedsland
```

**Fix:** Legg til manglende container-entry i oversettelsene.

### Forhåndsvisning vs sending

PDF-forhåndsvisning og SED-sending bruker **forskjellige dataflyter** i melosys:

```
Forhåndsvisning (PDF preview):
  Frontend → SedPdfData → EessiService.genererSedPdf()
    → SedPdfData.utfyllSedDataDto() → SedDataDto
    → melosys-eessi SedMapper → eux-rina-api /sed/pdf

Sending (faktisk SED):
  Frontend → AnmodningUnntakDto → ProsessinstansBuilder
    → ProsessDataKey → AbstraktSendUtland
    → EessiService.opprettOgSendSed() → SedDataDto
    → melosys-eessi SedMapper → eux-rina-api
```

**Vanlig feil:** Nye felter legges til i send-flyten men glemmes i preview-flyten. Sjekk:
1. `SedPdfData.java` - at feltet finnes og settes i `utfyllSedDataDto()`
2. `melosys-web/.../operations.ts` `forhandsvisSed()` - at feltet inkluderes i `utfyltdata`
3. Frontend-komponenten - at feltet settes i `sedData` for `pdfDokumenter`

## Mocking for E2E/Local Testing

Mock RINA SED structure (EU format returned from RINA):
```json
{
  "A003": {
    "Person": {
      "PersonIdentification": {
        "forename": "Ola",
        "familyName": "Nordmann",
        "dateBirth": "1980-01-15"
      }
    },
    "DecisionLegislationApplicable": {
      "memberStateWhichLegislationApplies": { "value": ["NO"] },
      "PeriodForWhichDecisionApplies": {
        "FixedPeriod": {
          "startDate": "2024-01-01",
          "endDate": "2024-12-31"
        }
      }
    }
  }
}
```

## References

### Field Mappings
- **[field-mapping.md](references/field-mapping.md)**: Complete NAV → RINA field mapping tables
- **[rina-templates.md](references/rina-templates.md)**: RINA template JSON patterns for each SED type
- **[nav-sed-structure.md](references/nav-sed-structure.md)**: NAV SED DTO class structure (Kotlin)

### Architecture & Implementation
- **[acl-architecture.md](references/acl-architecture.md)**: ACL transformation flow, key classes, error handling
- **[adding-fields-guide.md](references/adding-fields-guide.md)**: Step-by-step guide for CDM upgrades and adding new fields
- **[kodeverk-mappings.md](references/kodeverk-mappings.md)**: Code mapping system (enums, radio buttons, yes/no fields)
