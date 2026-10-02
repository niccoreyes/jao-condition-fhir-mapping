import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TerminologyDialogDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.loads((ROOT / 'mindmap-index.json').read_text())['rows']
        cls.by_excel = {row['excel']: row for row in cls.rows}
        cls.html = (ROOT / 'condition-row-profile-mindmap.html').read_text()
        cls.validation = json.loads((ROOT / 'terminology-validation.json').read_text())
        cls.checked = {(x['excel'], x['code']): x for x in cls.validation['results'] if x.get('ok')}

    def test_all_34_rows_keep_identity_and_dialog_option_structure(self):
        self.assertEqual(len(self.rows), 34)
        self.assertEqual(len(self.by_excel), 34)
        for row in self.rows:
            self.assertTrue(row['section'])
            self.assertTrue(row['label'])
            self.assertTrue(row['optionSources'])
            self.assertTrue(row['optionSources'][0]['label'])
            self.assertTrue(row['optionSources'][0]['options'] or row['optionSources'][0]['absence'])

    def test_validated_candidates_copy_authority_version_and_have_links(self):
        for row in self.rows:
            for candidate in row['candidateTerminology']:
                checked = self.checked[(row['excel'], candidate['code'])]
                self.assertEqual(candidate['system'], checked['system'])
                self.assertEqual(candidate['display'], checked['display'])
                self.assertEqual(candidate['validation']['version'], checked['version'])
                self.assertEqual(candidate['validation']['checkedAt'], self.validation['checkedAt'])
                self.assertTrue(candidate['link'].startswith('https://'))
                self.assertIn(candidate['role'], {'question (US certificate)','question (manual coding)','question (automated coding)','diagnosis','finding','registration','qualifier (not standalone finding)'})
                self.assertEqual(candidate['classification'], 'Proposed international candidate')

    def test_high_value_question_answers_are_not_presented_as_diagnosis_codes(self):
        for excel in (7, 29, 48):
            row = self.by_excel[excel]
            self.assertTrue(row['candidateTerminology'])
            self.assertTrue(all(c['role'] == 'diagnosis' for c in row['candidateTerminology']))
        self.assertIn('Yes', self.by_excel[29]['optionSources'][0]['options'])
        self.assertEqual(self.by_excel[48]['optionSources'][0]['options'], [])
        self.assertIn('No policy answer list verified', self.by_excel[48]['optionSources'][0]['absence'])
        for excel in (39, 43, 44, 46, 47, 49):
            self.assertIsNone(self.by_excel[excel]['policyUrl'])
            self.assertIn('2013-0005', self.by_excel[excel]['policyBasis'])
        self.assertEqual(self.by_excel[4]['existingPhCoreTerminology']['artifact'], 'ph-core-disability-type-vs')
        self.assertEqual(len(self.by_excel[4]['existingPhCoreTerminology']['codes']), 9)
        package = Path.home() / '.fhir/packages/fhir.ph.core#current/package/CodeSystem-ph-core-disability-type-cs.json'
        if package.exists():
            concepts = json.loads(package.read_text())['concept']
            self.assertEqual(self.by_excel[4]['existingPhCoreTerminology']['codes'],
                             [{'code': item['code'], 'display': item['display']} for item in concepts])
        self.assertEqual(len(self.by_excel[9]['candidateTerminology']), 3)
        self.assertFalse(self.by_excel[10]['candidateTerminology'])
        self.assertIn('not mean no code exists', self.by_excel[10]['candidateAbsence'])

    def test_ranges_and_no_candidate_are_explicit_gaps(self):
        for excel, expected in ((39,'I10–I15'),(41,'I60–I64'),(44,'E10–E14'),(48,'A15–A16'),(29,'O10–O16')):
            self.assertEqual(self.by_excel[excel]['terminologyRange'], expected)
        for excel in (39,41,43,44,46,47,49):
            self.assertFalse(self.by_excel[excel]['candidateTerminology'])
            self.assertIn('not mean no code exists', self.by_excel[excel]['candidateAbsence'])

    def test_terminology_has_own_modal_section_and_measured_desktop_width(self):
        opener = self.html.split('function openRow(n,trigger)', 1)[1].split('function openPath', 1)[0]
        self.assertIn('<div id="row-phcdi" tabindex="-1">${phcdiBlock(r)}</div><section id="row-terminology" class="terminology-section" tabindex="-1"', opener)
        self.assertLess(opener.index('${qualityBlock(r)}'), opener.index('${terminologyBlock(r)}'))
        self.assertIn('href="#row-source"', opener)
        self.assertIn('href="#row-transaction"', opener)
        metrics = json.loads((ROOT / 'terminology-presentation-layout.json').read_text())
        self.assertEqual(metrics['terminologyParent'], 'dialog-body')
        self.assertFalse(metrics['desktopHorizontalScrollRequired'])
        self.assertGreaterEqual(metrics['tableViewportShareOfModal'], .8)

    def test_safe_semantic_responsive_dialog_rendering_is_present(self):
        self.assertIn('function terminologyBlock(r)', self.html)
        self.assertIn('esc(c.code)', self.html)
        self.assertIn('<caption>Existing PH Core and proposed candidate concepts</caption>', self.html)
        self.assertIn('<th scope="col">Role</th>', self.html)
        self.assertIn('No row-specific code proposed or checked.', self.html)
        self.assertIn('@media(max-width:780px){', self.html)
        self.assertIn('.dialog-cols{grid-template-columns:minmax(0,1fr)}', self.html)
        self.assertIn('.term-table-scroll{width:100%;max-width:100%;min-width:0;overflow-x:auto', self.html)
        self.assertIn('aria-label="Terminology comparison table; scroll horizontally on narrow screens"', self.html)
        self.assertIn('function openRow(n,trigger)', self.html)
        self.assertIn("'#row-'+n", self.html)


if __name__ == '__main__':
    unittest.main()
