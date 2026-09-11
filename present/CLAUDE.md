# present/CLAUDE.md

PD landing page — **"Play With D13's Homegrown Apps: Purpose-Built Tools for STEM Classrooms."**
Served at `/present/`. One screen, projector-first: title, a row of app URLs big enough for
the room to type by hand, and a feedback form URL + QR.

## Stack

Single `index.html`. No build step, no JS. Inherits the site theme from `../styles.css`
(Inter, blue gradient, `--primary-dark` etc.); page-specific rules live in an inline
`<style>` scoped to `#present-page`.

| File | Role |
|------|------|
| `index.html` | The whole page |
| `feedback-qr.svg` | QR for the feedback short URL. Generated, not hand-edited — see below |

## Rules

- **The split is spatial, so the design is.** *Front of the classroom* sits open and light on
  the page gradient; *back of the classroom* is a solid dark panel (`--back-bg`) — literally
  behind the scenes. That contrast is the whole idea; don't flatten the two into matching cards.
  Front = student blue (`--front`), back = workshop amber (`--amber`). Cool is kids, warm is machines.
- **The base URL is said once.** `nycfirst-d13.github.io/` lives in the `.base` line above the
  columns, so each app row is only its slug. Never reintroduce the full host per row — repeating
  it five times is what made the earlier version feel cluttered.
- **The slug is the app's name.** No separate name line: `/bed-maker` plus one plain sentence
  about what it does. Two lines per app, no more.
- Sections: front = `laser-maker`, `stem-stations`, `arcade` (students open these themselves);
  back = `bed-maker`, `bird-bingo` (teacher utilities). `hello-waves` and
  `card-prompt-builder.html` are deliberately absent.
- **It has to fit one screen at 1440x900** — no scrolling on a projector, and the QR must never
  be below the fold. Adding a row means taking the height back out of the spacing.
- Type: Inter (from `../styles.css`) for prose, JetBrains Mono for URLs only. The mono is
  functional, not decorative — a room full of people typing needs unambiguous `l`, `1`, `0`.

## Regenerating the QR

The QR encodes the feedback short URL verbatim. If that URL changes, update **both** the
`<a class="url">` href and its text in `index.html`, then regenerate:

```bash
python3 -m venv /tmp/qrvenv && /tmp/qrvenv/bin/pip install -q segno
/tmp/qrvenv/bin/python -c "import segno; segno.make('https://NEW-URL', error='h').save('present/feedback-qr.svg', scale=10, border=2, dark='#1d4ed8', light='#ffffff')"
```

Error correction is `H` so the code still scans from across a room or off a projector.

## Git & Commits

The git repo is the **parent directory**. Always commit from there:

```bash
git -C /Users/avigoldman/nycfirst-d13.github.io add present/
git -C /Users/avigoldman/nycfirst-d13.github.io commit -m "feat(present): ..."
```

Scope each commit to this directory only — never a bare `git add .` that sweeps in other apps.
