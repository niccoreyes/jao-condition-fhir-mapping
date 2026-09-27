// Run in the browser: agent-browser eval --stdin < tests/sankey-geometry.js
// Checks the *rendered* SVG endpoints, not just row-to-subpath membership.
(() => {
  const stage = document.querySelector('#stage');
  const svg = document.querySelector('#flows');
  if (!stage.offsetWidth) {
    const count = svg.querySelectorAll('path').length;
    if (count) throw Error(`Hidden mobile SVG still contains ${count} paths`);
    return { mobile: true, paths: 0, pairedRows: document.querySelectorAll('.mobile-row').length };
  }
  const box = stage.getBoundingClientRect(), overlay = svg.getBoundingClientRect();
  const paths = [...svg.querySelectorAll('path')];
  const problems = [];
  for (const p of paths) {
    const row = document.getElementById('row-' + p.dataset.row);
    const target = document.querySelector(`[data-key="${p.dataset.key}"]`);
    if (!row || !target) { problems.push(`Missing DOM anchor: ${p.dataset.row} -> ${p.dataset.key}`); continue; }
    const a = row.getBoundingClientRect(), b = target.getBoundingClientRect();
    const start = p.getPointAtLength(0), end = p.getPointAtLength(p.getTotalLength());
    const tolerance = 0.15; // D3 emits coordinates rounded to 3 fractional digits.
    const near = (actual, wanted) => Math.abs(actual - wanted) < tolerance;
    if (!near(start.x + overlay.left, a.right) || !near(end.x + overlay.left, b.left) ||
        !(start.y + overlay.top >= a.top && start.y + overlay.top <= a.bottom) ||
        !(end.y + overlay.top >= b.top && end.y + overlay.top <= b.bottom)) {
      problems.push(`Detached: ${p.dataset.row} -> ${p.dataset.key}`);
    }
    if (start.x >= end.x) problems.push(`Reversed: ${p.dataset.row} -> ${p.dataset.key}`);
  }
  const expectedCount = [...document.querySelectorAll('.source-row')].reduce((count, row) => {
    const n = Number(row.dataset.row), group = rawById.get(n).profileKey;
    return count + PATHS[group].filter(([, ,members]) => members.includes(n)).length;
  }, 0);
  if (paths.length !== expectedCount) problems.push(`Missing edges: ${paths.length}/${expectedCount}`);
  if (problems.length) throw Error(problems.join('\n'));
  return { paths: paths.length, detached: 0, reversed: 0, width: Math.round(box.width), height: Math.round(box.height) };
})()
