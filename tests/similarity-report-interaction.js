// Run in the browser (desktop width) after opening condition-row-profile-mindmap.html:
//   agent-browser eval --stdin < tests/similarity-report-interaction.js
// Exercises the advisory PHCDI similarity report controls against the *rendered* page:
// default 34-row ascending order, search, band/status/review filters, combined
// intersection, every sort mode, reset, zero-result empty state, the live count and a
// row-detail link (modal, hash and focus return). Expectations are derived from the
// unfiltered population captured first, plus the workbook's own section membership.
(async () => {
  const problems = [];
  const TOTAL = 34;
  const $ = s => document.querySelector(s);
  const dataRows = () => [...document.querySelectorAll('#similarity-report-rows tr')].filter(tr => !tr.classList.contains('sim-empty'));
  const excel = tr => Number(tr.querySelector('td.num').textContent);
  const pct = tr => Number(tr.querySelector('.sim-num').textContent);
  const band = tr => tr.querySelector('.sim-band').textContent.trim();
  const status = tr => tr.querySelector('.sim-status-token').textContent.trim();
  const review = tr => tr.querySelector('.sim-review').dataset.review;
  const confidence = tr => Number(tr.querySelectorAll('td.num')[1].textContent.replace('%', ''));
  const label = tr => tr.querySelector('td:nth-child(2)').textContent.trim();
  const countText = () => $('#sim-count').textContent.trim();
  const setText = value => { const el = $('#sim-search'); el.value = value; el.dispatchEvent(new Event('input', { bubbles: true })); };
  const setSelect = (id, value) => { const el = $(id); el.value = value; el.dispatchEvent(new Event('change', { bubbles: true })); };
  const reset = () => $('#sim-clear').click();
  const frame = () => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  const settle = async () => { await frame(); await new Promise(r => setTimeout(r, 60)); await frame(); };
  const expect = (cond, msg) => { if (!cond) problems.push(msg); };
  const nonDecreasing = a => a.every((v, i) => i === 0 || v >= a[i - 1]);
  const nonIncreasing = a => a.every((v, i) => i === 0 || v <= a[i - 1]);
  const excels = () => dataRows().map(excel).sort((a, b) => a - b);
  const sameSet = (a, b) => a.length === b.length && a.every((v, i) => v === b[i]);

  // --- Controls are labelled, native and singular -------------------------------
  const controls = $('#similarity-report-controls');
  expect(!!controls, 'missing #similarity-report-controls');
  for (const id of ['#sim-search', '#sim-band', '#sim-status', '#sim-review', '#sim-sort', '#sim-clear']) {
    const el = $(id);
    expect(!!el, `missing control ${id}`);
  }
  expect($('#sim-search').tagName === 'INPUT' && $('#sim-search').type === 'search', 'search control is not a native search input');
  const labelFor = id => [...controls.querySelectorAll('label')].find(l => l.contains($(id)));
  for (const id of ['#sim-search', '#sim-band', '#sim-status', '#sim-review', '#sim-sort']) {
    expect(!!labelFor(id) && labelFor(id).textContent.trim().length > 0, `${id} has no visible <label>`);
  }
  expect($('#sim-clear').tagName === 'BUTTON' && $('#sim-clear').type === 'button', 'clear control is not a native button');
  expect(!!$('#sim-count').closest('[aria-live="polite"]'), 'live count lacks aria-live="polite"');
  const statusOptions = [...$('#sim-status').options].slice(1).map(o => o.value);

  // --- Baseline: the unfiltered population, captured before any filtering -------
  reset();
  const base = dataRows().map(tr => ({ excel: excel(tr), pct: pct(tr), band: band(tr), status: status(tr), review: review(tr), confidence: confidence(tr), label: label(tr) }));
  expect(base.length === TOTAL, `default view shows ${base.length} rows, expected ${TOTAL}`);
  expect(countText().startsWith(`${TOTAL} of ${TOTAL} rows shown`), `default live count is "${countText()}"`);
  expect(nonDecreasing(base.map(r => r.pct)), 'default order is not similarity ascending');
  for (let i = 1; i < base.length; i += 1) {
    if (base[i].pct === base[i - 1].pct) expect(base[i].excel > base[i - 1].excel, `equal similarity not tie-broken by Excel row at index ${i}`);
  }
  expect(sameSet([...statusOptions].sort(), [...new Set(base.map(r => r.status))].sort()),
    `status options ${statusOptions} do not match the statuses present (${[...new Set(base.map(r => r.status))]})`);
  expect(new Set(base.map(r => r.excel)).size === base.length, 'duplicate rendered rows');

  const expected = (predicate, list = base) => list.filter(predicate).map(r => r.excel).sort((a, b) => a - b);

  // --- Search over Excel number, label, section, source ID, FHIR path and PHCDI element
  reset(); setText('Type of Disability');
  expect(sameSet(excels(), expected(r => r.label === 'Type of Disability')), 'label search returned the wrong set');
  reset(); setText('MASTER PERSON DATA');
  expect(sameSet(excels(), [4, 5]), `section search returned ${excels()}, expected the two MASTER PERSON DATA rows`);
  reset(); setText('SRC746');
  expect(sameSet(excels(), [33]), `source-ID search returned ${excels()}, expected the SRC746 row`);
  reset(); setText('disabilityType');
  expect(excels().includes(4), 'proposed FHIR path search did not match the disabilityType row');
  reset(); setText('RegistrationNo');
  expect(excels().includes(4), 'cited PHCDI element search did not match the RegistrationNo row');
  reset(); setText('46');
  expect(excels().includes(46), 'Excel-number search did not match row 46');
  reset(); setText('disability MASTER');
  expect(excels().includes(4), 'multi-term search did not intersect on both terms');
  reset(); setText('DISABILITY');
  expect(excels().length > 0 && excels().length < TOTAL, 'case-insensitive search did not narrow the table');
  expect(countText().startsWith(`${excels().length} of ${TOTAL} rows shown`), `live count did not follow search ("${countText()}")`);

  // --- Similarity band ----------------------------------------------------------
  reset(); setSelect('#sim-band', 'close');
  const closeSet = expected(r => r.band === 'Close');
  expect(sameSet(excels(), closeSet) && closeSet.length === 1, `close-band filter returned ${excels()}, expected ${closeSet}`);
  expect(dataRows().every(tr => band(tr) === 'Close'), 'band filter rendered a non-Close row');
  reset(); setSelect('#sim-band', 'weak');
  expect(sameSet(excels(), expected(r => r.band === 'Weak')), 'weak-band filter returned the wrong set');

  // --- Deterministic path status (never conflated with the advisory band) -------
  for (const value of statusOptions) {
    reset(); setSelect('#sim-status', value);
    expect(sameSet(excels(), expected(r => r.status === value)), `status filter "${value}" returned the wrong set`);
    expect(dataRows().every(tr => status(tr) === value), `status filter "${value}" rendered a different status`);
    expect(dataRows().every(tr => band(tr) !== ''), `status filter "${value}" dropped the advisory band column`);
  }

  // --- Human-review flag --------------------------------------------------------
  reset(); setSelect('#sim-review', 'true');
  expect(sameSet(excels(), expected(r => r.review === 'true')), 'human-review=true filter returned the wrong set');
  expect(dataRows().every(tr => review(tr) === 'true'), 'human-review=true filter rendered an unflagged row');
  reset(); setSelect('#sim-review', 'false');
  expect(sameSet(excels(), expected(r => r.review === 'false')), 'human-review=false filter returned the wrong set');

  // --- Combined selections intersect -------------------------------------------
  reset();
  setSelect('#sim-band', 'weak'); setSelect('#sim-status', 'choice-base'); setSelect('#sim-review', 'true');
  const intersected = expected(r => r.band === 'Weak' && r.status === 'choice-base' && r.review === 'true');
  expect(sameSet(excels(), intersected), `band+status+review intersection returned ${excels()}, expected ${intersected}`);
  setText('illness');
  expect(excels().every(n => intersected.includes(n)) && excels().length > 0 && excels().length < intersected.length,
    `adding a search term did not narrow the active filters (${excels()} vs ${intersected})`);
  expect(countText().startsWith(`${excels().length} of ${TOTAL} rows shown`), 'live count did not follow combined filters');

  // --- Sort modes ---------------------------------------------------------------
  reset(); setSelect('#sim-sort', 'similarity-desc');
  expect(nonIncreasing(dataRows().map(pct)), 'similarity-desc is not descending');
  reset(); setSelect('#sim-sort', 'workbook-asc');
  expect(nonDecreasing(dataRows().map(excel)), 'workbook order is not ascending by Excel row');
  reset(); setSelect('#sim-sort', 'confidence-asc');
  expect(nonDecreasing(dataRows().map(confidence)), 'confidence-asc is not ascending');
  reset(); setSelect('#sim-sort', 'confidence-desc');
  expect(nonIncreasing(dataRows().map(confidence)), 'confidence-desc is not descending');
  reset();
  expect(nonDecreasing(dataRows().map(pct)) && $('#sim-sort').value === 'similarity-asc', 'reset did not restore ascending similarity order');

  // --- Zero-result empty state, live count and its own clear button -------------
  reset(); setText('zzzz-no-such-row');
  expect(dataRows().length === 0, `nonsense search still rendered ${dataRows().length} rows`);
  expect(countText().startsWith(`0 of ${TOTAL} rows shown`), `zero-result live count is "${countText()}"`);
  const emptyCell = $('#similarity-report-rows .sim-empty td');
  expect(!!emptyCell, 'zero-result state has no empty-state row');
  expect(emptyCell && emptyCell.getAttribute('colspan') === '7', 'empty-state row does not span the table');
  const emptyReset = emptyCell && emptyCell.querySelector('[data-sim-clear]');
  expect(!!emptyReset, 'empty-state row has no clear control');
  if (emptyReset) emptyReset.click();
  expect(dataRows().length === TOTAL && countText().startsWith(`${TOTAL} of ${TOTAL} rows shown`), 'empty-state clear did not restore all rows');

  // --- Reset restores every default --------------------------------------------
  setText('x'); setSelect('#sim-band', 'weak'); setSelect('#sim-status', 'exact'); setSelect('#sim-review', 'false'); setSelect('#sim-sort', 'workbook-asc');
  reset();
  expect($('#sim-search').value === '', 'search was not cleared');
  expect($('#sim-band').value === '' && $('#sim-status').value === '' && $('#sim-review').value === '', 'a filter select was not reset');
  expect($('#sim-sort').value === 'similarity-asc', 'sort was not reset to the default');
  expect(dataRows().length === TOTAL, `reset restored ${dataRows().length} of ${TOTAL} rows`);
  expect(nonDecreasing(dataRows().map(pct)), 'reset did not restore ascending order');

  // --- Row-detail link: correct modal, hash and focus return --------------------
  reset(); setSelect('#sim-band', 'close');
  const linkRow = dataRows()[0];
  const linkExcel = excel(linkRow);
  const link = linkRow.querySelector('a[href^="#row-"]');
  expect(!!link, 'row detail link missing');
  expect(link && link.getAttribute('href') === `#row-${linkExcel}`, `row detail link href is ${link && link.getAttribute('href')}, expected #row-${linkExcel}`);
  if (link) {
    link.focus();
    link.click();
    await settle();
    const dlg = $('#detail');
    expect(dlg.open, 'row detail link did not open the modal');
    expect($('#dialog-title').textContent.includes(`Excel ${linkExcel}`), `modal title "${$('#dialog-title').textContent}" does not match Excel ${linkExcel}`);
    expect(location.hash === `#row-${linkExcel}`, `hash is ${location.hash}, expected #row-${linkExcel}`);
    expect($('#dialog-body').textContent.includes('Advisory Jev similarity'), 'dialog lost the advisory similarity measure');
    $('#close-detail').click();
    await settle();
    expect(document.activeElement === link, 'focus did not return to the row detail link after closing the modal');
    expect(location.hash === `#row-${linkExcel}`, `hash changed to ${location.hash} after closing the modal`);
    expect(dataRows().length === 1 && /#row-\d+/.test($('#similarity-report-rows').innerHTML), 'report filter state was lost after using the modal');
  }
  reset();
  expect(dataRows().length === TOTAL, 'report did not return to 34 rows after the interaction run');
  expect($('#similarity-report-summary').textContent.includes(`All ${TOTAL} rows`), 'summary is not labelled as the all-rows, unfiltered summary');
  // Leave the page as found: default filters, ascending order, no modal hash.
  if (location.hash) history.replaceState(null, '', location.pathname);

  if (problems.length) throw Error(problems.join('\n'));
  return {
    totalShown: base.length,
    defaultAscending: true,
    bandSets: { close: closeSet.length },
    statuses: statusOptions.length,
    intersectionSize: intersected.length,
    sortModes: ['similarity-asc', 'similarity-desc', 'workbook-asc', 'confidence-asc', 'confidence-desc'],
    zeroResultEmptyState: true,
    resetTo34: true,
    rowDetailModal: { excel: linkExcel, hashPreserved: true, focusReturned: true },
  };
})()
