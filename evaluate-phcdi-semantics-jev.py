#!/usr/bin/env python3
"""Advisory Jev semantic/workflow comparison for each proposed assertion and cited PHCDI evidence.

The deterministic path comparator owns structural status. This evaluator never changes it.
Output is atomically replaced only after every row succeeds; failures preserve prior results.
"""
import json, os, sys, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
API='https://api.typesafe.ai/v1/systemone'; MODEL='jev-latest'
OPTIONS={
 'overlap':'The element definition and proposed assertion describe meaning and workflow that substantially overlap, beyond a generic FHIR path resemblance.',
 'partial':'Some meaning or workflow is shared, but important distinctions or missing details prevent a full match.',
 'conflict':'The element definition explicitly describes a different meaning or workflow from the proposed assertion.',
 'no-support':'The cited element definition does not substantively support the proposed assertion; any resemblance is generic or lexical.',
 'undetermined':'Evidence is too incomplete, ambiguous, or unresolved to judge semantic/workflow correspondence.'}

def main():
 key=os.environ.get('TYPESAFE_API_KEY')
 if not key: raise RuntimeError('TYPESAFE_API_KEY is not set')
 index=json.loads((ROOT/'mindmap-index.json').read_text())['rows']
 questions={}
 for r in index:
  questions[str(r['excel'])]={'type':'choice','instructions':{'question':f"For JAO Excel row {r['excel']}, how does the cited historical PHCDI evidence compare semantically and in workflow to that row's exact proposed assertion? Compare only `rows` entry with `excel_row` {r['excel']}: its `proposed_fhir_path_exact`, `clinical_use_case`, `cited_phcdi_elements`, and definitions.",'constraints':'Judge the JAO proposal against the CSV element definitions. Generic path resemblance is not semantic support. Do not infer clinical equivalence, recommendation, authority, or profile approval. Choose undetermined for an explicitly unresolved proposal or insufficient evidence.'},'criteria':OPTIONS}
 state={'comparison_scope':'advisory comparison of exact JAO proposal assertion and cited PHCDI CSV definitions; historical source only',
  'rows':[{'excel_row':r['excel'],'jao_source_element':r['sourcePath'],'jao_source_definition':r['definition'],
   'proposed_fhir_path_exact':r['fhirPath'],'proposed_profile_status':r.get('proposalStatus'),
   'clinical_use_case':r['useCase'],'cited_phcdi_elements':r['phcdiComparison']['references'],
   'phcdi_deviation_note':r['phcdiComparison']['deviation']} for r in index]}
 payload=json.dumps({'state':state,'model':MODEL,'questions':questions}).encode()
 req=urllib.request.Request(API,data=payload,headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=180) as resp: result=json.loads(resp.read().decode())
 if set(result.get('answers',{})) != set(questions): raise RuntimeError('Jev returned an incomplete row set')
 out=[]
 for r in index:
  a=result['answers'][str(r['excel'])]
  if a.get('type')!='choice' or a.get('choice') not in OPTIONS: raise RuntimeError(f"Invalid Jev answer for row {r['excel']}")
  out.append({'excel':r['excel'],'choice':a['choice'],'probabilities':a['probabilities'],'confidence':a['confidence'],
   'humanReview':a['confidence']<0.5 or a['choice'] in ('conflict','undetermined'),'model':result.get('model')})
 output={'model':result.get('model',MODEL),'endpoint':API,'checkedAt':datetime.now(timezone.utc).isoformat(timespec='seconds'),
  'purpose':'advisory semantic/workflow signal only; cannot alter deterministic structural comparison','options':OPTIONS,
  'requested':len(index),'scored':len(out),'skipped':0,'results':out,'usage':result.get('usage')}
 tmp=ROOT/'phcdi-semantics-jev.json.tmp'; tmp.write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n'); tmp.replace(ROOT/'phcdi-semantics-jev.json')
 print(f"Jev {output['model']}: scored={len(out)} skipped=0 checkedAt={output['checkedAt']}")
if __name__=='__main__':
 try: main()
 except Exception as e:
  print(f'Jev semantic comparison failed; prior result preserved: {type(e).__name__}: {e}',file=sys.stderr); sys.exit(1)
