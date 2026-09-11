# Webflow Cloud Migration Plan

Migrate the `nycfirst-d13.github.io` repo off GitHub Pages and onto a Webflow
Cloud app that **builds directly from this repo** — first at
`nycfirst.org/d13-app`, later at a `d13.nycfirst.org` subdomain — then update
the repo's documentation to describe the new deployment.

**GitHub Pages is not part of the end state.** During the migration period it
stays up, untouched and unredirected — two independent hosts serving the same
repo, neither pointing at the other. It is switched off in Phase 7, once the
Cloud app is proven and the new URL has been distributed. Nothing in this plan
proxies, redirects, or falls back to Pages by design.

**Status:** Phase 0 complete (2026-09-11). Phase 1 not started — no
`webflow.json`, no Cloud app.

---

## 1. Current state

| Thing | Value |
|---|---|
| Repo | `nycfirst-d13/nycfirst-d13.github.io` |
| Local root | `/Users/avigoldman/nycfirst-d13.github.io` |
| Host today | GitHub Pages, repo root = site root, `.nojekyll`, no workflows, no CNAME |
| Host during migration | Both, independently. No redirect either direction. |
| Host in end state | Webflow Cloud app, built from `main` |
| Tracked files | 145 files, ~11 MB |
| Build step | None. Plain HTML/CSS/JS |
| Webflow site | NYC FIRST — `5d45ab770ae4a12ae3df8293`, domains `nycfirst.org` + `www.nycfirst.org` |
| Existing Cloud app | `nyc-first-display-api-cloud` ← `NYC-FIRST/nyc-first-display-api-cloud`, mounted at `/display-api` |
| Target page | Designer page "D13 App", id `6a9990cb967581032d3aee6e`, slug `/d13-app` — currently an empty Body |

Child apps: `arcade/`, `bed-maker/`, `bird-bingo/`, `hello-waves/`,
`laser-maker/`, `stem-stations/`, plus root `index.html` and
`card-prompt-builder.html`.

---

## 2. Established facts

Verified against Webflow docs and by probing the live site — not assumed.

**Webflow Cloud builds from the repo.** Each environment tracks one GitHub
branch; every push to that branch triggers a deploy. The deploy clones the
repo, detects or reads the framework, builds, and serves the output. Nothing
proxies or redirects to another host.

**Route precedence.** Webflow docs, verbatim:

> "If a route conflict occurs between your Webflow Cloud application and your Webflow site, the Webflow Cloud application route takes precedence."

So a Cloud app mounted at `/d13-app` **replaces** the Designer page at that
slug. Webflow does *not* create or reserve a page at a mount path — the empty
"D13 App" page was made by hand and is unrelated to Cloud. Once mounted, it is
shadowed and inert.

**This is a replacement, not an embed.** No Webflow nav, header, or footer will
wrap the app.

**`static` is a supported framework value** alongside `nextjs`, `astro`,
`vite`. No adapter to install — Webflow wires one at build time.

**Multiple Cloud apps per site at different mount paths is supported.**
`/display-api` is unaffected by anything here.

**The repo has no root-absolute paths.** Audited all tracked HTML/JS/CSS:

- zero `src="/…"`, `href="/…"`, `action="/…"`
- zero absolute `fetch()`, `import`, or CSS `url()`
- no service workers, no web manifest
- no `location.origin` / `location.pathname` assumptions

**Trailing slashes are stripped.** Probing the existing mount:

```
/display-api          200
/display-api/         301 → /display-api
/display-api/index.html  404
```

This matches Cloudflare Workers' default `auto-trailing-slash` asset handling,
which is what Webflow Cloud runs on. See §4 — this is the one real risk.

---

## 3. Open unknowns

Neither the Webflow docs nor Webflow's own docs assistant answer these. Do not
plan around a guess; each has a cheap empirical resolution.

| Unknown | How to resolve |
|---|---|
| Which directory a `static` app publishes (repo root? `public/`? `dist/`?) | First deploy log. Advanced settings has an app-root override if it isn't repo root. |
| Whether `package.json` is required for `static` | First deploy. If detection fails, `webflow.json` should still pin it. |
| Deployment limits (file count, file size, total size) | 145 files / 11 MB is small; unlikely to matter. |
| Whether the trailing-slash 301 is platform-wide or specific to the display-api app's own router | Phase 2 test deploy. |
| Whether site password protection covers Cloud apps | Phase 2 — note the behavior, don't gate on it. The 401 is pre-launch safety on the Webflow site, not a user-facing state at deployment. |
| Whether a mount path of `/` is permitted (needed for the subdomain plan) | Phase 5 — test, or ask Webflow support. |
| How far back Webflow Cloud's redeployable build history goes | Phase 1 — check the environment dashboard. This is the rollback mechanism after Phase 7 (§11). |

---

## 4. The one real risk: relative paths at a slash-less mount root

Every asset reference in this repo is bare-relative, which is correct for a
site served at a domain root:

```html
<link rel="stylesheet" href="styles.css">
<a href="card-prompt-builder.html">
<img src="d13_logo.png">
```

Under a mount path with the trailing slash stripped, the browser's base URL for
`https://www.nycfirst.org/d13-app` is `https://www.nycfirst.org/` — the last
path segment is treated as a file, not a directory. So:

| Reference | Resolves to | Result |
|---|---|---|
| `styles.css` | `nycfirst.org/styles.css` | Webflow site, 404 |
| `d13_logo.png` | `nycfirst.org/d13_logo.png` | 404 |
| `card-prompt-builder.html` | `nycfirst.org/card-prompt-builder.html` | 404 |
| `laser-maker/` | `nycfirst.org/laser-maker/` | 404 |

The same applies one level down: at `/d13-app/laser-maker`, a reference to
`modules/canvas-cache.js` resolves to `/d13-app/modules/canvas-cache.js`, not
`/d13-app/laser-maker/modules/canvas-cache.js`.

Phase 2 checks for this on the first deploy. Remedies in Phase 3.

Do not test this at a throwaway mount path first. `/d13-app` has no traffic and
no inbound links today, so there is nothing to protect; changing a mount path
later forces a redeploy and a full re-verification anyway; and the remedy below
hardcodes the mount path, so tuning it against a temporary path means editing
all 7 files twice.

Note that this problem is an artifact of the *mount path*, not of Webflow
Cloud. At the root of a subdomain (Phase 5) it disappears entirely.

---

## 5. Phase 0 — pre-flight

- [x] **Admin/owner rights confirmed.** Repo owner on `nycfirst-d13`, cleared
      with the Webflow admin. The existing Cloud app lives under the separate
      `NYC-FIRST` org, so expect a second, separate GitHub App install prompt
      scoped to `nycfirst-d13`.
- [x] Confirm the Webflow site plan permits an additional Cloud app.
- [x] Start an inventory of where `nycfirst-d13.github.io` URLs have been
      shared — student handouts, Google Classroom, slide decks, QR codes,
      printed material, the NYC FIRST Webflow site itself. Those links keep
      working through the whole migration and die only at Phase 7, so this is
      a checklist to work through, not a blocker. Anything laminated sets the
      pace.

## 6. Phase 1 — first deploy to a test mount

- [x] Add `webflow.json` at repo root:

      {
        "cloud": {
          "framework": "static"
        }
      }

      Inert on GitHub Pages — Pages never reads or serves it, so adding it
      changes nothing about the currently live site.

- [ ] Commit and push:

      git -C /Users/avigoldman/nycfirst-d13.github.io add webflow.json
      git -C /Users/avigoldman/nycfirst-d13.github.io commit -m "chore: pin Webflow Cloud framework to static"
      git -C /Users/avigoldman/nycfirst-d13.github.io push

- [ ] Webflow → site settings → **Webflow Cloud** tab → **Log in to GitHub**
      (not yet connected).
- [ ] **New app** → import `nycfirst-d13/nycfirst-d13.github.io`. If the repo
      doesn't appear in the picker, paste the full repo URL directly.
- [ ] Approve the GitHub App install for the `nycfirst-d13` org.
- [ ] Branch: `main`. App root: blank. Mount path: **`d13-app`**.
- [ ] Deploy. Read the build log and record which directory was published
      (resolves an unknown from §3).
- [ ] Check the environment dashboard for redeployable build history — this is
      the rollback mechanism from §11.

From here on, every push to `main` deploys to Webflow Cloud *and* republishes
GitHub Pages. Two hosts, same commit, no coordination needed between them.

## 7. Phase 2 — verify

Against `nycfirst.org/d13-app`, with the browser console open:

- [ ] Root page renders; `styles.css` and the logo images load (no 404s).
- [ ] Note whether `/d13-app/` 301s to `/d13-app`.
- [ ] Each child app opens and loads its own assets:
      `arcade`, `bed-maker`, `bird-bingo`, `hello-waves`, `laser-maker`,
      `stem-stations`.
- [ ] `card-prompt-builder.html` opens.
- [ ] Password protection: note whether the Cloud app sits behind the site
      password. Informational — the 401 is pre-launch safety, lifted before
      anyone is sent to the URL.
- [ ] Apps Script endpoints still work from the new origin — three of them, all
      origin-agnostic in principle but untested from `nycfirst.org`:
      - `laser-maker/modules/drive-upload.js` (Drive upload, PIN-gated)
      - `arcade/submit.html` (game submission)
      - `stem-stations/index.html` (submission)
- [ ] Third-party embeds load: `arcade.makecode.com`, `makecode.microbit.org`,
      `musiclab.chromeexperiments.com`, `phet.colorado.edu`, `esm.sh`,
      `cdnjs.cloudflare.com`, `cdn.jsdelivr.net`.

**User data does not travel between hosts.** `localStorage` and IndexedDB are
origin-scoped. Saved laser-maker designs and bed-maker caches on
`nycfirst-d13.github.io` will not appear at `nycfirst.org`. During the
migration period both origins are reachable, so users can still get at old
work — but it becomes unreachable at Phase 7. Affected files:
`laser-maker/modules/canvas-cache.js`, `laser-maker/modules/drive-upload.js`,
`bed-maker/modules/cache.js`, `card-prompt-builder.html`.

- [ ] Tell users to export anything they want to keep. Gates Phase 7, not
      Phase 4.

## 8. Phase 3 — decision point

**If Phase 2 is clean:** skip to Phase 4.

**If relative paths break**, pick one:

1. **`<base href="/d13-app/">`** in each `index.html` (7 files). One line each,
   fixes every reference below it. **This breaks GitHub Pages** for as long as
   both hosts are live, since it hardcodes the Webflow mount path — acceptable
   only if you're willing to bring Phase 7 forward and end the dual-host
   period early. Cost beyond that: Phase 5 means editing those 7 lines again
   (or deleting them, if the subdomain serves at root).
2. **Jump to Phase 5 first.** At the root of `d13.nycfirst.org` there is no
   mount path and no base-URL problem at all. Zero code changes, and GitHub
   Pages keeps working untouched throughout.

Option 2 is the better default — it costs nothing and preserves the dual-host
period. Record the decision here before proceeding.

## 9. Phase 4 — roll out

Non-destructive. GitHub Pages keeps serving throughout.

- [ ] Delete or repurpose the now-shadowed Designer page
      `6a9990cb967581032d3aee6e`.
- [ ] Start pointing people at the new URL. Work through the Phase 0 inventory.
- [ ] Leave GitHub Pages alone. No redirect, no banner, no changes — it simply
      continues serving the same repo until Phase 7.

## 10. Phase 5 — `d13.nycfirst.org` subdomain

Worth resolving early — per Phase 3 it may replace Phase 4 rather than follow
it. Webflow Cloud mounts are path-based under a Webflow site's domain, so a
subdomain is not just a mount-path change.

1. **Separate Webflow site for `d13.nycfirst.org`**, with the Cloud app mounted
   at its root. Gives `d13.nycfirst.org/arcade/` — clean, no base-path problem,
   §4 stops applying entirely. Depends on whether a `/` mount path is permitted
   (§3) and on the cost of a second Webflow site. **Preferred.**
2. **Add `d13.nycfirst.org` as a custom domain on the existing site.** The app
   still lives at `d13.nycfirst.org/d13-app` — a subdomain *and* a path, so §4
   still applies. Strictly worse than option 1.

- [ ] Ask Webflow support whether a `/` mount path is permitted.
- [ ] Pick an option, record it here, then redo Phase 2 verification against
      the subdomain.
- [ ] If Phase 4 already shipped, set up a Webflow redirect from
      `nycfirst.org/d13-app` to the subdomain so links shared in between keep
      working. (A redirect *within* Webflow — not from GitHub Pages.)

## 11. Rollback

Through Phases 1–6, rollback is cheap: delete the Webflow Cloud app. The only
repo change up to that point is an inert `webflow.json`, and GitHub Pages has
been serving the whole time. Note that this is a property of the migration
window, not a fallback the architecture depends on — Pages is on its way out
either way.

Once Phase 7 lands, rollback means going backwards *within Webflow Cloud*:

- **Bad deploy** — redeploy the previous build from the environment dashboard.
  Confirm in Phase 1 how many builds back that list reaches (§3).
- **Bad commit** — `git revert` on `main` and push. That triggers a fresh
  deploy of the reverted tree, same as any other push.
- **Broken mount path** — change it back and redeploy. The app keeps serving at
  the old path until the change lands.

The point of no return is Phase 7. Everything before it is reversible.

---

## 12. Phase 6 — documentation updates

The repo's docs say "GitHub Pages" in a dozen places and hardcode a stale local
path. Do this **after** Phase 4 succeeds, so the docs describe reality rather
than an intention. Pages is still live at this point — the docs should describe
the end state and say Pages is being retired, not pretend it's already gone.

### 12.1 Design principle: name the host once

Today each child `CLAUDE.md` restates the host. When the subdomain lands in
Phase 5, that's another sweep through every file. Instead:

- **Root `CLAUDE.md` / `AGENTS.md`** own the deployment facts — host, URL,
  deploy mechanism. One place to edit.
- **Child `CLAUDE.md` files** state only the path *relative to the site root*
  ("served at `/arcade/`") and point at the root file for the canonical host.

That makes Phase 5's doc change a two-file edit instead of a ten-file one.

### 12.2 Bundled fix: stale local path

Every `git -C` example points at `/Users/avigoldman/Desktop/nycfirst-d13.github.io`,
which **does not exist**. The real root is `/Users/avigoldman/nycfirst-d13.github.io`.
Fix it in the same pass — same files, same commit scope.

### 12.3 File-by-file

| File | Lines | Change |
|---|---|---|
| `CLAUDE.md` | 7 | Rewrite the overview: Webflow Cloud app built from this repo, served at `nycfirst.org/d13-app`. Note that GitHub Pages is still live but being retired (Phase 7). Note the §4 base-URL behavior. |
| `CLAUDE.md` | 9, 31–32, 40–41 | `Desktop/` → real path |
| `AGENTS.md` | 7, 9, 31–32, 40–41 | Same as `CLAUDE.md` — the two files are duplicates. Keep them in sync, or make one a pointer to the other. |
| `arcade/CLAUDE.md` | 9 | "served as-is by GitHub Pages at `/arcade/`" → served as-is by Webflow Cloud at `/arcade/` relative to the site root |
| `arcade/CLAUDE.md` | 69–70 | `Desktop/` → real path |
| `arcade/plans/submission-form.md` | 11 | "GitHub Pages file" → static file served by Webflow Cloud. The security point (secrets live only in Apps Script) is unchanged and still correct. |
| `bed-maker/CLAUDE.md` | 54, 58–59 | `Desktop/` → real path |
| `bird-bingo/CLAUDE.md` | 3 | Drop "GitHub Pages site"; keep "served at `/bird-bingo/`", point at root `CLAUDE.md` |
| `bird-bingo/CLAUDE.md` | 10–11 | `Desktop/` → real path |
| `hello-waves/CLAUDE.md` | 3 | As `bird-bingo` |
| `stem-stations/CLAUDE.md` | 3 | As `bird-bingo` |
| `stem-stations/plans/bot-submission-plan.md` | 20 | "public GitHub Pages file" → public static file. Security point unchanged. |
| `laser-maker/CLAUDE.md` | 75 | "the parent directory that serves the GitHub Pages site" → …that serves the Webflow Cloud app; fix `Desktop/` path |
| `laser-maker/docs/superpowers/plans/2026-06-22-svg-import-editable.md` | 15 | `Desktop/` → real path |

### 12.4 New content for root `CLAUDE.md` / `AGENTS.md`

Add a Deployment section covering:

- Host: Webflow Cloud app on the NYC FIRST Webflow site. **GitHub Pages is
  being retired and is not the deployment target** — say so explicitly, so the
  next contributor doesn't reinstate it.
- Live URL: `https://www.nycfirst.org/d13-app` (and the subdomain once Phase 5
  lands)
- Source: this repo, branch `main`, framework pinned `static` via `webflow.json`
- Deploys: automatic on push to `main`. **Publishing the Webflow site does not
  deploy the app, and deploying the app does not publish the site.** Two
  separate actions.
- Manual deploy: `webflow cloud deploy`, or "Deploy latest build" in the
  environment dashboard
- Rollback: redeploy a previous build from the environment dashboard, or
  `git revert` and push
- Path rule for contributors: keep every asset reference relative, never
  root-absolute, and never hardcode a base path — Webflow injects it from the
  mount path at build time
- Whatever §4 turns out to require (base tags, trailing-slash caveats)
- The `/display-api` app is a *different* repo (`NYC-FIRST/nyc-first-display-api-cloud`)
  serving the poster display — not this one

### 12.5 Leave alone

`docs/superpowers/**` and `laser-maker/docs/superpowers/**` are dated,
completed plan and spec documents — historical records of what was decided
then. Do not rewrite them. The `gh-pages` workflow described in
`docs/superpowers/plans/2026-06-24-game-gallery.md` is obsolete; add a one-line
"superseded by Webflow-plan.md — this repo is moving off GitHub Pages" note at
the top rather than editing the body.

### 12.6 Commits

Per repo convention — one child directory, one logical change, staged by path,
never a bare `git add .`:

    git -C /Users/avigoldman/nycfirst-d13.github.io add CLAUDE.md AGENTS.md
    git -C /Users/avigoldman/nycfirst-d13.github.io commit -m "docs: describe Webflow Cloud deployment, fix repo root path"

    git -C /Users/avigoldman/nycfirst-d13.github.io add arcade/
    git -C /Users/avigoldman/nycfirst-d13.github.io commit -m "docs(arcade): Webflow Cloud host, fix repo root path"

...and so on, one commit per child directory. Run `git status` before each.

---

## 13. Phase 7 — retire GitHub Pages

The irreversible step. Run it when the dual-host period has served its purpose:
the Cloud app is stable, the shared-link inventory is worked through, and users
have exported anything they cared about.

- [ ] Confirm the Phase 0 link inventory is fully migrated. After this step,
      `nycfirst-d13.github.io` stops resolving — there is no redirect, because
      a redirect would mean keeping Pages on.
- [ ] Confirm the Phase 2 user-data export has happened. `localStorage` on the
      old origin becomes unreachable.
- [ ] Repo Settings → Pages → source: **None**.
- [ ] Delete `.nojekyll`. It exists only for GitHub Pages.

      git -C /Users/avigoldman/nycfirst-d13.github.io rm .nojekyll
      git -C /Users/avigoldman/nycfirst-d13.github.io commit -m "chore: drop .nojekyll, GitHub Pages retired"

- [ ] Update root `CLAUDE.md` / `AGENTS.md` to drop the "being retired"
      language — Pages is now simply gone.

---

## 14. Sequencing

    Phase 0  pre-flight  ── admin access confirmed; plan check + link inventory
    Phase 1  deploy, mounted at /d13-app    ┐
    Phase 2  verify  ──► broken? ──► Phase 3 │  GitHub Pages live
                            └─► opt 2 ──┐    │  throughout, no redirect
    Phase 4  roll out                   │    │
    Phase 6  documentation sweep        │    │
    Phase 5  subdomain  ◄───────────────┘    ┘
    Phase 7  retire GitHub Pages            ← point of no return

Phase 7 is the only irreversible step. Everything before it is undone by
deleting the Cloud app.
