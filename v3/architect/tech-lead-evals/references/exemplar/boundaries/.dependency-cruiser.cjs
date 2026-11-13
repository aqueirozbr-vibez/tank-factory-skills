// Import contracts for fieldco/reading-web (TRD §4 Component map).
module.exports = {
  forbidden: [
    { name: 'capture-isolated', severity: 'error', from: { path: '^src/capture/' }, to: { path: '^src/review/' } },
    { name: 'review-isolated', severity: 'error', from: { path: '^src/review/' }, to: { path: '^src/(capture|sync)/' } },
    { name: 'sync-isolated', severity: 'error', from: { path: '^src/sync/' }, to: { path: '^src/(capture|review)/' } },
    { name: 'api-client-leaf', severity: 'error', from: { path: '^src/api/' }, to: { path: '^src/(capture|review|sync)/' } },
    { name: 'ui-leaf', severity: 'error', from: { path: '^src/ui/' }, to: { path: '^src/(capture|review|sync|api)/' } },
  ],
  options: { doNotFollow: { path: 'node_modules' }, tsConfig: { fileName: 'tsconfig.json' } },
};
