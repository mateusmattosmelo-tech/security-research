#!/usr/bin/env python3
"""
cors_probe.py — check whether an endpoint reflects an arbitrary Origin with credentials.

The dangerous CORS misconfiguration is: the server echoes back whatever `Origin` you send in
`Access-Control-Allow-Origin` AND sets `Access-Control-Allow-Credentials: true`. That lets any
website read authenticated responses on behalf of a logged-in victim.

Usage:
    python3 cors_probe.py https://api.example.com/me

Sends a couple of unauthenticated requests (a GET and an OPTIONS preflight) with a test Origin.
Use only against targets you're authorized to test.
"""
import sys
import urllib.request

EVIL = "https://cors-probe.attacker.example.com"


def headers_for(url, method):
    req = urllib.request.Request(url, method=method,
                                 headers={"User-Agent": "cors-probe/1.0", "Origin": EVIL})
    if method == "OPTIONS":
        req.add_header("Access-Control-Request-Method", "GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, {k.lower(): v for k, v in r.getheaders()}
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k, v in e.headers.items()}
    except Exception as e:
        return 0, {"error": str(e)}


def report(url, method):
    status, h = headers_for(url, method)
    acao = h.get("access-control-allow-origin", "")
    acac = h.get("access-control-allow-credentials", "")
    print(f"\n{method} {url}  (HTTP {status})")
    print(f"  Access-Control-Allow-Origin:      {acao or '(none)'}")
    print(f"  Access-Control-Allow-Credentials: {acac or '(none)'}")
    reflected = acao == EVIL or acao == "*"
    if reflected and acac.lower() == "true" and acao != "*":
        print("  *** VULNERABLE: reflects arbitrary Origin WITH credentials ***")
    elif acao == "*" and acac.lower() == "true":
        print("  note: wildcard + credentials is rejected by browsers, but check the code path")
    elif reflected:
        print("  Origin reflected but no credentials — lower impact; check what data is exposed")
    else:
        print("  not reflecting the test Origin — not exploitable via this vector")


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip())
        return 1
    report(argv[1], "GET")
    report(argv[1], "OPTIONS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
