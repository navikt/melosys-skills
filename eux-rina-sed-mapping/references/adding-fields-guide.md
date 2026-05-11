# Adding New SED Fields (CDM Upgrade Guide)

Step-by-step guide for adding new fields when upgrading CDM versions.

## Example: A008 CDM 4.3 → 4.4 Changes

New fields to add:
1. Radio button for purpose (change notification vs. work in multiple states)
2. Cancellation indicator (person didn't work in receiving country)
3. Additional information text field

## Step 1: Update SED Template (eux-rina-api)

**File:** `src/main/resources/sedtemplates/v44/legislationapplicable/A008_v4.4.json`

Add new field mappings:

```json
{
  "A008": {
    "PurposeofSED": {
      "purposeOfSED": { "value": ["$medlemskap.formaal"] },
      "NotificationChangesInRelevantData": {
        "Cancellation": {
          "personDidNotWorkIndicator": { "value": ["$medlemskap.kansellering.personIkkeJobbet"] }
        }
      }
    },
    "AdditionalInformation": {
      "additionalInformation": "$nav.ytterligereinformasjon"
    }
  }
}
```

**Field patterns:**
- Radio buttons/enums: `{ "value": ["$path"] }` wrapper
- Text fields: Direct `"$path"` reference
- Arrays: Use `[x]` placeholder

## Step 2: Add Kodeverk Mapping (if enum/radio button)

**A) Register mapping in:** `src/main/resources/codes/codeMappingConfig.properties`

```properties
.formaal=A008PurposeType
.personIkkeJobbet=EESSIYesNoType
```

The path ending (`.formaal`) matches any flattened path ending with that suffix.

**B) Create or use mapping file:** `src/main/resources/codes/mappings/A008PurposeType.properties`

```properties
# NAV value = EU value
endringsmelding=01
arbeid_flere_land=02
```

For Yes/No fields, use existing `EESSIYesNoType.properties`:
```properties
ja=1
nei=0
```

## Step 3: Update NAV SED DTOs (melosys-eessi)

**File:** `MedlemskapA008.kt` (or similar in melosys-eessi)

```kotlin
data class MedlemskapA008(
    var endring: Endring? = null,
    var kansellering: Kansellering? = null,
    var formaal: String? = null  // NEW: "endringsmelding" | "arbeid_flere_land"
)

data class Kansellering(
    var heleperioden: HelePeriodenType? = null,
    var personIkkeJobbet: String? = null  // NEW: "ja" | "nei"
)
```

## Step 4: Update SED Mapper (melosys-eessi)

**File:** `A008Mapper.kt` (or similar)

```kotlin
class A008Mapper : LovvalgSedMapper<MedlemskapA008> {
    override fun getMedlemskap(sedData: SedDataDto) = MedlemskapA008(
        endring = getEndring(sedData),
        kansellering = getKansellering(sedData),
        formaal = sedData.vedtakDto?.formaal  // NEW
    )

    private fun getKansellering(sedData: SedDataDto) = Kansellering(
        heleperioden = sedData.vedtakDto?.kansellering?.heleperioden,
        personIkkeJobbet = sedData.vedtakDto?.kansellering?.personIkkeJobbet  // NEW
    )
}
```

## Step 5: Update Nav Object (if $nav.* field)

For fields under `$nav.*` (like `ytterligereinformasjon`):

**File:** `Nav.kt` in melosys-eessi

```kotlin
data class Nav(
    var bruker: Bruker? = null,
    var arbeidsgiver: List<Arbeidsgiver>? = null,
    var ytterligereinformasjon: String? = null  // Ensure field exists
)
```

## Step 6: Update PDF Generation (eux-rina-api)

PDF generation uses HTML form metadata from:
`src/main/resources/templates/v4.4/A008_Read/no_form.html`

The META_MODEL JavaScript in this file defines:
- Field labels shown in PDF
- Field ordering
- Enum value display text

If missing, update the HTML template to include new fields.

## Step 7: Testing

### Unit Test (eux-rina-api)

```java
@Test
void testA008NewFields() {
    String navSed = """
        {
          "nav": {"bruker": {"person": {"fornavn": "Test"}}},
          "medlemskap": {
            "formaal": "endringsmelding",
            "kansellering": {"personIkkeJobbet": "ja"}
          },
          "sedType": "A008"
        }
        """;

    String euSed = eessiAcl.mapNavToEu(navSed, "4.4");

    // Verify new fields mapped correctly
    assertThat(euSed).contains("\"purposeOfSED\"");
    assertThat(euSed).contains("\"value\":[\"01\"]");  // Code mapped
}
```

### Integration Test

Test full flow: melosys-api → melosys-eessi → eux-rina-api → RINA mock

## Checklist for New Fields

| Step | Location | Action |
|------|----------|--------|
| 1 | `sedtemplates/v{X}/{SED}_v{X}.json` | Add field mapping |
| 2a | `codes/codeMappingConfig.properties` | Register path→mapping (if enum) |
| 2b | `codes/mappings/{Name}.properties` | Create value mappings (if new enum) |
| 3 | melosys-eessi DTOs | Add field to Medlemskap/Nav class |
| 4 | melosys-eessi Mapper | Map from SedDataDto |
| 5 | `templates/v{X}/{SED}_Read/` | Update PDF template (if needed) |
| 6 | Tests | Add unit and integration tests |

## Common Issues

### Field not appearing in output
- Check template path matches DTO field name exactly
- Verify `$nav.` vs `$medlemskap.` prefix is correct
- Check for typos in path (case-sensitive)

### Code not converted
- Verify path ending in `codeMappingConfig.properties`
- Check mapping file exists in `codes/mappings/`
- Verify NAV value exists in mapping file

### Array fields not working
- Ensure `[x]` placeholder in template path
- Check parent array is not null in DTO
