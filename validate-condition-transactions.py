#!/usr/bin/env python3
"""Validate generated synthetic Bundles against cached FHIR R4 schema and transaction rules.

This is not terminology or proposed-PH-profile conformance validation.
"""
from pathlib import Path
import json
import sys
from jsonschema import Draft6Validator

ROOT=Path(__file__).resolve().parent
PACKAGE=Path.home()/'.fhir/packages/hl7.fhir.r4.core#4.0.1/package/openapi/fhir.schema.json'
if not PACKAGE.exists():
    sys.exit('Missing local hl7.fhir.r4.core#4.0.1 JSON schema package.')
s=json.loads(PACKAGE.read_text())
validator=Draft6Validator({'$schema':s['$schema'],'$ref':'#/definitions/Bundle','definitions':s['definitions']})
files=sorted((ROOT/'fhir-transactions').glob('Transaction-Excel-*.json'))
if len(files)!=30:sys.exit(f'Expected 30 transaction examples, found {len(files)}')
issues=[]
for path in files:
    bundle=json.loads(path.read_text())
    for error in validator.iter_errors(bundle):issues.append(f'{path.name}: schema {list(error.path)}: {error.message}')
    if bundle.get('resourceType')!='Bundle' or bundle.get('type')!='transaction':
        issues.append(f'{path.name}: must be a transaction Bundle')
    entries=bundle.get('entry',[]);full_urls=[e.get('fullUrl') for e in entries]
    if len(full_urls)!=len(set(full_urls)) or not all(isinstance(url,str) and url.startswith('urn:uuid:') for url in full_urls):
        issues.append(f'{path.name}: invalid or duplicate transaction fullUrl')
    for entry in entries:
        r=entry.get('resource',{});t=r.get('resourceType');request=entry.get('request',{})
        if request!={'method':'POST','url':t}:issues.append(f'{path.name}: POST request for {t} must use its resource type')
        required={'Condition':('subject','code'),'Encounter':('status','class'),'Observation':('status','code','subject')}
        for field in required.get(t,()):
            if not r.get(field):issues.append(f'{path.name}: {t}.{field} missing')
        refs=[r[k]['reference'] for k in ('subject','encounter') if isinstance(r.get(k),dict) and 'reference' in r[k]]
        refs += [x['condition']['reference'] for x in r.get('diagnosis',[]) if x.get('condition',{}).get('reference')]
        refs += [x['reference'] for ev in r.get('evidence',[]) for x in ev.get('detail',[]) if x.get('reference')]
        for ref in refs:
            if ref not in full_urls:issues.append(f'{path.name}: unresolved local reference {ref}')
if issues:sys.exit('\n'.join(issues))
print(f'{len(files)} synthetic transaction Bundles pass local FHIR R4 JSON schema and transaction-reference checks. Profile and terminology validation not performed.')
