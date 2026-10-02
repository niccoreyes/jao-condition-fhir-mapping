"""Focused static invariants for the row modal hierarchy/navigation."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'condition-row-profile-mindmap.html').read_text()
INDEX = json.loads((ROOT / 'mindmap-index.json').read_text())


class ModalReadabilityTests(unittest.TestCase):
    def test_modal_jumps_cover_major_full_width_sections(self):
        for target in ('row-source', 'row-phcdi', 'row-terminology', 'row-transaction'):
            self.assertIn(f'href="#{target}"', HTML)
            self.assertIn(f'id="{target}"', HTML)
        self.assertIn('aria-label="Jump to row evidence"', HTML)

    def test_decision_summary_keeps_question_and_recommendation_distinct(self):
        open_row = re.search(r'function openRow\(n,trigger\)\{.*?\nfunction openPath', HTML, re.S).group()
        self.assertIn('Working proposal', open_row)
        self.assertIn('Human review question · unresolved', open_row)
        self.assertNotIn('Approve', open_row)
        self.assertIn('qualityBlock(r)', open_row)
        self.assertLess(open_row.index('modal-jumps'), open_row.index('qualityBlock(r)'))

    def test_phcdi_is_explicitly_historical_and_not_advice(self):
        self.assertIn('historical comparison', HTML)
        self.assertIn('PHCDI is a different organization’s historical inventory—not an approved JAO crosswalk, clinical recommendation, or current FHIR authority.', HTML)

    def test_inventory_and_transactions_unchanged(self):
        self.assertEqual(len(INDEX['rows']), 34)
        self.assertEqual(len(INDEX['profiles']), 8)
        self.assertIn("const order=['patient','pwdGap','mortality','encounter','question','problem','recency','copd']", HTML)
        self.assertIn('[49]', HTML)
        self.assertEqual(len(list((ROOT / 'fhir-transactions').glob('*.json'))), 30)
        for n in (4, 23, 43, 49):
            self.assertTrue(any(row['excel'] == n for row in INDEX['rows']))

    def test_modal_owns_scroll_and_keyboard_focus_style(self):
        self.assertRegex(HTML, r'dialog\{[^}]*overflow-y:auto')
        self.assertIn('overscroll-behavior:contain', HTML)
        self.assertIn('a:focus-visible,button:focus-visible', HTML)
        self.assertIn('target.focus({preventScroll:true});target.scrollIntoView({block:\'start\'})', HTML)
        self.assertIn('e.preventDefault()', HTML)
        self.assertIn('(origin?.isConnected?origin:search)?.focus', HTML)
        self.assertIn('Workbook crosswalk · Excel ${n} (opens new tab)', HTML)
        self.assertIn('Source logical element · row ${n} (opens new tab)', HTML)


if __name__ == '__main__':
    unittest.main()
