# present/CLAUDE.md

PD landing page — **"Play With D13's Homegrown Apps: Purpose-Built Tools for STEM Classrooms."**
Served at `/present/`. One screen, projector-first: title, a row of app URLs big enough for
the room to type by hand, and a feedback form URL + QR.

## Stack

Single `index.html`. No build step, no JS. **Self-contained — it deliberately does not load
`../styles.css`**; that sheet's Inter + blue gradient fights the look below.

| File | Role |
|------|------|
| `index.html` | The whole page |
| `feedback-qr.svg` | QR for the feedback short URL. Generated, not hand-edited — see below |

## Design system

Lifted wholesale from `../laser-maker/docs/slides-drive-v1.html` and
`../laser-maker/docs/drive-cloud-saving.html`. **Do not invent colours for this page** — if
something needs a new value, take it from those two files.

- Paper `#E8EFF8` under a blue dot grid (`rgba(37,99,235,.09)` 1px dots at `34px`).
- Type: **Geist** (300-700) and **Geist Mono** (400-600), Google Fonts. Mono is for URLs and
  eyebrows only.
- Rules are **1.5px** `#CDDAEE`, never 1px. Radii 6/8/10/14px — small, never pills.
- Ink `#0F1117` / `#3A3D45` / `#6B6F7A`, blue `#2563EB`, blue-soft `#DCE8FC`,
  red accent `#E0241B` (the short rule under the hero).
- Mono uppercase letter-spaced blue eyebrows above each block — that's the house style here,
  not a generic label.

## Rules

- **`nycfirst-d13.github.io/` is the largest thing on the page** (~75px, above the red rule) and
  is said exactly once. Each app row is only its slug — never reintroduce the full host per row.
  Nothing labels or explains the host; it speaks for itself.
- **The h1 stays on one line at full width.** If the copy grows, shrink the clamp, don't let it wrap.
- Section headings are the eyebrow alone. No explanatory line underneath.
- **Front of the classroom is the tinted group** (`blue-soft` cards, blue names), back is plain
  white — the same way the deck tints the card that matters. That tint is the front/back
  division; don't add a second device on top of it.
- Sections: front = `laser-maker`, `stem-stations`, `arcade` (students open these themselves);
  back = `bed-maker`, `bird-bingo` (teacher utilities). `hello-waves` and
  `card-prompt-builder.html` are deliberately absent.
- **The feedback card is the last row of the back column**, and the whole card is one link to the
  form. It keeps the solid `--blue` so it reads as not-an-app despite sitting in that column.
- **The feedback card's height must come from its text, never from its QR.** It carries the same
  `name` / `what` / `slug` stack as every app card, and the QR is `position: absolute` pinned
  `top/right/bottom` with `aspect-ratio: 1`, so it sizes itself from the card rather than setting
  it. Card heights are `clamp()`-driven and scale with viewport width; a fixed-px QR matches at
  exactly one window size and drifts everywhere else (it was 32px too tall at 800px wide).
  `.copy` must stay `display: block` — it is a `<span>`, and its `padding-right` that keeps text
  clear of the QR does nothing while it is inline.
- **Spacing is a 4px scale: 4 / 12 / 16 / 24 / 32.** Inside a card 4 (name to description)
  and 12 (description to URL); between cards 12; heading to its first card 24, so group
  separation always reads as double the item separation. No off-scale one-off values.
- **Cards keep their natural height** — all five are the same box. Don't stretch the shorter
  back column to match the front; that was tried and it made back cards 194px against the
  front's 126px for identical content. The uneven column bottom is fine, the dot grid carries it.
- **It has to fit one screen at 1440x900** — no scrolling on a projector, and the QR must never
  be below the fold. Adding a row means taking the height back out of the spacing.

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
