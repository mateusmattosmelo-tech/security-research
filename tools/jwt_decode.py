#!/usr/bin/env python3
"""
jwt_decode.py — decode a JWT's header and payload (no verification) and flag risky settings.

Decoding is not verifying — this never checks the signature; it just makes the token readable and
points out the common weak spots (alg confusion openings, missing expiry, long lifetimes). Use it
to understand a token you already have, from an authorized test.

Usage:
    python3 jwt_decode.py <token>
    echo <token> | python3 jwt_decode.py -
"""
import base64
import datetime as dt
import json
import sys


def b64url(seg):
    seg += "=" * (-len(seg) % 4)
    return base64.urlsafe_b64decode(seg.encode())


def decode(token):
    parts = token.split(".")
    if len(parts) < 2:
        print("not a JWT (need at least header.payload)")
        return 1
    header = json.loads(b64url(parts[0]))
    payload = json.loads(b64url(parts[1]))
    print("# Header\n" + json.dumps(header, indent=2))
    print("\n# Payload\n" + json.dumps(payload, indent=2))

    print("\n# Notes")
    alg = str(header.get("alg", "")).lower()
    if alg == "none":
        print("  [!] alg=none — unsigned token accepted here means auth bypass")
    if alg.startswith("hs"):
        print("  [.] HMAC alg — if a server also accepts RS/ES, test key-confusion")
    if "kid" in header:
        print(f"  [.] kid present ({header['kid']!r}) — test path traversal / injection via kid")
    if "exp" not in payload:
        print("  [!] no exp claim — token may never expire")
    else:
        try:
            exp = dt.datetime.utcfromtimestamp(int(payload["exp"]))
            iat = payload.get("iat")
            span = f", lifetime {int(payload['exp']) - int(iat)}s" if iat else ""
            state = "EXPIRED" if exp < dt.datetime.utcnow() else "valid"
            print(f"  [.] exp = {exp}Z ({state}){span}")
        except Exception:
            pass
    for c in ("aud", "iss"):
        if c not in payload:
            print(f"  [.] no {c} claim — check whether the server enforces it")
    return 0


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip())
        return 1
    token = sys.stdin.read().strip() if argv[1] == "-" else argv[1]
    return decode(token.strip())


if __name__ == "__main__":
    sys.exit(main(sys.argv))
