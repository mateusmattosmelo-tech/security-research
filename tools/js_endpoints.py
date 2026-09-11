#!/usr/bin/env python3
"""
js_endpoints.py — pull candidate API paths and URLs out of JavaScript bundles.

Front-end bundles are a map of the backend: every route the SPA can call is in there
somewhere. This extracts likely endpoints so you can diff them against what the UI
actually exercises — the gap is often unlinked or forgotten surface.

Usage:
    python3 js_endpoints.py app.js [more.js ...]
    cat bundle.js | python3 js_endpoints.py -

Only reads local files / stdin. It sends no traffic anywhere.
"""
import re
import sys

# Absolute URLs, and root-relative paths that look like API routes.
URL_RE = re.compile(r"""https?://[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+""")
PATH_RE = re.compile(r"""["'`](/(?:api|v\d|graphql|internal|admin|rest)[A-Za-z0-9._~/{}:-]*)["'`]""")


def extract(text):
    urls = set(URL_RE.findall(text))
    paths = set(m.group(1) for m in PATH_RE.finditer(text))
    return urls, paths


def read_source(name):
    if name == "-":
        return sys.stdin.read()
    with open(name, "r", errors="ignore") as fh:
        return fh.read()


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip())
        return 1
    all_urls, all_paths = set(), set()
    for name in argv[1:]:
        urls, paths = extract(read_source(name))
        all_urls |= urls
        all_paths |= paths
    if all_urls:
        print("# URLs")
        for u in sorted(all_urls):
            print(u)
    if all_paths:
        print("\n# API-looking paths")
        for p in sorted(all_paths):
            print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
