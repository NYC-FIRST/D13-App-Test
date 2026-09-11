# present/CLAUDE.md

PD landing page — **"Play with some of SC @ D13's Homegrown Apps."**
Served at `/present/`. One screen, projector-first: title, a row of app URLs big enough for
the room to type by hand, and a feedback form URL + QR.

## Stack

Single `index.html`. No build step; the only JS is the few lines at the end that measure the
URLs for the type-in animation. **Self-contained — it deliberately does not load
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
- Type: **Geist** (300-700) and **Geist Mono** (400-600), Google Fonts. Mono is for URLs only.
- Rules are **1.5px** `#CDDAEE`, never 1px. Radii 6/8/10/14px — small, never pills.
- Ink `#0F1117` / `#3A3D45` / `#6B6F7A`, blue `#2563EB`, blue-soft `#DCE8FC`,
  red accent `#E0241B` (the short rule under the hero).

## Rules

- **`nycfirst-d13.github.io/present` is the largest thing on the page**, above the red rule. It is
  this page's own address, so the room can pull it up. Nothing labels or explains it, and it must
  stay on one line — if the path grows, lower the clamp.
- **Every URL splits host from path the same way:** host in ink, path in `--blue` via `.seg`.
  The hero and all three cards follow it, so the pattern reads as one system.
- **Cards carry the full URL, not a bare slug.** A slug alone next to a hero ending in `/present`
  read as `/present/laser-maker`, which does not exist. Keep the host on every card.
- **The h1 stays on one line at full width.** If the copy grows, shrink the clamp, don't let it wrap.
- **No section headings.** The app list carries no title; the cards speak for themselves.
- App cards are the `blue-soft` tinted group, the way the deck tints the cards that matter.
- Three apps only: `laser-maker`, `stem-stations`, `arcade`. `bed-maker`, `bird-bingo`,
  `hello-waves` and `card-prompt-builder.html` are deliberately absent — the front/back-of-
  classroom split was tried and dropped.
- **Feedback floats to the right of the app list** and the whole block is one link to the form.
  `.rooms` is `minmax(0, 1fr) 380px`; it goes single-column at **900px**, not 760 — below that the
  fixed right column squeezes the left one until the full URLs overflow their chips.
- **Feedback is not a card** — no fill, border or shadow. Blue type and a bare QR, centre-aligned
  and `align-self: center` so it floats level with the middle of the app stack. It is sized for a
  room, not a desk: QR up to 260px, short URL at 31px. Its block height (~404px) is deliberately
  just under the app stack's (~417px) — grow it further and it starts driving the page past one screen.
- **The QR is transparent with blue modules, and it must keep `border=4`.** That is the quiet
  zone; without it the code does not reliably scan. The dot grid showing through is fine —
  verified by decoding the rendered pixels at both 260px and 150px. **Re-verify after any change
  to the QR's colour, size or background** (see below).
- **Spacing is a 4px scale: 4 / 12 / 16 / 24 / 32.** Inside a card 4 (name to description)
  and 12 (description to URL); between cards 12. Group separation always reads as double the
  item separation. No off-scale one-off values.
- **Cards keep their natural height** — all three are the same box. Stretching cards to fill a
  column was tried and made them 194px against 126px for identical content. Don't.
- **It has to fit one screen at 1440x900** — no scrolling on a projector, and the QR must never
  be below the fold. Adding a row means taking the height back out of the spacing.

## Motion

One orchestrated page-load pass, nothing on scroll and nothing on hover. Easing is the deck's
own `--ease-expo`; the shape is its `translateY` fade-up.

- Blocks ease up in reading order via `.reveal` with an inline `--d` delay: masthead 0-.30s,
  cards .46/.59/.72s, feedback .90s.
- Every URL then types itself in like an address bar, each starting .26s after its own block
  lands. A blinking caret runs for the duration and ends transparent.
- **The type-in animates `width` with `steps()`, deliberately.** Rewriting the text
  character-by-character would destroy the host/path two-tone colouring; animating the width of
  an `overflow: hidden` box leaves the markup untouched.
- **The pixel target has to be measured, not computed.** `ch` units ignore `letter-spacing` and a
  percentage resolves against the containing block, so both leave a trailing gap inside the chip.
  The script measures each URL's natural width after `document.fonts.ready` — measuring earlier
  gets the fallback font's metrics.
- The hero URL is skipped below 900px, where it is allowed to wrap and a `nowrap` type-in
  would clip it.
- `prefers-reduced-motion` is honoured in both places: the CSS drops the animations and the
  script returns before arming anything. Verified — every URL renders full width, opacity 1.

## Regenerating the QR

The QR encodes the feedback short URL verbatim. If that URL changes, update **both** the
`.fb` anchor's href and its `.slug` text in `index.html`, then regenerate:

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
