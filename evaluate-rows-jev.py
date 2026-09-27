#!/usr/bin/env python3
"""Score each workbook row element with TypeSafe's Jev (System One) model.

Composite-scoring pattern: five independent Score questions per row, normalized
to 0-1 and combined with weights in this code. Noul/Choice thresholds are not
needed here; each Score returns probabilities and a confidence.

Requires TYPESAFE_API_KEY. Writes row-evaluation.json and prints a table.
Terminology membership comes from terminology-validation.json when present.
"""
from pathlib import Path
import json
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
API = 'https://api.typesafe.ai/v1/systemone'
MODEL = 'jev-latest'

# Five dimensions, each judged independently on a 5-level rubric (0..4).
DIMENSIONS = {
    'traceability': {
        'weight': 0.25,
        'instructions': 'How completely and consistently is this workbook row traced to its one source element and its proposed FHIR destination?',
        'criteria': [
            'Source row and destination are missing or mutually inconsistent.',
            'Source is present but the source identity or destination is ambiguous.',
            'Traced to a source element and a destination, with a minor gap such as a missing source id.',
            'Clearly traced: one source element and one destination path, section preserved.',
            'Fully traceable and self-consistent, including source id, group path and preserved section, with no merged repeats.',
        ],
    },
    'policy_link': {
        'weight': 0.15,
        'instructions': 'How well does this row cite the current Philippine policy that requires or defines the data element?',
        'criteria': [
            'No policy cited anywhere for the element.',
            'A policy is named but its relevance, issuing body or currency is unclear.',
            'A relevant policy is named with issuing body, but no link and no version.',
            'A specific current policy is cited with issuing body and a link, or a stated reason there is none.',
            'A specific current policy is cited with link or version and demonstrably governs this element.',
        ],
    },
    'policy_options': {
        'weight': 0.15,
        'instructions': 'Does the row state the answer options the policy defines, or correctly establish that the policy defines none?',
        'criteria': [
            'No options given and no statement about whether the policy defines any.',
            'Options are hinted at but not sourced from the policy.',
            'Some policy options are listed but incomplete, or mixed with an adopted code range.',
            'Policy-defined options are enumerated, or their absence is explicitly established.',
            'Policy options are fully enumerated (or absence demonstrated) and clearly distinguished from candidate codes.',
        ],
    },
    'meaning': {
        'weight': 0.25,
        'instructions': 'Does the proposed representation respect what this row actually asserts: a question, a finding, a diagnosis, a registration field, or a mortality statement?',
        'criteria': [
            'The representation contradicts the assertion, for example inferring a diagnosis from a Yes/No or treating a missing record as a negative answer.',
            'The resource cannot carry the meaning without a major unstated assumption.',
            'The correct resource family is used but a question, answer, status or role is conflated.',
            'The correct resource and path are used, with status, timing or provenance mostly handled.',
            'The correct resource and path are used, and the assertion type, status, timing and non-inference of negatives are all explicit.',
        ],
    },
    'terminology': {
        'weight': 0.20,
        'instructions': 'How sound is the terminology handling for this row, given that the workbook defines no bindings?',
        'criteria': [
            'A binding or code is invented or implied without policy support.',
            'A code is used whose meaning does not match the row, or a code range is treated as a single code.',
            'A candidate code is plausible but unverified, or its scope is not stated.',
            'An exact candidate concept is used, membership is verified on a public server, and it is clearly marked as not a binding.',
            'An exact verified concept is used with its code-system version recorded, and the question/answer/diagnosis distinction is maintained.',
        ],
    },
}

PASS, REVIEW = 0.75, 0.55

def get_key():
    key = os.environ.get('TYPESAFE_API_KEY')
    if not key:
        sys.exit('TYPESAFE_API_KEY is not set.')
    return key

def call(state, key, attempts=4):
    body = json.dumps({'state': state, 'model': MODEL,
                       'questions': {k: {'type': 'score', 'instructions': v['instructions'], 'criteria': v['criteria']}
                                     for k, v in DIMENSIONS.items()}}).encode()
    for n in range(attempts):
        try:
            req = urllib.request.Request(API, data=body, headers={
                'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            code = getattr(e, 'code', None)
            if n == attempts - 1 or code not in (429, 529, None):
                raise
            time.sleep(2 ** n)
    raise RuntimeError('unreachable')

def row_state(row, term_validation):
    return {
        'workbook_row': row['excel'],
        'section': row['section'],
        'label': row['label'],
        'source_definition': row['definition'],
        'source_path': row['sourcePath'],
        'source_id': row['sourceId'],
        'proposed_fhir_path': row['fhirPath'],
        'proposed_profile': row['profileKey'],
        'review_state': row['state'],
        'clinical_use_case': row['useCase'],
        'recommendation': row['recommendation'],
        'human_review_question': row['humanReview'],
        'policy_basis': row['policyBasis'],
        'policy_source_url': row['policyUrl'],
        'policy_defined_options': row['policyOptions'],
        'policy_gap': row['policyGap'],
        'terminology_note': row['terminologyNote'],
        'terminology_server_validation': term_validation,
        'has_transaction_example': bool(row['example']),
    }

def main():
    key = get_key()
    rows = json.loads((ROOT / 'mindmap-index.json').read_text())['rows']
    tv_path = ROOT / 'terminology-validation.json'
    tv = {}
    if tv_path.exists():
        for r in json.loads(tv_path.read_text())['results']:
            tv.setdefault(r['excel'], []).append(
                {'code': r['code'], 'version': r.get('version'), 'ok': r.get('ok'), 'display': r.get('display')})

    def evaluate(row):
        state = row_state(row, tv.get(row['excel'], 'no candidate code for this row'))
        try:
            resp = call(state, key)
        except Exception as e:
            return {'excel': row['excel'], 'label': row['label'], 'error': f'{type(e).__name__}: {e}'}
        answers = resp['answers']
        norm, detail = 0.0, {}
        for dim, spec in DIMENSIONS.items():
            a = answers[dim]
            top = len(spec['criteria']) - 1
            n = a['score'] / top
            norm += spec['weight'] * n
            detail[dim] = {'score': round(a['score'], 2), 'normalized': round(n, 3),
                           'confidence': round(a['confidence'], 3),
                           'probabilities': a['probabilities']}
        verdict = 'pass' if norm >= PASS else ('review' if norm >= REVIEW else 'fail')
        low_conf = [d for d, v in detail.items() if v['confidence'] < 0.5]
        return {'excel': row['excel'], 'label': row['label'], 'section': row['section'],
                'composite': round(norm, 3), 'verdict': verdict,
                'lowConfidenceDimensions': low_conf, 'dimensions': detail,
                'model': resp.get('model'), 'usage': resp.get('usage')}

    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(evaluate, rows))
    results.sort(key=lambda r: r['excel'])

    ok = [r for r in results if 'error' not in r]
    payload = {
        'model': MODEL, 'endpoint': API,
        'checkedAt': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'dimensions': {k: {'weight': v['weight'], 'criteria': v['criteria']} for k, v in DIMENSIONS.items()},
        'thresholds': {'pass': PASS, 'review': REVIEW},
        'scored': len(ok), 'errored': len(results) - len(ok),
        'meanComposite': round(sum(r['composite'] for r in ok) / len(ok), 3) if ok else None,
        'results': results,
    }
    (ROOT / 'row-evaluation.json').write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n')

    print(f"Jev {MODEL}  rows={len(ok)}  mean={payload['meanComposite']}  at {payload['checkedAt']}")
    for r in results:
        if 'error' in r:
            print(f"  [ERR ] row {r['excel']:>2} {r['error'][:70]}")
        else:
            flags = ','.join(r['lowConfidenceDimensions']) or '-'
            print(f"  [{r['verdict'].upper():<6}] row {r['excel']:>2} {r['composite']:.3f}  lowconf={flags:<28} {r['label'][:36]}")
    print('Wrote row-evaluation.json (Jev scores, probabilities, confidence).')
    return 0

if __name__ == '__main__':
    sys.exit(main())
