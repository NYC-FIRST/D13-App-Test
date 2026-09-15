# NYC FIRST District 13 — STEM Center site

Browser tools and activities built for the students and staff of the NYC FIRST District 13 STEM center. Everything here is plain HTML, CSS and JavaScript — no build step, no framework, no dependencies.

**Live:** [www.nycfirst.org/d13-app](https://www.nycfirst.org/d13-app)

## What's here

| App | URL | What it does |
|-----|-----|--------------|
| **Start** | [/d13-app](https://www.nycfirst.org/d13-app) | Onboarding page — how to make your STEM card and sign in to the space |
| **Card Prompt Builder** | [/d13-app/card-prompt-builder](https://www.nycfirst.org/d13-app/card-prompt-builder) | Helps students write a good image prompt for their STEM card art |
| **Laser Maker** | [/d13-app/laser-maker](https://www.nycfirst.org/d13-app/laser-maker) | Vector design tool for the Epilog Fusion Edge 36 laser cutter. An Illustrator-shaped interface cut down to what a student needs: draw, assign process types, export clean SVG |
| **Bed Maker** | [/d13-app/bed-maker](https://www.nycfirst.org/d13-app/bed-maker) | Teacher tool — merges a day's Laser Maker exports onto one 36×24 bed so a whole class cuts in a single job |
| **D13 Arcade** | [/d13-app/arcade](https://www.nycfirst.org/d13-app/arcade) | 8-bit arcade for student-made MakeCode games, with a submission form and a kiosk mode for the shared station |
| **STEM Stations** | [/d13-app/stem-stations](https://www.nycfirst.org/d13-app/stem-stations) | Browsable directory of STEM activities, driven by a Google Sheet |
| **Bird Bingo** | [/d13-app/bird-bingo](https://www.nycfirst.org/d13-app/bird-bingo) | Bird identification bingo |
| **Hello Waves** | [/d13-app/hello-waves](https://www.nycfirst.org/d13-app/hello-waves) | Sound and waves activities for the micro:bit |

## Layout

Each app is one self-contained directory holding its page and every asset that page uses. The page is named after its directory:

```
arcade/
  arcade.html      ← the page, served at /d13-app/arcade
  app.js  style.css  games.html  submit.html  dev-games.csv
```

The repo root holds only site-level pages (`start.html`, `card-prompt-builder.html`) and shared assets.

Two generated things you should never edit by hand — both are rewritten by `tools/set-base.sh`:

- the `<base href>` tag on line 4 of every page, which makes relative paths resolve under the deployment's mount path
- `_redirects`, which maps each short URL (`/d13-app/arcade`) to its page with no redirect

## Working on it

```bash
npm run serve     # http://127.0.0.1:8787/d13-app — mirrors the live redirect behavior
npm run check     # every relative reference resolves to a real file
```

Use `npm run serve` rather than any other static server: the deployment does things to URLs (strips `.html`, strips trailing slashes) that a plain server does not, and this one reproduces them.

After adding or moving any page:

```bash
tools/set-base.sh /d13-app
python3 tools/check-links.py
python3 tools/serve-like-webflow.py --audit
```

**Adding a page or app?** Read [`CLAUDE.md`](CLAUDE.md) → *Creating a New Page or App*. It's written for AI coding agents but the rules are the same for people, and a couple of them are not guessable — most importantly, **never name a file `index.html`**; it will hang in a redirect loop on the live site.

## Contributing

The repo is owned by the [NYC-FIRST](https://github.com/NYC-FIRST) org, and commits keep their individual authors.

- **Org members:** branch in `NYC-FIRST/d13`, open a PR into `main`.
- **Everyone else:** fork, branch, open a PR into `NYC-FIRST/d13`. No org seat needed.

Scope each commit to one app plus one logical change, with a conventional prefix — `feat(arcade): …`, `fix(laser-maker): …`.

## Deployment

Pushing to `main` on `NYC-FIRST/d13` deploys automatically via Webflow Cloud. There is no build — the repo root is published as-is. Rolling back means reverting the commit and pushing.

[`Webflow-plan.md`](Webflow-plan.md) documents how the deployment works, the two structural constraints it imposes, and what's still open (notably moving the site to a `d13.nycfirst.org` subdomain).

*Previously hosted on GitHub Pages at `nycfirst-d13.github.io`; retired September 2026.*
