#!/usr/bin/env python3
"""Score modal presentation with independent Jev Scores, not rendered pixels or clinical truth.

Requires TYPESAFE_API_KEY. One batched System One request returns 0..4 distributions
and confidence for each dimension; save a pre-edit snapshot with --output.
"""
from pathlib import Path
import argparse, json, os, re, sys, urllib.request
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
API = 'https://api.typesafe.ai/v1/systemone'
MODEL = 'jev-latest'
WEIGHTS = {'scanability': .17, 'decision_visibility': .20, 'navigation': .16,
           'source_phcdi_separation': .15, 'mobile_accessibility': .12,
           'action_clarity': .20}
RUBRICS = {
 'scanability': ['The row dialog is a dense, undifferentiated wall; row identity and key facts cannot be found.', 'Several headings exist, but key facts compete with long detail and require extensive reading.', 'The dialog has recognizable sections, but the most useful row summary is not consistently scannable.', 'A concise row-specific summary and headings surface source meaning, recommendation and unresolved issue before detailed evidence.', 'A compact, clearly ordered row overview makes identity, assertion, recommendation and unresolved question immediately scannable without removing evidence.'],
 'decision_visibility': ['Recommendation and unresolved human question are absent or buried after substantial unrelated content.', 'Only one decision element is visible early; the other is buried or visually subordinate.', 'Recommendation and review question exist but compete with detail or each other.', 'Recommendation and unresolved question are distinct, prominent near the top, with quality review clearly secondary.', 'At first reading, distinct recommendation and unresolved question are prominent; no score or stylistic cue can be mistaken for approval.'],
 'navigation': ['No way to move among long modal sections; users must repeatedly scroll without landmarks.', 'Some navigation exists but misses major evidence sections or is not keyboard accessible.', 'Section headings support browsing but there are no direct jumps to multiple important sections.', 'Native keyboard-operable jump links reach all major sections including source, PHCDI, terminology and transaction.', 'Clearly labelled native in-dialog navigation reaches every major full-width evidence section, with stable targets and understandable return/scroll behavior.'],
 'source_phcdi_separation': ['Source meaning and historical PHCDI evidence are conflated with current recommendations or presented as endorsement.', 'Some labels distinguish sources, but historical comparison risks appearing normative or source assertion is hard to find.', 'Source and PHCDI are labelled but remain mixed with recommendations or lack clear context.', 'Source assertion is distinct from recommendation; PHCDI is clearly a separate historical comparison and not advice.', 'Full-width, explicit source and PHCDI sections maintain provenance; PHCDI is unmistakably neutral historical material, never approval or current recommendation.'],
 'mobile_accessibility': ['Narrow-screen dialog clips or has inaccessible controls/content; keyboard operation is not supported.', 'Some responsive layout but summary/navigation or focus/scroll behavior is unreliable.', 'Basic native dialog and responsive columns work, but long content or section navigation remains cumbersome.', 'Native named dialog, visible focus, keyboard-operable navigation and contained responsive scrolling preserve all section access.', 'Mobile layout keeps the decision overview, operable labelled jumps, readable wrapped content, native dialog semantics and visible keyboard focus without page overflow.'],
 'action_clarity': ['No row-specific next step or usable link is given, or a false approval/action control is presented.', 'Next step is vague or buried; links do not clearly lead to relevant follow-up evidence.', 'Some action or links exist but do not clearly connect the row question to next review context.', 'Each row surfaces its unresolved question and useful next-step links to source/crosswalk evidence without implying approval.', 'A concise row-specific unresolved question directly guides follow-up, with clearly named source/crosswalk destinations and no approval control or unsupported decision.']}

def main():
 p=argparse.ArgumentParser(); p.add_argument('--output',default='modal-readability-jev.json'); a=p.parse_args()
 key=os.environ.get('TYPESAFE_API_KEY')
 if not key: sys.exit('BLOCKER: TYPESAFE_API_KEY unavailable; Jev score not produced; preserve existing outputs.')
 html=(ROOT/'condition-row-profile-mindmap.html').read_text()
 fn=re.search(r'function openRow\(n,trigger\)\{.*?\nfunction openPath',html,re.S)
 rows=json.loads((ROOT/'mindmap-index.json').read_text())['rows']
 exemplars={str(x['excel']):{'label':x['label'],'section':x['section'],'sourcePath':x['sourcePath'],'definition':x['definition'],'recommendation':x['recommendation'],'humanReview':x['humanReview'],'phcdiComparison':x.get('phcdiComparison')} for x in rows if x['excel'] in (4,23,43,49)}
 state={'scope':'row modal readability/actionability only; do not judge row medical meaning, FHIR mapping or generated row evaluation.',
        'row_templates':fn.group(0)[:24000] if fn else 'openRow source not located',
        'modal_css':re.search(r'dialog\{.*?</style>',html,re.S).group(0)[:7000] if 'dialog{' in html else '',
        'representative_rows':exemplars,
        'limitations':'Jev sees supplied source/markup descriptions, not browser pixels, real assistive technology or clinical truth. Geometry/accessibility require independent browser QA.'}
 body={'state':state,'model':MODEL,'questions':{k:{'type':'score','instructions':f"Independently rate the row modal's {k.replace('_',' ')} for row-specific review using the supplied template and evidence. Judge presentation only, not correctness of medicine, mapping or generated row scores.",'criteria':v} for k,v in RUBRICS.items()}}
 req=urllib.request.Request(API,data=json.dumps(body).encode(),headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=120) as r: result=json.loads(r.read())
 except Exception as e: sys.exit(f'BLOCKER: Jev request failed; preserve earlier results. {e}')
 dims={}; composite=0
 for k,w in WEIGHTS.items():
  ans=result['answers'][k]; dims[k]={'score':ans['score'],'normalized':round(ans['score']/4,3),'confidence':ans['confidence'],'probabilities':ans['probabilities']}; composite+=w*ans['score']/4
 critical=min(dims['action_clarity']['normalized'],dims['navigation']['normalized'])
 out={'purpose':'modal readability/actionability presentation only; not clinical truth, approval or pixel/accessibility certification','model':result.get('model',MODEL),'endpoint':API,'checkedAt':datetime.now(timezone.utc).isoformat(timespec='seconds'),'requestCount':1,'weights':WEIGHTS,'thresholds':{'overall':.75,'actionAndNavigation':.75},'composite':round(composite,3),'criticalMinimum':round(critical,3),'verdict':'pass' if composite>=.75 and critical>=.75 else 'review','dimensions':dims,'usage':result.get('usage')}
 Path(a.output).write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
 return 0
if __name__=='__main__': raise SystemExit(main())
