#!/usr/bin/env python3
"""
openapi_diff.py — diff two OpenAPI specs to see how the API surface changed.

New endpoints between two spec snapshots are unlinked/fresh surface worth testing first; removed
ones may still answer if not decommissioned. Run it across versions of a vendor's shipped spec.

Usage:
    python3 openapi_diff.py old.json new.json

Reads local JSON files only; sends no traffic.
"""
import json
import sys


def operations(spec):
    ops = {}
    for path, item in spec.get("paths", {}).items():
        for method, op in item.items():
            if method.lower() in ("get", "post", "put", "patch", "delete"):
                key = f"{method.upper()} {path}"
                ops[key] = op.get("operationId", "")
    return ops


def main(argv):
    if len(argv) != 3:
        print(__doc__.strip())
        return 1
    old = operations(json.load(open(argv[1])))
    new = operations(json.load(open(argv[2])))
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))

    print(f"old: {len(old)} ops   new: {len(new)} ops\n")
    print(f"# Added ({len(added)}) — fresh surface, test first")
    for k in added:
        print(f"  + {k}  [{new[k]}]")
    print(f"\n# Removed ({len(removed)}) — may still answer if not decommissioned")
    for k in removed:
        print(f"  - {k}  [{old[k]}]")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
