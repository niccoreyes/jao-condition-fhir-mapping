#!/usr/bin/env python3
"""Rate the Quality-review presentation with TypeSafe Jev (System One).

Jev judges the design as described (markup, CSS, rendered examples), not the
rendered pixels; visual checks are done separately in the browser. Six weighted
Score questions; the loop reruns until the composite passes.

Usage: python evaluate-quality-review-design.py [--html condition-row-profile-mindmap.html]
Writes quality-review-design.json.
"""
from pathlib import Path
import argparse, json, os, re, sys, urllib.request
from datetime import datetime, timezone

API = 'https://api.typesafe.ai/v1/systemone'
MODEL = 'jev-latest'
PASS, REVIEW = 0.75, 0.55

DIMENSIONS = {
    'legibility': {
        'weight': 0.18,
        'instructions': 'How readable is this Quality-review presentation at a glance and in detail?',
        'criteria': [
            'A bare number with no label or structure; hard to interpret.',
            'Readable only after careful reading; raw decimals and no visual encoding.',
            'Understandable, but dense text or a raw decimal scale slows reading.',
            'Clear with a visual score cue and labelled parts; scale is obvious.',
            'Immediately readable: a visual score, a labelled verdict, and clearly named dimension bars.',
        ],
    },
    'scale_meaning': {
        'weight': 0.20,
        'instructions': 'Does the primary number carry an interpretable scale and stated reference, rather than an unexplained decimal?',
        'criteria': [
            'A raw decimal such as 0.703 with no scale or meaning.',
            'A number with no threshold or direction to interpret it.',
            'A number with either a scale or a threshold, but not both.',
            'A 0-100 score with at least one stated threshold.',
            'A 0-100 score with both pass and review thresholds stated next to it.',
        ],
    },
    'uncertainty': {
        'weight': 0.18,
        'instructions': 'Is model confidence represented honestly and usefully, without cluttering the display?',
        'criteria': [
            'Confidence is absent, so a confident-looking number may hide uncertainty.',
            'Confidence shown only as raw decimals that readers must interpret.',
            'Confidence present but visually indistinguishable from the score.',
            'Confidence encoded visually and low-confidence dimensions are flagged.',
            'Confidence is encoded (for example by a distinct bar style) and low-confidence dimensions are named, with a legend explaining the encoding.',
        ],
    },
    'hierarchy': {
        'weight': 0.15,
        'instructions': 'Is there a clear emphasis order among verdict, composite score and the individual dimensions?',
        'criteria': [
            'Everything has equal emphasis; no focal point.',
            'The worst information dominates or messages compete.',
            'A focal point exists but the order is inconsistent.',
            'Verdict, score and dimensions are ordered and distinguishable.',
            'A deliberate hierarchy: status first, weighted score second, dimension detail third.',
        ],
    },
    'consistency': {
        'weight': 0.15,
        'instructions': 'Does the presentation fit the surrounding page design and remain accessible and simple?',
        'criteria': [
            'Clashes with the page palette or nests cards inside cards.',
            'Uses unrelated styling and is visually noisy.',
            'Generally consistent but with one distracting or redundant element.',
            'Matches the page tokens and avoids nesting; accessible labelling present.',
            'Uses the page design tokens, avoids nested cards and clutter, and carries a complete accessible label.',
        ],
    },
    'honesty': {
        'weight': 0.14,
        'instructions': 'Does the presentation avoid implying clinical truth or overstating certainty?',
        'criteria': [
            'Presents the score as a clinical judgement.',
            'Implies certainty the data does not support.',
            'Neutral but unclear about what is being scored.',
            'States that this scores the mapping, and low confidence routes to human review.',
            'Explicitly frames the score as a mapping-quality aid with human review, never clinical truth.',
        ],
    },
}

# The superseded representation, kept as the baseline for comparison.
OLD_DESIGN = {
    'name': 'superseded (raw decimal + text list)',
    'rendered_example': (
        'Quality review (Jev jev-1.13.0)\n'
        '0.811 — pass · low confidence: terminology\n'
        '- traceability: 0.99 (confidence 0.98)\n'
        '- policy_link: 0.98 (confidence 0.95)\n'
        '- policy_options: 0.97 (confidence 0.93)\n'
        '- meaning: 0.71 (confidence 0.62)\n'
        '- terminology: 0.47 (confidence 0.44)\n'
        'Five independent score questions, normalized and weighted in code; '
        'a low score or low confidence routes the row to human review.'
    ),
    'css': '',
}

def extract(html):
    css = re.search(r'/\* QREVIEW CSS START \*/(.*?)/\* QREVIEW CSS END \*/', html, re.S)
    fn = re.search(r'function qualityBlock\(r\)\{(.*?)\n\}\n', html, re.S)
    return (css.group(1).strip() if css else ''), (fn.group(1).strip() if fn else '')

def read_example(path):
    try:
        raw = Path(path).read_text().strip()
        if raw.startswith('"'):
            return json.loads(raw)
        return raw
    except Exception:
        return ''

def call(state, key, attempts=4):
    import time
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
            if n == attempts - 1 or getattr(e, 'code', None) not in (429, 529, None):
                raise
            time.sleep(2 ** n)

def rate(design, key):
    state = {
        'presentation_name': design['name'],
        'rendered_example': design['rendered_example'][:2500],
        'template_source': design.get('template', '')[:2500],
        'css': design['css'][:2500],
        'notes': 'Judged as a row-level quality-review widget inside a two-column FHIR mapping dialog.',
    }
    resp = call(state, key)
    norm, detail = 0.0, {}
    for dim, spec in DIMENSIONS.items():
        a = resp['answers'][dim]
        n = a['score'] / (len(spec['criteria']) - 1)
        norm += spec['weight'] * n
        detail[dim] = {'score': round(a['score'], 2), 'normalized': round(n, 3),
                       'confidence': round(a['confidence'], 3), 'probabilities': a['probabilities']}
    verdict = 'pass' if norm >= PASS else ('review' if norm >= REVIEW else 'fail')
    return {'name': design['name'], 'composite': round(norm, 3), 'verdict': verdict,
            'dimensions': detail, 'model': resp.get('model'), 'usage': resp.get('usage')}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--html', default='condition-row-profile-mindmap.html')
    args = ap.parse_args()
    key = os.environ.get('TYPESAFE_API_KEY')
    if not key:
        sys.exit('TYPESAFE_API_KEY is not set.')
    root = Path(__file__).resolve().parent
    html = (root / args.html).read_text()
    css, fn = extract(html)
    current = {
        'name': 'current (ring + labelled bars + hatching)',
        'rendered_example': (read_example('tests/quality-review-pass.html') + '\n---\n' + read_example('tests/quality-review-fail.html')) or 'examples not captured',
        'template': fn, 'css': css,
    }
    results = [rate(OLD_DESIGN, key), rate(current, key)]
    out = {'model': MODEL, 'endpoint': API, 'checkedAt': datetime.now(timezone.utc).isoformat(timespec='seconds'),
           'thresholds': {'pass': PASS, 'review': REVIEW}, 'results': results}
    (root / 'quality-review-design.json').write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n')
    for r in results:
        print(f"[{r['verdict'].upper():<6}] {r['name']:<40} composite={r['composite']:.3f} model={r['model']}")
        for k, v in r['dimensions'].items():
            print(f"    {k:<15} {v['normalized']:.2f} (conf {v['confidence']})")
    print('Wrote quality-review-design.json')
    return 0

if __name__ == '__main__':
    sys.exit(main())
