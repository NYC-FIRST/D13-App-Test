# stem-stations/CLAUDE.md

STEM stations landing page — a child page of the NYC FIRST D13 site, served by Webflow Cloud at `/d13-app/stem-stations`.

The page is `stem-stations.html`, here alongside its data and images. See the root `CLAUDE.md` for the layout rule and the `<base href>` contract.

Data-driven: `stem-stations.html` fetches a published Google Sheet (CSV via the gviz endpoint) on load and renders cards from it; `stations.csv` is a baked snapshot used only as a fallback when the live fetch fails (offline / CORS / `file://`). Sheet: https://docs.google.com/spreadsheets/d/1xclY-0sWt70mZ_jQxMDWOr8XtwgaZivqhDlD2_hnBs0/edit

Sheet columns: `title, description, url, tags, difficulty, active, screenshot`. `tags` and `difficulty` are comma-separated multi-values. `active` must be `TRUE` to show. Blank `url` → card renders non-clickable. `screenshot` → hover preview (bare filename resolves under `images/`, or a full `http(s)` URL). Rows deduped by `title`, last row wins.

Two view modes (segmented toggle): "Browse by section" (one section per tag, cards repeat across their tags) and "Filter by tag" (single grid + toggleable tag chips, OR filter). No card icons in this version.

## Community submission form

Floating gradient "+" button (bottom-right) opens a popover form so students/interns/teachers can suggest stations. Submissions POST to a **Google Apps Script Web App** (`submit.gs`, deployed off the same Sheet) which appends a row with `active=FALSE` and emails staff. Wire it up by pasting the deployed `/exec` URL into `SUBMIT_URL` in `stem-stations.html`.

`submit.gs` in this repo is the **canonical copy-paste source** — it holds the real CONFIG values (including `DRIVE_FOLDER_ID`). It is NOT auto-deployed: after editing it here, paste the full contents into the Apps Script editor (Sheet → Extensions → Apps Script) and **Deploy → Manage deployments → new version** for changes to go live. Editing the repo file alone changes nothing on Google's side. The web app runs "Execute as" the shared automation account **`d13-internal@nycfirst.org`** (the account that runs all D13 internal automation — a Workspace account, not a GCP service account), so `MailApp` sends from `d13-internal@` to `STAFF_EMAIL` (`sc-d13-accounts@nycfirst.org`), and `d13-internal@` must own or have Editor access to the Drive folder. Custom "add your own" tags are free text — they render on the site immediately; to also appear as a Sheet dropdown-chip option, add them to the Sheet's data-validation list. Screenshots must be a URL in the `screenshot` column (uploads go to Drive via `submit.gs`); in-cell pasted images don't survive CSV export and won't show.

## Git & Commits

Repo root is the parent directory — `stem-stations/` is a plain subdir, not a separate repo. Always commit from the parent. Scope each commit to one app + one logical change; stage `stem-stations/` paths only, never bare `git add .`:

```bash
git -C /Users/avigoldman/dev/d13 add stem-stations/<path>
git -C /Users/avigoldman/dev/d13 commit -m "feat(stem-stations): ..."
```

Conventional prefix scoped to the area. Run `git status` to verify staging before committing. Don't ask permission to commit from the parent.
