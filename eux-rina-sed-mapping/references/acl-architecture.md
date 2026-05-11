# ACL Architecture (Anti-Corruption Layer)

The ACL transforms SEDs between NAV internal format and EU RINA format.

## Core Classes

```
no/nav/eux/acl/
├── EessiAcl.java           # Main facade
├── EessiAclHelper.java     # Utility functions
├── SedTemplateContainer.java # Template loading
└── CodesContainer.java     # Kodeverk mappings
```

## Transformation Flow

### NAV → EU (outbound SED)

```
1. Input: NAV SED JSON
   {"nav": {...}, "medlemskap": {...}}
        ↓
2. Flatten JSON (EessiAclHelper.getFlattenedJson)
   {"$nav.bruker.person.fornavn": "Ola", ...}
        ↓
3. Replace codes NAV→EU (EessiAclHelper.replaceCodes)
   "ja" → "1", "m" → "male", etc.
        ↓
4. Load template (SedTemplateContainer)
   A008_v4.4.json → flattened BiMap
        ↓
5. Map paths using inverse template lookup
   $nav.bruker.person.fornavn → Person.PersonIdentification.forename
        ↓
6. Unfold to hierarchical JSON
        ↓
7. Remove empty entries
        ↓
8. Output: EU SED JSON
```

### EU → NAV (inbound SED)

```
1. Input: EU SED JSON from RINA
        ↓
2. Flatten JSON
        ↓
3. Load template (forward lookup)
   Person.PersonIdentification.forename → $nav.bruker.person.fornavn
        ↓
4. Replace codes EU→NAV
   "1" → "ja", "male" → "m", etc.
        ↓
5. Unfold and cleanup
        ↓
6. Output: NAV SED JSON
```

## Key Methods

### EessiAcl.java

```java
// NAV → EU transformation
public String mapNavToEu(String jsonFromNav, String sedVersion) {
    Map<String, Object> flatJson = getFlattenedJson(jsonFromNav);
    replaceCodes(flatJson, NAV_EU, sedType);

    // Get template and inverse map
    Map<String, Object> template = SedTemplateContainer.get(sedType + "_v" + version);
    BiMap<String, String> inverse = getInverseTemplate(template);

    // Transform paths
    Map<String, Object> euFlat = transformPaths(flatJson, inverse);
    return unflatten(euFlat);
}
```

### SedTemplateContainer.java

Templates loaded at startup from `classpath:/sedtemplates/v*/`

```java
// Template storage
static Map<String, String> SED_TEMPLATES;           // Raw JSON
static Map<String, Map<String,Object>> SED_TEMPLATES_FLATTENED;  // Flattened
static Map<String, BiMap<String,String>> SED_TEMPLATES_FLATTENED_BIMAP; // Bidirectional

// Key format: "A008_v4.4"
```

### CodesContainer.java

```java
// Load code mappings from /codes/mappings/*.properties
BiMap<String, String> getCodes(String fieldPath) {
    // Match path ending (ignores array indices)
    // e.g., ".kjoenn" matches "nav.bruker.person.kjoenn"
    String mappingFile = codeMappingConfig.getProperty(pathEnding);
    return loadBiMap("/codes/mappings/" + mappingFile + ".properties");
}
```

## Template Path Patterns

```json
{
  "A008": {
    "Person": {
      "forename": "$nav.bruker.person.fornavn",    // Direct value
      "sex": { "value": ["$nav.bruker.person.kjoenn"] }  // Enum wrapper
    },
    "Employers": [{
      "name": "$nav.arbeidsgiver[x].navn"          // Array with [x]
    }]
  }
}
```

**Prefix meanings:**
- `$nav.` → Maps to `SED.nav.*` object
- `$medlemskap.` → Maps to `SED.medlemskap.*` object
- `[x]` → Array index placeholder

## Array Handling

During transformation, `[x]` is replaced with actual indices:

```
Template:  $nav.arbeidsgiver[x].navn
Flat key:  $nav.arbeidsgiver[0].navn = "Company A"
           $nav.arbeidsgiver[1].navn = "Company B"
```

Regex for index matching: `\[[0-9]{1,4}]`

## Error Handling

```java
enum EessiAclErrorCode {
    SED_STRUCTURAL_ERROR,        // 400: Invalid JSON
    SED_LACKING_TEMPLATE,        // 404: Template not found
    SED_FIELD_DATA_FORMAT_ERROR, // Field transformation failed
    SED_TRANSFORMS_TO_EMPTY,     // 400: Result has no data
    TEMPLATE_ERROR               // Template loading issue
}
```

## EessiAclClient (Service Layer)

Wraps ACL with pre/post processing:

```java
public String fraNavSedTilEuSed(String navSed, String version) {
    // Pre-process: flatten, adjust addresses, ISO codes
    String prepared = preProcess(navSed);

    // Core transformation
    String euSed = eessiAcl.mapNavToEu(prepared, version);

    // Post-process: cleanup
    return postProcess(euSed);
}
```
