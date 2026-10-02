# Policy-backed terminology review

This review tracks the policy named for each data element, its verified or still-unverified answer options, and candidate terminology separately. Some linked documents were not accessible for direct inspection; a link or a workbook definition alone does **not** verify that a form enumerates the displayed choices. Where no stable public URL could be verified, the issuance is named without an invented link. Nothing here is an approved binding; the workbook's Terminology Binding column remains blank.

## Headline finding: the PWD disability list is broader than PH Core's value set

`Type of Disability` (Excel row 4) is governed by **NCDA Administrative Order No. 001, s. 2021** (PWD ID issuance, issued with DOH, DSWD and DILG), and by the **DOH Philippine Registry for Persons with Disabilities (PRPWD)** under **DOH AO No. 2013-0005 / -A / -B**. The current policy enumerates:

| # | NCDA AO 001 s. 2021 / PRPWD v4.0 Type of Disability |
| --- | --- |
| 1 | Deaf / Hard of Hearing |
| 2 | Intellectual Disability |
| 3 | Learning Disability |
| 4 | Mental Disability |
| 5 | Physical Disability (includes orthopedic) |
| 6 | Psychosocial Disability |
| 7 | Speech and Language Impairment |
| 8 | Visual Disability |
| 9 | Cancer (RA 11215) |
| 10 | Rare Disease (RA 10747) |
| — | Others, specify (PRPWD v4.0 form) |

AO 2013-0005-B (PRPWD v4.0) explicitly adds **Cancer** and **Rare Disease** under Type of Disability, consistent with RA 11215, RA 10747 and DILG Memorandum Circular No. 017, s. 2022.

**Gap:** the draft PH Core 0.2.0 value set `ph-core-disability-type-vs` contains only **9** codes — `visual`, `hearing`, `speech`, `physical`, `intellectual`, `learning`, `psychosocial`, `visual-low-vision`, `visual-blindness`. It **omits Mental Disability, Cancer and Rare Disease**, and folds Deaf/Hard of Hearing into a single `hearing` concept. A conformant PH PWD registration therefore cannot yet be coded purely from that value set. This is a profile-content gap for the PH Core authors, not a terminology choice the workbook can make.

- NCDA AO 001 s. 2021 — https://ncda.gov.ph/disability-laws/administrative-orders/ncda-administrative-order-no-001-series-of-2021/
- DOH AO 2013-0005-A — https://ncda.gov.ph/disability-laws/administrative-orders/doh-administrative-order-no-2013-0005-a/
- DOH AO 2013-0005-B (PRPWD v4.0) PDF — https://ncda.gov.ph/wp-content/uploads/2023/07/ao2013-0005-B.pdf
- DILG MC 017 s. 2022 — https://ncda.gov.ph/disability-laws/dilg-memorandum-circular/dilg-memorandum-circular-no-017-series-of-2022/
- PH Core value set (draft CI build) — https://build.fhir.org/ig/UPM-NTHC/ph-core/ValueSet-ph-core-disability-type-vs.html
- PH Core code system (draft CI build) — https://build.fhir.org/ig/UPM-NTHC/ph-core/CodeSystem-ph-core-disability-type-cs.html

## Element-by-element policy basis

The last column includes source definitions and clinical classification context, **not always a verified policy answer list**. In particular, the original Unified Registry Systems AO named in the workbook is not interchangeable with PWD amendments -A/-B; disease-registry form versions and their exact answer lists remain unverified.

| Excel | Element | Named policy/source | Source wording, classification context or verified options |
| --- | --- | --- | --- |
| 4 | Type of Disability | NCDA AO 001 s. 2021; PRPWD v4.0 | The 10 categories above + Others |
| 5 | With Permanent Disability | NCDA AO 001 s. 2021 | Permanence is an eligibility precondition; **no** enumerated value set |
| 7 | COVID-19 case status | DOH AO 2020-0013; DOH DM 2024-0073 | Suspect; Probable; Confirmed; or not a case |
| 8 | Date of Onset of Illness | DOH Hospital HIM Manual | Onset of signs/symptoms |
| 9 | Underlying Cause of Death (ICD-10) | DOH AO 2020-0008 (MCCOD); ICD-10 (DOH/PSA) | Part I causal sequence, lowest used line = underlying cause; Part II contributory |
| 10 | Underlying Cause of Death Description | DOH AO 2020-0008 | Certifier's own wording, best medical opinion |
| 12 | Date of Onset of Illness (COVID-19) | DOH Hospital HIM Manual | Onset of first signs/symptoms |
| 13 | History of Other Illness | DOH Hospital HIM Manual | Presence-of-history question; no answer list published |
| 15, 16 | Complication date / time | DOH Hospital HIM Manual | Date/time the complication occurred (pair them) |
| 17, 21 | Complication | DOH Hospital HIM Manual | Complication experienced; no governed role code list |
| 19, 20 | Complication date / time (COMPLICATIONS) | DOH Hospital HIM Manual | Date/time the complication occurred |
| 23, 24 | Date / Time Diagnosed | DOH Hospital HIM Manual | Clinician diagnosis date/time |
| 25 | Diagnosis Code | ICD-10 as adopted by DOH/PSA | ICD-10 code; national ICD-10-PH canonical not stated |
| 26, 27 | Diagnosis Description / Remarks | DOH Hospital HIM Manual | Free text |
| 29 | PIH / Pre-eclampsia | Workbook: Yes / No/None; WHO ICD-10 Ch. XV (O10–O16) | The workbook responses are separate from the ICD-10 category context; WHO does not define the answer options for this question. |
| 31–35 | Past medical history fields | DOH Hospital HIM Manual | Narrative / code as recorded |
| 37 | Signs and symptoms on admission | DOH Hospital HIM Manual | Includes "Others, specify"; no answer list |
| 39 | Type of Hypertension | Workbook cites DOH AO 2013-0005 (Unified Registry Systems); DOH PhilPEN (AO 2012-0029) | Subtype; ICD-10 I10–I15 is a workbook example range, not a verified form answer list. |
| 41 | Type of Stroke | DOH AO 2020-0059 (Acute Stroke) | Type; workbook cites ICD-10 I60–I64 as a range |
| 43 | Newly or Previously Diagnosed Diabetes | Workbook cites DOH AO 2013-0005 (Unified Registry Systems) | Workbook label says newly/previously; definition says newly/not. Exact form choices and comparison window unverified. |
| 44 | Type of Diabetes | Workbook cites DOH AO 2013-0005 (Unified Registry Systems) | ICD-10 E10–E14 is a workbook example range, not a verified form answer list. |
| 46, 47 | GOLD Classification / COPD Group | Workbook cites DOH AO 2013-0005; GOLD report (edition unverified) | Classification axes and edition-dependent ABCD/ABE context; source form values unverified. |
| 48 | Pulmonary Tuberculosis | DOH AO 2015-0024 (ITIS); DOH AO 2011-0010 | Workbook asks if patient has pulmonary TB; TB case classifications are separate, not established answers to this question. |
| 49 | Basis for Asthma diagnosis | Workbook cites DOH AO 2013-0005 (Unified Registry Systems) | No verified disease-form annex or answer list; PWD amendments do not establish asthma options. |

## Enumerated option and candidate comparison (dialog data)

The generated row dialogs separate source-labelled options from terminology candidates; none are bindings. Candidate validation metadata is copied verbatim from `terminology-validation.json` (FHIRsmith, checked 2026-09-27; SNOMED CT International 20250201 / LOINC 2.82). Concept links use SNOMED CT identifiers or LOINC pages. An empty candidate list explicitly means no candidate was proposed/checked, not that no code exists.

| Row | Policy/form options recorded | Candidate comparison (role; status) | Existing PH Core / gap |
|---|---|---|---|
| 4 | NCDA AO 001 s.2021 / PRPWD v4.0: Deaf/Hard of Hearing; Intellectual; Learning; Mental; Physical (incl. orthopedic); Psychosocial; Speech and Language Impairment; Visual; Cancer; Rare Disease; Others, specify | SNOMED [105719004](https://snomed.info/id/105719004) broad finding; [21134002](https://snomed.info/id/21134002) disability finding; [161048004](https://snomed.info/id/161048004) registration status; [161045001](https://snomed.info/id/161045001) severity finding — all FHIRsmith checked | Existing 9-code `ph-core-disability-type-vs`; omits Mental/Cancer/Rare Disease and folds Deaf/Hard of Hearing into hearing. |
| 5 | Permanence is a policy precondition; no policy value list | SNOMED [6934004](https://snomed.info/id/6934004) Permanent qualifier — checked, not a disability assertion | No permanence element/value set. |
| 7 | Suspect; Probable; Confirmed; not a case (explicit negative) | SNOMED [840539006](https://snomed.info/id/840539006) COVID-19 diagnosis — checked, not question/answer code | No case-status answer codes established. |
| 9–10 | Part I causal sequence (lowest used line underlying), Part II contributing conditions; certifier wording and duration/interval | LOINC [69453-9](https://loinc.org/69453-9) US certificate Part I; [80359-3](https://loinc.org/80359-3) manual underlying; [80358-5](https://loinc.org/80358-5) automated underlying — checked, stage-dependent *question* codes; row 10 has no candidate | Certifier vs later coding stage unresolved; candidates not interchangeable. |
| 29 | Workbook: Yes; No/None. WHO O10–O16 distinguishes PIH/pre-eclampsia/eclampsia but does not supply question answers. | SNOMED [398254007](https://snomed.info/id/398254007) pre-eclampsia — checked, narrower than PIH and not a yes/no answer | No answer/negative code. |
| 39, 41, 44 | Hypertension I10–I15; stroke I60–I64; diabetes E10–E14 are workbook ranges, not selectable code lists | No specific code proposed or checked | National ICD-10-PH system/canonical and subtype details unresolved; AO 2020-0059 URL unverified (name only). |
| 43 | Workbook: “newly or previously” label; “newly ... or not” definition. Registry form options not verified. | No candidate proposed or checked | “Newly” comparison window and data element undecided. |
| 46–47 | GOLD spirometric grade and group are separate axes; source form choices/edition unverified. | No candidates proposed or checked | Edition-specific scale values not established; GOLD cited by name without a verified URL. |
| 48 | Workbook: “Does the patient have Pulmonary Tuberculosis?”; its answer options are not enumerated. National TB case classifications are separate. | SNOMED [154283005](https://snomed.info/id/154283005) pulmonary tuberculosis disorder — checked, not the question/negative answer | AO 2011-0010 remains name-only; A15–A16 is a range, not a code. |
| Other populated rows | Policy/workbook meaning displayed as source text; explicit “no enumerated answer list” where reviewed source establishes none | No row-specific code proposed or checked unless listed above | No candidate checked ≠ no code exists; HIM Manual URL is human-use-only (HTTP 403 to automation). |

## Rules applied

- **Cite the policy even when no code exists.** For rows 5, 13, 17, 26, 27, 31–35, 37 and 49 the value is narrative or a local flag; naming the cited manual or original registry policy and marking unverified form attribution is better than inventing a code.
- **Source options outrank candidate codes.** For row 7 the policy case categories are Suspect/Probable/Confirmed, not a SNOMED disease code. For row 43 the workbook label says Newly/Previously but the definition says Newly/Not; the registry form choices have not been verified. Neither is an onset date.
- **Ranges are not codes.** ICD-10 I10–I15, I60–I64 and E10–E14 are ranges. A profile must define the selectable codes, not adopt the range as a value.
- **Edition and version matter.** GOLD ABCD vs ABE, and the ICD-10 edition adopted by DOH, change the permitted values.
- **Link the source, or say why there is none.** A workbook deep link is not a link to a policy. For disease-registry rows citing the original DOH AO 2013-0005, no verified stable link to the applicable original form was found; -A/-B are PWD amendments, not evidence for their options. DOH AO No. 2015-0024 (ITIS) is linked through the official NTP library — https://ntp.doh.gov.ph/download/ao2015-0024/. The Hospital HIM Manual is linked to its DOH publication — http://ehealth.doh.gov.ph/nehehrsv/sys/assets/HOSPITAL%20HEALTH%20INFORMATION%20MANAGEMENT%20MANUAL%20formerly%20HOSPITAL%20MEDICAL%20RECORDS%20MANAGEMENT%20MANUAL.pdf — but that host answers automated requests with HTTP 403, so the link is offered for human use and was not fetch-verified. DOH AO No. 2020-0059 (Acute Stroke) and DOH AO No. 2011-0010 (FHSIS reporting) also remain name-only, because no stable public URL was confirmed.

## Terminology validation (HL7 FHIRsmith)

Candidate SNOMED CT and LOINC concepts are checked against the public **HL7 FHIRsmith** server, `https://tx.fhir.org/r4`, with the community FHIRLab server as a fallback. Run:

```bash
python validate-terminology.py
```

The script performs `CodeSystem/$lookup` (falling back to `$validate-code`) for each candidate, writes `terminology-validation.json`, and **records the server used and the code-system version it returned** alongside the `checkedAt` timestamp. Version is recorded deliberately: a concept valid in one SNOMED CT or LOINC release may not exist in another, and SNOMED GPS is only a subset of the International Edition.

Last recorded run (all listed candidates returned valid) against `https://tx.fhir.org/r4`; checked date and individual version are stored in `terminology-validation.json`:

| Row | Code | System version returned | Display |
| --- | --- | --- | --- |
| 4 | [SNOMED CT 105719004](https://snomed.info/id/105719004) | International 20250201 | Body disability AND/OR failure state |
| 4 | [SNOMED CT 21134002](https://snomed.info/id/21134002) | International 20250201 | Disability |
| 4 | [SNOMED CT 161048004](https://snomed.info/id/161048004) | International 20250201 | Registered disabled |
| 4 | [SNOMED CT 161045001](https://snomed.info/id/161045001) | International 20250201 | Disability - severe |
| 5 | [SNOMED CT 6934004](https://snomed.info/id/6934004) | International 20250201 | Permanent |
| 7 | [SNOMED CT 840539006](https://snomed.info/id/840539006) | International 20250201 | COVID-19 |
| 29 | [SNOMED CT 398254007](https://snomed.info/id/398254007) | International 20250201 | Pre-eclampsia |
| 48 | [SNOMED CT 154283005](https://snomed.info/id/154283005) | International 20250201 | Pulmonary tuberculosis |
| 9 | [LOINC 69453-9](https://loinc.org/69453-9) | 2.82 | Cause of death [US Standard Certificate of Death] |
| 9 | [LOINC 80359-3](https://loinc.org/80359-3) | 2.82 | Cause of death.underlying [Manual] |
| 9 | [LOINC 80358-5](https://loinc.org/80358-5) | 2.82 | Cause of death.underlying [Automated] |

These are terminology-membership checks by a public server, not the Philippine national terminology service and not a binding. Rows with no candidate code were not sent for validation.

Unresolved, requiring owner decisions: (1) reconcile PH Core's disability value set with the full PRPWD list; (2) define permanence and its value set; (3) define the diabetes "newly diagnosed" window; (4) confirm the national ICD-10-PH canonical; (5) state the GOLD edition; (6) confirm the certified-vs-coded stage for rows 9–10; (7) choose the durable terminology service and pin its editions.
