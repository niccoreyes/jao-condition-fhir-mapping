"""Invariants for the advisory per-row Jev PHCDI similarity measure.

The measure is advisory: it must never alter the deterministic structural status
produced by `compare_phcdi_paths.compare`, and must stay separated in the UI from
any approval-style control.
"""
import csv
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from compare_phcdi_paths import compare as compare_phcdi_paths  # noqa: E402

LEVELS = [
    'No PHCDI element corresponds; any cited element is unrelated or only a generic container.',
    'A cited element is adjacent or a parent carrier only; meaning or workflow differs substantially.',
    'Partial overlap: some shared structure or intent, but important meaning, timing, granularity or workflow is missing.',
    'Substantial overlap in documented meaning and workflow, with minor unresolved differences.',
    'The cited element and the proposed assertion describe the same documented meaning and workflow.',
]
BAND_RANGES = {'none': (0, 24), 'weak': (25, 49), 'partial': (50, 74), 'close': (75, 100)}


def band_for(pct):
    for name, (low, high) in BAND_RANGES.items():
        if low <= pct <= high:
            return name
    raise AssertionError(f'no band for {pct}')


class PHCDISimilarityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.measure = json.loads((ROOT / 'phcdi-similarity-jev.json').read_text())
        cls.rows = json.loads((ROOT / 'mindmap-index.json').read_text())['rows']
        cls.index = json.loads((ROOT / 'mindmap-index.json').read_text())
        cls.crosswalk = json.loads((ROOT / 'condition-phcdi-comparison.json').read_text())
        with (ROOT / cls.crosswalk['source']).open(encoding='utf-8-sig', newline='') as fh:
            cls.csv_rows = list(csv.reader(fh))
        cls.html = (ROOT / 'condition-row-profile-mindmap.html').read_text()
        cls.by_excel = {r['excel']: r for r in cls.rows}

    def test_34_rows_and_exact_ordered_levels(self):
        self.assertEqual(self.measure['requested'], 34)
        self.assertEqual(self.measure['scored'], 34)
        self.assertEqual(self.measure['skipped'], 0)
        self.assertEqual(self.measure['levels'], LEVELS)
        self.assertEqual({r['excel'] for r in self.measure['results']}, {r['excel'] for r in self.rows})
        self.assertIn('advisory', self.measure['purpose'].lower())
        self.assertIn('never alters deterministic structural status', self.measure['purpose'])
        self.assertEqual(self.measure['bands'], {k: list(v) for k, v in BAND_RANGES.items()})

    def test_percent_matches_score_band_and_probabilities(self):
        for r in self.measure['results']:
            self.assertEqual(r['similarityPct'], round(r['similarityScore'] / 4 * 100), r['excel'])
            self.assertEqual(r['band'], band_for(r['similarityPct']), r['excel'])
            self.assertGreaterEqual(r['similarityScore'], 0)
            self.assertLessEqual(r['similarityScore'], 4)
            # Both questions keep a full probability distribution.
            self.assertEqual(set(r['probabilities']), {str(i) for i in range(5)})
            self.assertLessEqual(abs(sum(r['probabilities'].values()) - 1), 0.02, r['excel'])
            self.assertEqual(set(r['counterpartProbabilities']), {'true', 'false'})
            self.assertLessEqual(abs(sum(r['counterpartProbabilities'].values()) - 1), 0.02, r['excel'])
            self.assertGreaterEqual(r['counterpartProbability'], 0)
            self.assertLessEqual(r['counterpartProbability'], 1)
            self.assertGreaterEqual(r['confidence'], 0)
            self.assertLessEqual(r['confidence'], 1)
            expected_review = (r['confidence'] < 0.5 or r['counterpartProbability'] < 0.5
                               or r['band'] in ('none', 'weak', 'partial'))
            self.assertEqual(r['humanReview'], expected_review, r['excel'])

    def test_summary_counts_match_results(self):
        summary = self.measure['summary']
        results = self.measure['results']
        pcts = [r['similarityPct'] for r in results]
        self.assertEqual(summary['meanSimilarityPct'], round(sum(pcts) / len(pcts), 1))
        self.assertEqual(summary['bandCounts'], {b: sum(1 for r in results if r['band'] == b) for b in BAND_RANGES})
        self.assertEqual(summary['humanReviewCount'], sum(1 for r in results if r['humanReview']))
        self.assertEqual(summary['comparableCount'], sum(1 for r in results if r['comparable']))
        self.assertEqual(summary['lowConfidenceCount'], sum(1 for r in results if r['lowConfidence']))
        self.assertIn('not source verification', summary['limitations'])
        self.assertIn('never changes the deterministic', summary['limitations'])

    def test_jev_never_changes_deterministic_path_status(self):
        """Recompute the deterministic comparison independently and match both artifacts."""
        for r in self.rows:
            original = self.crosswalk['rows'][str(r['excel'])]
            refs = [{'csvRow': line, 'element': element, 'definition': self.csv_rows[line - 1][2]}
                    for line, element in original['references']]
            recomputed = compare_phcdi_paths(r['fhirPath'], refs)
            self.assertEqual(recomputed['status'], r['phcdiPathComparison']['status'], r['excel'])
            self.assertEqual(recomputed['matchedCount'], r['phcdiPathComparison']['matchedCount'], r['excel'])
            self.assertEqual(recomputed['totalCount'], r['phcdiPathComparison']['totalCount'], r['excel'])
            self.assertIsNotNone(r['phcdiSimilarity'])
            self.assertEqual(r['phcdiSimilarity']['similarityPct'],
                             next(x['similarityPct'] for x in self.measure['results'] if x['excel'] == r['excel']))
        for result in self.measure['results']:
            embedded = self.by_excel[result['excel']]['phcdiPathComparison']
            self.assertEqual(result['deterministic']['status'], embedded['status'], result['excel'])
            self.assertEqual(result['deterministic']['matchedCount'], embedded['matchedCount'], result['excel'])
            self.assertEqual(result['deterministic']['totalCount'], embedded['totalCount'], result['excel'])
            self.assertEqual(result['deterministic']['algorithmVersion'], embedded['algorithmVersion'])

    def test_evaluator_fails_closed_and_writes_atomically(self):
        code = (ROOT / 'evaluate-phcdi-similarity-jev.py').read_text()
        self.assertIn("tmp.replace(ROOT/'phcdi-similarity-jev.json')", code)
        self.assertIn('prior result preserved', code)
        self.assertIn("time.sleep(2 ** attempt)", code)
        self.assertIn('429, 529', code)
        self.assertIn("'questions': {\n            'similarity'", code)

    def test_html_report_section_measure_and_accessibility(self):
        self.assertIn('id="similarity-report"', self.html)
        self.assertIn('id="similarity-report-title"', self.html)
        self.assertIn('Advisory PHCDI similarity report', self.html)
        report = self.html.split('<section id="similarity-report"', 1)[1]
        report = report.split('<section class="section" aria-labelledby="validation-title"', 1)[0]
        # Summary, band legend, jump/skip target and focusable scroll region.
        self.assertIn('id="similarity-report-summary"', report)
        self.assertIn('Skip to the 34-row similarity table', report)
        self.assertIn('id="similarity-report-scroll"', report)
        self.assertIn('role="region"', report)
        self.assertIn('tabindex="0"', report)
        for band_label in ('None 0–24', 'Weak 25–49', 'Partial 50–74', 'Close 75–100'):
            self.assertIn(band_label, report)
        self.assertIn('id="similarity-report-rows"', report)
        self.assertIn('Deterministic status · matched/total', report)
        self.assertIn('Similarity · band', report)
        self.assertIn('Review flag', report)
        # Explicit advisory disclaimer.
        self.assertIn('it never changes the deterministic structural status', report)
        self.assertIn('not verify sources, policy, conformance or clinical validity', report)
        # No approval control anywhere in the report.
        self.assertNotIn('Approve', report)
        self.assertNotIn('approve', report.lower())

    def test_per_row_dialog_measure_is_advisory_and_accessible(self):
        self.assertIn('function phcdiBlock(r)', self.html)
        self.assertIn('${simMeasure(r)}', self.html)
        block = self.html.split('function phcdiBlock(r)', 1)[1].split('function openRow(n,trigger)', 1)[0]
        self.assertIn('${simMeasure(r)}', block)
        self.assertIn('Advisory Jev similarity measure, separate from the deterministic structural status above', block)
        table_row = self.html.split('function simTableRow(r)', 1)[1].split('function renderSimilarityReport()', 1)[0]
        self.assertIn('<a href="#row-${esc(r.excel)}">Open row ${esc(r.excel)} detail</a>', table_row)
        self.assertIn('separate from the deterministic structural status', table_row)
        self.assertIn('Not clinical equivalence, conformance or approval.', table_row)
        measure = self.html.split('function simMeasure(r)', 1)[1].split('function simTableRow(r)', 1)[0]
        self.assertIn('role="img"', measure)
        self.assertIn('aria-label="${esc(aria)}"', measure)
        self.assertIn('not clinical equivalence, conformance or approval', measure)
        self.assertIn('${s.similarityPct}', measure)
        self.assertIn('confidence ${conf}% · counterpart ${cp}%', measure)
        self.assertNotIn('Approve', block)

    def test_html_embeds_generated_similarity_metadata(self):
        raw = re.search(r'const PHCDI_SIMILARITY=(.*?);\nconst esc=', self.html, re.S).group(1)
        meta = json.loads(raw)
        self.assertEqual(meta['summary']['meanSimilarityPct'], self.measure['summary']['meanSimilarityPct'])
        self.assertEqual(meta['summary']['bandCounts'], self.measure['summary']['bandCounts'])
        self.assertEqual(meta['levels'], LEVELS)
        self.assertEqual(meta['model'], self.measure['model'])
        self.assertEqual(meta['checkedAt'], self.measure['checkedAt'])
        self.assertIn('function renderSimilarityReport()', self.html)
        self.assertIn('render();renderSimilarityReport();', self.html)


if __name__ == '__main__':
    unittest.main()
