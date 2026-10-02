import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class PHCDIJevTest(unittest.TestCase):
 def test_34_advisory_choices_keep_distributions_and_routing(self):
  result=json.loads((ROOT/'phcdi-semantics-jev.json').read_text())
  index=json.loads((ROOT/'mindmap-index.json').read_text())['rows']
  self.assertEqual(result['requested'],34); self.assertEqual(result['scored'],34); self.assertEqual(result['skipped'],0)
  self.assertIn('cannot alter deterministic structural comparison',result['purpose'])
  self.assertEqual({r['excel'] for r in result['results']},{r['excel'] for r in index})
  for r in result['results']:
   self.assertIn(r['choice'],result['options'])
   self.assertGreaterEqual(r['confidence'],0); self.assertLessEqual(r['confidence'],1)
   self.assertLessEqual(abs(sum(r['probabilities'].values())-1),0.02)
  code=(ROOT/'evaluate-phcdi-semantics-jev.py').read_text()
  self.assertIn('tmp.replace(ROOT/\'phcdi-semantics-jev.json\')',code)
  self.assertIn('prior result preserved',code)
 def test_embedded_jev_is_advisory_not_structural_input(self):
  rows=json.loads((ROOT/'mindmap-index.json').read_text())['rows']
  for r in rows:
   self.assertIsNotNone(r['phcdiSemanticJev'])
   self.assertIn(r['phcdiPathComparison']['status'],{'exact','choice-base','parent-carrier','related-nonmatch','partial-gap','unsupported-extension/slice','none','undecided','unresolved-proposal'})
   self.assertIn('probabilities',r['phcdiSemanticJev'])

if __name__=='__main__': unittest.main()
