# Webflow Cloud deployment

How this site is deployed, the two constraints that shape the repo, and the work still open.
Current as of 2026-09-15. For day-to-day rules see the root `CLAUDE.md`; this file is the
reference for the platform itself.

---

## 1. What is deployed

| | |
|---|---|
| **App** | Webflow Cloud app on the NYC FIRST Webflow site (`5d45ab770ae4a12ae3df8293`, domains `nycfirst.org` + `www.nycfirst.org`) |
| **Source** | `NYC-FIRST/d13`, branch `main` |
| **Framework** | `static` — `webflow.json` is `{"cloud":{"framework":"static"}}`, the entire config |
| **Mount path** | `/d13-app`, set in the Webflow dashboard, **not in this repo** |
| **Live** | `https://www.nycfirst.org/d13-app/home` |
| **Staging** | `https://nycfirst.webflow.io/d13-app/home` |
| **Entry URL** | `/d13-app/home`. The bare `/d13-app` 404s — see §3.1 |

A sibling Cloud app, `nyc-first-display-api-cloud` (from `NYC-FIRST/nyc-first-display-api-cloud`),
is mounted at `/display-api` on the same site. Multiple apps per site at different mount
paths is supported and works.

A Cloud app **replaces** any Designer page at its mount slug — it does not embed in one.
Webflow does not reserve or create a page at a mount path.

## 2. How deploys work

- **Trigger:** every push to `NYC-FIRST/d13` `main` builds and deploys. Pushing to a personal
  fork does nothing.
- **Build:** none. For `framework: static` no build step runs; the **repo root is the published
  directory**. There is no `public/`, `dist/` or `out/`. `npm run build` is a deliberate no-op.
- **What ships:** everything tracked in the repo, including `*.md`, `plans/` and `docs/`. Nothing
  is excluded — assume any committed file is publicly fetchable under `/d13-app/...`.
- **Logs:** App → Environment → Deployment ID (commit SHA) in the Webflow dashboard. Runtime
  logs exist but a static app has no server runtime to log.
- **Rollback is git-only.** Revert the commit on `main` and push; there is no "redeploy a
  previous build" button, and previous deployments cannot be previewed.
- **Mount path can be changed** after the fact (environment → ⋯ → Edit), but the pages hardcode
  it — re-stamp and redeploy (§3.2).

Platform limits that matter here: 100 MB compressed build output (repo is ~23 MB), 20 MB per
static file, 10 environments per app. Nothing is close.

## 3. The two structural constraints

Both are consequences of `static` on Webflow Cloud, both are load-bearing, and neither is
obvious from the code.

### 3.1 No `index.html`, anywhere

Two layers of Webflow's stack disagree about trailing slashes:

```
Webflow Cloud worker (wf-app-prod.cosmic.webflow.services)
  /x.html                          307 -> /x      strip the extension
  /x   where x/index.html exists   307 -> /x/     canonicalise toward a directory
  /x   where x.html exists                        serve it
Webflow site edge (x-wf-region)
  /x/                              301 -> /x      strip the trailing slash
```

Any directory holding an `index.html` therefore loops: `/x → /x/ → /x → …`, surfacing as
`ERR_TOO_MANY_REDIRECTS`. A page **not** named `index.html` is exempt.

So every `index.html` was renamed up a level and took its directory's name: `arcade/index.html`
became `arcade.html`, still serving at `/d13-app/arcade`, with its assets still in `arcade/`
(commit `2262bb5`). **Adding an `index.html` back re-breaks the site.**

The app root `/d13-app` cannot be fixed this way — it maps to the app's own root directory, so
it either 404s (no index) or loops (with one). Entry is `/d13-app/home`.

`tools/serve-like-webflow.py` models both layers and `--audit` walks every page reporting
cycles. It reproduced all 8 live loops before the rename and reports none after.

### 3.2 Every page needs a generated `<base href>`

Webflow Cloud does not rewrite paths for static apps — their docs: *"It doesn't rewrite HTML,
CSS, or JavaScript paths"*, and *"Absolute asset paths can break under mount paths."* Nothing
injects a base URL or asset prefix the way it does for Next.js or Astro.

Under a slash-less mount the browser treats the last segment as a file, so a bare
`href="app.js"` on `/d13-app/arcade` resolves to `/app.js` — the Webflow marketing site, 404.
A `<base>` tag pins the directory and fixes every relative `href`, `src`, CSS `url()` and
`fetch()` in one line per page.

```bash
tools/set-base.sh /d13-app     # stamp every tracked .html (idempotent)
python3 tools/check-links.py   # every relative ref resolves to a real file
python3 tools/serve-like-webflow.py --audit    # no redirect loops
```

The stamps are generated, never hand-edited. The script derives each page's base from its own
location: `<x>.html` beside a directory `<x>/` gets `$MOUNT/<x>/`. A page with no `<head>` is
skipped and will not resolve assets. Verify without changing anything by re-running and letting
git answer: `tools/set-base.sh /d13-app && git diff --exit-code -- '*.html'`.

This hardcodes the mount path in 14 places, which is why a mount change is a re-stamp
(`b223fb2`, `d034e26`).

## 4. Known rough edges

- **`/d13-app` 404s.** No page links to `home` except `card-prompt-builder.html`, so there is no
  site-wide nav to soften it. A site-level redirect `/d13-app → /d13-app/home` in Site Settings →
  Publishing → Redirects is untested and worth one attempt.
- **`.html` links cost a redirect.** `href="card-prompt-builder.html"` works but eats a 307 that
  strips the extension and changes the URL under the user. Query strings survive the strip.
- **`hello-waves/micro.html`** has no `<head>`, so it is unstamped; nothing links it. Delete it
  or give it a `<head>`.
- **Everything in the repo is published**, `CLAUDE.md` and `plans/` included.

## 5. Open work

### 5.1 Unverified from the origin change

Never tested since the move off GitHub Pages. These are the only plausible functional
regressions — a different origin, same code:

- [ ] Apps Script endpoints from `www.nycfirst.org`: stem-stations submit (`SUBMIT_URL` in
      `stem-stations.html`), arcade submit (`arcade/submit.html`), laser-maker Drive upload
      (`laser-maker/docs/apps-script-uploader.js`). One real submission each.
- [ ] Third-party embeds from the new origin: MakeCode iframes (`arcade/games.html`), Google
      Sheets gviz CSV fetches (arcade + stem-stations).
- [ ] `localStorage`/IndexedDB does not travel between origins. Anyone with unsaved Laser Maker
      work on the old host cannot reach it from the new one — tell users to export first.

### 5.2 Live Sheet still carries an old URL

`stem-stations/stations.csv` was fixed, but it is only the offline fallback. The published
Google Sheet almost certainly has the same `nycfirst-d13.github.io/hello-waves` row and needs
the same edit by hand.

## 6. Next: `d13.nycfirst.org`

Goal: serve the app at a subdomain instead of a path under the marketing apex. Three routes,
in the order they should be attempted.

**Constraint from the org side:** the apex `nycfirst.org` is on GoDaddy DNS and should stay
there. Proxying only the subdomain through Cloudflare is not cheap: Cloudflare's docs say
*"Subdomain setup is only available for Enterprise accounts"* (delegating `d13.nycfirst.org` to
Cloudflare via NS records), and a partial/CNAME setup is *"only available to customers on a
Business or Enterprise plan"*. The free path means moving the entire apex zone to Cloudflare
nameservers — off the table.

### A. Webflow Cloud standalone app — ask first

Webflow Cloud now offers a second deploy target: *"choose **Existing site** to attach the app to
a Webflow site (mounted at a path like `/app`), or **New domain** to deploy as a standalone app
hosted on its own subdomain."* That removes the mount path entirely — re-stamp with
`tools/set-base.sh /` and §3.2 shrinks to nothing.

**Unconfirmed:** the announcement names Next.js and Astro; nothing in the docs says whether a
`static` app is eligible. One support ticket settles it, and should also carry the question open
since the start of this migration: **is a `/` mount path permitted on a site-attached app?**

- [ ] Ask Webflow support both questions.

### B. Separate Webflow site on the subdomain

A second Webflow site with the app mounted at its root. DNS is the standard Webflow subdomain
flow at GoDaddy: `CNAME d13 → proxy-ssl.webflow.com` plus a one-time TXT verification record.
No proxy, no Cloudflare, nothing extra to own. Costs another site + hosting plan, and still
depends on a `/` mount being permitted.

### C. Reverse proxy at the subdomain

Since Cloudflare's subdomain-only options are Business+, the same shape is free from any host
that needs only a CNAME — e.g. a one-file Vercel or Netlify project on `d13.nycfirst.org`
rewriting `/*` → `https://www.nycfirst.org/d13-app/*`. GoDaddy keeps the zone; one record; TLS
automatic.

Worth knowing before building it: **if the proxy adds the `/d13-app` prefix itself, re-stamp the
pages with `tools/set-base.sh /`** — `<base href="/">` plus the proxy's prefix resolves
correctly, and no response-body rewriting is needed. The tradeoff is that direct
`www.nycfirst.org/d13-app/...` access then breaks, so this is a cutover, not dual-serve.

**Sequencing:** A's answer decides everything. If `static` is eligible for a standalone domain,
take it — one form and a re-stamp. If not, B (money, zero moving parts) vs C (free, one more
service to own). Do not build C before asking.

### Also open

- [ ] Redirect `/d13-app` → the subdomain once it lands, so shared links keep working.

---

## Appendix — how this shape was arrived at

Condensed from the original 834-line investigation log (2026-09-11). Kept because each decision
looks arbitrary without it.

- **Phase 0–1.** Plan was: add `webflow.json`, create the app on `main` at mount `d13-app`. App
  creation failed with *"No package.json found"* — the create flow requires one even for a
  static app. A minimal no-dependency `package.json` was added (`9532140`); it exists only for
  that reason and still has no dependencies.
- **Three silent failures.** Creation then failed with no error at mount paths `d13-app` (twice,
  before and after deleting the empty Designer page that shadowed the slug) and `d13app`. It
  succeeded at `d13-avi`. The colliding published page was the likely cause of at least the
  first.
- **The abandoned Next.js wrapper.** Read as evidence that `framework: static` was reserved and
  unimplemented, a full Next.js wrapper was specced on a `d13-app` branch. It was never built:
  the `d13-avi` deploy proved `static` works — it builds, deploys and serves. The `d13-app`
  branch on both remotes is that dead plan and can be deleted. Astro remains the fallback if
  `static` is ever withdrawn.
- **`<base href>` over everything else.** The original plan preferred jumping straight to a
  subdomain over stamping base tags, on the theory that a subdomain root has no base-URL problem.
  That is wrong: it disappears only for the *root page*; at `d13.nycfirst.org/arcade` a bare
  `src="app.js"` still resolves to `/app.js`. The subdomain shrinks the problem, it does not
  remove it — so the stamp is needed either way, and `set-base.sh` makes a mount change cheap.
- **`d13-avi` → `d13-app`.** The app was moved to its intended mount path; the org deploy served
  unstyled HTML until the stamps were re-run (`d034e26`). Any mount change is a re-stamp.
- **Two dead ends worth not repeating.** The Webflow MCP server exposes no Cloud app,
  environment or deployment surface — the dashboard is the only control plane. Webflow's
  site-wide password protection does not cover Cloud apps.
