# Pinned local visualization dependencies

- `d3-path-3.1.0.min.js` — [d3-path 3.1.0](https://github.com/d3/d3-path/tree/v3.1.0), BSD-3-Clause; see `d3-path-v3.1.0-LICENSE`.
- `d3-shape-3.2.0.min.js` — [d3-shape 3.2.0](https://github.com/d3/d3-shape/tree/v3.2.0), BSD-3-Clause; see `d3-shape-v3.2.0-LICENSE`.

Pinned UMD distributions obtained from jsDelivr's version-specific npm package paths. `build-condition-mindmap.py` embeds them into `condition-row-profile-mindmap.html` for offline viewing. Only D3 Shape's [horizontal link generator](https://d3js.org/d3-shape/link) is used: the existing row/profile layout is retained. Do not manually edit the embedded builds; update the pins, license notices, source copies and HTML regeneration together.
