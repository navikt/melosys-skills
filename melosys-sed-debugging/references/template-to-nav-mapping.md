# A008 v4.4 Template: NAV ↔ RINA Field Mapping

Complete mapping from the eux-rina-api template `A008_v4.4.json`.

## Table of Contents
- [Person Identification](#person-identification)
- [PIN (Personal ID Numbers)](#pin-personal-id-numbers)
- [Nationality](#nationality)
- [Birth Info and Parents](#birth-info-and-parents)
- [Competent Institution](#competent-institution)
- [Work in Multiple States (PurposeofSED)](#work-in-multiple-states)
- [Change Notification](#change-notification)
- [Additional Information](#additional-information)

## Person Identification

| NAV SED path | RINA path | Required |
|-------------|-----------|----------|
| `$nav.bruker.person.fornavn` | `Person.PersonIdentification.forename` | Yes |
| `$nav.bruker.person.etternavn` | `Person.PersonIdentification.familyName` | Yes |
| `$nav.bruker.person.foedselsdato` | `Person.PersonIdentification.dateBirth` | Yes |
| `$nav.bruker.person.kjoenn` | `Person.PersonIdentification.sex.value` | No |
| `$nav.bruker.person.etternavnvedfoedsel` | `Person.PersonIdentification.familyNameAtBirth` | No |
| `$nav.bruker.person.fornavnvedfoedsel` | `Person.PersonIdentification.forenameAtBirth` | No |

**Code mappings for sex:** `m` → `male`, `k` → `female`, `u` → `unknown`

## PIN (Personal ID Numbers)

| NAV SED path | RINA path |
|-------------|-----------|
| `$nav.bruker.person.pin[x].identifikator` | `Person.PersonIdentification.PINPersonInEachInstitution.PersonalIdentificationNumber[x].personalIdentificationNumber` |
| `$nav.bruker.person.pin[x].land` | `...PersonalIdentificationNumber[x].country.value` |
| `$nav.bruker.person.pin[x].sektor` | `...PersonalIdentificationNumber[x].sector.value` |
| `$nav.bruker.person.pin[x].institusjonsid` | `...PersonalIdentificationNumber[x].Institution.institutionID` |
| `$nav.bruker.person.pin[x].institusjonsnavn` | `...PersonalIdentificationNumber[x].Institution.institutionName` |

## Nationality

| NAV SED path | RINA path |
|-------------|-----------|
| `$nav.bruker.person.statsborgerskap[x].land` | `Person.AdditionalInformationPerson.nationality.value` |

## Birth Info and Parents

| NAV SED path | RINA path |
|-------------|-----------|
| `$nav.bruker.person.foedested.by` | `...IfPINNotProvidedForEveryInstitutionPleaseProvide.PlaceBirth.town` |
| `$nav.bruker.person.foedested.land` | `...IfPINNotProvidedForEveryInstitutionPleaseProvide.PlaceBirth.country.value` |
| `$nav.bruker.person.foedested.region` | `...IfPINNotProvidedForEveryInstitutionPleaseProvide.PlaceBirth.region` |
| `$nav.bruker.mor.person.fornavn` | `...IfPINNotProvidedForEveryInstitutionPleaseProvide.forenameMother` |
| `$nav.bruker.mor.person.etternavnvedfoedsel` | `...IfPINNotProvidedForEveryInstitutionPleaseProvide.motherFamilyNameAtBirth` |
| `$nav.bruker.far.person.fornavn` | `...IfPINNotProvidedForEveryInstitutionPleaseProvide.forenameFather` |
| `$nav.bruker.far.person.etternavnvedfoedsel` | `...IfPINNotProvidedForEveryInstitutionPleaseProvide.fatherFamilyNameAtBirth` |

## Competent Institution

| NAV SED path | RINA path |
|-------------|-----------|
| `$nav.eessisak.institusjonsid` | `CompetentInstitutionIfDiffersFromSending.institutionID` |
| `$nav.eessisak.institusjonsnummer` | `CompetentInstitutionIfDiffersFromSending.institutionName` |

## Work in Multiple States

Parent: `A008.PurposeofSED.InformationWorkingInTwoOrMoreMemberStates`

**XSD element order within this parent:**
1. StatesResidence
2. IdentificationEmployers
3. IdentificationSelfEmployment
4. PlaceWork

### StatesResidence (REQUIRED - minOccurs=1)

| NAV SED path | RINA path |
|-------------|-----------|
| `$medlemskap.bruker.arbeidiflereland[x].bosted.land` | `StatesResidence.StateResidence[x].stateResidence.value` |
| `$medlemskap.bruker.arbeidiflereland[x].yrkesaktivitet.startdato` | `StatesResidence.StateResidence[x].startDateActivities` |
| `$nav.arbeidsland[x].bosted.adresse.gate` | `StatesResidence.StateResidence[x].Address.street` |
| `$nav.arbeidsland[x].bosted.adresse.by` | `StatesResidence.StateResidence[x].Address.town` |
| `$nav.arbeidsland[x].bosted.adresse.postnummer` | `StatesResidence.StateResidence[x].Address.postalCode` |
| `$nav.arbeidsland[x].bosted.adresse.region` | `StatesResidence.StateResidence[x].Address.region` |
| `$nav.arbeidsland[x].bosted.adresse.bygning` | `StatesResidence.StateResidence[x].Address.buildingName` |
| `$nav.arbeidsland[x].bosted.adresse.land` | `StatesResidence.StateResidence[x].Address.country.value` |

**Key insight:** `stateResidence` comes from `$medlemskap` while the address comes from `$nav.arbeidsland[x].bosted`.

### IdentificationEmployers (optional)

| NAV SED path | RINA path |
|-------------|-----------|
| `$nav.arbeidsland[x].arbeidsgiver.navn` | `IdentificationEmployers.Employer[x].name` |
| `$nav.arbeidsland[x].arbeidsgiver.adresse.gate` | `IdentificationEmployers.Employer[x].Address.street` |
| `$nav.arbeidsland[x].arbeidsgiver.adresse.by` | `IdentificationEmployers.Employer[x].Address.town` |
| `$nav.arbeidsland[x].arbeidsgiver.adresse.postnummer` | `IdentificationEmployers.Employer[x].Address.postalCode` |
| `$nav.arbeidsland[x].arbeidsgiver.adresse.region` | `IdentificationEmployers.Employer[x].Address.region` |
| `$nav.arbeidsland[x].arbeidsgiver.adresse.bygning` | `IdentificationEmployers.Employer[x].Address.buildingName` |
| `$nav.arbeidsland[x].arbeidsgiver.adresse.land` | `IdentificationEmployers.Employer[x].Address.country.value` |
| `$nav.arbeidsland[x].arbeidsgiver.identifikator[x].id` | `IdentificationEmployers.Employer[x].IdentificationNumbers.IdentificationNumber[x].number` |
| `$nav.arbeidsland[x].arbeidsgiver.identifikator[x].type` | `IdentificationEmployers.Employer[x].IdentificationNumbers.IdentificationNumber[x].type.value` |

### IdentificationSelfEmployment (optional)

| NAV SED path | RINA path |
|-------------|-----------|
| `$nav.arbeidsland[x].selvstendig.navn` | `IdentificationSelfEmployment.SelfEmployment[x].name` |
| `$nav.arbeidsland[x].selvstendig.adresse.*` | `IdentificationSelfEmployment.SelfEmployment[x].Address.*` |
| `$nav.arbeidsland[x].selvstendig.identifikator[x].id` | `...SelfEmployment[x].IdentificationNumbers.IdentificationNumber[x].number` |
| `$nav.arbeidsland[x].selvstendig.identifikator[x].type` | `...SelfEmployment[x].IdentificationNumbers.IdentificationNumber[x].type.value` |

### PlaceWork (optional)

| NAV SED path | RINA path |
|-------------|-----------|
| `$nav.arbeidsland[x].land` | `PlaceWork.CountriesWork[x].countryWork.value` |
| `$nav.arbeidsland[x].arbeidssted[x].adresse.navn` | `PlaceWork.CountriesWork[x].PlaceWork.PlaceWork[x].companyNameVesselName` |
| `$nav.arbeidsland[x].arbeidssted[x].adresse.gate` | `PlaceWork.CountriesWork[x].PlaceWork.PlaceWork[x].Address.street` |
| `$nav.arbeidsland[x].arbeidssted[x].adresse.by` | `PlaceWork.CountriesWork[x].PlaceWork.PlaceWork[x].Address.town` |
| `$nav.arbeidsland[x].arbeidssted[x].adresse.postnummer` | `...PlaceWork[x].Address.postalCode` |
| `$nav.arbeidsland[x].arbeidssted[x].adresse.region` | `...PlaceWork[x].Address.region` |
| `$nav.arbeidsland[x].arbeidssted[x].adresse.bygning` | `...PlaceWork[x].Address.buildingName` |
| `$nav.arbeidsland[x].arbeidssted[x].adresse.hjemmebase` | `PlaceWork.CountriesWork[x].PlaceWork.PlaceWork[x].flagStatehomeBase` |
| `$nav.harfastarbeidssted` | `PlaceWork.aFixedPlaceWorkExistsIndicator.value` |

## Change Notification

Parent: `A008.PurposeofSED.NotificationChangesInRelevantData`

| NAV SED path | RINA path |
|-------------|-----------|
| `$medlemskap.endring.fornavn` | `Person.forename` |
| `$medlemskap.endring.etternavn` | `Person.familyName` |
| `$medlemskap.endring.adresse.gate` | `Address.street` |
| `$medlemskap.endring.adresse.by` | `Address.town` |
| `$medlemskap.endring.adresse.postnummer` | `Address.postalCode` |
| `$medlemskap.endring.adresse.region` | `Address.region` |
| `$medlemskap.endring.adresse.bygning` | `Address.buildingName` |
| `$medlemskap.endring.adresse.land` | `Address.country.value` |
| `$medlemskap.endring.arbeidssted.adresse.*` | `PlaceWorkInHostCountry.Address.*` |
| `$medlemskap.endring.arbeidssted.navn` | `PlaceWorkInHostCountry.companyNameVesselName` |
| `$medlemskap.endring.periode.startdato` | `ChangeInPeriod.actualStartingDate` |
| `$medlemskap.endring.periode.sluttdato` | `ChangeInPeriod.actualEndDate` |
| `$medlemskap.endring.ihhtparagraf` | `ChangeInPeriod.periodChange.value` |
| `$medlemskap.endring.trerikraftfra` | `changeEffectiveFrom` |
| `$medlemskap.kansellering.heleperioden.EESSIYesNoType` | `Cancellation.cancellationWholePeriod.value` |

## Additional Information

| NAV SED path | RINA path |
|-------------|-----------|
| `$nav.ytterligereinformasjon` | `AdditionalInformation.additionalInformation` |
