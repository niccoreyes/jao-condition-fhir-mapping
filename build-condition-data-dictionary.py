#!/usr/bin/env python3
"""Build a compact, editable DOCX assertion-review worksheet for all 34 JAO rows.

Requires pandoc; stdlib otherwise. Source label/definition/section and empty terminology
binding are checked against the XLSX before building. The Word tables are editable.
"""
import json
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BOOK = ROOT / 'FHIR MAPPING_DOH-PHIC-JAO-No-2021-002 - Dictionary.xlsx'
OUT = ROOT / 'condition-jao-data-dictionary-review.docx'
GOLD = 'https://goldcopd.org/2026-gold-report-and-pocket-guide/'
PWD_B = 'https://ncda.gov.ph/wp-content/uploads/2023/07/ao2013-0005-B.pdf'
PHCORE = 'https://build.fhir.org/ig/UPM-NTHC/ph-core/ValueSet-ph-core-disability-type-vs.html'
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
Q = '{' + W + '}'
ET.register_namespace('w', W)

# Deliberately short, falsifiable proposed assertions. Each is a question for the
# reviewer, not a replacement for the exact worksheet definition printed alongside it.
ASSERTION = {
 4: 'PWD registration disability category on Patient; not itself a diagnosis.',
 5: 'Explicit permanence answer; blank, No, and unassessed are distinct.',
 7: 'COVID case-status answer; a confirmed diagnosis is a separate assertion.',
 8: 'Onset date of a named encounter illness, not encounter start.',
 9: 'Coded underlying cause of death; coding stage must be identified.',
 10: 'Verbatim underlying-cause wording paired with row 9 and certificate line.',
 12: 'First COVID signs/symptoms date; do not imply confirmed COVID.',
 13: 'Explicit history-of-other-illness response, not a disease diagnosis.',
 15: 'Date of one DETECTED ISSUE complication, paired only with row 16.',
 16: 'Clock time of the same row-15 complication and event.',
 17: 'A separately diagnosed DETECTED ISSUE complication if clinically asserted.',
 19: 'Date of one COMPLICATIONS-section event, paired only with row 20.',
 20: 'Clock time of the same row-19 complication and event.',
 21: 'A separately diagnosed COMPLICATIONS-section event if asserted.',
 23: 'Clinician diagnosis assertion date, distinct from record creation/upload.',
 24: 'Time of the same row-23 assertion; offset and date required for dateTime.',
 25: 'Specific clinically asserted diagnosis code, not an ICD range.',
 26: 'Original diagnosis description paired with row 25; not a second diagnosis.',
 27: 'Narrative remarks qualifying the diagnosis, not hidden status/codes.',
 29: 'PIH/pre-eclampsia question answer; No/None is not a diagnosis.',
 31: 'Named past disease only when clinically established; status is explicit.',
 32: 'Text describing the row-31 disease, not a duplicate Condition.',
 33: 'Named present illness only if asserted; “active” is not inferred.',
 34: 'One independently asserted disease per co-morbidity, not one list code.',
 35: 'General history narrative unless clearly tied to one Condition.',
 37: 'Specified admission symptom as a finding or question answer; not automatically a Condition.',
 39: 'Clinically supported hypertension subtype, not the I10–I15 range.',
 41: 'Clinically supported stroke subtype; unspecified remains possible.',
 43: 'Registry diagnosis-recency answer relative to a defined time window.',
 44: 'Clinically supported diabetes type, not the E10–E14 range.',
 46: 'GOLD spirometric grade, with its assessment and edition; not COPD group.',
 47: 'GOLD symptom/exacerbation group, edition and assessment date; not grade.',
 48: 'Explicit pulmonary-TB question answer, separate from an established TB diagnosis.',
 49: 'Actual documented basis of final asthma diagnosis; COPD section placement needs review.',
}

# The short policy label is a navigation aid, not a claim that the issuance mandates
# this specific field. Detailed source qualification appears in the legend and notes.
POLICY = {
 4: ('NCDA AO 001 s.2021; DOH PRPWD v4.0 (-B)', 'https://ncda.gov.ph/disability-laws/administrative-orders/ncda-administrative-order-no-001-series-of-2021/'),
 5: ('NCDA AO 001 s.2021 (eligibility)', 'https://ncda.gov.ph/disability-laws/administrative-orders/ncda-administrative-order-no-001-series-of-2021/'),
 7: ('DOH AO 2020-0013; DM 2024-0073 (verify version)', 'https://law.upd.edu.ph/wp-content/uploads/2020/05/DOH-AO-No-2020-0013.pdf'),
 9: ('DOH AO 2020-0008 MCCOD; DOH/PSA ICD', 'https://legaldex.com/laws/rules-on-medical-certification-of-cause-of-death-mccod'),
 10: ('DOH AO 2020-0008 MCCOD', 'https://legaldex.com/laws/rules-on-medical-certification-of-cause-of-death-mccod'),
 25: ('DOH-adopted ICD-10; encounter policy not verified', None),
 29: ('PH question policy unverified; WHO ICD-10 is context', 'https://icd.who.int/browse10/2019/en#/O10-O16'),
 39: ('DOH AO 2013-0005 original form unverified; PhilPEN AO 2012-0029', None),
 41: ('DOH AO 2020-0059 named only; workbook also cites AO 2013-0005', None),
 43: ('DOH AO 2013-0005 original diabetes form unverified', None),
 44: ('DOH AO 2013-0005 original diabetes form unverified', None),
 46: ('DOH AO 2013-0005 COPD form unverified', None),
 47: ('DOH AO 2013-0005 COPD form unverified', None),
 48: ('DOH AO 2015-0024 ITIS; AO 2011-0010 named only', 'https://ntp.doh.gov.ph/download/ao2015-0024/'),
 49: ('DOH AO 2013-0005 original asthma form unverified', None),
}

# Source choices distinguish workbook wording from approved policy response sets.
VALUES = {
 4: 'PRPWD v4.0: Deaf/Hard of Hearing; Intellectual; Learning; Mental; Physical; Psychosocial; Speech/Language; Visual; Cancer; Rare Disease; Others. Reconcile edition.',
 5: 'Workbook Yes/No. Policy requires permanence for eligibility; no approved response value set verified.',
 7: 'DOH case classes Suspect / Probable / Confirmed / not a case; JAO field may instead be binary. Confirm form.',
 9: 'Part I causal sequence / Part II contributing; certificate line and later coded stage differ.',
 10: 'Certifier wording and interval; no coded response list.',
 29: 'Workbook Yes / No/None; no Philippine question answer set verified.',
 37: '“Others, specify” recorded; full source form options unverified.',
 39: 'I10–I15 workbook example RANGE; original form choices unverified.',
 41: 'I60–I64 workbook example RANGE; original form choices unverified.',
 43: 'Label “newly/previously” vs definition “newly/not”; form and window unverified.',
 44: 'E10–E14 workbook example RANGE; original form choices unverified.',
 46: 'Source grade choices and GOLD edition unverified. Grade 1–4 is an international comparator only.',
 47: 'Source group/edition unverified. ABCD (legacy) differs from ABE (2023+); 2026 E threshold changed.',
 48: 'Question answers unverified; TB case classifications are not its answer list.',
 49: 'Asthma “basis” choices and original annex unverified.',
}

PRIORITY = {
 4: 'DOH/NCDA + PH Core: reconcile value set and form.',
 5: 'NCDA + JAO: define attester and unknown semantics.',
 7: 'DOH surveillance + JAO: get exact form/answer set.',
 9: 'DOH/PSA + certifier: establish coding stage and ICD edition.',
 10: 'JAO + certifier: prove line/code pairing.',
 23: 'JAO + PH Core: distinguish assertion from upload.',
 24: 'JAO + clinician: pair date/time and offset.',
 25: 'DOH + terminology owner: encounter policy, URI, edition.',
 29: 'JAO + clinician: clarify PIH versus pre-eclampsia, No/None.',
 39: 'DOH registry + clinician: retrieve subtype form.',
 41: 'DOH stroke + clinician: approve subtype evidence.',
 43: 'DOH registry + JAO: define “new” and its window.',
 44: 'DOH registry + terminology owner: verify choices.',
 46: 'Registry + pulmonologist: pin source GOLD edition and spirometry.',
 47: 'Registry + pulmonologist: pin group edition and inputs.',
 48: 'DOH TB + clinician: get question options and case status.',
 49: 'DOH registry + JAO: find asthma annex and section intent.',
}

def clean(x):
    return re.sub(r'\s+', ' ', str(x or '')).strip()

def md(x):
    return re.sub(r'([\\`*\[\]<>|])', r'\\\1', clean(x))

def url(label, target):
    return f'[{md(label)}]({target})' if target else md(label)

def cells_from_workbook():
    with zipfile.ZipFile(BOOK) as z:
        strings = [''.join(si.itertext()) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', NS)]
        sheet = ET.fromstring(z.read('xl/worksheets/sheet7.xml'))  # Condition sheet
        result = {}
        for row in sheet.findall('.//m:sheetData/m:row', NS):
            values = {}
            for c in row.findall('m:c', NS):
                v = c.find('m:v', NS)
                if v is not None:
                    col = re.match('[A-Z]+', c.get('r')).group()
                    values[col] = strings[int(v.text)] if c.get('t') == 's' else v.text
            result[int(row.get('r'))] = values
        return result

def policy(r):
    n = r['excel']
    if n in POLICY:
        label, target = POLICY[n]
        s = url(label, target)
        if n == 4:
            s += '; ' + url('DOH -B PRPWD v4.0', PWD_B)
        if n in (46, 47):
            s += '; ' + url('GOLD 2026 (comparison only)', GOLD)
    else:
        s = url('DOH Hospital HIM Manual (form/edition unverified)', r.get('policyUrl'))
    return s + 'BRKSEGResponses: ' + md(VALUES.get(n, 'No enumerated answer list verified.'))

def terminology(r):
    n = r['excel']
    chunks = []
    if n == 4:
        chunks.append(url('PH Core 0.2.0 draft disability VS (9 codes; missing Mental/Cancer/Rare Disease)', PHCORE))
    for c in r.get('candidateTerminology', []):
        v = c.get('validation') or {}
        system = 'SCT' if 'snomed' in c['system'] else 'LOINC'
        chunks.append(url(f'{system} {c["code"]} ({c.get("role", "candidate")})', c.get('link')))
        if v.get('status') != 'checked':
            chunks[-1] += ' [unchecked]'
    if chunks:
        chunks.append('Public lookup: SCT Int 20250201 / LOINC 2.82 (as returned; see validation file). Candidates ≠ bindings.')
    else:
        chunks.append('No specific SNOMED/LOINC concept checked.')
    if r.get('terminologyRange'):
        chunks.append(url('ICD-10 ' + r['terminologyRange'] + ' is a range, NOT a code',
                          'https://icd.who.int/browse10/2019/en#/'))
    if n in (25, 39, 41, 44):
        chunks.append('ICD-10-PH URI and edition unresolved.')
    if n in (46, 47):
        chunks.append('No GOLD group/grade value set approved.')
    return 'BRKSEG'.join(chunks)

def format_docx(path):
    """Landscape letter, compact editable tables, repeating headers and stable widths."""
    width = [1700, 2600, 2700, 2250, 2250, 2600]  # 14100 twips; 0.6-inch margins
    with zipfile.ZipFile(path) as zin:
        members = [(i, zin.read(i.filename)) for i in zin.infolist()]
    with zipfile.ZipFile(path, 'w') as zout:
        for info, data in members:
            if info.filename == 'word/document.xml':
                root = ET.fromstring(data)
                for sect in root.findall('.//' + Q + 'sectPr'):
                    size = sect.find(Q + 'pgSz')
                    if size is None: size = ET.SubElement(sect, Q + 'pgSz')
                    size.set(Q + 'w', '15840'); size.set(Q + 'h', '12240'); size.set(Q + 'orient', 'landscape')
                    margin = sect.find(Q + 'pgMar')
                    if margin is None: margin = ET.SubElement(sect, Q + 'pgMar')
                    for side in ('left', 'right'): margin.set(Q + side, '864')
                    for side in ('top', 'bottom'): margin.set(Q + side, '720')
                for table in root.findall('.//' + Q + 'tbl'):
                    rows = table.findall(Q + 'tr')
                    if not rows or len(rows[0].findall(Q + 'tc')) != 6: continue
                    tblpr = table.find(Q + 'tblPr')
                    if tblpr is None: tblpr = ET.SubElement(table, Q + 'tblPr')
                    layout = tblpr.find(Q + 'tblLayout')
                    if layout is None: layout = ET.SubElement(tblpr, Q + 'tblLayout')
                    layout.set(Q + 'type', 'fixed')
                    tw = tblpr.find(Q + 'tblW')
                    if tw is None: tw = ET.SubElement(tblpr, Q + 'tblW')
                    tw.set(Q + 'type', 'dxa'); tw.set(Q + 'w', str(sum(width)))
                    grid = table.find(Q + 'tblGrid')
                    if grid is None: grid = ET.Element(Q + 'tblGrid'); table.insert(1, grid)
                    grid.clear()
                    for w in width:
                        ET.SubElement(grid, Q + 'gridCol', {Q + 'w': str(w)})
                    for ri, row in enumerate(rows):
                        trpr = row.find(Q + 'trPr')
                        if trpr is None: trpr = ET.Element(Q + 'trPr'); row.insert(0, trpr)
                        if ri == 0:
                            ET.SubElement(trpr, Q + 'tblHeader', {Q + 'val': 'true'})
                        else:
                            ET.SubElement(trpr, Q + 'cantSplit')
                        for ci, cell in enumerate(row.findall(Q + 'tc')):
                            tcpr = cell.find(Q + 'tcPr')
                            if tcpr is None: tcpr = ET.Element(Q + 'tcPr'); cell.insert(0, tcpr)
                            cw = tcpr.find(Q + 'tcW')
                            if cw is None: cw = ET.SubElement(tcpr, Q + 'tcW')
                            cw.set(Q + 'type', 'dxa'); cw.set(Q + 'w', str(width[ci]))
                            shade = tcpr.find(Q + 'shd')
                            if ri == 0:
                                if shade is None: shade = ET.SubElement(tcpr, Q + 'shd')
                                shade.set(Q + 'fill', 'DCE9E7')
                            elif ri % 2 == 0:
                                if shade is None: shade = ET.SubElement(tcpr, Q + 'shd')
                                shade.set(Q + 'fill', 'F4F7F7')
                            for para in cell.findall('.//' + Q + 'p'):
                                pp = para.find(Q + 'pPr')
                                if pp is None: pp = ET.Element(Q + 'pPr'); para.insert(0, pp)
                                sp = pp.find(Q + 'spacing')
                                if sp is None: sp = ET.SubElement(pp, Q + 'spacing')
                                sp.set(Q + 'before', '0'); sp.set(Q + 'after', '0')
                                for run in para.findall('.//' + Q + 'r'):
                                    rp = run.find(Q + 'rPr')
                                    if rp is None: rp = ET.Element(Q + 'rPr'); run.insert(0, rp)
                                    sz = rp.find(Q + 'sz')
                                    if sz is None: sz = ET.SubElement(rp, Q + 'sz')
                                    sz.set(Q + 'val', '17')  # 8.5 pt
                # Pandoc ignores HTML <br> inside pipe-table cells. Convert a plain
                # sentinel to real Word soft line breaks while retaining inline styles.
                for run in root.findall('.//' + Q + 'r'):
                    for node in list(run):
                        if node.tag != Q + 't' or not node.text or 'BRKSEG' not in node.text: continue
                        pieces = node.text.split('BRKSEG')
                        node.text = pieces[0]
                        pos = list(run).index(node) + 1
                        for piece in pieces[1:]:
                            run.insert(pos, ET.Element(Q + 'br')); pos += 1
                            new = ET.Element(Q + 't')
                            new.text = piece
                            if piece.startswith(' ') or piece.endswith(' '):
                                new.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                            run.insert(pos, new); pos += 1
                data = ET.tostring(root, encoding='utf-8', xml_declaration=True)
            zout.writestr(info, data)

def main():
    rows = json.loads((ROOT / 'mindmap-index.json').read_text())['rows']
    sheet = cells_from_workbook()
    assert len(rows) == len(ASSERTION) == 34 and len({r['excel'] for r in rows}) == 34
    assert len({r['section'] for r in rows}) == 13
    for r in rows:
        b = sheet[r['excel']]
        for col, key in [('E', 'label'), ('J', 'definition'), ('L', 'section')]:
            assert clean(b.get(col)) == clean(r[key]), (r['excel'], col)
        assert not clean(b.get('D')), (r['excel'], 'workbook binding not empty')

    lines = [
        '% JAO Condition | Assertion confirmation worksheet',
        '% 34 Excel rows · 13 source sections · editable review draft',
        '% ' + date.today().isoformat(),
        '',
        '**Use:** In each row, tick Confirm / Revise / Reject; type the correction, evidence, '
        'owner and date into the editable Word cell. Repeated worksheet items remain separate.',
        '',
        '**Key:** “Source” = exact workbook definition; “Confirm” = proposed assertion, not '
        'approval. Policy citations ≠ proof the specific field is required; unverified responses '
        'must be checked against the original form. SCT/LOINC candidates were looked up on public '
        'FHIRsmith (2026-09-27; SCT International 20250201 / LOINC 2.82), not approved as PH '
        'bindings. All 34 binding cells are empty. HIM Manual text (HTTP 403 to automation) '
        'and original AO 2013-0005 disease-form annexes remain to be verified; PWD amendments '
        'do not establish disease-form choices. FHIR paths are proposals, not conformance claims.',
        '',
        f'**GOLD hold (46–47):** [GOLD 2026]({GOLD}) is only an international comparator; '
        'source edition unknown. Grade 1–4 ≠ ABCD/ABE group. ABE began in 2023, and the '
        '2026 E threshold includes one moderate exacerbation in the prior year. Preserve '
        'the original form version and raw answer; do not convert silently.',
        '',
        '# Review table',
        '',
    ]
    section = None
    for r in rows:
        n = r['excel']
        if r['section'] != section:
            section = r['section']
            lines += ['## ' + md(section), '',
                      '| Excel / field | Assertion to confirm | Policy / source responses | Terminology dictionary | Proposed FHIR (not approved) | Reviewer decision / correction |',
                      '|:--|:--|:--|:--|:--|:--|']
        source = f'**{n} · {md(r["label"])}**BRKSEGSource ID {md(r["sourceId"])}'
        assertion = f'**Source:** {md(r["definition"])}BRKSEG**Confirm:** {md(ASSERTION[n])}'
        if n == 41:
            assertion += 'BRKSEG**Note:** workbook K names AO 2013-0005; current review also cites AO 2020-0059.'
        term = terminology(r)
        fhir = md(r['fhirPath']).replace('.', '.\u200b').replace(':', ':\u200b')
        if n in (4, 5):
            fhir += 'BRKSEGPH Core Patient draft extension; permanence is a gap.'
        elif n in (7, 13, 29, 37, 48):
            fhir += 'BRKSEGPH Core Observation exists; question use is proposed.'
        elif n in (43,):
            fhir += 'BRKSEGUnresolved element.'
        decision = '☐ Confirm  ☐ Revise  ☐ RejectBRKSEGCorrection: __________________BRKSEGEvidence / owner / date: __________________'
        if n in PRIORITY:
            decision += 'BRKSEG**Route:** ' + md(PRIORITY[n])
        else:
            decision += 'BRKSEG**Route:** ' + md(r['humanReview'])
        lines += ['| ' + ' | '.join([source, assertion, policy(r), term, fhir, decision]) + ' |']
        if n == rows[-1]['excel'] or rows[rows.index(r)+1]['section'] != section:
            lines += ['', '']
    lines += ['# Meeting sign-off', '',
             '| Scope / row numbers | Decision owner | Evidence and exact edition | Approved / deferred | Date |',
             '|:--|:--|:--|:--|:--|',
             '| ____________________ | ____________________ | ____________________ | ____________________ | __________ |',
             '| ____________________ | ____________________ | ____________________ | ____________________ | __________ |',
             '',
             'After decisions are recorded, update the source mapping data and regenerate the HTML separately. '
             'Historical PHCDI Release 01 is a different organization’s inventory, not a JAO clinical authority. '
             'Base R4 transaction checks do not establish proposed-profile conformance.', '']
    with tempfile.TemporaryDirectory(prefix='jao-worksheet-') as tmp:
        text = Path(tmp) / 'worksheet.md'
        text.write_text('\n'.join(lines))
        subprocess.run(['pandoc', str(text), '-f', 'markdown', '-t', 'docx',
                        '--standalone', '--metadata=lang:en', '-o', str(OUT)], check=True)
    format_docx(OUT)
    print(f'{OUT.name}: {len(rows)} editable review rows across {len({r["section"] for r in rows})} sections')

if __name__ == '__main__':
    main()
