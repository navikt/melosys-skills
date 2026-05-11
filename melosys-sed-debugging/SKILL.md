---
name: melosys-sed-debugging
description: |
  Debug SED flows across melosys-eessi → eux-rina-api → RINA mock. Use when:
  (1) XSD validation errors from RINA or melosys-mock,
  (2) Tracing missing/wrong NAV SED fields to RINA format,
  (3) Figuring out what NAV SED JSON is needed for CDM 4.4 (A008),
  (4) Improving mock XSD validator to show actionable errors,
  (5) Debugging send-SED flow end-to-end,
  (6) JSON-to-XML conversion and element ordering in mock,
  (7) Understanding eux-rina-api template mappings.
  Triggers: "XSD validation", "SED feil", "mapping error", "missing field",
  "element order", "RINA validation", "NAV SED", "CDM 4.4", "A008", "trace SED"
---

# Melosys SED Debugging

## Service Chain

```
melosys-web (3000) → melosys-api (8080) → melosys-eessi (8081) → eux-rina-api (9090) → melosys-mock (8083)
                                                                         ↓
                                                                   ACL: NAV SED → RINA SED
                                                                         ↓
                                                                   melosys-mock validates
                                                                   RINA SED against XSD
```

## Data Formats at Each Stage

| Stage | Format | Root structure |
|-------|--------|---------------|
| melosys-eessi output | NAV SED | `{"sed":"A008","nav":{...},"medlemskap":{...}}` |
| eux-rina-api output | RINA SED | `{"A008":{"Person":{...},"PurposeofSED":{...}}}` |
| XSD validation | XML | `<sed:A008 xmlns:sed="http://ec.europa.eu/eessi/ns/4_4/A008">` |

## Debugging Workflow: XSD Error → NAV SED Fix

### Step 1: Read the XSD error
```
cvc-complex-type.2.4.a: Invalid content starting with element 'PlaceWork'.
One of '{StatesResidence}' is expected.
```

### Step 2: Find the RINA element in the eux-rina-api template
Read the template at:
```
eux-rina-api/src/main/resources/sedtemplates/v44/legislationapplicable/A008_v4.4.json
```
Find the failing element and its `$nav.*` or `$medlemskap.*` source path.

### Step 3: Trace backwards to NAV SED
Template value `$nav.arbeidsland[x].land` means the NAV SED needs:
```json
{"nav": {"arbeidsland": [{"land": "SE"}]}}
```

### Step 4: Check the mapper in melosys-eessi
```
melosys-eessi/src/main/java/.../service/sed/mapper/til_sed/lovvalg/A008Mapper.kt
```

## Key Files by Repository

### melosys-eessi (builds NAV SED)
| File | Purpose |
|------|---------|
| `service/sed/mapper/til_sed/lovvalg/A008Mapper.kt` | A008 mapping |
| `service/sed/mapper/til_sed/lovvalg/LovvalgSedMapper.kt` | Base class |
| `service/sed/mapper/til_sed/SedMapper.kt` | Common mapping (person, pin) |
| `models/sed/SED.kt` | Root SED class |
| `models/sed/nav/Nav.kt` | Nav object model |
| `models/sed/medlemskap/impl/MedlemskapA008.kt` | A008 medlemskap |
| `integration/eux/rina_api/EuxConsumer.java` | HTTP to eux-rina-api |

### eux-rina-api (transforms NAV → RINA)
| File | Purpose |
|------|---------|
| `sedtemplates/v44/legislationapplicable/A008_v4.4.json` | A008 template |
| `acl/EessiAcl.java` | Core mapping engine |
| `acl/SedTemplateContainer.java` | Template loading/caching |
| `acl/CodesContainer.java` | Value code mappings |
| `rina/cpi/service/EessiAclClient.java` | Pre/post processing |
| `rina/cpi/service/RinaCpiService.java` | Orchestration |

### melosys-mock (validates RINA SED)
| File | Purpose |
|------|---------|
| `rina/SedXsdValidator.kt` | XSD validation |
| `rina/JsonToXmlConverter.kt` | RINA JSON → XML |
| `rina/XsdElementOrderExtractor.kt` | Element ordering from XSD |
| `rina/RinaCpiApi.kt` | `/eessiRest/*` endpoints |
| `rina/RinaAdminApi.kt` | Admin + validation endpoints |
| `resources/xsd/cdm44/A008.xsd` | XSD schema |

## ACL Transformation (eux-rina-api)

1. **Flatten** NAV SED: `$nav.bruker.person.fornavn = "Ola"`
2. **Convert codes**: `m → male`, `ja → yes`, `k → female`
3. **Template lookup** (inverse BiMap): `$nav.bruker.person.fornavn` → `Person.PersonIdentification.forename`
4. **Replace** `[x]` with actual indices `[0]`, `[1]`
5. **Unflatten** to hierarchical RINA JSON
6. **Remove** empty entries

## XSD Validation in melosys-mock

### Endpoints
| Endpoint | Input | Description |
|----------|-------|-------------|
| `POST /rina/xsd-validate` | RINA SED JSON | Direct XSD validation |
| `POST /rina/nav-sed-validate` | NAV SED JSON | Converts via eux-rina-api first |
| `GET /portal_new/xsd-validator` | Browser | Interactive web UI |

### JSON → XML Conversion
- Root element gets namespace: `<sed:A008 xmlns:sed="http://ec.europa.eu/eessi/ns/4_4/A008">`
- Children are unqualified (XSD `elementFormDefault="unqualified"`)
- Element ordering enforced from XSD `<xsd:sequence>` definitions

### Common XSD Errors

| XSD Error | Likely NAV SED cause |
|-----------|---------------------|
| Missing `StatesResidence` | `medlemskap.bruker.arbeidiflereland[x].bosted.land` not set |
| Wrong element order | JSON→XML converter ordering issue |
| Invalid enum value | Kodeverk mapping: check `codes/mappings/*.properties` |
| Unexpected element | Field in template but not in XSD for this version |

### A008 Element Ordering (InformationWorkingInTwoOrMoreMemberStates)
1. `StatesResidence` (**required**, minOccurs=1)
2. `IdentificationEmployers` (optional)
3. `IdentificationSelfEmployment` (optional)
4. `PlaceWork` (optional)

## CDM 4.4 Specifics for A008

- `arbeidiflereland` changed from object (4.3) to **array** (4.4)
- New field `formaal` with values: `arbeid_flere_land`, `endringsmelding`
- Feature toggle `CDM_4_4` in melosys-eessi controls version

## References

- **[template-to-nav-mapping.md](references/template-to-nav-mapping.md)**: Full A008 v4.4 template with every NAV ↔ RINA field path
- **[nav-sed-a008-example.md](references/nav-sed-a008-example.md)**: Complete NAV SED JSON examples for A008
- **[xsd-debugging-guide.md](references/xsd-debugging-guide.md)**: Step-by-step guide for diagnosing XSD errors
