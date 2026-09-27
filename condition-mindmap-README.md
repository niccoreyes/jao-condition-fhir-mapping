# Source-to-profile Sankey and transaction examples

Open [condition-row-profile-mindmap.html](condition-row-profile-mindmap.html#map). It connects **34** Excel clinical rows to **8 consolidated destinations** and **22 target subpaths** via **45 directed flows**. Shared profiles have one box with multiple subpaths; the proposed encounter, problem and COPD derivatives each have their own box. Unresolved destinations are explicitly marked as gaps. Selecting a row opens its use case, international IG comparison, recommendation, human-review question, and either a synthetic FHIR R4 transaction or an explicit modeling gap. Selecting a subpath shows all rows that share it. This is a proposed implementation mapping, not a published PH Core profile or an approved clinical policy.

## Provenance and reproducibility

- `build-condition-mindmap.py` joins the source logical-model index, the 34-row crosswalk, its reviewed IG discussions, and the row-specific proposal map. It writes `mindmap-index.json`, embeds the data and transactions into the standalone HTML, and creates **30** synthetic `Bundle.type=transaction` examples in `fhir-transactions/`.
- Rebuild: `python jao-l3-prototype/build_logical_model.py && python build-condition-mindmap.py`.
- Connection audit: `python audit-condition-sankey.py` (independent row/subpath expectations). In a browser, `agent-browser eval --stdin < tests/sankey-geometry.js` checks each rendered SVG endpoint against the row and path button borders. Decision rationale and terminology evidence: [condition-sankey-audit.md](condition-sankey-audit.md).
- Local checks: `python validate-condition-transactions.py`. All 30 passed the cached `hl7.fhir.r4.core#4.0.1` JSON schema, unique `urn:uuid` fullUrl checks, POST request URL checks, required structural fields and internal-reference resolution.
- Representative Excel rows **4, 17, 29, 46, 49** were sent to HAPI baseR4 `Bundle/$validate` for a read-only validation operation. Each returned an OperationOutcome with **zero error/fatal issues**. Warnings included absent narratives/Observation performer/effective time, and an unknown PH PWD extension on the public server. This was not an execution of the transaction; no resources were committed.
- No example claims conformance to a proposed PH Core Condition derivative. The proposed profiles are not published, and ICD-10-PH / questionnaire / GOLD terminology bindings are not approved by the workbook.

## Link rendering

The page keeps its existing row/profile layout and highlight interactions. Curves use the [D3 Shape `linkHorizontal` generator](https://d3js.org/d3-shape/link) (pinned d3-shape 3.2.0 and d3-path 3.1.0, BSD-3-Clause; local copies and notices in `vendor/`). The builder inlines these into the HTML so the one-page view works offline. `d3-sankey` is not used because its node layout would replace the already-approved row/profile layout. The SVG is confined to the actual connection corridor; measured row-right and path-left anchors determine its link endpoints. When the layout changes, `ResizeObserver`/resize and filter renders redraw the paths. The independent audit checks membership; the browser test checks *visible geometry*.

## Deliberate non-examples

Excel **5** (disability permanence), **9-10** (proposed mortality Observation pending certification/coding-stage decisions), and **43** (newly/previously diagnosed diabetes) have no approved FHIR mapping/profile. A syntactically valid Bundle for them would not establish the requested clinical meaning. The diagram therefore displays the decision gate and **does not** fabricate a transaction.

All example clinical text, dates and local UUIDs are synthetic. Several examples use text-only CodeableConcepts to demonstrate R4 structure, not terminology interoperability. Excel 25 uses an illustrative ICD-10 coding; it does not bind the proposed PH profile or declare an ICD-10-PH system.
