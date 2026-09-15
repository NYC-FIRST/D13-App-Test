#!/usr/bin/env python3
"""Serve the repo the way Webflow Cloud actually behaves, including the
redirect loop, so breakage is reproducible locally.

Observed 2026-09-11 against www.nycfirst.org (mount /d13-avi at the time; the
app now mounts at /d13-app — the behavior is the same). TWO layers act:

  Webflow Cloud worker (wf-app-prod.cosmic.webflow.services)
    /x.html          307 -> /x           (strip the extension)
    /x  where x/index.html exists
                     307 -> /x/          (canonicalise toward a directory)
    /x  where x.html exists              serve it
  Webflow site edge (x-wf-region)
    /x/              301 -> /x           (strip the trailing slash)

Those two rules collide on any directory index: /x -> /x/ -> /x -> ... which
is the ERR_TOO_MANY_REDIRECTS users see. This server reproduces that, and
reports LOOP when a path cycles, so the fix can be verified before deploying.

Usage:  tools/serve-like-webflow.py [--mount /d13-app] [--port 8787] [--audit]
"""
import argparse, os, posixpath, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOUNT = "/d13-app"


def rules():
    """Parse _redirects into {source: (target, code)}, mount prefix stripped.

    Cloudflare applies these before asset routing, so a 200 rule serves the
    target's asset at the source URL with no redirect. Verified against the
    live site - see Webflow-plan.md.
    """
    out = {}
    path = os.path.join(ROOT, "_redirects")
    if not os.path.isfile(path):
        return out
    for line in open(path, encoding="utf-8"):
        line = line.split("#")[0].split()
        if len(line) < 2:
            continue
        src, dst = line[0], line[1]
        code = int(line[2]) if len(line) > 2 else 302
        if MOUNT:
            if not src.startswith(MOUNT):
                continue          # a bare source never matches under a mount
            src = src[len(MOUNT):] or "/"
            dst = dst[len(MOUNT):] if dst.startswith(MOUNT) else dst
        out[src.rstrip("/") or "/"] = (dst or "/", code)
    return out


def resolve(rel):
    """Return ('serve', diskpath) | ('redirect', code, newpath) | ('404', None)."""
    disk = posixpath.normpath(rel).lstrip("/")

    # _redirects runs first, before any asset routing.
    rule = rules().get(rel.rstrip("/") or "/")
    if rule:
        dst, code = rule
        if code != 200:
            return ("redirect", code, dst)
        # A 200 proxy serves the target's asset in place. The target must be
        # extensionless: a .html target picks up the extension-strip 307 below.
        return resolve(dst) if dst != rel else ("404", None)

    # Site edge: strip a trailing slash (never at the mount root).
    if rel.endswith("/") and rel != "/":
        return ("redirect", 301, rel.rstrip("/"))

    # Worker: strip a .html extension.
    if rel.endswith(".html"):
        base = rel[:-5]
        if base.endswith("/index"):
            base = base[: -len("index")] or "/"
        return ("redirect", 307, base)

    if rel == "/":
        disk = ""

    # Worker: a directory holding index.html canonicalises toward the slash.
    if os.path.isfile(os.path.join(ROOT, disk, "index.html")):
        return ("redirect", 307, "/" + disk + "/" if disk else "/")

    for cand in (disk, disk + ".html"):
        if cand and os.path.isfile(os.path.join(ROOT, cand)):
            return ("serve", cand)
    return ("404", None)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def do_GET(self, head=False):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        suffix = ("?" + parsed.query) if parsed.query else ""
        if MOUNT and not path.startswith(MOUNT):
            self.send_error(404, "outside mount %s" % MOUNT)
            return
        rel = path[len(MOUNT):] or "/"

        kind, *rest = resolve(rel)
        if kind == "redirect":
            code, to = rest
            self.send_response(code)
            self.send_header("Location", MOUNT + to + suffix)
            self.end_headers()
        elif kind == "serve":
            self.path = "/" + rest[0]
            return super().do_HEAD() if head else super().do_GET()
        else:
            self.send_error(404, "no asset for %s" % path)

    def do_HEAD(self):
        self.do_GET(head=True)

    def log_message(self, *a):
        pass


def audit():
    """Walk every page URL and report which ones cycle."""
    pages, loops = [], []
    for dirpath, _, files in os.walk(ROOT):
        if "/.git" in dirpath:
            continue
        for fn in files:
            if not fn.endswith(".html"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), ROOT)
            pages.append("/" + (rel[:-len("/index.html")] if rel.endswith("/index.html")
                                else "" if rel == "index.html" else rel[:-5]))
    for url in sorted(set(pages)):
        seen, cur = [], url or "/"
        for _ in range(12):
            if cur in seen:
                loops.append((url, seen + [cur]))
                break
            seen.append(cur)
            kind, *rest = resolve(cur)
            if kind != "redirect":
                break
            cur = rest[1]
    print(f"page URLs checked: {len(set(pages))}")
    if loops:
        print(f"\nREDIRECT LOOPS ({len(loops)}):")
        for url, chain in loops:
            print(f"  {MOUNT}{url}\n      {' -> '.join(chain)}")
        return 1
    print("no redirect loops ✓")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mount", default="/d13-app")
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--audit", action="store_true",
                    help="report looping page URLs and exit")
    a = ap.parse_args()
    MOUNT = a.mount.rstrip("/")
    if a.audit:
        sys.exit(audit())
    print(f"serving {ROOT} at http://127.0.0.1:{a.port}{MOUNT or '/'}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", a.port), Handler).serve_forever()
