# NAV SED A008 Examples

## Table of Contents
- [Minimal NAV SED (required fields only)](#minimal-nav-sed)
- [Full NAV SED (all fields)](#full-nav-sed)
- [CDM 4.3 vs 4.4 differences](#cdm-43-vs-44-differences)
- [Resulting RINA SED after ACL transformation](#resulting-rina-sed)

## Minimal NAV SED

Minimum fields to pass XSD validation for A008 "arbeid i flere land":

```json
{
  "sed": "A008",
  "sedVer": "4",
  "sedGVer": "4",
  "nav": {
    "bruker": {
      "person": {
        "fornavn": "Ola",
        "etternavn": "Nordmann",
        "foedselsdato": "1980-01-15",
        "pin": [
          {
            "identifikator": "12345678901",
            "land": "NO"
          }
        ]
      }
    }
  },
  "medlemskap": {
    "formaal": "arbeid_flere_land",
    "bruker": {
      "arbeidiflereland": [
        {
          "bosted": { "land": "NO" }
        }
      ]
    }
  }
}
```

**Why these fields?** XSD requires:
- `Person` block with at least `forename`, `familyName`, `dateBirth`
- `StatesResidence` (minOccurs=1) → needs `medlemskap.bruker.arbeidiflereland[x].bosted.land`

## Full NAV SED

All fields populated for A008 CDM 4.4:

```json
{
  "sed": "A008",
  "sedVer": "4",
  "sedGVer": "4",
  "nav": {
    "bruker": {
      "person": {
        "fornavn": "Ola",
        "etternavn": "Nordmann",
        "foedselsdato": "1980-01-15",
        "kjoenn": "m",
        "fornavnvedfoedsel": "Ola",
        "etternavnvedfoedsel": "Nordmann",
        "statsborgerskap": [
          { "land": "NO" }
        ],
        "foedested": {
          "by": "Oslo",
          "land": "NO",
          "region": "Oslo"
        },
        "pin": [
          {
            "identifikator": "12345678901",
            "land": "NO",
            "institusjonsid": "NO:NAVAT07",
            "institusjonsnavn": "NAV",
            "sektor": "alle"
          }
        ]
      },
      "far": {
        "person": {
          "fornavn": "Per",
          "etternavnvedfoedsel": "Nordmann"
        }
      },
      "mor": {
        "person": {
          "fornavn": "Kari",
          "etternavnvedfoedsel": "Hansen"
        }
      }
    },
    "arbeidsland": [
      {
        "land": "SE",
        "arbeidsgiver": {
          "navn": "Swedish Company AB",
          "adresse": {
            "gate": "Sveavägen 1",
            "by": "Stockholm",
            "postnummer": "11157",
            "land": "SE"
          },
          "identifikator": [
            { "id": "5591234567", "type": "organisasjonsnummer" }
          ]
        },
        "bosted": {
          "adresse": {
            "gate": "Birger Jarlsgatan 10",
            "by": "Stockholm",
            "postnummer": "11145",
            "land": "SE"
          }
        },
        "arbeidssted": [
          {
            "adresse": {
              "gate": "Sveavägen 1",
              "by": "Stockholm",
              "postnummer": "11157",
              "navn": "Main Office"
            }
          }
        ]
      },
      {
        "land": "NO",
        "arbeidsgiver": {
          "navn": "Norsk AS",
          "adresse": {
            "gate": "Karl Johans gate 1",
            "by": "Oslo",
            "postnummer": "0154",
            "land": "NO"
          }
        }
      }
    ],
    "harfastarbeidssted": "ja",
    "eessisak": {
      "institusjonsid": "NO:NAVAT07",
      "institusjonsnummer": "NAV Arbeid og ytelser"
    },
    "ytterligereinformasjon": "Personen pendler mellom NO og SE"
  },
  "medlemskap": {
    "formaal": "arbeid_flere_land",
    "bruker": {
      "arbeidiflereland": [
        {
          "bosted": { "land": "SE" },
          "yrkesaktivitet": { "startdato": "2024-01-01" }
        }
      ]
    }
  }
}
```

## CDM 4.3 vs 4.4 Differences

### arbeidiflereland structure

**CDM 4.3** (single object):
```json
"medlemskap": {
  "bruker": {
    "arbeidiflereland": {
      "bosted": { "land": "SE" },
      "yrkesaktivitet": { "startdato": "2024-01-01" }
    }
  }
}
```

**CDM 4.4** (array):
```json
"medlemskap": {
  "bruker": {
    "arbeidiflereland": [
      {
        "bosted": { "land": "SE" },
        "yrkesaktivitet": { "startdato": "2024-01-01" }
      }
    ]
  }
}
```

### formaal field (new in CDM 4.4)
```json
"medlemskap": {
  "formaal": "arbeid_flere_land"  // or "endringsmelding"
}
```

### Version fields
```json
{
  "sedVer": "4",   // CDM 4.4: "4", CDM 4.3: "1"
  "sedGVer": "4"   // Always "4"
}
```

## Resulting RINA SED

After ACL transformation by eux-rina-api, the minimal NAV SED becomes:

```json
{
  "A008": {
    "Person": {
      "PersonIdentification": {
        "forename": "Ola",
        "familyName": "Nordmann",
        "dateBirth": "1980-01-15",
        "PINPersonInEachInstitution": {
          "PersonalIdentificationNumber": [
            {
              "personalIdentificationNumber": "12345678901",
              "country": { "value": ["NO"] }
            }
          ]
        }
      }
    },
    "PurposeofSED": {
      "InformationWorkingInTwoOrMoreMemberStates": {
        "StatesResidence": {
          "StateResidence": [
            {
              "stateResidence": { "value": ["NO"] }
            }
          ]
        }
      }
    }
  }
}
```

## Kotlin Model Classes (melosys-eessi)

```kotlin
// Root
data class SED(
    var nav: Nav? = null,
    var medlemskap: Medlemskap? = null,
    @JsonProperty("sed") var sedType: String? = null,
    var sedVer: String? = null,
    var sedGVer: String? = null
)

// Nav
data class Nav(
    var bruker: Bruker? = null,
    var arbeidsland: List<Arbeidsland>? = null,
    var arbeidsgiver: List<Arbeidsgiver>? = null,
    var harfastarbeidssted: String? = null,
    var eessisak: EessiSak? = null,
    var ytterligereinformasjon: String? = null
)

// A008 Medlemskap
data class MedlemskapA008(
    var endring: EndringA008? = null,
    var bruker: MedlemskapA008Bruker? = null,
    var formaal: String? = null  // CDM 4.4 only
) : Medlemskap

// CDM 4.4: array
data class MedlemskapA008Bruker(
    var arbeidiflereland: Any? = null  // CDM 4.3: ArbeidIFlereLand, CDM 4.4: List<ArbeidIFlereLand>
)

data class ArbeidIFlereLand(
    var bosted: Bosted? = null,
    var yrkesaktivitet: Yrkesaktivitet? = null
)
```
