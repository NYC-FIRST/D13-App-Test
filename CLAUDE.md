# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Repository Overview

Static site for the NYC FIRST District 13 STEM center, deployed as a **Webflow Cloud app** on the org's Webflow site. No build step, no framework, no dependencies — the repo root **is** the published directory.

| | |
|---|---|
| **Live** | `https://www.nycfirst.org/d13-app/home` |
| **Staging** | `https://nycfirst.webflow.io/d13-app/home` |
| **Entry URL** | `/d13-app/home` — the bare `/d13-app` 404s by design (see File Layout) |
| **Git root** | `/Users/avigoldman/d13` |
| **Config** | `webflow.json` → `{"cloud":{"framework":"static"}}`. The mount path lives in the Webflow dashboard, not in this repo. |

*History: this was `nycfirst-d13.github.io` on GitHub Pages until 2026-09. Pages is retired — it is not a fallback, not a mirror, and nothing here should reference it. See `Webflow-plan.md`.*

## Repo & Remotes

| Remote | Repo | Role |
|--------|------|------|
| `upstream` | `NYC-FIRST/d13` | Org-owned. **Webflow Cloud deploys from here** (`main`). |
| `origin` | `aaavvviii333/d13` | Personal fork. |

**Pushing to `origin` alone does not deploy.** A change is only live once it is on `upstream main`.

```bash
git -C /Users/avigoldman/d13 push upstream main
git -C /Users/avigoldman/d13 push origin main     # keep the fork in sync
```

## Contributing

The org owns the repo; individuals keep credit for their commits. Two paths:

- **Org members** (including Avi): branch in `NYC-FIRST/d13`, PR into `main`.
- **Outside contributors**: fork, branch, PR into `NYC-FIRST/d13`. No org seat needed.

Preserve per-contributor authorship — don't squash away who wrote what.

## File Layout

A page named `<x>.html` at the repo root serves at `/d13-app/<x>` and **owns the sibling `<x>/` directory**, which holds its assets. `arcade.html` serves at `/d13-app/arcade`; its JS, CSS and data live in `arcade/`.

**Never create an `index.html` anywhere.** Webflow Cloud's worker redirects a directory holding `index.html` toward a trailing slash (307 → `/dir/`) while the Webflow site edge strips trailing slashes (301 → `/dir`). Any directory index therefore loops forever (`ERR_TOO_MANY_REDIRECTS`). Every `index.html` was renamed out of existence in commit `2262bb5`; re-adding one re-breaks the site. This is also why `/d13-app` itself 404s — it maps to the app's own root directory.

## The `<base href>` Contract

Webflow Cloud does not rewrite paths for static apps. Under a slash-less mount, the browser treats the last path segment as a file, so a bare `href="app.js"` on `/d13-app/arcade` would resolve to `/app.js` and 404. Every page therefore carries a generated `<base href="/d13-app/…">` on line 4.

**These stamps are generated — never hand-edit them.** After adding or moving any page:

```bash
tools/set-base.sh /d13-app          # re-stamp every tracked .html
python3 tools/check-links.py        # verify every relative ref resolves
python3 tools/serve-like-webflow.py --audit   # verify no redirect loops
npm run serve                       # local server that models Webflow's redirects
```

A page needs a `<head>` to be stamped; files without one are skipped and will not resolve their assets correctly.

## Child Directories

Each child directory is a self-contained app or page, served by its root-level `.html` page.

| Page | Directory | URL | Purpose |
|------|-----------|-----|---------|
| `home.html` | — | `/d13-app/home` | Site entry page |
| `card-prompt-builder.html` | — | `/d13-app/card-prompt-builder` | STEM card art prompt builder |
| `laser-maker.html` | `laser-maker/` | `/d13-app/laser-maker` | Browser-based vector design tool for laser cutting |
| `bed-maker.html` | `bed-maker/` | `/d13-app/bed-maker` | Merges a day's Laser Maker SVGs onto one 36×24 laser bed |
| `arcade.html` | `arcade/` | `/d13-app/arcade` | 8-bit virtual arcade for student MakeCode games |
| `stem-stations.html` | `stem-stations/` | `/d13-app/stem-stations` | STEM stations landing page |
| `bird-bingo.html` | `bird-bingo/` | `/d13-app/bird-bingo` | Bird bingo game |
| `hello-waves.html` | `hello-waves/` | `/d13-app/hello-waves` | Hello waves app |
| `present.html` | `present/` | `/d13-app/present` | One-off projector page for the 2026-09-11 staff PD. Standalone, not linked from the site |

## Git & Commits

The git repo is always the **parent directory**, regardless of which child directory Claude Code is invoked from. There are no nested git repos — child directories are plain subdirectories.

**Always commit from the parent:**

```bash
git -C /Users/avigoldman/d13 add <path>
git -C /Users/avigoldman/d13 commit -m "..."
```

Do not ask for permission to commit from the parent directory — this is always correct.

**Scope each commit to one child directory + one logical change.** Stage by path — never bare `git add .` that sweeps multiple apps into one commit:

```bash
git -C /Users/avigoldman/d13 add laser-maker/         # one app only
git -C /Users/avigoldman/d13 commit -m "feat(laser-maker): ..."
```

- Conventional prefix scoped to the area: `feat(arcade): …`, `docs(stem-stations): …`.
- Run `git status` to verify what's staged before committing.
- Touched two apps? Make two commits, one per app.

**When working in a child directory that has its own `CLAUDE.md`:** that file should document the same `git -C` commit formula so future Claude instances invoked from within that child know where to commit.

**When adding a new child directory:** create `<name>.html` at the repo root (not `<name>/index.html`), put its assets in `<name>/`, run `tools/set-base.sh /d13-app`, and create a `CLAUDE.md` inside the directory with a Git & Commits section pointing at the parent.
