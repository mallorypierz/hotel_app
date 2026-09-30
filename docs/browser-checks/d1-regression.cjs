// Reuse the existing controlled suite while preserving its earlier evidence.
const fs = require('node:fs');
const Module = require('node:module');
const path = require('node:path');
const filename = path.resolve('docs/browser-checks/discovery.cjs');
const source = fs.readFileSync(filename, 'utf8')
  .replaceAll('docs/live-hotel-ui-', 'docs/d1-controlled-')
  .replaceAll('docs/browser-checks/discovery-results.json', 'docs/browser-checks/d1-regression-results.json');
const suite = new Module(filename, module);
suite.filename = filename;
suite.paths = module.paths;
suite._compile(source, filename);
