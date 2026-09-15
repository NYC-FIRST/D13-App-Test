# hello-waves/CLAUDE.md

Hello waves app — a child app of the NYC FIRST D13 site, served by Webflow Cloud at `/d13-app/hello-waves`.

The page is `hello-waves.html`, here alongside its images. See the root `CLAUDE.md` for the layout rule and the `<base href>` contract.

`micro.html` is an unused embed snippet (a bare MakeCode iframe, no `<head>`). Nothing links it and `set-base.sh` skips it. Delete it or give it a `<head>` if it is ever wanted as a real page.

## Git & Commits

Repo root is the parent directory — `hello-waves/` is a plain subdir, not a separate repo. Always commit from the parent. Scope each commit to one app + one logical change; stage `hello-waves/` paths only, never bare `git add .`:

```bash
git -C /Users/avigoldman/dev/d13 add hello-waves/<path>
git -C /Users/avigoldman/dev/d13 commit -m "feat(hello-waves): ..."
```

Conventional prefix scoped to the area. Run `git status` to verify staging before committing. Don't ask permission to commit from the parent.
