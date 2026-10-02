import csv
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PHCDIComparisonTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.crosswalk = json.loads((ROOT / 'condition-phcdi-comparison.json').read_text())
        cls.rows = json.loads((ROOT / 'mindmap-index.json').read_text())['rows']
        with (ROOT / cls.crosswalk['source']).open(encoding='utf-8-sig', newline='') as fh:
            cls.csv_rows = list(csv.reader(fh))
        cls.html = (ROOT / 'condition-row-profile-mindmap.html').read_text()

    def test_all_34_jao_rows_have_comparisons_and_live_csv_references(self):
        self.assertEqual(len(self.rows), 34)
        self.assertEqual(set(map(int, self.crosswalk['rows'])), {r['excel'] for r in self.rows})
        for row in self.rows:
            comparison = row['phcdiComparison']
            original = self.crosswalk['rows'][str(row['excel'])]
            self.assertEqual(comparison['relation'], original['relation'])
            self.assertEqual(comparison['deviation'], original['deviation'])
            self.assertEqual(comparison['sourceFile'], self.crosswalk['source'])
            for ref in original['references']:
                line, element = ref
                self.assertEqual(self.csv_rows[line - 1][1], element)
                embedded = next(x for x in comparison['references'] if x['csvRow'] == line)
                self.assertEqual(embedded['definition'], self.csv_rows[line - 1][2])

    def test_distinguishes_historical_overlap_from_jao_meaning(self):
        expected = {4: 'not-listed', 5: 'not-listed', 9: 'related',
                    23: 'meaning-conflict', 24: 'meaning-conflict',
                    43: 'not-listed', 46: 'related', 47: 'related', 49: 'not-listed'}
        for excel, relation in expected.items():
            item = self.crosswalk['rows'][str(excel)]
            self.assertEqual(item['relation'], relation)
            self.assertTrue(item['deviation'])
        self.assertIn('upload time', self.crosswalk['rows']['23']['deviation'])
        self.assertIn('HBCR/cancer', self.crosswalk['rows']['46']['deviation'])

    def test_modal_section_is_separate_and_explicitly_non_authoritative(self):
        self.assertIn('function phcdiBlock(r)', self.html)
        self.assertIn('PHCDI is a different organization’s historical inventory—not an approved JAO crosswalk, clinical recommendation, or current FHIR authority.', self.html)
        self.assertIn('not clinical equivalence', self.html)
        self.assertIn('CSV row ${esc(best.csvRow)} (opens file)', self.html)
        self.assertNotIn('}#L${esc(x.csvRow)}', self.html)
        self.assertIn('<div id="row-phcdi" tabindex="-1">${phcdiBlock(r)}</div><section id="row-terminology" class="terminology-section" tabindex="-1"', self.html)
        block = self.html.split('function phcdiBlock(r)', 1)[1].split('function openRow(n,trigger)', 1)[0]
        # The friendly status labels live once in a shared mapping reused by both the
        # row modal and the advisory similarity report table; phcdiBlock must reference it.
        self.assertEqual(self.html.count('const statusLabel='), 1)
        for label in ('Same element path · meaning unverified','Same R4 [x] base · type unproven','Parent carrier only','Related structure · not a match',
                      'No cited extension/slice match','No cited path match','Some proposed paths absent','Undecided / unresolved path'):
            self.assertIn(label, self.html)
        self.assertIn('statusLabel[best.status]', block)
        self.assertIn('statusLabel[cmp.status]', block)
        for label in ('JAO source trace · secondary','Structural difference · deterministic','Jev semantic signal'):
            self.assertIn(label, block)
        self.assertIn('esc(c.deviation)', block)
        self.assertIn('esc(best.element)', block)
        self.assertIn('esc(best.definition', block)
        self.assertIn('CSV row ${esc(best.csvRow)} (opens file)', block)
        self.assertIn('condition-logical-model.html#/crosswalk/row/${esc(c.jaoWorkbookRow)}', block)
        self.assertIn('${esc(best.matchedComponents)}/${esc(p.componentCount)}', block)
        self.assertIn('r.phcdiPathComparison', block)
        self.assertIn('Other cited CSV entries · not path matches', block)
        self.assertIn('const extraRefs=c.references.filter', block)
        self.assertIn('Jev does not alter the deterministic path status or establish clinical equivalence.', block)
        self.assertIn("c.relation==='meaning-conflict'||r.profileKey==='copd'", block)
        self.assertIn('JAO context:', block)
        self.assertIn('encodeURIComponent(c.sourceFile)', block)
        self.assertIn('@media(max-width:780px){.dialog-body,.compare li,.terminology-section p{overflow-wrap:anywhere}.phcdi-compare{grid-template-columns:minmax(0,1fr);gap:0}', self.html)

    def test_required_relation_examples_remain_distinct_and_source_backed(self):
        rows = {r['excel']: r for r in self.rows}
        self.assertEqual(rows[4]['phcdiComparison']['relation'], 'not-listed')
        self.assertEqual(rows[43]['phcdiComparison']['relation'], 'not-listed')
        self.assertEqual(rows[49]['phcdiComparison']['relation'], 'not-listed')
        self.assertEqual(rows[8]['phcdiPathComparison']['status'], 'choice-base')
        self.assertEqual(rows[23]['phcdiPathComparison']['status'], 'unsupported-extension/slice')
        self.assertEqual(rows[46]['phcdiPathComparison']['status'], 'exact')
        row23 = rows[23]
        self.assertEqual(row23['definition'], 'The date when the patient was diagnosed')
        self.assertEqual(row23['phcdiComparison']['references'][0]['csvRow'], 228)
        self.assertEqual(row23['phcdiComparison']['references'][0]['definition'],
                         'The recordedDate represents when this particular record was uploaded into the NHDR.')
        self.assertIn('not clinician diagnosis/assertion time', row23['phcdiComparison']['deviation'])
        self.assertIn('HBCR/cancer', rows[46]['phcdiComparison']['deviation'])


if __name__ == '__main__':
    unittest.main()
