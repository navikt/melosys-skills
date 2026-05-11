# XSD Debugging Guide

Step-by-step procedures for diagnosing and fixing XSD validation errors.

## Table of Contents
- [Quick diagnosis](#quick-diagnosis)
- [Error type: Missing required element](#missing-required-element)
- [Error type: Wrong element order](#wrong-element-order)
- [Error type: Invalid enum value](#invalid-enum-value)
- [Error type: Unexpected element](#unexpected-element)
- [Using the mock validation endpoints](#using-the-mock-validation-endpoints)
- [Improving error messages](#improving-error-messages)

## Quick Diagnosis

Given an XSD error message, determine the type:

| Error pattern | Type |
|--------------|------|
| `cvc-complex-type.2.4.a: ... One of '{ElementName}' is expected` | Missing required element OR wrong order |
| `cvc-complex-type.2.4.d: ... not expected` | Unexpected element |
| `cvc-enumeration-valid: Value '...' is not facet-valid` | Invalid enum value |
| `cvc-type.3.1.3: ... is not a valid value of type` | Wrong data format |
| `cvc-minInclusive-valid` / `cvc-maxInclusive-valid` | Value out of range |

## Missing Required Element

**Example error:**
```
cvc-complex-type.2.4.a: Invalid content was found starting with element 'PlaceWork'.
One of '{StatesResidence}' is expected.
```

**Diagnosis steps:**

1. The error says `StatesResidence` is expected. Check the template:
   ```
   StatesResidence.StateResidence[x].stateResidence.value → $medlemskap.bruker.arbeidiflereland[x].bosted.land
   ```

2. The NAV SED needs `medlemskap.bruker.arbeidiflereland` with at least one entry with `bosted.land`.

3. Check A008Mapper.kt:
   ```kotlin
   // Does getMedlemskap() populate arbeidiflereland correctly?
   override fun getMedlemskap(sedData: SedDataDto) = MedlemskapA008(
       bruker = hentA008Bruker(sedData),
       formaal = hentFormaal(sedData)
   )
   ```

4. Check if `SedDataDto` has the required data from melosys-api.

**Fix patterns:**
- If field exists in SedDataDto but mapper doesn't use it → update mapper
- If field doesn't exist in SedDataDto → trace back to melosys-api
- If field is optional in business logic but required by XSD → add default/empty value

## Wrong Element Order

**Example error:**
```
cvc-complex-type.2.4.a: Invalid content was found starting with element 'IdentificationEmployers'.
One of '{IdentificationSelfEmployment, PlaceWork}' is expected.
```

**Diagnosis steps:**

1. This means `IdentificationEmployers` appeared AFTER elements that should come after it.
2. Check the XSD-defined order for the parent element.
3. The `XsdElementOrderExtractor` in melosys-mock extracts ordering from XSD.
4. The `JsonToXmlConverter` uses this ordering to sort elements.

**Fix:** Usually a bug in `JsonToXmlConverter` or `XsdElementOrderExtractor`. Check:
- Is the parent element name correctly resolved?
- Does the XSD use `<xsd:sequence>` (strict order) or `<xsd:all>` (any order)?
- Are all child elements registered in the order map?

## Invalid Enum Value

**Example error:**
```
cvc-enumeration-valid: Value 'mann' is not facet-valid with respect to enumeration
'[male, female, unknown]'. It must be a value from the enumeration.
```

**Diagnosis steps:**

1. The NAV value (`mann`) was not converted to EU value (`male`).
2. Check code mappings in eux-rina-api:
   ```
   /codes/mappings/kjoennkoder.properties
   ```
3. Check `codeMappingConfig.properties` to see which mapping file is used for the field path.

**Fix:** Add or correct the mapping in the `.properties` file.

## Unexpected Element

**Example error:**
```
cvc-complex-type.2.4.d: Invalid content was found starting with element 'someElement'.
No child element is expected at this point.
```

**Diagnosis steps:**

1. The element exists in the template but NOT in the XSD.
2. Check if this is a CDM version mismatch (field added in 4.4 but using 4.3 template).
3. Check if the template has extra fields not in the XSD.

**Fix:** Either update the XSD or remove the field from the template.

## Using the Mock Validation Endpoints

### Validate RINA SED directly
```bash
curl -X POST http://localhost:8083/rina/xsd-validate \
  -H "Content-Type: application/json" \
  -d '{"A008":{"Person":{"PersonIdentification":{"forename":"Ola","familyName":"Nordmann","dateBirth":"1980-01-15"}},"PurposeofSED":{"InformationWorkingInTwoOrMoreMemberStates":{"StatesResidence":{"StateResidence":[{"stateResidence":{"value":["NO"]}}]}}}}}'
```

### Validate NAV SED (converts via eux-rina-api first)
```bash
curl -X POST http://localhost:8083/rina/nav-sed-validate \
  -H "Content-Type: application/json" \
  -d '{"sed":"A008","sedVer":"4","sedGVer":"4","nav":{"bruker":{"person":{"fornavn":"Ola","etternavn":"Nordmann","foedselsdato":"1980-01-15","pin":[{"identifikator":"12345678901","land":"NO"}]}}},"medlemskap":{"formaal":"arbeid_flere_land","bruker":{"arbeidiflereland":[{"bosted":{"land":"NO"}}]}}}'
```

### Use the web UI
Open `http://localhost:8083/portal_new/xsd-validator` in a browser.

## Improving Error Messages

When improving the XSD validator to show actionable errors, map each XSD error to:

1. **Which RINA element** failed (from XSD error message)
2. **Which template path** maps to that element (from `A008_v4.4.json`)
3. **Which NAV SED field** is the source (the `$nav.*` or `$medlemskap.*` value in template)
4. **What the user needs to do** (set field, fix format, add mapping)

### Implementation approach

In `SedXsdValidator.kt` or a new `XsdErrorEnricher`:

```kotlin
// Pseudocode for enriching XSD errors with NAV field info
fun enrichError(xsdError: XsdValidationError, sedType: String): EnrichedError {
    val rinaElement = extractElementFromError(xsdError.message)  // e.g., "StatesResidence"
    val templatePath = findInTemplate(sedType, rinaElement)      // search A008_v4.4.json
    val navField = templatePath?.extractNavPrefix()              // e.g., "$medlemskap.bruker.arbeidiflereland[x].bosted.land"
    return EnrichedError(
        xsdError = xsdError,
        rinaElement = rinaElement,
        navSedField = navField,
        suggestion = "Set $navField in NAV SED to fix this error"
    )
}
```

### Key: Loading the template for reverse lookup

The eux-rina-api templates can be read in the `eux-rina-api` repo at:
```
src/main/resources/sedtemplates/v44/legislationapplicable/A008_v4.4.json
```

Or copy relevant templates into the mock at:
```
mock/src/main/resources/sedtemplates/
```

Flatten the template JSON and build a map from RINA element name to NAV path for quick lookups.
