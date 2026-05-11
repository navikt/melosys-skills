---
name: eux-rina-mock
description: |
  Add new SED types, BUC types, and XSD validation to the melosys-mock RINA/EUX implementation.
  Use this skill whenever working with the RINA mock — adding SED support (A001-A012, X001-X008),
  updating BUC-to-SED mappings, adding XSD schemas, debugging mock endpoint issues, or understanding
  the mock architecture for EESSI integration. Also use when working in melosys-e2e-tests and you
  need to extend what the mock supports for a new test scenario.
  Triggers: "legg til SED", "ny SED-type", "mock SED", "eux-rina-mock", "RINA mock",
  "add SED to mock", "BUC type", "XSD for SED", "mock endepunkt", "mock støtter ikke",
  "trenger mock for", "utvide mock"
---

# EUX-RINA Mock Skill

This skill guides you through extending the melosys-mock's RINA/EUX implementation.
The mock lives in the `melosys-docker-compose` repo under `mock/`.

## Architecture — Three API Surfaces, One Store

The mock exposes three API surfaces that all share a single `RinaCaseStore`:

```
melosys-api ──────────────► /api/*       (simulates melosys-eessi)
melosys-eessi ────────────► /eux/*       (simulates eux-rina-api)
eux-rina-api ─────────────► /eessiRest/* (simulates RINA CPI)
```

Which surface is used depends on the test scenario:
- **E2E without real eux-rina-api** (`make dev-eessi`): melosys-eessi calls `/eux/*`
- **E2E with real eux-rina-api** (`make dev-rina`): eux-rina-api calls `/eessiRest/*`
- **Component tests in melosys-api**: melosys-api calls `/api/*`

When adding a new SED, you usually only need to touch the shared `RinaCaseStore` — the
three API controllers delegate to it. Exception: if a SED has unique endpoint behavior,
you may need to update a controller too.

## Key Files

All paths relative to the mock root (`mock/src/main/kotlin/no/nav/melosys/melosysmock/`):

| File | Role |
|------|------|
| `rina/RinaCaseStore.kt` | Central storage — BUC/SED lifecycle, action generation, BUC-to-SED mapping |
| `rina/RinaCpiApi.kt` | RINA CPI endpoints (`/eessiRest/*`) — used by eux-rina-api |
| `eux/EuxRinaApi.kt` | EUX convenience endpoints (`/eux/*`) — used by melosys-eessi |
| `melosyseessi/MelosysEessiApi.kt` | melosys-eessi mock (`/api/*`) — used by melosys-api |
| `rina/RinaCpiDtos.kt` | DTO classes (ActionDto, DocumentMetadata, OrganisationDto, etc.) |
| `rina/SedXsdValidator.kt` | XSD validation with schema cache |
| `rina/JsonToXmlConverter.kt` | JSON-to-XML with namespace and element ordering |
| `rina/XsdElementOrderExtractor.kt` | Reads `xsd:sequence` element order from XSD schemas |
| `rina/SedFieldMappingRegistry.kt` | NAV SED field to RINA element reverse-mapping |
| `eux/SedTypeRegistry.kt` | Document ID to SED type mapping |
| `testdata/TestDataGenerator.kt` | Test data creation endpoints (`/testdata/*`) |

## Adding a New SED Type — Step by Step

### Step 1: Update BUC-to-SED Mapping

In `RinaCaseStore.kt`, find the `generateInitialActions()` method and its `when (bucType)` block.
Add your SED type to the correct BUC:

```kotlin
// RinaCaseStore.kt — generateInitialActions()
val sedTypes = when (bucType) {
    "LA_BUC_01" -> listOf("A001")
    "LA_BUC_02" -> listOf("A003", "A008", "A009", "A010", "A011")
    "LA_BUC_02a" -> listOf("A003", "A008", "A009", "A010", "A011")
    "LA_BUC_03" -> listOf("A008")
    "LA_BUC_04" -> listOf("A008")
    "LA_BUC_05" -> listOf("A009", "A010")
    "LA_BUC_06" -> listOf("A004", "A005", "A006")
    else -> listOf("A001", "X001")
}
```

This is the only change needed for basic SED support. The mock will automatically:
- Generate `Create_<SedType>` actions with pre-assigned document IDs
- Accept document submission via POST/PUT
- Store and return the SED content
- Include the SED in BUC overview responses

### Step 2: Add SED Title (Optional but Recommended)

In `EuxRinaApi.kt`, update the `getSedTitle()` function:

```kotlin
private fun getSedTitle(sedType: String): String = when (sedType) {
    "A001" -> "Soknad om bestemmelse av lovvalg"
    "A003" -> "Svar på soknad"
    // ... add your SED type here
    else -> sedType
}
```

### Step 3: Add XSD Validation (Optional)

Only needed if you want to validate SED content against the EU XSD schema.

1. Copy the XSD file from CDM 4.4 package to `src/main/resources/xsd/cdm44/<SedType>.xsd`
2. If the XSD imports other schemas, make sure `XAdES.xsd` and `xmldsig-core-schema.xsd`
   are already present (they are for CDM 4.4)
3. The validator auto-discovers XSD files by SED type name — no code changes needed

### Step 4: Add Integration Test

Create a test following the existing pattern. Use `A001XsdValidationIntegrationTest.kt` or
`A008XsdValidationIntegrationTest.kt` as template:

```kotlin
// src/test/kotlin/.../rina/<SedType>XsdValidationIntegrationTest.kt
class A009XsdValidationIntegrationTest {
    private val objectMapper = ObjectMapper()
    private val xsdElementOrderExtractor = XsdElementOrderExtractor()
    private val converter = JsonToXmlConverter(objectMapper, xsdElementOrderExtractor)
    private val validator = SedXsdValidator(validationEnabled = true, failOnError = true)

    @Test
    fun `simple <SedType> should produce XSD-valid XML`() {
        val json = objectMapper.readTree("""
            {
                "<SedType>": {
                    "Person": {
                        "PersonIdentification": {
                            "familyName": "Nordmann",
                            "forename": "Ola",
                            "dateBirth": "1990-01-01",
                            "sex": {"value": ["01"]}
                        }
                    }
                    // ... add required fields for this SED type
                }
            }
        """.trimIndent())

        val conversionResult = converter.convert(json)
        assertNull(conversionResult.error)

        val validationResult = validator.validate(conversionResult.xml!!, "<SedType>")
        assertTrue(validationResult.isValid,
            "Errors: ${validationResult.errors}")
    }
}
```

### Step 5: Test Data for E2E Tests

If the SED needs to be received (MOTTAK), add a test resource JSON file and use the
`/testdata/lag-melosys-eessi-melding` endpoint to publish it to Kafka:

```bash
curl -X POST http://localhost:8083/testdata/lag-melosys-eessi-melding \
  -H "Content-Type: application/json" \
  -d '{
    "fnr": "30056928150",
    "sedType": "A009",
    "bucType": "LA_BUC_05",
    "avsenderLandkode": "SE"
  }'
```

## SED Format Reference

The mock handles two SED formats. Understanding when each is used prevents confusion:

**NAV SED format** — sent FROM melosys-eessi TO eux-rina-api:
```json
{
  "sed": "A008",
  "nav": {
    "bruker": { "person": { "fornavn": "Ola", "etternavn": "Nordmann" } },
    "arbeidsgiver": [{ "navn": "Company AS" }]
  }
}
```

**RINA/EU SED format** — what eux-rina-api transforms it to, and what the mock stores:
```json
{
  "A008": {
    "Person": {
      "PersonIdentification": { "forename": "Ola", "familyName": "Nordmann" }
    }
  }
}
```

The mock stores content AS RECEIVED. When coming through eux-rina-api, content arrives
in RINA format. When coming directly from melosys-eessi (via `/eux/*`), it arrives in
NAV format.

## Debugging Checklist

When something isn't working with the mock:

1. **Check which API surface is being called** — look at logs for `RINA CPI:` vs `CPI:` vs `Mock`
2. **Inspect stored data** — `curl http://localhost:8083/rina/admin/cases | jq .`
3. **Check actions** — `curl http://localhost:8083/rina/admin/cases/{id}/debug | jq .`
4. **Visual inspection** — open http://localhost:8083/portal_new in browser
5. **XSD validation** — add `X-Enable-XSD-Validation: true` header to check content validity

Common issues:
- SED type not in `when(bucType)` mapping → no Create action generated
- Document status is wrong → must be `"new"` (not `"draft"`) for melosys-eessi to recognize it
- Full SED content overwritten by metadata → `updateDocument()` has protection, but check logs
- Missing attachment → verify `addAttachment()` stores on `DocumentMetadata.attachments`

## Documentation

For deeper reference, read these docs in `mock/docs/`:
- `MOCK-SCENARIOS.md` — which endpoints for which test scenario
- `EUX-RINA-API-MOCK.md` — complete API reference with all endpoints and DTOs
- `XSD_VALIDATION_IMPLEMENTATION.md` — XSD validation architecture details
- `SED-SENDT-KAFKA-FLOW.md` — known gap: Kafka sed-sendt not mocked
