#!/usr/bin/env python3
"""Validate candidate SNOMED CT / LOINC concepts against the FHIRLab terminology server.

Temporary terminology authority: https://tx.fhirlab.net/fhir
Every run records the code-system *version* returned by the server, because a
candidate that is valid in one SNOMED/LOINC release may not be in another.

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

BASE = 'https://tx.fhirlab.net/fhir'
OUT = Path(__file__).resolve().parent / 'terminology-validation.json'

# (worksheet row, role, system, code) -- candidates only, never bindings.
CANDIDATES = [
    (7,  'confirmed COVID-19 diagnosis (not the case-status question)', 'http://snomed.info/sct', '840539006'),
    (29, 'pre-eclampsia (narrower than all PIH)', 'http://snomed.info/sct', '398254007'),
    (48, 'pulmonary tuberculosis disorder (not the question answer)', 'http://snomed.info/sct', '154283005'),
    (9,  'US certificate Part I cause-of-death line', 'http://loinc.org', '69453-9'),
    (9,  'manually assigned underlying cause of death', 'http://loinc.org', '80359-3'),
    (9,  'automatically selected underlying cause of death', 'http://loinc.org', '80358-5'),
]

def lookup(system, code, timeout=30):
    params = urllib.parse.urlencode({'system': system, 'code': code})
    req = urllib.request.Request(f'{BASE}/CodeSystem/$lookup?{params}',
                                 headers={'Accept': 'application/fhir+json'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode())
    got = {}
    for p in data.get('parameter', []):
        if 'valueString' in p:
            got[p['name']] = p['valueString']
        elif 'valueCode' in p:
            got[p['name']] = p['valueCode']
    return got

def validate_one(system, code):
    """$lookup gives name/display/version; fall back to $validate-code."""
    try:
        got = lookup(system, code)
        return {'reachable': True, 'ok': bool(got.get('display') or got.get('name')),
                'display': got.get('display') or got.get('name'),
                'version': got.get('version'), 'system': got.get('system', system),
                'code': got.get('code', code), 'operation': '$lookup'}
    except Exception as lookup_error:
        try:
            params = urllib.parse.urlencode({'url': system, 'code': code})
            req = urllib.request.Request(f'{BASE}/CodeSystem/$validate-code?{params}',
                                         headers={'Accept': 'application/fhir+json'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
            got = {p['name']: (p.get('valueString') or p.get('valueBoolean') or p.get('valueCode'))
                   for p in data.get('parameter', [])}
            return {'reachable': True, 'ok': got.get('result') is True,
                    'display': got.get('display'), 'version': got.get('version'),
                    'system': system, 'code': code, 'operation': '$validate-code',
                    'note': f'$lookup failed: {type(lookup_error).__name__}'}
        except Exception as validate_error:
            return {'reachable': False, 'ok': False, 'system': system, 'code': code,
                    'error': f'{type(lookup_error).__name__} / {type(validate_error).__name__}'}

def main():
    results, reachable = [], False
    for row, role, system, code in CANDIDATES:
        r = validate_one(system, code)
        reachable = reachable or r['reachable']
        results.append({'excel': row, 'role': role, 'system': system, 'code': code, **r})
    payload = {
        'server': BASE,
        'checkedAt': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'serverReachable': reachable,
        'note': ('Server unreachable during this run; re-run when it responds to record code-system versions.'
                 if not reachable else 'Code-system versions below are those returned by the server at checkedAt.'),
        'results': results,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n')
    print(f'FHIRLab {BASE}  reachable={reachable}  checkedAt={payload["checkedAt"]}')
    for r in results:
        if r['reachable']:
            print(f"  [{'OK ' if r['ok'] else 'FAIL'}] row {r['excel']:>2} {r['system'].split('/')[-1]} {r['code']:<10} "
                  f"v={r['version']} {r.get('display')}")
        else:
            print(f"  [DOWN] row {r['excel']:>2} {r['system']} {r['code']}  {r.get('error')}")
    print(f'Wrote {OUT.name}. Temporary terminology authority; version recorded per code. Not a binding.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
