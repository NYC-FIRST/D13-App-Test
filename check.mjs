// Deploy parity check: dist/ must contain exactly the tracked site files.
// Run after `npm run build`. Fails loudly on a missing file or a leaked one.
import { execFileSync } from 'node:child_process';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const repoRoot = path.resolve(import.meta.dirname, '..');
const dist = path.join(import.meta.dirname, 'dist');

const tracked = execFileSync('git', ['ls-files', '--', '.', ':!:webflow/**',
  ':!:docs/**', ':!:*.md', ':!:**/*.md', ':!:package.json', ':!:.gitignore'],
  { cwd: repoRoot, encoding: 'utf8' }).split('\n').filter(Boolean);

const walk = (dir) => fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) =>
  e.isDirectory() ? walk(path.join(dir, e.name)) : [path.relative(dist, path.join(dir, e.name))]);
// Astro's own output is expected; everything else must be a tracked site file.
const built = walk(dist).filter((f) => !f.startsWith('_astro/') && !f.startsWith('health/'));

const missing = tracked.filter((f) => !built.includes(f));
const leaked = built.filter((f) => !tracked.includes(f));
assert.deepEqual(missing, [], `missing from dist: ${missing}`);
assert.deepEqual(leaked, [], `leaked into dist: ${leaked}`);
console.log(`[d13] ok — ${built.length} files, exact parity with git`);
