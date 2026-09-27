# Project guidance for future agents

## Intent

This workspace makes the Condition worksheet in `FHIR MAPPING_DOH-PHIC-JAO-No-2021-002 - Dictionary.xlsx` auditable from **source concepts → reusable FHIR implementation patterns**. The workbook has 34 populated clinical rows in 13 sections; preserve each row and its section even when concepts repeat. The WHO-style Level 3 logical model describes source meaning independently of FHIR decisions. The crosswalk and Sankey then express proposed mappings and open questions. The Sankey is a valued one-page overview: **refine its connections/content rather than replacing its visual form** unless the user asks for a redesign.

## Working habits

- Start with the workbook/source logical model and compare `mindmap-index.json`, `build-condition-mindmap.py`, the main crosswalk (`condition-logical-model.html`), and `condition-row-profile-mindmap.html`. Preserve sidebar navigation and source-row deep links across pages.
- Separate **existing PH Core 0.2.0 artifacts**, **proposed derivatives/canonicals (not live URLs)**, **international examples**, and **unresolved gaps**. Do not claim profile conformance based on base R4 validation. Source terminology examples are not bindings; workbook Terminology Binding cells are empty.
- Model the meaning of an assertion: a Yes/No/unknown answer is not automatically a diagnosis; no Condition is not a negative answer. PWD registration belongs on Patient, encounter symptoms can be Observations, and mortality is proposed as an **Observation** in light of current MDI/VRDR. Keep certification/coding-stage and national policy decisions visible.
- **Always link the terminology source or the policy, inline, as you go** — every SNOMED CT/LOINC concept gets an authoritative link, and every data element gets a link to the current Philippine policy that requires or defines it (issuing body, date, version). Read the policy to enumerate its answer options before proposing any code; if a policy has no stable public URL, cite it by name rather than invent one. Never fill unknowns by inventing bindings, clinical facts, or PH canonical endpoints.
- Prefer exact, source-backed SNOMED CT/LOINC concepts when the **clinical meaning and workflow match**; distinguish question codes from answer/diagnosis codes, and record uncertainties. For example, for disability type, read the current PH PWD policy and list its permitted classifications rather than guessing from SNOMED alone.
- Validate candidate SNOMED CT/LOINC codes with `python validate-terminology-fhirlab.py`, which uses the FHIRLab server `https://tx.fhirlab.net/fhir` as a **temporary** terminology authority and records the code-system **version** and timestamp for every check. Report an unreachable server as unreachable; never claim a version that was not returned. This is a temporary check, not the Philippine national terminology service, and never a binding.
- Preserve small, coherent reusable profile boundaries rather than making a profile per row or disease. Keep dates, time zones, event pairing, provenance and status semantics explicit. Document decisions and unanswered human-review questions.
- Edit the generator for generated index/transaction/embedded diagram data, regenerate, and run `python audit-condition-sankey.py`, `python validate-condition-transactions.py` and, for terminology changes, `python validate-terminology-fhirlab.py`. For source-model changes, first run `python jao-l3-prototype/build_logical_model.py`. For link-rendering changes, open the page in a browser and run `agent-browser eval --stdin < tests/sankey-geometry.js` at desktop/narrow widths and after filtering; the independent static audit cannot establish visible endpoints. Keep the pinned D3 libraries and notices in `vendor/` synchronized with the self-contained HTML. Verify row dialogs, filters and links when the UI changes. `condition-sankey-audit.md` records the latest connection/terminology rationale.

## Useful prompts to frame a new task

- “For this workbook row, what exactly is asserted, where does it occur in the source model, and what would distinguish a question, finding, diagnosis, registration field, or certified mortality statement?”
- “Is the target path an actual R4/PH Core element, a proposed extension/slice/profile, or an unresolved gap? What evidence supports the chosen coding and its processing stage?”
- “Which current Philippine policy enforces this element? Link it; list the permitted response options and compare candidate terminologies even when the workbook contains no code.”
- “If two source rows share a FHIR element, how will users still trace each one back to its original section and review decision?”
- “What was actually validated—base R4 syntax, IG-specific profile constraints, terminology membership, or clinical policy—and what still needs owner approval?”

This guidance is intentionally revisable. Update this file when project scope, evidence or approved requirements change; preserve intent and provenance rather than freezing today's UI or profile choices.
