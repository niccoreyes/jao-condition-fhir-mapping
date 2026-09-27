#!/usr/bin/env python3
"""Validate candidate SNOMED CT / LOINC concepts against public FHIR terminology servers.

Primary server: HL7 FHIRsmith, https://tx.fhir.org/r4 (public, HL7-hosted).
Fallback server: FHIRLab, https://tx.fhirlab.net/fhir (temporary community server).

Every run records the server used and the code-system *version* it returned,
because a candidate valid in one SNOMED/LOINC release may not exist in another.

This checks terminology meaning only. It does NOT claim a binding, and it does
not establish that a code is appropriate for a worksheet row (policy review in
condition-terminology-policy-review.md governs that).
"""
from pathlib import Path
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

PRIMARY = 'https://tx.fhir.org/r4'          # HL7 FHIRsmith
FALLBACK = 'https://tx.fhirlab.net/fhir'    # community server, temporary
OUT = Path(__file__).resolve().parent / 'terminology-validation.json'

# (worksheet row, role, system, code) -- candidates only, never bindings.
CANDIDATES = [
    (7,  'confirmed COVID-19 diagnosis (not the case-status question)', 'http://snomed.info/sct', '840539006'),
    (29, 'pre-eclampsia (narrower than all PIH)', 'http://snomed.info/sct', '398254007'),
    (48, 'pulmonary tuberculosis disorder (not the question answer)', 'http://snomed.info/sct', '154283005'),
    (9,  'US certificate Part I cause-of-death line', 'http://loinc.org', '69453-9'),
    (9,  'manually assigned underlying cause of death', 'http://loinc.org', '80359-3'),
    (9,  'automatically selected underlying cause of death', 'http://loinc.org', '80358-5'),
    # PWD scoping (rows 4-5): disability framing and permanence candidates.
    (4,  'disability / body failure state (broad umbrella)', 'http://snomed.info/sct', '105719004'),
    (4,  'disability (general finding)', 'http://snomed.info/sct', '21134002'),
    (4,  'registered disabled (administrative status)', 'http://snomed.info/sct', '161048004'),
    (4,  'disability - severe (severity qualifier)', 'http://snomed.info/sct', '161045001'),
    (5,  'permanent (qualifier value)', 'http://snomed.info/sct', '6934004'),
]

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={'Accept': 'application/fhir+json'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())

def params_to_dict(data, prefix=''):
    got = {}
    for p in data.get('parameter', []):
        name = prefix + p['name']
        for key in ('valueString', 'valueCode', 'valueUri', 'valueBoolean'):
            if key in p:
                got[name] = p[key]
                break
    return got

def lookup(base, system, code):
    q = urllib.parse.urlencode({'system': system, 'code': code})
    got = params_to_dict(fetch(f'{base}/CodeSystem/$lookup?{q}'))
    return {'ok': bool(got.get('display') or got.get('name')),
            'display': got.get('display') or got.get('name'),
            'version': got.get('version'), 'operation': '$lookup'}

def validate_code(base, system, code):
    q = urllib.parse.urlencode({'url': system, 'code': code})
    got = params_to_dict(fetch(f'{base}/CodeSystem/$validate-code?{q}'))
    return {'ok': got.get('result') is True, 'display': got.get('display'),
            'version': got.get('version'), 'operation': '$validate-code'}

def try_server(base, system, code):
    errors = []
    for op in (lookup, validate_code):
        try:
            r = op(base, system, code)
            r['server'] = base
            return r
        except Exception as e:                      # HTTP error, timeout, bad JSON
            errors.append(f'{op.__name__}:{type(e).__name__}')
    return {'ok': False, 'server': base, 'system': system, 'code': code,
            'error': ' / '.join(errors)}

def validate_one(system, code):
    for base in (PRIMARY, FALLBACK):
        r = try_server(base, system, code)
        if r.get('version') or r.get('ok'):
            return {**r, 'system': system, 'code': code}
    return {**r, 'system': system, 'code': code, 'reachable': False}

def main():
    results, used = [], set()
    for row, role, system, code in CANDIDATES:
        r = validate_one(system, code)
        if r.get('display'):
            used.add(r['server'])
        results.append({'excel': row, 'role': role, **r})
    payload = {
        'primaryServer': PRIMARY,
        'fallbackServer': FALLBACK,
        'serversResponding': sorted(used),
        'checkedAt': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'note': 'HL7 FHIRsmith (tx.fhir.org) is the primary public server; versions are those it returned at checkedAt.',
        'results': results,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n')
    print(f"primary {PRIMARY}  fallback {FALLBACK}  checkedAt={payload['checkedAt']}")
    for r in results:
        print(f"  [{'OK ' if r.get('ok') else 'FAIL'}] row {r['excel']:>2} {r['system'].split('/')[-1]} {r['code']:<10} "
              f"server={r.get('server','-')} v={r.get('version')} {r.get('display') or r.get('error','')}")
    print(f'Wrote {OUT.name}. Public terminology check; version recorded per code. Not a binding.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
