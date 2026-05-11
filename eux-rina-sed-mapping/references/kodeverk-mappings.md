# Kodeverk (Code) Mappings

Maps NAV values to EU EESSI values and vice versa during SED transformation.

## Files

```
src/main/resources/codes/
├── codeMappingConfig.properties    # Path → mapping file registry
└── mappings/
    ├── EESSIYesNoType.properties   # ja/nei → 1/0
    ├── landkoder.properties        # Country codes
    ├── kjoennkoder.properties      # Gender codes
    ├── sivilstandkoder.properties  # Marital status
    └── ...                         # ~100+ mapping files
```

## How It Works

### 1. codeMappingConfig.properties

Maps flattened JSON path endings to mapping files:

```properties
# Path ending = mapping file name (without .properties)
.kjoenn=kjoennkoder
.land=landkoder
.EESSIYesNoType=EESSIYesNoType
.harfastarbeidssted=janeikoder
.vedtak.eropprinneligvedtak=janeikoder
```

**Path matching**: The path ending (`.kjoenn`) matches any field ending with that suffix:
- `$nav.bruker.person.kjoenn` ✓
- `$nav.annenperson.person.kjoenn` ✓
- `$medlemskap.endring.kjoenn` ✓

### 2. Mapping Files

BiMap (bidirectional) for NAV ↔ EU conversion:

**EESSIYesNoType.properties**:
```properties
ja=1    # NAV "ja" → EU "1"
nei=0   # NAV "nei" → EU "0"
```

**kjoennkoder.properties**:
```properties
m=male      # NAV "m" → EU "male"
k=female    # NAV "k" → EU "female"
u=unknown   # NAV "u" → EU "unknown"
```

## Common Mapping Types

### Boolean Fields (ja/nei)
Use `janeikoder` or `EESSIYesNoType`:

```properties
# janeikoder.properties
ja=yes
nei=no

# EESSIYesNoType.properties
ja=1
nei=0
```

Common boolean paths:
- `.harfastarbeidssted`
- `.vedtak.eropprinneligvedtak`
- `.vedtak.erendringsvedtak`
- `.anmodning.erendring`
- `.isDeterminationProvisional`

### Country Codes
Use `landkoder`:
```properties
NO=NO
SE=SE
DK=DK
# ISO-2 codes (identical in most cases)
```

Note: Separate files for ISO-2/ISO-3 conversion in `kodeverksmapping/`:
- `landkoderIso2VsIso3.properties`
- `countryCodeNavEu.properties`

### Article References
Use `artikkelfor8832004eller9872009koder`:
```properties
12_1=12_1      # Posted workers
12_2=12_2      # Self-employed posting
13_1_a=13_1_a  # Work in multiple states
13_2_a=13_2_a  # Self-employed multiple states
16_1=16_1      # Exception agreement
```

### Period Types
Use `medlemskapendringsperiodekoder`:
```properties
# Change notification period types for A008
...
```

## Adding New Mappings

### 1. Create mapping file

**File**: `src/main/resources/codes/mappings/NewEnumType.properties`

```properties
# NAV value = EU value
nav_value_1=eu_value_1
nav_value_2=eu_value_2
```

### 2. Register in config

**File**: `codeMappingConfig.properties`

```properties
.newFieldPath=NewEnumType
```

### 3. Test bidirectional mapping

```java
@Test
void testNewEnumMapping() {
    BiMap<String, String> codes = CodesContainer.getCodes(".newFieldPath");

    // NAV → EU
    assertEquals("eu_value_1", codes.get("nav_value_1"));

    // EU → NAV
    assertEquals("nav_value_1", codes.inverse().get("eu_value_1"));
}
```

## Debugging Mapping Issues

### Code not converted

Check logs for warnings:
```
WARN - Could not find mapping for value 'xyz' in field '.somepath'
```

Causes:
1. Path not registered in `codeMappingConfig.properties`
2. Value not in mapping file
3. Typo in path ending

### Wrong mapping applied

Multiple path endings can match. More specific paths take precedence:
```properties
# Less specific
.type=generalTypeCodes

# More specific (wins for sivilstand.status)
.sivilstand.status=sivilstandkoder
```

## A008-Specific Mappings

| Field | Config Path | Mapping File |
|-------|-------------|--------------|
| Purpose type | `.formaal` | (create new) |
| Change period | `.ihhtparagraf` | `medlemskapendringsperiodekoder` |
| Cancellation | `.kansellering.*` | `EESSIYesNoType` |

## Key Mapping Files

| File | NAV Values | EU Values | Used For |
|------|------------|-----------|----------|
| `EESSIYesNoType` | ja, nei | 1, 0 | Boolean indicators |
| `janeikoder` | ja, nei | yes, no | Yes/No fields |
| `kjoennkoder` | m, k, u | male, female, unknown | Gender |
| `landkoder` | ISO-2 | ISO-2 | Country codes |
| `sivilstandkoder` | ugift, gift, etc. | single, married, etc. | Marital status |
| `sektorkoder` | privat, offentlig | private, public | Employment sector |
| `ansettelsestypekoder` | ansatt, selvstendig | employed, self-employed | Employment type |

## Template Value Syntax

For enum/code fields, templates use the `value` wrapper:

```json
"sex": { "value": ["$nav.bruker.person.kjoenn"] }
```

This indicates the field contains a code that needs mapping.

Plain string fields (no mapping needed):
```json
"forename": "$nav.bruker.person.fornavn"
```
