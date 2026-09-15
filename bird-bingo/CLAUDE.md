# bird-bingo/CLAUDE.md

Bird bingo game — a child app of the NYC FIRST D13 site, served by Webflow Cloud at `/d13-app/bird-bingo`.

The page is `bird-bingo.html`, here alongside its images. See the root `CLAUDE.md` for the layout rule and the `<base href>` contract.

## Git & Commits

Repo root is the parent directory — `bird-bingo/` is a plain subdir, not a separate repo. Always commit from the parent. Scope each commit to one app + one logical change; stage `bird-bingo/` paths only, never bare `git add .`:

```bash
git -C /Users/avigoldman/dev/d13 add bird-bingo/<path>
git -C /Users/avigoldman/dev/d13 commit -m "feat(bird-bingo): ..."
```

Conventional prefix scoped to the area. Run `git status` to verify staging before committing. Don't ask permission to commit from the parent.
