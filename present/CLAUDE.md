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

- **URLs are the content.** Flat vertical stack, one app per row, rule between rows — no
  cards, no columns. The URL is the largest thing on the row; host is muted (`.host`), path
  is bold. Adding an app means checking the longest URL still sits on one line at 1440px.
- **Two sections, and the split is the point.** *Front of the classroom* = apps students
  open themselves (`laser-maker`, `stem-stations`, `arcade`). *Back of the classroom* =
  teacher utilities students never see (`bed-maker`, `bird-bingo`). The distinction is
  spelled out in a `.note` under each heading — keep it there, it's the takeaway.
- A curated subset, not every child directory. `hello-waves` and `card-prompt-builder.html`
  are deliberately absent.
- **It has to fit one screen at 1440×900** — no scrolling on a projector, and the QR must
  never be below the fold. Adding a row means taking the height back out of the spacing.

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
