// Run at desktop width after opening condition-row-profile-mindmap.html:
// agent-browser eval --stdin < tests/terminology-geometry.js > terminology-presentation-layout.json
// Checks actual modal/table geometry; Jev's markup review cannot establish pixels.
(() => {
  if (innerWidth < 781) throw Error('Run this geometry check at desktop width (at least 781 px).');
  const dialog = document.querySelector('#detail');
  if (!dialog.open) document.querySelector('#row-4').click();
  const section = dialog.querySelector('.terminology-section');
  const viewport = section?.querySelector('.term-table-scroll');
  const table = viewport?.querySelector('.terminology-table');
  if (!section || !viewport || !table) throw Error('Terminology section or comparison table missing.');
  const modalWidthPx = dialog.clientWidth;
  const tableViewportWidthPx = viewport.clientWidth;
  const tableContentWidthPx = viewport.scrollWidth;
  const tableViewportShareOfModal = +(tableViewportWidthPx / modalWidthPx).toFixed(3);
  const desktopHorizontalScrollRequired = tableContentWidthPx > tableViewportWidthPx + 1;
  const terminologyParent = section.parentElement.id;
  if (terminologyParent !== 'dialog-body') throw Error('Terminology is not in its own full-width modal section.');
  if (tableViewportShareOfModal < .8 || desktopHorizontalScrollRequired)
    throw Error(`Desktop terminology table is squeezed: ${tableViewportWidthPx}/${modalWidthPx}px; scroll=${desktopHorizontalScrollRequired}`);
  return {
    view: `${innerWidth}x${innerHeight} desktop, Excel row 4 dialog`,
    modalWidthPx, dialogContentWidthPx: dialog.querySelector('#dialog-body').clientWidth,
    terminologyParent, tableViewportWidthPx, tableContentWidthPx,
    desktopHorizontalScrollRequired, tableViewportShareOfModal,
    source: 'Chromium agent-browser DOM measurements of the rendered modal'
  };
})()
