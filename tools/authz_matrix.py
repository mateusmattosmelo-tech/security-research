#!/usr/bin/env python3
"""
authz_matrix.py — run a two-account authorization matrix against a list of endpoints.

For each URL (which references account B's objects), it sends the request as:
  - account A's token (the attacker)   -> should be denied
  - account B's token (the owner)      -> the positive control (should succeed)
  - no token                           -> should be denied
A confirmed BOLA is A getting B's resource (A: 200 while the owner also gets 200 and anon is
denied). This is a triage aid — confirm each hit shows the real cross-account resource by hand.

Usage:
    python3 authz_matrix.py urls.txt --a "Authorization: Bearer AAA" --b "Authorization: Bearer BBB"

urls.txt: one full URL per line, each pointing at account B's object ids.
Authorized testing only, with two accounts you own.
"""
import argparse
import urllib.request


def call(url, header):
    req = urllib.request.Request(url, headers={"User-Agent": "authz-matrix/1.0"})
    if header:
        k, _, v = header.partition(":")
        req.add_header(k.strip(), v.strip())
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, len(r.read())
    except urllib.error.HTTPError as e:
        return e.code, len(e.read() or b"")
    except Exception:
        return 0, 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("urls")
    ap.add_argument("--a", required=True, help="attacker header, e.g. 'Authorization: Bearer ...'")
    ap.add_argument("--b", required=True, help="owner header (positive control)")
    args = ap.parse_args()

    print(f"{'A(attacker)':>14} {'B(owner)':>12} {'anon':>10}   URL")
    for line in open(args.urls):
        url = line.strip()
        if not url:
            continue
        a_s, a_n = call(url, args.a)
        b_s, b_n = call(url, args.b)
        n_s, _ = call(url, None)
        flag = ""
        if a_s == 200 and b_s == 200 and n_s in (401, 403):
            # A got a 200 like the owner while anon is denied -> candidate BOLA
            flag = "  *** BOLA candidate — verify A sees B's data ***"
        print(f"{a_s:>6}/{a_n:<7} {b_s:>5}/{b_n:<6} {n_s:>10}   {url}{flag}")
    print("\nA size similar to the owner's, with anon denied, is the tell. Confirm the actual data by hand.")


if __name__ == "__main__":
    main()
