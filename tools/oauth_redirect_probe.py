#!/usr/bin/env python3
"""
oauth_redirect_probe.py — test whether an OAuth/OIDC authorization endpoint validates
redirect_uri strictly, or accepts bypass variants.

A loose redirect_uri check is a token-theft bug: the authorization code (or token) is sent to
an attacker-controlled URL. The correct behavior is exact-match — every variant below should be
rejected, and only the registered URI should proceed.

Usage:
    python3 oauth_redirect_probe.py \
        --authorize https://idp.example.com/oauth/authorize \
        --client-id CLIENT_ID \
        --registered https://app.example.com/callback

Sends unauthenticated GETs to the authorize endpoint. Use only against targets you're
authorized to test. Does not complete any login.
"""
import argparse
import sys
import urllib.parse
import urllib.request


def variants(registered):
    p = urllib.parse.urlparse(registered)
    host, path = p.netloc, p.path or "/"
    base = f"{p.scheme}://{host}"
    return {
        "registered (baseline)": registered,
        "different host": "https://attacker.example.com" + path,
        "attacker subdomain suffix": f"https://{host}.attacker.example.com" + path,
        "userinfo @attacker": f"https://{host}@attacker.example.com" + path,
        "path append": registered.rstrip("/") + "/../attacker",
        "different path, same host": base + "/anything-else",
        "appended open param": registered + "?next=https://attacker.example.com",
        "backslash trick": f"https://{host}\\@attacker.example.com" + path,
    }


def probe(authorize, client_id, redirect_uri):
    q = urllib.parse.urlencode({
        "client_id": client_id, "response_type": "code", "scope": "openid",
        "state": "probe", "redirect_uri": redirect_uri,
        "code_challenge": "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM",
        "code_challenge_method": "S256",
    })
    req = urllib.request.Request(f"{authorize}?{q}",
                                 headers={"User-Agent": "oauth-redirect-probe/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read(400).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read(400).decode("utf-8", "ignore")
    except Exception as e:
        return 0, str(e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--authorize", required=True)
    ap.add_argument("--client-id", required=True)
    ap.add_argument("--registered", required=True)
    a = ap.parse_args()

    print(f"authorize: {a.authorize}\nclient_id: {a.client_id}\n")
    for label, uri in variants(a.registered).items():
        code, body = probe(a.authorize, a.client_id, uri)
        looks_rejected = code >= 400 or "invalid" in body.lower() or "redirect" in body.lower()
        verdict = "rejected" if looks_rejected else "*** ACCEPTED — investigate ***"
        if label.startswith("registered"):
            verdict = f"baseline (HTTP {code})"
        print(f"  [{code}] {label:32} {verdict}")
    print("\nAll non-baseline variants should be rejected. Any ACCEPTED = potential token theft.")


if __name__ == "__main__":
    sys.exit(main())
