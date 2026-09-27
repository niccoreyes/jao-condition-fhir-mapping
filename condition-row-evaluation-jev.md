# Per-row quality review (Jev / TypeSafe System One)

Model `jev-latest` (served as `jev-1.13.0`) via `https://api.typesafe.ai/v1/systemone`, checked 2026-09-27T06:08:51+00:00. Scope: **this mapping and its evidence**, not clinical truth. Weights are set in `evaluate-rows-jev.py` and combine in code; thresholds pass ≥ 0.75, review ≥ 0.55. Rows below threshold or with low-confidence dimensions are routed to human review.

Composite mean **0.701** across 34 scored rows (0 errors).

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
| 4 | Type of Disability | **0.811** | pass | 0.99/0.97 | 0.98/0.94 | 0.97/0.90 | 0.71/0.61 | 0.47/0.52 | — |
| 5 | With Permanent Disability | **0.710** | review | 0.93/0.78 | 0.88/0.61 | 0.95/0.84 | 0.36/0.44 | 0.55/0.22 | meaning, terminology |
| 7 | COVID-19 | **0.803** | pass | 0.87/0.57 | 0.85/0.56 | 0.98/0.94 | 0.57/0.38 | 0.84/0.48 | meaning, terminology |
| 8 | Date of Onset of Illness | **0.800** | pass | 0.99/0.97 | 0.81/0.74 | 0.88/0.59 | 0.72/0.64 | 0.60/0.53 | — |
| 9 | Underlying Cause of Death (ICD-10) | **0.749** | review | 0.83/0.43 | 0.92/0.74 | 0.84/0.56 | 0.48/0.58 | 0.78/0.28 | traceability, terminology |
| 10 | Underlying Cause of Death Description | **0.676** | review | 0.77/0.24 | 0.83/0.57 | 0.83/0.62 | 0.54/0.55 | 0.49/0.32 | traceability, terminology |
| 12 | Date of Onset of Illness | **0.732** | review | 0.99/0.96 | 0.80/0.73 | 0.71/0.45 | 0.58/0.23 | 0.56/0.54 | policy_options, meaning |
| 13 | History of Other Illness | **0.679** | review | 0.89/0.62 | 0.75/0.85 | 0.87/0.58 | 0.47/0.58 | 0.48/0.40 | terminology |
| 15 | Date of Complication | **0.674** | review | 0.72/0.34 | 0.82/0.74 | 0.81/0.62 | 0.58/0.37 | 0.52/0.56 | traceability, meaning |
| 16 | Time of Complication | **0.712** | review | 0.85/0.50 | 0.81/0.77 | 0.80/0.54 | 0.57/0.28 | 0.57/0.44 | meaning, terminology |
| 17 | Complication | **0.641** | review | 0.74/0.14 | 0.76/0.88 | 0.89/0.62 | 0.49/0.63 | 0.43/0.35 | traceability, terminology |
| 19 | Date of Complication | **0.742** | review | 0.86/0.55 | 0.84/0.68 | 0.82/0.61 | 0.65/0.48 | 0.57/0.54 | meaning |
| 20 | Time of Complication | **0.749** | review | 0.88/0.61 | 0.84/0.65 | 0.79/0.57 | 0.64/0.27 | 0.61/0.49 | meaning, terminology |
| 21 | Complication | **0.622** | review | 0.65/0.00 | 0.82/0.73 | 0.81/0.62 | 0.48/0.71 | 0.48/0.40 | traceability, terminology |
| 23 | Date Diagnosed | **0.639** | review | 0.64/0.00 | 0.80/0.77 | 0.76/0.50 | 0.52/0.08 | 0.58/0.48 | traceability, meaning, terminology |
| 24 | Time Diagnosed | **0.688** | review | 0.85/0.50 | 0.78/0.81 | 0.73/0.43 | 0.53/0.03 | 0.58/0.49 | policy_options, meaning, terminology |
| 25 | Diagnosis Code | **0.620** | review | 0.73/0.09 | 0.59/0.41 | 0.78/0.56 | 0.58/0.51 | 0.45/0.48 | traceability, policy_link, terminology |
| 26 | Diagnosis Description | **0.750** | pass | 0.97/0.92 | 0.78/0.78 | 0.85/0.63 | 0.61/0.50 | 0.55/0.42 | terminology |
| 27 | Diagnosis Remarks | **0.795** | pass | 0.98/0.95 | 0.78/0.84 | 0.81/0.70 | 0.77/0.66 | 0.58/0.47 | terminology |
| 29 | If Pregnancy - Induced Hypertension (Pre - Eclampsia) | **0.681** | review | 0.89/0.61 | 0.33/0.00 | 0.65/0.38 | 0.57/0.64 | 0.85/0.52 | policy_link, policy_options |
| 31 | Disease | **0.764** | pass | 0.98/0.93 | 0.80/0.79 | 0.80/0.57 | 0.77/0.55 | 0.44/0.58 | — |
| 32 | Disease Description | **0.755** | pass | 0.98/0.94 | 0.78/0.81 | 0.87/0.56 | 0.62/0.51 | 0.53/0.45 | terminology |
| 33 | Present Illness | **0.713** | review | 0.89/0.63 | 0.76/0.85 | 0.72/0.50 | 0.66/0.35 | 0.52/0.47 | meaning, terminology |
| 34 | Co-morbidities | **0.691** | review | 0.95/0.84 | 0.81/0.75 | 0.88/0.60 | 0.40/0.36 | 0.51/0.60 | meaning |
| 35 | Pertinent Past Medical History | **0.713** | review | 0.95/0.85 | 0.79/0.78 | 0.84/0.60 | 0.47/0.21 | 0.56/0.45 | meaning, terminology |
| 37 | Pertinent Signs and Symptoms on Admission, Others specify | **0.688** | review | 0.94/0.78 | 0.81/0.75 | 0.83/0.56 | 0.52/0.60 | 0.39/0.39 | terminology |
| 39 | Type of Hypertension | **0.679** | review | 0.95/0.82 | 0.64/0.43 | 0.72/0.21 | 0.54/0.27 | 0.51/0.62 | policy_link, policy_options, meaning |
| 41 | Type of Stroke | **0.698** | review | 0.96/0.86 | 0.73/0.93 | 0.68/0.38 | 0.61/0.45 | 0.47/0.61 | policy_options, meaning |
| 43 | Newly or Previously Diagnosed Diabetes | **0.517** | fail | 0.31/0.76 | 0.79/0.63 | 0.92/0.74 | 0.26/0.83 | 0.59/0.40 | terminology |
| 44 | Type of Diabetes | **0.670** | review | 0.95/0.84 | 0.77/0.63 | 0.60/0.58 | 0.61/0.49 | 0.36/0.39 | meaning, terminology |
| 46 | GOLD Classification | **0.630** | review | 0.90/0.65 | 0.77/0.79 | 0.68/0.59 | 0.50/0.56 | 0.32/0.31 | terminology |
| 47 | COPD Group | **0.634** | review | 0.82/0.42 | 0.77/0.67 | 0.77/0.61 | 0.51/0.53 | 0.35/0.39 | traceability, terminology |
| 48 | Pulmonary Tuberculosis | **0.737** | review | 0.90/0.65 | 0.81/0.79 | 0.72/0.71 | 0.51/0.55 | 0.79/0.30 | terminology |
| 49 | Basis for the final diagnosis of Asthma | **0.658** | review | 0.94/0.79 | 0.76/0.72 | 0.52/0.00 | 0.52/0.58 | 0.51/0.45 | policy_options, terminology |

Cell format is `normalized/confidence` on a 0–1 scale.

## Interpretation

- **1 fail, 26 review, 7 pass.** The single fail is row 43 (Newly or Previously Diagnosed Diabetes) — the policy defines a Newly/Previously answer while the element is still an unmapped gap.
- **Low confidence clusters on `terminology` and `meaning`,** which is expected and correct: many rows are narrative or policy-only and have no candidate code, and several assertions (Yes/No questions, permanence, mortality) are genuinely undecided. Low confidence here is a signal to a human, not a defect to hide.
- **`policy_link` and `policy_options` score highest** where a current issuance with enumerated options exists (for example Type of Disability and COVID-19 case status).
- **Composite is a ranking aid, not a gate for clinical approval.** Every row still needs the named owner decision.
