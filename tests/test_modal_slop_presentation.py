"""Focused checks for source-faithful modal presentation revisions."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'condition-row-profile-mindmap.html').read_text()
INDEX = json.loads((ROOT / 'mindmap-index.json').read_text())


class ModalSlopPresentationTests(unittest.TestCase):
    def test_all_source_rows_and_sections_remain_traced(self):
        self.assertEqual(len(INDEX['rows']), 34)
        self.assertEqual(len({r['section'] for r in INDEX['rows']}), 13)
        for row_id in (4, 23, 43, 49):
            row = next(r for r in INDEX['rows'] if r['excel'] == row_id)
            self.assertTrue(row['sourcePath'])
            self.assertTrue(row['sourceId'])
        self.assertIn("history.replaceState(null,'','#row-'+n)", HTML)
        self.assertIn('id="row-${r.excel}"', HTML)
        self.assertIn('const order=[\'patient\',\'pwdGap\',\'mortality\',\'encounter\',\'question\',\'problem\',\'recency\',\'copd\']', HTML)

    def test_row4_candidate_is_qualified_and_cites_policy(self):
        open_row = re.search(r'function openRow\(n,trigger\)\{.*?\nfunction openPath', HTML, re.S).group()
        self.assertIn('Candidate Patient registration path; validate national-list coverage against', open_row)
        self.assertIn('NCDA AO No. 001, s. 2021 (opens new tab)', open_row)
        self.assertIn('r.policyUrl', open_row)
        self.assertNotIn('Keep this row on PH Core Patient', open_row)

    def test_dialog_keeps_unresolved_question_and_source_destinations(self):
        self.assertIn('Human review question · unresolved', HTML)
        self.assertIn('Workbook crosswalk · Excel ${n} (opens new tab)', HTML)
        self.assertIn('Source logical element · row ${n} (opens new tab)', HTML)
        for target in ('row-source', 'row-phcdi', 'row-terminology', 'row-transaction'):
            self.assertIn(f'href="#{target}"', HTML)
            self.assertIn(f'id="{target}"', HTML)

    def test_phcdi_remains_separate_historical_comparison_with_csv_refs(self):
        self.assertIn('Proposed FHIR path vs PHCDI Release 01', HTML)
        self.assertIn('PHCDI is a different organization’s historical inventory', HTML)
        self.assertIn('PHCDI is a different organization’s historical inventory—not an approved JAO crosswalk, clinical recommendation, or current FHIR authority.', HTML)
        self.assertIn('CSV row ${esc(best.csvRow)} (opens file)', HTML)
        self.assertIn('condition-logical-model.html#/crosswalk/row/${esc(c.jaoWorkbookRow)}', HTML)
        self.assertIn('Full historical comparison', HTML)

    def test_quality_score_remains_accessible_and_separate_from_approval(self):
        self.assertIn('Quality review · ${quality} · mapping evidence only', HTML)
        self.assertIn('aria-label="${esc(aria)}"', HTML)
        self.assertIn('Scores judge this mapping\'s evidence — not clinical truth.', HTML)
        self.assertIn('qreview-disclosure', HTML)
        self.assertNotIn('Approve', re.search(r'function openRow\(n,trigger\)\{.*?\nfunction openPath', HTML, re.S).group())

    def test_mobile_jumps_scroll_horizontally_without_page_overflow(self):
        self.assertIn('.modal-jumps{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))', HTML)
        self.assertIn('.modal-jumps a{display:flex;align-items:center;min-width:0;min-height:44px', HTML)
        self.assertIn('target.focus({preventScroll:true});target.scrollIntoView({block:\'start\'})', HTML)
        self.assertIn('dialog.addEventListener(\'close\'', HTML)

    def test_evaluator_rubric_is_fixed_and_scores_typed_judgments(self):
        evaluator = (ROOT / 'evaluate-modal-slop-jev.py').read_text()
        self.assertIn("API = 'https://api.typesafe.ai/v1/systemone'", evaluator)
        self.assertIn("EXEMPLARS = [('4','mobile'),('23','desktop'),('43','desktop'),('49','mobile')]", evaluator)
        for dimension in ('redundancy', 'actionable_language', 'evidence_attribution', 'phcdi_historical_separation', 'mobile_density'):
            self.assertIn(f"'{dimension}'", evaluator)
        self.assertIn('Rubric level {level} interpretation:', evaluator)
        self.assertIn('Jev returns typed judgments/probabilities/confidence, not explanations.', evaluator)


if __name__ == '__main__':
    unittest.main()
