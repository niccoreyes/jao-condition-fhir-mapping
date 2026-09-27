#!/usr/bin/env python3
"""Rebuild the draft WHO-style L3 logical model from the Condition worksheet.

The local source-row codes, types, and cardinalities are provisional. This script
never edits the workbook or the upstream PH Core implementation guide.
"""
from pathlib import Path
import json
import openpyxl

ROOT = Path(__file__).resolve().parent
WORKBOOK = ROOT.parent / "FHIR MAPPING_DOH-PHIC-JAO-No-2021-002 - Dictionary.xlsx"

# One logical model for the Condition tab. Repeated concepts remain separate
# in their original worksheet sections. These camelCase names are *local* names,
# not WHO SMART codes or FHIR resource element names.
GROUPS = [
    ("MASTER PERSON DATA", "masterPersonData"),
    ("ENCOUNTER LOG", "encounterLog"),
    ("COVID-19", "covid19"),
    ("DETECTED ISSUE", "detectedIssue"),
    ("COMPLICATIONS", "complications"),
    ("DIAGNOSIS", "diagnosis"),
    ("PREGNANCY", "pregnancy"),
    ("PAST MEDICAL HISTORY", "pastMedicalHistory"),
    ("PERTINENT SIGNS & SYMPTOMS ON ENCOUNTER", "signsSymptomsOnEncounter"),
    ("DISEASE REGISTRY - HYPERTENSION", "hypertensionRegistry"),
    ("DISEASE REGISTRY - STROKE", "strokeRegistry"),
    ("DISEASE REGISTRY - DIABETES MELLITUS", "diabetesRegistry"),
    ("DISEASE REGISTRY - CHRONIC OBSTRUCTIVE PULMONARY DISEASE", "copdRegistry"),
]

# Excel physical row -> distinct logical field / provisional FHIR datatype.
# A date and time remain separate in the source model; the FHIR crosswalk may
# combine them into one Condition dateTime only after confirming equivalence.
FIELDS = {
    4: ("disabilityType", "CodeableConcept"),
    5: ("permanentDisability", "boolean"),
    7: ("covid19CaseStatus", "CodeableConcept"),
    8: ("illnessOnsetDate", "date"),
    9: ("underlyingCauseOfDeathCode", "CodeableConcept"),
    10: ("underlyingCauseOfDeathDescription", "string"),
    12: ("illnessOnsetDate", "date"),
    13: ("otherIllnessHistory", "CodeableConcept"),
    15: ("complicationDate", "date"),
    16: ("complicationTime", "time"),
    17: ("complication", "CodeableConcept"),
    19: ("complicationDate", "date"),
    20: ("complicationTime", "time"),
    21: ("complication", "CodeableConcept"),
    23: ("diagnosedDate", "date"),
    24: ("diagnosedTime", "time"),
    25: ("diagnosisCode", "CodeableConcept"),
    26: ("diagnosisDescription", "string"),
    27: ("diagnosisRemarks", "string"),
    29: ("pregnancyInducedHypertensionAnswer", "CodeableConcept"),
    31: ("disease", "CodeableConcept"),
    32: ("diseaseDescription", "string"),
    33: ("presentIllness", "string"),
    34: ("comorbidities", "CodeableConcept"),
    35: ("pertinentPastHistory", "string"),
    37: ("otherSignsSymptoms", "string"),
    39: ("hypertensionType", "CodeableConcept"),
    41: ("strokeType", "CodeableConcept"),
    43: ("diabetesDiagnosisRecency", "CodeableConcept"),
    44: ("diabetesType", "CodeableConcept"),
    46: ("goldClassification", "CodeableConcept"),
    47: ("copdGroup", "CodeableConcept"),
    48: ("pulmonaryTuberculosisAnswer", "CodeableConcept"),
    49: ("asthmaDiagnosisBasis", "string"),
}

def quoted(value):
    """A safe FSH string literal; preserve wording while flattening Excel breaks."""
    value = " ".join(str(value).split())
    return json.dumps(value, ensure_ascii=False)

def source_num(value):
    return str(int(value)) if isinstance(value, (int, float)) and value == int(value) else str(value)

sheet = openpyxl.load_workbook(WORKBOOK, read_only=True, data_only=True)["Condition"]
groups = dict(GROUPS)
active_section = None
rows = []
for cells in sheet.iter_rows(min_row=3, values_only=False):
    row = cells[0].row
    label = cells[4].value
    if not label:
        continue
    if row not in FIELDS:
        if label in groups:
            active_section = label
        else:
            raise ValueError(f"Unexpected worksheet row {row}: {label}")
        continue
    if not active_section:
        raise ValueError(f"No section for Excel row {row}")
    local_name, datatype = FIELDS[row]
    rows.append(dict(excel=row, section=active_section, group=groups[active_section],
                     name=local_name, datatype=datatype, label=label,
                     definition=cells[9].value or "Definition missing in worksheet.",
                     definition_source=cells[10].value,
                     source_id=source_num(cells[0].value),
                     number=source_num(cells[1].value),
                     terminology_binding=cells[3].value))
assert {item['excel'] for item in rows} == set(FIELDS), "Missing or unexpected clinical rows"
assert len(rows) == 34 and len({item['section'] for item in rows}) == 13
assert len({item['source_id'] for item in rows}) == 34
assert all(item['terminology_binding'] is None for item in rows)

header = '''// WHO L3 logical-model method adapted to the JAO Condition worksheet.
// This is a WORKING PROTOTYPE, not an approved WHO DAK or PH Core artifact.
// Source codes are local provisional identifiers, NOT WHO SMART codes.
// Worksheet cardinalities and answer value sets are not supplied; 0..1 is
// provisional for source fields. Review repeatability, requiredness and types.
// This model is source/implementation independent. FHIR paths live in the
// separate mapping crosswalk; no PH Core profile rules are inherited here.
Logical: JAOConditionSheet
Id: JAOConditionSheet
Title: "JAO Condition worksheet logical data model"
Description: "Draft data structure for all 34 populated clinical rows in the JAO Condition worksheet, organized by its 13 source sections. Not a FHIR Condition profile."
* ^status = #draft
* ^experimental = true
* ^purpose = "Preserve source concepts and row identifiers independently of FHIR resource choices; support review of cardinality, terminology, and mapping."
* ^mapping[+].identity = "worksheet"
* ^mapping[=].uri = "urn:jao:condition-worksheet"
* ^mapping[=].name = "JAO Condition worksheet coordinates"
'''
model = [header]
for label, group in GROUPS:
    model.append(f'* {group} 0..1 BackboneElement {quoted(label)} {quoted("Grouping from the Condition worksheet; not a separate FHIR resource or assertion.")}')
    section_rows = [r for r in rows if r['section'] == label]
    for r in section_rows:
        path = f"{group}.{r['name']}"
        source_id = f"SRC{r['source_id']}"
        model.append(f'* {path} 0..1 {r["datatype"]} {quoted(r["label"])} {quoted(r["definition"])}')
        model.append(f'* {path} ^code[0] = JAOConditionSourceRows#{source_id} {quoted(r["label"])}')
        model.append(f'* {path} ^mapping[+].identity = "worksheet"')
        coordinate = f"Condition!E{r['excel']}; SOURCE ROW {r['source_id']}; NO {r['number']}"
        model.append(f'* {path} ^mapping[=].map = {quoted(coordinate)}')
        comment = "Source terminology binding blank. Cardinality and datatype are provisional pending source-owner review."
        if r['definition_source']:
            comment += ' Source of definition (worksheet): ' + r['definition_source']
        model.append(f'* {path} ^comment = {quoted(comment)}')
        model.append('')

code_lines = ['''// One provisional local identifier per populated clinical worksheet row.
// These identifiers MUST NOT be described as WHO SMART codes.
CodeSystem: JAOConditionSourceRows
Id: JAOConditionSourceRows
Title: "JAO Condition worksheet source row identifiers"
Description: "Local traceability identifiers for the JAO Condition worksheet. Not a clinical terminology or WHO concept registry."
* ^status = #draft
* ^experimental = true
* ^content = #complete
''']
for r in rows:
    provenance = f"Excel row {r['excel']}; SOURCE ROW {r['source_id']}; section {r['section']}"
    code_lines.append(f'* #SRC{r["source_id"]} {quoted(r["label"])} {quoted(provenance)}')

model_file = ROOT / 'input/fsh/models/StructureDefinition/JAOConditionSheet.fsh'
codes_file = ROOT / 'input/fsh/codeSystems/CodeSystem/JAOConditionSourceRows.fsh'
model_file.parent.mkdir(parents=True, exist_ok=True)
codes_file.parent.mkdir(parents=True, exist_ok=True)
model_file.write_text('\n'.join(model) + '\n')
codes_file.write_text('\n'.join(code_lines) + '\n')
(ROOT / 'worksheet-index.json').write_text(json.dumps(rows, indent=2, ensure_ascii=False) + '\n')
# Keep the standalone file:// preview in sync with source and FSH after rebuild.
page = ROOT / 'logical-model.html'
if page.exists():
    html = page.read_text()
    prefix, tail = html.split('const ROWS=', 1)
    old_rows, suffix = tail.split(';\nconst GROUP_ORDER=', 1)
    if not old_rows.startswith('['):
        raise ValueError('Unexpected logical-model.html data segment')
    embedded = json.dumps(rows, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    page.write_text(prefix + 'const ROWS=' + embedded + ';\nconst GROUP_ORDER=' + suffix)
print(f'Built {len(rows)} source elements in {len(GROUPS)} groups; generated FSH, worksheet-index.json and preview data')
