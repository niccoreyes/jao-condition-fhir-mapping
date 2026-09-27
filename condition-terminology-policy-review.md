# Policy-backed terminology review

This review answers two questions per data element: **which current Philippine policy authorises or defines it**, and **which answer options that policy actually enumerates** — before proposing any SNOMED CT or LOINC concept. Policy citations were read directly and linked. Where no stable public URL could be verified, the issuance is named without an invented link. Nothing here is an approved binding; the workbook's Terminology Binding column remains blank.

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
- PH Core value set (draft) — https://build.fhir.org/ig/UP-Manila-SILab/ph-core/en/ValueSet-ph-core-disability-type-vs.html

## Element-by-element policy basis

| Excel | Element | Policy basis | Policy-defined options |
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
| 29 | PIH / Pre-eclampsia | WHO ICD-10 Ch. XV (O10–O16) | PIH category; pre-eclampsia and eclampsia are distinct |
| 31–35 | Past medical history fields | DOH Hospital HIM Manual | Narrative / code as recorded |
| 37 | Signs and symptoms on admission | DOH Hospital HIM Manual | Includes "Others, specify"; no answer list |
| 39 | Type of Hypertension | PRPWD; DOH PhilPEN (AO 2012-0029) | Subtype; workbook cites ICD-10 I10–I15 as a range |
| 41 | Type of Stroke | DOH AO 2020-0059 (Acute Stroke) | Type; workbook cites ICD-10 I60–I64 as a range |
| 43 | Newly or Previously Diagnosed Diabetes | PRPWD Diabetes Registry Form | Newly diagnosed; previously diagnosed |
| 44 | Type of Diabetes | PRPWD Diabetes Registry Form | Type; workbook cites ICD-10 E10–E14 as a range |
| 46, 47 | GOLD Classification / COPD Group | PRPWD COPD Registry Form; GOLD report | Edition-specific grades/groups (ABCD before 2023, ABE from 2023) |
| 48 | Pulmonary Tuberculosis | DOH AO 2015-0024 (ITIS); DOH AO 2011-0010 | Answer to TB question; national TB guidance distinguishes bacteriologically confirmed, clinically diagnosed, not a case |
| 49 | Basis for Asthma diagnosis | PRPWD | Supporting evidence for the asthma problem |

## Rules applied

- **Cite the policy even when no code exists.** For rows 5, 13, 17, 26, 27, 31–35, 37 and 49 the value is narrative or a local flag; naming the governing manual/registry is the useful outcome, not inventing a code.
- **Policy options outrank candidate codes.** For row 7 the answer set is Suspect/Probable/Confirmed, not a SNOMED disease code; for row 43 it is Newly/Previously diagnosed, not an onset date.
- **Ranges are not codes.** ICD-10 I10–I15, I60–I64 and E10–E14 are ranges. A profile must define the selectable codes, not adopt the range as a value.
- **Edition and version matter.** GOLD ABCD vs ABE, and the ICD-10 edition adopted by DOH, change the permitted values.
- **Do not link what was not verified.** DOH AO 2020-0059, AO 2015-0024, AO 2011-0010 and the Hospital HIM Manual are cited by name because no stable public URL was confirmed during this review.

Unresolved, requiring owner decisions: (1) reconcile PH Core's disability value set with the full PRPWD list; (2) define permanence and its value set; (3) define the diabetes "newly diagnosed" window; (4) confirm the national ICD-10-PH canonical; (5) state the GOLD edition; (6) confirm the certified-vs-coded stage for rows 9–10.
