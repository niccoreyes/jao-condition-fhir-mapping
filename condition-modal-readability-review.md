# Row-modal readability and actionability review

**Scope:** `condition-row-profile-mindmap.html` row details (34 source rows). This is presentation and reviewer workflow quality, **not** clinical validity, profile conformance, terminology approval, or PHCDI endorsement.

## Independent Pi-subagent reviews

Two fresh Luna read-only reviewers inspected the markup, project guidance and rendered row 43 desktop/mobile screenshots. A third fresh Luna reviewer checked the changed code and Jev outputs after implementation. The initial DeepSeek V4.1 Flash lane failed at launch with a provider `401 invalid API key`; it produced **no review or edit**. The failed workflow was stopped before its writer ran; the Luna-only workflow performed the review and implementation.

| Finding | Before | Change made |
| --- | --- | --- |
| Decision is buried | The entire comparable-IG column precedes the recommendation/review question on mobile (row 43 was ~2,813 px of content). | Row-specific recommendation and **unresolved human-review question** lead the modal. No approve/submit control was added. |
| Long-document navigation | No shortcuts to separate source, PHCDI, terminology and transaction evidence. | Four keyboard-operable in-dialog jumps now appear **before** the detailed Jev score, plus new-tab links to the verbatim workbook crosswalk and independent source logical element so the modal remains open. Jumps focus the section while preserving the row deep-link hash. |
| Evidence competes with action | IG precedent occupied the first column and the Jev score was nested within the warning panel. | IG precedent is a labelled native disclosure. Score is a separate block below the quick-action links; detailed source, PHCDI and terminology retain their full-width sections. |
| Modal/focus risk | Long content relied on implicit scrolling; row selected from a profile subpath could replace its originating member button. | Explicit contained modal scrolling, sticky Close, section scroll offsets and focus restoration to the original profile path or stable search fallback. |
| Historical interpretation | PHCDI comparison could be mistaken for a clinical recommendation. | It remains a separate descriptive, source-row-linked historical comparison with an explicit non-authority notice. |

## Jev presentation ratings

`evaluate-modal-readability-jev.py` uses **one batched System One request per iteration** with six independent 0–4 Score questions. The code normalizes and weights them; pass requires both overall ≥0.75 and action/navigation ≥0.75. Full probabilities and confidence are retained in [`modal-readability-before-jev.json`](modal-readability-before-jev.json) and [`modal-readability-jev.json`](modal-readability-jev.json).

| Presentation dimension | Before | Revised | Revised confidence |
| --- | ---: | ---: | ---: |
| Scanability | 0.735 | 0.938 | 0.79 |
| Decision visibility | 0.635 | 0.900 | 0.67 |
| Navigation | 0.458 | 0.955 | 0.85 |
| Source/PHCDI separation | 0.807 | 0.927 | 0.76 |
| Mobile/accessibility (described design) | 0.542 | 0.760 | **0.51 — near low-confidence boundary** |
| Action clarity | 0.945 | 0.973 | 0.91 |
| **Weighted composite** | **0.700 · review** | **0.917 · pass** | — |

Jev scores markup and supplied row examples, **not pixels, screen readers, medical correctness or permission to approve a mapping**. Before/after snapshots use the same rubric in the script, but the original request payload and rubric hash were not saved; treat the numerical delta as **directional**, not a controlled reproducibility claim. The mobile dimension remains the weakest and near the low-confidence boundary, so browser and assistive-technology review remains necessary rather than being concealed by the composite.

## Browser and deterministic checks

- Chromium at 1280 px: 45/45 Sankey flows connected, 0 detached/reversed. Question-profile filter: 10/10 connected. Row 23 jump focused PHCDI without changing `#row-23`; target heading cleared the sticky header. A profile-path → member row → Escape sequence returned focus to the original profile-path button.
- At 390 px: row 43's unresolved question **and all four jumps are visible in the initial modal viewport**; jump to terminology focuses a visible target and retains `#row-43`. Escape returns focus to row 43. All 34 paired mobile rows remain visible; no page-level horizontal overflow.
- At 320 px: row 49 modal remains inside the viewport, scrollable, with four jumps and no page-level horizontal overflow.
- Axe on sampled desktop/mobile dialogs: **zero reported violations**, with one **incomplete** contrast assessment on each run. This is not a contrast pass for that element, nor an assistive-technology certification.
- Static suite: `python -m unittest discover -s tests -p 'test_*.py'`; semantic/layout audit: `python audit-condition-sankey.py`; transaction schema/reference check: `python validate-condition-transactions.py`. No row meaning or terminology code changed; the mapping-row Jev and terminology membership results were not rerun for this presentation-only pass.

## Remaining improvement opportunities

1. **Manual screen-reader and high-text-zoom review.** The mobile/accessibility Jev dimension passed narrowly with low confidence; test headings, jump announcement, source links and long terminology-table scrolling in VoiceOver/TalkBack and at 200% text zoom. Never use the axe zero-violation count as a substitute.
2. **Quality-review density.** The full per-dimension score block is still long, especially for rows 43 and 49. If user testing shows reviewers skip later evidence, consider a compact score summary with the detailed bars in an accessible disclosure; re-run `evaluate-quality-review-design.py` because it currently expects visible bars.
3. **Long policy/candidate detail.** Row 4's eleven disability choices and 13 code rows remain vertically lengthy. Consider a source-preserving, accessible table/list navigation aid only if reviewers need it; do not hide missing codes or policy gaps to improve a score.
4. **Evidence handoff.** The modal offers source and crosswalk links but does not record approval, assign an owner, or export a review decision. Add workflow tooling only after an owner defines decision states and provenance; a cosmetic approval button would be misleading.
