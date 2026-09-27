# Scoping review: how PWD is captured as Condition or Observation, with IDs and permanence

**Question.** In FHIR R4, how are Persons with Disabilities (PWD) represented — as a Condition, an Observation, a Patient extension, or an assessment — and how are the PWD **identifier** and **permanence** associated with that representation?

**Scope.** International HL7/US/AU guidance, the HL7 core extensions registry, and current Philippine policy (NCDA and DOH). Focus on the two workbook rows that touch this: **Excel 4** (`Type of Disability`) and **Excel 5** (`With Permanent Disability`).

**Method.** Targeted (non-systematic) scoping review: source pages and IG profiles read directly and linked inline; candidate SNOMED CT concepts validated on the public HL7 FHIRsmith server (`https://tx.fhir.org/r4`) with the returned code-system version recorded. No binding is asserted. This follows the project rule to link the source or say why there is none.

---

## 1. There is no dedicated "Disability" resource

FHIR R4 has no `Disability` resource. Disability is modelled along four patterns that answer different questions. The choice is driven by **what is being asserted**, not by the word "disability".

| Pattern | FHIR shape | What it asserts | Typical use |
| --- | --- | --- | --- |
| A. Patient attribute | `Patient.extension` (CodeableConcept) | "This person has disability type X" as a durable patient characteristic | Registration / administrative profile |
| B. Observation | `Observation` with a disability `code` and coded/boolean `value` | "This disability status was assessed and is yes/no/severity" | Survey or screening assessment, point-in-time finding |
| C. Condition | `Condition` (`category = problem-list-item`) | "This impairment/problem is being managed clinically" | Longitudinal clinical problem list |
| D. QuestionnaireResponse / assessment scale | `QuestionnaireResponse`, or `Observation` panel | The **answers to a standard disability question set** | Structured data collection (ASC/ACS six-item set) |

### A. Patient-level extension (administrative / registration)

- **PH Core 0.2.0** models PWD registration on **Patient**, not Condition: `ph-core-pwd-disability` at `https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-pwd-disability` (context `Patient`). It is a complex extension with four optional sub-extensions:
  - `pwdId` — Value[x] = **string** ("PWD ID Number")
  - `disabilityType` — Value[x] = **CodeableConcept** (bound to `ph-core-disability-type-vs`)
  - `idExpirationDate` — Value[x] = **date**
  - `issuingLGU` — Value[x] = **CodeableConcept** ("Issuing LGU (Barangay)")
  - All four are `0..1`; the parent is `0..*`. There is **no permanence element**.
  Source (draft CI): https://build.fhir.org/ig/UPM-NTHC/ph-core/StructureDefinition-ph-core-pwd-disability.html
- **HL7 core extension `patient-disability`** (`http://hl7.org/fhir/StructureDefinition/patient-disability`), Trial-use, maturity 3, context `Patient`, `0..*`, `value[x]` = CodeableConcept. This is the generic HL7 equivalent of a patient disability attribute.
  https://hl7.org/fhir/extensions/5.2.0/StructureDefinition-patient-disability.html
- **QI-Core** binds a disability **value set** to that extension: `qicore-patient-disability`, "concept is-a 105719004 |Body disability AND/OR failure state|" (97 concepts in the US edition).
  https://hl7.org/fhir/us/qicore/STU4.1.1/ValueSet-qicore-patient-disability.html

### B. Observation (assessment / status)

- **US Public Health Disability Status** (`us-ph-disability-status`) is an **Observation**, derived from US Core Simple Observation. It fixes `category` to `disability-status`, requires `Observation.code` bound to a Disability Status Assessment value set, and requires `Observation.value[x]` bound to Yes/No/Unknown/Not asked. The assessed content is the **six-item ACS disability question set** (hearing, vision, cognition, mobility, self-care, independent living), with age thresholds.
  https://hl7.org/fhir/us/ph-library/en/StructureDefinition-us-ph-disability-status.html
- The **C-CDA 5.0** equivalent is a `DisabilityStatusObservation` template that may hold an `AssessmentScaleObservation` for the same six items.
  http://hl7.org/cda/us/ccda/5.0.0/StructureDefinition-DisabilityStatusObservation.html

Key modelling point: in pattern B the disability question set produces an **answer** (yes/no/unknown/not asked). That is not the same as a diagnosis, and a missing Observation is not a "No".

### C. Condition (clinical problem)

`Condition` remains the right resource when a **clinician asserts and manages** an impairment, with `category = problem-list-item`, a `code`, `clinicalStatus`, and `onset[x]`. PH Core's general Condition profile leaves `code` at `0..1` with the inherited **example** binding, so it does not by itself carry a disability classification.
https://hl7.org/fhir/R4/condition.html · PH Core Condition FSH (draft): https://build.fhir.org/ig/UPM-NTHC/ph-core/StructureDefinition-ph-core-condition.html

### D. Assessment scale / questionnaire

The six-item set can also be captured as `QuestionnaireResponse`, or an `Observation` panel with `hasMember`/`derivedFrom`. C-CDA explicitly allows an `AssessmentScaleObservation` inside the disability template (link above).

**Synthesis.** PH Core's choice (extension on Patient for the **registration** fact; Condition for a **managed clinical problem**; Observation for an **assessment answer**) is consistent with international practice. Do not collapse them: a PWD registration category is not a diagnosis, and an assessment answer is not a problem-list item.

---

## 2. The PH disability type list is broader than the PH Core value set

Current Philippine policy enumerates the disability types. **NCDA Administrative Order No. 001, s. 2021** lists: deaf/hard of hearing, Intellectual, learning, mental, orthopedic, physical, psychosocial, speech and language impairment, visual, people with cancer (RA 11215), and people with rare disease (RA 10747).
https://ncda.gov.ph/disability-laws/administrative-orders/ncda-administrative-order-no-001-series-of-2021/

**DOH AO No. 2013-0005-B** adds Cancer and Rare Disease to the PRPWD Type of Disability field (PRPWD v4.0 form):
https://ncda.gov.ph/wp-content/uploads/2023/07/ao2013-0005-B.pdf
Also **DILG Memorandum Circular No. 017, s. 2022**: https://ncda.gov.ph/disability-laws/dilg-memorandum-circular/dilg-memorandum-circular-no-017-series-of-2022/

**Draft PH Core 0.2.0** `ph-core-disability-type-cs` has only **9** codes — `visual`, `hearing`, `speech`, `physical`, `intellectual`, `learning`, `psychosocial`, `visual-low-vision`, `visual-blindness`:
https://build.fhir.org/ig/UPM-NTHC/ph-core/CodeSystem-ph-core-disability-type-cs.html

| NCDA AO 001 s.2021 / PRPWD v4.0 | PH Core 0.2.0 code present? |
| --- | --- |
| Deaf / Hard of Hearing | Partly (`hearing`, merged) |
| Intellectual | Yes |
| Learning | Yes |
| Mental | **No** |
| Physical (incl. orthopedic) | Yes |
| Psychosocial | Yes |
| Speech and Language Impairment | Yes |
| Visual | Yes (+ low-vision, blindness) |
| Cancer (RA 11215) | **No** |
| Rare Disease (RA 10747) | **No** |
| Others, specify | n/a |

**Gap:** a registration that legally lists Mental, Cancer or Rare Disease cannot be coded from `ph-core-disability-type-vs` as it stands. This is a profile-content defect for the PH Core authors, not a mapping choice for this workbook.

---

## 3. Associating the PWD ID

An identifier is a **business identifier**, not a clinically coded value, so it belongs on an `Identifier`, with system, type, value, period and assigner — not buried in free text.

**What the identifier is.** Per NCDA AO 001 s. 2021 and the DOH PRPWD v4.0 form, the PWD ID number format is `RR-PPMM-BBB-NNNNNNN` (region, province/city, barangay, sequential), the card is valid for **five (5) years**, and it is issued by the city/municipality through the PDAO/C/MSWDO or by NCDA. PH Core's extension stores it as a plain `string` (`pwdId`) plus `issuingLGU` and `idExpirationDate`.

**Options:**

| Option | Where | Pros | Cons |
| --- | --- | --- | --- |
| Extension only (current PH Core) | `Patient.extension:pwdDisability.extension:pwdId` (string) | Matches the published draft; groups registration fields together | Not searchable as an identifier; type/system/period not expressed; duplicates the identifier elsewhere |
| `Patient.identifier` (+ keep extension context) | `Patient.identifier` with `system`, `type`, `value`, `period.end`, `assigner` | Standard identity semantics, searchable (`identifier=`), supports `period` = 5-year validity, `assigner` = LGU | Requires a PH-defined `system`/`NamingSystem` and a type code |
| Both, with one authority | Extension holds registration category; `identifier` holds the number | Separates the legal identifier from the registration attributes | Requires a rule to prevent divergence |

**Recommendation.** Express the PWD number as `Patient.identifier` (system-owned, with `period.end` for the 5-year expiry and `assigner` for the LGU), and keep the extension for the **registration attributes** (`disabilityType`, `issuingLGU`) plus a reference to the identifier. At minimum, PH Core 0.2.0's `pwdId` should change from `string` to `Identifier` so type, system and validity can be carried. PH Core already ships `NamingSystem` resources (e.g. PhilSys, PhilHealth) to model exactly this kind of national identifier.
Reference: FHIR R4 Patient identifier — https://hl7.org/fhir/R4/patient.html

---

## 4. Capturing permanence

**Policy context.** NCDA AO 001 s. 2021 restricts PWD ID issuance to *permanent* disabilities, and the PRPWD separates two axes: **Type of Disability** and **Cause of Disability** (Congenital/Inborn, Acquired, Chronic illness, Injury, …). Permanence is therefore a policy-relevant attribute, but it is **not** the same as clinical status or abatement.

**Options considered:**

| Option | Representation | Assessment |
| --- | --- | --- |
| Infer from `Condition.abatement[x]` absent | nothing stored | **Reject.** Absence is not permanence; an active condition may be curable. |
| `Condition.clinicalStatus` | `active`/`recurrence`/`remission`/`resolved` | Describes the **problem's** activity, not permanence of disability. |
| SNOMED CT qualifier `6934004 |Permanent|` | attach to a finding/extension CodeableConcept | Valid concept (see §5), but as a bare qualifier it needs a finding to qualify. |
| Dedicated coded element | extension `CodeableConcept` = Permanent / Temporary / Unknown / Not assessed | **Preferred.** Explicit, testable, and separable from clinical status. |
| Reuse `idExpirationDate` | date | A 5-year card expiry is **not** permanence. |

**Recommendation.** Add a small PH Core extension (or a coded component on the existing PWD extension) for **permanence**, e.g. `permanent | temporary | unknown | not-assessed`, with provenance: who attested it (`attester`/`asserter`), when, and from which certificate of disability. Never derive it from a missing `abatement`, an empty answer, or a card expiry date. If policy requires "Yes/No" only, still allow an explicit **Unknown** — a documented "No" and an unanswered question are different facts.

---

## 5. Terminology validated on HL7 FHIRsmith

Checked with `python validate-terminology.py` against `https://tx.fhir.org/r4` (primary). SNOMED CT **International Edition 20250201**; LOINC **2.82**. Membership only — not a binding.

| Concept | Code | Display |
| --- | --- | --- |
| Disability umbrella | SNOMED CT 105719004 | Body disability AND/OR failure state |
| Disability (general) | SNOMED CT 21134002 | Disability |
| Registered disabled | SNOMED CT 161048004 | Registered disabled |
| Disability – severe | SNOMED CT 161045001 | Disability – severe |
| Permanence qualifier | SNOMED CT 6934004 | Permanent |

Notes: `161048004 |Registered disabled|` is the closest administrative concept but is a **status/finding**, not the PWD registration category; the PH list is a jurisdictional classification and should stay in `ph-core-disability-type-cs`. `6934004 |Permanent|` is a **qualifier value**, usable only with a finding, which is why a dedicated coded element is preferred over embedding it in a diagnosis.

---

## 6. Recommendations for this workbook

1. **Row 4 (`Type of Disability`)** — keep on **Patient** as in PH Core, but treat the value set as **incomplete**: it must be reconciled with the NCDA AO 001 s. 2021 / PRPWD v4.0 list (add Mental, Cancer, Rare Disease; decide whether `deaf/hard of hearing` is one concept or two). Candidate SNOMED concepts are documented, not bound.
2. **Row 5 (`With Permanent Disability`)** — model as an **explicit coded permanence attribute with provenance**, or as a separate Observation if policy treats it as an assessed status; do **not** infer it from `Condition.abatement`, missing data, or the ID expiry date. Add an explicit `unknown`/`not-assessed` value.
3. **PWD ID** — represent as `Patient.identifier` (system, type, value, `period.end`, `assigner`) rather than only a free-text `string`; keep the extension for registration attributes.
4. **Separation of concerns** — registration category (Patient extension) ≠ clinical problem (`Condition`) ≠ assessment answer (`Observation`/`QuestionnaireResponse`, "No" ≠ missing).

## 7. Open questions for owners

- Does Philippine policy treat cancer and rare disease as permanent for PWD eligibility, or only as PWD-eligible conditions? (The PRPWD form lists them under Type of Disability; the "permanent" precondition in NCDA AO 001 s. 2021 is separate.)
- Who is the authoritative issuer and verifier of the PWD number for FHIR: LGU/PDAO, DOH PRPWD, or NCDA mirror?
- Which PH identifier `system`/`NamingSystem` should back the PWD number, and how is it reconciled with PhilSys/PhilHealth identifiers already in PH Core?
- Does the national model want a "temporary disability" value at all, or is disability always permanent by policy?

*Reviewed against PH Core 0.2.0 (draft) and, for international comparison only, US Public Health, QI-Core, C-CDA, and the HL7 core extensions registry. No PH Core profile conformance is claimed.*
