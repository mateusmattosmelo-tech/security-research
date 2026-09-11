#!/usr/bin/env python3
"""
wellknown_scan.py — probe an origin for common discovery / metadata endpoints.

Discovery documents are unauthenticated by design and hand you the map: OAuth/OIDC config,
security contacts, change-management files, health/version endpoints. Cheap first pass on any
new web target.

Usage:
    python3 wellknown_scan.py https://example.com

Sends one GET per path to the origin you pass. Use only against authorized targets.
"""
import sys
import urllib.request

PATHS = [
    "/.well-known/openid-configuration",
    "/.well-known/oauth-authorization-server",
    "/.well-known/oauth-protected-resource",
    "/.well-known/security.txt",
    "/.well-known/change-password",
    "/.well-known/assetlinks.json",
    "/.well-known/apple-app-site-association",
    "/.well-known/host-meta",
    "/robots.txt",
    "/sitemap.xml",
    "/health", "/healthz", "/livez", "/readyz",
    "/version", "/api/version",
    "/openapi.json", "/swagger.json", "/graphql",
    "/.git/config", "/.env",
]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "wellknown-scan/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            body = r.read(200).decode("utf-8", "ignore").replace("\n", " ")
            return r.status, r.getheader("content-type", ""), body
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("content-type", ""), ""
    except Exception:
        return 0, "", ""


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip())
        return 1
    base = argv[1].rstrip("/")
    for p in PATHS:
        status, ct, body = get(base + p)
        if status and status not in (0, 404):
            flag = ""
            if p in ("/.git/config", "/.env") and status == 200:
                flag = "  *** exposed! ***"
            preview = f"  {body[:60]}" if status == 200 and "json" in ct else ""
            print(f"  [{status}] {p:42} {ct.split(';')[0]}{preview}{flag}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
