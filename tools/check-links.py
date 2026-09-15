#!/usr/bin/env python3
"""Resolve every relative reference in the site's HTML/CSS the way a browser
would under Webflow Cloud's URL convention, and report any that miss a file.

Webflow Cloud (Cloudflare Workers Assets) serves `foo/index.html` at `/foo` and
301s `/foo/` back to `/foo`. Without a trailing slash the browser treats the
last path segment as a FILE, so bare-relative refs resolve one directory too
high. The <base> tag stamped by tools/set-base.sh corrects that; this proves it.

Usage:  tools/check-links.py
"""
import os, re, subprocess, sys
from urllib.parse import urljoin, urlparse, unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

def tracked(pat):
    return subprocess.run(["git", "ls-files", pat],
                          capture_output=True, text=True).stdout.split()

BASE_RE  = re.compile(r'<base\s+href="([^"]+)"', re.I)
# Skip <base> itself - its href is the resolution root, not a reference.
REF_RE   = re.compile(r'<(?!base\b)[^>]+?(?:href|src)\s*=\s*"([^"]*)"', re.I)
STYLE_RE = re.compile(r'<style\b[^>]*>(.*?)</style>', re.I | re.S)
CSSURL   = re.compile(r'url\(\s*["\']?(?!data:)([^"\')]+)["\']?\s*\)', re.I)
SKIP     = ("http://", "https://", "//", "data:", "mailto:", "tel:",
            "javascript:", "#", "blob:")

def main():
    html = tracked("*.html")
    # The mount prefix is whatever precedes the repo-relative dir in <base>.
    # It is the longest path prefix common to every stamped base - not the
    # shortest base, which is only the same thing while some page sits at the
    # mount root. Every page now lives in its own directory, so none does.
    bases = []
    for f in html:
        m = BASE_RE.search(open(f, encoding="utf-8", errors="replace").read())
        if m:
            bases.append(m.group(1))
    if not bases:
        print("no <base> tags found - run tools/set-base.sh first", file=sys.stderr)
        return 2
    common = os.path.commonprefix(bases)
    mount = common[:common.rfind("/")] if "/" in common else ""

    # Short URLs served by a _redirects 200 proxy, mount prefix stripped.
    short_urls = set()
    if os.path.isfile("_redirects"):
        for line in open("_redirects", encoding="utf-8"):
            parts = line.split("#")[0].split()
            if len(parts) >= 3 and parts[2] == "200" and parts[0].startswith(mount):
                short_urls.add(parts[0][len(mount):].rstrip("/") or "/")

    problems, checked, no_base = [], 0, []

    def check(origin, ref, kind, doc):
        nonlocal checked
        if not ref or ref.startswith(SKIP) or "${" in ref or "<" in ref:
            return
        resolved = urlparse(urljoin(doc, ref)).path
        if mount and not resolved.startswith(mount + "/"):
            problems.append((origin, ref, resolved, kind, "escapes the mount"))
            return
        rel = unquote(resolved[len(mount):].lstrip("/"))
        checked += 1
        # A short URL wired up by a _redirects 200 proxy resolves to whatever
        # that rule targets, not to a file of its own name.
        if "/" + rel.rstrip("/") in short_urls or (rel == "" and "/" in short_urls):
            return
        if rel == "" or rel.endswith("/"):
            rel += "index.html"
        # A bare /foo may be served by foo.html or foo/index.html.
        if (os.path.isfile(rel) or os.path.isfile(rel + ".html")
                or os.path.isfile(os.path.join(rel, "index.html"))):
            return
        problems.append((origin, ref, resolved, kind, "no file"))

    for f in html:
        src = open(f, encoding="utf-8", errors="replace").read()
        m = BASE_RE.search(src)
        if not m:
            no_base.append(f)
            continue
        doc = "https://x" + m.group(1)
        for ref in REF_RE.findall(src):
            check(f, ref, "href/src", doc)
        for block in STYLE_RE.findall(src):
            for ref in CSSURL.findall(block):
                check(f, ref, "inline css url()", doc)

    # External stylesheets resolve against their OWN location, not the page's.
    for f in tracked("*.css"):
        doc = "https://x" + mount + "/" + f
        for ref in CSSURL.findall(open(f, encoding="utf-8", errors="replace").read()):
            check(f, ref, "css url()", doc)

    print(f"mount prefix: {mount or '/'}")
    print(f"checked {checked} references across {len(html)} HTML + "
          f"{len(tracked('*.css'))} CSS files")
    if no_base:
        print(f"no <base> (fragments, inherit parent): {', '.join(no_base)}")
    print()
    if problems:
        print(f"UNRESOLVED ({len(problems)}):")
        for f, ref, resolved, kind, why in problems:
            print(f"  {f}\n      {kind}: {ref!r}\n      -> {resolved}  ({why})")
        return 1
    print("all relative references resolve to real files ✓")
    return 0

sys.exit(main())
