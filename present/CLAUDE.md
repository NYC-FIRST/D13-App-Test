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

- **`nycfirst-d13.github.io/present` is the largest thing on the page**, above the red rule, with
  `/present` in `--blue` to match the slug chips on the cards. It is this page's own address, so
  the room can pull it up; it is not a prefix for the slugs below, which hang off the site root.
  Nothing labels or explains it. It must stay on one line — if the path grows, lower the clamp.
- **The h1 stays on one line at full width.** If the copy grows, shrink the clamp, don't let it wrap.
- **No section headings.** The app list carries no title; the cards speak for themselves.
- App cards are the `blue-soft` tinted group, the way the deck tints the cards that matter.
- Three apps only: `laser-maker`, `stem-stations`, `arcade`. `bed-maker`, `bird-bingo`,
  `hello-waves` and `card-prompt-builder.html` are deliberately absent — the front/back-of-
  classroom split was tried and dropped.
- **The feedback card floats to the right of the app list** (`.rooms` is `1fr 380px`,
  `align-items: start`), and the whole card is one link to the form.
- **Feedback is not a card** — no fill, border or shadow. Blue type and a bare QR, centre-aligned
  and `align-self: center` so it floats level with the middle of the app stack.
- **The QR is transparent with blue modules, and it must keep `border=4`.** That is the quiet
  zone; without it the code does not reliably scan. The dot grid showing through is fine —
  verified by decoding the rendered pixels at both 180px and 120px. **Re-verify after any change
  to the QR's colour, size or background** (see below).
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
python3 -m venv /tmp/qrvenv && /tmp/qrvenv/bin/pip install -q segno opencv-python-headless
/tmp/qrvenv/bin/python -c "import segno; segno.make('https://NEW-URL', error='h').save('present/feedback-qr.svg', scale=10, border=4, dark='#2563EB', light=None)"
```

Error correction is `H` so the code still scans from across a room or off a projector, and
`border=4` is the quiet zone — do not drop it.

Then confirm it still decodes **as rendered**, dot grid and all, rather than trusting the file:

```bash
npx playwright-cli goto http://localhost:8777/present/
npx playwright-cli screenshot ".fb .qr" --filename=/tmp/qr.png
/tmp/qrvenv/bin/python -c "import cv2; print(cv2.QRCodeDetector().detectAndDecode(cv2.imread('/tmp/qr.png'))[0])"
```

## Git & Commits

The git repo is the **parent directory**. Always commit from there:

```bash
git -C /Users/avigoldman/nycfirst-d13.github.io add present/
git -C /Users/avigoldman/nycfirst-d13.github.io commit -m "feat(present): ..."
```

Scope each commit to this directory only — never a bare `git add .` that sweeps in other apps.
