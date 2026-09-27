#!/usr/bin/env python3
"""Build synthetic R4 transaction examples and a standalone row-to-profile mind map.

This does not publish or validate proposed PH Core profiles. Examples are
synthetic, checked against the local FHIR R4 JSON schema plus transaction rules.
"""
from pathlib import Path
import json
import re
import uuid
import subprocess

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'fhir-transactions'
OUT.mkdir(exist_ok=True)

# 34 unique rows; destinations are design proposals, not claims about PH Core 0.2.0.
# (profile group, candidate FHIR element, clinical use case, example pattern)
MAP = {
  4: ('patient','Patient.extension:pwdDisability.extension:disabilityType.valueCodeableConcept','Register a PWD disability type on the person record, separate from any managed medical problem.','patient'),
  5: ('pwdGap','Patient.extension:pwdDisability (permanence not defined)','Record a legal/administrative permanence answer only after its meaning and extension are defined.',None),
  7: ('question','Observation.code + Observation.valueCodeableConcept','Record the explicit COVID-19 case-status answer, including a negative answer; a positive clinical diagnosis is a separate Condition.','answer'),
  8: ('encounter','Condition.onsetDateTime','Capture onset of the encounter-linked illness, not encounter start or system record time.','encounter'),
  9: ('mortality','Observation.code + Observation.valueCodeableConcept.coding (underlying cause; proposed)','Represent a coded underlying cause on a mortality Observation; select certifier-asserted versus manual/automated coding workflow before fixing the LOINC question code.',None),
 10: ('mortality','Observation.code + Observation.valueCodeableConcept.text (cause text; proposed)','Preserve the verbatim cause description on the corresponding mortality Observation, without treating text as a coded result or inventing a causal sequence.',None),
 12: ('problem','Condition.onsetDateTime (inherited R4 element)','Record when COVID illness signs or symptoms first appeared, only when attached to an asserted Condition. Use the problem derivative only if longitudinally managed.','problem'),
 13: ('question','Observation.code + Observation.valueCodeableConcept','Record the explicit history-of-other-illness answer; if a named illness is separately established, represent that diagnosis on its own Condition.','answer'),
 15: ('encounter','Condition.onsetDateTime (date from row 15; time from row 16)','Combine complication date and time for one asserted encounter complication, after source grouping is confirmed.','encounter'),
 16: ('encounter','Condition.onsetDateTime (time with row 15 date)','Record the time component of the same complication onset; a time alone is not a FHIR dateTime.','encounter'),
 17: ('encounter','Condition.code + Encounter.diagnosis.condition','Record a diagnosed complication in encounter context; do not send an ungoverned complication role code.','encounter'),
 19: ('encounter','Condition.onsetDateTime (date from row 19; time from row 20)','Capture onset of the COMPLICATIONS-section event without deduplicating its separate workbook trace.','encounter'),
 20: ('encounter','Condition.onsetDateTime (time with row 19 date)','Pair this clock time with the date of the same complication before constructing a timestamp.','encounter'),
 21: ('encounter','Condition.code + Encounter.diagnosis.condition','Assert the COMPLICATIONS-section diagnosis as a Condition linked to an Encounter if clinically established.','encounter'),
 23: ('encounter','Condition.extension:assertedDate (candidate)','Record the date of clinician assertion rather than system creation if that is what “Date Diagnosed” means.','asserted'),
 24: ('encounter','Condition.extension:assertedDate (candidate; paired time)','Combine diagnosed date and time into one offset-bearing assertion timestamp; never publish a time-only dateTime.','asserted'),
 25: ('encounter','Condition.code.coding / Condition.code.text','Exchange the encounter diagnosis code and its display; a PH code system and binding remain a governance task.','encounter'),
 26: ('encounter','Condition.code.text','Keep a clinician-entered diagnosis description with its diagnosis code on the same Condition.','encounter'),
 27: ('encounter','Condition.note.text','Add contextual diagnosis remarks as an Annotation, not as a hidden coded qualifier.','encounter'),
 29: ('question','Observation.code + Observation.valueCodeableConcept','Capture a Yes/No/None pre-eclampsia or PIH question; a confirmed positive diagnosis may have a separate Condition.','answer'),
 31: ('problem','Condition.code','Represent a named past disease as one longitudinal Condition with clinically appropriate status.','problem'),
 32: ('problem','Condition.code.text','Attach the disease description to the same coded problem rather than making a second Condition.','problem'),
 33: ('problem','Condition.code + Condition.clinicalStatus (only if asserted)','Represent a named current illness; do not infer active status solely from the section label.','problem'),
 34: ('problem','Condition.code (one Condition per disease)','Exchange each clinically asserted co-morbidity as its own problem record.','problem'),
 35: ('problem','Condition.note.text (only if about this Condition)','Retain pertinent narrative when it qualifies a specific problem; global history needs a separate context.','problem'),
 37: ('question','Observation.code + Observation.valueCodeableConcept','Record the specified admission symptom as an Observation with a question/finding code and result.','symptom'),
 39: ('problem','Condition.code','Capture the clinically established hypertension subtype, not the whole ICD range as a code.','problem'),
 41: ('problem','Condition.code','Capture a supported stroke subtype without forcing unspecified cases into a specific subtype.','problem'),
 43: ('recency','Diagnosis-recency assertion (element undecided)','Assess newly versus previously diagnosed diabetes relative to a defined event and timeframe.',None),
 44: ('problem','Condition.code','Capture a clinically supported type of diabetes with governed local terminology.','problem'),
 46: ('copd','Condition.stage.type + Condition.stage.summary','Record a typed GOLD spirometric grade, preserving the classification edition and assessment.','stage'),
 47: ('copd','Condition.stage.type + Condition.stage.summary','Record a separate typed GOLD group under the same COPD Condition when clinically applicable.','stage'),
 48: ('question','Observation.code + Observation.valueCodeableConcept','Record the explicit pulmonary-TB question answer separately from any verified TB diagnosis.','answer'),
 49: ('problem','Condition.evidence.detail','Reference an actual supporting assessment from the asthma Condition; evidence.code is only appropriate when an evidence finding itself is supplied.','evidence'),
}
PROFILE = {
 'patient':('Existing PH Core Patient','Existing','https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-patient'),
 'pwdGap':('PWD permanence gap','Unspecified',None),
 'question':('PH Core Observation: question/finding','Existing profile; proposed use-case pattern','https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-observation'),
 'encounter':('PH Condition: encounter diagnosis','Proposed profile','https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-condition-encounter-diagnosis'),
 'mortality':('PH mortality cause Observation','Proposed Observation pattern; mortality workflow pending','https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-mortality-cause-observation'),
 'problem':('PH Condition: problem','Proposed profile','https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-condition-problem'),
 'recency':('Diabetes diagnosis-recency model','Deferred registry decision',None),
 'copd':('PH Condition: COPD registry','Proposed downstream derivative','https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-condition-registry-copd'),
}

# Terminology candidates are evidence for review, NOT workbook bindings or PH policy.
TERMINOLOGY = {
  7: 'SNOMED CT 840539006 names confirmed COVID-19 disease, not the Yes/No case-status question; only use on a separately asserted diagnosis. https://docs.snomed.org/implementation-guides/snomed-ct-guide-for-covid-19/3-mapping-to-icd-10',
  9: 'VRDR 3.0.0: LOINC 69453-9 codes the certifier-authored Part I cause line; 80359-3 and 80358-5 code manually and automatically selected underlying causes respectively. The worksheet does not say which workflow produced its ICD-10 value. https://hl7.org/fhir/us/vrdr/StructureDefinition-vrdr-cause-of-death-part1.html',
 10: 'LOINC 69453-9 identifies a US certificate Part I cause line, not generic mortality status. Keep certifier wording in Observation.valueCodeableConcept.text; establish whether this is paired with row 9 on the same line. https://hl7.org/fhir/us/mdi/StructureDefinition-Observation-mdi-cause-of-death-part1.html',
 29: 'SNOMED CT 398254007 denotes pre-eclampsia, not all pregnancy-induced hypertension and not a Yes/No answer. Use only for a separately confirmed pre-eclampsia diagnosis. https://evsexplore.semantics.cancer.gov/evsexplore/concept/snomedct_us/398254007',
 48: 'SNOMED CT 154283005 denotes pulmonary tuberculosis (disorder), not the question or an explicit negative result. https://evsexplore.semantics.cancer.gov/evsexplore/concept/snomedct_us/154283005',
 39: 'I10–I15 is an ICD-10 range, not a single code. Select a precise hypertension subtype only after source detail and a national value set are confirmed. https://icd.who.int/browse10/2019/en#/I10-I15',
 41: 'I60–I64 is an ICD-10 range, not a single code. Do not force ischemic or hemorrhagic subtype without supporting evidence. https://icd.who.int/browse10/2019/en#/I60-I69',
 44: 'E10–E14 is an ICD-10 range, not a single code. Code only an established diabetes type. https://icd.who.int/browse10/2019/en#/E10-E14',
 46: 'GOLD spirometric grade needs a governed grade and edition; do not treat the name of the scale as a patient result. GOLD is cited by name (Global Initiative for Chronic Obstructive Lung Disease report); no stable public URL was verified, so none is linked.',
 47: 'GOLD ABCD and ABE are edition-dependent; select a versioned group scale before coding. GOLD is cited by name (GOLD report); no stable public URL was verified.'
}

# Policy basis for each data element, with the answer options the policy itself enumerates.
# (basis, authoritative URL or None if no stable public link was located, policy-defined options, gap note)
# Sources were read while preparing this review; 'None' means the policy is cited by name but no
# stable public URL could be verified, so no link is invented.
NCDA_PWD = 'NCDA Administrative Order No. 001, s. 2021 (PWD ID issuance)'
NCDA_PWD_URL = 'https://ncda.gov.ph/disability-laws/administrative-orders/ncda-administrative-order-no-001-series-of-2021/'
PRPWD = 'DOH AO No. 2013-0005 / -A / -B (Philippine Registry for Persons with Disabilities)'
PRPWD_URL = 'https://ncda.gov.ph/disability-laws/administrative-orders/doh-administrative-order-no-2013-0005-a/'
PRPWD_B_URL = 'https://ncda.gov.ph/wp-content/uploads/2023/07/ao2013-0005-B.pdf'
MCCOD = 'DOH Administrative Order No. 2020-0008 (Rules on Medical Certification of Cause of Death)'
MCCOD_URL = 'https://legaldex.com/laws/rules-on-medical-certification-of-cause-of-death-mccod'
COVID = 'DOH AO No. 2020-0013 and DM No. 2024-0073 (COVID-19 case definitions and PDITR+)'
COVID_URL = 'https://law.upd.edu.ph/wp-content/uploads/2020/05/DOH-AO-No-2020-0013.pdf'
HIM = 'DOH Hospital Health Information Management Manual'
HIM_URL = ('http://ehealth.doh.gov.ph/nehehrsv/sys/assets/HOSPITAL%20HEALTH%20INFORMATION%20MANAGEMENT%20MANUAL'
           '%20formerly%20HOSPITAL%20MEDICAL%20RECORDS%20MANAGEMENT%20MANUAL.pdf')
POLICY = {
  4: (NCDA_PWD + '; ' + PRPWD + ' (v4.0 form)', NCDA_PWD_URL,
      'Deaf/Hard of Hearing; Intellectual; Learning; Mental; Physical (includes orthopedic); Psychosocial; Speech and Language Impairment; Visual; Cancer (RA 11215); Rare Disease (RA 10747); Others, specify.',
      'PH Core 0.2.0 ph-core-disability-type-vs carries only 9 codes and omits Mental Disability, Cancer and Rare Disease, and folds Deaf/Hard of Hearing into "hearing". The profile value set therefore does not yet cover the full PRPWD v4.0 national list.'),
  5: (NCDA_PWD, NCDA_PWD_URL, 'Eligibility is limited to a person with a *permanent* disability; the policy does not enumerate a permanence value set, so the workbook\u2019s Yes/No remains unbound.',
      'Permanence is a registration precondition, not a coded element. No PH Core element or value set currently represents it.'),
  7: (COVID, COVID_URL, 'Case classification: Suspect; Probable; Confirmed. A person who does not meet a case definition is not a case (explicit negative).', None),
  8: (HIM, None, 'Date of onset of the encounter-linked illness; not encounter start or record creation.', None),
  9: (MCCOD + '; ICD-10 as adopted by DOH/PSA', MCCOD_URL, 'Certified cause per the ICD-10 medical certificate of cause of death: Part I causal sequence (line a immediate, lowest used line = underlying cause) and Part II contributing conditions; coded under ICD-10 selection rules.',
      'The workbook does not state whether its ICD-10 value is the certified underlying cause (Part I) or a later manually/automatically assigned code. PSA codes certificates with Iris; those are different processing stages.'),
 10: (MCCOD, MCCOD_URL, 'Certifier\u2019s own wording of the cause, based on best medical opinion and available records; duration/interval per condition.', None),
 12: (HIM, None, 'Onset is the date signs/symptoms first appeared; for COVID-19 surveillance the workbook cites the same operational definition.', None),
 13: (HIM, None, 'Presence-of-history question in the workbook; no answer list is published.', None),
 15: (HIM, None, 'Date the patient experienced the complication; combine with the same block\u2019s time.', None),
 16: (HIM, None, 'Time the patient experienced the complication; must pair with its date.', None),
 17: (HIM, None, 'Complication experienced by the patient; the workbook shows no governed complication-role code list.',
      'Encounter.diagnosis.use role values are not a national code list here.'),
 19: (HIM, None, 'Date the patient experienced the complication (COMPLICATIONS block).', None),
 20: (HIM, None, 'Time the patient experienced the complication (COMPLICATIONS block).', None),
 21: (HIM, None, 'Complication experienced by the patient (COMPLICATIONS block).', None),
 23: (HIM, None, 'Date the patient was diagnosed.', None),
 24: (HIM, None, 'Time the patient was diagnosed.', None),
 25: ('DOH/adopted ICD-10 diagnosis coding', MCCOD_URL, 'Diagnosis as represented by an ICD-10 code. National edition and ICD-10-PH canonical are not stated by the workbook.',
      'PH Core 0.2.0 Condition.code keeps the inherited example binding with no ICD-10-PH value set.'),
 26: (HIM, None, 'Free-text diagnosis description attached to the coded diagnosis.', None),
 27: (HIM, None, 'Diagnosis remarks as narrative context.', None),
 29: ('WHO ICD-10, Chapter XV (O10\u2013O16); SNOMED CT 398254007', 'https://icd.who.int/browse10/2019/en#/O10-O16', 'Pregnancy-induced hypertension category (O10\u2013O16); oedema/proteinuria in pregnancy, pre-eclampsia and eclampsia are distinct concepts.',
      'The workbook\u2019s label pairs PIH with pre-eclampsia. SNOMED CT 398254007 denotes pre-eclampsia only, which is narrower than all PIH.'),
 31: (HIM, None, 'Past disease as represented by a code.', None),
 32: (HIM, None, 'Free-text specific disease description.', None),
 33: (HIM, None, 'Present illness as recorded by the clinician.', None),
 34: (HIM, None, 'Co-morbidities; one Condition per clinically asserted disease.', None),
 35: (HIM, None, 'Pertinent past medical history narrative.', None),
 37: (HIM, None, 'Admission signs and symptoms, including \u201cOthers, specify\u201d; no answer list is published.', None),
 39: (PRPWD + '; DOH PhilPEN (AO 2012-0029)', PRPWD_URL, 'Hypertension type/subtype; the workbook names ICD-10 I10\u2013I15 as the example range, not a single code.', None),
 41: ('DOH AO No. 2020-0059 (National Policy Framework on Acute Stroke)', None, 'Stroke type; the workbook names ICD-10 I60\u2013I64 as the example range, not a single code.',
      'No public URL for AO 2020-0059 was verified during this review, so none is linked.'),
 43: (PRPWD + ' (Diabetes Registry Form)', PRPWD_URL, 'Indicator: newly diagnosed or previously diagnosed diabetes.',
      'The registry does not define the comparison window, so \u201cnewly\u201d remains ambiguous.'),
 44: (PRPWD + ' (Diabetes Registry Form)', PRPWD_URL, 'Type of diabetes; the workbook names ICD-10 E10\u2013E14 as the example range, not a single code.', None),
 46: (PRPWD + ' (COPD Registry Form); GOLD report', PRPWD_URL, 'GOLD spirometric grade; the classification edition must be stated because grades are edition-specific.', None),
 47: (PRPWD + ' (COPD Registry Form); GOLD report', PRPWD_URL, 'COPD group; GOLD used ABCD before 2023 and ABE from the 2023 report, so the edition must be stated.', None),
 48: ('DOH AO No. 2015-0024 (Integrated Tuberculosis Information System); DOH AO No. 2011-0010',
      'https://ntp.doh.gov.ph/download/ao2015-0024/', 'Pulmonary TB question answer; national TB guidance distinguishes bacteriologically confirmed, clinically diagnosed and not a TB case.',
      'DOH AO No. 2011-0010 (field health services reporting) is cited by name; no stable public URL was verified.'),
 49: (PRPWD, PRPWD_URL, 'Basis for the final diagnosis of asthma, captured as supporting evidence for the asthma problem.', None),
}

# The HIM Manual is published by DOH under the Health Facility Development Bureau; its host
# blocks automated requests (HTTP 403), so the link is offered for human use and was not
# fetch-verified. Fill it in wherever the HIM Manual is the policy basis.
POLICY = {k: (v[0], v[1] or (HIM_URL if v[0].startswith('DOH Hospital Health Information') else None), v[2], v[3])
           for k, v in POLICY.items()}

# Use local workbook model for field paths; copy previously reviewed comparative
# discussions from the main crosswalk without evaluating page/browser code.
rows=json.loads((ROOT/'jao-l3-prototype/worksheet-index.json').read_text())
source=(ROOT/'condition-logical-model.html').read_text()
match=re.search(r'const DATA=(\[.*?\]);\n// The workbook',source,re.S)
if not match:raise RuntimeError('Cannot locate source crosswalk DATA')
crosswalk=json.loads(match.group(1))
js=source[source.index('const IG_SOURCES='):source.index('const byId=')]
js+='\nconsole.log(JSON.stringify({sources:IG_SOURCES,discussions:DISCUSSIONS}))'
comparison=json.loads(subprocess.check_output(['node','-e',js],text=True))
by_excel={r['excel']:r for r in rows}
assert set(by_excel)==set(MAP)=={r['excel'] for r in crosswalk}
assert set(map(int,comparison['discussions']))==set(MAP)

# Stable synthetic UUIDs make each transaction self-contained and reproducible.
def urn(row,kind):return 'urn:uuid:'+str(uuid.uuid5(uuid.NAMESPACE_URL,f'jao-mindmap/{row}/{kind}'))
def example(row,kind):
    i=row['excel']
    pat_id, enc_id, cond_id, obs_id=[urn(i,t) for t in ('patient','encounter','condition','observation')]
    def entry(obj,id):return {'fullUrl':id,'resource':obj,'request':{'method':'POST','url':obj['resourceType']}}
    patient={'resourceType':'Patient'}
    items=[entry(patient,pat_id)]
    date='2026-03-01T10:30:00+08:00'  # synthetic, not from the workbook
    if kind=='patient':
        patient['extension']=[{'url':'https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-pwd-disability','extension':[{'url':'disabilityType','valueCodeableConcept':{'text':'Illustrative disability type'}}]}]
    elif kind in ('answer','symptom'):
        observation={'resourceType':'Observation','status':'final','code':{'text':row['label']},'subject':{'reference':pat_id},'effectiveDateTime':date,
                     'valueCodeableConcept':{'text':'Illustrative answer' if kind=='answer' else 'Illustrative symptom'}}
        items.append(entry(observation,obs_id))
    else:
        condition={'resourceType':'Condition','subject':{'reference':pat_id},'code':{'text':'Illustrative '+row['label']}}
        if i==12:condition['code']={'text':'Illustrative COVID-19 diagnosis'}
        elif i==8:condition['code']={'text':'Illustrative encounter illness'}
        elif i in (15,16,17,19,20,21):condition['code']={'text':'Illustrative complication diagnosis'}
        elif i in (23,24,25,26,27):condition['code']={'text':'Illustrative encounter diagnosis'}
        elif i in (32,35):condition['code']={'text':'Illustrative named disease'}
        if kind in ('encounter','asserted'):
            enc={'resourceType':'Encounter','status':'finished','class':{'system':'http://terminology.hl7.org/CodeSystem/v3-ActCode','code':'AMB'},
                 'subject':{'reference':pat_id},'diagnosis':[{'condition':{'reference':cond_id}}]}
            items.append(entry(enc,enc_id))
            condition['category']=[{'coding':[{'system':'http://terminology.hl7.org/CodeSystem/condition-category','code':'encounter-diagnosis'}]}]
            condition['encounter']={'reference':enc_id}
            if i in (8,15,16,19,20):condition['onsetDateTime']=date
            if kind=='asserted':
                condition['extension']=[{'url':'http://hl7.org/fhir/StructureDefinition/condition-assertedDate','valueDateTime':date}]
                condition['recordedDate']='2026-03-02T09:00:00+08:00'
            if i==25:condition['code']={'coding':[{'system':'http://hl7.org/fhir/sid/icd-10','code':'E11.9','display':'Type 2 diabetes mellitus without complications'}], 'text':'Illustrative type 2 diabetes mellitus diagnosis'}
            if i==26:condition['code']={'text':'Illustrative diagnosis description'}
            if i==27:condition['note']=[{'text':'Illustrative diagnosis remarks'}]
        else:
            condition['category']=[{'coding':[{'system':'http://terminology.hl7.org/CodeSystem/condition-category','code':'problem-list-item'}]}]
            condition['clinicalStatus']={'coding':[{'system':'http://terminology.hl7.org/CodeSystem/condition-clinical','code':'active'}]}
            if i==12:condition['onsetDateTime']=date
            if i==33:condition['code']={'text':'Illustrative named present illness'}
            if i==35:condition['note']=[{'text':'Illustrative history about this condition'}]
            if kind=='stage':
                condition['code']={'text':'Illustrative COPD diagnosis'}
                condition['stage']=[{'type':{'text':'GOLD spirometric grade'},'summary':{'text':'Illustrative grade'}},
                                    {'type':{'text':'GOLD clinical group'},'summary':{'text':'Illustrative group; edition unassigned'}}]
            if kind=='evidence':
                condition['code']={'text':'Illustrative asthma diagnosis'}
                observation={'resourceType':'Observation','status':'final','code':{'text':'Illustrative supporting assessment'},'subject':{'reference':pat_id},'valueCodeableConcept':{'text':'Illustrative finding'}}
                items.append(entry(observation,obs_id))
                condition['evidence']=[{'detail':[{'reference':obs_id}]}]
        items.append(entry(condition,cond_id))
    return {'resourceType':'Bundle','type':'transaction','entry':items}

records=[]
# Optional Jev quality scores (evaluate-rows-jev.py). Absent scores simply omit the block.
EVALUATION={};EVAL_META=None
ev_path=ROOT/'row-evaluation.json'
if ev_path.exists():
    _ev=json.loads(ev_path.read_text())
    EVAL_META={'model':_ev.get('model'),'checkedAt':_ev.get('checkedAt')}
    EVALUATION={x['excel']:x for x in _ev['results'] if 'error' not in x}
for r in crosswalk:
    i=r['excel'];group,path,usecase,kind=MAP[i]; src=by_excel[i]; disc=comparison['discussions'][str(i)]
    obj={'excel':i,'section':src['section'],'label':src['label'],'sourcePath':f"JAOConditionSheet.{src['group']}.{src['name']}",
         'sourceId':'SRC'+src['source_id'],'definition':src['definition'],'profileKey':group,'fhirPath':path,
         'useCase':usecase,'recommendation':disc['recommend'],'humanReview':disc['review'],'comparisons':disc['compare'],
         'state':r['state'],'terminologyNote':TERMINOLOGY.get(i,'No row-specific SNOMED CT/LOINC concept is established from this source alone; use a governed value set when the actual diagnosis, finding or answer is known.'),
         'policyBasis':POLICY[i][0],'policyUrl':POLICY[i][1],'policyOptions':POLICY[i][2],'policyGap':POLICY[i][3],
         'evaluation':({'composite':EVALUATION[i]['composite'],'verdict':EVALUATION[i]['verdict'],
                        'lowConfidenceDimensions':EVALUATION[i]['lowConfidenceDimensions'],
                        'dimensions':{k:{'normalized':v['normalized'],'confidence':v['confidence']}
                                      for k,v in EVALUATION[i]['dimensions'].items()},
                        'model':EVALUATION[i].get('model') or EVAL_META['model'],'checkedAt':EVAL_META['checkedAt']}
                       if i in EVALUATION and EVAL_META else None),'exampleKind':kind,'example':None}
    if i in (9,10,13,17,21):obj['state']='Decision needed'
    if kind:
        bundle=example(src,kind)
        filename=f'Transaction-Excel-{i}.json';(OUT/filename).write_text(json.dumps(bundle,indent=2,ensure_ascii=False)+'\n')
        obj['example']=filename
    records.append(obj)
assert len(records)==34
page=ROOT/'condition-row-profile-mindmap.html'
if page.exists():
    html=page.read_text();start='const ROWS=';end=';\nconst PROFILES='
    before,rest=html.split(start,1);old,suffix=rest.split(end,1)
    if not (old.startswith('[') or old == '__ROWS__'):raise RuntimeError('Unexpected HTML data block')
    html=before+start+json.dumps(records,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+end+suffix
    start='const PROFILES=';end=';\nconst SOURCES='
    before,rest=html.split(start,1);old,suffix=rest.split(end,1)
    html=before+start+json.dumps(PROFILE,ensure_ascii=False,separators=(',',':'))+end+suffix
    start='const SOURCES=';end=';\nconst TRANSACTIONS='
    before,rest=html.split(start,1);old,suffix=rest.split(end,1)
    html=before+start+json.dumps(comparison['sources'],ensure_ascii=False,separators=(',',':'))+end+suffix
    start='const TRANSACTIONS=';end=';\nconst esc='
    before,rest=html.split(start,1);old,suffix=rest.split(end,1)
    examples={str(r['excel']):json.loads((OUT/r['example']).read_text()) for r in records if r['example']}
    html=before+start+json.dumps(examples,ensure_ascii=False,separators=(',',':'))+end+suffix
    # Keep the distributed HTML offline/self-contained; pinned D3 builds live in
    # vendor/ with their original license notices and are inlined on rebuild.
    begin='<!-- BEGIN PINNED D3 CURVE LIBRARIES -->'
    end='<!-- END PINNED D3 CURVE LIBRARIES -->'
    prefix,rest=html.split(begin,1)
    _,suffix=rest.split(end,1)
    vendor='\n'.join('<script>'+ (ROOT/'vendor'/name).read_text().replace('</script','<\\/script') +'</script>' for name in ('d3-path-3.1.0.min.js','d3-shape-3.2.0.min.js'))
    html=prefix+begin+'\n<!-- BSD-3-Clause D3 builds; source and notices in vendor/. -->\n'+vendor+'\n'+end+suffix
    page.write_text(html)
(ROOT/'mindmap-index.json').write_text(json.dumps({'rows':records,'profiles':PROFILE,'sources':comparison['sources']},indent=2,ensure_ascii=False)+'\n')
print(f'Mapped {len(records)} rows to {len(PROFILE)} destination groups; wrote {sum(bool(r["example"]) for r in records)} synthetic transaction Bundles.')
