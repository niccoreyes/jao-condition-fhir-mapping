# Per-row quality review (Jev / TypeSafe System One)

Model `jev-latest` (served as `jev-1.13.0`) via `https://api.typesafe.ai/v1/systemone`, checked 2026-09-27T06:29:11+00:00. Scope: **this mapping and its evidence**, not clinical truth. Weights are set in `evaluate-rows-jev.py` and combine in code; thresholds pass ≥ 0.75, review ≥ 0.55. Rows below threshold or with low-confidence dimensions are routed to human review.

Composite mean **0.703** across 34 scored rows (0 errors).

## Dimensions and weights

| Dimension | Weight | What it asks |
| --- | --- | --- |
| traceability | 0.25 | Traced to one source element and one destination, section preserved |
| policy_link | 0.15 | Cites the current PH policy that governs the element |
| policy_options | 0.15 | States the policy-defined answer options, or their absence |
| meaning | 0.25 | Respects the assertion type (question/finding/diagnosis/registration/mortality) |
| terminology | 0.2 | Terminology soundness and no invented bindings |

## Scores

| Row | Element | Composite | Verdict | Trace | Policy link | Options | Meaning | Term | Low-confidence dimensions |
|---|---|---|---|---|---|---|---|---|---|
| 4 | Type of Disability | **0.838** | pass | 0.98/0.95 | 0.97/0.92 | 0.97/0.92 | 0.67/0.58 | 0.66/0.00 | terminology |
| 5 | With Permanent Disability | **0.775** | pass | 0.94/0.81 | 0.87/0.60 | 0.95/0.83 | 0.37/0.41 | 0.87/0.57 | meaning |
| 7 | COVID-19 | **0.798** | pass | 0.85/0.52 | 0.85/0.52 | 0.98/0.93 | 0.55/0.45 | 0.86/0.54 | meaning |
| 8 | Date of Onset of Illness | **0.805** | pass | 0.99/0.97 | 0.82/0.71 | 0.89/0.62 | 0.73/0.62 | 0.58/0.55 | — |
| 9 | Underlying Cause of Death (ICD-10) | **0.733** | review | 0.77/0.21 | 0.93/0.77 | 0.87/0.57 | 0.47/0.60 | 0.77/0.23 | traceability, terminology |
| 10 | Underlying Cause of Death Description | **0.662** | review | 0.72/0.08 | 0.84/0.55 | 0.85/0.58 | 0.53/0.59 | 0.48/0.31 | traceability, terminology |
| 12 | Date of Onset of Illness | **0.739** | review | 0.99/0.97 | 0.79/0.75 | 0.73/0.49 | 0.59/0.29 | 0.57/0.54 | policy_options, meaning |
| 13 | History of Other Illness | **0.679** | review | 0.89/0.63 | 0.75/0.87 | 0.89/0.63 | 0.45/0.52 | 0.49/0.43 | terminology |
| 15 | Date of Complication | **0.686** | review | 0.75/0.36 | 0.81/0.75 | 0.81/0.61 | 0.59/0.40 | 0.53/0.51 | traceability, meaning |
| 16 | Time of Complication | **0.713** | review | 0.85/0.52 | 0.81/0.76 | 0.81/0.56 | 0.56/0.25 | 0.58/0.40 | meaning, terminology |
| 17 | Complication | **0.633** | review | 0.72/0.08 | 0.76/0.89 | 0.89/0.62 | 0.49/0.66 | 0.41/0.28 | traceability, terminology |
| 19 | Date of Complication | **0.719** | review | 0.81/0.35 | 0.82/0.72 | 0.82/0.58 | 0.61/0.35 | 0.59/0.45 | traceability, meaning, terminology |
| 20 | Time of Complication | **0.737** | review | 0.88/0.59 | 0.85/0.62 | 0.73/0.47 | 0.64/0.28 | 0.60/0.45 | policy_options, meaning, terminology |
| 21 | Complication | **0.635** | review | 0.66/0.00 | 0.80/0.77 | 0.84/0.62 | 0.49/0.68 | 0.50/0.45 | traceability, terminology |
| 23 | Date Diagnosed | **0.636** | review | 0.65/0.00 | 0.80/0.76 | 0.77/0.47 | 0.49/0.16 | 0.57/0.50 | traceability, policy_options, meaning |
| 24 | Time Diagnosed | **0.669** | review | 0.78/0.27 | 0.78/0.78 | 0.74/0.46 | 0.52/0.06 | 0.58/0.48 | traceability, policy_options, meaning, terminology |
| 25 | Diagnosis Code | **0.618** | review | 0.71/0.03 | 0.57/0.37 | 0.79/0.58 | 0.58/0.50 | 0.46/0.55 | traceability, policy_link |
| 26 | Diagnosis Description | **0.759** | pass | 0.98/0.94 | 0.80/0.78 | 0.85/0.61 | 0.63/0.55 | 0.55/0.48 | terminology |
| 27 | Diagnosis Remarks | **0.799** | pass | 0.98/0.93 | 0.78/0.85 | 0.82/0.67 | 0.78/0.65 | 0.60/0.44 | terminology |
| 29 | If Pregnancy - Induced Hypertension (Pre - Eclampsia) | **0.686** | review | 0.90/0.65 | 0.34/0.14 | 0.64/0.39 | 0.57/0.65 | 0.87/0.57 | policy_link, policy_options |
| 31 | Disease | **0.763** | pass | 0.98/0.93 | 0.79/0.78 | 0.79/0.53 | 0.76/0.53 | 0.46/0.55 | — |
| 32 | Disease Description | **0.758** | pass | 0.98/0.94 | 0.78/0.84 | 0.88/0.59 | 0.63/0.53 | 0.53/0.46 | terminology |
| 33 | Present Illness | **0.712** | review | 0.88/0.61 | 0.77/0.84 | 0.73/0.54 | 0.65/0.26 | 0.52/0.45 | meaning, terminology |
| 34 | Co-morbidities | **0.709** | review | 0.96/0.88 | 0.82/0.69 | 0.87/0.58 | 0.45/0.43 | 0.52/0.58 | meaning |
| 35 | Pertinent Past Medical History | **0.717** | review | 0.94/0.79 | 0.80/0.79 | 0.85/0.55 | 0.50/0.10 | 0.56/0.49 | meaning, terminology |
| 37 | Pertinent Signs and Symptoms on Admission, Others specify | **0.691** | review | 0.94/0.78 | 0.82/0.73 | 0.85/0.56 | 0.52/0.62 | 0.39/0.32 | terminology |
| 39 | Type of Hypertension | **0.689** | review | 0.95/0.83 | 0.65/0.42 | 0.76/0.20 | 0.55/0.28 | 0.52/0.60 | policy_link, policy_options, meaning |
| 41 | Type of Stroke | **0.706** | review | 0.96/0.87 | 0.73/0.93 | 0.69/0.34 | 0.62/0.50 | 0.48/0.62 | policy_options |
| 43 | Newly or Previously Diagnosed Diabetes | **0.514** | fail | 0.32/0.74 | 0.77/0.65 | 0.93/0.77 | 0.27/0.80 | 0.56/0.42 | terminology |
| 44 | Type of Diabetes | **0.672** | review | 0.95/0.84 | 0.77/0.63 | 0.59/0.59 | 0.60/0.45 | 0.39/0.38 | meaning, terminology |
| 46 | GOLD Classification | **0.632** | review | 0.89/0.64 | 0.77/0.75 | 0.68/0.60 | 0.53/0.55 | 0.30/0.27 | terminology |
| 47 | COPD Group | **0.636** | review | 0.82/0.40 | 0.80/0.68 | 0.77/0.60 | 0.52/0.52 | 0.32/0.34 | traceability, terminology |
| 48 | Pulmonary Tuberculosis | **0.738** | review | 0.87/0.56 | 0.80/0.82 | 0.75/0.72 | 0.51/0.51 | 0.81/0.35 | terminology |
| 49 | Basis for the final diagnosis of Asthma | **0.644** | review | 0.92/0.73 | 0.75/0.74 | 0.49/0.00 | 0.52/0.58 | 0.49/0.43 | policy_options, terminology |

Cell format is `normalized/confidence` on a 0–1 scale.
## Interpretation

- **1 fail, 25 review, 8 pass.** The fail is row 43 (Newly or Previously Diagnosed Diabetes) — the policy defines a Newly/Previously answer while the element is still an unmapped gap.
- **Low confidence clusters on `terminology` and `meaning`,** which is expected: many rows are narrative or policy-only with no candidate code, and several assertions are genuinely undecided. Low confidence is a signal to a human, not a defect to hide.
- **`policy_link` and `policy_options` score highest** where a current issuance with enumerated options exists (for example Type of Disability, COVID-19 case status).
- **Composite is a ranking aid, not a gate for clinical approval.** Every row still needs the named owner decision.
