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

- **URLs are the content.** They are displayed for people typing them, so they never wrap
  mid-word: the host sits on its own line (`.host`) and the path stays `white-space: nowrap`.
  Adding an app means keeping that intact — check the longest slug still fits its card.
- Apps listed are a curated subset for the session, not every child directory.
  Currently: `laser-maker`, `stem-stations`, `arcade`.

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
