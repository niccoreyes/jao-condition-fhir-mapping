// One provisional local identifier per populated clinical worksheet row.
// These identifiers MUST NOT be described as WHO SMART codes.
CodeSystem: JAOConditionSourceRows
Id: JAOConditionSourceRows
Title: "JAO Condition worksheet source row identifiers"
Description: "Local traceability identifiers for the JAO Condition worksheet. Not a clinical terminology or WHO concept registry."
* ^status = #draft
* ^experimental = true
* ^content = #complete

* #SRC8 "Type of Disability" "Excel row 4; SOURCE ROW 8; section MASTER PERSON DATA"
* #SRC9 "With Permanent Disability" "Excel row 5; SOURCE ROW 9; section MASTER PERSON DATA"
* #SRC129 "COVID-19" "Excel row 7; SOURCE ROW 129; section ENCOUNTER LOG"
* #SRC136 "Date of Onset of Illness" "Excel row 8; SOURCE ROW 136; section ENCOUNTER LOG"
* #SRC147 "Underlying Cause of Death (ICD-10)" "Excel row 9; SOURCE ROW 147; section ENCOUNTER LOG"
* #SRC148 "Underlying Cause of Death Description" "Excel row 10; SOURCE ROW 148; section ENCOUNTER LOG"
* #SRC202 "Date of Onset of Illness" "Excel row 12; SOURCE ROW 202; section COVID-19"
* #SRC210 "History of Other Illness" "Excel row 13; SOURCE ROW 210; section COVID-19"
* #SRC300 "Date of Complication" "Excel row 15; SOURCE ROW 300; section DETECTED ISSUE"
* #SRC301 "Time of Complication" "Excel row 16; SOURCE ROW 301; section DETECTED ISSUE"
* #SRC302 "Complication" "Excel row 17; SOURCE ROW 302; section DETECTED ISSUE"
* #SRC322 "Date of Complication" "Excel row 19; SOURCE ROW 322; section COMPLICATIONS"
* #SRC323 "Time of Complication" "Excel row 20; SOURCE ROW 323; section COMPLICATIONS"
* #SRC324 "Complication" "Excel row 21; SOURCE ROW 324; section COMPLICATIONS"
* #SRC333 "Date Diagnosed" "Excel row 23; SOURCE ROW 333; section DIAGNOSIS"
* #SRC334 "Time Diagnosed" "Excel row 24; SOURCE ROW 334; section DIAGNOSIS"
* #SRC336 "Diagnosis Code" "Excel row 25; SOURCE ROW 336; section DIAGNOSIS"
* #SRC337 "Diagnosis Description" "Excel row 26; SOURCE ROW 337; section DIAGNOSIS"
* #SRC338 "Diagnosis Remarks" "Excel row 27; SOURCE ROW 338; section DIAGNOSIS"
* #SRC418 "If Pregnancy - Induced Hypertension (Pre - Eclampsia)" "Excel row 29; SOURCE ROW 418; section PREGNANCY"
* #SRC744 "Disease" "Excel row 31; SOURCE ROW 744; section PAST MEDICAL HISTORY"
* #SRC745 "Disease Description" "Excel row 32; SOURCE ROW 745; section PAST MEDICAL HISTORY"
* #SRC746 "Present Illness" "Excel row 33; SOURCE ROW 746; section PAST MEDICAL HISTORY"
* #SRC747 "Co-morbidities" "Excel row 34; SOURCE ROW 747; section PAST MEDICAL HISTORY"
* #SRC748 "Pertinent Past Medical History" "Excel row 35; SOURCE ROW 748; section PAST MEDICAL HISTORY"
* #SRC793 "Pertinent Signs and Symptoms on Admission, Others specify" "Excel row 37; SOURCE ROW 793; section PERTINENT SIGNS & SYMPTOMS ON ENCOUNTER"
* #SRC898 "Type of Hypertension" "Excel row 39; SOURCE ROW 898; section DISEASE REGISTRY - HYPERTENSION"
* #SRC908 "Type of Stroke" "Excel row 41; SOURCE ROW 908; section DISEASE REGISTRY - STROKE"
* #SRC917 "Newly or Previously Diagnosed Diabetes" "Excel row 43; SOURCE ROW 917; section DISEASE REGISTRY - DIABETES MELLITUS"
* #SRC918 "Type of Diabetes" "Excel row 44; SOURCE ROW 918; section DISEASE REGISTRY - DIABETES MELLITUS"
* #SRC927 "GOLD Classification" "Excel row 46; SOURCE ROW 927; section DISEASE REGISTRY - CHRONIC OBSTRUCTIVE PULMONARY DISEASE"
* #SRC928 "COPD Group" "Excel row 47; SOURCE ROW 928; section DISEASE REGISTRY - CHRONIC OBSTRUCTIVE PULMONARY DISEASE"
* #SRC933 "Pulmonary Tuberculosis" "Excel row 48; SOURCE ROW 933; section DISEASE REGISTRY - CHRONIC OBSTRUCTIVE PULMONARY DISEASE"
* #SRC934 "Basis for the final diagnosis of Asthma" "Excel row 49; SOURCE ROW 934; section DISEASE REGISTRY - CHRONIC OBSTRUCTIVE PULMONARY DISEASE"
