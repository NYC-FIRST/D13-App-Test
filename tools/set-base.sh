#!/usr/bin/env bash
# Stamp a <base href> into every HTML page so bare-relative references resolve
# correctly no matter where the site is mounted.
#
# Why this exists
# ---------------
# GitHub Pages redirects /arcade  -> /arcade/   (adds a trailing slash)
# Webflow Cloud    redirects /arcade/ -> /arcade   (strips it)
#
# Under the strip convention the browser treats the last path segment as a
# FILE, so a bare href="app.js" on /arcade resolves to /app.js instead of
# /arcade/app.js. A <base> tag pins the directory explicitly and fixes every
# relative href, src, CSS url() and fetch() in one line per page.
#
# Usage
#   tools/set-base.sh /d13-app    # mounted at nycfirst.org/d13-app
#   tools/set-base.sh /           # mounted at a domain/subdomain root
#
# To verify rather than change, re-run and let git answer — the script is
# idempotent, so a clean diff means every stamp is already correct:
#   tools/set-base.sh /d13-app && git diff --exit-code -- '*.html'
#
# Idempotent: re-running replaces the existing tag rather than adding another.

set -euo pipefail
cd "$(dirname "$0")/.."

MOUNT="${1:-}"
if [ -z "$MOUNT" ] || [ "${MOUNT#-}" != "$MOUNT" ]; then
  # A leading dash is a flag, not a mount path. Without this guard a stray
  # --check would be stamped verbatim as <base href="/--check/">.
  echo "usage: tools/set-base.sh <mount-path>   e.g. /d13-app  or  /" >&2
  exit 2
fi

# Normalise: leading slash, no trailing slash. "/" becomes "".
[ "${MOUNT#/}" = "$MOUNT" ] && MOUNT="/$MOUNT"
MOUNT="${MOUNT%/}"

changed=0
skipped=0

while IFS= read -r f; do
  # A page needs a <head> to hold the tag. Fragments (no <head>) are skipped;
  # they are included by a parent document and inherit its base.
  if ! grep -qi '<head>' "$f"; then
    printf '  skip   %-36s (no <head>)\n' "$f"
    skipped=$((skipped + 1))
    continue
  fi

  dir="$(dirname "$f")"
  stem="$(basename "$f" .html)"

  # A page named <x>.html that sits beside a directory <x>/ owns that
  # directory's assets, so its base is the directory - not its own location.
  # This is the shape that avoids Webflow Cloud's directory-index redirect
  # loop: arcade.html serves at /arcade and its assets live in /arcade/.
  if [ "$dir" = "." ]; then
    if [ -d "$stem" ]; then base="$MOUNT/$stem/"; else base="$MOUNT/"; fi
  elif [ -d "$dir/$stem" ]; then
    base="$MOUNT/$dir/$stem/"
  else
    base="$MOUNT/$dir/"
  fi

  tag="<base href=\"$base\">"

  # Drop any previous stamp, then insert directly after <head>.
  perl -0pi -e 's{\n[ \t]*<base [^>]*>(?:[ \t]*<!-- set-base\.sh -->)?}{}g' "$f"
  perl -0pi -e "s{(<head>)}{\$1\n  $tag <!-- set-base.sh -->}i" "$f"

  printf '  base   %-36s %s\n' "$f" "$base"
  changed=$((changed + 1))
done < <(git ls-files '*.html')

echo
echo "stamped $changed file(s), skipped $skipped."
