"""Focused invariants for the filterable advisory PHCDI similarity report table.

The controls refine a read-only view of the generated `ROWS` block. They must not
mutate `ROWS`/`PHCDI_SIMILARITY`, must not touch the primary Sankey search/filter
state, must keep the advisory Jev similarity band separate from the deterministic
structural status, and the report summary must always describe all 34 rows.

The rendered behaviour (filters, sorts, reset, zero-result state, live count and the
row-detail modal link) is exercised in a real browser by
`tests/similarity-report-interaction.js`; the default 34-row ascending table geometry is
covered by `tests/similarity-report-geometry.js`.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BAND_RANGES = [('none', 'None 0–24'), ('weak', 'Weak 25–49'), ('partial', 'Partial 50–74'), ('close', 'Close 75–100')]


class SimilarityReportFilterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / 'condition-row-profile-mindmap.html').read_text()
        cls.rows = json.loads((ROOT / 'mindmap-index.json').read_text())['rows']
        cls.section = cls.html.split('<section id="similarity-report"', 1)[1].split(
            '<section class="section" aria-labelledby="validation-title"', 1)[0]
        cls.haystack = cls.html.split('function simHaystack(r){', 1)[1].split('function simFilteredRows(){', 1)[0]
        cls.filters = cls.html.split('function simFilteredRows(){', 1)[1].split('function setSimilarityControls()', 1)[0]
        cls.bind = cls.html.split('function bindSimilarityControls(){', 1)[1].split('function renderSimilarityTable()', 1)[0]
        cls.render_table = cls.html.split('function renderSimilarityTable(){', 1)[1].split('function renderSimilarityReport()', 1)[0]
        cls.report_fn = cls.html.split('function renderSimilarityReport(){', 1)[1].split('let invokingLink=null;', 1)[0]
        cls.clear = cls.html.split('function clearSimilarityFilters(){', 1)[1].split('function bindSimilarityControls()', 1)[0]
        cls.browser_test = (ROOT / 'tests' / 'similarity-report-interaction.js').read_text()

    # --- generated data is untouched ------------------------------------------------
    def test_generated_rows_and_similarity_blocks_are_unchanged(self):
        raw = re.search(r'const ROWS=(.*?);\nconst PROFILES=', self.html, re.S).group(1)
        self.assertEqual(json.loads(raw), self.rows)
        self.assertEqual(len(self.rows), 34)
        self.assertEqual(len({r['excel'] for r in self.rows}), 34)
        self.assertTrue(all(r.get('phcdiSimilarity') for r in self.rows))
        self.assertEqual(self.html.count('const ROWS='), 1)
        # Filters only read the generated array.
        self.assertIn('ROWS.filter(r=>{', self.filters)
        self.assertNotIn('ROWS=', self.filters)
        self.assertNotIn('ROWS.push', self.html)
        self.assertNotIn('ROWS.sort', self.html)
        # The report never rewrites the primary Sankey search/filter state.
        for block in (self.filters, self.render_table, self.clear, self.bind):
            self.assertNotIn('search.value', block)
            self.assertNotIn('filter.value', block)
            self.assertNotIn('#search', block)
            self.assertNotIn('#filter', block)

    # --- controls: placement, native semantics, labels ------------------------------
    def test_controls_are_labelled_native_and_placed_before_the_table(self):
        controls = self.section.index('id="similarity-report-controls"')
        scroll = self.section.index('id="similarity-report-scroll"')
        self.assertLess(controls, scroll, 'filter controls must precede the table scroll region')
        self.assertIn('<fieldset id="similarity-report-controls" class="sim-controls"><legend>Filter and sort the 34-row similarity table</legend>', self.section)
        self.assertIn('<label class="sim-controls-search">Search rows (Excel number, label, section, source ID, proposed FHIR path or cited PHCDI element)<input id="sim-search" type="search"', self.section)
        self.assertIn('<label>Similarity band<select id="sim-band">', self.section)
        self.assertIn('<label>Deterministic path status<select id="sim-status">', self.section)
        self.assertIn('<label>Human-review flag<select id="sim-review">', self.section)
        self.assertIn('<label>Sort order<select id="sim-sort">', self.section)
        self.assertIn('<button type="button" id="sim-clear" class="sim-reset" data-sim-clear>Clear filters</button>', self.section)
        # A fieldset (not a form) avoids implicit submission when Enter is pressed in search.
        self.assertNotIn('<form', self.section)
        self.assertIn('autocomplete="off"', self.section)

    def test_live_count_and_visible_focus_are_present(self):
        self.assertIn('<output id="sim-count" class="sim-count" aria-live="polite" for="sim-search sim-band sim-status sim-review sim-sort"></output>', self.section)
        self.assertIn('rows.length===ROWS.length', self.render_table)
        self.assertIn('of ${ROWS.length} rows shown', self.render_table)
        self.assertIn('a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible{outline:3px solid var(--blue);outline-offset:2px}', self.html)
        self.assertIn('.sim-controls-grid input,.sim-controls-grid select{width:100%;min-width:0;min-height:39px;', self.html)
        self.assertIn('.sim-reset{min-height:39px;', self.html)

    # --- search coverage -------------------------------------------------------------
    def test_search_covers_number_label_section_source_id_path_and_cited_element(self):
        self.assertIn('const parts=[r.excel,r.label,r.section,r.sourceId,r.fhirPath];', self.haystack)
        self.assertIn('(r.phcdiComparison&&r.phcdiComparison.references)', self.haystack)
        self.assertIn('parts.push(ref.element)', self.haystack)
        self.assertIn('.toLowerCase()', self.haystack)
        self.assertIn('const terms=simState.query.trim().toLowerCase().split(/\\s+/).filter(Boolean);', self.filters)
        self.assertIn('terms.every(t=>simHaystack(r).includes(t))', self.filters)
        # Excel number is searched as text, so "46" resolves the workbook row.
        self.assertIn('parts.filter(Boolean).join', self.haystack)

    # --- band / status / review / sort are distinct axes -----------------------------
    def test_band_select_matches_the_legend_and_separates_similarity_from_status(self):
        for value, label in BAND_RANGES:
            self.assertIn(f'<option value="{value}">{label}</option>', self.section)
        self.assertIn('if(simState.band&&(!s||s.band!==simState.band))return false;', self.filters)
        # Deterministic status is read from phcdiPathComparison, never from the similarity band.
        self.assertIn('r.phcdiPathComparison||{}', self.filters)
        self.assertIn('if(simState.status&&cmp.status!==simState.status)return false;', self.filters)
        self.assertIn('if(simState.review&&(!s||String(s.humanReview)!==simState.review))return false;', self.filters)
        self.assertIn('<option value="true">Flagged for human review</option><option value="false">Not flagged</option>', self.section)
        # Status options are derived from the single shared friendly-status mapping.
        self.assertEqual(self.html.count('const statusLabel='), 1)
        self.assertIn('Object.keys(statusLabel).filter(k=>ROWS.some(r=>(r.phcdiPathComparison||{}).status===k))', self.bind)
        self.assertIn("status.insertAdjacentHTML('beforeend'", self.bind)

    def test_sort_options_include_default_ascending_and_all_requested_modes(self):
        for value in ('similarity-asc', 'similarity-desc', 'workbook-asc', 'confidence-asc', 'confidence-desc'):
            self.assertIn(f'<option value="{value}">', self.section)
        self.assertIn('<option value="similarity-asc">Similarity: low to high (default)</option>', self.section)
        self.assertIn("const simState={query:'',band:'',status:'',review:'',sort:'similarity-asc'};", self.html)
        self.assertIn("'similarity-asc':(a,b)=>(simSimilarityPct(a)-simSimilarityPct(b))||byExcel(a,b),", self.filters)
        self.assertIn("'similarity-desc':(a,b)=>(simSimilarityPct(b)-simSimilarityPct(a))||byExcel(a,b),", self.filters)
        self.assertIn("'workbook-asc':byExcel,", self.filters)
        self.assertIn("'confidence-asc':(a,b)=>(simConfidence(a)-simConfidence(b))||byExcel(a,b),", self.filters)
        self.assertIn("'confidence-desc':(a,b)=>(simConfidence(b)-simConfidence(a))||byExcel(a,b)", self.filters)
        self.assertIn("return filtered.sort(comparators[simState.sort]||comparators['similarity-asc']);", self.filters)

    # --- intersection, reset, single listener registration ---------------------------
    def test_filters_intersect_and_reset_restores_defaults(self):
        # Every clause returns false inside one filter callback: selections intersect.
        for clause in ('if(terms.length&&!terms.every(t=>simHaystack(r).includes(t)))return false;',
                       'if(simState.band&&(!s||s.band!==simState.band))return false;',
                       'if(simState.status&&cmp.status!==simState.status)return false;',
                       'if(simState.review&&(!s||String(s.humanReview)!==simState.review))return false;'):
            self.assertIn(clause, self.filters)
        callback = self.filters.split('ROWS.filter(r=>{', 1)[1].split('});', 1)[0]
        self.assertEqual(callback.count('return false;'), 4, 'each filter axis must exclude rows on its own')
        self.assertEqual(callback.count('return true;'), 1)
        self.assertTrue(callback.strip().endswith('return true;'), 'the surviving rows are the intersection of every axis')
        self.assertIn("simState.query='';simState.band='';simState.status='';simState.review='';simState.sort='similarity-asc';", self.clear)
        self.assertIn('setSimilarityControls();renderSimilarityTable();', self.clear)
        self.assertIn("for(const [sel,key] of [['#sim-search','query'],['#sim-band','band'],['#sim-status','status'],['#sim-review','review'],['#sim-sort','sort']])", self.html)
        self.assertIn("if(el)el.value=simState[key]", self.html)

    def test_event_listeners_are_registered_exactly_once(self):
        self.assertIn('let simControlsBound=false', self.html)
        self.assertIn('if(simControlsBound)return;simControlsBound=true;', self.bind)
        self.assertIn("el.addEventListener('change',()=>{simState[key]=el.value;renderSimilarityTable()})", self.bind)
        self.assertIn("q.addEventListener('input',()=>{simState.query=q.value;renderSimilarityTable()})", self.bind)
        # Registered once per render pass; no inline onchange/oninput duplication.
        self.assertNotIn('onchange=', self.section)
        self.assertNotIn('oninput=', self.section)
        self.assertNotIn('onclick=', self.section)
        # The clear control and the empty-state control share one delegated handler.
        self.assertIn("section.addEventListener('click',e=>{if(e.target.closest('[data-sim-clear]'))clearSimilarityFilters()})", self.bind)

    # --- summary stays all-rows; empty state -----------------------------------------
    def test_summary_is_all_rows_unfiltered_and_explains_the_measure(self):
        self.assertIn('id="similarity-report-summary"', self.section)
        self.assertIn('<span class="sim-summary-scope"><b>All ${esc(ROWS.length)} rows</b>unfiltered summary · filters below do not change these totals</span>', self.report_fn)
        self.assertIn('mean similarity /100', self.report_fn)
        self.assertIn("<span>Jev ${esc(meta.model||'unrecorded')} · checked ${esc(checked)}</span>", self.report_fn)
        self.assertIn('id="similarity-report-method"', self.section)
        self.assertIn('method.innerHTML=', self.report_fn)
        # Summary and method are generated before the filtered table is rendered.
        self.assertLess(self.report_fn.index('simSummaryRendered=true'), self.report_fn.index('renderSimilarityTable();'))

    def test_zero_result_empty_state_row_and_default_table_contract(self):
        self.assertIn('<tr class="sim-empty"><td colspan="7"><b>No rows match these filters.</b>', self.render_table)
        self.assertIn('data-sim-clear>Clear filters</button>', self.render_table)
        # Caption, accessible measure cell and row-detail link are intact for the geometry test.
        self.assertIn('<caption>Advisory Jev similarity between each proposed mapping and its cited historical PHCDI CSV evidence</caption>', self.section)
        self.assertIn('function simTableRow(r){', self.html)
        self.assertIn('<a href="#row-${esc(r.excel)}">Open row ${esc(r.excel)} detail</a>', self.html)
        self.assertIn('<tbody id="similarity-report-rows"></tbody>', self.section)
        self.assertIn('render();renderSimilarityReport();', self.html)

    def test_no_approval_control_was_added_to_the_report(self):
        self.assertNotIn('approve', self.section.lower())
        self.assertNotIn('Approve', self.section)
        self.assertIn('it never changes the deterministic structural status', self.section)

    # --- browser test coverage -------------------------------------------------------
    def test_browser_interaction_test_covers_every_requested_scenario(self):
        for token in ('#sim-search', '#sim-band', '#sim-status', '#sim-review', '#sim-sort', '#sim-clear', '#sim-count', '.sim-empty'):
            self.assertIn(token, self.browser_test)
        for scenario in ('default', 'search', 'band', 'status', 'review', 'intersection', 'sort', 'reset', 'zero-result', 'row detail'):
            self.assertIn(scenario.lower(), self.browser_test.lower())
        self.assertIn('.sim-empty td', self.browser_test)
        self.assertIn("location.hash === `#row-", self.browser_test)
        self.assertIn('document.activeElement === link', self.browser_test)


if __name__ == '__main__':
    unittest.main()
