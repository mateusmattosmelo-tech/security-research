#!/usr/bin/env python3
"""
csp_analyze.py — parse a Content-Security-Policy and flag weaknesses.

A CSP decides which of your XSS/clickjacking payloads can even run, so reading it is the first
step of exploitation and of judging impact. Give it a header string or a URL to fetch the header
from.

Usage:
    python3 csp_analyze.py "default-src 'self'; script-src 'self' 'unsafe-inline' ..."
    python3 csp_analyze.py --url https://example.com

--url sends one request. Header-string mode is offline.
"""
import sys
import urllib.request


def parse(csp):
    out = {}
    for part in csp.split(";"):
        part = part.strip()
        if not part:
            continue
        name, *vals = part.split()
        out[name.lower()] = vals
    return out


def analyze(csp):
    d = parse(csp)
    notes = []
    script = d.get("script-src", d.get("default-src", []))
    if not d.get("script-src") and not d.get("default-src"):
        notes.append("[!] no script-src and no default-src — scripts are unrestricted")
    if "'unsafe-inline'" in script and "'strict-dynamic'" not in script:
        notes.append("[!] script-src has 'unsafe-inline' without 'strict-dynamic' — inline XSS runs")
    if "'unsafe-eval'" in script:
        notes.append("[.] script-src 'unsafe-eval' — eval-based sinks usable")
    for src in script:
        if src in ("*", "http:", "https:", "data:"):
            notes.append(f"[!] script-src allows {src!r} — effectively any script host")
        if src.endswith("*") or src.startswith("*."):
            notes.append(f"[.] script-src wildcard host {src!r} — check for a JSONP/upload gadget")
    if "object-src" not in d and "default-src" not in d:
        notes.append("[.] no object-src — plugin/object vectors not restricted")
    elif d.get("object-src") and d["object-src"] != ["'none'"]:
        notes.append("[.] object-src is not 'none'")
    if "base-uri" not in d:
        notes.append("[.] no base-uri — <base> tag injection can redirect relative script src")
    if "frame-ancestors" not in d:
        notes.append("[.] no frame-ancestors — clickjacking not blocked by CSP (check XFO)")
    nonce = any("'nonce-" in s or "'sha256-" in s for s in script)
    if nonce:
        notes.append("[ok] script-src uses a nonce/hash — strong if no unsafe-inline bypass")
    return d, notes


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip())
        return 1
    if argv[1] == "--url" and len(argv) == 3:
        req = urllib.request.Request(argv[2], headers={"User-Agent": "csp-analyze/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                csp = r.getheader("Content-Security-Policy", "")
        except Exception as e:
            print("fetch failed:", e)
            return 1
        if not csp:
            print("no Content-Security-Policy header on that response")
            return 0
    else:
        csp = argv[1]
    d, notes = analyze(csp)
    print("# Directives")
    for k, v in d.items():
        print(f"  {k}: {' '.join(v) if v else '(empty)'}")
    print("\n# Notes")
    for n in notes:
        print("  " + n)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
