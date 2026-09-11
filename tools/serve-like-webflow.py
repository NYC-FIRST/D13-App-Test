#!/usr/bin/env python3
"""Serve the repo the way Webflow Cloud (Cloudflare Workers Assets) does, so
breakage can be found locally instead of on the Nth deploy.

Emulates `auto-trailing-slash` html_handling plus a mount prefix:
  /d13-app/arcade/   -> 301 /d13-app/arcade
  /d13-app/arcade    -> serves arcade/index.html
  /d13-app/foo.html  -> 301 /d13-app/foo
  /d13-app/foo       -> serves foo.html

Usage:  tools/serve-like-webflow.py [--mount /d13-app] [--port 8787]
"""
import argparse, os, posixpath, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOUNT = "/d13-app"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def _redirect(self, to):
        self.send_response(301)
        self.send_header("Location", to)
        self.end_headers()

    def do_GET(self, head=False):
        parsed = urlparse(self.path)
        path, query = unquote(parsed.path), parsed.query
        suffix = ("?" + query) if query else ""

        if MOUNT and not path.startswith(MOUNT):
            self.send_error(404, "outside mount %s" % MOUNT)
            return
        rel = path[len(MOUNT):] if MOUNT else path

        # /foo.html -> /foo   (auto-trailing-slash strips the extension)
        if rel.endswith(".html"):
            base = rel[:-5]
            if base.endswith("/index"):
                base = base[: -len("index")]
            self._redirect(MOUNT + (base or "/") + suffix)
            return

        # /foo/ -> /foo   (strip the trailing slash), except the mount root
        if rel.endswith("/") and rel != "/":
            self._redirect(MOUNT + rel.rstrip("/") + suffix)
            return

        disk = posixpath.normpath(rel).lstrip("/")
        for cand in ([disk] if disk else []) + [
            os.path.join(disk, "index.html"), disk + ".html", "index.html" if not disk else None
        ]:
            if cand and os.path.isfile(os.path.join(ROOT, cand)):
                self.path = "/" + cand
                return super().do_HEAD() if head else super().do_GET()

        self.send_error(404, "no asset for %s" % path)

    def do_HEAD(self):
        self.do_GET(head=True)

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mount", default="/d13-app")
    ap.add_argument("--port", type=int, default=8787)
    a = ap.parse_args()
    MOUNT = a.mount.rstrip("/")
    print(f"serving {ROOT} at http://127.0.0.1:{a.port}{MOUNT or '/'} "
          f"(Webflow Cloud convention)", flush=True)
    ThreadingHTTPServer(("127.0.0.1", a.port), Handler).serve_forever()
