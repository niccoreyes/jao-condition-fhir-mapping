# JAO Condition sheet: WHO-style L3 logical model prototype

This is a **local working prototype**, not part of the official PH Core IG and not a WHO-approved DAK. The [interactive logical model](logical-model.html) and [FHIR mapping architecture](../condition-core-reuse-evaluation.html) are separate views.

## Method

Adapted from the [WHO SMART Guidelines Starter Kit 2.0.0 Logical Models](https://smart.who.int/ig-starter-kit/l3_logicalmodels.html), [authoring conventions](https://smart.who.int/ig-starter-kit/authoring_conventions.html), [value-set guidance](https://smart.who.int/ig-starter-kit/l3_valuesets.html) and [versioning guidance](https://smart.who.int/ig-starter-kit/versioning.html). WHO's cited starter kit uses FHIR R5; this prototype serializes a logical StructureDefinition using FHIR R4 4.0.1 to align with PH Core 0.2.0.

- **One workbook tab, one root model:** `JAOConditionSheet`, with 13 source grouping backbones. Each of the 34 populated clinical rows is a distinct leaf field, including repeated concepts in different sections.
- **Source identity:** Each field carries a **local provisional** CodeSystem code (`SRC{SOURCE ROW}`) in `ElementDefinition.code`, plus an Excel cell / source-row mapping. These are **not WHO SMART codes**. `worksheet-index.json` retains the full original definition and labels.
- **Meaning before implementation:** The logical model's names, definitions, provisional types and cardinalities do not inherit from `Condition`, Patient, or any profile. The [row-level FHIR crosswalk](../condition-logical-model.html#/crosswalk) discusses proposed destinations separately. Workbook base/PH mappings are not asserted as approved mappings in the logical StructureDefinition.
- **Reuse:** Section backbones are contained structures. No inheritance from a common logical model or reference to a patient/encounter logical model has been asserted without an approved common glossary. The [architecture page](../condition-core-reuse-evaluation.html#architecture) shows the later FHIR mapping layer.
- **Terminology:** The workbook's Terminology Binding column is blank in all 34 rows. No binding or value-set strength has been fabricated. Any later coded options need terminology stewardship.

## Artifacts

| File | Purpose |
|---|---|
| `input/fsh/models/StructureDefinition/JAOConditionSheet.fsh` | Draft logical model authored as FSH |
| `input/fsh/codeSystems/CodeSystem/JAOConditionSourceRows.fsh` | Local source-row traceability codes; not clinical terminology |
| `fsh-generated/resources/StructureDefinition-JAOConditionSheet.json` | Computable FHIR R4 logical StructureDefinition (`kind=logical`, `derivation=specialization`) |
| `fsh-generated/resources/CodeSystem-JAOConditionSourceRows.json` | Computable source-row CodeSystem |
| `worksheet-index.json` | Workbook-derived source details for the local HTML preview |
| `build_logical_model.py` | Rebuild FSH and source index from the original workbook |

Regenerate from this directory: `python build_logical_model.py && sushi build .`. SUSHI 3.20.0 compiled 1 logical model and 1 CodeSystem with **0 errors**. The 3 warnings are incomplete IG packaging metadata (copyright year, release label, menu), not logical-element errors. Generated files are a prototype; no IG Publisher build or profile-conformance claim was made.

## Approval gates before publication

1. Verify a common glossary and assign approved concept identifiers where available. WHO's unique SMART codes were not supplied and must not be invented.
2. Review **every** provisional `0..1` and datatype against source-owner requirements, including multiplicity, conditionality, question answer types, and the unusual DETECTED ISSUE complications grouping.
3. For coded answers and classifications, establish or reuse governed ValueSets, confirm allowed options, strengthen bindings only where justified, and link terminology via reviewed mappings. The local source-row CodeSystem does **not** replace clinical value sets.
4. Decide which structural mappings are approved before authoring transformation artifacts or PH Core profile derivatives. Underlying cause of death, diagnosis timestamp, permanent disability, and diabetes recency remain unresolved.
5. Reconcile PH Core R4 tooling with WHO R5-based CRMI shareable/publishable criteria before claiming compliance. Replace the `example.org` working canonical only under an authorized publisher. Manage future canonical versions through IG publication, not per-model hardcoding.
