#!/usr/bin/env python3
"""Independent row-to-subpath regression audit; not a profile/terminology validator."""
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

root = Path(__file__).resolve().parent
html = (root / 'condition-row-profile-mindmap.html').read_text()
index = json.loads((root / 'mindmap-index.json').read_text())
rows = json.loads(re.search(r'const ROWS=(.*?);\nconst PROFILES=', html, re.S).group(1))
profiles = json.loads(re.search(r'const PROFILES=(.*?);\nconst SOURCES=', html, re.S).group(1))
assert 'const linkCurve=d3.linkHorizontal()' in html
for name in ('d3-path-3.1.0.min.js', 'd3-shape-3.2.0.min.js'):
    assert (root / 'vendor' / name).read_text().strip() in html, f'Missing pinned {name} in standalone HTML'
js = re.search(r'const PATHS=(.*?);\nconst rawById', html, re.S).group(1)
paths = json.loads(subprocess.check_output(['node', '-e', f'console.log(JSON.stringify({js}))'], text=True))
# Independently reviewed source-row destination/subpath membership. Keep separate from the renderer.
expected = {
  4:'patient.type', 5:'pwdGap.permanence', 7:'question.question question.answer',
  8:'encounter.onset', 9:'mortality.code mortality.cause',
 10:'mortality.code mortality.description', 12:'problem.onset',
 13:'question.question question.answer', 15:'encounter.onset', 16:'encounter.onset',
 17:'encounter.code encounter.diagnosisLink', 19:'encounter.onset', 20:'encounter.onset',
 21:'encounter.code encounter.diagnosisLink', 23:'encounter.asserted', 24:'encounter.asserted',
 25:'encounter.code encounter.codeText', 26:'encounter.codeText', 27:'encounter.note',
 29:'question.question question.answer', 31:'problem.code', 32:'problem.codeText',
 33:'problem.code problem.status', 34:'problem.code', 35:'problem.note',
 37:'question.question question.answer', 39:'problem.code', 41:'problem.code',
 43:'recency.recency', 44:'problem.code', 46:'copd.spirometric',
 47:'copd.group', 48:'question.question question.answer', 49:'problem.evidenceDetail',
}
actual = defaultdict(set)
for group, entries in paths.items():
    assert group in profiles
    for path_id, label, ids in entries:
        assert len(ids) == len(set(ids)), (group, path_id)
        for n in ids:
            actual[n].add(f'{group}.{path_id}')
assert len(expected) == len(rows) == len(index['rows']) == 34
assert len({r['excel'] for r in rows}) == len(rows)
assert rows == index['rows'] and profiles == index['profiles'], 'Embedded diagram differs from generated index'
for row in rows:
    n = row['excel']
    assert actual[n] == set(expected[n].split()), (n, actual[n], expected[n])
    assert {s.split('.')[0] for s in actual[n]} == {row['profileKey']}, n
    assert row['sourcePath'].startswith('JAOConditionSheet.') and row['sourceId'].startswith('SRC'), n
    if n in (5,9,10,43):
        assert row['example'] is None, n
    else:
        bundle = json.loads((root / 'fhir-transactions' / row['example']).read_text())
        resource_types = {e['resource']['resourceType'] for e in bundle['entry']}
        expected_type = {'patient':'Patient', 'question':'Observation'}.get(row['profileKey'], 'Condition')
        assert expected_type in resource_types, (n, expected_type, resource_types)
        if n == 49:
            assert 'Observation' in resource_types
assert sum(map(len, paths.values())) == 22
assert len(actual) == 34
assert sum(map(len, actual.values())) == sum(len(v[2]) for entries in paths.values() for v in entries) == 45
print('34 source rows, 8 destinations, 22 subpaths and 45 flows agree with reviewed membership; examples have expected resource types.')
print('Semantic/profile/terminology conformance remains pending human and package-specific review.')
