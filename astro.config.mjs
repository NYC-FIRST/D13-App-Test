import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { defineConfig } from 'astro/config';

// The site's real files live at the repo root, not in this wrapper — GitHub
// Pages serves that root directly and must keep working. So collect them into
// public/ at build time instead of moving them.
//
// Source of truth is git, not the working directory: a local checkout carries
// untracked junk (.playwright-cli, .claude/memory) that must never deploy.
// ponytail: git pathspecs do the filtering, so there is no filter logic here.
// Add a child app and it ships with no change to this file.
const EXCLUDE = [
  ':!:webflow/**',
  ':!:docs/**',
  ':!:*.md',
  ':!:**/*.md',
  ':!:package.json',
  ':!:.gitignore',
];

const repoRoot = path.resolve(import.meta.dirname, '..');
const publicDir = path.join(import.meta.dirname, 'public');

const files = execFileSync('git', ['ls-files', '-z', '--', '.', ...EXCLUDE], {
  cwd: repoRoot,
  encoding: 'utf8',
}).split('\0').filter(Boolean);

fs.rmSync(publicDir, { recursive: true, force: true });
for (const file of files) {
  const dest = path.join(publicDir, file);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.copyFileSync(path.join(repoRoot, file), dest);
}
console.log(`[d13] collected ${files.length} tracked files into public/`);

export default defineConfig({
  // Webflow Cloud injects the mount path. Never hardcode it.
  base: process.env.BASE_URL || '/',
});
