import csv, json, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0,str(ROOT))
from compare_phcdi_paths import compare, split_proposal, components, ALGORITHM_VERSION

class ComparatorTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.index=json.loads((ROOT/'mindmap-index.json').read_text())['rows']
  cls.comparisons=json.loads((ROOT/'condition-phcdi-comparison.json').read_text())['rows']
  with (ROOT/'PHCDI Release 01(Core Datasets).csv').open(encoding='utf-8-sig',newline='') as f: cls.csv=list(csv.reader(f))
 def runrow(self,n):
  r=next(x for x in self.index if x['excel']==n)
  refs=[{'csvRow':line,'element':el,'definition':self.csv[line-1][2]} for line,el in self.comparisons[str(n)]['references']]
  return compare(r['fhirPath'],refs)
 def test_all_34_have_deterministic_algorithm_and_proposed_denominator(self):
  self.assertEqual(len(self.index),34)
  for row in self.index:
   result=row.get('phcdiPathComparison') or self.runrow(row['excel'])
   self.assertEqual(result['algorithmVersion'],ALGORITHM_VERSION)
   self.assertEqual(result['proposedComponents'],sum(p['componentCount'] for p in result['paths']))
   self.assertEqual(result['matchedCount'],result['matchedComponents'])
   self.assertIn(result['status'],{'exact','choice-base','parent-carrier','related-nonmatch','partial-gap','unsupported-extension/slice','none','undecided','unresolved-proposal'})
 def test_required_rows(self):
  expected={4:'unsupported-extension/slice',8:'choice-base',9:'parent-carrier',23:'unsupported-extension/slice',24:'unsupported-extension/slice',43:'unresolved-proposal',46:'exact',47:'exact',49:'none'}
  for n,status in expected.items(): self.assertEqual(self.runrow(n)['status'],status,n)
  self.assertEqual(self.runrow(8)['paths'][0]['normalizedComponents'],['Condition','onset[x]'])
  self.assertEqual(self.runrow(9)['status'],'parent-carrier')
  self.assertEqual([p['bestMatch']['status'] for p in self.runrow(9)['paths']],['exact','parent-carrier'])
  self.assertEqual(self.runrow(9)['matchedComponents'],4)
  self.assertEqual(self.runrow(46)['matchedComponents'],6)
  self.assertEqual(self.runrow(49)['matchedComponents'],0)
 def test_component_by_component_evidence_and_physical_source_definitions(self):
  for n in (4,8,9,23,24,43,46,47,49):
   result=self.runrow(n)
   for path in result['paths']:
    self.assertEqual(len(path['normalizedComponents']),path['componentCount'])
    if path['bestMatch']:
     self.assertTrue(path['bestMatch']['definition'])
     self.assertEqual(path['bestMatch']['definition'],self.csv[path['bestMatch']['csvRow']-1][2])
     self.assertEqual(len(path['bestMatch']['componentEvidence']),path['componentCount'])
 def test_no_token_overlap_or_definition_text_false_positives(self):
  ref=[{'csvRow':140,'element':'Encounter.diagnosis.condition','definition':'... evidence.detail ...'}]
  result=compare('Condition.evidence.detail',ref)
  self.assertEqual(result['status'],'none')
  self.assertIsNone(result['paths'][0]['bestMatch'])
  self.assertEqual(result['paths'][0]['references'][0]['element'],'Encounter.diagnosis.condition')
  self.assertEqual(compare('Observation.valueCodeableConcept.coding',[{'csvRow':304,'element':'Observation.value[x]','definition':'generic result'}])['status'],'parent-carrier')
  self.assertEqual(compare('Condition.foo.detail',[{'csvRow':1,'element':'Condition.bar.detail','definition':'foo detail'}])['status'],'none')
  self.assertEqual(compare('Condition.foo',[{'csvRow':1,'element':'Observation.foo','definition':'same leaf'}])['status'],'none')
  self.assertEqual(compare('Observation.code + Observation.valueCodeableConcept',[
   {'csvRow':299,'element':'Observation.code','definition':'name'},
   {'csvRow':304,'element':'Observation.value[x]','definition':'result'}])['status'],'choice-base')
  self.assertEqual(compare('Observation.code + Observation.valueCodeableConcept.coding',[
   {'csvRow':299,'element':'Observation.code','definition':'name'}])['status'],'partial-gap')
 def test_extensions_and_choices_keep_identity(self):
  self.assertEqual(components('Patient.extension:pwdDisability.extension:disabilityType.valueCodeableConcept'),['Patient','extension:pwdDisability','extension:disabilityType','value[x]'])
  self.assertEqual(components('Condition.onsetDateTime'),['Condition','onset[x]'])
  self.assertEqual(split_proposal('Condition.code.coding / Condition.code.text'),['Condition.code.coding','Condition.code.text'])
  self.assertEqual(compare('Patient.extension:pwdDisability',[])['status'],'unsupported-extension/slice')
  self.assertIsNone(compare('Patient.extension:pwdDisability',[{'csvRow':9,'element':'RegistrationNo','definition':'identifier'}])['paths'][0]['bestMatch'])
 def test_multiple_paths_do_not_borrow_overlap(self):
  got=compare('Observation.code + Condition.evidence.detail',[{'csvRow':299,'element':'Observation.code','definition':'code'}])
  self.assertEqual([x['bestMatch']['status'] if x['bestMatch'] else None for x in got['paths']],['exact',None])
  self.assertEqual(got['status'],'partial-gap')
  self.assertEqual(got['matchedComponents'],2)

if __name__=='__main__': unittest.main()
