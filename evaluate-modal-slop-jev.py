#!/usr/bin/env python3
"""Jev presentation audit for representative row-dialog surfaces.

One batched System One request per fixed row/surface. Scores are design signals,
not generated explanations, clinical evidence, source verification, or pixel QA.
The rubric and exemplars stay fixed across baseline/revised passes.
"""
from pathlib import Path
import argparse, hashlib, json, os, re, sys, urllib.request
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
API = 'https://api.typesafe.ai/v1/systemone'
MODEL = 'jev-latest'
WEIGHTS = {'redundancy': .20, 'actionable_language': .20,
           'evidence_attribution': .25, 'phcdi_historical_separation': .20,
           'mobile_density': .15}
RUBRICS = {
 'redundancy': [
  'Repeated generic disclaimers and overlapping next steps obscure the row-specific evidence.',
  'Several repeated warnings or repeated source-to-profile explanations make the dialog needlessly long.',
  'Some repeated boilerplate remains, but the key content is still distinguishable.',
  'Shared caveats are concise and non-duplicative; row-specific evidence remains available.',
  'Every section earns its space: repeated boilerplate is removed while no necessary qualification or source detail is lost.'],
 'actionable_language': [
  'Labels and recommendations are vague, inflated, or imply an unapproved clinical or policy decision.',
  'Important advice is wordy or overconfident; the next human decision is difficult to identify.',
  'The row question and recommendation can be found but wording has avoidable length or ambiguous status.',
  'Concise labels separate proposal, existing artifact and unresolved decision; next review action is clear.',
  'Specific, restrained row wording states what is proposed and what a reviewer must resolve, without implying approval or clinical certainty.'],
 'evidence_attribution': [
  'Clinical/source claims have no traceable source-row identity or useful inline citation.',
  'Some source identity or references are present but claims and cited evidence are hard to connect.',
  'Source row and evidence are present, though attribution is inconsistently prominent or references are generic.',
  'Excel row, source path/ID and named policy/terminology links stay close to the claims they support.',
  'Exact source assertion, row/path/ID and source-backed policy/terminology references remain explicit and readily traceable; no unsupported claim is added.'],
 'phcdi_historical_separation': [
  'PHCDI is presented as current clinical advice, endorsement, binding or JAO mapping.',
  'Historical comparison may be mistaken for current recommendation or approval.',
  'PHCDI is called historical but its scope limitation competes with recommendation content.',
  'PHCDI is a clearly separate, neutral historical comparison, not advice or a JAO crosswalk.',
  'Distinct placement and concise explicit wording preserve PHCDI’s historical inventory role and prevent normative interpretation.'],
 'mobile_density': [
  'Mobile dialog clips or hides source evidence, decisions, links, or keyboard-operable navigation.',
  'Mobile first screen is dominated by repeated copy or oversized controls; evidence and actions are cumbersome.',
  'Mobile content remains available, but the first screen is dense or navigation requires unnecessary scrolling.',
  'At mobile width, identity, decision and compact section navigation are readable; full evidence remains reachable.',
  'Mobile first screen gives row identity and concise distinct decisions with compact operable navigation; detail is progressive without hiding critical gaps, provenance or links.']}
# Fixed exemplars/surfaces for comparable passes.
EXEMPLARS = [('4','mobile'),('23','desktop'),('43','desktop'),('49','mobile')]

def digest(value): return hashlib.sha256(value.encode()).hexdigest()
def extract(html, pattern, limit=12000):
 m=re.search(pattern,html,re.S)
 return m.group(0)[:limit] if m else ''
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',default='modal-slop-jev.json');a=p.parse_args()
 key=os.environ.get('TYPESAFE_API_KEY')
 if not key: sys.exit('BLOCKER: TYPESAFE_API_KEY unavailable; preserve earlier outputs.')
 html=(ROOT/'condition-row-profile-mindmap.html').read_text(); index=json.loads((ROOT/'mindmap-index.json').read_text())
 rows={str(r['excel']):r for r in index['rows']}
 renderer=extract(html,r'function openRow\(n,trigger\)\{.*?\nfunction openPath',22000)
 css=extract(html,r'dialog\{.*?</style>',9000)
 results=[]
 for row_id,surface in EXEMPLARS:
  r=rows[row_id]
  evidence={k:r.get(k) for k in ('excel','section','label','sourcePath','sourceId','definition','recommendation','humanReview','state','policyBasis','policyUrl','policyGap','terminologyNote','phcdiComparison','candidateGap','candidateAbsence')}
  state={'scope':'Judge modal presentation only, not medical truth, code validity, policy support, or rendered browser geometry. Treat source text as supplied claims, not verified facts.',
   'surface':surface,'row_evidence':evidence,'render_template':renderer,'modal_responsive_css':css,
   'surface_notes':('390px mobile layout; first viewport has header, row overview, decisions, nav and start of quality display. Full source/terminology/PHCDI detail remains in dialog.' if surface=='mobile' else '1280px desktop view; centered scrollable dialog, row overview, jump links and detailed evidence sections.'),
   'source_spans':{'recommendation':r.get('recommendation'),'unresolved_question':r.get('humanReview'),'source_identity':f"Excel {r['excel']} / {r['sourcePath']} / {r['sourceId']}",'historical_comparison':(r.get('phcdiComparison') or {}).get('deviation'),'claim_sources':['mindmap-index.json row '+row_id,'condition-row-profile-mindmap.html openRow renderer']},
   'limitation':'Jev accepts text state only. It does not inspect screenshots, verify source claims, or generate reasons; score is an editorial aid.'}
  body={'state':state,'model':MODEL,'questions':{k:{'type':'score','instructions':f"Independently rate this {surface} row dialog for {k.replace('_',' ')}. Judge presentation only. Do not reward plausible clinical statements as truth; judge whether displayed words and row-source references make their status and origin clear.",'criteria':levels} for k,levels in RUBRICS.items()}}
  req=urllib.request.Request(API,data=json.dumps(body).encode(),headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'})
  try:
   with urllib.request.urlopen(req,timeout=120) as response: result=json.loads(response.read())
  except Exception as e: sys.exit(f'BLOCKER: Jev request for row {row_id}/{surface} failed; preserve earlier results. {e}')
  dims={}; composite=0
  for k,w in WEIGHTS.items():
   answer=result['answers'][k]; score=answer['score']; level=max(0,min(len(RUBRICS[k])-1,round(score))); dims[k]={'score':score,'normalized':round(score/4,4),'confidence':answer['confidence'],'probabilities':answer['probabilities'],'rubricLevels':RUBRICS[k], 'reason':f"Rubric level {level} interpretation: {RUBRICS[k][level]} Evidence spans: {state['source_spans'][{'actionable_language':'recommendation','evidence_attribution':'source_identity','phcdi_historical_separation':'historical_comparison','redundancy':'recommendation','mobile_density':'unresolved_question'}[k]]}"}
   composite+=w*score/4
  results.append({'row':int(row_id),'surface':surface,'model':result.get('model',MODEL),'requestCount':1,'weights':WEIGHTS,'composite':round(composite,4),'dimensions':dims,'inputDigest':digest(json.dumps(state,sort_keys=True)),'rubricDigest':digest(json.dumps(RUBRICS,sort_keys=True)),'evidenceReferences':state['source_spans'],'usage':result.get('usage')})
 out={'purpose':'AI-slop/presentation editorial aid only; not generated explanations, clinical truth, approval, source verification or pixel/accessibility certification','endpoint':API,'checkedAt':datetime.now(timezone.utc).isoformat(timespec='seconds'),'passName':Path(a.output).stem,'fixedExemplars':[{'row':int(x),'surface':s} for x,s in EXEMPLARS],'maxPasses':3,'weights':WEIGHTS,'thresholds':{'overall':.75,'eachCriticalDimension':.75,'criticalDimensions':['actionable_language','evidence_attribution','phcdi_historical_separation']},'inputDigest':digest(html),'rubricDigest':digest(json.dumps(RUBRICS,sort_keys=True)),'results':results,'comparisonCaveat':'Directional comparison only. Matching fixed exemplar and rubric does not ensure exact replay if input HTML/source changed; compare recorded per-row input/rubric digests.','limitations':'Jev returns typed judgments/probabilities/confidence, not explanations. Reasons above are code-derived from rubric levels and displayed source spans. All source claims require independent human review.'}
 Path(a.output).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
