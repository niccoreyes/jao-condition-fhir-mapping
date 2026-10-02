// Run in the browser: agent-browser eval --stdin < tests/similarity-report-geometry.js
// Checks the rendered advisory PHCDI similarity report, its scroll containment and
// accessible labels; the per-row dialog measure is asserted separately after opening a row.
(() => {
  const problems = [];
  const section = document.querySelector('#similarity-report');
  if (!section) throw Error('Missing #similarity-report section');
  const rows = [...document.querySelectorAll('#similarity-report-rows tr')];
  if (rows.length !== 34) problems.push(`Expected 34 table rows, found ${rows.length}`);
  const pcts = rows.map(tr => Number(tr.querySelector('.sim-num')?.textContent));
  for (let i = 1; i < pcts.length; i += 1) {
    if (!(pcts[i] >= pcts[i - 1])) { problems.push(`Rows not sorted ascending at ${i} (${pcts[i - 1]} -> ${pcts[i]})`); break; }
  }
  const cells = [...document.querySelectorAll('#similarity-report .sim-cell[role="img"]')];
  if (cells.length !== rows.length) problems.push(`Expected an accessible measure per row, found ${cells.length}/${rows.length}`);
  for (const cell of cells) {
    const label = cell.getAttribute('aria-label') || '';
    if (!/(\d+) of 100/.test(label) || !/advisory/i.test(label)) { problems.push('Similarity cell aria-label missing the measure'); break; }
    if (!/not clinical equivalence/i.test(label)) { problems.push('Similarity cell aria-label omits the non-equivalence caveat'); break; }
  }
  const scroll = document.querySelector('#similarity-report-scroll');
  let containedScroller = false;
  if (!scroll) problems.push('Missing #similarity-report-scroll region');
  else {
    const overflowX = getComputedStyle(scroll).overflowX;
    const focusable = scroll.getAttribute('tabindex') === '0';
    if (overflowX !== 'auto' && overflowX !== 'scroll') problems.push(`Scroll region overflow-x is ${overflowX}, not auto/scroll`);
    if (!focusable) problems.push('Scroll region is not focusable');
    // A wide table must be a real, contained, keyboard-reachable scroller: when the
    // region actually overflows, it must scroll (overflow-x auto/scroll) and be focusable.
    if (scroll.scrollWidth > scroll.clientWidth + 1) {
      containedScroller = (overflowX === 'auto' || overflowX === 'scroll') && focusable;
      if (!containedScroller) {
        problems.push(`Wide table overflows ${scroll.scrollWidth} > ${scroll.clientWidth} but the region is not a contained scroller (overflow-x:${overflowX}, tabindex:${scroll.getAttribute('tabindex')})`);
      }
    }
  }
  const doc = document.documentElement;
  if (doc.scrollWidth > doc.clientWidth + 1) problems.push(`Page horizontal overflow: ${doc.scrollWidth} > ${doc.clientWidth}`);
  if (!section.querySelector('.sim-legend')) problems.push('Missing band legend');
  if (!section.querySelector('a[href="#similarity-report-scroll"]')) problems.push('Missing jump/skip target');
  if (!/#row-\d+/.test(section.innerHTML)) problems.push('Missing per-row detail link');
  if (problems.length) throw Error(problems.join('\n'));
  return {
    tableRows: rows.length,
    sortedAscending: true,
    minPct: pcts[0],
    maxPct: pcts[pcts.length - 1],
    accessibleMeasures: cells.length,
    scrollViewport: Math.round(scroll?.clientWidth ?? 0),
    scrollContent: Math.round(scroll?.scrollWidth ?? 0),
    containedInsideRegion: !!scroll && scroll.scrollWidth > scroll.clientWidth,
    containedScroller,
    pageHorizontalOverflow: false,
    viewportWidth: doc.clientWidth,
  };
})()
