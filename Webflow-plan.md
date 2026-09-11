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

**Status:** Phase 0 complete (2026-09-11). Phase 1 blocked: framework `static`
does not work (§15). Current approach is a Next.js wrapper on a `d13-app`
branch (§16).

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
| ~~Whether the trailing-slash 301 is platform-wide or specific to the display-api app's own router~~ | **Resolved §15.4.** Platform-wide. |
| ~~Whether site password protection covers Cloud apps~~ | **Resolved §15.4.** It does not. |
| Whether a mount path of `/` is permitted (needed for the subdomain plan) | Phase 5 — test, or ask Webflow support. |
| Whether `static` is a usable framework or a reserved-but-unimplemented value | §15. App creation rejects a repo with no `package.json`. |

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
- [ ] Note the published directory in the build log. There is no build-history
      rollback to check for — see §11, corrected.

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

- **Bad deploy** — there is no dashboard redeploy. Webflow Cloud's documented
  rollback is git-only: "Revert your branch to the desired commit in GitHub"
  and push. It "creates a new deployment with the previous code version. It
  doesn't restore the exact state of the previous deployment." Old deployments
  cannot even be previewed — only the most recent successful one.
- **Bad commit** — same mechanism: `git revert` on `main` and push.
- **Failed build** — nothing to do. "The most recent successful build will
  continue running. Failed deployments never impact your live site.""
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

---

## 15. Phase 1 blocker — `package.json` required at app creation (2026-09-11)

Creating the Cloud app failed before any deploy, at repo validation:

> No package.json found
> Astro and Next.js apps need a package.json to deploy.

`webflow.json` was already pushed and present at the repo root (`62c4c25`), so
it was either not read at this stage or does not exempt the repo from the check.

### 15.1 What the docs actually say

- `static` **is** a listed value: "Supported values are `nextjs`, `astro`,
  `vite`, and `static`." That is the *only* mention of it anywhere in the
  Webflow Cloud docs. No static-site guide, no published directory, no
  statement about whether it skips `npm install` or a build command.
- The CLI reference is narrower still: `framework` is "Framework preset either
  `nextjs` or `astro`".
- Prerequisites list only Astro 6/7, Next.js 15+, Vite 6.1+, plus "Node.js 22
  or later and npm installed". npm is the only supported package manager.
- The build pipeline is framework-shaped end to end: clone → **detect framework
  and version from `package.json`** → validate → `npm install` (plus the
  adapter) → run the framework's build command → collect output.
- Webflow's own docs assistant will not confirm that `static` works, and points
  at support for an authoritative answer.

**Read:** `static` is a real enum value on a pipeline that assumes a Node
project. Treat it as undocumented, not as a supported no-build path.

### 15.2 Useful limits (from the limits page)

- Apps per Site: 5 (Starter) / 15 (Core, Freelancer) / 50 (Growth, Agency,
  Enterprise). Confirms Phase 0 — `/display-api` plus this one is fine on any
  plan.
- Build output: 100 MB compressed. Other static files: 20 MB each. Images:
  20 MB each. This repo is ~11 MB total — no concern.
- Worker bundle: 10 MB. Static assets are not part of the worker bundle.
- 1 GitHub repo per Cloud app; 10 environments per app.

### 15.3 Options

1. **Minimal `package.json` at the repo root**, keep `webflow.json` framework
   `static`. 6 lines, no dependencies, a no-op `build` script. Inert on GitHub
   Pages. Resolves the question with one push: either app creation proceeds and
   the build log tells us what `static` publishes, or it fails again with a
   *different* error, which is itself the answer. **Try this first.**
2. **Vite shell, no repo restructure.** `vite` as a devDependency so detection
   succeeds, `webflow.json` framework `vite`, and a build script that copies
   the tracked files into `dist/`. Documented framework, undocumented shape.
   Files stay at the repo root, so GitHub Pages keeps working.
3. **Real Astro or Vite wrapper**, all 145 files moved under `public/`. Fully
   documented path. **Breaks GitHub Pages immediately** — Pages serves the repo
   root and cannot be pointed at `public/` — so it ends the dual-host period
   and pulls Phase 7 forward. Worst fit for this plan.
4. **Ask Webflow support** what `static` does and whether it is available on
   this plan. Authoritative, slow. Worth sending in parallel with option 1, and
   it can carry the Phase 5 `/` mount-path question (§3) in the same ticket.

Options 1 and 2 both leave GitHub Pages untouched, so rollback (§11) is still
just "delete the Cloud app".

- [ ] Option 1 attempted — record the exact error or the published directory.
- [ ] Option 2 if option 1 fails.
- [ ] Support ticket sent (also ask about a `/` mount path).

### 15.4 Deployment silently reverts to the form (2026-09-11)

With `package.json` pushed (`9532140`) the repo validates and the creation form
is accepted — then initialization stops and the UI drops back to the form. No
error surfaced. No app created.

Probing the live site while diagnosing resolved two §3 unknowns for free:

```
/d13-app        401   Designer page, published, password-protected
/d13-app/       301 -> /d13-app
/display-api    200   Cloud app, not behind the password
/               200
/d13, /d13app   404   unused
```

- **Site/page password protection does not cover Cloud apps.** A
  password-protected Webflow page returns 401 while the Cloud app at
  `/display-api` returns 200.
- **The trailing-slash 301 is platform-wide**, not the display-api app's own
  router — a plain Webflow page does it too. So §4's base-URL risk is real and
  Phase 2 must check it.
- **`/d13-app` is a live published page**, not a draft. Leading suspect for the
  silent failure: the mount path collides with an existing page slug. The
  docs' precedence rule covers route conflicts at *serve* time and says nothing
  about whether creation accepts a colliding path.

Diagnostic order, cheapest first:

- [ ] DevTools → Network, retry. The failing request's response body carries
      the real error; a silent form-revert is a swallowed 4xx.
- [ ] Retry with mount path `d13`. One form field, no code change. Creating
      successfully confirms the collision.
- [ ] Delete the empty Designer page `6a9990cb967581032d3aee6e` — Phase 4
      deletes it anyway, and it is empty and password-gated — then retry
      `d13-app`.
- [ ] If all three fail, `static` is being rejected server-side. Go to §15
      option 2.

This supersedes §4's "do not test at a throwaway mount path" for *diagnosis*
only. That argument was about not tuning hardcoded base-path remedies twice;
no code has been changed yet, so a temporary mount path costs nothing here.

---

## 16. Phase 1b — framework wrapper on a `d13-app` branch (2026-09-11)

`static` is out. Evidence: app creation is accepted with a `package.json`
present, then initialization silently reverts to the form — no error, no
deployment, at three different mount paths (`d13-app` before and after deleting
the colliding Designer page, and `d13app`). Every executable surface names only
two frameworks:

| Source | Accepted `framework` values |
|---|---|
| BYOA doc, `webflow.json` note | `nextjs`, `astro`, `vite`, `static` |
| CLI `webflow.json` reference | "either `nextjs` or `astro`" |
| `apps init --framework` | `astro`, `nextjs` |
| `apps deploy --framework` | `nextjs`, `astro` |

One sentence in the entire corpus says `static`. Treat it as reserved and
unimplemented.

**The Webflow MCP server cannot help here.** Its tools cover CMS, pages,
elements, styles, assets, forms, comments, localization, scripts and
publishing. There is no Cloud app, environment, or deployment surface — Cloud
app management is UI or CLI only. The UI swallows the error; the CLI prints it
(`webflow apps init --import … --dry-run --json`, CLI installed locally at
`2.8.0-next.2`, login pending).

### 16.1 Approach — Astro wrapper in `webflow/`, on a `d13-app` branch

A branch, `d13-app`, adds an Astro wrapper that packages the existing vanilla
files for Webflow Cloud. Webflow Cloud environments track one branch, so the
env points at `d13-app` through Phases 1–2 while `main` — and therefore GitHub
Pages — stays untouched. After Phase 2 verification the branch merges to `main`
and the env repoints there.

**Framework: Astro**, decided 2026-09-11, over Next.js. Astro copies `public/*`
into `dist/` verbatim and needs no routes, so the repo's own `index.html`
becomes `/` with nothing to reconcile. Next's `output: 'export'` writes
`out/index.html` from `app/page.tsx`, which collides with the repo's root
`index.html` — and the tempting fix for that collision (rename or move the root
file) is exactly the change that breaks GitHub Pages. Astro removes the
temptation. It is also a smaller dependency and a lighter worker bundle against
the 10 MB cap.

**The wrapper lives in `webflow/`**, set as the environment's app root, rather
than at the repo root. Webflow clones the whole repo and builds in the
configured app path, so a subdirectory works. This keeps the Node toolchain out
of the repo root permanently: after the merge, `main` gains one clearly-labeled
folder instead of a lockfile, a config and an `app/` directory scattered across
the root that students and volunteers have to step around. Phase 7, or leaving
Webflow entirely, deletes one folder.

### 16.2 Hard constraints on the wrapper

1. **The 145 files do not move.** GitHub Pages serves the repo root; moving
   them into `public/` breaks Pages the moment the branch merges, ending the
   dual-host period and pulling Phase 7 forward.
2. **Generated directories are gitignored** — `webflow/public/`,
   `webflow/dist/`, `webflow/node_modules/`, `webflow/.astro/`.
3. **No hardcoded base path.** `base` reads Webflow's injected `BASE_URL`.
4. **Wrapper files are inert on GitHub Pages.** Pages ignores `package.json`,
   `astro.config.mjs` and `webflow.json`, and has no directory listing, so
   `/webflow/` is a 404. Nothing shadows a real route.
5. **No new dependency the site consumes.** The wrapper is packaging only; the
   six child apps stay plain HTML/CSS/JS with no build step of their own.

### 16.3 What was built

| File | Purpose |
|---|---|
| `webflow/astro.config.mjs` | Collects the tracked site files into `public/` at config load, then `base` from `BASE_URL` |
| `webflow/package.json` | `astro@^7.3.2` as the only dependency; `build`, `dev`, `test` |
| `webflow/webflow.json` | Pins `framework: "astro"`. Moved here from the repo root — it belongs at the app root |
| `webflow/src/pages/health.astro` | Build proof. `/health` renders `ok` only if Astro actually ran |
| `webflow/check.mjs` | Parity check, `npm test` |

**The collector reads from git, not the working directory.** First attempt
copied the repo root wholesale and swept in 225 untracked local files —
`.playwright-cli` caches in three child apps, `.claude/memory`, local `docs/`
and `plans/` directories. GitHub Pages never served any of that, because Pages
serves the committed tree. `git ls-files` with exclude pathspecs is both the fix
and the filter, so there is no filter logic to maintain and a new child app
ships without touching the config.

`npm test` asserts exact parity: every tracked site file present in `dist/`,
nothing in `dist/` that git does not track. Current state: **114 files, exact
parity, clean build.** That check is what catches a leak or a dropped app the
next time this config is edited.

The repo-root `package.json` is **deleted on this branch**. It existed only to
get past the creation-time validation in §15; once `webflow/package.json`
exists, Webflow reports "multiple package.json found" and asks which project
root to use. Deleting the root one resolves the ambiguity and leaves no fake
manifest on `main` after the merge. If a future creation attempt reinstates the
§15 block, that is the signal the check reads the repo root rather than the app
path — re-add it then, not preemptively. It still exists on `main` and
disappears with the merge.

### 16.4 What the wrapper does not fix

§4 still applies. Astro's `base` rewrites only Astro-generated URLs — it does
not touch hand-written `href="styles.css"` in these files. At a slash-less
mount root those still resolve against the domain root. Phase 2 checks; Phase 3
chooses between a `<base href>` sweep and jumping to the subdomain (§10), and
Phase 3's reasoning is unchanged.

### 16.5 Steps

- [x] Branch `d13-app` off `main`.
- [x] Astro wrapper in `webflow/`, gitignored build artifacts.
- [x] `npm run build` clean; `npm test` confirms 114-file parity with git.
- [ ] Push the branch.
- [x] Delete the repo-root `package.json` — Webflow reported multiple
      manifests and asked for a project root.
- [ ] Create the Cloud app: repo `nycfirst-d13/nycfirst-d13.github.io`, branch
      **`d13-app`**, **app root `webflow`**, mount path `d13-app`.
- [ ] Read the build log. Record the published directory (§3 unknown) — it
      should be `webflow/dist`.
- [ ] If creation fails again, the wrapper is not the cause. Get the CLI
      dry-run error before changing anything else: `webflow auth login`, then
      `webflow apps init --import <repo-url> --branch d13-app --mount /d13-app
      --site-id 5d45ab770ae4a12ae3df8293 --skip-clone --dry-run --json`.
- [ ] Check `/d13-app/health` first — it isolates "did Astro run" from "do the
      static files resolve".
- [ ] Run Phase 2 verification (§7) against the deployed branch.
- [ ] Merge `d13-app` to `main`, repoint the environment to `main`, confirm
      GitHub Pages still serves correctly from the merged tree, delete the
      branch.
