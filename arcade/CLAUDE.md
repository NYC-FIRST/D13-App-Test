# arcade/CLAUDE.md

NYC FIRST District 13 arcade — 8-bit virtual arcade for student MakeCode Arcade games.

**Design spec:** `../docs/superpowers/specs/2026-06-24-game-gallery-design.md` (reference only; the Next.js stack it describes was replaced — see below).

## Stack

Plain static HTML/CSS/JS. **No build step, no framework, no node_modules.** Files are served as-is by Webflow Cloud at `/d13-app/arcade`. Edit and commit directly.

The grid page is `arcade.html`, here in this directory alongside its assets. It serves at the short URL `/d13-app/arcade` (a `_redirects` 200 proxy, no redirect) and also at `/d13-app/arcade/arcade`. See the root `CLAUDE.md` for why it is not named `index.html`.

| File | Role |
|------|------|
| `arcade.html` | Grid page — fetches CSV, renders cards, loading/error/empty states, XP footer |
| `games.html` | Detail page — reads `?id=`, iframes the game, shows provenance |
| `app.js` | Shared data layer — CSV fetch/parse, sort-newest, `findGame`, thumbnail URLs |
| `style.css` | 8-bit arcade theme, minimal black & white (Press Start 2P + VT323, Google Fonts) |
| `kiosk.js` | Always-on arcade navigation + full-screen play (mouse/keyboard/Makey Makey/gamepad). See `KIOSK.md` |
| `help.js` | Help button + popover (controls, navigation, view-code, learn), injected into the header on both pages |
| `dev-games.csv` | Committed fixture of real public MakeCode games (made-up student names) |

> History: previously a Next.js static-export app in `game-gallery-src/`. Dropped — a static CSV-driven gallery didn't need React or a build pipeline. Source is still in git history (commit `12e9ea8`) if ever needed.

## Styling

**Prioritize high visual clarity for children (elementary–middle school).** This
is an arcade used by kids, often from a distance at a shared station. When adding
or changing UI:

- **Big, legible text and icons.** Bump size before adding cleverness. Interactive
  glyphs (arrows, ↗, ⛶) use `.ico` so they render oversized next to their label.
- **Icon + label centered on one line** (`display: inline-flex; align-items:
  center; gap`) — never a tiny icon crammed against text.
- **Generous tap targets** — buttons/chips are `min-height: 44px+` with roomy
  padding.
- **High contrast, minimal clutter** — the black & white arcade theme; red
  (`--accent`) only for emphasis. Few words, plain language.
- Shared button styles: `.btn` (bordered, on the game page) and `.chip` (solid,
  in headers/overlays). Reuse them instead of one-off styles.

## Data Source

`CSV_URL` at the top of `app.js` picks the data source. Defaults to the local `dev-games.csv` fixture. To go live, set it to the published "Approved" Google Sheet CSV:

```
https://docs.google.com/spreadsheets/d/<id>/pub?gid=<n>&single=true&output=csv
```

Sheet columns (Approved tab): `id`, `game_title`, `student_name`, `grade`, `student_url`, `d13_url`, `submitted_at`, `session`

- `d13_url` — D13 Cloud MakeCode share URL, used for the iframe
- `student_url` — original student submission URL, shown on the game page as provenance

New approved rows go live on refresh — no rebuild, no redeploy.

## Routes

- `/d13-app/arcade` → `arcade.html` — game grid
- `/d13-app/arcade/games?id=<slug>` → `games.html` — single game; reads `?id=`, iframes `d13_url`. A link written as `games.html?id=…` works but eats a 307 that strips the `.html`.

## Testing

`app.js` has a built-in parser self-check (quoted-comma fields, newest-first sort, case-insensitive lookup). Run it by loading any page with `?selftest=1` and watching the console, or in node.

## Git & Commits

Repo root is the parent directory — `arcade/` is a plain subdir, not a separate repo. Always commit from the parent. Scope each commit to one app + one logical change; stage `arcade/` paths only, never bare `git add .`:

```bash
git -C /Users/avigoldman/dev/d13 add arcade/<path>
git -C /Users/avigoldman/dev/d13 commit -m "feat(arcade): ..."
```

Conventional prefix scoped to the area. Run `git status` to verify staging before committing. Don't ask permission to commit from the parent.
