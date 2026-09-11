#!/usr/bin/env python3
"""
header_audit.py — quick read of a response's security-relevant headers.

Fetches a URL and reports which common security headers are present or missing, and
flags a few values worth a second look. This is a triage aid, not a scanner — missing
headers are usually low/informational on their own, but they colour how you read the
rest of the target.

Usage:
    python3 header_audit.py https://example.com

Sends exactly one GET to the URL you pass. Point it only at targets you're authorized
to test, and add any research/identification header your program requires (see notes).
"""
import sys
import urllib.request

WANTED = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
    "Permissions-Policy",
    "Cross-Origin-Opener-Policy",
    "Cross-Origin-Resource-Policy",
    "Cache-Control",
    "Set-Cookie",
]


def audit(url):
    req = urllib.request.Request(url, headers={"User-Agent": "header-audit/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        headers = {k.title(): v for k, v in resp.getheaders()}
        status = resp.status
    print(f"{status}  {url}\n")
    for name in WANTED:
        key = name.title()
        if key in headers:
            print(f"  [+] {name}: {headers[key]}")
        else:
            print(f"  [-] {name}: (missing)")
    # a couple of cheap value checks
    setc = headers.get("Set-Cookie", "")
    if setc:
        for flag in ("HttpOnly", "Secure", "SameSite"):
            if flag.lower() not in setc.lower():
                print(f"  [!] Set-Cookie missing {flag}")


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip())
        return 1
    audit(argv[1])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
