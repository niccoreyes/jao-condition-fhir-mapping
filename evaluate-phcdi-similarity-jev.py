#!/usr/bin/env python3
"""Advisory per-row Jev similarity measure for the historical PHCDI comparison.

For each of the 34 JAO rows this makes ONE System One request with TWO questions:

  * ``similarity``  - a Score over five ordered levels (0..4): how similarly is
    the current proposed FHIR mapping represented in the cited PHCDI CSV
    evidence, judged on DOCUMENTED meaning and workflow only.
  * ``counterpart`` - a Noul: does at least one cited PHCDI element correspond to
    the proposed assertion, rather than being only a generic resource container?

The deterministic comparator (``compare_phcdi_paths.py``) owns structural status.
This measure is advisory, carries probabilities and confidence, and never changes
the deterministic ``phcdiPathComparison``. It is not source verification, policy
approval, conformance, clinical correctness, or clinical equivalence.

The output is written atomically (tmp + replace) and only after every row
succeeds; any failure preserves the prior artifact and exits non-zero.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
API = 'https://api.typesafe.ai/v1/systemone'
MODEL = 'jev-latest'
OUT = ROOT / 'phcdi-similarity-jev.json'
ATTEMPTS = 5

# Five ordered levels, lowest (0) to highest (4). Exactly these strings.
LEVELS = [
    'No PHCDI element corresponds; any cited element is unrelated or only a generic container.',
    'A cited element is adjacent or a parent carrier only; meaning or workflow differs substantially.',
    'Partial overlap: some shared structure or intent, but important meaning, timing, granularity or workflow is missing.',
    'Substantial overlap in documented meaning and workflow, with minor unresolved differences.',
    'The cited element and the proposed assertion describe the same documented meaning and workflow.',
]
# Inclusive 0-100 band thresholds derived from similarityPct.
BANDS = [('none', 0, 24), ('weak', 25, 49), ('partial', 50, 74), ('close', 75, 100)]
CONFIDENCE_REVIEW = 0.5
COUNTERPART_REVIEW = 0.5

SIMILARITY_INSTRUCTION = (
    'Judge how similarly the proposed FHIR mapping assertion is represented in the historical PHCDI '
    'Release 01 CSV evidence. Compare `row.proposed_fhir_path_exact` together with `row.jao_source_definition` '
    'and `row.clinical_use_case` against `row.cited_phcdi_elements` (each element name and its definition '
    'text). Judge similarity of DOCUMENTED meaning and workflow only. This is not clinical correctness, '
    'conformance, approval, or equivalence, and level 4 still does not establish clinical equivalence. '
    'Treat `row.deterministic_phcdi_path_status` and its matched/total components as separate structural '
    'context only, never as the answer. Choose the single ordered level in `criteria` (0 lowest, 4 highest) '
    'that best describes the documented overlap.'
)
COUNTERPART_INSTRUCTION = (
    'Does at least one cited PHCDI element in `row.cited_phcdi_elements` correspond to the proposed '
    'assertion in `row.proposed_fhir_path_exact` and `row.jao_source_definition`? Answer yes when at least '
    'one cited element corresponds in documented meaning or workflow. Answer no when none corresponds; an '
    'element that is only a generic resource container (for example a bare resource name with no shared '
    'documented meaning) does not count as corresponding.'
)
COUNTERPART_CRITERIA = {
    'true': 'At least one cited PHCDI element corresponds to the proposed assertion in documented meaning or workflow (not merely a generic resource container).',
    'false': 'No cited PHCDI element corresponds to the proposed assertion; any resemblance is generic, lexical or only a container.',
}

LIMITATIONS = (
    'Advisory ranking signal only. Jev judges described text, not rendered meaning: it is not source '
    'verification, policy approval, FHIR conformance, clinical truth, clinical equivalence, or a binding. '
    'Probabilities and confidence are retained and low-confidence, low-counterpart or none/weak/partial-band '
    'rows are routed to human review. This measure never changes the deterministic phcdiPathComparison status.'
)


def band_for(pct: int) -> str:
    for name, low, high in BANDS:
        if low <= pct <= high:
            return name
    return 'none'


def pct_for(score: float) -> int:
    return int(round(score / 4 * 100))


def row_state(row: dict) -> dict:
    comparison = row['phcdiPathComparison']
    return {
        'scope': 'advisory similarity of documented meaning/workflow only; historical source; deterministic status unchanged',
        'row': {
            'excel_row': row['excel'],
            'jao_label': row['label'],
            'jao_source_path': row['sourcePath'],
            'jao_source_id': row['sourceId'],
            'jao_source_definition': row['definition'],
            'proposed_fhir_path_exact': row['fhirPath'],
            'proposed_profile_status': row.get('proposalStatus'),
            'clinical_use_case': row.get('useCase'),
            'deterministic_phcdi_path_status': comparison['status'],
            'deterministic_matched_components': comparison['matchedCount'],
            'deterministic_total_components': comparison['totalCount'],
            'cited_phcdi_elements': [
                {'physical_csv_row': ref['csvRow'], 'element': ref['element'], 'definition': ref['definition']}
                for ref in row['phcdiComparison']['references']
            ],
            'jao_deviation_note': row['phcdiComparison']['deviation'],
        },
    }


def request_row(key: str, row: dict) -> dict:
    payload = json.dumps({
        'state': row_state(row),
        'model': MODEL,
        'questions': {
            'similarity': {'type': 'score', 'instructions': SIMILARITY_INSTRUCTION, 'criteria': LEVELS},
            'counterpart': {'type': 'noul', 'instructions': COUNTERPART_INSTRUCTION, 'criteria': COUNTERPART_CRITERIA},
        },
    }).encode()
    last = None
    for attempt in range(ATTEMPTS):
        try:
            req = urllib.request.Request(API, data=payload, headers={
                'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=180) as resp:
                return json.loads(resp.read().decode())
        except Exception as exc:  # noqa: BLE001 - retry policy decided in code below
            code = getattr(exc, 'code', None)
            retryable = code in (429, 529) if code is not None else isinstance(
                exc, (urllib.error.URLError, TimeoutError, ConnectionError))
            last = exc
            if not retryable or attempt == ATTEMPTS - 1:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError(f'unreachable: {last}')


def score_answer(answer: dict, excel: int) -> dict:
    if answer.get('type') != 'score':
        raise RuntimeError(f'Row {excel}: similarity answer type {answer.get("type")!r}, expected score')
    levels = {str(i) for i in range(len(LEVELS))}
    if set(answer.get('probabilities', {})) != levels:
        raise RuntimeError(f'Row {excel}: similarity probabilities do not cover all five levels')
    score = float(answer['score'])
    if not 0 <= score <= len(LEVELS) - 1:
        raise RuntimeError(f'Row {excel}: similarity score {score} out of range')
    probabilities = {str(i): float(answer['probabilities'][str(i)]) for i in range(len(LEVELS))}
    confidence = float(answer.get('confidence', 0.0))
    return {'score': score, 'probabilities': probabilities, 'confidence': confidence}


def counterpart_answer(answer: dict, excel: int) -> float:
    if answer.get('type') != 'noul':
        raise RuntimeError(f'Row {excel}: counterpart answer type {answer.get("type")!r}, expected noul')
    value = float(answer['noul'])
    if not 0.0 <= value <= 1.0:
        raise RuntimeError(f'Row {excel}: counterpart probability {value} out of range')
    return value


def main() -> int:
    key = os.environ.get('TYPESAFE_API_KEY')
    if not key:
        raise RuntimeError('TYPESAFE_API_KEY is not set')

    index = json.loads((ROOT / 'mindmap-index.json').read_text())['rows']
    results = []
    usage = {'input_tokens': 0, 'output_tokens': 0}
    model = MODEL
    for position, row in enumerate(index, start=1):
        response = request_row(key, row)
        answers = response.get('answers', {})
        if set(answers) != {'similarity', 'counterpart'}:
            raise RuntimeError(f'Row {row["excel"]}: Jev returned {sorted(answers)} for two questions')
        sim = score_answer(answers['similarity'], row['excel'])
        counterpart = counterpart_answer(answers['counterpart'], row['excel'])
        pct = pct_for(sim['score'])
        band = band_for(pct)
        low_confidence = sim['confidence'] < CONFIDENCE_REVIEW
        comparable = counterpart >= COUNTERPART_REVIEW
        human_review = low_confidence or not comparable or band in ('none', 'weak', 'partial')
        model = response.get('model') or model
        row_usage = response.get('usage') or {}
        for field in ('input_tokens', 'output_tokens'):
            usage[field] += int(row_usage.get(field) or 0)
        results.append({
            'excel': row['excel'],
            'label': row['label'],
            'similarityScore': round(sim['score'], 4),
            'similarityPct': pct,
            'band': band,
            'probabilities': {level: round(prob, 4) for level, prob in sim['probabilities'].items()},
            'confidence': round(sim['confidence'], 4),
            'counterpartProbability': round(counterpart, 4),
            'counterpartProbabilities': {'true': round(counterpart, 4), 'false': round(1 - counterpart, 4)},
            'lowConfidence': low_confidence,
            'comparable': comparable,
            'humanReview': human_review,
            'deterministic': {
                'status': row['phcdiPathComparison']['status'],
                'matchedCount': row['phcdiPathComparison']['matchedCount'],
                'totalCount': row['phcdiPathComparison']['totalCount'],
                'algorithmVersion': row['phcdiPathComparison']['algorithmVersion'],
            },
            'citedElements': [
                {'physicalCsvRow': ref['csvRow'], 'element': ref['element']}
                for ref in row['phcdiComparison']['references']
            ],
            'model': model,
        })
        print(f'  [{position:>2}/{len(index)}] row {row["excel"]:>2} '
              f'pct={pct:>3} band={band:<7} sim={sim["score"]:.2f} conf={sim["confidence"]:.2f} '
              f'counterpart={counterpart:.2f} review={"yes" if human_review else "no"}', flush=True)

    pcts = [r['similarityPct'] for r in results]
    band_counts = {name: sum(1 for r in results if r['band'] == name) for name, _, _ in BANDS}
    output = {
        'model': model,
        'endpoint': API,
        'checkedAt': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'purpose': 'advisory per-row similarity of documented meaning/workflow between each proposed FHIR mapping and the historical PHCDI CSV evidence; never alters deterministic structural status',
        'measure': 'similarityPct = round(proposedScore/4*100) from a Jev Score over five ordered levels',
        'levels': LEVELS,
        'bands': {name: [low, high] for name, low, high in BANDS},
        'thresholds': {'confidenceReviewBelow': CONFIDENCE_REVIEW, 'counterpartReviewBelow': COUNTERPART_REVIEW,
                       'humanReviewBands': ['none', 'weak', 'partial']},
        'requested': len(index),
        'scored': len(results),
        'skipped': 0,
        'summary': {
            'meanSimilarityPct': round(sum(pcts) / len(pcts), 1),
            'bandCounts': band_counts,
            'comparableCount': sum(1 for r in results if r['comparable']),
            'lowConfidenceCount': sum(1 for r in results if r['lowConfidence']),
            'humanReviewCount': sum(1 for r in results if r['humanReview']),
            'limitations': LIMITATIONS,
        },
        'results': results,
        'usage': usage,
    }
    if output['scored'] != output['requested'] or output['skipped'] != 0:
        raise RuntimeError('Incomplete run; refusing to write')
    tmp = ROOT / 'phcdi-similarity-jev.json.tmp'
    tmp.write_text(json.dumps(output, indent=2, ensure_ascii=False) + '\n')
    tmp.replace(ROOT/'phcdi-similarity-jev.json')
    print(f"Jev {model}: scored={output['scored']} mean={output['summary']['meanSimilarityPct']} "
          f"bands={band_counts} humanReview={output['summary']['humanReviewCount']} "
          f"checkedAt={output['checkedAt']}")
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 - fail closed, preserve prior artifact
        print(f'Jev similarity measure failed; prior result preserved: {type(exc).__name__}: {exc}', file=sys.stderr)
        sys.exit(1)
