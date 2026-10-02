#!/usr/bin/env python3
"""Score the row-dialog terminology presentation with Jev (not clinical content).

Requires TYPESAFE_API_KEY. Keeps each 0..4 Score distribution and confidence in JSON.
"""
from pathlib import Path
import argparse, json, os, re, sys, urllib.request
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parent
API='https://api.typesafe.ai/v1/systemone'
MODEL='jev-latest'
WEIGHTS={'separation':.16,'options_source':.13,'candidate_provenance':.16,'absence':.11,'responsive':.12,'accessibility':.10,'layout_room':.22}
RUBRICS={
'separation':['Options, codes and mappings are conflated or imply bindings.','Some separation, but candidate role/status is ambiguous.','Separate headings exist but role distinctions are incomplete.','Policy options and candidate concepts are separate; roles and non-binding status clear.','Policy/form options, existing artifacts and proposed international candidates are separately labelled; question, answer and diagnosis roles cannot be confused.'],
'options_source':['Options lack sources and absence is hidden.','Some source text appears but options are not structured or absence unclear.','Source-labelled options mostly structured; one no-list case ambiguous.','Each row labels policy source/link status and shows options or explicit absence.','Every row ties enumerated options to named policy/workbook evidence, differentiates unverified/name-only sources, and explicitly states no-list gaps.'],
'candidate_provenance':['Codes lack systems, displays or provenance.','Some code metadata but validation status/version/link missing.','Most candidates include metadata; some validation uncertainty missing.','Candidates include system/code/display/role/link and validation version/status.','Candidate provenance is complete and traceable; checked vs unverified, authority, version/time, role and caveat are explicit without implying binding.'],
'absence':['Missing codes appear as negative answers or definitive no-code facts.','Absence is inconsistent or overclaims nonexistence.','Some explicit absence, with gaps in interpretation.','No-candidate cases say none proposed/checked, not no code exists.','Every empty list is explicit evidence gap, never a negative answer or claim no code exists; range is not rendered as a code.'],
'responsive':['Long identifiers overflow and mobile use is blocked.','Responsive behavior absent or wrapping unreliable.','Some wrapping, dense table remains difficult.','Dialog list/table wraps on narrow screens and retains navigation.','Long IDs/links wrap and remain selectable; semantic list/table and dialog work at narrow widths without losing navigation.'],
'accessibility':['Unlabelled or inaccessible controls/content.','Weak semantics and names; keyboard access uncertain.','Basic headings/links but incomplete table/list semantics or names.','Native headings/lists/table, scoped headers, descriptive links and labelled dialog.','Complete semantic headings/list/table captions/scoped headers, useful labels, keyboard-operable native controls, and visible focus/navigation.'],
'layout_room':['Terminology is confined to a narrow sidebar; code comparison scrolls even at a desktop modal width.','Terminology has some width but shares the review sidebar; desktop table is clipped.','Terminology uses most of the modal but long entries or categories are cramped on desktop.','Terminology occupies its own full-width modal section with a readable desktop table; narrow screens scroll the table inside its region.','Terminology has its own clearly separated full-width modal section, desktop code columns remain readable without horizontal scroll, and narrow screens keep a focusable contained scroll region.']}

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--layout-metrics', help='Browser-measured geometry JSON for the current markup')
 parser.add_argument('--output', default='terminology-presentation-jev.json')
 args=parser.parse_args()
 key=os.environ.get('TYPESAFE_API_KEY')
 if not key: sys.exit('BLOCKER: TYPESAFE_API_KEY unavailable; Jev presentation score not produced.')
 html=(ROOT/'condition-row-profile-mindmap.html').read_text()
 fn=re.search(r'function terminologyBlock\(r\)\{.*?\nfunction openRow',html,re.S)
 state={'presentation':'Generated source-labelled terminology/options table in condition row dialogs',
        'template':fn.group(0)[:12000] if fn else 'terminologyBlock source not located',
        'css':re.search(r'\.terminology-table\{.*?</style>',html,re.S).group(0)[:3000] if '.terminology-table{' in html else '',
        'representative_rows':{str(x['excel']):{'options':x.get('optionSources'),'candidateTerminology':x.get('candidateTerminology'),'existingPHCore':x.get('existingPhCoreTerminology'),'candidateAbsence':x.get('candidateAbsence'),'range':x.get('terminologyRange')} for x in json.loads((ROOT/'mindmap-index.json').read_text())['rows'] if x['excel'] in [4,5,7,9,10,29,39,41,43,44,46,47,48,49]},
        'layout_metrics':json.loads(Path(args.layout_metrics).read_text()) if args.layout_metrics else {'status':'not measured; do not assume adequate desktop width'},
        'limits':'Jev assesses described presentation and supplied geometry, not policy correctness, code validity, browser pixels or clinical truth.'}
 questions={k:{'type':'score','instructions':f"Rate the row-dialog terminology presentation for {k.replace('_',' ')} against its evidence in state. Do not assess clinical correctness.",'criteria':v} for k,v in RUBRICS.items()}
 req=urllib.request.Request(API,data=json.dumps({'state':state,'model':MODEL,'questions':questions}).encode(),headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=120) as response: result=json.loads(response.read())
 except Exception as e: sys.exit(f'BLOCKER: Jev request failed; preserve earlier results. {e}')
 scores={}; composite=0
 for k,w in WEIGHTS.items():
  a=result['answers'][k]; probs=a['probabilities']; scores[k]={'score':a['score'],'normalized':round(a['score']/4,3),'confidence':a['confidence'],'probabilities':probs};composite+=w*a['score']/4
 geometry=state['layout_metrics']
 layout_pass=scores['layout_room']['normalized']>=.75
 measured_pass=(geometry.get('desktopHorizontalScrollRequired') is False and
                geometry.get('tableViewportShareOfModal',0)>=.8)
 gates={'weightedScore':composite>=.75,'layoutRoom':layout_pass,'desktopGeometry':measured_pass}
 out={'purpose':'terminology-presentation only; not clinical truth','model':result.get('model',MODEL),'endpoint':API,'checkedAt':datetime.now(timezone.utc).isoformat(timespec='seconds'),'weights':WEIGHTS,'thresholds':{'pass':.75,'layoutRoom':.75,'desktopTableShare':.8},'composite':round(composite,3),'verdict':'pass' if all(gates.values()) else 'review','gates':gates,'layoutMetrics':geometry,'dimensions':scores,'usage':result.get('usage')}
 Path(args.output).write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out,indent=2))
 return 0
if __name__=='__main__':raise SystemExit(main())
